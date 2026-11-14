from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DashboardState(BaseModel):
    """Contract for data/dashboard_state.json, written by the dashboard and
    read by src.main every cycle. WHY validate: two writers/readers on one
    untyped JSON file drift silently — a bad value must fall back to defaults,
    never crash the 24/7 loop or publish to the wrong platforms."""
    threshold: float = Field(7.0, ge=1.0, le=10.0)
    platforms: Optional[List[Literal["youtube", "tiktok", "x"]]] = None
    auto: bool = False
    model_config = {"extra": "allow"}  # dashboard may add UI-only keys

class PipelineSettings(BaseSettings):
    AUDIO_INGEST_DIR: str = "data/audio_ingest"
    TRANSCRIPT_STORAGE_DIR: str = "data/transcripts"
    RENDER_OUTPUT_DIR: str = "data/render_output"

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""

    YOUTUBE_CLIENT_SECRET: str = ""
    TIKTOK_SESSION_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = PipelineSettings()