# MEMORY.md
## Architectural Observations
- The system is built as 5 distinct microservices using Python and Docker.
- Communication between services is primarily file-based (JSONL, WAV, MP4) rather than using an external message queue or database, which keeps the system lightweight but requires careful file management (e.g., watchdog for ingestion).

## Codebase Traits
- **Data Modeling:** Heavily relies on Pydantic `BaseModel` and `pydantic-settings` for robust schema validation and environment management.
- **Testing:** Comprehensive test coverage using `pytest` and `unittest.mock` to simulate external APIs (Gemini, Whisper, Social APIs) and heavy processing (MoviePy).
- **Extensibility:** The architecture is designed to easily swap out components (e.g., changing `faster-whisper` for a cloud API, or `edge-tts` for ElevenLabs).

## Design Preferences
- Prefer simple, robust, and readable implementations over complex abstractions.
- All configuration must reside in environment variables loaded into a single `Settings` object.
- Strive for complete autonomy; error handling should recover or log and skip, never crash the main process.