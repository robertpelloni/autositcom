# autositcom

An automated sitcom pipeline for **"BOB & LUM"** — a dark-comedy/adult-animation sitcom starring Robert Pelloni and Lumbros "Lum" Kourlos (the screenplay lives at [robertpelloni.com/script](https://robertpelloni.com/script/)). The pipeline's goal: record two people's real conversations, transcribe and distill them into the best topics and dialogue, generate new sitcom episodes in the established style from that material, render them as video, and post them to video platforms.

## Status

**Early implementation. Pipeline orchestration is proven by an end-to-end integration test with external APIs stubbed (tests/test_e2e.py); no live episode has been produced yet.** Version 0.2.8. The repo began as a design/spec document; implementation of all five subsystems landed in October 2026 (built by Google Jules agent tasks, merged to main 2026-11-05). No end-to-end run or published episode from this pipeline has been verified — treat it as a first implementation of the blueprint, not a working production system.

## The five subsystems

1. **Ingestion & Transcription** (`src/ingestion/`) — audio capture (watchdog + pydub), live transcription via faster-whisper
2. **Topic Analysis & Distillation** (`src/distiller/`) — selecting the most interesting topics/dialogue, using Gemini 2.5 Pro
3. **Script & Lore Generator** (`src/scriptwriter/`) — episode scripts in the show's style, grounded in distilled material and prior episodes
4. **Audio/Visual Render Engine** (`src/renderer/`) — episode rendering with edge-tts and moviepy
5. **Multi-Platform Publisher** (`src/publisher/`) — mock integration for YouTube, TikTok, and X (not a live publisher)

Plus: `src/main.py` orchestrator, `src/dashboard.py` UI, `src/tray.py` system tray, `Dockerfile` / `docker-compose.yml` for containerized deployment.

## What's not done

- No verified end-to-end run (record → transcribe → script → render → publish).
- Publisher is a mock — no real platform posting.
- `CHANGELOG.md` dates the 0.1.0 release to 2024-10-24, which is wrong; the code landed in October 2026.

## Docs in this repo

`VISION.md`, `ROADMAP.md`, `TODO.md`, `HANDOFF.md`, `MEMORY.md`, `IDEAS.md`, `DEPLOY.md`, `docs/`.

## Operations (0.2.x)

- **Dashboard** (`src/dashboard.py`): single consolidated page - episode/health first, then controls, ingestion, distiller, scriptwriter/lore, renderer, publisher, config, logs. Every backend feature has a labelled control with a tooltip; Run Cycle spawns a real `python -m src.main --once`.
- **Tray** (`python -m src.tray`): icon is green (healthy), red (a stage failed), or grey (never ran); menu opens the dashboard, starts/stops servers, and quits.
- **Health**: per-stage badges in the dashboard and tray color both come from `src.main.parse_stage_health()` over `data/pipeline.log`.
- **Run it**: `.\scripts\run.ps1 all` (BelowNormal), then open http://localhost:8501. Full setup in `DEPLOY.md`.

