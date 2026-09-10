# GDT911 — sechs Verse bestimmen noch keinen eindeutigen Wortlaut

**EXPOSED_SIX_VERSE_COLLISION_CONFIRMED.** Ein bestimmtes Silbenmodell lässt
für denselben verschlüsselten Sechsvers-Ausschnitt zwei grammatische und
metrische Lesungen zu, die sich in einer Eigenschaft unterscheiden: kalt oder
heiß. Dies ist ein Befund an einem konstruierten historischen Kontrolltext.
Es wurde keine Voynich-Lesung gefunden oder geprüft.

## Konkreter Nachweis

Die historische Ausgangsstelle ist Macer Floridus, Ausgabe Choulant1832,
Verse716–721, gedruckte Seiten57–58. Ihr erster Vers lautet:

> Virtus est illi siccans et frigida valde

Sinngemäß: Die Pflanze besitzt eine trocknende und sehr kalte Wirkung.
Die konstruierte Gegenlesung ersetzt einzig **frigida** durch **fervida**:
Sie besitzt eine trocknende und sehr heiße/brennende Wirkung. Diese zweite
Aussage ist **keine überlieferte Textvariante** und keine Behauptung über die
wirkliche Heilpflanze oder ihre Wirkung.

Die festgelegte Schreibregel ordnet jedem wiederkehrenden Symbol genau eine
orthographische Silbe zu, injektiv und durch den gesamten Ausschnitt gleich.
Die zwei vollständigen Schlüssel unterscheiden sich nur so:

| Symbol | Schlüssel A | Schlüssel B |
|---|---|---|
| C09 | fri | fer |
| C10 | gi | vi |

Alle übrigen72 Zuordnungen stimmen überein. Beide Schlüssel ergeben genau
denselben Chiffretext mit43 Wörtern,92 Silbenvorkommen und74 Symboltypen. Die
Wortgrenzen bleiben erhalten, die Versgrenzen sind im Chiffretext entfernt.
Die nur einmal vorkommenden Silben fri und gi können hier gegen fer und vi
getauscht werden, ohne mit einer anderen Silbe zu kollidieren.

Beide Wörter füllen denselben daktylischen Fuß: **lang–kurz–kurz**. Bei frīgĭda
ist die erste Silbe von Natur lang; bei fervĭda macht rv die erste Silbe
positionslang. Beide Adjektive stimmen mit virtus überein. Auch die anderen
fünf Verse behalten ihren Wortlaut und ihr Versmaß. Der vollständige
[Chiffretext, beide Schlüssel und sämtliche Scans](artifacts/CERTIFICATE.md)
sind nachprüfbar, ebenso das [maschinenlesbare Ergebnis](artifacts/RESULT.json).

## Was der Versuch beantwortet

Das Beispiel zeigt, dass die gewählte Kombination aus injektiver
Silbenzuordnung, grammatischer Verträglichkeit und Hexameter für **diesen
Ausschnitt** keine eindeutige Lesung garantiert. Selbst bekannte Versgrenzen
lösen die Mehrdeutigkeit nicht; das Entfernen dieser Zusatzinformation kann
sie deshalb nicht beseitigen. Es wurde keine vollständige Suche über alle
lateinischen Lesungen durchgeführt. Nachgewiesen sind mindestens zwei.

Die allgemeine Gefahr plausibler falscher Klartexte war aus GDT606 und
GDT832–837 bekannt. Neu ist nur dieser konkrete, vollständig offengelegte
Silben-/Versmaß-Nachweis. Er rechtfertigt keine große Decoderentwicklung mit
der Annahme, Versmaß würde Bedeutungen bereits eindeutig festlegen. Er
widerlegt weder metrisches Latein im Voynich noch die Möglichkeit, mit mehr
Text oder unabhängigen Schrift-/Bedeutungsbindungen Eindeutigkeit zu erreichen.

## Grenzen und Prüfung

Dies ist **kein Blindtest**. Quelle und vorgeschlagene Gegenlesung waren vor
Berechnung und Veröffentlichung bekannt. Statt der zunächst vorgeschlagenen
Entschlüsselung einer unabhängigen Sechsvers-Probe wurde dieser kleinere,
quellenoffene Mehrdeutigkeitsnachweis ausgeführt. Die vorgesehene blinde
Wiedergewinnung unbekannten Wortlauts und die Prüfung an Voynich bleiben
unausgeführt. Eine Trefferquote oder erfolgreiche Entschlüsselung wird daraus
nicht abgeleitet.

Die sechs Verszeilen sind kein vollständiges historisches Rezept: Vers721
wird in722–723 durch eine ausdrückliche Anwendungsbedingung fortgesetzt;
der Pflanzenbezug am Anfang stammt ebenfalls aus dem Kontext. Die
Gegenlesung ist grammatisch/metrisch möglich, aber damit noch nicht
medizinisch oder historisch gleich plausibel. Ein unabhängig erkannter
Pflanzenbezug oder weitere Textstellen könnten sie verwerfen.

Eine separate Prüfung bestätigte Quelle, Silbengleichheiten, Grammatik und
alle sechs Scans. Die Mengenberechnung wurde zusätzlich ohne Import des
Hauptprogramms geprüft. Der Prüfer bestätigt das konkrete Zertifikat, keinen
vollständigen lateinischen Grammatik- oder Quantitätenlexikon-Decoder.
Die Quantitätenanalyse ist manuell; in podagrae wird die gewöhnliche
positionslange Behandlung vor gr ausdrücklich benutzt. Die während der
Prüfung korrigierte Deklinationsangabe zu virtus (dritte, nicht vierte)
verändert weder Quantität noch Schlüssel. [Unabhängiger Audit](src/INDEPENDENT_AUDIT.md),
[Prüfergebnis](artifacts/VALIDATION.json).

Keine neue Voynich-Abbildung, Transkriptionszeile, reservierte Passage oder
f84/f84r wurde geöffnet. Die98 BPE-Einheiten aus GDT605 motivieren nur die
Obergrenze des gedachten Codes; sie beweisen keine Silbenschrift. Die
abgeschlossenen Modelle GDT884 und GDT906 bleiben unverändert. Bestätigte
neue Manuskriptwörter: **0**.

## Reproduktion und Quellen

```
python3 experiments/yolo/gdt911_syllabic_metre_identifiability/src/run.py
python3 experiments/yolo/gdt911_syllabic_metre_identifiability/src/validate.py
```

[Choulants Primärausgabe1832](https://api.worldherblibrary.org/pdf/De-viribus-herbarum-compressed.pdf),
[beigefügte Seite57](artifacts/SOURCE_PAGE_73.png) und
[Seite58](artifacts/SOURCE_PAGE_74.png). Der Hash der vollständigen Quelldatei
steht in SPEC.json. Die Haupttextzeilen und die anschließende Bedingung stehen
in SOURCE_EXCERPT.txt; OCR und Variantenapparat werden nicht vermischt.

[Quellengebundene Quantitäten und Bedeutungen](src/LEXICAL_NOTES.md) mit Lewis
und Short1879, frigidus/fervidus; gewöhnliche Quantitätenregeln nach
[Allen und Greenough](https://dcc.dickinson.edu/grammar/latin/quantity-syllables).
[Protokoll und Entscheidung](METHOD.md),
[Offenlegung der Quellenkenntnis](PREREGISTRATION.md).
