import os
import time
import asyncio
from src.config import settings
from src.ingestion.audio_receiver import start_listening
from src.ingestion.transcriber import AudioTranscriber
from src.distiller.topic_extractor import TopicExtractor
from src.scriptwriter.script_generator import ScriptGenerator
from src.renderer.tts_engine import TTSEngine
from src.renderer.video_composer import VideoComposer
from src.publisher.social_uploader import SocialUploader

async def run_pipeline_iteration():
    """
    Runs a single full loop of the pipeline based on existing transcript chunks.
    In a real 24/7 system, this might be triggered by a cron job or an event bus
    whenever enough chunks are collected.
    """
    print("--- Starting Pipeline Iteration ---")

    # 1. & 2. Ingestion & Transcription are running continuously in background (or via start_listening)
    # We assume transcripts.jsonl is being populated.
    transcripts_file = os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")

    # 3. Topic Analysis & Distillation
    extractor = TopicExtractor(comedy_threshold=7.0)
    chunks = extractor.read_recent_chunks(transcripts_file)
    topics = extractor.extract_topics(chunks)

    if not topics:
        print("No high-value topics found this iteration.")
        return

    print(f"Extracted {len(topics)} viable topics.")

    # We'll just process the top topic for this iteration
    top_topic = sorted(topics, key=lambda x: x.comedy_score, reverse=True)[0]

    # 4. Script & Lore Generation
    generator = ScriptGenerator()
    script = generator.generate_script(top_topic)

    if not script:
        print("Script generation failed.")
        return

    print(f"Script Generated: {script.title}")

    # 5. Audio/Visual Render Engine
    tts = TTSEngine()
    audio_assets = await tts.generate_scene_audio(script)

    composer = VideoComposer()
    episode = composer.compose_episode(script, audio_assets)

    print(f"Video Rendered: {episode.video_path} (Duration: {episode.duration_seconds}s)")

    # 6. Multi-Platform Publisher
    uploader = SocialUploader()
    uploader.publish_all(script, episode)

    print("--- Pipeline Iteration Complete ---")

def main():
    """
    Main entry point for Docker/background execution.
    """
    import threading

    # Start audio listener in a background thread
    listener_thread = threading.Thread(target=start_listening, daemon=True)
    listener_thread.start()

    # Periodically run the processing pipeline
    try:
        while True:
            # Run the async pipeline loop
            asyncio.run(run_pipeline_iteration())

            # Wait a few hours before the next processing batch
            # For testing, we might do 60 seconds
            print("Sleeping until next extraction cycle...")
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Shutting down pipeline.")

if __name__ == "__main__":
    main()