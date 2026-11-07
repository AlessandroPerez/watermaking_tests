"""Semi-blind codes: a known 128-bit header and a random 384-bit ID.

The 512-bit message is a fixed 128-bit header, known to the decoder, followed by a
384-bit ID drawn at random for each image. The header says that the image carries
our watermark; the ID identifies the image. Two ways to join them:

* ``*_split`` (encode, then join): each part is encoded on its own by the same code
  (same family, same rate) and the two codewords are embedded side by side,
  ``header codeword | ID codeword``. The header codeword is known in full, so the
  decoder can count how many extracted bits agree with it before decoding anything
  (a detector whose false-positive rate follows from the binomial law) and use it
  as a pilot.
* ``*_joint`` (join, then encode): ``header | ID`` is encoded as one 512-bit message
  by the code of the same name in its own module, as in the earlier runs. The
  header is checked after decoding: it acts as a 128-bit check on the whole word.
  5G LDPC never sends its first 128 information bits, so here the header is not in
  the codeword at all, only implied by the parity bits.
* ``ldpc_r12_jidh`` (join the other way, then encode): ``ID | header``. The same code,
  but the header now falls on information bits that are sent as they are (codeword
  positions 256-383): they are a 128-bit pilot that can be counted before decoding,
  and once that count has flagged the image the decoder can fix them to the known
  header and decode only the ID (``decode_known``).

Codes: no ECC (both ways are the same bits), and 5G LDPC, 5G polar and LTE turbo,
all at rate 1/2.

The module is not in the default registry: a config selects it with
``code_modules: [split]``.
"""

from __future__ import annotations

import numpy as np

from .base import Code, DecodeResult
from .ldpc import LDPC5GCode
from .polar import Polar5GCode
from .simple import Uncoded, check_msg, prep_llr
from .turbo import TurboCode

__all__ = ["HEADER_BITS", "ID_BITS", "JointCode", "SplitCode", "codes"]

HEADER_BITS, ID_BITS = 128, 384


class SplitCode(Code):
    """Header codeword followed by ID codeword; ``decode`` decodes both."""

    def __init__(self, name: str, header: Code, ident: Code, inner: "SplitCode | None" = None):
        if (header.k, ident.k) != (HEADER_BITS, ID_BITS):
            raise ValueError(f"need k = {HEADER_BITS} and {ID_BITS}, got {header.k} and {ident.k}")
        self.name, self.header, self.ident = name, header, ident
        self.family, self.soft, self.has_check = ident.family, ident.soft, ident.has_check
        self.k, self.n = header.k + ident.k, header.n + ident.n
        self.n_header = header.n
        self.pilot = np.arange(header.n)        # codeword positions fixed by the header
        self.design = "uncoded" if ident.family == "Uncoded" else "split"
        if inner is not None:       # decoder variant: the experiment reuses inner's embedding
            self.inner = inner

    def encode(self, msg):
        msg = check_msg(msg, self.k)
        return np.concatenate([self.header.encode(msg[:, :HEADER_BITS]),
                               self.ident.encode(msg[:, HEADER_BITS:])], axis=1)

    def decode_parts(self, llr) -> tuple[DecodeResult, DecodeResult]:
        llr = prep_llr(llr, self.n)
        return self.header.decode(llr[:, :self.n_header]), self.ident.decode(llr[:, self.n_header:])

    def decode(self, llr):
        h, i = self.decode_parts(llr)
        return DecodeResult(np.concatenate([h.msg, i.msg], axis=1), h.valid & i.valid)

    def describe(self) -> str:
        return (f"{self.name} (header {self.header.describe()}; ID {self.ident.describe()}; "
                f"n={self.n})")


class JointCode(Code):
    """The header and the ID encoded as one message by ``code``; ``decode_parts`` splits
    the result. ``header_last`` encodes ``ID | header`` instead of ``header | ID``; the
    codeword positions that carry header bits as they are become the pilot."""

    BIG = 50.0            # LLR given to a known bit (the Sionna wrappers clip at 50)

    def __init__(self, name: str, code: Code, header_last: bool = False):
        if code.k != HEADER_BITS + ID_BITS:
            raise ValueError(f"need k = {HEADER_BITS + ID_BITS}, got {code.k}")
        self.name, self.code, self.header_last = name, code, header_last
        self.family, self.soft, self.has_check = code.family, code.soft, code.has_check
        self.k, self.n = code.k, code.n
        self.design = "joint_idh" if header_last else "joint"
        self.pilot = self._systematic_header() if header_last else np.arange(0)
        self.n_header = len(self.pilot)

    def _order(self, msg):                 # header | ID  ->  the code's message order
        return np.concatenate([msg[:, HEADER_BITS:], msg[:, :HEADER_BITS]], axis=1) \
            if self.header_last else msg

    def _systematic_header(self) -> np.ndarray:
        """Codeword position of each header bit (in header order); all must be sent."""
        m = np.random.default_rng(0).integers(0, 2, (64, self.k), dtype=np.uint8)
        c = self.encode(m)
        pos = []
        for b in range(HEADER_BITS):
            hit = np.flatnonzero((c == m[:, [b]]).all(axis=0))
            if len(hit) != 1:
                raise ValueError(f"{self.name}: header bit {b} is not sent as it is")
            pos.append(hit[0])
        return np.array(pos)

    def encode(self, msg):
        return self.code.encode(self._order(check_msg(msg, self.k)))

    def _parts(self, r: DecodeResult) -> tuple[DecodeResult, DecodeResult]:
        h, i = ((r.msg[:, ID_BITS:], r.msg[:, :ID_BITS]) if self.header_last
                else (r.msg[:, :HEADER_BITS], r.msg[:, HEADER_BITS:]))
        return DecodeResult(h, r.valid), DecodeResult(i, r.valid)

    def decode(self, llr):
        h, i = self._parts(self.code.decode(llr))
        return DecodeResult(np.concatenate([h.msg, i.msg], axis=1), h.valid)

    def decode_parts(self, llr) -> tuple[DecodeResult, DecodeResult]:
        return self._parts(self.code.decode(prep_llr(llr, self.n)))

    def decode_known(self, llr, header: np.ndarray) -> tuple[DecodeResult, DecodeResult]:
        """Decode with the header bits fixed to ``header`` (after the pilot has flagged
        the frame): only the ID is left to the decoder."""
        if not self.n_header:
            raise ValueError(f"{self.name} does not send its header bits")
        llr = np.array(prep_llr(llr, self.n), dtype=float)
        llr[:, self.pilot] = self.BIG * (1.0 - 2.0 * np.asarray(header, float))
        return self.decode_parts(llr)

    def describe(self) -> str:
        order = "ID | header" if self.header_last else "header | ID"
        return f"{self.name} ({order} encoded together by {self.code.describe()})"


def _split(name: str, make) -> SplitCode:
    return SplitCode(name, make(HEADER_BITS), make(ID_BITS))


def codes(k: int = 512) -> list[Code]:
    if k != HEADER_BITS + ID_BITS:
        raise NotImplementedError("the split is fixed at 128 + 384 bits")
    full = HEADER_BITS + ID_BITS
    return [
        SplitCode("uncoded", Uncoded(HEADER_BITS), Uncoded(ID_BITS)),
        _split("ldpc_r12_split", lambda kk: LDPC5GCode(f"ldpc_r12_k{kk}", 2 * kk, kk)),
        _split("polar_r12_split", lambda kk: Polar5GCode(f"polar_r12_k{kk}", 2 * kk, kk)),
        _split("turbo_r12_split", lambda kk: TurboCode(f"turbo_r12_k{kk}", 1 / 2, kk)),
        JointCode("ldpc_r12_joint", LDPC5GCode("ldpc_r12", 1024, full)),
        JointCode("polar_r12_joint", Polar5GCode("polar_r12", 1024, full)),
        JointCode("turbo_r12_joint", TurboCode("turbo_r12", 1 / 2, full)),
        JointCode("ldpc_r12_jidh", LDPC5GCode("ldpc_r12", 1024, full), header_last=True),
    ]
