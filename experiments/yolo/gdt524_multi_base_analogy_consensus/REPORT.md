# GDT524 — Zwei unabhängige Analogien statt einer lauten Einzelstimme

## Ergebnis

GDT524 verbessert den aktuellen 159-Formen-Satz von 142 auf **144 richtige
Rang-1-Rezepte**, ohne einen bisherigen Rang-1-Treffer zu verlieren. Korrigiert
werden `kchody` und `ld`. Im rotierenden Altformenlauf steigt Rang 1 ebenfalls
von 1.096 auf **1.098**; dort werden `qoteody` und `shkchy` korrigiert, wiederum
ohne Rang-1-Verlust.

Der produktive Unterschied zu GDT522 ist klein, aber wichtig: Eine einzelne
ähnliche Altform darf einen Kandidaten weiterhin anheben. Für den stärkeren
Konsensbonus müssen nun jedoch **zwei verschiedene alte Basisformen über zwei
verschiedene Editkanäle** dasselbe Rezept stützen.

| Deck | Modell | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme | tiefster Rang |
|---|---|---:|---:|---:|---:|---:|---:|
| vier rotierende Altgruppen | GDT523 | 1.096 | 1.327 | **1.387** | 1.418 | 2.111 | 22 |
| vier rotierende Altgruppen | GDT524 | **1.098** | **1.328** | 1.386 | 1.418 | **2.109** | 22 |
| aktuelle 159 Formen | GDT523 | 142 | 154 | 158 | 158 | 187 | 9 |
| aktuelle 159 Formen | GDT524 | **144** | 154 | 158 | 158 | **185** | 9 |

Der eine verlorene alte Top-3-Treffer ist der einzige kleine Gegeneffekt der
ausgewählten Stufe; Top 5 bleibt gleich und die Rangsumme verbessert sich.

## Die zwei neuen aktuellen Treffer

Für `kchody` lautet der Konsens:

```text
kchod + y  -> Y        69/72 passende alte Relationen
chody + k  -> K        32/34 passende alte Relationen
Ergebnis: K+CH+O+D_ADDR+Y
```

Die erste Basis liefert den rechten `y -> Y`-Kanal, die zweite den linken
`k -> K`-Kanal. Beide Wege treffen unabhängig dasselbe vollständig
komponierte Rezept und verdrängen `K+CH+O+DY`.

Für `ld` ist die Konstruktion spiegelbildlich:

```text
d + l -> L             43/45 passende alte Relationen
l + d -> D_ADDR        10/12 passende alte Relationen
Ergebnis: L+D_ADDR
```

Damit ist `ld` nicht als gelernte Ausnahme nötig: je eine alte Ein-Zeichen-
Erweiterung erklärt die andere Hälfte.

## Weshalb verschiedene Kanäle verlangt werden

Der erste Entwurf hätte `kcheeky` beschädigt. Zwei verschiedene alte
Basisformen schienen dort gemeinsam für einen Rivalen zu stimmen, doch beide
Belege wiederholten in Wahrheit nur denselben Kanal `k -> K`. GDT524 zählt
solche Wiederholungen nicht doppelt. `kcheeky` bleibt deshalb korrekt auf Rang
1 und dient als konkrete Schutzprobe gegen Scheinkonsens.

## Arbeitsbedeutung

Die sichtbaren Gruppen verhalten sich in diesem Teilmodell zunehmend wie
Kompositionen aus wiederkehrenden Renderern und kurzen atomaren Zusätzen. Eine
neue Ganzform kann aus zwei bereits beobachteten Nachbarschaftsänderungen
rekonstruiert werden, ohne dass ihre komplette Schreibform als Sonderkarte
gespeichert wird. Das ist genau die gesuchte Brücke zwischen produktiven
Kürzeln und gelernten Ganz- oder Teilrenderern.

Fünfzehn aktuelle Rang-1-Fehler bleiben. Der nächste sinnvolle Griff ist, für
diese Restformen die Fälle mit nur **einer** starken Analogie von jenen zu
trennen, bei denen zwei schwächere, aber kompatible Teilwege erst über einen
Zwischenstamm verbunden werden müssen. Neue Seiten sind dafür noch nicht
nötig.
