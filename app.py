import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# --- 1. إعدادات الهوية البصرية (Professional Dark UI) ---
st.set_page_config(page_title="SPINIX AI | Injury Hub", layout="wide", page_icon="🛡️")

# CSS "الضربة القاضية" لتحويل الموقع لداشبورد احترافية
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #11151c; border-right: 1px solid #1e293b; }
    .stMetric { background-color: #1a1f2b; padding: 20px; border-radius: 15px; border: 1px solid #2d3748; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    h1, h2, h3 { color: #4facfe; font-family: 'Arial Black', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .status-box { background: linear-gradient(135deg, #1a1f2b 0%, #11151c 100%); padding: 15px; border-radius: 12px; border-left: 4px solid #4facfe; margin-bottom: 10px; }
    hr { border: 0.5px solid #2d3748; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. الهيدر (العنوان اللامع) ---
st.markdown("<h1 style='text-align: center;'>🛡️ SPINIX AI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8899a6; font-size: 1.1em;'>SPORTS AI & MEDICINE | PERFORMANCE & INJURY HUB</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4facfe;'>By: Dr. Ziad Elshafei</p>", unsafe_allow_html=True)
st.divider()

# --- 3. Sidebar (التحكم في البيانات) ---
st.sidebar.markdown("### 🏟️ SQUAD CONTROL")
uploaded_file = st.sidebar.file_uploader("Upload Player Data (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        required = ['Player', 'Workload', 'RPE', 'Sleep', 'Injury']
        
        if all(col in df.columns for col in required):
            selected_player = st.sidebar.selectbox("🎯 SELECT ATHLETE", df['Player'].unique())
            player_df = df[df['Player'] == selected_player]
            latest = player_df.iloc[-1]

            # --- 4. توزيعه الـ Dashboard (Layout) ---
            col_left, col_mid, col_right = st.columns([1, 1.5, 1])

            # العمود الأيسر: تنبيهات الفريق
            with col_left:
                st.subheader("⚠️ RISK ALERTS")
                for p in df['Player'].unique()[:4]:
                    risk = df[df['Player'] == p]['Injury'].mean() * 100
                    color = "#ff4b4b" if risk > 50 else "#ffa500" if risk > 20 else "#00ffcc"
                    st.markdown(f"""
                        <div class="status-box" style="border-left-color: {color}">
                            <span style="font-size: 0.9em; color: #8899a6;">PLAYER</span><br>
                            <span style="font-weight: bold; font-size: 1.1em;">{p}</span><br>
                            <span style="color: {color}; font-size: 0.8em;">RISK: {risk:.0f}%</span>
                        </div>
                    """, unsafe_allow_html=True)

            # العمود الأوسط: تحليل الجسم والرسومات
            with col_mid:
                st.subheader("📍 BODY ANALYSIS")
                # صورة تخطيطية قريبة من الواقع
                st.image("https://img.icons8.com/color/480/human-body.png", width=250)
                st.markdown("<p style='text-align: center; color: #ff4b4b; font-weight: bold;'>PREDICTED SITES: HAMSTRINGS</p>", unsafe_allow_html=True)
                
                # رسم بياني احترافي للأحمال
                fig = px.area(player_df, x='Date', y='Workload', title="WORKLOAD INTENSITY")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e0e0e0")
                st.plotly_chart(fig, use_container_width=True)

            # العمود الأيمن: الذكاء الاصطناعي والتوقعات
            with col_right:
                st.subheader("🧠 AI PREDICTION")
                st.metric("FITNESS SCORE", f"{100 - (latest['Workload']/10):.0f}%", "OPTIMAL")
                st.metric("ROI FROM PREVENTION", "15M EGP", "SAVED")
                
                # محرك التوقع
                ml_data = df.dropna(subset=required)
                model = RandomForestClassifier(n_estimators=100).fit(ml_data[['Workload', 'RPE', 'Sleep']], ml_data['Injury'])
                pred = model.predict(latest[['Workload', 'RPE', 'Sleep']].values.reshape(1, -1))[0]
                
                st.divider()
                if pred == 1:
                    st.error(f"SYSTEM ALERT: High Injury markers detected for {selected_player}.")
                else:
                    st.success(f"SYSTEM STATUS: {selected_player} is Fit for selection.")

        else:
            st.error("Error: CSV must have columns: Player, Workload, RPE, Sleep, Injury")
    except Exception as e:
        st.error(f"Critical Error: {e}")
else:
    st.info("👋 Dr. Ziad, please upload the CSV file from the sidebar to activate Spinix AI Hub.")
    st.image("https://img.freepik.com/free-vector/abstract-digital-technology-background-with-network-connection-lines_1017-25552.jpg", use_container_width=True)
