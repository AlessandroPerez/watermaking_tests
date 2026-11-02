"""5G NR polar codes (3GPP TS 38.212, uplink/UCI), Sionna ``Polar5GEncoder`` /
``Polar5GDecoder``.

* ``polar_r12``: A = 512 message bits, E = n = 1024, CRC11 (the UCI CRC for
  A >= 20), K = 523, mother code N = 1024 (no puncturing/shortening),
  5G reliability sequence, sub-block and channel (uplink) interleavers.
* ``polar_r23`` (n = 768), ``polar_r34`` (n = 684): same CRC and K; rate matching
  by shortening down from N = 1024.
* ``polar_r14``: Sionna's 5G rate matching is limited to E <= 1088 (no code
  block segmentation).  For A = 512 and E = 2048 the standard itself
  prescribes segmentation (I_seg = 1 since A >= 360 and E >= 1088, 38.212
  6.3.1.2.1): two code blocks of A' = 256 bits, each with its own CRC11
  (K = 267), rate-matched to E_r = 1024 (N = 1024), concatenated in order
  (5.2.1 / 5.5).  This is implemented by splitting the message in two halves
  and running each through ``Polar5GEncoder(256, 1024)``; ``valid`` requires
  both CRCs to pass.  n = 2048.
* Decoder: ``Polar5GDecoder(dec_type='SCL', list_size=8,
  return_crc_status=True)`` -- CRC-aided fast SCL (LLR-based path metric;
  rate-1 nodes use Sionna's single-flip approximation).  ``valid`` is
  Sionna's CRC status.
* Note: CRC11 with L = 8 is a weak integrity check: measured false "valid"
  on pure-noise LLRs ~0.25 % (polar_r12, 10/4096; ~L * 2^-11) and ~1 % of
  AWGN frame errors pass the CRC.  polar_r14 needs both blocks to pass
  (0/2048 on noise).
"""

from __future__ import annotations

import numpy as np

from .base import Code, HardInput
from ._sionna import SionnaCode

__all__ = ["Polar5GCode", "codes"]


class Polar5GCode(SionnaCode):
    family = "Polar"
    soft = True
    has_check = True
    chunk = 256

    def __init__(self, name: str, n: int, k: int = 512, segments: int = 1, list_size: int = 8):
        super().__init__()
        if k % segments or n % segments:
            raise ValueError("k and n must split evenly into segments")
        self.name, self.n, self.k = name, n, k
        self.segments, self.list_size = segments, list_size
        enc = self.blocks["enc"]
        self.k_polar, self.n_polar = enc.k_polar, enc.n_polar
        self.crc_length = enc.enc_crc.crc_length
        assert enc.n == n // segments and enc.k == k // segments

    def _build(self) -> dict:
        from sionna.phy.fec.polar import Polar5GDecoder, Polar5GEncoder
        enc = Polar5GEncoder(self.k // self.segments, self.n // self.segments,
                             channel_type="uplink", device="cpu", precision="single")
        dec = Polar5GDecoder(enc, dec_type="SCL", list_size=self.list_size,
                             return_crc_status=True, device="cpu", precision="single")
        return {"enc": enc, "dec": dec}

    def _encode_t(self, u):
        b = u.shape[0]
        s = self.segments
        cw = self.blocks["enc"](u.reshape(b * s, self.k // s))
        return cw.reshape(b, self.n)

    def _decode_t(self, logits):
        b = logits.shape[0]
        s = self.segments
        u_hat, crc_ok = self.blocks["dec"](logits.reshape(b * s, self.n // s))
        ok = crc_ok.reshape(b, s).all(dim=1).numpy()
        return u_hat.reshape(b, self.k), ok

    def describe(self) -> str:
        seg = f"{self.segments} x " if self.segments > 1 else ""
        return (f"{self.name} (5G NR polar UL, {seg}(N={self.n_polar}, K={self.k_polar} incl. "
                f"CRC{self.crc_length}), n={self.n}, k={self.k}, R={self.rate:.3f}, "
                f"sionna CA-SCL L={self.list_size})")


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("codes are only configured for k = 512")
    r12 = Polar5GCode("polar_r12", 1024, k)
    r14 = Polar5GCode("polar_r14", 2048, k, segments=2)
    return [r12, r14, HardInput(r12), Polar5GCode("polar_r23", 768, k), Polar5GCode("polar_r34", 684, k)]
