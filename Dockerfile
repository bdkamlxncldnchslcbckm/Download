# Keep this Dockerfile, requirements.txt, and the original Python file together.
# Build: docker build -t kd-bot .
# Generate keys once: docker run --rm kd-bot --keygen
# Set the printed SESSION_KEY and PROVISION_PRIVATE_KEY exports on your host.
# Keep those same keys for every restart and restore.
# Run:
# docker run -d --name kd-bot --restart unless-stopped \
#   -e SESSION_KEY -e PROVISION_PRIVATE_KEY \
#   -v kd-bot-data:/data kd-bot
# Run only one container per database volume.

FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    KD_DB=/data/kd.sqlite3 \
    KD_BACKUP_DIR=/data/kd-backups \
    TZ=Asia/Kolkata

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 kdbot \
    && useradd --uid 10001 --gid kdbot --create-home kdbot \
    && mkdir -p /data/kd-backups \
    && chown -R kdbot:kdbot /data \
    && chmod 700 /data /data/kd-backups

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt \
    && python -m pip check

COPY ["ʙᴏᴛ_𝟸_hardcoded.py", "/app/main.py"]

USER kdbot
VOLUME ["/data"]
STOPSIGNAL SIGTERM
ENTRYPOINT ["python", "/app/main.py"]
