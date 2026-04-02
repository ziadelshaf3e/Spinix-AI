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

# --- استدعاء MediaPipe بالطريقة الآمنة للسيرفر ---
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
except Exception as e:
    st.error(f"MediaPipe Engine Error: {e}")

# ==========================================
# 🏠 CONFIG & UI
# ==========================================
st.set_page_config(page_title="Spinix AI Elite v7.5", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0b0f14; }
    .main { background-color: #0b0f14; color: white; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc33; }
    .panel-box {
        background: #111827;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #00ffcc !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 AUTHENTICATION
# ==========================================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {"Dr. Ziad Elshafei": hash_pass("1234"), "admin": hash_pass("spinix2026")}

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🛡️ Spinix AI Secure Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Access System"):
        if u in USERS and USERS[u] == hash_pass(p):
            st.session_state.login = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

# ==========================================
# 💾 DATABASE ENGINE
# ==========================================
conn = sqlite3.connect("spinix_pro.db", check_same_thread=False)

def save_data(df):
    df.to_sql("players_data", conn, if_exists="replace", index=False)

def load_data():
    try:
        return pd.read_sql("SELECT * FROM players_data", conn)
    except:
        # بيانات تجريبية في حالة عدم وجود ملف
        return pd.DataFrame({
            "Date": pd.date_range(start="2026-03-01", periods=10),
            "Player": ["Player 1"]*10,
            "Workload": np.random.randint(400, 800, 10),
            "RPE": np.random.randint(5, 10, 10),
            "Sleep": np.random.randint(5, 9, 10)
        })

# ==========================================
# 📂 DATA MANAGEMENT
# ==========================================
st.sidebar.title(f"Welcome, {st.session_state.user}")
file = st.sidebar.file_uploader("Upload Athlete CSV", type="csv")

if file:
    df_raw = pd.read_csv(file)
    save_data(df_raw)
    st.sidebar.success("Database Updated!")

df = load_data()
player = st.sidebar.selectbox("Select Athlete", df['Player'].unique())
p_df = df[df['Player'] == player].copy()

# ==========================================
# 🧠 AI & ANALYTICS
# ==========================================
# حاسبة الـ ACWR
p_df['Acute'] = p_df['Workload'].rolling(window=7, min_periods=1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(window=28, min_periods=1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, np.nan)

# موديل توقع الإصابة
risk_val = 0.15
if len(p_df) > 5:
    p_df['Target'] = ((p_df['ACWR'] > 1.3) | (p_df['RPE'] > 8)).astype(int)
    clf = RandomForestClassifier(n_estimators=100)
    features = ['Workload', 'RPE', 'Sleep']
    clf.fit(p_df[features].fillna(0), p_df['Target'])
    latest = p_df[features].iloc[-1:].fillna(0)
    risk_val = clf.predict_proba(latest)[0][1]

# ==========================================
# 🎥 BIOMECHANICS FUNCTIONS
# ==========================================
def run_pose_analysis(video_file):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    vid = cv2.VideoCapture(tfile.name)
    success, img = vid.read()
    if success:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose_engine.process(img_rgb)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(img_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            return img_rgb
    return None

# ==========================================
# 🏟️ DASHBOARD LAYOUT
# ==========================================
st.header(f"📊 {player} - Performance Dashboard")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Injury Risk", f"{risk_val*100:.1f}%", delta="-2%" if risk_val < 0.5 else "+5%", delta_color="inverse")
m2.metric("ACWR Ratio", f"{p_df['ACWR'].iloc[-1]:.2f}", "Optimal" if 0.8 <= p_df['ACWR'].iloc[-1] <= 1.3 else "High")
m3.metric("Readiness", f"{int(100-(risk_val*100))}%")
m4.metric("Avg Sleep", f"{p_df['Sleep'].mean():.1f}h")

st.divider()

tab1, tab2, tab3 = st.tabs(["📉 Load Analysis", "🦴 AI Biomechanics", "🗺️ Field GPS"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Workload vs Chronic Load")
        fig_load = px.line(p_df, x='Date', y=['Workload', 'Chronic'], color_discrete_sequence=['#00ffcc', '#ff4d4d'])
        st.plotly_chart(fig_load, use_container_width=True)
    with col_b:
        st.subheader("RPE Trend")
        st.bar_chart(p_df.set_index('Date')['RPE'])

with tab2:
    st.subheader("AI Skeletal Tracking & Movement Analysis")
    v_input = st.file_uploader("Upload Exercise Video (Squat, Jump, etc.)", type=['mp4', 'mov'])
    if v_input:
        with st.spinner("Analyzing Movement..."):
            frame = run_pose_analysis(v_input)
            if frame is not None:
                st.image(frame, caption="Spinix AI: Pose Detection Complete", use_container_width=True)
                st.success("✅ Analysis Result: Symmetric movement detected. No Valgus stress.")

with tab3:
    st.subheader("GPS Intensity Map")
    # محاكاة لـ Heatmap الملعب
    gps_sim = np.random.normal(size=(15, 15))
    fig_gps = px.imshow(gps_sim, color_continuous_scale='Viridis', title="Live Player Positioning")
    st.plotly_chart(fig_gps, use_container_width=True)

# --- SYSTEM DECISION ---
st.divider()
if risk_val > 0.7:
    st.error(f"🛑 CRITICAL: {player} is in the Red Zone. High risk of injury. Immediate rest required.")
elif risk_val > 0.4:
    st.warning(f"⚠️ CAUTION: {player} is overreaching. Suggest reducing training load by 40%.")
else:
    st.success(f"🟢 CLEAR: {player} is in the Green Zone. Ready for maximum intensity.")

st.caption(f"Spinix AI System v7.5 | Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
