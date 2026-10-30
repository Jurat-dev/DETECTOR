"""JSON kitoblarni Supabase Postgres'ga yuklash.

python -m ingest.load [--no-embed] [--no-words] [--schema]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings, BASE  # noqa: E402
from app.normalize import normalize  # noqa: E402
from app.chunking import chunk_text  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", action="store_true", help="sql/schema.sql ni avval ishga tushirish")
    ap.add_argument("--no-embed", action="store_true")
    ap.add_argument("--no-words", action="store_true")
    a = ap.parse_args()

    import psycopg
    conn = psycopg.connect(settings.database_url, autocommit=False)
    if a.schema:
        conn.execute((BASE / "sql" / "schema.sql").read_text())
        conn.commit()
    files = sorted(settings.data_dir.glob("*.json"))
    print(f"{len(files)} ta JSON topildi")
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        title = d.get("title") or f.stem
        fname = Path(d.get("file") or "").name
        conn.execute("delete from books where file_url=%s", (fname,))
        bid = conn.execute("insert into books(title,author,file_url,page_count,source_type) values(%s,%s,%s,%s,%s) returning id",
                           (title, d.get("author"), fname, d.get("page_count") or len(d["pages"]),
                            d.get("source_type") or "text")).fetchone()[0]
        pdf = settings.pdf_dir / fname
        doc = None
        if not a.no_words and pdf.exists():
            import fitz
            doc = fitz.open(pdf)
        chunk_rows = []
        for p in d["pages"]:
            raw = p.get("text_raw") or ""
            pn = int(p["page"])
            pid = conn.execute("insert into pages(book_id,page_number,text_raw,text_norm,source,ocr_confidence) "
                               "values(%s,%s,%s,%s,%s,%s) returning id",
                               (bid, pn, raw, normalize(raw), p.get("source") or "text", p.get("ocr_confidence"))).fetchone()[0]
            if doc is not None and 1 <= pn <= doc.page_count:
                pg = doc[pn - 1]
                rows = [(pid, w[4], normalize(w[4]), w[0], w[1], w[2], w[3], pg.rect.width, pg.rect.height)
                        for w in pg.get_text("words")]
                with conn.cursor() as cur:
                    cur.executemany("insert into words(page_id,word,word_norm,x0,y0,x1,y1,page_width,page_height) "
                                    "values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
            for c in chunk_text(raw):
                chunk_rows.append((bid, pn, c, normalize(c)))
        embs = [None] * len(chunk_rows)
        if not a.no_embed and chunk_rows:
            from app.embeddings import embed_passages
            embs = [str(e) for e in embed_passages([r[2] for r in chunk_rows])]
        with conn.cursor() as cur:
            cur.executemany("insert into chunks(book_id,page_number,text,text_norm,embedding) values(%s,%s,%s,%s,%s::vector)",
                            [(*r, e) for r, e in zip(chunk_rows, embs)])
        conn.commit()
        print(f"✓ {title}: {len(d['pages'])} bet, {len(chunk_rows)} parcha")


if __name__ == "__main__":
    main()
