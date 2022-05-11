import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent))
from src.api import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello CoinTracker!"


def test_data():
    response = client.get("/data")
    assert response.status_code == 200
    # data = response.json()
    # assert data


def test_data_btc():
    response = client.get("/data/BTC")
    assert response.status_code == 200
    # data = response.json()
    # assert data
