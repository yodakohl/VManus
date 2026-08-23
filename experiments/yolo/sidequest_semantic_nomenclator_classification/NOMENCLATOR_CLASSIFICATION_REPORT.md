# Was ein Lehrling tatsächlich lernen muss

## Ergebnis

Die 487 sichtbaren Oberflächen sind jetzt nach der **Lernhandlung** klassifiziert, nicht bloß nach ihrer derzeitigen deutschen Lesung.

- **233 Oberflächen / 476 von 776 Gruppen** sind mit Besitzer vollständig aus der kleinen Grammatik bildbar.
- **166 Oberflächen / 187 Gruppen** sind Mischformen: ein bekannter Kern hilft, aber ein lokaler Körper oder Rest muss gelernt werden.
- **88 Oberflächen / 113 Gruppen** sind echte Ganzkarten ohne produktive Zerlegung.

Damit sind 61,3 Prozent der tatsächlich geschriebenen Gruppen regelhaft erzeugbar, 24,1 Prozent teilregelhaft und 14,6 Prozent reine Nomenklatorwerte. Das ist eine realistische Werkstattmischung: Die häufige Prosa wird stark komprimiert, während die seltenen Stern- und Diagrammnamen den großen Karteikasten bilden.

## Die 13 praktischen Klassen

| Klasse | Typen | Gruppen | Lernhandlung |
|---|---:|---:|---|
| produktiver Brevigraf | 86 | 167 | sichtbare Kerne direkt zusammensetzen |
| bekannter Kern + produktiver Rand | 98 | 167 | Kern aus der 25er-Liste nehmen, Argument/Grad/Schluss anfügen |
| Renderer-Allograph | 19 | 93 | q/s/ch/d/t-Rahmen abziehen, dann denselben Wert lesen |
| produktive Astrokomposition | 13 | 20 | Kerne lesen, Besitzer ergänzt Stern/Ring/Platz |
| nacktes produktives Kernzeichen | 5 | 17 | `ain`, `air`, `ar`, `cheo`, `ot` direkt lesen |
| gebundene Modifierkomposition | 12 | 12 | Grundwert plus E/EE/Y/DY-Regel lesen |
| lokaler Astrowert mit einem Kernhinweis | 123 | 143 | ganzen lokalen Namen lernen; Kern nur als Gedächtnishilfe |
| lokaler Astrowert mit mehreren Hinweisen | 28 | 28 | ganzen lokalen Namen lernen; bekannte Relation als Teilhinweis nutzen |
| lokaler Astro-Ganzwert | 74 | 84 | mit Ring/Sternplatz komplett lernen |
| Prosa-Ganzkarte | 14 | 29 | komplett lernen; längster Eintrag blockiert Teilung |
| gelernter Körper + produktiver Rand | 6 | 7 | kleinen Fachkörper plus Rand lernen |
| produktiver Rahmen + gelernter Körper | 7 | 7 | Rahmen lesen, Körper aus dem Nomenklator einsetzen |
| noch nicht beförderte Mehrkernfolge | 2 | 2 | provisorisch als lokale Karte lernen |

## Prosa und Himmel verhalten sich verschieden

Die Prosa ist inzwischen fast eine echte Kurzgrammatik: **347 von 381 Gruppen** sind aus den produktiven Kernen oder ihren Renderer-Allographen vollständig bildbar; 14 sind Mischformen und 20 reine Ganzkarten. Das erklärt, warum dieselben Arbeitskarten auf den Pflanzen- und Badseiten ständig wiederkehren.

Die Astroseiten tragen dagegen vor allem Namen und Adressen. Nur **129 von 395 Gruppen** sind vollständig produktiv, 173 tragen einen brauchbaren Kernhinweis, und 93 müssen als lokale Ganzwerte gelernt werden. Das ist kein Scheitern des Modells: Eine Stern- oder Sektorbezeichnung ist genau der Teil, den ein Nomenklator oder eine Tabelle auswendig speichern soll.

## Wichtige Korrektur gegenüber einem zu großzügigen Parser

Ein Astrowort wie `airchy` wird nicht automatisch vollständig aus `AIR` erzeugt. `AIR` ist sichtbar und hilft als **Lauf/Bahn**, aber `chy` bleibt lokal; die ganze Oberfläche muss im Sternregister gelernt werden. Nur wenn die Oberfläche selbst der Kern ist (`air`) oder eine belegte Familienregel den Rest erklärt, gilt die Form als vollständig produktiv.

Diese Korrektur verhindert, dass bloßes Teilstringfinden als Übersetzung ausgegeben wird, ohne in den strengen wissenschaftlichen Modus zurückzufallen. Für die Werkstatt heißt es einfach: *Bekannten Teil sprechen, unbekannten Rest aus der lokalen Liste lernen.*

## Wo Renderer sitzen

Es gibt in diesem Zehnseiten-Wörterbuch keine isolierte „Nullkarte“, die allein gesprochen werden müsste. Stattdessen liegen 19 häufige Oberflächen-Allographen vor, bei denen ein q/s/ch/d/t-Rahmen denselben produktiven Kern anders schreibt. Diese 19 Formen tragen 93 Gruppen. Der Lehrling lernt also keine Bedeutung für `q` oder `ch`; er lernt eine Schreiberregel.

## Der reale Lernaufwand

`NOMENCLATOR_DECK.tsv` enthält 254 Oberflächen, die ganz oder teilweise gelernt werden müssen, und deckt 300 Gruppen. Diese Zahl ist eine Obergrenze, weil mehrere Oberflächen denselben Körper oder denselben Besitzer teilen können. Die produktive Hälfte ist wesentlich kleiner: 25 Kerne, wenige Reihen und fünf gebundene Modifier reichen für 476 Gruppen.

Die wahrscheinlichste tatsächliche Unterrichtsform wäre deshalb:

1. ein Blatt mit 25 Kernen und den Reihen OK/OL/OT, AIIN/AIN/IIN, AL/AR/AIR;
2. ein kurzes Blatt mit E/EE/EEE, Y und den lizenzierten Schlusskarten;
3. ein Pflanzen-/Bad-Nomenklator mit den häufigen Ganzkörpern;
4. je Diagramm ein lokales Stern- oder Ringverzeichnis.

## Nächster Angriffspunkt

Die 166 teilregelhaften Oberflächen sind jetzt die wertvollste Schicht. Dort können neue wiederkehrende Körper entdeckt werden, ohne noch einmal die bereits geschlossene Kernliste umzudeuten. Besonders ergiebig sind die 123 Astroformen mit genau einem bekannten Kern: Wenn sich ihre Reste an mehreren Besitzern wiederholen, wird aus einem lokalen Namen eine neue produktive Unterfamilie; wenn nicht, bleibt er korrekt im Nomenklator.
