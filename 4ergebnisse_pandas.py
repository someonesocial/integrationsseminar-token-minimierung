# -*- coding: utf-8 -*-
"""
Erzeugt pandas DataFrame und aggregierte Statistiken aus alle_ergebnisse.
Voraussetzung: 1, 2 und 3 wurden ausgeführt (alle_ergebnisse, encoder, TEST_PROMPTS).
Die Aufbereitungsform (Spalten, Struktur) bleibt für 5visualisierung.py und
6ergebnisse_detail.py unverändert.
"""
import pandas as pd

# Szenario-Namen aus original_tokens zuordnen (wie in 6)
def _szenario_fuer_tokens(original_tokens):
    for name, text in TEST_PROMPTS.items():
        if len(encoder.encode(text)) == original_tokens:
            return name
    return 'unbekannt'

data = []
for r in alle_ergebnisse:
    data.append({
        'Strategie': r.strategie,
        'Szenario': _szenario_fuer_tokens(r.original_tokens),
        'Original Tokens': r.original_tokens,
        'Komprimierte Tokens': r.komprimierte_tokens,
        'Kompressionsrate': r.kompressionsrate,
        'Latenz (ms)': r.latenz_ms,
        'Kosten (€)': r.kosten_euro,
        'Qualität (%)': r.qualitaets_score * 100
    })

df = pd.DataFrame(data)
agg_stats = df.groupby('Strategie').agg({
    'Original Tokens': 'mean',
    'Komprimierte Tokens': 'mean',
    'Kompressionsrate': 'mean',
    'Latenz (ms)': 'mean',
    'Kosten (€)': 'mean',
    'Qualität (%)': 'mean'
}).round(4)

print("DataFrame und agg_stats erzeugt (für Visualisierung und Detailauswertung).")
