# Inhaltliche Deduplikation und Priorität — 2026-09-06

Die erste inhaltliche Zusammenführung ist durchgeführt. Sie ist kein abgeschlossener
Primäraudit jedes historischen Eintrags und keine neue Entschlüsselung.

## Tatsächlich zusammengeführt

- **okaiin = Pulver?** in GDT813/814/815: eine wiederholte Wortzuweisung.
- **okaiin = ist?** in denselben drei Versuchen: eine andere wiederholte Wortzuweisung.
- GDT814/815 prüfen dieselbe Eigenschaft-versus-Besitzreferenz-Frage mit unterschiedlichen
  Erweiterungen. GDT798/IP023 wiederholen die konkrete qokaldy-Referenzfrage;
  GDT625/768 führen die cthy-Blattgut-Vermutung weiter. Ergebnisse zählen dadurch
  nicht mehrfach als unabhängige Bestätigungen.
- Zwei Pflanzenfamilien zitieren denselben IL017-Unterversuch. Der Quellenverweis
  zählt einmal; der fehlende Primärbericht bleibt ausdrücklich fehlend.

**Keine ganzen Experimente wurden verschmolzen.** „davon“, „dessen“, „daraus“,
Ditto und eine Rückkehroperation sind verschiedene Hypothesen. Auch ein geänderter
`dair`-Lesetext ist keine Bestätigung seiner früheren Wortzuweisung. Die Zuordnung
steht auf Ebene der konkret benannten Teilbehauptung; alte Versuche und Fehler bleiben erhalten.

## Arbeitspriorität

Keiner der geprüften Ansätze liefert derzeit einen neuen ausführbaren Bedeutungstest.
Die folgende Reihenfolge gilt **nur für die Bewertung neu eintreffender Belege**,
nicht als Auftrag, dieselben Textstellen noch einmal zu untersuchen:

| Rang | Frage | Was eine Entscheidung ermöglichen würde | Warum hier |
|---|---|---|---|
| 1 | `okaiin`: Eigenschaft oder Besitzreferenz? | Eine unabhängig begrenzte Eigenschafts-/Bezugsrelation mit verschiedenen Vorhersagen der festen Modelle | Zwei konkrete konkurrierende Konstruktionen und dokumentierte Textketten liegen vor; deren bloße Vereinbarkeit entscheidet noch nichts. |
| 2 | `qokaldy`: Rückverweis oder Inhaltswort? | Eine unabhängig bestimmte Auswahl eines bestimmten Antezedenten | Der alte Vergleich ist ein dokumentiertes Unentschieden; eine tatsächlich selektierende Beobachtung würde dieses direkt ändern. |
| 3 | `cthy`: Blattmaterial oder allgemeinere Stoffklasse? | Eine unabhängige Unterscheidung der Referenten ohne unsere Arbeitsglosse als Etikett | Verhindert, dass eine häufig weiterverwendete unbestätigte Wortzuweisung als gesichertes Fundament dient. |

GDT391 bleibt eine bedingte Beschaffungsroute: vier passende Relationen reichen
nicht für die ursprünglichen 50 Relationen, zehn gemischten Einheiten und fünf
Blätter. Eine konkrete Quelle müsste diese Lücke plausibel verkleinern. Kein
pauschales Freigeben weiterer Seiten. GDT855 ist mit den drei verbliebenen
q05-Pflanzenblättern nicht reparierbar. GDT853/854 sind strukturelle Fragen;
sie konkurrieren hier nicht als vermeintlich direkte Bedeutungsfortschritte.
GDT340 ist weder ein rein datenloser Versuch noch ein Nachweis fehlender Rezepte.

Fehlende Primärberichte werden nur zurückgeholt, wenn eine konkrete neue Entscheidung
von ihrem Inhalt abhängt. Keine weitere allgemeine Archiv-, Metadaten- oder Decoder-Runde.

## Abdeckung und Grenzen

- Alle **82 IP-Vorschläge** haben eine ausdrücklich vorläufige Warteschlangenentscheidung:
  **26 roh/ungeprüft, 32 bedingt, 7 Quellenprüfung, 17 aktuelle Instanzen archiviert**.
  „Archiviert“ widerlegt nicht die allgemeine Idee. Kein Vorschlag wurde allein
  aufgrund dieser Sichtung zur Ausführung freigegeben.
- Der Katalog enthält **20 gezielt bearbeitete Hypothesen-/Vergleichsgruppen** und
  **70 einzelne vorhandene Familien-/Ankerdossiers**. Diese 90 Einträge sind
  ausdrücklich **nicht 90 unabhängige Bedeutungsideen**.
- Neun vorhandene Registerkarten erhielten 20 append-only Teilbehauptungsbeziehungen.
  Zwei Gruppen bezeichnen identische Wortzuweisungen, drei dieselbe geprüfte Frage.
- Sechs der zwölf gezielt geprüften Familien haben hier teilweise geprüfte
  Primärquellen; sechs bleiben geerbte Zusammenfassungen. Ein Teilbericht bewertet
  nicht automatisch eine ganze Familie.
- Jeder importierte Datensatz erscheint in `decisions/full_history_coverage.tsv`.
  `decisions/coverage_audit.json` unterscheidet geprüfte Gruppenbezüge, geerbte
  Einzeldossiers, bloße Navigation und ungeklärte Zuordnung. Ein Ledger-Eintrag
  kann eine Korrektur oder Verwaltung sein; die Restmenge ist keine Ideenanzahl.
- Die vollständige inhaltliche Zuordnung sämtlicher historischen Einträge bleibt
  offen. Weder Stichwortgleichheit noch derselbe Bericht dürfen diese Lücke scheinbar schließen.

## Benutzung ohne Kontextüberladung

```bash
./vmanus-work priorities --limit 8
./vmanus-work priorities --queue --disposition raw_unreviewed --limit 8
./vmanus-work priorities --show WH_PROPERTY_ARCHITECTURE
./vmanus-work priorities okaiin
./vmanus-work ideas relations GDT813 --limit 6
./vmanus-work ideas reconsider GDT855 --change new_data
```

Die Gruppenansicht zeigt Belege, Unterschiede, Wiederaufnahmebedingungen und
unzureichende Änderungen. Der zugehörige Versuch bleibt über `ideas show` abrufbar.
Vor Auswahl eines neuen Versuchs bleiben Primärprüfung und `route-check` erforderlich.

Prüfung: 102 Unit-Tests bestanden; Katalog-, Queue- und Abdeckungsprüfungen bestanden.
Der Gesamtaudit meldet weiter acht vorbestehende Fehler (GDT600/Index).

Reproduktion: `python -m tools.semantic_catalog --build`,
`python -m tools.validate_semantic_catalog --check`, danach
`python -m tools.research_priority_coverage --check` beziehungsweise nach einer
beabsichtigten Registeränderung zuerst dessen Ausgabe neu erzeugen. Quellenentscheidungen
sind dokumentierte Beurteilungen; diese Befehle reproduzieren ihre Darstellung und
Abdeckungsprüfung, nicht automatisch die wissenschaftliche Beurteilung.
