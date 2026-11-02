"""Glue between the suite's conventions (base.py) and Sionna's PyTorch FEC blocks.

* Sionna decoders take *logits* ``log p(1)/p(0)`` (verified empirically for
  every decoder used here), i.e. the negative of our ``llr = log P0/P1``;
  :func:`to_logits` flips the sign, maps NaN -> 0 and clips to +-50 (Sionna
  clips again internally).
* Bits travel as float32 0./1. tensors inside Sionna, uint8 outside.
* ``torch.set_num_threads(1)`` is applied inside every encode/decode call
  (decoders run in parallel worker processes); nothing else thread-related is
  touched.  No scrambling/whitening is done here (the experiment layer does it).
* Sionna blocks are built lazily and dropped when a code is pickled, so code
  objects are cheap to send to workers; they are rebuilt deterministically on
  first use.
* Batches are processed in chunks of ``chunk`` frames to bound memory.
"""

from __future__ import annotations

import numpy as np

from .base import Code, DecodeResult

LLR_CLIP = 50.0


def torch_single_thread():
    import torch
    if torch.get_num_threads() != 1:
        torch.set_num_threads(1)
    return torch


def to_logits(llr: np.ndarray, n: int) -> np.ndarray:
    """Our LLR (log P0/P1), shape (B, n) -> Sionna logits (log P1/P0), float32."""
    x = np.asarray(llr, dtype=np.float64).reshape(-1, n)
    x = np.nan_to_num(x, nan=0.0, posinf=LLR_CLIP, neginf=-LLR_CLIP)
    return np.ascontiguousarray(-np.clip(x, -LLR_CLIP, LLR_CLIP), dtype=np.float32)


class SionnaCode(Code):
    """Base class: subclasses implement ``_build`` (returns a dict of Sionna
    blocks), ``_encode_t`` and ``_decode_t`` on torch tensors."""

    chunk: int = 256

    def __init__(self):
        self._blk = None

    # -- lazy blocks -------------------------------------------------------
    def _build(self) -> dict:
        raise NotImplementedError

    @property
    def blocks(self) -> dict:
        if self._blk is None:
            self._blk = self._build()
        return self._blk

    def __getstate__(self):
        d = self.__dict__.copy()
        d["_blk"] = None
        return d

    # -- torch-level hooks -----------------------------------------------------
    def _encode_t(self, u):          # (b, k) float32 -> (b, n) float32
        raise NotImplementedError

    def _decode_t(self, logits):     # (b, n) float32 -> (bits (b, k), valid (b,) | None)
        raise NotImplementedError

    # -- Code API ----------------------------------------------------------------
    def encode(self, msg: np.ndarray) -> np.ndarray:
        torch = torch_single_thread()
        msg = np.asarray(msg, dtype=np.uint8).reshape(-1, self.k)
        out = np.empty((msg.shape[0], self.n), dtype=np.uint8)
        with torch.inference_mode():
            for s in range(0, msg.shape[0], self.chunk):
                u = torch.from_numpy(msg[s:s + self.chunk].astype(np.float32))
                out[s:s + self.chunk] = self._encode_t(u).numpy() > 0.5
        return out

    def decode(self, llr: np.ndarray) -> DecodeResult:
        torch = torch_single_thread()
        logits = to_logits(llr, self.n)
        B = logits.shape[0]
        msg = np.empty((B, self.k), dtype=np.uint8)
        valid = np.ones(B, dtype=bool)
        with torch.inference_mode():
            for s in range(0, B, self.chunk):
                bits, ok = self._decode_t(torch.from_numpy(logits[s:s + self.chunk]))
                msg[s:s + self.chunk] = bits.numpy() > 0.5
                if ok is not None:
                    valid[s:s + self.chunk] = np.asarray(ok, dtype=bool)
        return DecodeResult(msg=msg, valid=valid)
