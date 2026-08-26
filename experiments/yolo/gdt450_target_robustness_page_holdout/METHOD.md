# GDT450 — Methode

## Question

Kann der in GDT449 gelernte Zielstatus `READABLE` oder `STOP` als sicherer
Kurzfilter auf eine ausgelassene physische Seite übertragen werden?

## Inputs

- GDT448: 61.878 Kontextproben und 4.275 Kontextsignaturen;
- GDT441: Ereignis→physische-Seite-Zuordnung;
- GDT449: Zielidentität und globale Robustheitsklasse.

## Method

Die gewichteten GDT448-Kontexte werden auf 65.746 tatsächliche
Ziel×Quellereignis-Proben expandiert. Für jedes Ziel wird jede seiner Seiten
einmal gehalten. Aus allen übrigen Seiten entsteht genau eine grobe Klasse:

- `READABLE`: kein Trainingsstopp;
- `STOP`: keine Trainingslesung;
- `MIXED`: beides, daher Enthaltung;
- `NO_TRAINING`: Ziel nur auf der gehaltenen Seite erreichbar.

`READABLE` auf Training plus mindestens ein Stopp im Holdout ist ein kritischer
`FALSE_SAFE`. Zusätzlich wird geprüft, ob der gehaltene operative Kontext
bereits auf einer Trainingsseite vorkam.

## Decision rule and claim ceiling

Ein einziger `FALSE_SAFE` verbietet dem Kurzfilter, den Live-Zertifizierer zu
überstimmen. Falsche Stopps sind Übervorsicht; gemischtes oder fehlendes
Training enthält sich.

Der Test erzeugt weder Zielidentität noch Oberfläche, Auftreten oder Bedeutung.
