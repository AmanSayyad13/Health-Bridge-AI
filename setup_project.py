import os, sys

print("🏥 HealthBridge AI — Project Setup")
print("=" * 40)

files = {}

files[".env"] = """GEMINI_API_KEY=paste_your_key_here
SECRET_KEY=healthbridge-super-secret-key-2024
"""

files["backend/__init__.py"] = ""
files["backend/routers/__init__.py"] = ""

files["app.py"] = """import streamlit as st
import requests
import json
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HealthBridge AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; }

/* Dark medical theme */
.stApp { background: #0a0f1e; color: #e2e8f0; }

[data-testid="stSidebar"] {
    background: #0d1529 !important;
    border-right: 1px solid #1e3a5f;
}

/* Cards */
.hb-card {
    background: linear-gradient(135deg, #0d1f3c 0%, #0a1628 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: transform 0.2s, box-shadow 0.2s;
}
.hb-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(59,130,246,0.15);
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0d1f3c, #0a1628);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #38bdf8;
}
.metric-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14,165,233,0.4) !important;
}

/* Input fields */
.stTextArea textarea, .stTextInput input {
    background: #0d1f3c !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Risk badges */
.badge-low { background: #052e16; color: #4ade80; border: 1px solid #16a34a; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.badge-medium { background: #431407; color: #fb923c; border: 1px solid #ea580c; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.badge-high { background: #450a0a; color: #f87171; border: 1px solid #dc2626; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #38bdf8;
    border-bottom: 2px solid #1e3a5f;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Logo */
.logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* AI response box */
.ai-response {
    background: linear-gradient(135deg, #0f172a, #0d1f3c);
    border-left: 4px solid #38bdf8;
    border-radius: 0 12px 12px 0;
    padding: 20px;
    margin-top: 16px;
    line-height: 1.8;
}

/* Alert box */
.alert-warning {
    background: #431407;
    border: 1px solid #ea580c;
    border-radius: 10px;
    padding: 12px 16px;
    color: #fed7aa;
    font-size: 0.9rem;
}
.alert-success {
    background: #052e16;
    border: 1px solid #16a34a;
    border-radius: 10px;
    padding: 12px 16px;
    color: #bbf7d0;
    font-size: 0.9rem;
}
</style>
\"\"\", unsafe_allow_html=True)

# ─── Backend API URL ────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

# ─── Session State ──────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# ─── Helper Functions ───────────────────────────────────────────────────────────
def api_post(endpoint, data, auth=False):
    headers = {"Content-Type": "application/json"}
    if auth and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def api_get(endpoint):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        r = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ─── Auth Pages ─────────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="logo-text">🏥 HealthBridge AI</div>', unsafe_allow_html=True)
        st.markdown("##### *Your intelligent health companion*")
        st.markdown("---")

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.markdown("### Welcome back")
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login →", key="login_btn", use_container_width=True):
                resp = api_post("/auth/login", {"email": email, "password": password})
                if "access_token" in resp:
                    st.session_state.token = resp["access_token"]
                    st.session_state.user = {"email": email, "name": resp.get("name", email)}
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error(resp.get("detail", "Login failed"))

        with tab2:
            st.markdown("### Create account")
            name = st.text_input("Full Name", key="reg_name")
            email2 = st.text_input("Email", key="reg_email")
            age = st.number_input("Age", min_value=1, max_value=120, value=25, key="reg_age")
            password2 = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Register →", key="reg_btn", use_container_width=True):
                resp = api_post("/auth/register", {
                    "name": name, "email": email2,
                    "password": password2, "age": age
                })
                if "id" in resp:
                    st.success("Account created! Please login.")
                else:
                    st.error(resp.get("detail", "Registration failed"))

# ─── Sidebar ────────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown('<div class="logo-text">🏥 HealthBridge</div>', unsafe_allow_html=True)
        st.markdown(f"*Welcome, {st.session_state.user['name']}*")
        st.markdown("---")

        pages = {
            "🏠 Dashboard": "dashboard",
            "🔍 Symptom Checker": "symptoms",
            "💊 Medicine Info": "medicine",
            "📋 Health History": "history",
            "⚙️ Settings": "settings"
        }

        for label, page in pages.items():
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

# ─── Dashboard Page ─────────────────────────────────────────────────────────────
def show_dashboard():
    st.markdown('<div class="section-title">📊 Health Dashboard</div>', unsafe_allow_html=True)

    history = api_get("/health/history")
    records = history if isinstance(history, list) else []

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Total Checks", len(records), "🔍"),
        ("This Month", sum(1 for r in records if datetime.fromisoformat(r.get("created_at","2000-01-01")).month == datetime.now().month) if records else 0, "📅"),
        ("High Risk Flags", sum(1 for r in records if r.get("risk_level") == "high"), "🚨"),
        ("Medicines Looked Up", api_get("/medicine/count").get("count", 0) if st.session_state.token else 0, "💊"),
    ]
    for col, (label, val, icon) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f\"\"\"
            <div class="metric-card">
                <div style="font-size:1.8rem">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>\"\"\", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown('<div class="section-title">🕐 Recent Activity</div>', unsafe_allow_html=True)
        if records:
            for r in records[-5:][::-1]:
                risk = r.get("risk_level", "low")
                badge_class = f"badge-{risk}"
                st.markdown(f\"\"\"
                <div class="hb-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>{r.get('symptoms','')[:60]}...</strong><br>
                            <small style="color:#64748b">{r.get('created_at','')[:10]}</small>
                        </div>
                        <span class="{badge_class}">{risk.upper()}</span>
                    </div>
                </div>\"\"\", unsafe_allow_html=True)
        else:
            st.markdown('<div class="hb-card"><p style="color:#64748b">No health checks yet. Start with the Symptom Checker!</p></div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Check Symptoms", use_container_width=True):
            st.session_state.page = "symptoms"; st.rerun()
        if st.button("💊 Medicine Lookup", use_container_width=True):
            st.session_state.page = "medicine"; st.rerun()
        if st.button("📋 View Full History", use_container_width=True):
            st.session_state.page = "history"; st.rerun()

        st.markdown('<div class="section-title" style="margin-top:20px">💡 Health Tip</div>', unsafe_allow_html=True)
        tips = [
            "Drink 8 glasses of water daily",
            "Sleep 7-8 hours for optimal health",
            "Walk 10,000 steps a day",
            "Eat 5 portions of fruits & vegetables",
        ]
        import random
        st.markdown(f'<div class="hb-card"><p>💡 {random.choice(tips)}</p></div>', unsafe_allow_html=True)

# ─── Symptom Checker Page ───────────────────────────────────────────────────────
def show_symptom_checker():
    st.markdown('<div class="section-title">🔍 AI Symptom Checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-warning">⚠️ This is for informational purposes only. Always consult a qualified doctor for medical advice.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        symptoms = st.text_area(
            "Describe your symptoms",
            height=150,
            placeholder="e.g., I have a severe headache for 2 days, mild fever around 99°F, and feel very tired...",
            key="symptom_input"
        )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            age = st.number_input("Age", 1, 120, 25)
        with col_b:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col_c:
            duration = st.selectbox("Duration", ["< 1 day", "1-3 days", "1 week", "> 1 week"])

        existing = st.multiselect("Existing conditions (if any)",
            ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "None"])

        if st.button("🧠 Analyze Symptoms", use_container_width=True):
            if not symptoms.strip():
                st.error("Please describe your symptoms")
            else:
                with st.spinner("AI is analyzing your symptoms..."):
                    resp = api_post("/symptom/analyze", {
                        "symptoms": symptoms,
                        "age": age,
                        "gender": gender,
                        "duration": duration,
                        "existing_conditions": existing
                    }, auth=True)

                if "error" not in resp:
                    st.session_state["last_analysis"] = resp
                else:
                    st.error(f"Error: {resp['error']}")

    with col2:
        st.markdown("#### 📌 How it works")
        steps = [
            ("1", "Describe symptoms in detail"),
            ("2", "AI analyzes using medical knowledge"),
            ("3", "Get possible conditions & risk level"),
            ("4", "Receive doctor consultation advice"),
        ]
        for num, step in steps:
            st.markdown(f\"\"\"
            <div class="hb-card" style="padding:12px; margin:6px 0">
                <span style="background:#1d4ed8; color:white; border-radius:50%; padding:2px 8px; font-weight:bold; margin-right:8px">{num}</span>
                {step}
            </div>\"\"\", unsafe_allow_html=True)

    # Show analysis result
    if "last_analysis" in st.session_state:
        r = st.session_state["last_analysis"]
        st.markdown("---")
        st.markdown('<div class="section-title">🤖 AI Analysis Result</div>', unsafe_allow_html=True)

        risk = r.get("risk_level", "low")
        badge = f"badge-{risk}"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Risk Level</div><br><span class="{badge}">{risk.upper()}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">See Doctor</div><div class="metric-value" style="font-size:1.2rem">{"Yes ⚠️" if r.get("see_doctor") else "Monitor 👁️"}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Urgency</div><div class="metric-value" style="font-size:1.2rem">{r.get("urgency","Normal")}</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="ai-response">{r.get("analysis","")}</div>', unsafe_allow_html=True)

        if r.get("possible_conditions"):
            st.markdown("#### 🩺 Possible Conditions")
            cols = st.columns(len(r["possible_conditions"][:3]))
            for i, cond in enumerate(r["possible_conditions"][:3]):
                with cols[i]:
                    st.markdown(f\"\"\"
                    <div class="hb-card" style="text-align:center">
                        <strong>{cond.get('name','')}</strong><br>
                        <small style="color:#64748b">{cond.get('probability','')} match</small>
                    </div>\"\"\", unsafe_allow_html=True)

# ─── Medicine Info Page ─────────────────────────────────────────────────────────
def show_medicine_info():
    st.markdown('<div class="section-title">💊 Medicine Information</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        medicine_name = st.text_input("Enter medicine name", placeholder="e.g., Paracetamol, Amoxicillin, Metformin...")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔍 Get Medicine Info", use_container_width=True):
                if medicine_name:
                    with st.spinner("Fetching medicine information..."):
                        resp = api_post("/medicine/info", {"medicine_name": medicine_name}, auth=True)
                    if "error" not in resp:
                        st.session_state["medicine_info"] = resp
                    else:
                        st.error(resp["error"])
        with col_b:
            if st.button("⚠️ Check Interactions", use_container_width=True):
                st.info("Enter two medicines below to check interactions")

    with col2:
        st.markdown('<div class="hb-card"><p>🔎 <strong>What you get:</strong></p><ul><li>Uses & dosage</li><li>Side effects</li><li>Precautions</li><li>Drug interactions</li><li>Indian brand names</li></ul></div>', unsafe_allow_html=True)

    if "medicine_info" in st.session_state:
        info = st.session_state["medicine_info"]
        st.markdown("---")
        st.markdown(f'<div class="section-title">📋 {info.get("name", medicine_name)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-response">{info.get("information","")}</div>', unsafe_allow_html=True)

# ─── Health History Page ────────────────────────────────────────────────────────
def show_history():
    st.markdown('<div class="section-title">📋 Health History</div>', unsafe_allow_html=True)
    history = api_get("/health/history")

    if isinstance(history, list) and history:
        for record in history[::-1]:
            risk = record.get("risk_level", "low")
            badge = f"badge-{risk}"
            with st.expander(f"🔍 {record.get('symptoms','')[:80]}... — {record.get('created_at','')[:10]}"):
                st.markdown(f'<span class="{badge}">{risk.upper()} RISK</span>', unsafe_allow_html=True)
                st.markdown(f"**Analysis:** {record.get('analysis','')}")
                st.markdown(f"**Doctor Visit Recommended:** {'✅ Yes' if record.get('see_doctor') else '❌ Not urgent'}")
    else:
        st.markdown('<div class="hb-card"><p style="color:#64748b; text-align:center">No health records yet. Use the Symptom Checker to get started!</p></div>', unsafe_allow_html=True)

# ─── Main App ───────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        show_login()
    else:
        show_sidebar()
        page = st.session_state.page
        if page == "dashboard":
            show_dashboard()
        elif page == "symptoms":
            show_symptom_checker()
        elif page == "medicine":
            show_medicine_info()
        elif page == "history":
            show_history()
        elif page == "settings":
            st.markdown('<div class="section-title">⚙️ Settings</div>', unsafe_allow_html=True)
            st.info("Profile settings coming soon.")

if __name__ == "__main__":
    main()
"""

files["backend/main.py"] = """from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from database import init_db
from routers import auth, symptom, medicine, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="HealthBridge AI API",
    description="Intelligent Healthcare Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/auth",     tags=["Authentication"])
app.include_router(symptom.router,  prefix="/symptom",  tags=["Symptom Analysis"])
app.include_router(medicine.router, prefix="/medicine",  tags=["Medicine Info"])
app.include_router(health.router,   prefix="/health",    tags=["Health Records"])

@app.get("/")
def root():
    return {"message": "HealthBridge AI API", "status": "running", "version": "1.0.0"}

@app.get("/health-check")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
"""

files["backend/database.py"] = """import sqlite3
import os

DB_PATH = "healthbridge.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    \"\"\")

    # Symptom analysis history
    cursor.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS symptom_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symptoms TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            duration TEXT,
            existing_conditions TEXT,
            analysis TEXT,
            risk_level TEXT DEFAULT 'low',
            see_doctor BOOLEAN DEFAULT 0,
            urgency TEXT DEFAULT 'Normal',
            possible_conditions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    \"\"\")

    # Medicine lookup history
    cursor.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS medicine_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            information TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    \"\"\")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")
"""

files["backend/routers/auth.py"] = """from fastapi import APIRouter, HTTPException, status, Depends
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
"""

files["backend/routers/symptom.py"] = """from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
import json
import os
import logging
from datetime import datetime
from database import get_connection
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# ─── Configure Gemini ──────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None
    logger.warning("GEMINI_API_KEY not set — AI features will be limited")

# ─── Schemas ───────────────────────────────────────────────────────────────────
class SymptomRequest(BaseModel):
    symptoms: str
    age: int = 25
    gender: str = "Male"
    duration: str = "1-3 days"
    existing_conditions: List[str] = []

# ─── AI Analysis ───────────────────────────────────────────────────────────────
def analyze_with_gemini(req: SymptomRequest) -> dict:
    if not model:
        # Fallback response if no API key
        return {
            "analysis": "AI analysis unavailable. Please set GEMINI_API_KEY environment variable.",
            "risk_level": "low",
            "see_doctor": False,
            "urgency": "Normal",
            "possible_conditions": []
        }

    prompt = f\"\"\"
You are a medical AI assistant. Analyze the following symptoms and provide a structured medical assessment.

Patient Information:
- Age: {req.age}
- Gender: {req.gender}
- Symptom Duration: {req.duration}
- Existing Conditions: {', '.join(req.existing_conditions) if req.existing_conditions else 'None'}

Symptoms Described: {req.symptoms}

Provide your response ONLY as a valid JSON object with this exact structure:
{{
  "analysis": "Detailed 3-4 sentence medical analysis explaining possible causes, what the symptoms could indicate, and general advice",
  "risk_level": "low|medium|high",
  "see_doctor": true|false,
  "urgency": "Normal|Soon|Urgent|Emergency",
  "possible_conditions": [
    {{"name": "Condition Name", "probability": "High/Medium/Low"}},
    {{"name": "Condition Name", "probability": "High/Medium/Low"}},
    {{"name": "Condition Name", "probability": "High/Medium/Low"}}
  ],
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "disclaimer": "Always consult a qualified medical professional for diagnosis and treatment."
}}

Risk level guide: low=mild symptoms manageable at home, medium=needs monitoring/possible doctor visit, high=should see doctor soon/emergency.
Respond with ONLY the JSON, no other text.
\"\"\"

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse Gemini response as JSON")
        return {
            "analysis": response.text[:500] if 'response' in dir() else "Analysis failed",
            "risk_level": "medium",
            "see_doctor": True,
            "urgency": "Soon",
            "possible_conditions": []
        }
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

# ─── Routes ────────────────────────────────────────────────────────────────────
@router.post("/analyze")
def analyze_symptoms(req: SymptomRequest, user_id: int = Depends(get_current_user)):
    # Get AI analysis
    result = analyze_with_gemini(req)

    # Save to database
    conn = get_connection()
    try:
        conn.execute(\"\"\"
            INSERT INTO symptom_records
            (user_id, symptoms, age, gender, duration, existing_conditions,
             analysis, risk_level, see_doctor, urgency, possible_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            user_id,
            req.symptoms,
            req.age,
            req.gender,
            req.duration,
            json.dumps(req.existing_conditions),
            result.get("analysis", ""),
            result.get("risk_level", "low"),
            result.get("see_doctor", False),
            result.get("urgency", "Normal"),
            json.dumps(result.get("possible_conditions", []))
        ))
        conn.commit()
        logger.info(f"Symptom record saved for user {user_id}")
    except Exception as e:
        logger.error(f"DB error saving symptom record: {e}")
    finally:
        conn.close()

    return result

@router.get("/history")
def get_symptom_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    records = conn.execute(
        "SELECT * FROM symptom_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]
"""

files["backend/routers/medicine.py"] = """from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import json
import os
import logging
from database import get_connection
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

class MedicineRequest(BaseModel):
    medicine_name: str

def get_medicine_info_from_ai(medicine_name: str) -> dict:
    if not model:
        return {"name": medicine_name, "information": "AI service unavailable. Set GEMINI_API_KEY."}

    prompt = f\"\"\"
You are a pharmacist AI. Provide comprehensive information about the medicine: {medicine_name}

Respond ONLY as a valid JSON object:
{{
  "name": "Medicine generic name",
  "brand_names_india": ["Brand1", "Brand2"],
  "category": "Drug category",
  "uses": ["use 1", "use 2", "use 3"],
  "how_it_works": "Brief mechanism of action",
  "dosage": "Typical adult dosage and frequency",
  "side_effects": ["common side effect 1", "common side effect 2", "serious side effect"],
  "precautions": ["precaution 1", "precaution 2"],
  "interactions": ["drug interaction 1", "drug interaction 2"],
  "avoid_if": ["condition 1", "condition 2"],
  "available_otc": true|false,
  "information": "2-3 sentence comprehensive summary for the patient",
  "disclaimer": "Always take medicines as prescribed by your doctor."
}}

Respond with ONLY the JSON, no other text.
\"\"\"
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Medicine info error: {e}")
        return {"name": medicine_name, "information": f"Could not retrieve information for {medicine_name}."}

@router.post("/info")
def get_medicine_info(req: MedicineRequest, user_id: int = Depends(get_current_user)):
    result = get_medicine_info_from_ai(req.medicine_name)

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO medicine_records (user_id, medicine_name, information) VALUES (?, ?, ?)",
            (user_id, req.medicine_name, json.dumps(result))
        )
        conn.commit()
    except Exception as e:
        logger.error(f"DB error: {e}")
    finally:
        conn.close()

    return result

@router.get("/count")
def get_medicine_count(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) as count FROM medicine_records WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return {"count": count["count"] if count else 0}

@router.get("/history")
def get_medicine_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    records = conn.execute(
        "SELECT * FROM medicine_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]
"""

files["backend/routers/health.py"] = """from fastapi import APIRouter, Depends
from database import get_connection
from routers.auth import get_current_user
import json

router = APIRouter()

@router.get("/history")
def get_full_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    records = conn.execute(
        \"\"\"SELECT id, symptoms, risk_level, see_doctor, urgency, analysis, created_at
           FROM symptom_records WHERE user_id = ?
           ORDER BY created_at DESC LIMIT 50\"\"\",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]

@router.get("/summary")
def get_health_summary(user_id: int = Depends(get_current_user)):
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) as count FROM symptom_records WHERE user_id = ?", (user_id,)
    ).fetchone()["count"]

    high_risk = conn.execute(
        "SELECT COUNT(*) as count FROM symptom_records WHERE user_id = ? AND risk_level = 'high'", (user_id,)
    ).fetchone()["count"]

    medicines = conn.execute(
        "SELECT COUNT(*) as count FROM medicine_records WHERE user_id = ?", (user_id,)
    ).fetchone()["count"]

    conn.close()
    return {
        "total_checks": total,
        "high_risk_count": high_risk,
        "medicines_looked_up": medicines
    }
"""


# Create directories and files
dirs = ["backend", "backend/routers"]
for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"📁 Created folder: {d}/")

for filepath, code in files.items():
    with open(filepath, "w") as f:
        f.write(code)
    print(f"✅ Created: {filepath}")

print("")
print("🎉 All files created successfully!")
print("")
print("Next steps:")
print("1. Edit .env file — add your Gemini API key")
print("2. Run: source venv/bin/activate")
print("3. Run backend: cd backend && uvicorn main:app --reload --port 8000")
print("4. Run frontend (new terminal): streamlit run app.py")
