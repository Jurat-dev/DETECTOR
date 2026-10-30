"""Qidiruv: 1) aniq ibora  2) so'z shakllari  3) ma'no (taxminiy)."""
from __future__ import annotations
from .matching import find_hits, snippet, bboxes_for
from .store import BaseStore

MAX_SNIPPETS = 3


def _book_out(b: dict) -> dict:
    return {k: b.get(k) for k in ("id", "title", "author", "page_count", "source_type")}


def search(store: BaseStore, q: str, semantic_k: int = 6) -> dict:
    q = (q or "").strip()
    res: dict[int, dict] = {}
    for b, p in store.candidate_pages(q):
        hits = find_hits(p["text_raw"], q)
        if not hits:
            continue
        r = res.setdefault(b["id"], {"book": _book_out(b), "count": 0, "exact_count": 0, "forms_count": 0,
                                     "pages": 0, "snippets": [], "match_type": "forms"})
        r["count"] += len(hits)
        r["pages"] += 1
        for h in hits:
            r[f"{h.level}_count"] += 1
        if any(h.level == "exact" for h in hits):
            r["match_type"] = "exact"
        # aniq mosliklar parchalarda birinchi ko'rsatiladi
        h = next((x for x in hits if x.level == "exact"), hits[0])
        cand = r.setdefault("_cand", [])
        if sum(1 for c in cand if c["match_type"] == h.level) < MAX_SNIPPETS:
            cand.append({"page": p["page_number"], "match_type": h.level, **snippet(p["text_raw"], h)})
    for r in res.values():
        cand = r.pop("_cand", [])
        cand.sort(key=lambda c: (c["match_type"] != "exact", c["page"]))
        r["snippets"] = cand[:MAX_SNIPPETS]
    results = sorted(res.values(), key=lambda r: (r["match_type"] != "exact", -r["exact_count"], -r["count"]))
    approximate = []
    if q and not results:
        for c in store.semantic(q, semantic_k):
            b = store.get_book(c["book_id"])
            if b:
                txt = c["text"]
                approximate.append({"book": _book_out(b), "page": c["page_number"], "score": round(float(c["score"]), 4),
                                    "text": txt[:300] + ("…" if len(txt) > 300 else ""), "match_type": "semantic",
                                    "approximate": True})
    return {"query": q, "total": sum(r["count"] for r in results), "books": results,
            "approximate": approximate}


def book_matches(store: BaseStore, book_id: int, q: str, with_coords: bool = True) -> dict | None:
    b = store.get_book(book_id)
    if not b:
        return None
    pages = list(store.candidate_pages(q, book_id))
    page_hits = [(p, find_hits(p["text_raw"], q)) for _, p in pages]
    page_hits = [(p, h) for p, h in page_hits if h]
    has_exact = any(x.level == "exact" for _, hs in page_hits for x in hs)
    matches = []
    for p, hits in page_hits:
        if has_exact:
            hits = [h for h in hits if h.level == "exact"]
            if not hits:
                continue
        boxes, pw, ph = [], 0, 0
        if with_coords:
            words, pw, ph = store.page_words(book_id, p["page_number"])
            boxes = bboxes_for(words, q, hits[0].level)
        for i, h in enumerate(hits):
            matches.append({"index": len(matches), "page": p["page_number"], "match_type": h.level,
                            **snippet(p["text_raw"], h),
                            "bbox": boxes[i] if i < len(boxes) else [],
                            "page_width": pw, "page_height": ph})
    return {"book": _book_out(b), "query": q, "total": len(matches), "matches": matches}
