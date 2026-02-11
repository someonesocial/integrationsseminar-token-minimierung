
# Finale Zusammenfassung für die Präsentation
print("=" * 100)
print("FINALE EXPERIMENT-ERGEBNISSE: Token-Minimierungsstrategien")
print("=" * 100)

# Manuelle Zusammenfassung der Ergebnisse
strategie_namen = ['Baseline (keine Kompression)', 'Chunking (100 Tokens)', 
                   'Manuelle Prompt-Kompression', 'Strukturierte Kompression', 
                   'Token-Budget (100 Tokens)']

ergebnisse_dict = {}

for strategie in strategie_namen:
    strategie_ergebnisse = [r for r in alle_ergebnisse if r.strategie == strategie]
    
    avg_original = np.mean([r.original_tokens for r in strategie_ergebnisse])
    avg_komprimiert = np.mean([r.komprimierte_tokens for r in strategie_ergebnisse])
    avg_kompressionsrate = np.mean([r.kompressionsrate for r in strategie_ergebnisse])
    avg_latenz = np.mean([r.latenz_ms for r in strategie_ergebnisse])
    avg_kosten = np.mean([r.kosten_euro for r in strategie_ergebnisse])
    avg_qualitaet = np.mean([r.qualitaets_score for r in strategie_ergebnisse])
    
    ergebnisse_dict[strategie] = {
        'original_tokens': avg_original,
        'komprimierte_tokens': avg_komprimiert,
        'kompressionsrate': avg_kompressionsrate,
        'latenz_ms': avg_latenz,
        'kosten_euro': avg_kosten,
        'qualitaet': avg_qualitaet
    }

# Ausgabe
for strategie, daten in ergebnisse_dict.items():
    print(f"\n📊 {strategie}")
    print("-" * 80)
    print(f"  Original Tokens:        {daten['original_tokens']:.0f}")
    print(f"  Komprimierte Tokens:    {daten['komprimierte_tokens']:.0f}")
    print(f"  Kompressionsrate:       {daten['kompressionsrate']:.2f}x")
    print(f"  Latenz:                 {daten['latenz_ms']:.1f} ms")
    print(f"  Kosten pro Anfrage:     {daten['kosten_euro']:.6f} €")
    print(f"  Kosten pro 1K Anfragen: {daten['kosten_euro'] * 1000:.4f} €")
    print(f"  Qualität:               {daten['qualitaet'] * 100:.0f}%")

# Speichere die Ergebnisse für die Präsentation
import json

export_daten = {}
for strategie, daten in ergebnisse_dict.items():
    export_daten[strategie] = {
        'original_tokens': float(daten['original_tokens']),
        'komprimierte_tokens': float(daten['komprimierte_tokens']),
        'kompressionsrate': float(daten['kompressionsrate']),
        'latenz_ms': float(daten['latenz_ms']),
        'kosten_euro_pro_anfrage': float(daten['kosten_euro']),
        'kosten_euro_pro_1k': float(daten['kosten_euro'] * 1000),
        'kosten_euro_pro_1m': float(daten['kosten_euro'] * 1000000),
        'qualitaet_prozent': float(daten['qualitaet'] * 100)
    }

import os
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'
with open(os.path.join(OUTPUT_DIR, 'experiment_daten.json'), 'w', encoding='utf-8') as f:
    json.dump(export_daten, f, indent=2, ensure_ascii=False)

print("\n✅ Experiment-Daten gespeichert: experiment_daten.json")
