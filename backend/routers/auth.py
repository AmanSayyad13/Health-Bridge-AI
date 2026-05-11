from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from database import get_connection

router = APIRouter()
security = HTTPBearer()

# ─── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "healthbridge-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int = 25

class LoginRequest(BaseModel):
    email: str
    password: str

# ─── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ─── Routes ────────────────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(req: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if email exists
    existing = cursor.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    password_hash = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, age) VALUES (?, ?, ?, ?)",
        (req.name, req.email, password_hash, req.age)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {"id": user_id, "name": req.name, "email": req.email, "message": "Registration successful"}

@router.post("/login")
def login(req: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT id, name, email, password_hash FROM users WHERE email = ?", (req.email,)
    ).fetchone()
    conn.close()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"user_id": user["id"], "email": user["email"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "name": user["name"],
        "email": user["email"]
    }

@router.get("/me")
def get_me(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, name, email, age, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)
