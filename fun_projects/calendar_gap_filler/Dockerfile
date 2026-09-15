# Runtime image for Calendar Gap Filler.
#
# Meant to be run via docker-compose (see docker-compose.yml, Phase 9.3),
# which mounts credentials.json / token.json / .env / profile.json /
# feedback.db from the host — none of that personal data is baked into
# this image (see .dockerignore).
FROM python:3.12-slim

WORKDIR /app

# Copied separately from the rest of the source so this (slow) layer is
# only re-run when requirements.txt actually changes, not on every
# code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the TinyBERT checkpoint into the image at build time (Развилка №3,
# Phase 9) instead of downloading it lazily on first request. This
# container is expected to stop/start often (Mac reboots, docker
# restarts) — without this, every restart would re-download a couple
# hundred MB from Hugging Face and require internet access just to
# answer the first request. The model name is hardcoded here rather than
# imported from config.py so this layer stays cacheable independently of
# the application source copied below; keep it in sync with
# config.TINYBERT_MODEL_NAME if that ever changes.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-TinyBERT-L6-v2')"

COPY . .

EXPOSE 8000

# --host 0.0.0.0 is required here — unlike the local "uvicorn --reload"
# command in README (which defaults to 127.0.0.1, fine for a process
# talking to itself on your own machine), a container only listening on
# 127.0.0.1 is unreachable from outside its own network namespace, so
# Docker's port mapping / docker-compose networking couldn't reach it at
# all. No --reload either — that's a local-dev convenience, not something
# a running deployment needs.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
