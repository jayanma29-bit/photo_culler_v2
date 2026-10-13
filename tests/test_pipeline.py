import json
import random
from pathlib import Path

import pytest
from PIL import Image

from src import evaluate as ev
from src import main as culler


def make_blocks(path, seed, quality=95):
    """Write a deterministic test photo: an 8x8 grid of random colored blocks."""
    rng = random.Random(seed)
    small = Image.new("RGB", (8, 8))
    small.putdata([(rng.randrange(256), rng.randrange(256), rng.randrange(256)) for _ in range(64)])
    small.resize((256, 256), Image.Resampling.NEAREST).save(path, quality=quality)


def test_group_duplicates(tmp_path):
    a, a_copy, b = tmp_path / "a.jpg", tmp_path / "a_copy.jpg", tmp_path / "b.jpg"
    make_blocks(a, seed=1, quality=95)
    make_blocks(a_copy, seed=1, quality=40)  # same picture, heavier compression
    make_blocks(b, seed=2)                   # a different picture
    groups = culler.group_duplicates([a, a_copy, b], threshold=6)
    names = sorted(sorted(p.name for p in g) for g in groups)
    assert names == [["a.jpg", "a_copy.jpg"], ["b.jpg"]]


def test_sort_and_report(tmp_path):
    photo_dir = tmp_path / "in"
    out = tmp_path / "out"
    photo_dir.mkdir()
    out.mkdir()
    paths = {}
    for name, seed in [("good.jpg", 1), ("bad.jpg", 2), ("dup.jpg", 3)]:
        p = photo_dir / name
        make_blocks(p, seed)
        paths[name] = p
    decisions = {
        paths["good.jpg"]: ("kept", None),
        paths["bad.jpg"]: ("low_rated", None),
        paths["dup.jpg"]: ("duplicate", "good.jpg"),
    }
    results = {n: {"keep": True, "score": 7, "reason": "caf\u00e9 test"} for n in paths}

    culler.sort_into_folders(decisions, out)
    culler.sort_into_folders(decisions, out)  # a second run must rebuild cleanly
    culler.write_report(decisions, results, out / "report.csv")

    assert (out / "kept" / "good.jpg").exists()
    assert (out / "rejected" / "low_rated" / "bad.jpg").exists()
    assert (out / "rejected" / "duplicates" / "dup.jpg").exists()
    assert all(p.exists() for p in paths.values())  # originals untouched
    rows = (out / "report.csv").read_text(encoding="utf-8-sig").splitlines()
    assert rows[0] == "filename,status,score,reason,duplicate_of"
    assert len(rows) == 4


def test_refuses_to_delete_foreign_folders(tmp_path):
    out = tmp_path / "out"
    (out / "kept").mkdir(parents=True)
    (out / "kept" / "mine.txt").write_text("important", encoding="utf-8")
    with pytest.raises(SystemExit):
        culler.sort_into_folders({}, out)
    assert (out / "kept" / "mine.txt").exists()


def test_corrupt_cache_recovers(tmp_path):
    cache = tmp_path / "results.json"
    cache.write_text("", encoding="utf-8")
    assert culler.load_results(cache) == {}
    assert (tmp_path / "results.json.bad").exists()


def test_results_roundtrip(tmp_path):
    cache = tmp_path / "results.json"
    data = {"a.jpg": {"keep": True, "score": 9, "reason": "ok"}}
    culler.save_results(cache, data)
    assert culler.load_results(cache) == data
    assert not (tmp_path / "results.json.tmp").exists()


def test_main_end_to_end_with_fake_judge(tmp_path, monkeypatch):
    photos = tmp_path / "photos"
    photos.mkdir()
    make_blocks(photos / "a.jpg", 1, 95)
    make_blocks(photos / "a_copy.jpg", 1, 40)
    make_blocks(photos / "b.jpg", 2)
    make_blocks(photos / "c.jpg", 3)

    verdicts = {"a.jpg": (True, 9), "a_copy.jpg": (True, 7), "b.jpg": (True, 8), "c.jpg": (False, 2)}

    def fake_judge(path):
        keep, score = verdicts[Path(path).name]
        return {"keep": keep, "score": score, "reason": "fake"}

    monkeypatch.setattr(culler, "judge_photo", fake_judge)
    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", ["main", "--input", str(photos), "--output", str(out),
                                     "--results", str(tmp_path / "cache.json")])
    culler.main()

    assert (out / "kept" / "a.jpg").exists()
    assert (out / "kept" / "b.jpg").exists()
    assert (out / "rejected" / "duplicates" / "a_copy.jpg").exists()
    assert (out / "rejected" / "low_rated" / "c.jpg").exists()


def test_evaluate_handles_excel_bom(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    Path("results.json").write_text(json.dumps({
        "a.jpg": {"keep": True, "score": 8, "reason": "ok"},
        "b.jpg": {"keep": False, "score": 2, "reason": "blurry"},
    }), encoding="utf-8")
    Path("labels.csv").write_text("filename,keep\na.jpg,1\nb.jpg,0\n", encoding="utf-8-sig")
    ev.evaluate()
    out = capsys.readouterr().out
    assert "Evaluated 2 labeled photos" in out
    assert "100.0%" in out