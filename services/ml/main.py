from fastapi import FastAPI
from pydantic import BaseModel
from src.sentiment import run_sentiment

app = FastAPI()

class SentimentRequest(BaseModel):
    name: str
    plot: bool = False

@app.post("/sentiment")
def sentiment(data: SentimentRequest):
    result = run_sentiment(data.name, data.plot)
    return result