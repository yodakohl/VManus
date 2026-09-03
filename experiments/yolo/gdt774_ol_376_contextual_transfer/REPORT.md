# GDT774 — Transfer des `ol`-Kontextoperators auf 376 Stellen

Status: `PASS__PARTIAL_CONTEXT_TRANSFER__NO_PLAINTEXT`. Diese Runde benutzt ausschließlich bereits
gecachte, reader-exakte Positionen. Sie öffnet keine neue Seite und behauptet
weiterhin null bestätigte Lexeme oder Klartextsätze. Der unabhängige Validator
bestätigt 28.954 Checks, alle fünfzehn Source Locks und den bytegleichen Replay
aller 24 Runner-Ausgaben plus Bericht.

## Das konkrete Ergebnis

Der occurrence-ID-freie Renderer gibt allen 376 exakten
`ol`-Vorkommen eine sichtbare Arbeitsbedeutung. Er findet aber nur
**49 kontextspezifische Stellen
(13.03%)**. Die übrigen
**327 (86.97%)** bleiben
ehrlich beim schwachen Ganzwortdefault `Ansatz-/Zubereitungsposten`.

Die automatische Ausgabe verteilt sich auf:

- 10 × `Ansatz:` nach einer Mengenform;
- 5 × `Menge:` vor einer Mengenform;
- 4 × `und dann` vor einem direkten Prozessanker;
- 3 × `;` nach einem direkten Abschlussanker;
- 27 × `und` in einer beidseitigen F15-Zustandsbrücke;
- 327 × nominaler Fallback.

Ein automatischer Doppelpunkt wird **nie** erzeugt: Der eine GDT773-Fall hat
keinen übertragbaren, occurrence-ID-freien Trigger. Ebenso bleiben rechtsseitige
Abschlüsse, linksseitige Prozesse, bloße Zeilenränder, nackte F14-Geometrie
und alle sieben `ol ol`-Paare nominal.

## Wie viel von GDT773 wirklich überträgt

Die Regeln reproduzieren nur **9 von 15**
fixierten GDT773-Ausgaben. Die sechs Fehlstellen waren durch fallweise
Feldinterpretation gewonnen, nicht durch eine portable Beobachtungsregel. Der
praktische Hybridreader bewahrt die fünfzehn alten Kalibrierentscheidungen und
wendet die automatischen Regeln sonst unverändert an. Dadurch erhält er
55 kontextspezifische und
321 nominale Ausgaben; das ist ein Arbeitsrenderer,
kein besserer semantischer Test.

## Mengenrichtung und Sperren

Die sechzehn bekannten Mengenkontakte enthalten wegen des bilateralen
`ol s aiin ol` genau 17 occurrence-spezifische Kanten.
Fünf `ol` links von der Mengenform werden `Menge:`. Zwölf liegen rechts;
zwei davon sind jedoch zeilenfinal und würden einen baumelnden Kopf `Ansatz:`
erzeugen. Sie fallen zurück auf das Nomen. Damit bleiben
15 ausgewählte Mengenoutputs. Phrase-Lizenz,
GDT763-Slotfunktion und die beidseitige Ambiguität bleiben im Kantenaudit
sichtbar: 8 der ausgewählten Kanten
haben die stärkere alte Phrasenlizenz, 7
nur den explorativen Richtungsdefault. Keine Einheit wird dadurch identifiziert.

## Formale Realität der breiten Verteilung

Die 376 Token liegen auf 340 Zeilen,
98 Seitenlabels und 61
physischen Folios. Ihre Lage ist 22 first,
317 medial und 37 last. Nur
35 haben irgendeine direkte Signatur; die
meisten Kontexte sind also nicht fein genug typisiert.

Der operatorartige Eindruck ist zudem registerabhängig: In Sektion B liegen
nur 2 von 167 Token first,
außerhalb B dagegen 20 von 209.
Mehrfach-`ol` konzentriert sich ebenfalls in B/Hand 2. Gleichzeitig sind die
14 Token in sieben benachbarten `ol ol`-Paaren
signaturlos und bleiben nominal. Das stützt einen gemischten Recordkopf/Operator,
nicht ein globales Satzzeichen.

Der feste 20.000er Folio-Slotvergleich erwartet im Mittel
47.90 first-Positionen statt der
beobachteten 22; das interne Profil ist
also nicht bloß Seitenmischung. Zugleich sind sieben benachbarte Paare gegen
7.99 erwartet unauffällig. Die
rechte Nachbarvielfalt ist mit 188
gegen 224.81 im
folio-und-positionsgleichen Nullmodell stark konzentriert. Das ist der beste
nächste Hebel, kann aber sowohl einen Feldkopf mit Komplement als auch einen
Operator vor einem Feld anzeigen.

Eine breitere, bereits vorhandene Evidenz-Vereinigung erreicht nur
73 Token; 303
bleiben außerhalb dieser Typisierung. Dreizehn der fünfzehn GDT773-Fälle liegen
in jener Vereinigung. Der Kalibrierdeck war damit stark auf informative
Kontexte angereichert und darf nicht als repräsentativ für alle 376 gelten.

## Vergleich zum alten `Grundansatz`

Alle 376 Stellen kreuzen zum alten GDT683-Output `Grundansatz`; alle beruhen
auf derselben geerbten GDT664-Karte, nicht auf 376 unabhängigen Bestätigungen.
GDT774 verwirft diesen Bestand nicht. Es zerlegt ihn in 49
gerichtete Feldausgaben und 327 schwächere nominale
Fallbacks. Öl, Wasser und Wein bleiben ununterscheidbar.

Die 24 manuell ausgewählten Kontrastkontexte werden vom automatischen Reader
24/24 und vom Hybridreader
24/24 wie spezifiziert ausgegeben. Diese
Stichprobe dokumentiert Richtungsfälle und Sperren; weil sie zur Regelprüfung
entworfen wurde, erhält sie null unabhängigen Bedeutungs- oder Scorecredit.

## Grenze und nächster Hebel

`ol` bleibt ein komplettes EVA-Ganzwort. Kein Zeichen oder Teilstring bekommt
eine Bedeutung. Strukturrollen und deutsche Arbeitsausgaben stehen getrennt.
Der nächste sinnvolle Hebel liegt in den 327
Fallbackstellen: die stark konzentrierten rechten Folger und der B/Hand-2-Split
können neue, occurrence-ID-freie Unterklassen liefern. Erst solche Unterklassen
dürfen weitere konkrete Outputs ersetzen.
