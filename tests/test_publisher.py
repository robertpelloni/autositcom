import pytest
from src.schemas import SitcomScript, RenderedEpisode
from src.publisher.social_uploader import SocialUploader

@pytest.fixture
def mock_script():
    return SitcomScript(
        script_id="test_ep_1",
        title="Episode 1",
        theme="Testing",
        characters=["JERRY", "GEORGE"],
        scenes=[]
    )

@pytest.fixture
def mock_episode():
    return RenderedEpisode(
        episode_id="test_ep_1",
        video_path="dummy_path.mp4",
        duration_seconds=30.0,
        thumbnail_path="dummy_thumb.jpg"
    )

def test_metadata_extraction(mock_script):
    uploader = SocialUploader()
    metadata = uploader._extract_metadata(mock_script)

    assert metadata["title"] == "Autositcom: Episode 1 (Shorts)"
    assert "Testing" in metadata["description"]
    assert "JERRY" in metadata["description"]
    assert "Testing" in metadata["tags"]
    assert "sitcom" in metadata["tags"]

def test_upload_to_youtube(mock_script, mock_episode, monkeypatch):
    # Mock secrets to allow the stub to run
    monkeypatch.setattr("src.publisher.social_uploader.settings.YOUTUBE_CLIENT_SECRET", "dummy")
    uploader = SocialUploader()
    uploader.youtube_secret = "dummy" # Ensure it's set

    # Should run the simulated try/except block and return True
    success = uploader.upload_to_youtube(mock_script, mock_episode)
    assert success == True

def test_upload_to_youtube_no_secret(mock_script, mock_episode, monkeypatch):
    monkeypatch.setattr("src.publisher.social_uploader.settings.YOUTUBE_CLIENT_SECRET", "")
    uploader = SocialUploader()
    uploader.youtube_secret = ""

    # Should skip and return False
    success = uploader.upload_to_youtube(mock_script, mock_episode)
    assert success == False

def test_publish_all(mock_script, mock_episode, monkeypatch, capsys):
    monkeypatch.setattr("src.publisher.social_uploader.settings.YOUTUBE_CLIENT_SECRET", "dummy")
    monkeypatch.setattr("src.publisher.social_uploader.settings.TIKTOK_SESSION_TOKEN", "dummy")

    uploader = SocialUploader()
    uploader.youtube_secret = "dummy"
    uploader.tiktok_token = "dummy"

    uploader.publish_all(mock_script, mock_episode)

    captured = capsys.readouterr()
    assert "Publishing Episode: Autositcom: Episode 1" in captured.out
    assert "YouTube upload simulated" in captured.out
    assert "TikTok upload simulated" in captured.out
    assert "X upload simulated" in captured.out