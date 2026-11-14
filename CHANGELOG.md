# CHANGELOG.md
## [0.1.0] - 2024-10-24
### Added
- Initial project scaffolding and architecture design.
- Pydantic configurations and data schemas.
- Audio Ingestion service utilizing `watchdog` and `pydub`.
- Live Transcription Engine utilizing `faster-whisper`.
- Content Distiller utilizing Gemini 2.5 Pro.
- Lore-compliant Sitcom Script Generator utilizing Gemini 2.5 Pro.
- Audio & Video Rendering Engine utilizing `edge-tts` and `moviepy`.
- Multi-Platform Publisher mock integration for YouTube, TikTok, and X.
- Main orchestrator script (`src/main.py`) for continuous async execution.
- Dockerfile and `docker-compose.yml` for containerized deployment.
- Initial global documentation suite.
## [0.2.0] - 2026-11-13
### Changed
- Dashboard consolidated to one page ordered by value (episode/health, controls, ingestion, distiller, scriptwriter/lore, renderer, publisher, config, logs); every backend feature now has a labelled control + tooltip; settings persist to data/dashboard_state.json.
- Tray rewritten: browser-open (no duplicate Streamlit), Start Dashboard/Pipeline, Stop Servers, Quit, live status, BelowNormal children.
- Added scripts/run.ps1 unified BelowNormal launcher.

## [0.2.1] - 2026-11-13
### Added
- Dashboard Run Cycle now spawns real `python -m src.main --once` (BelowNormal, logs to data/pipeline.log, shown in Logs); Character Bible check runs real validator.load_character_bible().
- src/main.py: load_comedy_threshold() reads dashboard state; lazy stage imports so missing native deps (pyaudioop/av/edge-tts on Python 3.15) fail one stage, not startup.
### Fixed
- Distiller form saved hardcoded 7.0 regardless of slider; test_config isolated from ambient API-key env vars.
