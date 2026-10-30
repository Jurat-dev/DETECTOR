"""Sahifa ichida moslik topish: aniq ibora -> so'z shakllari. Parcha va bbox."""
from __future__ import annotations
import re
from dataclasses import dataclass
from .normalize import normalize, normalize_with_map, tokens, stem

SNIPPET_RADIUS = 80


@dataclass
class Hit:
    start: int  # asl matndagi indeks
    end: int
    level: str  # exact | forms


def _word_spans(norm: str):
    for m in re.finditer(r"[a-z0-9']+", norm):
        s, e = m.start(), m.end()
        while s < e and norm[s] == "'":
            s += 1
        while e > s and norm[e - 1] == "'":
            e -= 1
        if s < e:
            yield s, e, norm[s:e]


def find_hits(text_raw: str, q: str, allow_forms: bool = True) -> list[Hit]:
    qn = normalize(q).strip()
    if not qn or not text_raw:
        return []
    norm, idx = normalize_with_map(text_raw)
    hits: list[Hit] = []
    pat = re.compile(r"(?<![a-z0-9'])" + re.escape(qn) + r"(?![a-z0-9])")
    for m in pat.finditer(norm):
        hits.append(Hit(idx[m.start()], idx[m.end() - 1] + 1, "exact"))
    if hits or not allow_forms:
        return hits
    qstems = [stem(t) for t in tokens(qn)]
    if not qstems:
        return []
    words = list(_word_spans(norm))
    n = len(qstems)
    for i in range(len(words) - n + 1):
        ok = True
        for j in range(n):
            w = words[i + j][2]
            if not (w.startswith(qstems[j]) and len(w) - len(qstems[j]) <= 8):
                ok = False
                break
        if ok:
            hits.append(Hit(idx[words[i][0]], idx[words[i + n - 1][1] - 1] + 1, "forms"))
    return hits


def snippet(text_raw: str, hit: Hit, radius: int = SNIPPET_RADIUS) -> dict:
    s = max(0, hit.start - radius)
    e = min(len(text_raw), hit.end + radius)
    # so'z chegarasiga moslash
    while s > 0 and not text_raw[s - 1].isspace() and hit.start - s < radius + 20:
        s -= 1
    while e < len(text_raw) and not text_raw[e].isspace() and e - hit.end < radius + 20:
        e += 1
    pre = re.sub(r"\s+", " ", text_raw[s:hit.start])
    mid = re.sub(r"\s+", " ", text_raw[hit.start:hit.end])
    post = re.sub(r"\s+", " ", text_raw[hit.end:e])
    return {
        "text": (("…" if s > 0 else "") + pre + mid + post + ("…" if e < len(text_raw) else "")),
        "highlight": mid,
        "before": ("…" if s > 0 else "") + pre,
        "after": post + ("…" if e < len(text_raw) else ""),
    }


def bboxes_for(words: list[dict], q: str, level: str) -> list[list[dict]]:
    """words: [{word,x0,y0,x1,y1}] -> har bir moslik uchun to'rtburchaklar ro'yxati."""
    qt = tokens(normalize(q))
    if not qt or not words:
        return []
    wn = [" ".join(tokens(normalize(w["word"]))) for w in words]
    qs = [stem(t) for t in qt]
    out = []
    n = len(qt)
    for i in range(len(words) - n + 1):
        ok = True
        for j in range(n):
            w = wn[i + j]
            if level == "exact":
                if w != qt[j] and not w.startswith(qt[j] + " "):
                    ok = False; break
            else:
                if not w.startswith(qs[j]):
                    ok = False; break
        if ok:
            out.append([{k: words[i + j][k] for k in ("x0", "y0", "x1", "y1")} for j in range(n)])
    return out
