import json
from unittest.mock import patch, MagicMock
from src.schemas import ExtractedTopic, SitcomScript, ScriptScene
from src.scriptwriter.validator import validate_script_characters
from src.scriptwriter.script_generator import ScriptGenerator

def test_character_validator():
    # Valid Script
    scene1 = ScriptScene(
        scene_number=1,
        setting="Living Room",
        dialogue=[{"JERRY": "Hello"}, {"GEORGE": "Hi"}],
        visual_action_notes="Walks in"
    )
    script_valid = SitcomScript(
        script_id="script_1",
        title="Episode 1",
        theme="Friendship",
        characters=["JERRY", "GEORGE"],
        scenes=[scene1]
    )

    # Invalid Script
    scene2 = ScriptScene(
        scene_number=1,
        setting="Living Room",
        dialogue=[{"BATMAN": "Hello"}],
        visual_action_notes="Walks in"
    )
    script_invalid = SitcomScript(
        script_id="script_2",
        title="Episode 2",
        theme="Friendship",
        characters=["BATMAN"],
        scenes=[scene2]
    )

    # Assuming docs/CHARACTER_BIBLE.json exists and contains JERRY and GEORGE
    assert validate_script_characters(script_valid) == True
    assert validate_script_characters(script_invalid) == False

@patch('src.scriptwriter.script_generator.genai.Client')
def test_script_generation(mock_genai_client):
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "script_id": "test_script",
        "title": "The Test Episode",
        "theme": "Testing",
        "characters": ["JERRY", "ELAINE"],
        "scenes": [
            {
                "scene_number": 1,
                "setting": "Coffee Shop",
                "visual_action_notes": "Drinking coffee",
                "dialogue": [
                    {"JERRY": "Did you run the tests?"},
                    {"ELAINE": "Of course I did."}
                ]
            }
        ]
    })
    mock_client_instance.models.generate_content.return_value = mock_response

    generator = ScriptGenerator()

    topic = ExtractedTopic(
        topic_id="topic_1",
        title="Testing Code",
        summary="They argue about writing tests.",
        key_quotes=["Did you run the tests?"],
        comedy_score=8.5,
        source_chunk_ids=["chunk_1"]
    )

    script = generator.generate_script(topic)

    assert script is not None
    assert script.title == "The Test Episode"
    assert len(script.characters) == 2
    assert "JERRY" in script.characters
    assert script.scenes[0].setting == "Coffee Shop"