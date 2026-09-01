# GDT727 method

## Frage

Können die sechs in GDT726 offengebliebenen Bedeutungsgruppen jetzt mit
konkreten Arbeitsdefaults belegt werden, sodass Wörterbuch, Positionskontexte
und der vollständige 51-Zeilen-Reader dieselbe Entscheidung tragen?

## Basis

- V98s 324 aktive Lexikreadings, 479 Positionskontexte und vollständiges
  Wörterbuch aus GDT725.
- V98R1s 479 Positionsverbrauchszeilen, 471 Ausgabeeinheiten und 51 Leserzeilen
  aus GDT726.
- GDT705s Dreifachkontrast für `sheky`.
- Vier physisch unmittelbar vor P002, P142, P394 und P405 stehende ZL3b-Zeilen.
  Sie werden über `GuardedTSV` mit expliziter Seiten-Allowlist geladen; `f84*`
  wird vor dem Materialisieren der übrigen Felder verworfen.

## Bedeutungsdispatch

1. Die sechs aktiven Dosis-Stellen erhalten gemeinsam `Portion(en)`. `Maß`
   bleibt Formen mit ausgeschriebenem Maßkopf vorbehalten, `Wert` nackten
   Wert-/Stufenformen. Das ändert fünf Ganzwortkerne an sechs Positionen.
2. `cpheesy` behält den neutralen Kern Kompositum und wird lokal als
   vollständig bereitetes und abgeschlossenes Gemisch ausgegeben. `tail`
   wird auch lokal auf den bereits neutralen Kern kaltgestellter Materialanteil
   II zurückgeführt.
3. Für BOS-Anschlüsse zählt die physische Manuskriptzeile, nicht die lückenhafte
   Reihenfolge des 51-Zeilen-Decks. P002 und P142 verlieren den unbelegten
   Zeigewert. P394 bindet lokal an den vorherigen kalten Ansatz Grad II; P405
   an `qokar oly`, den unmittelbar zuvor abgeseihten heißen Drogenanteil I.
4. Der portable `sheky`-Kern bleibt einweichen, erhitzen und abschließen bis
   Mittelstufe. Seine drei Vorkommen werden nicht als „dreimal“ gelesen,
   sondern positionslokal an feuchte Mischung, heißen Drogenanteil I und
   heißen Holzanteil I im Ansatz Grad II gebunden.

Alle Ergänzungen erhalten eine positive Evidenzzeile, den stärksten
Gegenbeleg, Arbeitsconfidence und `H0_NONE`. Lokale Patientenwörter werden
nicht als Teilstringbedeutung exportiert und kein Score wird angehoben.

## Vollständige Rekonstruktion

Der Generator erstellt die vollständigen V99-Tabellen mit 324 Lexikreadings,
479 Kontexten und 1.586 Wörterbuchzeilen. Danach baut er aus den unveränderten
GDT726-Spans und lokalen Leseregeln alle 471 Einheiten neu auf. Jede der 479
Positionen wird genau einmal konsumiert. Das f7r.2-Spezialartefakt wird neu
erzeugt, weil P287 von Dosis zu Portion wechselt; sein `keo|r`-Span bleibt
unverändert eine heiße Portion.

Der unabhängige Validator importiert den Generator nicht. Er prüft Feldparität
außerhalb der zehn aktualisierten Lexikrecords und 13 Kontextpositionen,
Confidence/Evidenz für alle 1.586 Wörterbuchzeilen, die vier echten
Vorgängerzeilen, 479 eindeutige Positionsverbräuche, 471 Units und neun
geänderte Leserzeilen.

## Reichweite

V99 ist die konkreteste aktuelle deutsche Arbeitslesung dieser 51 Zeilen.
`Portion`, die beiden BOS-Patienten und die drei `sheky`-Patienten sind
explorative Defaults, keine historisch identifizierten Einheiten oder
Klartextübersetzungen. Die geerbten globalen V48-Zeilen außerhalb der aktiven
V99-Tranche werden nicht durch bloßes Suchen-und-Ersetzen umgeschrieben.
