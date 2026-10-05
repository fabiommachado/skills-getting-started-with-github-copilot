from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activities_data(monkeypatch):
    data = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", data)
    return data


@pytest.fixture
def client(activities_data):
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_static_index(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client, activities_data):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities_data


def test_signup_adds_student_to_activity(client, activities_data):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Team"
    }
    assert email in activities_data["Basketball Team"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_student(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_remove_participant_removes_student(client, activities_data):
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/Chess%20Club/participants/{email}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from Chess Club"
    }
    assert email not in activities_data["Chess Club"]["participants"]


def test_remove_participant_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/participants/student%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_404_for_unregistered_student(client):
    response = client.delete(
        "/activities/Chess%20Club/participants/student%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }