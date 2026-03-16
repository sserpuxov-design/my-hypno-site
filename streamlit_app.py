import streamlit as st
import pandas as pd
import requests
import os

# --- НАСТРОЙКИ (ЗАПОЛНИТЕ СВОИ) ---
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
    .review-form { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. ФУНКЦИИ ДАННЫХ
def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])
        df.to_csv(DB_FILE, index=False)
        return df
    try:
        return pd.read_csv(DB_FILE).fillna("")
    except:
        return pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])

def save_item(t, tit, con, url):
    new_row = pd.DataFrame([{
        "date": pd.Timestamp.now().strftime("%d.%m.%Y"),
        "type": t, "title": tit, "content": con, "file_url": url.strip()
    }])
    new_row.to_csv(DB_FILE, mode='a', header=False, index=False)

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
    
    # КНОПКА И ФОРМА ДЛЯ КЛИЕНТА
    with st.expander("➕ Оставить свой отзыв"):
        with st.form("client_review", clear_on_submit=True):
            name = st.text_input("Ваше имя")
            text = st.text_area("Ваш отзыв")
            photo = st.text_input("Ссылка на фото (необязательно)")
            if st.form_submit_button("Опубликовать отзыв"):
                if name and text:
                    save_item("Отзыв", name, text, photo)
                    # Опционально: уведомление вам в Telegram о новом отзыве
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": f"🌟 Новый отзыв на сайте от: {name}"})
                    st.success("Спасибо! Ваш отзыв опубликован.")
                    st.rerun()
                else:
                    st.error("Пожалуйста, введите имя и текст отзыва.")

    # ВЫВОД ОТЗЫВОВ
    revs = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in revs.iterrows():
        with st.container():
            st.markdown(f'<div class="card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
            if row["file_url"]:
                st.image(row["file_url"], caption=f"Фото от {row['title']}")

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
        with st.form("add_admin", clear_on_submit=True):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка на файл")
            if st.form_submit_button("Опубликовать"):
                save_item(t, tit, con, url)
                st.success("Сохранено!")
                st.rerun()
