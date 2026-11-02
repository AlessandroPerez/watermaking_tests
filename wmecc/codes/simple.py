"""Baselines: uncoded, repetition, Hamming(7,4) -- thin wrappers around komm.

Library classes (komm 0.37):

* ``repR``: ``komm.RepetitionCode(R)`` applied to every message bit,
  decoded with ``komm.ExhaustiveCodewordDecoder(code, input_type="soft")``
  (ML over the two codewords = sign of the summed LLRs, i.e. soft combining;
  ties -> 0).  ``rep3_hard`` = ``HardInput(rep3)`` = majority vote.
* ``hamming74``: ``komm.HammingCode(3)`` per 4-bit block, soft ML with
  ``komm.ExhaustiveCodewordDecoder(code, input_type="soft")``;
  ``hamming74_hard``: ``komm.SyndromeTableDecoder`` on hard decisions.
* ``uncoded``: identity (no library needed).

komm's L-value convention is the same as ours (positive => bit 0: its soft
metric is ``L @ (-1)**c``).

Codeword layouts:

* ``repR``: copy ``j`` of bit ``i`` at index ``j * k + i`` (codeword = the
  message tiled R times).  komm produces copies contiguously per bit; the
  wrapper transposes (a pure index permutation).
* ``hamming74``: komm's block layout, block ``b`` = ``msg[4b:4b+4]`` occupies
  codeword indices ``7b .. 7b+6`` as ``[d1 d2 d3 d4 p1 p2 p3]`` (systematic,
  information set on the left; p1 = d1+d2+d4, p2 = d1+d3+d4, p3 = d2+d3+d4).

Also hosts the input helpers :func:`prep_llr` / :func:`check_msg` used by the
other classical-code wrappers.
"""

from __future__ import annotations

import numpy as np
import komm

from .base import Code, DecodeResult, HardInput, hard

LLR_CLIP = 50.0


# ------------------------------------------------------------------ helpers

def prep_llr(llr: np.ndarray, n: int) -> np.ndarray:
    """Validate shape (B, n), cast to float64, map NaN -> 0 / +-inf -> +-clip
    and clip to +-LLR_CLIP so that garbage inputs cannot overflow."""
    llr = np.asarray(llr, dtype=np.float64)
    if llr.ndim != 2 or llr.shape[1] != n:
        raise ValueError(f"expected LLRs of shape (B, {n}), got {llr.shape}")
    llr = np.nan_to_num(llr, nan=0.0, posinf=LLR_CLIP, neginf=-LLR_CLIP)
    return np.clip(llr, -LLR_CLIP, LLR_CLIP)


def check_msg(msg: np.ndarray, k: int) -> np.ndarray:
    """Validate a (B, k) {0,1} message batch and return it as uint8."""
    msg = np.asarray(msg)
    if msg.ndim != 2 or msg.shape[1] != k:
        raise ValueError(f"expected messages of shape (B, {k}), got {msg.shape}")
    msg = msg.astype(np.uint8, copy=False)
    if msg.size and msg.max() > 1:
        raise ValueError("message bits must be 0/1")
    return msg


# komm's decoders open a tqdm progress bar that shows up after 2.5 s; decoding
# in slices of this many frames keeps every call well below that.
_CHUNK = 4096


def _chunked(fn, x: np.ndarray) -> np.ndarray:
    if x.shape[0] <= _CHUNK:
        return fn(x)
    return np.concatenate([fn(x[i:i + _CHUNK]) for i in range(0, x.shape[0], _CHUNK)])


# ------------------------------------------------------------------ codes

class Uncoded(Code):
    family = "Uncoded"
    soft = False          # output depends on the LLR signs only
    has_check = False

    def __init__(self, k: int = 512):
        self.name = "uncoded"
        self.k = self.n = k

    def encode(self, msg):
        return check_msg(msg, self.k).copy()

    def decode(self, llr):
        llr = prep_llr(llr, self.n)
        return DecodeResult(hard(llr), np.ones(llr.shape[0], dtype=bool))


class Repetition(Code):
    """R-fold repetition via komm.RepetitionCode + soft exhaustive ML."""
    family = "Repetition"
    soft = True
    has_check = False

    def __init__(self, reps: int, k: int = 512):
        if reps < 2:
            raise ValueError("reps must be >= 2")
        self.reps = reps
        self.name = f"rep{reps}"
        self.k = k
        self.n = reps * k
        self.code = komm.RepetitionCode(reps)
        self.decoder = komm.ExhaustiveCodewordDecoder(self.code, input_type="soft")

    def encode(self, msg):
        msg = check_msg(msg, self.k)
        B = msg.shape[0]
        cw = self.code.encode(msg)                                   # (B, k*R), copies contiguous
        cw = cw.reshape(B, self.k, self.reps).transpose(0, 2, 1)     # copy j of bit i -> j*k + i
        return np.ascontiguousarray(cw.reshape(B, self.n)).astype(np.uint8)

    def _decode(self, llr):
        B = llr.shape[0]
        blocks = llr.reshape(B, self.reps, self.k).transpose(0, 2, 1).reshape(B, self.n)
        return self.decoder.decode(blocks)

    def decode(self, llr):
        llr = prep_llr(llr, self.n)
        msg = _chunked(self._decode, llr).astype(np.uint8)
        return DecodeResult(msg, np.ones(llr.shape[0], dtype=bool))


class Hamming74(Code):
    """k/4 blocks of komm.HammingCode(3).  ``soft=True``: soft exhaustive ML
    per block; ``soft=False``: komm.SyndromeTableDecoder on hard decisions."""
    family = "Hamming"
    has_check = False

    def __init__(self, k: int = 512, soft: bool = True):
        if k % 4:
            raise NotImplementedError("Hamming(7,4) needs k % 4 == 0")
        self.k = k
        self.n = 7 * (k // 4)
        self.soft = soft
        self.name = "hamming74" if soft else "hamming74_hard"
        self.code = komm.HammingCode(3)
        if soft:
            self.decoder = komm.ExhaustiveCodewordDecoder(self.code, input_type="soft")
        else:
            self.decoder = komm.SyndromeTableDecoder(self.code)

    def encode(self, msg):
        return self.code.encode(check_msg(msg, self.k)).astype(np.uint8)

    def decode(self, llr):
        llr = prep_llr(llr, self.n)
        x = llr if self.soft else hard(llr)
        msg = _chunked(self.decoder.decode, x).astype(np.uint8)
        return DecodeResult(msg, np.ones(llr.shape[0], dtype=bool))


def codes(k: int = 512) -> list[Code]:
    rep3 = Repetition(3, k)
    return [Uncoded(k), Repetition(2, k), rep3, Repetition(4, k), HardInput(rep3),
            Hamming74(k, soft=True), Hamming74(k, soft=False)]
