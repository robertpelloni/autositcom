import os
import time
from pathlib import Path
from pydub import AudioSegment
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import settings

class AudioIngestHandler(FileSystemEventHandler):
    def __init__(self, chunk_length_ms=300000, overlap_ms=10000):
        super().__init__()
        self.chunk_length_ms = chunk_length_ms
        self.overlap_ms = overlap_ms

        # Ensure the ingest and processing directories exist
        os.makedirs(settings.AUDIO_INGEST_DIR, exist_ok=True)
        self.processing_dir = os.path.join(settings.AUDIO_INGEST_DIR, "processing")
        os.makedirs(self.processing_dir, exist_ok=True)

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.wav'):
            return

        print(f"New audio file detected: {event.src_path}")
        # Wait a moment to ensure file is fully written (simple approach)
        time.sleep(1)
        self.process_audio(event.src_path)

    def process_audio(self, file_path):
        try:
            audio = AudioSegment.from_wav(file_path)
            duration = len(audio)

            filename = Path(file_path).stem

            # Step size is chunk length minus overlap
            step = self.chunk_length_ms - self.overlap_ms

            chunk_index = 0
            for start_ms in range(0, duration, step):
                end_ms = start_ms + self.chunk_length_ms
                if end_ms > duration:
                    end_ms = duration

                chunk = audio[start_ms:end_ms]

                chunk_filename = f"{filename}_chunk_{chunk_index:04d}.wav"
                chunk_path = os.path.join(self.processing_dir, chunk_filename)

                chunk.export(chunk_path, format="wav")
                print(f"Exported chunk: {chunk_path}")
                chunk_index += 1

                if end_ms == duration:
                    break
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def start_listening():
    os.makedirs(settings.AUDIO_INGEST_DIR, exist_ok=True)
    event_handler = AudioIngestHandler()
    observer = Observer()
    observer.schedule(event_handler, settings.AUDIO_INGEST_DIR, recursive=False)
    observer.start()
    print(f"Listening for audio in {settings.AUDIO_INGEST_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_listening()