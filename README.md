# autositcom

**Design/spec repository** for an automated sitcom pipeline ("BOB & LUM"): a system that records two people's real conversations 24/7 on a pocket recorder, transcribes and distills them into the best topics and dialogue, generates new sitcom episodes in the established style from that material, renders them as video, and posts them to video platforms.

## Current state of this repo

This repo currently contains **only the design document** — there is no code here yet. The full architecture specification (previously the entire README, written as a build brief for an AI coding agent) covers five subsystems:

1. **Ingestion & Transcription** — real-time audio capture (RTSP/WebRTC/upload from pocket recorders/phones), chunked transcription
2. **Topic Analysis & Distillation** — selecting the most interesting topics/dialogue from the transcript stream
3. **Script & Lore Generator** — episode scripts in the show's style, grounded in the distilled material and prior episodes' documentation
4. **Audio/Visual Render Engine** — rendering episodes using the documented style/techniques, compiling clips into episodes
5. **Multi-Platform Publisher** — posting finished episodes to video platforms

The show itself: **BOB & LUM** — a dark-comedy/adult-animation sitcom starring Robert Pelloni and Lumbros "Lum" Kourlos; the screenplay lives at [robertpelloni.com/script](https://robertpelloni.com/script/).

## Status

Spec stage. Implementation has not landed in this repo; treat everything here as the blueprint, not a runnable system.
