# IDEAS.md
## Aggressive Pivots & Expansions

- **3D Rendering Pipeline:** Rip out MoviePy and replace it with a headless Blender rendering script that animates 3D avatars lip-syncing to the TTS audio.
- **Voice Cloning:** Upgrade `edge-tts` to ElevenLabs or Coqui TTS to dynamically clone the voices of the real people from the ingested audio streams.
- **Live Stream Output:** Instead of publishing pre-rendered VODs, stream the output directly to a 24/7 Twitch or YouTube Live channel, buffering generated scenes into a continuous broadcast.
- **Audience Interaction:** Allow Twitch chat to vote on the next topic to be extracted from the transcript backlog.
- **Language Porting:** Port the heavy rendering and chunking components to Rust or Go for massive performance gains, leaving Python strictly for orchestration and ML API orchestration.
## Near-Term, Grounded (from 0.2.x operations)
- **Health-driven tray actions:** tray menu 'Run cycle now' + balloon notification when a stage turns red.
- **Dashboard render progress:** stream per-line TTS/compose progress from pipeline.log into the Renderer section.
- **State schema:** version data/dashboard_state.json and validate it in src/config.py so dashboard and pipeline cannot drift.
- **Bible-driven casting:** once the real BOB & LUM bible lands, add a dashboard character editor writing docs/CHARACTER_BIBLE.json.
