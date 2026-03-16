import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- 1. КРУТОЙ ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    
    /* Карточка поста */
    .hypno-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border-left: 5px solid #4A90E2;
        transition: transform 0.3s ease;
    }
    .hypno-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Кнопки меню */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        background: rgba(255,255,255,0.05);
        margin-bottom: 5px;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ЛОГИКА И БАЗА ---
# (Оставляем подключение к таблице и функции отправки как были)
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(ttl="0")

# --- 3. ОБНОВЛЕННЫЙ ВЫВОД КОНТЕНТА ---
st.sidebar.title("💎 Меню")
page = st.sidebar.radio("Перейти:", ["Главная", "Блог", "Медитации", "Отзывы", "Записаться", "🔒 Админка"])

if page == "Блог":
    st.title("📜 Полезные статьи")
    posts = data[data["type"] == "Пост"].iloc[::-1]
    
    for _, row in posts.iterrows():
        # Используем HTML внутри Streamlit для красоты
        st.markdown(f"""
            <div class="hypno-card">
                <h3 style="margin-top:0;">{row['title']}</h3>
                <p style="color: gray; font-size: 0.8rem;">{row['date']}</p>
                <p>{row['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        if str(row['file_url']) != "nan":
            st.image(row['file_url'], use_container_width=True)

elif page == "Медитации":
    st.title("🎧 Погружение")
    meds = data[data["type"] == "Медитация"].iloc[::-1]
    
    for _, row in meds.iterrows():
        with st.container():
            st.markdown(f'<div class="hypno-card"><h3>{row["title"]}</h3><p>{row["content"]}</p></div>', unsafe_allow_html=True)
            if str(row['file_url']) != "nan":
                st.audio(row['file_url'])

# (Остальные вкладки Записаться и Админка остаются без изменений)
