"""Data models used to validate API input and output."""

from pydantic import BaseModel, Field


class StudentInput(BaseModel):
    """Fields students can send when creating or updating a record."""

    name: str = Field(min_length=1)
    age: int = Field(ge=0)

    @staticmethod
    def list_students(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                """SELECT 
                s.id, 
                s.name, 
                s.age, 
                si.student_info_id, 
                si.grade 
            FROM students s
            LEFT JOIN student_infos si ON s.id = si.student_id
            ORDER BY s.id"""
            ).fetchall()
        return [rows]

    @staticmethod
    def create_student(student_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO students (name, age) VALUES (?, ?)",
                (student_input.name, student_input.age),
            )
            row = connection.execute(
                "SELECT id, name, age FROM students WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return row

    @staticmethod
    def get_student(student_id, database_connection):
        with database_connection() as connection:
            row = connection.execute(
                "SELECT id, name, age FROM students WHERE id = ?", (student_id,)
            ).fetchone()
        return row

    @staticmethod
    def update_student(student_id, student_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "UPDATE students SET name = ?, age = ? WHERE id = ?",
                (student_input.name, student_input.age, student_id),
            )
            row = connection.execute(
                "SELECT id, name, age FROM students WHERE id = ?", (student_id,)
            ).fetchone()
        return row

    @staticmethod
    def delete_student(student_id, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM students WHERE id = ?", (student_id,)
            )


class Student(StudentInput):
    """A student record returned by the API."""

    id: int

from pydantic import BaseModel, Field

# 1. Keep your existing Student model
class StudentInput(BaseModel):
    """Fields students can send when creating or updating a record."""
    name: str = Field(min_length=1)
    age: int = Field(ge=0)

    @staticmethod
    def list_students(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, age FROM students ORDER BY id"
            ).fetchall()
        return rows


# 2. Add a new input model for the student info fields
class StudentInfoInput(BaseModel):
    """Fields required to create a student info record."""
    grade: str = Field(min_length=1)
    student_id: int = Field(ge=1)  # ID must be a positive integer

    @staticmethod
    def create_student_info(student_info_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO student_infos (grade, student_id) VALUES (?, ?)",
                (student_info_input.grade, student_info_input.student_id),
            )
            row = connection.execute(
                "SELECT student_info_id, grade, student_id FROM student_infos WHERE student_info_id = ?", 
                (cursor.lastrowid,)
            ).fetchone()
        return row
