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
    section[data-testid="stSidebar"] { width: 170px !important; min-width: 170px !important; }
    .stApp { background: #0f172a; color: white; }
    h1, h2, h3 { color: #60a5fa !important; }
    .card { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
    }
    .stButton>button { background: #3b82f6; color: white !important; border-radius: 8px; width: 100%; border: none; }
    img { border-radius: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. РАБОТА С ДАННЫМИ
def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])
        df.to_csv(DB_FILE, index=False)
        return df
    try:
        # Читаем файл и принудительно заменяем все пустоты на пустую строку
        df = pd.read_csv(DB_FILE).fillna("")
        return df
    except:
        return pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])

data = load_data()

# 3. МЕНЮ
st.sidebar.title("💎 МЕНЮ")
page = st.sidebar.radio("", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

# 4. СТРАНИЦЫ
if page == "Главная":
    st.title("Специалист по гипнозу")
    st.write("Используйте меню слева для навигации.")

elif page == "Блог":
    st.title("📜 Блог")
    posts = data[data["type"] == "Пост"].iloc[::-1]
    for _, row in posts.iterrows():
        with st.container():
            st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p style="color:#94a3b8">{row["date"]}</p><p>{row["content"]}</p></div>', unsafe_allow_html=True)
            if row["file_url"] and str(row["file_url"]).strip() != "":
                st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    meds = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in meds.iterrows():
        with st.container():
            st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
            if row["file_url"] and str(row["file_url"]).strip() != "":
                st.audio(row["file_url"])

elif page == "Отзывы":
    st.title("💬 Отзывы клиентов")
    revs = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in revs.iterrows():
        with st.container():
            # Выводим заголовок (имя) и текст отзыва, только если они не пустые
            title_html = f'<h3>{row["title"]}</h3>' if row["title"] else ""
            content_html = f'<p>{row["content"]}</p>' if row["content"] else ""
            
            if title_html or content_html:
                st.markdown(f'<div class="card">{title_html}{content_html}</div>', unsafe_allow_html=True)
            
            # Выводим картинку (скриншот), если ссылка есть
            url = str(row["file_url"]).strip()
            if url and url != "":
                if "youtu" in url:
                    st.video(url)
                else:
                    st.image(url, caption="Скриншот отзыва")

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"Заявка!\n{n}\n{c}\n{m}"})
            st.success("Отправлено!")

elif page == "🔒 Админка":
    st.title("Управление")
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("add", clear_on_submit=True):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка на файл")
            if st.form_submit_button("Опубликовать"):
                # Собираем новую строку
                new_row = pd.DataFrame([{
                    "date": pd.Timestamp.now().strftime("%d.%m.%Y"),
                    "type": t, "title": tit, "content": con, "file_url": url.strip()
                }])
                # Дописываем в файл
                new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success("Сохранено!")
                st.rerun()
