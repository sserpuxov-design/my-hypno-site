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
    .card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { background: #3b82f6; color: white !important; border-radius: 8px; width: 100%; border: none; }
    .auth-badge { font-size: 0.7em; background: #0ea5e9; color: white; padding: 2px 8px; border-radius: 10px; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. ДАННЫЕ
def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE).fillna("")

def save_item(t, tit, con, url):
    new_row = pd.DataFrame([{"date": pd.Timestamp.now().strftime("%d.%m.%Y"), "type": t, "title": tit, "content": con, "file_url": url.strip()}])
    new_row.to_csv(DB_FILE, mode='a', header=False, index=False)

data = load_data()

# 3. МЕНЮ
st.sidebar.title("💎 ГИПНОЗ")
page = st.sidebar.radio("", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

# 4. ЛОГИКА СТРАНИЦ
if page == "Отзывы":
    st.title("💬 Отзывы клиентов")

    # ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ
    # В Streamlit Cloud st.user содержит данные, если включена авторизация в настройках
    user = st.user 

    if user:
        with st.expander(f"✅ Вы вошли как {user.email}. Оставить отзыв"):
            with st.form("confirmed_review", clear_on_submit=True):
                u_text = st.text_area("Ваш текст")
                if st.form_submit_button("Опубликовать"):
                    if u_text:
                        # Берем имя из почты (до @)
                        u_name = user.email.split('@')[0]
                        save_item("Отзыв", u_name, u_text, user.email)
                        
                        # Сообщение вам
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                      json={"chat_id": CHAT_ID, "text": f"✅ РЕАЛЬНЫЙ ОТЗЫВ!\nОт: {user.email}\nТекст: {u_text}"})
                        st.success("Отзыв добавлен!")
                        st.rerun()
    else:
        st.info("Чтобы оставить отзыв от своего имени, пожалуйста, авторизуйтесь в системе Streamlit (кнопка в правом верхнем углу или в меню приложения).")
        st.write("Это нужно, чтобы мы знали, что вы реальный человек.")

    # ВЫВОД
    revs = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in revs.iterrows():
        st.markdown(f'''
            <div class="card">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <b style="color: #60a5fa;">👤 {row["title"]}</b>
                    <span class="auth-badge">Подтвержден аккаунтом</span>
                </div>
                <div>{row["content"]}</div>
            </div>
        ''', unsafe_allow_html=True)

# Код остальных вкладок
elif page == "Главная":
    st.title("Специалист по гипнозу")
    st.write("Трансформация через подсознание.")

elif page == "Блог":
    st.title("📜 Блог")
    posts = data[data["type"] == "Пост"].iloc[::-1]
    for _, row in posts.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p style="color:gray">{row["date"]}</p><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]: st.image(row["file_url"])

elif page == "Медитации":
    st.title("🎧 Медитации")
    meds = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in meds.iterrows():
        st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
        if row["file_url"]: st.audio(row["file_url"])

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"ЗАЯВКА!\n{n}\n{c}\n{m}"})
            st.success("Отправлено!")

elif page == "🔒 Админка":
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("adm"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit, con, url = st.text_input("Заголовок"), st.text_area("Текст"), st.text_input("Ссылка")
            if st.form_submit_button("Сохранить"):
                save_item(t, tit, con, url)
                st.success("Сохранено!")
                st.rerun()
