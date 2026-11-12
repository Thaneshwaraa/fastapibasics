from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
app = FastAPI()

students =[]

#post
@app.post("/add")
def add_student(name: str , age: int):
    student ={"name": name, "age":age}
    students.append(student)
    return student

#get
@app.get("/students")
def get_students():
    return students

#Tocheck
@app.get("/")
def home():
    return {"message": "FastAPI is working!"}

#put
@app.put("/update/{id}")
def update_student(id:int,name:str,age:int):
    students[id] ={"name":name, "age":age}
    return students[id]

#delete
@app.delete("/delete/{id}")
def delete_student(id: int):
    students.pop(id)
    return {"message":"student deleted"}

#frontend
@app.get("/ui")
def frontend():
    return FileResponse(Path(__file__).parent / "index.html")
