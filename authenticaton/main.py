import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ---------- Settings (from the .env file) ----------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_MINUTES = 60

if not DATABASE_URL or not SECRET_KEY:
    raise RuntimeError("Set DATABASE_URL and SECRET_KEY in the .env file")

# Use the installed psycopg2 driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# ---------- Database ----------
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # never store the real password


Base.metadata.create_all(bind=engine)  # creates the table if it doesn't exist


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Request shapes ----------
class RegisterData(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginData(BaseModel):
    email: EmailStr
    password: str


# ---------- Password hashing (Argon2) ----------
hasher = PasswordHasher()

# ---------- App ----------
app = FastAPI(title="JWT Auth")

# Lets the React app (port 5173) call this API (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- JWT helpers ----------
def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),  # "sub" = who the token belongs to
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


bearer = HTTPBearer(auto_error=False)  # reads the "Authorization: Bearer <token>" header


# Dependency: any route that lists this runs it first and gets the logged-in user
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


# ---------- Routes ----------
@app.post("/register", status_code=201)
def register(data: RegisterData, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(name=data.name.strip(), email=email, password_hash=hasher.hash(data.password))
    db.add(user)
    db.commit()
    return {"message": "Registration successful. Please log in."}


@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()

    # Same message for "no such email" and "wrong password" so attackers learn nothing
    bad_login = HTTPException(status_code=401, detail="Incorrect email or password")
    if user is None:
        raise bad_login
    try:
        hasher.verify(user.password_hash, data.password)
    except VerifyMismatchError:
        raise bad_login

    return {"access_token": create_token(user.id), "token_type": "bearer"}


@app.get("/me")
def me(user: User = Depends(get_current_user)):  # protected: needs a valid token
    return {"id": user.id, "name": user.name, "email": user.email}
