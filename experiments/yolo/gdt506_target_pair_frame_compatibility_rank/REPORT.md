# GDT506 — sieben Paarziele haben einen passenden alten Rahmen, vier noch nicht

Status: `SEVEN_TARGET_FRAMES_HAVE_ARGUMENT_COMPATIBLE_REDUCTIONS__FOUR_CONTEXTUAL_TRANSFERS_REMAIN_OPEN`

## Ergebnis

Alle elf GDT505-Zielrezepte lassen sich als geordnete Teilfolge aus alten
Paarträgern herausschneiden. Das ergibt 84 konkrete Reduktionswege. Der
entscheidende Unterschied erscheint erst beim Argument: 40 Wege haben
denselben expliziten oder geerbten Argumentmodus wie das Ziel, 44 nicht.

Die elf Karten teilen sich dadurch sinnvoll in drei Stufen:

- **Tier A — 3 lokale Rahmenreduktionen:** ein argumentverträglicher alter
  Träger liegt im Zielregister;
- **Tier B — 4 registerübergreifende Rahmenreduktionen:** der vollständige
  Rahmenweg ist alt, aber nur bei einem anderen Besitzer;
- **Tier C — 4 offene Kontextübertragungen:** die Handlungskette ist alt, doch
  jeder alte Träger nennt das Argument ausdrücklich, während der aktuelle Satz
  „das zuvor Genannte“ erbt.

Keine Tier-C-Karte wird verworfen. Die Stufe sagt nur präzise, welche Annahme
noch zusätzlich zum alten Handgriff nötig ist.

## Die drei lokalen Karten

Pharmazeutisches `P+CH+E+Y` besitzt einen besonders guten alten Träger im
gleichen Register:

`P+CH+E+O+L+Y` → `P+CH+E+Y`

Man entfernt nur AUSFÜHRUNG und VERBINDUNG; DROGENPOSTEN und GRAD I bleiben.
Der aktuelle Satz „Setze den Drogenposten ein und nimm den Drogenposten; auf
Grad I“ folgt damit aus einem wirklichen lokalen Rahmenabbau.

Die beiden kontextuellen `CH+P`-Ziele sind ebenfalls lokal gut. Unter 25 alten
Trägern haben dreizehn bereits ein geerbtes oder freies Argument; je drei davon
liegen in PHARMA und SOURCE_SECTION_T. Die knappsten Wege entfernen nur
FORTSETZEN beziehungsweise AUSGANG:

- `CH+P+OL` → `CH+P` in PHARMA;
- `CH+P+AR` → `CH+P` im Quellenregister.

## Vier gute, aber fremdregisterige Karten

Alle vier alten `S>CHD`-Ereignisse enthalten explizit `Y=POSTEN`. Drei tragen
FORTSETZEN, eines ZIELORT zwischen den Handlungen. Das Ziel `S+CHD+Y` entsteht
jedes Mal durch Entfernen genau dieser einen Relation. Die drei aktuellen
celestialen, pharmazeutischen und Quellen-Sätze erhalten deshalb Tier B: Der
Rahmen ist vierfach alt, nur bislang biologisch.

Auch celestiales `P+CH+E+Y` hat dieselbe exakte Reduktion wie die lokale
pharmazeutische Karte. Das Paar selbst ist im celestialen Register dreimal alt;
die spezielle Kombination Grad I plus Posten kommt als Reduktionsweg aber nur
im pharmazeutischen Träger vor.

## Die vier ehrlichen offenen Karten

`CH+CH` besitzt sieben alte Träger und `CH+SH` drei. Ihre Handlungslesarten sind
durch GDT505 klar. Aber alle zehn alten Träger haben `EXPLICIT_ARGUMENTS`:

- die beste `CH+CH`-Reduktion entfernt EINHEIT plus POSTEN;
- die beste `CH+SH`-Reduktion entfernt DANACH, AUSFÜHRUNG und EINHEIT.

Keiner zeigt bereits dieselbe kontextuelle Objektübernahme wie
„Nimm/Entnimm das zuvor Genannte zweimal“ oder „… und halte es“. Genau dieser
eine Schritt bleibt also offen — nicht NEHMEN, HALTEN, Wiederholung oder
Reihenfolge.

## Bilanz und nächster Schritt

Fünf explizite Zielargument-Karten haben alle eine kompatible Reduktion. Von
sechs Kontextkarten haben zwei (`CH+P`) eine alte Kontextbrücke und vier keine.
Alle elf Annahmen und Sätze bleiben unverändert. Der unabhängige Validator
besteht 508/508 Prüfungen.

Als Nächstes wird nur für die vier Tier-C-Karten nach einer Brücke gesucht:
erstens in den 65 breiteren alten `CH>CH`-Ketten, zweitens in anderen alten
`CH>@ACTION`-Handgriffen mit geerbtem Argument im Source/Pharma-Rahmen. Eine
solche Brücke darf den Handgriff stützen, ohne ein neues Wort oder einen neuen
Zielsatz zu erfinden.

`FRAME_COMPATIBILITY_RANK_ONLY__OPEN_CONTEXTUAL_TARGETS_RETAINED_NOT_REJECTED`
