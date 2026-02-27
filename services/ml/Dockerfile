FROM python:3.11

WORKDIR /app

# Copy requirements
COPY services/ml/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy src
COPY src/ ./src

# Create data folders
RUN mkdir -p /app/data/raw
RUN mkdir -p /app/data/processed

ENTRYPOINT ["python", "src/sentiment.py"]