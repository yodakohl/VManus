# GDT457 — Der sichere Horizont reicht mindestens 16 Karten

## Gleiche Stellen, wachsende Insel

55 fest ausgewählte 16-Karten-Fenster decken alle fünf laufenden Register und
23 der aktuellen Seiten ab. Auf genau diesen Fenstern wächst die Ersatzinsel
schrittweise, ohne dass günstige Aussagen oder Startstellen ausgetauscht werden.

| Insel | Ersatzkarten | Stopps | unveränderte Stopps |
|---:|---:|---:|---:|
| 1 | 55 | 5 | 0 |
| 4 | 220 | 9 | 0 |
| 8 | 440 | 17 | 0 |
| 12 | 660 | 20 | 0 |
| 16 | 880 | 32 | 0 |

Über alle 16 Längen entstehen 276 Stopps. Jeder liegt innerhalb der absichtlich
ersetzten Insel und bewahrt Handlung, Argument und Aussage-Scope. Keine einzige
unveränderte Karte stoppt; die maximale Folge-Stoppkette ist daher null.

## Unmittelbar nach der Insel

Bei Längen 1 bis 15 besitzen alle 55 Inseln noch eine unveränderte Karte in
derselben Aussage, und alle 55 lesen. Bei Länge 16 besitzen 49 Inseln eine
solche Folgekarte; alle 49 lesen. Die sechs übrigen enden einfach am
Aussageende.

Von 880 Inseln erreichen 869 vor der nächsten Insel derselben Besitzerbank
exakt den Baseline-Zustand. Fünf treffen vorher auf die nächste planmäßige Insel,
sechs enden an der Bankgrenze. Alle 912 global-gegen-isoliert verglichenen
Bankläufe sind ereignisgenau gleich.

Damit wurde bis Länge 16 kein Ausfallhorizont gefunden. Das ist ein unterer
Grenzwert, keine Behauptung unbegrenzter Robustheit. Der nächste sinnvolle Test
verwendet den kleineren gemeinsamen Ankersatz, der bis 32 Karten reicht.
