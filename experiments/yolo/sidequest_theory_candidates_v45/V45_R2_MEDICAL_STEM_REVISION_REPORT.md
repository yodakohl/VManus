# V45 R2 — medizinische Stammrevision der vollständigen Zehnseiten-Edition

## Urteil

Die V43-Übersetzung wird als Werkstatttext wesentlich konsistenter, wenn jede
lange deutsche Karte in drei Schichten gelesen wird:

```text
stabiler minimaler Stammwert
+ exakte formale Kartenkompletierung
+ lokale Ergänzung aus Bild, Record und laufendem Verfahren
```

Das ist keine gewöhnliche Lautmorphologie. Ein Stamm kann hier ein gelerntes
Sigel, eine Suspensionskarte oder eine Formularfunktion sein. Der Lehrling muss
nicht hinter jedem sichtbaren Zeichen eine Silbe hören. Er lernt einen kleinen
Kern, eine Tabelle zulässiger Ganzkarten und die lokale Ergänzungsroutine.

Die vollständige Revision umfasst **173 exakte Prosakarten und alle 381
Vorkommen**. 41 Karten mussten sprachlich umformuliert werden, damit ihr
Minimalstamm nicht mehr zwischen verschiedenen Bedeutungen wandert. Die
übrigen lokalen Expansionen bleiben bestehen, sind nun aber entweder einem
stabilen Stamm oder ausdrücklich einem unzerlegten Ganzkartenkern
untergeordnet.

## Gemeinsame Lehre für die wichtigsten Stämme

| Einheit | Stabiler Minimalwert | Was erst lokal ergänzt wird |
|---|---|---|
| `AIIN` | vorgeschriebener/standardisierter Wert | Gewicht, Volumen, Anzahl oder Dauer |
| `OR` | bereitetes verwendbares Ergebnis | Flüssigkeit, Sud, Arznei, frischer Gebrauch |
| `CHOR` | Beschaffung in einem Zeitfenster | Frühjahr, vor der Blüte, gezeigter Pflanzenteil |
| `CHEY` | bestimmten Materialteil auswählen | Wurzel, Anteil, unterer oder markierter Teil |
| `OK` | spezifizierten Arbeitsposten aktivieren | zugeben, mischen, öffnen, anwenden, beginnen |
| `OT` | markierten Gegen-/Bezugsplatz wählen | vorherige Dauer, unterer Ablauf, Folgeweg |
| `L` | kontextuell angeschlossene Station wählen | Voransatz, Nachlauf, Empfänger, Abführung |
| `E` | Vorgang bis zu einem Sollzustand führen | Bereitschaft oder Klarheit |
| `EY` | verlangten sichtbaren Prüfzustand erreichen | im lokalen Abflussrecord: klarer Lauf |
| `DY` | Handlung vollziehen und Zelle schließen | die konkrete Handlung der vollständigen Karte |
| `Y` | gegenwärtigen Träger wiederaufnehmen | Stoff, Anteil oder Bildbesitzer |
| `AL` | bezeichnete Ziel-/Parallelstation | Zielstelle oder zweite Öffnung |

`DY` ist dabei kein PAGE_HOST und nicht einfach ein gesprochenes Suffix. Es ist
eine formale Schlussrealisation in 89 der 381 Ereignisse. Die Karten vor diesem
Schluss liefern die Handlung; `DY` liefert höchstens Vollzug und lokalen
Abschluss.

## Die wichtigsten Reparaturen

### `EY` wird kurz

Alt:

```text
cheey/sheey = bis die Flüssigkeit klar abläuft
```

Neu:

```text
EY = verlangten beobachtbaren Endzustand erreichen
lokale Expansion auf f11r = bis der laufende Abfluss klar/frei ist
```

`Flüssigkeit`, `Ablauf` und `Klarheit` stammen nicht alle aus `EY`. Der
Verfahrenskontext liefert sie. Sichtbares `chey` ist weiterhin der Host `y`,
nicht `ey`.

### `OK` wird nicht mehr fünf verschiedene Verben

Alle fünf Karten behalten denselben Kopf **AKTIVIERE DEN ARBEITSPOSTEN**:

```text
OK + AIN   -> aktiviere die Zugabe eines vorgeschriebenen Anteils
OK + AL    -> aktiviere das Zusammenführen der bezeichneten Anteile
OK + AR    -> aktiviere den Schritt an der bezeichneten Stelle
OK + AIR   -> aktiviere als Nächstes den oberen Lauf
OK + AIIN  -> aktiviere den nächsten quantifizierten Posten
```

Die Kompletierung entscheidet, was ausgeführt wird. `OK` selbst heißt weder
Wasser noch mischen noch nehmen.

### `L` wird relationell statt gegenständlich

Die frühere Sammlung „Öl / Voransatz / Abziehen / Kochen / unterer Ablauf“
kann kein gemeinsames Inhaltswort sein. Als Anschlussachse ist sie lehrbar:

```text
L = wähle die im lokalen Record angeschlossene Station
```

Die Station kann rückwärts der Voransatz, vorwärts der Nachlauf oder räumlich
der Empfänger sein. Das ist breit, aber stabiler als `L = Flüssigkeit` oder
`L = unten`. Der historische Schreiber ergänzt die Relationsrichtung aus dem
Formularplatz.

### `Y` bleibt nur als deiktischer Träger

Die drei Karten werden nicht mehr als „aktive Portion / Rühren / Habitat“ drei
freien Bedeutungen zugewiesen. Der minimale gemeinsame Wert lautet
**gegenwärtiger Träger**:

- die reine Y-Karte bezeichnet den geführten Stoff/Anteil;
- die geschlossene Y-Karte bearbeitet diesen Stoff gleichmäßig;
- die Habitatkarte macht den aktuellen Bildbesitzer zum Gegenstand der
  Standortangabe.

Das ist weiterhin schwächer als AIIN, OR oder OK. Falls diese Deixis in einer
späteren Runde mehr Ausnahmen erzeugt, müssen die Y-Karten wieder als
Ganzkarten getrennt werden.

## Wie die Übersetzung jetzt gelesen werden soll

Ein Interlinearereignis wie `qokaiin` erhält nicht mehr die unanalysierte
Satzbedeutung „beginne den nächsten abgemessenen Posten“. Es wird notiert als:

```text
Stamm:       OK = Arbeitsposten aktivieren
Kompletion:  exakte AIIN-bezogene Karte
Lokal:       aktiviere den nächsten quantifizierten Arbeitsposten
```

Ebenso:

```text
otchor
Stamm:       CHOR = Beschaffung in einem Zeitfenster
Kompletion:  markierter zeitlicher Bezug
Lokal:       beschaffe den Bildbesitzer vor der Blüte
```

und:

```text
dchdy
Stamm:       CH = flüssigen Bestand trennen
Kompletion:  klare Trennung + DY-Schluss
Lokal:       seihe klar und schließe den Schritt
```

Die lokale deutsche Fassung darf daher länger als die sichtbare Karte sein,
aber sie darf den Minimalstamm nicht neu definieren.

## Was bewusst unzerlegt bleibt

Für die meisten seltenen Hosts gibt das feste Panel kein echtes Paradigma her.
Sie stehen im vollständigen Lexikon als `WHOLE_CARD_*`. Das ist kein
Ausweichen, sondern die historisch einfachere Lösung: häufige Kürzungen werden
regelhaft gelernt, seltene Fachwerte aus Exemplaren kopiert. Besonders
ähnliche Oberflächen dürfen nicht gegen die formale PAGE_HOST-Zuordnung
zusammengezogen werden.

Die frühere R2-Idee eines sichtbaren `OL = Vorquelle` wird dabei korrigiert:
die häufige Voransatzkarte liegt formal im PAGE_HOST `l`; der PAGE_HOST `ol`
des festen Panels ist die einzelne Handvollkarte. Sichtbare Buchstabenfolge und
formaler Host sind nicht dasselbe Analyseobjekt.

Dasselbe gilt für `AIN`: PAGE_HOST `aiin` trägt im festen Panel die starke
Maßkarte. PAGE_HOST `ain` ist hier dagegen nur die Karte `dain = durch ein
Tuch` und wird nicht in die Mengenfamilie gezwungen. Ähnlichkeit der sichtbaren
Folge reicht nicht für einen gemeinsamen Stamm.

## Historische Plausibilität

Der Mechanismus passt zu einer Werkstatt um 1420 besser als 173 frei
ausgeschriebene Mikrosätze: Suspensionen, Kontraktionen, Brevigrafen,
Rezeptzeichen und kontextabhängige Ergänzungen erlauben kurze, organisch
unregelmäßige Karten. Die historische Parallele stützt nur den Mechanismus,
nicht die konkreten Voynichwerte. Die bereits in V44 dokumentierten
Vergleichspunkte bleiben maßgeblich: die Abbreviaturübersicht der Library of
Congress, die hyperdiplomatische CoReMA-Editionspraxis und die mittelalterliche
medizinische Maßtabelle der National Library of Medicine.

## Astro bleibt separat

`f67r2`, `f68r1` und `f69v` bleiben unverändert im lokalen WHEN-/Diagrammraum.
Sie besitzen in dieser Sidequest keine GDT327-Prosaereignisse. Deshalb wurden
keine Prosastämme auf die 395 Astro-Labels übertragen und keine Astro-Lesung
aus AIIN/OR/OK/L/EY abgeleitet.

## Artefakte und Grenze

- `V45_R2_STEM_LEXICON.tsv`: die gemeinsame Stammlehre;
- `V45_R2_REVISED_173_CARD_LEXICON.tsv`: jede exakte Karte mit Stamm,
  Kompletierung und lokaler Expansion;
- `V45_R2_REVISED_381_EVENT_INTERLINEAR.tsv`: jedes feste Prosaereignis in
  Manuskriptreihenfolge;
- `V45_R2_VALIDATION.json`: Abdeckung und Versiegelung.

Dies bleibt eine kreative Übersetzungsrevision, keine Entzifferung. Es wurden
keine zusätzlichen Seiten und insbesondere weder `f84` noch `f84r` geöffnet.
