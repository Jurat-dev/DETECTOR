def chunk_text(text: str, size: int = 700, overlap: int = 120) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    out, i = [], 0
    while i < len(text):
        j = min(len(text), i + size)
        if j < len(text):
            sp = text.rfind(" ", i + size // 2, j)
            if sp > 0:
                j = sp
        out.append(text[i:j].strip())
        if j >= len(text):
            break
        i = max(j - overlap, i + 1)
    return [c for c in out if c]
