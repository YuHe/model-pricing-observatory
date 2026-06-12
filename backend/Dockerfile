FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc libffi-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 3722

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3722"]
