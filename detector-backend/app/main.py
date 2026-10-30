from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .store import get_store
from . import search as S
from .chat import chat as do_chat

app = FastAPI(title="Detector API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"ok": True, "backend": settings.search_backend, "books": len(get_store().list_books())}


@app.get("/books")
def books():
    return [S._book_out(b) for b in get_store().list_books()]


@app.get("/search")
def search(q: str = Query(..., min_length=1, max_length=200)):
    return S.search(get_store(), q)


@app.get("/books/{book_id}")
def book(book_id: int):
    b = get_store().get_book(book_id)
    if not b:
        raise HTTPException(404, "Kitob topilmadi")
    return S._book_out(b)


@app.get("/books/{book_id}/matches")
def matches(book_id: int, q: str = Query(..., min_length=1, max_length=200)):
    r = S.book_matches(get_store(), book_id, q)
    if r is None:
        raise HTTPException(404, "Kitob topilmadi")
    return r


@app.get("/books/{book_id}/pdf")
def pdf(book_id: int):
    st = get_store()
    b = st.get_book(book_id)
    if not b:
        raise HTTPException(404, "Kitob topilmadi")
    p = st.pdf_path(b)
    if not p:
        raise HTTPException(404, "PDF fayl topilmadi")
    return FileResponse(p, media_type="application/pdf", headers={"Accept-Ranges": "bytes"})


class ChatIn(BaseModel):
    question: str


@app.post("/chat")
def chat(body: ChatIn):
    return do_chat(get_store(), body.question)
