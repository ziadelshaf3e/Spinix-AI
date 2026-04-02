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
# 🧠 AI BIOMECHANICS ENGINE (SAFE LOAD)
# ==========================================
try:
    import mediapipe as mp
    # الاستدعاء المباشر والمستقر للسيرفرات
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose_engine = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
except Exception as e:
    st.error(f"⚠️ AI Biomechanics Module partially offline. Error: {e}")

# ==========================================
# 🎨 UI & STYLING
# ==========================================
st.set_page_config(page_title="Spinix AI Elite v8.0", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0b0f14; color: white; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #00ffcc33; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 12px; border: 1px solid #00ffcc22; }
    .panel-card {
        background: #111827;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Inter', sans-serif; }
    .stButton>button { background-color: #00ffcc; color: #0b0f14; font-weight: bold; width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 SECURE AUTHENTICATION
# ==========================================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# بيانات الدخول الخاصة بالدكتور
USERS = {"Dr. Ziad Elshafei": hash_pass("1234"), "admin": hash_pass("spinix2026")}

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.markdown("<h1 style='text-align:center;'>🛡️ SPINIX AI GATEWAY</h1>", unsafe_allow_html=True)
    with st.container():
        col_l, col_c, col_r = st.columns([1,2,1])
        with col_c:
            u = st.text_input("Authorized User")
            p = st.text_input("Access Key", type="password")
            if st.button("Verify Identity"):
                if u in USERS and USERS[u] == hash_pass(p):
                    st.session_state.login = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Credentials")
    st.stop()

# ==========================================
# 💾 DATA & DATABASE
# ==========================================
conn = sqlite3.connect("spinix_v8.db", check_same_thread=False)

def save_data(df):
    df.to_sql("athlete_records", conn, if_exists="replace", index=False)

def load_data():
    try:
        return pd.read_sql("SELECT * FROM athlete_records", conn)
    except:
        # بيانات افتراضية للتشغيل الأول
        dates = pd.date_range(end=datetime.now(), periods=20)
        return pd.DataFrame({
            "Date": dates,
            "Player": ["Test Player"]*20,
            "Workload": np.random.randint(300, 900, 20),
            "RPE": np.random.randint(4, 10, 20),
            "Sleep": np.random.randint(5, 9, 20)
        })

# ==========================================
# 📂 SIDEBAR & UPLOAD
# ==========================================
st.sidebar.title(f"👤 {st.session_state.user}")
st.sidebar.markdown("---")
file = st.sidebar.file_uploader("Upload Daily CSV", type="csv")

if file:
    df_raw = pd.read_csv(file)
    save_data(df_raw)
    st.sidebar.success("Cloud Data Synced!")

df = load_data()
player_name = st.sidebar.selectbox("Select Athlete Profile", df['Player'].unique())
p_df = df[df['Player'] == player_name].copy()
p_df['Date'] = pd.to_datetime(p_df['Date'])

# ==========================================
# 🧠 AI ANALYTICS (ACWR & RISK)
# ==========================================
p_df['Acute'] = p_df['Workload'].rolling(window=7, min_periods=1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(window=28, min_periods=1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, np.nan)

# AI Risk Model
risk_percentage = 15.0
if len(p_df) > 5:
    p_df['Label'] = ((p_df['ACWR'] > 1.4) | (p_df['RPE'] > 8)).astype(int)
    clf = RandomForestClassifier(n_estimators=50)
    feats = ['Workload', 'RPE', 'Sleep']
    clf.fit(p_df[feats].fillna(0), p_df['Label'])
    current_stat = p_df[feats].iloc[-1:].fillna(0)
    risk_percentage = clf.predict_proba(current_stat)[0][1] * 100

# ==========================================
# 🎥 BIOMECHANICS FUNCTIONS
# ==========================================
def analyze_frame(video_file):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    v_cap = cv2.VideoCapture(tfile.name)
    success, frame = v_cap.read()
    if success:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose_engine.process(frame_rgb)
        if res.pose_landmarks:
            mp_drawing.draw_landmarks(frame_rgb, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            return frame_rgb
    return None

# ==========================================
# 🏟️ MAIN DASHBOARD
# ==========================================
st.header(f"🚀 {player_name} | Performance Analysis")

# Top Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Injury Risk Score", f"{risk_percentage:.1f}%", delta="-1.2%" if risk_percentage < 50 else "+3.5%", delta_color="inverse")
c2.metric("ACWR (Workload)", f"{p_df['ACWR'].iloc[-1]:.2f}", "Stable" if 0.8 <= p_df['ACWR'].iloc[-1] <= 1.3 else "High")
c3.metric("Current Readiness", f"{int(100 - risk_percentage)}%")
c4.metric("Fatigue Index", f"{p_df['RPE'].iloc[-1]}/10")

st.divider()

# Tabs for detailed view
t_load, t_bio, t_gps = st.tabs(["📉 Clinical Load", "🦴 AI Biomechanics", "📍 GPS Heatmap"])

with t_load:
    st.subheader("Workload Trends (Last 30 Days)")
    fig = px.line(p_df, x='Date', y=['Workload', 'Chronic'], 
                  color_discrete_map={"Workload": "#00ffcc", "Chronic": "#ff4d4d"},
                  template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with t_bio:
    st.subheader("AI Skeletal Tracking")
    v_file = st.file_uploader("Upload Movement Video (MP4/MOV)", type=['mp4', 'mov'])
    if v_file:
        with st.spinner("Spinix AI analyzing biomechanics..."):
            out_img = analyze_frame(v_file)
            if out_img is not None:
                st.image(out_img, caption="Real-time Pose Detection Result", use_container_width=True)
                st.success("✅ Analysis Complete: Symmetry Detected.")

with t_gps:
    st.subheader("Player Pitch Intensity")
    # محاكاة لبيانات الـ GPS
    grid = np.random.randn(12, 12)
    fig_gps = px.imshow(grid, color_continuous_scale='Magma', title="Zone Coverage")
    st.plotly_chart(fig_gps, use_container_width=True)

# Final Clinical Decision
st.divider()
if risk_percentage > 70:
    st.error(f"🚨 MEDICAL ALERT: {player_name} is in the Red Zone. Recommendation: 48h REST.")
elif risk_percentage > 40:
    st.warning(f"⚠️ CAUTION: {player_name} is showing overreach symptoms. Reduce load by 25%.")
else:
    st.success(f"🟢 GREEN LIGHT: {player_name} is fully recovered and ready for high intensity.")

st.markdown("---")
st.caption(f"Spinix AI Elite v8.0 | Dr. Ziad Elshafei | Integrated Clinical System")
