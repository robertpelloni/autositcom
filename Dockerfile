FROM python:3.12-slim

# Install system dependencies required for audio/video processing
RUN apt-get update && \
    apt-get install -y ffmpeg imagemagick libmagickwand-dev && \
    rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow text rendering for moviepy
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<!-- <policy domain="path" rights="none" pattern="@\*" -->/' /etc/ImageMagick-6/policy.xml || true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.main"]