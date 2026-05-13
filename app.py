import streamlit as st
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
st.markdown("""
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
""", unsafe_allow_html=True)

# ─── Backend API URL ────────────────────────────────────────────────────────────
API_URL = "https://healthbridge-backend-ws6z.onrender.com"

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
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.8rem">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown('<div class="section-title">🕐 Recent Activity</div>', unsafe_allow_html=True)
        if records:
            for r in records[-5:][::-1]:
                risk = r.get("risk_level", "low")
                badge_class = f"badge-{risk}"
                st.markdown(f"""
                <div class="hb-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>{r.get('symptoms','')[:60]}...</strong><br>
                            <small style="color:#64748b">{r.get('created_at','')[:10]}</small>
                        </div>
                        <span class="{badge_class}">{risk.upper()}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
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
            st.markdown(f"""
            <div class="hb-card" style="padding:12px; margin:6px 0">
                <span style="background:#1d4ed8; color:white; border-radius:50%; padding:2px 8px; font-weight:bold; margin-right:8px">{num}</span>
                {step}
            </div>""", unsafe_allow_html=True)

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
                    st.markdown(f"""
                    <div class="hb-card" style="text-align:center">
                        <strong>{cond.get('name','')}</strong><br>
                        <small style="color:#64748b">{cond.get('probability','')} match</small>
                    </div>""", unsafe_allow_html=True)

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
