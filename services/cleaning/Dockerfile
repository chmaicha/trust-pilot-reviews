FROM python:3.11-slim

WORKDIR /app

# Install requirements
COPY services/cleaning/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full src (business logic)
COPY src/ ./src

# Copy API wrapper
COPY services/cleaning/main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]