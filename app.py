import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# ==========================================
# 🎨 1. UI & BRANDING
# ==========================================
st.set_page_config(layout="wide", page_title="Spinix AI ULTIMATE")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {background:#010409; color:#c9d1d9;}
    [data-testid="stSidebar"] {background:#0d1117; border-right: 1px solid #30363d;}
    .metric-card {background:#0d1117; padding:20px; border-radius:15px; border:1px solid #30363d;}
    h1, h2, h3 {color:#58a6ff !important;}
    .stButton>button {background: linear-gradient(90deg, #238636, #2ea043); color:white; width:100%; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 2. AUTHENTICATION (SaaS Ready)
# ==========================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Spinix AI Secure Login")
    col_l, col_c, col_r = st.columns([1,1.5,1])
    with col_c:
        u = st.text_input("User ID")
        p = st.text_input("Access Key", type="password")
        if st.button("Unlock System"):
            if (u == "admin" or u == "Dr. Ziad Elshafei") and p == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Access Denied")
    st.stop()

# ==========================================
# 📊 3. DIVERSE SQUAD DATA (Male/Female/Elite/Danger)
# ==========================================
@st.cache_data
def get_squad_data():
    data = {
        "Player": ["Ziad (Elite)", "Mohamed (Danger)", "Sara (Optimal)", "Tarek (Overload)", 
                   "Nour (Pro)", "Ahmed (Fatigue)", "Layla (Fit)", "Mona (Caution)", 
                   "Omar (Stable)", "Yasmine (Fresh)"],
        "Gender": ["Male", "Male", "Female", "Male", "Female", "Male", "Female", "Female", "Male", "Female"],
        "Workload": [750, 1450, 420, 1280, 510, 990, 315, 680, 595, 245],
        "RPE": [7, 10, 5, 10, 6, 9, 3, 8, 6, 2],
        "Sleep": [8, 4, 9, 3, 7, 5, 9, 5, 7, 9],
        "HRV": [82, 35, 92, 28, 85, 45, 96, 60, 72, 98],
        "Salary": [5000, 4000, 4500, 3800, 5500, 3200, 4800, 3500, 4200, 6000]
    }
    return pd.DataFrame(data)

df = get_squad_data()

# ==========================================
# 📂 4. SIDEBAR COMMAND
# ==========================================
st.sidebar.title("👨‍⚕️ Spinix Commander")
player_name = st.sidebar.selectbox("Select Athlete", df['Player'])
p = df[df['Player'] == player_name].iloc[0]

# ==========================================
# 🤖 5. AI RISK MODEL & FATIGUE
# ==========================================
df['Injury_Label'] = ((df['Workload']>1200)|(df['Sleep']<5)|(df['RPE']>8)).astype(int)
clf = RandomForestClassifier(n_estimators=50)
clf.fit(df[['Workload','RPE','Sleep','HRV']], df['Injury_Label'])
risk_prob = clf.predict_proba([[p['Workload'], p['RPE'], p['Sleep'], p['HRV']]])[0][1]

fatigue = (0.4 * p['RPE']) + (0.3 * (10 - p['Sleep'])) + (0.3 * (100 - p['HRV']) / 10)
readiness = max(0, 100 - fatigue * 10)

def get_injury_zone(p):
    if p['HRV'] < 40: return "Hamstring", (0, -1, 0)
    if p['Workload'] > 1300: return "ACL / Knee", (0, -2, 0)
    if p['Sleep'] < 5: return "CNS Fatigue", (0, 0, 0)
    return "Full Body Fit", (0, 1, 0)

inj_name, coords = get_injury_zone(p)

# ==========================================
# 🏟️ 6. DASHBOARD LAYOUT
# ==========================================
st.title(f"🚀 Spinix Performance: {player_name}")

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Injury Risk", f"{risk_prob*100:.1f}%")
m2.metric("Fatigue Index", f"{fatigue:.1f}")
m3.metric("Readiness", f"{readiness:.0f}%")
m4.metric("Pred. Injury", inj_name)

st.divider()

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📊 Squad Load Contrast (Male vs Female)")
    fig_bar = px.bar(df, x='Player', y='Workload', color='Gender', 
                     color_discrete_map={"Male": "#58a6ff", "Female": "#ff7b72"},
                     template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.subheader("💰 Financial ROI (Injury Prevention)")
    days_saved = int(risk_prob * 14)
    money_saved = p['Salary'] * days_saved * (1 - risk_prob)
    st.metric("Estimated Revenue Saved", f"${money_saved:,.0f}", f"+{days_saved} days")

with col_right:
    st.subheader("🦴 3D Biomechanics View")
    fig_3d = go.Figure()
    # Skeleton Line
    fig_3d.add_trace(go.Scatter3d(x=[0,0], y=[2,-2], z=[0,0], mode='lines', line=dict(color='#58a6ff', width=8)))
    # Injury Point
    fig_3d.add_trace(go.Scatter3d(x=[coords[0]], y=[coords[1]], z=[coords[2]], 
                                 mode='markers', marker=dict(size=15, color='red', symbol='diamond')))
    
    fig_3d.update_layout(height=450, paper_bgcolor="#010409", scene_bgcolor="#010409",
                         scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)))
    st.plotly_chart(fig_3d, use_container_width=True)

# ==========================================
# 🧠 7. AI COACH & SPX RECOMMENDATION
# ==========================================
st.divider()
st.subheader("🤖 Spinix AI Coach & SPX Protocol")
q = st.text_input("Ask Coach (e.g., 'What is the recovery plan?')")

if q:
    if "recover" in q.lower() or "علاج" in q.lower():
        st.success(f"Coach: For {player_name}, focus on deep sleep and SPX Magnesium. Recovery time: {int(risk_prob*5)} days.")
    elif "train" in q.lower() or "تمرين" in q.lower():
        status = "No training" if risk_prob > 0.6 else "Light Load" if risk_prob > 0.3 else "Full Intensity"
        st.info(f"Coach: Recommendation is [{status}].")
    else:
        st.write(f"Coach: Risk is {risk_prob*100:.0f}%. Focus on {inj_name} prevention.")

if fatigue > 7:
    st.warning(f"⚠️ SPX ALERT: {player_name} requires immediate BCAA + Recovery suit session.")

st.caption(f"Spinix AI ULTIMATE CORE v15.0 | Dr. Ziad Elshafei Edition | {datetime.now().year}")
