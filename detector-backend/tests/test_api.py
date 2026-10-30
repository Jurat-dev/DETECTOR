from fastapi.testclient import TestClient
from app.main import app


def test_search_exact(store):
    c = TestClient(app)
    r = c.get("/search", params={"q": "o'zbekiston"}).json()
    assert r["books"][0]["count"] == 2  # lotin + kirill
    assert r["books"][0]["match_type"] == "exact"
    assert {s["page"] for s in r["books"][0]["snippets"]} == {1, 3}


def test_search_forms(store):
    r = TestClient(app).get("/search", params={"q": "kitob"}).json()
    b = r["books"][0]
    assert b["exact_count"] == 1 and b["forms_count"] == 1 and b["snippets"][0]["match_type"] == "exact"


def test_search_forms_only(store):
    r = TestClient(app).get("/search", params={"q": "kitoblarni"}).json()
    b = r["books"][0]
    assert b["match_type"] == "forms" and b["count"] >= 3


def test_semantic_fallback(store):
    r = TestClient(app).get("/search", params={"q": "javondagi qo'shiqlar"}).json()
    assert r["books"] == [] and all(a["approximate"] for a in r["approximate"])


def test_matches_bbox(store):
    r = TestClient(app).get("/books/1/matches", params={"q": "kitobni"}).json()
    assert r["total"] == 1 and r["matches"][0]["page"] == 1
    assert r["matches"][0]["bbox"] and r["matches"][0]["page_width"] > 0


def test_pdf(store):
    r = TestClient(app).get("/books/1/pdf")
    assert r.status_code == 200 and r.content[:4] == b"%PDF"
    assert TestClient(app).get("/books/99/pdf").status_code == 404


def test_chat(store):
    c = TestClient(app)
    r = c.post("/chat", json={"question": "Zebi nima qildi?"}).json()
    assert r["found"] and r["sources"][0]["page"] == 2
    r = c.post("/chat", json={"question": "xyzzy plutonium"}).json()
    assert not r["found"] and "topilmadi" in r["answer"]
