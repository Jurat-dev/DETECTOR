"""O'zbek matnini qidiruv uchun normallashtirish.

Asl matn o'zgarmaydi; bu funksiyalar faqat qidiruv nusxasi uchun.
"""
from __future__ import annotations
import re
import unicodedata

# o‘ o' oʻ o` o’ ... -> o'   ;  tutuq belgilari -> '
APOSTROPHES = "\u2018\u2019\u02bb\u02bc\u02b9\u0060\u00b4\u2032\u02bd\u055a\uff07'"
_APOS_RE = re.compile(f"[{re.escape(APOSTROPHES)}]")

CYR2LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "j",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "x", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sh", "ъ": "'", "ы": "i", "ь": "", "э": "e", "ю": "yu",
    "я": "ya", "ў": "o'", "қ": "q", "ғ": "g'", "ҳ": "h",
}
LAT2CYR_MULTI = [("o'", "ў"), ("g'", "ғ"), ("sh", "ш"), ("ch", "ч"), ("yo", "ё"),
                 ("yu", "ю"), ("ya", "я"), ("ts", "ц")]
LAT2CYR = {"a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и",
           "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ",
           "r": "р", "s": "с", "t": "т", "u": "у", "v": "в", "x": "х", "y": "й", "z": "з",
           "'": "ъ"}

_CYR_RE = re.compile("[\u0400-\u04ff]")
_WS_RE = re.compile(r"\s+")


def unify_apostrophes(text: str) -> str:
    return _APOS_RE.sub("'", text)


def has_cyrillic(text: str) -> bool:
    return bool(_CYR_RE.search(text))


def cyr_to_lat(text: str) -> str:
    out = []
    for ch in text:
        low = ch.lower()
        if low in CYR2LAT:
            rep = CYR2LAT[low]
            out.append(rep.capitalize() if ch != low and rep else rep)
        else:
            out.append(ch)
    return "".join(out)


def lat_to_cyr(text: str) -> str:
    s = unify_apostrophes(text.lower())
    res, i = [], 0
    while i < len(s):
        for lat, cyr in LAT2CYR_MULTI:
            if s.startswith(lat, i):
                res.append(cyr); i += len(lat); break
        else:
            res.append(LAT2CYR.get(s[i], s[i])); i += 1
    return "".join(res)


def normalize(text: str) -> str:
    """Qidiruv uchun: kichik harf, lotin, yagona apostrof, bitta bo'shliq.

    Uzunlik o'zgarishi mumkin (kirill ш -> sh), shuning uchun parcha
    ko'rsatishda `normalize_with_map` ishlatiladi.
    """
    return normalize_with_map(text)[0]


# Qidiruvdan chiqariladigan suv belgilari va qator oxiridagi bo'g'in ko'chirish
WATERMARK_RE = re.compile(r"(?:https?://)?(?:www\.)?ziyouz\.(?:com|uz)(?:[ \t]+kutubxonasi)?", re.I)
HYPHEN_BREAK_RE = re.compile(r"(?<=\w)[-\u00ad\u2010\u2011][ \t]*\r?\n\s*(?=\w)")


def _skip_mask(text: str) -> list[bool]:
    skip = [False] * len(text)
    for rx in (WATERMARK_RE, HYPHEN_BREAK_RE):
        for m in rx.finditer(text):
            for k in range(m.start(), m.end()):
                skip[k] = True
    return skip


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Normallashgan matn va har bir belgi uchun asl matndagi indeks.

    Qator oxiridagi "so-\nz" -> "soz", suv belgisi (www.ziyouz.com kutubxonasi)
    tashlab yuboriladi, yumshoq tire (U+00AD) e'tiborga olinmaydi.
    """
    text = unicodedata.normalize("NFC", text)
    skip = _skip_mask(text)
    out: list[str] = []
    idx: list[int] = []
    prev_space = True
    for i, ch in enumerate(text):
        if skip[i]:
            if WATERMARK_RE is not None and not ch.isspace() and ch not in "-\u00ad\u2010\u2011" and not prev_space:
                out.append(" "); idx.append(i); prev_space = True
            continue
        if ch.isspace() or ch == "\u00ad":
            if ch == "\u00ad":
                continue
            if not prev_space:
                out.append(" "); idx.append(i)
            prev_space = True
            continue
        prev_space = False
        if _APOS_RE.match(ch):
            rep = "'"
        else:
            low = ch.lower()
            rep = CYR2LAT.get(low, low)
        for c in rep:
            out.append(c); idx.append(i)
    if out and out[-1] == " ":
        out.pop(); idx.pop()
    return "".join(out), idx


WORD_RE = re.compile(r"[a-z0-9']+")


def tokens(text_norm: str) -> list[str]:
    return [t.strip("'") for t in WORD_RE.findall(text_norm) if t.strip("'")]


# Oddiy o'zbek qo'shimchalari (so'z shakllari uchun)
SUFFIXES = sorted({
    "lar", "larni", "larning", "larga", "larda", "lardan", "lari", "larini", "larining",
    "lariga", "larida", "laridan", "ni", "ning", "ga", "ka", "qa", "da", "dan", "ta", "tan",
    "im", "ing", "i", "si", "imiz", "ingiz", "imni", "ingni", "ini", "sini", "ining", "sining",
    "iga", "siga", "ida", "sida", "idan", "sidan", "dir", "mi", "chi", "cha", "lik", "likni",
    "dek", "day", "gacha", "u", "yu", "ham", "m", "ng", "miz", "ngiz",
}, key=len, reverse=True)


def stem(word: str) -> str:
    w = word.strip("'")
    for _ in range(3):
        for suf in SUFFIXES:
            if len(w) - len(suf) >= 3 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        else:
            break
    return w
