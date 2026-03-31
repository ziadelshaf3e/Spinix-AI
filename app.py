import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# إعدادات الصفحة وبراند Spinix
st.set_page_config(page_title="Spinix AI - Sports Injury Prediction", layout="wide")
st.title("🛡️ Spinix AI: Sports Injury Prediction")
st.sidebar.image("https://via.placeholder.com/150?text=Spinix+Clinic", width=150) # حط لوجو العيادة هنا
st.sidebar.header("Data Management")

# رفع الملف
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type="csv")

if uploaded_file:
    try:
        # الحل السحري للعربي: utf-8-sig
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        
        # التأكد إن الأعمدة المطلوبة موجودة (عشان ما يطلعش KeyError)
        required_columns = ['Player', 'Workload', 'RPE', 'Sleep', 'Injury']
        if all(col in df.columns for col in required_columns):
            
            # اختيار اللاعب
            player = st.sidebar.selectbox("Select Player", df['Player'].unique())
            player_df = df[df['Player'] == player]
            
            st.subheader(f"📊 Dashboard for: {player}")
            
            # عرض البيانات
            st.dataframe(player_df)

            # جزء الذكاء الاصطناعي (AI Model)
            # تنظيف الداتا أوتوماتيك (عشان ما يطلعش ValueError)
            ml_data = df.dropna(subset=required_columns)
            
            if not ml_data.empty:
                X = ml_data[['Workload', 'RPE', 'Sleep']]
                y = ml_data['Injury']
                
                model = RandomForestClassifier(n_estimators=100)
                model.fit(X, y)
                
                # التوقع لآخر حالة للاعب
                latest_stat = player_df.tail(1)[['Workload', 'RPE', 'Sleep']]
                prediction = model.predict(latest_stat)[0]
                
                st.divider()
                if prediction == 1:
                    st.error(f"⚠️ Spinix AI Warning: {player} is at High Risk of Injury!")
                else:
                    st.success(f"✅ Spinix AI Status: {player} is Fit and Ready.")
            else:
                st.warning("Please provide more data rows to activate AI Prediction.")
        else:
            st.error(f"Missing columns! Make sure your file has: {', '.join(required_columns)}")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("👋 Welcome Dr. Ziad! Please upload the players' CSV file to start analysis.")
    st.markdown("""
    **Required CSV Format:**
    `Date, Player, Workload, RPE, Sleep, Injury`
    """)
