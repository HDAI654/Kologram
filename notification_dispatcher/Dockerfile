FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

COPY notification_dispatcher/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY notification_dispatcher /app

RUN mkdir -p /app/data \
    && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV IDEMPOTENCY_DB_PATH=/app/data/idempotency.sqlite3

USER appuser

CMD ["python", "-m", "src.worker"]
