# GDT1172 — die vollständige wörtliche Musikvorlage passt nicht

**COMPLETE_LITERAL_INSTRUCTION_COUNT_CONTRADICTED.** Die vollständige
Anleitung auf Harley978 f11v hat86 Quellenwörter. IDEA871 verlangt für dieselbe
Anleitung genau62 Wortgruppen im festgelegten ZL-Absatz f83r.31–44 und
unveränderte Wortgrenzen. Diese notwendige Bedingung scheitert. Beide Varianten
des Vorschlags — englisches Lied oder lateinischer Liedtext, jeweils mit
derselben vollständigen Anleitung — scheitern damit bereits am gemeinsamen
Anleitungsteil. Es wurde kein Voynich-Wort übersetzt.

| Vollständiger Quellenbereich | Gelesene Wörter |
|---|---:|
| Schwarzer Anleitungskasten, R01–R05 |62|
| Obere rote Begleitanweisung, R06 |10|
| Untere rote Begleitanweisung, R07 |14|
| Gesamte verlangte Anleitung |86|
| Fester ZL-Zielabsatz des Vorschlags |62|

Der schwarze Kasten **allein** hat tatsächlich ebenfalls62 Wörter. Das ist eine
erhaltene Teilübereinstimmung, kein erfolgreicher Test: Die ursprüngliche Karte
verlangt ausdrücklich sämtliche Ausführungsanweisungen; das gebundene
Quelleninventar schließt beide roten Texte ein. Nur den schwarzen Kasten zu
wählen oder24 Wörter zu verbergen würde den geprüften Vertrag ändern. Es gibt
keinen Codefit, keinen Test wiederkehrender Wortidentitäten und keine
nachträgliche Auswahl dieser Teilvorlage. Eine bloße gleiche Anzahl würde
ohnehin weder Liedinhalt noch Quellenidentität bestimmen.

## Manuelle Quellenprüfung

Die [vollständige Originalabbildung](artifacts/HARLEY978_F11V.jpg) stammt aus
der [British Library](https://www.flickr.com/photos/britishlibrary/12458897473).
Der frühere lokale Cache war nicht auffindbar. Dieselbe öffentliche Datei wurde
erneut bezogen; ihre981730 Bytes und SHA256 stimmen exakt mit dem vorhandenen
[Quellenbeleg](../../../research_registry/work_batches/ten_hours_20260915/ROTA_SOURCE_EVENTS.md)
überein. Das ist derselbe Zeuge, keine unabhängige neue Handschrift.

Root las den ganzen Quellenbereich am Bild und in einer vergrößerten Ansicht.
[SOURCE_WORDS.json](artifacts/SOURCE_WORDS.json) bewahrt sämtliche elf physischen
Textzeilen. Die Wörter paucioribus und Tacentibus laufen jeweils über einen
Zeilenumbruch und werden je einmal gezählt. Kontraktionen bleiben ein
geschriebener Wortträger; ausgeschriebene Buchstaben erzeugen keine weiteren
Wörter. Die vollständigen R01–R07 ergeben6/17/12/14/13/10/14 Wörter.

Die gelesenen lateinischen Wörter dienen im Inventar als Ortsbezeichnungen,
**nicht als behauptete diplomatische Glyphentranskription**. Ihre Trennung
berücksichtigt lesbares Latein und die Schrift, nicht einen automatischen
Abstandsschwellenwert. Enge Schriftabstände werden nicht als Erlaubnis zum
Zusammenziehen beliebiger Quellenwörter behandelt. Die bekannten Lesarten
Canitur/Cantatur, repetit/repetat, dicit/dicat und vel/aut ändern die Anzahl
nicht. Eine unabhängige paläographische Begutachtung liegt nicht vor.

Die englischen/lateinischen Liedtexte wurden nicht kollationiert. Der vorab
festgelegte erste Widerspruch beendet diesen Versuch vor Wiederholungsprüfung,
Notenunterlegung und Decoder. Es wäre unnötig, weitere Teilauswertungen für
eine bereits gescheiterte notwendige Verknüpfung zu erzeugen.

## Tragweite und Vorwissen

62 ist die **bestehende ZL-Projektion** des Vorschlags, keine hier neu gelöste
diplomatische Absatzgliederung. GDT1022 behält zwei unsichere Schreibungen;
IT hat60 Gruppen im entsprechenden Ausschnitt innerhalb eines92-Gruppen-
Absatzes; RF liefert dort keine eigenen Absatzgrenzen. Diese Lesungen werden
weder zusammengelegt noch als weitere negative Tests gezählt. Keine neue
Voynich-Zeile, Abbildung oder Reserve wurde geöffnet; f84/f84r/f116v bleiben
ausgeschlossen.

GDT1022s ausführbare Musikgeschichte mit53 angenommenen Bedeutungen bleibt ein
bedingtes Ergebnis. GDT1024s18 neue Bedeutungen/sechs Konstruktionen und
GDT1041s gescheiterte Erweiterung bleiben ebenfalls erhalten. GDT970s
Notenereignis-Code und GDT911s Silbenmehrdeutigkeit sind andere Verträge.
Hier neu ist nur die Prüfung der konkreten, bisher ungetesteten IDEA871-
Kopierbedingung. Musik allgemein, Abkürzungen, Übersetzungen einer Vorlage
oder bedeutungsvoller Voynich-Text werden dadurch nicht widerlegt.

Der erweiterte lateinische Quellentext war vor Auswahl bekannt; der Prüfer
erwartete eine mögliche Abweichung. Das lokale Protokoll wurde vor dem neuen
Bildabruf/der manuellen Zählung versiegelt und wird zusammen mit dem Ergebnis
veröffentlicht. Kein vorheriger öffentlicher Freeze, keine Blindheit, kein
p-Wert und keine unabhängige Entzifferung werden behauptet.

Der [separate Validator](src/validate.py) importiert das Zählprogramm nicht:
Er setzt die Zeilenfragmente wieder zusammen, extrahiert unabhängig die sieben
älteren Quellenklauseln und gleicht jeden Wortplatz samt bekannten Varianten,
Bildhash, Protokollhash und Resultat ab. [VALIDATION.json](artifacts/VALIDATION.json):
PASS. Das überprüft die Umsetzung; beide Programme und die Bildlesung stammen
vom selben Autor. Es ist keine zweite unabhängige Quellenlesung.

## Entscheidung

Die feste vollständige Kopierhypothese wird geschlossen. Kein Decoder und
keine neue Musikglosse folgen. Eine andere Quellenabgrenzung/Schreibregel müsste
eigenständig begründet und mit anderer vorher festgelegter Konsequenz geprüft
werden; diese Niederlage würde dadurch nicht gelöscht. Der passende Teilwert62
allein begründet keinen solchen Vorrang. Bestätigte neue Manuskriptwörter:0.

Reproduktion:

```
python3 experiments/yolo/gdt1172_literal_rota_source_word_contract/src/run.py
python3 experiments/yolo/gdt1172_literal_rota_source_word_contract/src/validate.py
```

Vorbereitung/Auswahl geschätzt15–20Minuten; kein exakter Starttimer. Lokaler
Freeze17:46:30UTC, Quellabruf danach; Durchführung und Prüfung vor18:00UTC.
Das inklusive Publikationscheckpoint18:22UTC bleibt in METHOD.md gebunden;
der abschließende Commit dokumentiert die tatsächliche Veröffentlichung.
