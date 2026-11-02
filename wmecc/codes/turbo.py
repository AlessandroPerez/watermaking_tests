"""LTE turbo code (3GPP TS 36.212), Sionna ``TurboEncoder`` / ``TurboDecoder``.

* Two 8-state RSC constituents (constraint_length=4: g0 = 13, g1 = 15 octal,
  feedback 13), Sionna's 3GPP QPP internal interleaver (``"3GPP"``) for
  K = 512, trellis termination (12 tail bits).
* ``turbo_r13``: rate 1/3, n = 3 * 512 + 12 = 1548.
* ``turbo_r12``: Sionna's rate-1/2 puncturing (pattern [[1,1,0],[1,0,1]]:
  systematic always, parities alternate), terminated: n = 1032.
* Decoder: iterative BCJR, 8 iterations, ``algorithm`` = ``"log"`` (exact
  log-MAP, Sionna offers it at ~1.4x the cost of max-log; ``"maxlog"`` is
  available via the constructor).  No extrinsic scaling option in Sionna.
* No intrinsic check: ``has_check = False``, ``valid`` all True.
* Speed: Sionna's BCJR loops over trellis steps in Python, so each decode
  call has a ~1.6 s fixed cost; pass large batches (12.7 ms/frame at
  B = 1024, 19 ms at B = 256, 117 ms at B = 16).
"""

from __future__ import annotations

from .base import Code, HardInput
from ._sionna import SionnaCode

__all__ = ["TurboCode", "codes"]


class TurboCode(SionnaCode):
    family = "Turbo"
    soft = True
    has_check = False
    chunk = 1024        # the BCJR loops over trellis steps in Python: big chunks amortize it

    def __init__(self, name: str, rate: float, k: int = 512, num_iter: int = 8,
                 algorithm: str = "log"):
        super().__init__()
        self.name, self.k = name, k
        self.design_rate, self.num_iter, self.algorithm = rate, num_iter, algorithm
        import torch
        self.n = int(self.blocks["enc"](torch.zeros(1, k)).shape[-1])

    def _build(self) -> dict:
        from sionna.phy.fec.turbo import TurboDecoder, TurboEncoder
        enc = TurboEncoder(constraint_length=4, rate=self.design_rate, terminate=True,
                           interleaver_type="3GPP", device="cpu", precision="single")
        dec = TurboDecoder(enc, num_iter=self.num_iter, algorithm=self.algorithm,
                           hard_out=True, device="cpu", precision="single")
        return {"enc": enc, "dec": dec}

    def _encode_t(self, u):
        return self.blocks["enc"](u)

    def _decode_t(self, logits):
        return self.blocks["dec"](logits), None

    def describe(self) -> str:
        return (f"{self.name} (LTE turbo (13,15)_8 QPP terminated, n={self.n}, k={self.k}, "
                f"R={self.rate:.3f}, sionna BCJR {self.algorithm} x{self.num_iter})")


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("codes are only configured for k = 512")
    r13 = TurboCode("turbo_r13", 1 / 3, k)
    r12 = TurboCode("turbo_r12", 1 / 2, k)
    return [r13, r12, HardInput(r13)]
