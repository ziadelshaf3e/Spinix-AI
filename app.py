# ==========================================
# Spinix AI v5.1 - ELITE SYSTEM (MODIFIED)
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import hashlib

# إعداد الصفحة
st.set_page_config(page_title="Spinix AI v5.1", layout="wide", page_icon="🛡️")

# ==============================
# 🔐 نظام الدخول (Security)
# ==============================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {
    "admin": {"password": hash_pass("1234"), "role": "Admin"},
    "ziad": {"password": hash_pass("spinix2026"), "role": "Doctor"}
}

if "login" not in st.session_state:
    st.session_state.login = False

def login_screen():
    st.markdown("<h1 style='text-align: center; color: #00ffcc;'>🛡️ Spinix AI Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Access Dashboard", use_container_width=True):
            if u in USERS and USERS[u]["password"] == hash_pass(p):
                st.session_state.login = True
                st.session_state.role = USERS[u]["role"]
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Access Denied: Invalid Credentials")

if not st.session_state.login:
    login_screen()
    st.stop()

# ==============================
# 🎨 الهوية البصرية (Dark Mode)
# ==============================
st.markdown("""
<style>
    .main { background-color: #0b0f14; color: #00ffcc; }
    [data-testid="stSidebar"] { background-color: #11151c; }
    .stMetric { background-color: #1a1f2b; padding: 15px; border-radius: 12px; border: 1px solid #00ffcc33; }
    h1, h2, h3 { color: #00ffcc; font-family: 'Arial Black', sans-serif; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 💾 قاعدة البيانات (Stable Storage)
# ==============================
conn = sqlite3.connect("spinix_elite.db", check_same_thread=False)

def save_data(df):
    df.to_sql("players_data", conn, if_exists="replace", index=False)

def load_data():
    try:
        return pd.read_sql("SELECT * FROM players_data", conn)
    except:
        return None

# ==============================
# 📂 إدارة الملفات (Mapping System)
# ==============================
st.sidebar.markdown(f"### 👨‍⚕️ Dr. {st.session_state.user.capitalize()}")
file = st.sidebar.file_uploader("Upload Squad CSV", type="csv")

if file:
    raw = pd.read_csv(file, encoding='utf-8-sig')
    st.sidebar.info("Map your columns below:")
    
    mapping = {}
    cols = ["Ignore", "Date", "Player", "Workload", "RPE", "Sleep", "Heart Rate", "Fatigue"]
    for c in raw.columns:
        mapping[c] = st.sidebar.selectbox(f"Column: {c}", cols, key=c)

    df_final = pd.DataFrame()
    for k, v in mapping.items():
        if v != "Ignore":
            df_final[v] = raw[k]
    
    if 'Date' in df_final.columns:
        df_final['Date'] = pd.to_datetime(df_final['Date'])
        save_data(df_final)
        st.sidebar.success("Data Synced!")

df = load_data()

if df is None or df.empty:
    st.warning("👋 Welcome Dr. Ziad! Please upload a CSV file to activate the AI system.")
    st.stop()

# ==============================
# 🧠 محرك الذكاء الاصطناعي (ACWR Engine)
# ==============================
player_names = df['Player'].unique()
selected_player = st.selectbox("🎯 Select Athlete for Analysis", player_names)
p_df = df[df['Player'] == selected_player].sort_values('Date').copy()

# حسابات الأحمال (Advanced Metrics)
p_df['Acute'] = p_df['Workload'].rolling(window=7, min_periods=1).mean()
p_df['Chronic'] = p_df['Workload'].rolling(window=28, min_periods=1).mean()
p_df['ACWR'] = p_df['Acute'] / (p_df['Chronic'] + 0.001)

# تنظيف الداتا للـ AI
features = ['Workload', 'RPE', 'Sleep'] # الميزات الأساسية المضمونة
p_df['Injury_Label'] = ((p_df['ACWR'] > 1.3) | (p_df['RPE'] > 8)).astype(int)

# تدريب الموديل سريعاً
X = p_df[features].fillna(0)
y = p_df['Injury_Label']
model = RandomForestClassifier(n_estimators=50).fit(X, y)

latest = p_df.iloc[-1]
risk_prob = model.predict_proba([latest[features].values])[0][1]

# ==============================
# 📊 الهيكل البصري (Layout)
# ==============================
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    st.markdown("### 🚨 Squad Alerts")
    risk_color = "red" if risk_prob > 0.7 else "orange" if risk_prob > 0.4 else "green"
    st.markdown(f"""
        <div style="padding:20px; border-radius:10px; border-left: 5px solid {risk_color}; background:#1a1f2b;">, use_container_width=True)
