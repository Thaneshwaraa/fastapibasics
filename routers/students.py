from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Student(BaseModel):
    name: str
    age: int

students = []

@router.get("/")
def get_students():
    return students

@router.post("/")
def add_student(student: Student):
    students.append(student)
    return {"message": "student added", "student": student}
