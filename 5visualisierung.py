import matplotlib
matplotlib.use('Agg')  # Nicht-interaktives Backend (kein Fenster)
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import textwrap
import os

# Kosten in Mikro-Euro umrechnen für bessere Darstellung
df['Kosten (μ€)'] = df['Kosten (€)'] * 1000000
agg_stats['Kosten (μ€)'] = agg_stats['Kosten (€)'] * 1000000

print("KOSTENEINSPARUNGEN (in Mikro-Euro):")
print("-" * 60)
baseline_kosten_ue = agg_stats.loc['Baseline (keine Kompression)', 'Kosten (μ€)']
for strategie in agg_stats.index:
    if strategie != 'Baseline (keine Kompression)':
        einsparung = (1 - agg_stats.loc[strategie, 'Kosten (μ€)'] / baseline_kosten_ue) * 100
        print(f"  {strategie}:")
        print(f"    Kosten: {agg_stats.loc[strategie, 'Kosten (μ€)']:.1f} μ€ (Baseline: {baseline_kosten_ue:.1f} μ€)")
        print(f"    Einsparung: {einsparung:.1f}%")
        print()

# --- Kurzlabels für die X-Achse (keine Überlappung) ---
KURZLABELS = {
    'Baseline (keine Kompression)': 'Baseline',
    'Chunking (100 Tokens)': 'Chunking',
    'Manuelle Prompt-Kompression': 'Manuell',
    'Strukturierte Kompression': 'Strukturiert',
    'Token-Budget (100 Tokens)': 'Token-Budget',
}
kurz_namen = [KURZLABELS.get(s, s) for s in agg_stats.index]
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

# Visualisierungen erstellen
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('Ergebnisse: Token-Minimierungsstrategien',
             fontsize=16, fontweight='bold', y=0.98)

# --- 1. Kompressionsrate ---
ax1 = axes[0, 0]
kompressionsraten = agg_stats['Kompressionsrate'].values
bars1 = ax1.bar(kurz_namen, kompressionsraten, color=colors, edgecolor='black', linewidth=1.2)
ax1.set_ylabel('Kompressionsrate (x)', fontweight='bold')
ax1.set_title('Kompressionsrate', fontweight='bold', fontsize=12)
ax1.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Baseline (1x)')
ax1.legend(fontsize=9)
y_max1 = max(kompressionsraten) * 1.25
ax1.set_ylim(0, y_max1)
for bar, val in zip(bars1, kompressionsraten):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + y_max1 * 0.02,
             f'{val:.2f}x', ha='center', va='bottom', fontweight='bold', fontsize=10)
ax1.tick_params(axis='x', labelsize=10)

# --- 2. Latenz ---
ax2 = axes[0, 1]
latenzen = agg_stats['Latenz (ms)'].values
bars2 = ax2.bar(kurz_namen, latenzen, color=colors, edgecolor='black', linewidth=1.2)
ax2.set_ylabel('Latenz (ms)', fontweight='bold')
ax2.set_title('Latenzreduktion', fontweight='bold', fontsize=12)
y_max2 = max(latenzen) * 1.20
ax2.set_ylim(0, y_max2)
for bar, val in zip(bars2, latenzen):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + y_max2 * 0.02,
             f'{val:.0f} ms', ha='center', va='bottom', fontweight='bold', fontsize=10)
ax2.tick_params(axis='x', labelsize=10)

# --- 3. Kosteneinsparungen ---
ax3 = axes[1, 0]
kosten = agg_stats['Kosten (μ€)'].values
bars3 = ax3.bar(kurz_namen, kosten, color=colors, edgecolor='black', linewidth=1.2)
ax3.set_ylabel('Kosten (μ€)', fontweight='bold')
ax3.set_title('Kosteneinsparungen', fontweight='bold', fontsize=12)
y_max3 = max(kosten) * 1.25
ax3.set_ylim(0, y_max3)
for bar, val in zip(bars3, kosten):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + y_max3 * 0.02,
             f'{val:.1f} μ€', ha='center', va='bottom', fontweight='bold', fontsize=10)
ax3.tick_params(axis='x', labelsize=10)

# --- 4. Qualität – Semantische Ähnlichkeit ---
ax4 = axes[1, 1]
qualitaeten = agg_stats['Qualität (%)'].values
bars4 = ax4.bar(kurz_namen, qualitaeten, color=colors, edgecolor='black', linewidth=1.2)
ax4.set_ylabel('Qualität (%)', fontweight='bold')
ax4.set_title('Qualität – Semantische Ähnlichkeit', fontweight='bold', fontsize=12)
ax4.set_ylim(0, 115)
for bar, val in zip(bars4, qualitaeten):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
ax4.tick_params(axis='x', labelsize=10)

# --- Legende unter dem Plot ---
legend_labels = [f'{KURZLABELS.get(s, s)}' for s in agg_stats.index]
fig.legend(bars1, legend_labels, loc='lower center', ncol=len(legend_labels),
           fontsize=10, frameon=True, fancybox=True, shadow=True,
           bbox_to_anchor=(0.5, -0.02))

plt.tight_layout(rect=[0, 0.04, 1, 0.95])
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'
plt.savefig(os.path.join(OUTPUT_DIR, 'experiment_ergebnisse.png'), dpi=150, bbox_inches='tight')
plt.close('all')
print("\n✅ Visualisierung gespeichert: experiment_ergebnisse.png")
