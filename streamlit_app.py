import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- КОНФИГУРАЦИЯ ---
TOKEN = "ВАШ_ТОКЕН_БОТА"  # Получите у @BotFather
CHAT_ID = "ВАШ_CHAT_ID"    # Получите у @userinfobot
ADMIN_PASSWORD = "admin"  # Смените на свой пароль для входа

st.set_page_config(page_title="Гипнолог: Глубинная Трансформация", layout="centered")

# Функция отправки в Telegram
def send_tg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    except:
        pass

# Подключение базы данных (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0") # Мы отключаем кэш, чтобы данные обновлялись сразу

# --- ГЛАВНОЕ МЕНЮ ---
st.sidebar.title("Навигация")
page = st.sidebar.radio("Перейти:", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

data = load_data()

# --- СТРАНИЦЫ ---
if page == "Главная":
    st.title("Специалист по глубокому гипнозу")
    st.markdown("---")
    st.write("Добро пожаловать. Здесь вы найдете инструменты для работы с подсознанием.")

elif page == "Блог":
    st.title("Статьи и мысли")
    posts = data[data["type"] == "Пост"].iloc[::-1] # Показываем новые сверху
    for _, row in posts.iterrows():
        with st.expander(f"{row['date']} — {row['title']}", expanded=True):
            if str(row['file_url']) != "nan": st.image(row['file_url'])
            st.write(row['content'])

elif page == "Медитации":
    st.title("🎧 Сопровождающие медитации")
    meds = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in meds.iterrows():
        st.subheader(row['title'])
        st.write(row['content'])
        if str(row['file_url']) != "nan": st.audio(row['file_url'])
        st.divider()

elif page == "Отзывы":
    st.title("💬 Отзывы")
    reviews = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in reviews.iterrows():
        st.subheader(row['title'])
        if ".mp4" in str(row['file_url']).lower() or "youtu" in str(row['file_url']).lower():
            st.video(row['file_url'])
        elif str(row['file_url']) != "nan":
            st.image(row['file_url'])
        st.info(row['content'])

elif page == "Записаться":
    st.title("Запись на консультацию")
    with st.form("tg_form"):
        u_name = st.text_input("Ваше имя")
        u_contact = st.text_input("Ваш Telegram или Телефон")
        u_msg = st.text_area("Ваш запрос")
        if st.form_submit_button("Отправить"):
            full_msg = f"🔔 НОВАЯ ЗАПИСЬ!\n👤 {u_name}\n📞 {u_contact}\n📝 {u_msg}"
            send_tg(full_msg)
            st.success("Спасибо! Я свяжусь с вами в ближайшее время.")

elif page == "🔒 Админка":
    st.title("Управление контентом")
    pwd = st.text_input("Введите пароль", type="password")
    if pwd == ADMIN_PASSWORD:
        with st.form("admin_form"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка на файл (аудио/фото/видео)")
            if st.form_submit_button("Опубликовать на сайт"):
                new_row = pd.DataFrame([{"date": pd.Timestamp.now().strftime("%d.%m.%Y"), "type": t, "title": tit, "content": con, "file_url": url}])
                updated_df = pd.concat([data, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Готово! Сайт обновлен.")
