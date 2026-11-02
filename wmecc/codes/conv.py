"""Convolutional codes (K = 7), Sionna ``ConvEncoder`` / ``ViterbiDecoder``.

* ``conv_r12``: generators (171, 133) octal, rate 1/2, zero-terminated
  (6 tail bits): n = 2 (512 + 6) = 1036.
* ``conv_r13``: generators (133, 171, 165) octal, rate 1/3 (the LTE TBCC
  polynomials, here zero-terminated): n = 3 (512 + 6) = 1554.
* Decoder: ``ViterbiDecoder(method='soft_llr')`` (soft-input ML sequence
  decoding).  ``*_hard`` variants feed +-1 LLRs (HardInput); for Viterbi this
  is exactly hard-decision (Hamming-metric) decoding.
* No intrinsic check: ``has_check = False``, ``valid`` all True.
"""

from __future__ import annotations

from .base import Code, HardInput
from ._sionna import SionnaCode

__all__ = ["ConvCode", "codes"]


def _octal_to_bits(p: str) -> str:
    """'171' (octal) -> '1111001' (Sionna's binary gen_poly format)."""
    return format(int(p, 8), "b")


class ConvCode(SionnaCode):
    family = "Convolutional"
    soft = True
    has_check = False
    chunk = 1024

    def __init__(self, name: str, gen_poly_octal: tuple[str, ...], k: int = 512):
        super().__init__()
        self.name, self.k = name, k
        self.gen_poly_octal = tuple(gen_poly_octal)
        self.gen_poly = tuple(_octal_to_bits(p) for p in gen_poly_octal)
        blk = self.blocks
        self.n = int(blk["enc"](self._dummy(k)).shape[-1])

    @staticmethod
    def _dummy(k):
        import torch
        return torch.zeros(1, k)

    def _build(self) -> dict:
        from sionna.phy.fec.conv import ConvEncoder, ViterbiDecoder
        enc = ConvEncoder(gen_poly=self.gen_poly, terminate=True, device="cpu",
                          precision="single")
        dec = ViterbiDecoder(encoder=enc, method="soft_llr", return_info_bits=True,
                             device="cpu", precision="single")
        return {"enc": enc, "dec": dec}

    def _encode_t(self, u):
        return self.blocks["enc"](u)

    def _decode_t(self, logits):
        return self.blocks["dec"](logits), None

    def describe(self) -> str:
        return (f"{self.name} (conv K=7 ({','.join(self.gen_poly_octal)})_8 terminated, "
                f"n={self.n}, k={self.k}, R={self.rate:.3f}, sionna Viterbi soft_llr)")


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("codes are only configured for k = 512")
    r12 = ConvCode("conv_r12", ("171", "133"), k)
    r13 = ConvCode("conv_r13", ("133", "171", "165"), k)
    return [r12, r13, HardInput(r12), HardInput(r13)]
