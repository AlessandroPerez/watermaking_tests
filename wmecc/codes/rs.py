"""Reed-Solomon codes over GF(2^8), shortened to 64 message bytes (k = 512
bits) -- thin wrapper around ``galois.ReedSolomon`` (galois 0.4.11).

* Mother codes ``galois.ReedSolomon(255, 255 - 2t)`` (narrow-sense,
  primitive polynomial x^8+x^4+x^3+x^2+1, alpha = x), shortened by passing
  64 message symbols to ``encode`` / ``n`` symbols to ``decode``.
* Bits <-> bytes MSB first (``base.bits_to_bytes`` / ``bytes_to_bits``);
  systematic, so ``codeword[:, :512] == msg``.
* Hard-decision bounded-distance decoding by galois (errors only, up to t
  symbol errors); ``valid`` = galois did not report a failure.  On failure
  galois returns the received word, so ``msg`` = hard systematic bits.

Codes: rs_r23 = RS(96, 64), t = 16  (n = 768 bits);
       rs_r12 = RS(128, 64), t = 32 (n = 1024 bits);
       rs_r13 = RS(192, 64), t = 64 (n = 1536 bits).

``*_i4``: interleaved RS of depth 4, four codewords of a quarter of the length
(RS(24, 16), RS(32, 16), RS(48, 16)), byte j of the frame in word j mod 4. Same
n and same total redundancy; the frame is correct only if every word decodes.

``*_er``: errors-and-erasures decoding of the same codeword (Forney's generalised
minimum distance decoding). Bytes are ranked by the probability that all their
bits are right, given the LLRs. galois decodes with the s least reliable bytes
erased, for every even s, and among the words it returns the one that correlates
best with the LLRs is kept. ``MARGIN`` check symbols are never erased, so that
each candidate is still verified by the remaining redundancy (galois needs
2 e + s <= n - k; with no margin a decode would always "succeed").

galois is called with numba limited to one thread (see ``bch.py``), and the
galois object is built lazily on first use.
"""

from __future__ import annotations

import galois
import numpy as np

from .base import Code, DecodeResult, bits_to_bytes, bytes_to_bits, hard
from .bch import numba_single_thread
from .simple import check_msg, prep_llr


MARGIN = 16     # check symbols that are never erased


class RSCode(Code):
    family = "RS"
    soft = False
    has_check = True

    def __init__(self, name: str, n_sym: int, k_sym: int = 64, depth: int = 1):
        if not 0 < k_sym < n_sym or n_sym // depth > 255:
            raise ValueError("need 0 < k_sym < n_sym and words of at most 255 symbols")
        if n_sym % depth or k_sym % depth:
            raise ValueError("depth must divide n_sym and k_sym")
        self.name = name
        self.n_sym, self.k_sym, self.depth = n_sym, k_sym, depth
        self.t = (n_sym - k_sym) // depth // 2       # per word
        self.k = 8 * k_sym
        self.n = 8 * n_sym
        self.n_full, self.k_full = 255, 255 - (n_sym - k_sym) // depth
        self._gal = None

    @property
    def gal(self) -> galois.ReedSolomon:
        """The underlying RS(255, k') galois code, built on first use."""
        if self._gal is None:
            with numba_single_thread():
                self._gal = galois.ReedSolomon(self.n_full, self.k_full)
        return self._gal

    def describe(self) -> str:
        word = f"RS({self.n_sym // self.depth},{self.k_sym // self.depth})"
        depth = f"{self.depth} x " if self.depth > 1 else ""
        return (f"{self.name} (RS, {depth}{word} over GF(256), n={self.n}, "
                f"k={self.k}, t={self.t} symbols per word, R={self.rate:.3f})")

    def _words(self, frames: np.ndarray) -> np.ndarray:
        """(B, m * depth) bytes -> (B * depth, m): byte j goes to word j mod depth."""
        b = len(frames)
        return frames.reshape(b, -1, self.depth).transpose(0, 2, 1).reshape(b * self.depth, -1)

    def _frames(self, words: np.ndarray) -> np.ndarray:
        """Inverse of ``_words``."""
        return (words.reshape(-1, self.depth, words.shape[1]).transpose(0, 2, 1)
                .reshape(len(words) // self.depth, -1))

    def encode(self, msg):
        data = self._words(bits_to_bytes(check_msg(msg, self.k)))
        g = self.gal
        with numba_single_thread():
            cw = g.encode(g.field(data))
        return bytes_to_bits(self._frames(np.asarray(cw, dtype=np.uint8)))

    def decode(self, llr):
        r = self._words(bits_to_bytes(hard(prep_llr(llr, self.n))))
        g = self.gal
        with numba_single_thread():
            dec, nerr = g.decode(g.field(r), errors=True)
        ok = (np.asarray(nerr) >= 0).reshape(-1, self.depth).all(axis=1)
        return DecodeResult(bytes_to_bits(self._frames(np.asarray(dec, dtype=np.uint8))), ok)


class RSErasure(Code):
    """Errors-and-erasures decoder of a single-word ``RSCode`` (see module docstring)."""

    family = "RS"
    soft = True
    has_check = True

    def __init__(self, inner: RSCode, suffix: str = "_er", margin: int = MARGIN):
        if inner.depth != 1:
            raise ValueError("defined for a single codeword")
        self.inner = inner
        self.name = inner.name + suffix
        self.k, self.n = inner.k, inner.n
        self.erased = np.arange(0, inner.n_sym - inner.k_sym - margin + 1, 2)

    def encode(self, msg):
        return self.inner.encode(msg)

    def decode(self, llr):
        llr = prep_llr(llr, self.n)
        c, s = self.inner, self.erased
        b, frames = len(llr), np.arange(len(llr))
        rx = hard(llr)
        p_wrong = np.log1p(np.exp(-np.abs(llr))).reshape(b, c.n_sym, 8).sum(axis=2)
        rank = (-p_wrong).argsort(axis=1).argsort(axis=1)        # 0 = least reliable byte
        erasures = rank[:, None, :] < s[None, :, None]           # (b, candidates, n_sym)
        g = c.gal
        with numba_single_thread():
            words, nerr = g.decode(g.field(np.repeat(bits_to_bytes(rx), len(s), axis=0)),
                                   erasures=erasures.reshape(-1, c.n_sym),
                                   output="codeword", errors=True)
        ok = (np.asarray(nerr) >= 0).reshape(b, len(s))
        bits = bytes_to_bits(np.asarray(words, dtype=np.uint8)).reshape(b, len(s), self.n)
        fit = np.where(ok, (llr[:, None, :] * (1.0 - 2.0 * bits)).sum(axis=2), -np.inf)
        best = fit.argmax(axis=1)
        valid = ok[frames, best]
        # systematic: on failure ``msg`` = hard bits, as for the errors-only decoder
        msg = np.where(valid[:, None], bits[frames, best], rx)[:, :self.k]
        return DecodeResult(msg.astype(np.uint8), valid)

    def describe(self) -> str:
        return (f"{self.name} (RS, RS({self.inner.n_sym},{self.inner.k_sym}) errors-and-erasures, "
                f"n={self.n}, k={self.k}, up to {self.erased[-1]} erasures, R={self.rate:.3f})")


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("RS parameters are fixed for k = 512 (64 bytes)")
    plain = [RSCode("rs_r23", 96), RSCode("rs_r12", 128), RSCode("rs_r13", 192)]
    return (plain + [RSCode(f"{c.name}_i4", c.n_sym, depth=4) for c in plain]
            + [RSErasure(c) for c in plain])
