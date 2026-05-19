"""
Gestione del processo Ollama.
Verifica se Ollama è già in esecuzione e, in caso contrario, lo avvia
come sottoprocesso in background prima che l'app inizi a fare richieste.
"""

import subprocess
import sys
import time

import requests

from src.config.settings import OLLAMA_URL

# URL usato solo per l'health-check (non invia dati al modello)
_HEALTH_URL = OLLAMA_URL.replace("/api/generate", "/api/tags")

# Secondi di attesa massimi per la messa in ascolto di Ollama dopo l'avvio
_STARTUP_TIMEOUT = 15

# Intervallo tra un tentativo di health-check e il successivo
_POLL_INTERVAL = 0.5


def _is_running() -> bool:
    """Restituisce True se Ollama risponde all'health-check."""
    try:
        r = requests.get(_HEALTH_URL, timeout=2)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def ensure_ollama() -> tuple[bool, str]:
    """
    Garantisce che Ollama sia in esecuzione.

    Se il servizio è già attivo non fa nulla.
    Se non lo è, tenta di avviarlo con ``ollama serve`` in background.

    Returns:
        Tupla (successo: bool, messaggio: str) da mostrare nell'UI.
    """
    if _is_running():
        return True, "Ollama già in esecuzione."

    try:
        # Avvia `ollama serve` come processo figlio, scollegato dal terminale
        kwargs: dict = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }

        if sys.platform == "win32":
            # Su Windows usa DETACHED_PROCESS per non aprire una finestra
            kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            # Su Unix avvia in un nuovo gruppo di processi
            kwargs["start_new_session"] = True

        subprocess.Popen(["ollama", "serve"], **kwargs)

    except FileNotFoundError:
        return False, (
            "Eseguibile `ollama` non trovato. "
            "Assicurati che Ollama sia installato e presente nel PATH di sistema."
        )

    # Attendi che Ollama sia pronto a rispondere
    elapsed = 0.0
    while elapsed < _STARTUP_TIMEOUT:
        time.sleep(_POLL_INTERVAL)
        elapsed += _POLL_INTERVAL
        if _is_running():
            return True, f"Ollama avviato correttamente ({elapsed:.1f}s)."

    return False, (
        f"Ollama non ha risposto entro {_STARTUP_TIMEOUT}s dall'avvio. "
        "Prova ad avviarlo manualmente con `ollama serve`."
    )