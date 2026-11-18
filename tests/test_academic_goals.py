"""Sprint 3 Issue #25: persistent student course goals and validation."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code" / "backend"))
import database
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_goals.db")
    database.initialize_database()
    with database.get_connection() as c:
        c.executemany("INSERT INTO students(id, name) VALUES(?, ?)", [(1, "Alice"), (2, "Bob")])
        c.execute("INSERT INTO instructors(id, name) VALUES(1, 'Smith')")
        c.executemany("INSERT INTO courses(id, name, instructor_id) VALUES(?, ?, 1)", [(1, "CptS 322"), (2, "CptS 360")])
        c.executemany("INSERT INTO enrollments(student_id, course_id) VALUES(?, ?)", [(1, 1), (1, 2), (2, 2)])
        c.execute("INSERT INTO grades(student_id, course_id, score) VALUES (1,1,80)")
        c.execute("INSERT INTO grades(student_id, course_id, score) VALUES (1,1,90)")
        c.commit()


def test_goal_created_updated_and_persists():
    r = client.put('/students/1/courses/1/goal', json={'target_percentage':90})
    assert r.status_code == 200
    assert client.get('/students/1/goals').json()['courses'][0]['target_percentage'] == 90
    assert client.put('/students/1/courses/1/goal', json={'target_percentage':85}).status_code == 200
    assert client.get('/students/1/goals').json()['courses'][0]['status'] == 'met'
    with database.get_connection() as c:
        assert c.execute('SELECT COUNT(*) FROM academic_goals').fetchone()[0] == 1


def test_below_goal_and_no_grades():
    client.put('/students/1/courses/1/goal', json={'target_percentage':90})
    client.put('/students/1/courses/2/goal', json={'target_percentage':92})
    courses = client.get('/students/1/goals').json()['courses']
    assert courses[0]['current_average'] == 85
    assert courses[0]['status'] == 'below_target'
    assert courses[1]['current_average'] is None
    assert courses[1]['status'] == 'no_grades'


@pytest.mark.parametrize('value', [-1, 101, 'NaN', None])
def test_invalid_goal_rejected(value):
    assert client.put('/students/1/courses/1/goal', json={'target_percentage':value}).status_code == 422


def test_unknown_student_and_non_enrollment():
    assert client.get('/students/999/goals').status_code == 404
    assert client.put('/students/999/courses/1/goal', json={'target_percentage':90}).status_code == 404
    assert client.put('/students/2/courses/1/goal', json={'target_percentage':90}).status_code == 403


def test_student_goals_are_separate():
    client.put('/students/1/courses/2/goal', json={'target_percentage':89})
    r = client.get('/students/2/goals')
    assert r.status_code == 200
    assert r.json()['courses'][0]['target_percentage'] is None
