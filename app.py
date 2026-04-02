import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import hashlib
import cv2
import tempfile
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="Spinix AI Elite", layout="wide")

# 2. موديول الذكاء الاصطناعي (حماية من الـ Errors)
pose_engine = None
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose_engine = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
except:
    st.sidebar.warning("AI Video Module Offline")

# 3. نظام التأمين
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Spinix Secure Login")
    u = st.text_input("User ID")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "Dr. Ziad Elshafei" and p == "1234":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# 4. قاعدة البيانات (داتا متباينة: رجالة وستات وحالات مختلفة)
conn = sqlite3.connect("spinix_v102.db", check_same_thread=False)
def get_data():
    try:
        return pd.read_sql("SELECT * FROM squad", conn)
    except:
        df_init = pd.DataFrame({
            "Date": pd.to_datetime(["2026-04-02"]*10),
            "Player": ["Ziad (Elite)", "Mohamed (Danger)", "Sara (Optimal)", "Tarek (Overload)", "Nour (Pro)", "Ahmed (Fatigue)", "Layla (Fit)", "Mona (Caution)", "Omar (Stable)", "Yasmine (Fresh)"],
            "Gender": ["Male", "Male", "Female", "Male", "Female", "Male", "Female", "Female", "Male", "Female"],
            "Workload": [750, 1300, 420, 1150, 500, 980, 320, 650, 580, 250],
            "RPE": [7, 10, 5, 10, 6, 9, 3, 8, 6, 2],
            "Sleep": [8, 4, 9, 3, 7, 5, 9, 5, 7, 9]
        })
        df_init.to_sql("squad", conn, if_exists="replace", index=False)
        return df_init

df = get_data()
st.sidebar.title(f"👨‍⚕️ Dr. Ziad")
player = st.sidebar.selectbox("Select Athlete", df['Player'].unique())
p_df = df[df['Player'] == player].copy()

# 5. حسابات الـ AI
risk_val = (p_df['Workload'].iloc[-1] / 1000) * (10 / p_df['Sleep'].iloc[-1])

# 6. الداشبورد
st.title(f"🚀 Spinix AI: {player}")
c1, c2, c3 = st.columns(3)
c1.metric("Injury Risk", f"{min(risk_val*10, 100):.1f}%")
c2.metric("Load Status", "High" if risk_val > 1 else "Normal")
c3.metric("Gender", p_df['Gender'].iloc[0])

tab1, tab2 = st.tabs(["📉 Analytics", "🦴 Biomechanics"])

with tab1:
    st.plotly_chart(px.bar(df, x='Player', y='Workload', color='Gender', template="plotly_dark"))

with tab2:
    v_file = st.file_uploader("Upload Video", type=['mp4', 'mov'])
    if v_file and pose_engine:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(v_file.read())
        cap = cv2.VideoCapture(tfile.name)
        ret, frame = cap.read()
        if ret:
            st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
        cap.release()

# 7. اتخاذ القرار (الجزء اللي كان بيعمل Error - تم إصلاحه)
st.divider()
if risk_val > 1.5:
    st.error(f"🛑 ALERT: {player} needs immediate rest.")
elif risk_val > 0.8:
    st.warning(f"⚠️ CAUTION: {player} is overreaching.")
else:
    st.success(f"🟢 CLEAR: {player} is ready.")

st.caption("Spinix AI v10.2 | Elite Dashboard")
else:
    st.success(f"🟢 CLEAR: {player} is in optimal condition. READY for full training load and match intensity.")

st.caption(f"Spinix AI Ultimate v9.0 | Designed for Dr. Ziad Elshafei | Last System Check: {datetime.now().strftime('%H:%M:%S')}")
