FROM python:3.12-slim

WORKDIR /app

COPY notification_dispatcher/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY notification_dispatcher /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Ensure data dir for idempotency sqlite
RUN mkdir -p /app/data

CMD ["python", "src/worker.py"]
