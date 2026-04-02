import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import cv2
import tempfile
import openai  # لازم تسطبها: pip install openai

# ==========================================
# 🎨 UI & THEME
# ==========================================
st.set_page_config(layout="wide", page_title="SPINIX AI - GPT MODE")

st.markdown("""
<style>
    .main { background: #010409; color: #c9d1d9; }
    .stChatFloatingInputContainer { background-color: #0d1117 !important; }
    .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 15px; }
    h1, h2 { color: #58a6ff !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 DATA (Squad Data)
# ==========================================
@st.cache_data
def get_data():
    return pd.DataFrame({
        "Player": ["Ziad", "Sara", "Mohamed", "Nour", "Tarek"],
        "Status": ["Ready", "Optimal", "Danger", "Caution", "Overload"],
        "Risk": [15, 5, 85, 45, 90],
        "Readiness": [90, 98, 20, 65, 10]
    })

df = get_data()
player = st.sidebar.selectbox("Select Athlete", df['Player'])
p_data = df[df['Player'] == player].iloc[0]

# ==========================================
# 🏟️ DASHBOARD METRICS
# ==========================================
st.title(f"🚀 Spinix Intelligence Hub")
c1, c2, c3 = st.columns(3)
c1.metric("Current Athlete", player)
c2.metric("Injury Risk", f"{p_data['Risk']}%")
c3.metric("System Status", "AI Online")

st.divider()

# ==========================================
# 🤖 THE AI COACH (GPT MODE)
# ==========================================
st.subheader("💬 Spinix AI Coach (Ask me anything)")

# مكان لوضع الـ API Key الخاص بك (اختياري)
api_key = st.text_input("Enter OpenAI API Key (Optional for Full GPT Mode)", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# إدخال السؤال
if prompt := st.chat_input("Ask about training, recovery, or medical advice..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # 1. إذا كان اليوزر حاطط API Key (يشتغل كـ ChatGPT حقيقي)
        if api_key:
            try:
                openai.api_key = api_key
                client = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a World-Class Sports Scientist at Spinix Clinic. Current athlete context: {player} has a risk of {p_data['Risk']}% and status is {p_data['Status']}."},
                        {"role": "user", "content": prompt}
                    ]
                )
                full_response = client.choices[0].message.content
            except Exception as e:
                full_response = f"API Error: {e}. Please check your key."
        
        # 2. إذا مفيش API Key (يشتغل بالذكاء المدمج)
        else:
            if "تمرين" in prompt.lower() or "train" in prompt.lower():
                if p_data['Risk'] > 70:
                    full_response = f"يا دكتور زياد، اللاعب {player} حالته خطر ({p_data['Risk']}%). أي تمرين دلوقتي غلط، لازم راحة تامة وجلسة استشفاء بمنتجات SPX."
                else:
                    full_response = f"اللاعب {player} جاهز بنسبة ممتازة. ممكن نشتغل تمرين شدة عالية (High Intensity) النهاردة."
            elif "إصابة" in prompt.lower() or "injury" in prompt.lower():
                full_response = f"بناءً على تحليلي لـ {player}، هو معرض لإصابة في العضلة الخلفية بسبب الحمل الزائد."
            else:
                full_response = "أنا Spinix AI، حالياً شغال بالنمط المحدود. لو عايزني أجاوب على أي حاجة زي ChatGPT، حط الـ API Key بتاعك فوق!"

        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# ==========================================
# 📊 VISUAL ANALYTICS (Optional)
# ==========================================
with st.expander("See Analytics"):
    fig = px.pie(df, values='Risk', names='Player', hole=0.4, title="Squad Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Spinix AI v17.0 | Powered by Dr. Ziad Elshafei")
