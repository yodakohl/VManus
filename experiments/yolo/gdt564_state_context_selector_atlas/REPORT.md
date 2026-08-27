# GDT564 — Zwei kleine Zustände wählen alle variablen Mikrophrasen

Status:
`PASS_402_RECIPE_SELECTOR_ATLAS__101_VARIABLE_RECIPES_RESOLVED__415_CONTEXT_CELLS__ZERO_AMBIGUITY__THREE_PORTABLE_ROUTES`

## Ergebnis

Die 402 Zustandsrezepte brauchen kein Wörterbuch aus 1.656 langen Sätzen. Sie
lassen sich in 716 konkrete Lesefälle komprimieren:

```text
301 Rezepte mit fester beobachteter Mikrophrase
415 Handlung-/Argument-Kontextzellen für 101 variable Rezepte
──────────────────────────────────────────────────────────────
716 vollständige Rezept-Kontext-Lesungen
```

Für alle 101 variablen Rezepte gilt:

```text
exaktes Rezept + aktive Handlung + aktives Argument → genau eine Mikrophrase
```

Das ergibt 415/415 eindeutige Zellen und 1.277/1.277 aufgelöste Ereignisse.
Besitzer, Seite, Register, Satzposition und lange Ganzwortdefinitionen werden
nicht benötigt.

## Die portable Dreiwegregel

Noch wichtiger als die 415 Einträge ist die kleine Regel, die den richtigen
Kontext auswählt:

| Sichtbarer Zustand des Rezepts | Einzusetzender Kontext | Rezepte | Ereignisse | Zellen |
|---|---|---:|---:|---:|
| Handlung steht geschrieben | aktives Argument | 54 | 638 | 144 |
| Argument steht geschrieben, Handlung fehlt | aktive Handlung | 15 | 206 | 76 |
| Handlung und Argument fehlen | beide aktiven Werte | 32 | 433 | 195 |

Zusammen mit den 301 festen Rezepten ist das eine vollständige Vier-Routen-
Anleitung für alle 402 Rezepte. Sie schaut auf offene Slots, nicht auf den Namen
der Seite oder auf ein auswendig gelerntes langes Wort.

## Drei konkrete Typen

`SH+E+DY` schreibt HALTEN, Grad I und ABSCHLIESSEN. Nur das Argument bleibt
offen. Die größte Zelle lautet:

```text
SH+E+DY + ARG=Y  → Halte den Posten; auf Grad I; abschließen.  (64-mal)
```

`OT+Y` schreibt DANACH und POSTEN, aber keine Handlung. Seine acht aktuellen
Phrasen werden allein durch das aktive Verb getrennt:

```text
OT+Y + ACTION=CH  → Danach: nimm den Posten.
OT+Y + ACTION=K   → Danach: gib den Posten.
OT+Y + ACTION=SH  → Danach: halte den Posten.
```

Das nackte `OL` schreibt weder Handlung noch Argument. Deshalb braucht es beide:

```text
OL + ACTION=OK + ARG=Y    → Weiter: setze den Posten.
OL + ACTION=SH + ARG=Y    → Weiter: halte den Posten.
OL + ACTION=CHD + ARG=Y   → Weiter: bearbeite den Posten.
```

Seine 33 Varianten sind damit keine 33 Bedeutungen von `OL`, sondern 33
beobachtete Füllungen zweier offener Slots. `OL` selbst bleibt FORTSETZEN.

## Wie viel die Zustände tatsächlich leisten

Wenn man bei jedem variablen Rezept blind nur seine häufigste Phrase nimmt,
trifft man 566/1.277 Ereignisse (44,32%). Nur die aktive Handlung erreicht
932/1.277 (72,98%), nur das Argument 872/1.277 (68,29%). Beide zusammen
erreichen 1.277/1.277 und lassen keine mehrdeutige Zelle.

Die vollständige Paarregel ist dabei nicht bloß eine Sammlung von
Einzelereignissen. 183/415 Zellen wiederholen sich und tragen 1.045/1.277
Ereignisse. 172 Zellen stehen auf mehreren Seiten, 123 in mehreren Registern
und 47 in beiden Seitenkohorten. Die größte Zelle wiederholt sich 64-mal.

## Was sich noch kleiner machen lässt

Im aktuell beobachteten Material genügt bei 60 Rezepten das Argument allein,
bei 26 die Handlung allein und nur bei 15 wirklich das Paar. Darin stecken zwei
ehrlich ausgewiesene Gleichstände:

```text
49  nur Argument ausreichend
26  nur Handlung ausreichend
15  Handlung + Argument erforderlich
 6  Handlung oder Argument gleich gut
 5  Argument oder Auflösungsmodus gleich gut
```

Für eine kompakte Tabelle wird bei Gleichstand das Argument gewählt. Für die
spätere Anwendung bleibt die sichtbare Dreiwegregel absichtlich vorsichtiger:
Bei einem Rezept ohne beide geschriebenen Slots setzt sie beide Zustände ein,
auch wenn sie in den bisherigen zwei oder vier Belegen zufällig gemeinsam
wechseln. Das ist Hausverstand im besten Sinn: offene Felder füllen, nicht eine
zufällige Korrelation zu einem neuen Wortgesetz erklären.

## Neue Arbeitsbasis

Die aktuelle Zustandslesung braucht damit nur vier Schichten:

```text
19 kurze Grundwerte
+ exakte geschriebene Reihenfolge
+ zwei laufende Speicherwerte: Handlung und Argument
+ lokaler Besitzer erst für die konkrete Kontextzeile
```

Das ist genau die gesuchte Mischung aus gelernten Fachkürzeln und Komposition.
Ein geschriebenes Rezept kann ein vollständiger Satz sein, oder ein Rahmen mit
einem oder zwei offenen Slots. Die lange deutsche Zeile gehört zum Ereignis,
nicht als Monsterdefinition in das Stammwörterbuch.

## Nächster Arbeitsweg

Als Nächstes sollten die 415 Zellen nicht weiter auswendig gelernt, sondern auf
wenige wiederkehrende Satzschablonen reduziert werden: Zustandsoperator,
Aktionsschablone, Argumentschablone und sichtbare Modifikatoren. Dann lässt sich
prüfen, ob jede der 716 Rezept-Kontext-Lesungen aus einem kleinen Satzbaukasten
erzeugt wird und welcher echte Bedeutungsrest danach noch übrig bleibt. Dafür
ist weiterhin keine neue Seite nötig.

## Grenze

Der Selektor bestätigt die innere Konsequenz der kreativen Arbeitsgrammatik,
nicht ihre historische Richtigkeit. Eine noch unbeobachtete Handlung-Argument-
Kombination kann sprachlich zusammengesetzt werden, ist dadurch aber weder als
Vorkommen noch als Voynich-Oberfläche vorhergesagt. Keine Seite, Oberfläche,
Rezeptfolge oder Wurzelbedeutung wurde geändert. Alle 40 Prüfungen bestehen.
