"""
Costanti e impostazioni globali per l'applicazione.
"""

# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------
 
OLLAMA_URL: str = "http://localhost:11434/api/generate"
OLLAMA_MODEL: str = "glm-ocr:latest"
 
# Token di contesto allocati per ogni richiesta.
# Con immagini a 1400px servono ~3000-4000 token; 8192 dà margine sufficiente.
# Richiede ~512 MB di VRAM extra rispetto al default da 4096.
OLLAMA_NUM_CTX: int = 8192
 
# Token massimi di output per pagina.
OLLAMA_NUM_PREDICT: int = 4096
 
# Timeout in secondi per la chiamata HTTP a Ollama.
OLLAMA_TIMEOUT: int = 180
 
# ---------------------------------------------------------------------------
# Elaborazione immagini
# ---------------------------------------------------------------------------
 
# Larghezza massima (px) dell'immagine inviata al modello.
# Valori > 1700px a 200 DPI producono > 5000 token, causando il crash
# GGML_ASSERT nel runner Ollama per overflow del context window.
IMAGE_MAX_WIDTH: int = 1400
 
# DPI usati nella conversione PDF => immagine.
# 150 DPI è sufficiente per testo stampato; aumentare a 200 per scansioni a bassa qualità.
PDF_DPI: int = 150
 
# ---------------------------------------------------------------------------
# Prompt OCR
# ---------------------------------------------------------------------------
 
OCR_PROMPT: str = (
    "You are a precise OCR engine. Analyze the document image and convert it to clean, "
    "well-structured Markdown following these formatting rules exactly:\n\n"
 
    "HEADINGS: Convert any centered, large, bold, underlined, or visually prominent title "
    "to a Markdown heading. Use # for the main document title, ## for section titles, "
    "### for subsection titles.\n\n"
 
    "BOLD: Any text that is visually bold, or ALL-CAPS keywords acting as labels or section "
    "markers (e.g. 'Visto', 'Considerato', 'PRESO ATTO', 'RITIENE', 'RACCOMANDA') "
    "must be wrapped in **double asterisks**.\n\n"
 
    "ITALIC: Any text that is visually slanted or rendered in a cursive/oblique style "
    "must be wrapped in *single asterisks*. This includes quoted passages, Latin phrases, "
    "titles of publications, and any text that appears visually different from the "
    "surrounding upright body text due to its slant.\n\n"
 
    "UNDERLINE: Markdown has no underline syntax. Render any underlined text as **bold** instead.\n\n"
 
    "LISTS: Convert bullet points or numbered items to Markdown lists (- item or 1. item).\n\n"
 
    "TABLES: Reproduce any table using Markdown table syntax "
    "(| col | col | with a --- separator row).\n\n"
 
    "SIGNATURES/FOOTER: Preserve signature blocks as plain text, each label on its own line.\n\n"
 
    "PAGE NUMBERS: Ignore any standalone page number.\n\n"
 
    "Output ONLY the Markdown. No preamble, no explanation, no code fences."
)