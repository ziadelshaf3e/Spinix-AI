# ==============================
# Spinix AI v6.5 FULL SYSTEM
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import hashlib

st.set_page_config(page_title="Spinix AI v6.5", layout="wide")

# ==============================
# 🔐 AUTH SYSTEM
# ==============================

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {
    "admin": {"password": hash_pass("1234"), "role": "Admin"},
    "doctor": {"password": hash_pass("1234"), "role": "Doctor"}
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
# 🎨 UI STYLE
# ==============================

st.markdown("""
<style>
body {background:#0b0f14;color:#e0e0e0;}
.stMetric {background:#161b22;padding:15px;border-radius:10px;border:1px solid #00ffcc33;}
h1,h2,h3 {color:#00ffcc;}
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

    st.sidebar.write("Column Mapping")

    mapping = {}
    options = ["Ignore","Date","Player","Workload","RPE","Sleep","Heart Rate","Fatigue"]

    for c in raw.columns:
        mapping[c] = st.sidebar.selectbox(f"{c}", options)

    df_new = pd.DataFrame()

    for k,v in mapping.items():
        if v!="Ignore":
            df_new[v]=raw[k]

    if not df_new.empty:
        save(df_new)
        st.success("Data Saved")

df = load()

if df is None:
    st.stop()

# ==============================
# ✅ VALIDATION
# ==============================

required = ['Player','Workload','RPE','Sleep']
for col in required:
    if col not in df.columns:
        st.error(f"Missing column: {col}")
        st.stop()

# ترتيب التاريخ
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date')

# ==============================
# 👤 PLAYER SELECT
# ==============================

player = st.selectbox("Select Player", df['Player'].dropna().unique())
pdf = df[df['Player']==player].copy()

# ==============================
# 🧠 AI ENGINE
# ==============================

pdf['Acute'] = pdf['Workload'].rolling(7, min_periods=1).mean()
pdf['Chronic'] = pdf['Workload'].rolling(28, min_periods=1).mean()

pdf['ACWR'] = np.where(pdf['Chronic']>0, pdf['Acute']/pdf['Chronic'],0)

pdf['Fatigue Index'] = (
0.4*pdf['RPE'] + 0.3*pdf['ACWR'] + 0.3*(10-pdf['Sleep'])
)

pdf['Performance'] = (
0.5*pdf['Workload'] + 0.3*pdf['RPE'] + 0.2*pdf['Sleep']
)

pdf['Injury'] = (
(pdf['ACWR']>1.3) | (pdf['RPE']>8) | (pdf['Sleep']<6)
).astype(int)

train = pdf.dropna()

risk = 0.3

if len(train)>5:
    try:
        model = RandomForestClassifier(n_estimators=100)
        model.fit(train[['Workload','RPE','Sleep']], train['Injury'])

        latest = pdf[['Workload','RPE','Sleep']].dropna().iloc[-1:]
        risk = model.predict_proba(latest)[0][1]
    except:
        risk = 0.5

# ==============================
# 🎯 COLOR
# ==============================

if risk>0.7:
    color="#ff4d4d"
elif risk>0.4:
    color="#ffaa00"
else:
    color="#00ffcc"

# ==============================
# 🧍 BODY MAP
# ==============================

def body():
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=[0,0],y=[0,2],mode='lines',line=dict(color="white")))
    fig.add_trace(go.Scatter(x=[0],y=[2],mode='markers',marker=dict(size=15,color="white")))

    fig.add_trace(go.Scatter(x=[0],y=[1],mode='markers',
        marker=dict(size=40,color=color,opacity=0.6)))

    fig.update_layout(height=300,paper_bgcolor="#0b0f14",
                      xaxis=dict(visible=False),yaxis=dict(visible=False))
    return fig

# ==============================
# 📡 LIVE TRACKING (SIM)
# ==============================

pdf['Distance'] = pdf['Workload']*0.8
pdf['Sprints'] = pdf['RPE']*2

# ==============================
# 💰 ROI
# ==============================

salary = st.sidebar.number_input("Daily Salary",1000)
days = st.sidebar.number_input("Days Saved",5)

saved = salary*days*(1-risk)

# ==============================
# 📊 LAYOUT
# ==============================

col1,col2,col3 = st.columns([1,2,1])

# LEFT
with col1:
    st.markdown("### Squad Alerts")

    high = (pdf['ACWR']>1.3).sum()

    if high>=3:
        st.error("🚨 Squad Overload")
    else:
        st.success("Squad OK")

    st.metric("Risk", f"{risk*100:.1f}%")

# CENTER
with col2:
    st.markdown("### Injury Map")
    st.plotly_chart(body(),use_container_width=True)

# RIGHT
with col3:
    st.markdown("### Market & ROI")

    value = pdf['Performance'].iloc[-1]*120000
    st.metric("Value", f"${value:,.0f}")
    st.metric("Saved", f"${saved:,.0f}")

# ==============================
# 📉 CHARTS
# ==============================

st.markdown("### Workload")
st.line_chart(pdf['Workload'])

st.markdown("### ACWR")
st.line_chart(pdf['ACWR'])

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
st.caption("Spinix AI v6.5 | Elite System")round:#1a1f2b;">, use_container_width=True)
