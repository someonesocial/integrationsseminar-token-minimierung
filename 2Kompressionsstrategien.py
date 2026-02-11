# -*- coding: utf-8 -*-
"""
Kompressionsstrategien für Token-Minimierung von LLM-Prompts.
Angelehnt an: LLMLingua (Jiang et al. 2023/2024), Selective Context (Li et al. 2023),
Lost in the Middle (Liu et al. 2023). Alle Strategien sind allgemein anwendbar (keine
prompt-spezifischen Fallunterscheidungen) und in echten Systemen nutzbar.
"""
import re
import tiktoken
from typing import List, Callable, Optional

# Encoder für GPT-4/GPT-3.5 (Token-Zählung)
encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

# --- Hilfsfunktionen (für alle Strategien) ---

def _saetze_zerlegen(text: str) -> List[str]:
    """Zerlegt Text in Sätze (Punkt, Ausrufe-, Fragezeichen, Zeilenumbruch)."""
    text = re.sub(r'\s+', ' ', text.strip())
    # Abkürzungen nicht trennen (z.B. "Nr.", "z.B.")
    for abbr in ['Nr.', 'z.B.', 'bzw.', 'u.a.', 'etc.', 'evtl.']:
        text = text.replace(abbr, abbr.replace('.', '<PUNKT>'))
    saetze = re.split(r'[.!?]\s+|\n+', text)
    saetze = [s.replace('<PUNKT>', '.').strip() for s in saetze if s.strip()]
    return saetze if saetze else [text]


# Stoppwörter / Floskeln (regelbasiert entfernbar)
FLOSKEL_ANFANG = re.compile(
    r'^(Sehr\s+geehrte\s+Damen\s+und\s+Herren,?|Dear\s+(Sir|Madam),?|Hi\s+,?|Hallo\s*,?|Guten\s+Tag\s*,?)\s*',
    re.IGNORECASE
)
FLOSKEL_ENDE = re.compile(
    r'\s*(Mit\s+freundlichen\s+Grüßen|Best\s+regards|Kind\s+regards|Viele\s+Grüße|Sincerely,?)\s*[.\s]*$',
    re.IGNORECASE
)
REDUNDANTE_LEERZEICHEN = re.compile(r'[ \t]+')

# Optionale Stoppwörter (häufige Füllwörter, die semantisch wenig tragen)
STOPWORDS_DE_EN = {
    'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines',
    'und', 'oder', 'aber', 'dass', 'daß', 'ist', 'sind', 'war', 'waren', 'wird', 'werden',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'für', 'von', 'zu', 'mit', 'bei', 'nach', 'aus', 'auf', 'über', 'unter',
    'for', 'of', 'to', 'with', 'by', 'from', 'on', 'at', 'in', 'as',
    'ich', 'wir', 'sie', 'es', 'er', 'sie', 'Sie', 'man',
    'haben', 'hat', 'hatte', 'haben', 'has', 'have', 'had',
    'können', 'müssen', 'sollen', 'will', 'wollen', 'may', 'must', 'should', 'would',
}


def _token_count(text: str) -> int:
    return len(encoder.encode(text))


# =============================================================================
# Strategie 1: Regelbasierte Kompression (ohne ML)
# =============================================================================
# Begründung: In Produktionssystemen oft erste Wahl – keine Laufzeit-Abhängigkeit
# von Modellen, deterministisch, gut erklärbar. Entfernt Floskeln, Redundanzen
# und optional Füllwörter (vgl. klassische Text-Normalisierung / Preprocessing).
# =============================================================================

def kompression_manuell(prompt: str, stopwords_entfernen: bool = True) -> str:
    """
    Allgemeine regelbasierte Kompression:
    - Entfernen von Anrede und Grußformel (regex-basiert)
    - Mehrfache Leerzeichen/Zeilen auf ein Zeichen reduzieren
    - Optional: Füllwörter entfernen (Stoppwortliste)
    - Keine prompt-spezifischen Regeln – funktioniert für beliebige Texte.
    """
    if not prompt or not prompt.strip():
        return prompt
    text = prompt.strip()
    text = FLOSKEL_ANFANG.sub('', text)
    text = FLOSKEL_ENDE.sub('', text)
    text = REDUNDANTE_LEERZEICHEN.sub(' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    if not stopwords_entfernen:
        return text

    # Optional: Stoppwörter nur in längeren Wörtern belassen (Wortgrenzen)
    woerter = text.split()
    gefiltert = []
    for w in woerter:
        w_norm = w.lower().strip('.,;:!?()"\'-')
        if w_norm and w_norm not in STOPWORDS_DE_EN:
            gefiltert.append(w)
        elif w_norm in STOPWORDS_DE_EN and len(woerter) > 30:
            continue  # Nur in langen Texten Stoppwörter weglassen
        else:
            gefiltert.append(w)
    return ' '.join(gefiltert)


# =============================================================================
# Strategie 2: Strukturierte Kompression (LLMLingua-/LongLLMLingua-inspiriert)
# =============================================================================
# Idee: Nur „wichtige“ Teile behalten. LLMLingua nutzt ein kleines Modell zur
# Token-Importanz; wir approximieren das durch Satz-Embeddings und Centrality:
# Sätze, die dem Dokument-Durchschnitt (oder dem ersten Satz) semantisch am
# nächsten sind, gelten als zentral und werden behalten (vgl. Extractive
# Summarization). So bleibt die Bedeutung erhalten, ohne task-spezifisches Training.
# =============================================================================

_embedding_model = None

def _get_embedding_model():
    """Lazy-Load des Satz-Embedding-Modells (nur bei Bedarf)."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(
                'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
            )
        except Exception as e:
            raise RuntimeError(
                "Für 'Strukturierte Kompression' wird sentence-transformers benötigt. "
                "Installation: pip install sentence-transformers"
            ) from e
    return _embedding_model


def kompression_strukturiert(
    prompt: str,
    ziel_anteil: float = 0.45,
    min_saetze: int = 2,
) -> str:
    """
    Strukturierte Kompression durch semantische Centrality:
    - Text in Sätze zerlegen, jeden Satz embedden
    - Wichtigkeit = Ähnlichkeit zum mittleren Dokument-Vektor (Centrality)
    - Behalte die wichtigsten Sätze bis ca. ziel_anteil der Original-Token-Anzahl
    """
    saetze = _saetze_zerlegen(prompt)
    if len(saetze) <= min_saetze:
        return prompt

    model = _get_embedding_model()
    embeddings = model.encode(saetze)
    import numpy as np
    zentrum = np.mean(embeddings, axis=0)
    scores = np.array([np.dot(e, zentrum) / (np.linalg.norm(e) * np.linalg.norm(zentrum) + 1e-9)
                      for e in embeddings])
    # Nach Wichtigkeit sortieren (höchster Score zuerst)
    reihenfolge = np.argsort(-scores)
    ziel_tokens = max(50, int(_token_count(prompt) * ziel_anteil))
    gewaehlt = []
    akt_tokens = 0
    for idx in reihenfolge:
        s = saetze[idx]
        neue_tokens = akt_tokens + _token_count(s) + 1
        if neue_tokens <= ziel_tokens or len(gewaehlt) < min_saetze:
            gewaehlt.append((idx, s))
            akt_tokens = neue_tokens
        else:
            break
    gewaehlt.sort(key=lambda x: x[0])
    return ' '.join(s for _, s in gewaehlt)


# =============================================================================
# Strategie 3: Token-Budget (Selective Context / Lost in the Middle)
# =============================================================================
# Selective Context wählt Kontext nach Relevanz; „Lost in the Middle“ zeigt,
# dass mittlere Passagen von LLMs schlechter genutzt werden. Daher: festes
# Token-Budget, Sätze nach Position gewichten (Anfang + Ende bevorzugt) und
# optional nach Centrality, dann greedy auffüllen bis Budget voll.
# =============================================================================

def kompression_token_budget(
    prompt: str,
    ziel_tokens: int = 100,
    position_weight: bool = True,
) -> str:
    """
    Kompression mit festem Token-Budget:
    - Sätze werden nach Position bewertet (Anfang und Ende höher, „Lost in the Middle“)
    - Greedy-Auswahl: höchste Bewertung zuerst, bis ziel_tokens erreicht
    """
    saetze = _saetze_zerlegen(prompt)
    if not saetze:
        return prompt[: encoder.decode(encoder.encode(prompt)[:ziel_tokens]).rfind(' ') or ziel_tokens]
    n = len(saetze)
    if n == 1:
        tokens = encoder.encode(prompt)
        if len(tokens) <= ziel_tokens:
            return prompt
        return encoder.decode(tokens[:ziel_tokens])

    # Positionsgewicht: U-förmig (Anfang und Ende wichtiger)
    scores = []
    for i, s in enumerate(saetze):
        pos = (i + 1) / n
        if position_weight:
            # Höhere Werte an den Rändern
            score = 2 * max(pos, 1 - pos)
        else:
            score = 1.0
        scores.append((score, _token_count(s), s, i))
    # Nach Score absteigend, dann greedy Token-Budget füllen
    scores.sort(key=lambda x: -x[0])
    gewaehlt = []
    tokens_aktuell = 0
    for score, t_len, s, orig_idx in scores:
        if tokens_aktuell + t_len <= ziel_tokens or not gewaehlt:
            gewaehlt.append((orig_idx, s))
            tokens_aktuell += t_len + 1
    gewaehlt.sort(key=lambda x: x[0])
    return ' '.join(s for _, s in gewaehlt)


# =============================================================================
# Strategie 4: Chunking mit Überlappung (LongLLMLingua / lange Kontexte)
# =============================================================================
# Lange Dokumente werden in Chunks mit Überlappung geteilt; pro Chunk wird
# eine kurze Repräsentation erzeugt (Anfang + Ende des Chunks oder zentrale
# Sätze), um Kontextverlust in der Mitte zu mindern. Die Repräsentationen
# werden konkateniert – so bleibt eine dokumentweite Übersicht erhalten.
# =============================================================================

def kompression_chunking(
    prompt: str,
    chunk_groesse: int = 100,
    overlap: int = 20,
    saetze_pro_chunk: int = 3,
) -> str:
    """
    Chunking mit Überlappung:
    - Prompt in Token-Chunks (chunk_groesse) mit Überlappung (overlap) zerlegen
    - Pro Chunk: erste und letzte Sätze bzw. bis zu saetze_pro_chunk Sätze behalten
    - Alle Chunk-Repräsentationen aneinanderhängen (kein Verlust „welcher Teil wo stand“)
    """
    tokens = encoder.encode(prompt)
    if len(tokens) <= chunk_groesse:
        return prompt

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_groesse, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = encoder.decode(chunk_tokens)
        saetze = _saetze_zerlegen(chunk_text)
        if len(saetze) <= saetze_pro_chunk:
            rep = chunk_text
        else:
            rep = ' '.join(saetze[:1] + saetze[-saetze_pro_chunk+1:] if saetze_pro_chunk > 1 else saetze[:1])
        chunks.append(rep)
        start += chunk_groesse - overlap
        if end == len(tokens):
            break
    return '\n\n'.join(f"[Abschnitt {i+1}/{len(chunks)}] {c}" for i, c in enumerate(chunks))


# --- Ausgabe zur Kontrolle ---
print("Kompressionsstrategien implementiert:")
print("  1. Regelbasierte Kompression (Floskeln, Redundanzen, optional Stoppwörter)")
print("  2. Strukturierte Kompression (LLMLingua-inspiriert: Embedding-Centrality)")
print("  3. Token-Budget (Selective Context / Lost in the Middle: positionsbasiert)")
print("  4. Chunking mit Überlappung (LongLLMLingua-inspiriert: Chunk-Repräsentationen)")
