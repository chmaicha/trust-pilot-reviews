FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY services/scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

COPY services/scraper/main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]