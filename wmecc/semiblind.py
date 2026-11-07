"""Semi-blind experiment: a known 128-bit header and a random 384-bit ID per image.

    python -m wmecc.semiblind {calibrate,run,analyze} --config configs/semiblind.yaml
    python -m wmecc.semiblind {run,compare} --config configs/semiblind_idh.yaml

The message of an image is the experiment's fixed header (128 bits, the same for every
image) followed by an ID drawn for that image (384 bits, the same for every code).
``codes/split.py`` joins them in two ways: ``*_split`` encodes each part on its own and
embeds the two codewords side by side; ``*_joint`` encodes ``header | ID`` as one message.
The extractor stays blind with respect to the image; the decoder knows the header.

Three decoders read every frame:

plain   decodes as extracted, as in the earlier runs.
pilot   undoes a whole-frame inversion (a colour attack that flips more than half of the
        blocks inverts every bit). Split codes see it before decoding: fewer than half of
        the extracted bits agree with the known header codeword. Joint codes decode the
        inverted frame too, and keep it if its header decodes to the header.
search  pilot, and when the header does not decode to the header (or the ID fails its
        own check), it tries corrections of the attacked image: chroma gains (the frame is
        redrawn from its own chroma, scaled, at a neutral luminance, which undoes the gain
        that brightness, contrast and saturation put on the chroma channel without clipping)
        and gammas (``skimage.exposure.adjust_gamma``). Split codes keep the candidate whose
        extracted bits agree most with the header codeword and decode it; joint codes decode
        every candidate (and its inversion) and keep one whose header decodes to the header.
        Unwatermarked frames get the search only on every ``search_null_every``-th image.

Codes whose header can be decoded on its own terms (``ldpc_r12_jidh``: the header bits
are sent as they are) get three more rows, ``<decoder>_known``: a frame that the pilot
count of that decoder flags is decoded again with the header bits fixed to the header,
which leaves only the ID to the code; frames the count does not flag get no ID.

Detection, split codes (and ``ldpc_r12_jidh``): count the agreements m of the extracted
bits with the header codeword (with the header bits sent as they are). Without a watermark each agreement is a fair coin (the codeword is whitened), so
m ~ Bin(n_h, 1/2), and the threshold for a false-positive rate alpha follows from the
binomial law: one-sided for plain, two-sided for pilot (the sign is unknown), and alpha
divided by the number of candidates for search (union bound). Both designs also detect by
decoding: does the header decode to the known header?
"""

from __future__ import annotations

import argparse
import functools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import cv2
from scipy.stats import binom
from skimage.exposure import adjust_gamma

from . import experiment as ex
from .attacks import attack_suite, get_attacks
from .data import load_rgb
from .metrics import nvf_map, psnr, ssim, wpsnr
from .watermark import imwm

DECODERS = ("plain", "pilot", "search")
GAINS = [round(1.1 ** j, 4) for j in (-4, -3, -2, -1, 1, 2, 3, 4)]      # 0.68 .. 1.46
GAMMAS = [round(1.2 ** j, 4) for j in (-4, -3, -2, -1, 1, 2, 3, 4)]     # 0.48 .. 2.07
ALPHA = 1e-6           # false-positive rate of the agreement detector


def _chroma(x, c):
    """The frame redrawn at luminance 128 with its chroma scaled by c around 128 (OpenCV
    YUV, the colour space the watermark library reads)."""
    yuv = cv2.cvtColor(np.ascontiguousarray(x[..., ::-1]), cv2.COLOR_BGR2YUV).astype(np.float32)
    yuv[..., 0] = 128.0
    yuv[..., 1:] = 128.0 + c * (yuv[..., 1:] - 128.0)
    bgr = cv2.cvtColor(np.clip(np.rint(yuv), 0, 255).astype(np.uint8), cv2.COLOR_YUV2BGR)
    return np.ascontiguousarray(bgr[..., ::-1])


def _gamma(x, g):
    return adjust_gamma(x, g)


def corrections(cfg: ex.ExpConfig) -> list:
    """(name, function) of every candidate the search tries, the identity first."""
    out = [("none", None)]
    out += [(f"chroma_x{c:g}", functools.partial(_chroma, c=c)) for c in cfg.search_gains or GAINS]
    out += [(f"gamma_{g:g}", functools.partial(_gamma, g=g)) for g in cfg.search_gammas or GAMMAS]
    return out


def threshold(n: int, alpha: float = ALPHA, two_sided: bool = False, tests: int = 1) -> int:
    """Smallest agreement count t whose false-positive rate, P(Bin(n, 1/2) >= t) times
    the number of sides and of tests, is at most alpha."""
    return int(binom.isf(alpha / ((2 if two_sided else 1) * tests), n, 0.5)) + 1


def flag_threshold(n_header: int, decoder: str, n_fixes: int, alpha: float = ALPHA) -> float:
    """Pilot count that flags a frame read by ``decoder`` (``*_known`` as its base)."""
    if not n_header:
        return np.inf
    base = decoder.removesuffix("_known")
    return threshold(n_header, alpha, base != "plain", n_fixes if base == "search" else 1)


def _outcome(v, L: np.ndarray, header: np.ndarray, ident: np.ndarray) -> dict:
    h, i = v.decode_parts(L)
    return dict(header_ok=(h.msg == header).all(axis=1), header_bits=(h.msg == header).sum(axis=1),
                header_valid=h.valid.copy(),
                id_ok=(i.msg == ident).all(axis=1), id_valid=i.valid.copy(),
                id_ber=(i.msg != ident).mean(axis=1))


def _patch(base: dict, idx: np.ndarray, v, L: np.ndarray, header, ident) -> dict:
    out = {key: val.copy() for key, val in base.items()}
    if idx.any():
        for key, val in _outcome(v, L[idx], header, ident).items():
            out[key][idx] = val
    return out


def _pick_joint(code, cands: np.ndarray, header, ident) -> tuple[int, dict]:
    """Decode every candidate (rows of ``cands``) and return the index of the best one,
    ranked by: header decoded, ID check passed, header bits right."""
    out = _outcome(code, cands, header, ident)
    score = (out["header_ok"].astype(int) * 2 * len(header)
             + (out["id_valid"] & code.has_check).astype(int) * len(header) + out["header_bits"])
    best = int(np.argmax(score))
    return best, {k: v[best] for k, v in out.items()}


def _run_one(args):
    cfg, i, path, conditions, cal = args
    ex._init_worker()
    from .codes.base import hard
    img = load_rgb(path)
    nvf = nvf_map(img)
    attacks = get_attacks(conditions)
    seeds = [int(ex._rng(cfg.seed, 5, i, j).integers(2**31)) for j in range(len(attacks))]
    attacked0 = [a(img, seed=s) for a, s in zip(attacks, seeds)]
    msg = cfg.message_for(path.name)
    header, ident = msg[0, :128], msg[0, 128:]
    fixes = corrections(cfg)
    search_null = i % cfg.search_null_every == 0
    frames = [(j, marked) for j in range(len(attacks)) for marked in (True, False)]
    marked = np.array([m for _, m in frames])
    rows, embeds = [], []
    # The library's block votes depend only on the frame and the strength, and
    # extraction is most of the run time: an unwatermarked frame (after each
    # correction) is read once per strength and shared by the codes that use it.
    cover_votes = {}
    for name, (code, variants) in ex._embedding_codes(cfg).items():
        assert variants == [code], "decoder variants are not supported here"
        t0 = time.perf_counter()
        scale = cal[name]["scale"]
        cw = code.encode(msg)[0]
        key = ex.whitening(cfg, code.n)
        nh, pil = code.n_header, code.pilot
        wm = imwm.embed(img, cw ^ key, scale, cfg.seed, cfg.votes_per_bit)

        attacked = {}      # attacked watermarked frames, kept for the search

        def votes(r, f=0):
            """Block votes of frame r after correction f (0: none)."""
            j, m = frames[r]
            if m:
                if j not in attacked:
                    attacked[j] = attacks[j](wm, seed=seeds[j])
                x = attacked[j]
                return imwm.block_votes(fixes[f][1](x) if f else x, scale)
            if (j, f, scale) not in cover_votes:
                x = attacked0[j]
                cover_votes[j, f, scale] = imwm.block_votes(fixes[f][1](x) if f else x, scale)
            return cover_votes[j, f, scale]

        def llr(v):
            ones, count = imwm.tally(v, code.n, cfg.seed, cfg.votes_per_bit)
            return imwm.votes_to_llr(ones, count) * (1.0 - 2.0 * key)

        def agreement(L):
            return (hard(L[..., pil]) == cw[pil]).sum(axis=-1)

        L = np.stack([llr(votes(r)) for r in range(len(frames))])
        plain = _outcome(code, L, header, ident)
        if nh:                                    # split, jidh: the header bits are a pilot
            agree = agreement(L)
            flip = 2 * agree < nh
        else:                                     # joint: try the inverted frame as well
            agree = np.full(len(frames), -1)
            flip = np.zeros(len(frames), bool)
            idx = np.flatnonzero(~plain["header_ok"])
            if len(idx):
                flip[idx] = _outcome(code, -L[idx], header, ident)["header_ok"]
        Lp = np.where(flip[:, None], -L, L)
        pilot = _patch(plain, flip, code, Lp, header, ident)
        searched = ((~pilot["header_ok"] | (code.has_check & ~pilot["id_valid"]))
                    & (marked | search_null))

        search = {k: v.copy() for k, v in pilot.items()}
        best_L, best_agree = Lp.copy(), np.where(agree >= 0, np.maximum(agree, nh - agree), -1)
        best_fix = np.array(["none"] * len(frames), dtype=object)
        for r in np.flatnonzero(searched):
            cands = np.stack([llr(votes(r, f)) for f in range(1, len(fixes))])
            if nh:
                a = agreement(cands)
                a2 = np.maximum(a, nh - a)
                c = int(np.argmax(a2))
                if a2[c] > best_agree[r]:
                    best_agree[r], best_fix[r] = a2[c], fixes[1 + c][0]
                    best_L[r] = -cands[c] if 2 * a[c] < nh else cands[c]
            else:
                both = np.concatenate([cands, -cands])
                c, out = _pick_joint(code, both, header, ident)
                if out["header_ok"] and not pilot["header_ok"][r] or (
                        out["header_ok"] and out["id_valid"] and not pilot["id_valid"][r]):
                    best_fix[r] = fixes[1 + c % len(cands)][0]
                    best_L[r] = both[c]
                    for k, v in out.items():
                        search[k][r] = v
        if nh:
            search = _patch(pilot, searched & (best_fix != "none"), code, best_L, header, ident)
        seconds = time.perf_counter() - t0
        embeds.append(dict(image=path.name, code=name, n=code.n, n_header=nh, scale=scale,
                           wpsnr=wpsnr(img, wm, nvf=nvf), psnr=psnr(img, wm), ssim=ssim(img, wm),
                           searched=int(searched.sum()), seconds=seconds))

        pilot_agree = np.where(agree >= 0, np.maximum(agree, nh - agree), -1)
        used = dict(plain=(L, agree), pilot=(Lp, pilot_agree),
                    search=(np.where(searched[:, None], best_L, Lp),
                            np.where(searched, best_agree, pilot_agree)))
        results = dict(zip(DECODERS, (plain, pilot, search)))
        if nh and hasattr(code, "decode_known"):          # two stages: flag, then known header
            for d in DECODERS:
                Ld, ad = used[d]
                flagged = ad >= flag_threshold(nh, d, len(fixes))
                res = {k: v.copy() for k, v in results[d].items()}
                res["header_ok"] = flagged
                res["id_ok"] &= False
                res["id_valid"] &= False
                if flagged.any():
                    h, i_ = code.decode_known(Ld[flagged], header)
                    res["id_ok"][flagged] = (i_.msg == ident).all(axis=1)
                    res["id_valid"][flagged] = i_.valid
                    res["id_ber"][flagged] = (i_.msg != ident).mean(axis=1)
                results[f"{d}_known"] = res
                used[f"{d}_known"] = used[d]
        for d, res in results.items():
            Ld, ad = used[d]
            raw = (hard(Ld) != cw).mean(axis=1)
            for r, (j, m) in enumerate(frames):
                if d.startswith("search") and not m and not search_null:
                    continue
                rows.append(dict(
                    image=path.name, code=code.name, design=code.design,
                    family=code.family, n=code.n, n_header=nh, has_check=code.has_check,
                    decoder=d, attack=attacks[j].name, category=attacks[j].family,
                    watermarked=m, agree=int(ad[r]),
                    flipped=bool(not d.startswith("plain") and flip[r]),
                    searched=bool(d.startswith("search") and searched[r]),
                    fix=best_fix[r] if d.startswith("search") else "none",
                    raw_ber=float(raw[r]), header_ok=bool(res["header_ok"][r]),
                    header_bits=int(res["header_bits"][r]),
                    id_ok=bool(res["id_ok"][r]), id_valid=bool(res["id_valid"][r]),
                    id_ber=float(res["id_ber"][r]), search_null=search_null))
    return rows, embeds


# ----------------------------------------------------------------- analysis
def _ci(per_image: pd.DataFrame, frames: int, seed: int):
    """Bootstrap over whole images -> (keys, BOOTSTRAP) percentages."""
    from .extended import _resample
    return _resample(per_image, frames, seed)


def _thresholds(df: pd.DataFrame, n_fixes: int, alpha: float = ALPHA) -> np.ndarray:
    keys = list(zip(df.n_header, df.decoder))
    t = {k: flag_threshold(k[0], k[1], n_fixes, alpha) for k in set(keys)}
    return np.array([t[k] for k in keys], dtype=float)


def analyze(cfg: ex.ExpConfig) -> None:
    out = cfg.path / "analysis"
    out.mkdir(exist_ok=True)
    res = pd.read_csv(cfg.path / "results.csv")
    emb = pd.read_csv(cfg.path / "embedding.csv")
    kind = {a.name: a.kind for a in attack_suite()}
    n_fixes = len(corrections(cfg))
    res["key"] = res.code + " " + res.decoder
    res["detected"] = res.agree.to_numpy() >= _thresholds(res, n_fixes)
    h1 = res[res.watermarked]
    attacked = h1[h1.attack != "none"]
    per_frame = attacked.attack.nunique()

    # exact ID recovery, header decoded, detection, per code and decoder
    rec = attacked.groupby(["code", "decoder"], sort=False).agg(
        design=("design", "first"), family=("family", "first"), n=("n", "first"),
        n_header=("n_header", "first"), id_ok=("id_ok", "mean"), header_ok=("header_ok", "mean"),
        detected=("detected", "mean"), searched=("searched", "mean"),
        flipped=("flipped", "mean")).reset_index()
    rec["key"] = rec.code + " " + rec.decoder
    per_image = attacked.pivot_table(index="key", columns="image", values="id_ok", aggfunc="sum")
    boot = _ci(per_image, per_frame, cfg.seed)
    keys = list(per_image.index)
    lo, hi = np.percentile(boot, [2.5, 97.5], axis=1)
    rec = rec.join(pd.DataFrame(dict(low=lo, high=hi), index=keys), on="key")
    for c in ("id_ok", "header_ok", "detected", "searched", "flipped"):
        rec[c] *= 100
    rec.loc[rec.n_header == 0, "detected"] = np.nan
    rec["threshold"] = [flag_threshold(h, d, n_fixes) if h else np.nan
                        for h, d in zip(rec.n_header, rec.decoder)]
    rec["clean"] = rec.key.map(h1[h1.attack == "none"].groupby("key").id_ok.sum())
    earlier = cfg.path.parent / "top10" / "analysis" / "ranking.csv"
    if earlier.exists():
        old = pd.read_csv(earlier).set_index("code").percent
        rec["full_message_run"] = rec.code.str.replace(r"_(split|joint)$", "", regex=True).map(old)
    rec = rec.sort_values(["decoder", "id_ok"], ascending=[True, False])
    rec.drop(columns="key").to_csv(out / "recovery.csv", index=False)

    # paired differences: each decoder against plain, and split against joint
    def diff(a, b):
        d = boot[keys.index(a)] - boot[keys.index(b)]
        lo, hi = np.percentile(d, [2.5, 97.5])
        return dict(difference=float(d.mean()), low=lo, high=hi, resolved=bool(lo > 0 or hi < 0))
    pairs = []
    for code in res.code.unique():
        for d in ("pilot", "search"):
            pairs.append(dict(a=f"{code} {d}", b=f"{code} plain") | diff(f"{code} {d}", f"{code} plain"))
    for fam in ("ldpc_r12", "polar_r12", "turbo_r12"):
        for d in DECODERS:
            a, b = f"{fam}_split {d}", f"{fam}_joint {d}"
            if a in keys and b in keys:
                pairs.append(dict(a=a, b=b) | diff(a, b))
    pairs = pd.DataFrame(pairs)
    pairs.to_csv(out / "pairs.csv", index=False)

    # unwatermarked frames, and wrong IDs on watermarked ones
    rows = []
    for (code, d), g in res[~res.watermarked].groupby(["code", "decoder"], sort=False):
        nh = int(g.n_header.iloc[0])
        loose = flag_threshold(nh, d, n_fixes, 1e-2)
        claimed = g.detected | g.header_ok
        rows.append(dict(code=code, decoder=d, frames=len(g), detected=int(g.detected.sum()),
                         over_1e2=int((g.agree >= loose).sum()), expected_1e2=round(len(g) * 1e-2, 1),
                         max_agree=int(g.agree.max()), n_header=nh,
                         header_decoded=int(g.header_ok.sum()), id_valid=int(g.id_valid.sum()),
                         false_id=int((claimed & g.id_valid).sum())))
    null = pd.DataFrame(rows)
    null.to_csv(out / "null.csv", index=False)
    wrong = (attacked.assign(wrong=attacked.header_ok & attacked.id_valid & ~attacked.id_ok)
             .pivot_table(index="code", columns="decoder", values="wrong", aggfunc="sum"))
    wrong.to_csv(out / "wrong_ids.csv")

    by_kind = (100 * attacked.assign(kind=attacked.attack.map(kind))
               .pivot_table(index="kind", columns=["decoder", "code"], values="id_ok", sort=False))
    by_kind.to_csv(out / "by_kind.csv")
    attacked.pivot_table(index="attack", columns=["decoder", "code"], values="id_ok",
                         aggfunc="sum", sort=False).to_csv(out / "by_attack.csv")
    fixes = (attacked[attacked.searched].groupby(["attack", "fix"]).size()
             .unstack(fill_value=0))
    fixes.to_csv(out / "fixes.csv")
    e = emb.groupby("code", sort=False).agg(
        n=("n", "first"), scale=("scale", "first"), wpsnr=("wpsnr", "mean"),
        wpsnr_low=("wpsnr", "min"), wpsnr_high=("wpsnr", "max"), psnr=("psnr", "mean"),
        searched=("searched", "mean"), seconds=("seconds", "mean")).reset_index()
    e.to_csv(out / "embedding.csv", index=False)

    with pd.option_context("display.width", 250, "display.max_rows", 300, "display.max_columns", 40):
        print(rec.drop(columns=["key", "family"]).round(2).to_string(index=False))
        print(pairs.round(2).to_string(index=False))
        print(null.to_string(index=False))
        print(wrong.to_string())
        print(by_kind.round(1).T.to_string())
        print(fixes.to_string())
        print(e.round(3).to_string(index=False))

COMPARED = ("uncoded", "ldpc_r12_split", "ldpc_r12_joint")


def compare(cfg: ex.ExpConfig, main_run: Path = Path("results/semiblind")) -> None:
    """ID | header joint LDPC (this run) against split and header | ID joint LDPC (the
    main run): same images, attacks, seeds and strength, so every frame is paired.

    flagged: the pilot count reaches the threshold of the decoder (split, jidh), or the
    header decodes to the header (header | ID joint, which sends no header bits).
    id_ok: the ID decoded exactly (for ``*_known``, only on flagged frames)."""
    out = cfg.path / "analysis"
    out.mkdir(exist_ok=True)
    old = pd.read_csv(main_run / "results.csv")
    df = pd.concat([old[old.code.isin(COMPARED)], pd.read_csv(cfg.path / "results.csv")],
                   ignore_index=True)
    n_fixes = len(corrections(cfg))
    df["flagged"] = np.where(df.n_header > 0, df.agree >= _thresholds(df, n_fixes), df.header_ok)
    df["key"] = df.code + " " + df.decoder
    h1 = df[df.watermarked & (df.attack != "none")]
    frames = h1.attack.nunique()
    keys = sorted(h1.key.unique())
    boot = {}
    rows = []
    for metric in ("flagged", "id_ok"):
        per_image = h1.pivot_table(index="key", columns="image", values=metric, aggfunc="sum").loc[keys]
        boot[metric] = _ci(per_image, frames, cfg.seed)
    for k, key in enumerate(keys):
        g = h1[h1.key == key]
        row = dict(code=g.code.iloc[0], decoder=g.decoder.iloc[0], design=g.design.iloc[0],
                   pilot_bits=int(g.n_header.iloc[0]))
        for metric in ("flagged", "id_ok"):
            lo, hi = np.percentile(boot[metric][k], [2.5, 97.5])
            row |= {metric: 100 * g[metric].mean(), f"{metric}_low": lo, f"{metric}_high": hi}
        rows.append(row)
    summary = pd.DataFrame(rows).sort_values(["decoder", "id_ok"], ascending=[True, False])
    summary.to_csv(out / "compare.csv", index=False)

    pairs = []
    for d in DECODERS:
        for a, b in ((f"ldpc_r12_jidh {d}_known", f"ldpc_r12_split {d}"),
                     (f"ldpc_r12_jidh {d}_known", f"ldpc_r12_joint {d}"),
                     (f"ldpc_r12_jidh {d}", f"ldpc_r12_split {d}"),
                     (f"ldpc_r12_jidh {d}_known", f"ldpc_r12_jidh {d}")):
            if a in keys and b in keys:
                for metric in ("flagged", "id_ok"):
                    diff = boot[metric][keys.index(a)] - boot[metric][keys.index(b)]
                    lo, hi = np.percentile(diff, [2.5, 97.5])
                    pairs.append(dict(a=a, b=b, metric=metric, difference=diff.mean(), low=lo,
                                      high=hi, resolved=bool(lo > 0 or hi < 0)))
    pairs = pd.DataFrame(pairs)
    pairs.to_csv(out / "compare_pairs.csv", index=False)

    kind = {a.name: a.kind for a in attack_suite()}
    sel = h1[h1.decoder.isin(["search", "search_known"])]
    by_kind = 100 * (sel.assign(kind=sel.attack.map(kind))
                     .pivot_table(index="kind", columns="key", values=["flagged", "id_ok"], sort=False))
    by_kind.to_csv(out / "compare_by_kind.csv")

    h0 = df[~df.watermarked]
    null = (h0.assign(false_id=h0.flagged & h0.id_valid & ~h0.id_ok)
            .groupby("key").agg(frames=("flagged", "size"), false_flags=("flagged", "sum"),
                                 max_agree=("agree", "max"), false_ids=("false_id", "sum"))
            .reset_index())
    null.to_csv(out / "compare_null.csv", index=False)
    wrong = h1.assign(wrong=h1.flagged & h1.id_valid & ~h1.id_ok).groupby("key").wrong.sum()
    wrong.to_csv(out / "compare_wrong_ids.csv")

    with pd.option_context("display.width", 250, "display.max_rows", 200, "display.max_columns", 40):
        print(f"{h1.image.nunique()} images, {frames} attacks")
        print(summary.round(2).to_string(index=False))
        print(pairs.round(2).to_string(index=False))
        print(by_kind.round(1).T.to_string())
        print(null.to_string(index=False))
        print(wrong.to_string())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["calibrate", "run", "analyze", "compare"])
    ap.add_argument("--config", default="configs/semiblind.yaml")
    args = ap.parse_args(argv)
    cfg = ex.ExpConfig.load(args.config)
    if not cfg.semi_blind:
        raise SystemExit("the config must set semi_blind: true")
    cfg.path.mkdir(parents=True, exist_ok=True)
    (cfg.path / "config.json").write_text(json.dumps(
        ex.asdict(cfg) | dict(header=np.packbits(cfg.message[0, :128]).tobytes().hex()), indent=1))
    t = time.time()
    print(f"== {args.stage}", flush=True)
    if args.stage == "calibrate":
        ex.stage_calibrate(cfg)
    elif args.stage == "run":
        # images that also search their unwatermarked frames take twice as long
        ex.stage_run(cfg, worker=_run_one, first=lambda i: i % cfg.search_null_every == 0)
    elif args.stage == "compare":
        compare(cfg)
    else:
        analyze(cfg)
    print(f"== {args.stage} done in {(time.time() - t) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
