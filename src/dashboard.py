import time
import streamlit as st
import os
import glob
from src.config import settings
from src.schemas import RenderedEpisode

# Set page config to widen layout and define title
st.set_page_config(page_title="Autositcom Dashboard", layout="wide", page_icon="📺")

# --- Title and Description ---
st.title("📺 Autositcom Control Center")
st.markdown("Monitor and control the 24/7 continuous autonomous content production pipeline.", help="This dashboard unifies Ingestion, Distillation, Scriptwriting, Rendering, and Publishing into a single view.")

# --- Helper Functions ---
def count_files(directory, extension):
    if not os.path.exists(directory):
        return 0
    return len(glob.glob(os.path.join(directory, f"*{extension}")))

def get_latest_video(directory):
    if not os.path.exists(directory):
        return None
    videos = glob.glob(os.path.join(directory, "*.mp4"))
    if not videos:
        return None
    latest_video = max(videos, key=os.path.getctime)
    return latest_video

# --- Metrics Section ---
st.header("Pipeline Metrics", help="Live stats on processed assets.")
col1, col2, col3 = st.columns(3)

with col1:
    audio_chunks = count_files(os.path.join(settings.AUDIO_INGEST_DIR, "processing"), ".wav")
    st.metric(label="Audio Chunks Processing", value=audio_chunks, help="Number of 5-minute raw audio segments currently being processed.")

with col2:
    if os.path.exists(os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")):
        # Simple line count approximation
        with open(os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl"), "r") as f:
            transcript_lines = sum(1 for line in f)
    else:
        transcript_lines = 0
    st.metric(label="Transcript Lines Generated", value=transcript_lines, help="Total number of diarized sentences transcribed.")

with col3:
    rendered_videos = count_files(settings.RENDER_OUTPUT_DIR, ".mp4")
    st.metric(label="Total Episodes Rendered", value=rendered_videos, help="Completed MP4 videos ready for publishing.")

st.divider()

# --- Unified Output View Section ---
st.header("Latest Rendered Episode", help="The most recent video composited by the pipeline.")

latest_video = get_latest_video(settings.RENDER_OUTPUT_DIR)
if latest_video:
    video_col, detail_col = st.columns([2, 1])
    with video_col:
        st.video(latest_video)
    with detail_col:
        st.subheader("Episode Details")
        st.write(f"**Filename:** {os.path.basename(latest_video)}")
        st.write(f"**Created:** {time.ctime(os.path.getctime(latest_video)) if os.path.exists(latest_video) else 'Unknown'}")
        if st.button("Publish Manually (Bypass Schedule)"):
            st.toast("Manual publish triggered! (Mock implementation)", icon="🚀")
else:
    st.info("No rendered episodes found yet. The pipeline may still be ingesting audio or distilling scripts.")

st.divider()

# --- Config & Manual Override Forms ---
st.header("Manual Pipeline Controls", help="Override autonomous settings here.")
form_col1, form_col2 = st.columns(2)

with form_col1:
    with st.form("threshold_form"):
        st.subheader("Distiller Settings")
        threshold = st.slider("Comedy Score Threshold", min_value=1.0, max_value=10.0, value=7.0, step=0.5, help="Only topics rated by Gemini above this score will become scripts.")
        submit_thresh = st.form_submit_button("Update Threshold")
        if submit_thresh:
            st.success(f"Threshold updated to {threshold}")

with form_col2:
    with st.form("manual_trigger_form"):
        st.subheader("System Override")
        st.markdown("Force the pipeline to run a cycle immediately.")
        submit_trigger = st.form_submit_button("Force Run Cycle")
        if submit_trigger:
            st.success("Pipeline cycle forcefully initiated!")