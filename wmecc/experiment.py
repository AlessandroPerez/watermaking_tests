"""ECCs on top of invisible-watermark (``dwtDctSvd``) with blind extraction.

    python -m wmecc.experiment {calibrate,select,run,sweep,analyze,all} [--config FILE]

calibrate  per code: on each calibration image (all 100), find the strength whose
           wPSNR is closest to the target (40 dB); the mean of those values is
           the strength of its length: codes of equal length mark the same area,
           so their results are pooled into one strength, used on every image.
           The decoder knows it (a system parameter, like the code length)
select     pilot on 10 non-test images with the uncoded baseline: for each
           attack category pick the listed setting whose raw bit error rate is
           closest to ``select_target_ber`` (15 %: clearly damaging, while the
           channel still carries information); lossless PNG is excluded since
           it is identical to no attack
run        test images x codes x (no attack + selected attacks):
           embed -> attack -> blind extract -> decode (soft and hard variants);
           the same chain on the unwatermarked covers gives false positives
sweep      the run again at slightly different strengths (``strength_factors``), on
           ``sweep_images`` of the test images, watermarked frames only: the raw BER
           under JPEG-like attacks depends on the exact strength, on every image
analyze    tables, figures and the report data

One message, fixed by the seed, is used for every code, image and stage, so that
codes differ only in what they do to it.

The test images are part of the 100 calibration images (DIV2K-val has no more),
but each one is only 1 % of an average. Before embedding, every
codeword is XORed with a keyed pseudo-random sequence (whitening, standard
practice; the key is a system parameter like the strength). Without it an
unwatermarked image whose votes are all biased to 0 would decode as the valid
all-zero codeword of a linear code.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("TQDM_DISABLE", "1")   # komm decoders open progress bars on long calls

import argparse
import functools
import json
import shutil
import time
import zlib
from dataclasses import asdict, dataclass, replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import brentq

from .attacks import attack_suite, get_attacks
from .data import ROOT, cover_paths, load_rgb
from .metrics import nvf_map, psnr, ssim, wpsnr
from .watermark import imwm


@dataclass
class ExpConfig:
    run_dir: str = "results/imwm_svd"
    n_test: int = 10
    n_calib: int = 100
    n_pilot: int = 10
    target_wpsnr: float = 40.0
    select_target_ber: float = 0.15
    select_exclude: tuple = ("PNG",)   # lossless: identical to no attack
    votes_per_bit: int | None = None   # None = codes share all blocks; v = v blocks per coded bit
    attacks: dict | None = None      # {category: attack name} overrides the pilot selection
    codes: list | None = None        # None = every registered code
    code_modules: list | None = None  # restrict the code registry to these modules
    seed: int = 2026
    message_seed: int = 4
    workers: int = 6
    all_images: bool = False         # test on the first n_test covers, not on every tenth
    conditions: list | None = None   # explicit attack list, instead of the selection
    false_positives: bool = True     # also run the chain on the unwatermarked covers
    image_start: int = 0             # run test images image_start, +stride, +2 stride, ...
    image_stride: int = 1
    strength_factor: float = 1.0     # multiplies every calibrated strength
    strength_factors: list | None = None   # sweep stage: repeat the run at these factors
    sweep_images: int = 20
    semi_blind: bool = False         # message = fixed 128-bit header + 384-bit ID drawn per image
    search_gains: list | None = None    # semi-blind search: chroma gains tried (None = default grid)
    search_gammas: list | None = None   # semi-blind search: gammas tried (None = default grid)
    search_null_every: int = 10      # semi-blind search: also on the unwatermarked frames of every m-th image

    @classmethod
    def load(cls, path: str | None) -> "ExpConfig":
        if not path:
            return cls()
        with open(path) as f:
            return cls(**(yaml.safe_load(f) or {}))

    @property
    def path(self) -> Path:
        p = Path(self.run_dir)
        return p if p.is_absolute() else ROOT / p

    def test_images(self) -> list[Path]:
        return cover_paths()[:self.n_test] if self.all_images else cover_paths()[0::10][:self.n_test]

    def calib_images(self) -> list[Path]:
        return cover_paths()[:self.n_calib]

    def pilot_images(self) -> list[Path]:
        return cover_paths()[5::10][:self.n_pilot]

    @property
    def message(self) -> np.ndarray:
        """The one message of the experiment, shape (1, 512). Only embedding and
        scoring use it: the extractor and the decoders never see it."""
        return _rng(self.seed, self.message_seed).integers(0, 2, (1, 512), dtype=np.uint8)

    def message_for(self, image: str) -> np.ndarray:
        """The message embedded in one image, shape (1, 512): the one message, or in a
        semi-blind run its first 128 bits (the header, the same for every image)
        followed by 384 bits drawn for this image (the ID, the same for every code)."""
        if not self.semi_blind:
            return self.message
        ident = _rng(self.seed, self.message_seed, 7, zlib.crc32(Path(image).name.encode()))
        return np.concatenate([self.message[:, :128],
                               ident.integers(0, 2, (1, 384), dtype=np.uint8)], axis=1)


def _rng(*parts) -> np.random.Generator:
    return np.random.default_rng([int(p) & 0xFFFFFFFF for p in parts])


def whitening(cfg: "ExpConfig", n: int) -> np.ndarray:
    """Keyed pseudo-random bits XORed onto every length-n codeword."""
    return _rng(cfg.seed, 99, n).integers(0, 2, n, dtype=np.uint8)


def _init_worker():
    import cv2
    cv2.setNumThreads(1)
    try:
        import torch
        torch.set_num_threads(1)
    except ImportError:
        pass


def _embedding_codes(cfg: ExpConfig):
    """{embedding code name: (code, [decoder variants])}: decoder variants (*_hard,
    *_er) reuse the embedding of the code they wrap."""
    from .codes import MODULES
    return _code_groups(tuple(cfg.codes) if cfg.codes else None,
                        tuple(cfg.code_modules or MODULES))


@functools.lru_cache(maxsize=4)
def _code_groups(names, modules):
    # cached per worker process: building galois BCH/RS objects takes seconds
    from .codes import get_codes
    groups: dict = {}
    for c in get_codes(list(names) if names else None, modules=modules):
        base = getattr(c, "inner", c)
        groups.setdefault(base.name, (base, []))[1].append(c)
        c.decode(np.zeros((1, c.n)))      # warm-up: JIT compilation stays out of the timings
    return groups


# --------------------------------------------------------------- calibrate
def _calibrate_one(args):
    cfg, name, path = args
    _init_worker()
    code = _embedding_codes(cfg)[name][0]
    img = load_rgb(path)
    nvf = nvf_map(img)
    bits = code.encode(cfg.message_for(path.name))[0] ^ whitening(cfg, code.n)
    tried: dict = {}

    def gap(log_scale):
        s = float(np.exp(log_scale))
        tried[s] = wpsnr(img, imwm.embed(img, bits, s, cfg.seed, cfg.votes_per_bit), nvf=nvf) - cfg.target_wpsnr
        return tried[s]

    # wPSNR falls with strength, but not smoothly (quantisation steps, uint8
    # wrap-around in the library), so keep the closest value actually measured
    for lo, hi in ((15.0, 200.0), (1.0, 1000.0)):
        try:
            brentq(gap, np.log(lo), np.log(hi), xtol=5e-3)
            break
        except ValueError:      # 40 dB is not inside this bracket for this image
            continue
    best = min(tried, key=lambda s: abs(tried[s]))
    return dict(code=name, n=code.n, image=path.name, strength=best,
                wpsnr=tried[best] + cfg.target_wpsnr, evaluations=len(tried))


def _strengths(df: pd.DataFrame, cfg: ExpConfig, groups: dict) -> dict:
    """One strength per length, from the searches of every code of that length.

    Strengths that differ only by search noise would not be harmless: under blur +
    JPEG the raw BER can change several times over for a change of 0.25 in strength,
    which would decide between codes of equal length.
    """
    scale = df.groupby("n").strength.mean()
    res = {n: dict(scale=float(scale[g.n.iloc[0]]), code_scale=float(g.strength.mean()),
                   scale_sd=float(g.strength.std()), n=int(g.n.iloc[0]), k=groups[n][0].k,
                   images=len(g), wpsnr_miss=float((g.wpsnr - cfg.target_wpsnr).abs().max()))
           for n, g in df.groupby("code", sort=False)}
    return {n: res[n] for n in groups}


def stage_calibrate(cfg: ExpConfig):
    groups = _embedding_codes(cfg)
    log = cfg.path / "strengths.csv"          # one row per code and image, resumable
    done = pd.read_csv(log) if log.exists() else pd.DataFrame(columns=["code", "image"])
    seen = set(zip(done.code, done.image))
    jobs = [(cfg, n, p) for n in groups for p in cfg.calib_images()
            if (n, p.name) not in seen]
    print(f"  {len(jobs)} strength searches to do", flush=True)
    with Pool(cfg.workers, initializer=_init_worker) as pool:
        for k, r in enumerate(pool.imap_unordered(_calibrate_one, jobs), 1):
            pd.DataFrame([r]).to_csv(log, mode="a", header=not log.exists(), index=False)
            if k % 100 == 0:
                print(f"  {k}/{len(jobs)}", flush=True)
    res = _strengths(pd.read_csv(log), cfg, groups)
    (cfg.path / "calibration.json").write_text(json.dumps(res, indent=1))
    print(pd.DataFrame(res).T.to_string())


# ------------------------------------------------------------------ select
def _pilot_one(args):
    cfg, i, path, scale = args
    _init_worker()
    img = load_rgb(path)
    bits = cfg.message[0]
    wm = imwm.embed(img, bits, scale, cfg.seed, cfg.votes_per_bit)
    rows = []
    for j, a in enumerate(attack_suite()):
        x = a(wm, seed=int(_rng(cfg.seed, 3, i, j).integers(2**31)))
        ones, count = imwm.extract(x, 512, scale, cfg.seed, cfg.votes_per_bit)
        llr = imwm.votes_to_llr(ones, count)
        rows.append(dict(image=path.name, attack=a.name, category=a.family, kind=a.kind,
                         raw_ber=float(np.mean((llr < 0) != bits)),
                         separation=imwm.separation(ones, count)))
    return rows


def stage_select(cfg: ExpConfig):
    cal = json.loads((cfg.path / "calibration.json").read_text())
    scale = cal["uncoded"]["scale"]
    rows = []
    with Pool(cfg.workers, initializer=_init_worker) as pool:
        for r in pool.imap_unordered(_pilot_one, [(cfg, i, p, scale) for i, p in
                                                  enumerate(cfg.pilot_images())]):
            rows += r
    pilot = pd.DataFrame(rows).groupby(["category", "kind", "attack"], sort=False).agg(
        raw_ber=("raw_ber", "mean"), raw_ber_sd=("raw_ber", "std"),
        separation=("separation", "mean")).reset_index()
    pilot["dist"] = (pilot.raw_ber - cfg.select_target_ber).abs()
    pilot.to_csv(cfg.path / "pilot.csv", index=False)
    chosen = {}
    cand = pilot[(pilot.category != "None") & ~pilot.kind.isin(cfg.select_exclude)]
    for cat, g in cand.groupby("category", sort=False):
        chosen[cat] = g.sort_values(["dist", "raw_ber"]).iloc[0].attack
    if cfg.attacks:
        chosen.update(cfg.attacks)
    (cfg.path / "selection.json").write_text(json.dumps(chosen, indent=1))
    with pd.option_context("display.width", 160, "display.max_rows", 200):
        print(pilot.round(4).to_string(index=False))
    print("\nselected:", json.dumps(chosen, indent=1))


# --------------------------------------------------------------------- run
def _run_one(args):
    cfg, i, path, conditions, cal = args
    _init_worker()
    from .codes.base import hard
    img = load_rgb(path)
    nvf = nvf_map(img)
    attacks = get_attacks(conditions)
    seeds = [int(_rng(cfg.seed, 5, i, j).integers(2**31)) for j in range(len(attacks))]
    frames = (True, False) if cfg.false_positives else (True,)    # watermarked?
    attacked0 = [a(img, seed=s) for a, s in zip(attacks, seeds)] if cfg.false_positives else None
    rows, embeds = [], []
    for name, (code, variants) in _embedding_codes(cfg).items():
        scale = cal[name]["scale"] * cfg.strength_factor
        msg = cfg.message
        cw = code.encode(msg)[0]
        key = whitening(cfg, code.n)
        wm = imwm.embed(img, cw ^ key, scale, cfg.seed, cfg.votes_per_bit)
        embeds.append(dict(image=path.name, code=name, n=code.n, scale=scale,
                           wpsnr=wpsnr(img, wm, nvf=nvf), psnr=psnr(img, wm), ssim=ssim(img, wm)))
        llrs, rel = [], []
        for j, a in enumerate(attacks):
            for marked in frames:
                x = a(wm, seed=seeds[j]) if marked else attacked0[j]
                ones, count = imwm.extract(x, code.n, scale, cfg.seed, cfg.votes_per_bit)
                llrs.append(imwm.votes_to_llr(ones, count) * (1.0 - 2.0 * key))
                rel.append(imwm.separation(ones, count))
        L = np.stack(llrs)                                   # (fA, n): H1, H0 interleaved
        raw = np.mean(hard(L) != cw[None, :], axis=1)
        for v in variants:
            t = time.perf_counter()
            res = v.decode(L)
            ms = 1e3 * (time.perf_counter() - t) / len(L)
            for r in range(len(L)):
                j, f = divmod(r, len(frames))
                rows.append(dict(image=path.name, code=v.name, base=name, family=v.family,
                                 n=v.n, rate=v.k / v.n, soft=v.soft, has_check=v.has_check,
                                 attack=attacks[j].name, category=attacks[j].family,
                                 watermarked=frames[f], raw_ber=float(raw[r]),
                                 separation=rel[r],
                                 success=bool(np.array_equal(res.msg[r], msg[0])),
                                 msg_ber=float(np.mean(res.msg[r] != msg[0])),
                                 valid=bool(res.valid[r]), decode_ms=ms))
    return rows, embeds


def stage_run(cfg: ExpConfig, worker=None, first=None):
    """``worker`` runs one image (default ``_run_one``; the semi-blind run has its own).
    ``first(i)`` true for image ``i`` starts it before the others: give the slowest
    images to the workers first, so that none of them is left running alone at the end."""
    cal = json.loads((cfg.path / "calibration.json").read_text())
    conditions = cfg.conditions
    if not conditions:
        conditions = ["none"] + list(json.loads((cfg.path / "selection.json").read_text()).values())
    jobs = [(cfg, i, p, conditions, cal) for i, p in enumerate(cfg.test_images())]
    jobs = jobs[cfg.image_start::cfg.image_stride]
    parts = cfg.path / "parts"          # one pair of files per finished image, resumable
    parts.mkdir(exist_ok=True)
    todo = [j for j in jobs if not (parts / f"{j[2].stem}.embedding.csv").exists()]
    if first is not None:
        todo.sort(key=lambda j: not first(j[1]))
    print(f"  {len(jobs) - len(todo)} of {len(jobs)} images already done", flush=True)
    with Pool(cfg.workers, initializer=_init_worker) as pool:
        for k, (r, e) in enumerate(pool.imap_unordered(worker or _run_one, todo), 1):
            stem = Path(e[0]["image"]).stem
            pd.DataFrame(r).to_csv(parts / f"{stem}.results.csv", index=False)
            pd.DataFrame(e).to_csv(parts / f"{stem}.embedding.csv", index=False)
            print(f"  {k}/{len(todo)} images", flush=True)
    stems = [j[2].stem for j in jobs]
    pd.concat(pd.read_csv(parts / f"{s}.results.csv") for s in stems).to_csv(
        cfg.path / "results.csv", index=False)
    emb = pd.concat(pd.read_csv(parts / f"{s}.embedding.csv") for s in stems)
    emb.to_csv(cfg.path / "embedding.csv", index=False)
    shutil.rmtree(parts)
    print(emb.groupby("code")[["scale", "wpsnr", "psnr", "ssim"]].mean().round(3).to_string())


def sweep_runs(cfg: ExpConfig) -> list[ExpConfig]:
    """One sub-run per factor, in its own folder. Same images, same attack seeds.

    Starting half a stride in keeps away from covers 0, 5, 10, ..., the test and pilot
    images of the earlier runs, which helped to choose the codes and the attacks.
    """
    stride = len(cfg.test_images()) // cfg.sweep_images
    return [replace(cfg, run_dir=str(cfg.path / f"strength_{f}"), strength_factor=f,
                    false_positives=False, image_start=stride // 2, image_stride=stride,
                    strength_factors=None)
            for f in cfg.strength_factors or []]


def stage_sweep(cfg: ExpConfig):
    for sub in sweep_runs(cfg):
        print(f"  strength x {sub.strength_factor}", flush=True)
        sub.path.mkdir(exist_ok=True)
        shutil.copy(cfg.path / "calibration.json", sub.path)
        stage_run(sub)


# -------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["calibrate", "select", "run", "sweep", "analyze", "all"])
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    cfg = ExpConfig.load(args.config)
    cfg.path.mkdir(parents=True, exist_ok=True)
    message = np.packbits(cfg.message).tobytes().hex()
    (cfg.path / "config.json").write_text(json.dumps(asdict(cfg) | dict(message=message), indent=1))
    stages = ["calibrate", "select", "run", "sweep", "analyze"] if args.stage == "all" else [args.stage]
    for s in stages:
        t = time.time()
        print(f"== {s}", flush=True)
        if s == "analyze":
            from .analysis import analyze
            analyze(cfg)
        else:
            globals()[f"stage_{s}"](cfg)
        print(f"== {s} done in {(time.time() - t) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
