# GDT458 method

## Question

Bleibt der zustandsbehaftete Leser auch nach zusammenhängenden Blöcken von bis
zu 32 sichtbaren neuen Kompositionen sicher, oder stoppt anschließend eine
unveränderte Karte beziehungsweise tritt Besitzerzustand aus seiner Bank aus?

## Inputs

- GDT441: geordneter 4.576er Strom und Referenzzustände;
- GDT454: feste nichtleere Ein-Schritt-Nachbarn;
- GDT455: zustandsbehafteter Besitzerbank-Treiber;
- GDT457: quellengebundene Nachbarwahl und kanonische Replay-Helfer.

## Method

Für jedes Quellrezept bleibt exakt derselbe GDT457-Nachbar gewählt: das
SHA-256-Minimum über ausschließlich Quellrezept, Zielrezept und Nachbar-ID.
Keine spätere Leseentscheidung geht in die Auswahl ein.

Gesucht werden Aussagen mit einem vollständig ersetzbaren 32-Karten-Fenster.
Das ergibt 13 Aussagen über alle fünf laufenden Register. Je Aussage wird ein
Fenster per Statement-Hash festgelegt. Die 32 Läufe ersetzen strikt
verschachtelte Präfixe der Länge 1, 2, …, 32 auf denselben Startpositionen.
Damit entstehen 416 Inseln, 6.864 Ersatzkarten und 146.432 Stromentscheidungen.

Für jede Insel werden alle Stopps, die erste unveränderte Folgekarte, eine
mögliche Stoppkaskade und die Rückkehr zum Referenzzustand erfasst. Zusätzlich
werden pro Länge alle 57 Besitzerbanken isoliert wiederholt und mit dem globalen
Strom verglichen. Vollständige Replays sind durch kanonische SHA-256-Digests
gebunden, ohne große doppelte Tabellen einzuchecken.

## Decision rule and claim ceiling

Ein Stopp muss Handlung, Argument und Scope unverändert lassen. Kein Stopp darf
auf eine unveränderte Folgekarte überspringen; Besitzerbanken dürfen nie
voneinander abhängen. Der Befund gilt nur für die 13 Aussagen, die ein
durchgehend ersetzbares 32er-Fenster besitzen. Der Test erzeugt keine Form,
erkennt keinen Inhalt und ändert keine Bedeutung.
