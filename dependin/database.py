import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Reads DATABASE_URL (your Neon connection string) from the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Use the installed psycopg2 driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# Dependency function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
