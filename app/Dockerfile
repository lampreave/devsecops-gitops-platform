# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build
COPY src/ ./src/

FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="demo-service" \
      org.opencontainers.image.description="Hardened reference microservice for DevSecOps and GitOps CI/CD" \
      org.opencontainers.image.source="https://github.com/lampreave/devsecops-gitops-platform" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8080

# Apply OS security patches and create a dedicated non-root user
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid 10001 --shell /usr/sbin/nologin --create-home appuser

WORKDIR /app
COPY --from=builder --chown=10001:10001 /build/src ./src

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"]

ENTRYPOINT ["python3", "-m", "src.server"]
