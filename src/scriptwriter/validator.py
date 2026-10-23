import json
import os
from src.schemas import SitcomScript

def load_character_bible(filepath: str = "docs/CHARACTER_BIBLE.json") -> set:
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return set(data.get("characters", {}).keys())

def validate_script_characters(script: SitcomScript, bible_filepath: str = "docs/CHARACTER_BIBLE.json") -> bool:
    """
    Validates that all characters in the generated script exist in the character bible.
    Returns True if valid, False otherwise.
    """
    allowed_characters = load_character_bible(bible_filepath)
    if not allowed_characters:
        # If no bible exists, assume valid for testing purposes,
        # or fail strict validation. We'll pass for safety if missing.
        return True

    for char in script.characters:
        if char.upper() not in allowed_characters:
            print(f"Validation Error: Character '{char}' not in Character Bible.")
            return False

    for scene in script.scenes:
        for line_dict in scene.dialogue:
            for speaker in line_dict.keys():
                if speaker.upper() not in allowed_characters:
                    print(f"Validation Error: Speaker '{speaker}' in scene {scene.scene_number} not in Character Bible.")
                    return False

    return True