import os
import json
import uuid
from google import genai
from src.config import settings
from src.schemas import ExtractedTopic, SitcomScript
from src.scriptwriter.validator import validate_script_characters

class ScriptGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-pro"

        # Load context
        self.style_guide = self._read_file("docs/STYLE_GUIDE.md")
        self.character_bible = self._read_file("docs/CHARACTER_BIBLE.json")

    def _read_file(self, filepath: str) -> str:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def generate_script(self, topic: ExtractedTopic) -> SitcomScript | None:
        """
        Synthesizes a SitcomScript from an ExtractedTopic.
        """
        prompt = f"""
You are an expert sitcom scriptwriter.
Based on the following topic, character bible, and style guide, write a multi-scene sitcom script.

### STYLE GUIDE
{self.style_guide}

### CHARACTER BIBLE
{self.character_bible}

### EPISODE TOPIC
Title: {topic.title}
Summary: {topic.summary}
Key Quotes: {", ".join(topic.key_quotes)}

### OUTPUT REQUIREMENT
Return ONLY a valid JSON object matching this structure exactly (no markdown formatting or extra text):
{{
    "script_id": "string",
    "title": "string",
    "theme": "string",
    "characters": ["string", "string"],
    "scenes": [
        {{
            "scene_number": 1,
            "setting": "string",
            "visual_action_notes": "string",
            "dialogue": [
                {{"CHARACTER_NAME": "Their spoken line."}}
            ]
        }}
    ]
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            raw_json = response.text
            script_data = json.loads(raw_json)

            # Ensure script_id exists
            if "script_id" not in script_data or not script_data["script_id"]:
                script_data["script_id"] = str(uuid.uuid4())

            script = SitcomScript(**script_data)

            if validate_script_characters(script):
                return script
            else:
                print("Generated script failed character validation.")
                return None

        except Exception as e:
            print(f"Error generating script: {e}")
            return None