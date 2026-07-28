def isimKelimeKontrol(metin: str) -> bool:
    metin = metin.lower().strip()
    if len(metin) < 4:
        return False
    return any(metin.count(metin[j : j + 3]) > 1 for j in range(len(metin) - 2))


def soyisimKelimeKontrol(metin: str) -> bool:
    metin = metin.lower().strip()
    if len(metin) < 6:
        return False
    for i in range(2, len(metin) // 3 + 1):
        for j in range(len(metin) - i + 1):
            parca = metin[j : j + i]
            if metin.count(parca) > 2:
                return True
    return False


def harftekrar_kontrol(metin: str) -> bool:
    metin = metin.lower().strip()
    for i in range(len(metin) - 2):
        if metin[i] == metin[i + 1] == metin[i + 2]:
            return True
    return False
