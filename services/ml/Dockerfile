FROM python:3.11

WORKDIR /app

# Copy requirements
COPY services/ml/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# Download NLTK data
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader vader_lexicon

# Download spaCy French model
# Copy src
COPY src/ ./src
COPY services/ml/main.py .

# Create data folders
RUN mkdir -p /app/data/raw
RUN mkdir -p /app/data/processed

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

