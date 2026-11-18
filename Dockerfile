# syntax=docker/dockerfile:1
#
# Runs the AnkiNote web app (`ankinote-web`). The image installs a published
# release straight from PyPI, so its contents match
# `pip install 'ankinote-ai==<version>'` exactly. The `anki` library comes with
# it, so the in-process collection backend works out of the box; the setup
# wizard (or ANKI_BACKEND) picks it or AnkiConnect.
#
#   docker build --build-arg ANKINOTE_VERSION=1.1.0 -t ankinote .
FROM python:3.14-slim

ARG ANKINOTE_VERSION
RUN test -n "$ANKINOTE_VERSION" || (echo "ANKINOTE_VERSION build-arg is required" && exit 1)

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    XDG_CONFIG_HOME=/config \
    ANKI_CONNECT_URL=http://host.docker.internal:8765

# Retry: right after a release, a CDN node can still serve an index without the
# new version even after the workflow's PyPI wait step has seen it.
RUN for i in 1 2 3 4 5 6; do \
        pip install --no-cache-dir "ankinote-ai==${ANKINOTE_VERSION}" && exit 0; \
        echo "pip install attempt $i failed, retrying in 20s"; sleep 20; \
    done; exit 1

RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /config/ankinote /data \
    && chown -R appuser:appuser /config /data
USER appuser
WORKDIR /home/appuser

EXPOSE 8080
VOLUME ["/config"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/').status == 200 else 1)"]

CMD ["ankinote-web", "--host", "0.0.0.0", "--port", "8080"]
