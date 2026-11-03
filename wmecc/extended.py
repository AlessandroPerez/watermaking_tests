"""Analysis of the extended test of the best codes (``configs/top10.yaml``).

    python -m wmecc.extended --config configs/top10.yaml

Writes, under ``<run_dir>/analysis``:
  ranking.csv        recovery on every attacked frame, with a 95 % interval, on all
                     images and on the images that did not choose the codes or attacks
  pairs.csv          every difference between two codes, with a 95 % interval
  by_kind.csv        recovery per code and kind of attack (JPEG, WebP, ...)
  by_attack.csv      recoveries per code and attack, out of the number of images
  reference.csv      the moderate and hard attack sets of the first experiment
  checks.csv         passes, wrong passes and false passes of the codes with a check
  presence.csv       detection by the code-independent separation statistic
  embedding.csv      strength and wPSNR per code
  strength.csv       recovery per code at each strength of the sweep
  strength_attacks.csv   the same per attack, where the sweep moved recovery most

The frames of one image are not independent: an image that is hard for one attack
tends to be hard for the others, for every code. So intervals come from resampling
whole images, and code pairs from resampling the same images for both codes.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from .attacks import attack_suite
from .data import ROOT
from .experiment import ExpConfig, sweep_runs

BOOTSTRAP = 10_000
REFERENCE = dict(moderate="configs/imwm_fixed_moderate.yaml", hard="configs/imwm_fixed.yaml")


def _resample(totals: pd.DataFrame, frames_per_image: int, seed: int) -> np.ndarray:
    """(codes, images) recoveries -> (codes, BOOTSTRAP) percentages on resampled images."""
    images = totals.shape[1]
    picks = np.random.default_rng(seed).integers(0, images, (BOOTSTRAP, images))
    return 100.0 * totals.values[:, picks].sum(axis=2) / (images * frames_per_image)


def _per_image(attacked: pd.DataFrame, order) -> pd.DataFrame:
    return attacked.pivot_table(index="code", columns="image", values="success",
                                aggfunc="sum").loc[order]


def ranking(attacked: pd.DataFrame, fresh: list[str], seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """-> (one row per code, best first; every pair of codes)."""
    t = attacked.groupby("code", sort=False).agg(
        family=("family", "first"), n=("n", "first"), rate=("rate", "first"),
        recovered=("success", "sum"), frames=("success", "size"), percent=("success", "mean"),
        msg_ber=("msg_ber", "mean"), raw_ber=("raw_ber", "mean"))
    t["percent"] *= 100
    t = t.sort_values(["percent", "n"], ascending=[False, True])
    order = list(t.index)
    per_frame = attacked.attack.nunique()

    boot = _resample(_per_image(attacked, order), per_frame, seed)
    t["low"], t["high"] = np.percentile(boot, [2.5, 97.5], axis=1)
    held_out = attacked[attacked.image.isin(fresh)]
    t["percent_fresh"] = 100 * held_out.groupby("code").success.mean()
    fresh_boot = _resample(_per_image(held_out, order), per_frame, seed)
    t["low_fresh"], t["high_fresh"] = np.percentile(fresh_boot, [2.5, 97.5], axis=1)
    categories = 100 * attacked.pivot_table(index="code", columns="category", values="success")
    t = t.join(categories.add_prefix("cat_"))

    rows = []
    for i, a in enumerate(order):
        for j, b in enumerate(order):
            if i < j:
                d, df = boot[i] - boot[j], fresh_boot[i] - fresh_boot[j]
                lo, hi = np.percentile(d, [2.5, 97.5])
                flo, fhi = np.percentile(df, [2.5, 97.5])
                rows.append(dict(code=a, against=b, difference=t.percent[a] - t.percent[b],
                                 low=lo, high=hi, resolved=bool(lo > 0 or hi < 0),
                                 difference_fresh=t.percent_fresh[a] - t.percent_fresh[b],
                                 low_fresh=flo, high_fresh=fhi,
                                 resolved_fresh=bool(flo > 0 or fhi < 0)))
    return t.reset_index(), pd.DataFrame(rows)


def checks(res: pd.DataFrame) -> pd.DataFrame:
    """Only codes with a check can say "this is the message": a pass is that claim."""
    rows = []
    for code, g in res[res.has_check].groupby("code", sort=False):
        h1, h0 = g[g.watermarked], g[~g.watermarked]
        wrong = int((h1.valid & ~h1.success).sum())
        false = int(h0.valid.sum())
        ci = binomtest(false, len(h0)).proportion_ci(method="exact") if len(h0) else None
        wrong_ci = binomtest(wrong, max(int(h1.valid.sum()), 1)).proportion_ci(method="exact")
        rows.append(dict(code=code, frames=len(h1), passed=int(h1.valid.sum()), wrong_passes=wrong,
                         wrong_pass_upper=wrong_ci.high, null_frames=len(h0), false_passes=false,
                         false_pass_upper=ci.high if ci else np.nan))
    return pd.DataFrame(rows)


def presence(res: pd.DataFrame) -> pd.DataFrame:
    """Separation above the highest value on any unwatermarked frame of that code."""
    rows = []
    for code, g in res.groupby("code", sort=False):
        h1, h0 = g[g.watermarked & (g.attack != "none")], g[~g.watermarked]
        threshold = float(h0.separation.max())
        rows.append(dict(code=code, threshold=threshold,
                         detected=float((h1.separation > threshold).mean()),
                         recovered=float(h1.success.mean())))
    return pd.DataFrame(rows)


def strength_sweep(attacked: pd.DataFrame, cfg: ExpConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recovery at each factor on the sweep images, paired with the main run at 1.0."""
    runs = {}
    for sub in sweep_runs(cfg):
        path = sub.path / "results.csv"
        if path.exists():
            r = pd.read_csv(path)
            runs[sub.strength_factor] = r[r.watermarked & (r.attack != "none")]
    if not runs:
        return pd.DataFrame(), pd.DataFrame()
    images = next(iter(runs.values())).image.unique()
    runs[1.0] = attacked[attacked.image.isin(images)]
    long = pd.concat(r.assign(factor=f) for f, r in sorted(runs.items()))
    table = 100 * long.pivot_table(index="code", columns="factor", values="success")
    spread = table.max(axis=1) - table.min(axis=1)
    table.columns = [f"x{c:g}" for c in table.columns]
    table.insert(0, "mean", table.mean(axis=1))
    table["spread"] = spread
    table = table.sort_values("mean", ascending=False).reset_index()
    per_attack = (long.groupby(["attack", "code", "factor"]).success.sum().unstack("factor")
                  .assign(spread=lambda d: d.max(axis=1) - d.min(axis=1))
                  .sort_values("spread", ascending=False).reset_index())
    return table, per_attack


def analyze(cfg: ExpConfig) -> None:
    out = cfg.path / "analysis"
    out.mkdir(exist_ok=True)
    res = pd.read_csv(cfg.path / "results.csv")
    emb = pd.read_csv(cfg.path / "embedding.csv")
    kind = {a.name: a.kind for a in attack_suite()}
    # covers 0, 5, 10, ... were the test and pilot images of the earlier runs
    fresh = [p.name for i, p in enumerate(cfg.test_images()) if i % 5]

    h1 = res[res.watermarked]
    attacked = h1[h1.attack != "none"]
    rank, pairs = ranking(attacked, fresh, cfg.seed)
    order = list(rank.code)
    # decoder variants have no embedding of their own
    rank["strength"] = rank.code.map(res.groupby("code").base.first()).map(
        emb.groupby("code").scale.first())
    rank["clean"] = rank.code.map(h1[h1.attack == "none"].groupby("code").success.sum())
    rank.to_csv(out / "ranking.csv", index=False)
    pairs.to_csv(out / "pairs.csv", index=False)

    by_attack = attacked.pivot_table(index="attack", columns="code", values="success",
                                     aggfunc="sum", sort=False)[order]
    by_attack.to_csv(out / "by_attack.csv")
    by_kind = (100 * attacked.assign(kind=attacked.attack.map(kind))
               .pivot_table(index="kind", columns="code", values="success", sort=False))[order]
    by_kind.to_csv(out / "by_kind.csv")

    rows = []
    for name, path in REFERENCE.items():
        chosen = list(ExpConfig.load(ROOT / path).attacks.values())
        cut = attacked[attacked.attack.isin(chosen)]
        for code in order:
            c = cut[cut.code == code]
            rows.append(dict(set=name, code=code, recovered=int(c.success.sum()), frames=len(c),
                             recovered_fresh=int(c[c.image.isin(fresh)].success.sum()),
                             frames_fresh=int(c.image.isin(fresh).sum())))
    reference = pd.DataFrame(rows)
    reference.to_csv(out / "reference.csv", index=False)

    check, pres = checks(res), presence(res)
    check.to_csv(out / "checks.csv", index=False)
    pres.to_csv(out / "presence.csv", index=False)
    e = emb.groupby("code", sort=False).agg(
        n=("n", "first"), scale=("scale", "first"), wpsnr=("wpsnr", "mean"), low=("wpsnr", "min"),
        high=("wpsnr", "max"), psnr=("psnr", "mean"), ssim=("ssim", "mean")).reset_index()
    e.to_csv(out / "embedding.csv", index=False)

    sweep, per_attack = strength_sweep(attacked, cfg)
    if len(sweep):
        sweep.to_csv(out / "strength.csv", index=False)
        per_attack.to_csv(out / "strength_attacks.csv", index=False)

    (out / "summary.json").write_text(json.dumps(dict(
        images=int(res.image.nunique()), fresh_images=len(fresh), attacks=int(attacked.attack.nunique()),
        frames_per_code=int(attacked.groupby("code").size().max())), indent=1))

    with pd.option_context("display.width", 240, "display.max_rows", 200, "display.max_columns", 60):
        print(rank.drop(columns=["family", "frames"]).round(2).to_string(index=False))
        print("\npairs that are resolved:")
        print(pairs[pairs.resolved].round(2).to_string(index=False))
        print(reference.pivot(index="code", columns="set", values="recovered").loc[order].to_string())
        print(by_kind.round(1).to_string())
        print(check.to_string(index=False))
        print(pres.round(3).to_string(index=False))
        print(e.round(3).to_string(index=False))
        if len(sweep):
            print(sweep.round(2).to_string(index=False))
            print(per_attack.head(20).to_string(index=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/top10.yaml")
    analyze(ExpConfig.load(ap.parse_args(argv).config))


if __name__ == "__main__":
    main()
