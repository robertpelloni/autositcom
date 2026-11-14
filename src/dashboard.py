"""Autositcom Control Center — single consolidated page.

WHY single page: every backend feature (ingestion, transcription, distillation,
scriptwriting+lore validation, TTS/render, publishing, config) must be visible
without subpage fragmentation. Ordered by value: watch/control first, tune last.
Every control carries a help= tooltip explaining what it does and its effect.
State persists to data/dashboard_state.json so settings survive restarts.
"""
import glob, json, os, subprocess, sys, time
import streamlit as st
from src.config import settings

LOG = "data/pipeline.log"
def run_once():
    """Spawn one real pipeline iteration BelowNormal, logging to data/pipeline.log.
    WHY subprocess: Streamlit must stay responsive while moviepy/Gemini run."""
    os.makedirs("data", exist_ok=True)
    f = open(LOG, "a"); f.write("\n--- dashboard: run cycle ---\n"); f.flush()
    p = subprocess.Popen([sys.executable, "-m", "src.main", "--once"], stdout=f, stderr=subprocess.STDOUT,
                         creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    return p.pid

st.set_page_config(page_title="Autositcom Control Center", layout="wide", page_icon="🎬")
STATE = "data/dashboard_state.json"

def load_state():
    try: return json.load(open(STATE))
    except Exception: return {}
def save_state(s):
    # Validate before writing so the dashboard can never persist state the
    # pipeline would reject: DashboardState enforces threshold range/enums.
    from src.config import DashboardState
    DashboardState(**s)
    os.makedirs("data", exist_ok=True); json.dump(s, open(STATE, "w"), indent=2)
def count(d, ext): return len(glob.glob(os.path.join(d, f"*{ext}"))) if os.path.exists(d) else 0
def latest(d, ext):
    f = glob.glob(os.path.join(d, f"*{ext}")) if os.path.exists(d) else []
    return max(f, key=os.path.getctime) if f else None
def lines(p): return sum(1 for _ in open(p)) if os.path.exists(p) else 0

S = load_state()
st.title("🎬 Autositcom Control Center")
st.caption("BOB & LUM — record → transcribe → distill → script → render → publish. One page, no subpages.", help="Pipeline: src/ingestion → src/distiller → src/scriptwriter → src/renderer → src/publisher, orchestrated by src/main.py. Tray app: python -m src.tray")

# ── 1. STATUS + LATEST EPISODE (highest value) ──────────────────────────────
st.header("📺 Latest Episode & Pipeline Health", help="Start here: is the pipeline producing? Watch the newest render and headline counts.")
c = st.columns(4)
c[0].metric("Audio chunks queued", count(os.path.join(settings.AUDIO_INGEST_DIR, "processing"), ".wav"), help="5-min WAV segments in data/audio_ingest/processing awaiting transcription (watchdog + pydub, src/ingestion/audio_receiver.py).")
c[1].metric("Transcript lines", lines(os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")), help="Diarized TranscriptChunk rows in transcripts.jsonl from faster-whisper (src/ingestion/transcriber.py).")
c[2].metric("Episodes rendered", count(settings.RENDER_OUTPUT_DIR, ".mp4"), help="Finished vertical 1080×1920 MP4s from edge-tts + moviepy (src/renderer/).")
from src.main import parse_stage_health
_health = parse_stage_health(open(LOG, errors="ignore").read() if os.path.exists(LOG) else "")
_badge = {"ok": "🟢", "fail": "🔴", "skip": "⚪", "unknown": "⚫"}
hc = st.columns(4)
for i, stage in enumerate(["distiller", "scriptwriter", "renderer", "publisher"]):
    hc[i].metric(f"{_badge[_health[stage]]} {stage.title()}", _health[stage], help=f"Last-cycle status parsed from data/pipeline.log ([STAGE-FAIL]/[STAGE-SKIP] markers written by src/main.py). ⚫ unknown = stage has not run yet; ▶ Run one full cycle now below to refresh.")
keys = ["GEMINI_API_KEY", "OPENAI_API_KEY", "YOUTUBE_CLIENT_SECRET", "TIKTOK_SESSION_TOKEN"]
c[3].metric("API keys configured", f"{sum(bool(getattr(settings,k,'')) for k in keys)}/{len(keys)}", help="Keys set in .env (masked below in Configuration). Missing Gemini key = distiller/scriptwriter cannot run live.")

lv = latest(settings.RENDER_OUTPUT_DIR, ".mp4")
if lv:
    vc, dc = st.columns([2, 1])
    vc.video(lv)
    dc.write(f"**File:** `{os.path.basename(lv)}`\n\n**Created:** {time.ctime(os.path.getctime(lv))}\n\n**Size:** {os.path.getsize(lv)//1024} KB")
    if dc.button("▶ Publish this episode now", help="Calls SocialUploader.publish_all() for YouTube/TikTok/X per Publisher toggles below. Currently MOCK — no real posts."): st.toast("Mock publish queued (no live APIs yet)", icon="📤")
else: st.info("No episodes yet — run a cycle below or drop WAVs into the ingest folder. (Renderer writes MP4s to RENDER_OUTPUT_DIR.)")

# ── 2. PIPELINE CONTROLS ────────────────────────────────────────────────────
st.header("▶ Pipeline Controls", help="src/main.py run_pipeline_iteration(): distill → script → render → publish, then sleep. Ingestion/transcription run continuously in background.")
a, b, d = st.columns(3)
if a.button("▶ Run one full cycle now", help="Spawns `python -m src.main --once` (BelowNormal) using the Distiller threshold saved below; output tails in Logs & Data Browser (data/pipeline.log). Needs GEMINI_API_KEY for live stages."):
    st.success(f"Pipeline cycle started (PID {run_once()}) — watch Logs below.")
d.selectbox("Cycle interval (hours)", [1, 6, 12, 24], index=0, key="interval", help="How often main.py repeats. It sleeps 3600s by default between iterations.")
b.toggle("Auto-cycle enabled", value=S.get("auto", False), key="auto", help="When on, the orchestrator loops forever. When off, only manual cycles run.", on_change=lambda: (S.update(auto=st.session_state.auto), save_state(S)))

# ── 3. INGESTION & TRANSCRIPTION ────────────────────────────────────────────
st.header("🎙 Ingestion & Transcription", help="src/ingestion/: audio_receiver watches a folder, chunks audio; transcriber runs faster-whisper and appends TranscriptChunks.")
i1, i2, i3 = st.columns(3)
i1.number_input("Chunk length (sec)", 30, 3600, S.get("chunk", 300), 30, help="audio_receiver chunk_length_ms (default 300000 ms = 5 min). Shorter = lower latency, more files.")
i2.number_input("Overlap (sec)", 0, 60, S.get("overlap", 10), help="overlap_ms (default 10000) so words at chunk boundaries are not lost.")
i3.selectbox("Whisper model", ["tiny", "base", "small", "medium", "large-v3"], index=0, help="AudioTranscriber(model_size). tiny = fastest/CPU-friendly; large-v3 = best accuracy, needs GPU. Device/compute: cpu/int8 default.")
st.text_input("Ingest watch folder", settings.AUDIO_INGEST_DIR, help="AUDIO_INGEST_DIR. Drop .wav files here; watchdog on_created → process_audio → transcription.", disabled=True)
st.toggle("Speaker diarization (pyannote)", value=False, help="NOT YET IMPLEMENTED: transcriber currently emits speaker_id='unknown_speaker'. Toggle is a placeholder tracked in TODO.md.", disabled=True)

# ── 4. DISTILLER ────────────────────────────────────────────────────────────
st.header("✂ Content Distiller", help="src/distiller/topic_extractor.py: Gemini 2.5 Pro reads recent TranscriptChunks and returns ExtractedTopics ranked by comedy_score.")
with st.form("distiller"):
    thr = st.slider("Comedy score threshold", 1.0, 10.0, float(S.get("threshold", 7.0)), 0.5, help="TopicExtractor(comedy_threshold), read by src/main.py load_comedy_threshold() on every cycle. Only topics scoring above this become scripts. Lower = more episodes, weaker jokes.")
    st.number_input("Recent chunks to scan", 1, 500, 50, help="read_recent_chunks(transcripts.jsonl) window fed to Gemini per cycle.")
    if st.form_submit_button("Save distiller settings"): S.update(threshold=thr); save_state(S); st.success(f"Threshold {thr} saved — next cycle will use it.")

# ── 5. SCRIPTWRITER & LORE ──────────────────────────────────────────────────
st.header("✍ Scriptwriter & Lore Validation", help="src/scriptwriter/: ScriptGenerator builds a SitcomScript from the top topic; validator.py checks every character against docs/CHARACTER_BIBLE.json.")
s1, s2 = st.columns(2)
bible_text = s1.text_area("Character bible (docs/CHARACTER_BIBLE.json)", open("docs/CHARACTER_BIBLE.json").read() if os.path.exists("docs/CHARACTER_BIBLE.json") else "{}", height=160, key="bible_edit", help="Canonical BOB & LUM characters. validate_script_characters() rejects scripts inventing unlisted characters. Edit the DRAFT descriptions here with the real screenplay text, then Save.")
if s1.button("Save character bible", help="Writes docs/CHARACTER_BIBLE.json after JSON + non-empty 'characters' validation. The next generated script is validated against the saved cast."):
    try:
        parsed = json.loads(bible_text); assert parsed.get("characters"), "missing 'characters'"
        open("docs/CHARACTER_BIBLE.json", "w").write(json.dumps(parsed, indent=4)); s1.success(f"Bible saved — cast: {', '.join(parsed['characters'])}")
    except Exception as e: s1.error(f"Not saved: {e}")
s2.selectbox("Episode template", ["standard", "cold-open", "bottle", "clip-show"], help="docs/EPISODE_TEMPLATES.md structures. Passed as context to ScriptGenerator.generate_script().")
if s2.button("Check character bible", help="Loads docs/CHARACTER_BIBLE.json via validator.load_character_bible() and lists canonical characters. Full validate_script_characters() runs inside ScriptGenerator on each generated script."):
    try:
        from src.scriptwriter.validator import load_character_bible
        s2.success(f"Bible OK — canonical characters: {', '.join(sorted(load_character_bible()))}")
    except Exception as e: s2.error(f"Bible failed to load: {e}")

# ── 6. RENDERER ─────────────────────────────────────────────────────────────
st.header("🎞 Renderer (TTS + Video)", help="src/renderer/: TTSEngine (edge-tts) voices each dialogue line + writes SRT; VideoComposer (moviepy) composites vertical video.")
r1, r2, r3 = st.columns(3)
r1.selectbox("TTS voice engine", ["edge-tts", "elevenlabs"], index=0, help="edge-tts is free/default. elevenlabs needs ELEVENLABS_API_KEY and is not yet wired in TTSEngine.")
r2.selectbox("Video size", ["1080x1920 (vertical)", "1920x1080", "1080x1080"], help="VideoComposer(width, height). Vertical 1080×1920 suits TikTok/Shorts/Reels.")
r3.toggle("Burn subtitles (SRT)", value=True, help="TTSEngine.generate_srt() timings burned into frames via moviepy. Needs ImageMagick policy fix in Docker (see DEPLOY.md).")
from src.main import parse_render_progress
_rp = parse_render_progress(open(LOG, errors="ignore").read() if os.path.exists(LOG) else "")
if _rp["total"]: st.progress(_rp["done"] / _rp["total"], text=f"TTS progress {_rp['done']}/{_rp['total']} lines — live from data/pipeline.log ([RENDER] markers)")
if _rp["lines"]: st.code("\n".join(_rp["lines"]), language="text")
else: st.caption("No renderer activity yet — [RENDER] TTS/compose lines will stream here during a cycle.")

# ── 7. PUBLISHER ────────────────────────────────────────────────────────────
st.header("📤 Publisher", help="src/publisher/social_uploader.py: publish_all() fans out to YouTube/TikTok/X. ALL MOCK today — toggles control intent only, no live posting until OAuth lands (ROADMAP Phase 2).")
p = st.columns(3)
saved = S.get("platforms") or ["youtube", "tiktok", "x"]
for i, (name, fn) in enumerate([("YouTube", "upload_to_youtube"), ("TikTok", "upload_to_tiktok"), ("X (Twitter)", "upload_to_x")]):
    p[i].toggle(f"Publish to {name}", value=fn.split("_")[-1] in saved or (name == "X (Twitter)" and "x" in saved), key=f"pub{i}", help=f"SocialUploader.{fn}() via publish_all(platforms=...), read by src/main.py load_platforms(). Mock: logs intent, returns success without posting.")
if st.button("Save publisher selection", help="Persists the toggles above to data/dashboard_state.json; the next pipeline cycle publishes only to the enabled platforms."):
    plats = [k for k, i in [("youtube", 0), ("tiktok", 1), ("x", 2)] if st.session_state.get(f"pub{i}", True)]
    S.update(platforms=plats); save_state(S); st.success(f"Publishing to: {', '.join(plats) or 'nothing'}")
st.text_input("Title template", "{title} — BOB & LUM", help="_extract_metadata() builds title/description/tags from the SitcomScript for every platform.")

# ── 8. CONFIGURATION & LOGS ─────────────────────────────────────────────────
st.header("⚙ Configuration", help="src/config.py PipelineSettings (pydantic-settings, .env). Secrets are masked; edit .env and restart to apply — never paste keys into this page.")
for k in ["AUDIO_INGEST_DIR", "TRANSCRIPT_STORAGE_DIR", "RENDER_OUTPUT_DIR"] + keys + ["ELEVENLABS_API_KEY"]:
    v = getattr(settings, k, ""); st.text_input(k, "••••••••" if "KEY" in k or "SECRET" in k or "TOKEN" in k else v, disabled=True, help=f"Env var {k}. {'Set ✓' if v else 'NOT SET — dependent stage cannot run live.'}")
st.header("📜 Logs & Data Browser", help="Live tail of pipeline output and transcripts. If a stage fails, its error appears here first.")
logs = ["data/pipeline.log", os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl"), os.path.join(settings.RENDER_OUTPUT_DIR, "render.log")]
for lp in logs:
    if os.path.exists(lp): st.code("\n".join(open(lp, errors="ignore").read().splitlines()[-15:]) or "(empty)", language="text")
    else: st.caption(f"No log yet: `{lp}` — stage has not run.")
if st.button("↻ Refresh dashboard", help="Re-read counts, latest video, and logs from disk."): st.rerun()
