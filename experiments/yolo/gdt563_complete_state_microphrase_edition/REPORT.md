# GDT563 — Alle 1.656 Zustandskarten haben jetzt eine konkrete Mikrophrase

Status:
`PASS_1656_COMPLETE_STATE_MICROPHRASES__706_ACTIONLESS_PLUS_950_VISIBLE__ALL_ACTION_SLOTS_RETAINED__402_CONTEXT_PROFILES__301_STABLE_101_CONTEXT_VARIABLE_RECIPES`

## Ergebnis

Die beiden bisher getrennten Hälften sind jetzt eine vollständige Arbeitsausgabe:

```text
 950 Karten mit sichtbarer Handlung
 706 Zustandsellipsen aus GDT562
──────────────────────────────────
1.656 konkrete Mikrophrasen
```

Jede Karte zeigt gleichzeitig:

```text
Atomspur       = was tatsächlich geschrieben steht
Mikrophrase    = die mit dem aktiven Satzzustand ergänzte Anweisung
Kontextzeile   = dieselbe Anweisung im jeweiligen Besitzerkontext
```

Alle 4.684 geschriebenen Atome und alle 1.158 sichtbaren Handlungsslots bleiben
erhalten. Die 706 bereits aufgelösten Zustandsellipsen werden bytegleich aus
GDT562 übernommen. Keine Seite, Oberfläche, Rezeptfolge oder Wurzelbedeutung
wurde hinzugefügt oder geändert.

## Fast alles wird zu einer Operation

| Auflösung | Karten |
|---|---:|
| sichtbare Handlung + wirksames Argument | 898 |
| geerbte Handlung + wirksames Argument | 687 |
| sichtbare objektlose Handlung | 52 |
| geerbte objektlose Handlung | 6 |
| Argumentbezug ohne Handlung | 5 |
| formaler/relationaler Vorspann | 4 |
| selbständiger abgestufter Abschluss | 3 |
| reine Fortsetzung | 1 |

Damit sind 1.585/1.656 Karten vollständige Handlung-plus-Argument-Operationen.
Weitere 58 sind verständliche objektlose Handlungen. Nur 13 Karten besitzen
überhaupt keine Handlung; sie sind bereits als Bezug, Vorspann, Abschluss oder
reine Fortsetzung benannt und bleiben deshalb nicht bedeutungslos.

## Ein Rezept ist ein Rahmen, nicht zwingend ein ganzer Satz

Die 1.656 Karten verwenden 402 exakte Rezepte. 301 Rezepte ergeben in allen
beobachteten Kontexten nur eine Mikrophrase, aber 262 davon kommen überhaupt
nur einmal vor. Der aussagekräftigere Vergleich ist daher:

```text
140 wiederkehrende Rezepte
 39 mit einer einzigen Mikrophrase
101 mit mehreren Mikrophrasen, zusammen 1.277 Karten
```

Das variable Extrem ist das bloße `OL=FORTSETZEN`: Es trägt in den vorhandenen
Satzkontexten 33 Mikrophrasen, weil Handlung und Argument aus dem aktiven
Satzspeicher kommen. Das macht `OL` nicht zu 33 Wörtern. Sein stabiler Beitrag
bleibt „weiter/fortsetzen“; die längere Anweisung entsteht kompositionell:

```text
OL + aktives HALTEN + aktiver ANTEIL  → Weiter: halte den Anteil.
OL + aktives GEBEN  + aktiver POSTEN  → Weiter: gib den Posten.
OL + aktives NEHMEN + aktiver POSTEN  → Weiter: nimm den Posten.
```

Genau dieses Verhalten passt besser zu einem kleinen gelernten Codevokabular
mit Satzgedächtnis als zu grotesk langen Ganzwortdefinitionen.

## Reihenfolge bleibt Bedeutung

Neun Zustandsfolgen sind belegt. Die seltenen Gegenrichtungen werden nicht
zusammengelegt:

```text
R+OL+OT+Y   Weiter: markiere den Posten; danach nächsten Gang eröffnen.
OK+EE+DY+OL Setze den Wert; auf Grad II; abschließen; danach weiterführen.
```

Auch Wiederholung wird nur dort geglättet, wo sie sichtbar unmittelbar ist.
Sechzehn Karten wiederholen einen Handlungsroot. Sieben direkte Doppelungen
werden als „zweimal“ ausgesprochen; neun durch Grad, Argument oder Steueratom
getrennte Wiederholungen bleiben als zwei Handlungsslots expandiert. Der
flüssige Satz darf die Schriftstruktur also vereinfachen, aber nie verbergen.

## Neue Arbeitstheorie

Für diese Zustandskarten ist die derzeit beste konkrete Lesemechanik:

```text
geschriebenes Rezept
  + zuletzt aktive Handlung
  + zuletzt aktives Argument
  + lokaler Besitzer
  = konkrete Arbeitsanweisung
```

Die sichtbaren Wurzeln liefern kurze Fachkürzel. Der laufende Satzzustand liefert
Auslassungen, und der Besitzer macht aus einem allgemeinen POSTEN etwa einen
Pflanzen-, Drogen-, Stations- oder Positionsposten. Damit bekommt jede Sequenz
eine Defaultbedeutung, ohne `shey`-artige Formen zu künstlichen Definitionen wie
„Pflanzenmaterial zeitgebunden beschaffen“ aufzublähen.

## Nächster Arbeitsweg

Die 101 kontextvariablen wiederkehrenden Rezepte sind jetzt der produktive Kern.
Als Nächstes wird für jedes davon geprüft, welcher kleinste Kontextschlüssel
seine Mikrophrase auswählt: aktive Handlung, aktives Argument, Zustandsquelle
oder eine Kombination daraus. Ziel ist ein kompakter Kontextwähler, der auf den
vorhandenen Seiten jede Variante erklärt und später auf neue Seiten angewendet
werden kann, ohne die 19 Grundwerte erneut umzudeuten.

## Grenze

Dies bleibt eine kreative Arbeitsübersetzung, kein entzifferter Klartext. Die
eingesetzten Handlungen und Argumente sind sichtbarer Redaktionskontext, keine
unsichtbaren Manuskriptzeichen. Eine Ereignisphrase ist keine universelle
Ganzwortbedeutung. Alle 36 unabhängigen Prüfungen bestehen.
