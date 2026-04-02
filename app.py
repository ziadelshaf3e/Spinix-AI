import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import cv2
import tempfile
from datetime import datetime

# ==========================================
# 🧠 1. AI BIOMECHANICS ENGINE (ULTRA STABLE)
# ==========================================
pose_engine = None
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose_engine = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
except:
    st.sidebar.warning("⚠️ AI Video Engine Offline (Check Cloud Dependencies)")

# ==========================================
# 🎨 2. ELITE UI & BRANDING (SPINIX DARK THEME)
# ==========================================
st.set_page_config(page_title="Spinix AI Masterpiece v12", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { background: linear-gradient(90deg, #238636, #2ea043); color: white; border-radius: 8px; font-weight: bold; border: none; }
    .status-card { padding: 20px; border-radius: 10px; border-left: 10px solid #58a6ff; background: #161b22; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 3. SECURE AUTHENTICATION (DR. ZIAD ONLY)
# ==========================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🛡️ SPINIX AI SECURE GATEWAY</h1>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,1.5,1])
    with col_c:
        u = st.text_input("AUTHORIZED USER ID")
        p = st.text_input("SECURITY ACCESS KEY", type="password")
        if st.button("AUTHENTICATE"):
            if u == "Dr. Ziad Elshafei" and p == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("ACCESS DENIED: Unauthorized Identity")
    st.stop()

# ==========================================
# 💾 4. THE DATA EMPIRE (BUILT-IN SQUAD)
# ==========================================
# هنا حطينا الداتا المتباينة (رجالة وستات ومستويات متباينة جداً)
@st.cache_data
def load_elite_squad():
    squad_data = {
        "Date": pd.to_datetime(["2026-04-02"]*14),
        "Player": [
            "Ziad (Elite)", "Mohamed (Critical)", "Sara (Optimal)", "Tarek (Overload)", 
            "Nour (Pro)", "Ahmed (Fatigue)", "Layla (Fit)", "Mona (Caution)", 
            "Omar (Stable)", "Yasmine (Fresh)", "Hassan (Weak)", "Mariam (Elite)",
            "Karim (Injured)", "Dina (Ready)"
        ],
        "Gender": ["Male", "Male", "Female", "Male", "Female", "Male", "Female", "Female", "Male", "Female", "Male", "Female", "Male", "Female"],
        "Workload": [780, 1400, 430, 1200, 510, 995, 320, 690, 600, 250, 880, 420, 1500, 380],
        "RPE": [7, 10, 5, 10, 6, 9, 3, 8, 6, 2, 9, 4, 10, 4],
        "Sleep": [8, 4, 9, 3, 7, 5, 9, 5, 7, 9, 5, 8, 3, 8],
        "HRV": [85, 35, 92, 30, 84, 45, 96, 58, 70, 99, 52, 89, 25, 86]
    }
    return pd.DataFrame(squad_data)

df = load_elite_squad()

# ==========================================
# 📂 5. SIDEBAR & CONTROLS
# ==========================================
st.sidebar.markdown("### 👨‍⚕️ CHIEF MEDICAL OFFICER")
st.sidebar.write(f"**Dr. Ziad Elshafei**")
st.sidebar.markdown("---")

# اختيار اللاعب
selected_athlete = st.sidebar.selectbox("🎯 SELECT ACTIVE PROFILE", df['Player'].unique())
p_df = df[df['Player'] == selected_athlete].copy()

# رفع داتا جديدة لو حبيت
up = st.sidebar.file_uploader("📂 SYNC EXTERNAL CSV", type="csv")
if up:
    df = pd.read_csv(up)
    st.sidebar.success("Cloud Data Synced!")

# ==========================================
# 🧠 6. AI ANALYTICS ENGINE (ACWR & RISK)
# ==========================================
risk_index = (p_df['Workload'].iloc[-1] / 1000) * (10 / p_df['Sleep'].iloc[-1])
p_df['Acute'] = p_df['Workload'].rolling(7, 1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(28, 1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, 1)

# ==========================================
# 🏟️ 7. MASTER DASHBOARD LAYOUT
# ==========================================
st.markdown(f"<h1>🚀 SPINIX AI ELITE HUB: {selected_athlete}</h1>", unsafe_allow_html=True)

# Metrics Grid
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("INJURY RISK", f"{min(risk_index*10, 100):.1f}%", delta="CRITICAL" if risk_index > 1.2 else "SAFE")
with c2: st.metric("ACWR RATIO", f"{p_df['ACWR'].iloc[-1]:.2f}", "DANGER" if p_df['ACWR'].iloc[-1] > 1.5 else "OPTIMAL")
with c3: st.metric("READINESS SCORE", f"{int(100 - (risk_index*5))}%")
with c4: st.metric("GENDER GROUP", p_df['Gender'].iloc[0])

st.divider()

# TAB SYSTEM
tab_analytics, tab_bio, tab_roi, tab_squad = st.tabs(["📉 CLINICAL ANALYTICS", "🦴 AI BIOMECHANICS", "💰 BUSINESS ROI", "👥 SQUAD CONTRAST"])

with tab_analytics:
    st.subheader("Workload Trends (Acute vs Chronic)")
    fig_line = px.area(p_df, x='Date', y=['Workload', 'Chronic'], color_discrete_sequence=['#58a6ff', '#ff7b72'], template="plotly_dark")
    st.plotly_chart(fig_line, use_container_width=True)

with tab_bio:
    st.subheader("AI Motion Tracking Engine")
    v_file = st.file_uploader("Upload Athlete Video (MP4/MOV)", type=['mp4', 'mov'])
    if v_file:
        if pose_engine:
            with st.spinner("Spinix AI Analyzing..."):
                t_f = tempfile.NamedTemporaryFile(delete=False)
                t_f.write(v_file.read())
                cap = cv2.VideoCapture(t_f.name)
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = pose_engine.process(frame_rgb)
                    if res.pose_landmarks:
                        mp_drawing.draw_landmarks(frame_rgb, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    st.image(frame_rgb, use_container_width=True, caption="Spinix AI Biomechanics Tracker")
                cap.release()
        else:
            st.error("AI Engine Offline: Please check server requirements.")

with tab_roi:
    st.subheader("SPX Brand & Clinic ROI")
    r1, r2 = st.columns(2)
    with r1: st.metric("Revenue Saved (Prevention)", f"${int(risk_index*1800)}", "+15% vs Last Month")
    with r2: st.metric("SPX Brand Reach", "32.4k Users", "+8.2%")

with tab_squad:
    st.subheader("Squad Workload Contrast (Male vs Female)")
    fig_bar = px.bar(df, x='Player', y='Workload', color='Gender', barmode='group', color_discrete_map={"Male": "#58a6ff", "Female": "#ff7b72"}, template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 📋 8. CLINICAL DECISION SUPPORT
# ==========================================
st.divider()
st.subheader("📋 CLINICAL DECISION & RECOMMENDATION")
if risk_index > 1.5:
    st.error(f"🛑 CRITICAL ALERT: {selected_athlete} is in the high-risk zone. Stop training for 48h. Focus on recovery and SPX Magnesium.")
elif risk_index > 0.8:
    st.warning(f"⚠️ CAUTION: {selected_athlete} is showing signs of overreaching. Reduce training load by 40%.")
else:
    st.success(f"🟢 CLEAR: {selected_athlete} is in optimal condition. Ready for match-day intensity.")

st.caption(f"Spinix AI Ultimate v12.0 | Designed by Dr. Ziad Elshafei | Real Madrid Graduate School Integrated Models")
    st.success(f"🟢 CLEAR: {player} is fit for elite performance.")

st.caption(f"Spinix AI Ultimate v10.5 | Specialized Clinical System | {datetime.now().year}")
