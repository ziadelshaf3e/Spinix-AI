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
# 🧠 AI BIOMECHANICS ENGINE (ULTRA STABLE)
# ==========================================
# تغيير جذري في طريقة الاستدعاء لتجنب AttributeError
try:
    import mediapipe as mp
    from mediapipe.python.solutions import pose as mp_pose
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    
    # تعريف موديل التحليل الحركي
    pose_engine = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    st.sidebar.success("✅ AI Engine Online")
except Exception as e:
    # محاولة بديلة في حالة فشل الاستدعاء المباشر
    try:
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        pose_engine = mp_pose.Pose()
        st.sidebar.success("✅ AI Engine Online (Legacy)")
    except:
        st.sidebar.error(f"❌ AI Module Error: {e}")

# ==========================================
# 🎨 UI & STYLING
# ==========================================
st.set_page_config(page_title="Spinix AI Elite v8.5", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0b0f14; color: white; }
    [data-testid="stSidebar"] { background-color: #111827; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 12px; border: 1px solid #00ffcc22; }
    .panel-card { background: #111827; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 SECURE AUTHENTICATION
# ==========================================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {"Dr. Ziad Elshafei": hash_pass("1234"), "admin": hash_pass("spinix2026")}

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🛡️ Spinix AI Secure Gateway")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Enter System"):
        if u in USERS and USERS[u] == hash_pass(p):
            st.session_state.login = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# ==========================================
# 💾 DATABASE ENGINE
# ==========================================
conn = sqlite3.connect("spinix_final.db", check_same_thread=False)

def load_data():
    try:
        return pd.read_sql("SELECT * FROM records", conn)
    except:
        return pd.DataFrame({
            "Date": pd.date_range(end=datetime.now(), periods=10),
            "Player": ["Sample Athlete"]*10,
            "Workload": [500, 550, 480, 600, 700, 750, 800, 400, 300, 500],
            "RPE": [6, 7, 6, 8, 9, 9, 10, 5, 4, 6],
            "Sleep": [8, 7, 8, 6, 5, 5, 4, 8, 9, 7]
        })

# ==========================================
# 📂 DATA MANAGEMENT
# ==========================================
st.sidebar.title(f"👤 {st.session_state.user}")
file = st.sidebar.file_uploader("Sync CSV Data", type="csv")

if file:
    df_raw = pd.read_csv(file)
    df_raw.to_sql("records", conn, if_exists="replace", index=False)
    st.sidebar.success("Data Updated!")

df = load_data()
player_name = st.sidebar.selectbox("Athlete Profile", df['Player'].unique())
p_df = df[df['Player'] == player_name].copy()
p_df['Date'] = pd.to_datetime(p_df['Date'])

# ==========================================
# 🧠 AI ANALYTICS (ACWR)
# ==========================================
p_df['Acute'] = p_df['Workload'].rolling(7, 1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(28, 1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, np.nan)

risk_val = 0.2
if len(p_df) > 5:
    clf = RandomForestClassifier(n_estimators=50)
    p_df['Label'] = ((p_df['ACWR'] > 1.3) | (p_df['RPE'] > 8)).astype(int)
    clf.fit(p_df[['Workload', 'RPE', 'Sleep']].fillna(0), p_df['Label'])
    risk_val = clf.predict_proba(p_df[['Workload', 'RPE', 'Sleep']].iloc[-1:].fillna(0))[0][1]

# ==========================================
# 🎥 BIOMECHANICS FUNCTION
# ==========================================
def process_video_frame(video_file):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    cap = cv2.VideoCapture(tfile.name)
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # استخدام الـ Engine المعرف في البداية
        results = pose_engine.process(frame_rgb)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            return frame_rgb
    return None

# ==========================================
# 🏟️ DASHBOARD UI
# ==========================================
st.header(f"🚀 {player_name} Performance Analysis")

c1, c2, c3 = st.columns(3)
c1.metric("Injury Risk", f"{risk_val*100:.1f}%")
c2.metric("ACWR Ratio", f"{p_df['ACWR'].iloc[-1]:.2f}")
c3.metric("Training Status", "Ready" if risk_val < 0.5 else "Danger")

st.divider()

tab1, tab2 = st.tabs(["📉 Data Insights", "🦴 AI Biomechanics"])

with tab1:
    st.plotly_chart(px.line(p_df, x='Date', y=['Workload', 'Chronic'], color_discrete_sequence=['#00ffcc', '#ff4d4d']), use_container_width=True)

with tab2:
    v_file = st.file_uploader("Upload Video", type=['mp4', 'mov'])
    if v_file:
        res_img = process_video_frame(v_file)
        if res_img is not None:
            st.image(res_img, caption="Spinix AI Analysis", use_container_width=True)
            st.success("✅ Pose Estimation Active")

st.caption("Spinix AI Elite v8.5 | Specialized Clinical System")
    st.success(f"🟢 GREEN LIGHT: {player_name} is fully recovered and ready for high intensity.")

st.markdown("---")
st.caption(f"Spinix AI Elite v8.0 | Dr. Ziad Elshafei | Integrated Clinical System")
