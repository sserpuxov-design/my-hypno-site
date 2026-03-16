import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- 1. ТЕМНЫЙ «ГИПНОТИЧЕСКИЙ» ДИЗАЙН ---
st.markdown("""
    <style>
    /* Основной фон сайта - глубокий темный */
    .stApp {
        background: radial-gradient(circle, #1a1c2c 0%, #0a0b10 100%);
        color: #e0e0e0;
    }
    
    /* Карточки постов - темный графит с подсветкой */
    .hypno-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        transition: all 0.3s ease;
    }
    .hypno-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid #4A90E2;
        transform: translateY(-5px);
    }
    
    /* Заголовки - теперь они ВИДНЫ (ярко-белые и голубые) */
    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 0px 0px 10px rgba(74, 144, 226, 0.5);
    }
    
    /* Текст в постах */
    p, span, label {
        color: #ced4da !important;
    }

    /* Боковое меню */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    /* Кнопки формы */
    .stButton>button {
        background: linear-gradient(90deg, #4A90E2, #357ABD);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ПОДКЛЮЧЕНИЕ ---
# Убедитесь, что в Secrets вставлена ссылка на таблицу!
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(ttl="0")
    except:
        return pd.DataFrame(columns=["date", "type", "title", "content", "file_url"])

data = load_data()

# --- 3. НАВИГАЦИЯ ---
st.sidebar.title("🌌 Навигация")
page = st.sidebar.radio("Перейти в раздел:", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

# --- 4. КОНТЕНТ ---
if page == "Главная":
    st.title("Специалист по глубокому гипнозу")
    st.markdown("### Трансформация сознания и работа с подсознанием")
    st.write("Использую передовые методы гипнотерапии для достижения ваших целей.")

elif page == "Блог":
    st.title("📜 Блог гипнолога")
    posts = data[data["type"] == "Пост"].iloc[::-1]
    for _, row in posts.iterrows():
        st.markdown(f"""
            <div class="hypno-card">
                <h3>{row['title']}</h3>
                <p style="font-size: 0.8em; color: #4A90E2 !important;">{row['date']}</p>
                <p>{row['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        if str(row['file_url']) != "nan" and row['file_url']:
            st.image(row['file_url'], use_container_width=True)

elif page == "Медитации":
    st.title("🎧 Сопровождающие медитации")
    meds = data[data["type"] == "Медитация"].iloc[::-1]
    for _, row in meds.iterrows():
        with st.container():
            st.markdown(f'<div class="hypno-card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
            if str(row['file_url']) != "nan" and row['file_url']:
                st.audio(row['file_url'])

elif page == "🔒 Админка":
    st.title("Панель управления")
    pwd = st.text_input("Введите пароль для редактирования", type="password")
    if pwd == "admin": # Смените на свой
        st.success("Доступ разрешен")
        with st.form("add_new"):
            t = st.selectbox("Что добавляем?", ["Пост", "Медитация", "Отзыв"])
            tit = st.text_input("Заголовок")
            con = st.text_area("Текст")
            url = st.text_input("Ссылка на фото или аудио")
            if st.form_submit_button("Опубликовать на сайт"):
                new_row = pd.DataFrame([{
                    "date": pd.Timestamp.now().strftime("%d.%m.%Y"),
                    "type": t, "title": tit, "content": con, "file_url": url
                }])
                updated_df = pd.concat([data, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Данные успешно сохранены в Google Таблицу!")
