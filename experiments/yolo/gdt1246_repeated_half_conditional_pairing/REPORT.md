# GDT1246 — kein zusätzlicher Wiederholungsüberschuss; belegte Doppelungen ohne beweglichen Vergleich

**NO_ROBUST_PRIMARY_DIAGONAL_EXCESS.** Der festgelegte deskriptive Vergleich
findet keinen positiven Überschuss identischer Hälften. Die wichtigere Grenze:
**Alle tatsächlich beobachteten Doppelungen liegen in Schichten, in denen ihre
Gesamtzahl unter dem Vergleich unveränderlich ist.** Deshalb ist dies keine
Widerlegung einer Wiederholungsregel. GDT1200s belegte Formen bleiben erhalten;
ein zusätzlicher Wiederholungsterm erhält aus diesem Vergleich keine Motivation.

## Was tatsächlich verglichen wurde

Vollständige, wörtliche Prosa-Gruppen mit Endung dy und gerader Restlänge werden
in U und V gleicher ASCII-Länge zerlegt. Ganze Rohgruppen und bestimmte äußere
Grenzen bleiben erhalten; Zeilenränder sind zugelassen. Die analytische Trennung
ist weder eine erkannte Morphemgrenze noch eine native Buchstabenzählung.

Der feste Vergleich bewahrt pro Lesung Abschnitt, Currier, Hand, Halblänge,
die beiden Zeichen an der inneren Naht und die Zeilenpositionsklasse. Innerhalb
dieser Schichten bleiben die vollständigen linken und rechten Halbformen samt
Häufigkeiten erhalten; nur ihre Paarungen werden ausgetauscht. Längere
Schreibbeschränkungen und gelernte Ganzwortabhängigkeiten sind damit nicht
vollständig kontrolliert. Keine Bedeutungen, Normalisierungen oder nachträglich
ausgewählten Basen gehen ein.

| Lesung | geeignete Gruppen | Schichten | Schichten mit beweglicher Doppelungszahl | beobachtete Doppelungen | bedingter Erwartungswert |
|---|---:|---:|---:|---:|---:|
| ZL3b | 1.986 | 544 | 1 | 7 | 7,857 |
| IT2a | 2.143 | 570 | 2 | 6 | 7,375 |
| RF1b | 1.481 | 453 | 1 | 5 | 5,833 |

Das sind alternative Lesungen desselben Manuskripts, keine drei unabhängigen
Bestätigungen. Die Erwartungswerte sind exakt 55/7,59/8,35/6. Die bedingten
Varianzen sind 6/49,23/64,5/36; sie beschreiben den künstlichen Paarvergleich,
nicht die Unsicherheit einer unabhängigen Manuskriptstichprobe. Es gibt keinen
p-Wert, Signifikanznachweis oder Übersetzungsgrad.

## Manuelle Prüfung der entscheidenden Fälle

Die sieben ZL-Doppelungen sind chchdy, zweimal ololdy, dydydy, dardardy,
alaldy und daldaldy. IT enthält sechs: chchdy, zweimal ololdy, zweimal dydydy,
alaldy. RF enthält fünf: chchdy, zweimal ololdy, zweimal dydydy.
Die bekannten Trennungs-/Entity-Unterschiede bleiben erhalten. Beispielsweise
zählt ITs getrenntes dal daldy nicht als geschlossene Doppelung daldaldy.
Diese Auswahl unterscheidet sich bewusst vom B/By/Bdy-Familienvertrag1200:
hier zählen alle zugelassenen Halbpaare, auch ohne beobachtetes By.

Die nachgelagerte Durchsicht von EVENTS und STRATA zeigt: Sämtliche dieser
Doppelungen gehören zu Schichten mit Varianz null. Ihre Zahl liefert keinen
beweglichen Vergleich. Die wenigen beweglichen Schichten enthalten stattdessen:

- ZL: lkechedy zweimal, checthdy einmal, okechedy viermal.
- IT: dieselben Formen mit Häufigkeiten3/1/4; zusätzlich eeeody und feeedy.
- RF: dieselben ersten drei Formen mit Häufigkeiten3/1/2.

So kann der Vergleich zum Beispiel che mit che zu einer rechnerischen
Doppelung paaren, obwohl das beobachtete Paar che/cth lautet. Diese mögliche
Neupaarung erzeugt den Erwartungswert oberhalb der beobachteten Zahl. Daraus
folgt weder eine allgemeine Vermeidung von Wiederholung noch die Zulässigkeit
des künstlich erzeugten Wortes in der ursprünglichen Schrift. Insbesondere
wurde kein che-, dy- oder anderer Bedeutungswert angenommen.

Beim Weglassen jeweils eines physischen Blattes bleibt beobachtet-minus-erwartet
zwischen −0,857 und0 in ZL, zwischen −1,375 und−0,5 in IT sowie zwischen−0,833
und0 in RF. Die83/82/82Blattlöschungen sind Sensitivitätsprüfungen am exponierten
Bestand, keine neuen Vorhersagen. In je einer ZL- und RF-Löschung fällt die
Varianz aufnull. Kein ausgewähltes Blatt oder Leser wurde zum Erfolgskriterium
nachgereicht.

## Was die Designkorrektur bedeutet

IDEA968s voriger synthetischer Beweis bleibt richtig: ganze Basis kopieren,
ein Merkmal an zwei Stellen realisieren und eine vollständige Form nachschlagen
können dieselben Ausgaben erzeugen. Kein Paarungswert identifiziert dann den
inneren Schreibvorgang. Dies verbietet jedoch nicht grundsätzlich eine getrennte,
eng begrenzte Beschreibung von Paarabhängigkeit. GDT1246 prüft nur diese engere
Frage; es behauptet keine Wiederöffnung der Mechanismusidentifikation.

Der Ausgang beantwortet diese engere Frage nicht positiv und zeigt wenig
Vergleichsspielraum gerade an den motivierenden Formen. Entscheidung: keine
Lockerung der Schichten, neue Endung, andere Trennung oder Kopierregel anschließen.
Kein großer Schreiber- oder Decoderbau. GDT1200s Formen,608s gerichteter Wortbau
mit Ganzformresten und983s fehlender Expansionsvergleich bleiben unverändert.

## Reproduktion und Grenzen

Lokale Bindung am6.Oktober2026 um23:23:11UTC vor diesem Lauf. Alle Quellen waren
bereits exponiert, die Idee entstand aus bekannten Beispielen. Die Metadaten-
und Nahtkontrollen wurden vor Auswertung festgelegt. Dies ist keine unabhängige
Bestätigung und keine historische Erstentdeckung.

Der Runner berechnet die exakten rationalen Momente aus den Häufigkeiten. Der
separat geschriebene Validator berechnet sie über Kovarianzen geordneter
Positionen, überprüft fünf vollständig enumerierte kleine Permutationsfälle und
rekonstruiert alle5.610Ereignisse,1.567Schichten und247Blattlöschungen aus einer
neuen bewachten Projektion der Originalquelle. PASS am23:23:44UTC. Beide stammen
vom selben Autor und teilen Quelle und Annahmen; das ist Rechen-/Quellentreue,
keine unabhängige sprachliche Bestätigung. Die manuelle Nullvarianz-Einordnung
steht nach dem Ergebnis und ist kein nachträglich verändertes Erfolgskriterium.

Keine neuen Seiten, Bilder, Wörter oder Bedeutungen; f84/f84r/f116v und Reserven
bleiben geschlossen. Keine semantische Relationskante bewertet. Der gesamte
Arbeitsblock endet innerhalb des23:55UTC-Budgets; Abschluss im bestehenden Dossier.
Die geforderten zehn Arbeitsstunden sind damit nicht erfüllt. Lokaler Checkpoint,
kein Commit oder Push. Unveränderte Altfehler werden nicht als behoben ausgegeben.

Reproduktion: Manifestbefehle in einer isolierten Kopie mit leerem Ausgabeordner
verwenden, REGISTRATION_LOCK.json erhalten. Der Runner überschreibt RESULT nicht.
