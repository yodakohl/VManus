# GDT595 — die letzten Badegut-Defaults sind konkretisiert

Status: `PASS_44_COLD_DEFAULTS_COMPLETED__20_AIIN_FILL_CONTEXTS__18_LATE_Y_PACKETS__6_BARE_CONTEXTS__HYBRID_16_BODY_23_STATION_3_PORTION_2_BATH_UNIT__2_DEPENDENT_CARRIES_PROPAGATED__254_SPECIFIC_OBJECTS__0_BATH_OBJECT_DEFAULTS_REMAIN`

## Ergebnis

Der 254-Aktionen-Badeleser enthält erstmals kein generisches `Badegut` mehr.
Die letzten 44 kalten Defaults werden direkt konkretisiert; zwei bereits
bestehende Episodenverweise übernehmen anschließend den neu bestimmten Typ
ihrer Quelle.

Die 44 direkten Ergänzungen sind:

| Objekt | Anzahl |
|---|---:|
| Körper | 16 |
| Stationsansatz | 23 |
| Anwendungsportion | 3 |
| Becken- oder Körpereinheit | 2 |

Nach E3219→Körper und E3489→Stationsansatz lautet das vollständige Profil:

| Objekt | Anzahl in 254 Aktionen |
|---|---:|
| Körper | 100 |
| Stationsansatz | 122 |
| Anwendungsportion | 15 |
| Bade-/Stationseinheit | 15 |
| Strom | 2 |
| Badegut | 0 |

46 Aktionen in 42 Aussagen ändern sich. 751 von 793 Aussagen bleiben
gegenüber GDT594 byte-identisch.

## Die entscheidende Verbesserung

Die alte Restbeschreibung `17 AIIN-carry + 27 no-state` war für Bedeutungen zu
grob. Zwei voneinander unabhängige Schnitte sind nötig.

Der Formbestand lautet:

- 20 Vorkommen besitzen irgendeine AIIN-Füllspur;
- 18 Zielwörter besitzen ein späteres Y-Paket im selben Ereignis;
- 6 besitzen keines von beidem.

Das ist keine Objektzuweisung. AIIN bleibt Füllung oder Medium und kann Körper,
Station oder Portion begleiten. Auch Y ist kein globales Stationswort.

Die eigentliche Objektquelle lautet:

- 21 linke, sichtbare Teilnehmer werden mit `denselben/dieselbe`
  wiederaufgenommen;
- 8 gleichereignisige Endträger schließen als definite gemeinsame Komplemente
  eine kurze Verbkette ab;
- E2952 bleibt eine Station/Portion-Gabel, die durch die nachfolgende
  Stationsbehandlung zugunsten Station entschieden wird;
- 14 resetgebundene Stellen ohne hinreichenden nicht-mediumhaften Teilnehmer
  erhalten Körper als ersten definiten Default.

Damit wird aus `AIIN → Körper` die sinnvollere Konstruktion:

```text
SH-Aktion + AIIN-Füllung + separat bestimmter Patient
```

## Drei vollständige Modelle statt einer Scheingewissheit

Die vollständige Werkstattlektüre ergab zunächst `20 Körper / 19 Station / 3
Portion / 2 Einheit`. Ein unabhängiges Body/Station-Quellenmodell ergab `23
Körper / 21 Station`, verlor aber Portion und Einheit trotz sichtbarer
Teilnehmer.

Der ausgewählte Hybrid behält die reichere Werkstattregel und ändert nur vier
Vorkommen von Körper zu Station:

| Ereignis | Werkstatt | Hybrid | Grund |
|---|---|---|---|
| E2863 | Körper | Station | gleichereignisiges P+Y mit Y=Stationsansatz |
| E3523 | Körper | Station | CHD+Y; GDT589 liest den Träger als Station |
| E3533 | Körper | Station | K+Y; die folgende Badeaktion ist ebenfalls Station |
| E3664 | Körper | Station | T+…+Y mit Stationsadressierung und folgender Stationsaktion |

Diese vier Änderungen verwenden eine einheitliche explorative Regel: Ein am
rechten Rand desselben geschriebenen Ereignisses realisierter Gegenstand darf
über die unmittelbar davorstehende kurze Verbkette greifen. Er wird trotzdem
nicht zum direkten SH-Slot umetikettiert. Die enge Hostlesung bleibt Rivale.

Eine zweite manuelle Nachlese bevorzugte bei sechs Streitfällen die enge
Host-/Stufenwechsel-Lesung (`E2863`, `E3224`, `E3523`, `E3533`, `E3563`,
`E3664`). Diese Gegenlesungen werden nicht verworfen. Der Hybrid bleibt primär,
weil er eine einfachere kompositionelle Vorhersage für Endträger liefert und
historisch mögliche Rezeptsyntax nutzt.

## Konkrete Lesungen

Starke linke Wiederaufnahmen:

```text
E1445  Führe die Anwendungsportion zu. Halte dieselbe Anwendungsportion im Bad auf Grad II.
E1523  Wähle die Einheit aus. Halte dieselbe Becken- oder Körpereinheit im Bad auf Grad I.
E2426  Behandle den Stationsansatz. Halte denselben Stationsansatz bei der angegebenen Füllung im Bad auf Grad I.
E2552  Bereite die Anwendungsportion und das Badmaß vor. Halte dieselbe Anwendungsportion im Bad auf Grad I.
E2988  Verwende die Becken- oder Körpereinheit. Halte dieselbe Becken- oder Körpereinheit im Bad auf Grad I.
```

Rechtsabschließende gemeinsame Komplemente:

```text
E1742  Halte den Körper im Bad auf Grad II. Lass den Körper anschließend abkühlen.
E2863  Halte den Stationsansatz im Bad auf Grad I. Entnimm oder lass ab. Wende den Stationsansatz an.
E3523  Halte den Stationsansatz im Bad auf Grad I. Entnimm oder lass ab. Behandle den Stationsansatz.
E3664  Halte den Stationsansatz im Bad auf Grad I. Temperiere den Stationsansatz. Halte denselben Stationsansatz erneut im Bad.
```

Definite Defaults und Episodenfortsetzung:

```text
E3218  Halte den Körper im Bad bei der angegebenen Füllung auf Grad I.
E3219  Halte denselben Körper im Bad auf Grad I.
E3488  Halte denselben Stationsansatz im Bad auf Grad I.
E3489  Halte denselben Stationsansatz im Bad auf Grad I.
```

## Historische Plausibilität

Die historischen Quellen sind keine Voynich-Schlüssel. Sie zeigen aber, dass
die Arbeitsgrammatik nicht modern erfunden sein muss.

- [Harley MS 279, ca. 1420](https://quod.lib.umich.edu/c/cme/CookBk/1%3A6?rgn=div1&view=fulltext)
  belegt koordinierte Operationen vor einem gemeinsamen rechten Objekt und
  unmittelbare pronominale Wiederaufnahme.
- Dasselbe Manuskript trennt eine Portionsangabe grammatisch vom anschließend
  pluralisch wiederaufgenommenen Reis. Maß und fortgeführter Stoff sind also
  nicht dasselbe syntaktische Argument.
- Das [Buch von guter Speise](https://www.uni-giessen.de/de/fbz/fb05/germanistik/absprache/sprachverwendung/gloning/tx/bvgs.htm?set_language=de)
  führt eingeführte Werkstoffe durch lange parataktische Operationsketten mit
  Pronomen weiter.
- Das [Feuerwerkbuch, Freiburger Hs. 362 von 1432](https://kdih.badw.de/datenbank/untergruppe/39/2)
  verbindet genaue Mengen mit einem danach als Charge behandelten Gemenge.
- [Heidelberg Cpg 539, um 1425](https://digi.ub.uni-heidelberg.de/diglit/cpg539)
  enthält medizinische Rezepte und Badevorschriften im passenden Zeitfenster.

Der historische Gewinn ist begrenzt, aber nützlich: Verbketten, Anaphora,
Mengen/Patient-Trennung und markierte Referentenwechsel sind zeitnah
plausibel. Er beweist weder `Y=Station` noch `AIIN=Füllung` noch einen Körper.

## Patch- und Erhaltungsaudit

S502 enthält drei Änderungen, S565 und S583 je zwei. In S583 sind die beiden
alten Klauseln identisch. E3664 teilt seinen alten Klauseltext außerdem mit der
späteren bereits konkreten E3673-Stelle. GDT595 lokalisiert daher alle
Originalspannen vor dem Ersetzen und patcht von rechts nach links.

Der Validator prüft 112 Invarianten, darunter die exakten 44/2 Zielmengen,
alle drei Modellprofile, die 20/18/6- und 21/8/1/14-Schnitte, sämtliche
Rivalenkanäle, alle Mehrfachersetzungen, 208 unveränderte Aktionen, 751
unveränderte Aussagen, fünf historische Quellen, keine f84-Zeile und den
byte-identischen Neubau aller Ergebnisartefakte.

Keine neue Seite, kein neuer Stamm, kein neues Surface, kein anderer Parser und
keine neue Segmentierung wurden verwendet.
