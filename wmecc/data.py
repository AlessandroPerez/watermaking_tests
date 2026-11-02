"""Cover images: DIV2K validation set, center-cropped (no resampling, except
the single image whose short side is below the crop size)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "div2k" / "DIV2K_valid_HR"
COVER_DIR = ROOT / "data" / "covers"
DIV2K_URL = "http://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip"


def load_rgb(path: Path | str) -> np.ndarray:
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"), dtype=np.uint8)


def save_rgb(path: Path | str, img: np.ndarray) -> None:
    Image.fromarray(img).save(path, compress_level=1)


def prepare_covers(size: int = 1024, raw_dir: Path = RAW_DIR,
                   out_dir: Path = COVER_DIR) -> list[Path]:
    """Center-crop every DIV2K image to ``size`` x ``size`` and store as PNG."""
    if not raw_dir.exists():
        raise FileNotFoundError(
            f"{raw_dir} missing: download {DIV2K_URL} and unzip into {raw_dir.parent}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for src in sorted(raw_dir.glob("*.png")):
        dst = out_dir / src.name
        if not dst.exists():
            img = load_rgb(src)
            h, w = img.shape[:2]
            if min(h, w) < size:  # only DIV2K 0830 (2040x816): upscale, then crop
                f = size / min(h, w)
                w, h = max(size, round(w * f)), max(size, round(h * f))
                img = np.asarray(Image.fromarray(img).resize((w, h), Image.LANCZOS))
            y0, x0 = (h - size) // 2, (w - size) // 2
            save_rgb(dst, img[y0:y0 + size, x0:x0 + size])
        out.append(dst)
    return out


def cover_paths(out_dir: Path = COVER_DIR) -> list[Path]:
    return sorted(out_dir.glob("*.png"))
