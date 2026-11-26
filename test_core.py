from core.pdf_utils import clean_text, chunk_text
from core.tts import strip_markdown
from core.readability import compare, number_retention


def test_clean_joins_wrapped_lines():
    assert clean_text("Hello\nworld.\n\nNew para") == "Hello world.\n\nNew para"


def test_chunking_respects_limit():
    text = "\n\n".join(["word " * 300] * 10)
    chunks = chunk_text(text, max_words=1000)
    assert all(len(c.split()) <= 1000 for c in chunks)
    assert len(chunks) >= 3


def test_strip_markdown():
    assert strip_markdown("**Hi** `x`\n- item") == "Hi x item"


def test_readability_easier_text_scores_better():
    hard = "Photosynthesis constitutes the biochemical conversion of electromagnetic radiation into chemical energy."
    easy = "Plants use sunlight. They make food from it. This is called photosynthesis."
    rows = {r["Metric"]: r for r in compare(hard, easy)}
    fre = "Flesch Reading Ease (higher = easier)"
    assert rows[fre]["Simplified"] > rows[fre]["Original"]


def test_number_retention():
    assert number_retention("Add 5 g and 10 ml in 2 steps", "Use 5 g and 10 ml") == 0.67
    assert number_retention("no digits", "anything") == 1.0
