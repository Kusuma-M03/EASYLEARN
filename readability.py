"""Before/after readability metrics (English only; formulas are English-specific)."""
import re


def _sentences(text: str) -> int:
    return max(1, len(re.findall(r"[.!?]+", text)))


def metrics(text: str) -> dict:
    import textstat

    words = max(1, len(text.split()))
    return {
        "Words": words,
        "Avg sentence length": round(words / _sentences(text), 1),
        "Flesch Reading Ease (higher = easier)": round(textstat.flesch_reading_ease(text), 1),
        "Flesch-Kincaid Grade (lower = easier)": round(textstat.flesch_kincaid_grade(text), 1),
    }


def compare(original: str, simplified: str) -> list:
    a, b = metrics(original), metrics(simplified)
    return [{"Metric": k, "Original": a[k], "Simplified": b[k]} for k in a]


def number_retention(original: str, simplified: str) -> float:
    """Share of numbers in the source that still appear in the output (faithfulness proxy, 0-1)."""
    nums = set(re.findall(r"\d+(?:[.,]\d+)?", original))
    if not nums:
        return 1.0
    out = set(re.findall(r"\d+(?:[.,]\d+)?", simplified))
    return round(len(nums & out) / len(nums), 2)
