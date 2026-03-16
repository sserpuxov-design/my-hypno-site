import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- 1. СТИЛЬ (ТЕМНЫЙ, КОНТРАСТНЫЙ) ---
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    h1, h2, h3 { color: #60a5fa !important; }
    p, span, label { color: #f1f5f9 !important; }
    .stButton>button { background: #3b82f6; color: white !important; width: 100%; border-radius: 8px; }
    /* Карточка */
    .card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ПОДКЛЮЧЕНИЕ ---
TOKEN = "ВАШ_ТОКЕН_ИЗ_BOTFATHER"
CHAT_ID = "ВАШ_CHAT_ID"

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    data = conn.read(ttl="0")
except:
    data = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])

# --- 3. МЕНЮ ---
st.sidebar.title("Меню")
page = st.sidebar.radio("Перейти:", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "Админка"])

# --- 4. ЛОГИКА СТРАНИЦ ---
if page == "Главная":
    st.title("Специалист по гипнозу")
    st.write("Добро пожаловать. Листайте меню слева, чтобы изучить блог или послушать медитации.")

elif page == "Блог":
    st.title("📜 Блог")
    items = data[data["type"] == "Пост"].iloc[::-1]
    for _, row in items.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan": st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    items = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in items.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan": st.audio(row["file_url"])

elif page == "Отзывы":
    st.title("💬 Отзывы клиентов")
    items = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in items.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan":
            if "youtu" in str(row["file_url"]): st.video(row["file_url"])
            else: st.image(row["file_url"])

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        name = st.text_input("Имя")
        contact = st.text_input("Telegram / Телефон")
        msg = st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": f"Заявка!\n{name}\n{contact}\n{msg}"})
            st.success("Отправлено!")

elif page == "Админка":
    st.title("🔒 Вход")
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("add"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("URL файла")
            if st.form_submit_button("Сохранить"):
                new = pd.DataFrame([{"date": "16.03.2026", "type": t, "title": tit, "content": con, "file_url": url}])
                conn.update(data=pd.concat([data, new], ignore_index=True))
                st.success("Сохранено!")
