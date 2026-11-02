"""Attack suite: thin parameterisations of OpenCV / Pillow / scikit-image
operations. Every attack maps a uint8 RGB image to a uint8 RGB image
(possibly of a different size) and is deterministic given its seed.

Conventions:
* rotation: about the image center, same canvas size, black fill, bilinear;
* scaling: whole image resized by the factor (INTER_AREA down, cubic up);
* cropping p%: centered window keeping p% of the *area* (no resize);
* translation t%: content shifted by t% of width and height (diagonal),
  same canvas size, black fill;
* noise sigmas / amounts are relative to the [0, 1] intensity range
  (skimage.util.random_noise; uniform noise via numpy's generator);
* brightness / contrast / saturation use PIL.ImageEnhance factors 1 +/- p;
* gamma: skimage.exposure.adjust_gamma; sharpening: skimage.filters.unsharp_mask;
* PNG is lossless: those entries are sanity controls (must equal "none").
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Callable

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from skimage.exposure import adjust_gamma
from skimage.filters import unsharp_mask
from skimage.util import img_as_ubyte, random_noise


@dataclass(frozen=True)
class Attack:
    name: str          # unique id, e.g. "jpeg_q75"
    family: str        # e.g. "Compression"
    kind: str          # e.g. "JPEG"
    param: float       # numeric parameter for plotting (NaN if none)
    fn: Callable[[np.ndarray, np.random.Generator], np.ndarray]

    def __call__(self, img: np.ndarray, seed: int = 0) -> np.ndarray:
        out = self.fn(img, np.random.default_rng(seed))
        assert out.dtype == np.uint8 and out.ndim == 3, self.name
        return out


def _u8(x: np.ndarray) -> np.ndarray:
    return np.clip(np.rint(x), 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- geometric
def rotate(img, deg):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def scale(img, s):
    h, w = img.shape[:2]
    interp = cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC
    return cv2.resize(img, (max(1, round(w * s)), max(1, round(h * s))), interpolation=interp)


def crop(img, area_frac):
    h, w = img.shape[:2]
    f = np.sqrt(area_frac)
    ch, cw = round(h * f), round(w * f)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    return np.ascontiguousarray(img[y0:y0 + ch, x0:x0 + cw])


def translate(img, frac):
    h, w = img.shape[:2]
    M = np.float32([[1, 0, frac * w], [0, 1, frac * h]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_NEAREST,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


# -------------------------------------------------------------- compression
def _pil_roundtrip(img, fmt, **kw):
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format=fmt, **kw)
    buf.seek(0)
    with Image.open(buf) as im:
        return np.asarray(im.convert("RGB"), dtype=np.uint8).copy()


def jpeg(img, q):
    return _pil_roundtrip(img, "JPEG", quality=int(q))


def webp(img, q):
    return _pil_roundtrip(img, "WEBP", quality=int(q), method=4)


def png(img, level, filt):
    flags = [cv2.IMWRITE_PNG_COMPRESSION, int(level)]
    if hasattr(cv2, "IMWRITE_PNG_FILTER") and filt is not None:
        flags += [cv2.IMWRITE_PNG_FILTER, int(filt)]
    ok, buf = cv2.imencode(".png", img[..., ::-1], flags)
    assert ok
    return np.ascontiguousarray(cv2.imdecode(buf, cv2.IMREAD_COLOR)[..., ::-1])


# ---------------------------------------------------------------- filtering
def gaussian_blur(img, sigma):
    k = 2 * int(np.ceil(3 * sigma)) + 1
    return cv2.GaussianBlur(img, (k, k), sigma)


def median(img, k):
    return cv2.medianBlur(img, int(k))


def bilateral(img, d, sc, ss):
    return cv2.bilateralFilter(img, int(d), sc, ss)


def sharpen(img, amount, radius=1.0):
    return img_as_ubyte(unsharp_mask(img, radius=radius, amount=amount, channel_axis=2))


# -------------------------------------------------------------------- noise
def gauss_noise(img, sigma, rng):
    return img_as_ubyte(random_noise(img, mode="gaussian", var=sigma ** 2, rng=rng))


def salt_pepper(img, p, rng):
    return img_as_ubyte(random_noise(img, mode="s&p", amount=p, rng=rng))


def uniform_noise(img, a, rng):
    return _u8(img + rng.uniform(-a * 255, a * 255, img.shape))


def poisson_noise(img, rng):
    return img_as_ubyte(random_noise(img, mode="poisson", rng=rng))


# -------------------------------------------------------------------- color
def _enhance(img, cls, factor):
    return np.asarray(cls(Image.fromarray(img)).enhance(factor), dtype=np.uint8).copy()


def gamma(img, g):
    return adjust_gamma(img, g)


# -------------------------------------------------------------------- suite
def attack_suite() -> list[Attack]:
    A: list[Attack] = []
    add = lambda name, fam, kind, p, fn: A.append(Attack(name, fam, kind, float(p), fn))
    add("none", "None", "None", np.nan, lambda x, r: x.copy())

    G = "Geometric"
    for d in (1, 5, 10, 15, 20, 25, 30):
        add(f"rot_{d}", G, "Rotation", d, lambda x, r, d=d: rotate(x, d))
    for s in (0.5, 0.8, 1.2, 1.5, 2.0):
        add(f"scale_{s}", G, "Scaling", s, lambda x, r, s=s: scale(x, s))
    for p in (90, 80, 70, 60, 50):
        add(f"crop_{p}", G, "Cropping", p, lambda x, r, p=p: crop(x, p / 100))
    for t in (10, -10, 20, -20, 30, -30):
        add(f"trans_{t:+d}", G, "Translation", t, lambda x, r, t=t: translate(x, t / 100))

    C = "Compression"
    for q in (95, 90, 85, 80, 75, 70, 65, 60, 55, 50):
        add(f"jpeg_{q}", C, "JPEG", q, lambda x, r, q=q: jpeg(x, q))
    for level, fname in ((1, "NONE"), (6, "SUB"), (6, "UP"), (9, "AVG"), (9, "PAETH")):
        add(f"png_l{level}_{fname.lower()}", C, "PNG", level,
            lambda x, r, l=level, f=fname: png(x, l, getattr(cv2, f"IMWRITE_PNG_FILTER_{f}", None)))
    for q in (90, 75, 60, 45, 30):
        add(f"webp_{q}", C, "WebP", q, lambda x, r, q=q: webp(x, q))

    F = "Filtering"
    for s in (0.5, 1.0, 1.5, 2.0, 2.5):
        add(f"gblur_{s}", F, "Gaussian blur", s, lambda x, r, s=s: gaussian_blur(x, s))
    for k in (3, 5, 7):
        add(f"median_{k}", F, "Median", k, lambda x, r, k=k: median(x, k))
    for d, sc, ss in ((5, 25, 25), (9, 50, 50), (9, 75, 75)):
        add(f"bilateral_{d}_{sc}", F, "Bilateral", sc,
            lambda x, r, d=d, sc=sc, ss=ss: bilateral(x, d, sc, ss))
    for a in (0.5, 1.0, 2.0):
        add(f"sharpen_{a}", F, "Sharpening", a, lambda x, r, a=a: sharpen(x, a))

    N = "Noise"
    for s in (0.01, 0.02, 0.03, 0.04, 0.05):
        add(f"gnoise_{s}", N, "Gaussian noise", s, lambda x, r, s=s: gauss_noise(x, s, r))
    for p in (1, 2, 3, 4, 5):
        add(f"sp_{p}", N, "Salt & pepper", p, lambda x, r, p=p: salt_pepper(x, p / 100, r))
    for a in (0.02, 0.05, 0.08):
        add(f"unoise_{a}", N, "Uniform noise", a, lambda x, r, a=a: uniform_noise(x, a, r))
    add("poisson", N, "Poisson", np.nan, lambda x, r: poisson_noise(x, r))

    K = "Color"
    for p in (10, -10, 20, -20, 30, -30):
        add(f"bright_{p:+d}", K, "Brightness", p,
            lambda x, r, p=p: _enhance(x, ImageEnhance.Brightness, 1 + p / 100))
    for p in (10, -10, 20, -20, 30, -30):
        add(f"contrast_{p:+d}", K, "Contrast", p,
            lambda x, r, p=p: _enhance(x, ImageEnhance.Contrast, 1 + p / 100))
    for p in (20, -20, 40, -40):
        add(f"sat_{p:+d}", K, "Saturation", p,
            lambda x, r, p=p: _enhance(x, ImageEnhance.Color, 1 + p / 100))
    for g in (0.5, 0.8, 1.2, 1.5, 2.0):
        add(f"gamma_{g}", K, "Gamma", g, lambda x, r, g=g: gamma(x, g))

    M = "Combined"
    for s, q in ((0.5, 90), (1.0, 80), (1.0, 60), (1.5, 50)):
        add(f"blur{s}+jpeg{q}", M, "JPEG + blur", q,
            lambda x, r, s=s, q=q: jpeg(gaussian_blur(x, s), q))
    for d, p in ((5, 90), (10, 80), (15, 70), (30, 50)):
        add(f"rot{d}+crop{p}", M, "Rotation + crop", d,
            lambda x, r, d=d, p=p: crop(rotate(x, d), p / 100))
    for s, q in ((0.01, 90), (0.02, 75), (0.03, 60), (0.05, 50)):
        add(f"noise{s}+jpeg{q}", M, "Noise + compression", q,
            lambda x, r, s=s, q=q: jpeg(gauss_noise(x, s, r), q))
    names = [a.name for a in A]
    assert len(names) == len(set(names))
    return A


def get_attacks(names: list[str] | None = None) -> list[Attack]:
    suite = attack_suite()
    if names is None:
        return suite
    by = {a.name: a for a in suite}
    return [by[n] for n in names]
