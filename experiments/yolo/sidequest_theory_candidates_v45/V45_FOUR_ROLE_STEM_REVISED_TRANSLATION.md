# V45 — vollständige Übersetzung auf gemeinsame Stämme revidiert

## Auswahl

Alle vier Rollen lieferten vollständige Fassungen mit 173 Prosakarten und 381
Ereignissen. Als neue Basis wird gewählt:

```text
R2 konservative medizinische Stammrevision
+ R1 vollständiges Inventar aller 136 PAGE_HOSTs
+ R3 unveränderte 395 Astro-Labels
+ R4 unabhängiger Vollständigkeitsabgleich
```

R3 zeigt, dass sich bis zu 73 Karten in eine weit gefasste Registeralgebra
einordnen lassen. Seine großen Anfangsachsen `A/C/E/K/O/...` sind jedoch zu
leicht mit bloßer Formähnlichkeit zu verwechseln. Sie werden nicht als
Wortstämme in die ausgewählte Übersetzung übernommen.

## Neue Übersetzungsregel

Jede Prosakarte wird ab jetzt so gelesen:

```text
STABILER STAMM ODER FORMALE ACHSE
+ EXAKTE KOMPLETIERUNG/KOORDINATE
+ LOKALES STILLES ARGUMENT
= KONKRETE DEUTSCHE EXPANSION
```

Die konkrete Expansion bleibt vollständig. Aber sie darf den Minimalwert des
gemeinsamen Stamms nicht mehr von Karte zu Karte wechseln.

## Ausgewählte gemeinsame Kerne

| Kern | unveränderlicher Minimalwert | Beispiel lokaler Expansion |
|---|---|---|
| `AIIN` | vorgeschriebener/standardisierter Wert | ein Maß, eine Dauer oder ein quantifizierter Posten |
| `OR` | bereitetes verwendbares Ergebnis | Arbeitsflüssigkeit oder frischer fertiger Ansatz |
| `CHOR` | Beschaffung in einem Zeitfenster | vor der Blüte oder im Frühjahr sammeln |
| `CHEY` | bestimmten Materialteil auswählen | untere Wurzel oder bezeichneten Anteil wählen |
| `OK` | spezifizierten Arbeitsposten aktivieren | Anteil zugeben, Anteile vereinen, Lauf öffnen |
| `OT` | markierten Gegen-/Bezugsplatz wählen | vorige Dauer, unterer Ablauf oder Folgeweg |
| `L` | angeschlossenen Vorgänger, Nachfolger oder Empfänger wählen | Voransatz, Nachlauf oder unterer Empfänger |
| `E` | Vorgang bis zum Sollzustand führen | Bereitschaft oder Klarheit |
| `EY` | verlangten beobachtbaren Endzustand erreichen | im Nassrecord bis zum klaren/freien Lauf |
| `Y` | gegenwärtigen Träger wiederaufnehmen | aktueller Stoff; im Habitatfeld der Bildbesitzer |
| `AL` | Ziel-/Parallelstation | bezeichnete Stelle oder zweite Öffnung |
| `AR` | bereits eingeführte Quelle | daraus/aus demselben Ansatz |
| `DY` | lokale Handlung vollziehen und Zelle schließen | konkrete Handlung kommt aus der ganzen Karte |

`Y` und `L` bleiben schwächer als `AIIN`, `OR` und `OK`. Sie werden als
deiktische bzw. relationale Achsen verwendet, nicht als konkrete Wörter für
„Gegenstand“ oder „Flüssigkeit“.

## 41 tatsächlich geänderte Karten

Die ausgewählte Edition formuliert 41 der 173 Ganzkarten neu. Die wichtigsten
Reparaturen sind:

```text
qokaiin
ALT: beginne den nächsten abgemessenen Posten
NEU: aktiviere den nächsten quantifizierten Arbeitsposten
     OK = aktivieren; AIIN-Kompletierung = Standardwert

chor / or / shor / sor
ALT: die bereitete Arbeitsflüssigkeit
NEU: das bereitete verwendbare Ergebnis des aktiven Ansatzes
     OR bleibt auch außerhalb eines Flüssigkeitsglosses stabil

cheey / shey
ALT: bis die Flüssigkeit klar abläuft
NEU: führe den Vorgang bis zum verlangten sichtbaren Endzustand
     „klarer Lauf“ bleibt nur die lokale Nassprozess-Expansion

cheol / chol / ol / qol / sol / tol
ALT: mit der vorigen Zubereitung weiter
NEU: knüpfe an den bereits eingeführten Ansatz an
     PAGE_HOST L = Anschluss; sichtbares OL ist nicht Host OL

chdy / chedy
ALT: rühre, bis alles gleichmäßig vermischt ist
NEU: bearbeite den aktuellen Stoff gleichmäßig und schließe den Schritt
     Y = gegenwärtiger Träger; INNER-D/DY spezifizieren Bearbeitung und Schluss
```

Alle 41 Vorher-/Nachher-Werte stehen im ausgewählten 173-Kartenlexikon.

## Zwei notwendige Trennungen

### `AIIN` ist nicht `AIN`

PAGE_HOST `aiin` trägt die starke Maßkarte. PAGE_HOST `ain` erscheint im
festen Panel als `dain`, lokal „durch ein Tuch“. Sichtbare Ähnlichkeit reicht
nicht, um beide zu einem Mengenstamm zu verschmelzen.

### sichtbares `OL` ist nicht PAGE_HOST `ol`

Die häufige Voransatzkarte `ol/chol/qol/...` liegt formal im PAGE_HOST `l`.
PAGE_HOST `ol` ist im festen Panel dagegen die einzelne Handvollkarte. Die
ausgewählte Edition folgt der formalen Hostidentität, nicht der bloßen
Oberflächenzerlegung.

## Wie vollständig ist die Stammübersetzung?

- 136/136 PAGE_HOSTs besitzen einen expliziten Minimalwert;
- 173/173 Prosakarten besitzen Stamm/Achse, formale Ergänzung und konkrete
  deutsche Expansion;
- 381/381 Prosavorkommen sind interlinear vollständig;
- 41 Karten wurden wirklich zur gemeinsamen Stammlesung umformuliert;
- seltene Hosts bleiben konkrete memorierte Ganzkarten statt erfundener
  produktiver Stämme;
- 395 Astro-Labels bleiben im getrennten lokalen Diagrammnamensraum
  unverändert.

Damit ist die Übersetzung jetzt **stammtransparent**, aber nicht vollständig
aus wenigen Stämmen generierbar. Das wäre eine falsche Glättung: Ein
historisch gewachsenes Werkstattsystem darf produktive Kerne und memorierte
Ausnahmen zugleich besitzen.

## Neue Basis

Die autoritative kreative Sidequest-Basis ist nun:

- `V45_SELECTED_COMMON_STEM_LEXICON.tsv` — alle 136 Hostkerne;
- `V45_SELECTED_REVISED_173_CARD_LEXICON.tsv` — vollständiges Kartenwörterbuch;
- `V45_SELECTED_REVISED_381_EVENT_INTERLINEAR.tsv` — vollständige Prosa;
- `V45_SELECTED_ASTRO_395_LABELS_UNCHANGED.tsv` — Astro separat;
- `V45_SELECTED_VALIDATION.json` — Abdeckung und Konsistenz.

## Grenze

Dies ist eine konkrete kreative Revision der zehn Seiten, keine Entzifferung.
Die gemeinsamen Werte sind Werkstatthypothesen, keine nachgewiesenen Wörter,
Morpheme, Laute oder historische Bedeutungen. `f84` und `f84r` blieben
vollständig versiegelt.
