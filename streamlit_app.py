import streamlit as st
import pandas as pd
import requests
import os

# --- НАСТРОЙКИ ---
TOKEN = "ВАШ_ТОКЕН"
CHAT_ID = "ВАШ_CHAT_ID"
DB_FILE = "data.csv"

# Дизайн
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 170px !important; min-width: 170px !important; }
    .stApp { background: #0f172a; color: white; }
    h1, h2, h3 { color: #60a5fa !important; }
    .card { background: rgba(255, 255, 255, 0.07); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# Загрузка данных из файла
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])
    df.to_csv(DB_FILE, index=False)

def load_data():
    return pd.read_csv(DB_FILE)

data = load_data()

# Меню
st.sidebar.title("МЕНЮ")
page = st.sidebar.radio("", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "Админка"])

if page == "Блог":
    st.title("📜 Блог")
    for _, row in data[data["type"] == "Пост"].iloc[::-1].iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p style="color:gray">{row["date"]}</p><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan": st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    for _, row in data[data["type"] == "Медитация"].iloc[::-1].iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan": st.audio(row["file_url"])

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"Заявка: {n}\n{c}\n{m}"})
            st.success("Отправлено!")

elif page == "Админка":
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("add"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка")
            if st.form_submit_button("Сохранить"):
                new = pd.DataFrame([{"date": "16.03.2026", "type": t, "title": tit, "content": con, "file_url": url}])
                new.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success("Готово! Перезагрузите страницу.")
