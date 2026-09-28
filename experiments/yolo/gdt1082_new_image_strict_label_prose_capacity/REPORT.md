# GDT1082 — kein neuer eindeutig gebundener Label/Text-Träger

**Registrierte Entscheidung: `NO_NEW_STRICT_SAME_PAGE_CANDIDATE`.** Die elf
vollständig zugelassenen Bild- und Textselektoren, die nach GDT791 hinzukamen,
enthalten in der vorhandenen ZL3b-Quelle 80 lokale Ein-Gruppen-Labels. Keines
erfüllt zugleich die vorab festgelegten drei Annotationsbedingungen:
ungehedgte Aussage, objekttragender Kontext und **lokaler** expliziter
Anschluss/Einschluss/Identitätsvermerk. Folglich gibt es keinen neuen
streng besessenen Labelträger mit identischer Form im eigenen Fließtext.

Die Prüfung hat alle elf Selektoren abgearbeitet: f100r, f100v, f104r,
f104v, f114r, f21r, f32v, f6v, f75v, f99v und f9v. Nur vier haben in der
bewachten Umschrift lokale Ein-Gruppen-Loci: f100r 16, f100v 12, f75v 30 und
f99v 22. Die Annotationsquelle lieferte 122 Zeilen; die vollständige
dreifache Umschrift 7.456 Gruppenzeilen. Alle 80 Labels und 171 exakten
Label-zu-Prosa-Ereignisse stehen in den Ergebnisartefakten, nicht nur Treffer.

Es gibt acht **nicht streng gebundene** exakte Wiederverwendungen auf derselben
Seite. Das ist die vollständige Menge ab zwei Zeichen, nicht eine Auswahl:

| Label-Locus | Form | gleiche Seite: P-Treffer | Warum nicht streng gebunden |
| --- | --- | ---: | --- |
| f75v.25 | `qokal` | 6 | unhedged, aber nur Reihen-/Nähevermerk auf Einheitsebene |
| f75v.31 | `dal` | 5 | unhedged, aber nur Reihen-/Nähevermerk auf Einheitsebene |
| f75v.52 | `olol` | 1 | hedged und nur Nähe |
| f75v.54 | `otedy` | 3 | hedged; lokal Reihe/Nähe, kein Einzelanschluss |
| f75v.55 | `oteey` | 1 | hedged und nur Nähe |
| f75v.56 | `qotedy` | 2 | hedged und nur Nähe |
| f99v.4 | `oldy` | 1 | unhedged, aber lokal nur Nähe |
| f99v.31 | `doldam` | 1 | hedged und lokal nur Nähe |

Das Gegenbeispiel aus GDT1071 ist relevant: `cheody` schien unter einer
Einheitsannotation streng, doch der Kommentar besaß nur eine Pflanzengruppe,
kein Einzelobjekt. GDT1082 benutzt deshalb vor dem Lesen seiner Zielinhalte
bereits die engere Regel der **lokalen** Relationstags. Die acht Zeilen wurden
danach vollständig und ohne Hochstufung geprüft. Alte GDT790-Brücken und
GDT1071s lokal an einen Stern geschriebenes `otor` bleiben unverändert;
`otor` erhält dadurch weiterhin keine Wortbedeutung.

Der unabhängige Validator fragt beide gemischten Quellen erneut mit den elf
rohen `page`-Allow-Werten ab, kontrolliert Eingangsbytes, Methodenhistorie,
alle 80 Labels, ihre Zählwerte und die 171 Matchzeilen. Er bestätigt null
strenge lokale Besitzer und genau die acht nichtstrengen Same-Page-Loci:
`PASS`. Der Guard verwirft `f84*` vor Materialisierung. f84/f84r und Reserven
blieben geschlossen; f1r und partielle spätere Bildfreigaben waren nicht im
Vertrag. Die Seiten sind zuvor im Projekt exponiert und liefern keine
unabhängige Bestätigung. Drei Lesungen sind drei Umschriften eines Manuskripts.

**Konsequenz:** Aus dieser hinzugekommenen Vollseitenmenge entsteht kein
neuer Wortkandidat mit singulärer Bildzuordnung. Das ist kein Beweis, dass die
acht Formen bedeutungslos sind oder dass kein Bild einen von den alten
Annotationen übersehenen Anschluss besitzt. Ein separater vollständiger
nativer Bildaudit aller acht könnte genau diese andere Voraussetzung prüfen;
er dürfte die hier eingefrorene Entscheidung nicht nachträglich verändern.
Keine Signifikanz und **0 bestätigte übersetzte Wörter**.

Reproduktion: `python3 experiments/yolo/gdt1082_new_image_strict_label_prose_capacity/src/run.py`
und danach `python3 experiments/yolo/gdt1082_new_image_strict_label_prose_capacity/src/validate.py`.
