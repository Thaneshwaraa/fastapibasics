from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from database import engine, Session, Base

app = FastAPI()


# Database Model
class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    color = Column(String)


Base.metadata.create_all(bind=engine)


# Database Connection
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# CREATE CAR
@app.post("/add-car")
def add_car(
    brand: str,
    model: str,
    year: int,
    color: str,
    db: Session = Depends(get_db)
):
    car = Car(
        brand=brand,
        model=model,
        year=year,
        color=color
    )

    db.add(car)
    db.commit()

    return {"message": "Car added successfully"}


# READ ALL CARS
@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    return db.query(Car).all()


# READ ONE CAR
@app.get("/car/{id}")
def get_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()

    if car:
        return car

    return {"message": "Car not found"}


# UPDATE CAR
@app.put("/update-car/{id}")
def update_car(
    id: int,
    brand: str,
    model: str,
    year: int,
    color: str,
    db: Session = Depends(get_db)
):
    car = db.query(Car).filter(Car.id == id).first()

    if car:
        car.brand = brand
        car.model = model
        car.year = year
        car.color = color

        db.commit()

        return {"message": "Car updated successfully"}

    return {"message": "Car not found"}


# DELETE CAR
@app.delete("/delete-car/{id}")
def delete_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()

    if car:
        db.delete(car)
        db.commit()

        return {"message": "Car deleted successfully"}

    return {"message": "Car not found"}
