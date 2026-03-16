import streamlit as st
import pandas as pd
import requests
import os

# --- НАСТРОЙКИ ---
TOKEN = "ВАШ_ТОКЕН"
CHAT_ID = "ВАШ_CHAT_ID"
DB_FILE = "data.csv"

# 1. ДИЗАЙН (Узкое меню, темная тема, крупные кнопки)
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 160px !important; min-width: 160px !important; }
    .stApp { background: #0f172a; color: white; }
    h1, h2, h3 { color: #60a5fa !important; }
    .card { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 15px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
    }
    .stButton>button { 
        background: #2563eb; 
        color: white !important; 
        font-weight: bold;
        border-radius: 10px; 
        width: 100%; 
        height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ФУНКЦИИ ДАННЫХ
def load_data():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=["date", "type", "title", "content", "file_url"]).to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE).fillna("")

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

# 4. ЛОГИКА СТРАНИЦ
if page == "Отзывы":
    st.title("💬 Отзывы клиентов")

    # Форма в экспандере (сворачивается сама после рефраша)
    with st.expander("⭐ Написать отзыв (без регистрации)"):
        with st.form("quick_review", clear_on_submit=True):
            name = st.text_input("Ваше имя")
            text = st.text_area("Ваш отзыв")
            contact = st.text_input("Ваш @ник или ссылка (необязательно)")
            submit = st.form_submit_button("ОПУБЛИКОВАТЬ")
            
            if submit:
                if len(name) > 1 and len(text) > 5:
                    save_item("Отзыв", name, text, contact)
                    # Уведомление в ТГ
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": f"🔥 НОВЫЙ ОТЗЫВ!\nОт: {name}\nСвязь: {contact}\nТекст: {text}"})
                    st.success("Спасибо! Ваш отзыв добавлен.")
                    st.rerun() # Страница обновится, форма закроется
                else:
                    st.error("Пожалуйста, напишите чуть подробнее.")

    # Вывод списка отзывов
    revs = data[data["type"] == "Отзыв"].iloc[::-1]
    for _, row in revs.iterrows():
        st.markdown(f'''
            <div class="card">
                <div style="font-weight: bold; color: #60a5fa; margin-bottom: 5px;">👤 {row["title"]}</div>
                <div style="font-size: 1.1em;">{row["content"]}</div>
                <div style="font-size: 0.8em; color: #4b5563; margin-top: 10px;">{row["file_url"]}</div>
            </div>
        ''', unsafe_allow_html=True)

elif page == "Главная":
    st.title("Специалист по гипнозу")
    st.write("Трансформация реальности через работу с подсознанием.")

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
    with st.form("order_form"):
        n, c, m = st.text_input("Имя"), st.text_input("Контакт"), st.text_area("Запрос")
        if st.form_submit_button("ОТПРАВИТЬ ЗАЯВКУ"):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"ЗАЯВКА!\n{n}\n{c}\n{m}"})
            st.success("Заявка ушла! Скоро свяжусь.")

elif page == "🔒 Админка":
    if st.text_input("Пароль", type="password") == "admin":
        with st.form("admin_form"):
            t = st.selectbox("Тип", ["Пост", "Медитация", "Отзыв"])
            tit, con, url = st.text_input("Заголовок"), st.text_area("Текст"), st.text_input("Ссылка")
            if st.form_submit_button("СОХРАНИТЬ"):
                save_item(t, tit, con, url)
                st.success("Опубликовано!")
                st.rerun()
