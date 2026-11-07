import numpy as np
import pytest
from PIL import Image, ImageEnhance
from scipy.stats import binom

from wmecc import experiment, semiblind
from wmecc.codes import get_codes
from wmecc.data import save_rgb


def test_semi_blind_messages_share_the_header_and_differ_in_the_id():
    cfg = experiment.ExpConfig(semi_blind=True)
    a, b = cfg.message_for("0801.png"), cfg.message_for("0802.png")
    assert a.shape == b.shape == (1, 512)
    assert np.array_equal(a[:, :128], cfg.message[:, :128])
    assert np.array_equal(a[:, :128], b[:, :128])
    assert not np.array_equal(a[:, 128:], b[:, 128:])
    assert np.array_equal(a, cfg.message_for("/elsewhere/0801.png"))
    assert np.array_equal(experiment.ExpConfig().message_for("0801.png"), cfg.message)


def test_split_codes_put_the_header_codeword_first():
    code = {c.name: c for c in get_codes(modules=("split",))}["ldpc_r12_split"]
    assert (code.n_header, code.n) == (256, 1024)
    msg = np.random.default_rng(0).integers(0, 2, (2, 512), dtype=np.uint8)
    cw = code.encode(msg)
    assert np.array_equal(cw[:, :256], code.header.encode(msg[:, :128]))
    h, i = code.decode_parts(6.0 * (1.0 - 2.0 * cw))
    assert np.array_equal(h.msg, msg[:, :128]) and np.array_equal(i.msg, msg[:, 128:])


@pytest.mark.parametrize("two_sided, tests", [(False, 1), (True, 1), (True, 17)])
def test_threshold_keeps_the_false_positive_rate(two_sided, tests):
    t = semiblind.threshold(256, 1e-6, two_sided, tests)
    rate = (2 if two_sided else 1) * tests * binom.sf(np.array([t - 1, t - 2]), 256, 0.5)
    assert rate[0] <= 1e-6 < rate[1]


def test_the_chroma_correction_undoes_a_pil_colour_gain():
    x = np.random.default_rng(0).integers(40, 220, (64, 64, 3), dtype=np.uint8)
    fixes = dict(semiblind.corrections(experiment.ExpConfig()))
    assert next(iter(fixes)) == "none"
    for enhancer in (ImageEnhance.Brightness, ImageEnhance.Contrast, ImageEnhance.Color):
        attacked = np.asarray(enhancer(Image.fromarray(x)).enhance(1.21))
        back = fixes["chroma_x0.8264"](attacked)
        u = lambda im: -0.147 * im[..., 0] - 0.289 * im[..., 1] + 0.436 * im[..., 2]  # noqa: E731
        assert np.abs(u(back.astype(float)) - u(x.astype(float))).mean() < 1.0


class _Attack:
    family = "Test"

    def __init__(self, name, f):
        self.name, self.f = name, f

    def __call__(self, x, seed=0):
        return self.f(x)


def _colour_gain(x):
    return np.asarray(ImageEnhance.Color(Image.fromarray(x)).enhance(1.21))


def _run(tmp_path, monkeypatch, cover, name="uncoded"):
    code = {c.name: c for c in get_codes([name], modules=("split",))}[name]
    monkeypatch.setattr(experiment, "_embedding_codes", lambda _: {code.name: (code, [code])})
    monkeypatch.setattr(semiblind, "get_attacks", lambda names: [
        _Attack("none", lambda x: x), _Attack("gain", _colour_gain)])
    path = tmp_path / "0801.png"
    save_rgb(path, cover)
    cfg = experiment.ExpConfig(semi_blind=True, votes_per_bit=8, search_null_every=1)
    rows, _ = semiblind._run_one((cfg, 0, path, ["none", "gain"], {code.name: dict(scale=60.0)}))
    return {(r["attack"], r["watermarked"], r["decoder"]): r for r in rows}


def _cover(blue_rows: slice):
    """Grey (no chroma) with a bluish band: a chroma gain of 1.21 shifts the quantised
    value of its blocks by about half the step of 60, which inverts their bits."""
    rng = np.random.default_rng(1)
    img = np.full((1024, 1024, 3), 128.0)
    img[blue_rows] = (120.0, 120.0, 160.0)
    return np.clip(img + rng.normal(0, 2, img.shape), 0, 255).astype(np.uint8)


def test_the_pilot_undoes_an_inverted_frame(tmp_path, monkeypatch):
    rows = _run(tmp_path, monkeypatch, _cover(slice(None)))     # every block inverts
    assert all(rows[("none", True, d)]["id_ok"] for d in semiblind.DECODERS)
    gain = {d: rows[("gain", True, d)] for d in semiblind.DECODERS}
    assert not gain["plain"]["id_ok"] and gain["plain"]["agree"] < 20
    assert gain["pilot"]["flipped"] and gain["pilot"]["id_ok"]
    assert not rows[("gain", False, "pilot")]["id_ok"]


def test_the_search_undoes_a_colour_gain_that_scrambles_half_the_blocks(tmp_path, monkeypatch):
    rows = _run(tmp_path, monkeypatch, _cover(slice(0, 512)))  # half the blocks invert
    gain = {d: rows[("gain", True, d)] for d in semiblind.DECODERS}
    assert not gain["plain"]["id_ok"] and not gain["pilot"]["id_ok"]
    assert gain["search"]["searched"] and gain["search"]["fix"] == "chroma_x0.8264"
    assert gain["search"]["id_ok"] and gain["search"]["agree"] >= 120
    assert rows[("gain", False, "search")]["agree"] < semiblind.threshold(128, 1e-6, True, 17)


def test_a_joint_code_finds_an_inverted_frame_by_decoding_its_header(tmp_path, monkeypatch):
    rows = _run(tmp_path, monkeypatch, _cover(slice(None)), "ldpc_r12_joint")
    gain = {d: rows[("gain", True, d)] for d in semiblind.DECODERS}
    assert not gain["plain"]["header_ok"] and not gain["plain"]["id_ok"]
    assert gain["pilot"]["flipped"] and gain["pilot"]["header_ok"] and gain["pilot"]["id_ok"]
    assert gain["pilot"]["agree"] == -1
    assert not any(rows[("gain", False, d)]["header_ok"] for d in semiblind.DECODERS)


def test_the_designs_label_their_rows(tmp_path, monkeypatch):
    rows = _run(tmp_path, monkeypatch, _cover(slice(0, 8)), "turbo_r12_split")
    assert {r["design"] for r in rows.values()} == {"split"}
    assert all(rows[("none", True, d)]["id_ok"] and rows[("none", True, d)]["header_ok"]
               for d in semiblind.DECODERS)


def test_the_id_first_joint_code_sends_its_header_as_a_pilot():
    from scipy.stats import norm
    code = {c.name: c for c in get_codes(["ldpc_r12_jidh"], modules=("split",))}["ldpc_r12_jidh"]
    assert (code.design, code.n, code.n_header) == ("joint_idh", 1024, 128)
    assert np.array_equal(code.pilot, np.arange(256, 384))
    rng = np.random.default_rng(3)
    msg = rng.integers(0, 2, (40, 512), dtype=np.uint8)
    cw = code.encode(msg)
    assert np.array_equal(cw[:, code.pilot], msg[:, :128])
    assert np.array_equal(code.decode(6.0 * (1.0 - 2.0 * cw)).msg, msg)
    sigma = -1 / norm.ppf(0.145)                       # past what r1/2 corrects, not r 0.43
    llr = 2 * ((1.0 - 2.0 * cw) + rng.normal(0, sigma, cw.shape)) / sigma ** 2
    plain = (code.decode_parts(llr)[1].msg == msg[:, 128:]).all(axis=1).sum()
    known = sum((code.decode_known(llr[r:r + 1], msg[r, :128])[1].msg == msg[r, 128:]).all()
                for r in range(len(msg)))
    assert known >= plain + 10


def test_known_header_rows_need_the_pilot_to_flag_the_frame(tmp_path, monkeypatch):
    rows = _run(tmp_path, monkeypatch, _cover(slice(0, 8)), "ldpc_r12_jidh")
    assert {r["design"] for r in rows.values()} == {"joint_idh"}
    for d in semiblind.DECODERS:
        assert semiblind.flag_threshold(128, f"{d}_known", 17) == semiblind.flag_threshold(128, d, 17)
        clean, null = rows[("none", True, f"{d}_known")], rows[("none", False, f"{d}_known")]
        assert clean["header_ok"] and clean["id_ok"] and clean["agree"] >= 120
        assert not null["header_ok"] and not null["id_ok"] and not null["id_valid"]
