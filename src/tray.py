"""Autositcom system tray — status, dashboard, pipeline control, clean quit.

WHY: operator must see health and stop servers without a terminal.
Dashboard opens in the browser (never spawns a duplicate Streamlit);
Quit terminates child processes it started, then exits.
Run: python -m src.tray   (below-normal priority recommended, see scripts/run.ps1)
"""
import os, subprocess, sys, webbrowser
import pystray
from PIL import Image, ImageDraw

_children: list[subprocess.Popen] = []
DASH_URL = "http://localhost:8501"

def create_image(ok=True):
    img = Image.new("RGB", (64, 64), (30, 120, 30) if ok else (180, 30, 30))
    d = ImageDraw.Draw(img); d.rectangle((16, 16, 48, 48), fill=(255, 255, 255)); return img

def _spawn(args):
    flags = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)  # never hang the machine
    p = subprocess.Popen(args, creationflags=flags); _children.append(p); return p

def on_open_dashboard(icon, item): webbrowser.open(DASH_URL)  # just browse; dashboard may already run via Docker/run.ps1
def on_start_dashboard(icon, item): _spawn([sys.executable, "-m", "streamlit", "run", "src/dashboard.py", "--server.port", "8501"])
def on_start_pipeline(icon, item): _spawn([sys.executable, "-m", "src.main"])
def on_stop_servers(icon, item):
    for p in _children:
        try: p.terminate()
        except Exception: pass
    _children.clear(); icon.notify("Autositcom servers stopped", "Autositcom")
def on_quit(icon, item):
    on_stop_servers(icon, item); icon.stop(); os._exit(0)  # _exit needed: pystray loop owns the main thread

def _status(item): return f"Autositcom — {len(_children)} server(s) running"

def run_tray():
    menu = pystray.Menu(
        pystray.MenuItem(_status, None, enabled=False),
        pystray.MenuItem("Open Dashboard (browser)", on_open_dashboard, default=True),
        pystray.MenuItem("Start Dashboard server", on_start_dashboard),
        pystray.MenuItem("Start Pipeline", on_start_pipeline),
        pystray.MenuItem("Stop Servers", on_stop_servers),
        pystray.MenuItem("Quit (stop servers + exit)", on_quit),
    )
    pystray.Icon("Autositcom", create_image(), "Autositcom Server", menu).run()

if __name__ == "__main__": run_tray()
