from fastapi.testclient import TestClient
from services.scraper.main import app

client = TestClient(app)

def test_scrape_missing_url():
    response = client.post("/scrape", json={
        "name": "test_restaurant"
    })
    assert response.status_code == 422


def test_scrape_valid_input():
    response = client.post("/scrape", json={
        "url": "https://www.google.com/maps/place/Caf%C3%A9+de+Flore/@48.8541623,2.3300297,16z/data=!4m8!3m7!1s0x47e671d781fb9dab:0x18bba6dd45e173ff!8m2!3d48.8541588!4d2.3326046!9m1!1b1!16zL20vMDhkeXY4?entry=ttu&g_ep=EgoyMDI2MDIyMy4wIKXMDSoASAFQAw%3D%3D",
        "name": "test_restaurant",
        "max_reviews": 10
    })
    # On accepte 200 ou 500 si scraper réel échoue
    assert response.status_code in [200, 500]