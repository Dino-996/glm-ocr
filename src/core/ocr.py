"""
Logica OCR: ridimensionamento immagini e chiamata diretta all'API Ollama.
"""

import base64
import os
import tempfile

import requests
from PIL import Image

from src.config.settings import (
    IMAGE_MAX_WIDTH,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_PREDICT,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
    OCR_PROMPT,
)


def resize_for_ocr(image: Image.Image, max_width: int = IMAGE_MAX_WIDTH) -> Image.Image:
    """
    Ridimensiona l'immagine mantenendo l'aspect ratio se supera max_width.

    Ridurre la larghezza abbassa il numero di token visivi e previene il crash
    da prompt truncation del runner Ollama (ggml.c GGML_ASSERT fallito).

    Args:
        image: immagine PIL da ridimensionare.
        max_width: larghezza massima in pixel.

    Returns:
        Immagine ridimensionata, o l'originale se già entro i limiti.
    """
    w, h = image.size
    if w <= max_width:
        return image
    new_h = int(h * max_width / w)
    return image.resize((max_width, new_h), Image.LANCZOS)


def run_ocr(pil_image: Image.Image) -> str:
    """
    Converte un'immagine PIL in Markdown tramite GLM-OCR su Ollama.

    Chiama direttamente POST /api/generate con l'immagine in base64,
    bypassando il wrapper GlmOcr che non gestisce correttamente il campo
    ``images`` richiesto da Ollama per i modelli vision.

    Args:
        pil_image: pagina del documento come oggetto PIL.Image.

    Returns:
        Stringa Markdown estratta dall'immagine.

    Raises:
        requests.HTTPError: se Ollama risponde con un codice di errore HTTP.
        requests.ConnectionError: se Ollama non è raggiungibile.
        requests.Timeout: se Ollama non risponde entro OLLAMA_TIMEOUT secondi.
    """
    resized = resize_for_ocr(pil_image)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        resized.save(tmp.name, format="PNG")
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": OCR_PROMPT,
            "images": [img_b64],
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": OLLAMA_NUM_PREDICT,
                "num_ctx": OLLAMA_NUM_CTX,
            },
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()

        return response.json().get("response", "").strip()

    finally:
        os.unlink(tmp_path)