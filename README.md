# Strategien zur Token-Minimierung in LLM-Anwendungen

**Experimentelle Analyse von Prompt-Kompressionsverfahren**

> W1 Integrationsseminar – Onlinemedien, 5. Semester  
> Paul Klemm · DHBW Mosbach · Wintersemester 2025/26

---

## Präsentation

Die Präsentation ist als PDF verfügbar: [WON-23B Paul Klemm W1 Integrationsseminar Strategien zur Token-Minimierung in LLM-Anwendungen.pdf](WON-23B%20Paul%20Klemm%20W1%20Integrationsseminar%20Strategien%20zur%20Token-Minimierung%20in%20LLM-Anwendungen.pdf)
Nachfolgend ist der gesamte Folieninhalt als Textversion eingebettet.

---

### Folie 1 – Titel

<div align="center">

# Strategien zur Token-Minimierung in LLM-Anwendungen

_Experimentelle Analyse von Prompt-Kompressionsverfahren_

W1 Integrationsseminar – Onlinemedien, 5. Semester

Paul Klemm  
DHBW Mosbach | Wintersemester 2025/26

</div>

---

### Folie 2 – Agenda

1. Motivation & Problemstellung
2. Forschungsfrage & Ziele
3. Theoretischer Hintergrund
4. Methodik & Messgrößen
5. Kompressionsstrategien
6. Ergebnisse
7. Diskussion & Fazit
8. Quellenverzeichnis

---

### Folie 3 – Motivation & Problemstellung

|                                                       |                                         |                                                   |
| :---------------------------------------------------: | :-------------------------------------: | :-----------------------------------------------: |
|                       **391 €**                       |                 **20×**                 |                     **75 %**                      |
| Kosten pro 1 Mio. Anfragen (GPT-3.5 Turbo, nur Input) | teurer bei GPT-4 → bis zu 8.000 €/Monat | mögliche Kosteneinsparung durch Token-Minimierung |

> **Kernfrage:** Wie können Tokens reduziert werden – ohne die Antwortqualität zu verlieren?

- Mehr Tokens = höhere Kosten + höhere Latenz
- Prompts enthalten oft **Redundanzen** (Floskeln, irrelevanter Kontext)
- Systematischer Vergleich von Minimierungsstrategien fehlt

_Vgl. Brown et al. (2020); Jiang et al. (2023); OpenAI Pricing (2024)_

---

### Folie 4 – Forschungsfrage & Ziele

> **Forschungsfrage:** Inwiefern können verschiedene Token-Minimierungsstrategien die Betriebskosten und Latenz von LLM-Anwendungen reduzieren, ohne die semantische Qualität signifikant zu beeinträchtigen?

**Ziele**

- Vergleich von 4 Strategien + Baseline
- Quantifizierung: Kosten, Latenz, Qualität
- Handlungsempfehlungen für Praxis

**Abgrenzung**

- Fokus: **Input-Token-Reduktion**
- Kein Fine-Tuning / Modellwechsel
- Deutschsprachige Testprompts

---

### Folie 5 – Theoretischer Hintergrund

#### Tokenisierung (BPE)

- Text → **Subwort-Einheiten** (Byte-Pair Encoding)
- 1 Token ≈ 0,75 Wörter (Deutsch)
- Input- **und** Output-Tokens werden berechnet

> **Kosten** = Tokens / 1000 × Preis/1K

#### Kostenmodell (OpenAI, 2024)

| Modell        | Input/1K | Output/1K |
| ------------- | -------- | --------- |
| GPT-3.5 Turbo | 0,0015 € | 0,002 €   |
| GPT-4         | 0,03 €   | 0,06 €    |

Für diese Studie: **0,00138 € / 1K Input-Tokens**

_Sennrich et al. (2016); OpenAI (2024); tiktoken-Dokumentation_

---

### Folie 6 – Stand der Forschung

#### Prompt Compression

- **LLMLingua** (Jiang et al., 2023) – Token-Wichtigkeit per kleinem Sprachmodell
- **Selective Context** (Li et al., 2023) – Self-Information-basiert
- **LongLLMLingua** (Jiang et al., 2024) – Für lange Kontexte

#### Kontextnutzung

- **Lost in the Middle** (Liu et al., 2023) – Anfang & Ende werden besser genutzt

#### Semantische Ähnlichkeit

- **Sentence-BERT** (Reimers & Gurevych, 2019) – Satz-Embeddings
- **BERTScore** (Zhang et al., 2020) – Evaluation von Textgenerierung

> **Lücke:** Vergleichende Evaluation unter einheitlichem Messrahmen fehlt.

_Jiang et al. (2023/2024); Li et al. (2023); Liu et al. (2023); Reimers & Gurevych (2019); Zhang et al. (2020)_

---

### Folie 7 – Methodik & Messgrößen

#### Experimentdesign

| Parameter       | Wert                   |
| --------------- | ---------------------- |
| Tokenizer       | tiktoken (GPT-3.5 BPE) |
| Testszenarien   | 3 (deutschsprachig)    |
| Strategien      | 4 + Baseline           |
| Einzelmessungen | 15 (3 × 5)             |

#### Messgrößen

| Metrik   | Methode                             |
| -------- | ----------------------------------- |
| Tokens   | tiktoken (exakt)                    |
| Kosten   | 0,00138 €/1K Tokens                 |
| Latenz   | Kompressionszeit + 50ms + 2ms/Token |
| Qualität | Cosine-Similarity (Embeddings)      |

#### Testszenarien

- **Kundensupport** – 264 Tokens – E-Mail mit Bestelldaten, Grußformeln
- **Dokumentenzusammenfassung** – 353 Tokens – Marktbericht mit Zahlen & Prognosen
- **Code-Review** – 234 Tokens – Python-Code mit Analyseanfrage

∅ 284 Tokens/Prompt

---

### Folie 8 – Qualitätsmessung

#### Methode: Semantische Ähnlichkeit

- Modell: **paraphrase-multilingual-MiniLM-L12-v2**
- Original-Text → Embedding (384-dim)
- Komprimierter Text → Embedding
- Qualität = Cosine-Similarity der Vektoren

> **Qualität** = cos(v_orig, v_komp) × 100%

| ≥ 90 %: Hoch | 70–89 %: Mittel | < 70 %: Niedrig |
| :----------: | :-------------: | :-------------: |

#### Vorteile

- Etabliert in NLP (vgl. BERTScore)
- Multilingual (Deutsch + Englisch)
- Automatisiert & reproduzierbar
- Keine manuelle Bewertung nötig

> ⚠️ **Limitation:** Misst semantische Nähe, nicht tatsächliche LLM-Antwortqualität (Proxy-Metrik)

_Reimers & Gurevych (2019); Zhang et al. (2020)_

---

### Folie 9 – Kompressionsstrategien

#### 1. Regelbasierte Kompression

Regex-basiertes Entfernen von Anrede/Grußformeln, Reduktion von Leerzeichen, optionale Stoppwort-Entfernung.  
→ _Deterministisch, kein ML nötig, gut erklärbar_

#### 2. Strukturierte Kompression

Satz-Embeddings → Centrality-Bewertung (Ähnlichkeit zum Dokument-Mittelwert) → nur zentrale Sätze behalten (~45%).  
→ _LLMLingua-inspiriert, semantisch gesteuert_

#### 3. Token-Budget (100 Tokens)

Festes Token-Limit. Sätze nach Position gewichtet (U-Kurve: Anfang & Ende höher). Greedy-Auswahl bis Budget voll.  
→ _Aggressivste Kompression, Lost in the Middle_

#### 4. Chunking mit Überlappung

Text in Chunks mit Überlappung teilen. Pro Chunk: erste + letzte Sätze als Repräsentation. Alle Chunk-Repräsentationen konkatenieren.  
→ _LongLLMLingua-inspiriert, für lange Dokumente_

_Jiang et al. (2023/2024); Li et al. (2023); Liu et al. (2023)_

---

### Folie 10 – Ergebnisse: Gesamtübersicht

| Strategie    | Kompression | Tokens (∅) |   Latenz    | Kosten/1K | Einsparung | Qualität  |
| ------------ | :---------: | :--------: | :---------: | :-------: | :--------: | :-------: |
| Baseline     |    1,0×     |    284     |   617 ms    |  0,391 €  |     –      | **100 %** |
| Chunking     |    1,0×     |    278     |   607 ms    |  0,384 €  |    2 %     | **92 %**  |
| Regelbasiert |    1,2×     |    233     |   516 ms    |  0,321 €  |  **18 %**  | **97 %**  |
| Strukturiert |    2,0×     |    161     | ⚠️ 2.247 ms |  0,222 €  |  **43 %**  | **91 %**  |
| Token-Budget |    5,5×     |     72     | **194 ms**  |  0,099 €  |  **75 %**  |   80 %    |

Durchschnitt über 3 Szenarien (n = 15 Messungen). Kosten: nur Input-Tokens, GPT-3.5 Turbo.

> ⚠️ **Kritische Beobachtung:** Strukturierte Kompression ist durch Embedding-Berechnung **3,6× langsamer** als Baseline!

---

### Folie 11 – Ergebnisse: Detailvergleich

_Balkendiagramme: 15 Einzelmessungen (3 Szenarien × 5 Strategien). Qualität = semantische Ähnlichkeit._

_(Siehe Visualisierung in `experiment_ergebnisse.png`)_

---

### Folie 12 – Kostenanalyse

#### Pro 1.000 Anfragen

| Strategie    | Kosten  | Einsparung |
| ------------ | :-----: | :--------: |
| Baseline     | 0,391 € |     –      |
| Regelbasiert | 0,321 € |  **18 %**  |
| Strukturiert | 0,222 € |  **43 %**  |
| Token-Budget | 0,099 € |  **75 %**  |

#### Hochrechnung: 1 Mio. Anfragen/Monat

|                                    |                                    |
| :--------------------------------: | :--------------------------------: |
| **169 €** Ersparnis – Strukturiert | **293 €** Ersparnis – Token-Budget |

Bei GPT-4: Einsparungen × 20 (bis zu 5.860 €/Monat)

> **Praxisbeispiel:** Ein Kundensupport-Chatbot mit 10.000 Anfragen/Tag spart mit Token-Budget **~3.000 €/Jahr** (nur Input-Tokens).

---

### Folie 13 – Diskussion

#### Kernerkenntnisse

- **Trade-off bestätigt:** Mehr Kompression → weniger Qualität
- **Texttyp entscheidend:** Code ≠ E-Mail ≠ Bericht
- **Embedding-Overhead:** Strukturierte Kompression 3,6× langsamer
- **Token-Budget:** Höchste Einsparung (75 %), aber Qualitätseinbußen (80 %)

#### Empfehlungen

| Anwendungsfall                                     | Strategie    | Qualität | Ersparnis |  Latenz  |
| -------------------------------------------------- | ------------ | :------: | :-------: | :------: |
| **Qualitätskritisch** (Support, Medizin, Recht)    | Regelbasiert |   97 %   |   18 %    |  516 ms  |
| **Balanciert** (Analytics, Massenverarbeitung)     | Strukturiert |   91 %   |   43 %    | 2.247 ms |
| **Kostenoptimiert** (Pre-Filtering, interne Tools) | Token-Budget |   80 %   |   75 %    |  194 ms  |

---

### Folie 14 – Limitationen

- **n = 3 Szenarien** – begrenzte Generalisierbarkeit
- **Proxy-Metrik** – semantische Ähnlichkeit ≠ LLM-Antwortqualität
- **Keine echten API-Calls** – Latenz modelliert (50ms + 2ms/Token)
- **Nur Input-Tokens** – Output-Kosten nicht gemessen
- **Nur Deutsch** – Sprachübertragbarkeit offen
- **Ein Embedding-Modell** – andere Modelle könnten abweichen

#### Ausblick

- Dynamische Kompressionsraten je nach Query-Komplexität
- Kombination mit Output-Token-Optimierung
- Evaluation mit verschiedenen LLM-Modellen (GPT-4, Claude, Llama)

---

### Folie 15 – Fazit

#### Beantwortung der Forschungsfrage

- **Kompressionsraten:** 1,2× (regelbasiert) bis 5,5× (Token-Budget) erreichbar
- **Kosteneinsparungen:** 18 % bis 75 % realistisch (Input-Tokens)
- **Qualität:** Ab ~2× Kompression sinkt Qualität merklich; bei 5,5× nur noch 80 %
- **Latenz-Trade-off:** Embedding-basierte Methoden haben signifikanten Overhead

> **Kernbotschaft:** Regelbasierte Kompression sollte **immer als Grundlage** eingesetzt werden – sie liefert 18 % Einsparung bei 97 % Qualität ohne Latenz-Overhead. Weiterführende Strategien (strukturiert, Token-Budget) können **bei Bedarf ergänzt** werden, um noch mehr Kontext zu komprimieren.

---

### Folie 16 – Quellenverzeichnis (APA)

- Brown, T. B., Mann, B., Ryder, N., et al. (2020). Language models are few-shot learners. _Advances in Neural Information Processing Systems, 33_, 1877–1901. https://arxiv.org/abs/2005.14165
- Jiang, H., Wu, Q., Luo, X., et al. (2023). LLMLingua: Compressing prompts for accelerated inference of large language models. _arXiv preprint arXiv:2310.05736_. https://arxiv.org/abs/2310.05736
- Jiang, H., Wu, Q., Luo, X., et al. (2024). LongLLMLingua: Accelerating and enhancing LLMs in long context scenarios via prompt compression. _arXiv preprint arXiv:2310.06839_. https://arxiv.org/abs/2310.06839
- Li, X., Zhu, J., & Zhao, Y. (2023). Selective context: Efficient processing of long documents with language models. _arXiv preprint arXiv:2305.07726_.
- Liu, N. F., Lin, K., Hewitt, J., et al. (2023). Lost in the middle: How language models use long contexts. _arXiv preprint arXiv:2307.03172_. https://arxiv.org/abs/2307.03172
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. _Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing_. https://arxiv.org/abs/1908.10084
- Sennrich, R., Haddow, B., & Birch, A. (2016). Neural machine translation of rare words with subword units. _Proceedings of the 54th Annual Meeting of the ACL_, 1715–1725.
- Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). BERTScore: Evaluating text generation with BERT. _International Conference on Learning Representations (ICLR)_. https://arxiv.org/abs/1904.09675
- OpenAI. (2024). _Pricing for OpenAI API_. https://openai.com/pricing

---

## Projekt-Dateien

| Datei                                          | Beschreibung                               |
| ---------------------------------------------- | ------------------------------------------ |
| `1token_berechnung_anfragen.py`                | Token-Berechnung und API-Anfragen          |
| `2Kompressionsstrategien.py`                   | Implementierung der Kompressionsstrategien |
| `3schaetzung_qualitat_aufgrund_kompression.py` | Qualitätsschätzung nach Kompression        |
| `4ergebnisse_pandas.py`                        | Ergebnisauswertung mit pandas              |
| `5visualisierung.py`                           | Visualisierungen                           |
| `6ergebnisse_detail.py`                        | Detaillierte Ergebnisse                    |
| `7finale_ergebnisse.py`                        | Finale Ergebnisaufbereitung                |
| `run_all_experiments.py`                       | Alle Experimente ausführen                 |
| `scatter_plot.py`                              | Scatter-Plot-Visualisierung                |
| `experiment_daten.json`                        | Experimentdaten (JSON)                     |
| `experiment_ausgabe.txt`                       | Experimentausgabe (Log)                    |

## Setup

```bash
pip install -r requirements.txt
```

