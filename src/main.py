import json, os, sys, time
import asyncio
from src.config import settings
# NOTE: stage modules (pydub/faster-whisper/moviepy) are imported lazily inside
# the functions that use them — WHY: heavy/native deps unavailable on some
# interpreters (e.g. pyaudioop/av on Python 3.15) must not block --once, the
# dashboard, or tests from even starting. Missing dep = one stage logs, not a crash.

STATE_FILE = "data/dashboard_state.json"

def load_dashboard_state():
    """Validated dashboard state; ANY error (missing/corrupt/out-of-range)
    falls back to defaults so a bad UI write can never break the loop."""
    from src.config import DashboardState
    try: return DashboardState(**json.load(open(STATE_FILE)))
    except Exception: return DashboardState()

def load_comedy_threshold(default: float = 7.0) -> float:
    return load_dashboard_state().threshold

STAGES = ("distiller", "scriptwriter", "renderer", "publisher")
def parse_stage_health(log_text: str) -> dict:
    """Last-cycle health per stage from pipeline.log. WHY in main: pure and
    unit-testable without importing Streamlit; the dashboard only renders it.
    Values: 'ok' (cycle completed / stage passed), 'fail', 'skip', 'unknown'."""
    health = {s: "unknown" for s in STAGES}
    current = {}
    for line in log_text.splitlines():
        if "Starting Pipeline Iteration" in line: current = {}
        elif "[STAGE-FAIL]" in line:
            for s in STAGES:
                if s in line: current[s] = "fail"
        elif "[STAGE-SKIP]" in line:
            for s in STAGES:
                if s in line: current[s] = "skip"
        elif "Pipeline Iteration Complete" in line:
            health = {s: current.get(s, "ok") for s in STAGES}
        elif "No high-value topics" in line:
            health = {**{s: "unknown" for s in STAGES}, "distiller": "ok"}
    if current and health["distiller"] == "unknown": health.update(current)
    return health

def load_platforms():
    """Dashboard Publisher toggles persisted as state['platforms']; None = all."""
    return load_dashboard_state().platforms or None


async def run_pipeline_iteration():
    """
    Runs a single full loop of the pipeline based on existing transcript chunks.
    In a real 24/7 system, this might be triggered by a cron job or an event bus
    whenever enough chunks are collected.
    """
    print("--- Starting Pipeline Iteration ---")
    # WHY per-stage guards: one missing native dep or API key must degrade to a
    # logged skip, never kill the 24/7 loop. Dependents log [STAGE-SKIP].
    def fail(stage, e): print(f"[STAGE-FAIL] {stage}: {type(e).__name__}: {e}")
    transcripts_file = os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")

    # 3. Topic Analysis & Distillation (1&2 ingestion/transcription run continuously)
    try:
        from src.distiller.topic_extractor import TopicExtractor
        extractor = TopicExtractor(comedy_threshold=load_comedy_threshold())
        topics = extractor.extract_topics(extractor.read_recent_chunks(transcripts_file))
    except Exception as e: fail("distiller", e); return
    if not topics: print("No high-value topics found this iteration."); return
    print(f"Extracted {len(topics)} viable topics.")
    top_topic = sorted(topics, key=lambda x: x.comedy_score, reverse=True)[0]

    # 4. Script & Lore Generation
    try:
        from src.scriptwriter.script_generator import ScriptGenerator
        script = ScriptGenerator().generate_script(top_topic)
    except Exception as e: fail("scriptwriter", e); return
    if not script: print("Script generation failed."); return
    print(f"Script Generated: {script.title}")

    # 5. Audio/Visual Render Engine
    try:
        from src.renderer.tts_engine import TTSEngine
        from src.renderer.video_composer import VideoComposer
        episode = VideoComposer().compose_episode(script, await TTSEngine().generate_scene_audio(script))
    except Exception as e: fail("renderer", e); print("[STAGE-SKIP] publisher: no rendered episode"); return
    print(f"Video Rendered: {episode.video_path} (Duration: {episode.duration_seconds}s)")

    # 6. Multi-Platform Publisher
    try:
        from src.publisher.social_uploader import SocialUploader
        SocialUploader().publish_all(script, episode, platforms=load_platforms())
    except Exception as e: fail("publisher", e); return
    print("--- Pipeline Iteration Complete ---")

def main():
    """
    Main entry point for Docker/background execution.
    """
    import threading
    from src.ingestion.audio_receiver import start_listening

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
    # --once: single iteration for the dashboard Run Cycle button / cron / tests.
    if "--once" in sys.argv: asyncio.run(run_pipeline_iteration())
    else: main()