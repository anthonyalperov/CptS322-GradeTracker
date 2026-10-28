
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import get_connection, initialize_database


app = FastAPI(
    title="GradeTracker API",
    description="Backend API for GradeTracker",
    version="0.1.0"
)

initialize_database()


# Locate the frontend folder relative to this file.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# Serve frontend CSS and JavaScript files.
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


@app.get("/dashboard", include_in_schema=False)
def instructor_dashboard():
    """Display the instructor grade management dashboard."""
    return FileResponse(FRONTEND_DIR / "index.html")


class GradeInput(BaseModel):
    instructor_id: int
    student_id: int
    course_id: int
    score: float = Field(ge=0, le=100)


class GradeUpdate(BaseModel):
    instructor_id: int
    score: float = Field(ge=0, le=100)


@app.get("/")
def home():
    return {
        "message": "Welcome to GradeTracker",
        "status": "running"
    }


@app.post("/grades", status_code=201)
def enter_grade(grade: GradeInput):
    with get_connection() as connection:

        # Verify the instructor teaches this course.
        course = connection.execute(
            """
            SELECT id FROM courses
            WHERE id = ? AND instructor_id = ?
            """,
            (grade.course_id, grade.instructor_id)
        ).fetchone()

        if course is None:
            raise HTTPException(
                status_code=403,
                detail="Instructor is not assigned to this course"
            )

        # Verify the student is enrolled.
        enrollment = connection.execute(
            """
            SELECT student_id FROM enrollments
            WHERE student_id = ? AND course_id = ?
            """,
            (grade.student_id, grade.course_id)
        ).fetchone()

        if enrollment is None:
            raise HTTPException(
                status_code=403,
                detail="Student is not enrolled in this course"
            )

        # Save the grade.
        cursor = connection.execute(
            """
            INSERT INTO grades (student_id, course_id, score)
            VALUES (?, ?, ?)
            """,
            (grade.student_id, grade.course_id, grade.score)
        )

        connection.commit()

        return {
            "message": "Grade saved successfully",
            "grade_id": cursor.lastrowid,
            "student_id": grade.student_id,
            "course_id": grade.course_id,
            "score": grade.score
        }


@app.put("/grades/{grade_id}")
def update_grade(grade_id: int, grade: GradeUpdate):
    with get_connection() as connection:

        # Find the existing grade.
        existing_grade = connection.execute(
            """
            SELECT id, student_id, course_id, score
            FROM grades
            WHERE id = ?
            """,
            (grade_id,)
        ).fetchone()

        if existing_grade is None:
            raise HTTPException(
                status_code=404,
                detail="Grade not found"
            )

        # Verify the instructor teaches the grade's course.
        course = connection.execute(
            """
            SELECT id FROM courses
            WHERE id = ? AND instructor_id = ?
            """,
            (existing_grade["course_id"], grade.instructor_id)
        ).fetchone()

        if course is None:
            raise HTTPException(
                status_code=403,
                detail="Instructor is not assigned to this course"
            )

        # Update the existing grade.
        connection.execute(
            """
            UPDATE grades
            SET score = ?
            WHERE id = ?
            """,
            (grade.score, grade_id)
        )

        connection.commit()

        return {
            "message": "Grade updated successfully",
            "grade_id": grade_id,
            "student_id": existing_grade["student_id"],
            "course_id": existing_grade["course_id"],
            "score": grade.score
        }


@app.get("/students/{student_id}/grades")
def view_student_grades(student_id: int):
    with get_connection() as connection:

        # Check whether the student exists.
        student = connection.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        # Retrieve grades with their course names.
        grades = connection.execute(
            """
            SELECT
                grades.course_id,
                courses.name AS course_name,
                grades.score
            FROM grades
            JOIN courses ON grades.course_id = courses.id
            WHERE grades.student_id = ?
            ORDER BY grades.id
            """,
            (student_id,)
        ).fetchall()

        return {
            "student_id": student_id,
            "grades": [
                {
                    "course_id": grade["course_id"],
                    "course_name": grade["course_name"],
                    "score": grade["score"]
                }
                for grade in grades
            ]
        }
