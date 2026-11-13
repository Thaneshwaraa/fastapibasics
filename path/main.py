from fastapi import FastAPI, HTTPException

app = FastAPI(title="Student Management System")

students = {
    101: {"name": "Arun", "department": "Information Technology"},
    102: {"name": "Priya", "department": "Computer Science"},
    103: {"name": "Karthik", "department": "Electronics"},
}


@app.get("/students/{student_id}")
def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    student = students[student_id]

    return {
        "student_id": student_id,
        "name": student["name"],
        "department": student["department"],
    }
