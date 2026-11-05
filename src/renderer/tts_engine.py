import os
import asyncio
import edge_tts
from typing import Dict, List, Tuple
from src.schemas import SitcomScript
from src.config import settings

class TTSEngine:
    def __init__(self):
        # We can map specific characters to specific voices
        self.voice_map: Dict[str, str] = {
            "JERRY": "en-US-GuyNeural",
            "GEORGE": "en-US-ChristopherNeural",
            "ELAINE": "en-US-AriaNeural",
            "KRAMER": "en-US-EricNeural"
        }
        self.default_voice = "en-US-GuyNeural"
        os.makedirs(settings.RENDER_OUTPUT_DIR, exist_ok=True)

    def format_time(self, seconds: float) -> str:
        """Formats time in seconds into SRT timestamp format (HH:MM:SS,ms)."""
        millisecs = int((seconds - int(seconds)) * 1000)
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02}:{mins:02}:{secs:02},{millisecs:03}"

    async def generate_line_audio(self, text: str, character: str, output_path: str) -> List[Tuple[float, float, str]]:
        """
        Generates audio for a single line using edge-tts.
        Returns word boundaries for subtitle generation.
        """
        voice = self.voice_map.get(character.upper(), self.default_voice)
        communicate = edge_tts.Communicate(text, voice)

        # We'll save the audio and collect subtitles (word boundaries)
        subtitles = []
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Convert edge-tts ticks (100ns) to seconds
                    start_time = chunk["offset"] / 10_000_000
                    duration = chunk["duration"] / 10_000_000
                    end_time = start_time + duration
                    subtitles.append((start_time, end_time, chunk["text"]))

        return subtitles

    def generate_srt(self, subtitles: List[Tuple[float, float, str]], srt_path: str):
        """Generates an SRT file from word boundaries."""
        with open(srt_path, 'w', encoding='utf-8') as f:
            for idx, (start, end, text) in enumerate(subtitles, 1):
                f.write(f"{idx}\n")
                f.write(f"{self.format_time(start)} --> {self.format_time(end)}\n")
                f.write(f"{text}\n\n")

    async def generate_scene_audio(self, script: SitcomScript) -> List[Dict]:
        """
        Generates audio for all lines in the script.
        Returns a list of metadata for the composer.
        """
        audio_assets = []
        for scene in script.scenes:
            for line_idx, line_dict in enumerate(scene.dialogue):
                for character, text in line_dict.items():
                    base_filename = f"{script.script_id}_scene_{scene.scene_number}_line_{line_idx}"
                    audio_path = os.path.join(settings.RENDER_OUTPUT_DIR, f"{base_filename}.mp3")
                    srt_path = os.path.join(settings.RENDER_OUTPUT_DIR, f"{base_filename}.srt")

                    subtitles = await self.generate_line_audio(text, character, audio_path)
                    self.generate_srt(subtitles, srt_path)

                    audio_assets.append({
                        "scene_number": scene.scene_number,
                        "character": character,
                        "audio_path": audio_path,
                        "srt_path": srt_path,
                        "text": text
                    })
        return audio_assets