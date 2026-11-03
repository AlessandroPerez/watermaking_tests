import numpy as np
import pandas as pd

from wmecc import experiment
from wmecc.codes import get_codes
from wmecc.data import save_rgb


def test_message_depends_only_on_the_seed():
    a, b = experiment.ExpConfig(run_dir="a"), experiment.ExpConfig(run_dir="b", votes_per_bit=8)
    assert a.message.shape == (1, 512)
    assert np.array_equal(a.message, b.message)
    assert not np.array_equal(a.message, experiment.ExpConfig(seed=1).message)


def test_codes_of_equal_length_share_one_strength():
    class Code:
        k = 512

    df = pd.DataFrame(dict(code=["a", "a", "b", "b", "c"], n=[8, 8, 8, 8, 16],
                           strength=[10.0, 12.0, 14.0, 16.0, 5.0],
                           wpsnr=[40.0, 40.1, 39.9, 40.0, 40.0]))
    groups = {c: (Code, []) for c in "cab"}
    res = experiment._strengths(df, experiment.ExpConfig(), groups)
    assert list(res) == ["c", "a", "b"]
    assert res["a"]["scale"] == res["b"]["scale"] == 13.0 and res["c"]["scale"] == 5.0
    assert res["a"]["code_scale"] == 11.0 and res["b"]["code_scale"] == 15.0


def test_every_code_and_image_gets_the_same_message(tmp_path, monkeypatch):
    cfg = experiment.ExpConfig(votes_per_bit=8)
    codes = get_codes(["uncoded", "hamming74"])
    seen = []
    for c in codes:
        encode = c.encode
        monkeypatch.setattr(c, "encode", lambda m, encode=encode: seen.append(m.copy()) or encode(m))
    monkeypatch.setattr(experiment, "_embedding_codes", lambda _: {c.name: (c, [c]) for c in codes})

    rng = np.random.default_rng(0)
    paths = [tmp_path / f"{i}.png" for i in range(2)]
    for p in paths:
        save_rgb(p, rng.integers(60, 200, (1024, 1024, 3), dtype=np.uint8))
    cal = {c.name: dict(scale=60.0) for c in codes}

    for i, p in enumerate(paths):
        experiment._run_one((cfg, i, p, ["none"], cal))
        experiment._calibrate_one((cfg, codes[1].name, p))

    assert len(seen) == 6
    assert all(np.array_equal(m, cfg.message) for m in seen)


def test_watermarked_frames_only_at_a_scaled_strength(tmp_path, monkeypatch):
    code = get_codes(["uncoded"])[0]
    monkeypatch.setattr(experiment, "_embedding_codes", lambda _: {code.name: (code, [code])})
    path = tmp_path / "0.png"
    save_rgb(path, np.random.default_rng(0).integers(60, 200, (1024, 1024, 3), dtype=np.uint8))
    cal = {code.name: dict(scale=60.0)}

    both, _ = experiment._run_one((experiment.ExpConfig(votes_per_bit=8), 0, path, ["none"], cal))
    assert [r["watermarked"] for r in both] == [True, False]

    cfg = experiment.ExpConfig(votes_per_bit=8, false_positives=False, strength_factor=0.5)
    rows, embeds = experiment._run_one((cfg, 0, path, ["none"], cal))
    assert [r["watermarked"] for r in rows] == [True]
    assert embeds[0]["scale"] == 30.0


class _SerialPool:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def imap_unordered(self, f, jobs):
        return map(f, jobs)


def _covers(tmp_path, monkeypatch, count):
    paths = [tmp_path / f"{i:04d}.png" for i in range(count)]
    monkeypatch.setattr(experiment, "cover_paths", lambda: paths)
    return paths


def test_a_killed_run_resumes_from_the_finished_images(tmp_path, monkeypatch):
    paths = _covers(tmp_path, monkeypatch, 3)
    cfg = experiment.ExpConfig(run_dir=str(tmp_path), all_images=True, n_test=3,
                               conditions=["none"], image_start=0)
    (tmp_path / "calibration.json").write_text("{}")
    parts = tmp_path / "parts"
    parts.mkdir()
    done = dict(image=paths[1].name, code="c", scale=1.0, wpsnr=40.0, psnr=40.0, ssim=1.0)
    pd.DataFrame([dict(image=paths[1].name, code="c")]).to_csv(parts / "0001.results.csv", index=False)
    pd.DataFrame([done]).to_csv(parts / "0001.embedding.csv", index=False)

    ran = []

    def run_one(job):
        ran.append(job[2].name)
        return [dict(image=job[2].name, code="c")], [done | dict(image=job[2].name)]

    monkeypatch.setattr(experiment, "_run_one", run_one)
    monkeypatch.setattr(experiment, "Pool", _SerialPool)
    experiment.stage_run(cfg)

    assert ran == [paths[0].name, paths[2].name]
    assert list(pd.read_csv(tmp_path / "results.csv").image) == [p.name for p in paths]
    assert not parts.exists()


def test_the_sweep_avoids_the_images_that_chose_the_codes(tmp_path, monkeypatch):
    paths = _covers(tmp_path, monkeypatch, 100)
    cfg = experiment.ExpConfig(run_dir=str(tmp_path), all_images=True, n_test=100,
                               strength_factors=[0.9, 1.1], sweep_images=20)
    subs = experiment.sweep_runs(cfg)
    assert [s.strength_factor for s in subs] == [0.9, 1.1]
    assert all(not s.false_positives and not s.strength_factors for s in subs)
    chosen = paths[subs[0].image_start::subs[0].image_stride]
    assert len(chosen) == 20
    assert not set(chosen) & set(paths[::5])
    assert experiment.ExpConfig(n_test=3).test_images() == paths[0::10][:3]
