import streamlit as st
import requests
import json
from datetime import datetime
import random

st.set_page_config(
    page_title="HealthBridge",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = "http://localhost:8000"

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "medicine_info" not in st.session_state:
    st.session_state.medicine_info = None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600&display=swap');
:root {
    --bg:#f8f6f1;--surface:#ffffff;--surface2:#f2efe8;--border:#e8e2d9;
    --text:#1a1814;--text2:#6b6560;--text3:#9b958e;
    --accent:#2d6a4f;--accent2:#52b788;--accent-bg:#d8f3dc;
    --red:#c1121f;--red-bg:#ffe0e0;--amber:#b45309;--amber-bg:#fef3c7;
}
*{margin:0;padding:0;box-sizing:border-box;}
html,body,.stApp{background:var(--bg)!important;font-family:'Geist',sans-serif!important;color:var(--text)!important;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
.hb-nav{display:flex;align-items:center;justify-content:space-between;padding:18px 48px;background:var(--surface);border-bottom:1px solid var(--border);}
.hb-logo{font-family:'Instrument Serif',serif;font-size:1.5rem;color:var(--text);letter-spacing:-0.02em;}
.hb-logo span{color:var(--accent);}
.hb-avatar{width:36px;height:36px;border-radius:50%;background:var(--accent);color:white;display:inline-flex;align-items:center;justify-content:center;font-weight:600;font-size:0.875rem;}
.hb-page{max-width:1100px;margin:0 auto;padding:40px 48px;}
.hb-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:28px;margin-bottom:16px;}
.hb-card-sm{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:10px;}
.hb-stat{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px;}
.hb-stat-num{font-family:'Instrument Serif',serif;font-size:2.5rem;color:var(--text);line-height:1;margin-bottom:4px;}
.hb-stat-label{font-size:0.75rem;font-weight:500;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;}
.hb-section-title{font-family:'Instrument Serif',serif;font-size:1.75rem;color:var(--text);margin-bottom:6px;letter-spacing:-0.02em;}
.hb-section-sub{font-size:0.9rem;color:var(--text2);margin-bottom:28px;}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;}
.badge-low{background:var(--accent-bg);color:var(--accent);}
.badge-medium{background:var(--amber-bg);color:var(--amber);}
.badge-high{background:var(--red-bg);color:var(--red);}
.stButton>button{background:var(--text)!important;color:white!important;border:none!important;border-radius:10px!important;padding:12px 24px!important;font-family:'Geist',sans-serif!important;font-size:0.875rem!important;font-weight:500!important;width:100%!important;transition:all 0.15s!important;}
.stButton>button:hover{background:#2d2a26!important;transform:translateY(-1px)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;font-family:'Geist',sans-serif!important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(45,106,79,0.1)!important;}
.stSelectbox>div>div{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:10px!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface2)!important;border-radius:10px!important;padding:4px!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;border-radius:8px!important;color:var(--text2)!important;font-family:'Geist',sans-serif!important;font-weight:500!important;}
.stTabs [aria-selected="true"]{background:var(--surface)!important;color:var(--text)!important;box-shadow:0 1px 4px rgba(0,0,0,0.08)!important;}
.stExpander{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important;margin-bottom:10px!important;}
.hb-alert{padding:14px 18px;border-radius:10px;font-size:0.875rem;margin-bottom:20px;}
.hb-alert-warning{background:var(--amber-bg);color:var(--amber);border:1px solid #fcd34d;}
.hb-ai-response{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:0 12px 12px 0;padding:24px;font-size:0.9rem;line-height:1.8;color:var(--text);}
.hb-divider{height:1px;background:var(--border);margin:28px 0;}
.hb-empty{text-align:center;padding:60px 20px;color:var(--text3);}
.stMultiSelect>div{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:10px!important;}
.stTextInput label,.stTextArea label,.stNumberInput label,.stSelectbox label,.stMultiSelect label{font-size:0.75rem!important;font-weight:600!important;color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:0.06em!important;}
</style>
""", unsafe_allow_html=True)

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

def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;margin:60px 0 40px">
            <div style="font-family:'Instrument Serif',serif;font-size:3rem;color:#1a1814;letter-spacing:-0.03em">
                Health<span style="color:#2d6a4f">Bridge</span>
            </div>
            <div style="font-size:0.9rem;color:#9b958e;margin-top:8px">Your intelligent health companion</div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign in", "Create account"])

        with tab1:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            email = st.text_input("Email address", key="li_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="li_pass", placeholder="••••••••")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Sign in →", key="login_btn"):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    with st.spinner(""):
                        resp = api_post("/auth/login", {"email": email, "password": password})
                    if "access_token" in resp:
                        st.session_state.token = resp["access_token"]
                        st.session_state.user = {"email": email, "name": resp.get("name", email)}
                        st.rerun()
                    else:
                        st.error(resp.get("detail", "Invalid credentials"))

        with tab2:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            name = st.text_input("Full name", key="reg_name", placeholder="Your name")
            email2 = st.text_input("Email address", key="reg_email", placeholder="you@example.com")
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", min_value=1, max_value=120, value=25, key="reg_age")
            with c2:
                st.selectbox("Gender", ["Male", "Female", "Other"], key="reg_gender")
            password2 = st.text_input("Password", type="password", key="reg_pass", placeholder="Min. 6 characters")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Create account →", key="reg_btn"):
                with st.spinner(""):
                    resp = api_post("/auth/register", {"name": name, "email": email2, "password": password2, "age": age})
                if "id" in resp:
                    st.success("Account created! Please sign in.")
                else:
                    st.error(resp.get("detail", "Registration failed"))

        st.markdown("""
        <div style="text-align:center;margin-top:32px;padding-top:24px;border-top:1px solid #e8e2d9;font-size:0.8rem;color:#9b958e">
            ⚕️ For informational purposes only. Not a substitute for medical advice.
        </div>
        """, unsafe_allow_html=True)

def show_nav():
    name = st.session_state.user.get("name", "User")
    initial = name[0].upper()
    pages = {"dashboard": "Overview", "symptoms": "Symptom Check", "medicine": "Medicines", "history": "History"}
    links = ""
    for pg, label in pages.items():
        active_style = "background:#f2efe8;color:#1a1814;" if st.session_state.page == pg else ""
        links += f'<span style="padding:8px 16px;border-radius:8px;font-size:0.875rem;font-weight:500;color:#6b6560;{active_style}">{label}</span>'
    st.markdown(f"""
    <div class="hb-nav">
        <div class="hb-logo">Health<span>Bridge</span></div>
        <div style="display:flex;gap:4px">{links}</div>
        <div style="display:flex;align-items:center;gap:12px">
            <span style="font-size:0.875rem;color:#6b6560">{name}</span>
            <div class="hb-avatar">{initial}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    nav_cols = st.columns([1,1,1,1,5,1])
    for i, (pg, label) in enumerate(pages.items()):
        with nav_cols[i]:
            if st.button(label, key=f"nav_{pg}"):
                st.session_state.page = pg; st.rerun()
    with nav_cols[5]:
        if st.button("Sign out", key="logout"):
            st.session_state.token = None; st.session_state.user = None; st.rerun()

def show_dashboard():
    st.markdown('<div class="hb-page">', unsafe_allow_html=True)
    name = st.session_state.user.get("name", "there").split()[0]
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    st.markdown(f"""
    <div style="margin-bottom:36px">
        <div style="font-family:'Instrument Serif',serif;font-size:2.2rem;color:#1a1814;letter-spacing:-0.02em">{greeting}, {name} ✦</div>
        <div style="font-size:0.95rem;color:#6b6560;margin-top:6px">Here's a summary of your health activity</div>
    </div>
    """, unsafe_allow_html=True)
    history = api_get("/health/history")
    records = history if isinstance(history, list) else []
    med_count = api_get("/medicine/count").get("count", 0)
    high_risk = sum(1 for r in records if r.get("risk_level") == "high")
    c1,c2,c3,c4 = st.columns(4)
    for col,(num,label,icon) in zip([c1,c2,c3,c4],[(str(len(records)),"Total checks","🔍"),(str(med_count),"Medicines looked up","💊"),(str(high_risk),"High risk flags","⚠️"),("Active","Account status","✓")]):
        with col:
            st.markdown(f'<div class="hb-stat"><div style="font-size:1.4rem;margin-bottom:12px">{icon}</div><div class="hb-stat-num">{num}</div><div class="hb-stat-label">{label}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="hb-divider"></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([2,1])
    with col_l:
        st.markdown('<div style="font-family:\'Instrument Serif\',serif;font-size:1.3rem;color:#1a1814;margin-bottom:16px">Recent activity</div>', unsafe_allow_html=True)
        if records:
            for r in records[-4:][::-1]:
                risk = r.get("risk_level","low")
                st.markdown(f'<div class="hb-card-sm" style="display:flex;justify-content:space-between;align-items:center"><div><div style="font-size:0.875rem;font-weight:500;color:#1a1814;margin-bottom:4px">{r.get("symptoms","")[:70]}...</div><div style="font-size:0.8rem;color:#9b958e">{str(r.get("created_at",""))[:10]}</div></div><span class="badge badge-{risk}">{risk}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="hb-empty"><div style="font-size:2rem;margin-bottom:8px">🩺</div><div>No health checks yet</div></div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div style="font-family:\'Instrument Serif\',serif;font-size:1.3rem;color:#1a1814;margin-bottom:16px">Quick actions</div>', unsafe_allow_html=True)
        if st.button("Check symptoms →"): st.session_state.page="symptoms"; st.rerun()
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Look up medicine →"): st.session_state.page="medicine"; st.rerun()
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("View history →"): st.session_state.page="history"; st.rerun()
        tips = [("💧","Stay hydrated","Aim for 8 glasses of water daily."),("😴","Prioritize sleep","7–9 hours supports immune function."),("🚶","Move daily","A 20-min walk improves heart health."),("🥗","Eat the rainbow","Colorful veg provide key micronutrients.")]
        tip = tips[datetime.now().day % 4]
        st.markdown(f'<div class="hb-card" style="margin-top:20px;border-left:3px solid #2d6a4f"><div style="font-size:1.4rem;margin-bottom:8px">{tip[0]}</div><div style="font-size:0.875rem;font-weight:600;color:#1a1814;margin-bottom:4px">{tip[1]}</div><div style="font-size:0.825rem;color:#6b6560;line-height:1.5">{tip[2]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_symptoms():
    st.markdown('<div class="hb-page">', unsafe_allow_html=True)
    st.markdown('<div class="hb-section-title">Symptom checker</div><div class="hb-section-sub">Describe your symptoms and get an AI-powered assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="hb-alert hb-alert-warning">⚠️  This tool is for informational purposes only. Always consult a licensed physician for medical decisions.</div>', unsafe_allow_html=True)
    col_f, col_i = st.columns([3,1])
    with col_f:
        symptoms = st.text_area("Describe your symptoms in detail", height=130, placeholder="e.g. I've had a persistent headache for 2 days, mild fever around 99°F...", key="symptom_input")
        c1,c2,c3 = st.columns(3)
        with c1: age = st.number_input("Age", min_value=1, max_value=120, value=25, key="s_age")
        with c2: gender = st.selectbox("Gender", ["Male","Female","Other"], key="s_gender")
        with c3: duration = st.selectbox("Duration", ["< 1 day","1–3 days","4–7 days","> 1 week"], key="s_dur")
        existing = st.multiselect("Pre-existing conditions", ["Diabetes","Hypertension","Asthma","Heart Disease","None"], default=["None"], key="s_existing")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        if st.button("Analyze symptoms →", key="analyze_btn"):
            if not symptoms.strip():
                st.error("Please describe your symptoms.")
            else:
                with st.spinner("Analyzing..."):
                    resp = api_post("/symptom/analyze", {"symptoms": symptoms,"age": age,"gender": gender,"duration": duration,"existing_conditions": [e for e in existing if e != "None"]}, auth=True)
                if "error" not in resp:
                    st.session_state.last_analysis = resp
                else:
                    st.error(f"Analysis failed: {resp['error']}")
    with col_i:
        st.markdown('<div class="hb-card"><div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#9b958e;margin-bottom:16px">How it works</div>' + "".join([f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px"><div style="width:24px;height:24px;border-radius:50%;background:#f2efe8;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;color:#2d6a4f;flex-shrink:0">{n}</div><div style="font-size:0.825rem;color:#6b6560;line-height:1.5">{t}</div></div>' for n,t in [("1","Describe your symptoms clearly"),("2","AI cross-references medical knowledge"),("3","Get risk assessment and guidance"),("4","Decide whether to see a doctor")]]) + '</div>', unsafe_allow_html=True)
    if st.session_state.last_analysis:
        r = st.session_state.last_analysis
        risk = r.get("risk_level","low")
        see_doc = r.get("see_doctor", False)
        st.markdown('<div class="hb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Instrument Serif\',serif;font-size:1.3rem;color:#1a1814;margin-bottom:20px">Analysis result</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="hb-stat"><div class="hb-stat-label" style="margin-bottom:10px">Risk level</div><span class="badge badge-{risk}">{risk.upper()}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="hb-stat"><div class="hb-stat-label" style="margin-bottom:10px">See a doctor</div><div style="font-size:1rem;font-weight:600;color:{"#c1121f" if see_doc else "#2d6a4f"}">{"Recommended" if see_doc else "Not urgent"}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="hb-stat"><div class="hb-stat-label" style="margin-bottom:10px">Urgency</div><div style="font-size:1rem;font-weight:600;color:#1a1814">{r.get("urgency","Normal")}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hb-ai-response" style="margin-top:20px">{r.get("analysis","")}</div>', unsafe_allow_html=True)
        conditions = r.get("possible_conditions", [])
        if conditions:
            st.markdown('<div style="font-size:0.875rem;font-weight:600;color:#1a1814;margin-top:24px;margin-bottom:12px">Possible conditions</div>', unsafe_allow_html=True)
            cols = st.columns(len(conditions[:3]))
            for i,cond in enumerate(conditions[:3]):
                prob = cond.get("probability","").lower()
                color = "#c1121f" if prob=="high" else "#b45309" if prob=="medium" else "#2d6a4f"
                with cols[i]:
                    st.markdown(f'<div class="hb-card-sm" style="text-align:center"><div style="font-size:0.875rem;font-weight:600;color:#1a1814;margin-bottom:6px">{cond.get("name","")}</div><div style="font-size:0.775rem;color:{color};font-weight:500">{cond.get("probability","")} probability</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_medicine():
    st.markdown('<div class="hb-page">', unsafe_allow_html=True)
    st.markdown('<div class="hb-section-title">Medicine information</div><div class="hb-section-sub">Look up any medicine for dosage, side effects, and precautions</div>', unsafe_allow_html=True)
    col_s, col_t = st.columns([2,1])
    with col_s:
        med_name = st.text_input("Medicine name", placeholder="e.g. Paracetamol, Metformin, Amoxicillin...", key="med_input")
        if st.button("Search →", key="med_btn"):
            if med_name.strip():
                with st.spinner("Fetching information..."):
                    resp = api_post("/medicine/info", {"medicine_name": med_name}, auth=True)
                if "error" not in resp:
                    st.session_state.medicine_info = resp
                else:
                    st.error(resp["error"])
    with col_t:
        st.markdown('<div class="hb-card-sm" style="border-left:3px solid #2d6a4f"><div style="font-size:0.8rem;font-weight:600;color:#2d6a4f;margin-bottom:8px">What you\'ll get</div><div style="font-size:0.825rem;color:#6b6560;line-height:1.9">✓ Uses & dosage<br>✓ Side effects<br>✓ Drug interactions<br>✓ Indian brand names<br>✓ Precautions</div></div>', unsafe_allow_html=True)
    if st.session_state.medicine_info:
        info = st.session_state.medicine_info
        st.markdown('<div class="hb-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-bottom:20px"><div style="font-family:\'Instrument Serif\',serif;font-size:1.5rem;color:#1a1814">{info.get("name", med_name)}</div><div style="font-size:0.875rem;color:#6b6560;margin-top:4px">{info.get("category","")}</div></div>', unsafe_allow_html=True)
        brands = info.get("brand_names_india", [])
        if brands:
            b_html = " ".join([f'<span style="background:#f2efe8;color:#1a1814;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:500;margin-right:6px">{b}</span>' for b in brands[:6]])
            st.markdown(f'<div style="margin-bottom:20px"><div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#9b958e;margin-bottom:10px">Indian brand names</div>{b_html}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hb-ai-response">{info.get("information","")}</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            uses = info.get("uses",[])
            if uses:
                u_html = "".join([f'<div style="padding:8px 0;border-bottom:1px solid #f2efe8;font-size:0.875rem;color:#1a1814">✓ {u}</div>' for u in uses])
                st.markdown(f'<div class="hb-card" style="margin-top:16px"><div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#9b958e;margin-bottom:12px">Uses</div>{u_html}</div>', unsafe_allow_html=True)
        with c2:
            effects = info.get("side_effects",[])
            if effects:
                e_html = "".join([f'<div style="padding:8px 0;border-bottom:1px solid #f2efe8;font-size:0.875rem;color:#1a1814">· {e}</div>' for e in effects])
                st.markdown(f'<div class="hb-card" style="margin-top:16px"><div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#9b958e;margin-bottom:12px">Side effects</div>{e_html}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hb-alert hb-alert-warning" style="margin-top:16px">⚠️ &nbsp;{info.get("disclaimer","Always take medicines as prescribed by your doctor.")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_history():
    st.markdown('<div class="hb-page">', unsafe_allow_html=True)
    st.markdown('<div class="hb-section-title">Health history</div><div class="hb-section-sub">All your previous symptom checks and assessments</div>', unsafe_allow_html=True)
    history = api_get("/health/history")
    if isinstance(history, list) and history:
        for record in history[::-1]:
            risk = record.get("risk_level","low")
            date = str(record.get("created_at",""))[:10]
            preview = record.get("symptoms","")[:80]
            with st.expander(f"{preview}{'...' if len(record.get('symptoms',''))>80 else ''}   —   {date}"):
                c1,c2,c3 = st.columns(3)
                with c1: st.markdown(f'<span class="badge badge-{risk}">{risk.upper()} RISK</span>', unsafe_allow_html=True)
                with c2:
                    see_doc = record.get("see_doctor",False)
                    st.markdown(f'<span style="font-size:0.875rem;color:{"#c1121f" if see_doc else "#2d6a4f"}">{"Doctor recommended" if see_doc else "No doctor needed"}</span>', unsafe_allow_html=True)
                with c3: st.markdown(f'<span style="font-size:0.875rem;color:#6b6560">Urgency: {record.get("urgency","Normal")}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="hb-ai-response" style="margin-top:16px">{record.get("analysis","No analysis available")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hb-empty"><div style="font-size:2.5rem;margin-bottom:12px">📋</div><div style="font-size:1rem;font-weight:500;color:#1a1814">No records yet</div><div style="font-size:0.875rem;color:#9b958e;margin-top:6px">Your symptom checks will appear here</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    if not st.session_state.token:
        show_login()
    else:
        show_nav()
        page = st.session_state.page
        if page == "dashboard": show_dashboard()
        elif page == "symptoms": show_symptoms()
        elif page == "medicine": show_medicine()
        elif page == "history": show_history()

if __name__ == "__main__":
    main()
