import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PAGES = [
    "Kitob — bilim manbai. Men kitobni sevaman. O‘zbekiston go‘zal yurt.",
    "Kecha va kunduz romanida Zebi qo'shiq aytdi. Kitoblar javonda turardi.",
    "Ўзбекистон буюк келажак сари. Ғалаба бизники.",
]


@pytest.fixture()
def store(tmp_path, monkeypatch):
    import fitz
    from app.config import settings
    pdf_dir = tmp_path / "pdf"; pdf_dir.mkdir()
    doc = fitz.open()
    for t in PAGES:
        pg = doc.new_page()
        pg.insert_textbox(fitz.Rect(50, 50, 550, 800), t.replace("‘", "'").replace("—", "-"), fontsize=12)
    doc.save(pdf_dir / "namuna.pdf")
    data = tmp_path / "data"; data.mkdir()
    (data / "namuna.json").write_text(json.dumps({
        "title": "Namuna kitob", "author": "Test", "file": "namuna.pdf", "page_count": 3, "source_type": "text",
        "pages": [{"page": i + 1, "text_raw": t, "source": "text", "ocr_confidence": None} for i, t in enumerate(PAGES)],
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(settings, "pdf_dir", pdf_dir)
    monkeypatch.setattr(settings, "enable_semantic", False)
    monkeypatch.setattr(settings, "openai_api_key", "")
    from app.store import LocalStore, set_store
    s = LocalStore(data)
    set_store(s)
    return s
