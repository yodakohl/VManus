# GDT1032: historische Beschriftungen können ausdrücklich auf andere Stellen verweisen

**Positiver Quellenbefund:** Auf Ashmole399 f13v steht an drei getrennten
kurzen Beschriftungsstellen `similiter hic`, teils mit abgekürztem erstem Wort:
**„hier ebenso“**. Root und ein zweiter Modellagent haben diese Stellen unabhängig
in den unveränderten Vollbildern gelesen. Das ist eine relationale/deiktische
Beschriftung, kein gewöhnlicher Gegenstandsname. Daneben steht ein nominaler
Ausdruck `collum matric[?]`, wahrscheinlich `collum matricis`; die Endung bleibt
in der gemeinsamen Bewertung unsicher. Es handelt sich um lesbares Latein in
einer historischen Vergleichshandschrift, **nicht um übersetzte Voynich-Wörter**.

## Festgelegter Umfang und tatsächliche Ausführung

Vor Bildzugriff öffentlich registriert: `7eb1bd802`. Vier alte Bildadressen und
Hashes aus GDT213/214, keine neue Quelle oder Zielauswahl. Die beiden Bodleian-
Downloads sind bytegleich den gebundenen Vorgängern und wurden vollständig mit
nativer Vision betrachtet. Die Met-Antworten besitzen andere Hashes und wurden
entsprechend dem vorherigen Vertrag **nicht geöffnet**, nicht gespeichert und
nicht durch andere Bilder ersetzt. Der Grund der Byteabweichung ist ungeklärt;
sie ist weder eine Inhaltsänderung noch ein Quellenfehlerbefund.

| Bild | Ergebnis | Tatsächliche Sichtung |
|---|---|---|
| Ashmole399 f13v | alter SHA256 stimmt | ganze Seite, kurze Inschriften und Prosaregionen inventarisiert |
| Ashmole399 f22v | alter SHA256 stimmt | ganze Seite; keine sicher isolierte kurze Inschrift identifiziert |
| Met55.121.11 obverse | SHA256 abweichend | nicht geöffnet |
| Met55.121.11 reverse | SHA256 abweichend | nicht geöffnet |

[FETCH.json](artifacts/FETCH.json) enthält Soll-/Ist-Hashes und Bytemengen.
Bilder werden nicht veröffentlicht. Institutionelle Ausgangsobjekte:
[Bodleian Ashmole399](https://digital.bodleian.ox.ac.uk/objects/2b7310aa-9199-4a5b-93fb-4f5f075ca28a/)
und [Met55.121.11](https://www.metmuseum.org/art/collection/search/451298).
Die bereits bekannten institutionellen Objektseiten wurden zusätzlich als
Navigation erneut geöffnet; keine dort verlinkte weitere Abbildung oder
zusätzliche wissenschaftliche Quelle wurde aufgenommen. Historische Angaben
werden dadurch nicht zu neuen Befunden.

## Alle Lesungen bleiben nachprüfbar

Die vollständigen manuellen Inventare stehen getrennt in
[OBSERVATIONS.json](artifacts/OBSERVATIONS.json) und
[INDEPENDENT_READING.json](artifacts/INDEPENDENT_READING.json). Sie enthalten
auch unlesbare, randabgeschnittene und hinsichtlich ihrer Regionengrenzen
mehrdeutige Inschriften. Root zählte28 Regionen auf f13v und2 große Prosafelder
auf f22v; die unabhängige Sichtung teilt f13v in30 und f22v in7 Prosaregionen,
einschließlich eines als solchen ausgewiesenen Nachbarseitenstreifens. Die
Zählweisen werden nicht vereinheitlicht oder als Caption-Häufigkeiten verkauft.
Die übrigen unsicheren Buchstaben werden nicht aus der vermuteten Anatomie ergänzt.

| Fester Ort im Gesamtbild f13v | Root / unabhängige Lesung | Gemeinsame belastbare Folge |
|---|---|---|
| oben links am schrägen Band | `similiter hic` / `similiter hic` | kurzer relationaler Verweis |
| kleiner Kreis links in mittlerer Höhe | `similiter hic` / `similit[abbr] hic` | gleiche Lesung nach offengelegter Abkürzungsexpansion |
| Kappe der äußeren linken Säule | `similiter hic.` / `similit[abbr] hic.` | gleiche relationale/deiktische Lesung; kein mitgelesenes Nomen |
| Kappe der äußeren rechten Säule | `collum matricis.` / `collum matric[?]` | nominale Grammatik plausibel; ganze Endung nicht gesichert |
| mittlere senkrechte Kurzinschrift | `hec est ...` / `hec est uia ...` | möglicher Kopulasatz; vollständiger Wortlaut bleibt offen |
| kleiner Kreis rechts in mittlerer Höhe | `hic ... unde / fluit seme[n?]` / ähnlich | möglicher Satz-/Relativbezug; keine vollständig sichere Übersetzung |

Root hatte zwei Abkürzungen zunächst wie ausgeschriebene Zeichen wiedergegeben.
Die Originalbeobachtung bleibt erhalten; der Endbericht trennt sichtbare Kürzung
und Expansion. Auch die höhere ursprüngliche Sicherheit von `matricis` wird
nicht durch Mehrheitsentscheidung erzwungen. Sämtliche Unterschiede sind in
[RECONCILIATION.json](artifacts/RECONCILIATION.json) ausgewiesen. Die drei klaren
Verweisstellen sind drei Vorkommen **eines** Blatts, keine drei unabhängigen
historischen Stichproben. Für den qualitativen Existenzbefund genügt schon die
klare Säulenkappe; die vollständige Sichtung verhindert das Weglassen anderer
Beschriftungsarten.

## Konsequenz für die Bedeutungssuche

Die zusätzliche Universalregel „eine isolierte kurze Inschrift ist ein
selbständiger Gegenstandsname“ ist für diese Kontrollpraxis falsch. Ein sinnvoller
Lesekandidat kann stattdessen „hier ebenso“ ausdrücken und seinen Bezugsinhalt
von einer anderen Stelle oder dem Diagramm beziehen. Diese konkrete Möglichkeit
war in213nur als Architektur sichtbar; die neue native Lesung bindet sie jetzt
an tatsächliche Wörter.

Das liefert **keine** Häufigkeitsverteilung für Nomen gegen Konjunktionen und
keinen Bayesfaktor für qokaiin=AND oder HOURS. Insbesondere wurde kein allein
stehendes AND in der Quelle identifiziert. Die relationale Deixis belegt nicht,
dass jeder Operator beliebig ohne Argumente stehen kann. Ein zukünftiger
vollständiger Voynich-Inschriftencheck darf daher zusätzliche Erklärungslast
unter ausdrücklich angenommener lokaler Beschriftungspraxis vergleichen;
er darf aus einem isolierten Treffer keine harte Wortwiderlegung ableiten.
HOURS bleibt ohne unabhängig identifizierten Stundenbezug ebenso unbestätigt.

**Entscheidung:** gemischte nominale und referenzielle Beschriftungsgrammatik
als konkretes historisches Vergleichswissen behalten. Keine neue Kontrollsammlung
und kein scheinbar kalibriertes Nomen-/AND-Modell bauen. Eine eventuelle Zielzählung
braucht einen eigenen festen Vertrag und bleibt qualitativ. Der jetzige Versuch
öffnet keine Voynich-Zeile, kein neues Voynich-Bild, keine Reserve oder f84/f84r.

## Prüfung, Kosten und Grenzen

Der unveränderte [Validator](src/validate.py) prüft neun Quellen-/Programm-
Bindungen, alle vier Bildstatus und das manuelle Ergebnisformat. Seine PASS-
Ausgabe ist [VALIDATION.json](artifacts/VALIDATION.json); sie bestätigt keine
Paläographie. Die unabhängige Sichtung las die Vollbilder vor Öffnung der Root-
Beobachtungen; Root fixierte die eigene Lesung vor Öffnung des Gegenberichts.
Beide sind Modelllesungen, keine externe Fachprüfung. Kein OCR, Ausschnitt,
neue Auflösung oder Bildbearbeitung wurde verwendet.

Auswahlbeginn10:32:06UTC; unabhängige Lesung abgeschlossen10:43:34UTC; Budget
bis10:57:06UTC einschließlich Veröffentlichung. Keine wissenschaftliche Code-
Änderung nach der öffentlichen Registrierung. Der Cachepfad wurde davor auf
portable temporäre Pfadbildung korrigiert, ohne Bildzugriff. Bestätigte Voynich-
Wörter: **0**. Keine Signifikanzbehauptung über die gesamte Projektsuche.

Reproduktion: Hauptlauf lädt genau die vier gebundenen URLs einmal und prüft die
alten Hashes; veränderte Antworten bleiben geschlossen. Die manuellen Lesungen
können an passenden Originalbytes nachvollzogen, nicht durch den Validator
historisch bewiesen werden.
