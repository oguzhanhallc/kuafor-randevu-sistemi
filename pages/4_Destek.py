import _st_client_boot

_st_client_boot.apply()

import streamlit as st

TITLE = "📞 Destek"

st.set_page_config(
    page_title="Destek",
    page_icon="📞",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_st_client_boot.inject_sidebar_hidden(st)

st.title(TITLE)
st.write("Bizimle iletişime geçmek için aşağıdaki bilgileri kullanabilirsiniz.")

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.info("📍 **Adres:** İstanbul Kültür Üniversitesi, Ataköy Yerleşkesi")
st.info("📞 **Telefon:** 0555 555 99 00")
st.info("💬 **WhatsApp:** 0555 555 99 00")
st.info("📧 **E-posta:** kuaforumkultur@gmail.com")
st.write("Randevu iptali veya değişikliği için **Randevu Sorgula** sayfasını kullanabilirsiniz.")

if st.button("⬅️ Ana Sayfaya Dön"):
    st.switch_page("App1.py")
