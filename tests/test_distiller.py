import os
import json
from unittest.mock import patch, MagicMock
from src.config import settings
from src.schemas import TranscriptChunk
from src.distiller.topic_extractor import TopicExtractor

@patch('src.distiller.topic_extractor.genai.Client')
def test_read_recent_chunks(mock_genai_client, tmp_path):
    settings.TRANSCRIPT_STORAGE_DIR = str(tmp_path / "transcripts")
    os.makedirs(settings.TRANSCRIPT_STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")

    chunk_data = {
        "ID": "chunk_1",
        "timestamp": 10.0,
        "speaker_id": "SpeakerA",
        "text": "This is a very funny joke.",
        "audio_path": "dummy.wav"
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(chunk_data) + "\n")

    extractor = TopicExtractor()
    chunks = extractor.read_recent_chunks(filepath)

    assert len(chunks) == 1
    assert chunks[0].ID == "chunk_1"
    assert chunks[0].text == "This is a very funny joke."

@patch('src.distiller.topic_extractor.genai.Client')
def test_extract_topics_filtering(mock_genai_client):
    # Setup mock
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance

    # Create dummy response from Gemini (JSON string)
    mock_response = MagicMock()
    mock_response.text = json.dumps([
        {
            "topic_id": "topic_1",
            "title": "Hilarious Story",
            "summary": "It was so funny.",
            "key_quotes": ["quote1"],
            "comedy_score": 9.5,
            "source_chunk_ids": ["chunk_1"]
        },
        {
            "topic_id": "topic_2",
            "title": "Boring Story",
            "summary": "Not funny at all.",
            "key_quotes": ["quote2"],
            "comedy_score": 2.0,
            "source_chunk_ids": ["chunk_2"]
        }
    ])
    mock_client_instance.models.generate_content.return_value = mock_response

    # Initialize extractor with threshold 7.0
    extractor = TopicExtractor(comedy_threshold=7.0)

    # Provide dummy chunks
    dummy_chunks = [
        TranscriptChunk(
            ID="chunk_1",
            timestamp=0.0,
            speaker_id="A",
            text="hello",
            audio_path="test.wav"
        )
    ]

    extracted = extractor.extract_topics(dummy_chunks)

    # Should only return the first topic (score 9.5 >= 7.0)
    assert len(extracted) == 1
    assert extracted[0].topic_id == "topic_1"
    assert extracted[0].comedy_score == 9.5