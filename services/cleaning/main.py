from fastapi import FastAPI
from pydantic import BaseModel
from src.run_cleaning import run_cleaning

app = FastAPI()

class CleaningRequest(BaseModel):
    name: str

@app.post("/clean")
def clean(data: CleaningRequest):
    return run_cleaning(data.name)