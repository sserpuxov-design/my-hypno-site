import streamlit as st
import pandas as pd
import requests
import os

# --- НАСТРОЙКИ ---
TOKEN = "ВАШ_ТОКЕН"
CHAT_ID = "ВАШ_CHAT_ID"
DB_FILE = "data.csv"

# 1. ДИЗАЙН (Все прозрачно и понятно)
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 170px !important; min-width: 170px !important; }
    .stApp { background: #0f172a; color: white; }
    h1, h2, h3 { color: #60a5fa !important; }
    .card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { background: #3b82f6; color: white !important; border-radius: 8px; width: 100%; border: none; }
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
if page == "Главная":
    st.title("Добро пожаловать")
    st.write("Вы здесь, чтобы изменить свою реальность. Посмотрите мои статьи или послушайте медитации в меню слева.")

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

elif page == "Отзывы":
    st.title("💬 Отзывы")
    
    # Кнопка для всех без входа!
    with st.expander("✨ Оставить свой отзыв"):
        with st.form("simple_review", clear_on_submit=True):
            name = st.text_input("Ваше имя или ник в соцсетях")
            text = st.text_area("Ваши впечатления")
            social_link = st.text_input("Ссылка на ваш профиль (по желанию, для доверия)")
            if st.form_submit_button("Опубликовать"):
                if name and text:
                    # Сохраняем отзыв. В поле file_url запишем ссылку на соцсеть, если она есть
                    save_item("Отзыв", name, text, social_link)
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"🌟 НОВЫЙ ОТЗЫВ!\nОт: {name}\nТекст: {text}"})
                    st.success("Спасибо! Ваш отзыв добавлен.")
                    st.rerun()

    # Показываем отзывы
    for _, row in data[data["type"] == "Отзыв"].iloc[::-1].iterrows():
        with st.container():
            # Если есть ссылка на соцсеть, делаем имя кликабельным
            header = f'<a href="{row["file_url"]}" style="text-decoration:none; color:#60a5fa;">👤 {row["title"]}</a>' if "http" in str(row["file_url"]) else f'👤 {row["title"]}'
            st.markdown(f'<div class="card"><h3>{header}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)

elif page == "Записаться":
    st.title("📅 Запись")
    with st.form("order"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("Отправить"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"Заявка!\n{n}\n{c}\n{m}"})
            st.success("Заявка отправлена!")

elif page == "🔒 Админка":
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("admin_add"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit, con, url = st.text_input("Заголовок"), st.text_area("Текст"), st.text_input("Ссылка")
            if st.form_submit_button("Сохранить"):
                save_item(t, tit, con, url)
                st.success("Готово!")
                st.rerun()
