"""Tests for the classical-code wrappers: simple (komm), bch / rs (galois)."""

from __future__ import annotations

import pickle

import numpy as np
import pytest

from wmecc.codes import bch, rs, simple
from wmecc.codes.base import HardInput, simulate_awgn

K = 512

EXPECTED = {  # name: (n, soft, has_check, t)
    "uncoded": (512, False, False, None),
    "rep2": (1024, True, False, None),
    "rep3": (1536, True, False, None),
    "rep4": (2048, True, False, None),
    "rep3_hard": (1536, False, False, None),
    "hamming74": (896, True, False, None),
    "hamming74_hard": (896, False, False, None),
    "bch_r23": (767, False, True, 26),
    "bch_r12": (1022, False, True, 57),
    "bch_r13": (1535, False, True, 106),
    "rs_r23": (768, False, True, 16),
    "rs_r12": (1024, False, True, 32),
    "rs_r13": (1536, False, True, 64),
    "rs_r23_i4": (768, False, True, 4),
    "rs_r12_i4": (1024, False, True, 8),
    "rs_r13_i4": (1536, False, True, 16),
    "rs_r23_er": (768, True, True, None),
    "rs_r12_er": (1024, True, True, None),
    "rs_r13_er": (1536, True, True, None),
}


@pytest.fixture(scope="module")
def all_codes():
    return {c.name: c for c in simple.codes() + bch.codes() + rs.codes()}


@pytest.fixture(scope="module", params=sorted(EXPECTED))
def code(request, all_codes):
    return all_codes[request.param]


def bpsk_llr(cw, amp=4.0):
    return amp * (1.0 - 2.0 * cw)


# ------------------------------------------------------------ generic

def test_registry(all_codes):
    assert sorted(all_codes) == sorted(EXPECTED)
    for name, c in all_codes.items():
        n, soft, has_check, t = EXPECTED[name]
        assert "/" not in name
        assert (c.k, c.n, c.soft, c.has_check) == (K, n, soft, has_check), name
        if t is not None:
            assert c.t == t
    with pytest.raises(NotImplementedError):
        bch.codes(256)
    with pytest.raises(NotImplementedError):
        rs.codes(256)


def test_galois_parameters(all_codes):
    for name in ("bch_r23", "bch_r12", "bch_r13"):
        c = all_codes[name]
        g = c.gal
        assert (g.n, g.k, g.t) == (c.n_full, c.k_full, c.t)
        assert c.n == g.n - (g.k - K)
    for name in ("rs_r23", "rs_r12", "rs_r13", "rs_r23_i4", "rs_r12_i4", "rs_r13_i4"):
        c = all_codes[name]
        assert (c.gal.n, c.gal.k, c.gal.t) == (255, 255 - 2 * c.t, c.t)


def test_roundtrip_noiseless(code):
    rng = np.random.default_rng(1)
    msg = rng.integers(0, 2, (50, K), dtype=np.uint8)
    cw = code.encode(msg)
    assert cw.shape == (50, code.n) and cw.dtype == np.uint8
    assert set(np.unique(cw)) <= {0, 1}
    for amp in (0.3, 4.0, 1e6):
        res = code.decode(bpsk_llr(cw, amp))
        assert res.msg.shape == (50, K) and res.msg.dtype == np.uint8
        assert res.valid.shape == (50,) and res.valid.dtype == bool
        assert np.array_equal(res.msg, msg)
        assert res.valid.all()


def test_bad_shapes(code):
    with pytest.raises(ValueError):
        code.encode(np.zeros((2, K + 1), np.uint8))
    with pytest.raises(ValueError):
        code.decode(np.zeros((2, code.n + 1)))


def test_garbage_input_no_crash(code):
    rng = np.random.default_rng(2)
    B = 50
    inputs = {
        "zeros": np.zeros((B, code.n)),
        "huge": rng.choice([-1e6, 1e6], size=(B, code.n)),
        "noise": 3.0 * rng.normal(size=(B, code.n)),
        "nonfinite": np.where(rng.random((B, code.n)) < 0.1, np.nan,
                              rng.choice([-np.inf, np.inf, 1.0, -1.0], size=(B, code.n))),
    }
    for kind, llr in inputs.items():
        res = code.decode(llr)
        assert res.msg.shape == (B, K) and res.msg.dtype == np.uint8, kind
        assert set(np.unique(res.msg)) <= {0, 1}
        assert res.valid.shape == (B,) and res.valid.dtype == bool
        if code.has_check and kind in ("huge", "noise"):
            assert res.valid.sum() == 0, (code.name, kind)
        if not code.has_check:
            assert res.valid.all()


def test_all_zero_llr_decodes_to_zero_codeword(all_codes):
    # Inherent to linear codes without coset scrambling: all-zero LLRs give
    # the all-zero hard word, which IS a codeword -> valid all-zero message.
    for name in ("bch_r23", "rs_r12"):
        res = all_codes[name].decode(np.zeros((3, all_codes[name].n)))
        assert res.valid.all() and not res.msg.any()


def test_pickle_roundtrip(all_codes):
    rng = np.random.default_rng(3)
    for name in ("rep3_hard", "hamming74", "bch_r12", "rs_r13"):
        c2 = pickle.loads(pickle.dumps(all_codes[name]))
        msg = rng.integers(0, 2, (5, K), dtype=np.uint8)
        assert np.array_equal(c2.decode(bpsk_llr(c2.encode(msg))).msg, msg)


# ------------------------------------------------------------ layouts

def test_layouts(all_codes):
    rng = np.random.default_rng(4)
    msg = rng.integers(0, 2, (10, K), dtype=np.uint8)
    assert np.array_equal(all_codes["uncoded"].encode(msg), msg)
    for r in (2, 3, 4):   # copy j of bit i at j*k + i
        assert np.array_equal(all_codes[f"rep{r}"].encode(msg), np.tile(msg, (1, r)))
    cw = all_codes["hamming74"].encode(msg).reshape(10, K // 4, 7)
    assert np.array_equal(cw[:, :, :4].reshape(10, K), msg)          # [d1..d4 p1 p2 p3] per block
    d = cw[:, :, :4].astype(int)
    assert np.array_equal(cw[:, :, 4], (d[..., 0] + d[..., 1] + d[..., 3]) % 2)
    assert np.array_equal(cw[:, :, 5], (d[..., 0] + d[..., 2] + d[..., 3]) % 2)
    assert np.array_equal(cw[:, :, 6], (d[..., 1] + d[..., 2] + d[..., 3]) % 2)
    for name in ("bch_r23", "bch_r12", "bch_r13", "rs_r23", "rs_r12", "rs_r13"):
        assert np.array_equal(all_codes[name].encode(msg)[:, :K], msg), name   # systematic


# ------------------------------------------------------------ soft decoders

@pytest.mark.parametrize("name", ["rep2", "rep3", "rep4", "hamming74"])
def test_llr_scaling_invariance(all_codes, name):
    c = all_codes[name]
    rng = np.random.default_rng(5)
    msg = rng.integers(0, 2, (100, K), dtype=np.uint8)
    llr = (1.0 - 2.0 * c.encode(msg)) + rng.normal(0, 1.0, (100, c.n))
    ref = c.decode(llr).msg
    for s in (0.01, 0.37, 9.0):
        assert np.array_equal(c.decode(s * llr).msg, ref)


def test_repetition_is_llr_sum(all_codes):
    rng = np.random.default_rng(6)
    for r in (2, 3, 4):
        c = all_codes[f"rep{r}"]
        llr = rng.normal(0, 2.0, (40, c.n))
        expect = (llr.reshape(40, r, K).sum(axis=1) < 0).astype(np.uint8)
        assert np.array_equal(c.decode(llr).msg, expect)


def test_rep3_hard_is_majority(all_codes):
    rng = np.random.default_rng(7)
    llr = rng.normal(0, 1.0, (40, 3 * K))
    hb = (llr < 0).reshape(40, 3, K).sum(axis=1)
    assert np.array_equal(all_codes["rep3_hard"].decode(llr).msg, (hb >= 2).astype(np.uint8))


def test_hamming_hard(all_codes):
    rng = np.random.default_rng(8)
    soft, hard = all_codes["hamming74"], all_codes["hamming74_hard"]
    msg = rng.integers(0, 2, (30, K), dtype=np.uint8)
    cw = hard.encode(msg)
    # one random error in every block -> always corrected
    err = np.zeros_like(cw).reshape(30, K // 4, 7)
    err[np.arange(30)[:, None], np.arange(K // 4)[None, :], rng.integers(0, 7, (30, K // 4))] = 1
    assert np.array_equal(hard.decode(bpsk_llr(cw ^ err.reshape(30, -1))).msg, msg)
    # perfect code: syndrome decoding == ML on hard decisions (komm vs komm)
    llr = rng.normal(0, 1.0, (100, hard.n))
    assert np.array_equal(hard.decode(llr).msg, HardInput(soft).decode(llr).msg)


# ------------------------------------------------------------ BCH / RS

@pytest.mark.parametrize("name", ["bch_r23", "bch_r12", "bch_r13"])
def test_bch_t_errors(all_codes, name):
    c = all_codes[name]
    rng = np.random.default_rng(9)
    B = 24
    msg = rng.integers(0, 2, (B, K), dtype=np.uint8)
    cw = c.encode(msg)
    for extra, should_decode in ((0, True), (1, False), (5, False)):
        r = cw.copy()
        for b in range(B):
            r[b, rng.choice(c.n, c.t + extra, replace=False)] ^= 1
        res = c.decode(bpsk_llr(r))
        if should_decode:
            assert res.valid.all() and np.array_equal(res.msg, msg)
        else:
            assert not res.valid.any()               # beyond t: flagged
            assert np.array_equal(res.msg, r[:, :K])  # failure -> hard systematic bits
    # fewer than t errors also fine
    r = cw.copy()
    for b in range(B):
        r[b, rng.choice(c.n, b % (c.t + 1), replace=False)] ^= 1
    res = c.decode(bpsk_llr(r))
    assert res.valid.all() and np.array_equal(res.msg, msg)


def _corrupt_bytes(r, frame, positions, rng):
    r[frame, positions] ^= np.unpackbits(rng.integers(1, 256, len(positions), dtype=np.uint8)[:, None], axis=1)


@pytest.mark.parametrize("name", ["rs_r23_i4", "rs_r12_i4", "rs_r13_i4"])
def test_interleaved_rs_is_systematic_and_corrects_t_per_word(all_codes, name):
    c = all_codes[name]
    rng = np.random.default_rng(12)
    B = 12
    msg = rng.integers(0, 2, (B, K), dtype=np.uint8)
    cw = c.encode(msg)
    assert np.array_equal(cw[:, :K], msg)
    r = cw.reshape(B, c.n_sym, 8).copy()
    for b in range(B):
        for w in range(c.depth):      # t errors in every word: 4 t bytes in the frame
            _corrupt_bytes(r, b, rng.choice(c.n_sym // c.depth, c.t, replace=False) * c.depth + w, rng)
    res = c.decode(bpsk_llr(r.reshape(B, c.n)))
    assert res.valid.all() and np.array_equal(res.msg, msg)
    r = cw.reshape(B, c.n_sym, 8).copy()
    for b in range(B):                # t + 1 errors in one word fail the frame
        _corrupt_bytes(r, b, rng.choice(c.n_sym // c.depth, c.t + 1, replace=False) * c.depth, rng)
    assert not c.decode(bpsk_llr(r.reshape(B, c.n))).valid.any()


@pytest.mark.parametrize("name", ["rs_r23", "rs_r12", "rs_r13"])
def test_rs_erasures_go_beyond_t_when_the_llrs_flag_the_bad_bytes(all_codes, name):
    c, er = all_codes[name], all_codes[name + "_er"]
    rng = np.random.default_rng(13)
    B = 8
    msg = rng.integers(0, 2, (B, K), dtype=np.uint8)
    cw = c.encode(msg)
    r = cw.reshape(B, c.n_sym, 8).copy()
    llr = np.full(r.shape, 6.0)
    for b in range(B):
        bad = rng.choice(c.n_sym, c.t + 6, replace=False)      # more than t byte errors
        _corrupt_bytes(r, b, bad, rng)
        llr[b, bad] = 0.2                                      # ... that the channel flags
    llr = (llr * (1.0 - 2.0 * r)).reshape(B, c.n)
    assert not c.decode(llr).valid.any()
    res = er.decode(llr)
    assert res.valid.all() and np.array_equal(res.msg, msg)


def test_rs_erasure_decoder_rejects_noise(all_codes):
    er = all_codes["rs_r12_er"]
    assert not er.decode(np.random.default_rng(14).normal(0, 2, (64, er.n))).valid.any()


@pytest.mark.parametrize("name", ["rs_r23", "rs_r12", "rs_r13"])
def test_rs_t_symbol_errors(all_codes, name):
    c = all_codes[name]
    rng = np.random.default_rng(10)
    B = 24
    msg = rng.integers(0, 2, (B, K), dtype=np.uint8)
    cw = c.encode(msg)
    for extra, should_decode in ((0, True), (1, False), (8, False)):
        r = cw.copy().reshape(B, c.n_sym, 8)
        for b in range(B):
            pos = rng.choice(c.n_sym, c.t + extra, replace=False)
            pat = np.unpackbits(rng.integers(1, 256, len(pos), dtype=np.uint8)[:, None], axis=1)
            r[b, pos] ^= pat                          # nonzero symbol error
        r = r.reshape(B, c.n)
        res = c.decode(bpsk_llr(r))
        if should_decode:
            assert res.valid.all() and np.array_equal(res.msg, msg)
        else:
            assert not res.valid.any()
    # t symbol errors made of single bit flips, and bursts inside one symbol
    r = cw.copy()
    for b in range(B):
        r[b, 8 * rng.choice(c.n_sym, c.t, replace=False) + rng.integers(0, 8)] ^= 1
    res = c.decode(bpsk_llr(r))
    assert res.valid.all() and np.array_equal(res.msg, msg)


# ------------------------------------------------------------ AWGN sanity

def test_awgn_sanity(all_codes):
    rng = np.random.default_rng(11)
    unc = simulate_awgn(all_codes["uncoded"], 4.0, 400, rng)
    assert 0.010 < unc["ber"] < 0.015                        # Q(sqrt(2*10^0.4)) = 1.25e-2
    rep = simulate_awgn(all_codes["rep3"], 4.0, 400, rng)
    assert 0.010 < rep["ber"] < 0.015                        # soft repetition: no coding gain
    ham = simulate_awgn(all_codes["hamming74"], 6.0, 400, rng)["ber"]
    hamh = simulate_awgn(all_codes["hamming74_hard"], 6.0, 400, rng)["ber"]
    assert ham < hamh < 2.4e-3                               # soft > hard > uncoded
    for name, ebn0 in (("bch_r12", 6.0), ("rs_r12", 6.0), ("bch_r13", 6.0)):
        res = simulate_awgn(all_codes[name], ebn0, 100, rng)
        assert res["fer"] <= 0.05, (name, res)
        assert res["false_valid_rate"] == 0.0
