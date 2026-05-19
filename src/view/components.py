"""
Componenti UI Streamlit.
"""

import streamlit as st
from PIL import Image

from src.core.ocr import run_ocr
from src.config.settings import OLLAMA_MODEL

import requests


def render_document_column(image: Image.Image, page_number: int, total_pages: int) -> None:
    """Colonna sinistra: visualizza la pagina originale del documento."""
    st.markdown("### Documento originale")
    st.image(
        image,
        width="stretch",
        caption=f"Pagina {page_number} di {total_pages}",
    )


def render_ocr_column(page_number: int, current_page: Image.Image) -> None:
    """
    Colonna destra: bottone OCR, anteprima Markdown e download.
    """
    st.markdown("### Risultato Markdown")

    already_processed = page_number in st.session_state.ocr_results
    btn_label = (
        f"🔄 Rielabora pagina {page_number}"
        if already_processed
        else f"▶️ Esegui OCR su pagina {page_number}"
    )

    if st.button(btn_label, type="primary", width="stretch"):
        with st.spinner("Il modello sta analizzando la pagina…"):
            try:
                result = run_ocr(current_page)
                if result:
                    st.session_state.ocr_results[page_number] = result
                else:
                    st.warning(
                        "Il modello ha restituito una risposta vuota. "
                        "Verifica che l'immagine sia leggibile e riprova."
                    )
            except requests.ConnectionError:
                st.error(
                    f"Impossibile connettersi a Ollama. "
                    f"Assicurati che il servizio sia avviato (`ollama serve`) "
                    f"e che il modello `{OLLAMA_MODEL}` sia installato."
                )
            except requests.HTTPError as e:
                st.error(f"Ollama ha risposto con un errore HTTP: {e}")
            except requests.Timeout:
                st.error("Timeout: Ollama non ha risposto in tempo. Riprova o aumenta OLLAMA_TIMEOUT.")
            except Exception as e:
                st.error(f"Errore imprevisto: {e}")

    if page_number in st.session_state.ocr_results:
        markdown = st.session_state.ocr_results[page_number]
        tab_preview, tab_source = st.tabs(["Anteprima renderizzata", "Sorgente Markdown"])

        with tab_preview:
            st.markdown(markdown)

        with tab_source:
            st.code(markdown, language="markdown")

        st.download_button(
            label="Scarica Markdown",
            data=markdown,
            file_name=f"{st.session_state.file_name}_pagina_{page_number}.md",
            mime="text/markdown",
            width="stretch",
        )
    else:
        st.info("Clicca il pulsante sopra per avviare l'estrazione del testo.")


def render_batch_section(images: list[Image.Image]) -> None:
    """Sezione in fondo alla pagina: elaborazione batch e download documento completo."""
    st.divider()
    st.markdown("### Elaborazione batch")
    st.caption("Elabora tutte le pagine in sequenza e scarica un unico file Markdown.")

    col_btn, col_dl = st.columns(2, gap="medium")

    with col_btn:
        if st.button("Elabora tutte le pagine", width="stretch"):
            n = len(images)
            progress = st.progress(0, text="Avvio elaborazione batch…")
            for i, img in enumerate(images):
                page_num = i + 1
                progress.progress(i / n, text=f"Elaborazione pagina {page_num} di {n}…")
                try:
                    result = run_ocr(img)
                    if result:
                        st.session_state.ocr_results[page_num] = result
                except Exception as e:
                    st.warning(f"Pagina {page_num}: errore — {e}")
            progress.progress(1.0, text="Elaborazione completata!")
            st.rerun()

    with col_dl:
        processed = sorted(st.session_state.ocr_results.keys())
        if processed:
            combined = "\n\n---\n\n".join(
                f"<!-- Pagina {p} -->\n\n{st.session_state.ocr_results[p]}"
                for p in processed
            )
            st.download_button(
                label=f"Scarica documento completo ({len(processed)} pagine)",
                data=combined,
                file_name=f"{st.session_state.file_name}_completo.md",
                mime="text/markdown",
                width="stretch",
            )
        else:
            st.info("Nessuna pagina ancora elaborata.")