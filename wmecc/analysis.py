"""Tables, figures and report data for the invisible-watermark ECC experiment.

Outputs (under ``<run_dir>/analysis``):
  per_code_attack.csv   successes / 10, message BER, raw coded BER, valid rate
  per_code.csv          totals per code, false-valid rate on unwatermarked images
  embedding.csv         strength and wPSNR / PSNR / SSIM per code
  presence.csv          separation statistic, watermarked vs unwatermarked
  fig_success.png       successes per code and attack
  examples/             original / watermarked / amplified difference crops
  report_data.json      everything the HTML report needs
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .watermark import imwm

FAMILY_ORDER = ["Uncoded", "Repetition", "Hamming", "BCH", "RS",
                "Convolutional", "LDPC", "Polar", "Turbo"]
SEQ = ["#f0efec", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


def wilson(k, n, z=1.96):
    k, n = np.asarray(k, float), np.asarray(n, float)
    p = k / np.maximum(n, 1)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return np.clip(c - h, 0, 1), np.clip(c + h, 0, 1)


def _family_rank(f: str) -> int:
    return FAMILY_ORDER.index(f) if f in FAMILY_ORDER else len(FAMILY_ORDER)


def analyze(cfg):
    run = cfg.path
    out = run / "analysis"
    out.mkdir(exist_ok=True)
    res = pd.read_csv(run / "results.csv")
    emb = pd.read_csv(run / "embedding.csv")
    sel = json.loads((run / "selection.json").read_text())
    cal = json.loads((run / "calibration.json").read_text())
    pilot = pd.read_csv(run / "pilot.csv")
    conditions = ["none"] + list(sel.values())
    cat_of = {v: k for k, v in sel.items()} | {"none": "No attack (control)"}

    h1, h0 = res[res.watermarked], res[~res.watermarked]
    pca = (h1.groupby(["code", "attack"], sort=False)
           .agg(family=("family", "first"), n=("n", "first"), soft=("soft", "first"),
                has_check=("has_check", "first"), trials=("success", "size"),
                successes=("success", "sum"), msg_ber=("msg_ber", "mean"),
                raw_ber=("raw_ber", "mean"), valid=("valid", "mean"))
           .reset_index())
    lo, hi = wilson(pca.successes, pca.trials)
    pca["success_lo"], pca["success_hi"] = lo, hi
    pca["category"] = pca.attack.map(cat_of)
    pca.loc[~pca.has_check, "valid"] = np.nan
    pca.to_csv(out / "per_code_attack.csv", index=False)

    attacked = h1[h1.attack != "none"]
    pc = (h1.groupby("code", sort=False)
          .agg(family=("family", "first"), base=("base", "first"), n=("n", "first"),
               rate=("rate", "first"), soft=("soft", "first"), has_check=("has_check", "first"),
               decode_ms=("decode_ms", "mean"))
          .reset_index())
    pc["clean_successes"] = pc.code.map(h1[h1.attack == "none"].groupby("code").success.sum())
    pc["attack_successes"] = pc.code.map(attacked.groupby("code").success.sum())
    pc["attack_trials"] = pc.code.map(attacked.groupby("code").success.size())
    pc["attack_msg_ber"] = pc.code.map(attacked.groupby("code").msg_ber.mean())
    pc["attack_raw_ber"] = pc.code.map(attacked.groupby("code").raw_ber.mean())
    pc["false_valid"] = pc.code.map(h0.groupby("code").valid.mean())
    pc["null_trials"] = pc.code.map(h0.groupby("code").valid.size())
    pc.loc[~pc.has_check, "false_valid"] = np.nan
    pc["scale"] = pc.base.map(lambda b: cal[b]["scale"])
    pc["votes"] = cfg.votes_per_bit or imwm.BLOCKS / pc.n
    pc["marked"] = pc.votes * pc.n / imwm.BLOCKS
    pc["rank"] = pc.family.map(_family_rank)
    pc = pc.sort_values(["rank", "rate", "soft"], ascending=[True, False, False]).drop(columns="rank")
    pc.to_csv(out / "per_code.csv", index=False)

    e = (emb.groupby("code", sort=False)
         .agg(n=("n", "first"), scale=("scale", "first"), wpsnr_mean=("wpsnr", "mean"),
              wpsnr_sd=("wpsnr", "std"), psnr_mean=("psnr", "mean"), ssim_mean=("ssim", "mean"))
         .reset_index())
    e.to_csv(out / "embedding.csv", index=False)

    # code-independent presence statistic: mixture separation, all codes pooled
    pres = (res.groupby(["attack", "watermarked"]).separation
            .agg(["mean", "min", "max"]).unstack("watermarked"))
    pres.columns = [f"{s}_{'wm' if w else 'clean'}" for s, w in pres.columns]
    thr = float(h0.separation.max())
    pres["detected_frac"] = h1.groupby("attack").separation.apply(lambda s: float(np.mean(s > thr)))
    pres = pres.reindex(conditions)
    pres.to_csv(out / "presence.csv")

    data = dict(
        config=json.loads((run / "config.json").read_text()),
        selection=sel, conditions=conditions, categories=[cat_of[c] for c in conditions],
        pilot=pilot.round(4).to_dict(orient="records"),
        codes=pc.replace({np.nan: None}).to_dict(orient="records"),
        cells=pca.replace({np.nan: None}).round(5).to_dict(orient="records"),
        embedding=e.round(4).to_dict(orient="records"),
        presence=dict(threshold=thr, rows=pres.reset_index().round(4).replace({np.nan: None})
                      .to_dict(orient="records")),
    )
    (out / "report_data.json").write_text(json.dumps(data, default=float))
    try:
        figures(pca, pc, conditions, cat_of, out)
        examples(run, cfg, emb, out)
    except Exception as ex:   # figures are a convenience; never lose the tables
        print("figure generation failed:", ex)

    with pd.option_context("display.width", 220, "display.max_rows", 200):
        M = pca.pivot(index="code", columns="attack", values="successes").loc[pc.code, conditions]
        M.columns = [f"{c}" for c in conditions]
        print(M.to_string())
        print()
        print(pc[["code", "n", "scale", "votes", "marked", "clean_successes", "attack_successes",
                  "attack_raw_ber", "attack_msg_ber", "false_valid", "decode_ms"]]
              .round(4).to_string(index=False))
        print()
        print(e.round(3).to_string(index=False))
        print()
        print(pres.round(2).to_string())


def figures(pca, pc, conditions, cat_of, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm

    plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "axes.edgecolor": BASE,
                         "xtick.color": INK2, "ytick.color": INK2,
                         "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
    order = list(pc.code)
    M = pca.pivot(index="code", columns="attack", values="successes").loc[order, conditions]
    trials = int(pca.trials.max())
    cmap = ListedColormap(SEQ)
    norm = BoundaryNorm(np.linspace(-0.5, trials + 0.5, len(SEQ) + 1), len(SEQ))
    fig, ax = plt.subplots(figsize=(7.5, 0.24 * len(order) + 1.6))
    ax.imshow(M.values, aspect="auto", cmap=cmap, norm=norm, interpolation="nearest")
    for (r, c), v in np.ndenumerate(M.values):
        ax.text(c, r, f"{int(v)}", ha="center", va="center", fontsize=7,
                color="#ffffff" if v > trials * 0.55 else INK)
    ax.set_yticks(range(len(order)), order)
    ax.set_xticks(range(len(conditions)),
                  [f"{cat_of[c]}\n{c}" for c in conditions], fontsize=7)
    ax.xaxis.tick_top()
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(f"Exact 512-bit message recovery (out of {trials} images), wPSNR-matched",
                 loc="left", color=INK, pad=28)
    fig.tight_layout()
    fig.savefig(out / "fig_success.png", dpi=150)
    plt.close(fig)


def examples(run: Path, cfg, emb: pd.DataFrame, out: Path, size: int = 320, gain: float = 6.0):
    """Original / watermarked / amplified difference for one test image, using
    the uncoded embedding (every code is at the same distortion level)."""
    from PIL import Image
    from .data import load_rgb
    ex = out / "examples"
    ex.mkdir(exist_ok=True)
    path = cfg.test_images()[0]
    img = load_rgb(path)
    cal = json.loads((run / "calibration.json").read_text())
    bits = np.random.default_rng(0).integers(0, 2, 512, dtype=np.uint8)
    wm = imwm.embed(img, bits, cal["uncoded"]["scale"], cfg.seed, cfg.votes_per_bit)
    g = img.astype(np.float32).mean(2)
    best, pos = -1.0, (0, 0)
    for y in range(0, img.shape[0] - size + 1, size // 2):
        for x in range(0, img.shape[1] - size + 1, size // 2):
            v = float(np.abs(wm[y:y + size, x:x + size].astype(np.float32) - img[y:y + size, x:x + size]).mean())
            if v > best:
                best, pos = v, (y, x)
    y, x = pos
    ca, cb = img[y:y + size, x:x + size], wm[y:y + size, x:x + size]
    diff = np.clip(128 + gain * (cb.astype(np.float32) - ca), 0, 255).astype(np.uint8)
    for kind, im in (("orig", ca), ("wm", cb), ("diff", diff)):
        Image.fromarray(im).save(ex / f"{kind}.png")
    (ex / "examples.json").write_text(json.dumps(dict(image=path.name, crop=[y, x, size],
                                                      diff_gain=gain), indent=1))
