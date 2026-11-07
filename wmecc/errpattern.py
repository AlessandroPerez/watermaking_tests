"""Where do the bit errors fall: uniformly, or in a pattern?

The answer bears on the choice of code (random-error codes such as LDPC, polar and turbo
assume independent errors; Reed-Solomon pays off on bursts) and on the placement of the
bits in the image (the keyed layout spreads the votes of each bit over the whole frame).

``collect`` embeds the rate-1/2 channel of the semi-blind run (1024 coded bits, 8 votes
per bit, the calibrated strength of the r1/2 codes) in a sample of images, applies every
attack with the run's seeds, and keeps the library's vote of every block, the embedded
bit of every block and seven content features of the cover per block.

``analyze`` looks at three levels, per attack type:

* frames, from the semi-blind run: is a frame either clean or lost, or are there near
  misses that a stronger code would catch? (decoding success against raw BER)
* blocks: do wrong votes cluster in space (lift of the joint error rate of two blocks at
  distance d over independence), and does the content of a block predict its error?
  (gradient boosting on the cover features, trained on half the images and scored,
  frame by frame, on the other half: AUC 0.5 = no pattern)
* coded bits, after the layout and the vote: are errors independent along the codeword
  (autocorrelation), equal across positions and between header and ID, equally likely
  for 0 and 1, and are the votes of one bit independent? (dispersion of the number of
  wrong votes per bit against the binomial: 1 = independent)

``features`` and ``weighted`` test a blind decoder that weights each vote by the
reliability of its block. A gradient-boosting model, trained offline on other images,
predicts from what the decoder sees (features of the attacked block, the vote itself and
frame-wide means of the features) whether the vote is wrong. Images are split in two
halves; each half is decoded with the model trained on the other. Five LLRs feed the same
code (the n = 1024 split LDPC that was embedded):

* ``equal``: every vote counts the same (the experiment's decoder);
* ``weighted``: votes weighted by |log((1-q)/q)|, then the same blind mixture fit;
* ``model``: each vote adds +-log((1-q)/q), q the predicted chance that it is wrong;
* ``capped``: as ``model`` with q at most 0.5, so a vote is discounted, never turned over;
* ``hybrid``: as ``capped``, with the error level of the frame set by the blind mixture
  fit and the model giving only how much better or worse each block is than average.

    python -m wmecc.errpattern collect --images 12 --workers 2
    python -m wmecc.errpattern analyze
    python -m wmecc.errpattern features --workers 2
    python -m wmecc.errpattern weighted
"""

from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from . import experiment as ex
from .attacks import attack_suite, get_attacks
from .codes import get_codes
from .data import load_rgb
from .watermark import imwm

CODE = "ldpc_r12_split"     # any n = 1024 code: the channel depends on n and strength only
FEATURES = ("y_mean", "y_std", "u_dev", "u_std", "v_dev", "v_std", "clipped")
LAGS = (1, 2, 4, 8, 16, 32)
OUT = Path("results/errpattern")


def _blocks(a: np.ndarray) -> np.ndarray:
    """(1024, 1024) -> (blocks, 64) in the library's block order (row by row)."""
    s, b = imwm.SIDE, imwm.BLOCK
    return a.reshape(s, b, s, b).swapaxes(1, 2).reshape(s * s, b * b)


def _features(rgb: np.ndarray) -> np.ndarray:
    """Per block of the cover: luma mean and spread, chroma distance from grey and
    spread (U carries the mark), and the share of clipped pixels."""
    yuv = cv2.cvtColor(np.ascontiguousarray(rgb[..., ::-1]), cv2.COLOR_BGR2YUV).astype(float)
    y, u, v = (_blocks(yuv[..., c]) for c in range(3))
    clipped = _blocks(((rgb <= 2) | (rgb >= 253)).any(axis=2).astype(float))
    return np.stack([y.mean(1), y.std(1), np.abs(u.mean(1) - 128), u.std(1),
                     np.abs(v.mean(1) - 128), v.std(1), clipped.mean(1)], 1).astype(np.float32)


def _collect_one(args):
    cfg, i, path, conditions, scale, out = args
    ex._init_worker()
    code = {c.name: c for c in get_codes([CODE], modules=("split",))}[CODE]
    img = load_rgb(path)
    bits = code.encode(cfg.message_for(path.name))[0] ^ ex.whitening(cfg, code.n)
    wm = imwm.embed(img, bits, scale, cfg.seed, cfg.votes_per_bit)
    attacks = get_attacks(conditions)
    votes = np.full((len(attacks), imwm.BLOCKS), 255, np.uint8)     # 255: frame too small
    for j, a in enumerate(attacks):
        seed = int(ex._rng(cfg.seed, 5, i, j).integers(2**31))    # the run's attack seeds
        v = imwm.block_votes(a(wm, seed=seed), scale)
        if v is not None:
            votes[j] = v
    np.savez_compressed(out / f"{path.stem}.npz", votes=votes, bits=bits,
                        layout=imwm._layout(code.n, cfg.seed, cfg.votes_per_bit),
                        features=_features(img), attacks=np.array([a.name for a in attacks]))
    return path.stem


def collect(cfg: ex.ExpConfig, images: int, workers: int, out: Path = OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    scale = json.loads((cfg.path / "calibration.json").read_text())[CODE]["scale"]
    paths = cfg.test_images()
    step = max(1, len(paths) // images)
    jobs = [(cfg, i, paths[i], cfg.conditions, scale, out) for i in range(3, len(paths), step)][:images]
    jobs = [j for j in jobs if not (out / f"{j[2].stem}.npz").exists()]
    print(f"  {len(jobs)} images to collect at strength {scale}", flush=True)
    with Pool(workers) as pool:
        for k, stem in enumerate(pool.imap_unordered(_collect_one, jobs), 1):
            print(f"  {k}/{len(jobs)} {stem}", flush=True)


# ----------------------------------------------------------------- analysis
def _frames(out: Path, n: int):
    """Yield one record per attacked frame with the block and coded-bit errors."""
    kind = {a.name: a.kind for a in attack_suite()}
    for f in sorted(out.glob("*.npz")):
        if f.name.count(".") != 1:        # skip the .feat.npz files
            continue
        z = np.load(f)
        layout, bits = z["layout"], z["bits"]
        marked = layout >= 0
        sent = np.where(marked, bits[np.maximum(layout, 0)], 0)
        for j, name in enumerate(z["attacks"]):
            v = z["votes"][j]
            if name == "none" or v[0] == 255:
                continue
            wrong = (v != sent) & marked
            ones = np.bincount(layout[marked], v[marked].astype(float), n)
            count = np.bincount(layout[marked], minlength=n).astype(float)
            llr = imwm.votes_to_llr(ones, count)
            yield dict(image=f.stem, attack=str(name), kind=kind[str(name)], wrong=wrong,
                       marked=marked, sent=sent, layout=layout, features=z["features"],
                       bit_err=((llr < 0).astype(np.uint8) != bits),
                       wrong_votes=np.bincount(layout[marked], wrong[marked].astype(float), n))


def _lift(wrong: np.ndarray, marked: np.ndarray, p: float) -> list[float]:
    """Joint error rate of two marked blocks d apart (rows and columns) over p**2."""
    s = imwm.SIDE
    w, m = wrong.reshape(s, s).astype(float), marked.reshape(s, s)
    out = []
    for d in LAGS:
        both = pairs = 0.0
        for a, b, ma, mb in ((w[:, :-d], w[:, d:], m[:, :-d], m[:, d:]),
                             (w[:-d], w[d:], m[:-d], m[d:])):
            k = ma & mb
            both += (a[k] * b[k]).sum()
            pairs += k.sum()
        out.append(both / pairs / p ** 2)
    return out


def _autocorr(e: np.ndarray, lag: int) -> float:
    a, b = e[:-lag].astype(float), e[lag:].astype(float)
    if a.std() == 0 or b.std() == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def analyze(cfg: ex.ExpConfig, out: Path = OUT) -> None:
    n, vpb = 1024, cfg.votes_per_bit
    frames, blocks = [], {}
    rng = np.random.default_rng(0)
    for r in _frames(out, n):
        m = r["marked"]
        p = r["wrong"][m].mean()
        ber = r["bit_err"].mean()
        row = dict(image=r["image"], attack=r["attack"], kind=r["kind"], block_err=p, bit_err=ber)
        informative = 0.02 <= p <= 0.45
        if informative:
            row |= {f"lift_{d}": x for d, x in zip(LAGS, _lift(r["wrong"], m, p))}
            sent = r["sent"][m]
            row["err_given_0"] = r["wrong"][m][sent == 0].mean()
            row["err_given_1"] = r["wrong"][m][sent == 1].mean()
            w = r["wrong_votes"]
            row["dispersion"] = w.var() / (vpb * p * (1 - p))
            # single-feature AUC within the frame (direction-free)
            for k, name in enumerate(FEATURES):
                a = roc_auc_score(r["wrong"][m], r["features"][m, k])
                row[f"auc_{name}"] = max(a, 1 - a)
            # sample of blocks for the content model
            idx = rng.choice(np.flatnonzero(m), 2000, replace=False)
            blocks.setdefault(r["kind"], []).append(pd.DataFrame(
                r["features"][idx], columns=FEATURES).assign(
                frame_logit=np.log(p / (1 - p)), y=r["wrong"][idx], image=r["image"],
                frame=f"{r['image']} {r['attack']}"))
        if 0.01 <= ber <= 0.40:
            e = r["bit_err"]
            row |= {f"acf_{k}": _autocorr(e, k) for k in (1, 2, 3, 4)}
            row["bit_err_header"] = e[:256].mean()
            row["bit_err_id"] = e[256:].mean()
            row["bit_errors"] = int(e.sum())
            row["bins"] = e.reshape(16, 64).sum(1).tolist()
        frames.append(row)
    df = pd.DataFrame(frames)
    out_a = out / "analysis"
    out_a.mkdir(exist_ok=True)
    df.drop(columns="bins").to_csv(out_a / "frames.csv", index=False)

    # content model: train on half the images, score each held-out frame on its own
    images = sorted(df.image.unique())
    train_images = set(images[0::2])
    content = []
    for kd, parts in blocks.items():
        b = pd.concat(parts)
        tr, te = b[b.image.isin(train_images)], b[~b.image.isin(train_images)]
        if tr.y.nunique() < 2 or te.empty:
            continue
        cols = list(FEATURES) + ["frame_logit"]
        model = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1).fit(tr[cols], tr.y)
        te = te.assign(score=model.predict_proba(te[cols])[:, 1])
        aucs, top = [], []
        for _, g in te.groupby("frame"):
            if g.y.nunique() < 2:
                continue
            aucs.append(roc_auc_score(g.y, g.score))
            worst = g.score >= g.score.quantile(0.8)        # the 20 % of blocks the model fears most
            top.append(g.y[worst].sum() / g.y.sum())
        content.append(dict(kind=kd, model_frames=len(aucs), auc=np.median(aucs),
                            errors_in_worst_20pct=np.median(top)))
    content = pd.DataFrame(content)

    # coded-bit positions, pooled per attack type
    pos = []
    for kd, g in df.dropna(subset=["acf_1"]).groupby("kind"):
        bins = np.array(g.bins.tolist())                      # frames x 16 bins of 64 bits
        tot = bins.sum(0)
        chi = chi2_contingency(np.stack([tot, 64 * len(g) - tot]))[1]
        pos.append(dict(kind=kd, bit_frames=len(g), position_p=chi,
                        header=g.bit_err_header.mean(), ident=g.bit_err_id.mean()))
    pos = pd.DataFrame(pos)

    agg = {c: "median" for c in df.columns if c.startswith(("lift_", "auc_", "acf_"))}
    agg |= dict(dispersion="median", err_given_0="mean", err_given_1="mean",
                block_err="median", bit_err="median")
    summary = df.groupby("kind").agg(frames=("attack", "size"), **{k: (k, v) for k, v in agg.items()})
    summary = summary.join(content.set_index("kind")).join(pos.set_index("kind"))
    summary.to_csv(out_a / "summary.csv")

    # spread across images: share of the variance of logit(block error) due to the image
    lp = np.log(df.block_err.clip(1e-3, 1 - 1e-3) / (1 - df.block_err.clip(1e-3, 1 - 1e-3)))
    t = df.assign(lp=lp).pivot_table(index="image", columns="attack", values="lp")
    attack_eff = t.mean(0) - t.values.mean()
    image_eff = t.mean(1) - t.values.mean()
    rest = t.values - t.values.mean() - attack_eff.values[None, :] - image_eff.values[:, None]
    var = dict(attack=float(t.shape[0] * (attack_eff ** 2).sum()),
               image=float(t.shape[1] * (image_eff ** 2).sum()),
               rest=float((rest ** 2).sum()))
    tot = sum(var.values())
    (out_a / "variance.json").write_text(json.dumps({k: v / tot for k, v in var.items()}, indent=1))

    near = near_misses(cfg.path)
    near.to_csv(out_a / "near_misses.csv", index=False)

    with pd.option_context("display.width", 250, "display.max_columns", 60):
        print(f"{df.image.nunique()} images, {len(df)} attacked frames")
        print("variance of logit(block error rate):", {k: round(v / tot, 3) for k, v in var.items()})
        print(summary.round(3).T.to_string())
        print(near.round(3).to_string(index=False))


RAW_BINS = [0, .02, .05, .08, .11, .15, .20, .30, .40, .45, 1.01]


def near_misses(run: Path) -> pd.DataFrame:
    """From the semi-blind run: the frames each code fails on, by raw BER of the
    codeword it decoded. Failures just above what the code corrects are near misses
    that a stronger code would catch; failures at 40-50 % are lost frames no code reads."""
    files = ([run / "results.csv"] if (run / "results.csv").exists()
             else sorted((run / "parts").glob("*.results.csv")))
    cols = ["image", "code", "decoder", "attack", "watermarked", "raw_ber", "id_ok"]
    res = pd.concat(pd.read_csv(f, usecols=cols) for f in files)
    res = res[res.watermarked & (res.attack != "none") & res.decoder.isin(["plain", "search"])]
    res["raw"] = pd.cut(res.raw_ber, RAW_BINS, right=False)
    g = res.groupby(["code", "decoder", "raw"], observed=False).id_ok
    t = pd.DataFrame(dict(frames=g.size(), recovered=g.mean(), failed=g.size() - g.sum()))
    t["share_of_failures"] = t.failed / t.groupby(level=[0, 1]).failed.transform("sum")
    return t.reset_index().assign(images=res.image.nunique())


# ------------------------------------------------- reliability-weighted votes
def _features_one(args):
    """Block features of every attacked frame, as the extractor reads it."""
    cfg, i, path, conditions, scale, out = args
    ex._init_worker()
    z = np.load(out / f"{path.stem}.npz")
    wm = imwm.embed(load_rgb(path), z["bits"], scale, cfg.seed, cfg.votes_per_bit)
    attacks = get_attacks(conditions)
    feats = np.zeros((len(attacks), imwm.BLOCKS, len(FEATURES)), np.float16)
    for j, a in enumerate(attacks):
        seed = int(ex._rng(cfg.seed, 5, i, j).integers(2**31))
        x = imwm.to_frame(a(wm, seed=seed))
        if x is not None:
            feats[j] = _features(x)
    np.savez_compressed(out / f"{path.stem}.feat.npz", features=feats)
    return path.stem


def collect_features(cfg: ex.ExpConfig, workers: int, out: Path = OUT) -> None:
    scale = json.loads((cfg.path / "calibration.json").read_text())[CODE]["scale"]
    index = {p.stem: i for i, p in enumerate(cfg.test_images())}
    paths = {p.stem: p for p in cfg.test_images()}
    stems = [f.name.split(".")[0] for f in sorted(out.glob("*.npz")) if f.name.count(".") == 1]
    jobs = [(cfg, index[s], paths[s], cfg.conditions, scale, out) for s in stems
            if not (out / f"{s}.feat.npz").exists()]
    print(f"  {len(jobs)} images", flush=True)
    with Pool(workers) as pool:
        for k, stem in enumerate(pool.imap_unordered(_features_one, jobs), 1):
            print(f"  {k}/{len(jobs)} {stem}", flush=True)


def _inputs(feats: np.ndarray, votes: np.ndarray) -> np.ndarray:
    """Decoder-side inputs per block: its features, its vote, frame-wide feature means."""
    f = feats.astype(np.float32)
    return np.column_stack([f, votes, np.broadcast_to(f.mean(0), f.shape)])


VARIANTS = ("equal", "weighted", "model", "capped", "hybrid")


def _oof_reliability(data: dict, out: Path, per_frame: int) -> dict:
    """q = predicted chance that each vote is wrong, for every image from the model
    trained on the other half of the images (cached in ``<image>.q.npz``)."""
    stems = sorted(data)
    if all((out / f"{s}.q.npz").exists() for s in stems):
        return {s: np.load(out / f"{s}.q.npz")["q"] for s in stems}
    halves = [stems[0::2], stems[1::2]]
    rng = np.random.default_rng(0)
    qs = {}
    for h in (0, 1):
        X, y = [], []
        for s in halves[h]:
            d = data[s]
            for j in range(len(d["names"])):
                idx = rng.choice(len(d["sent"]), per_frame, replace=False)
                X.append(_inputs(d["feats"][j][idx], d["votes"][j][idx]))
                y.append(d["votes"][j][idx] != d["sent"][idx])
        model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=0)
        model.fit(np.concatenate(X), np.concatenate(y))
        for s in halves[1 - h]:
            d = data[s]
            qs[s] = np.stack([model.predict_proba(_inputs(d["feats"][j], d["votes"][j]))[:, 1]
                              for j in range(len(d["names"]))]).astype(np.float16)
            np.savez_compressed(out / f"{s}.q.npz", q=qs[s])
        print(f"  half {h + 1} of 2 scored", flush=True)
    return qs


def _llrs(v: np.ndarray, q: np.ndarray, lay: np.ndarray, n: int) -> dict:
    """Coded-bit LLRs (whitened bits) of one frame under each decoder variant.

    capped: q at most 0.5, so a vote is discounted, never turned over.
    hybrid: capped, and the level of the frame comes from the blind mixture fit of the
    equal votes; the model only says which blocks are more or less reliable than the
    average block of the frame."""
    q = np.clip(q, 1e-4, 1 - 1e-4)
    logit = np.log(q / (1 - q))
    ones, count = np.bincount(lay, v, n), np.bincount(lay, minlength=n).astype(float)
    sign = 1 - 2 * v
    out = dict(equal=imwm.votes_to_llr(ones, count))
    w = np.abs(logit)
    out["weighted"] = imwm.votes_to_llr(np.bincount(lay, w * v, n), np.bincount(lay, w, n))
    out["model"] = np.bincount(lay, sign * -logit, n)
    out["capped"] = np.bincount(lay, sign * np.maximum(-logit, 0.0), n)
    m = imwm._mixture(ones, count)
    p = 0.49 if m is None else float(np.clip((m[0] + 1 - m[1]) / 2, 1e-3, 0.49))
    frame = np.log(p / (1 - p)) + logit - logit.mean()
    out["hybrid"] = np.bincount(lay, sign * np.maximum(-frame, 0.0), n)
    return out


def weighted(cfg: ex.ExpConfig, out: Path = OUT, per_frame: int = 3000) -> None:
    code = {c.name: c for c in get_codes([CODE], modules=("split",))}[CODE]
    key = ex.whitening(cfg, code.n)
    kind = {a.name: a.kind for a in attack_suite()}
    stems = [f.name.split(".")[0] for f in sorted(out.glob("*.feat.npz"))]
    data = {}
    for s in stems:
        z, f = np.load(out / f"{s}.npz"), np.load(out / f"{s}.feat.npz")
        names = [str(a) for a in z["attacks"]]
        keep = [j for j, a in enumerate(names) if a != "none" and z["votes"][j, 0] != 255]
        layout = z["layout"]
        marked = layout >= 0
        data[s] = dict(names=[names[j] for j in keep], votes=z["votes"][keep][:, marked],
                       feats=f["features"][keep][:, marked], layout=layout[marked],
                       sent=z["bits"][layout[marked]], bits=z["bits"])
    qs = _oof_reliability(data, out, per_frame)
    rows = []
    for s in stems:
        d, q_all = data[s], qs[s]
        msg = cfg.message_for(f"{s}.png")[0]
        cw = d["bits"] ^ key
        llrs = {v: [] for v in VARIANTS}
        for j in range(len(d["names"])):
            v, lay = d["votes"][j].astype(float), d["layout"]
            for name, L in _llrs(v, q_all[j].astype(float), lay, code.n).items():
                llrs[name].append(L)
        for variant, L in llrs.items():
            L = np.stack(L) * (1.0 - 2.0 * key)          # LLRs of the codeword bits
            hd, idd = code.decode_parts(L)
            raw = ((L < 0) != cw).mean(1)
            for j, a in enumerate(d["names"]):
                rows.append(dict(image=s, attack=a, kind=kind[a], decoder=variant,
                                 raw_ber=raw[j],
                                 header_ok=bool(np.array_equal(hd.msg[j], msg[:128])),
                                 id_ok=bool(np.array_equal(idd.msg[j], msg[128:]))))
    df = pd.DataFrame(rows)
    out_a = out / "analysis"
    out_a.mkdir(exist_ok=True)
    df.to_csv(out_a / "weighted.csv", index=False)
    wide = df.pivot_table(index=["image", "attack", "kind"], columns="decoder", values="id_ok").reset_index()
    by_kind = 100 * df.pivot_table(index="kind", columns="decoder", values="id_ok")
    by_kind.loc["all"] = 100 * df.groupby("decoder").id_ok.mean()
    ber = 100 * df.pivot_table(index="kind", columns="decoder", values="raw_ber", aggfunc="median")
    flips = pd.DataFrame({v: dict(gained=int(((wide[v] == 1) & (wide.equal == 0)).sum()),
                                  lost=int(((wide[v] == 0) & (wide.equal == 1)).sum()),
                                  images_better=int((wide.groupby("image")[v].sum()
                                                     > wide.groupby("image").equal.sum()).sum()),
                                  images_worse=int((wide.groupby("image")[v].sum()
                                                    < wide.groupby("image").equal.sum()).sum()))
                          for v in VARIANTS[1:]}).T
    by_kind.to_csv(out_a / "weighted_by_kind.csv")
    flips.to_csv(out_a / "weighted_flips.csv")
    with pd.option_context("display.width", 200):
        print(f"{df.image.nunique()} images, {len(wide)} attacked frames, ID exact recovery (%)")
        print(by_kind.round(1).to_string())
        print("median raw BER (%)")
        print(ber.round(1).to_string())
        print(flips.to_string())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["collect", "analyze", "features", "weighted"])
    ap.add_argument("--config", default="configs/semiblind.yaml")
    ap.add_argument("--images", type=int, default=12)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args(argv)
    cfg = ex.ExpConfig.load(args.config)
    t = time.time()
    if args.stage == "collect":
        collect(cfg, args.images, args.workers)
    elif args.stage == "features":
        collect_features(cfg, args.workers)
    elif args.stage == "weighted":
        weighted(cfg)
    else:
        analyze(cfg)
    print(f"== {args.stage} done in {(time.time() - t) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
