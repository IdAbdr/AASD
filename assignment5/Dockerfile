# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt     && useradd --create-home --uid 10001 researcher
COPY service ./service
ARG SOURCE_REVISION=local-development
ENV APP_REVISION=${SOURCE_REVISION}
LABEL org.opencontainers.image.title="Skin image research service"       org.opencontainers.image.revision=${SOURCE_REVISION}
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
USER researcher
CMD ["python", "-m", "service.server"]

FROM base AS test
COPY tests ./tests
COPY ci ./ci
CMD ["python", "ci/run_tests.py", "--junit", "/tmp/junit.xml"]

FROM base AS runtime
