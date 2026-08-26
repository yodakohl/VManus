# GDT456 — Fehlersicherheit hängt nicht an einer günstigen Auswahl

## Sechs vollständige Läufe

Jeder Lauf ersetzt 1.026 sichtbare Karten in 513 Aussagen, insgesamt also
6.156 Ersatzkarten und 27.456 gelesene Stromereignisse.

| Auswahl | grün | gelb | Stopp | davon unverändert |
|---|---:|---:|---:|---:|
| lexikographisch zuerst | 4.518 | 20 | 38 | 1 |
| lexikographisch zuletzt | 4.519 | 16 | 41 | 0 |
| Hash-Auswahl | 4.512 | 20 | 44 | 0 |
| Löschung zuerst | 4.554 | 18 | 4 | 1 |
| Tausch zuerst | 4.500 | 26 | 50 | 0 |
| Substitution zuerst | 4.521 | 19 | 36 | 0 |

Die Stoppzahl ist also auswahlabhängig—vier bis fünfzig—aber die
Sicherheitswirkung nicht: alle 213 Stopps bewahren Handlung, Argument und
Aussage-Scope. Alle 342 global-gegen-isoliert verglichenen Besitzerbanken sind
ereignisgenau gleich.

## Die einzigen zwei Folgestopps

211/213 Stopps liegen direkt auf einer Ersatzkarte. Die zwei übrigen sind in
zwei verschiedenen Plänen dieselbe echte Karte `G407-E1391`, `EEE+DY` auf
f72r. Beide vorangehenden Ersatzkarten haben den benötigten Handlungskopf
entfernt; der Schluss ohne Kopf stoppt deshalb korrekt. `G407-E1392` liest in
beiden Fällen genau eine Karte später wieder grün. Das ist derselbe eng
begrenzte Mechanismus wie in GDT454, kein neuer Ausfalltyp.

## Rückkehr über alle Pläne

Von 3.078 Bursts erreichen 2.554 vor dem nächsten Fehler wieder den
Baseline-Zustand. 460 treffen vorher auf den nächsten geplanten Burst; 64 enden
an einer isolierenden Besitzergrenze. Kein Zustand springt in eine andere Bank.

Damit ist der GDT455-Vertrag nicht bloß auf eine stopp-priorisierte Auswahl
zugeschnitten. Was weiterhin offen bleibt, ist die inhaltliche Richtigkeit der
19 Arbeitswerte: Das Ensemble prüft Verarbeitung und sichere Ablehnung, nicht
Übersetzung oder Auftreten.
