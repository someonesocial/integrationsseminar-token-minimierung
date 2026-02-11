# -*- coding: utf-8 -*-
"""
Experiment-Durchführung mit maschineller Qualitätsbewertung.
Qualität = semantische Ähnlichkeit zwischen Original- und Kompressions-Prompt
(Cosine Similarity der Embeddings). Keine Schätzung mehr – wissenschaftlich
reproduzierbare Metrik (vgl. BERTScore, Semantic Similarity in Summarization).

Hinweis: Dieses Skript setzt voraus, dass zuerst 1token_berechnung_anfragen.py
und 2Kompressionsstrategien.py ausgeführt wurden (encoder, TEST_PROMPTS,
ExperimentResult, Kompressionsfunktionen im Namensraum).
"""
import time
import numpy as np

# Embedding-Modell für Qualitätsmessung (einmal laden)
_qualitaets_model = None

def _get_qualitaets_model():
    global _qualitaets_model
    if _qualitaets_model is None:
        from sentence_transformers import SentenceTransformer
        _qualitaets_model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
    return _qualitaets_model


def qualitaet_semantische_aehnlichkeit(original: str, komprimiert: str) -> float:
    """
    Maschinelle Qualitätsbewertung: Cosine Similarity der Satz-Embeddings.
    Wert in [0, 1]; höher = mehr semantische Information des Originals
    im komprimierten Text erhalten (wissenschaftlich etablierte Metrik).
    """
    if not original.strip() or not komprimiert.strip():
        return 0.0
    model = _get_qualitaets_model()
    emb_orig = model.encode(original.strip(), normalize_embeddings=True)
    emb_comp = model.encode(komprimiert.strip(), normalize_embeddings=True)
    if emb_orig.ndim == 1:
        emb_orig = emb_orig.reshape(1, -1)
    if emb_comp.ndim == 1:
        emb_comp = emb_comp.reshape(1, -1)
    # Bei mehreren Sätzen: Durchschnittsvektor dann Cosine Sim
    v_orig = np.mean(emb_orig, axis=0)
    v_comp = np.mean(emb_comp, axis=0)
    v_orig = v_orig / (np.linalg.norm(v_orig) + 1e-9)
    v_comp = v_comp / (np.linalg.norm(v_comp) + 1e-9)
    cos = float(np.dot(v_orig, v_comp))
    # Rohes Cosine-Similarity [0,1] – wissenschaftlich transparenter,
    # da Textembeddings gleicher Domäne stets positiv korrelieren.
    # Werte: 1.0 = identisch, 0.0 = keinerlei semantische Überlappung
    return max(0.0, min(1.0, cos))


def run_experiment(
    prompt_name: str,
    prompt_text: str,
    strategie_func,
    strategie_name: str,
    qualitaets_fn=None,
) -> ExperimentResult:
    """
    Führt ein einzelnes Experiment durch und misst alle relevanten Metriken.
    Qualität wird maschinell über semantische Ähnlichkeit (Embedding) ermittelt,
    sofern qualitaets_fn übergeben wird; sonst 1.0 (nur bei Baseline sinnvoll).
    """
    original_tokens = len(encoder.encode(prompt_text))

    start_time = time.perf_counter()
    komprimierter_prompt = strategie_func(prompt_text)
    kompressions_zeit = (time.perf_counter() - start_time) * 1000  # ms

    komprimierte_tokens = len(encoder.encode(komprimierter_prompt))
    kompressionsrate = original_tokens / max(komprimierte_tokens, 1)

    # Latenz: gemessene Kompressionszeit + modellierte LLM-Latenz (OpenAI-typisch)
    # Quelle: typische Werte ~2 ms/Input-Token + Basislatenz (z. B. 50 ms)
    llm_latenz = 50 + (komprimierte_tokens * 2)
    gesamt_latenz = kompressions_zeit + llm_latenz

    # Kosten: OpenAI GPT-3.5 Turbo (Stand 2024), ~0,0015 USD/1K Input → ~0,00138 €/1K
    kosten = (komprimierte_tokens / 1000) * 0.00138

    # Qualität: maschinell über Embedding-Similarität (keine Schätzung)
    if qualitaets_fn is not None:
        qualitaet = qualitaets_fn(prompt_text, komprimierter_prompt)
    else:
        qualitaet = 1.0

    return ExperimentResult(
        strategie=strategie_name,
        original_tokens=original_tokens,
        komprimierte_tokens=komprimierte_tokens,
        latenz_ms=gesamt_latenz,
        qualitaets_score=qualitaet,
        kosten_euro=kosten,
        kompressionsrate=kompressionsrate
    )


# Alle Experimente durchführen
alle_ergebnisse = []

strategien = [
    (lambda p: p, "Baseline (keine Kompression)"),
    (kompression_manuell, "Manuelle Prompt-Kompression"),
    (kompression_strukturiert, "Strukturierte Kompression"),
    (lambda p: kompression_token_budget(p, 100), "Token-Budget (100 Tokens)"),
    (lambda p: kompression_chunking(p, 100, 20), "Chunking (100 Tokens)")
]

# Einmal Modell laden (damit erste Messung nicht die Laufzeit verfälscht)
print("Lade Embedding-Modell für Qualitätsbewertung …")
_get_qualitaets_model()
print("Modell geladen.")

print("=" * 80)
print("EXPERIMENT-ERGEBNISSE: Token-Minimierungsstrategien (maschinelle Qualität)")
print("=" * 80)

for prompt_name, prompt_text in TEST_PROMPTS.items():
    print(f"\n📋 Test-Szenario: {prompt_name.upper()}")
    print("-" * 60)

    for strategie_func, strategie_name in strategien:
        # Bei Baseline keine Qualitätsberechnung nötig (Original = Komprimiert)
        q_fn = None if strategie_name == "Baseline (keine Kompression)" else qualitaet_semantische_aehnlichkeit
        result = run_experiment(
            prompt_name, prompt_text, strategie_func, strategie_name, qualitaets_fn=q_fn
        )
        alle_ergebnisse.append(result)

        print(f"\n  {strategie_name}:")
        print(f"    Original: {result.original_tokens} Tokens → Komprimiert: {result.komprimierte_tokens} Tokens")
        print(f"    Kompressionsrate: {result.kompressionsrate:.2f}x")
        print(f"    Latenz: {result.latenz_ms:.1f} ms")
        print(f"    Kosten: {result.kosten_euro:.6f} €")
        print(f"    Qualität (semant. Ähnlichkeit): {result.qualitaets_score*100:.1f}%")

print("\n" + "=" * 80)
