from pydantic import BaseModel
from typing import List, Dict

class TranscriptChunk(BaseModel):
    ID: str
    timestamp: float
    speaker_id: str
    text: str
    audio_path: str

class ExtractedTopic(BaseModel):
    topic_id: str
    title: str
    summary: str
    key_quotes: List[str]
    comedy_score: float
    source_chunk_ids: List[str]

class ScriptScene(BaseModel):
    scene_number: int
    setting: str
    dialogue: List[Dict[str, str]]
    visual_action_notes: str

class SitcomScript(BaseModel):
    script_id: str
    title: str
    theme: str
    characters: List[str]
    scenes: List[ScriptScene]

class RenderedEpisode(BaseModel):
    episode_id: str
    video_path: str
    duration_seconds: float
    thumbnail_path: str