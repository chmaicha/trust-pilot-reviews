from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

SCRAPER_URL = "http://scraper:8000"
CLEANING_URL = "http://cleaning:8000"
ML_URL = "http://ml:8000"

class PipelineRequest(BaseModel):
    url: str
    name: str

@app.post("/run-full-pipeline")
def run_pipeline(data: PipelineRequest):

    # 1️⃣ Scraper
    requests.post(
        f"{SCRAPER_URL}/scrape",
        json={"url": data.url, "name": data.name}
    )

    # 2️⃣ Cleaning
    requests.post(
        f"{CLEANING_URL}/clean",
        json={"name": data.name}
    )

    # 3️⃣ ML
    requests.post(
        f"{ML_URL}/sentiment",
        json={"name": data.name, "plot": False}
    )

    return {"status": "Pipeline executed successfully"}

@app.get("/health")
def health():
    return {"status": "API running"}