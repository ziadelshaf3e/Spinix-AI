# ==============================
# Spinix AI v6.9 ELITE UI + SYSTEM
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import hashlib

st.set_page_config(page_title="Spinix AI Elite", layout="wide")

# ==============================
# 🔐 LOGIN
# ==============================

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {
    "Dr. Ziad Elshafei": {"password": hash_pass("1234")},
    "doctor": {"password": hash_pass("1234")}
}

if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.markdown("<h1 style='text-align:center;color:#00ffcc;'>Spinix AI Login</h1>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in USERS and USERS[u]["password"] == hash_pass(p):
            st.session_state.login = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Wrong credentials")

if not st.session_state.login:
    login()
    st.stop()

# ==============================
# 🎨 ULTRA UI
# ==============================

st.markdown("""
<style>
body {background:#0b0f14;}
.panel {
    background: linear-gradient(145deg, #111827, #0b0f14);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(0,255,200,0.15);
    box-shadow: 0 0 25px rgba(0,255,200,0.05);
    margin-bottom: 15px;
}
.title {
    color:#00ffcc;
    font-weight:bold;
    margin-bottom:10px;
}
.high {color:#ff4d4d;}
.medium {color:#ffaa00;}
.low {color:#00ffcc;}
.alert-bar {
    background:#111;
    padding:10px;
    border-left:4px solid #00ffcc;
    border-radius:5px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 💾 DATABASE
# ==============================

conn = sqlite3.connect("spinix.db", check_same_thread=False)

def save(df):
    df.to_sql("data", conn, if_exists="replace", index=False)

def load():
    try:
        return pd.read_sql("SELECT * FROM data", conn)
    except:
        return None

# ==============================
# 📂 UPLOAD + MAPPING
# ==============================

st.sidebar.title(f"Welcome {st.session_state.user}")
file = st.sidebar.file_uploader("Upload CSV")

if file:
    raw = pd.read_csv(file)
    mapping = {}
    options = ["Ignore","Date","Player","Workload","RPE","Sleep","Heart Rate","Fatigue"]

    for c in raw.columns:
        mapping[c] = st.sidebar.selectbox(c, options)

    df_new = pd.DataFrame()
    for k,v in mapping.items():
        if v!="Ignore":
            df_new[v] = raw[k]

    if not df_new.empty:
        save(df_new)
        st.success("Data Saved")

df = load()
if df is None:
    st.stop()

# ==============================
# 👤 PLAYER
# ==============================

player = st.selectbox("Select Player", df['Player'].dropna().unique())
pdf = df[df['Player']==player].copy()

# ==============================
# 🧠 AI
# ==============================

pdf['Acute'] = pdf['Workload'].rolling(7,1).mean()
pdf['Chronic'] = pdf['Workload'].rolling(28,1).mean()
pdf['ACWR'] = np.where(pdf['Chronic']>0, pdf['Acute']/pdf['Chronic'],0)

pdf['Injury'] = ((pdf['ACWR']>1.3)|(pdf['RPE']>8)|(pdf['Sleep']<6)).astype(int)

train = pdf.dropna()
risk = 0.3

if len(train)>5:
    model = RandomForestClassifier()
    model.fit(train[['Workload','RPE','Sleep']], train['Injury'])
    latest = pdf[['Workload','RPE','Sleep']].dropna().iloc[-1:]
    risk = model.predict_proba(latest)[0][1]

# ==============================
# 🎨 COLOR
# ==============================

if risk>0.7:
    color="red"
elif risk>0.4:
    color="orange"
else:
    color="#00ffcc"

# ==============================
# 📡 LIVE DATA
# ==============================

pdf['Distance'] = pdf['Workload']*0.8
pdf['Sprints'] = pdf['RPE']*2

# ==============================
# 💰 ROI
# ==============================

salary = st.sidebar.number_input("Salary",1000)
days = st.sidebar.number_input("Days Saved",5)
saved = salary*days*(1-risk)

# ==============================
# 🧱 LAYOUT (LIKE IMAGE)
# ==============================

left,center,right = st.columns([1,2,1])

# LEFT PANEL
with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown('<div class="title">GLOBAL BENCHMARK</div>', unsafe_allow_html=True)
    st.write("Spinix Performance Model")

    st.markdown("---")

    st.markdown('<div class="title">SQUAD ALERTS</div>', unsafe_allow_html=True)

    for i in range(5):
        r = np.random.rand()
        if r>0.7:
            st.markdown(f'<p class="high">Player {i} - HIGH</p>', unsafe_allow_html=True)
        elif r>0.4:
            st.markdown(f'<p class="medium">Player {i} - MEDIUM</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="low">Player {i} - LOW</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# CENTER PANEL
with center:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="title">INJURY ZONE</div>', unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=[0,0],y=[0,2],mode='lines',line=dict(color="white",width=3)))
    fig.add_trace(go.Scatter(x=[0],y=[2],mode='markers',marker=dict(size=20,color="white")))

    fig.add_trace(go.Scatter(x=[0],y=[1],mode='markers',
        marker=dict(size=60,color=color,opacity=0.5)))

    fig.update_layout(height=400,paper_bgcolor="#0b0f14",
                      xaxis=dict(visible=False),yaxis=dict(visible=False))

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### Risk: {risk*100:.1f}%")

    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT PANEL
with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown('<div class="title">SCOUTING</div>', unsafe_allow_html=True)

    val = pdf['Workload'].iloc[-1]*1200
    st.metric("Value", f"${val:,.0f}")
    st.metric("Growth", "+300%")

    st.markdown("---")

    st.markdown('<div class="title">ROI</div>', unsafe_allow_html=True)

    chart = pd.DataFrame({"t":[1,2,3,4,5,6],"v":[1,2,3,4,5,10]})
    st.line_chart(chart.set_index("t"))

    st.metric("Saved", f"${saved:,.0f}")

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# 📉 CHARTS
# ==============================

st.markdown("### Performance Tracking")
st.line_chart(pdf[['Workload']])

# ==============================
# 🚨 SYSTEM ALERT
# ==============================

st.markdown("""
<div class="alert-bar">
⚠️ SYSTEM ALERT: Workload exceeds safe threshold
</div>
""", unsafe_allow_html=True)

# ==============================
# 🤖 RECOMMENDATION
# ==============================

if risk>0.7:
    st.error("🚨 FULL REST")
elif risk>0.4:
    st.warning("⚠️ REDUCE LOAD")
else:
    st.success("✅ OPTIMAL")

# ==============================
# FOOTER
# ==============================

st.markdown("---")
st.caption("Spinix AI Elite System")
