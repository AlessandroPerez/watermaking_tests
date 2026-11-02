"""5G NR LDPC codes (3GPP TS 38.212), Sionna ``LDPC5GEncoder`` / ``LDPC5GDecoder``.

* k = 512 -> base graph 2, lifting size Z = 64 (K_ldpc = 640 incl. 128
  filler bits, mother code N = 52 Z = 3328); the first 2Z systematic bits are
  punctured and the rate matcher (RV 0) takes the first n bits of the
  circular buffer.
* ``ldpc_r12`` n = 1024, ``ldpc_r13`` n = 1536, ``ldpc_r14`` n = 2048.
* ``ldpc_r23`` n = 768 (base graph 2) and ``ldpc_r34`` n = 684 (rate > 0.67, so
  Sionna selects base graph 1 as 38.212 prescribes; the numbers above are BG2).
* Decoder: flooding belief propagation, check-node rule ``boxplus``
  (exact sum-product in the tanh domain; same FER as Sionna's default
  ``boxplus-phi`` on AWGN and ~25 % faster), ``num_iter`` = 100, Sionna's
  internal message clipping (20) and pruning of punctured degree-1 nodes
  (default).  Sionna has NO early stopping: every frame runs all
  ``num_iter`` iterations (on AWGN 50 iterations give the same FER at half
  the cost; 20 cost ~0.2 dB).
* ``valid``: zero syndrome of the decoder's final hard decisions over the
  decoder's own (pruned) parity-check matrix, i.e. the decoded word is a
  codeword.  The final variable-node estimates are read from Sionna through
  its documented ``v2c_callbacks`` hook (called after every VN update with
  ``x_hat``); the parity-check matrix is ``decoder.pcm``.
"""

from __future__ import annotations

import numpy as np

from .base import Code, HardInput
from ._sionna import SionnaCode

__all__ = ["LDPC5GCode", "codes"]


class _LastEstimate:
    """Sionna v2c callback keeping the latest VN estimate (internal LLRs,
    log P0/P1) of the running decode call."""

    def __init__(self):
        self.x_hat = None

    def __call__(self, msg_vn, it, x_hat):
        self.x_hat = x_hat
        return msg_vn


class LDPC5GCode(SionnaCode):
    family = "LDPC"
    soft = True
    has_check = True
    chunk = 256

    def __init__(self, name: str, n: int, k: int = 512, num_iter: int = 100,
                 cn_update: str = "boxplus"):
        super().__init__()
        self.name, self.n, self.k = name, n, k
        self.num_iter, self.cn_update = num_iter, cn_update
        enc = self.blocks["enc"]
        assert enc.n == n and enc.k == k
        self.base_graph, self.z = enc._bg, enc.z

    def _build(self) -> dict:
        import scipy.sparse as sp
        from sionna.phy.fec.ldpc import LDPC5GDecoder, LDPC5GEncoder
        enc = LDPC5GEncoder(self.k, self.n, device="cpu", precision="single")
        cb = _LastEstimate()
        dec = LDPC5GDecoder(enc, cn_update=self.cn_update, num_iter=self.num_iter,
                            hard_out=True, return_infobits=True, v2c_callbacks=[cb],
                            device="cpu", precision="single")
        pcm = sp.csr_matrix(dec.pcm, dtype=np.int32)
        return {"enc": enc, "dec": dec, "cb": cb, "pcm": pcm}

    def _encode_t(self, u):
        return self.blocks["enc"](u)

    def _decode_t(self, logits):
        blk = self.blocks
        cb = blk["cb"]
        cb.x_hat = None
        u_hat = blk["dec"](logits)
        if cb.x_hat is None:              # num_iter == 0
            return u_hat, np.zeros(u_hat.shape[0], dtype=bool)
        # same decision rule as Sionna's hard output: bit = 1 iff LLR <= 0
        bits = (cb.x_hat.reshape(u_hat.shape[0], -1) <= 0).numpy().astype(np.int32)
        cb.x_hat = None
        syndrome = blk["pcm"] @ bits.T          # (m, b)
        return u_hat, ~(syndrome & 1).any(axis=0)

    @property
    def H(self):
        """Pruned parity-check matrix used by the decoder (scipy CSR)."""
        return self.blocks["pcm"]

    def describe(self) -> str:
        return (f"{self.name} (5G NR LDPC BG{self.base_graph[-1]} Z={self.z}, n={self.n}, "
                f"k={self.k}, R={self.rate:.3f}, sionna BP {self.cn_update} x{self.num_iter})")


_RATES = {"r12": 1024, "r13": 1536, "r14": 2048, "r23": 768, "r34": 684}


def codes(k: int = 512) -> list[Code]:
    if k != 512:
        raise NotImplementedError("codes are only configured for k = 512")
    soft = [LDPC5GCode(f"ldpc_{tag}", n, k) for tag, n in _RATES.items()]
    return soft + [HardInput(soft[0])]
