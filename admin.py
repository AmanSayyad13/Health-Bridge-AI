import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="HealthBridge Admin", page_icon="🔐", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
* { font-family: 'DM Sans', sans-serif; }
h1,h2,h3 { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0f1e; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #0d1529 !important; border-right: 1px solid #1e3a5f; }
.metric-card { background: linear-gradient(135deg, #0d1f3c, #0a1628); border: 1px solid #1e3a5f; border-radius: 12px; padding: 20px; text-align: center; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #38bdf8; }
.metric-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; }
.user-card { background: #0d1f3c; border: 1px solid #1e3a5f; border-radius: 12px; padding: 16px; margin: 8px 0; }
.badge-low { background: #052e16; color: #4ade80; border: 1px solid #16a34a; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-medium { background: #431407; color: #fb923c; border: 1px solid #ea580c; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-high { background: #450a0a; color: #f87171; border: 1px solid #dc2626; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.stButton > button { background: linear-gradient(135deg, #1d4ed8, #0ea5e9) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

if "admin_token" not in st.session_state:
    st.session_state.admin_token = None

def api_get(endpoint):
    headers = {"Authorization": f"Bearer {st.session_state.admin_token}"}
    try:
        r = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=30)
        return r.json()
    except:
        return {}

def api_post(endpoint, data):
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=data, timeout=30)
        return r.json()
    except:
        return {}

# ── LOGIN ──
if not st.session_state.admin_token:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("## 🔐 Admin Login")
        email = st.text_input("Admin Email", value="admin@healthbridge.com")
        password = st.text_input("Password", type="password")
        if st.button("Login →", use_container_width=True):
            resp = api_post("/auth/admin/login", {"email": email, "password": password})
            if "access_token" in resp:
                st.session_state.admin_token = resp["access_token"]
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("### 🔐 Admin Panel")
        st.markdown("---")
        page = st.radio("Navigate", ["📊 Dashboard", "👥 All Users", "🔍 Symptom Logs"])
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.admin_token = None
            st.rerun()

    # ── DASHBOARD ──
    if page == "📊 Dashboard":
        st.markdown("## 📊 Platform Overview")
        stats = api_get("/admin/stats")
        col1, col2, col3, col4 = st.columns(4)
        metrics = [
            ("Total Users", stats.get("total_users", 0), "👥"),
            ("Symptom Checks", stats.get("total_symptom_checks", 0), "🔍"),
            ("Medicine Lookups", stats.get("total_medicine_lookups", 0), "💊"),
            ("High Risk Cases", stats.get("high_risk_cases", 0), "🚨"),
        ]
        for col, (label, val, icon) in zip([col1,col2,col3,col4], metrics):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div style="font-size:1.8rem">{icon}</div>
                    <div class="metric-value">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>""", unsafe_allow_html=True)

    # ── ALL USERS ──
    elif page == "👥 All Users":
        st.markdown("## 👥 Registered Users")
        users = api_get("/admin/users")
        if isinstance(users, list):
            for u in users:
                with st.expander(f"👤 {u.get('name')} — {u.get('email')} | Joined: {str(u.get('created_at',''))[:10]}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Age", u.get('age', 'N/A'))
                    with col2:
                        st.metric("Symptom Checks", u.get('symptom_checks', 0))
                    with col3:
                        st.metric("Medicine Lookups", u.get('medicine_lookups', 0))
                    if st.button(f"View Full Activity", key=f"act_{u['id']}"):
                        activity = api_get(f"/admin/users/{u['id']}/activity")
                        st.session_state[f"activity_{u['id']}"] = activity
                    if f"activity_{u['id']}" in st.session_state:
                        act = st.session_state[f"activity_{u['id']}"]
                        st.markdown("**Symptom History:**")
                        for s in act.get("symptom_checks", []):
                            risk = s.get('risk_level','low')
                            st.markdown(f"""<div class="user-card">
                                <span class="badge-{risk}">{risk.upper()}</span>
                                <strong> {s.get('symptoms','')[:80]}...</strong><br>
                                <small style="color:#64748b">{str(s.get('created_at',''))[:10]}</small>
                            </div>""", unsafe_allow_html=True)
                        st.markdown("**Medicine Lookups:**")
                        for m in act.get("medicine_lookups", []):
                            st.markdown(f"💊 **{m.get('medicine_name')}** — {str(m.get('created_at',''))[:10]}")

    # ── SYMPTOM LOGS ──
    elif page == "🔍 Symptom Logs":
        st.markdown("## 🔍 All Symptom Checks")
        logs = api_get("/admin/symptoms/all")
        if isinstance(logs, list):
            for log in logs:
                risk = log.get('risk_level', 'low')
                st.markdown(f"""<div class="user-card">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div>
                            <strong>{log.get('name')}</strong>
                            <span style="color:#64748b"> ({log.get('email')})</span>
                        </div>
                        <span class="badge-{risk}">{risk.upper()}</span>
                    </div>
                    <p style="margin:8px 0; color:#94a3b8">{log.get('symptoms','')[:120]}...</p>
                    <small style="color:#64748b">🕐 {str(log.get('created_at',''))[:16]} &nbsp;|&nbsp; 
                    Doctor: {'✅ Yes' if log.get('see_doctor') else '❌ No'} &nbsp;|&nbsp; 
                    Urgency: {log.get('urgency','Normal')}</small>
                </div>""", unsafe_allow_html=True)
