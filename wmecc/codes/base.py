"""Common interface for every error-correcting code in the suite.

Conventions (all codes MUST follow them):

* Bits are ``np.uint8`` arrays with values in {0, 1}.
* ``encode(msg)``: ``msg`` has shape ``(B, k)`` -> codewords of shape ``(B, n)``.
* ``decode(llr)``: ``llr`` has shape ``(B, n)`` (float64) with
  ``llr = log P(c=0 | y) / P(c=1 | y)``, i.e. positive means bit 0.
  The channel maps bit 0 -> +1 and bit 1 -> -1 (BPSK), so on AWGN
  ``llr = 2 * y / sigma**2``. Returns a :class:`DecodeResult`.
* ``valid[b]`` is the decoder's own integrity verdict (bounded-distance
  success for BCH/RS, zero syndrome for LDPC, CRC pass for polar, ...).
  Codes without an intrinsic check set ``has_check = False`` and return
  ``valid = True`` everywhere.
* ``soft`` tells whether the decoder uses LLR magnitudes. Hard-decision
  variants of soft decoders are obtained with :class:`HardInput`.
* Every code carries exactly ``k`` message bits (512 in the experiment) and
  ``n`` channel bits; ``n`` differs between codes. Fairness between codes
  (equal image distortion) is handled by the watermark layer, not here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class DecodeResult:
    msg: np.ndarray    # (B, k) uint8
    valid: np.ndarray  # (B,) bool


class Code(ABC):
    name: str          # unique id used in result tables, e.g. "bch_r12" (no slashes)
    family: str        # e.g. "BCH", "LDPC"
    k: int
    n: int
    soft: bool = True
    has_check: bool = False

    @property
    def rate(self) -> float:
        return self.k / self.n

    @abstractmethod
    def encode(self, msg: np.ndarray) -> np.ndarray: ...

    @abstractmethod
    def decode(self, llr: np.ndarray) -> DecodeResult: ...

    def describe(self) -> str:
        return f"{self.name} ({self.family}, n={self.n}, k={self.k}, R={self.rate:.3f})"

    def __repr__(self) -> str:
        return f"<{self.describe()}>"


class HardInput(Code):
    """Hard-decision variant of a soft decoder: the channel is reduced to a
    binary symmetric channel. Only the signs of the LLRs are passed on, all
    with the same magnitude log((1-p)/p), where p is the frame's average error
    probability implied by the calibrated LLRs. A fixed +/-1 would tell
    sum-product / log-MAP decoders that every bit is 27 % unreliable."""

    def __init__(self, inner: Code, suffix: str = "_hard"):
        self.inner = inner
        self.name = inner.name + suffix
        self.family = inner.family
        self.k, self.n = inner.k, inner.n
        self.soft = False
        self.has_check = inner.has_check

    def encode(self, msg):
        return self.inner.encode(msg)

    def decode(self, llr):
        llr = np.asarray(llr, dtype=float)
        a = np.minimum(np.abs(np.nan_to_num(llr)), 50.0)
        p = np.clip(np.mean(1.0 / (1.0 + np.exp(a)), axis=1, keepdims=True), 1e-9, 0.5)
        mag = np.log((1.0 - p) / p)
        return self.inner.decode(np.where(llr >= 0, mag, -mag))


# ----------------------------------------------------------------- helpers

def bits_to_bytes(bits: np.ndarray) -> np.ndarray:
    """(B, 8m) bits -> (B, m) uint8, MSB first."""
    return np.packbits(bits.astype(np.uint8), axis=-1)


def bytes_to_bits(data: np.ndarray) -> np.ndarray:
    """(B, m) uint8 -> (B, 8m) bits, MSB first."""
    return np.unpackbits(data.astype(np.uint8), axis=-1)


def hard(llr: np.ndarray) -> np.ndarray:
    """LLR -> hard bits (ties go to 0)."""
    return (llr < 0).astype(np.uint8)


def simulate_awgn(code: Code, ebn0_db: float, trials: int,
                  rng: np.random.Generator | None = None,
                  batch: int = 256) -> dict:
    """BPSK/AWGN Monte Carlo with Eb/N0 defined per *information* bit.

    Returns dict with fer, ber, valid_rate, false_valid_rate (valid but
    wrong). Used by the unit tests to sanity-check every decoder against
    textbook performance."""
    rng = rng or np.random.default_rng(0)
    esn0 = 10 ** (ebn0_db / 10) * code.k / code.n
    sigma2 = 1.0 / (2.0 * esn0)
    frame_err = bit_err = n_valid = n_false_valid = done = 0
    while done < trials:
        b = min(batch, trials - done)
        msg = rng.integers(0, 2, size=(b, code.k), dtype=np.uint8)
        cw = code.encode(msg)
        assert cw.shape == (b, code.n) and cw.dtype == np.uint8
        y = (1.0 - 2.0 * cw) + rng.normal(0.0, np.sqrt(sigma2), size=cw.shape)
        res = code.decode(2.0 * y / sigma2)
        wrong = np.any(res.msg != msg, axis=1)
        frame_err += int(wrong.sum())
        bit_err += int((res.msg != msg).sum())
        n_valid += int(res.valid.sum())
        n_false_valid += int((res.valid & wrong).sum())
        done += b
    return dict(fer=frame_err / trials, ber=bit_err / (trials * code.k),
                valid_rate=n_valid / trials, false_valid_rate=n_false_valid / trials)
