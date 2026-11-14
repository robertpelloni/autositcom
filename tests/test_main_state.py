import asyncio, json
from src.main import load_comedy_threshold, run_pipeline_iteration

def test_iteration_survives_empty_input(tmp_path, monkeypatch):
    # No transcripts anywhere: cycle must log and return, never raise (24/7 loop).
    monkeypatch.chdir(tmp_path)
    assert asyncio.run(run_pipeline_iteration()) is None

def test_threshold_default_when_no_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_comedy_threshold() == 7.0

def test_threshold_reads_dashboard_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "dashboard_state.json").write_text(json.dumps({"threshold": 8.5}))
    assert load_comedy_threshold() == 8.5

def test_threshold_falls_back_on_bad_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "dashboard_state.json").write_text("not json")
    assert load_comedy_threshold() == 7.0
