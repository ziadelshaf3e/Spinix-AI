# ==============================
# Spinix AI v5 - FULL SYSTEM
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import hashlib

st.set_page_config(page_title="Spinix AI v5", layout="wide")

# ==============================
# 🔐 AUTH SYSTEM
# ==============================

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {
    "admin": {"password": hash_pass("1234"), "role": "Admin"},
    "coach": {"password": hash_pass("1234"), "role": "Coach"},
    "doctor": {"password": hash_pass("1234"), "role": "Doctor"}
}

if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("Spinix AI Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and USERS[u]["password"] == hash_pass(p):
            st.session_state.login = True
            st.session_state.role = USERS[u]["role"]
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
body {background:#0b0f14;color:#00ffcc;}
.card {
background:linear-gradient(145deg,#111,#0b0f14);
padding:20px;border-radius:15px;
border:1px solid rgba(0,255,200,0.2);
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

file = st.sidebar.file_uploader("Upload CSV")

if file:
    raw = pd.read_csv(file, encoding='utf-8-sig')

    st.sidebar.write("Column Mapping")

    mapping = {}
    for c in raw.columns:
        mapping[c] = st.sidebar.selectbox(c,
            ["Ignore","Date","Player","Workload","RPE","Sleep","Heart Rate","Fatigue"])

    df = pd.DataFrame()
    for k,v in mapping.items():
        if v!="Ignore":
            df[v]=raw[k]

    df['Date'] = pd.to_datetime(df['Date'])
    save(df)

else:
    df = load()

if df is None:
    st.stop()

# ==============================
# 👤 PLAYER SELECT
# ==============================

player = st.selectbox("Select Player", df['Player'].unique())
df = df[df['Player']==player]

# ==============================
# 🧠 AI ENGINE
# ==============================

df['Acute'] = df['Workload'].rolling(7).sum()
df['Chronic'] = df['Workload'].rolling(28).sum()
df['ACWR'] = df['Acute'] / df['Chronic']
df['Cumulative'] = df['Workload'].cumsum()

df['Fatigue Index'] = (
0.4*df['RPE'] + 0.3*df['ACWR'] + 0.3*(10-df['Sleep'])
)

df['Performance'] = (
0.5*df['Workload'] + 0.3*df['RPE'] + 0.2*df['Sleep']
)

df['Injury'] = ((df['ACWR']>1.3)|(df['Fatigue']>7)).astype(int)

ml = df.dropna()

features = ['ACWR','RPE','Sleep','Heart Rate','Fatigue']

model = RandomForestClassifier()
# تنظيف الداتا قبل ما الـ AI يلمسها
        ml = df_input.dropna(subset=['Workload', 'RPE', 'Sleep', 'Injury'])
        
        # التأكد إن فيه داتا كافية
        if not ml.empty:
            features = ['Workload', 'RPE', 'Sleep']
            model = RandomForestClassifier()
            model.fit(ml[features], ml['Injury'])
            
            # التوقع للاعب المختار
            latest_data = df_player.iloc[-1:]
            prediction = model.predict(latest_data[features])[0]
            
            if prediction == 1:
                st.error(f"⚠️ Spinix AI Warning: High Injury Risk for {player_name}")
            else:
                st.success(f"✅ Spinix AI Status: {player_name} is Fit")
latest = df.iloc[-1]
risk = model.predict_proba([latest[features]])[0][1]

# ==============================
# 🧍 INJURY TYPE
# ==============================

def injury_type(r):
    if r['Fatigue']>8: return "Hamstring"
    elif r['ACWR']>1.5: return "ACL"
    else: return "Fatigue"

inj = injury_type(latest)

# ==============================
# 🧍 3D BODY
# ==============================

def body():
    fig = go.Figure()

    color = "green"
    if risk>0.7: color="red"
    elif risk>0.4: color="orange"

    fig.add_trace(go.Scatter3d(
        x=[0],y=[0],z=[0],
        mode='markers',
        marker=dict(size=20,color=color)
    ))

    fig.update_layout(
        paper_bgcolor="#0b0f14",
        scene=dict(bgcolor="#0b0f14")
    )
    return fig

# ==============================
# 📡 LIVE DATA (SIMULATION)
# ==============================

df['Distance'] = df['Workload']*0.8
df['Sprints'] = df['RPE']*2

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
    high = (df['ACWR']>1.3).sum()

    if high>=3:
        st.error("🚨 Squad Overload")

# CENTER
with col2:
    st.markdown("### Injury Map")
    st.plotly_chart(body(),use_container_width=True)

    st.write(f"Risk: {risk*100:.1f}%")
    st.write(f"Injury: {inj}")

# RIGHT
with col3:
    st.markdown("### Market & ROI")

    value = latest['Performance']*120000
    st.metric("Value",f"${value:,.0f}")
    st.metric("Saved",f"${saved:,.0f}")

# ==============================
# 📉 CHARTS
# ==============================

st.line_chart(df[['ACWR']])
st.line_chart(df[['Performance']])

# ==============================
# 🤖 RECOMMENDATION
# ==============================

if risk>0.7:
    st.error("FULL REST")
elif risk>0.4:
    st.warning("REDUCE LOAD")
else:
    st.success("OK")

# ==============================
# 📄 FOOTER
# ==============================

st.markdown("---")
st.markdown("Spinix AI v5 - Elite System")
