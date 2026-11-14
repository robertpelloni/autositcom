# TODO.md
## Immediate Tasks & Bug Fixes

- [ ] Connect the `SocialUploader` mock endpoints to actual API SDK calls (e.g., proper YouTube OAuth flow).
- [ ] Investigate `moviepy` text rendering issues on minimal Docker images (ensure ImageMagick policy is correctly bypassed in production).
- [ ] Add real-time log tailing to the Streamlit UI dashboard.
- [ ] Implement actual speaker diarization in `src/ingestion/transcriber.py` instead of the "unknown_speaker" mock.
- [ ] Write integration tests that run the entire pipeline end-to-end on a small 10-second sample audio file.
## Done 2026-11-13 (0.2.0)
- [x] Consolidated dashboard to single page, all subsystems represented with tooltips/forms; tray fixed (browser-open, stop/quit, status).
## Next
- [ ] Wire dashboard Run Cycle button to actual src.main.run_pipeline_iteration() subprocess (currently toast-only).
- [ ] Wire distiller threshold slider persistence into TopicExtractor call (state file read in main.py).
- [ ] Real diarization, real OAuth publisher, end-to-end 10s sample integration test.
- [x] Wire Run Cycle + threshold persistence (0.2.1). Next: per-stage try/except in run_pipeline_iteration so a missing renderer dep still publishes/logs cleanly; Python 3.12 venv for full suite.
- [x] E2E integration test on sample transcripts (0.2.3). FINDING: docs/CHARACTER_BIBLE.json still contains Seinfeld placeholder characters (JERRY/GEORGE/ELAINE/KRAMER), not BOB & LUM - replace with real bible before live script generation.
- [ ] Replace DRAFT bible descriptions with canonical BOB & LUM text from robertpelloni.com/script (site unreachable from this machine; needs user paste).
