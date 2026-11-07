"""Thin wrapper around invisible-watermark (``imwatermark``, method ``dwtDctSvd``).

The library takes the largest singular value of the DCT of every 4x4 block of
the Haar-LL band of the chroma (U) channel and quantises it with step
``scale``. Each block carries one bit and its decoder gives one 0/1 vote per
block. The library is used unmodified.

The library assigns bit ``j mod n`` to block ``j``, which puts all the votes of
a bit in one vertical stripe whenever ``n`` is a multiple of the row length,
so robustness would depend on ``n mod 256``. To avoid that, the library is
given one bit per block (``wmLen`` = number of blocks) through a keyed layout:
every coded bit gets the same number of votes, spread over the whole image.

Two layouts, both blind (the decoder knows the code length and the key):

* ``votes=None``: the bits share all the blocks. Every code marks the same area,
  so distortion does not depend on length and a longer code pays in votes per
  bit.
* ``votes=v``: every coded bit gets exactly ``v`` blocks and the other blocks are
  left unmarked, so a longer code marks more of the image and pays in strength.
  A block of the Haar-LL band is exactly one ``BLOCK`` x ``BLOCK`` pixel square,
  so the pixels of unmarked blocks are put back after the library has run.

``extract`` first resizes to the embedding frame ``SIZE`` (a system parameter),
then returns per-bit vote counts. ``votes_to_llr`` turns the vote fractions
into LLRs with a two-component Gaussian mixture (scikit-learn, shared variance)
fitted blindly on the frame itself: one component per bit value. The shared
variance keeps the LLR linear in the fraction. Extraction is blind: it needs
only system parameters (code length, strength, layout key), never the cover or
the message.
"""

from __future__ import annotations

import functools

import cv2
import numpy as np
import pywt
from imwatermark import WatermarkEncoder
from imwatermark.dwtDctSvd import EmbedDwtDctSvd
from sklearn.mixture import GaussianMixture

SIZE = 1024                 # embedding frame
BLOCK = 8                   # pixels per side of one 4x4 block of the Haar-LL band
SIDE = SIZE // BLOCK
BLOCKS = SIDE ** 2


class _VoteDecoder(EmbedDwtDctSvd):
    """``EmbedDwtDctSvd.decode`` without the final average-and-threshold step."""

    def decode_votes(self, bgr: np.ndarray) -> list[list[int]]:
        row, col, _ = bgr.shape
        yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
        scores = [[] for _ in range(self._wmLen)]
        for channel in range(2):
            if self._scales[channel] <= 0:
                continue
            ca1, _ = pywt.dwt2(yuv[:row // 4 * 4, :col // 4 * 4, channel], "haar")
            scores = self.decode_frame(ca1, self._scales[channel], scores)
        return scores


def _scales(scale: float) -> list[float]:
    # library default layout [Y, U, V] = [0, 36, 0]: only the strength changes
    return [0, float(scale), 0]


@functools.lru_cache(maxsize=64)
def _layout(n: int, key: int, votes: int | None = None) -> np.ndarray:
    """Block -> coded bit (-1 = unmarked): equal votes per bit, keyed permutation."""
    used = BLOCKS if votes is None else n * votes
    if used > BLOCKS:
        raise ValueError(f"{n} bits x {votes} votes do not fit in {BLOCKS} blocks")
    blocks = np.full(BLOCKS, -1)
    blocks[:used] = np.resize(np.arange(n), used)
    return np.random.default_rng([n, key]).permutation(blocks)


def embed(rgb: np.ndarray, bits: np.ndarray, scale: float, key: int = 0,
          votes: int | None = None) -> np.ndarray:
    assert rgb.shape[:2] == (SIZE, SIZE)
    layout = _layout(len(bits), key, votes)
    enc = WatermarkEncoder()
    # the library marks every block: the bit given to an unmarked block is irrelevant
    enc.set_watermark("bits", np.asarray(bits)[layout].tolist())
    out = enc.encode(np.ascontiguousarray(rgb[..., ::-1]), "dwtDctSvd", scales=_scales(scale))
    out = np.ascontiguousarray(out[..., ::-1])
    unmarked = (layout < 0).reshape(SIDE, SIDE).repeat(BLOCK, 0).repeat(BLOCK, 1)
    out[unmarked] = rgb[unmarked]
    return out


def to_frame(rgb: np.ndarray) -> np.ndarray | None:
    """The frame extraction reads: resized to the embedding frame (None if too small)."""
    h, w = rgb.shape[:2]
    if h * w < 256 * 256:   # same limit the library enforces
        return None
    if (h, w) != (SIZE, SIZE):
        rgb = cv2.resize(rgb, (SIZE, SIZE), interpolation=cv2.INTER_AREA if h > SIZE else cv2.INTER_CUBIC)
    return rgb


def block_votes(rgb: np.ndarray, scale: float) -> np.ndarray | None:
    """The library's 0/1 vote of every block (``None`` if the frame is too small).

    Depends on the frame and the strength only, not on the code: frames read at the
    same strength by several codes need one call (the slow part of extraction)."""
    rgb = to_frame(rgb)
    if rgb is None:
        return None
    dec = _VoteDecoder(watermarks=[], wmLen=BLOCKS, scales=_scales(scale))
    scores = dec.decode_votes(np.ascontiguousarray(rgb[..., ::-1]))
    return np.array([s[0] for s in scores], np.uint8)


def tally(block: np.ndarray | None, n: int, key: int = 0,
          votes: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Block votes -> (votes for bit 1, number of votes) per coded bit."""
    if block is None:
        return np.zeros(n), np.zeros(n)
    layout = _layout(n, key, votes)
    marked = layout >= 0
    ones = np.bincount(layout[marked], block[marked].astype(float), n)
    return ones, np.bincount(layout[marked], minlength=n).astype(float)


def extract(rgb: np.ndarray, n: int, scale: float, key: int = 0,
            votes: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Blind extraction -> (votes for bit 1, number of votes) per coded bit."""
    return tally(block_votes(rgb, scale), n, key, votes)


def _mixture(ones: np.ndarray, count: np.ndarray):
    """(mu0, mu1, sigma) of a tied 2-component GMM on the vote fractions, or None."""
    ok = count > 0
    if ok.sum() < 8:
        return None
    f = (ones[ok] / count[ok])[:, None]
    if np.ptp(f) == 0:
        return None
    gm = GaussianMixture(2, covariance_type="tied", random_state=0, reg_covar=1e-4).fit(f)
    mu0, mu1 = np.sort(gm.means_.ravel())     # fewer "1" votes <=> bit 0
    return float(mu0), float(mu1), float(np.sqrt(gm.covariances_.ravel()[0]))


def separation(ones: np.ndarray, count: np.ndarray) -> float:
    """d' = (mu1 - mu0) / sigma of the vote-fraction mixture (presence statistic)."""
    m = _mixture(ones, count)
    return 0.0 if m is None else (m[1] - m[0]) / m[2]


def votes_to_llr(ones: np.ndarray, count: np.ndarray) -> np.ndarray:
    """LLR (positive => bit 0) of each coded bit from its block votes."""
    m = _mixture(ones, count)
    if m is None:
        return np.zeros(len(ones))
    mu0, mu1, sigma = m
    f = np.where(count > 0, ones / np.maximum(count, 1), (mu0 + mu1) / 2)
    return (mu1 - mu0) / sigma ** 2 * ((mu0 + mu1) / 2 - f)
