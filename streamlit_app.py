import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- 1. ПОЛНЫЙ ДИЗАЙН (УЗКОЕ МЕНЮ И КОНТРАСТ) ---
st.markdown("""
    <style>
    /* Сужаем боковую панель */
    section[data-testid="stSidebar"] {
        width: 170px !important;
        min-width: 170px !important;
        max-width: 170px !important;
    }
    
    /* Основной фон и текст */
    .stApp { background: #0f172a; color: #ffffff; }
    
    /* Заголовки - ярко-голубые */
    h1, h2, h3 { color: #60a5fa !important; font-weight: 700; }
    
    /* Весь обычный текст - белый */
    p, span, label, div { color: #ffffff !important; }

    /* Карточки постов */
    .card {
        background: rgba(255, 255, 255, 0.07);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* Кнопка */
    .stButton>button {
        background: #3b82f6;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. НАСТРОЙКИ СВЯЗИ (ЗАМЕНИТЕ НА СВОИ) ---
# Если не вставите свои данные ниже, форма записи не будет работать!
TOKEN = "ВАШ_ТОКЕН_ИЗ_BOTFATHER"
CHAT_ID = "ВАШ_CHAT_ID"

# Подключение к таблице
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    data = conn.read(ttl="0")
except:
    data = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])

# --- 3. БОКОВОЕ МЕНЮ ---
st.sidebar.markdown("### МЕНЮ")
page = st.sidebar.radio("", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

# --- 4. КОНТЕНТ СТРАНИЦ ---

if page == "Главная":
    st.title("Специалист по гипнозу")
    st.write("Добро пожаловать в пространство глубокой трансформации.")
    st.write("Используйте меню слева, чтобы изучить материалы.")

elif page == "Блог":
    st.title("📜 Статьи")
    items = data[data["type"] == "Пост"].iloc[::-1]
    for _, row in items.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan" and row["file_url"]:
            st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    items = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in items.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan" and row["file_url"]:
            st.audio(row["file_url"])

elif page == "Отзывы":
    st.title("💬 Отзывы")
    items = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in items.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if str(row["file_url"]) != "nan" and row["file_url"]:
            if "youtu" in str(row["file_url"]): st.video(row["file_url"])
            else: st.image(row["file_url"])

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        name = st.text_input("Ваше имя")
        contact = st.text_input("Ваш Telegram или Телефон")
        msg = st.text_area("Ваш запрос")
        if st.form_submit_button("Отправить заявку"):
            txt = f"🔔 НОВАЯ ЗАЯВКА!\n👤 {name}\n📞 {contact}\n📝 {msg}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": txt})
            st.success("Данные успешно отправлены!")

elif page == "🔒 Админка":
    st.title("Вход для автора")
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("add_content"):
            t = st.selectbox("Тип контента", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка (URL) на фото или аудио")
            if st.form_submit_button("Опубликовать"):
                new_row = pd.DataFrame([{"date": "16.03.2026", "type": t, "title": tit, "content": con, "file_url": url}])
                conn.update(data=pd.concat([data, new_row], ignore_index=True))
                st.success("Опубликовано! Обновите страницу, чтобы увидеть результат.")
