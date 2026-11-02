"""ECCs on top of invisible-watermark (``dwtDctSvd``) with blind extraction.

    python -m wmecc.experiment {calibrate,select,run,analyze,all} [--config FILE]

calibrate  per code: on each calibration image (all 100), find the strength whose
           wPSNR is closest to the target (40 dB); the mean of those values is
           the code's one strength for every image. The decoder knows it (a
           system parameter, like the code length)
select     pilot on 10 non-test images with the uncoded baseline: for each
           attack category pick the listed setting whose raw bit error rate is
           closest to ``select_target_ber`` (15 %: clearly damaging, while the
           channel still carries information); lossless PNG is excluded since
           it is identical to no attack
run        test images x codes x (no attack + selected attacks):
           embed -> attack -> blind extract -> decode (soft and hard variants);
           the same chain on the unwatermarked covers gives false positives
analyze    tables, figures and the report data

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
import time
import zlib
from dataclasses import asdict, dataclass
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
    workers: int = 6

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
        return cover_paths()[0::10][:self.n_test]

    def calib_images(self) -> list[Path]:
        return cover_paths()[:self.n_calib]

    def pilot_images(self) -> list[Path]:
        return cover_paths()[5::10][:self.n_pilot]


def _rng(*parts) -> np.random.Generator:
    return np.random.default_rng([int(p) & 0xFFFFFFFF for p in parts])


def whitening(cfg: "ExpConfig", n: int) -> np.ndarray:
    """Keyed pseudo-random bits XORed onto every length-n codeword."""
    return _rng(cfg.seed, 99, n).integers(0, 2, n, dtype=np.uint8)


def _h(s: str) -> int:
    return zlib.crc32(s.encode())


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
    cfg, name, i, path = args
    _init_worker()
    code = _embedding_codes(cfg)[name][0]
    img, rng = load_rgb(path), _rng(cfg.seed, 1, _h(name), i)
    nvf = nvf_map(img)
    bits = code.encode(rng.integers(0, 2, (1, code.k), dtype=np.uint8))[0] ^ whitening(cfg, code.n)
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


def stage_calibrate(cfg: ExpConfig):
    groups = _embedding_codes(cfg)
    log = cfg.path / "strengths.csv"          # one row per code and image, resumable
    done = pd.read_csv(log) if log.exists() else pd.DataFrame(columns=["code", "image"])
    seen = set(zip(done.code, done.image))
    jobs = [(cfg, n, i, p) for n in groups for i, p in enumerate(cfg.calib_images())
            if (n, p.name) not in seen]
    print(f"  {len(jobs)} strength searches to do", flush=True)
    with Pool(cfg.workers, initializer=_init_worker) as pool:
        for k, r in enumerate(pool.imap_unordered(_calibrate_one, jobs), 1):
            pd.DataFrame([r]).to_csv(log, mode="a", header=not log.exists(), index=False)
            if k % 100 == 0:
                print(f"  {k}/{len(jobs)}", flush=True)
    df = pd.read_csv(log)
    res = {n: dict(scale=float(g.strength.mean()), scale_sd=float(g.strength.std()),
                   n=int(g.n.iloc[0]), k=groups[n][0].k, images=len(g),
                   wpsnr_miss=float((g.wpsnr - cfg.target_wpsnr).abs().max()))
           for n, g in df.groupby("code", sort=False)}
    res = {n: res[n] for n in groups}
    (cfg.path / "calibration.json").write_text(json.dumps(res, indent=1))
    print(pd.DataFrame(res).T.to_string())


# ------------------------------------------------------------------ select
def _pilot_one(args):
    cfg, i, path, scale = args
    _init_worker()
    img = load_rgb(path)
    bits = _rng(cfg.seed, 2, i).integers(0, 2, 512, dtype=np.uint8)
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
    attacked0 = [a(img, seed=int(_rng(cfg.seed, 5, i, j).integers(2**31))) for j, a in enumerate(attacks)]
    rows, embeds = [], []
    for name, (code, variants) in _embedding_codes(cfg).items():
        scale = cal[name]["scale"]
        msg = _rng(cfg.seed, 4, i, _h(name)).integers(0, 2, (1, code.k), dtype=np.uint8)
        cw = code.encode(msg)[0]
        key = whitening(cfg, code.n)
        wm = imwm.embed(img, cw ^ key, scale, cfg.seed, cfg.votes_per_bit)
        embeds.append(dict(image=path.name, code=name, n=code.n, scale=scale,
                           wpsnr=wpsnr(img, wm, nvf=nvf), psnr=psnr(img, wm), ssim=ssim(img, wm)))
        llrs, rel = [], []
        for j, a in enumerate(attacks):
            for h, src in ((1, None), (0, attacked0[j])):
                x = a(wm, seed=int(_rng(cfg.seed, 5, i, j).integers(2**31))) if h else src
                ones, count = imwm.extract(x, code.n, scale, cfg.seed, cfg.votes_per_bit)
                llrs.append(imwm.votes_to_llr(ones, count) * (1.0 - 2.0 * key))
                rel.append(imwm.separation(ones, count))
        L = np.stack(llrs)                                   # (2A, n): H1, H0 interleaved
        raw = np.mean(hard(L) != cw[None, :], axis=1)
        for v in variants:
            t = time.perf_counter()
            res = v.decode(L)
            ms = 1e3 * (time.perf_counter() - t) / len(L)
            for r in range(len(L)):
                j, h = divmod(r, 2)
                rows.append(dict(image=path.name, code=v.name, base=name, family=v.family,
                                 n=v.n, rate=v.k / v.n, soft=v.soft, has_check=v.has_check,
                                 attack=attacks[j].name, category=attacks[j].family,
                                 watermarked=bool(1 - h), raw_ber=float(raw[r]),
                                 separation=rel[r],
                                 success=bool(np.array_equal(res.msg[r], msg[0])),
                                 msg_ber=float(np.mean(res.msg[r] != msg[0])),
                                 valid=bool(res.valid[r]), decode_ms=ms))
    return rows, embeds


def stage_run(cfg: ExpConfig):
    cal = json.loads((cfg.path / "calibration.json").read_text())
    sel = json.loads((cfg.path / "selection.json").read_text())
    conditions = ["none"] + list(sel.values())
    rows, embeds = [], []
    jobs = [(cfg, i, p, conditions, cal) for i, p in enumerate(cfg.test_images())]
    with Pool(cfg.workers, initializer=_init_worker) as pool:
        for k, (r, e) in enumerate(pool.imap_unordered(_run_one, jobs), 1):
            rows += r
            embeds += e
            print(f"  {k}/{len(jobs)} images", flush=True)
    pd.DataFrame(rows).to_csv(cfg.path / "results.csv", index=False)
    emb = pd.DataFrame(embeds)
    emb.to_csv(cfg.path / "embedding.csv", index=False)
    print(emb.groupby("code")[["scale", "wpsnr", "psnr", "ssim"]].mean().round(3).to_string())


# -------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["calibrate", "select", "run", "analyze", "all"])
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    cfg = ExpConfig.load(args.config)
    cfg.path.mkdir(parents=True, exist_ok=True)
    (cfg.path / "config.json").write_text(json.dumps(asdict(cfg), indent=1))
    stages = ["calibrate", "select", "run", "analyze"] if args.stage == "all" else [args.stage]
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
