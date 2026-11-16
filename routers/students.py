
from fastapi import APIRouter

router = APIRouter()

# GET - View students
@router.get("/")
def get_students():
    return {"message": "All students"}

# POST - Add student
@router.post("/")
def add_student():
    return {"message": "Student added"}
