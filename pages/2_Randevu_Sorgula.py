import _st_client_boot

_st_client_boot.apply()

import streamlit as st
import pandas as pd
from database import get_connection, randevu_iptal_et


TITLE = "📅 Randevu Sorgula"

st.set_page_config(
    page_title="Randevu Sorgula",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_st_client_boot.inject_sidebar_hidden(st)

st.title(TITLE)
st.subheader("Lütfen telefon numaranızı girerek randevunuzu sorgulayınız.")

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.write("---")

# Kullanıcıdan telefonu alalım
sorgu_tel = st.text_input("Telefon Numaranızı Giriniz", placeholder="05XX XXX XX XX")

# --- HAFIZA YÖNETİMİ ---
# Arama sonuçlarını sayfada tutmak için session_state kullanıyoruz
if "sorgu_df" not in st.session_state:
    st.session_state.sorgu_df = None
if "temiz_tel" not in st.session_state:
    st.session_state.temiz_tel = ""

if st.button("Randevumu Bul"):
    if not sorgu_tel:
        st.error("Lütfen bir telefon numarası girin!")
    else:
        # --- VERİ TEMİZLEME ---
        temiz_sorgu_tel = "".join(filter(str.isdigit, sorgu_tel))
        st.session_state.temiz_tel = temiz_sorgu_tel
        
        conn = get_connection()
        
        query = """
        SELECT 
            r.musteri_isim || ' ' || r.musteri_soyisim AS 'Müşteri Adı',
            r.randevu_tarih AS 'Randevu Tarihi', 
            r.randevu_saati AS 'Randevu Saati', 
            r.randevu_hizmeti AS 'Randevu Hizmeti',
            p.personel_isim AS 'Hizmet Verecek Personel'
        FROM randevular r
        JOIN personeller p ON r.personel_id = p.id
        WHERE REPLACE(r.musteri_telefon, ' ', '') = ?
        """
        
        try:
            df = pd.read_sql_query(query, conn, params=(temiz_sorgu_tel,))
            st.session_state.sorgu_df = df # Sonucu hafızaya al
            
            if df.empty:
                st.warning(f"⚠️ {temiz_sorgu_tel} numarasına ait aktif bir randevu kaydı bulunamadı.")
        except Exception as e:
            st.error(f"Sorgulama sırasında bir teknik hata oluştu: {e}")
        finally:
            conn.close()

# --- SONUÇLARI GÖSTER VE İPTAL ETME PANELİ ---
if st.session_state.sorgu_df is not None and not st.session_state.sorgu_df.empty:
    df = st.session_state.sorgu_df
    st.success(f"✅ Randevunuz bulundu!")
    st.dataframe(df, use_container_width=True) 
    st.info("💡 Lütfen randevu saatinizden 5 dakika önce dükkanda olunuz.")

    # --- İPTAL ETME BÖLÜMÜ (YENİ ENTEGRE) ---
    st.write("---")
    st.subheader("🗑️ Randevu İptal Et")
    
    # Kullanıcıya hangi randevuyu sileceğini seçtiriyoruz
    secenekler = df.apply(lambda x: f"{x['Randevu Tarihi']} | {x['Randevu Saati']} | {x['Randevu Hizmeti']}", axis=1).tolist()
    secilen_randevu = st.selectbox("İptal edilecek randevuyu seçin:", secenekler)
    
    if st.button("Seçili Randevuyu İptal Et"):
        # Seçilen bilginin içinden tarih ve saati geri alalım
        parcalar = secilen_randevu.split(" | ")
        tarih_sil = parcalar[0]
        saat_sil = parcalar[1]
        
        conn = get_connection()
        try:
            if randevu_iptal_et(
                conn,
                telefon=st.session_state.temiz_tel,
                tarih=tarih_sil,
                saat=saat_sil,
            ):
                conn.commit()
                st.success(f"❌ {tarih_sil} tarihli randevunuz başarıyla iptal edildi.")
                st.session_state.sorgu_df = None
                st.rerun()
            else:
                st.error("Randevu bulunamadı veya zaten iptal edilmiş.")
        except Exception as e:
            conn.rollback()
            st.error(f"İptal işlemi sırasında hata: {e}")
        finally:
            conn.close()

# Sayfa altına küçük bir not
st.markdown("<br><br><p style='text-align: center; font-size: 0.8rem;'>Herhangi bir sorun yaşarsanız lütfen bizimle iletişime geçin.</p>", unsafe_allow_html=True)

if st.button("⬅️ AnaSayfaya Dön"):
    st.switch_page("App1.py")    
    st.rerun()