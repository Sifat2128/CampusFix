from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CampusFix"


def test_security_headers_present():
    res = client.get("/")
    assert res.status_code == 200
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert res.headers.get("x-frame-options") == "SAMEORIGIN"
    assert res.headers.get("x-xss-protection") == "1; mode=block"
    assert res.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


def test_rate_limiting_protects_login():
    # Attempt rapid repeated logins from same test client
    responses = []
    for _ in range(12):
        r = client.post("/auth/login", json={
            "email": "2203098@student.ruet.ac.bd",
            "password": "wrongpassword",
            "role": "student"
        })
        responses.append(r.status_code)
    
    # After 10 attempts in 60s, rate limiter should return 429
    assert 429 in responses, f"Expected 429 in responses, got {responses}"
