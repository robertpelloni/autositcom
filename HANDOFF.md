# HANDOFF.md — Autositcom session handoff (v0.3.2, 2026-11-13)

## What this project is
"BOB & LUM" automated sitcom pipeline: record real conversations → transcribe
(faster-whisper) → distill topics (Gemini) → generate lore-checked scripts →
render vertical video (edge-tts + moviepy) → publish (YouTube/TikTok/X, mock).
Five subsystems in `src/{ingestion,distiller,scriptwriter,renderer,publisher}`,
orchestrated by `src/main.py`, operated from `src/dashboard.py` + `src/tray.py`.

## Current state (verified this session)
- **Dashboard** (`src/dashboard.py`): ONE consolidated page, value-ordered —
  Latest Episode & Health (metrics + stage badges) → Pipeline Controls →
  Ingestion & Transcription → Distiller → Scriptwriter & Lore → Renderer
  (live TTS progress bar) → Publisher (working platform toggles) → Config
  (masked) → Logs. Every control has a `help=` tooltip. Settings persist to
  `data/dashboard_state.json`, validated by `DashboardState` in `src/config.py`.
- **Run Cycle is real**: dashboard/tray spawn `python -m src.main --once`
  (BelowNormal priority) logging to `data/pipeline.log`. `main.py` guards each
  stage with `[STAGE-FAIL]`/`[STAGE-SKIP]` logging and always exits 0.
  `load_comedy_threshold()`/`load_platforms()` read the validated state file.
- **Tray** (`src/tray.py`, `python -m src.tray`): menu = status, Open Dashboard
  (browser), Start Dashboard, Start Pipeline, Run Cycle Now (notifies on
  failure), Stop Servers, Quit. Icon color = pipeline health (green/red/grey)
  via the same `src.main.parse_stage_health()` the dashboard badges use.
- **Tests**: 29 passing (config, distiller, publisher, scriptwriter, tray,
  main-state, E2E). `tests/test_e2e.py` runs the full cycle over
  `tests/fixtures/sample_transcripts.jsonl` + a real generated 10s WAV with
  Gemini/TTS/moviepy/social stubbed at the repo's existing seams.
- **Launch**: `.\scripts\run.ps1 all` (BelowNormal) → http://localhost:8501.
  Deployment truth is in `DEPLOY.md`.

## What is NOT working (needs a human / external access)
1. **Git push blocked**: `Invalid username or token` — many local commits
   pending. Re-authenticate Git, then `git push origin main`.
2. **No live episode yet**: needs `GEMINI_API_KEY` in `.env` (dashboard shows
   keys configured 0/4) plus real transcripts in `data/transcripts/`.
3. **Character bible is placeholder**: `docs/CHARACTER_BIBLE.json` contains
   Seinfeld characters (JERRY/GEORGE/ELAINE/KRAMER), NOT BOB & LUM. Replace
   from robertpelloni.com/script before any live script generation. Voice/color
   maps in `tts_engine.py`/`video_composer.py` key off those same names.
4. **Publisher is mock**: `publish_all(platforms=...)` filtering works, but
   uploads are simulated; real OAuth (YouTube/TikTok/X) is ROADMAP Phase 2.
5. **Diarization mock**: transcriber emits `unknown_speaker`; pyannote pending.
6. **Python 3.15 limits**: `av`/`pyaudioop`/moviepy have no 3.15 wheels —
   ingestion/renderer suites only run on Python 3.12 or Docker
   (`python:3.12-slim`). The local `.venv` is 3.15; use Docker for full suite.

## Operating loop
A permanent Muse cron (`*/15`, "continue to proceed as you advise") advances
this work: dashboard coverage → wiring → guards → tests → docs, one versioned
commit per step (`VERSION.md` is the single version source; every bump is a
commit named `feat/docs: vX.Y.Z ...`). Pushes fail until item 1 is fixed.

## Next recommended steps (in order)
1. Human: fix Git auth + push; add `GEMINI_API_KEY` to `.env`.
2. Replace character bible with real BOB & LUM entries; update voice/color maps.
3. Run one live `--once` cycle on real transcripts; watch the dashboard.
4. Real publisher OAuth; pyannote diarization; Python 3.12 CI for full suite.

## Update 0.3.3
- FULL SUITE GREEN: Python 3.12 exists on this machine; .venv312 created, `pip install -r requirements.txt` succeeds, **32/32 tests pass** including ingestion+renderer. scripts/run.ps1 now prefers .venv312. GEMINI_API_KEY + OPENAI + ELEVENLABS are set in the ambient environment (no .env file; YOUTUBE/TIKTOK unset). Remaining human blockers: git push auth, real BOB & LUM bible. A live cycle is now possible once real transcripts exist.
