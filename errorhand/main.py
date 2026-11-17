
from fastapi import FastAPI, HTTPException

app = FastAPI()

cars = [
    {"id": 1, "brand": "Toyota", "model": "Fortuner"},
    {"id": 2, "brand": "BMW", "model": "M4"}
]


# 200 - Successful
@app.get("/cars")
def get_cars():
    return cars


# 201 - Created
@app.post("/cars")
def add_car(brand: str, model: str):

    car = {
        "id": len(cars) + 1,
        "brand": brand,
        "model": model
    }

    cars.append(car)

    return car


# 400 - Bad Request
@app.get("/check-age/{age}")
def check_age(age: int):

    if age < 18:
        raise HTTPException(
            status_code=400,
            detail="Age must be 18 or above"
        )

    return {"message": "Valid age"}


# 401 - Unauthorized
@app.get("/login")
def login():

    is_logged_in = False

    if not is_logged_in:
        raise HTTPException(
            status_code=401,
            detail="Please login first"
        )

    return {"message": "Login successful"}


# 403 - Forbidden
@app.get("/admin")
def admin():

    is_admin = False

    if not is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return {"message": "Welcome Admin"}


# 404 - Not Found
@app.get("/cars/{car_id}")
def get_car(car_id: int):

    for car in cars:
        if car["id"] == car_id:
            return car

    raise HTTPException(
        status_code=404,
        detail="Car not found"
    )


# 409 - Conflict
@app.post("/register")
def register(brand: str):

    for car in cars:
        if car["brand"] == brand:
            raise HTTPException(
                status_code=409,
                detail="Car already exists"
            )

    return {"message": "Car registered"}


# 500 - Internal Server Error
@app.get("/server-error")
def server_error():

    raise HTTPException(
        status_code=500,
        detail="Something went wrong on the server"
    )
