import os
import json
import time
import uuid
from pathlib import Path
from faster_whisper import WhisperModel
from src.config import settings
from src.schemas import TranscriptChunk

class AudioTranscriber:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        # Ensure the transcript storage directory exists
        os.makedirs(settings.TRANSCRIPT_STORAGE_DIR, exist_ok=True)
        self.output_file = os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")

        # Load the faster-whisper model
        print(f"Loading Whisper model ({model_size})...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_chunk(self, audio_path: str) -> list[TranscriptChunk]:
        """
        Transcribes an audio chunk, creates TranscriptChunk objects, and returns them.
        """
        print(f"Transcribing {audio_path}...")
        segments, info = self.model.transcribe(audio_path, beam_size=5)

        chunks = []
        for segment in segments:
            # We don't have true diarization out of the box with standard whisper,
            # but we'll mock speaker_id for now or integrate pyannote later if needed.
            # In a real system you'd use a diarization pipeline.
            chunk = TranscriptChunk(
                ID=str(uuid.uuid4()),
                timestamp=segment.start,
                speaker_id="unknown_speaker",
                text=segment.text.strip(),
                audio_path=audio_path
            )
            chunks.append(chunk)

        self.save_chunks(chunks)
        return chunks

    def save_chunks(self, chunks: list[TranscriptChunk]):
        """
        Appends chunks to a JSON lines file.
        """
        with open(self.output_file, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(chunk.model_dump_json() + '\n')

def process_directory():
    """
    Scans the processing directory for new wav files and transcribes them.
    In a real system this would be a continuous loop or queue worker.
    """
    processing_dir = os.path.join(settings.AUDIO_INGEST_DIR, "processing")
    os.makedirs(processing_dir, exist_ok=True)
    transcriber = AudioTranscriber()

    for filename in os.listdir(processing_dir):
        if filename.endswith(".wav"):
            filepath = os.path.join(processing_dir, filename)
            transcriber.transcribe_chunk(filepath)
            # Optionally remove or move the file after processing
            # os.remove(filepath)

if __name__ == "__main__":
    process_directory()