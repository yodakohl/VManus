# V49 R3 — atomarer Komponentenvertrag statt Satzglossen

## Ergebnis in einem Satz

Wenn eine Einheit wirklich wie ein wiederverwendbarer Stamm behandelt werden
soll, dürfen wir ihr **nicht** die Schnittmenge unserer eigenen langen
Übersetzungssätze unterschieben. Nach diesem Audit bleiben nur drei knappe
operative Arbeitsnamen übrig:

```text
OK = SET        (einen formal bezeichneten Posten setzen)
OT = MARK       (einen formal bezeichneten Bezug markieren)
L  = LINK       (an einen lokal gegebenen Anschluss anknüpfen)
```

Auch diese drei sind keine entschlüsselten Wörter. Es sind atomare
Werkstatt-Pseudonyme für drei wiederkehrende formale Operationen. Alle
inhaltlichen Nomen und konkreten Handlungen bleiben unbekannt.

## Harte Korrektur von V47/V48

Die folgenden alten Werte werden als Stammglossen zurückgezogen:

| Host | alter Wert | R3-Entscheid |
|---|---|---|
| `or` | bereitetes Ergebnis/Arbeitsmedium | `UNKNOWN` |
| `al` | Ziel-/Parallelstation | `UNKNOWN` |
| `e` | bis zur Zustandsgrenze führen | `UNKNOWN` |
| `chey` | ausgewählten Materialanteil aufnehmen | `UNKNOWN` |
| `chor` | Pflanzenmaterial zeitgebunden beschaffen | `UNKNOWN` |

Dasselbe gilt für die angeblichen Bedeutungen der wiederkehrenden Ganzkarten
`AIIN`, `EY`, `OKY`, `LCHE`, `OKE`, `CTHY`, `OKEEY`, `CKHY` und `OLOR`.
Ihre Wiederkehr ist real; die aus den V42/V45-Sätzen abgeleiteten Bedeutungen
sind es nicht.

Insbesondere ist `CHOR` ein **atomarer PAGE_HOST**. Die eingefrorene formale
Darstellung lizenziert weder `CHO + R` noch `CH + OR`. Seine drei Vorkommen
ergeben nur:

```text
qotchor / otchor = FRAME_OT(UNKNOWN_HOST[CHOR])
chochor          = FRAME_O(UNKNOWN_HOST[CHOR])
```

„Pflanzenmaterial zeitgebunden beschaffen“ war eine ganze interpretierte
Proposition, keine lexikalisch plausible Stammglosse.

## Warum gerade `SET`, `MARK` und `LINK`?

Diese Bezeichnungen entstehen nicht aus den konkreten Herbal-/Bad-
Übersetzungen, sondern aus wiederkehrender formaler Kombinatorik.

### `OK → SET`

- 5 exakte Kartenarten;
- 24 Ereignisse auf 4 Prosaseiten;
- Kombination mit fünf verschiedenen RIGHT-Klassen;
- überwiegend am Feldanfang oder im Feldinneren, fast nie als Abschluss.

Die Alternativen `ITEM`, `ACTIVATE`, `ASSIGN` und `WORK` waren jeweils
inhaltlich enger. `SET` bedeutet hier lediglich: einen durch die formale
Kompletierung bestimmten Posten einsetzen.

```text
okain   = SET(<ARG_AIN>)
okal    = SET(<ARG_AL>)
okar    = SET(<ARG_AR>)
okair   = SET(<ARG_AIR>)
okaiin  = SET(<ARG_AIIN>)
```

`ARG_AIN` usw. sind anonyme Argumentklassen, nicht „Maß“, „Ziel“, „Quelle“
oder „Laufweg“.

### `OT → MARK`

- 3 exakte Kartenarten;
- 7 Ereignisse auf 3 Prosaseiten;
- Kombination mit drei RIGHT-Klassen;
- formaler Gegenlauf zum produktiveren `OK`-Paradigma.

`REFERENCE`, `ROUTE` und `TIME` waren konkrete Interpretationen einzelner
Sätze. `MARK` ist die kleinere gemeinsame Arbeitsanweisung:

```text
otaiin = MARK(<ARG_AIIN>)
otal   = MARK(<ARG_AL>)
otar   = MARK(<ARG_AR>)
```

### `L → LINK`

- 5 exakte Kartenarten;
- 26 Ereignisse auf 5 Prosaseiten;
- nackte, gerahmte, RIGHT-tragende und geschlossene Realisierungen.

`LIQUID`, `RECEIVER` und `PREVIOUS PREPARATION` sind nicht gemeinsam
haltbar. `LINK` ist nur die formale Gemeinsamkeit:

```text
l       = LINK
lar     = LINK(<ARG_AR>)
ol      = FRAME_O(LINK)
ldy     = CLOSE(LINK)
oldy    = CLOSE(FRAME_O(LINK))
```

## Komponentenvertrag

Der ausführbare Vertrag benutzt genau diese Regeln:

```text
HOST:
    OK  -> SET
    OT  -> MARK
    L   -> LINK
    alles andere -> UNKNOWN_HOST[ID]

RIGHT:
    AIIN -> ARG_AIIN
    AIN  -> ARG_AIN
    AL   -> ARG_AL
    AR   -> ARG_AR
    AIR  -> ARG_AIR

CONSTRUCTION:
    O-frame  -> FRAME_O(base)
    OT-frame -> FRAME_OT(base)
    inner-D  -> VARIANT_D(base)
    DY       -> CLOSE(base)
    B3       -> CLOSE_B3(base)

WRAPPER:
    sichtbare q/s- und ähnliche Rendererformen -> kein Bedeutungsbeitrag
```

Die RIGHT-, FRAME- und D-Namen halten nur formal verschiedene Klassen
auseinander. Sie sind keine Übersetzungen. Sicher inhaltlich interpretierbar
sind lediglich `CLOSE` und `CLOSE_B3` als bereits definierte formale
Abschlussoperationen; auch sie sagen nicht, welche reale Handlung abgeschlossen
wurde.

Kompositionsreihenfolge:

```text
HOST
→ optional VARIANT_D
→ optional RIGHT-Argument
→ optional FRAME
→ optional DY/B3-Schluss
```

## Wie längere Lesungen jetzt entstehen dürfen

Eine längere Lesung darf nur ein **stilles, inhaltlich unbekanntes Argument**
einsetzen, das Bild, Seite oder unmittelbarer Arbeitskontext bereitstellen.
Sie darf diesem Argument nicht nachträglich „Wasser“, „Wurzel“, „Becken“,
„Frühjahr“ oder „klar“ zuschreiben.

Beispiele:

```text
qokaiin -> SETZE <formal ausgewiesenes, inhaltlich unbekanntes Argument>
qotal   -> MARKIERE <formal ausgewiesenen, inhaltlich unbekannten Bezug>
oldy    -> VERKNÜPFE <lokalen unbekannten Anschluss>; SCHLIESSE DIE EINHEIT
otchor  -> <unbekannter Kartenwert CHOR> im FRAME_OT
dchey   -> <unbekannter Kartenwert CHEY>
orain   -> <unbekannter Kartenwert OR> + <ARG_AIN>
```

Damit ist jede Ausgabe vollständig, aber keine Lücke wird mit einer erfundenen
Satzbedeutung kaschiert.

## Vollständige Ausgabe

- `V49_R3_ATOMIC_COMPONENT_CONTRACT.tsv`: alle aktiven Hosts sowie sämtliche
  RIGHT-/FRAME-/D-/DY-/B3-Entscheidungen;
- `V49_R3_COMPLETE_173_ATOMIC_CARD_LEXICON.tsv`: alle 173 exakten Karten;
- `V49_R3_COMPLETE_381_ATOMIC_EVENT_EDITION.tsv`: alle 381 Prosavorkommen;
- `V49_R3_COMPLETE_135_ATOMIC_FIELD_EDITION.tsv`: alle 135 Prosafelder;
- `V49_R3_REJECTED_GLOSSES.tsv`: zurückgezogene Komponenten- und lokale
  Satzglossen;
- `V49_R3_VALIDATION.json`: Gleichheits-, Vollständigkeits- und Siegelchecks.

Die drei Astroseiten besitzen in diesem Panel keine GDT327-Ereignisse und
werden daher nicht künstlich in dieselbe Kartenübersetzung gepresst. Die
Arbeit bleibt eine kreative Zehnseiten-Werkstatttheorie, keine Entzifferung.
`f84` und `f84r` blieben versiegelt.
