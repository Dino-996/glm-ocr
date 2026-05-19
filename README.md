#  GLM-OCR PDF => Markdown

Trasforma PDF sporchi, scansioni e immagini in Markdown pulito e strutturato, usando il modello **GLM-OCR** in esecuzione locale tramite **Ollama**. Nessun dato viene inviato al cloud.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Funzionalità

- Caricamento di file **PDF, PNG, JPG, WEBP, TIFF**
- Conversione pagina per pagina con **anteprima affiancata** (documento originale + Markdown)
- Riconoscimento di **testo, grassetto, corsivo, titoli, liste, tabelle e firme**
- **Elaborazione batch** dell'intero documento con download del file `.md` unificato
- **100% locale** — nessuna API esterna, nessun costo per token

---

## 🛠️ Requisiti

| Componente | Versione minima | Note |
|---|---|---|
| Python | 3.11 | |
| Ollama | 0.4+ | [ollama.ai](https://ollama.ai) |
| GLM-OCR | latest | `ollama pull glm-ocr:latest` |
| Poppler | qualsiasi | solo su Windows (vedi sotto) |
| GPU VRAM | 4 GB | 8 GB consigliati per `num_ctx=8192` |

---

## Installazione

### Clona il repository

```bash
git clone https://github.com/tuo-username/glm-ocr-pdf.git
cd glm-ocr-pdf
```

### Crea e attiva un ambiente virtuale

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### Installa le dipendenze Python

```bash
pip install -r requirements.txt
```

### Installa Ollama e il modello GLM-OCR

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Poi scarica il modello (circa 2 GB)
ollama pull glm-ocr:latest
```

Su **Windows** scarica l'installer da [ollama.ai/download](https://ollama.ai/download).

### Installa Poppler (solo Windows)

Scarica i binari precompilati da [github.com/oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) e posiziona la cartella `poppler/` nella root del progetto:

```
glm-ocr-pdf/
└── poppler/
    └── bin/
        ├── pdftoppm.exe
        └── ...
```

---

## Avvio

```bash
# Assicurati che Ollama sia in esecuzione
ollama serve

# In un altro terminale, avvia l'app
streamlit run app.py
```

Apri il browser su [http://localhost:8501](http://localhost:8501).

---

## Configurazione

Tutte le costanti sono centralizzate in `src/config/settings.py`:

| Costante | Default | Descrizione |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Endpoint Ollama |
| `OLLAMA_MODEL` | `glm-ocr:latest` | Modello da usare |
| `OLLAMA_NUM_CTX` | `8192` | Context window (token) |
| `OLLAMA_NUM_PREDICT` | `4096` | Token massimi di output |
| `OLLAMA_TIMEOUT` | `180` | Timeout HTTP in secondi |
| `IMAGE_MAX_WIDTH` | `1400` | Larghezza max immagine (px) |
| `PDF_DPI` | `150` | DPI conversione PDF |

---

## Struttura del progetto

```
glm-ocr-pdf/
│
├── app.py                      # Entry point — layout e session state
│
├── src/
│   ├── config/
│   │   └── settings.py         # Costanti e configurazione globale
│   │
│   ├── core/
│   │   └── ocr.py              # Logica OCR: resize immagine + chiamata Ollama
│   │
│   ├── ui/
│   │   └── components.py       # Componenti Streamlit (colonne, batch, download)
│   │
│   └── utils/
│       └── pdf.py              # Caricamento PDF e immagini → lista PIL.Image
│
├── requirements.txt
└── README.md
```

---

## Come funziona

```
File caricato
     │
     ▼
utils/pdf.py          → converte PDF in lista di PIL.Image (via pdf2image + Poppler)
     │
     ▼
core/ocr.py           → ridimensiona l'immagine (max 1400px) per rispettare il
                         context window di Ollama, la codifica in base64 e chiama
                         POST /api/generate con il campo `images`
     │
     ▼
GLM-OCR su Ollama     → elabora l'immagine e restituisce il Markdown
     │
     ▼
ui/components.py      → visualizza anteprima renderizzata, sorgente e download
```

> **Perché chiamata diretta a `/api/generate`?**  
> Il wrapper Python `GlmOcr` non include il campo `images` nel payload JSON quando usa il backend Ollama, causando risposte vuote. La chiamata diretta tramite `requests` garantisce il formato corretto.

---

## Troubleshooting

| Errore | Causa | Soluzione |
|---|---|---|
| `ConnectionError` | Ollama non è avviato | Eseguire `ollama serve` |
| `GGML_ASSERT` crash | Immagine troppo grande (> 4096 token) | Abbassare `IMAGE_MAX_WIDTH` o `PDF_DPI` |
| Output vuoto `## ` | Immagine non passata correttamente | Verificare che si usi `run_ocr` da `core/ocr.py` |
| Errore Poppler (Windows) | Binari non trovati | Posizionare `poppler/bin/` nella root del progetto |

---

## Licenza

MIT — libero per uso personale e commerciale