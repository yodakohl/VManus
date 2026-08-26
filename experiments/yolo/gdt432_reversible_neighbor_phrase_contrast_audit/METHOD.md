# GDT432 — Methode

## Question

Bleiben die 47 kurzen GDT431-Lesungen von jedem ihrer drei oder vier
beobachteten Ein-Kern-Nachbarn unterscheidbar, oder verwischt die flüssige
deutsche Paraphrase verschiedene Komponentenrezepte?

## Inputs

- 47 Karten, 235 Registerfassungen und 145 Nachbarn aus GDT431;
- die unveränderten Komponentenwerte aus GDT413;
- die fünf Registerexpansionen aus GDT415;
- die beobachteten Rezeptregister aus GDT416;
- die direkten Bedeutungsabstände und Frame-Zahlen aus GDT428/GDT429.

## Method

1. Jedes Nachbarpaar wird positionsgleich verglichen. Genau ein Atom muss sich
   ändern; Länge, Reihenfolge und alle übrigen Atome bleiben gleich.
2. Eine explizite Slotspur (`Position:Familie=Wert`) wird vor und nach dem
   Wechsel erzeugt. Genau ein semantischer Slot muss wechseln.
3. Die kurze Quell- und Zielphrase wird erzeugt und auf Gleichheit geprüft.
4. Dasselbe geschieht für alle fünf Register, also 145 × 5 = 725 lokale
   Kontraste. Wiederholte Argumente wie `Y+Y` erhalten ausdrücklich einen
   äußeren und inneren Scope.
5. Die 145 Wege werden zusätzlich nach 30 gerichteten Wurzelwechseln und nach
   47 Zielkarten zusammengefasst.

## Decision rule and claim ceiling

Eine Karte besteht nur, wenn alle Quellwege genau einen Slot verändern, jede
Quell- und Zielphrase verschieden bleibt und alle fünf lokalen Ziellesungen
bytegleich der veröffentlichten GDT431-Fassung sind.

Das prüft die Reversibilität unseres Phrasebooks, nicht die Wahrheit der
zugrunde gelegten Bedeutungen. Registerfassungen ohne beobachtetes Quellrezept
in genau diesem Register bleiben als Gegenproben kenntlich.
