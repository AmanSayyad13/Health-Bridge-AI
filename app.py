import streamlit as st
import requests
import re
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = "https://healthbridge-backend-ws6z.onrender.com"

st.set_page_config(
    page_title="HealthBridge — AI Health Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in [("token",None),("user",None),("page","dashboard"),("analysis",None),("med_info",None),("backend_ready",False)]:
    if k not in st.session_state: st.session_state[k] = v

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background-color: #0a0a0a !important;
    color: #e8e6e1 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"], .stDeployButton,
section[data-testid="stSidebar"], [data-testid="stDecoration"] {
    display: none !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Inputs ── */
input[type="text"], input[type="email"], input[type="password"],
input[type="number"], textarea,
.stTextInput input, .stTextArea textarea,
.stNumberInput input, .stPasswordInput input {
    background: #141414 !important;
    color: #e8e6e1 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
    -webkit-text-fill-color: #e8e6e1 !important;
}

input[type="text"]:focus, input[type="password"]:focus,
input[type="email"]:focus, textarea:focus,
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #22c55e !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(34,197,94,0.15) !important;
}

/* ── Selectbox — complete fix ── */
.stSelectbox > div > div,
.stSelectbox > div > div > div,
[data-baseweb="select"] > div {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e6e1 !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #e8e6e1 !important;
    background: #141414 !important;
}

[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="menu"] > ul {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
}

[role="option"] {
    background: #1a1a1a !important;
    color: #e8e6e1 !important;
    font-family: 'Inter', sans-serif !important;
}

[role="option"]:hover, [aria-selected="true"] {
    background: #222 !important;
    color: #22c55e !important;
}

/* ── Multiselect ── */
.stMultiSelect > div {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e6e1 !important;
}
[data-baseweb="tag"] {
    background: #1a3a27 !important;
    color: #22c55e !important;
    border-radius: 4px !important;
}

/* ── Labels ── */
label, .stTextInput label, .stSelectbox label,
.stTextArea label, .stNumberInput label, .stMultiSelect label {
    color: #666 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #22c55e !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 11px 20px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #16a34a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(34,197,94,0.3) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111 !important;
    border-radius: 8px !important;
    padding: 3px !important;
    border: 1px solid #1e1e1e !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #666 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: #1a1a1a !important;
    color: #e8e6e1 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Expander ── */
.stExpander {
    background: #111 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
details summary {
    color: #e8e6e1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    padding: 14px 18px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 3px; }

/* ── Number input buttons ── */
.stNumberInput button {
    background: #1a1a1a !important;
    color: #e8e6e1 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    width: auto !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def valid_email(e):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e))

def api_post(endpoint, data, auth=False):
    h = {"Content-Type": "application/json"}
    if auth and st.session_state.token:
        h["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=data, headers=h, timeout=35)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def api_get(endpoint):
    h = {}
    if st.session_state.token:
        h["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        r = requests.get(f"{API_URL}{endpoint}", headers=h, timeout=35)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def wake_backend():
    """Wake up Render backend silently"""
    if not st.session_state.backend_ready:
        try:
            r = requests.get(f"{API_URL}/health-check", timeout=60)
            if r.status_code == 200:
                st.session_state.backend_ready = True
        except:
            pass

# ── Card components ───────────────────────────────────────────────────────────
def card(content, border_color="#1e1e1e", padding="24px"):
    return f"""<div style="background:#111;border:1px solid {border_color};border-radius:12px;padding:{padding};margin-bottom:14px">{content}</div>"""

def stat_card(icon, value, label, color="#22c55e"):
    return f"""
    <div style="background:#111;border:1px solid #1e1e1e;border-radius:12px;
                padding:22px;border-top:2px solid {color}">
        <div style="font-size:20px;margin-bottom:12px">{icon}</div>
        <div style="font-family:'Playfair Display',serif;font-size:2rem;
                    font-weight:700;color:{color};line-height:1;margin-bottom:6px">{value}</div>
        <div style="font-size:11px;font-weight:600;color:#444;
                    text-transform:uppercase;letter-spacing:0.08em">{label}</div>
    </div>"""

def badge(text, level="low"):
    colors = {"low":("#22c55e","#1a3a27"),"medium":("#f59e0b","#3a2a10"),"high":("#ef4444","#3a1a1a")}
    fg, bg = colors.get(level, colors["low"])
    return f"""<span style="background:{bg};color:{fg};padding:4px 12px;border-radius:20px;
                font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em">{text}</span>"""

# ── Auth page ─────────────────────────────────────────────────────────────────
def show_login():
    # Wake backend silently while user is on login page
    wake_backend()

    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;min-height:100vh;padding:40px 20px;background:#0a0a0a">
        <div style="text-align:center;margin-bottom:48px">
            <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:12px">
                <div style="width:38px;height:38px;background:#22c55e;border-radius:9px;
                            display:flex;align-items:center;justify-content:center;font-size:18px">🏥</div>
                <span style="font-family:'Playfair Display',serif;font-size:1.8rem;
                             font-weight:700;color:#e8e6e1;letter-spacing:-0.02em">HealthBridge</span>
            </div>
            <div style="font-size:14px;color:#555;font-weight:400">
                AI-powered healthcare intelligence platform
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.05, 1])
    with col2:
        st.markdown("""
        <div style="background:#111;border:1px solid #1e1e1e;border-radius:16px;padding:36px 32px;">
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign in", "Create account"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", key="li_e", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="li_p", placeholder="Enter password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign in →", key="login_btn"):
                if not email.strip():
                    st.error("Please enter your email")
                elif not valid_email(email.strip()):
                    st.error("Please enter a valid email — e.g. name@gmail.com")
                elif not password:
                    st.error("Please enter your password")
                else:
                    with st.spinner("Signing in..."):
                        resp = api_post("/auth/login", {"email": email.strip().lower(), "password": password})
                    if "access_token" in resp:
                        st.session_state.token = resp["access_token"]
                        st.session_state.user = {"name": resp.get("name", email), "email": email}
                        st.rerun()
                    else:
                        st.error(resp.get("detail", "Invalid email or password"))

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            name = st.text_input("Full name", key="rn", placeholder="Your full name")
            email2 = st.text_input("Email", key="re", placeholder="you@example.com")
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", 1, 120, 22, key="ra")
            with c2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="rg")
            pw = st.text_input("Password", type="password", key="rp", placeholder="Minimum 6 characters")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create account →", key="reg_btn"):
                errors = []
                if not name.strip(): errors.append("Name is required")
                if not email2.strip(): errors.append("Email is required")
                elif not valid_email(email2.strip()): errors.append("Invalid email — use a real email like name@gmail.com")
                if len(pw) < 6: errors.append("Password must be at least 6 characters")
                if errors:
                    for e in errors: st.error(e)
                else:
                    with st.spinner("Creating account..."):
                        resp = api_post("/auth/register", {
                            "name": name.strip(), "email": email2.strip().lower(),
                            "password": pw, "age": int(age)
                        })
                    if "id" in resp:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error(resp.get("detail", "Registration failed. Please try again."))

        st.markdown("""
        <div style="text-align:center;margin-top:28px;padding-top:20px;
                    border-top:1px solid #1a1a1a;font-size:11px;color:#333">
            For informational purposes only · Not a substitute for medical advice
        </div>
        """, unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────────────────────
def show_nav():
    name = st.session_state.user.get("name","User")
    pg = st.session_state.page
    pages = [("dashboard","Overview"),("symptoms","Symptom Check"),("medicine","Medicines"),("history","History")]

    links = "".join([
        f'<div style="padding:7px 16px;border-radius:7px;font-size:13px;font-weight:500;cursor:pointer;'
        f'background:{"#1a1a1a" if pg==p else "transparent"};color:{"#22c55e" if pg==p else "#666"}">{l}</div>'
        for p,l in pages
    ])

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:14px 40px;background:#0d0d0d;border-bottom:1px solid #161616;
                position:sticky;top:0;z-index:999;">
        <div style="display:flex;align-items:center;gap:8px">
            <div style="width:30px;height:30px;background:#22c55e;border-radius:7px;
                        display:flex;align-items:center;justify-content:center;font-size:14px">🏥</div>
            <span style="font-family:'Playfair Display',serif;font-size:1.2rem;
                         font-weight:700;color:#e8e6e1;letter-spacing:-0.02em">HealthBridge</span>
        </div>
        <div style="display:flex;gap:2px;align-items:center">{links}</div>
        <div style="display:flex;align-items:center;gap:10px">
            <span style="font-size:13px;color:#555">{name.split()[0]}</span>
            <div style="width:32px;height:32px;border-radius:50%;background:#1a3a27;
                        border:1.5px solid #22c55e;display:inline-flex;align-items:center;
                        justify-content:center;color:#22c55e;font-weight:700;font-size:13px">
                {name[0].upper()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nc = st.columns([1,1,1,1,5,1])
    for i,(p,l) in enumerate(pages):
        with nc[i]:
            if st.button(l, key=f"n_{p}"):
                st.session_state.page = p; st.rerun()
    with nc[5]:
        if st.button("Sign out", key="n_out"):
            for k in ["token","user","analysis","med_info","backend_ready"]:
                st.session_state[k] = None if k!="backend_ready" else False
            st.session_state.page = "dashboard"
            st.rerun()

# ── Dashboard ──────────────────────────────────────────────────────────────────
def show_dashboard():
    st.markdown('<div style="max-width:1080px;margin:0 auto;padding:44px 40px">', unsafe_allow_html=True)

    name = st.session_state.user.get("name","there").split()[0]
    h = datetime.now().hour
    greet = "Good morning" if h<12 else "Good afternoon" if h<17 else "Good evening"

    st.markdown(f"""
    <div style="margin-bottom:40px">
        <div style="font-family:'Playfair Display',serif;font-size:2.2rem;font-weight:700;
                    color:#e8e6e1;letter-spacing:-0.02em;margin-bottom:6px">
            {greet}, {name}
        </div>
        <div style="font-size:14px;color:#555">Here's your personal health overview</div>
    </div>
    """, unsafe_allow_html=True)

    history = api_get("/health/history")
    records = history if isinstance(history, list) else []
    med_count = api_get("/medicine/count").get("count", 0)
    high_risk = sum(1 for r in records if r.get("risk_level")=="high")
    low_risk = len(records) - high_risk

    c1,c2,c3,c4 = st.columns(4)
    for col,(icon,val,label,color) in zip(
        [c1,c2,c3,c4],
        [("🔍",len(records),"Total Checks","#60a5fa"),
         ("💊",med_count,"Medicines Looked Up","#a78bfa"),
         ("⚠️",high_risk,"High Risk Flags","#ef4444"),
         ("✓",low_risk,"Low Risk Checks","#22c55e")]
    ):
        with col:
            st.markdown(stat_card(icon,val,label,color), unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    cl, cr = st.columns([3,2])

    with cl:
        st.markdown('<div style="font-size:13px;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px">Recent Activity</div>', unsafe_allow_html=True)
        if records:
            for r in records[-5:][::-1]:
                risk = r.get("risk_level","low")
                colors = {"low":"#22c55e","medium":"#f59e0b","high":"#ef4444"}
                bgs = {"low":"#1a3a27","medium":"#3a2a10","high":"#3a1a1a"}
                date = str(r.get("created_at",""))[:10]
                preview = r.get("symptoms","")[:72]
                st.markdown(f"""
                <div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;
                            padding:14px 18px;margin-bottom:8px;display:flex;
                            justify-content:space-between;align-items:center">
                    <div>
                        <div style="font-size:13px;color:#e8e6e1;margin-bottom:4px;font-weight:500">
                            {preview}{'...' if len(r.get('symptoms',''))>72 else ''}
                        </div>
                        <div style="font-size:11px;color:#444">{date}</div>
                    </div>
                    <span style="background:{bgs[risk]};color:{colors[risk]};padding:4px 12px;
                                 border-radius:20px;font-size:10px;font-weight:700;
                                 text-transform:uppercase;white-space:nowrap;margin-left:14px">
                        {risk}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;
                        padding:48px;text-align:center">
                <div style="font-size:2rem;margin-bottom:10px">🩺</div>
                <div style="font-size:13px;color:#444">No checks yet — use the Symptom Checker to start</div>
            </div>
            """, unsafe_allow_html=True)

    with cr:
        st.markdown('<div style="font-size:13px;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍  Check Symptoms", key="qa1"): st.session_state.page="symptoms"; st.rerun()
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("💊  Medicine Lookup", key="qa2"): st.session_state.page="medicine"; st.rerun()
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("📋  View History", key="qa3"): st.session_state.page="history"; st.rerun()

        tips = [
            ("💧","Stay Hydrated","8 glasses of water daily maintains energy and focus."),
            ("😴","Prioritize Sleep","7–9 hours supports your immune system."),
            ("🚶","Move Daily","20-minute walks significantly improve heart health."),
            ("🥗","Eat Colorfully","Colorful vegetables provide essential micronutrients."),
        ]
        tip = tips[datetime.now().day % 4]
        st.markdown(f"""
        <div style="background:#111;border:1px solid #1a1a1a;border-left:2px solid #22c55e;
                    border-radius:0 10px 10px 0;padding:18px;margin-top:12px">
            <div style="font-size:18px;margin-bottom:8px">{tip[0]}</div>
            <div style="font-size:13px;font-weight:600;color:#e8e6e1;margin-bottom:5px">{tip[1]}</div>
            <div style="font-size:12px;color:#555;line-height:1.6">{tip[2]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Symptoms ───────────────────────────────────────────────────────────────────
def show_symptoms():
    st.markdown('<div style="max-width:1080px;margin:0 auto;padding:44px 40px">', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:28px">
        <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;
                    color:#e8e6e1;letter-spacing:-0.02em;margin-bottom:6px">Symptom Checker</div>
        <div style="font-size:14px;color:#555">AI-powered health assessment based on your symptoms</div>
    </div>
    <div style="background:#1c1500;border:1px solid #3a2a00;border-radius:8px;
                padding:12px 16px;font-size:13px;color:#f59e0b;margin-bottom:28px">
        ⚠️  For informational purposes only. Always consult a licensed doctor for medical decisions.
    </div>
    """, unsafe_allow_html=True)

    cf, ci = st.columns([3,1])
    with cf:
        st.markdown('<div style="background:#111;border:1px solid #1a1a1a;border-radius:12px;padding:28px">', unsafe_allow_html=True)
        symptoms = st.text_area("Describe your symptoms", height=130,
            placeholder="e.g. I have had a persistent headache for 2 days, mild fever around 99°F, and feel very fatigued...",
            key="sym")
        c1,c2,c3 = st.columns(3)
        with c1: age = st.number_input("Age", 1, 120, 22, key="sa")
        with c2: gender = st.selectbox("Gender", ["Male","Female","Other"], key="sg")
        with c3: duration = st.selectbox("Duration", ["< 1 day","1–3 days","4–7 days","> 1 week"], key="sd")
        existing = st.multiselect("Pre-existing conditions", ["Diabetes","Hypertension","Asthma","Heart Disease","None"], default=["None"], key="se")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        go = st.button("🧠  Analyze Symptoms", key="analyze")
        st.markdown('</div>', unsafe_allow_html=True)

        if go:
            if not symptoms.strip():
                st.error("Please describe your symptoms first")
            else:
                with st.spinner("Analyzing with AI..."):
                    resp = api_post("/symptom/analyze", {
                        "symptoms": symptoms, "age": age, "gender": gender,
                        "duration": duration,
                        "existing_conditions": [e for e in existing if e != "None"]
                    }, auth=True)
                if "error" not in resp:
                    st.session_state.analysis = resp
                else:
                    st.error(f"Error: {resp['error']}")

    with ci:
        st.markdown("""
        <div style="background:#111;border:1px solid #1a1a1a;border-radius:12px;padding:22px">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:#333;margin-bottom:18px">How it works</div>
        """ + "".join([
            f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:14px">'
            f'<div style="min-width:24px;height:24px;border-radius:50%;background:#1a3a27;'
            f'display:flex;align-items:center;justify-content:center;font-size:11px;'
            f'font-weight:700;color:#22c55e">{n}</div>'
            f'<div style="font-size:12px;color:#555;line-height:1.5">{t}</div></div>'
            for n,t in [("1","Describe your symptoms clearly"),("2","AI cross-references medical data"),
                        ("3","Get risk level and conditions"),("4","Decide on doctor visit")]
        ]) + "</div>", unsafe_allow_html=True)

    if st.session_state.analysis:
        r = st.session_state.analysis
        risk = r.get("risk_level","low")
        see_doc = r.get("see_doctor",False)
        urgency = r.get("urgency","Normal")
        rc = {"low":"#22c55e","medium":"#f59e0b","high":"#ef4444"}.get(risk,"#22c55e")
        rb = {"low":"#1a3a27","medium":"#3a2a10","high":"#3a1a1a"}.get(risk,"#1a3a27")

        st.markdown("<div style='height:28px;border-top:1px solid #1a1a1a;margin-top:24px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.2rem;font-weight:600;color:#e8e6e1;margin-bottom:18px">Analysis Result</div>', unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:600;color:#333;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px">Risk Level</div>
                <span style="background:{rb};color:{rc};padding:5px 14px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase">{risk.upper()}</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:600;color:#333;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px">See a Doctor</div>
                <div style="font-size:14px;font-weight:700;color:{'#ef4444' if see_doc else '#22c55e'}">{'Recommended' if see_doc else 'Not Urgent'}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:18px">
                <div style="font-size:11px;font-weight:600;color:#333;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px">Urgency</div>
                <div style="font-size:14px;font-weight:700;color:#e8e6e1">{urgency}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#111;border:1px solid #1a1a1a;border-left:2px solid #22c55e;
                    border-radius:0 10px 10px 0;padding:22px;margin-top:14px;
                    font-size:14px;line-height:1.8;color:#ccc">
            {r.get("analysis","")}
        </div>""", unsafe_allow_html=True)

        conditions = r.get("possible_conditions",[])
        if conditions:
            st.markdown('<div style="font-size:13px;font-weight:600;color:#e8e6e1;margin-top:22px;margin-bottom:12px">Possible Conditions</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(conditions),3))
            for i,cond in enumerate(conditions[:3]):
                prob = cond.get("probability","").lower()
                c = {"high":"#ef4444","medium":"#f59e0b"}.get(prob,"#22c55e")
                bg = {"high":"#3a1a1a","medium":"#3a2a10"}.get(prob,"#1a3a27")
                with cols[i]:
                    st.markdown(f"""<div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:16px;text-align:center">
                        <div style="font-size:13px;font-weight:600;color:#e8e6e1;margin-bottom:8px">{cond.get('name','')}</div>
                        <span style="background:{bg};color:{c};padding:3px 12px;border-radius:20px;font-size:10px;font-weight:700;text-transform:uppercase">{cond.get('probability','')}</span>
                    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Medicine ───────────────────────────────────────────────────────────────────
def show_medicine():
    st.markdown('<div style="max-width:1080px;margin:0 auto;padding:44px 40px">', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:28px">
        <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;
                    color:#e8e6e1;letter-spacing:-0.02em;margin-bottom:6px">Medicine Information</div>
        <div style="font-size:14px;color:#555">Dosage, side effects, interactions and Indian brand names</div>
    </div>
    """, unsafe_allow_html=True)

    cs, ct = st.columns([2,1])
    with cs:
        med = st.text_input("Medicine name", placeholder="e.g. Paracetamol, Metformin, Amoxicillin...", key="med")
        if st.button("🔍  Search", key="med_go"):
            if not med.strip():
                st.error("Enter a medicine name")
            else:
                with st.spinner("Fetching information..."):
                    resp = api_post("/medicine/info", {"medicine_name": med.strip()}, auth=True)
                if "error" not in resp:
                    st.session_state.med_info = resp
                else:
                    st.error(resp["error"])
    with ct:
        st.markdown("""
        <div style="background:#111;border:1px solid #1a1a1a;border-left:2px solid #22c55e;
                    border-radius:0 10px 10px 0;padding:18px">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:#22c55e;margin-bottom:10px">You'll get</div>
            <div style="font-size:12px;color:#555;line-height:2">
                ✓ Uses & dosage<br>✓ Side effects<br>✓ Drug interactions<br>
                ✓ Indian brand names<br>✓ Precautions
            </div>
        </div>""", unsafe_allow_html=True)

    if st.session_state.med_info:
        info = st.session_state.med_info
        st.markdown("<div style='height:28px;border-top:1px solid #1a1a1a;margin-top:24px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-bottom:18px">
            <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;
                        color:#e8e6e1;margin-bottom:4px">{info.get('name', med)}</div>
            <div style="font-size:13px;color:#555">{info.get('category','')}</div>
        </div>""", unsafe_allow_html=True)

        brands = info.get("brand_names_india",[])
        if brands:
            b_html = "".join([f'<span style="background:#1a1a1a;color:#e8e6e1;padding:4px 12px;border-radius:20px;font-size:12px;border:1px solid #2a2a2a;margin-right:6px;display:inline-block;margin-bottom:6px">{b}</span>' for b in brands[:6]])
            st.markdown(f'<div style="margin-bottom:18px"><div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#333;margin-bottom:10px">Indian Brand Names</div>{b_html}</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="background:#111;border:1px solid #1a1a1a;border-left:2px solid #22c55e;border-radius:0 10px 10px 0;padding:22px;font-size:14px;line-height:1.8;color:#ccc;margin-bottom:18px">{info.get("information","")}</div>', unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            uses = info.get("uses",[])
            if uses:
                u = "".join([f'<div style="padding:9px 0;border-bottom:1px solid #161616;font-size:13px;color:#e8e6e1"><span style="color:#22c55e;margin-right:8px">✓</span>{u}</div>' for u in uses])
                st.markdown(f'<div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:20px"><div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#333;margin-bottom:12px">Uses</div>{u}</div>', unsafe_allow_html=True)
        with c2:
            fx = info.get("side_effects",[])
            if fx:
                f_html = "".join([f'<div style="padding:9px 0;border-bottom:1px solid #161616;font-size:13px;color:#e8e6e1"><span style="color:#ef4444;margin-right:8px">·</span>{f}</div>' for f in fx])
                st.markdown(f'<div style="background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:20px"><div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#333;margin-bottom:12px">Side Effects</div>{f_html}</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="background:#1c1500;border:1px solid #3a2a00;border-radius:8px;padding:12px 16px;font-size:13px;color:#f59e0b;margin-top:14px">⚠️  {info.get("disclaimer","Always take medicines as prescribed by your doctor.")}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── History ────────────────────────────────────────────────────────────────────
def show_history():
    st.markdown('<div style="max-width:1080px;margin:0 auto;padding:44px 40px">', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:28px">
        <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;
                    color:#e8e6e1;letter-spacing:-0.02em;margin-bottom:6px">Health History</div>
        <div style="font-size:14px;color:#555">All your previous symptom checks and AI assessments</div>
    </div>
    """, unsafe_allow_html=True)

    history = api_get("/health/history")
    if isinstance(history, list) and history:
        for r in history[::-1]:
            risk = r.get("risk_level","low")
            rc = {"low":"#22c55e","medium":"#f59e0b","high":"#ef4444"}.get(risk,"#22c55e")
            rb = {"low":"#1a3a27","medium":"#3a2a10","high":"#3a1a1a"}.get(risk,"#1a3a27")
            date = str(r.get("created_at",""))[:10]
            preview = r.get("symptoms","")[:75]
            see_doc = r.get("see_doctor",False)
            with st.expander(f"{preview}{'...' if len(r.get('symptoms',''))>75 else ''}   ·   {date}"):
                c1,c2,c3 = st.columns(3)
                with c1: st.markdown(f'<span style="background:{rb};color:{rc};padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;text-transform:uppercase">{risk.upper()} RISK</span>', unsafe_allow_html=True)
                with c2: st.markdown(f'<span style="font-size:13px;color:{"#ef4444" if see_doc else "#22c55e"}">{"Doctor recommended" if see_doc else "No doctor needed"}</span>', unsafe_allow_html=True)
                with c3: st.markdown(f'<span style="font-size:13px;color:#555">Urgency: {r.get("urgency","Normal")}</span>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:#0d0d0d;border:1px solid #1a1a1a;border-left:2px solid #22c55e;border-radius:0 8px 8px 0;padding:18px;margin-top:14px;font-size:13px;line-height:1.8;color:#aaa">{r.get("analysis","No analysis available")}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#111;border:1px solid #1a1a1a;border-radius:12px;padding:60px;text-align:center">
            <div style="font-size:2.5rem;margin-bottom:12px">📋</div>
            <div style="font-size:14px;font-weight:600;color:#e8e6e1;margin-bottom:6px">No records yet</div>
            <div style="font-size:13px;color:#444">Your symptom checks will appear here</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        show_login()
    else:
        show_nav()
        p = st.session_state.page
        if p == "dashboard": show_dashboard()
        elif p == "symptoms": show_symptoms()
        elif p == "medicine": show_medicine()
        elif p == "history": show_history()

if __name__ == "__main__":
    main()
