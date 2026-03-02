# 📊 Trust Pilot Reviews – MLOps Microservices Architecture

## 📖 Project Overview

This project aims to provide a simple, cost-effective solution for small online stores and startups to analyze customer reviews. The main goal is to extract insights from customer feedback that will help these businesses improve their products and services. By using Python tools and machine learning, this project helps to classify customer sentiment (positive, neutral, negative) and presents these insights in an easy-to-read dashboard using Streamlit.

## Problem Statement
Small commerce businesses often lack the resources to conduct in-depth analysis of customer reviews. Understanding customer satisfaction through reviews can be crucial for product and service improvements. This project addresses this need by delivering a solution that is both accessible and scalable, allowing small businesses to efficiently analyze customer sentiment without the need for extensive technical knowledge or expensive tools.

## Technologies
- **Selenium**: Used for scraping customer reviews from online stores.
- **CSV/Google Drive**: Data storage in CSV format, either locally or in Google Drive.
- **pandas**: Used for cleaning and processing the text data.
- **scikit-learn**: Implements a simple machine learning model for sentiment analysis.
- **streamlit**: Displays the results in an accessible and interactive dashboard.

![Preview of the dashboard](img/complete_flow.png)

This project is a complete **microservices-based Machine Learning pipeline** designed to help small commerce businesses analyze customer reviews.

It allows businesses to:

- Scrape Google Maps reviews  
- Clean and preprocess textual data  
- Perform Sentiment Analysis  
- Extract Topics (LDA)  
- Track experiments with MLflow  
- Orchestrate the pipeline with Airflow  

The system is fully containerized using Docker and orchestrated with Docker Compose.

---

# 🎯 Problem Statement

Small commerce businesses often lack the resources to perform in-depth customer review analysis.

Understanding customer satisfaction is crucial for improving products and services.  
This project delivers a scalable and accessible solution that allows businesses to analyze customer sentiment without expensive tools or deep technical expertise.

---

# 🧠 Technologies Used

- FastAPI
- Docker
- Docker Compose
- MLflow
- Apache Airflow
- Pytest
- GitHub Actions
- Selenium
- Pandas
- Scikit-learn
- NLTK
- Gensim (LDA)

---

# 🏗️ Global Architecture

## 🔁 Data Pipeline Flow

Scraper → Cleaning → ML (Sentiment + Topics)
↓
MLflow
↓
Airflow


---

## 🧩 Microservices Overview

### 1️⃣ Scraper Service
- Collects Google Maps reviews
- Built with Selenium
- Exposes a FastAPI endpoint

### 2️⃣ Cleaning Service
- Cleans and structures raw data
- Uses Pandas
- Saves processed CSV files

### 3️⃣ ML Service
- Performs:
  - Sentiment Analysis
  - Topic Modeling (LDA)
- Logs experiments into MLflow

### 4️⃣ MLflow
Tracks:
- Accuracy
- Parameters
- Artifacts
- Topics

### 5️⃣ Airflow
Orchestrates:
- run_scraper
- run_cleaning
- run_ml

---

# 📂 Project Structure

trust-pilot-reviews/
│
├── services/
│ ├── scraper/
│ ├── cleaning/
│ └── ml/
│
├── src/
│ ├── scraper.py
│ ├── run_cleaning.py
│ ├── sentiment.py
│
├── airflow/
│ └── dags/pipeline_dag.py
│
├── tests/
│
├── docker-compose.yml
├── README.md
└── .github/workflows/ci.yml


All services:

- Have their own Dockerfile  
- Have isolated dependencies  
- Share data via Docker volumes  

Shared folders:


data/
├── raw/
└── processed/



---

# 🐳 Running the Project

## 🔹 Build and Start All Services

```bash
docker compose up --build
```

🌐 Service Endpoints

| Service  | URL                                            |
| -------- | ---------------------------------------------- |
| Scraper  | [http://localhost:8001](http://localhost:8001) |
| Cleaning | [http://localhost:8002](http://localhost:8002) |
| ML       | [http://localhost:8003](http://localhost:8003) |
| MLflow   | [http://localhost:5000](http://localhost:5000) |
| Airflow  | [http://localhost:8080](http://localhost:8080) |


🧹 Scraper Service
Endpoint :POST /scrape

Request Body

{
  "url": "https://www.google.com/maps/place/Caf%C3%A9+de+Flore/@48.8541623,2.3300297,16z/data=!4m8!3m7!1s0x47e671d781fb9dab:0x18bba6dd45e173ff!8m2!3d48.8541588!4d2.3326046!9m1!1b1!16zL20vMDhkeXY4?entry=ttu&g_ep=EgoyMDI2MDIyMy4wIKXMDSoASAFQAw%3D%3D",
  "name": "cafe_de_flore",
  "max_reviews": 100
}


🧼 Cleaning Service
Endpoint : POST /clean

Request Body

{
  "name": "cafe_de_flore",
  "plot": false
}

This performs:

- Sentiment Analysis

- Topic Modeling (LDA)

- Logs metrics into MLflow

📊 MLflow

http://localhost:5000

You can monitor:

- Experiments

- Runs

- Metrics

- Parameters

- Artifacts

🔄 Airflow Orchestration

Access:

http://localhost:8080

Default credentials:

Username: admin

Password: admin

DAG Name:

microservices_pipeline

Execution Flow:

run_scraper → run_cleaning → run_ml

Manual trigger:

Open Airflow UI

Activate DAG

Click "Trigger DAG"

Airflow automatically calls each FastAPI microservice.

🧪 Running Tests

Install dev dependencies:

pip install -r requirements-dev.txt

Run tests:

pytest

Tests include:

Input validation

Endpoint status checks

Basic API behavior


⚙️ CI – GitHub Actions

On every push to main:

Python environment is created

Dependencies are installed

Tests are executed automatically

Workflow file:

.github/workflows/ci.yml

If tests fail → Build fails
If tests pass → Build succeeds

🗂️ Data Flow
Google Maps Reviews
        ↓
Raw JSON (data/raw/)
        ↓
Cleaned CSV (data/processed/)
        ↓
Sentiment + Topics
        ↓
MLflow Tracking
🏆 Project Highlights

Microservices architecture

End-to-end ML pipeline

Experiment tracking with MLflow

Workflow orchestration with Airflow

Fully containerized system

CI with automated tests

📌 Future Improvements

Add Streamlit dashboard

Cloud deployment (AWS / Azure)

Docker image push in CI

Coverage report

Monitoring (Prometheus)