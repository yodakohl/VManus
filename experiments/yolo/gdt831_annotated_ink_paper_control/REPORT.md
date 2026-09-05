# GDT831 — neue Bildreferenzen; feste Papierkontrolle verfehlt

2026-09-05. **HELD_POINT_CONTROL_FAIL**. Der registrierte Detektor erkennt
alle ausgewählten Schriftkerne, verfehlt aber auf f81r die vorher festgelegte
Papier-Spezifität. Diese konkrete Kombination aus Messregel und
Kalibrierungsverfahren besteht den Kontrollversuch nicht.

## Beobachtungen und festgelegtes Ergebnis

Zwei getrennte visuelle Modellprüfer haben auf 24 festen Ausschnitten aus vier
bereits freigegebenen Original-JPEGs insgesamt 192 einzelne Pixel annotiert:
je Ausschnitt vier klare Schriftkerne und vier benachbarte Papierpunkte.
Beide prüften ihre Markierungen am Bild; ein weiterer Modellprüfer betrachtete
alle 24 endgültigen Koordinatenbilder. Kein Prüfer sah dabei Detektorausgaben.
21 anfängliche Koordinatenschätzungen wurden vor der Messung visuell korrigiert;
Details stehen in den beiden Annotierungsberichten. Die ursprünglichen
Entwürfe sind nicht separat eingefroren; die endgültigen Koordinaten sind es.

Präregistrierung, sämtliche 192 Koordinaten, Quellen und beide Rechenprogramme
wurden mit **5aa88a56** veröffentlicht, bevor Klassifikatorwerte aus den
Manuskriptbildern berechnet wurden. Die 14 Dateien des Registrierungsschlosses
blieben danach unverändert. Es gibt keine nach Ergebnis entfernten Punkte.

Die feste Regel wählt auf f76r/f77r eine relative Dunkelheitsschwelle von
**0,03**. Sie ist der kleinste zugelassene Gitterwert, der auf beiden
Kalibrierungsseiten mindestens 95% der Papierpunkte richtig klassifiziert.
Diese Kalibrierung wurde gespeichert, bevor f81r/f83r ausgewertet wurden.

| Seite | Rolle | Schriftkerne richtig | Papierpunkte richtig | Seitenkriterium |
|---|---|---:|---:|---|
| f76r | Kalibrierung |24/24|23/24 =95,83%|bestanden|
| f77r | Kalibrierung |24/24|23/24 =95,83%|bestanden|
| f81r | Prüfung |24/24|22/24 =91,67%|**verfehlt**|
| f83r | Prüfung |24/24|23/24 =95,83%|bestanden|

Alle einzelnen Ausschnitte bestehen ihre gröbere 3/4-Regel je Klasse.
Entscheidend bleibt das zusätzliche Seitenkriterium: mindestens 22/24
Schriftkerne und 23/24 Papierpunkte je Seite. f81r verfehlt es um einen
Papierpunkt. Insgesamt sind 48/48 Schriftkerne und 45/48 Papierpunkte auf den
Prüfseiten richtig. Diese gepoolte Zahl ersetzt das Seitenkriterium nicht.
Konstant alles als Papier oder alles als Schrift zu klassifizieren scheitert
an der gemeinsamen Anforderung.

Die fünf Fehler über Kalibrierung und Prüfung sind ausschließlich als Papier
annotierte Punkte, die der Detektor als Schrift klassifiziert:

| Punkt | Relative Dunkelheit |
|---|---:|
| f76r_B2L_P4 |0,041451|
| f77r_B3L_P2 |0,035714|
| f81r_B1L_P3 |0,115385|
| f81r_B3L_P1 |0,043956|
| f83r_B2R_P2 |0,060109|

Ihre Werte stehen ungerundet mit allen anderen Punkten in FEATURES.tsv.
Keiner wird nachträglich umetikettiert; keine andere Schwelle wird gesucht.

## Was wir damit wissen

Die 14 gebundenen Registrierungsdateien und die 192 neuen visuellen Punktreferenzen
liefern eine nachvollziehbare Beobachtungsprüfung. Die eingefrorene
Median3/Median31-Messung mit realem 16-Pixel-Umfeld trennt die meisten dieser
klaren Stellen, erfüllt die gewählte Anforderung aber nicht auf jeder der
beiden Prüfseiten. Das ist erheblich enger als die Behauptung, Bildmessungen seien generell
unbrauchbar oder Federinformation fehle. Ebenso wäre ein knapper Kontrollfehler
kein Grund, das Kriterium nachträglich zu senken.

Die Auswahl ist absichtlich auf klare Schriftkerne und visuell freie
Papierzentren begrenzt. Sie ist keine zufällige Pixelstichprobe, keine
vollständige Schriftmaske und keine mikroskopische Bestimmung von Tinte.
Dünne/fahle Striche, Ränder, mögliche Durchscheinspuren und andere unsichere
Bereiche sind nicht quantitativ validiert. Die Papierpunkte des zweiten
Annotators liegen oft näher an Strichen; diese bereits vor der Auswertung
festgehaltene Auswahlabweichung bleibt bestehen. Seiten- und Annotatoreffekte
lassen sich in diesem Versuch nicht trennen. Eine unabhängige menschliche
Annotierung oder Übereinstimmungsstudie wurde nicht vorgenommen.

Die Fotos waren früher bereits betrachtet worden. Gehalten sind nur die
neuen f81r/f83r-Labels gegenüber der skalaren Kalibrierung. 192 benachbarte,
gezielt ausgewählte Punkte bedeuten keine 192 unabhängigen Manuskriptproben;
es wird keine entsprechende Signifikanz oder Populationsgenauigkeit behauptet.

## Rechenprüfung und Konsequenz

Zehn synthetische Prüfungen bestehen: strukturiertes, geneigtes Papier ohne
Striche; eingesetzte Striche verschiedener Breiten und Richtungen;
Beleuchtungswechsel; die ausdrücklich gezeigte Grenze bei dichten dunklen
Flächen; korrektes reales Filterumfeld; unabhängige Medianrechnung; sowie
Kalibrierungs-, Schwellen- und Seiten-/Ausschnittentscheidungen. Diese Prüfungen
ersetzen das reale Ergebnis nicht. Verwendet wurden NumPy 1.26.4 und Pillow 10.2.0.

Der unabhängige Validator bestätigt alle 14 Registrierungshashes, vier
JPEG-Hashes und 24 native Ausschnitthashes. Er berechnet sämtliche 192
Punktwerte mit eigenen NumPy-Nachbarschaftsmedianen nach, ohne den Runner
oder dessen Pillow-Filter aufzurufen, und rekonstruiert Schwelle sowie alle
Entscheidungen. Ergebnis: PASS für die Rechnung, unverändert FAIL für die
registrierte Kontrolle. VALIDATION.json hält diesen Prüfumfang fest. Auch
der vollständige unveränderte Runner-Replay aus den Originalpixeln stimmt
bytegenau mit seinen gespeicherten Artefakten überein.

Die neue Fehlerquote darf nicht direkt mit GDT830s 64,6757% Vordergrund auf
einem ganzen leeren Papierfeld verglichen werden: Auswahl, Nenner und
Fragestellung unterscheiden sich. Ein allgemeiner Leistungsgewinn wurde
nicht an einer gemeinsamen unabhängigen Stichprobe gemessen.

Die auf GDT831 begrenzte Prüfung des bereitgestellten Veröffentlichungsstands
besteht. Der vollständige Repository-Audit meldet weiterhin ausschließlich
die schon bestehende GDT600-Bindungs-/Indexschuld; sie wurde nicht verändert.

GDT831 endet an seinem registrierten Papierkriterium. GDT830 bleibt
abgeschlossen; es wird keine alte Fortsetzungsrate mit der neuen Messung
berechnet. Eine belastbare Federzustandsmessung und Schreibreihenfolge sind
weiterhin offen. Es gibt keine Bewertung strittiger Blöcke, Änderung von
Transkription oder Lesefolge, keine Sprachzuordnung und keine Übersetzung.
Keine neue Seite wurde geöffnet, f84/f84r bleiben geschlossen. Keine Suche
nach öffentlichen Entzifferungsansätzen und keine fremden LLM-API-Schlüssel.
