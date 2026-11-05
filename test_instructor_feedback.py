
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "code" / "backend")
)

import database
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database(tmp_path, monkeypatch):
    test_db = tmp_path / "instructor_feedback_test.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.initialize_database()

    with database.get_connection() as connection:
        connection.execute(
            "INSERT INTO instructors VALUES (1, 'Professor Smith')"
        )
        connection.execute(
            "INSERT INTO instructors VALUES (2, 'Professor Jones')"
        )
        connection.execute(
            "INSERT INTO students VALUES (1, 'Alice')"
        )
        connection.execute(
            "INSERT INTO students VALUES (2, 'Bob')"
        )
        connection.execute(
            "INSERT INTO courses VALUES (1, 'CptS 322', 1)"
        )
        connection.execute(
            "INSERT INTO enrollments VALUES (1, 1)"
        )
        connection.execute(
            "INSERT INTO grades (id, student_id, course_id, score) "
            "VALUES (1, 1, 1, 95)"
        )
        connection.commit()


def test_instructor_can_submit_feedback():
    response = client.post(
        "/grades/1/feedback",
        json={
            "instructor_id": 1,
            "comment": "Great work!"
        }
    )

    assert response.status_code == 201
    assert response.json()["comment"] == "Great work!"
    assert response.json()["grade_id"] == 1


def test_unauthorized_instructor():
    response = client.post(
        "/grades/1/feedback",
        json={
            "instructor_id": 2,
            "comment": "Needs improvement"
        }
    )

    assert response.status_code == 403


def test_nonexistent_grade():
    response = client.post(
        "/grades/999/feedback",
        json={
            "instructor_id": 1,
            "comment": "Good job"
        }
    )

    assert response.status_code == 404


def test_empty_feedback():
    response = client.post(
        "/grades/1/feedback",
        json={
            "instructor_id": 1,
            "comment": "   "
        }
    )

    assert response.status_code == 422


def test_student_can_view_feedback():
    client.post(
        "/grades/1/feedback",
        json={
            "instructor_id": 1,
            "comment": "Excellent progress"
        }
    )

    response = client.get("/students/1/feedback")

    assert response.status_code == 200
    assert len(response.json()["feedback"]) == 1
    assert response.json()["feedback"][0]["comment"] == (
        "Excellent progress"
    )


def test_student_with_no_feedback():
    response = client.get("/students/2/feedback")

    assert response.status_code == 200
    assert response.json()["feedback"] == []
