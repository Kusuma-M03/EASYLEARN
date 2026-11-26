"""EasyLearn - GenAI accessibility assistant for students with learning difficulties."""
import streamlit as st

from core import prompts
from core.llm import LLMError, available_providers
from core.pdf_utils import extract_text
from core.readability import compare
from core.simplify import Pipeline
from core.tts import LANG_CODES, speak

st.set_page_config(page_title="EasyLearn", page_icon="📖", layout="wide")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("📖 EasyLearn")
    st.caption("Study material made easier to read, hear and understand.")

    st.subheader("1. AI provider")
    groq_key = st.text_input("Groq API key", type="password", help="Free at console.groq.com")
    gem_key = st.text_input("Gemini API key", type="password", help="Free at aistudio.google.com")
    providers = available_providers(groq_key, gem_key)
    provider = st.selectbox("Use", list(providers)) if providers else None
    if not providers:
        st.warning("Add a Groq or Gemini key (or set it in .env).")

    st.subheader("2. Learner settings")
    profile = st.selectbox("Learner profile", list(prompts.PROFILES))
    level = st.selectbox("Reading level", list(prompts.LEVELS), index=1)
    language = st.selectbox("Output language", list(LANG_CODES))

    st.subheader("3. Display")
    dyslexia = st.toggle("Dyslexia-friendly font", value=False)
    contrast = st.toggle("High contrast", value=False)
    font_size = st.slider("Text size", 16, 30, 20)
    spacing = st.slider("Line spacing", 1.4, 2.4, 1.8, 0.1)

# ---------------------------------------------------------------- styling
css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600&display=swap');
.easy-text, .easy-text p, .easy-text li, .easy-text td, .easy-text th {{
    font-size: {font_size}px !important; line-height: {spacing} !important;
    {"font-family: 'Lexend', 'Comic Sans MS', sans-serif !important; letter-spacing: 0.04em; word-spacing: 0.12em;" if dyslexia else ""}
}}
"""
if contrast:
    css += """
    .easy-text { background:#000; color:#ffeb3b; padding:1rem 1.4rem; border-radius:8px; }
    .easy-text * { color:#ffeb3b !important; }
    """
css += "</style>"
st.markdown(css, unsafe_allow_html=True)


def show(md: str):
    """Render markdown inside the accessibility-styled container."""
    with st.container():
        st.markdown('<div class="easy-text">', unsafe_allow_html=True)
        st.markdown(md)
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------- input
st.header("Make any study material easier")
tab_up, tab_paste = st.tabs(["Upload file", "Paste text"])
source = ""
with tab_up:
    f = st.file_uploader("PDF or TXT", type=["pdf", "txt"])
    if f:
        try:
            source = extract_text(f.getvalue(), f.name)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
        if f and not source:
            st.error("No text found. Scanned PDFs need OCR (not supported yet).")
with tab_paste:
    pasted = st.text_area("Paste your notes", height=200)
    if pasted.strip():
        source = pasted.strip()

if source:
    words = len(source.split())
    st.caption(f"Loaded **{words}** words.")
    if words > 6000:
        st.info("Large document: only the first 6000 words will be processed to stay within free-tier limits.")
        source = " ".join(source.split()[:6000])
    with st.expander("Preview original text"):
        st.write(source[:3000] + ("..." if len(source) > 3000 else ""))

go = st.button("✨ Simplify", type="primary", disabled=not (source and provider))

# ---------------------------------------------------------------- processing
if go:
    pipe = Pipeline(provider, providers[provider], level, profile, language)
    st.session_state["pipe_cfg"] = (provider, providers[provider], level, profile, language)
    st.session_state["original"] = source
    st.session_state["lang"] = language
    st.session_state.pop("extras", None)
    bar = st.progress(0.0, text="Simplifying...")
    try:
        st.session_state["simplified"] = pipe.simplify(source, progress=lambda p: bar.progress(p, text="Simplifying..."))
    except LLMError as e:
        st.error(str(e))
        st.stop()
    bar.empty()

# ---------------------------------------------------------------- results
if "simplified" in st.session_state:
    simplified = st.session_state["simplified"]
    pipe = Pipeline(*st.session_state["pipe_cfg"])
    extras = st.session_state.setdefault("extras", {})

    def lazy(name: str, label: str, fn):
        """Generate an extra output on demand and cache it."""
        if name not in extras:
            if st.button(label, key=f"btn_{name}"):
                with st.spinner("Generating..."):
                    try:
                        extras[name] = fn()
                        st.rerun()
                    except LLMError as e:
                        st.error(str(e))
        return extras.get(name)

    t1, t2, t3, t4, t5, t6, t7 = st.tabs(
        ["📄 Simplified", "🔑 Key points", "📚 Glossary", "🪜 Steps", "🔊 Audio", "❓ Self-check", "📊 Readability"]
    )

    with t1:
        show(simplified)
        st.download_button("⬇ Download (.md)", simplified, "easylearn_simplified.md")
        st.warning("AI can make mistakes or lose nuance. Always verify important facts against the original.")

    with t2:
        out = lazy("kp", "Generate key points", lambda: pipe.key_points(simplified))
        if out:
            show(out)
    with t3:
        out = lazy("gl", "Generate glossary", lambda: pipe.glossary(simplified))
        if out:
            show(out)
    with t4:
        out = lazy("st", "Generate step-by-step", lambda: pipe.steps(simplified))
        if out:
            show(out)
    with t5:
        script = lazy("au", "Generate audio summary", lambda: pipe.audio_script(simplified))
        if script:
            show(script)
            slow = st.checkbox("Slow speech")
            if st.button("🔊 Create audio"):
                with st.spinner("Creating audio..."):
                    try:
                        st.session_state["audio"] = speak(script, st.session_state["lang"], slow)
                    except Exception as e:
                        st.error(f"Text-to-speech failed (needs internet): {e}")
            if "audio" in st.session_state:
                st.audio(st.session_state["audio"], format="audio/mp3")
                st.download_button("⬇ Download MP3", st.session_state["audio"], "easylearn_summary.mp3")
    with t6:
        out = lazy("qz", "Generate self-check questions", lambda: pipe.quiz(simplified))
        if out:
            show(out)
    with t7:
        if st.session_state["lang"] != "English":
            st.info("Readability formulas only work for English output. Choose English to see the comparison.")
        else:
            rows = compare(st.session_state["original"], simplified)
            st.table(rows)
            fre = rows[2]
            gain = fre["Simplified"] - fre["Original"]
            st.metric("Reading-ease improvement", f"{gain:+.1f} points")

st.divider()
st.caption("EasyLearn is a study aid, not a replacement for teachers or the original material. "
           "Your text is sent to the selected AI provider for processing; do not upload confidential documents.")
