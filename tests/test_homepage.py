import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from app import app


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_homepage_best_case(client):
    response = client.get("/")
    assert response.status_code == 200

def test_homepage_average_case(client):
    response = client.get("/?ref=test")
    assert response.status_code == 200


def test_homepage_worst_case(client):
    response = client.post("/")
    assert response.status_code == 405