
from fastapi import FastAPI
from routers.students import router

app = FastAPI()


app.include_router(router, prefix="/students")

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}
