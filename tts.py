"""Text-to-speech with gTTS (needs internet). Supports English, Kannada, Hindi."""
import io
import re

LANG_CODES = {"English": "en", "Kannada": "kn", "Hindi": "hi"}


def strip_markdown(text: str) -> str:
    text = re.sub(r"[*_`#>|]", "", text)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.M)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def speak(text: str, language: str, slow: bool = False) -> bytes:
    from gtts import gTTS

    buf = io.BytesIO()
    gTTS(strip_markdown(text), lang=LANG_CODES.get(language, "en"), slow=slow).write_to_fp(buf)
    return buf.getvalue()
