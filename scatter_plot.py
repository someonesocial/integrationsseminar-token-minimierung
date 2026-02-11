# -*- coding: utf-8 -*-
"""
Erzeugt ein Scatter-Plot (Punktdiagramm): Qualität vs. Kompressionsrate
für die Präsentation. Zeigt den Trade-off auf einen Blick.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "experiment_daten.json"), encoding="utf-8") as f:
    data = json.load(f)

# Einheitliche Labels
LABELS = {
    "Baseline (keine Kompression)": "Baseline",
    "Manuelle Prompt-Kompression": "Regelbasiert",
    "Strukturierte Kompression": "Strukturiert",
    "Token-Budget (100 Tokens)": "Token-Budget",
    "Chunking (100 Tokens)": "Chunking",
}
COLORS = {
    "Baseline": "#e74c3c",
    "Regelbasiert": "#2ecc71",
    "Strukturiert": "#3498db",
    "Token-Budget": "#f39c12",
    "Chunking": "#9b59b6",
}

fig, ax = plt.subplots(figsize=(10, 6))

for key, d in data.items():
    label = LABELS.get(key, key)
    x = d["kompressionsrate"]
    y = d["qualitaet_prozent"]
    color = COLORS.get(label, "#333")
    size = max(80, d["kosten_euro_pro_1m"] * 0.8)  # Bubble-Größe ~ Kosten
    ax.scatter(x, y, s=size, c=color, edgecolors="black", linewidths=1.2,
               zorder=5, alpha=0.9)
    # Label mit Offset
    offset_y = 2.5 if label != "Token-Budget" else -4
    ax.annotate(label, (x, y), textcoords="offset points",
                xytext=(8, offset_y), fontsize=11, fontweight="bold",
                color=color)

# Achsen
ax.set_xlabel("Kompressionsrate (×)", fontsize=13, fontweight="bold")
ax.set_ylabel("Semantische Qualität (%)", fontsize=13, fontweight="bold")
ax.set_title("Trade-off: Kompressionsrate vs. Qualität", fontsize=15, fontweight="bold")
ax.set_xlim(0.5, 6.5)
ax.set_ylim(50, 105)
ax.axhline(y=90, color="#27ae60", linestyle="--", alpha=0.4, label="Schwelle: 90 % Qualität")
ax.legend(fontsize=10, loc="lower left")
ax.grid(True, alpha=0.3)
ax.tick_params(labelsize=11)

plt.tight_layout()
out = os.path.join(BASE, "praesentation", "scatter_qualitaet_kompression.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Scatter-Plot gespeichert: {out}")
