from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback

from scraper import run_scraper
from run_cleaning import run_cleaning
from sentiment import run_sentiment


app = FastAPI(
    title="Trust Synthèse API",
    description="API to trigger scraping, cleaning and sentiment analysis pipeline",
    version="1.0.0"
)


# ==========================================================
# 📦 Request Models
# ==========================================================

class ScrapeRequest(BaseModel):
    url: str
    name: str
    max_reviews: int = 100


class NameRequest(BaseModel):
    name: str
    plot: bool = False


# ==========================================================
# 🔍 Health Check
# ==========================================================

@app.get("/health")
def health_check():
    return {"status": "API is running"}


# ==========================================================
# 🕷 SCRAPE
# ==========================================================

@app.post("/scrape")
def scrape(data: ScrapeRequest):
    try:
        result = run_scraper(
            url=data.url,
            name=data.name,
            max_reviews=data.max_reviews
        )
        return {
            "message": "Scraping completed",
            "details": result
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 🧹 CLEAN
# ==========================================================

@app.post("/clean")
def clean(data: NameRequest):
    try:
        result = run_cleaning(data.name)
        return {
            "message": "Cleaning completed",
            "details": result
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 🤖 SENTIMENT
# ==========================================================

@app.post("/sentiment")
def sentiment(data: NameRequest):
    try:
        result = run_sentiment(
            name=data.name,
            plot=data.plot
        )
        return {
            "message": "Sentiment pipeline completed",
            "details": result
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 🚀 FULL PIPELINE
# ==========================================================

@app.post("/run-full-pipeline")
def full_pipeline(data: ScrapeRequest):
    try:
        scrape_result = run_scraper(
            url=data.url,
            name=data.name,
            max_reviews=data.max_reviews
        )

        clean_result = run_cleaning(data.name)

        sentiment_result = run_sentiment(
            name=data.name,
            plot=False
        )

        return {
            "message": "Full pipeline executed successfully",
            "scrape": scrape_result,
            "clean": clean_result,
            "sentiment": sentiment_result
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))