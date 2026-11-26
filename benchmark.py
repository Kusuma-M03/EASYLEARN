"""Measure pre-processing latency (PDF extraction + cleaning + chunking) vs document size.
Usage: python benchmark.py   -> prints a table and saves bench.json. Needs no API key."""
import json, statistics as st, time
import fitz
from core.pdf_utils import extract_text, chunk_text

BASE = open("sample/sample_notes.txt").read().split()


def make_pdf(words: int) -> bytes:
    text = " ".join((BASE * (words // len(BASE) + 1))[:words])
    doc = fitz.open()
    per_page = 380
    toks = text.split()
    for i in range(0, len(toks), per_page):
        page = doc.new_page()
        page.insert_textbox(fitz.Rect(40, 40, 555, 800), " ".join(toks[i:i + per_page]), fontsize=9)
    data = doc.tobytes(); doc.close(); return data


def main(runs=30):
    out = []
    for n in (500, 1500, 3000, 6000):
        pdf = make_pdf(n); ext, chk = [], []
        for _ in range(runs):
            t0 = time.perf_counter(); text = extract_text(pdf, "x.pdf"); t1 = time.perf_counter()
            chunks = chunk_text(text); t2 = time.perf_counter()
            ext.append((t1 - t0) * 1000); chk.append((t2 - t1) * 1000)
        out.append(dict(words=n, pages=-(-n // 380), chunks=len(chunks), extract_ms=(st.mean(ext), st.stdev(ext)), chunk_ms=(st.mean(chk), st.stdev(chk))))
        print(out[-1])
    json.dump(out, open("bench.json", "w"), indent=1)


if __name__ == "__main__":
    main()
