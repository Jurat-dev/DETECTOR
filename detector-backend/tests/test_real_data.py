"""Haqiqiy data/*.json bo'lsa, ular bilan tutun testi."""
import pytest
from app.config import settings
from app.store import LocalStore
from app.search import search, book_matches


def test_real_data_smoke():
    s = LocalStore(settings.data_dir)
    if not s.books:
        pytest.skip("data/ bo'sh")
    r = search(s, "va")
    assert r["books"]
    b = r["books"][0]
    m = book_matches(s, b["book"]["id"], "va", with_coords=False)
    assert m["total"] >= 1
