# GDT726 method

## Frage

Lässt sich der vollständige aktuelle V98-Bestand auf denselben 51 Zeilen in
Originalreihenfolge ausgeben, sodass jede der 479 Positionen genau einmal
verbraucht wird, alle schon vereinbarten Span- und Companion-Regeln wirklich
ausgeführt werden und klar lokale Lesebrüche repariert werden können, ohne
offene Bedeutungsfragen stillschweigend umzudeuten?

## Eingaben

- V56 aus GDT682 und V57 aus GDT683 als vollständige 51-Zeilen-Baselines.
- V98s 479 Kontextrealisierungen aus GDT725.
- Die fünf V98-Spanregeln und ihre Ausführungstabelle.
- Die zwei Direktiven für den einen `keo r`-Span auf f7r.2 und dessen acht
  eingefrorene Ausgabe-Einheiten.
- Der GDT725-Companion für `daiin` auf f76v.10.
- Zehn kleine Render-Spezifikationen: neun neue lokale Reparaturen und der
  geerbte Companion.
- Sechs explizite Bedeutungs- oder Reichweitenfragen, die der Renderer nicht
  entscheiden darf.

Keine neue Seite, kein Bild und keine neue Transkription wird geladen.

## Zwei Ausgabekanäle

`V98_EXACT` ist der Reproduktionskanal. Er nimmt die 479 V98-Kontexte
unverändert, setzt die fünf geerbten Zweier-Spans je einmal und verwendet den
bereits in GDT725 belegten f76v.10-Companion. Fünf Doppelpositionen werden
dadurch zu je einer Einheit: 479 Positionen ergeben 474 Ausgabe-Einheiten.

`V98R1_PRACTICAL` ist der Lesekanal. Zusätzlich kommen drei lokale
Zweiergruppen und sechs lokale Positionsformulierungen hinzu. Zusammen mit
dem Companion sind das zehn Spezifikationszeilen, aber nur neun neue
Reparaturen. Acht Zweiergruppen reduzieren 479 Positionen auf 471 sichtbare
Einheiten. Jede Gruppe und jede Überschreibung ist an Positions-ID, Oberfläche,
Locus, aktuellen V98-Kontext und eine konkrete Quellzeile gebunden.

## Rekonstruktion und Kontrolle

1. V56, V57 und V98 müssen dieselben 51 Loci und dieselbe Tokenreihenfolge
   tragen; V98 muss genau `P001` bis `P479` enthalten.
2. Jede Spanposition muss in derselben Zeile unmittelbar benachbart sein. Eine
   Zweiergruppe gibt genau einmal Text aus; ihr zweites Mitglied wird nur
   konsumiert.
3. Jede übrige Position gibt ihren V98-Kontext oder genau eine lokale
   Überschreibung aus. Keine Position darf fehlen oder doppelt vorkommen.
4. Der unabhängige Validator importiert den Generator nicht. Er rekonstruiert
   zehn Tabellen mit zusammen 2.082 Zeilen, beide Gesamtreader und das
   Ergebnisobjekt neu und verlangt vollständige Zeilengleichheit.
5. f7r.2 muss in beiden Kanälen bytegleich zu den acht GDT725-Einheiten bleiben;
   die zwei Direktiven zählen als zwei Steuerzeilen für einen semantischen
   Span, nicht als zwei Spans.
6. Die sechs Bedeutungsfragen bleiben unverändert, mit
   `renderer_change_applied = 0`.

## Entscheidungsregel und Grenze

Eine praktische Reparatur ist erlaubt, wenn sie nur einen lokal sichtbaren
Kopf bindet, einen nackten Zahlenwert ausformuliert, einen Rückbezug sichtbar
macht oder redundante Wiederholung kürzt. Sie darf keinen Wörterbuchkern,
keinen V98-Kontextwert, keinen Score und keinen frei übertragbaren
Teilstringwert ändern.

Wenn Dosis gegen Portion, Arznei gegen neutrales Kompositum, Rohdroge gegen
Material oder die Reichweite einer Wiederholung betroffen ist, bleibt die
Frage offen. V98R1 ist eine explorative deutsche Arbeitslesung, keine
identifizierte historische Übersetzung. Sprache, Lautung, Klartext,
historisches Codebuch, konkrete Zutaten, Krankheit und Heilwirkung werden
nicht behauptet; alle historischen Felder bleiben `H0_NONE`. Weder f84 noch
f84r wird verwendet.
