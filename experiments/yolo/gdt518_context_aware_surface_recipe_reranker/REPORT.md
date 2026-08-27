# GDT518 — Die sichtbare Form schlägt den bloßen Kandidatenrang

## Ergebnis

Der GDT517-Compiler erzeugte zwar für alle 159 neuen Oberflächen das heutige
Rezept, setzte es aber nur 117-mal auf Rang 1. Der neue Reranker lernt aus den
älteren 1.558 Oberflächen, welche **Komponenten** und welche benachbarten
**Komponentenpaare** eine sichtbare Zeichenfolge erwarten lässt. Die unmittelbare
linke/rechte Kartenumgebung darf danach nur noch leicht korrigieren.

| Ordnung | Rang 1 | Top 3 | Top 5 | Rangsumme | tiefster richtiger Rang |
|---|---:|---:|---:|---:|---:|
| GDT517 unverändert | 117 | 150 | 157 | 281 | 56 |
| Formdecoder + alter Rang | 133 | 155 | 158 | 213 | 14 |
| plus Bigramm-Nachbarn | 134 | 155 | 158 | 212 | 14 |
| plus Trigramm-Nachbarn | 134 | 155 | 158 | 212 | 14 |
| ausgewähltes Mittel beider Kontexte | **134** | **155** | **158** | **212** | **14** |

Das ist kein kleiner kosmetischer Effekt. 22 alte Rang-1-Fehler werden richtig
umgestellt, fünf vorher richtige Defaults gehen verloren; netto kommen 17
richtige erste Entscheidungen hinzu. 112 der 117 alten Treffer bleiben stehen.

## Was das über unser Gesamtmodell sagt

Der größte Informationsgewinn kommt nicht aus Thema, Besitzer oder einer
erfundenen langen Übersetzung. Er kommt aus der **inneren sichtbaren Form**:
Zeichen-Einzelstücke, Zeichenpaare und Zeichen-Dreier sagen voraus, welche
Arbeitskomponenten und Komponentenpaare gebraucht werden. Das passt wesentlich
besser zu unserer gegenwärtigen Arbeitstheorie einer Mischung aus gelernten
Ganzkarten und zusammensetzbaren Fachkürzeln als zu einem Wörterbuch, in dem
jede lange Form eine frei erfundene komplexe deutsche Bedeutung erhält.

Kontext hilft, aber nur um einen Fall. Das ist ebenfalls wichtig: Wir sollen
Kontext zur Wahl zwischen endlichen Lesarten benutzen, nicht zur willkürlichen
Neudeutung einer sichtbaren Form.

Beispiele für echte Korrekturen sind:

- `cheod`: `CH+E+O` wird zu `CH+E+O+D_ADDR`;
- `dcheey`: `D_ADDR+SH+EE+Y` wird zu `D_ADDR+CH+EE+Y`;
- `rals`: `R+A_ADDR+L` wird zu `R+AL+S`;
- `shtchy`: `SH+T+Y` wird zu `SH+T+CH+Y`;
- `psheody`: Erst der kleine Nachbarterm entscheidet zwischen den zwei
  formseitig fast gleich guten Schlussanalysen richtig.

## Die verbleibenden 25 sind nicht beliebig

Die Restfehler konzentrieren sich weiter auf sichtbare Grenzstellen:

- `dy` gegen `D_ADDR+Y` und gegen bloßes `Y`;
- `ol` gegen `O+L`;
- verschlucktes oder zusätzliches `a/d/q` an einer Ganzstückgrenze;
- `CH`, `SH` und `CHD`;
- lokale Zeichen wie `LOCAL_CHAR_F/I`;
- lange Formen wie `aiicthy` und `dalcheeeky`, deren richtige Rezepte nun auf
  Rang 14 beziehungsweise Rang 5 liegen statt zuvor 6 und 56.

Das legt den nächsten Angriff ziemlich klar fest: Die Struktur-Tags besitzen
sichtbare Stammanker (`A_ADDR~a`, `D_ADDR~d`, `CH~ch`, `OL~ol` usw.). Ein
monotoner Oberflächen-/Atom-Transduktor kann prüfen, welche Kandidaten alle
sichtbaren Stammteile sparsam erklären und welche ein Zeichen in einem langen
Ganzstück verschlucken. Ein erster Nebenlauf zeigt bereits, dass dieser Hebel
zusätzliche Fälle gewinnt; er gehört wegen seiner eigenen Annahmen in den
nächsten, getrennten Durchgang.

## Praktischer Aufruf

```bash
python3 experiments/yolo/gdt518_context_aware_surface_recipe_reranker/src/rerank_surface.py \
  --surface NEUE_FORM \
  --left-recipe CH+E+Y \
  --right-recipe K+O+DY \
  --domain PROSE_STREAM --top 5
```

Für die bereits bekannten 30 Seiten bleibt die Reihenfolge: exakte
Ereigniskarte, eindeutige bekannte Oberflächen-/Domänenkarte, erst dann der
Reranker. Das Ergebnis verbessert also den Zukunftsdefault, ohne eine bekannte
Lesart rückwirkend zu überschreiben. Es bestätigt weder historische Wörter
noch deutsche Klartextbedeutungen.
