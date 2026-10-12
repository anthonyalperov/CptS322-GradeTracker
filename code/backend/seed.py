
from database import get_connection, initialize_database


def seed_database():
    initialize_database()

    with get_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO instructors (id, name) VALUES (?, ?)",
            (1, "Professor Smith")
        )

        connection.execute(
            "INSERT OR IGNORE INTO students (id, name) VALUES (?, ?)",
            (1, "Student Alice")
        )

        connection.execute(
            "INSERT OR IGNORE INTO students (id, name) VALUES (?, ?)",
            (2, "Student Bob")
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO courses (id, name, instructor_id)
            VALUES (?, ?, ?)
            """,
            (1, "CptS 322", 1)
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO enrollments (student_id, course_id)
            VALUES (?, ?)
            """,
            (1, 1)
        )

        connection.commit()

    print("Sample GradeTracker data created successfully!")


if __name__ == "__main__":
    seed_database()
