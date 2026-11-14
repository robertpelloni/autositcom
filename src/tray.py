"""Autositcom system tray — status, dashboard, pipeline control, clean quit.

WHY: operator must see health and stop servers without a terminal.
Dashboard opens in the browser (never spawns a duplicate Streamlit);
Quit terminates child processes it started, then exits.
Run: python -m src.tray   (below-normal priority recommended, see scripts/run.ps1)
"""
import os, subprocess, sys, threading, webbrowser
# NOTE: pystray imported lazily in run_tray() — WHY: on headless Linux it opens
# an X display at import time, which crashed CI collection of the tray tests.
from PIL import Image, ImageDraw

_children: list[subprocess.Popen] = []
DASH_URL = "http://localhost:8501"

def tray_health() -> dict:
    """Stage health from data/pipeline.log (same parser as the dashboard, so
    tray and UI can never disagree about pipeline state)."""
    try:
        from src.main import parse_stage_health
        return parse_stage_health(open("data/pipeline.log", errors="ignore").read())
    except Exception: return {}

def health_color(health: dict):
    # Red = any stage failed, grey = never ran, green = last cycle healthy.
    if any(v == "fail" for v in health.values()): return (180, 30, 30)
    if not health or all(v == "unknown" for v in health.values()): return (110, 110, 110)
    return (30, 120, 30)

def create_image(ok=True):
    img = Image.new("RGB", (64, 64), health_color(tray_health()) if ok else (180, 30, 30))
    d = ImageDraw.Draw(img); d.rectangle((16, 16, 48, 48), fill=(255, 255, 255)); return img

def _spawn(args):
    flags = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)  # never hang the machine
    p = subprocess.Popen(args, creationflags=flags); _children.append(p); return p

def on_open_dashboard(icon, item): webbrowser.open(DASH_URL)  # just browse; dashboard may already run via Docker/run.ps1
def on_start_dashboard(icon, item): _spawn([sys.executable, "-m", "streamlit", "run", "src/dashboard.py", "--server.port", "8501"])
def on_start_pipeline(icon, item): _spawn([sys.executable, "-m", "src.main"])
def cycle_command(): return [sys.executable, "-m", "src.main", "--once"]
def on_run_cycle(icon, item):
    """Run one pipeline cycle from the tray; notify when it finishes and
    loudly when any stage failed (health re-read from pipeline.log)."""
    def work():
        os.makedirs("data", exist_ok=True)
        with open("data/pipeline.log", "a") as f:
            f.write("\n--- tray: run cycle ---\n"); f.flush()
            p = _spawn(cycle_command()); p.wait()
        h = tray_health()
        bad = [s for s, v in h.items() if v == "fail"]
        icon.notify(f"FAILED: {', '.join(bad)} — see dashboard logs" if bad else "Cycle finished", "Autositcom")
        try: icon.icon = create_image()
        except Exception: pass
    threading.Thread(target=work, daemon=True).start()
    icon.notify("Pipeline cycle started", "Autositcom")
def on_stop_servers(icon, item):
    for p in _children:
        try: p.terminate()
        except Exception: pass
    _children.clear(); icon.notify("Autositcom servers stopped", "Autositcom")
def on_quit(icon, item):
    on_stop_servers(icon, item); icon.stop(); os._exit(0)  # _exit needed: pystray loop owns the main thread

def _status(item):
    h = tray_health()
    stages = ", ".join(f"{k}:{v}" for k, v in h.items()) or "no cycles yet"
    return f"Autositcom — {len(_children)} server(s) | {stages}"

def run_tray():
    import pystray
    menu = pystray.Menu(
        pystray.MenuItem(_status, None, enabled=False),
        pystray.MenuItem("Open Dashboard (browser)", on_open_dashboard, default=True),
        pystray.MenuItem("Start Dashboard server", on_start_dashboard),
        pystray.MenuItem("Start Pipeline", on_start_pipeline),
        pystray.MenuItem("Run Cycle Now", on_run_cycle),
        pystray.MenuItem("Stop Servers", on_stop_servers),
        pystray.MenuItem("Quit (stop servers + exit)", on_quit),
    )
    pystray.Icon("Autositcom", create_image(), "Autositcom Server", menu).run()

if __name__ == "__main__": run_tray()
