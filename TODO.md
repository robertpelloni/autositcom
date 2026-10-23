# TODO.md
## Immediate Tasks & Bug Fixes

- [ ] Connect the `SocialUploader` mock endpoints to actual API SDK calls (e.g., proper YouTube OAuth flow).
- [ ] Investigate `moviepy` text rendering issues on minimal Docker images (ensure ImageMagick policy is correctly bypassed in production).
- [ ] Add real-time log tailing to the Streamlit UI dashboard.
- [ ] Implement actual speaker diarization in `src/ingestion/transcriber.py` instead of the "unknown_speaker" mock.
- [ ] Write integration tests that run the entire pipeline end-to-end on a small 10-second sample audio file.