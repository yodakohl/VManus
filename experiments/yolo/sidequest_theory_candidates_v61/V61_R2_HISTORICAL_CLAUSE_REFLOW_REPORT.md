# V61 R2 — Historische Quellenklauseln und Zeilen-Reflow

## Entscheidung

Die 57 physischen Zeilen der elf Prosa-Records ergeben **nicht** 57 Sätze.
Ebenso wenig bilden sie eine einzige fortlaufende Prosa. Die historisch
sparsamste Arbeitslesung ist eine Mischform aus Herbal-/Rezeptparataxe und
kurzen Bade-/Gefäßzellen:

- 14 von 46 record-internen Zeilenübergängen setzen **dieselbe Klausel** fort;
- 9 nehmen einen noch aktiven Gegenstand in einer **neuen Klausel** wieder auf;
- 11 beginnen eine neue parataktische Klausel;
- 11 wechseln in die nächste parallele Arbeitszelle;
- 1 bleibt unaufgelöst.

Damit tragen 23/46 Grenzen einen semantischen Überhang, 22/46 einen wirklichen
Klausel- oder Zellwechsel. Zusätzlich liegen 78 Feldgrenzen innerhalb einer
physischen Zeile. Die physische Zeile ist also ein aktives Schreib- und
Layoutmaß, aber weder notwendige noch hinreichende Satzgrenze.

Dies bleibt eine kreative Quellenedition, keine Entzifferung. Kein Wert erhält
Lautung, Sprache oder neue Kartenbedeutung.

## Feste Entscheidungsklassen

| Klasse | Quellenlesung | Wirkung auf Statement-ID |
|---|---|---|
| `CONTINUE_SAME_CLAUSE` | Ein offenes Argument, Zeitfragment oder Arbeitsgang wird nach dem Zeilenwechsel vollendet. | dieselbe ID |
| `START_NEW_CLAUSE` | Der Record bleibt aktiv, doch ein neuer parataktischer Rezept- oder Handlungssatz beginnt. | neue ID |
| `RESUME_ACTIVE_ITEM` | Eine neue Klausel übernimmt still denselben Simplex, Ansatz, die Flüssigkeit oder Station. | neue ID, aktiver Referent bleibt |
| `NEXT_PARALLEL_CELL` | Die nächste kurze Listen-/Arbeitszelle folgt ohne syntaktische Fortsetzung. | neue ID |
| `UNRESOLVED` | Reflow, Neustart, Dittographie und Kopierhilfe lassen sich nicht trennen. | neue vorläufige ID |

`V61_R2_46_INTERLINE_BOUNDARIES.tsv` katalogisiert jede Grenze mit beiden
Feldern, Schlussstatus, deutscher Reflow-Vorschau, historischem Mechanismus,
Gegenrivalen und Konfidenz.

## Statement-Ausgabe und strikte Schichtentrennung

Die 135 Felder werden auf **121 ausführbare Quellenstatements** abgebildet. 13
Statements überqueren mindestens eine physische Zeile; H5 besitzt dabei eine
dreizeilige Klausel. Jedes Statement erhält eine konkrete deutsche
Rezept-/Arbeitsparataxe, ohne seine Feldfolge umzuschreiben.

In den TSVs gilt:

```text
{sichtbare Form/KARTE=V60-KURZMERKER}  = einziger exakter semantischer Anker
[STILL_GRAMMAR: ...]                  = Artikel, Objekt, Besitzer, Flexion usw.
[EXEMPLAR: ...]                       = lokale V59-Erweiterung eines UNKNOWN-Ereignisses
```

Die elf Kurzmerker bleiben unverändert: `MASS?`, `ANWENDEN?`, `BEREIT?`,
`ANSATZ?`, `ZIEL?`, `KLAR?`, `VORIGES?`, `ANTEIL?`, `TEMPERIEREN?`, `SPÜLEN?`
und `ABLASSEN?`. Sie decken 85 Ereignisse. Die übrigen 296 Ereignisse bleiben
`UNKNOWN`; ihre konkreten Wörter sind ausdrücklich Exemplartext und keine
Kartenwerte. Auch Ergänzungen wie Pflanze, Wurzel, Wein, Becken, Person, Tuch,
Körperstelle, Zahl oder Zielgefäß sind still und lokal.

`V61_R2_135_FIELD_STATEMENT_MAP.tsv` weist jedes Feld genau einmal zu.
`V61_R2_121_STATEMENTS.tsv` enthält pro Statement die vollständige Expansion,
Ankerfolge, alle stillen Ergänzungen, Klauselklasse und den historischen
Rivalen.

## Elf Record-Rekonstruktionen

| Record | Zeilen / Felder / Statements | stärkste Reflow-Lesung | stärkste Sollbruchstelle |
|---|---:|---|---|
| H1 | 2 / 2 / 2 | Die zweite Zeile nimmt die bereits bereitete Arznei als aktiven Gegenstand wieder auf. | Der Gegenstand ist nur im lokalen Exemplar, nicht in einer exakten Karte ausgedrückt. |
| H2 | 3 / 3 / 2 | f10r.6–.8 können eine offene Simplex-Bereitung bilden; f10r.9 beginnt den Gebrauch bei geöffneter Blüte neu. | Die Reihenfolge Wachstum–Bereitung–Sammelzeit ist unglatt; zwei selbstständige Listenpunkte bleiben stark. |
| H3 | 3 / 4 / 4 | Die zurückbehaltene Blütenkrone wird nach dem Zeilenwechsel als Anwendungsstoff wieder aufgenommen. | Das Folgefeld nennt wieder den abgebildeten Simplex und könnte einen ganz neuen Teil eröffnen. |
| H4 | 2 / 4 / 4 | Nach abgeschlossener Waschung eröffnet „zweiter Arzneigebrauch“ eine neue parataktische Klausel. | Medium und Anwendung bleiben bild-/genregeleitete Ergänzungen. |
| H5 | 7 / 7 / 5 | Sammeln, Ausziehen/Anwenden und Trocknen bilden eine dreizeilige Erstklausel; danach folgen Teilposten. | 21/27 Ereignisse sind opak; die Artikelgliederung kann ebenso eine Materialliste sein. |
| B1 | 7 / 24 / 22 | Exaktes `VORIGES?` am Beginn f81v.7 ist der beste aktive-Ansatz-Übertrag; zwei weitere offene Schritte fließen über die Zeile. | Becken, Rücklauf und Anwendung stammen aus Bild/Genre; kurze Zellen können rein technische Stationen sein. |
| B2 | 8 / 26 / 24 | Nächstes Becken, klare Flüssigkeit und offene Zutatenfolge werden jeweils in der Folgezeile ausgeführt. | Die beidseits einer Grenze wiederholte Postenformel ist Catchword, Dittographie oder echter Neustart; Entscheidung unmöglich. |
| B3 | 10 / 38 / 35 | Drei offene Arbeitsgänge laufen weiter; zwei andere nehmen Flüssigkeit/Portion in neuer Klausel wieder auf. | 50/86 Ereignisse sind opak und viele terminale Kurzfelder sprechen für ein Zellregister, nicht Prosa. |
| B4 | 10 / 20 / 18 | Gemischter Posten, Dauerangabe und Zielbezug werden über drei Grenzen wiederaufgenommen oder vollendet. | Auflage/Körper und Leitung/Gefäß sind gleichwertige Bildwelten; drei Grenzen passen besser zu Parallelzellen. |
| B5 | 3 / 5 / 4 | Das isolierte Zeitfragment auf f83r.47 verlangt Reflow; die vorige Mischung wird danach erneut aufgenommen. | Drei offene Felder erlauben auch eine technische Frist-/Übergabeliste ohne Satzsyntax. |
| B6 | 2 / 2 / 1 | Beide offenen Felder ergeben gemeinsam: kalten Vorlauf übernehmen, messen, durch Tuch/Öffnung zum Ziel führen. | Sechs von neun Ereignissen bleiben opak; Person, Filter und Ziel sind vollständig still ergänzt. |

Die vollständigen Recordtexte, Zählungen, Statement-IDs, Ankerinventare,
historischen Analogien und jeweiligen nichtmedizinischen Rivalen stehen in
`V61_R2_11_RECORD_RECONSTRUCTIONS.tsv`.

## Historischer Mechanismus

Für H1–H5 ist ein kompilierter Simplexartikel mit Bildlemma und angehängten
kurzen Rezeptgliedern plausibel. Ein Schreiber kann den Bildbesitzer über
mehrere Zeilen still halten und neue Glieder parataktisch wie *recipe* oder
*item* beginnen. Wiederaufnahmen nach Art von *de eodem*, *idem* oder
*praedictum* sind passende Funktionsvergleiche; keines dieser lateinischen
Wörter wird einer Voynich-Karte gleichgesetzt.

Für B1–B6 ist eine Folge kurzer Bade-, Wasch-, Irrigations- oder
Gefäßoperationen plausibler als ein durchgehender moderner Prosatext. Der
aktive Stoff oder die sichtbare Station kann fortgelten, während eine lokale
Terminalkarte die Arbeitszelle schließt. Dieselbe Schreibpraxis trägt jedoch
auch ein nichtmedizinisches Wasserwerk- oder Werkstattregister; Figuren und
Rohrformen entscheiden den Besitzer nicht zuverlässig.

Eine echte Kustode ist primär Kopier- und Lagenhilfe, nicht automatisch ein
semantischer Zeilenverknüpfer. Deshalb wird nur IB013 mit feldinitialem exaktem
`VORIGES?` als starker expliziter Übertrag gewertet. IB020 wiederholt die
gesamte lokale Postenformel beidseits der Grenze und bleibt ausdrücklich
`UNRESOLVED`: catchwordartige Wiederholung, Dittographie oder zwei gleiche
Arbeitszellen sind gleich gut möglich.

## Stärkster historischer Rivale

Der stärkste Gesamtrivale ist kein anderer Fließtext, sondern eine bebilderte
Material-/Stationsliste: Herbal-Zeilen katalogisieren Teile und getrennte
Verwendungen; Bio-Felder sind unabhängige Gefäß-, Leitungs- oder Badezellen.
Diese Lesung erklärt besonders die vielen Ein-Feld-Terminalsätze und benötigt
weniger still fortgeltende Syntax. Gegen sie sprechen die 14 gut lesbaren
offenen Reflows, das fragmentarische Zeitglied B5 und der anaphorische
`VORIGES?`-Einstieg B1. Die Daten entscheiden daher für ein gemischtes
Klausel-/Zellmodell, nicht für reine Prosa.

## Validierung und Scope

`V61_R2_VALIDATION.json` meldet **PASS**: 11 Records, 57 Zeilen, 135 Felder,
381 Ereignisse, 121 Statements und 46 vollständig klassifizierte
Zeilenübergänge. Die kanonischen Feldexpansionen und alle elf V60-Kurzmerker
sind byteinhaltlich übernommen; keine neue Kurzglosse erscheint. Alle
seitenführenden Quellen wurden vor Materialisierung auf die sieben erlaubten
Prosaseiten gefiltert. Keine V61-Geschwisterdatei, keine neue Seite und weder
f84 noch f84r wurden gelesen; keine externe Recherche wurde durchgeführt.
