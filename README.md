# EasyLearn: GenAI Accessibility Assistant

Turns study material (PDF/TXT/pasted notes) into versions that are easier to read, hear and understand for students with dyslexia, ADHD, low vision, or language barriers.

## Features
- Simplification at 3 reading levels (Grade 5 / Grade 8 / College)
- 4 learner profiles (Dyslexia, ADHD, Non-native reader, Low vision) that change the prompt style
- Output in English, Kannada, Hindi
- Key points, glossary table, step-by-step explanation, self-check questions
- Audio summary (gTTS) with MP3 download
- Dyslexia-friendly font, high-contrast mode, adjustable text size and line spacing
- Before/after readability scores (Flesch Reading Ease, Flesch-Kincaid Grade)

## Run
```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add GROQ_API_KEY or GEMINI_API_KEY (both free)
streamlit run app.py
```
Free keys: https://console.groq.com  |  https://aistudio.google.com

Try it with `sample/sample_notes.txt`.

## Tests
```bash
pytest -q tests
```

## Structure
```
app.py                 Streamlit UI
core/llm.py            Groq / Gemini wrapper with retries
core/prompts.py        All prompt templates
core/pdf_utils.py      Extraction, cleaning, chunking
core/simplify.py       Pipeline (chunk -> simplify -> extras)
core/tts.py            Text-to-speech
core/readability.py    Readability metrics
tests/test_core.py     Unit tests
```

## Limitations
Scanned PDFs need OCR (not included). The LLM may lose nuance or hallucinate; the UI reminds users to verify. Kannada/Hindi quality depends on the model. Readability metrics are English-only. TTS needs internet.
