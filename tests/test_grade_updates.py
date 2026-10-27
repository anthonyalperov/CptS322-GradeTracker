
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
    # Give each test its own temporary database.
    test_db = tmp_path / "grade_updates_test.db"
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
            "INSERT INTO courses VALUES (1, 'CptS 322', 1)"
        )
        connection.execute(
            "INSERT INTO enrollments VALUES (1, 1)"
        )
        connection.execute(
            """
            INSERT INTO grades (id, student_id, course_id, score)
            VALUES (1, 1, 1, 80)
            """
        )
        connection.commit()


def test_instructor_can_update_grade():
    response = client.put("/grades/1", json={
        "instructor_id": 1,
        "score": 95
    })

    assert response.status_code == 200
    assert response.json()["score"] == 95

    # Verify the change was saved to SQLite.
    with database.get_connection() as connection:
        saved_grade = connection.execute(
            "SELECT score FROM grades WHERE id = 1"
        ).fetchone()

    assert saved_grade["score"] == 95


def test_nonexistent_grade():
    response = client.put("/grades/999", json={
        "instructor_id": 1,
        "score": 95
    })

    assert response.status_code == 404


def test_unauthorized_instructor():
    response = client.put("/grades/1", json={
        "instructor_id": 2,
        "score": 95
    })

    assert response.status_code == 403

    # Verify the unauthorized request did not change the grade.
    with database.get_connection() as connection:
        saved_grade = connection.execute(
            "SELECT score FROM grades WHERE id = 1"
        ).fetchone()

    assert saved_grade["score"] == 80


@pytest.mark.parametrize("invalid_score", [-10, 150])
def test_invalid_grade_update(invalid_score):
    response = client.put("/grades/1", json={
        "instructor_id": 1,
        "score": invalid_score
    })

    assert response.status_code == 422
