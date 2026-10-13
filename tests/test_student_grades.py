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
    test_db = tmp_path / "student_grades_test.db"
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
        connection.execute(
            "INSERT INTO grades (student_id, course_id, score) VALUES (1, 1, 95)"
        )
        connection.commit()


def test_student_can_view_grades():
    response = client.get("/students/1/grades")

    assert response.status_code == 200
    assert response.json() == {
        "student_id": 1,
        "grades": [
            {
                "course_id": 1,
                "course_name": "CptS 322",
                "score": 95
            }
        ]
    }


def test_student_with_no_grades():
    response = client.get("/students/2/grades")

    assert response.status_code == 200
    assert response.json() == {
        "student_id": 2,
        "grades": []
    }


def test_nonexistent_student():
    response = client.get("/students/999/grades")

    assert response.status_code == 404


def test_student_cannot_view_other_students_grades():
    response = client.get("/students/2/grades")

    assert response.status_code == 200
    assert response.json()["grades"] == []