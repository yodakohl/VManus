# Ein anderer Weg zur Lesung: Inhalt als Änderung eines Schriftzustands

2026-09-14. Strategische Entscheidung auf Nutzerwunsch. **Ausgewählt zur
Ausarbeitung, noch kein ausgeführter Entzifferungsversuch und kein Bedeutungsbefund.**

## Entscheidung und Grund

Als nächsten begrenzten Arbeitsansatz wähle ich eine **Differentialschrift**:
Eine geschriebene Gruppe könnte einen Trägerzustand zeigen; der gelesene Laut
oder die gelesene Silbe wäre durch die Änderung gegenüber dem vorherigen Zustand
codiert. Derselbe sichtbare Träger könnte dann je nach Vorgänger verschieden
gelesen werden. Eine feste Veränderung könnte dagegen auf unterschiedlichen
Trägern denselben Laut ausdrücken.

Das ist eine spekulative Prioritätsentscheidung, keine Behauptung, dass Voynich
wahrscheinlich so funktioniert. Sie ändert eine grundlegende Zuordnung zwischen
Schrift und Inhalt, die in den zuletzt bearbeiteten Ganzwortlesungen feststand.
Eine weitere medizinische Fallbuchfassung wäre ebenfalls zulässig, aber derzeit
nicht hinreichend anders als die ursprünglichen P01–30.

Die Alternativen bleiben gewöhnliche Wortbildung/Schreibvariation und ein
Erzeugungsverfahren ohne Nachricht. Sie werden nicht durch die neue Benennung
schwächer. Insbesondere ist **jede endliche Zeichenfolge verlustfrei als Folge
von Änderungen darstellbar**. Rückwärtsrekonstruktion und gute Kompression allein
würden deshalb keinerlei geheime Botschaft nachweisen.

## Was die Vorgänger tatsächlich begrenzen

| Gelesener Primärbericht | Für diese Entscheidung relevante Grenze |
|---|---|
| [W89](../translation_programs_20260912/work/W89/REPORT.md) | Rezept und Beschreibung unterscheiden sich in fünf angesetzten Prädikaten und deren Argumentregeln; keiner ihrer Inhalte ist unabhängig gewählt. Nicht sämtliche denkbaren Rezeptlesungen wurden widerlegt. Der alte Glossenkern bleibt ausgesetzt. |
| [P20](../translation_programs_20260912/work/P20/REPORT.md) | Die Mischschrift schrieb fünf ausgewählte lateinische Werte nach. Zwei zusätzliche zerlegbare Formen ergaben keinen weiteren gelesenen Inhalt. Keine wiedergewonnene Sprache oder allgemeine Mischschriftwiderlegung. |
| [P30](../translation_programs_20260912/work/P30/REPORT.md) | Zwei frei angesetzte Verbindungsoperatoren ließen 878 von 940 Positionen offen und banden keine Bildteilnehmer. Ein neuer Gattungsname beseitigt diese Lücke nicht. |
| [GDT288](../../../GDT288_OPERATIONAL_GENERATIVE_GRAMMAR_REPORT.md) | Ein bedingtes Modell von Inhaltsträger und schriftlicher Gestaltung war bereits vorgeschlagen. Seine formale Synthese identifiziert weder Inhalt noch historisches Schreibverfahren; sie beweist unsere Differentialhypothese nicht. |
| [GDT303](../../../GDT303_RENDERER_OPERATION_POSITION_DELTA_REPORT.md) | Veränderungen formaler Felder wurden bereits mit physischen Positionsverteilungen verglichen. Keine Lautwerte und keine fortlaufende Nachrichtenlesung. |
| [GDT345](../../../experiments/yolo/gdt345_productive_operator_transfer/REPORT.md) | 8268 Übergänge zwischen sechs formalen Koordinaten wurden tatsächlich geprüft; kein belastbarer neuer produktiver Operatornachweis unter dem dortigen Vertrag. Das war keine Suche nach einer sprachlichen Folge, die dieselben Schriftzustände erzeugt. |
| [GDT914](../../../experiments/yolo/gdt914_local_parallel_one_edit_patterns/REPORT.md) | Der vollständige lokale Viererfenstertest liefert keinen wiederkehrenden, über Lesungen stabilen Ein-Zeichen-Parallelismus. Keine Wiederholung dieses Tests mit anderem Abstand oder Schwellenwert. |
| [RTA001](../../../experiments/semantic_assumptions/results/rta001_result_report.md) | Die dortige Transformationskompression trennte nicht von den falschen Zuordnungen. Regelmäßige Änderungen sind keine Bedeutungsbrücke. |
| [GDT613](../../../experiments/yolo/gdt613_observation_complete_fst34_recovery/REPORT.md) | Eine genaue ältere Mischgrammatik samt Kontrollvertrag war unvereinbar. Keine Wiederaufnahme ihrer Reparaturkette oder ihres Decoders. |

Zusätzlich wurden die gezielten IL008/IL011-Abschnitte des aktuellen Claimregisters
und IL008-Ledgerzeilen gelesen: Nachbarähnlichkeit und erneute Timm-Kontrollläufe
sind keine neue Route. Die dort verlinkte alte IL008-Reportdatei war am angegebenen
Ort nicht verfügbar; diese beiden Hinweise werden hier ausdrücklich als
Registerstand, nicht als neu geprüfte Primärberichte behandelt.

Die begrenzten Registry-/Duplikat-/route-check-Suchen fanden keinen identischen
vollständigen Sprachkanalversuch. **Das beweist keine historische Neuheit oder
vollständige Ausschöpfung des Archivs.** Der konkrete Unterschied ist der
gegenseitige Vertrag von Lautfolge und zustandsabhängiger Schriftproduktion,
nicht ein anderer Editabstand oder ein neues Kompressionsmaß.

## Konkreter Einstieg aus vorhandenem Text

Arbeitsumfang: die komplette bereits exponierte f83r-Projektion aus
[W92/PROSE.tsv](../translation_programs_20260912/work/W92/PROSE.tsv): sieben
Arbeitsrecords, 51 transkribierte Zeilen, 341 Gruppen. Die Recordgrenzen sind
übernommene Arbeitsgrenzen, keine bestätigten Sätze. Dieser Umfang ist kein
vollständiger diplomatischer Neuzugriff auf das Blatt.

Zwei Beispiele aus dieser vorhandenen Projektion erläutern die neue Frage:

| Stelle | Geschriebener Ausschnitt | Unterschied, ohne vorgeschlagene Bedeutung |
|---|---|---|
| f83r.4 | `qokshedy chedy qokedy chkedy` | `chedy → qokedy`: vor erhaltenem `edy` wird `ch` durch `qok` ersetzt. |
| f83r.20 | `solkeedy qoteedy qokeey qokedy sol cheeety qokedy qoky saiin` | `qokeey → qokedy`: im erhaltenen Rahmen `qoke…y` wird `e` durch `d` ersetzt. |

Dieselbe Zielgruppe `qokedy` entsteht also aus zwei unterschiedlichen Änderungen.
Diese nach Lektüre ausgewählten Beispiele sind **Illustrationen, keine
vorregistrierte Trefferprüfung und keine Evidenz für Differentialschrift**.
Die vollständige anschließende Ausarbeitung muss auch unähnliche Nachbarn und
identische Wiederholungen enthalten.

## Der erste Arbeitsblock muss bis zur Lesung reichen

Gesamtbudget für den ersten Block: etwa 90 Minuten einschließlich Vorbereitung,
Ausarbeitung, Prüfung und Veröffentlichung; Zwischenentscheidung nach spätestens
20 Minuten, bevor größere Software entsteht. Das ist eine Aufwandsschätzung,
keine neue globale Zeitgrenze des Nutzers.

1. **Einen endlichen Schreibvertrag formulieren und vor einer Auswertung fixieren.**
   Primär ist der unmittelbar vorhergehende Träger innerhalb desselben Records
   der Zustand. Kein nachträgliches Suchen des ähnlichsten früheren Worts und
   keine Sprünge über unpassende Wörter. Erste Gruppen sind vollständig
   ausgewiesene Anfangsangaben; sie werden nicht automatisch bedeutungslos.
   Zeilenumbrüche sind keine zusätzlichen Resets. Gleich lange Änderungswege
   dürfen nicht nach gewünschtem Klartext ausgewählt werden. Ein erlaubtes
   Operationsinventar, seine Positionskonvention, COPY und alle Literalreste
   müssen explizit vorliegen; dieses Planungspapier ist noch nicht dieses Inventar.
2. **Eine sprachliche Hypothese und das Schreibverfahren zusammen ausarbeiten.**
   Zuerst eine ausdrücklich versuchsweise lateinische Lesung wegen vorhandener
   Projektressourcen, nicht wegen eines neuen Sprachbefunds. Laut-/Silbenwerte,
   Wortgrenzen und grammatische Formen gelten gemeinsam. Keine freie lateinische
   Phrase pro Record, keine neuen Nullwerte oder Einzelworttabellen zur Rettung
   eines schönen Satzes. Jede Revision wird an sämtlichen bisherigen Positionen
   nachgeführt. Deutsch ist erst die Übersetzung dieser hypothetischen Lesung.
3. **Alle sieben Records vorlegen.** Alle 341 Gruppen müssen im Lesungsprotokoll
   stehen, einschließlich unaufgelöster Stellen. Eine echte Zwischenfassung
   darf Lücken haben; sie darf deren Inhalt nicht als unsichtbare Brücke benutzen.
   Schon dieser Block soll einen sprachlichen Entwurf versuchen. Ein bloßes
   Inventar von Änderungen, eine Entropietabelle oder einige passende Silben
   erfüllt den Arbeitsauftrag nicht.
4. **Die gemeinsame Verpflichtung tatsächlich prüfen.** Derselbe angenommene
   Lautwert muss bei verschiedenen zulässigen Vorgängerzuständen dieselbe
   Operation auslösen; dieselbe Operation muss überall denselben Wert behalten.
   Hypothetischer Klartext plus Anfangsangaben und ein einziges Regelwerk müssen
   die vollständigen beobachteten Folgen vorwärts erzeugen. Alle zusätzlich
   benötigten Entscheidungen zählen zum Modell, auch Grenzen, Varianten und
   wörtlich gespeicherte Reststücke. Unbeschränkter Ganzwortersatz würde das
   Modell entleeren und rechtfertigt keine Fortsetzung.
5. **Den resultierenden Text beurteilen, nicht nur die Maschine.** Derselbe
   Wortstamm, dieselbe Flexion und dieselben Bezugnahmen müssen über mehrere
   Aussagen hinweg funktionieren. Eine lateinische Lesung, die erst durch freie
   deutsche Ergänzungen sinnvoll wird, bleibt unzureichend. Gegenlesungen und
   widersprechende Positionen müssen neben dem Entwurf stehen.

Lieferung des Blocks: vollständige ausgerichtete Lesungsfassung, gemeinsame
Operation-/Lauttabelle, Vorwärtsspur aller Gruppen, sämtliche Widersprüche und
verbleibende alternative Lesungen. Für einen neuen empirischen Vergleich zuerst
ein reguläres GDT samt Manifest und genauer Preregistrierung anlegen; keine
Auswertung als nachträglich vorregistriert bezeichnen.

## Welche Ergebnisse ändern die Entscheidung?

- Eine über mehrere vollständige Records tragfähige sprachliche Fassung mit
  wiederverwendeten Regeln rechtfertigt ihre gemeinsame weitere Ausarbeitung
  im exponierten Umfang. Sie wäre eine unbestätigte Lesung, keine identifizierte
  Sprache, kein bewiesener Code und noch kein bestätigtes Wort.
- Braucht die Fassung praktisch pro Übergang eine neue Regel oder einen
  ausgeschriebenen Ersatztext, trägt der gewählte Schreibvertrag nicht. Diesen
  Vertrag stoppen; nicht automatisch größere Rückblicke, freie Resets oder einen
  Optimierer nachschieben. Das widerlegt keine beliebige zustandsabhängige Schrift.
- Gibt es nur eine verlustfreie Umcodierung, gute Kompression oder wenige
  wohlklingende Silben, ist der Block **inhaltlich unzureichend**. Kein neues
  Kontrollkorpus und keine weitere Infrastruktur allein zur Verlängerung der Route.
- Mehrere gleich tragfähige vollständige Klartexte bleiben mehrere Hypothesen.
  Keine Eindeutigkeit aus Solver-/Restart-Einigkeit oder subjektiver Lesbarkeit.

Der Weg zur Übersetzung wäre damit konkret: **Schreiboperationen und Sprache
gemeinsam erschließen → zusammenhängende Aussagen entwickeln → ihre gegenseitigen
inhaltlichen Verpflichtungen prüfen → erst eine nahezu vollständige plausible
Gesamtlesung im erklärten Umfang später an Reserven prüfen.** Eine einzelne
glücklich klingende Stelle löst keinen Reservetest aus.

## Exposition, Quellen und Grenzen dieser Entscheidung

Root las die genannten lokalen Berichte und die bereits exponierte W92-Projektion.
Ein begrenzter Ideenagent prüfte alternative Kapitelmodelle und kritisierte den
Differentialvertrag; er ist kein blinder Bestätiger. Alle drei Transkriptionen
bleiben alternative Lesungen desselben Manuskripts; die hier wiedergegebene
Projektion ist ZL3b, keine neue Übereinstimmungsprüfung.

Als externe Primärhinweise wurden nur die
[arXiv-Zusammenfassung von Timm](https://arxiv.org/abs/1407.6639) und die
[begleitende Autorenseite zum Textgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator)
gelesen. Sie zeigen, dass ähnliche Formen und deren Erzeugung längst untersuchte
Themen sind. Sie begründen weder unsere Nachrichtenhypothese noch deren
Neuheit. Der Verlagsvolltext war nicht zugänglich. Kein Generator, fremdes
Transkriptionskorpus oder verlinktes Manuskriptbild wurde heruntergeladen.

Keine neue Manuskriptseite, keine neuen Bildinhalte, keine Kontakte. f84/f84r
und alle übrigen Reserven bleiben geschlossen. Alte Lexika, Schlüssel,
Präfixregeln, Quellnamen und Transkriptionsregeln wurden nicht verändert.
Insbesondere bleiben GDT888s Nicht-Eindeutigkeit und GDT913s Zurückweisung aller
18 konkreten Kandidaten unverändert. Kein neuer Decoder, keine neue Teststatistik,
keine Signifikanz und keine Bedeutungsbestätigung in dieser Planungsrunde.
