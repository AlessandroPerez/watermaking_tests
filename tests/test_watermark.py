import numpy as np
import pytest
import cv2

from wmecc.attacks import attack_suite, get_attacks
from wmecc.metrics import wpsnr
from wmecc.watermark import imwm


@pytest.fixture(scope="module")
def cover():
    rng = np.random.default_rng(1)
    y = cv2.GaussianBlur(rng.normal(128, 50, (1024, 1024)).astype(np.float32), (0, 0), 2)
    y += rng.normal(0, 10, y.shape).astype(np.float32)
    rgb = np.stack([y, 0.8 * y + 30, 0.6 * y + 50], -1)
    return np.clip(rgb, 0, 255).astype(np.uint8)


@pytest.mark.parametrize("n", [512, 1024])
def test_blind_roundtrip(cover, n):
    bits = np.random.default_rng(n).integers(0, 2, n, dtype=np.uint8)
    wm = imwm.embed(cover, bits, 60.0)
    ones, count = imwm.extract(wm, n, 60.0)
    assert count.sum() == imwm.BLOCKS                # one vote per 4x4 block of the LL band
    assert np.ptp(count) <= 1                        # every bit gets the same number of votes
    llr = imwm.votes_to_llr(ones, count)
    assert np.mean((llr < 0) != bits) < 0.05         # positive LLR <=> bit 0
    assert imwm.separation(ones, count) > 4


def test_distortion_does_not_depend_on_length(cover):
    rng = np.random.default_rng(0)
    w = [wpsnr(cover, imwm.embed(cover, rng.integers(0, 2, n), 60.0)) for n in (512, 2048)]
    assert abs(w[0] - w[1]) < 0.3


@pytest.mark.parametrize("n", [512, 1024, 2048])
def test_fixed_votes_roundtrip(cover, n):
    bits = np.random.default_rng(n).integers(0, 2, n, dtype=np.uint8)
    wm = imwm.embed(cover, bits, 60.0, votes=8)
    ones, count = imwm.extract(wm, n, 60.0, votes=8)
    assert (count == 8).all()
    assert np.mean((imwm.votes_to_llr(ones, count) < 0) != bits) < 0.05


def test_fixed_votes_leaves_unmarked_blocks_untouched(cover):
    n = 512
    wm = imwm.embed(cover, np.zeros(n, np.uint8), 60.0, votes=8)
    free = (imwm._layout(n, 0, 8) < 0).reshape(imwm.SIDE, imwm.SIDE)
    changed = (wm != cover).any(2).reshape(imwm.SIDE, imwm.BLOCK, imwm.SIDE, imwm.BLOCK).any((1, 3))
    assert free.sum() == imwm.BLOCKS - n * 8
    assert not changed[free].any() and changed[~free].mean() > 0.9


def test_fixed_votes_makes_distortion_grow_with_length(cover):
    rng = np.random.default_rng(0)
    w = [wpsnr(cover, imwm.embed(cover, rng.integers(0, 2, n), 60.0, votes=8)) for n in (512, 1024, 2048)]
    assert w[0] > w[1] > w[2] and w[0] - w[2] > 4     # 4x the marked area is about 6 dB


def test_fixed_votes_fill_the_frame_like_the_shared_layout():
    assert np.array_equal(imwm._layout(2048, 3, 8), imwm._layout(2048, 3))


def test_too_many_votes_are_refused():
    with pytest.raises(ValueError):
        imwm._layout(2048, 0, 9)


def test_unwatermarked_has_low_separation(cover):
    assert imwm.separation(*imwm.extract(cover, 512, 60.0)) < 4


def test_layout_is_not_a_stripe():
    # the votes of a bit must not sit in one column of blocks, whatever n is
    layout = imwm._layout(1024, 0).reshape(128, 128)
    assert len(set(np.flatnonzero(layout == 0) % 128)) > 8


def test_resized_image_is_read_on_the_embedding_frame(cover):
    bits = np.random.default_rng(3).integers(0, 2, 512, dtype=np.uint8)
    wm = imwm.embed(cover, bits, 60.0)
    small = cv2.resize(wm, (512, 512), interpolation=cv2.INTER_AREA)
    assert np.mean((imwm.votes_to_llr(*imwm.extract(small, 512, 60.0)) < 0) != bits) < 0.05


def test_too_small_image_gives_zero_llr():
    ones, count = imwm.extract(np.zeros((100, 100, 3), np.uint8), 512, 60.0)
    assert not imwm.votes_to_llr(ones, count).any()


def test_attacks_are_deterministic_uint8():
    img = np.random.default_rng(0).integers(0, 256, (96, 128, 3), dtype=np.uint8)
    for a in attack_suite():
        out = a(img, 3)
        assert out.dtype == np.uint8 and out.ndim == 3, a.name
        assert np.array_equal(out, a(img, 3)), a.name
    for a in get_attacks(["png_l1_none", "png_l9_paeth"]):
        assert np.array_equal(a(img, 0), img)
