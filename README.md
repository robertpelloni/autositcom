# autositcom


please make detailed instructions on a comprehensive design for a realtime tv show which takes 24/7 transcripts from pocket recorder and then distills the conversations and takes the best and most interesting topics and dialogue and uses it as the basis for more sitcom episodes in the same style and theme as the previous episodes and content, based on the documentation from their generation, and then renders it out using style and techniques in documentation, compiles clips into episode, and posts to all video platforms, with detailed instructions to build it to give to google jules to build it on autopilot 

Here is an architecture specification and implementation prompt suite designed to delegate the end-to-end development of this continuous content production pipeline to Google Jules.

Because Jules operates asynchronously by cloning your repository, writing code inside a secure cloud VM, running tests, and submitting PRs, this plan breaks down the software into explicit modular sub-systems with concrete schemas, tests, and CLI task descriptions.   
Morph

System Architecture Overview
 ┌────────────────┐     ┌──────────────────┐     ┌───────────────────┐
 │ 24/7 Audio Stream│ ──> │ 1. Ingestion &   │ ──> │ 2. Topic Analysis │
 │ (Pocket Recorder)│     │    Transcription │     │    & Distillation │
 └────────────────┘     └──────────────────┘     └───────────────────┘
                                                           │
 ┌────────────────┐     ┌──────────────────┐               ▼
 │ 5. Multi-Platform│ <── │ 4. Audio/Visual  │ <── ┌───────────────────┐
 │    Publisher   │     │    Render Engine │     │ 3. Script & Lore  │
 └────────────────┘     └──────────────────┘     │    Generator      │
                                                 └───────────────────┘
The system consists of five microservices orchestrated via Python/Docker:

ingestion: Captures real-time audio streams (RTSP/WebRTC/FTP upload from local pocket recorders/phones), chunks audio, and generates diarized transcripts using Whisper / Deepgram.

distiller: Uses Gemini 2.5/3 Pro to parse raw stream logs, remove fluff/fillers, extract theme-based narrative seeds, and tag memorable quotes.

scriptwriter: Ingests lore/style documentation (docs/style_guide.md, docs/character_bible.json, docs/episode_templates/) and converts extracted narrative seeds into full, multi-character sitcom scripts.

renderer: Programmatically orchestrates video production using automated TTS (or voice cloning), 2D/3D visual renderers (e.g., Blender/Godot/Manim/Canvas pipelines), sound design, and FFmpeg composition.

publisher: Handles automated, scheduled posting to YouTube, TikTok, Instagram Reels, and X using platform APIs.

1. Repository File Structure & Setup Instructions
Create a GitHub repository initialized with the following structure:

Plaintext
tv-production-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── STYLE_GUIDE.md
│   ├── CHARACTER_BIBLE.json
│   └── EPISODE_TEMPLATES.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── audio_receiver.py
│   │   └── transcriber.py
│   ├── distiller/
│   │   ├── __init__.py
│   │   └── topic_extractor.py
│   ├── scriptwriter/
│   │   ├── __init__.py
│   │   └── script_generator.py
│   ├── renderer/
│   │   ├── __init__.py
│   │   ├── tts_engine.py
│   │   └── video_composer.py
│   └── publisher/
│       ├── __init__.py
│       └── social_uploader.py
├── tests/
│   ├── test_ingestion.py
│   ├── test_distiller.py
│   ├── test_scriptwriter.py
│   ├── test_renderer.py
│   └── test_publisher.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
2. Phase-by-Phase Task Prompts for Google Jules
Copy and paste the following sequential prompts into Google Jules (via web UI or CLI: jules remote new --session "...").

Task 1: Environment Core Setup & Config Framework
Jules Prompt:

Plaintext
Project Task: Initialize Configuration and Pipeline Data Schemas

1. In `src/config.py`, build a Pydantic Settings class (`PipelineSettings`) loading from environment variables:
   - AUDIO_INGEST_DIR, TRANSCRIPT_STORAGE_DIR, RENDER_OUTPUT_DIR
   - OPENAI_API_KEY, GEMINI_API_KEY, ELEVENLABS_API_KEY
   - YOUTUBE_CLIENT_SECRET, TIKTOK_SESSION_TOKEN
2. Create Pydantic data models in `src/schemas.py`:
   - `TranscriptChunk`: ID, timestamp, speaker_id, text, audio_path.
   - `ExtractedTopic`: topic_id, title, summary, key_quotes (list[str]), comedy_score (float), source_chunk_ids (list[str]).
   - `ScriptScene`: scene_number, setting, dialogue (list of dict with speaker and line), visual_action_notes.
   - `SitcomScript`: script_id, title, theme, characters (list[str]), scenes (list[ScriptScene]).
   - `RenderedEpisode`: episode_id, video_path, duration_seconds, thumbnail_path.
3. Add pytest unit tests in `tests/test_config.py` validating that settings load defaults and schema models validate correctly.
Task 2: Audio Ingestion & Live Transcription Engine
Jules Prompt:

Plaintext
Project Task: Build Audio Ingestion & Realtime Transcription Engine

1. Implement `src/ingestion/audio_receiver.py`:
   - Listen for continuous incoming audio files or streams saved to `AUDIO_INGEST_DIR`.
   - Automatically chunk incoming continuous audio into 5-minute WAV segments with rolling overlapping buffers (10s buffer).
2. Implement `src/ingestion/transcriber.py`:
   - Use faster-whisper or a cloud API fallback (Deepgram/Whisper) to transcribe 5-minute audio chunks.
   - Output speaker-diarized JSON matching the `TranscriptChunk` schema.
   - Append output to SQLite/PostgreSQL database or JSON line stream in `TRANSCRIPT_STORAGE_DIR`.
3. Write unit tests in `tests/test_ingestion.py` using mock audio signals to ensure audio chunking and transcript parsing function without errors.
Task 3: Content Distiller & Topic Selection Engine
Jules Prompt:

Plaintext
Project Task: Build Conversational Topic Distiller

1. Implement `src/distiller/topic_extractor.py`:
   - Read rolling transcript chunks from the database/storage over a specified interval (e.g., last 24 hours).
   - Use Gemini 2.5 Pro via Google GenAI SDK to filter out background noise, filler words, and dull banter.
   - Extract high-value, humorous, absurd, or deep conversation topics, ranking them with a `comedy_score` (0.0 - 10.0) and identifying core character dynamics.
   - Output an array of validated `ExtractedTopic` objects.
2. Include prompt templates in `src/distiller/prompts.py` enforcing structured JSON responses.
3. Write unit tests in `tests/test_distiller.py` mocking Gemini responses to verify score thresholding and topic filtering logic.
Task 4: Lore-Compliant Sitcom Script Generator
Jules Prompt:

Plaintext
Project Task: Build Sitcom Script Generation Engine

1. Implement `src/scriptwriter/script_generator.py`:
   - Load lore and formatting guides from `docs/STYLE_GUIDE.md` and `docs/CHARACTER_BIBLE.json`.
   - Accept an `ExtractedTopic` object and synthesize a full multi-scene sitcom script (`SitcomScript`).
   - Ensure script dialogue retains the authentic voice, jokes, and arguments from the real-life audio transcripts while transforming them into a structured sitcom format (setup, escalating conflict, punchline, resolution).
   - Format output script to conform to standardized screenplay conventions (scene headings, character names, parentheticals, action lines).
2. Add validation in `src/scriptwriter/validator.py` to confirm character names match `docs/CHARACTER_BIBLE.json`.
3. Create unit tests in `tests/test_scriptwriter.py` verifying full pipeline generation from topic input to valid `SitcomScript`.
Task 5: Audio & Video Automated Rendering Engine
Jules Prompt:

Plaintext
Project Task: Implement Video Composition & Rendering Engine

1. Implement `src/renderer/tts_engine.py`:
   - Convert `SitcomScript` dialogue lines into audio files using ElevenLabs / Edge-TTS with assigned character voice IDs.
   - Generate matching subtitle timing tracks (.srt / .ass).
2. Implement `src/renderer/video_composer.py`:
   - Use MoviePy / FFmpeg / OpenCV to compile visual elements matching the scene descriptions:
     * Overlay animated avatar sprites or dynamic visual waves / background plates matching character states.
     * Burn in stylized dynamic subtitles (word-by-word highlight).
     * Mix background sound effects (laughtrack, transition stingers) at appropriate cue points based on script tags.
   - Export high-definition final render `.mp4` (1080x1920 vertical for Shorts/Reels/TikTok and 1920x1080 horizontal for YouTube).
3. Write tests in `tests/test_renderer.py` generating a 5-second test video clip to verify FFmpeg pipeline completion.
Task 6: Multi-Platform Automated Publisher
Jules Prompt:

Plaintext
Project Task: Implement Automated Social Media Publisher

1. Implement `src/publisher/social_uploader.py`:
   - Create upload wrappers for YouTube Data API v3 (Shorts/Full episodes), TikTok API, and X (Twitter) API.
   - Extract title, description, and hashtags automatically from `SitcomScript` metadata.
   - Add retry logic and upload progress tracking.
2. Create `src/main.py` entry point orchestrating the entire automated loop:
   `Ingest -> Distill -> Write Script -> Render Video -> Publish`.
3. Add `docker-compose.yml` defining services for continuous background execution.
4. Add unit tests in `tests/test_publisher.py` with API endpoints fully mocked.
3. How to Deploy to Google Jules
Push your initial folder structure and documentation files (docs/STYLE_GUIDE.md, docs/CHARACTER_BIBLE.json) to your GitHub repository.

Install the Jules CLI:

Bash
npm install -g @google/jules
jules login
Issue tasks sequentially:

Bash
jules remote new --session "Task 1: Environment Core Setup & Config Framework"
As Jules opens Pull Requests on GitHub, review the code diffs, run pytest, merge the PRs, and launch the next session!

Would you like to customize the specific visual rendering engine (e.g., Blender 3D scripts, 2D VTuber sprites, or dynamic motion graphics) or refine the character bible details first?
