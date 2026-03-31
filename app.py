import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import hashlib

# 1. إعدادات الصفحة
st.set_page_config(page_title="Spinix AI Elite v6", layout="wide")

# 2. نظام الدخول (Security)
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

USERS = {
    "admin": {"password": hash_pass("1234"), "role": "Admin"},
    "ziad": {"password": hash_pass("spinix2026"), "role": "Doctor"}
}

if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.markdown("<h1 style='text-align: center; color: #00ffcc;'>🛡️ Spinix AI Login</h1>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in USERS and USERS[u]["password"] == hash_pass(p):
            st.session_state.login = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Wrong credentials")

if not st.session_state.login:
    login()
    st.stop()

# 3. ستايل الواجهة (Neon Dark Theme)
st.markdown("""
<style>
    .main { background-color: #0b0f14; color: #e0e0e0; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc33; }
    h1, h2, h3 { color: #00ffcc !important; }
</style>
""", unsafe_allow_html=True)

# 4. قاعدة البيانات (Database)
conn = sqlite3.connect("spinix_v6.db", check_same_thread=False)

def save(df):
    df.to_sql("data", conn, if_exists="replace", index=False)

def load():
    try:
        return pd.read_sql("SELECT * FROM data", conn)
    except:
        return None

# 5. رفع الملف والـ Mapping (حل مشكلة الـ Errors)
st.sidebar.title(f"Welcome Dr. {st.session_state.user}")
file = st.sidebar.file_uploader("Upload Squad CSV", type="csv")

if file:
    raw = pd.read_csv(file, encoding='utf-8-sig')
    st.sidebar.write("### Column Mapping")
    mapping = {}
    cols_options = ["Ignore", "Date", "Player", "Workload", "RPE", "Sleep", "Heart Rate", "Fatigue"]
    for c in raw.columns:
        mapping[c] = st.sidebar.selectbox(f"Map '{c}' to:", cols_options, key=c)

    df_new = pd.DataFrame()
    for k, v in mapping.items():
        if v != "Ignore":
            df_new[v] = raw[k]
    
    if not df_new.empty and 'Player' in df_new.columns:
        save(df_new)
        st.sidebar.success("Data Saved!")

df = load()

if df is None or df.empty:
    st.info("👋 Dr. Ziad, please upload a CSV file to activate the AI system.")
    st.stop()

# 6. محرك الذكاء الاصطناعي (The AI Engine)
player_list = df['Player'].unique()
player = st.selectbox("🎯 Select Player", player_list)
pdf = df[df['Player'] == player].copy()

# حسابات الأحمال (ACWR) - منع القسمة على صفر
pdf['Acute'] = pdf['Workload'].rolling(7, min_periods=1).mean()
pdf['Chronic'] = pdf['Workload'].rolling(28, min_periods=1).mean()
pdf['ACWR'] = pdf['Acute'] / (pdf['Chronic'] + 0.1)
pdf['Injury_Target'] = ((pdf['ACWR'] > 1.3) | (pdf['Fatigue'] > 8)).astype(int)

# تدريب الموديل (AI Training)
features = ['Workload', 'RPE', 'Sleep']
train_df = pdf.dropna(subset=features + ['Injury_Target'])

if len(train_df) > 1:
    model = RandomForestClassifier(n_estimators=50)
    model.fit(train_df[features], train_df['Injury_Target'])
    latest_feat = pdf[features].iloc[-1:].values
    risk = model.predict_proba(latest_feat)[0][1]
else:
    risk = 0.5 # قيمة افتراضية لو الداتا قليلة

# 7. التوزيعة البصرية (Visual Layout)
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("### 🚨 Squad Alerts")
    color = "red" if risk > 0.7 else "orange" if risk > 0.4 else "green"
    st.markdown(f"<div style='padding:20px; border-radius:10px; background:#161b22; border-left:5px solid {color};'>"
                f"<h4>{player}</h4><h2 style='color:{color}'>{risk*100:.0f}% Risk</h2></div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 🧍 Injury Map")
    fig = go.Figure(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=30, color=color)))
    fig.update_layout(height=300, paper_bgcolor="#0b0f14", scene=dict(bgcolor="#0b0f14", xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("### 💰 Market Value")
    val = pdf['Workload'].iloc[-1] * 1200
    st.metric("Player Value", f"${val:,.0f}",risk_color}; background:#1a1f2b;">, use_container_width=True)
