from src.tray import health_color

def test_color_red_on_any_failure():
    assert health_color({"distiller": "ok", "renderer": "fail"}) == (180, 30, 30)

def test_color_grey_when_never_ran():
    assert health_color({}) == (110, 110, 110)
    assert health_color({"distiller": "unknown"}) == (110, 110, 110)

def test_color_green_when_healthy():
    assert health_color({"distiller": "ok", "publisher": "skip"}) == (30, 120, 30)
