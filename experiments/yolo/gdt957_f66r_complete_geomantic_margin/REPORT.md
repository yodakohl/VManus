# GDT957 — 32 vollständige hypothetische Rechnungen, keine gewählte Wortbedeutung

Die vollständige15-Wort-Randliste von f66r verträgt das festgelegte geomantische Rechenverfahren. In der vollständig lesbaren IT2a-Fassung bleiben **16 Rechnungen je Leserichtung**, insgesamt32 Kandidaten mit ihrer Richtung, übrig. Die zwei anderen Editionen enthalten je zwei unverändert unbekannte Gruppen. Alle sechs Fälle bleiben erhalten; kein passender Ausschnitt wurde ausgewählt.

**Der Fit identifiziert diese Liste nicht als Geomantie:** Ihre15 IT2a-Wörter sind sämtlich verschieden. Jede beliebige Liste aus15 verschiedenen Wörtern hätte genau dieselben16 Rechenlösungen je Richtung. Das ist eine exakte Umbenennungsinvarianz, kein geschätzter Nulltest. Kein Wort hat in den verbleibenden Rechnungen nur eine mögliche Figur. Es gibt keinen bevorzugten Kandidaten, keine unabhängige Bestätigung und kein übersetztes Voynichwort.

| Edition / Richtung | bekannte Positionen | unbekannt | vollständige Rechenmöglichkeiten | Ergebnis |
|---|---:|---:|---:|---|
| ZL3b oben→unten |13|2|76|nur unaufgelöste Möglichkeiten|
| ZL3b unten→oben |13|2|152|nur unaufgelöste Möglichkeiten|
| IT2a oben→unten |15|0|16|vollständig kompatible Hypothesen|
| IT2a unten→oben |15|0|16|vollständig kompatible Hypothesen|
| RF1b oben→unten |13|2|60|nur unaufgelöste Möglichkeiten|
| RF1b unten→oben |13|2|56|nur unaufgelöste Möglichkeiten|

## Konkrete Lesungen und Vorhersagen

[Alle32 vollständigen benannten Lesungen](artifacts/ALL_COMPLETE_NAMED_READINGS.tsv) enthalten jede der15 Figuren für jeden Kandidaten. Die Positionen folgen der jeweils angegebenen Leserichtung. [Die90 Positionszeilen](artifacts/POSITION_CONSEQUENCES.tsv) ordnen jede Konsequenz dem unveränderten tatsächlichen Locus und Rohwort zu und nennen alle möglichen Figuren. [Alle Kandidaten](artifacts/ALL_CASES.json) und [alle überlebenden Rechnungen](artifacts/ALL_SURVIVING_CALCULATIONS.tsv.gz) enthalten auch die unbekannten ZL/RF-Stellen; deren ergänzte Figuren sind Vorhersagen, keine entzifferten Gruppen.

Beispiel ohne Vorrang: IT2a oben→unten, lexikographisch erste Mutterfolge, Kandidat18557:

| Locus | Rohwort | bedingte Figur |
|---|---|---|
|f66r.1|rary|Rubeus|
|f66r.2|rals|Laetitia|
|f66r.3|qor|Caput draconis|
|f66r.4|dara|Puer|
|f66r.5|ykcol|Acquisitio|
|f66r.6|syly|Puella|
|f66r.7|salf|Albus|
|f66r.8|fary|Fortuna major|
|f66r.9|qotesy|Fortuna minor|
|f66r.10|ykaly|Amissio|
|f66r.11|daoly|Cauda draconis|
|f66r.12|raiin|Tristitia|
|f66r.13|qokal|Conjunctio|
|f66r.14|qolsa|Via|
|f66r.15|raral|Carcer|

Diese Bezeichnungen sind Namen der hypothetischen geomantischen Figuren. Daraus folgt beispielsweise nicht `rary = rot` oder `raral = Gefängnis` im Voynichtext. Der Kandidat erklärt vier Eingaben, ihre vier transponierten Figuren und sieben daraus berechnete Ausgaben. Er erklärt weder das Befragungsthema noch die übrige Seite.

In allen16 IT2a-Rechnungen einer Richtung kommt jede von15 verschiedenen Figuren einmal vor; allein Populus fehlt. Bei der Richtung oben→unten müsste `raral` als Urteil eine der Figuren Acquisitio, Conjunctio, Carcer oder Amissio sein; unten→oben betrifft diese Einschränkung `rary`. Keine dieser Alternativen wird durch die Liste gewählt. Planet-, Haus- und Zukunftsaussagen wurden nicht aus den Namen übernommen.

## Quelle, Datenabgrenzung und Widersprüche

Die Quelle ist Turners1655-Übersetzung des Agrippa zugeschriebenen [*Of Geomancy*](https://www.princeton.edu/~ezb/geomancy/agrippa.html). Geprüft ist ausschließlich das dort beschriebene allgemeine Verfahren: vier Mutterfiguren, vier durch Zeilentransposition erzeugte Töchter und sieben Paritätskombinationen. Seine anschließend vorgeschlagene alternative astrologische Hausanordnung wurde nicht getestet. Die frühe Cod.Sang.756-Parallele bleibt eine partielle Quellenstütze; eine vollständige frühe Verfahrensbindung wurde nicht behauptet. Zwei getrennte native Lesungen stimmen bei allen16 benannten Punktfiguren überein.

[Die öffentliche Registrierung](PREREGISTRATION.md), Commit8d017cb3d, lag vor der Rohgruppenentnahme und Enumeration. Frühere Projektexposition einschließlich des ganzen f66r-Bildes und der ersten drei alten bereinigten Wortformen wird darin offengelegt. Die Auswahl als15er-Liste war explorativ; nicht nachträglich verblindet. GDT515s feste Randregel liefert Loci1–15.34 einzelne Randzeichen,32 Haupttextzeilen und der untere Nachtrag bleiben außerhalb dieses einen Registermodells. Das ältere Randhierarchie-Originalreport fehlt im Checkout; aktuelle Metadaten und GDT515s Primärcode wurden separat geprüft.

Alle65536 möglichen Mutterkombinationen wurden vollständig erzeugt. Jedes gleiche bekannte Wort muss dieselbe Figur, jedes verschiedene bekannte Wort eine andere Figur bezeichnen. Keine Widersprüche bleiben innerhalb der aufgeführten überlebenden Rechnungen. Die verworfenen Rechnungen und die sie ausschließenden Gleichheits-/Ungleichheitsbedingungen sind über [vollständige Quellvorhersagen](artifacts/ALL_SOURCE_PREDICTIONS.tsv.gz) und [kumulative Ausschlüsse](artifacts/CONSTRAINT_ELIMINATION.tsv) nachvollziehbar. Unbekannte Rohgruppen wurden weder normalisiert noch repariert.

## Entscheidung und Prüfung

Die32 vollständigen Rechnungen werden als bedingte Lesungskandidaten behalten. **Keine Figurenzuordnung wird als Arbeitsübersetzung übernommen.** Eine Fortsetzung benötigt eine zusätzliche, separat festgelegte Konsequenz für gerade diese Wörter oder einen weiteren vollständig abgegrenzten Rechengang mit derselben Zuordnung. Eine weitere15er-Zählung, ein schöner formulierter Kandidat oder die Wahl nach Neustart-Einigkeit ändern die Entscheidung nicht. Die zunächst erwogene15-Wort-Absatzsuche wurde nicht durchgeführt.

Die unabhängige Implementierung erzeugt alle65536 Rechnungen erneut mit Bitvektoren und prüft Quellprojektionen, sechs Fälle, sämtliche Kandidaten, Positionsmengen und komprimierte Tabellen: [VALIDATION.json](artifacts/VALIDATION.json), PASS ohne Abweichung. Auch die Umbenennungsinvarianz wurde kontrolliert. Diese Validierung prüft Rechen- und Datenkorrektheit, keine Manuskriptbedeutung. Ein einziges bereits exponiertes physisches Blatt bietet0 unabhängige Bestätigungsblätter; die drei Transkriptionen zählen nicht als Replikationen. Keine Signifikanzbehauptung, keine Reservenöffnung, keine Änderungen alter Experimente.
