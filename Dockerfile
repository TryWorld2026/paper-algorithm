FROM node:22-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages edge-tts mutagen

WORKDIR /app

COPY skills/ /app/skills/
COPY scripts/ /app/scripts/
COPY examples/ /app/examples/

RUN chmod +x /app/scripts/*.py

CMD ["python3", "-X", "utf8", "scripts/check_skills.py"]
