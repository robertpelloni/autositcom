# DEPLOY.md — Autositcom deployment & operations (v0.2.7)

## Prerequisites
- **Python 3.12** for local runs (Docker uses `python:3.12-slim`). Do NOT use
  Python 3.15 locally: `av` (faster-whisper), `pyaudioop` (pydub) and moviepy's
  Pillow pin have no 3.15 wheels — ingestion/renderer stages will log
  `[STAGE-FAIL]` and skip. Everything else (dashboard, distiller, publisher,
  tests for those stages) runs on 3.15.
- `ffmpeg` + ImageMagick on PATH for rendering; a `.env` with API keys (below).

## 1. Configure environment
Create `.env` (never commit it):
```ini
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_CLIENT_SECRET=your_youtube_secret
TIKTOK_SESSION_TOKEN=your_tiktok_token
# Optional: OPENAI_API_KEY, ELEVENLABS_API_KEY
```
Check what is configured — without printing secrets — in the dashboard's
Configuration section or health metric (`API keys configured n/4`).

## 2. Run with Docker Compose (recommended, full pipeline)
```bash
docker compose up --build -d   # pipeline only (python -m src.main)
```
Dockerfile already fixes the ImageMagick policy that moviepy text needs.

## 3. Run locally (development)
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt pytest
.\scripts\run.ps1 all        # pipeline + dashboard + tray, all BelowNormal priority
```
Or individually: `.\scripts\run.ps1 dashboard|pipeline|tray`. Heavy processes
are always started BelowNormal so the machine never hangs.

| Component | Command | Notes |
|---|---|---|
| Dashboard | `streamlit run src/dashboard.py` | http://localhost:8501 — single consolidated page |
| Pipeline (24/7) | `python -m src.main` | Ingestion listener + cycle every 3600s |
| One cycle | `python -m src.main --once` | Used by the dashboard Run Cycle button; exits 0 even when a stage fails |
| Tray | `python -m src.tray` | Icon: green healthy / red stage failed / grey never ran; menu can stop servers + quit |

## 4. Operator state & logs
- `data/dashboard_state.json` — dashboard settings (comedy threshold, publisher
  platform selection). Written by the UI, read by `src.main` every cycle
  (`load_comedy_threshold()`, `load_platforms()`); edit via the UI, not by hand.
- `data/pipeline.log` — cycle output with `[STAGE-FAIL]`/`[STAGE-SKIP]` markers;
  tailed in the dashboard Logs section and parsed for its health badges.
- Data dirs (`data/audio_ingest`, `data/transcripts`, `data/render_output`) are
  config keys `AUDIO_INGEST_DIR` / `TRANSCRIPT_STORAGE_DIR` / `RENDER_OUTPUT_DIR`.

## 5. Tests
```powershell
.venv\Scripts\python.exe -m pytest tests/ -q
```
On Python 3.15, expect ingestion/renderer collection errors (missing native
wheels) — run the full suite in Docker or a 3.12 venv. The E2E test
(`tests/test_e2e.py`) stubs external APIs at the usual seams and runs anywhere.

## 6. Troubleshooting
| Symptom | Cause / fix |
|---|---|
| `[STAGE-FAIL] renderer: No module named edge_tts/moviepy` | Wrong interpreter — use 3.12 venv or Docker |
| Dashboard cycle does nothing visible | Check `data/pipeline.log`; no transcripts = "No high-value topics" (healthy no-op) |
| Publisher stages all skipped | No platform selected in dashboard Publisher section, or credentials empty |
| `git push` rejected "Invalid username or token" | Re-authenticate Git (credential manager / PAT); commits are local until then |
