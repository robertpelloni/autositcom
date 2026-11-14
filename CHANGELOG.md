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

## [0.2.2] - 2026-11-13
### Changed
- run_pipeline_iteration: per-stage try/except - [STAGE-FAIL] distiller/scriptwriter/renderer/publisher logged, dependents [STAGE-SKIP], cycle always returns cleanly (verified: --once exits 0 on empty input).

## [0.2.3] - 2026-11-13
### Added
- End-to-end integration test (tests/test_e2e.py) over committed fixture tests/fixtures/sample_transcripts.jsonl + generated real 10s WAV: distill->script->render->publish orchestration proven with external APIs stubbed at the repo's existing seams.

## [0.2.4] - 2026-11-13
### Added
- Publisher platform filtering: SocialUploader.publish_all(platforms=...) + dashboard Publisher toggles persisted via Save button -> src/main.py load_platforms(). Default None = all platforms (existing callers unchanged).

## [0.2.5] - 2026-11-13
### Added
- Dashboard header stage-health badges (distiller/scriptwriter/renderer/publisher: ok/fail/skip/unknown) parsed from data/pipeline.log via pure src/main.parse_stage_health() with unit tests.

## [0.2.6] - 2026-11-13
### Added
- Tray icon now reflects pipeline health (green healthy / red any stage failed / grey never ran) via the same src/main.parse_stage_health() as the dashboard; tray status menu line lists per-stage state.

## [0.2.7] - 2026-11-13
### Changed
- DEPLOY.md rewritten: Python 3.12 requirement (3.15 native-wheel failures), .venv + scripts/run.ps1 launch, --once, tray health colors, operator state/logs, test + troubleshooting matrix.

## [0.2.8] - 2026-11-13
### Changed
- README/VISION/IDEAS synced with 0.2.x reality (consolidated dashboard, health badges, tray colors, E2E-tested orchestration; live-episode blockers stated plainly).

## [0.2.9] - 2026-11-13
### Added
- Tray 'Run Cycle Now' menu action: spawns src.main --once (BelowNormal, data/pipeline.log), notifies on start/finish, loudly notifies failed stages, and refreshes the health-colored icon.
