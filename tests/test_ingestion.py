import os
import wave
import json
from unittest.mock import patch, MagicMock
from src.config import settings
from src.ingestion.audio_receiver import AudioIngestHandler
from src.ingestion.transcriber import AudioTranscriber

def create_dummy_wav(filepath, duration_seconds=10):
    """Creates a dummy WAV file for testing."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        # Write dummy frames
        wav_file.writeframes(b'\x00\x00' * 44100 * duration_seconds)

def test_audio_chunking(tmp_path):
    # Override settings for testing
    settings.AUDIO_INGEST_DIR = str(tmp_path / "audio_ingest")

    # Create a 20 second dummy file
    dummy_wav = os.path.join(settings.AUDIO_INGEST_DIR, "test_input.wav")
    create_dummy_wav(dummy_wav, duration_seconds=20)

    # Initialize handler with 5 second chunks and 1 second overlap
    handler = AudioIngestHandler(chunk_length_ms=5000, overlap_ms=1000)

    # Trigger processing
    handler.process_audio(dummy_wav)

    processing_dir = os.path.join(settings.AUDIO_INGEST_DIR, "processing")
    files = os.listdir(processing_dir)

    # Total duration = 20s. Step = 4s.
    # Start times: 0, 4, 8, 12, 16. Total chunks = 5.
    assert len(files) == 5
    for i in range(5):
        expected_filename = f"test_input_chunk_{i:04d}.wav"
        assert expected_filename in files

@patch('src.ingestion.transcriber.WhisperModel')
def test_audio_transcription(mock_whisper_model, tmp_path):
    # Mock settings
    settings.TRANSCRIPT_STORAGE_DIR = str(tmp_path / "transcripts")

    # Setup mock whisper model
    mock_model_instance = MagicMock()

    # Mock the return value of transcribe
    class MockSegment:
        def __init__(self, start, text):
            self.start = start
            self.text = text

    mock_segments = [
        MockSegment(0.0, "Hello test"),
        MockSegment(2.5, "This is a dummy transcript")
    ]
    mock_model_instance.transcribe.return_value = (mock_segments, None)
    mock_whisper_model.return_value = mock_model_instance

    # Initialize transcriber
    transcriber = AudioTranscriber()

    # Run transcription
    dummy_audio_path = "dummy.wav"
    chunks = transcriber.transcribe_chunk(dummy_audio_path)

    assert len(chunks) == 2
    assert chunks[0].text == "Hello test"
    assert chunks[1].text == "This is a dummy transcript"
    assert chunks[0].audio_path == dummy_audio_path

    # Verify file saving
    output_file = os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")
    assert os.path.exists(output_file)

    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2
        data1 = json.loads(lines[0])
        assert data1['text'] == "Hello test"