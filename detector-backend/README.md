# Detector — Backend (FastAPI)

Foydalanuvchi yozgan so‘z yoki ibora faqat yuklangan kitoblardan qidiriladi: **qaysi kitob, qaysi bet, qaysi parcha**.

## Tuzilishi
```
app/main.py        API endpointlar
app/search.py      qidiruv: aniq ibora → so‘z shakllari → ma’no (taxminiy)
app/matching.py    sahifa ichida moslik, parcha, bbox koordinatalar
app/normalize.py   o‘/g‘ apostroflarini birlashtirish, kirill ↔ lotin
app/store.py       LocalStore (JSON, xotirada) va PgStore (Supabase)
app/chat.py        RAG chatbot (LlamaIndex + OpenAI), faqat parchalardan javob
app/embeddings.py  intfloat/multilingual-e5-large (1024)
ingest/load.py     data/*.json → Postgres (+ PyMuPDF so‘z koordinatalari + embedding)
sql/schema.sql     books, pages, chunks (pgvector 1024), words; pg_trgm + FTS
tests/             pytest
```

## O‘rnatish
Python 3.12+ kerak.
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
```
`data/` papkasida har bir kitob uchun JSON bo‘lishi kerak:
`{title, author, file, page_count, source_type, pages:[{page, text_raw, source, ocr_confidence}]}`.
PDF fayllar `PDF_DIR` (standart: `../detector/KITOBLAR`) papkasida.

## Ishga tushirish
### 1) Lokal rejim (Supabase’siz, test uchun)
`.env` da `SEARCH_BACKEND=local`. JSON fayllar xotiraga yuklanadi, so‘z koordinatalari PDFdan to‘g‘ridan-to‘g‘ri olinadi.
```bash
uvicorn app.main:app --reload --port 8000
```
### 2) Supabase rejimi
1. Supabase loyihasida SQL Editor orqali `sql/schema.sql` ni bajaring (yoki `--schema`).
2. `.env` da `SEARCH_BACKEND=postgres`, `DATABASE_URL=...`, semantik qidiruv uchun `ENABLE_SEMANTIC=true`.
3. Yuklash: `python -m ingest.load --schema` (embeddingsiz: `--no-embed`).
4. `uvicorn app.main:app --port 8000`

Chatbot uchun `OPENAI_API_KEY` ni kiriting. Kalit bo‘lmasa chatbot faqat topilgan parchalarni qaytaradi (o‘zidan to‘qimaydi).

## API
| Endpoint | Vazifa |
|---|---|
| `GET /search?q=` | Kitoblar + topilganlar soni + 2–3 parcha (bet bilan). Aniq moslik topilmasa `approximate` (taxminiy) natijalar |
| `GET /books/{id}/matches?q=` | Kitob ichidagi mosliklar: bet, parcha, `bbox` (PDF nuqtalarida, chap-yuqori 0,0) |
| `POST /chat` `{question}` | Javob + manbalar; topilmasa “Bu haqda kitoblarda ma’lumot topilmadi.” |
| `GET /books/{id}/pdf` | PDF fayl |
| `GET /books`, `GET /health` | Yordamchi |

## Test
```bash
pytest -q
```
