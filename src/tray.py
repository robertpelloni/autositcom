import os
import sys
import threading
import subprocess
import pystray
from PIL import Image, ImageDraw

def create_image():
    # Create a simple icon image (a red square with a white "A" for Autositcom)
    width = 64
    height = 64
    color1 = (200, 0, 0)
    color2 = (255, 255, 255)

    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    # Simple placeholder shape if text font isn't available
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=color2
    )
    return image

def on_quit(icon, item):
    icon.stop()
    # Need to properly terminate the underlying servers in a real deployment
    print("Quitting Autositcom tray app...")
    os._exit(0)

def on_open_dashboard(icon, item):
    print("Opening Dashboard...")
    # This spawns the streamlit process if it's not already running,
    # or ideally just opens the browser to the existing localhost port.
    # We'll do a simple subprocess call for demonstration.
    try:
        subprocess.Popen(["streamlit", "run", "src/dashboard.py"])
    except Exception as e:
        print(f"Error opening dashboard: {e}")

def run_tray():
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem('Open Dashboard', on_open_dashboard),
        pystray.MenuItem('Quit Servers', on_quit)
    )
    icon = pystray.Icon("Autositcom", image, "Autositcom Server", menu)
    icon.run()

if __name__ == "__main__":
    run_tray()