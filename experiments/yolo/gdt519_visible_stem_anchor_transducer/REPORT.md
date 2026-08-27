# GDT519 — Einzelstämme plus kurze gelernte Renderer

## Ergebnis

Wir haben jetzt genau die Mischform, nach der wir gesucht haben: nicht ein
Wörterbuch aus immer längeren deutschen Sätzen, aber auch keine naive
Buchstabe-für-Buchstabe-Ersetzung.

Das Oberflächenmodell besitzt:

- **45** elementare sichtbare Anker wie `CH~ch`, `OL~ol`, `A_ADDR~a` und
  `D_ADDR~d`;
- **287** gelernte kurze Zwei-/Drei-Atom-Renderer;
- insgesamt **332** Atomfolgen mit **473** möglichen sichtbaren Renderern.

Ein wichtiges Beispiel ist `chek~CH+K`. Der Schreiber kann also eine kurze
gelernte Form für zwei Komponenten verwenden; das Modell muss das sichtbare
`e` nicht automatisch als eigenen Grad `E` lesen. Gleichzeitig kostet ein
Kandidat, der einen sichtbaren Stamm vollständig verschluckt oder einen nicht
sichtbaren Stamm behauptet.

## Es trägt auch auf älteren Zusammensetzungen

In vier rotierenden Altform-Rehearsals wird jede Gruppe nur aus den anderen
drei Gruppen rekonstruiert. 1.441/1.558 Zielrezepte werden vom jeweiligen
Compiler erzeugt. Innerhalb dieses endlichen Raums ergibt sich:

| Ordnung | Rang 1 | Top 5 | Rangsumme | tiefster richtiger Rang |
|---|---:|---:|---:|---:|
| reiner Fold-Compiler | 1.000 | 1.395 | 2.609 | 69 |
| sichtbarer Formdecoder | 1.054 | 1.395 | 2.374 | 35 |
| plus Stamm-/Renderer-Transduktor | **1.082** | **1.418** | **2.152** | **23** |

Der Ankergewinn ist damit nicht nur eine Reparaturliste für die jüngsten vier
Seiten. Die verbleibenden 117 nicht erzeugten Altformen sind eine
Kandidatenraum-Frage; der Transduktor kann nur vorhandene endliche Kandidaten
ordnen.

## Die aktuellen 159 Formen

| Modell | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme | tiefster Rang |
|---|---:|---:|---:|---:|---:|---:|
| GDT517 | 117 | 145 | 150 | 157 | 281 | 56 |
| GDT518 | 134 | 147 | 155 | 158 | 212 | 14 |
| GDT519 | **138** | **153** | **157** | **158** | **192** | **8** |

Gegen GDT518 werden acht Fehler richtig umgestellt und vier Treffer verloren;
eine falsche Entscheidung wechselt zu einer anderen falschen. Netto kommen
vier Rang-1-Treffer hinzu. Gegen den ursprünglichen Compiler beträgt der
Gesamtgewinn nun 21 Rang-1-Treffer.

Korrekt gewinnt der Anker unter anderem:

- `cheta → CH+E+T+A_ADDR`;
- `chpady → CH+P+A_ADDR+DY`;
- `fshodchy → LOCAL_CHAR_F+SH+O+D_ADDR+CH+Y`;
- `qokchey → OK+CH+E+Y`;
- `shddy → SH+D_ADDR+DY`;
- `shekeefy → SH+E+K+EE+LOCAL_CHAR_F+Y`;
- `shyshol → SH+Y+SH+OL`;
- `shytchy → SH+Y+T+CH+Y`.

Vier zu aggressive Aufteilungen zeigen zugleich, was noch fehlt:
`chekeey`, `dsholdaiir`, `okedals` und `saiis`. Hier sieht der Transduktor einen
plausiblen Einzelstamm, obwohl die bessere Arbeitskarte ihn als Teil eines
kurzen Renderers behandelt. Das ist kein Grund, die Anker aufzugeben; es ist
die nächste Grenze zwischen produktivem Stamm und gelernter Hülle.

## Ein Beispiel mit vollständiger Spur

Für `aiicthy` richtet das heutige Zielrezept sichtbar aus:

`a→A_ADDR | i→LOCAL_CHAR_I | i→LOCAL_CHAR_I | cthy→CH+T+Y`.

Der konkurrierende Default `AIIN+CH+T+Y` muss dagegen `aii` gegen den Anker
`aiin` mit zwei Editkosten ausrichten. Das Ziel steigt dadurch von GDT518-Rang
14 auf Rang 8. Es ist noch nicht Rang 1, aber der Fehler ist nun als konkrete
Grenzfrage sichtbar statt als freie Bedeutungsfrage.

## Praktischer Aufruf

```bash
python3 experiments/yolo/gdt519_visible_stem_anchor_transducer/src/align_surface.py \
  --surface NEUE_FORM \
  --left-recipe SH+E+Y \
  --right-recipe K+O+DY \
  --domain PROSE_STREAM --top 5
```

Die Ausgabe zeigt für jeden Kandidaten Compiler-Rang, GDT518-Basiskosten,
Stammkosten und die vollständige monotone Segmentspur. Bekannte Ereignis- oder
Oberflächenkarten gewinnen weiterhin vor jedem automatischen Default.

Das ist eine starke Arbeitsarchitektur für Fachkürzel plus gelernte
Ganzstücke. Die Anker sind dennoch nur sichtbare Struktur-Tags; sie beweisen
weder historische Wörter noch die deutschen Arbeitsbedeutungen.
