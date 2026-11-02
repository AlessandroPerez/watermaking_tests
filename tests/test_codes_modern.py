"""Tests for the Sionna-backed codes: convolutional, 5G LDPC, 5G polar, LTE turbo.

The wrappers only adapt Sionna to base.py; these tests check the adaptation
(LLR sign, shapes/dtypes, exact n, valid flags, chunking, pickling, garbage
inputs) plus a light AWGN sanity check.
"""

from __future__ import annotations

import pickle
import warnings

import numpy as np
import pytest

from wmecc.codes import conv, ldpc, polar, turbo
from wmecc.codes.base import Code, HardInput, simulate_awgn

warnings.filterwarnings("ignore", message=".*sionna.rt.*")

K = 512
MODULES = (conv, ldpc, polar, turbo)
EXPECTED_N = {
    "conv_r12": 1036, "conv_r13": 1554, "conv_r12_hard": 1036, "conv_r13_hard": 1554,
    "ldpc_r12": 1024, "ldpc_r13": 1536, "ldpc_r14": 2048, "ldpc_r12_hard": 1024,
    "ldpc_r23": 768, "ldpc_r34": 684,
    "polar_r12": 1024, "polar_r14": 2048, "polar_r12_hard": 1024,
    "polar_r23": 768, "polar_r34": 684,
    "turbo_r13": 1548, "turbo_r12": 1032, "turbo_r13_hard": 1548,
}
WITH_CHECK = {"ldpc_r12", "ldpc_r13", "ldpc_r14", "ldpc_r12_hard", "ldpc_r23", "ldpc_r34",
              "polar_r12", "polar_r14", "polar_r12_hard", "polar_r23", "polar_r34"}


@pytest.fixture(scope="module")
def all_codes() -> dict[str, Code]:
    return {c.name: c for m in MODULES for c in m.codes(K)}


def _msgs(b: int, seed: int = 0) -> np.ndarray:
    m = np.random.default_rng(seed).integers(0, 2, size=(b, K), dtype=np.uint8)
    m[0] = 0
    m[1] = 1
    return m


def _bpsk_llr(cw: np.ndarray, ebn0_db: float, k: int, rng) -> np.ndarray:
    esn0 = 10 ** (ebn0_db / 10) * k / cw.shape[1]
    s2 = 1.0 / (2 * esn0)
    y = (1.0 - 2.0 * cw) + rng.normal(0.0, np.sqrt(s2), size=cw.shape)
    return 2.0 * y / s2


# ------------------------------------------------------------------ registry
def test_registry(all_codes):
    assert set(all_codes) == set(EXPECTED_N)
    for name, c in all_codes.items():
        assert "/" not in name
        assert c.k == K and c.n == EXPECTED_N[name], (name, c.n)
        assert c.soft == (not name.endswith("_hard"))
        assert c.has_check == (name in WITH_CHECK)
        assert isinstance(c.describe(), str)
    for m in MODULES:
        with pytest.raises(NotImplementedError):
            m.codes(256)


# ------------------------------------------------------------------ round trips
@pytest.mark.parametrize("name", sorted(EXPECTED_N))
def test_noiseless_roundtrip(all_codes, name):
    c = all_codes[name]
    msgs = _msgs(6)
    cw = c.encode(msgs)
    assert cw.shape == (6, c.n) and cw.dtype == np.uint8
    assert set(np.unique(cw)) <= {0, 1}
    np.testing.assert_array_equal(c.encode(msgs), cw)          # deterministic
    for amp in (1.0, 8.0):
        res = c.decode(amp * (1.0 - 2.0 * cw.astype(np.float64)))
        assert res.msg.shape == (6, K) and res.msg.dtype == np.uint8
        assert res.valid.shape == (6,) and res.valid.dtype == bool
        np.testing.assert_array_equal(res.msg, msgs)
        assert res.valid.all()


@pytest.mark.parametrize("name", ["conv_r12", "ldpc_r12", "turbo_r13"])
def test_llr_sign_convention(all_codes, name):
    # positive LLR => bit 0: feeding the negated LLRs must break decoding
    c = all_codes[name]
    msgs = _msgs(4, 1)
    llr = 4.0 * (1.0 - 2.0 * c.encode(msgs))
    bad = c.decode(-llr)
    assert np.any(bad.msg != msgs, axis=1).all()
    if c.has_check:
        assert not bad.valid.any()


# ------------------------------------------------------------------ valid flags
def test_ldpc_valid_is_codeword_check():
    c = ldpc.LDPC5GCode("ldpc_test", 1024, num_iter=20)
    rng = np.random.default_rng(3)
    msgs = rng.integers(0, 2, size=(40, K), dtype=np.uint8)
    llr = _bpsk_llr(c.encode(msgs), 0.75, K, rng)       # below threshold: mostly failures
    llr[:20] = 6.0 * (1.0 - 2.0 * c.encode(msgs[:20]))  # half the frames are clean
    res = c.decode(llr)
    ok = np.all(res.msg == msgs, axis=1)
    assert res.valid[:20].all() and ok[:20].all()
    assert (~ok[20:]).sum() >= 5
    assert not (res.valid & ~ok).any()                 # every failure flagged (no false valid)
    # (valid may be False while the info bits are already right: parity not converged)
    assert c.H.shape[1] > c.n                            # syndrome over the mother code graph


def test_polar_segmented_crc():
    c = {x.name: x for x in polar.codes(K)}["polar_r14"]
    assert c.segments == 2 and c.crc_length == 11 and c.k_polar == 256 + 11
    msgs = _msgs(4, 5)
    llr = 6.0 * (1.0 - 2.0 * c.encode(msgs))
    llr[:, 1024:] = np.random.default_rng(0).normal(0, 3, size=(4, 1024))  # destroy block 2
    res = c.decode(llr)
    np.testing.assert_array_equal(res.msg[:, :256], msgs[:, :256])         # block 1 intact
    assert not res.valid.any()


# ------------------------------------------------------------------ plumbing
@pytest.mark.parametrize("name", ["conv_r13", "ldpc_r12", "polar_r14", "turbo_r12"])
def test_chunking_batch_and_pickle(all_codes, name):
    c = all_codes[name]
    rng = np.random.default_rng(7)
    msgs = rng.integers(0, 2, size=(5, K), dtype=np.uint8)
    llr = _bpsk_llr(c.encode(msgs), 1.0, K, rng)
    ref = c.decode(llr)
    c2 = pickle.loads(pickle.dumps(c))       # Sionna blocks are rebuilt lazily
    c2.chunk = 2
    np.testing.assert_array_equal(c2.encode(msgs), c.encode(msgs))
    r2 = c2.decode(llr)
    np.testing.assert_array_equal(r2.msg, ref.msg)
    np.testing.assert_array_equal(r2.valid, ref.valid)
    r3 = c.decode(llr[3:4])
    np.testing.assert_array_equal(r3.msg[0], ref.msg[3])


def test_hard_input_wrapper(all_codes):
    for name in ("conv_r12_hard", "ldpc_r12_hard", "polar_r12_hard", "turbo_r13_hard"):
        c = all_codes[name]
        assert isinstance(c, HardInput) and c.inner.name == name[:-5]


# ------------------------------------------------------------------ garbage
def _garbage(n: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(11)
    return {
        "noise": rng.normal(0.0, 3.0, size=(16, n)),
        "zeros": np.zeros((2, n)),
        "plus_big": np.full((2, n), 1e6),
        "minus_big": np.full((2, n), -1e6),
        "random_big": rng.choice([-1e6, 1e6], size=(3, n)),
        "nonfinite": np.where(rng.random((2, n)) < 0.5, np.nan, np.inf) * rng.choice([-1, 1], (2, n)),
    }


@pytest.mark.parametrize("name", sorted(EXPECTED_N))
def test_garbage_inputs(all_codes, name):
    c = all_codes[name]
    for kind, llr in _garbage(c.n).items():
        res = c.decode(llr)
        assert res.msg.shape == (llr.shape[0], K) and res.msg.dtype == np.uint8, kind
        assert set(np.unique(res.msg)) <= {0, 1}
        assert res.valid.dtype == bool
        if not c.has_check:
            assert res.valid.all()
        elif kind in ("noise", "random_big", "minus_big", "nonfinite"):
            assert not res.valid.any(), (name, kind)
        elif kind == "plus_big":
            # constant "all bits 0" evidence decodes to the all-zero codeword,
            # which IS a codeword of these linear codes (see report)
            assert res.valid.all() and not res.msg.any()


# ------------------------------------------------------------------ AWGN sanity
@pytest.mark.parametrize("name,ebn0,trials,max_fer", [
    ("conv_r12", 4.5, 256, 0.05), ("ldpc_r12", 2.5, 64, 0.05),
    ("polar_r12", 2.5, 128, 0.05), ("turbo_r13", 1.5, 256, 0.05),
])
def test_awgn_sanity(all_codes, name, ebn0, trials, max_fer):
    c = all_codes[name]
    r = simulate_awgn(c, ebn0, trials, rng=np.random.default_rng(123), batch=trials)
    assert r["fer"] <= max_fer, r
    if c.has_check:
        assert r["false_valid_rate"] == 0.0
