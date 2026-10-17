from pydantic_settings import BaseSettings, SettingsConfigDict

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