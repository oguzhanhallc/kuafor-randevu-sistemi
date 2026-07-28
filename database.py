import os
import sqlite3
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "berberdata.db")

# Veritabanındaki hizmet adlarıyla birebir eşleşmeli
HIZMET_BLOKLARI = {
    "Saç Kesimi": 1,
    "Sakal Traşı": 1,
    "Cilt Bakımı": 2,
    "Saç Yıkama": 1,
}

def sql_tarih_sirala(kolon: str) -> str:
    """dd-mm-yyyy metin tarihini doğru sıralamak için (örn. r.randevu_tarih veya c.mesai_tarih)."""
    return f"substr({kolon}, 7, 4) || substr({kolon}, 4, 2) || substr({kolon}, 1, 2)"


SQL_TARIH_SIRALA = sql_tarih_sirala("r.randevu_tarih")
SQL_MESAI_TARIH_SIRALA = sql_tarih_sirala("c.mesai_tarih")


def get_connection(timeout: int = 20) -> sqlite3.Connection:
    return sqlite3.connect(db_path, timeout=timeout)


def hizmetleri_parse(hizmet_metni: str) -> list[str]:
    return [h.strip() for h in hizmet_metni.split(",") if h.strip()]


def randevu_slot_sayisi(hizmetler: list[str]) -> int:
    """Randevu için kapatılacak / açılacak 30 dk slot sayısı."""
    if not hizmetler:
        return 1
    ana = any("Saç" in h for h in hizmetler)
    yan = any("Saç" not in h for h in hizmetler)
    toplam = sum(HIZMET_BLOKLARI.get(h, 1) for h in hizmetler)
    if ana and yan and toplam < 2:
        return 2
    return max(toplam, 1)


def randevu_saat_araligi(
    baslangic_saati: str,
    hizmetler: list[str] | None = None,
    *,
    hizmet_metni: str | None = None,
    slot_sayisi: int | None = None,
) -> str:
    """Başlangıç saatinden hizmet süresine göre aralık metni (örn. 09:00-10:30)."""
    if slot_sayisi is not None:
        n = max(slot_sayisi, 1)
    elif hizmetler is not None:
        n = randevu_slot_sayisi(hizmetler)
    elif hizmet_metni:
        n = randevu_slot_sayisi(hizmetleri_parse(hizmet_metni))
    else:
        n = 1
    baslangic = datetime.strptime(baslangic_saati.strip(), "%H:%M")
    bitis = baslangic + timedelta(minutes=30 * n)
    return f"{baslangic.strftime('%H:%M')}-{bitis.strftime('%H:%M')}"


def _fallback_slot_araligi(baslangic_saati: str, slot_sayisi: int) -> list[str]:
    t = datetime.strptime(baslangic_saati, "%H:%M")
    return [(t + timedelta(minutes=30 * i)).strftime("%H:%M") for i in range(slot_sayisi)]


def slot_araligi(
    cursor: sqlite3.Cursor,
    personel_id: int,
    tarih: str,
    baslangic_saati: str,
    slot_sayisi: int,
) -> list[str]:
    cursor.execute(
        """
        SELECT mesai_saati FROM calisma_saatleri
        WHERE personel_id = ? AND mesai_tarih = ?
        ORDER BY mesai_saati ASC
        """,
        (personel_id, tarih),
    )
    saatler = [r[0] for r in cursor.fetchall()]
    if baslangic_saati in saatler:
        idx = saatler.index(baslangic_saati)
        return saatler[idx : idx + slot_sayisi]
    return _fallback_slot_araligi(baslangic_saati, slot_sayisi)


def slotlari_kapat(
    cursor: sqlite3.Cursor,
    personel_id: int,
    tarih: str,
    baslangic_saati: str,
    slot_sayisi: int,
) -> None:
    for saat in slot_araligi(cursor, personel_id, tarih, baslangic_saati, slot_sayisi):
        cursor.execute(
            """
            UPDATE calisma_saatleri SET durum = 1
            WHERE personel_id = ? AND mesai_tarih = ? AND mesai_saati = ?
            """,
            (personel_id, tarih, saat),
        )


def slotlari_ac(
    cursor: sqlite3.Cursor,
    personel_id: int,
    tarih: str,
    baslangic_saati: str,
    hizmet_metni: str,
) -> None:
    slot_sayisi = randevu_slot_sayisi(hizmetleri_parse(hizmet_metni))
    for saat in slot_araligi(cursor, personel_id, tarih, baslangic_saati, slot_sayisi):
        cursor.execute(
            """
            UPDATE calisma_saatleri SET durum = 0
            WHERE personel_id = ? AND mesai_tarih = ? AND mesai_saati = ?
            """,
            (personel_id, tarih, saat),
        )


def randevu_iptal_et(
    conn: sqlite3.Connection,
    *,
    randevu_id: int | None = None,
    telefon: str | None = None,
    tarih: str | None = None,
    saat: str | None = None,
) -> bool:
    """Randevuyu siler ve mesai slotlarını boşaltır. Başarılıysa True."""
    c = conn.cursor()
    if randevu_id is not None:
        c.execute(
            "SELECT personel_id, randevu_tarih, randevu_saati, randevu_hizmeti FROM randevular WHERE id = ?",
            (randevu_id,),
        )
    else:
        c.execute(
            """
            SELECT personel_id, randevu_tarih, randevu_saati, randevu_hizmeti
            FROM randevular
            WHERE REPLACE(musteri_telefon, ' ', '') = ? AND randevu_tarih = ? AND randevu_saati = ?
            """,
            (telefon, tarih, saat),
        )
    row = c.fetchone()
    if not row:
        return False
    p_id, r_tarih, r_saat, hizmet = row
    if randevu_id is not None:
        c.execute("DELETE FROM randevular WHERE id = ?", (randevu_id,))
    else:
        c.execute(
            """
            DELETE FROM randevular
            WHERE REPLACE(musteri_telefon, ' ', '') = ? AND randevu_tarih = ? AND randevu_saati = ?
            """,
            (telefon, tarih, saat),
        )
    slotlari_ac(c, p_id, r_tarih, r_saat, hizmet)
    return True


def _mesai_tekillestir_ve_indeks(c: sqlite3.Cursor) -> None:
    """Eski DB'deki çift mesai satırlarını temizler, sonra UNIQUE indeks kurar."""
    try:
        c.execute(
            """
            DELETE FROM calisma_saatleri
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM calisma_saatleri
                GROUP BY personel_id, mesai_tarih, mesai_saati
            )
            """
        )
    except sqlite3.Error:
        pass
    try:
        c.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_mesai_slot
            ON calisma_saatleri (personel_id, mesai_tarih, mesai_saati)
            """
        )
    except sqlite3.IntegrityError:
        # Nadiren yarış durumunda: bir kez daha tekilleştir
        c.execute(
            """
            DELETE FROM calisma_saatleri
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM calisma_saatleri
                GROUP BY personel_id, mesai_tarih, mesai_saati
            )
            """
        )
        c.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_mesai_slot
            ON calisma_saatleri (personel_id, mesai_tarih, mesai_saati)
            """
        )


def kur():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute(
            """CREATE TABLE IF NOT EXISTS personeller
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, personel_isim TEXT, personel_rol TEXT)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS hizmetler
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, hizmet_adi TEXT, gereken_rol TEXT)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS randevular
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      musteri_isim TEXT, musteri_soyisim TEXT, musteri_telefon TEXT,
                      randevu_tarih TEXT, randevu_saati TEXT, randevu_hizmeti TEXT, personel_id INTEGER)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS calisma_saatleri (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        personel_id INTEGER,
                        mesai_tarih TEXT,
                        mesai_saati TEXT,
                        durum INTEGER DEFAULT 0)"""
        )
        _mesai_tekillestir_ve_indeks(c)

        c.execute("SELECT COUNT(*) FROM personeller")
        if c.fetchone()[0] == 0:
            personeller = [
                ("Hakan", "Kuaför"),
                ("Ahmet", "Kuaför"),
                ("Mehmet", "Kuaför"),
                ("Can", "Çırak"),
            ]
            c.executemany(
                "INSERT INTO personeller (personel_isim, personel_rol) VALUES (?,?)",
                personeller,
            )

        c.execute("SELECT COUNT(*) FROM hizmetler")
        if c.fetchone()[0] == 0:
            hizmetler = [
                ("Saç Kesimi", "Kuaför"),
                ("Sakal Traşı", "Kuaför"),
                ("Cilt Bakımı", "Kuaför"),
                ("Saç Yıkama", "Çırak"),
            ]
            c.executemany(
                "INSERT INTO hizmetler (hizmet_adi, gereken_rol) VALUES (?,?)", hizmetler
            )

        conn.commit()


def hizmetleriGetir():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT hizmet_adi FROM hizmetler")
        return [satir[0] for satir in c.fetchall()]


def personelleriGetir(secilenHizmet):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT gereken_rol FROM hizmetler WHERE hizmet_adi = ?", (secilenHizmet,))
        sonuc = c.fetchone()
        if not sonuc:
            return []
        c.execute("SELECT personel_isim FROM personeller WHERE personel_rol = ?", (sonuc[0],))
        return [satir[0] for satir in c.fetchall()]


kur()
