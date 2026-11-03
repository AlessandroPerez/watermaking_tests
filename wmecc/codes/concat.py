"""Serial concatenation: outer code -> inner code, built from the suite's own codes.

The inner decoder works on the soft channel values and leaves its errors in short
bursts, which is what an outer byte code handles best. The outer code also gives
codes that have no check of their own a ``valid`` flag.

* ``rs72_conv``, ``rs80_conv``, ``rs96_conv``: RS(72|80|96, 64) over GF(256), then
  the K = 7 rate-1/2 convolutional code (Viterbi), the classic deep-space pairing.
* ``rs96i4_conv``: the same redundancy as ``rs96_conv`` in four RS(24, 16) words,
  byte j in word j mod 4, so that a burst is shared between the words.
* ``rs72_turbo``: RS(72, 64), then the punctured rate-1/2 LTE turbo code.
* ``rs72_ldpc``: RS(72, 64), then 5G LDPC with n = 1024 (total rate 1/2).
* ``bch_ldpc``: BCH t = 8 shortened from BCH(1023, 943), then 5G LDPC with n = 1024
  (total rate 1/2), the pairing of DVB-S2.
* ``rs80_conv_er``, ``rs96_conv_er``: other decoders of the same embeddings. BCJR
  (log-MAP) replaces Viterbi and its bit reliabilities drive the RS
  errors-and-erasures decoder of ``rs.py``. Half of the check symbols are never
  erased. RS(72, 64) has no such variant: it would leave 4 check symbols to verify
  a candidate, so noise would pass about 3 % of the time.

``valid`` is the verdict of the outer decoder. The class attribute names avoid
``inner`` on :class:`Concatenated`: the experiment reads that name as "decoder
variant of another embedding".
"""

from __future__ import annotations

import numpy as np

from .base import Code, DecodeResult
from .bch import BCHCode
from .conv import ConvCode
from .ldpc import LDPC5GCode
from .rs import RSCode, RSErasure
from .turbo import TurboCode
from ._sionna import to_logits, torch_single_thread

__all__ = ["Concatenated", "ConcatenatedErasure", "ConvBCJR", "codes"]

CONV_R12 = ("171", "133")


class ConvBCJR(ConvCode):
    """``ConvCode`` that also returns the posterior LLRs of its input bits."""

    def _build(self) -> dict:
        from sionna.phy.fec.conv import BCJRDecoder
        blk = super()._build()
        blk["bcjr"] = BCJRDecoder(encoder=blk["enc"], algorithm="log", hard_out=False,
                                  device="cpu", precision="single")
        return blk

    def posterior(self, llr: np.ndarray) -> np.ndarray:
        """(B, n) channel LLRs -> (B, k) LLRs (log P0/P1) of the input bits."""
        torch = torch_single_thread()
        with torch.inference_mode():
            out = self.blocks["bcjr"](torch.from_numpy(to_logits(llr, self.n)))
        return -out.numpy().astype(np.float64)


class Concatenated(Code):
    family = "Concatenated"
    soft = True
    has_check = True

    def __init__(self, name: str, outer: Code, inner_code: Code):
        if inner_code.k != outer.n:
            raise ValueError(f"inner k = {inner_code.k} does not take outer n = {outer.n}")
        self.name, self.outer, self.inner_code = name, outer, inner_code
        self.k, self.n = outer.k, inner_code.n

    def encode(self, msg):
        return self.inner_code.encode(self.outer.encode(msg))

    def decode(self, llr):
        bits = self.inner_code.decode(llr).msg
        return self.outer.decode(1.0 - 2.0 * bits.astype(np.float64))

    def describe(self) -> str:
        return (f"{self.name} (outer {self.outer.describe()}; "
                f"inner {self.inner_code.describe()}; R={self.rate:.3f})")


class ConcatenatedErasure(Code):
    """BCJR, then RS errors-and-erasures, on the embedding of a :class:`Concatenated`."""

    family = "Concatenated"
    soft = True
    has_check = True

    def __init__(self, inner: Concatenated):
        rs = inner.outer
        self.inner = inner
        self.name = inner.name + "_er"
        self.k, self.n = inner.k, inner.n
        self.rs = RSErasure(rs, margin=(rs.n_sym - rs.k_sym) // 2)

    def encode(self, msg):
        return self.inner.encode(msg)

    def decode(self, llr) -> DecodeResult:
        return self.rs.decode(self.inner.inner_code.posterior(llr))

    def describe(self) -> str:
        return f"{self.name} ({self.inner.name} with BCJR and RS errors-and-erasures)"


def _rs_conv(n_sym: int, depth: int = 1, name: str | None = None) -> Concatenated:
    outer = RSCode(f"rs{n_sym}", n_sym, depth=depth)
    return Concatenated(name or f"rs{n_sym}_conv", outer,
                        ConvBCJR(f"conv_k{outer.n}", CONV_R12, outer.n))


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("outer codes are fixed for k = 512")
    rs72 = RSCode("rs72", 72)
    rs80_conv, rs96_conv = _rs_conv(80), _rs_conv(96)
    bch = BCHCode("bch_t8", 1023, 943, 8)
    return [_rs_conv(72), rs80_conv, rs96_conv, _rs_conv(96, 4, "rs96i4_conv"),
            Concatenated("rs72_turbo", rs72, TurboCode("turbo_k576", 1 / 2, rs72.n)),
            Concatenated("rs72_ldpc", rs72, LDPC5GCode("ldpc_k576", 1024, rs72.n)),
            Concatenated("bch_ldpc", bch, LDPC5GCode("ldpc_k592", 1024, bch.n)),
            ConcatenatedErasure(rs80_conv), ConcatenatedErasure(rs96_conv)]
