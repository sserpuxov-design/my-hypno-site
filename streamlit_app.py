import streamlit as st
import pandas as pd
import requests
import os
import hashlib

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
    .card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { background: #3b82f6; color: white !important; border-radius: 8px; width: 100%; border: none; }
    /* Стиль для ника */
    .user-nick { color: #38bdf8; font-weight: bold; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# 2. ФУНКЦИИ
def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE).fillna("")

def save_item(t, tit, con, url):
    new_row = pd.DataFrame([{"date": pd.Timestamp.now().strftime("%d.%m.%Y"), "type": t, "title": tit, "content": con, "file_url": url.strip()}])
    new_row.to_csv(DB_FILE, mode='a', header=False, index=False)

# Генерируем "отпечаток" пользователя, чтобы ты его узнал
user_id = hashlib.md5(str(st.context.headers.get("User-Agent", "unknown")).encode()).hexdigest()[:8]

data = load_data()

# 3. МЕНЮ
st.sidebar.title("💎 ГИПНОЗ")
page = st.sidebar.radio("", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

# 4. СТРАНИЦЫ
if page == "Отзывы":
    st.title("💬 Отзывы клиентов")
    
    # Кнопка-спойлер (сама свернется после обновления)
    with st.expander("✨ Написать отзыв"):
        with st.form("user_review", clear_on_submit=True):
            u_name = st.text_input("Ваше имя или @никнейм")
            u_text = st.text_area("Что вы почувствовали после сеанса?")
            submit = st.form_submit_button("Опубликовать")
            
            if submit:
                if u_name and u_text:
                    save_item("Отзыв", u_name, u_text, "")
                    # Отправляем тебе в ТГ с пометкой ID
                    msg = f"🌟 НОВЫЙ ОТЗЫВ!\nОт: {u_name}\nТекст: {u_text}\n(ID устройства: {user_id})"
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg})
                    st.success("Готово! Ваш отзыв добавлен.")
                    st.rerun() # Страница обновится, форма свернется автоматически
                else:
                    st.error("Заполните имя и текст!")

    # Вывод
    revs = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in revs.iterrows():
        # Если в имени есть @, подсвечиваем его
        display_name = f'<span class="user-nick">{row["title"]}</span>' if "@" in str(row["title"]) else row["title"]
        st.markdown(f'''
            <div class="card">
                <div style="margin-bottom:10px;">👤 {display_name}</div>
                <div style="font-size:1.1em; line-height:1.4;">{row["content"]}</div>
            </div>
        ''', unsafe_allow_html=True)
        if row["file_url"]: st.image(row["file_url"])

elif page == "Главная":
    st.title("Добро пожаловать")
    st.write("Трансформация сознания начинается здесь.")

elif page == "Блог":
    st.title("📜 Блог")
    for _, row in data[data["type"] == "Пост"].iloc[::-1].iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p style="color:gray">{row["date"]}</p><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]: st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    for _, row in data[data["type"] == "Медитация"].iloc[::-1].iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]: st.audio(row["file_url"])

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"ЗАЯВКА!\n{n}\n{c}\n{m}\n(ID: {user_id})"})
            st.success("Ваша заявка в обработке!")

elif page == "🔒 Админка":
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("adm"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit, con, url = st.text_input("Заголовок"), st.text_area("Текст"), st.text_input("Ссылка")
            if st.form_submit_button("Сохранить"):
                save_item(t, tit, con, url)
                st.success("Сохранено!")
                st.rerun()
