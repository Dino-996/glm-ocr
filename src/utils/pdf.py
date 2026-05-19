"""
Utilità per il caricamento di file PDF e immagini.
Restituisce sempre una lista di oggetti PIL.Image, indipendentemente dal formato del file in ingresso.
"""

import os
import sys

from pdf2image import convert_from_bytes
from PIL import Image

from src.config.settings import PDF_DPI

# Su Windows Poppler non è nel PATH di sistema: cerca la cartella locale.
# Su Linux/macOS Poppler è gestito globalmente e non serve il path esplicito.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POPPLER_BIN_PATH: str | None = (
    os.path.join(_BASE_DIR, "poppler", "bin") if sys.platform == "win32" else None
)


def load_file(file_bytes: bytes, filename: str) -> list[Image.Image]:
    """
    Carica un file PDF o immagine e lo converte in una lista di pagine PIL.

    Args:
        file_bytes: contenuto grezzo del file caricato.
        filename: nome originale del file, usato per rilevare l'estensione.

    Returns:
        Lista di oggetti PIL.Image, una per pagina (o una sola per le immagini).

    Raises:
        ValueError: se l'estensione del file non è supportata.
        Exception: se Poppler non è installato o non trovato (per i PDF).
    """
    ext = os.path.splitext(filename.lower())[1]

    if ext == ".pdf":
        return convert_from_bytes(
            file_bytes,
            poppler_path=POPPLER_BIN_PATH,
            dpi=PDF_DPI,
        )

    if ext in {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}:
        import io
        return [Image.open(io.BytesIO(file_bytes))]

    raise ValueError(f"Formato file non supportato: '{ext}'")