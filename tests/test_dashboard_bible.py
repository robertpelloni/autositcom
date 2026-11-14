"""Dashboard Character Bible editor: valid JSON saves, invalid does not.

WHY AppTest: it drives the real Streamlit script (widgets, button, file
write) without a browser. The bible file is backed up and restored.
"""
import json, shutil
from streamlit.testing.v1 import AppTest

BIBLE = "docs/CHARACTER_BIBLE.json"

def test_bible_save_valid_and_invalid(tmp_path):
    backup = tmp_path / "bible_backup.json"
    shutil.copy(BIBLE, backup)
    original = open(BIBLE).read()
    try:
        # Valid: cast is written to disk and success is shown.
        at = AppTest.from_file(str(__import__("pathlib").Path(__file__).parent.parent / "src" / "dashboard.py"), default_timeout=30).run()
        assert not at.exception  # whole page must render (regression: st.info(help=) crashed it mid-page)
        at.text_area(key="bible_edit").set_value(
            json.dumps({"characters": {"BOB": {"description": "x"}, "LUM": {"description": "y"}}}))
        [b for b in at.button if "Save character bible" in b.label][0].click().run()
        assert "Bible saved" in " ".join(s.value for s in at.success)
        assert set(json.load(open(BIBLE))["characters"]) == {"BOB", "LUM"}

        # Invalid: error is shown and the file is untouched.
        before = open(BIBLE).read()
        at.text_area(key="bible_edit").set_value("{not json")
        [b for b in at.button if "Save character bible" in b.label][0].click().run()
        assert "Not saved" in " ".join(e.value for e in at.error)
        assert open(BIBLE).read() == before
    finally:
        open(BIBLE, "w").write(original)

