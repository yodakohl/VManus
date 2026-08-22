# V56 R1 — kleinstes Herbal/Biological-Phrasebook

Status: kreative Werkstattschicht, keine Entzifferung. Geprüft wurden nur die
vier erlaubten Herbal- und drei erlaubten Biological-Seiten. Ausgangspunkt
sind die 17 bereits publizierten exakten GDT327-Brückenkarten mit 136
Vorkommen; PAGE_HOST-Substrings wurden nicht gesucht.

## Ergebnis

V20s Mini-Sprache war zu ausführlich. Unter V50–V54 bleibt ein kleinerer,
parataktischer Bestand:

| gemeinsamer Prompt | exakte Karten | Herbal | Bio | Art |
|---|---|---:|---:|---|
| `SETZEN` | `308e…`, `b5f…` | 2 | 13 | formaler Operator; RIGHT bleibt opak |
| `VERKNÜPFEN` | `dcda…` | 3 | 16 | formaler Operator |
| `VERWENDEN` | `276a…` | 3 | 7 | schwaches Ganzkartenmerkwort |
| `MASS` | `2f1c…` | 9 | 11 | schwaches Ganzkartenmerkwort |
| `BEREITUNG` | `7a4b…` | 5 | 2 | schwaches Merkwort ohne Stoffangabe |
| `KLAR` | `b5df…` | 1 | 3 | schwacher Zustand |
| `AN` | `dd0e…` | 1 | 9 | schwache Relation ohne Ziel und Handlung |
| `ZUVOR` | `dec4…` | 1 | 1 | schwacher Rückbezug |
| `BEREIT` | `e0b6…` | 3 | 4 | schwacher Zustand |
| `TEIL` | `faf3…` | 1 | 1 | schwaches Merkwort; OT-Rahmen bleibt formal |
| **Summe** | **11 exakte Karten** | **29** | **67** | **96/136 Brückenereignisse** |

Fünf weitere Karten mit 38 Ereignissen bleiben `LOCAL_ONLY`; ihre knappen
Rivalen `WARM?`, `DARAUS?`, `MISCHEN?`, `BEARBEITEN?` und `DIES?` klingen in
beiden Registern flüssig, sind aber nicht durch einen ausgewählten Anker
getragen. Die terminale Karte `oldy` verliert die V20-Phrase „sanft kochen und
schließen“ vollständig; ihr formaler LINK+CLOSE-Bau bleibt außerhalb des
Quellenphrasebooks erhalten.

Die vollständige 17-Zeilen-Entscheidung steht in
`V56_R1_PHRASE_CANDIDATES.tsv`.

## Registerlokale Expansion

Das Phrasebook liefert niemals den Gegenstand:

```text
Herbal-Bild + BEREITUNG | MASS | VERWENDEN
  -> eine lokale Pflanzenzubereitung in angegebener Menge gebrauchen

Biological-Bild + BEREITUNG | MASS | VERWENDEN
  -> einen lokalen Arbeits-/Flüssigkeitsposten an der Station gebrauchen
```

Pflanze, Wurzel, Wasser, Wein, Becken, Leitung, Körperstelle und Anwendung
kommen aus Bild und Record. Sie sind kein Bestandteil der drei Prompts.
Dasselbe gilt für `SETZEN`: `SET(<ARG_AL>)` und `SET(<ARG_AIIN>)` erben weder
`AN` noch `MASS`; die RIGHT-Klassen bleiben formale Argumenttypen.

## Kurze Feldmuster

Der Registertransfer endet fast vollständig an der Einzelkarte:

- 0 gemeinsame vollständige sichtbare Feldfolgen;
- 0 gemeinsame vollständige formale Feldfolgen;
- 0 gemeinsame sichtbare Zwei- oder Dreikartenfolgen.

Nach Normalisierung auf exakte GDT327-Karten gibt es fünf gemeinsame Bigramme
und ein Trigramm. Nur zwei bestehen vollständig aus `KEEP`-Karten:

| exaktes Muster | Herbal | Bio | kleinste Rücklesung | Entscheidung |
|---|---:|---:|---|---|
| `dec401… → dcda95…` | 1 | 1 | `ZUVOR | VERKNÜPFEN` | KEEP |
| `276a7c… → 2f1c5e…` | 1 | 1 | `VERWENDEN | MASS` | KEEP |

Die übrigen vier enthalten die opake Karte `b921…`: `DIES? | MASS` (2/1),
`MASS | DIES?` (1/2), `BEREITUNG | DIES?` (2/1) und
`DIES? | MASS | DIES?` (1/1). Sie bleiben `LOCAL_ONLY`. Die Zählungen
überlappen und werden nicht zu den 136 Kartenereignissen addiert.

Auch die beiden behaltenen Muster sind keine Sätze. `VERWENDEN | MASS`
bestimmt weder Kasus noch Reihenfolge einer gesprochenen Phrase;
`ZUVOR | VERKNÜPFEN` nennt weder das Vorige noch die Art der Verbindung.

## Wichtigste Rückzüge gegenüber V20

- `boil gently; close the rubric` fällt weg: `CLOSE` trägt keine Semantik.
- `mix the two portions` schrumpft zu `SETZEN`; Mischen und zwei Portionen
  waren lokale Prosa.
- `begin the next measured entry` schrumpft zu `SETZEN`; `<ARG_AIIN>` ist
  nicht `MASS` und der Beginn kann aus der Position stammen.
- `apply at the pictured place` schrumpft zu `AN`; Handlung und Ziel liefert
  der Registerkontext.
- `take the final indicated share` schrumpft zu `TEIL`; „final“, „nehmen“ und
  die Komposition mit dem OT-Rahmen sind nicht kartenseitig erwiesen.
- `prepared decoction or working liquid` schrumpft zu `BEREITUNG`; Flüssigkeit
  und Dekokt sind stille lokale Objekte.

## Lehrregel

Ein Lehrling lernt zehn Prompts, aber elf exakte Karten:

1. Karte zuerst als vollständige Identität erkennen; Wrapperformen nicht als
   neue Wörter zerlegen.
2. Nur den kurzen Prompt sprechen; unbekannte Karten bleiben unbekannt.
3. RIGHT und `CLOSE` ausschließlich formal lesen.
4. Zwei Karten nur dann als Phrasebook-Muster merken, wenn die exakte Folge in
   Herbal und Biological belegt ist.
5. Erst nach der parataktischen Rücklesung Bild und Record einsetzen, um die
   vollständige lokale Arbeitsanweisung zu bilden.
6. Gleicher Prompt erlaubt nicht, zwei exakte Karten zusammenzulegen:
   `SET(<ARG_AL>)` und `SET(<ARG_AIIN>)` bleiben verschiedene Karten.

Die typische Fehlleistung wäre, aus `AN` „an die Wunde auftragen“, aus
`BEREITUNG` „Kräutersud“ oder aus `SET(<ARG_AIIN>)` „eine gemessene Portion
beginnen“ zu machen. Der Meister streicht jeweils das stille Objekt und lässt
nur Prompt plus lokale Expansion in getrennten Spalten stehen.

## Grenze

Die 96 behaltenen Ereignisse belegen formale und mnemonische Wiederverwendung,
nicht deutsche Wörter. Herbal besitzt insgesamt 100, Biological 281
Ereignisse; das kleine Phrasebook deckt davon nur 29 beziehungsweise 67. Die
vollständigen V53/V54-Recordtexte bleiben daher überwiegend registerlokale
Ganzfeldexpansionen.
