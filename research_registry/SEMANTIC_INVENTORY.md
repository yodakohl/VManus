# Alle dokumentierten Bedeutungsansätze in derselben Arbeitsliste

Die operative Liste ist nicht mehr auf IP001–IP082 beschränkt. Sie enthält jetzt
die vollständige erhaltene Registergeschichte und zusätzlich die aus älteren
Vorschlagssammlungen, Arbeitsmodellen und Berichten gewonnenen Quellenstellen.

```bash
./vmanus-work priorities --queue
./vmanus-work priorities --queue "iatromathematical"
./vmanus-work priorities --queue --item-type hypothesis_proposal
./vmanus-work priorities --queue --item-type hypothesis_component
./vmanus-work priorities --queue --show GDT815
```

Acht Treffer pro Seite, höchstens zwanzig; mit `--offset` weiterblättern. Jede
Fundstelle hat eine stabile ID, Originalformulierung oder einen klar bezeichneten
Quellenverweis, Herkunft, Status und getrennte Angaben zur Prüfung. Die bisherigen
IP-Karten behalten ihre IDs und Einordnungen. Hypothesen in bislang nicht einzeln
extrahierter sicherer Berichtprosa sind ebenfalls durchsuchbar; der Treffer bleibt
als Quellentreffer gekennzeichnet. Ganze Archive werden nicht in den Kontext geladen.

## Was jetzt enthalten ist

| Bestandteil des veröffentlichten Bestands | Anzahl | Bedeutung |
|---|---:|---|
| Vollständig erhaltene Registerdatensätze | 5.058 | 82 IP-Vorschläge, 870 Versuche, 4.036 historische Einträge, 59 Familien, 11 Anker |
| Fundstellen aus expliziten Vorschlagskontexten | 427 | Automatisch erkannte Kandidaten, noch keine 427 unabhängig geprüften Ideen |
| Zuordnungen, Hypothesentabellen und Deutungsauszüge | 3.788 | Historische Wort-/Rollenhypothesen einschließlich geänderter und verworfener Varianten |
| Weitere erhaltene Quellenauszüge | 4.943 | Nicht automatisch als Idee klassifizierte Prosa, etwa Methoden- oder Ergebnistext |
| Ungeklärte Blöcke und Quellenreste | 15.478 | Noch nicht einzeln erschlossene Inhalte; verbleiben sichtbar und suchbar, soweit sichere Prosa vorliegt |
| Gesamte öffentliche Arbeitsliste | 29.694 | Unterschiedliche Datensatzeinheiten, ausdrücklich keine Gesamtzahl unabhängiger Ideen |

Zusätzlich erscheinen in dieser lokalen Arbeitskopie **82 Auszüge aus 14 bislang
ungetrackten V81-Protokollen und Theorieberichten**, darunter fünf als Vorschlagskontext
erkannte Stellen. Sie werden beim Öffnen derselben Liste hinzugenommen. Ihre
Originaldateien bleiben unverändert; dieses lokale Supplement wurde nicht veröffentlicht.
Die lokale Ansicht umfasst damit 29.776 Einträge. Eine frische öffentliche Kopie
enthält den öffentlichen Bestand; sie benötigt das lokale Supplement nicht.

Beispiele wieder aufgenommener Ansätze sind die abgekürzte natürliche Sprache,
das bildbezogene Werkstattbuch, das astrologisch-medizinische Zuordnungssystem
sowie frühere Arbeitsglossen für `cthy`, `dair`, `okaiin` und `qokaldy`.
Auch die früheren Widersprüche und erfolglosen Varianten bleiben auffindbar.

Die **26 Rohideen** waren ausschließlich eine Statusklasse innerhalb der jüngsten
82 IP-Vorschläge. Diese Zahl beschreibt den gesamten Bestand nicht.

## Quellenabdeckung und Grenzen

Der Vorschlagslauf erfasst 5.268 ausgewählte getrackte Prosa-/Vorschlagsdateien,
einschließlich erhaltener Wurzelverzeichnis-Archive. Der Berichtslauf inventarisiert
2.739 Berichts-/Theoriedateien und liest 2.711 sichere Markdownquellen. Die Mengen
überlappen. Jede ausgewertete Quelle behält zusätzlich einen Verweis auf ihren
noch nicht vollständig erschlossenen Rest. Alle 4.110 Ledger-Ereignisse und auch
336 Datensätze ohne Zusammenfassung bleiben erhalten.

Die Klassifikation ist bewusst vorläufig: eine Tabelle unter „Kandidaten“ kann
auch ein Ergebnis enthalten; derselbe Ansatz kann in mehreren Berichten vorkommen.
Quellenauszüge werden deshalb weder stillschweigend verschmolzen noch als neue
Bestätigungen gezählt. Vollständige inhaltliche Deduplikation und Priorisierung
jeder älteren Einzelhypothese sind damit nicht vorgetäuscht.

Nicht wiederherstellbare gelöschte Altquellen bleiben als Lücke dokumentiert.
Versiegelte Stellen, Codeblöcke und Rohdaten werden nicht durch diesen Import
freigegeben. Nicht gelesene Artefakte bleiben Quellenverweise; ihre Inhalte werden
nicht erfunden. Weder ein historisches PASS noch eine vorgeschlagene deutsche
Lesart wird zu einer bestätigten Übersetzung hochgestuft.

## Wiederverwendung

Vor einer neuen Idee zuerst die **gesamte** Liste durchsuchen, anschließend die
konkreten Treffer und ihre Vorgänger lesen. Die ältere `ideas duplicates`-Suche
bleibt eine zusätzliche Suche in Registerkarten; sie allein deckt die neu
erschlossenen Quellenauszüge nicht ab.

```bash
./vmanus-work priorities --queue "okaiin"
./vmanus-work ideas duplicates "okaiin"
./vmanus-work ideas show GDT815
```

Zu einem Quellentreffer liefert `--show ID --source-text --limit 3 --offset 0`
eine begrenzte Seite sicherer Originalprosa. Das zeigt Quelleninhalt, keine
bestätigte Bedeutung. `ideas reconsider` behält seine bisherigen strengen
Wiederaufnahmebedingungen. Fehlende neue Evidenz wird nicht durch diesen Import ersetzt.

Reproduktion und Prüfung:

```bash
python -m tools.extract_legacy_proposals
python -m tools.extract_semantic_components
python -m tools.semantic_inventory --build
python -m tools.semantic_inventory --check
python -m unittest tests.test_semantic_inventory
```

Die Extraktoren öffnen nur ihre dokumentierte Quellenauswahl. Der Datenbestand
steht in `semantic_inventory.jsonl`, seine Quellenbindung in `INVENTORY_MANIFEST.json`.
Der SQLite-Suchindex und das lokale Supplement liegen ignoriert unter `runtime/`.
Prüfbericht: `decisions/full_inventory_validation.json`. Diese Prüfung belegt
Datenübernahme und Quellenbindung, nicht die wissenschaftliche Wahrheit der Ideen.

Prüfung dieses Stands: 111 Unit-Tests bestanden; vollständige Register-/Extrakt-
Übernahme und Quellenhashes geprüft. Die acht vorbestehenden Fehler des Gesamtaudits
(GDT600 und alter Index) bleiben unverändert.
