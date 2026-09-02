# GDT753 — `qokeol/okeol`: Ganzformen statt Bausteinprosa

Status: `PARTIAL__75_EXACT_TARGET_OCCURRENCES_40_PAGES__34_COMPLETE_FIELDS__Q_PROCESS_MATERIAL_MIDDLE_3_BASE_4__Q_PREPARATION_6_BASE_8__DIRECTIONAL_GATE_FAILS__TEN_MATCHED_PAIR_GATES_ZERO__GDT664_GDT666_COMPOSITIONAL_PROSE_DEMOTED__SHARED_HEAT_MIDDLE_HYPOTHESIS_RETAINED__WHOLE_PAIR_LEAD_RETAINED__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE`

## Ergebnis

Die alte Aufteilung hält nicht. Im zugelassenen Cache gibt es 34
reader-exakte `qokeol`- und 41 reader-exakte `okeol`-Vorkommen auf zusammen 40
Seiten. Von ihren target-zentrierten Feldern sind 15 beziehungsweise 19
vollständig begrenzt.

| Form | vollständige Felder | Prozess/Stoff + Mittelstufe | Zubereitung |
|---|---:|---:|---:|
| `qokeol` | 15 | 3 auf 2 Seiten | 6 auf 6 Seiten |
| `okeol` | 19 | 4 auf 4 Seiten | 8 auf 8 Seiten |

Der q-minus-Basis-Unterschied für Prozess/Stoff+Mittelstufe ist `-0.010526`;
der Basis-minus-q-Unterschied für Zubereitung ist `0.021053`. Das ist
praktisch dieselbe Verteilung, nicht die behauptete Gegenüberstellung. Der
gerichtete Test scheitert. Dasselbe gilt für alle fünf frequenzähnlichen
q/Basis- und fünf Nicht-q-Kontrollpaare.

## Woher die konkreten Sätze wirklich kamen

Die Provenienz ist eindeutig:

| Form | bisherige Prosa | Quelle | damalige Konstruktion |
|---|---|---|---|
| `qokeol` | erhitze den Drogenstoff bis zur Mittelstufe | GDT666, `G666-D149` | `QO_COMMAND+K_HOT+E_MIDDLE+OL_MATERIAL` |
| `okeol` | Grundansatz bis zur mittleren Heizstufe erwärmt | GDT664, `G664-D030` | `O_PREP+K_HOT+E_MIDDLE+OL_BASE` |

Beide Karten waren ausdrücklich `PRODUCTIVE_COMPOUND` und ersetzbare
Werkstattwerte. Die konkrete Handlung, der Drogenstoff und der Grundansatz
wurden also aus Analystenbausteinen zusammengesetzt; sie wurden nicht als
unabhängige Bedeutungen der beiden Ganzformen gefunden. Der heutige
No-component-export-Renderer darf diese Karten deshalb nicht als Bestätigung
seiner eigenen Bausteine verwenden.

## Renderer-Korrektur

Die beiden alten Sätze werden als gesprochene Ganzwortwerte abgezogen. Der
explorative Arbeitsdefault lautet nun für beide Formen:

> **Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen.**

Das ist bewusst nicht „bedeutungslos“. Der gemeinsame Wärme-/Stufenansatz
bleibt als Arbeitshypothese erhalten, weil er die Formfamilie weiterhin knapp
beschreibt und hier nicht unmöglich wird. Nicht mehr behauptet werden:

- `qokeol` sei bereits als Imperativ „erhitze“ identifiziert;
- sein Patient sei bereits „Drogenstoff“;
- `okeol` bezeichne bereits einen „Grundansatz“;
- der sichtbare q/Basis-Unterschied schalte sicher zwischen Handlung und
  Zubereitung um.

Die 75-Zeilen-Lesertabelle bewahrt zusätzlich jeden lokal sichtbaren Kontext.
Ein vollständiges Feld kann daher weiterhin konkret „Zubereitungskontext“ oder
„Mittelstufen-Verarbeitungs-/Stoffkontext“ sagen, ohne diesen Nachbarbefund zur
Wortübersetzung umzudeklarieren.

## Was übrig bleibt

Die schwache komplette Paarbeziehung aus GDT751 wird nicht verworfen. Die
beiden Formen können eng verwandt sein; GDT753 zeigt nur, dass diese eine
semantische Umschaltregel sie nicht erklärt. EVA `q`, `o`, `k`, `e`, `ol` und
alle anderen Teilstrings erhalten weiterhin null Exportkredit.

## Nächster Weg

GDT753 zeigt einen reparierbaren systemischen Fehler: Ein Teil der konkreten
V99R7-Prosa wurde als Ganzwort weitergereicht, obwohl ihre Bedeutung vorher aus
alten Bausteinrollen erzeugt worden war. Der nächste Pass soll deshalb die
noch aktiven, häufigen GDT664/GDT666-`PRODUCTIVE_COMPOUND`-Werte gegen
tatsächlich gelernte Ganzwörter trennen. Danach werden nur die Ganzformen mit
unabhängigem Rollenprofil an den historischen Fachwortschatz angeschlossen.
So entfernen wir erfundene Konkretheit, ohne die brauchbaren Arbeitsannahmen
oder die vorhandenen Formfamilien wegzuwerfen.

## Reproduktion

```bash
python3 experiments/yolo/gdt753_qokeol_okeol_whole_role_census/src/run.py
python3 experiments/yolo/gdt753_qokeol_okeol_whole_role_census/src/validate.py
```

Kein neues Blatt, Bild oder Transkript wurde geöffnet; f84 und f84r blieben
gesperrt.
