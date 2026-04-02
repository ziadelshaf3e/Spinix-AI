import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
import hashlib
import cv2
import tempfile
from datetime import datetime

# ==========================================
# 🧠 AI BIOMECHANICS ENGINE (FIXED NameError)
# ==========================================
# بنعرفه كـ None في الأول عشان نتفادى الـ NameError
pose_engine = None
mp_drawing = None
mp_pose = None

try:
    import mediapipe as mp
    from mediapipe.python.solutions import pose as mp_p
    from mediapipe.python.solutions import drawing_utils as mp_d
    mp_pose = mp_p
    mp_drawing = mp_d
    pose_engine = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
except:
    try:
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        pose_engine = mp_pose.Pose()
    except Exception as e:
        st.sidebar.warning("⚠️ AI Video Engine Offline (Check requirements.txt)")

# ==========================================
# 🎨 UI & CSS
# ==========================================
st.set_page_config(page_title="Spinix AI Elite v9.5", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0b1117; color: #e6edf3; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 LOGIN
# ==========================================
if "login" not in st.session_state: st.session_state.login = False
if not st.session_state.login:
    u = st.text_input("User ID")
    p = st.text_input("Access Key", type="password")
    if st.button("Unlock"):
        if u == "Dr. Ziad Elshafei" and p == "1234":
            st.session_state.login = True
            st.rerun()
    st.stop()

# ==========================================
# 💾 DATABASE (With Diverse Dummy Data)
# ==========================================
conn = sqlite3.connect("spinix_v95.db", check_same_thread=False)

def get_diverse_data():
    try: return pd.read_sql("SELECT * FROM data", conn)
    except:
        # داتا متباينة (الرجالة والستات والحالات المختلفة)
        data = {
            "Date": pd.to_datetime(["2026-04-01"]*10),
            "Player": ["Ziad (Elite)", "Mohamed (Bad)", "Sara (Good)", "Tarek (Danger)", "Nour (Pro)", 
                       "Ahmed (Weak)", "Layla (Fit)", "Mona (Fatigue)", "Omar (Stable)", "Yasmine (Fresh)"],
            "Gender": ["Male", "Male", "Female", "Male", "Female", "Male", "Female", "Female", "Male", "Female"],
            "Workload": [700, 1200, 450, 1100, 500, 950, 350, 600, 550, 200],
            "RPE": [7, 10, 5, 10, 6, 9, 4, 8, 6, 2],
            "Sleep": [8, 4, 8, 4, 7, 5, 9, 5, 7, 9],
            "HRV": [75, 45, 85, 40, 80, 50, 90, 60, 70, 95]
        }
        df_init = pd.DataFrame(data)
        df_init.to_sql("data", conn, if_exists="replace", index=False)
        return df_init

# ==========================================
# 📂 DATA LOADING
# ==========================================
df = get_diverse_data()
player = st.sidebar.selectbox("Select Athlete Profile", df['Player'].unique())
p_df = df[df['Player'] == player].copy()
p_df['Date'] = pd.to_datetime(p_df['Date'])

# الحسابات
p_df['Acute'] = p_df['Workload'].rolling(7, 1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(28, 1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, 1)

# ==========================================
# 🏟️ DASHBOARD
# ==========================================
st.title(f"🚀 Spinix Pro: {player} ({p_df['Gender'].iloc[0]})")

c1, c2, c3 = st.columns(3)
risk = (p_df['Workload'].iloc[-1] / 1200) * (10 / p_df['Sleep'].iloc[-1])
c1.metric("Injury Risk Index", f"{min(risk*10, 100):.1f}%")
c2.metric("ACWR Ratio", f"{p_df['ACWR'].iloc[-1]:.2f}")
c3.metric("Gender-Specific Load", p_df['Gender'].iloc[0])

tab1, tab2 = st.tabs(["📊 Performance Stats", "🦴 AI Biomechanics"])

with tab1:
    st.plotly_chart(px.bar(df, x='Player', y='Workload', color='Gender', title="Squad Load Comparison (Male vs Female)"))
    st.plotly_chart(px.line(p_df, x='Date', y='Workload', title="Personal Load Trend"))

with tab2:
    if pose_engine is None:
        st.error("AI Engine is offline. Check server logs.")
    else:
        v_file = st.file_uploader("Upload Movement Video", type=['mp4', 'mov'])
        if v_file:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(v_file.read())
            cap = cv2.VideoCapture(tfile.name)
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose_engine.process(frame_rgb)
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(frame_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                st.image(frame_rgb, use_container_width=True)

# Decision Support
st.divider()
if risk > 1.5:
    st.error(f"🚨 CRITICAL ALERT: {player} needs immediate rest.")
elif risk > 0.8:
    st.warning(f"⚠️ CAUTION: {player} is overreaching.")
else:
    st.success(f"🟢 CLEAR: {player} is ready for Elite performance.")
else:
    st.success(f"🟢 CLEAR: {player} is in optimal condition. READY for full training load and match intensity.")

st.caption(f"Spinix AI Ultimate v9.0 | Designed for Dr. Ziad Elshafei | Last System Check: {datetime.now().strftime('%H:%M:%S')}")
