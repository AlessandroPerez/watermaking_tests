import numpy as np
import pandas as pd

from wmecc import experiment, extended


def _frames(code, successes, image_names, attacks=("a", "b")):
    """successes: per image, how many of the attacks recover."""
    rows = []
    for image, wins in zip(image_names, successes):
        for j, attack in enumerate(attacks):
            rows.append(dict(image=image, code=code, family="F", n=8, rate=0.5, attack=attack,
                             category="C", success=j < wins, msg_ber=0.0, raw_ber=0.0))
    return rows


def test_ranking_counts_and_orders_codes():
    names = [f"{i}.png" for i in range(4)]
    df = pd.DataFrame(_frames("weak", [1, 1, 0, 0], names) + _frames("strong", [2, 2, 2, 1], names))
    rank, pairs = extended.ranking(df, names[:2], seed=0)
    assert list(rank.code) == ["strong", "weak"]
    assert rank.recovered.tolist() == [7, 2]
    assert rank.percent[0] == 87.5
    assert rank.percent_fresh.tolist() == [100.0, 50.0]
    assert rank.low[0] <= 87.5 <= rank.high[0]
    pair = pairs.iloc[0]
    assert (pair.code, pair.against) == ("strong", "weak")
    assert pair.difference == 62.5


def test_a_pair_is_resolved_only_when_images_agree():
    names = [f"{i}.png" for i in range(30)]
    always = pd.DataFrame(_frames("a", [2] * 30, names) + _frames("b", [0] * 30, names))
    assert extended.ranking(always, names, seed=0)[1].resolved.all()
    # the same totals, but the difference lies in a few images: resampling must widen it
    wins_a = [2] * 2 + [0] * 28
    uneven = pd.DataFrame(_frames("a", wins_a, names) + _frames("b", [0] * 30, names))
    _, pair = extended.ranking(uneven, names, seed=0)
    assert pair.high[0] - pair.low[0] > 5


def test_resampling_keeps_whole_images():
    totals = pd.DataFrame([[2, 0], [0, 2]], index=["a", "b"])
    boot = extended._resample(totals, 2, seed=0)
    assert boot.shape == (2, extended.BOOTSTRAP)
    # the same images are drawn for both codes: their percentages always sum to 100
    assert np.allclose(boot.sum(axis=0), 100)


def test_checks_count_wrong_and_false_passes():
    df = pd.DataFrame(dict(
        code=["c"] * 5 + ["no_check"] * 2, has_check=[True] * 5 + [False] * 2,
        watermarked=[True, True, True, False, False, True, False],
        valid=[True, True, False, True, False, True, True],
        success=[True, False, False, False, False, True, False]))
    row = extended.checks(df).iloc[0]
    assert len(extended.checks(df)) == 1
    assert (row.frames, row.passed, row.wrong_passes) == (3, 2, 1)
    assert (row.null_frames, row.false_passes) == (2, 1)
    assert 0.5 < row.false_pass_upper < 1


def test_presence_threshold_comes_from_unwatermarked_frames():
    df = pd.DataFrame(dict(code=["c"] * 4, watermarked=[True, True, True, False],
                           attack=["none", "a", "b", "a"], separation=[9.0, 3.0, 1.0, 2.0],
                           success=[True, True, False, False]))
    row = extended.presence(df).iloc[0]
    assert row.threshold == 2.0
    assert row.detected == 0.5


def test_the_sweep_is_paired_with_the_main_run(tmp_path, monkeypatch):
    names = [f"{i}.png" for i in range(3)]
    paths = [tmp_path / n for n in names]
    monkeypatch.setattr(experiment, "cover_paths", lambda: paths)
    cfg = experiment.ExpConfig(run_dir=str(tmp_path), all_images=True, n_test=3,
                               strength_factors=[0.5], sweep_images=1)
    sub = experiment.sweep_runs(cfg)[0]
    sub.path.mkdir()
    df = pd.DataFrame(_frames("c", [1, 2, 2], names))
    df["watermarked"] = True
    df[df.image == names[1]].assign(success=False).to_csv(sub.path / "results.csv", index=False)

    table, per_attack = extended.strength_sweep(df, cfg)
    assert table["x0.5"][0] == 0 and table["x1"][0] == 100
    assert table["spread"][0] == 100
    assert per_attack.spread.max() == 1
