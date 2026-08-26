# GDT458 — unbekannte Inseln bis 32 Karten

## Ergebnis

Der Leser bleibt auf dem geprüften Horizont sicher. Dreizehn fest ausgewählte
Aussagen besitzen je ein durchgehend ersetzbares 32-Karten-Fenster. Auf diesen
identischen Ankern wurden Inseln der Länge 1 bis 32 abgespielt:

| Länge | Ersatzkarten | Stopps in der Insel | Stopps danach |
|---:|---:|---:|---:|
| 1 | 13 | 1 | 0 |
| 8 | 104 | 4 | 0 |
| 16 | 208 | 8 | 0 |
| 24 | 312 | 13 | 0 |
| 32 | 416 | 15 | 0 |

Über alle Längen sind das 146.432 Stromentscheidungen, 6.864 sichtbare
Ersatzkarten und 259 Stopps. Sämtliche Stopps liegen innerhalb der künstlichen
Insel und bewahren den eingehenden Zustand. Von 416 Inseln haben 415 noch eine
unmittelbare unveränderte Karte in derselben Aussage; alle 415 lesen. Die eine
übrige 32er-Insel endet am Aussagenrand. Alle 416 Inseln erreichen vor einem
weiteren Fehler wieder exakt den Referenzzustand.

## Besitzerbanken

Die 13 Anker decken alle fünf laufenden Register ab: zwei Source-T, zwei
Herbal, eines Biological, eines Celestial und sieben Pharma. Sie liegen auf
sieben Seiten (`f1r`, `f11r`, `f13r`, `f67r2`, `f77r`, `f88r`, `f89r`). Alle
57 Besitzerbanken wurden bei jeder der 32 Längen isoliert wiederholt:
1.824/1.824 Bankläufe und sämtliche 146.432 darin enthaltenen Ereignisse
stimmen mit dem globalen Strom überein.

## Was sich daraus praktisch ergibt

Eine zukünftige Seite darf einen langen Block neuer, aber formal lesbarer
Kompositionen enthalten, ohne dass der Leser daraus zwangsläufig falschen
Zustand in die nächste bekannte Karte schleppt. Unbekannte oder blockierte
Karten können lokal in Quarantäne bleiben; der erste bekannte Anschluss wird
wieder gelesen.

Das ist keine Aussage, dass die 32 Ersatzkarten richtig verstanden wurden. Es
ist ausschließlich ein geprüfter Wiedereinstiegsvertrag. Gegenüber GDT457
schrumpft die gematchte Stichprobe von 55 Aussagen bei Länge 16 auf 13 Aussagen
bei Länge 32. Daher ist 32 eine sichere beobachtete Untergrenze für diese 13
Fenster, kein universaler Maximalhorizont und kein Grund, nun mechanisch immer
längere Inseln zu testen.

## Reproduzierbarkeit

Der Builder wählt Nachbarn und Fenster ohne Outcome-Feld, liest alle 32
Vollströme und bindet sie durch Digests. Der Validator rekonstruiert Auswahl,
Fenster, Präfixe, Stopps, Zustände und Besitzerbanken und erzeugt alle acht
Artefakte byte-identisch neu. Ergebnis: 28/28 Prüfungen bestanden.

Keine neue Seite, Form, Vorkommensprognose oder Bedeutung wurde hinzugefügt;
`f84` und `f84r` blieben versiegelt.
