# GDT457 — Methode

## Question

Wie lang darf ein zusammenhängender Block sichtbarer neuer Kompositionen werden,
bevor eine nachfolgende unveränderte Karte stoppt oder Besitzerzustand aus der
Bank austritt?

## Inputs

- GDT441: geordneter 4.576er Strom;
- GDT454: nichtleere Ein-Schritt-Nachbarn;
- GDT455: zustandsbehafteter Stream-Treiber.

## Method

Für jedes Quellrezept wird ohne Outcome-Spalte ein quellengebundener
SHA-256-Minimalnachbar gewählt. Dann werden alle Aussagen mit mindestens einem
durchgehend ersetzbaren 16-Karten-Fenster gesucht. Das ergibt 55 Aussagen in
allen fünf laufenden Registern.

Je Aussage wird genau ein 16er-Fenster per Statement-Hash festgelegt. Die 16
Tests ersetzen auf diesem selben Fenster strikt verschachtelte Präfixe der
Länge 1, 2, …, 16. Damit ändern sich weder Ankersatz noch Startposition, wenn
die Insel wächst. Insgesamt entstehen 880 Inseln, 7.480 Ersatzkarten und 73.216
Stromereignisse.

Je Länge werden Entscheidung, unmittelbare echte Folgekarte, Folge-Stoppkette,
Zustandsparität und alle 57 isolierten Besitzerbanken geprüft. Die vollständigen
Replays werden durch kanonische SHA-256-Digests gebunden; Fehler- und
Rückkehrzeilen bleiben explizit.

## Decision rule and claim ceiling

Jeder Stopp muss Zustand und Scope bewahren. Eine unveränderte Folgekarte darf
stoppen, wird dann aber als abhängige Kaskade ausgewiesen. Besitzerbanken dürfen
nie voneinander abhängen. Der Test erzeugt keine Form und ändert keine Bedeutung.
