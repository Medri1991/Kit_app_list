import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="עגלה חכמה - ניתוח תקציב", page_icon="📊", layout="wide")

# --- 1. הגדרת תקציב יעד (פיצ'ר חדש) ---
st.sidebar.header("⚙️ הגדרות תקציב")
budget_limit = st.sidebar.number_input("הגדר תקציב חודשי מקסימלי (₪):", value=2500, step=100)

# --- 2. סימולציית נתונים (כדי שיהיה מה לראות בגרף בהתחלה) ---
if 'monthly_history' not in st.session_state:
    st.session_state.monthly_history = [
        {"date": "2024-05-01", "total": 450, "items_count": 22},
        {"date": "2024-05-08", "total": 620, "items_count": 30},
        {"date": "2024-05-15", "total": 310, "items_count": 15},
        {"date": "2024-05-22", "total": 580, "items_count": 25}
    ]

# --- 3. ממשק הטאבים ---
tab1, tab2 = st.tabs(["🛒 ניהול קניות", "📊 מנתח תקציב חזותי"])

with tab1:
    st.info("כאן נמצאים כלי ניהול הרשימה (כפי שבנינו בשלב הקודם).")

with tab2:
    st.header("📊 ניתוח הוצאות חודשי")
    
    if st.session_state.monthly_history:
        df = pd.DataFrame(st.session_state.monthly_history)
        df['date'] = pd.to_datetime(df['date'])
        total_spent = df['total'].sum()
        
        # תצוגת מטרים (Metrics)
        c1, c2, c3 = st.columns(3)
        c1.metric("סה\"כ הוצאה", f"{total_spent:,.2f} ₪")
        
        remaining = budget_limit - total_spent
        color = "normal" if remaining > 0 else "inverse"
        c2.metric("יתרה לתקציב", f"{remaining:,.2f} ₪", delta_color=color)
        
        avg_purchase = df['total'].mean()
        c3.metric("ממוצע לקנייה", f"{avg_purchase:.2f} ₪")

        st.divider()

        # גרף 1: הוצאות לאורך זמן (Line Chart)
        st.subheader("📈 קצב ההוצאות לאורך החודש")
        fig_line = px.line(df, x='date', y='total', markers=True, 
                          labels={'total': 'סכום הקנייה (₪)', 'date': 'תאריך'},
                          title="הוצאות לפי תאריך")
        fig_line.update_traces(line_color='#4CAF50')
        st.plotly_chart(fig_line, use_container_width=True)

        # גרף 2: מדד ניצול תקציב (Gauge/Donut Chart)
        st.subheader("🎯 ניצול תקציב חודשי")
        usage_pct = min((total_spent / budget_limit) * 100, 100)
        
        # יצירת גרף עוגה שמראה ניצול מול יתרה
        budget_df = pd.DataFrame({
            "קטגוריה": ["נוצל", "נותר"],
            "סכום": [total_spent, max(0, remaining)]
        })
        fig_donut = px.pie(budget_df, values='סכום', names='קטגוריה', hole=0.6,
                          color_discrete_map={'נוצל': '#ef5350', 'נותר': '#81c784'})
        st.plotly_chart(fig_donut)

        if total_spent > budget_limit:
            st.error(f"⚠️ חרגת מהתקציב ב-{abs(remaining):,.2f} ₪!")
        elif total_spent > budget_limit * 0.8:
            st.warning("⚡ שים לב: ניצלת מעל 80% מהתקציב החודשי.")

    else:
        st.write("אין עדיין נתונים להצגת גרפים.")
