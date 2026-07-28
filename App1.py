import _st_client_boot

_st_client_boot.apply()

import streamlit as st
import database  # noqa: F401 — kur() import sırasında bir kez çalışır

TITLE = "Oğuzhan Kuaför✂️"

st.set_page_config(
    page_title=TITLE,
    page_icon="✂️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_st_client_boot.inject_sidebar_hidden(st)

query_params = st.query_params
if query_params.get("mod") == "admin":
    st.switch_page("pages/5_ypbaglanti.py")

st.title(TITLE)
st.write("💈Hoş Geldiniz! Randevu Almak İçin Aşağıdaki Menüleri Kullanabilirsiniz.💈")

st.markdown(
    """
    <style>
    /* RESİM VE ÇERÇEVE AYARLARI */
    .ana-cerceve {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    .jilet-resim {
        width: 100%;
        max-width: 900px;
        border: 8px solid #000000;
        box-shadow: 20px 20px 0px rgba(0,0,0,0.1);
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📅 Randevu AL", use_container_width=True):
        st.switch_page("pages/1_Randevu_AL.py")

with col2:
    if st.button("🔍 Randevu Sorgula", use_container_width=True):
        st.switch_page("pages/2_Randevu_Sorgula.py")

with col3:
    if st.button("📞 DESTEK", use_container_width=True):
        st.switch_page("pages/4_Destek.py")

st.write("---")

st.markdown('<div class="ana-cerceve">', unsafe_allow_html=True)
st.image("Ber2.jpeg", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

st.subheader("📍 Yerimiz")

YERLESKE_ADRES = "İstanbul Kültür Üniversitesi, Ataköy Yerleşkesi"
YERLESKE_LAT = 40.989291
YERLESKE_LON = 28.831516

st.write(YERLESKE_ADRES)

iku_harita_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; }}
    #map {{
      width: 100%;
      height: 450px;
      border-radius: 15px;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    var map = L.map("map").setView([{YERLESKE_LAT}, {YERLESKE_LON}], 17);
    L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap"
    }}).addTo(map);
    L.marker([{YERLESKE_LAT}, {YERLESKE_LON}])
      .addTo(map)
      .bindPopup("<b>Oğuzhan Kuaför</b><br>İstanbul Kültür Üniversitesi, Ataköy Yerleşkesi")
      .openPopup();
  </script>
</body>
</html>
"""

st.components.v1.html(iku_harita_html, height=450)

st.link_button(
    "🗺️ Google Maps'te aç / yol tarifi",
    f"https://www.google.com/maps/search/?api=1&query={YERLESKE_LAT},{YERLESKE_LON}",
    use_container_width=True,
)

st.info(
    "🚇 Metrobüs (Yenibosna Durağı) ve Metro (M1A hattı) ile yerleşkemize kolayca ulaşabilirsiniz."
)
