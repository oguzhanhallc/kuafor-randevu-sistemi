import _st_client_boot

_st_client_boot.apply()

import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta

from admin_session import admin_session_token, admin_session_verify
from database import (
    SQL_MESAI_TARIH_SIRALA,
    SQL_TARIH_SIRALA,
    get_connection,
    randevu_iptal_et,
    randevu_saat_araligi,
)

TITLE = "🏢 Yönetim Paneli"
st.set_page_config(
    page_title="Yönetim Paneli",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_st_client_boot.inject_sidebar_hidden(st)

# F5 sonrası session_state silinir; URL'deki yp_auth ile yetkiyi geri yükle
if st.session_state.get("yetki") != "admin":
    raw = st.query_params.get("yp_auth")
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if raw and admin_session_verify(str(raw)):
        st.session_state["yetki"] = "admin"

if st.session_state.get("yetki") != "admin":
    st.switch_page("pages/5_ypbaglanti.py")
    st.stop()

# Aynı oturumda URL'de token yoksa ekle ki F5'te adres çubuğu yetkiyi taşısın
if "yp_auth" not in st.query_params:
    st.query_params["yp_auth"] = admin_session_token()

st.title(TITLE)


st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Alt sayfa kontrolü (Artık sadece bu sayfa içinde çalışır)
if "yp_alt_sayfa" not in st.session_state:
    st.session_state.yp_alt_sayfa = "MENÜ"

# --- ANA MENÜ BUTONLARI ---
if st.session_state.yp_alt_sayfa == "MENÜ":
    col1, col2 = st.columns(2)
    
    if st.button("⬅️ Ana Sayfaya Dön"):
        if "yp_auth" in st.query_params:
            del st.query_params["yp_auth"]
        st.session_state.pop("yetki", None)
        st.switch_page("App1.py")
    
    with col1:
        if st.button("📋 Randevu Listesini Görüntüle", use_container_width=True):
            st.session_state.yp_alt_sayfa = "LISTE"
            st.rerun()
        
        if st.button("📅 Mesai Saatlerini Yönet", use_container_width=True):
            st.session_state.yp_alt_sayfa = "MESAI"
            st.rerun()

    with col2:
        if st.button("🗑️ Randevu İptal Paneli", use_container_width=True):
            st.session_state.yp_alt_sayfa = "IPTAL"
            st.rerun()

# --- 1. RANDEVU LİSTESİ BÖLÜMÜ ---
elif st.session_state.yp_alt_sayfa == "LISTE":
    st.subheader("📋 Randevu Listesi")

    with get_connection() as conn:
        df = pd.read_sql_query(
            f"""
            SELECT
                r.musteri_isim AS 'Ad',
                r.musteri_soyisim AS 'Soyad',
                r.musteri_telefon AS 'Telefon',
                r.randevu_tarih AS 'Tarih',
                r.randevu_saati AS 'BaslangicSaati',
                r.randevu_hizmeti AS 'Hizmet',
                p.personel_isim AS 'Personel'
            FROM randevular r
            JOIN personeller p ON r.personel_id = p.id
            ORDER BY {SQL_TARIH_SIRALA}, r.randevu_saati
            """,
            conn,
        )

    if not df.empty:
        df["Saat"] = df.apply(
            lambda r: randevu_saat_araligi(
                r["BaslangicSaati"], hizmet_metni=r["Hizmet"]
            ),
            axis=1,
        )
        df = df[
            ["Ad", "Soyad", "Telefon", "Tarih", "Saat", "Hizmet", "Personel"]
        ]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kayıtlı bir randevu bulunmuyor.")
    
    if st.button("⬅️ Menüye Dön"):
        st.session_state.yp_alt_sayfa = "MENÜ"
        st.rerun()

# --- 2. RANDEVU İPTAL BÖLÜMÜ (personel bazlı) ---
elif st.session_state.yp_alt_sayfa == "IPTAL":
    st.subheader("🗑️ Randevu İptal Paneli")
    st.caption("Önce personeli seçin; yalnızca o personele ait randevular listelenir.")

    if "iptal_personel" not in st.session_state:
        st.session_state.iptal_personel = None

    with get_connection() as conn:
        personel_satirlari = pd.read_sql_query(
            """
            SELECT
                p.id AS personel_id,
                p.personel_isim AS isim,
                COUNT(r.id) AS randevu_sayisi
            FROM personeller p
            LEFT JOIN randevular r ON r.personel_id = p.id
            GROUP BY p.id, p.personel_isim
            ORDER BY p.personel_isim
            """,
            conn,
        )

    st.write("**Personel seçin:**")
    p_cols = st.columns(len(personel_satirlari))
    for i, row in personel_satirlari.iterrows():
        isim = row["isim"]
        adet = int(row["randevu_sayisi"])
        etiket = f"💈 {isim}\n({adet} randevu)"
        with p_cols[i]:
            secili = st.session_state.iptal_personel == isim
            if st.button(
                etiket,
                key=f"iptal_personel_btn_{row['personel_id']}",
                use_container_width=True,
                type="primary" if secili else "secondary",
            ):
                st.session_state.iptal_personel = isim
                st.rerun()

    if st.session_state.iptal_personel:
        secilen_isim = st.session_state.iptal_personel
        if st.button("↩️ Personel seçimine dön", use_container_width=False):
            st.session_state.iptal_personel = None
            st.rerun()

        st.divider()
        st.subheader(f"📋 {secilen_isim} — randevular")

        with get_connection() as conn:
            df_iptal = pd.read_sql_query(
                f"""
                SELECT
                    r.id AS randevu_id,
                    r.musteri_isim AS 'Ad',
                    r.musteri_soyisim AS 'Soyad',
                    r.musteri_telefon AS 'Telefon',
                    r.randevu_tarih AS 'Tarih',
                    r.randevu_saati AS 'BaslangicSaati',
                    r.randevu_hizmeti AS 'Hizmet'
                FROM randevular r
                JOIN personeller p ON r.personel_id = p.id
                WHERE p.personel_isim = ?
                ORDER BY {SQL_TARIH_SIRALA}, r.randevu_saati
                """,
                conn,
                params=(secilen_isim,),
            )

        if df_iptal.empty:
            st.info(f"{secilen_isim} için kayıtlı randevu bulunmuyor.")
        else:
            df_iptal["Saat"] = df_iptal.apply(
                lambda r: randevu_saat_araligi(
                    r["BaslangicSaati"], hizmet_metni=r["Hizmet"]
                ),
                axis=1,
            )
            st.dataframe(
                df_iptal[["Ad", "Soyad", "Telefon", "Tarih", "Saat", "Hizmet"]],
                use_container_width=True,
                hide_index=True,
            )

            secenekler = {}
            for _, r in df_iptal.iterrows():
                etiket = (
                    f"{r['Ad']} {r['Soyad']} · {r['Tarih']} · {r['Saat']} · {r['Hizmet']}"
                )
                secenekler[etiket] = int(r["randevu_id"])

            secilen = st.selectbox("Silinecek randevuyu seçin:", list(secenekler.keys()))

            if st.button("Seçili Randevuyu Sil", type="primary", use_container_width=True):
                with get_connection() as conn:
                    if randevu_iptal_et(conn, randevu_id=secenekler[secilen]):
                        conn.commit()
                        st.success(
                            f"Randevu silindi; {secilen_isim} için mesai slotları boşaltıldı."
                        )
                        st.rerun()
                    else:
                        st.error("Randevu silinemedi.")
    else:
        st.info("👆 Listelemek ve silmek için yukarıdan bir personel seçin.")

    if st.button("⬅️ Menüye Dön"):
        st.session_state.iptal_personel = None
        st.session_state.yp_alt_sayfa = "MENÜ"
        st.rerun()


elif st.session_state.yp_alt_sayfa == "MESAI":
    st.subheader("📅 Personel Mesai Planla")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, personel_isim FROM personeller")
        personeller = c.fetchall()
        personel_dict = {p[1]: p[0] for p in personeller}

    secilen_p_isimi = st.selectbox("Personel Seç", list(personel_dict.keys()))
    p_id = personel_dict[secilen_p_isimi]

    # Tarih aralığı veya tek gün seçimi
    mesai_tarihi = st.date_input("Mesai Tarihi", value=date.today())
    formatli_tarih = mesai_tarihi.strftime("%d-%m-%Y")

    # Mesai Saat Aralığı Seçimi
    col1, col2 = st.columns(2)
    baslangic = col1.time_input("Mesai Başlangıç", value=time(9, 0))
    bitis = col2.time_input("Mesai Bitiş", value=time(19, 0))

    # --- MESAİ OLUŞTURMA BUTONU ---
    if st.button("Mesai Saatlerini Oluştur 🚀", use_container_width=True):
        su_an = datetime.combine(mesai_tarihi, baslangic)
        bitis_dt = datetime.combine(mesai_tarihi, bitis)
        
        saat_listesi = []
        
        while su_an <= bitis_dt:
            saat_listesi.append((p_id, formatli_tarih, su_an.strftime("%H:%M"), 0))
            su_an += timedelta(minutes=30)
        
        with get_connection() as conn:
            c = conn.cursor()
            try:
                c.executemany("""
                    INSERT OR IGNORE INTO calisma_saatleri (personel_id, mesai_tarih, mesai_saati, durum) 
                    VALUES (?, ?, ?, ?)
                """, saat_listesi)
                conn.commit()
                st.success(f"✅ {secilen_p_isimi} için {len(saat_listesi)} adet mesai slotu oluşturuldu!")
            except Exception as e:
                st.error(f"Hata: {e}")

    st.divider()

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"""
            SELECT
                p.personel_isim,
                c.mesai_tarih,
                c.personel_id,
                COUNT(*) AS toplam,
                SUM(CASE WHEN c.durum = 0 THEN 1 ELSE 0 END) AS bos
            FROM calisma_saatleri c
            JOIN personeller p ON c.personel_id = p.id
            GROUP BY c.personel_id, c.mesai_tarih
            ORDER BY {SQL_MESAI_TARIH_SIRALA}, p.personel_isim
            """
        )
        mesai_planlari = c.fetchall()

    if not mesai_planlari:
        st.info("Henüz kayıtlı mesai planı yok. Yukarıdan yeni mesai oluşturabilirsiniz.")
    else:
        silinebilir = {}
        silinebilir_satirlar = []
        for isim, tarih, pid, toplam, bos in mesai_planlari:
            dolu = toplam - bos
            if bos > 0:
                etiket = f"{isim} · {tarih} — {bos} boş slot (toplam {toplam})"
                silinebilir[etiket] = (pid, tarih, isim)
                silinebilir_satirlar.append(
                    {
                        "Personel": isim,
                        "Tarih": tarih,
                        "Toplam slot": toplam,
                        "Boş (silinebilir)": bos,
                        "Randevulu": dolu,
                    }
                )

        st.subheader("🗑️ Boş mesai silme")
        st.caption(
            "Sadece **Boş** sütunu 0'dan büyük olan günler buradan silinebilir. "
            "Randevulu slotlar müşteri randevusuna bağlıdır."
        )

        if not silinebilir:
            st.info(
                "Şu an silinecek **boş mesai yok** — tablodaki tüm slotlar dolu (randevulu). "
                "Müşteri randevusunu iptal etmek için ana menüden **Randevu İptal Paneli**'ni kullanın; "
                "iptal sonrası slotlar boşalır ve burada silinebilir hale gelir."
            )
        else:
            st.dataframe(
                pd.DataFrame(silinebilir_satirlar),
                use_container_width=True,
                hide_index=True,
            )
            secilen_plan = st.selectbox(
                "Boş mesaileri silinecek planı seçin:",
                list(silinebilir.keys()),
            )
            pid_sil, tarih_sil, isim_sil = silinebilir[secilen_plan]

            if st.button(
                "🗑️ Seçili plandaki boş mesaileri sil",
                type="secondary",
                use_container_width=True,
            ):
                with get_connection() as conn:
                    c = conn.cursor()
                    try:
                        c.execute(
                            """
                            DELETE FROM calisma_saatleri
                            WHERE personel_id = ? AND mesai_tarih = ? AND durum = 0
                            """,
                            (pid_sil, tarih_sil),
                        )
                        silinen_sayisi = conn.total_changes
                        conn.commit()
                        if silinen_sayisi > 0:
                            st.success(
                                f"🗑️ {isim_sil} — {tarih_sil}: "
                                f"{silinen_sayisi} adet boş slot silindi."
                            )
                            st.rerun()
                        else:
                            st.warning("⚠️ Silinecek boş mesai saati bulunamadı.")
                    except Exception as e:
                        st.error(f"Silme işlemi sırasında hata oluştu: {e}")

        with st.expander("📊 Tüm mesai planları (sadece bilgi — silme listesi değil)"):
            st.caption(
                "Bu özet, oluşturduğunuz mesai günlerini gösterir. "
                "«Randevulu» = dolu slot; tek randevu birden fazla slot kapatabilir."
            )
            st.dataframe(
                pd.DataFrame(
                    {
                        "Personel": [r[0] for r in mesai_planlari],
                        "Tarih": [r[1] for r in mesai_planlari],
                        "Toplam slot": [r[3] for r in mesai_planlari],
                        "Boş": [r[4] for r in mesai_planlari],
                        "Randevulu": [r[3] - r[4] for r in mesai_planlari],
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
                

    if st.button("⬅️ Menüye Dön"):
        st.session_state.yp_alt_sayfa = "MENÜ"
        st.rerun()