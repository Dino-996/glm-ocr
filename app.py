"""
Entry point dell'applicazione.
Gestisce esclusivamente il layout di pagina, il session state e il flusso principale.
"""

import streamlit as st

from src.view.components import render_batch_section, render_document_column, render_ocr_column
from src.utils.ollama import ensure_ollama
from src.utils.pdf import load_file

# ---------------------------------------------------------------------------
# Configurazione pagina
# ---------------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="Dirty PDF → Clean Markdown",
    page_icon="📄",
)

st.title("PDF → Clean Markdown")
st.subheader("Trasforma scansioni e PDF sporchi in Markdown strutturato — powered by GLM-OCR + Ollama")

# ---------------------------------------------------------------------------
# Avvio automatico Ollama (eseguito una sola volta per sessione)
# ---------------------------------------------------------------------------

if "ollama_ready" not in st.session_state:
    with st.spinner("Verifica connessione a Ollama…"):
        ok, msg = ensure_ollama()
    st.session_state.ollama_ready = ok
    if ok:
        st.toast(f"{msg}", icon="🟢")
    else:
        st.error(f"{msg}")

if not st.session_state.ollama_ready:
    st.stop()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "ocr_results" not in st.session_state:
    st.session_state.ocr_results: dict[int, str] = {}

if "images" not in st.session_state:
    st.session_state.images = []

if "file_name" not in st.session_state:
    st.session_state.file_name: str = ""

# ---------------------------------------------------------------------------
# Caricamento file
# ---------------------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Carica un file PDF o un'immagine del documento",
    type=["pdf", "png", "jpg", "jpeg", "webp", "tiff"],
)

if uploaded_file is not None:
    if uploaded_file.name != st.session_state.file_name:
        st.session_state.ocr_results = {}
        st.session_state.file_name = uploaded_file.name

        with st.spinner("Caricamento documento in corso..."):
            try:
                st.session_state.images = load_file(uploaded_file.read(), uploaded_file.name)
            except Exception as e:
                st.error(f"Errore nel caricamento del file: {e}")
                st.info(
                    "Su Windows assicurati che la cartella `poppler/bin` "
                    "sia presente nella directory del progetto."
                )
                st.stop()

    n_pages = len(st.session_state.images)
    st.success(
        f"**{uploaded_file.name}** caricato — "
        f"{n_pages} pagina{'e' if n_pages > 1 else ''} trovata{'e' if n_pages > 1 else ''}"
    )

# ---------------------------------------------------------------------------
# Layout principale
# ---------------------------------------------------------------------------

if st.session_state.images:
    images = st.session_state.images
    n_pages = len(images)

    page_number: int = st.number_input(
        "Pagina da visualizzare / elaborare",
        min_value=1,
        max_value=n_pages,
        value=1,
        step=1,
    )
    current_page = images[page_number - 1]

    st.divider()

    col_doc, col_ocr = st.columns(2, gap="large")

    with col_doc:
        render_document_column(current_page, page_number, n_pages)

    with col_ocr:
        render_ocr_column(page_number, current_page)

    render_batch_section(images)