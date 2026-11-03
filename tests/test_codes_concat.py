import numpy as np
import pytest

from wmecc.codes import concat

EXPECTED_N = {"rs72_conv": 1164, "rs80_conv": 1292, "rs96_conv": 1548, "rs96i4_conv": 1548,
              "rs72_turbo": 1160, "rs72_ldpc": 1024, "bch_ldpc": 1024,
              "rs80_conv_er": 1292, "rs96_conv_er": 1548}


@pytest.fixture(scope="module")
def codes():
    return {c.name: c for c in concat.codes()}


def test_registry(codes):
    assert {n: c.n for n, c in codes.items()} == EXPECTED_N
    assert all(c.k == 512 and c.has_check and c.soft for c in codes.values())


def test_only_decoder_variants_share_an_embedding(codes):
    base = {n: getattr(c, "inner", c).name for n, c in codes.items()}
    assert base.pop("rs80_conv_er") == "rs80_conv" and base.pop("rs96_conv_er") == "rs96_conv"
    assert all(n == b for n, b in base.items())


@pytest.mark.parametrize("name", sorted(EXPECTED_N))
def test_roundtrip_and_noise(codes, name):
    c, rng = codes[name], np.random.default_rng(0)
    msg = rng.integers(0, 2, (2, 512), dtype=np.uint8)
    res = c.decode(4.0 * (1.0 - 2.0 * c.encode(msg)))
    assert np.array_equal(res.msg, msg) and res.valid.all()
    assert not c.decode(rng.normal(0, 2, (4, c.n))).valid.any()


def test_bcjr_posterior_is_log_p0_over_p1(codes):
    c = codes["rs80_conv"]
    bits = np.random.default_rng(1).integers(0, 2, (2, 512), dtype=np.uint8)
    outer = c.outer.encode(bits)
    llr = c.inner_code.posterior(3.0 * (1.0 - 2.0 * c.encode(bits)))
    assert llr.shape == outer.shape
    assert np.array_equal(llr < 0, outer.astype(bool))


@pytest.mark.parametrize("name", ["rs96_conv", "rs96_conv_er"])
def test_outer_code_fixes_what_the_inner_decoder_leaves(codes, name):
    c, rng = codes[name], np.random.default_rng(2)
    msg = rng.integers(0, 2, (64, 512), dtype=np.uint8)
    y = 1.0 - 2.0 * c.encode(msg) + rng.normal(0, np.sqrt(0.72), (64, c.n))
    llr = 2.0 * y / 0.72
    inner = codes["rs96_conv"].inner_code.decode(llr).msg[:, :512]
    wrong_inner = (inner != msg).any(axis=1).sum()
    res = c.decode(llr)
    wrong = (res.msg != msg).any(axis=1)
    assert wrong_inner >= 10 and wrong.sum() < wrong_inner
    assert res.valid[~wrong].all() and not res.valid[wrong].any()
