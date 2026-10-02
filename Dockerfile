# Deno is the JavaScript runtime used by yt-dlp for YouTube extraction.
FROM denoland/deno:bin AS deno

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install the real FFmpeg/ffprobe binaries for merging, MP3 and thumbnails.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=deno /deno /usr/local/bin/deno

COPY requirements.txt ./requirements.txt
RUN python -m venv /opt/venv \
    && python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip check \
    && ffmpeg -version > /dev/null \
    && ffprobe -version > /dev/null \
    && deno --version

# Keep the uploaded Python file unchanged; use a simple name inside Docker.
COPY ["bot-1(1).py", "./bot.py"]

# A writable virtualenv lets the bot's existing yt-dlp updater keep working.
RUN groupadd --gid 1000 bot \
    && useradd --uid 1000 --gid bot --create-home bot \
    && mkdir -p /app/data /app/tmp /app/logs \
    && chown -R bot:bot /app /opt/venv

USER bot
VOLUME ["/app/data", "/app/logs"]
STOPSIGNAL SIGTERM
CMD ["python", "-u", "/app/bot.py"]
