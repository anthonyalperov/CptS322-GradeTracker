
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
    test_db = tmp_path / "course_grades_test.db"
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
            "INSERT INTO courses VALUES (2, 'CptS 355', 1)"
        )
        connection.execute(
            "INSERT INTO enrollments VALUES (1, 1)"
        )
        connection.execute(
            "INSERT INTO enrollments VALUES (1, 2)"
        )
        connection.execute(
            "INSERT INTO enrollments VALUES (2, 1)"
        )
        connection.execute(
            """
            INSERT INTO grades (student_id, course_id, score)
            VALUES (1, 1, 95)
            """
        )
        connection.execute(
            """
            INSERT INTO grades (student_id, course_id, score)
            VALUES (1, 2, 88)
            """
        )
        connection.commit()


def test_student_can_view_course_grades():
    response = client.get("/students/1/courses/1/grades")

    assert response.status_code == 200

    data = response.json()
    assert data["student_id"] == 1
    assert data["course_id"] == 1
    assert data["course_name"] == "CptS 322"
    assert len(data["grades"]) == 1
    assert data["grades"][0]["score"] == 95


def test_nonexistent_student():
    response = client.get("/students/999/courses/1/grades")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_nonexistent_course():
    response = client.get("/students/1/courses/999/grades")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_student_not_enrolled():
    response = client.get("/students/2/courses/2/grades")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Student is not enrolled in this course"
    )


def test_enrolled_student_with_no_grades():
    response = client.get("/students/2/courses/1/grades")

    assert response.status_code == 200
    assert response.json()["grades"] == []
