import _st_client_boot

_st_client_boot.apply()

import streamlit as st

st.set_page_config(
    page_title="Admin Girişi",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_st_client_boot.inject_sidebar_hidden(st)

if st.session_state.get("yetki") == "admin":
    st.switch_page("pages/3_Yönetim_Paneli.py")

st.markdown("<br><br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("🛡️ Admin Girişi")
    with st.container(border=True):
        sifre = st.text_input("Yönetici Anahtarını Girin", type="password")

        if st.button("SİSTEME GİRİŞ YAP", use_container_width=True, type="primary"):
            if sifre == "Admin034":
                st.session_state["yetki"] = "admin"
                st.success("Yetki Tanımlandı! Panele geçiliyor...")
                st.switch_page("pages/3_Yönetim_Paneli.py")
            else:
                st.error("Hatalı Şifre!")

        if st.button("⬅️ Ana Menüye Dön", use_container_width=True):
            st.switch_page("App1.py")
