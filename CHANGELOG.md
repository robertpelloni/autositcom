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

## [0.3.0] - 2026-11-13
### Added
- DashboardState pydantic schema (src/config.py) validates data/dashboard_state.json on both sides: dashboard save_state() validates before writing, src.main load_dashboard_state() falls back to full defaults on any invalid value (threshold range, platform enum).

## [0.3.1] - 2026-11-13
### Added
- Renderer emits [RENDER] TTS/compose progress lines; dashboard Renderer section shows a live TTS progress bar + recent render lines parsed from data/pipeline.log (src.main.parse_render_progress).

## [0.3.2] - 2026-11-13
### Changed
- HANDOFF.md rewritten as a complete resume document (verified state, blockers needing a human, operating loop, ordered next steps); ROADMAP progress appended.

## [0.3.3] - 2026-11-13
### Fixed
- Full test suite green (32/32) on the newly created Python 3.12 .venv312 - ingestion and renderer suites now run; scripts/run.ps1 prefers .venv312. Noted ambient GEMINI/OPENAI/ELEVENLABS keys present (no .env file).

## [0.3.4] - 2026-11-13
### Changed
- Character bible corrected from Seinfeld placeholders to the real cast BOB (Robert Pelloni) and LUM (Lumbros Kourlos); descriptions marked DRAFT pending the canonical screenplay text. Voice/color maps and all test fixtures updated to match.

## [0.3.5] - 2026-11-13
### Added
- Dashboard Scriptwriter section: editable Character Bible textarea + Save (JSON/characters validated) so operators can replace the DRAFT BOB & LUM descriptions without hand-editing files. Browser-verified via agent-browser: all sections, health badges, and Help tooltips render.

## [0.3.6] - 2026-11-14
### Fixed
- CRITICAL dashboard crash found by headless-browser verification: st.info(help=...) raised TypeError in Streamlit 1.67, halting the page at Latest Episode - every section below (controls, distiller, bible editor, renderer, publisher, logs) never rendered. Fixed; added AppTest regression test (tests/test_dashboard_bible.py) asserting the full page renders with no exception, valid bible JSON saves with confirmation, and invalid JSON errors without touching the file.
