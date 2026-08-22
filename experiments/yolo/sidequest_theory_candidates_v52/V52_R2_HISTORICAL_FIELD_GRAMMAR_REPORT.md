# V52 R2 — Historischer Drucktest der Feldgrammatik

## Ergebnis

Die ausgewählten V50-Atome und V51-Ganzkarten lassen sich **nur zu einer schwachen parataktischen Feldnotation**, nicht zu einer historisch lesbaren Satz- oder Rezeptklauselgrammatik komponieren.

Der schmale positive Befund lautet:

```text
FELD := KARTE{1..11}
GESCHLOSSEN(FELD) := die letzte Karte trägt die formale CLOSE-Koordinate
KARTE := opake Ganzkarte
       | Karte mit ausgewähltem PAGE_HOST-Merkwert
       | eine der neun ausgewählten exakten Ganzkarten
```

Die Karten stehen in beobachteter Reihenfolge; daraus folgt weder Konjunktion noch Prädikat–Argument-Bindung. `CLOSE` liegt in allen 90 geschlossenen Feldern ausschließlich auf der letzten Karte. Das ist ein belastbarer terminaler Feldbau, aber kein Wort *beenden*. Eine Zeile beziehungsweise ein Feld ist kein Satz.

## Vollständiger Audit

Geprüft wurden alle 135 festen Felder und alle darin enthaltenen 381 Ereignisse der freigegebenen V49-Tabellen. Die Seitenkontrolle ergibt f10r 5, f11r 4, f55v 4, f56r 7, f81v 24, f82r 26 und f83r 65 Felder, zusammen 135. Die Feldlängen sind:

| Karten pro Feld | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Felder | 53 | 20 | 17 | 22 | 10 | 3 | 5 | 2 | 1 | 1 | 1 |

Für die Klassifikation zählen als positive Host-/Rahmenwerte `OK=SET`, `OT=MARK`, `L=LINK`, `AL=AN?`, `OR=BEREITUNG?` und `CHEY=TEIL?`; `E` bleibt unbekannt. Positive exakte Ganzkarten sind `AIIN=MASS?`, `EY=KLAR?`, `OKY=VERWENDEN?`, `LCHE=ABLASSEN?`, `OKE=SPÜLEN?`, `CTHY=BEREIT?`, `OKEEY=WARM?` und `OLOR=ZUVOR?`; `CKHY` bleibt unbekannt. Die V49-Werte wurden nur zur Lokalisierung benutzt und dann durch die V50/V51-Auswahl ersetzt.

Wichtig: Ein exakter Ganzkartenwert wird **nicht** in eine andere Karte hineinkopiert. `<ARG_AIIN>` in `SET(<ARG_AIIN>)` ist daher nicht `MASS?`; `EY` liefert keinen freien Wert für `E` oder `-ey`; `OKY` ist nicht `OK+Y`; `OKE` ist nicht `OK+E`. Ebenso gilt ein PAGE_HOST-Merkwert nur am PAGE_HOST, nicht an ähnlich geschriebenen Argumenttags oder Substrings.

## Fünf erschöpfende Quellfeldtypen

Die fünf Typen sind disjunkt und summieren sich zu 135 Feldern beziehungsweise 381 Ereignissen.

| Typ | Regel | Felder | Ereignisse | geschlossen | Herbal | Bio |
|---|---|---:|---:|---:|---:|---:|
| Q1 OFFEN_OPAK | kein positiver Host-/Ganzkartenwert, kein `CLOSE` | 8 | 16 | 0 | 4 | 4 |
| Q2 TERMINAL_OPAK | kein positiver Host-/Ganzkartenwert, aber finales `CLOSE` | 44 | 57 | 44 | 0 | 44 |
| Q3 HOST_RAHMEN | mindestens ein positiver Host-/Rahmenwert, keine positive Ganzkarte | 33 | 107 | 19 | 2 | 31 |
| Q4 GANZKARTE | mindestens eine positive exakte Ganzkarte, kein positiver Host-/Rahmenwert | 26 | 72 | 18 | 6 | 20 |
| Q5 GEMISCHT_PARATAKTISCH | mindestens je ein positiver Host-/Rahmen- und Ganzkartenwert | 24 | 129 | 9 | 8 | 16 |

### Q1 OFFEN_OPAK — vollständiges Beispiel

```text
Feld:       f11r.1, Feld 2 (Herbal)
Quelle:     shoyty
Formal:     UNKNOWN_HOST[OYTY]
V49-Prosa:  behalte die Blütenkrone zurück
V52-R2:     UNKNOWN
```

Historisch kann ein kurzer Eintrag eine Überschrift, ein *Item*, eine Zutat oder eine ganze gelernte Notiz sein. Ohne lesbare Sprache lässt sich zwischen diesen Größen nicht wählen. Die Formgröße ist plausibel; die Blütenkrone und der Imperativ sind es als Ableitung aus dieser Karte nicht.

### Q2 TERMINAL_OPAK — vollständiges Beispiel

```text
Feld:       f83r.14, Feld 1 (Bio)
Quelle:     qokchedy
Formal:     CLOSE(UNKNOWN_HOST[OKCHE])
V49-Prosa:  lasse es abkühlen und beende den Schritt
V52-R2:     UNKNOWN {formal terminal}
```

Ein finales Zeichen oder eine gelernte Schlussformel ist handschriftlich denkbar. Der einzige hier wiederholte Befund ist jedoch die Endstellung: Er lizenziert weder *abkühlen* noch ein ausgesprochenes *beende den Schritt*. 86 der 90 `CLOSE`-Felder schmuggeln genau solches Beendigungsdeutsch in die V49-Prosa zurück.

### Q3 HOST_RAHMEN — vollständiges Beispiel

```text
Feld:       f83r.3, Feld 2 (Bio)
Quelle:     qotal chkeedy
Formal:     MARK(<ARG_AL>) | CLOSE(UNKNOWN_HOST[KEE])
V49-Prosa:  zum unteren Ablauf hin ; tauche vollständig ein und beende den Schritt
V52-R2:     MARK(<ARG_AL>) | UNKNOWN {formal terminal}
```

Markier-, Setz- und Verknüpfungszeichen passen von der historischen Größe her zu Randzeichen, Rezeptkürzeln und apothekarischen Siglen. Das Argumenttag `<ARG_AL>` ist aber keine lesbare Zielangabe. *Unterer Ablauf*, *eintauchen* und das Objekt sind ungestützt.

### Q4 GANZKARTE — vollständiges Beispiel

```text
Feld:       f83r.20, Feld 5 (Bio)
Quelle:     qoky saiin
Exakte IDs: OKY | AIIN
V49-Prosa:  Die aktive Portion verwenden ; Ein vorgeschriebenes Maß
V52-R2:     VERWENDEN? | MASS?
```

Gelernte Ganzzeichen für `Recipe`, Gewichte, Maße oder wiederkehrende Arbeitswörter sind historisch plausibel. Trotzdem bilden zwei Merkwörter noch keine Klausel: Das Feld nennt weder aktive Portion, Vorschrift, Einheit, Objekt noch grammatische Beziehung zwischen `VERWENDEN?` und `MASS?`.

### Q5 GEMISCHT_PARATAKTISCH — vollständiges Beispiel

```text
Feld:       f83r.26, Feld 1 (Bio)
Quelle:     otchey qokeey qoky tol shedy
Formal:     FRAME_OT(UNKNOWN_HOST[CHEY]) | UNKNOWN_HOST[OKEEY] |
            UNKNOWN_HOST[OKY] | FRAME_O(LINK) | CLOSE(UNKNOWN_HOST[E])
V49-Prosa:  Nimm den bezeichneten Anteil ; temperiere die Arbeitsflüssigkeit
            und halte sie lauwarm ; Die aktive Portion verwenden ; Mit der
            vorigen Zubereitung weiter ; lasse es bis zur Bereitschaft stehen
            und beende den Schritt
V52-R2:     FRAME_OT(TEIL?) | WARM? | VERWENDEN? | FRAME_O(LINK) |
            UNKNOWN {formal terminal}
```

Dies ist der stärkste denkbare Kompositionsfall, bleibt aber eine Kartenfolge. Unter den 24 gemischten Feldern gibt es 22 verschiedene vollständige `H/W/U`-Folgen (`H` Host, `W` Ganzkarte, `U` unbekannt); selbst nach Entfernung aller `U` bleiben zehn positive Reihenfolgen. Nur `HW` kommt häufiger vor (9/24). Es gibt daher keine stabile Quellordnung, aus der Subjekt, Verb, Objekt oder Rezeptslot ablesbar wäre.

Ein Herbal-Beispiel zeigt dieselbe Grenze mit anderer Ausprägung:

```text
f10r.8/1:
FRAME_OT(UNKNOWN) | BEREITUNG? | FRAME_OT(UNKNOWN) | FRAME_O(LINK) |
ZUVOR? | FRAME_O(LINK) | MASS? | UNKNOWN
```

Die V49-Fassung füllte daraus Blüte, Arbeitsflüssigkeit, Handvoll, vorigen Ansatz und Entnahmehandlung auf. Nichts davon steckt in der ausgewählten atomaren Folge.

## Herbal und Bio

Die unterschiedliche Verteilung darf als panelbedingte Ausprägung stehen, nicht als Semantikbeweis:

| Panel | Q1 | Q2 | Q3 | Q4 | Q5 | Gesamt |
|---|---:|---:|---:|---:|---:|---:|
| Herbal: f10r, f11r, f55v, f56r | 4 (20%) | 0 | 2 (10%) | 6 (30%) | 8 (40%) | 20 |
| Bio: f81v, f82r, f83r | 4 (3.5%) | 44 (38.3%) | 31 (27.0%) | 20 (17.4%) | 16 (13.9%) | 115 |

Alle 20 Herbal-Felder und 98/115 Bio-Felder enthalten nach der Auswahl mindestens eine unbekannte Karte. Nur 17/135 Felder bestehen vollständig aus positiv ausgewählten Merkwerten; alle 17 liegen im Bio-Panel. Auch diese 17 sind keine Sätze, sondern höchstens vollständig annotierte Kartenfolgen.

## Historische Analogien und Gegenproben

1. **Explizite Rezeptsyntax.** Eine deutsche Rezeptsammlung um 1463 reiht Imperative mit ausgesprochenen Gegenständen und Bindern wie `vnd`, `dar nach` und `vncz`/`byss`. Das zeigt eine plausible parataktische Rezeptgrammatik, aber zugleich, wie viel Syntax und Referenz in den V52-Karten fehlt. Die digitale Edition weist außerdem darauf hin, dass Abkürzungen editorisch aufgelöst und moderne Interpunktion ergänzt wurden; moderne Lesbarkeit darf daher nicht rückwärts in die Quelle projiziert werden. [HAB, Cod. germ. 1, Transkription](https://diglib.hab.de/edoc/ed000270/texts/tei-transcription.html)
2. **Standardisierte Rezeptbestandteile.** Die 360 mit `Rx` markierten Rezepte der spätmittelalterlichen *Lylye of Medicynes* beginnen in einem wiederkehrenden Format mit Arzneityp und Krankheitsphase, dann folgen Zutaten, häufig Mengen und Zubereitungsschritte. Diese historische Slotstruktur ist real, doch keine V52-Karte identifiziert hier unabhängig einen solchen Slot. Dass historische Texte Fachwissen gelegentlich voraussetzen, ist keine Erlaubnis, fehlende Voynich-Objekte zu erfinden. [Connelly et al., 2020](https://journals.asm.org/doi/10.1128/mbio.03136-19)
3. **Siglen und Maße.** In spätmittelalterlichen medizinischen Sammelhandschriften konnten Apothekerzeichen Gewichte wie Skrupel oder Drachme vertreten. Das macht `MASS?` als Ganzkarten-Merkwort größenplausibel, aber nicht `Ein vorgeschriebenes Maß` und keine bestimmte Einheit. [Journal of British Studies, practical miscellanies](https://www.cambridge.org/core/journals/journal-of-british-studies/article/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12/share/a024150fe1501e59df5b45628147fdd3df550196)
4. **Kurze Querverweise.** Dieselbe Studie dokumentiert knappe Folgetitel wie `Alia modo` und `For the same`. Das ist eine gute Größenanalogie für `ZUVOR?`, nicht aber ein Beleg für einen unsichtbaren vorigen Ansatz.
5. **Schreibergebundene Abbreviatur.** Mittelalterliche Kürzungssysteme waren nicht einheitlich, sondern regional und schreiberabhängig. Daher sind gelernte Ganzzeichen möglich; gerade deshalb darf Formähnlichkeit nicht als freie Segmentierung behandelt werden. [Ad fontes, “Abbreviations”](https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/abkuerzungen)

## Quantitative Grenze der Komposition

- Nur 145/381 Ereignisse tragen nach V50/V51 überhaupt einen positiven ausgewählten Wert; 236 bleiben unbekannt.
- 118/135 Felder enthalten mindestens eine unbekannte Karte.
- 52/135 Felder besitzen gar keinen positiven ausgewählten Host- oder Ganzkartenwert; bei 44 davon ist lediglich die terminale `CLOSE`-Position bekannt.
- Nur 24/135 Felder enthalten beide Klassen und testen deshalb echte Host–Ganzkarten-Komposition. Ihre Reihenfolgen liefern kein wiederholtes Klauselschema.
- Der einzige feldweite feste Bau ist `CLOSE` auf der letzten Karte. Dieser Befund ist strukturell, nicht lexikalisch.

## Reparaturprinzip

Jede V49-Satzphrase wird auf die tatsächlich ausgewählte Annotation zurückgeschnitten:

```text
SET(<ARG_X>)         nicht: beginne/gib/mische/öffne X
MARK(<ARG_X>)        nicht: gleiche Dauer/unterer Ablauf/örtliche Stelle
LINK mit Frames      nicht: vorige Zubereitung/Öl/Abziehen/Kochen
AN?                  nicht: an die bezeichnete Zielstelle führen
MASS?                nicht: ein vorgeschriebenes Maß einer stillen Substanz
WARM?                nicht: Flüssigkeit temperieren und lauwarm halten
UNKNOWN {CLOSE}      nicht: warten/abkühlen/kochen und den Schritt beenden
```

Die konkreten atomweisen Korrekturen und ihre Reichweite stehen in `V52_R2_REPAIRS.tsv`. Der Befund bleibt eine kreative, historisch maßstäbliche Werkstattnotation. Er identifiziert kein Quellwort, keine natürliche Sprache und keine übersetzte Klausel.

## Zugriffsschutz

Es wurden keine V52-Geschwisterdateien, keine weiteren Seiten und kein `f84`/`f84r` geöffnet. Es erfolgte kein Commit und kein Push.
