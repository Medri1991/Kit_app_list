import streamlit as st
import urllib.parse # לייצוג נתונים לכתובות URL

st.set_page_config(page_title="Pantry Planner & Share", page_icon="📸", layout="wide")

# --- 1. מאגר נתונים (מצרכים, מחירים, מתכונים עם תמונות) ---
ingredients_market = {
    "ירקות ופירות 🍅": {"עגבניות": 6, "מלפפונים": 5, "בצל": 5, "שום": 12, "תפוחי אדמה": 6, "גזר": 5, "לימון": 8},
    "בשר ודגים 🥩": {"חזה עוף": 35, "בשר טחון": 50, "פילה סלמון": 90, "טונה בשמן": 6, "אמנון": 35},
    "חלב וביצים 🧀": {"ביצים": 13, "חלב": 7, "חמאה": 8, "גבינה צהובה": 15, "שמנת מתוקה": 7, "פרמזן": 25},
    "מזווה 🥫": {"אורז": 9, "פסטה": 6, "קמח": 5, "סוכר": 4, "שמן זית": 45, "רסק עגבניות": 3, "קרם קוקוס": 10},
    "פרימיום ✨": {"שמן כמהין": 60, "יין לבן": 40, "צנוברים": 25, "אגוזי מלך": 15, "שוקולד מריר": 10}
}

recipes = [
    {"שם": "פסטה בולונז", "חובה": ["פסטה", "בשר טחון", "בצל", "רסק עגבניות"], "image": "https://images.unsplash.com/photo-1546545229-ef2797686523?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"שם": "סלמון בתנור", "חובה": ["פילה סלמון", "לימון", "שום"], "image": "https://images.unsplash.com/photo-1599026330089-0ed5c083697e?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"שם": "אורז קוקוס ועוף", "חובה": ["אורז", "חזה עוף", "קרם קוקוס"], "image": "https://images.unsplash.com/photo-1600891963283-a4422e11e03c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"שם": "שקשוקה", "חובה": ["ביצים", "עגבניות", "בצל", "שום"], "image": "https://images.unsplash.com/photo-1616439567950-c8e54e4c29d6?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"שם": "מוס שוקולד", "חובה": ["שוקולד מריר", "שמנת מתוקה"], "image": "https://images.unsplash.com/photo-1629859591942-1e9d1a38c92a?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"}
]

# יצירת מילון מחירים שטוח
price_dict = {item: price for cat in ingredients_market.values() for item, price in cat.items()}

# --- 2. ניהול המצב (State) של האפליקציה ---
if 'weekly_plan' not in st.session_state:
    st.session_state.weekly_plan = []

# --- 3. פונקציות שיתוף לוואטסאפ ---
def generate_whatsapp_link(text_message):
    """יוצר לינק לוואטסאפ עם הודעה מוכנה."""
    encoded_text = urllib.parse.quote(text_message)
    return f"https://wa.me/?text={encoded_text}"

def generate_shopping_list_message(plan, pantry, prices_dict):
    """מרכז את רשימת הקניות להודעת וואטסאפ."""
    message_parts = ["רשימת קניות שבועית מ'שף המזווה':\n"]
    
    all_missing_items_raw = []
    for r in plan:
        missing = [item for item in r["חובה"] if item not in pantry]
        all_missing_items_raw.extend(missing)
    
    unique_missing = sorted(list(set(all_missing_items_raw))) # מיון לקריאות טובה יותר
    
    total_cost = 0
    if unique_missing:
        message_parts.append("\n🛒 מצרכים שצריך לקנות:\n")
        for m in unique_missing:
            p = prices_dict.get(m, 0)
            total_cost += p
            message_parts.append(f"- {m} (~{p}₪)")
        message_parts.append(f"\nסה\"כ עלות משוערת: {total_cost}₪")
    else:
        message_parts.append("✅ יש לך את כל המצרכים! 0₪ הוצאה.")
    
    message_parts.append("\nבתיאבון!")
    return "\n".join(message_parts)

# --- 4. ממשק משתמש ---
st.title("📅 מתכנן ארוחות ושיתוף בוואטסאפ")

col_pantry, col_recipes, col_summary = st.columns([1, 1.5, 1])

# עמודה 1: המזווה שלי
with col_pantry:
    st.header("🛒 המזווה שלי")
    user_pantry = []
    for cat, items in ingredients_market.items():
        with st.expander(cat):
            for item in items:
                if st.checkbox(item, key=f"pantry_{item}"):
                    user_pantry.append(item)
    user_pantry_set = set(user_pantry)

# עמודה 2: בחירת מנות לשבוע
with col_recipes:
    st.header("🍳 בחר מנות לתפריט")
    for r in recipes:
        missing = [i for i in r["חובה"] if i not in user_pantry_set]
        cost = sum(price_dict.get(m, 0) for m in missing)
        
        with st.container(border=True): # מעטפת עם מסגרת לכל מתכון
            st.image(r['image'], width=250, caption=r['שם'])
            st.write(f"**{r['שם']}**")
            if not missing:
                st.caption("✅ יש לך הכל!")
            else:
                st.caption(f"❌ חסר: {', '.join(missing)} (עלות: {cost}₪)")
            
            c1_btn, c2_btn = st.columns(2)
            if c1_btn.button("הוסף לתפריט", key=f"add_{r['שם']}", use_container_width=True):
                st.session_state.weekly_plan.append(r)
                st.toast(f"'{r['שם']}' נוספה לתפריט!")
            
            # כפתור שיתוף מנה בודדת
            dish_share_msg = f"רעיון לארוחה מ'שף המזווה': *{r['שם']}*\n\n" \
                             f"מצרכי חובה: {', '.join(r['חובה'])}.\n"
            if missing:
                dish_share_msg += f"חסרים לי: {', '.join(missing)}.\n"
            dish_share_msg += f"תמונה: {r['image']}"
            
            c2_btn.link_button("שתף מנה ↗️", url=generate_whatsapp_link(dish_share_msg), use_container_width=True)

# עמודה 3: סיכום ורשימת קניות
with col_summary:
    st.header("📝 סיכום שבועי")
    if st.session_state.weekly_plan:
        total_cost = 0
        all_missing_items_raw = []
        
        st.write("**המנות שנבחרו:**")
        for i, r in enumerate(st.session_state.weekly_plan):
            st.write(f"{i+1}. {r['שם']}")
            missing = [item for item in r["חובה"] if item not in user_pantry_set]
            all_missing_items_raw.extend(missing)
        
        if st.button("נקה תפריט"):
            st.session_state.weekly_plan = []
            st.rerun() # מרענן את העמוד כדי לעדכן את המצב
            
        st.divider()
        
        # רשימת קניות מרוכזת (בלי כפילויות)
        unique_missing = sorted(list(set(all_missing_items_raw))) # מיון לקריאות טובה יותר
        if unique_missing:
            st.subheader("🛒 רשימת קניות מרוכזת:")
            for m in unique_missing:
                p = price_dict.get(m, 0)
                total_cost += p
                st.write(f"- {m} (~{p}₪)")
            
            st.metric("סה\"כ עלות משוערת", f"{total_cost} ₪")
            
            # כפתור שיתוף רשימת קניות בוואטסאפ
            whatsapp_message = generate_shopping_list_message(st.session_state.weekly_plan, user_pantry_set, price_dict)
            st.markdown(f'<a href="{generate_whatsapp_link(whatsapp_message)}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #25d366; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold;">שלח רשימת קניות בוואטסאפ ↗️</a>', unsafe_allow_html=True)
            
            # הסבר על יצירת קבוצה
            st.caption("💡 כדי לשתף בקבוצה קיימת או ליצור חדשה: לחצו על הכפתור, בחרו איש קשר או קבוצה קיימת, ואז תוכלו להוסיף אנשים נוספים מתוך וואטסאפ.")

        else:
            st.success("✅ יש לך את כל המצרכים לכל המנות שבחרת! (0 ₪ הוצאה)")
    else:
        st.write("התפריט שלך ריק. הוסף מנות מהרשימה המרכזית.")
