"""Ma'lumot manbalari: LocalStore (JSON fayllar, xotirada) va PgStore (Supabase)."""
from __future__ import annotations
import json
import math
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from .config import settings
from .normalize import normalize, tokens, stem
from .chunking import chunk_text


def extract_words(pdf_path: Path, page_number: int) -> tuple[list[dict], float, float]:
    import fitz
    with fitz.open(pdf_path) as doc:
        if page_number < 1 or page_number > doc.page_count:
            return [], 0, 0
        pg = doc[page_number - 1]
        ws = [{"word": w[4], "x0": w[0], "y0": w[1], "x1": w[2], "y1": w[3]} for w in pg.get_text("words")]
        return ws, pg.rect.width, pg.rect.height


class BaseStore:
    def list_books(self) -> list[dict]: ...
    def get_book(self, book_id: int) -> dict | None: ...
    def candidate_pages(self, q: str, book_id: int | None = None) -> Iterable[tuple[dict, dict]]: ...
    def page_words(self, book_id: int, page_number: int) -> tuple[list[dict], float, float]: ...
    def semantic(self, q: str, k: int = 8) -> list[dict]: ...

    def pdf_path(self, book: dict) -> Path | None:
        p = Path(book.get("file") or "")
        cands = [p] if p.is_absolute() else []
        cands += [settings.pdf_dir / p.name, settings.pdf_dir / str(book.get("file", ""))]
        for c in cands:
            if c.name and c.exists():
                return c
        return None


def _trigrams(s: str) -> Counter:
    s = f"  {s} "
    return Counter(s[i:i + 3] for i in range(len(s) - 2))


class LocalStore(BaseStore):
    """Supabase'siz rejim: data/*.json fayllarini xotiraga yuklaydi."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = Path(data_dir or settings.data_dir)
        self.books: list[dict] = []
        self.pages: dict[int, list[dict]] = {}
        self.chunks: list[dict] = []
        self._emb = None
        self.reload()

    def reload(self):
        self.books, self.pages, self.chunks, self._emb = [], {}, [], None
        files = sorted(self.data_dir.glob("*.json")) if self.data_dir.exists() else []
        for f in files:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(d, dict) or "pages" not in d:
                continue
            bid = len(self.books) + 1
            pages = []
            for p in d.get("pages") or []:
                raw = p.get("text_raw") or ""
                pages.append({"page_number": int(p.get("page", len(pages) + 1)), "text_raw": raw,
                              "text_norm": normalize(raw), "source": p.get("source", "text"),
                              "ocr_confidence": p.get("ocr_confidence")})
            book = {"id": bid, "title": d.get("title") or f.stem, "author": d.get("author") or "",
                    "file": d.get("file") or "", "page_count": d.get("page_count") or len(pages),
                    "source_type": d.get("source_type") or "text", "json": f.name}
            self.books.append(book)
            self.pages[bid] = pages
            for p in pages:
                for c in chunk_text(p["text_raw"]):
                    self.chunks.append({"book_id": bid, "page_number": p["page_number"], "text": c,
                                        "norm": normalize(c)})

    def list_books(self):
        return self.books

    def get_book(self, book_id):
        return next((b for b in self.books if b["id"] == book_id), None)

    def candidate_pages(self, q, book_id=None):
        qs = [stem(t) for t in tokens(normalize(q))]
        if not qs:
            return
        for b in self.books:
            if book_id is not None and b["id"] != book_id:
                continue
            for p in self.pages[b["id"]]:
                if all(s in p["text_norm"] for s in qs):
                    yield b, p

    @lru_cache(maxsize=512)
    def _words_cached(self, path: str, page: int):
        return extract_words(Path(path), page)

    def page_words(self, book_id, page_number):
        b = self.get_book(book_id)
        p = self.pdf_path(b) if b else None
        if not p:
            return [], 0, 0
        return self._words_cached(str(p), page_number)

    def semantic(self, q, k=8):
        if not self.chunks:
            return []
        if settings.enable_semantic:
            from .embeddings import embed_passages, embed_query
            import numpy as np
            if self._emb is None:
                self._emb = np.array(embed_passages([c["text"] for c in self.chunks]))
            sims = self._emb @ np.array(embed_query(q))
            order = sims.argsort()[::-1][:k]
            return [{**self.chunks[i], "score": float(sims[i])} for i in order]
        # Model yo'q: belgi trigrammalari bo'yicha taxminiy o'xshashlik
        qt = _trigrams(normalize(q))
        qn = math.sqrt(sum(v * v for v in qt.values())) or 1
        scored = []
        for c in self.chunks:
            ct = _trigrams(c["norm"])
            dot = sum(v * ct.get(g, 0) for g, v in qt.items())
            if dot:
                scored.append((dot / (qn * (math.sqrt(sum(v * v for v in ct.values())) or 1)), c))
        scored.sort(key=lambda x: -x[0])
        return [{**c, "score": s} for s, c in scored[:k] if s > 0.08]


class PgStore(BaseStore):
    """Supabase Postgres: pg_trgm + FTS nomzodlar, pgvector semantik qidiruv."""

    def __init__(self, dsn: str | None = None):
        import psycopg
        from psycopg.rows import dict_row
        self.conn = psycopg.connect(dsn or settings.database_url, row_factory=dict_row, autocommit=True)

    def list_books(self):
        rows = self.conn.execute("select id,title,author,file_url as file,page_count,source_type from books order by id").fetchall()
        return list(rows)

    def get_book(self, book_id):
        return self.conn.execute("select id,title,author,file_url as file,page_count,source_type from books where id=%s",
                                 (book_id,)).fetchone()

    def candidate_pages(self, q, book_id=None):
        qs = [stem(t) for t in tokens(normalize(q))]
        if not qs:
            return
        tsq = " & ".join(s.replace("'", "") + ":*" for s in qs if s.replace("'", ""))
        conds = " and ".join(["p.text_norm like %s"] * len(qs))
        params: list = [f"%{s}%" for s in qs]
        sql = (f"select p.*, b.id as b_id from pages p join books b on b.id=p.book_id "
               f"where ({conds} or p.tsv @@ to_tsquery('simple', %s))")
        params.append(tsq or "''")
        if book_id is not None:
            sql += " and p.book_id=%s"; params.append(book_id)
        sql += " order by p.book_id, p.page_number"
        books = {b["id"]: b for b in self.list_books()}
        for r in self.conn.execute(sql, params):
            yield books[r["book_id"]], r

    def page_words(self, book_id, page_number):
        rows = self.conn.execute(
            "select w.word,w.x0,w.y0,w.x1,w.y1,w.page_width,w.page_height from words w join pages p on p.id=w.page_id "
            "where p.book_id=%s and p.page_number=%s order by w.id", (book_id, page_number)).fetchall()
        if not rows:
            return [], 0, 0
        return [dict(r) for r in rows], rows[0]["page_width"] or 0, rows[0]["page_height"] or 0

    def semantic(self, q, k=8):
        if not settings.enable_semantic:
            rows = self.conn.execute(
                "select book_id,page_number,text,similarity(text_norm,%s) as score from chunks "
                "where text_norm %% %s order by score desc limit %s", (normalize(q), normalize(q), k)).fetchall()
            return [dict(r) for r in rows]
        from .embeddings import embed_query
        emb = embed_query(q)
        rows = self.conn.execute("select * from match_chunks(%s::vector, %s)", (str(emb), k)).fetchall()
        return [{**dict(r), "score": r["similarity"]} for r in rows]


_store: BaseStore | None = None


def get_store() -> BaseStore:
    global _store
    if _store is None:
        _store = PgStore() if settings.search_backend == "postgres" else LocalStore()
    return _store


def set_store(s: BaseStore):
    global _store
    _store = s
