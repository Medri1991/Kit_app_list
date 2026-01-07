import streamlit as st
import urllib.parse

st.set_page_config(page_title="Pantry Chef Pro", page_icon="👨‍🍳", layout="wide")

# --- 1. מאגר נתונים וערכים קלוריים ---
ingredients_db = {
    "ירקות ופירות 🍅": {"עגבניות": 18, "מלפפונים": 15, "בצל": 40, "שום": 149, "תפוחי אדמה": 77, "גזר": 41, "לימון": 29, "פטרוזיליה": 36},
    "קצביה ודגים 🥩": {"חזה עוף": 165, "בשר טחון": 250, "פילה סלמון": 208, "אמנון": 128},
    "חלב וביצים 🧀": {"ביצים": 155, "חלב": 60, "חמאה": 717, "גבינה צהובה": 350, "גבינה לבנה": 98},
    "מזווה ויבש 🥫": {"אורז": 130, "פסטה": 131, "קמח": 364, "סוכר": 387, "שמן זית": 884, "רסק עגבניות": 82, "פירורי לחם": 395},
    "תבלינים 🧂": {"מלח": 0, "פלפל שחור": 250, "פפריקה": 280, "כמון": 370, "סילאן": 280}
}

recipes = [
    {"שם": "פסטה בולונז", "חובה": ["פסטה", "בשר טחון", "בצל", "רסק עגבניות"], "calories": 650, "image": "https://images.unsplash.com/photo-1546545229-ef2797686523?w=500"},
    {"שם": "סלמון בתנור", "חובה": ["פילה סלמון", "לימון", "שום", "שמן זית"], "calories": 450, "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500"},
    {"שם": "שקשוקה ביתית", "חובה": ["ביצים", "עגבניות", "בצל", "שמן זית"], "calories": 350, "image": "https://images.unsplash.com/photo-1590412200988-a436bb715048?w=500"},
    {"שם": "שניצל ופירה", "חובה": ["חזה עוף", "פירורי לחם", "ביצים", "תפוחי אדמה"], "calories": 720, "image": "https://images.unsplash.com/photo-1594759844614-3c2761b15ad3?w=500"}
]

# --- 2. ניהול מצב (Session State) ---
# אתחול המזווה בזיכרון אם הוא לא קיים
if 'my_pantry' not in st.session_state:
    st.session_state.my_pantry = []
if 'weekly_plan' not in st.session_state:
    st.session_state.weekly_plan = []

# --- 3. ממשק משתמש ---
st.title("👨‍🍳 עוזר המטבח החכם")

tab1, tab2, tab3 = st.tabs(["🛒 מה יש לי?", "📖 מה אפשר לבשל?", "🗓️ התפריט שלי"])

# --- טאב 1: ניהול המזווה ---
with tab1:
    st.info("סמן את המוצרים שיש לך בבית. הבחירות שלך נשמרות אוטומטית.")
    
    # תצוגת מזווה
    cols = st.columns(3)
    current_pantry = []
    
    for i, (cat, items) in enumerate(ingredients_db.items()):
        with cols[i % 3]:
            st.subheader(cat)
            for item in items:
                # בדיקה אם הפריט כבר היה מסומן בזיכרון
                is_selected = item in st.session_state.my_pantry
                if st.checkbox(item, value=is_selected, key=f"pantry_cb_{item}"):
                    current_pantry.append(item)
    
    # עדכון הזיכרון
    st.session_state.my_pantry = current_pantry
    
    if st.button("רענן נתונים ועדכן מתכונים"):
        st.rerun()

# --- טאב 2: ספר מתכונים חכם ---
with tab2:
    pantry_set = set(st.session_state.my_pantry)
    
    # סינון מתכונים: בודק כמה מצרכים חסרים
    # נאפשר להראות מתכונים שחסר להם עד 1 מצרך (כדי שלא יהיה ריק)
    st.subheader("מתכונים שמתאימים למזווה שלך:")
    
    available_recipes = []
    for r in recipes:
        missing = [ing for ing in r["חובה"] if ing not in pantry_set]
        if len(missing) == 0:
            available_recipes.append((r, "מוכן להכנה! ✅"))
        elif len(missing) == 1:
            available_recipes.append((r, f"חסר רק: {missing[0]}"))

    if not available_recipes:
        st.warning("המזווה שלך ריק מדי. סמן מוצרים בטאב הראשון כדי לראות כאן מתכונים.")
    else:
        grid = st.columns(2)
        for idx, (r, status) in enumerate(available_recipes):
            with grid[idx % 2]:
                with st.container(border=True):
                    st.image(r['image'], use_container_width=True)
                    st.subheader(r['שם'])
                    st.write(f"**מצב:** {status}")
                    if st.button(f"הוסף לתפריט", key=f"btn_{idx}_{r['שם']}"):
                        st.session_state.weekly_plan.append(r)
                        st.success(f"{r['שם']} נוסף לתפריט!")

# --- טאב 3: סיכום וערכים ---
with tab3:
    if not st.session_state.weekly_plan:
        st.info("התפריט ריק. הוסף מנות בטאב 'מה אפשר לבשל'.")
    else:
        total_cal = 0
        for i, r in enumerate(st.session_state.weekly_plan):
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"**{i+1}. {r['שם']}** ({r['calories']} קלוריות)")
            if col_b.button("הסר", key=f"del_{i}"):
                st.session_state.weekly_plan.pop(i)
                st.rerun()
            total_cal += r['calories']
        
        st.divider()
        st.metric("סה\"כ קלוריות שבועי", f"{total_cal} קק\"ל")
        
        if st.button("איפוס תפריט שבועי"):
            st.session_state.weekly_plan = []
            st.rerun()
