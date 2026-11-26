"""All prompt templates in one place (prompt engineering is a key GenAI concept here)."""

SYSTEM = (
    "You are EasyLearn, an accessibility assistant that rewrites study material "
    "for students with learning difficulties. Rules: never invent facts, never "
    "add information that is not in the source, keep numbers, names, formulas "
    "and dates exactly as in the source, and keep the original meaning."
)

LEVELS = {
    "Grade 5": "a 10-year-old (Grade 5): very common words, sentences under 12 words",
    "Grade 8": "a 13-year-old (Grade 8): simple words, sentences under 18 words",
    "College (light)": "a first-year college student: clear language, brief technical terms allowed",
}

PROFILES = {
    "Dyslexia": "Use short sentences and short paragraphs. Avoid idioms, long words and dense blocks of text.",
    "ADHD": "Break content into small chunks with bullet points. Put the most important idea first. **Bold** key terms.",
    "Non-native English reader": "Avoid idioms and phrasal verbs. Explain jargon in simple words right where it appears.",
    "Low vision / general": "Use plain structure with clear headings and short paragraphs.",
}


def _lang(language: str) -> str:
    return f"Write the answer in {language}." + (
        " Keep technical terms in English in brackets after the translation."
        if language != "English" else ""
    )


def simplify(text: str, level: str, profile: str, language: str) -> str:
    return f"""Rewrite the study text below for {LEVELS[level]}.
Learner profile: {PROFILES[profile]}
Keep ALL important information. Do not summarize away details. Use markdown (short paragraphs, bullets where helpful).
{_lang(language)}

SOURCE TEXT:
\"\"\"
{text}
\"\"\""""


def key_points(text: str, level: str, language: str) -> str:
    return f"""From the text below, list the 5 to 8 KEY POINTS a student must remember.
Write for {LEVELS[level]}. One short bullet each, starting with a **bold** keyword.
{_lang(language)}

TEXT:
\"\"\"
{text}
\"\"\""""


def glossary(text: str, level: str, language: str) -> str:
    return f"""Find the 6 to 12 hardest terms in the text and explain each in simple words for {LEVELS[level]}.
Output ONLY a markdown table with columns: | Term | Simple meaning | Example |
{_lang(language)}

TEXT:
\"\"\"
{text}
\"\"\""""


def steps(text: str, level: str, language: str) -> str:
    return f"""Explain the main idea or process in the text as a numbered step-by-step explanation
(max 8 steps, one short sentence per step) for {LEVELS[level]}.
If the text is not a process, give the logical order of ideas instead.
{_lang(language)}

TEXT:
\"\"\"
{text}
\"\"\""""


def audio_script(text: str, level: str, language: str) -> str:
    return f"""Write a friendly spoken summary (about 120 to 160 words) of the text below for {LEVELS[level]}.
Plain text ONLY: no markdown, no bullets, no symbols, no emojis. Natural spoken sentences.
{_lang(language)}

TEXT:
\"\"\"
{text}
\"\"\""""


def quiz(text: str, level: str, language: str) -> str:
    return f"""Create 4 quick self-check questions with short answers based on the text, for {LEVELS[level]}.
Format: **Q1.** question  then  *Answer:* answer.
{_lang(language)}

TEXT:
\"\"\"
{text}
\"\"\""""
