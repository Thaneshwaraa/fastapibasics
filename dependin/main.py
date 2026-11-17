from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from database import get_db, Base, engine

app = FastAPI()


class Car(Base):
    __tablename__ = "dependin_cars"
    id = Column(Integer, primary_key=True)
    brand = Column(String)
    model = Column(String)


# Creates the table in Neon if it doesn't exist yet
Base.metadata.create_all(bind=engine)


@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).all()
    return cars
