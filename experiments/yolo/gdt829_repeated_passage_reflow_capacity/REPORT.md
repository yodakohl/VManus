# GDT829 — keine passenden Wiederholungskontexte für den Umbruchvergleich

2026-09-05. Status: **CAPACITY_FAIL_UPPER_BOUND**.

Die vorab festgelegte Suche liefert **keinen wiederkehrenden Kontext** um eine
maskierte terminale l/m-Stelle. Das scheitert bereits an der Kontextidentität,
bevor unterschiedliche Zeilenumbrüche, Schreiber oder Endzeichen verglichen
werden könnten. Der vorgeschlagene Versuch endet deshalb nach dieser einen
Bestandsaufnahme. Kein Richtungstest und keine Entzifferung wurden ausgeführt.

## Was gesucht wurde

Ein explizites terminales l oder m wird maskiert. Identisch sein müssen die
gesamte Zielgruppe bis auf die Endung sowie jeweils zwölf literal erhaltene
Transkriptionsatome links und rechts der Endstelle. Abstände bleiben zusätzlich
in der Signatur. Nur ein sicherer Gruppenabstand und ein zulässiger physischer
Zeilenübergang werden für den Vergleich gleich behandelt. Sonderzeichen und
unsichere Lesungen werden erhalten; Zeichnungsunterbrechungen trennen Ströme.

Es werden auch unveränderte l/l- und m/m-Kontexte gesucht. Beide Endungen zu
beobachten ist keine Auswahlbedingung. Die Randgruppen eines Fensters können
angeschnitten sein; gesucht werden somit längere lokale Kontexte, nicht
zwingend vollständige identische Sätze oder Absätze.

Die Präregistrierung und beide Implementierungen wurden mit Commit
`9a9380b0` vor der ersten Manuskriptextraktion öffentlich veröffentlicht.
`src/PREREG_LOCK.json` bindet die unveränderte Spezifikation und Präregistrierung.

## Umfang und Ergebnis

Die geschützte Abfrage verwendet ausschließlich die 179 freigegebenen
Textselektoren. Sie liefert 96.184 Quellgruppen in 12.405 Quellzeilen über die
drei Lesungen. Das sind keine unabhängigen Manuskriptzeugen. f84/f84r werden
vor dem Materialisieren ihrer Zeileninhalte verworfen; keine Seite wird neu
freigegeben und kein Bild geöffnet.

Das ZL-Gerüst umfasst 665 ausdrücklich begrenzte Absätze mit 3.768 P-Zeilen,
aufgeteilt in 703 Segmente. 39 eingeschobene Nicht-P-Zeilen unterbrechen die
Verbindungen. Nach Zeichnungsunterbrechungen ergeben sich in ZL 1.377
zusammenhängende Gruppenströme. P ist eine Transkriptionsklasse, keine
bestätigte sprachliche Textart.

| Lesung | Explizite Endstellen vor Flankenprüfung | Vollständige maskierte Fenster | Wiederkehrende Kontextfamilien | Paare mit geändertem Umbruch |
|---|---:|---:|---:|---:|
| ZL3b, primär | 5.513 | **4.455** | **0** | **0** |
| IT2a, Sensitivität | 5.649 | **4.596** | **0** | **0** |
| RF1b, Sensitivität | 5.511 | **4.474** | **0** | **0** |

In ZL fehlen bei 443 Endstellen die nötigen linken Flanken; bei weiteren 615
die rechten. IT verliert ein vollständiges fünfzeiliges Gerüstsegment wegen
fehlender Lesungsabdeckung. Die übernommenen ZL-Absatzmarkierungen weichen
an 104 IT-Zeilen und 1.330 RF-Zeilen von den dortigen nativen Flags ab. Diese
Abweichungen werden dokumentiert, nicht als unabhängige Absatzbelege gezählt.

Die Nullzahl der Wiederholungen gilt schon vor dem strengeren Filter für
eindeutige Transkriptionssyntax, gleiche bekannte Hand und unabhängige Folios.
Sie wird daher nicht erst durch diese Kontrollfilter oder die geforderte
Teststärke erzeugt. Die Obergrenze geeigneter unabhängiger Vergleiche ist U=0;
die geplante Teststärke wäre frühestens mit 32 informativen Vergleichen erreichbar.

## Prüfung und reproduzierbare Artefakte

Der unabhängig implementierte Validator importiert den Runner nicht. Er
rekonstruiert aus derselben geschützten Quellenprojektion alle **13.525**
Fenster der drei Lesungen und bestätigt jedes Fenster sowie die leeren
Wiederholungs-, Umbruch-, Paar- und Komponententabellen ohne Abweichung.
13.525 ist eine Buchhaltungszahl über alternative Lesungen, keine gemeinsame
statistische Stichprobengröße. Ein bytegenauer Replay des Runners besteht.

Zehn Kontrollen am tatsächlichen Runner und elf Kontrollen an der unabhängigen
Implementierung bestehen. Sie prüfen insbesondere bekannte Umbruchvarianten,
unveränderte Endungen, Quelllücken, unsichere Abstände, opake Entities und die
Abhängigkeit mehrerer Seiten desselben Blatts. Der Parser kann geeignete
synthetische Wiederholungen erkennen; der Nullbefund ist kein leerer Suchlauf.

- `MASKED_OCCURRENCES.tsv`: vollständiges Kandidatenuniversum mit Identitäten,
  maskierten Signaturen und Quellkoordinaten. Seine Größe von etwa 7,6 MB ist
  begründet: Auch der negative Vollständigkeitsbefund soll zeilenweise prüfbar
  bleiben, ohne nur eine Auswahl vermeintlich interessanter Stellen abzulegen.
- `RECURRENT_CONTEXTS.tsv`, `LAYOUT.tsv`, `PAIRS.tsv`, `COMPONENTS.tsv`: gültige
  Tabellen mit Kopfzeile und null Datenzeilen.
- `MASKED_FREEZE.json`: Bindung des eingefrorenen Kandidatenuniversums.
- `RESULT.json`, `VALIDATION.json`: kompakte Ergebnisse, Quellen- und Prüfnachweise.

Die Maskierung ist ein methodischer Ablauf, keine kryptographische Sperre:
Nachbarzeichen bleiben literal erhalten, überlappende Fenster könnten Endwerte
gegenseitig verraten und der Bestand war historisch bereits zugänglich. Es
gibt hier keine Ergebnis-Spalte mit Zielendungen und keine Richtungsstatistik.

## Was daraus folgt und was offen bleibt

**Diese konkrete Umbruchroute ist im registrierten Bestand nicht tragfähig.**
Die Flanken werden nicht nachträglich verkürzt; weder ungefähre Treffer noch
eine andere Endzeichenfamilie oder zusätzliche Seiten werden zur Rettung
nachgeschoben.

Das Ergebnis widerlegt weder die l/m-Zeilenpositionsabhängigkeit aus GDT800–801
noch Schreibvariation, Sprache, Kodierung oder bedeutungslose Erzeugung. Es
belegt auch keine generelle Abwesenheit von Textwiederholungen. Kürzere,
anders segmentierte oder an mehreren Stellen zugleich veränderte Kontexte
liegen außerhalb dieses Tests. Ein Schreibverfahren, das mehrere Nachbarformen
mit dem Umbruch verändert, könnte gerade die geforderte Kontextidentität
verhindern; dies ist eine Grenze der Methode, kein hier bestätigtes Verfahren.

Die Bedeutung und der Mechanismus von l/m bleiben offen. Es gibt keine neue
Normalisierung, Wortbedeutung, Sprache oder semantische Relation. Ein neuer
Versuch braucht einen tatsächlich anderen, vorab begründeten Prüfgegenstand
oder neue belastbare Vergleichsdaten; dieser Lauf wird nicht umgedeutet.
