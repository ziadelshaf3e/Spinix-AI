import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import cv2
import tempfile
from datetime import datetime

# ==========================================
# 🧠 1. AI BIOMECHANICS ENGINE (ELITE)
# ==========================================
pose_engine = None
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose_engine = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
except:
    st.sidebar.warning("⚠️ AI Engine Init: Partial Load")

# ==========================================
# 🎨 2. SPINIX MASTER BRANDING (CSS)
# ==========================================
st.set_page_config(page_title="Spinix AI OS v13", layout="wide")

st.markdown("""
<style>
    .main { background: #010409; color: #c9d1d9; }
    .stMetric { background: #0d1117; padding: 25px; border-radius: 15px; border: 1px solid #30363d; box-shadow: 0 8px 16px rgba(0,255,200,0.05); }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    h1 { color: #58a6ff !important; font-size: 45px; text-shadow: 2px 2px #000; }
    .stButton>button { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border: none; height: 3em; font-weight: bold; }
    .status-box { padding: 15px; border-radius: 10px; border-left: 5px solid #58a6ff; background: #161b22; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 3. ACCESS CONTROL (BIOMETRIC SIMULATION)
# ==========================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🛡️ SPINIX AI OS: ACCESS REQUIRED</h1>", unsafe_allow_html=True)
    c_l, c_c, c_r = st.columns([1,1.5,1])
    with c_c:
        user = st.text_input("CHIEF MEDICAL OFFICER ID")
        pwd = st.text_input("ENCRYPTION KEY", type="password")
        if st.button("BYPASS FIREWALL"):
            if user == "Dr. Ziad Elshafei" and pwd == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("UNAUTHORIZED ACCESS DETECTED")
    st.stop()

# ==========================================
# 💾 4. THE MASTER DATASET (DIVERSE SQUAD)
# ==========================================
@st.cache_data
def load_full_squad():
    return pd.DataFrame({
        "Date": pd.date_range(end=datetime.now(), periods=15),
        "Player": ["Ziad (Pro)", "Mohamed (Danger)", "Sara (Elite)", "Tarek (Overload)", 
                   "Nour (Optimal)", "Ahmed (Fatigue)", "Layla (Fit)", "Mona (Caution)", 
                   "Omar (Stable)", "Yasmine (Fresh)", "Hassan (Weak)", "Mariam (Elite)",
                   "Karim (Critical)", "Dina (Ready)", "Coach Khaled (Stable)"],
        "Gender": ["Male", "Male", "Female", "Male", "Female", "Male", "Female", "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male"],
        "Workload": [780, 1450, 410, 1220, 500, 980, 330, 670, 590, 260, 890, 420, 1550, 390, 600],
        "RPE": [7, 10, 5, 10, 6, 9, 3, 8, 6, 2, 9, 4, 10, 4, 6],
        "Sleep": [8, 4, 9, 3, 7, 5, 9, 5, 7, 9, 5, 8, 3, 8, 7],
        "HRV": [85, 30, 92, 28, 88, 44, 95, 60, 72, 99, 51, 87, 22, 85, 70]
    })

df = load_full_squad()

# ==========================================
# 📂 5. COMMAND CENTER (SIDEBAR)
# ==========================================
st.sidebar.markdown("## 🛰️ COMMAND CENTER")
st.sidebar.info(f"User: Dr. Ziad | Clinic: Spinix")
athlete = st.sidebar.selectbox("SELECT TARGET ATHLETE", df['Player'].unique())
p_df = df[df['Player'] == athlete].copy()

# ==========================================
# 🧠 6. AI CORE CALCULATIONS
# ==========================================
risk = (p_df['Workload'].iloc[-1] / 1000) * (10 / p_df['Sleep'].iloc[-1])
p_df['ACWR'] = p_df['Workload'] / p_df['Workload'].rolling(28, 1).mean().replace(0, 1)

# ==========================================
# 🏟️ 7. MASTER DASHBOARD LAYOUT
# ==========================================
st.markdown(f"<h1>🚀 SPINIX AI PERFORMANCE: {athlete}</h1>", unsafe_allow_html=True)

# --- Metric Row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("INJURY RISK INDEX", f"{min(risk*10, 100):.1f}%", "CRITICAL" if risk > 1.2 else "STABLE")
col2.metric("ACWR RATIO", f"{p_df['ACWR'].iloc[-1]:.2f}", "DANGER" if p_df['ACWR'].iloc[-1] > 1.5 else "OPTIMAL")
col3.metric("READINESS SCORE", f"{int(100 - (risk*5))}%")
col4.metric("MARKET VALUE SAVED", f"${int((1-risk)*60000):,}")

st.divider()

# --- Tabs System ---
t_clinical, t_bio, t_gps, t_biz = st.tabs(["📉 CLINICAL DATA", "🦴 AI BIOMECHANICS", "📍 GPS HEATMAP", "💰 SPX BUSINESS"])

with t_clinical:
    st.subheader("Performance vs Recovery (Dynamic Analysis)")
    fig_line = px.line(p_df, x='Date', y=['Workload', 'HRV'], color_discrete_sequence=['#58a6ff', '#3fb950'], markers=True, template="plotly_dark")
    st.plotly_chart(fig_line, use_container_width=True)

with t_bio:
    st.subheader("AI Motion Analysis Engine")
    v_up = st.file_uploader("Upload Movement Video", type=['mp4', 'mov'])
    if v_up and pose_engine:
        with st.spinner("Analyzing Movement Matrix..."):
            t_file = tempfile.NamedTemporaryFile(delete=False)
            t_file.write(v_up.read())
            cap = cv2.VideoCapture(t_file.name)
            ret, frame = cap.read()
            if ret:
                f_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose_engine.process(f_rgb)
                if res.pose_landmarks:
                    mp_drawing.draw_landmarks(f_rgb, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                st.image(f_rgb, use_container_width=True, caption="Spinix AI: Active Tracking Enabled")
            cap.release()

with t_gps:
    st.subheader("Live Field Positioning (Simulated)")
    gps_data = np.random.randn(20, 20)
    fig_heat = px.imshow(gps_data, color_continuous_scale='Hot', title="Player Intensity Heatmap")
    st.plotly_chart(fig_heat, use_container_width=True)

with t_biz:
    st.subheader("SPX Brand & ROI Tracker")
    b1, b2 = st.columns(2)
    b1.metric("Supplement Conversion", "+42%", "SPX Creatine")
    b2.metric("Clinic Saved Revenue", f"${int(risk*2200)}", "Prevention ROI")

# --- Final Decision Support ---
st.divider()
st.subheader("📋 CLINICAL RECOMMENDATION")
if risk > 1.5:
    st.error(f"🛑 CRITICAL: {athlete} is in the Red Zone. Recommendation: Absolute Rest + SPX Recovery Protocol.")
elif risk > 0.8:
    st.warning(f"⚠️ CAUTION: {athlete} is overreaching. Recommendation: Reduce Workload by 35%.")
else:
    st.success(f"🟢 OPTIMAL: {athlete} is ready for 100% intensity training/match.")

st.caption(f"Spinix AI OS v13.0 | Real Madrid Graduate School Standards | Last Check: {datetime.now().strftime('%H:%M:%S')}")
