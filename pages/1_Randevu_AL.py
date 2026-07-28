import _st_client_boot

_st_client_boot.apply()

import streamlit as st
import sqlite3
from database import (
    get_connection,
    personelleriGetir,
    randevu_saat_araligi,
    randevu_slot_sayisi,
    slot_araligi,
    slotlari_kapat,
)
from validations import harftekrar_kontrol, isimKelimeKontrol, soyisimKelimeKontrol
from datetime import date

def ardışık_blok_filtrele(musait_liste, gereken):
    uygun_baslangiclar = []
    def dakika_yap(saat_str):
        h, m = map(int, saat_str.split(':'))
        return h * 60 + m

    for i in range(len(musait_liste) - gereken + 1):
        pencere = musait_liste[i : i + gereken]
        gecerli = True
        for j in range(len(pencere) - 1):
            # Aradaki fark 30 dakikadan fazlaysa blok bozulmuştur
            if dakika_yap(pencere[j+1]) - dakika_yap(pencere[j]) != 30:
                gecerli = False
                break
        if gecerli:
            uygun_baslangiclar.append(pencere[0])
    return uygun_baslangiclar

TITLE = "📅 Randevu AL"

st.set_page_config(
    page_title="Randevu AL",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_st_client_boot.inject_sidebar_hidden(st)

st.title(TITLE)
st.subheader("Lütfen aşağıdaki formu doldurarak randevunuzu oluşturunuz.")

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

secilen_saat = None
secilen_personel = None
p_id = None
tarih = None
saat_secilebilir = False

musteri_isim = st.text_input("Adınız")
musteri_soyisim = st.text_input("Soy Adınız")
musteri_telefon = st.text_input("Telefon Numaranız")

st.markdown("""
    <style>
    .stMultiSelect input {
        pointer-events: none !important;
        caret-color: transparent !important;
        color: transparent !important;
    }
    .stMultiSelect div[data-baseweb="select"] {
        cursor: pointer !important;
    }
    .stMultiSelect span[data-baseweb="tag"] {
        color: black !important;
        background-color: #e0e0e0 !important;
        pointer-events: auto !important;
    }
    .stMultiSelect div[role="button"] {
        color: #31333F !important;
    }
    </style>
    """, unsafe_allow_html=True)

temizisim = musteri_isim.strip()
temizsoyisim = musteri_soyisim.strip()
temiztelefon = musteri_telefon.replace(" ", "").strip()

# --- 1. HİZMETLERİ VE ROLLERİ ÇEK ---
with get_connection() as conn:
    c = conn.cursor()
    c.execute("SELECT hizmet_adi, gereken_rol FROM hizmetler")
    hizmet_verileri = c.fetchall()

hizmet_rolleri = {satir[0]: satir[1] for satir in hizmet_verileri}

# --- 2. MULTISELECT VE ROL KİLİTLEME ---
if "gecici_secim" not in st.session_state:
    st.session_state.gecici_secim = []

tum_hizmet_isimleri = list(hizmet_rolleri.keys())

if st.session_state.gecici_secim:
    secili_rol = hizmet_rolleri[st.session_state.gecici_secim[0]]
    mevcut_opsiyonlar = [h for h, r in hizmet_rolleri.items() if r == secili_rol]
else:
    mevcut_opsiyonlar = tum_hizmet_isimleri

secilen_hizmetler = st.multiselect(
    "Hizmet Seçiniz", 
    options=mevcut_opsiyonlar,
    default=st.session_state.gecici_secim
)
st.session_state.gecici_secim = secilen_hizmetler

# --- 3. ADIM ADIM AKIŞ ---
if secilen_hizmetler:
    gereken_slot = randevu_slot_sayisi(secilen_hizmetler)

    # --- PERSONEL SEÇİMİ ---
    personelFiltreleme = personelleriGetir(secilen_hizmetler[0])
    secilen_personel = st.selectbox("Personel Seçiniz", personelFiltreleme)

    if secilen_personel:
        # --- TARİH SEÇİMİ ---
        tarih = st.date_input(
            "Randevu Tarihi Seçiniz",
            value=date.today(),
            min_value=date.today(),
            format="DD.MM.YYYY",
        )

        # --- SAATLERİ ÇEKME VE LİSTELEME ---
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("Select id from personeller WHERE personel_isim = ?", (secilen_personel,))
            p_sonuc = c.fetchone()
            
            if p_sonuc:
                p_id = p_sonuc[0]
                formatli_tarih = tarih.strftime("%d-%m-%Y")
                
                c.execute("""
                    SELECT mesai_saati FROM calisma_saatleri 
                    WHERE mesai_tarih = ? AND personel_id = ? AND durum = 0
                    ORDER BY mesai_saati ASC
                """, (formatli_tarih, p_id))
                
                musait_saatler = [satir[0] for satir in c.fetchall()]
                
                if musait_saatler:
                    # --- 🟢 AKILLI SÜZGEÇ DEVREDE ---
                    filtreli_saatler = ardışık_blok_filtrele(musait_saatler, gereken_slot)
                    
                    if filtreli_saatler:
                        saat_secilebilir = True
                        secilen_saat = st.selectbox("🕒 Uygun Bir Saat Seçin", filtreli_saatler)
                        st.info(f"💡 Seçtiğiniz hizmetler için {gereken_slot * 30} dakikalık randevu oluşturulacaktır.")
                        
                        # BUTON VE INSERT İŞLEMLERİNİ BURAYA EKLEYEBİLİRSİN BAŞKAN
                    else:
                        st.error("⚠️ Seçtiğiniz işlemler için ardışık boş slot bulunamadı.")
                else:
                    st.warning(f"⚠️ {formatli_tarih} tarihinde bu personel için müsait saat bulunmamaktadır.")
else:
    st.info("💡 Devam etmek için lütfen önce en az bir hizmet seçiniz.")
    st.info("❗ Saç Yıkama hizmeti için müşterilerimizin ekstra randevu olarak alması gerekmektedir.")

if st.button("Randevu Oluştur"):
    if not (temizisim and temizsoyisim and temiztelefon):
        st.error("Lütfen ad, soyad ve telefon bilgilerini eksiksiz giriniz!")
    elif harftekrar_kontrol(temizisim):
        st.error("⚠️ İsimde fazla harf tekrarı var, lütfen tekrar kontrol ediniz.")
    elif harftekrar_kontrol(temizsoyisim):
        st.error("⚠️ Soyisimde fazla harf tekrarı var, lütfen tekrar kontrol ediniz.")
    elif isimKelimeKontrol(temizisim):
        st.error("⚠️ İsimde kelime tekrarı tespit edildi!")
    elif soyisimKelimeKontrol(temizsoyisim):
        st.error("⚠️ Soyİsimde kelime tekrarı tespit edildi!")
    elif len(temizisim) < 3 or len(temizsoyisim) < 2:
        st.error("⚠️ Lütfen geçerli bir isim (en az 3 harf) ve soyisim (en az 2 harf) giriniz.")
    elif not (temizisim.replace(" ", "").isalpha() and temizsoyisim.replace(" ", "").isalpha()):
        st.error("⚠️ İsim ve soyisim sadece harflerden oluşmalıdır!")
    elif len(temizisim) > 20 or len(temizsoyisim) > 20:
        st.error("⚠️ İsim ve soyisim 20 karakterden fazla olamaz!")
    elif not (temiztelefon.isdigit() and len(temiztelefon) == 11):
        st.error("⚠️ Lütfen 11 haneli geçerli bir telefon numarası giriniz (Örn: 05xxxxxxxxx).")
    elif not secilen_hizmetler:
        st.error("💡 Lütfen önce en az bir hizmet seçiniz.")
    elif not secilen_personel:
        st.error("Lütfen personel seçiniz.")
    elif not saat_secilebilir or secilen_saat is None:
        st.error("Lütfen personel, tarih ve müsait bir randevu saati seçiniz.")
    else:
        alinan_blok = randevu_slot_sayisi(secilen_hizmetler)
        formatli_tarih = tarih.strftime("%d-%m-%Y")
        hizmet_metni = ", ".join(secilen_hizmetler)

        if tarih < date.today():
            st.warning("⚠️ Geçmiş bir zamana randevu alamazsınız!")
        else:
            try:
                with get_connection() as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    c = conn.cursor()

                    c.execute(
                        """
                        SELECT 1 FROM randevular
                        WHERE randevu_tarih = ? AND randevu_saati = ? AND personel_id = ?
                        """,
                        (formatli_tarih, secilen_saat, p_id),
                    )
                    if c.fetchone():
                        conn.rollback()
                        st.warning(
                            f"⚠️ Seçmiş olduğunuz {formatli_tarih} tarih ve {secilen_saat} saati zaten dolu."
                        )
                    else:
                        kapatilacak = slot_araligi(
                            c, p_id, formatli_tarih, secilen_saat, alinan_blok
                        )
                        for s in kapatilacak:
                            c.execute(
                                """
                                SELECT durum FROM calisma_saatleri
                                WHERE personel_id = ? AND mesai_tarih = ? AND mesai_saati = ?
                                """,
                                (p_id, formatli_tarih, s),
                            )
                            row = c.fetchone()
                            if not row or row[0] != 0:
                                conn.rollback()
                                st.warning(
                                    f"⚠️ {s} saati artık müsait değil. Lütfen başka bir saat seçin."
                                )
                                break
                        else:
                            c.execute(
                                """
                                INSERT INTO randevular (
                                    musteri_isim, musteri_soyisim, musteri_telefon,
                                    randevu_tarih, randevu_saati, randevu_hizmeti, personel_id
                                ) VALUES (?,?,?,?,?,?,?)
                                """,
                                (
                                    temizisim,
                                    temizsoyisim,
                                    temiztelefon,
                                    formatli_tarih,
                                    secilen_saat,
                                    hizmet_metni,
                                    p_id,
                                ),
                            )
                            slotlari_kapat(
                                c, p_id, formatli_tarih, secilen_saat, alinan_blok
                            )
                            conn.commit()
                            saat_araligi = randevu_saat_araligi(
                                secilen_saat,
                                secilen_hizmetler,
                                slot_sayisi=alinan_blok,
                            )
                            st.success(
                                f"""
                                ✅ Sayın **{temizisim.title()} {temizsoyisim.upper()}**, randevunuz başarıyla oluşturuldu!

                                📅 **Randevu Bilgileriniz:**
                                * **Tarih:** {formatli_tarih}
                                * **Saat:** {saat_araligi}
                                * **Hizmet:** {secilen_hizmetler}
                                * **Personel:** {secilen_personel}

                                Bizi tercih ettiğiniz için teşekkür ederiz.
                                """
                            )
                            st.balloons()
            except sqlite3.Error as e:
                st.error(f"Randevu kaydı sırasında bir hata oluştu: {e}")
                
if st.button("⬅️ Ana Sayfaya Dön"):
        st.switch_page("App1.py")    
        st.rerun()
# ------------------------------------------------------------------------------------------------------

