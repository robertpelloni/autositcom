"""End-to-end: sample transcripts -> distill -> script -> render -> publish.

WHY mocked boundaries: Gemini/edge-tts/moviepy/social APIs are external and
unavailable in CI; the repo's own tests already mock at these exact seams.
What is REAL here: the fixture JSONL on disk, a genuine 10s WAV, schema
validation, threshold filtering, and main.run_pipeline_iteration orchestration.
"""
import asyncio, json, shutil, sys, types, wave
from unittest.mock import AsyncMock, MagicMock, patch
from src import main
from src.schemas import ExtractedTopic, RenderedEpisode, SitcomScript, ScriptScene, TranscriptChunk

def _stub(monkeypatch, name, **attrs):
    # WHY sys.modules stubs: renderer modules import edge_tts/moviepy, which have
    # no wheels on this interpreter — stubbing the seam keeps the E2E hermetic.
    m = types.ModuleType(name)
    for k, v in attrs.items(): setattr(m, k, v)
    monkeypatch.setitem(sys.modules, name, m); return m

FIXTURE = "tests/fixtures/sample_transcripts.jsonl"

def make_wav(path):
    with wave.open(str(path), "wb") as w:  # real 10s of silence, stdlib only
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 8000 * 10)

def test_full_cycle_from_sample_transcripts(tmp_path, capsys, monkeypatch):
    make_wav(tmp_path / "sample_10s.wav")
    tdir = tmp_path / "transcripts"; tdir.mkdir()
    shutil.copy(FIXTURE, tdir / "transcripts.jsonl")
    chunks = json.loads(open(FIXTURE).readline())
    assert chunks["ID"] == "chunk_1"  # fixture really on disk and parseable

    topic = ExtractedTopic(topic_id="t1", title="Vending Machine Millions",
        summary="BOB invests his paycheck in vending machines.", key_quotes=["Mostly in quarters."],
        comedy_score=9.0, source_chunk_ids=["chunk_1", "chunk_3"])
    script = SitcomScript(script_id="s1", title="The Vending Machine", theme="Bad investments",
        characters=["BOB", "LUM"], scenes=[ScriptScene(scene_number=1, setting="Apartment",
        dialogue=[{"BOB": "Mostly in quarters."}], visual_action_notes="Coins everywhere")])
    episode = RenderedEpisode(episode_id="e1", video_path=str(tmp_path / "ep.mp4"),
        duration_seconds=10.0, thumbnail_path=str(tmp_path / "thumb.jpg"))

    Ext, Gen, TTS, VC, Pub = (MagicMock() for _ in range(5))
    _stub(monkeypatch, "src.distiller.topic_extractor", TopicExtractor=Ext)
    _stub(monkeypatch, "src.scriptwriter.script_generator", ScriptGenerator=Gen)
    _stub(monkeypatch, "src.renderer.tts_engine", TTSEngine=TTS)
    _stub(monkeypatch, "src.renderer.video_composer", VideoComposer=VC)
    _stub(monkeypatch, "src.publisher.social_uploader", SocialUploader=Pub)
    Ext.return_value.read_recent_chunks.return_value = [TranscriptChunk(**json.loads(l)) for l in open(FIXTURE) if l.strip()]
    Ext.return_value.extract_topics.return_value = [topic]
    Gen.return_value.generate_script.return_value = script
    TTS.return_value.generate_scene_audio = AsyncMock(return_value=[{"scene_number": 1}])
    VC.return_value.compose_episode.return_value = episode
    with patch.object(main.settings, "TRANSCRIPT_STORAGE_DIR", str(tdir)):
        assert asyncio.run(main.run_pipeline_iteration()) is None
    VC.return_value.compose_episode.assert_called_once()
    Pub.return_value.publish_all.assert_called_once_with(script, episode, platforms=None)
    out = capsys.readouterr().out
    assert "Pipeline Iteration Complete" in out and "STAGE-FAIL" not in out

