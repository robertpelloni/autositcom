import os
import pytest
from unittest.mock import patch, MagicMock
from src.schemas import SitcomScript, ScriptScene
from src.renderer.video_composer import VideoComposer

@pytest.fixture
def mock_script():
    scene = ScriptScene(
        scene_number=1,
        setting="Living Room",
        dialogue=[
            {"JERRY": "Test line one."},
            {"GEORGE": "Test line two."}
        ],
        visual_action_notes="Walks in"
    )
    return SitcomScript(
        script_id="test_ep_1",
        title="Episode 1",
        theme="Testing",
        characters=["JERRY", "GEORGE"],
        scenes=[scene]
    )

@patch('src.renderer.video_composer.AudioFileClip')
@patch('src.renderer.video_composer.TextClip')
@patch('src.renderer.video_composer.CompositeVideoClip')
@patch('src.renderer.video_composer.concatenate_videoclips')
def test_video_composer(mock_concat, mock_composite_clip_class, mock_text_clip, mock_audio_clip, mock_script, tmp_path):
    # Setup mocks
    mock_audio_instance = MagicMock()
    mock_audio_instance.duration = 2.0
    mock_audio_clip.return_value = mock_audio_instance

    mock_text_instance = MagicMock()
    mock_text_instance.with_position.return_value = mock_text_instance
    mock_text_instance.with_duration.return_value = mock_text_instance
    mock_text_clip.return_value = mock_text_instance

    mock_composite_instance = MagicMock()
    mock_composite_instance.with_audio.return_value = mock_composite_instance
    mock_composite_clip_class.return_value = mock_composite_instance

    mock_final_video = MagicMock()
    mock_final_video.duration = 4.0
    mock_concat.return_value = mock_final_video

    # Run Composer
    composer = VideoComposer()

    # Create fake audio assets based on the mock script
    audio_assets = [
        {
            "scene_number": 1,
            "character": "JERRY",
            "audio_path": "fake1.mp3",
            "srt_path": "fake1.srt",
            "text": "Test line one."
        },
        {
            "scene_number": 1,
            "character": "GEORGE",
            "audio_path": "fake2.mp3",
            "srt_path": "fake2.srt",
            "text": "Test line two."
        }
    ]

    episode = composer.compose_episode(mock_script, audio_assets)

    # Verify outputs
    assert episode.episode_id == mock_script.script_id
    assert mock_concat.called
    assert mock_final_video.write_videofile.called
    assert mock_final_video.save_frame.called
    assert episode.duration_seconds == 4.0