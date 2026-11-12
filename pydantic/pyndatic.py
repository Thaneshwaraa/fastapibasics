from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    name: str
    age: int
    department: str

students = []         

#home
@app.get("/")
def home():
    return {
        "message": "welcome to student API"
    }

@app.post("/students")
def create_student(student: Student):
    students.append(student)
    return {
        "message": "student added successfully",
        "student": student
    }

@app.get("/students")
def get_students():
    return students

#frontend page
@app.get("/ui")
def frontend():
    return FileResponse(Path(__file__).parent / "pydantic_ui.html")

#/doc (typo) -> /docs
@app.get("/doc", include_in_schema=False)
def doc_redirect():
    return RedirectResponse("/docs")
