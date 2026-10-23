import pytest
from src.config import PipelineSettings
from src.schemas import (
    TranscriptChunk,
    ExtractedTopic,
    ScriptScene,
    SitcomScript,
    RenderedEpisode,
)

def test_pipeline_settings_defaults():
    settings = PipelineSettings()
    assert settings.AUDIO_INGEST_DIR == "data/audio_ingest"
    assert settings.TRANSCRIPT_STORAGE_DIR == "data/transcripts"
    assert settings.RENDER_OUTPUT_DIR == "data/render_output"
    assert settings.OPENAI_API_KEY == ""
    assert settings.GEMINI_API_KEY == ""
    assert settings.ELEVENLABS_API_KEY == ""
    assert settings.YOUTUBE_CLIENT_SECRET == ""
    assert settings.TIKTOK_SESSION_TOKEN == ""

def test_transcript_chunk_schema():
    chunk = TranscriptChunk(
        ID="chunk_1",
        timestamp=12.5,
        speaker_id="speaker_a",
        text="Hello world",
        audio_path="/path/to/audio.wav"
    )
    assert chunk.ID == "chunk_1"
    assert chunk.timestamp == 12.5
    assert chunk.speaker_id == "speaker_a"
    assert chunk.text == "Hello world"
    assert chunk.audio_path == "/path/to/audio.wav"

def test_extracted_topic_schema():
    topic = ExtractedTopic(
        topic_id="topic_1",
        title="Funny Story",
        summary="A hilarious anecdote.",
        key_quotes=["Quote 1", "Quote 2"],
        comedy_score=8.5,
        source_chunk_ids=["chunk_1", "chunk_2"]
    )
    assert topic.topic_id == "topic_1"
    assert topic.title == "Funny Story"
    assert topic.summary == "A hilarious anecdote."
    assert topic.key_quotes == ["Quote 1", "Quote 2"]
    assert topic.comedy_score == 8.5
    assert topic.source_chunk_ids == ["chunk_1", "chunk_2"]

def test_script_scene_schema():
    scene = ScriptScene(
        scene_number=1,
        setting="Living Room",
        dialogue=[{"speaker_a": "Hello"}, {"speaker_b": "Hi"}],
        visual_action_notes="Walks in"
    )
    assert scene.scene_number == 1
    assert scene.setting == "Living Room"
    assert scene.dialogue == [{"speaker_a": "Hello"}, {"speaker_b": "Hi"}]
    assert scene.visual_action_notes == "Walks in"

def test_sitcom_script_schema():
    scene = ScriptScene(
        scene_number=1,
        setting="Living Room",
        dialogue=[{"speaker_a": "Hello"}, {"speaker_b": "Hi"}],
        visual_action_notes="Walks in"
    )
    script = SitcomScript(
        script_id="script_1",
        title="Episode 1",
        theme="Friendship",
        characters=["speaker_a", "speaker_b"],
        scenes=[scene]
    )
    assert script.script_id == "script_1"
    assert script.title == "Episode 1"
    assert script.theme == "Friendship"
    assert script.characters == ["speaker_a", "speaker_b"]
    assert script.scenes[0].scene_number == 1

def test_rendered_episode_schema():
    episode = RenderedEpisode(
        episode_id="ep_1",
        video_path="/path/to/video.mp4",
        duration_seconds=300.0,
        thumbnail_path="/path/to/thumb.jpg"
    )
    assert episode.episode_id == "ep_1"
    assert episode.video_path == "/path/to/video.mp4"
    assert episode.duration_seconds == 300.0
    assert episode.thumbnail_path == "/path/to/thumb.jpg"