
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "code" / "backend")
)

import database

# Import the app after database setup.
from main import app


@pytest.fixture(autouse=True)
def setup_database(tmp_path, monkeypatch):
    # Each test gets a separate temporary database.
    test_db = tmp_path / "gradetracker_test.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.initialize_database()

    with database.get_connection() as connection:
        connection.execute(
            "INSERT INTO instructors VALUES (1, 'Professor Smith')"
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
        connection.commit()

    yield


client = TestClient(app)


def test_valid_grade_entry():
    response = client.post("/grades", json={
        "instructor_id": 1,
        "student_id": 1,
        "course_id": 1,
        "score": 95
    })

    assert response.status_code == 201
    assert response.json()["score"] == 95


def test_student_not_enrolled():
    response = client.post("/grades", json={
        "instructor_id": 1,
        "student_id": 2,
        "course_id": 1,
        "score": 85
    })

    assert response.status_code == 403


def test_invalid_grade():
    response = client.post("/grades", json={
        "instructor_id": 1,
        "student_id": 1,
        "course_id": 1,
        "score": 150
    })

    assert response.status_code == 422


def test_instructor_not_assigned():
    response = client.post("/grades", json={
        "instructor_id": 2,
        "student_id": 1,
        "course_id": 1,
        "score": 90
    })

    assert response.status_code == 403



def test_grade_saved_to_database():
    # Submit a grade through the API
    response = client.post("/grades", json={
        "instructor_id": 1,
        "student_id": 1,
        "course_id": 1,
        "score": 95
    })

    assert response.status_code == 201

    # Check that the grade was actually saved
    with database.get_connection() as connection:
        saved_grade = connection.execute(
            """
            SELECT student_id, course_id, score
            FROM grades
            WHERE student_id = ? AND course_id = ?
            """,
            (1, 1)
        ).fetchone()

    assert saved_grade is not None
    assert saved_grade["student_id"] == 1
    assert saved_grade["course_id"] == 1
    assert saved_grade["score"] == 95
