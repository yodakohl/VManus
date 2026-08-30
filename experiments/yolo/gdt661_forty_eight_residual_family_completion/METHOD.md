# GDT661 — Methode

## Frage

Können die 48 von GDT660 neu freigelegten Restoberflächen über die bereits
sichtbaren Stoff-, Mengen-, Qualitäts- und Zubereitungsfamilien so konkret
gelesen werden, dass jede ihrer 872 Positionen einen praktischen Default und
jede der 48 Ausgangszeilen eine vollständige Arbeitsübersetzung erhält?

## Eingaben

- GDT660s V37-Arbeitsedition, Wörterbuch, Glossar, 48-Zeilen-Frontier und
  explizite 179-Seiten-Allowlist;
- die primären Familienberichte GDT627, GDT635, GDT636, GDT639, GDT645,
  GDT647, GDT655, GDT657 und GDT660;
- ZL3b-Token sowie ZL3b/IT2a/RF1b-Zeilen ausschließlich über
  `./vmanus-exp query-tsv` mit expliziten Allow-Werten und Sperren für f1r,
  f84 und f84r.

## Methode

1. Die Zielmenge ist die feste Reihenfolge der 48 unterschiedlichen
   `unknown_surface`-Werte in GDT660s neu exponierter Frontier.
2. Alle Vorkommen werden vor der Bedeutungszuweisung neu gezählt: Oberfläche,
   Seite, Zeile, Position, Tokenart, Nachbarn und die drei alternativen
   Leserfassungen. Eine enge Split-Normalisierung akzeptiert nur vollständige
   aufeinanderfolgende Lesertoken, deren Konkatenation exakt die
   ZL3b-Oberfläche bildet.
3. Die Kandidaten werden als vollständige Oberflächen in zwölf sichtbare
   Familien eingeordnet. Kompositionstags erklären eine Karte, sind aber
   getrennt von ihrer deutschen Lesefassung und dürfen nie per Substring in
   andere Wörter exportiert werden.
4. 46 Oberflächen erhalten exakte Ganzwortkarten. `r` und `d` erhalten keine
   globale Glossarzeile: 124 P-`r` werden als Wurzel/Wurzeldroge, fünf L-`r`
   als Wurzelzeichen; 47 P-`d` als Dosis/Maß und sechs L-`d` als
   Dosis-/Maßzeichen gelesen.
5. `cho`, `am`, `dam` und die fünf Y-Ganzformen behalten ihren Inhaltswert,
   werden je nach Stellung als Kopf, Bezug, Maßeinheit oder Abschluss lesbar
   gesetzt. Insgesamt existieren 26 beobachtete Renderingkarten.
6. Sieben ausdrücklich schwache Karten bleiben im Deck, statt ihre Lücken mit
   Neutralprosa zu verdecken: `qekeochor`, `shkair`, `oeeo`, `qoteees`,
   `saii`, `tdain`, `chakal`. Besonders `oeeo = zweiter Mazerationsansatz` ist
   eine kreative, ersetzbare Singleton-Lesung.
7. Die V37-Edition wird tokenweise nach V38 projiziert. Alle Nichtzielpositionen
   müssen in Glosse, Quelle und Scope exakt unverändert bleiben.
8. Der unabhängige Validator rekonstruiert die Quellzählungen ohne Import des
   Builders und verlangt anschließend einen byte-identischen Tempdir-Replay.

## Entscheidungsregel und Aussagegrenze

Jede Zielposition braucht eine kurze Stoff-, Teil-, Mengen-, Qualitäts- oder
Zubereitungslesung. „Arbeitsgut“, „Vorgang“, „Schritt ausführen“ und ähnliche
Nullinformation sind unzulässig. Eine sichtbare Label- oder Schlussfunktion
darf als Zeichen beziehungsweise Interpunktion erscheinen.

V38 ist eine kreative, austauschbare Arbeitstheorie. Sie bestätigt weder
Sprache noch Lautwerte, Glyphenidentitäten, freie Morpheme, Klartext oder eine
bestimmte Pflanze, Krankheit beziehungsweise Zutat. ZL3b, IT2a und RF1b sind
alternative Lesungen eines Manuskripts. Keine neue Seite oder Abbildung und
keine der gesperrten Seiten f1r/f84/f84r wird verwendet.
