import os
from typing import List, Dict
from moviepy import AudioFileClip, ColorClip, TextClip, concatenate_videoclips, CompositeVideoClip
from src.schemas import SitcomScript, RenderedEpisode
from src.config import settings

class VideoComposer:
    def __init__(self, width=1080, height=1920):
        self.width = width
        self.height = height
        os.makedirs(settings.RENDER_OUTPUT_DIR, exist_ok=True)

        # Color palette mapping for characters
        self.char_colors = {
            "JERRY": (0, 0, 255),    # Blue
            "GEORGE": (255, 0, 0),   # Red
            "ELAINE": (0, 255, 0),   # Green
            "KRAMER": (255, 165, 0)  # Orange
        }

    def create_line_clip(self, audio_asset: Dict) -> CompositeVideoClip:
        """
        Creates a video clip for a single line of dialogue.
        It uses a solid color background based on the character and overlays text.
        """
        # Load audio
        audio_clip = AudioFileClip(audio_asset["audio_path"])
        duration = audio_clip.duration

        # Create background
        char_name = audio_asset["character"].upper()
        bg_color = self.char_colors.get(char_name, (0, 0, 0))
        bg_clip = ColorClip(size=(self.width, self.height), color=bg_color, duration=duration)

        # We need to manually set fps on ColorClip if it's missing (MoviePy v2 requirement)
        bg_clip = bg_clip.with_fps(24)

        # Create text overlay
        try:
            txt_clip = TextClip(
                text=f"{char_name}:\n{audio_asset['text']}",
                font="Arial",
                font_size=50,
                color='white',
                method="caption",
                size=(self.width - 100, None) # Allow wrapping
            )
            # Position at center, match duration
            txt_clip = txt_clip.with_position('center').with_duration(duration)
        except Exception as e:
            # Fallback if ImageMagick is not configured correctly on host
            print(f"Warning: Text rendering failed, using empty text overlay. Error: {e}")
            txt_clip = ColorClip(size=(self.width, self.height), color=bg_color, duration=duration).with_fps(24)

        # Composite video
        video = CompositeVideoClip([bg_clip, txt_clip]).with_audio(audio_clip)
        return video

    def compose_episode(self, script: SitcomScript, audio_assets: List[Dict]) -> RenderedEpisode:
        """
        Takes the script and generated audio assets, strings them together, and exports an mp4.
        """
        video_clips = []
        for asset in audio_assets:
            clip = self.create_line_clip(asset)
            video_clips.append(clip)

        final_video = concatenate_videoclips(video_clips)

        output_path = os.path.join(settings.RENDER_OUTPUT_DIR, f"{script.script_id}_final.mp4")
        thumb_path = os.path.join(settings.RENDER_OUTPUT_DIR, f"{script.script_id}_thumb.jpg")

        # Export video (requires ffmpeg installed on system)
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast" # Speed up testing
        )

        # Save a thumbnail frame
        final_video.save_frame(thumb_path, t=0)

        # Close clips to free memory
        for clip in video_clips:
            clip.close()
        final_video.close()

        return RenderedEpisode(
            episode_id=script.script_id,
            video_path=output_path,
            duration_seconds=final_video.duration,
            thumbnail_path=thumb_path
        )