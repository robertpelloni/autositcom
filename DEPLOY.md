# DEPLOY.md
## Environment Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.
- Python 3.12+ (if running locally without Docker).
- An active `.env` file containing required API keys.

### 1. Configure Environment
Copy `.env.example` to `.env` (create one if it doesn't exist) and populate it:
```ini
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_CLIENT_SECRET=your_youtube_secret
TIKTOK_SESSION_TOKEN=your_tiktok_token
```

### 2. Run with Docker Compose
The easiest and most reliable way to run the entire system is via Docker.
```bash
docker-compose up --build -d
```
This will start the entire pipeline in the background.

### 3. Run Locally (Development)
If you wish to run the orchestrator locally for debugging:
1. Install dependencies: `pip install -r requirements.txt`
2. Ensure system dependencies are installed: `ffmpeg` and `imagemagick`.
3. Fix ImageMagick policy (Linux): Edit `/etc/ImageMagick-6/policy.xml` to allow text rendering if MoviePy text generation fails.
4. Run the orchestrator: `python -m src.main`
5. Run the UI dashboard: `streamlit run src/dashboard.py`