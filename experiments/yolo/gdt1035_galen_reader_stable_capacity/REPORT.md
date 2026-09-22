# GDT1035 — der gemeinsame Galen-Code scheitert auch am exakt übereinstimmenden Teil

**Der Widerspruch aus1034 bleibt auf161 eindeutig zugeordneten exakten
ZL/IT-Wortpositionen erhalten.** Sämtliche acht tragenden chey-Vorkommen
qualifizieren: fünf in Familie A, drei in B. Kein unveränderter konservativer
Quellpool kann die fünf A-Verwendungen tragen; seine Obergrenze bleibt vier.
Andere unsichere Gruppen derselben Zeilen wegzulassen beseitigt diesen
Widerspruch also nicht. Dies gilt unter dem festen Quellinventar und dem
expliziten Korrespondenzmodell, nicht als paläographischer Wahrheitsbeweis.

Die zwei Transkriptionen sind Lesarten desselben Manuskripts, keine unabhängigen
Zeugen. Beide könnten gemeinsam falsch sein. Kein Bild wurde geprüft oder neu
zugelassen. Die semantische Kompatibilitätsübermenge aus1034 bleibt eine von
KI-Bearbeitern beurteilte Quellenannahme. Kein externer Mensch wurde kontaktiert.
**Bestätigte Wörter:0.** GDT1034 und seine zwei ursprünglichen Panelentscheidungen
wurden nicht verändert; hier liegt ein gesonderter registrierter Folgeversuch vor.

## Tatsächlich ausgeführte Konsequenzen

Öffentliches Lock vor dem vollständigen Alignmentlauf: `13248c485`.
Alle vier Absätze waren schon Entwicklungsmaterial, einschließlich ihrer
Alternativlesungen. Der bekannte chey-Widerspruch motivierte diesen Audit;
keine blinde Auswahl oder unabhängige Bedeutungsbestätigung wird behauptet.

| Festes Panel | Gezählte A/B-Positionen | Geteilte Worttypen | K | Quellmatching-Obergrenze | Leere Domains | Entscheidung |
|---|---:|---:|---:|---:|---|---|
| Alle wörtlichen a–z-Gruppen in ZL |94/86|13|20|21|chey|gemeinsamer Code widersprochen|
| Alle wörtlichen a–z-Gruppen in IT |98/87|13|21|21|aiin, al, chey|gemeinsamer Code widersprochen|
| Eindeutiger erzwungener gemeinsamer Teil |82/79|11|18|21|chey|gemeinsamer Code widersprochen|

Die Gesamtmatchinggrenze allein widerspricht in keinem Panel. Entscheidend
ist jeweils die notwendige konstante Denotation des wiederholten Wortes.
Für jedes Panel bleiben ALLE95 A- und88 B-Quellpositionen verfügbar, auch wenn
Zielpositionen ausgeschlossen sind. Nichtleere Domains sind nur notwendige
Möglichkeiten und noch keine gemeinsam realisierbare Wortkarte.

| Exakte Schreibung im gemeinsamen Teil | A | B | Notwendige mögliche B-Pools |
|---|---:|---:|---|
| aiin | 3 | 4 | BP04, BP20 |
| al | 4 | 1 | BP04, BP20 |
| chedy | 3 | 3 | BP04, BP20 |
| chey | 5 | 3 | **keiner** |
| daiin | 1 | 2 | BP02, BP04, BP13, BP16, BP17, BP19, BP20, BP22, BP44 |
| dal | 1 | 1 | BP02, BP04, BP06, BP13, BP14, BP16, BP17, BP19, BP20, BP22, BP41, BP44, BP45, BP46 |
| or | 1 | 1 | BP02, BP04, BP06, BP13, BP14, BP16, BP17, BP19, BP20, BP22, BP41, BP44, BP45, BP46 |
| qokeedy | 1 | 1 | BP02, BP04, BP06, BP13, BP14, BP16, BP17, BP19, BP20, BP22, BP41, BP44, BP45, BP46 |
| qokey | 3 | 1 | BP02, BP04, BP20, BP46 |
| qoky | 2 | 3 | BP04, BP19, BP20 |
| shedy | 1 | 6 | BP13, BP19 |

Das sind alle elf geteilten Wörter des gemeinsamen Panels. Die vollständige
[CSV](artifacts/CANDIDATES.csv) und [JSON-Tabelle](artifacts/CANDIDATES.json)
enthalten sämtliche Wörter aller drei Panels samt Nullhäufigkeiten. Namen der
Quellpools sind keine Übersetzungen dieser Schreibungen. Alle46 Poolkapazitäten
und ihre Begrenzung bleiben exakt wie in
[GDT1034](../gdt1034_galen_shared_code_capacity/artifacts/WORD_DOMAINS.json).

## Die acht tragenden Vorkommen vollständig

| ZL-Position | Einziger erzwungener IT-Partner | Ganze ZL-Zeile eindeutig markiert | Ganze IT-Zeile eindeutig markiert |
|---|---|---|---|
| ZL3b|f107v.46|G003 | IT2a|f107v.46|G003 | True | True |
| ZL3b|f107v.48|G005 | IT2a|f107v.48|G005 | False | True |
| ZL3b|f107v.48|G009 | IT2a|f107v.48|G009 | False | True |
| ZL3b|f107v.49|G003 | IT2a|f107v.49|G004 | False | True |
| ZL3b|f111r.46|G007 | IT2a|f111r.46|G007 | False | True |
| ZL3b|f76v.38|G008 | IT2a|f76v.38|G007 | False | True |
| ZL3b|f76v.40|G006 | IT2a|f76v.40|G006 | False | True |
| ZL3b|f80v.22|G004 | IT2a|f80v.22|G004 | True | True |

Sechs dieser ZL-Zeilen waren als ganze Zeilen unsicher markiert. Dennoch
sind die jeweiligen chey-Gruppen unter ALLEN maximalen exakten Wortalignments
verpflichtend und jeweils einem einzigen IT-Partner zugeordnet. Alle acht
zugehörigen IT-Zeilen tragen anchor_eligible=True. Die alten ZL-Ganzzeilenflags
bleiben unverändert erhalten; kein Zeichen, Abstand oder Unsicherheitsflag
wurde nachträglich repariert.

Der neue gemeinsame Teil umfasst161 von183 ZL-Positionen. Die22 ausgeschlossenen
Positionen sind in [ALIGNMENTS.json](artifacts/ALIGNMENTS.json) mit allen möglichen
Partnern, obligatorischer/optionaler Rolle und Rohform-Literalität vollständig
aufgeführt. [SCOPE.json](artifacts/SCOPE.json) erhält beide ganzen Fassungen der
vier Absätze mit sämtlichen Zeilen, Gruppen, IDs und Flags. RF1b ist in diesem
festen GDT928-Paket nicht verfügbar und wurde weder nachbeschafft noch als
Zustimmung behandelt. Es wurden nicht nur chey-Zeilen ausgewertet.

## Forschungsentscheidung und verbleibende Möglichkeiten

Die gemeinsame183-Slot-Galen-Inventarhypothese wird nicht durch Auswahl einer
anderen gespeicherten Wortkarte oder Ausschluss der übrigen unsicheren Gruppen
fortgesetzt. Der konkrete Wiederholungswiderspruch liegt bereits im erhaltenen
exakten gemeinsamen Teil. Eine neue Gesamtlesung müsste einen tatsächlich
anderen, vorab begründeten Inhalts-/Schreibvertrag liefern; bloße Kontextausnahmen
oder neue Quellatome zur Rettung dieses Resultats folgen daraus nicht.

Offen bleiben die getrennten örtlichen Entwürfe, andere Inhalte und
kompositionelle oder kontextabhängige Schreibweisen. Auch die Richtigkeit der
übereinstimmenden Transkriptionen bleibt unbewiesen. Weder eine allgemeine
Galen-Widerlegung noch ein Beweis kontextabhängiger Voynich-Bedeutung folgt.
Keine Pflanzenbezeichnung wurde bestätigt. Unabhängige Bedeutungsprüfkapazität0;
keine Gegenkontrolle der gesamten Suche und keine Signifikanzbehauptung.

## Validierung und Aufwand

[VALIDATION.json](artifacts/VALIDATION.json): vollständige unabhängige Rekonstruktion
aller183 Alignmentpositionen, drei Panels, sämtlicher Domains, CSV und fünf
Resultatartefakte PASS. Der Validator las/importierte keinen Primärcode und
berechnet Pflichtkanten und Pflichtpositionen als Schnittmengen über alle
optimalen DP-Zweige; das Primärprogramm nutzt Präfix-/Suffix-LCS und Löschung.
Je225 vollständig exhaustive synthetische Zeichenfolgenpaare und zusätzliche
Mehrdeutigkeits-/Unsicherheitsfixtures prüfen die unterschiedliche Umsetzung.
12 neue Lockbindungen, sechs direkte Inputs und17 alte Lockbindungen geprüft.
Dies bestätigt Berechnung und Bytebindung, keine historischen Bedeutungen.

Vorbereitung begann12:13UTC; Lauf und unabhängige Prüfung abgeschlossen12:24UTC.
Das Gesamtbudget bis12:38UTC schließt Veröffentlichung ein. f84/f84r, f116v und
Reserven bleiben geschlossen. Keine Quelle, Glosse, Kompatibilitätskante,
Poolgrenze oder ursprüngliche Transkriptionsregel verändert.

```sh
python experiments/yolo/gdt1035_galen_reader_stable_capacity/src/run.py
python experiments/yolo/gdt1035_galen_reader_stable_capacity/src/validate.py --execute
```
