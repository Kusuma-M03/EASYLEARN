"""Run EasyLearn on sample files and print/save a readability results table.

Usage:  python evaluate.py sample/sample_notes.txt [more files...]
Needs GROQ_API_KEY or GEMINI_API_KEY in .env. Output: results.csv + a markdown table to paste in the report.
"""
import csv
import sys
import time

from core.llm import available_providers
from core.pdf_utils import extract_text
from core.prompts import LEVELS
from core.readability import metrics, number_retention
from core.simplify import Pipeline


def main(files):
    provs = available_providers()
    if not provs:
        sys.exit("Set GROQ_API_KEY or GEMINI_API_KEY in .env first.")
    name, key = next(iter(provs.items()))
    rows = []
    for f in files:
        text = extract_text(open(f, "rb").read(), f)
        base = metrics(text)
        rows.append([f, "Original", "-", base["Words"], base["Avg sentence length"],
                     base["Flesch Reading Ease (higher = easier)"],
                     base["Flesch-Kincaid Grade (lower = easier)"], "-", "-"])
        for level in LEVELS:
            t0 = time.time()
            out = Pipeline(name, key, level, "Dyslexia", "English").simplify(text)
            dt = round(time.time() - t0, 1)
            m = metrics(out)
            rows.append([f, "Simplified", level, m["Words"], m["Avg sentence length"],
                         m["Flesch Reading Ease (higher = easier)"],
                         m["Flesch-Kincaid Grade (lower = easier)"], dt, number_retention(text, out)])
    hdr = ["File", "Version", "Level", "Words", "AvgSentLen", "FleschEase", "FKGrade", "Seconds", "NumRetention"]
    with open("results.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(rows)
    print("| " + " | ".join(hdr) + " |\n|" + "---|" * len(hdr))
    for r in rows:
        print("| " + " | ".join(map(str, r)) + " |")


if __name__ == "__main__":
    main(sys.argv[1:] or ["sample/sample_notes.txt"])
