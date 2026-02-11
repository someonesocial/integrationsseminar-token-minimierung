# -*- coding: utf-8 -*-
"""Führt alle Experiment-Skripte nacheinander im gleichen Namensraum aus."""
import os
import sys
import io

# Arbeitsverzeichnis = Ordner dieses Skripts
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- Tee: Ausgabe gleichzeitig auf Konsole UND in Datei schreiben ---
class TeeWriter:
    """Schreibt stdout gleichzeitig in die Konsole und eine Datei."""
    def __init__(self, logfile_path, original_stdout):
        self._original = original_stdout
        self._logfile = open(logfile_path, 'w', encoding='utf-8')
    def write(self, text):
        self._original.write(text)
        self._logfile.write(text)
    def flush(self):
        self._original.flush()
        self._logfile.flush()
    def isatty(self):
        return False
    def fileno(self):
        return self._original.fileno()
    @property
    def encoding(self):
        return 'utf-8'
    def close(self):
        self._logfile.close()

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'experiment_ausgabe.txt')
_tee = TeeWriter(LOG_PATH, sys.stdout)
sys.stdout = _tee

g = {"__name__": "__main__", "__builtins__": __builtins__}

scripts = [
    "1token_berechnung_anfragen.py",
    "2Kompressionsstrategien.py",
    "3schaetzung_qualitat_aufgrund_kompression.py",
    "4ergebnisse_pandas.py",
    "5visualisierung.py",
    "6ergebnisse_detail.py",
    "7finale_ergebnisse.py",
]

for path in scripts:
    print("\n" + "=" * 60)
    print(f"Führe aus: {path}")
    print("=" * 60)
    with open(path, encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, path, "exec"), g)

print("\n" + "=" * 60)
print("Alle Skripte abgeschlossen.")
print("=" * 60)
print(f"\n✅ Gesamte Ausgabe gespeichert: experiment_ausgabe.txt")

# Tee schließen und stdout wiederherstellen
sys.stdout = _tee._original
_tee.close()
