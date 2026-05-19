# 📄 GLM-OCR PDF → Markdown

Trasforma PDF sporchi, scansioni e immagini in Markdown pulito e strutturato, usando il modello **GLM-OCR** in esecuzione locale tramite **Ollama**. Nessun dato viene inviato al cloud.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Funzionalità

- Caricamento di file **PDF, PNG, JPG, WEBP, TIFF**
- Conversione pagina per pagina con **anteprima affiancata** (documento originale + Markdown)
- Riconoscimento di **testo, grassetto, corsivo, titoli, liste, tabelle e firme**
- **Elaborazione batch** dell'intero documento con download del file `.md` unificato
- **Avvio automatico di Ollama** all'apertura dell'app, senza dover aprire un terminale separato
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

## 🚀 Installazione

### 1. Clona il repository

```bash
git clone https://github.com/tuo-username/glm-ocr-pdf.git
cd glm-ocr-pdf
```

### 2. Crea e attiva un ambiente virtuale

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Installa le dipendenze Python

```bash
pip install -r requirements.txt
```

### 4. Installa Ollama e il modello GLM-OCR

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Poi scarica il modello (circa 2 GB)
ollama pull glm-ocr:latest
```

Su **Windows** scarica l'installer da [ollama.ai/download](https://ollama.ai/download).

### 5. Installa Poppler (solo Windows)

Scarica i binari precompilati da [github.com/oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) e posiziona la cartella `poppler/` nella root del progetto:

```
glm-ocr-pdf/
└── poppler/
    └── bin/
        ├── pdftoppm.exe
        └── ...
```

Su **Linux/macOS** Poppler viene trovato automaticamente nel PATH di sistema:

```bash
# Ubuntu / Debian
sudo apt install poppler-utils

# macOS
brew install poppler
```

---

## ▶️ Avvio

```bash
streamlit run app.py
```

Apri il browser su [http://localhost:8501](http://localhost:8501).

> **Ollama si avvia da solo.** All'apertura dell'app viene verificato automaticamente se Ollama è in esecuzione. Se non lo è, viene lanciato in background senza bisogno di aprire un terminale separato. Un toast verde conferma la connessione riuscita.
>
> Se Ollama non viene trovato nel PATH, l'app mostra un messaggio di errore con le istruzioni per installarlo.

---

## ⚙️ Configurazione

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

## 🗂️ Struttura del progetto

```
glm-ocr-pdf/
│
├── app.py                      # Entry point — layout, session state e avvio Ollama
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
│       ├── ollama.py           # Avvio automatico e health-check di Ollama
│       └── pdf.py              # Caricamento PDF e immagini → lista PIL.Image
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧠 Come funziona

```
Avvio app
     │
     ▼
utils/ollama.py       → health-check su /api/tags; se Ollama non risponde,
                         lancia `ollama serve` in background e attende fino a 15s
     │
     ▼
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
GLM-OCR su Ollama     → elabora l'immagine e restituisce il Markdown strutturato
     │
     ▼
ui/components.py      → visualizza anteprima renderizzata, sorgente e download
```

> **Perché chiamata diretta a `/api/generate`?**
> Il wrapper Python `GlmOcr` non include il campo `images` nel payload JSON quando usa il backend Ollama, causando risposte vuote (`## \n## \n## `). La chiamata diretta tramite `requests` garantisce il formato corretto richiesto dai modelli vision.

> **Perché `num_ctx=8192`?**
> A 150 DPI una pagina A4 genera circa 3000–4000 token visivi. Il context window di default di Ollama (4096) non è sufficiente: il runner tronca l'immagine e crasha con `GGML_ASSERT`. Impostare `num_ctx=8192` risolve il problema usando circa 512 MB di VRAM extra.

---

## 🐛 Troubleshooting

| Errore | Causa | Soluzione |
|---|---|---|
| `ollama` non trovato nel PATH | Ollama non installato o non nel PATH | Installa Ollama e riavvia il terminale |
| Ollama non risponde entro 15s | Avvio lento o conflitto di porta | Avvia manualmente `ollama serve` |
| `GGML_ASSERT` crash (HTTP 500) | Immagine troppo grande per il context window | Abbassare `IMAGE_MAX_WIDTH` o `PDF_DPI` in `settings.py` |
| Output vuoto `## ` | Immagine non inclusa nella richiesta | Verificare che si usi `run_ocr` da `core/ocr.py` |
| Errore Poppler su Windows | Binari non trovati | Posizionare `poppler/bin/` nella root del progetto |

---

## 📄 Licenza

MIT — libero per uso personale e commerciale.