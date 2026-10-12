import sqlite3
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "gradetracker.db"
)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS instructors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                instructor_id INTEGER NOT NULL,
                FOREIGN KEY (instructor_id)
                    REFERENCES instructors(id)
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id)
                    REFERENCES students(id),
                FOREIGN KEY (course_id)
                    REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                score REAL NOT NULL
                    CHECK (score >= 0 AND score <= 100),
                FOREIGN KEY (student_id, course_id)
                    REFERENCES enrollments(student_id, course_id)
            );
        """)
