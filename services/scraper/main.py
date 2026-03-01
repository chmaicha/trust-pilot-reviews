from fastapi import FastAPI
from pydantic import BaseModel
from src.scraper import run_scraper
app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    name: str
    max_reviews: int = 100

@app.post("/scrape")
def scrape(data: ScrapeRequest):
    result = run_scraper(
        url=data.url,
        name=data.name,
        max_reviews=data.max_reviews
    )
    return result

@app.get("/health")
def health():
    return {"status": "scraper running"}

