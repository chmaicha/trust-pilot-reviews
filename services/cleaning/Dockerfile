FROM python:3.11-slim

WORKDIR /app

COPY services/cleaning/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader stopwords

COPY src/ ./src

RUN mkdir -p /app/data/raw
RUN mkdir -p /app/data/processed

ENTRYPOINT ["python", "src/run_cleaning.py"]