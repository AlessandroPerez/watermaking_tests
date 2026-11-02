"""Image-quality metrics. PSNR / SSIM come from scikit-image. No library ships
wPSNR, so it is implemented from its definition (Voloshynovskiy et al.,
"A stochastic approach to content adaptive digital image watermarking", 1999;
used by the Checkmark benchmark):

    NVF  = 1 / (1 + theta * var_local(Y)),  theta = D / max(var_local(Y))
    wPSNR = 10 log10(255^2 / mean((NVF * (I_w - I))^2))

NVF is computed on the original's luminance. The weighted error is averaged
over the R, G, B channels because invisible-watermark embeds in chroma.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

NVF_D = 75.0
NVF_WIN = 3


def luma(rgb: np.ndarray) -> np.ndarray:
    rgb = rgb.astype(np.float64)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def nvf_map(rgb: np.ndarray, D: float = NVF_D, win: int = NVF_WIN) -> np.ndarray:
    y = luma(rgb)
    m = ndi.uniform_filter(y, win)
    v = np.maximum(ndi.uniform_filter(y * y, win) - m * m, 0.0)
    return 1.0 / (1.0 + D / max(v.max(), 1e-12) * v)


def wpsnr(orig: np.ndarray, test: np.ndarray, nvf: np.ndarray | None = None) -> float:
    if nvf is None:
        nvf = nvf_map(orig)
    err = (test.astype(np.float64) - orig.astype(np.float64)) * nvf[..., None]
    return float(10 * np.log10(255.0 ** 2 / max(np.mean(err ** 2), 1e-20)))


def psnr(orig: np.ndarray, test: np.ndarray) -> float:
    return float(peak_signal_noise_ratio(orig, test, data_range=255))


def ssim(orig: np.ndarray, test: np.ndarray) -> float:
    return float(structural_similarity(orig, test, channel_axis=2, data_range=255))
