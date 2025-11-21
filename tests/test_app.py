import sys
import pathlib

# Ensure `src` is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test.student@mergington.edu"

    # Ensure participant is not already registered
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    if email in activities[activity]["participants"]:
        # remove if present to ensure clean state
        client.delete(f"/activities/{activity}/participants?email={email}")

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Confirm participant appears in activities
    resp = client.get("/activities")
    activities = resp.json()
    assert email in activities[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Confirm removal
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]
