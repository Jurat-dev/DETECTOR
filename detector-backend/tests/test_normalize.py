from app.normalize import normalize, cyr_to_lat, lat_to_cyr, stem


def test_apostrophes():
    vs = ["o‘zbek", "o'zbek", "oʻzbek", "o`zbek", "o’zbek", "Oʻzbek"]
    assert len({normalize(v) for v in vs}) == 1
    assert normalize("g‘alaba") == normalize("gʻalaba") == "g'alaba"


def test_cyrillic():
    assert normalize("Ўзбекистон") == "o'zbekiston"
    assert normalize("Ғалаба") == "g'alaba"
    assert cyr_to_lat("шаҳар") == "shahar"
    assert lat_to_cyr("o‘zbek") == "ўзбек"


def test_stem():
    assert stem("kitoblarni") == "kitob"
    assert stem("kitobni") == "kitob"


def test_hyphen_break_and_soft_hyphen():
    assert "tomonida" in normalize("tomo-\nnida")
    assert normalize("томони-\n нгизда") == "tomoningizda"
    assert normalize("far\u00adzand") == "farzand"
    assert normalize("ko\u2018k-yashil") == "ko'k-yashil"


def test_watermark_excluded():
    n = normalize("so'z www.ziyouz.com kutubxonasi 153 boshqa")
    assert "ziyouz" not in n and "kutubxonasi" not in n
    assert n == "so'z 153 boshqa"


def test_apostrophe_variants_ikki():
    assert normalize("do‘xtir") == normalize("do'xtir") == normalize("doʻxtir") == normalize("do’xtir")
