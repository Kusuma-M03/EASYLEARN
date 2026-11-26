"""Thin LLM wrapper supporting Groq and Gemini (both have free tiers)."""
import os
import time

from dotenv import load_dotenv

load_dotenv()


class LLMError(Exception):
    pass


def available_providers(groq_key: str = "", gemini_key: str = "") -> dict:
    """Return {provider_name: api_key} for every provider with a key."""
    found = {}
    gk = groq_key or os.getenv("GROQ_API_KEY", "")
    mk = gemini_key or os.getenv("GEMINI_API_KEY", "")
    if gk:
        found["Groq (GPT-OSS 120B)"] = gk
    if mk:
        found["Gemini"] = mk
    return found


def _call_groq(key: str, system: str, prompt: str, temperature: float) -> str:
    from groq import Groq

    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def _call_gemini(key: str, system: str, prompt: str, temperature: float) -> str:
    from google import genai

    client = genai.Client(api_key=key)
    resp = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        contents=prompt,
        config={"system_instruction": system, "temperature": temperature},
    )
    return (resp.text or "").strip()


def generate(provider: str, key: str, system: str, prompt: str,
             temperature: float = 0.3, retries: int = 3) -> str:
    """Call the chosen provider with simple exponential-backoff retries."""
    fn = _call_groq if provider.startswith("Groq") else _call_gemini
    last = None
    for attempt in range(retries):
        try:
            out = fn(key, system, prompt, temperature)
            if out:
                return out
            last = LLMError("Empty response from model")
        except Exception as e:  # network / rate limit / auth
            last = e
        time.sleep(2 ** attempt)
    raise LLMError(f"LLM call failed after {retries} tries: {last}")
