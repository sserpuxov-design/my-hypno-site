import streamlit as st
import pandas as pd
import requests
import os

# --- НАСТРОЙКИ ---
TOKEN = "ВАШ_ТОКЕН"
CHAT_ID = "ВАШ_CHAT_ID"
DB_FILE = "data.csv"

# 1. ДИЗАЙН
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 180px !important; min-width: 180px !important; }
    .stApp { background: #0f172a; color: white; }
    h1, h2, h3 { color: #60a5fa !important; font-weight: 700; }
    p, span, label, div { color: #ffffff !important; }
    .card { 
        background: rgba(255, 255, 255, 0.07); 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
    }
    .stButton>button { background: #3b82f6; color: white !important; border-radius: 8px; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. РАБОТА С ДАННЫМИ
def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])
        df.to_csv(DB_FILE, index=False)
        return df
    try:
        return pd.read_csv(DB_FILE).fillna("")
    except:
        return pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])

data = load_data()

# 3. МЕНЮ
st.sidebar.title("💎 МЕНЮ")
page = st.sidebar.radio("", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

# 4. СТРАНИЦЫ
if page == "Главная":
    st.title("Специалист по гипнозу")
    st.write("Добро пожаловать. Используйте меню слева для навигации.")

elif page == "Блог":
    st.title("📜 Блог")
    posts = data[data["type"] == "Пост"].iloc[::-1]
    for _, row in posts.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p style="color:#94a3b8">{row["date"]}</p><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]: st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    meds = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in meds.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]: st.audio(row["file_url"])

elif page == "Отзывы":
    st.title("💬 Отзывы клиентов")
    revs = data[data["type"] == "Отзыв"].iloc[::-1]
    if len(revs) == 0:
        st.info("Отзывов пока нет. Зайдите в Админку, чтобы добавить первый.")
    for _, row in revs.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]:
            if "youtu" in str(row["file_url"]): st.video(row["file_url"])
            else: st.image(row["file_url"])

elif page == "Записаться":
    st.title("📅 Запись на сеанс")
    with st.form("order"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"Заявка!\nИмя: {n}\nСвязь: {c}\nЗапрос: {m}"})
            st.success("Отправлено!")

elif page == "🔒 Админка":
    st.title("Управление")
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("add", clear_on_submit=True):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка на файл")
            submit = st.form_submit_button("Опубликовать")
            
            if submit:
                new_data = pd.DataFrame([{
                    "date": pd.Timestamp.now().strftime("%d.%m.%Y"),
                    "type": t, "title": tit, "content": con, "file_url": url.strip()
                }])
                new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success("Данные сохранены!")
                st.rerun() # ПРИНУДИТЕЛЬНАЯ ПЕРЕЗАГРУЗКА
