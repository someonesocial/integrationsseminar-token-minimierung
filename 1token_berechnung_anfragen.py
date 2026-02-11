
import tiktoken
import time
import json
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Encoder für GPT-4/GPT-3.5 Turbo
encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

@dataclass
class ExperimentResult:
    strategie: str
    original_tokens: int
    komprimierte_tokens: int
    latenz_ms: float
    qualitaets_score: float
    kosten_euro: float
    kompressionsrate: float

# Test-Prompts für verschiedene Szenarien
TEST_PROMPTS = {
    "kundensupport": """
Sehr geehrte Damen und Herren,

ich habe ein Problem mit meiner letzten Bestellung. Ich habe am 15. Januar 2024 die Produkte XYZ-123 und ABC-456 bestellt. 
Die Bestellnummer lautet ORD-2024-001598. Das Paket wurde laut Tracking am 18. Januar zugestellt, aber ich habe nur 
das Produkt XYZ-123 erhalten. Das Produkt ABC-456 fehlt komplett. 

Ich habe bereits zweimal versucht, den Kundenservice telefonisch zu erreichen, aber wurde nach 20 Minuten Warteschleife 
immer wieder getrennt. Das ist sehr frustrierend, da ich das fehlende Produkt dringend für ein Projekt benötige.

Können Sie bitte überprüfen, was mit meiner Bestellung passiert ist? Ich erwarte entweder die sofortige Zusendung 
des fehlenden Produkts oder eine vollständige Rückerstattung des Betrags für ABC-456 in Höhe von 89,99 €.

Mit freundlichen Grüßen
Max Mustermann
Kundennummer: KDN-78432
Telefon: +49 170 1234567
Email: max.mustermann@email.de
""",
    "dokumentenzusammenfassung": """
Der vorliegende Bericht analysiert die Marktentwicklung im Bereich erneuerbarer Energien für das Geschäftsjahr 2023. 
Die globalen Investitionen in erneuerbare Energien erreichten einen neuen Höchststand von 1,8 Billionen US-Dollar, 
was einem Anstieg von 17% gegenüber dem Vorjahr entspricht. 

Solarenergie dominierte mit einem Anteil von 73% an allen neu installierten erneuerbaren Kapazitäten. 
Windenergie folgte mit 21%, während Wasserkraft, Geothermie und andere Technologien die verbleibenden 6% ausmachten. 

Die Kosten für Solarmodule sind um weitere 12% gesunken, was die Wirtschaftlichkeit zusätzlich verbessert hat. 
In Europa verzeichnete Deutschland mit 14,6 GW neu installierter PV-Leistung den höchsten Zuwachs. 
China blieb mit 216 GW neu installierter Leistung der weltweit größte Markt.

Herausforderungen bestehen weiterhin in der Netzintegration, Speicherkapazitäten und regulatorischen Rahmenbedingungen. 
Die durchschnittliche Genehmigungszeit für Windenergieprojekte liegt in Deutschland immer noch bei 4,2 Jahren.

Für 2024 wird ein weiteres Wachstum von 15-20% erwartet, getrieben durch verbesserte Wirtschaftlichkeit und 
verschärfte Klimaziele. Die EU hat ihr Ziel für 2030 auf 42,5% erneuerbare Energien angehoben.
""",
    "code_review": """
Bitte analysiere den folgenden Python-Code und identifiziere mögliche Verbesserungen:

```python
def berechne_gesamtsumme(daten):
    summe = 0
    for i in range(len(daten)):
        if daten[i]['typ'] == 'einnahme':
            summe = summe + daten[i]['betrag']
        elif daten[i]['typ'] == 'ausgabe':
            summe = summe - daten[i]['betrag']
    return summe

def verarbeite_datei(dateipfad):
    with open(dateipfad, 'r') as f:
        inhalt = f.read()
    daten = json.loads(inhalt)
    ergebnis = berechne_gesamtsumme(daten)
    print("Ergebnis:", ergebnis)
    return ergebnis
```

Der Code soll finanzielle Transaktionen verarbeiten und die Gesamtsumme berechnen. 
Er liest Daten aus einer JSON-Datei und unterscheidet zwischen Einnahmen und Ausgaben.
"""
}

print("Test-Prompts geladen:")
for name, prompt in TEST_PROMPTS.items():
    tokens = len(encoder.encode(prompt))
    print(f"  {name}: {tokens} Tokens")
