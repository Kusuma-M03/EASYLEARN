"""Pipeline: chunk -> simplify -> derived outputs."""
from . import prompts
from .llm import generate
from .pdf_utils import chunk_text

MAX_CONTEXT_CHARS = 12000  # cap for derived outputs (key points, glossary, ...)


class Pipeline:
    def __init__(self, provider: str, key: str, level: str, profile: str, language: str):
        self.provider, self.key = provider, key
        self.level, self.profile, self.language = level, profile, language

    def _gen(self, prompt: str) -> str:
        return generate(self.provider, self.key, prompts.SYSTEM, prompt)

    def simplify(self, text: str, progress=None) -> str:
        chunks = chunk_text(text)
        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(self._gen(prompts.simplify(c, self.level, self.profile, self.language)))
            if progress:
                progress(i / len(chunks))
        return "\n\n".join(parts)

    def _ctx(self, simplified: str) -> str:
        return simplified[:MAX_CONTEXT_CHARS]

    def key_points(self, simplified: str) -> str:
        return self._gen(prompts.key_points(self._ctx(simplified), self.level, self.language))

    def glossary(self, simplified: str) -> str:
        return self._gen(prompts.glossary(self._ctx(simplified), self.level, self.language))

    def steps(self, simplified: str) -> str:
        return self._gen(prompts.steps(self._ctx(simplified), self.level, self.language))

    def audio_script(self, simplified: str) -> str:
        return self._gen(prompts.audio_script(self._ctx(simplified), self.level, self.language))

    def quiz(self, simplified: str) -> str:
        return self._gen(prompts.quiz(self._ctx(simplified), self.level, self.language))
