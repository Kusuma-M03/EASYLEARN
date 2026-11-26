"""Text extraction, cleaning and chunking."""
import re


def extract_text(data: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        import fitz  # PyMuPDF

        with fitz.open(stream=data, filetype="pdf") as doc:
            pages = [p.get_text("text") for p in doc]
        text = "\n\n".join(pages)
    else:
        text = data.decode("utf-8", errors="ignore")
    return clean_text(text)


def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"-\n(\w)", r"\1", text)          # fix hyphenated line breaks
    text = re.sub(r"(?<![.!?:\n])\n(?!\n)", " ", text)  # join wrapped lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, max_words: int = 1000) -> list:
    """Split on paragraph boundaries into chunks of at most ~max_words words."""
    paras = [p for p in text.split("\n\n") if p.strip()]
    chunks, cur, count = [], [], 0
    for p in paras:
        w = len(p.split())
        if w > max_words:  # a single huge paragraph: split by sentences
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                sw = len(s.split())
                if count + sw > max_words and cur:
                    chunks.append("\n\n".join(cur)); cur, count = [], 0
                cur.append(s); count += sw
            continue
        if count + w > max_words and cur:
            chunks.append("\n\n".join(cur)); cur, count = [], 0
        cur.append(p); count += w
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks
