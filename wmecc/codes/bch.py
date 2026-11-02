"""Binary BCH codes (narrow-sense, primitive, shortened to k = 512) --
thin wrapper around ``galois.BCH`` (galois 0.4.11).

* Mother codes ``galois.BCH(N, d=2t+1)`` (galois' default extension field,
  i.e. ``galois.matlab_primitive_poly(2, m)``), shortened by passing 512
  message bits to ``encode`` / ``n`` codeword bits to ``decode`` (galois'
  native shortened-code support).  Systematic: ``codeword[:, :512] == msg``.
* Hard-decision bounded-distance decoding by galois (Berlekamp-Massey +
  Chien); ``valid`` = galois did not report a failure (``errors == -1``).
  On failure galois returns the uncorrected word, so ``msg`` is then the hard
  decisions of the systematic part.

Codes (n, k, t), t = largest value whose mother-code dimension k' meets the
target: bch_r23 = (767, 512, 26) from BCH(1023, 768); bch_r12 =
(1022, 512, 57) from BCH(1023, 513); bch_r13 = (1535, 512, 106) from
BCH(2047, 1024).

Performance notes
-----------------
* The galois object is built lazily on first encode/decode (construction plus
  galois' first-call JIT costs ~5-15 s per code per process).
* galois' decoder calls a ``parallel=True`` numba kernel (polynomial
  evaluation) once per Chien-search position.  With several worker
  processes on a busy machine that turns into thousands of oversubscribed
  thread launches per frame (observed 10-200x slowdowns), so galois is
  called with numba limited to one thread (thread-local, restored after).
"""

from __future__ import annotations

from contextlib import contextmanager

import galois
import numba
import numpy as np

from .base import Code, DecodeResult, hard
from .simple import check_msg, prep_llr


@contextmanager
def numba_single_thread():
    """Run galois' numba kernels single-threaded (numba's setting is thread
    local; the previous value is restored)."""
    prev = numba.get_num_threads()
    numba.set_num_threads(1)
    try:
        yield
    finally:
        numba.set_num_threads(prev)


class BCHCode(Code):
    family = "BCH"
    soft = False
    has_check = True

    def __init__(self, name: str, n_full: int, k_full: int, t: int, k: int = 512):
        if not 0 < k <= k_full:
            raise ValueError(f"k={k} does not fit BCH({n_full}, {k_full})")
        self.name = name
        self.n_full, self.k_full, self.t, self.k = n_full, k_full, t, k
        self.n = k + (n_full - k_full)
        self._gal = None

    @property
    def gal(self) -> galois.BCH:
        """The underlying (unshortened) galois.BCH code, built on first use."""
        if self._gal is None:
            with numba_single_thread():
                g = galois.BCH(self.n_full, d=2 * self.t + 1)
            if (g.n, g.k, g.t) != (self.n_full, self.k_full, self.t):
                raise RuntimeError(f"galois built BCH({g.n},{g.k}) t={g.t}, expected "
                                   f"BCH({self.n_full},{self.k_full}) t={self.t}")
            self._gal = g
        return self._gal

    def describe(self) -> str:
        return (f"{self.name} (BCH, n={self.n}, k={self.k}, t={self.t}, "
                f"shortened from BCH({self.n_full},{self.k_full}), R={self.rate:.3f})")

    def encode(self, msg):
        msg = check_msg(msg, self.k)
        g = self.gal
        with numba_single_thread():
            cw = g.encode(g.field(msg))
        return np.asarray(cw, dtype=np.uint8)

    def decode(self, llr):
        r = hard(prep_llr(llr, self.n))
        g = self.gal
        with numba_single_thread():
            dec, nerr = g.decode(g.field(r), errors=True)
        return DecodeResult(np.asarray(dec, dtype=np.uint8), np.asarray(nerr) >= 0)


# (name, N, k', t)
SPECS = (("bch_r23", 1023, 768, 26),
         ("bch_r12", 1023, 513, 57),
         ("bch_r13", 2047, 1024, 106))


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("BCH parameters are fixed for k = 512")
    return [BCHCode(name, N, kf, t, k) for name, N, kf, t in SPECS]
