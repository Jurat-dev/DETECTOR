"""RAG chatbot: faqat topilgan parchalardan javob, manbalar bilan."""
from __future__ import annotations
from .config import settings
from .matching import find_hits, snippet
from .normalize import normalize, tokens
from .store import BaseStore

NOT_FOUND = "Bu haqda kitoblarda ma’lumot topilmadi."
STOP = {"va", "bu", "u", "nima", "kim", "qanday", "qaysi", "haqida", "bilan", "uchun", "ham", "edi", "deb",
        "qayerda", "nega", "qachon", "mi", "bormi", "the", "a"}

SYSTEM = (
    "Sen 'Detector' yordamchisisan. Faqat quyida berilgan kitob parchalariga tayanib o'zbek tilida javob ber. "
    "Har bir da'vodan keyin manbani [1], [2] ko'rinishida ko'rsat. Parchalarda javob bo'lmasa, aynan shunday yoz: "
    f"\"{NOT_FOUND}\" O'zingdan hech narsa qo'shma."
)


def retrieve(store: BaseStore, question: str, k: int = 6) -> list[dict]:
    out, seen = [], set()
    keys = [t for t in tokens(normalize(question)) if t not in STOP and len(t) > 2]
    # 1) kalit so'zlar bo'yicha aniq/shakl moslik
    scored = []
    for kw in keys:
        for b, p in store.candidate_pages(kw):
            hits = find_hits(p["text_raw"], kw)
            if hits:
                scored.append((len(hits), b, p, hits[0]))
    agg: dict[tuple, list] = {}
    for n, b, p, h in scored:
        key = (b["id"], p["page_number"])
        a = agg.setdefault(key, [0, b, p, h, 0])
        a[0] += n; a[4] += 1
    for _, (n, b, p, h, kc) in sorted(agg.items(), key=lambda x: (-x[1][4], -x[1][0]))[:k]:
        seen.add((b["id"], p["page_number"]))
        out.append({"book_id": b["id"], "title": b["title"], "page": p["page_number"],
                    "text": snippet(p["text_raw"], h, radius=350)["text"]})
    # 2) ma'no bo'yicha
    for c in store.semantic(question, k):
        key = (c["book_id"], c["page_number"])
        if key in seen or len(out) >= k:
            continue
        b = store.get_book(c["book_id"])
        seen.add(key)
        out.append({"book_id": c["book_id"], "title": b["title"] if b else "", "page": c["page_number"],
                    "text": c["text"], "approximate": True})
    return out


def _llm_answer(question: str, passages: list[dict]) -> str | None:
    if not settings.openai_api_key:
        return None
    try:
        from llama_index.core.llms import ChatMessage
        from llama_index.llms.openai import OpenAI
    except ImportError:
        return None
    ctx = "\n\n".join(f"[{i+1}] «{p['title']}», {p['page']}-bet:\n{p['text']}" for i, p in enumerate(passages))
    llm = OpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
    resp = llm.chat([ChatMessage(role="system", content=SYSTEM),
                     ChatMessage(role="user", content=f"Parchalar:\n{ctx}\n\nSavol: {question}")])
    return (resp.message.content or "").strip()


def chat(store: BaseStore, question: str) -> dict:
    question = (question or "").strip()
    passages = retrieve(store, question) if question else []
    if not passages:
        return {"answer": NOT_FOUND, "found": False, "sources": []}
    sources = [{"n": i + 1, **p} for i, p in enumerate(passages)]
    ans = _llm_answer(question, passages)
    if ans is None:
        # LLM kaliti yo'q: faqat parchalarni qaytaramiz (to'qimaydi)
        ans = "Kitoblardan topilgan parchalar:\n\n" + "\n\n".join(
            f"[{s['n']}] «{s['title']}», {s['page']}-bet: {s['text'][:280]}…" for s in sources[:3])
        mode = "extractive"
    else:
        mode = "llm"
    found = NOT_FOUND not in ans
    return {"answer": ans, "found": found, "mode": mode, "sources": sources if found else []}
