# ==========================================
# 🚀 SPINIX AI ULTIMATE CORE SYSTEM
# ==========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import requests
import json

st.set_page_config(layout="wide", page_title="Spinix AI ULTIMATE")

# ==========================================
# 🎨 UI
# ==========================================
st.markdown("""
<style>
body {background:#010409;color:#c9d1d9;}
.block {background:#0d1117;padding:20px;border-radius:15px;}
h1 {color:#58a6ff;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 AUTH (SaaS Ready)
# ==========================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Spinix AI Login")
    u = st.text_input("User")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()

    st.stop()

# ==========================================
# 📊 DATA (API READY)
# ==========================================
df = pd.DataFrame({
    "Player": ["Ziad","Ali","Omar","Sara"],
    "Workload": np.random.randint(300,1500,4),
    "RPE": np.random.randint(1,10,4),
    "Sleep": np.random.randint(3,10,4),
    "HRV": np.random.randint(20,100,4)
})

player = st.sidebar.selectbox("Player", df['Player'])
p = df[df['Player']==player].iloc[0]

# ==========================================
# 🤖 AI MODEL
# ==========================================
df['Injury'] = ((df['Workload']>1200)|(df['Sleep']<5)|(df['RPE']>8)).astype(int)

model = RandomForestClassifier()
model.fit(df[['Workload','RPE','Sleep','HRV']], df['Injury'])

risk = model.predict_proba([[p['Workload'],p['RPE'],p['Sleep'],p['HRV']]])[0][1]

# ==========================================
# 🧠 FATIGUE
# ==========================================
fatigue = 0.4*p['RPE'] + 0.3*(10-p['Sleep']) + 0.3*(100-p['HRV'])/10
readiness = max(0,100-fatigue*10)

# ==========================================
# 🧍 INJURY TYPE
# ==========================================
def injury_type(p):
    if p['HRV']<40: return "Hamstring"
    if p['Workload']>1300: return "ACL"
    if p['Sleep']<5: return "Fatigue"
    return "Fit"

inj = injury_type(p)

# ==========================================
# 🧍 3D BODY (ADVANCED)
# ==========================================
st.subheader("3D Body")

coords = {
    "Hamstring": (0,-1,0),
    "ACL": (0,-2,0),
    "Fatigue": (0,0,0),
    "Fit": (0,1,0)
}

x,y,z = coords[inj]

fig = go.Figure()

# skeleton
fig.add_trace(go.Scatter3d(x=[0,0],y=[2,-2],z=[0,0],mode='lines',line=dict(color='white',width=6)))

# injury
fig.add_trace(go.Scatter3d(x=[x],y=[y],z=[z],
mode='markers',marker=dict(size=20,color='red')))

fig.update_layout(height=400,paper_bgcolor="#010409",
scene=dict(xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False)))

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 📊 METRICS
# ==========================================
c1,c2,c3,c4 = st.columns(4)
c1.metric("Risk", f"{risk*100:.1f}%")
c2.metric("Fatigue", f"{fatigue:.1f}")
c3.metric("Readiness", f"{readiness:.0f}%")
c4.metric("Injury", inj)

# ==========================================
# 🧠 AI COACH (REAL API READY)
# ==========================================
st.subheader("AI Coach")

q = st.text_input("Ask Coach")

def coach(q):
    # لو عايز تربطه بـ OpenAI API حط هنا
    if "train" in q:
        return "No training" if risk>0.7 else "Light training"
    if "recover" in q:
        return "Sleep + hydration + physio"
    return f"Risk: {risk*100:.0f}% | Injury: {inj}"

if q:
    st.success(coach(q.lower()))

# ==========================================
# 📡 LIVE TRACK
# ==========================================
st.subheader("Live Match")

dist = np.random.randint(8000,11000)
sprint = np.random.randint(10,40)

st.metric("Distance", dist)
st.metric("Sprints", sprint)

# ==========================================
# 💰 ROI
# ==========================================
salary = 2000
days = int(risk*10)
saved = salary*days*(1-risk)

st.metric("Saved Money", f"${saved:.0f}")

# ==========================================
# 🌍 SaaS NOTE
# ==========================================
st.info("This system is SaaS-ready. Connect to API + Frontend for production.")

# ==========================================
# END
# ==========================================
st.caption("Spinix AI ULTIMATE CORE")
