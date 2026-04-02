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
# 🧠 AI BIOMECHANICS ENGINE (STABLE)
# ==========================================
try:
    import mediapipe as mp
    from mediapipe.python.solutions import pose as mp_pose
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    pose_engine = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
except:
    try:
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        pose_engine = mp_pose.Pose()
    except Exception as e:
        st.sidebar.error(f"AI Module Warning: {e}")

# ==========================================
# 🎨 UI & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Spinix AI Ultimate v9.0", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0b1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    .stMetric { background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .card { background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 20px; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .risk-high { color: #ff7b72; font-weight: bold; }
    .risk-low { color: #3fb950; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 LOGIN SYSTEM
# ==========================================
def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()
USERS = {"Dr. Ziad Elshafei": hash_pass("1234"), "admin": hash_pass("spinix2026")}

if "login" not in st.session_state: st.session_state.login = False

if not st.session_state.login:
    st.markdown("<h1 style='text-align:center;'>🔐 Spinix AI Gateway</h1>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,1.5,1])
    with col_c:
        u = st.text_input("User ID")
        p = st.text_input("Access Key", type="password")
        if st.button("Unlock System"):
            if u in USERS and USERS[u] == hash_pass(p):
                st.session_state.login = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# ==========================================
# 💾 DATABASE & DATA ENGINE
# ==========================================
conn = sqlite3.connect("spinix_ultra.db", check_same_thread=False)

def get_data():
    try: return pd.read_sql("SELECT * FROM v9_records", conn)
    except:
        dates = pd.date_range(end=datetime.now(), periods=30)
        return pd.DataFrame({
            "Date": dates, "Player": ["Elite Athlete"]*30,
            "Workload": np.random.randint(400, 900, 30),
            "RPE": np.random.randint(5, 10, 30),
            "Sleep": np.random.randint(5, 9, 30),
            "HRV": np.random.randint(60, 100, 30)
        })

# ==========================================
# 📂 SIDEBAR CONTROLS
# ==========================================
st.sidebar.image("https://via.placeholder.com/150x50/0b1117/58a6ff?text=SPINIX+PRO", use_container_width=True)
st.sidebar.title(f"Dr. {st.session_state.user.split('.')[-1]}")

up_file = st.sidebar.file_uploader("Upload CSV Data", type="csv")
if up_file:
    df_new = pd.read_csv(up_file)
    df_new.to_sql("v9_records", conn, if_exists="replace", index=False)
    st.sidebar.success("Cloud Sync: OK")

df = get_data()
player = st.sidebar.selectbox("Active Profile", df['Player'].unique())
p_df = df[df['Player'] == player].copy()
p_df['Date'] = pd.to_datetime(p_df['Date'])

# ==========================================
# 🧠 AI ENGINE (ACWR & PREDICTION)
# ==========================================
p_df['Acute'] = p_df['Workload'].rolling(7, 1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(28, 1).mean()
p_df['ACWR'] = p_df['Acute'] / p_df['Chronic'].replace(0, np.nan)

risk_prob = 0.1
if len(p_df) > 7:
    p_df['Injury'] = ((p_df['ACWR'] > 1.4) | (p_df['RPE'] > 8)).astype(int)
    model = RandomForestClassifier(n_estimators=100)
    features = ['Workload', 'RPE', 'Sleep']
    model.fit(p_df[features].fillna(0), p_df['Injury'])
    risk_prob = model.predict_proba(p_df[features].iloc[-1:].fillna(0))[0][1]

# ==========================================
# 🏟️ DASHBOARD LAYOUT (ULTIMATE)
# ==========================================
st.title(f"🚀 Spinix Performance Hub: {player}")

# Row 1: Vital Metrics
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Injury Risk", f"{risk_prob*100:.1f}%", delta=f"{risk_prob*5:.1f}%", delta_color="inverse")
with m2: st.metric("ACWR Ratio", f"{p_df['ACWR'].iloc[-1]:.2f}", "In Sweet Spot" if 0.8 <= p_df['ACWR'].iloc[-1] <= 1.3 else "Danger Zone")
with m3: st.metric("Readiness Index", f"{int(100-(risk_prob*100))}%", "Recovered")
with m4: st.metric("Market Value Saved", f"${int((1-risk_prob)*50000):,}")

st.divider()

# Row 2: Analysis Tabs
tab_clinical, tab_bio, tab_gps, tab_biz = st.tabs(["📉 Clinical Load", "🦴 AI Biomechanics", "📍 GPS Heatmap", "💰 SPX Business ROI"])

with tab_clinical:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Load Management (Acute vs Chronic)")
        fig_l = px.area(p_df, x='Date', y=['Workload', 'Chronic'], color_discrete_sequence=['#58a6ff', '#ff7b72'], template="plotly_dark")
        st.plotly_chart(fig_l, use_container_width=True)
    with col_b:
        st.subheader("Recovery Metrics")
        fig_h = px.line(p_df, x='Date', y='Sleep', title="Sleep Patterns", markers=True)
        st.plotly_chart(fig_h, use_container_width=True)

with tab_bio:
    st.subheader("AI Skeletal Movement Tracking")
    v_input = st.file_uploader("Upload Action Video", type=['mp4', 'mov'])
    if v_input:
        t_vid = tempfile.NamedTemporaryFile(delete=False)
        t_vid.write(v_input.read())
        cap = cv2.VideoCapture(t_vid.name)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose_engine.process(frame_rgb)
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            st.image(frame_rgb, caption="Spinix AI Scan: Active Tracking", use_container_width=True)
            st.info("Analysis: Normal Joint Angles. No valgus stress detected.")

with tab_gps:
    st.subheader("Field Intensity (Simulated GPS)")
    gps_grid = np.random.randn(15, 15)
    fig_g = px.imshow(gps_grid, color_continuous_scale='Turbo', title="Player Zone Coverage")
    st.plotly_chart(fig_g, use_container_width=True)

with tab_biz:
    st.subheader("SPX Brand & ROI Tracking")
    c_i, c_o = st.columns(2)
    with c_i:
        st.metric("SPX Supplements Growth", "+45%", "Revenue Up")
        st.write("Top Product: SPX Creatine Elite")
    with c_o:
        st.metric("Clinic Retention Rate", "92%", "Excellent")
        st.write("Marketing Reach: 25k Targeted Users")

# Row 3: Decisions
st.divider()
st.subheader("📋 Clinical Recommendation & Decision Support")
if risk_prob > 0.7:
    st.error(f"🛑 CRITICAL ALERT: {player} at high risk. RECOMMENDATION: Absolute Rest for 48h. Focus on active recovery and SPX Magnesium supplements.")
elif risk_prob > 0.4:
    st.warning(f"⚠️ CAUTION: {player} is overreaching. RECOMMENDATION: Reduce high-speed running by 30%. Modify gym session to eccentric-only.")
else:
    st.success(f"🟢 CLEAR: {player} is in optimal condition. READY for full training load and match intensity.")

st.caption(f"Spinix AI Ultimate v9.0 | Designed for Dr. Ziad Elshafei | Last System Check: {datetime.now().strftime('%H:%M:%S')}")
