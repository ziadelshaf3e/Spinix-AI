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
# 🧠 AI ENGINE INITIALIZATION
# ==========================================
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
except Exception as e:
    st.sidebar.warning("AI Video Module is Offline. Check requirements.txt")

# ==========================================
# 🎨 UI & STYLING
# ==========================================
st.set_page_config(page_title="Spinix AI Ultra v10.1", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; }
    .stButton>button { background-color: #238636; color: white; border-radius: 6px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 SECURE LOGIN
# ==========================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🛡️ Spinix AI Secure Gateway</h1>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,1.5,1])
    with col_c:
        u_in = st.text_input("User ID")
        p_in = st.text_input("Access Key", type="password")
        if st.button("Unlock Dashboard"):
            if u_in == "Dr. Ziad Elshafei" and p_in == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# ==========================================
# 💾 DATABASE & DIVERSE SQUAD DATA
# ==========================================
conn = sqlite3.connect("spinix_ultra_final.db", check_same_thread=False)

def get_squad_data():
    try:
        return pd.read_sql("SELECT * FROM squad_v10", conn)
    except:
        # داتا متباينة ضخمة (رجالة/ستات - مستويات مختلفة)
        squad = {
            "Date": pd.to_datetime(["2026-04-02"]*12),
            "Player": ["Ziad (Elite)", "Mohamed (Overtrained)", "Sara (Optimal)", "Tarek (Injury Risk)", 
                       "Nour (Pro)", "Ahmed (Fatigued)", "Layla (Recovery)", "Mona (Caution)", 
                       "Omar (Stable)", "Yasmine (Fresh)", "Hassan (Weak)", "Mariam (Elite)"],
            "Gender": ["Male", "Male", "Female", "Male", "Female", "Male", "Female", "Female", "Male", "Female", "Male", "Female"],
            "Workload": [750, 1350, 420, 1180, 500, 990, 310, 680, 590, 240, 860, 415],
            "RPE": [7, 10, 5, 10, 6, 9, 3, 8, 6, 2, 9, 4],
            "Sleep": [8, 4, 9, 3, 7, 5, 9, 5, 7, 9, 5, 8],
            "HRV": [82, 38, 92, 33, 84, 46, 96, 60, 71, 99, 54, 89]
        }
        df_db = pd.DataFrame(squad)
        df_db.to_sql("squad_v10", conn, if_exists="replace", index=False)
        return df_db

# ==========================================
# 📂 DATA HANDLING
# ==========================================
df = get_squad_data()
st.sidebar.title(f"👨‍⚕️ Dr. Ziad Elshafei")
st.sidebar.markdown("---")

up = st.sidebar.file_uploader("Sync CSV Data", type="csv")
if up:
    pd.read_csv(up).to_sql("squad_v10", conn, if_exists="replace", index=False)
    st.sidebar.success("Cloud Updated")

selected = st.sidebar.selectbox("Active Profile", df['Player'].unique())
p_df = df[df['Player'] == selected].copy()
p_df['Date'] = pd.to_datetime(p_df['Date'])

# AI Calculation
p_df['Acute'] = p_df['Workload'].rolling(7, 1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(28, 1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, 1)

# ==========================================
# 🏟️ MAIN DASHBOARD
# ==========================================
st.title(f"🚀 Spinix AI Hub | {selected}")

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
risk_idx = (p_df['Workload'].iloc[-1] / 1000) * (10 / p_df['Sleep'].iloc[-1])
m1.metric("Injury Risk Index", f"{min(risk_idx*10, 100):.1f}%")
m2.metric("ACWR Ratio", f"{p_df['ACWR'].iloc[-1]:.2f}")
m3.metric("Readiness Score", f"{int(100 - (risk_idx*5))}%")
m4.metric("Group", p_df['Gender'].iloc[0])

st.divider()

t_stats, t_bio, t_roi = st.tabs(["📉 Squad Analytics", "🦴 AI Biomechanics", "💰 Business ROI"])

with t_stats:
    st.subheader("Squad Load Comparison (Male vs Female)")
    fig_b = px.bar(df, x='Player', y='Workload', color='Gender', 
                   color_discrete_map={"Male": "#58a6ff", "Female": "#ff7b72"}, template="plotly_dark")
    st.plotly_chart(fig_b, use_container_width=True)

with t_bio:
    if pose_engine is None:
        st.error("AI Engine Offline.")
    else:
        v_in = st.file_uploader("Upload Video", type=['mp4', 'mov'])
        if v_in:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(v_in.read())
            cap = cv2.VideoCapture(tfile.name)
            ret, frame = cap.read()
            if ret:
                f_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose_engine.process(f_rgb)
                if res.pose_landmarks:
                    mp_drawing.draw_landmarks(f_rgb, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                st.image(f_rgb, use_container_width=True)
            cap.release()

with t_roi:
    st.subheader("Clinic & Brand Growth")
    st.metric("Revenue Saved (Prevention)", f"${int(risk_idx*1500)}")
    st.metric("SPX Brand Reach", "28.5k Users", "+12%")

# --- DECISION BLOCK (FIXED SYNTAX) ---
st.divider()
if risk_idx > 1.5:
    st.error(f"🛑 CRITICAL: {selected} is at extreme risk. Stop training immediately.")
elif risk_idx > 0.8:
    st.warning(f"⚠️ CAUTION: {selected} is showing signs of overtraining.")
else:
    st.success(f"🟢 CLEAR: {selected} is fit for elite performance.")

st.caption("Spinix AI Ultimate v10.1 | Dr. Ziad Elshafei")
else:
    st.success(f"🟢 CLEAR: {player} is in optimal condition. READY for full training load and match intensity.")

st.caption(f"Spinix AI Ultimate v9.0 | Designed for Dr. Ziad Elshafei | Last System Check: {datetime.now().strftime('%H:%M:%S')}")
