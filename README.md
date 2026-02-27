# 📊 Trust Pilot Reviews – MLOps Microservices Architecture

## 🚀 Overview

This project aims to provide a simple, cost-effective solution for small online stores and startups to analyze customer reviews. The main goal is to extract insights from customer feedback that will help these businesses improve their products and services. By using Python tools and machine learning, this project helps to classify customer sentiment (positive, neutral, negative) and presents these insights in an easy-to-read dashboard using Streamlit.

 **microservices architecture powered by Docker**.

## Problem Statement
Small commerce businesses often lack the resources to conduct in-depth analysis of customer reviews. Understanding customer satisfaction through reviews can be crucial for product and service improvements. This project addresses this need by delivering a solution that is both accessible and scalable, allowing small businesses to efficiently analyze customer sentiment without the need for extensive technical knowledge or expensive tools.

## Technologies
- **Selenium**: Used for scraping customer reviews from online stores.
- **CSV/Google Drive**: Data storage in CSV format, either locally or in Google Drive.
- **pandas**: Used for cleaning and processing the text data.
- **scikit-learn**: Implements a simple machine learning model for sentiment analysis.
- **streamlit**: Displays the results in an accessible and interactive dashboard.

## Project Phases
1. **Data Collection (raw and with Scraping)**: Reviews will be collected from online stores using Python's Scrapy framework and stored in CSV format.
2. **Data Cleaning**: The raw data will be saved in CSV files locally or in Google Drive.
3. **Sentiment Analysis**: The data will be processed using pandas to clean and prepare it for machine learning analysis.  A machine learning model, implemented in scikit-learn, will classify reviews as positive, neutral, or negative.
4. **Data Visualization**: The results of the analysis will be displayed with a streamlit app for easy interpretation and insights.


The pipeline includes:

1. **Scraper Service** – Collects reviews from Google Maps  
2. **Cleaning Service** – Cleans and structures raw data  
3. **ML Sentiment Service** – Performs NLP, embeddings, clustering & topic modeling  
4. **API Service (FastAPI)** – Exposes the pipeline via HTTP  
5. **Streamlit Service** – Provides an interactive dashboard  

This architecture follows modern **MLOps principles**:

- Containerized services  
- Isolated dependencies  
- Reproducible environments  
- Volume-based data exchange  
- Service modularity  
- Ready for orchestration (Docker Compose / Kubernetes)  

---

# 🏗 Architecture Overview

               ┌─────────────────┐
               │   Scraper       │
               │  (Selenium)     │
               └────────┬────────┘
                        │
                        ▼
                data/raw/*.csv
                        │
                        ▼
               ┌─────────────────┐
               │   Cleaning      │
               │  (Pandas)       │
               └────────┬────────┘
                        │
                        ▼
             data/processed/*_reviews.csv
                        │
                        ▼
               ┌─────────────────┐
               │  ML Sentiment   │
               │ (NLP + ML)      │
               └────────┬────────┘
                        │
                        ▼
    *_ml_processed_reviews.csv
    *_sample_selected_reviews.csv
                        │
                        ▼
               ┌─────────────────┐
               │  Streamlit App  │
               └─────────────────┘


All services share a mounted Docker volume:

```bash
-v ${PWD}/data:/app/data

TRUST-PILOT-REVIEWS/
│
├── services/
│   ├── scraper/        # Selenium scraping service
│   ├── cleaning/       # Data preprocessing service
│   ├── ml/             # Sentiment + NLP service
│   ├── api/            # FastAPI service
│   ├── streamlit/      # Dashboard
│   └── docker-compose.yml
│
├── src/                # Core business logic
│
├── data/
│   ├── raw/
│   └── processed/
 
```
Each service has:

Its own Dockerfile

Its own requirements.txt

Isolated dependency scope