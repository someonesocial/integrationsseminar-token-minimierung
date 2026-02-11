import pandas as pd

# Kosten mit höherer Präzision neu berechnen
# OpenAI GPT-3.5 Turbo Preise (Stand 2024): $0.0015 pro 1K Input-Token
# Umgerechnet bei ~0.92 €/$: ~0.00138 € pro 1K Input-Token

PREIS_PRO_1K_TOKENS = 0.00138  # Euro

def berechne_kosten(tokens):
    return (tokens / 1000) * PREIS_PRO_1K_TOKENS

# Kosten für alle Ergebnisse neu berechnen
for r in alle_ergebnisse:
    r.kosten_euro = berechne_kosten(r.komprimierte_tokens)

# DataFrame aktualisieren
data = []
for r in alle_ergebnisse:
    data.append({
        'Strategie': r.strategie,
        'Szenario': [k for k, v in TEST_PROMPTS.items() if len(encoder.encode(v)) == r.original_tokens][0] if any(len(encoder.encode(v)) == r.original_tokens for v in TEST_PROMPTS.values()) else 'unbekannt',
        'Original Tokens': r.original_tokens,
        'Komprimierte Tokens': r.komprimierte_tokens,
        'Kompressionsrate': r.kompressionsrate,
        'Latenz (ms)': r.latenz_ms,
        'Kosten (€)': r.kosten_euro,
        'Qualität (%)': r.qualitaets_score * 100
    })

df = pd.DataFrame(data)

# Kostenanalyse
print("KOSTENANALYSE (pro 1000 Anfragen):")
print("=" * 80)
print(f"{'Strategie':<35} {'Kosten/1K':<15} {'Einsparung':<15}")
print("-" * 80)

kosten_pro_1k = df.groupby('Strategie')['Kosten (€)'].mean() * 1000
baseline_kosten = kosten_pro_1k['Baseline (keine Kompression)']

for strategie in kosten_pro_1k.index:
    if strategie == 'Baseline (keine Kompression)':
        print(f"{strategie:<35} {kosten_pro_1k[strategie]:.4f} €{'':<10} {'(Referenz)':<15}")
    else:
        einsparung = (1 - kosten_pro_1k[strategie] / baseline_kosten) * 100
        print(f"{strategie:<35} {kosten_pro_1k[strategie]:.4f} €{'':<10} {einsparung:>6.1f}%")

print("\n")

# Kosten pro 1 Million Anfragen
print("KOSTENANALYSE (pro 1 Million Anfragen):")
print("=" * 80)
print(f"{'Strategie':<35} {'Kosten/1M':<15} {'Einsparung':<15}")
print("-" * 80)

for strategie in kosten_pro_1k.index:
    kosten_1m = kosten_pro_1k[strategie] * 1000
    if strategie == 'Baseline (keine Kompression)':
        print(f"{strategie:<35} {kosten_1m:.2f} €{'':<10} {'(Referenz)':<15}")
    else:
        einsparung = (1 - kosten_1m / (baseline_kosten * 1000)) * 100
        print(f"{strategie:<35} {kosten_1m:.2f} €{'':<10} {einsparung:>6.1f}%")

print("\n")

# Zusammenfassung der Ergebnisse für die Präsentation
print("ZUSAMMENFASSUNG DER EXPERIMENT-ERGEBNISSE:")
print("=" * 100)
zusammenfassung = df.groupby('Strategie').agg({
    'Original Tokens': 'mean',
    'Komprimierte Tokens': 'mean',
    'Kompressionsrate': 'mean',
    'Latenz (ms)': 'mean',
    'Kosten (€)': 'mean',
    'Qualität (%)': 'mean'
}).round(2)
print(zusammenfassung.to_string())
