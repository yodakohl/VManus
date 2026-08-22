# V65 R3 — Vollständige technische Wasserwerksedition

## Ergebnis

Der stärkste rein nichtmedizinische Rivale ist als ausführbares Becken-/Leitungsregister vollständig gebaut: **6 Records, 97 Aussagen, 115 Felder, 281 Ereignisse**. Jeder Record besitzt einen deterministischen Prozess-/Zustandsgraphen und einen vollständigen deutschen Defaulttext mit Becken, Zuführung, Leitungswahl, Filter, Erwärmung, Zirkulation, Spülung, Ablass, Rücklauf, Wartung und Übergabe.

Die Ausgabe ist keine Entzifferung. Nur 90/281 Ereignisse besitzen eine lizenzierte V63-Schablone; 191 bleiben `EXEMPLAR_ONLY`. Die festen Status bleiben unverändert:

```text
Felder:    14 UNIQUE / 41 AMBIGUOUS / 60 UNPARSED
Aussagen:  12 UNIQUE / 35 AMBIGUOUS / 50 UNPARSED
```

## Schichten- und Ausführungsvertrag

```text
opake joint_tuple_id
 -> fixer V60-Wert oder opaker formaler Prompt
 -> ausgewählte V61-Aussagegrenze
 -> unveränderter V62-Zustandsumschlag
 -> unveränderter V63-Parse-Status
 -> eingefrorene recordlokale Anlagenphase
 -> lokales Becken-/Leitungsnomen als EXEMPLAR, niemals Kartenglosse
```

Der Executor folgt der Feldreihenfolge. Eine vorab feste Anlagenphase darf nur durch bereits lizenzierte `TERMINAL_FLUSH`, `TERMINAL_DRAIN`, `ACTION_TEMPER`, `ACTION_APPLY` oder ein exaktes Zustands-Gate überschrieben werden. Danach wird der V62-Umschlag von `OWNER`, `ACTIVE_ITEM/PREPARATION`, `TARGET/STATION` und `PREVIOUS_ITEM` angewandt. Die opake Ereignisfolge bleibt vollständig rücklesbar.

Von 85 terminalen Feldern besitzen nur 16 eine exakte Spül-/Ablasskarte. Die übrigen 69 erhalten ausschließlich `OPAQUE_FIELD_COMMIT_ONLY`; `CLOSE` erzeugt weder „spülen“ noch „ablassen“. Weitere 30 Felder bleiben offen.

## Sechs Prozessgraphen

| Record | technische Anlage und Prozess | F/S/E | erkannte Ereignisse | Kosten T/M | Gewinner |
|---|---|---:|---:|---:|---|
| B1 | Grundbecken A: spülen, Charge zuführen, erwärmen, über Rinne zirkulieren, absetzen, filtern, rückführen, warten und übergeben | 24/21/66 | 23 | 132/129 | iatromedizinisch |
| B2 | Teilbecken B mit Z1–Z3: temperieren, verzweigen, filtern, am technischen Ziel einsetzen, ablassen, nachfüllen, spülen | 26/22/62 | 16 | 135/132 | iatromedizinisch |
| B3 | Hauptbecken C: mehrfache L1–L4-Zuführung, W3, F3, U3 und R3; wiederholte Stations-, Ablass-, Filter- und Rücklaufgänge | 38/34/86 | 29 | 188/184 | iatromedizinisch |
| B4 | Nachklärbecken D: warmer Nachgang, Teilcharge, F4, Spülung, U4-Ablass, Nachfüllung und Rückleitung R4 | 20/16/47 | 15 | 106/103 | iatromedizinisch |
| B5 | Übergabebecken E: Altbestand abziehen, einmal erwärmen, halten, Vorcharge/Maß verknüpfen und über L5 übergeben | 5/3/11 | 4 | 22/23 | technisch |
| B6 | offenes Kaltbecken F: Stand aufnehmen, durch F6 führen, Maß buchen und mit Z6 verknüpfen; kein Commit | 2/1/9 | 3 | 14/16 | technisch |

Die vollständigen Feld-, Phasen-, lokalen Zustands- und V62-Transitionspfade stehen in `V65_R3_6_RECORD_PROCESS_STATE_GRAPHS.tsv`. Die sechs deutschen Anlagenartikel stehen vollständig in `V65_R3_6_RECORD_WATERWORK_EDITION.tsv`.

## Direkter Vergleich

Alle 115 Felder und alle 97 identischen V61-Aussagen werden zeilenweise gegen die iatromedizinische Fassung verglichen. Auf Feldebene ergeben sich 14 technische, 26 iatromedizinische und 75 gleiche Urteile; auf Aussageebene 13 technische, 25 iatromedizinische und 59 Gleichstände.

Die Kostenregel ist symmetrisch und vor dem Endlauf fixiert: jede ungeparste Exemplarfüllung, lokaler Prozess, Medium, neue Station/Ziel sowie Filter-/Rücklaufmechanismus kosten je 1; Domänenzweck und menschliche Rolle/Körperbezug je 2. V60-Werte, formale Prompts und V62-Register kosten 0. Wenn eine Zelle in der medizinischen Lesung eine sichtbare oder lokal expandierte Person/Körperanwendung trägt, muss der reine technische Rivale dieselbe Zelle als Bediener, Maßfigur oder Stationsmarke bezahlen; Menschen dürfen nicht kostenlos verschwinden.

Gesamtkosten: **597 technisch gegenüber 587 iatromedizinisch**. Das ist ein Beschreibungsmaß, keine Wahrscheinlichkeit.

## Urteil und stärkster Widerspruch

Der Wasserwerksrivale ist vollständig, deterministisch und besonders stark bei den menschenarmen Nachträgen B5/B6 sowie den sichtbar figurenlosen Auslässen in B3. Er scheitert als Gesamtsieger an zwei Punkten:

- 191 Ereignisse, 60 Felder und 50 ganze Aussagen benötigen lokale Exemplare;
- B1–B4 zeigen beziehungsweise expandieren wiederholt menschliche Anwendung. Der reine Anlagenplan muss diese Figuren umdeuten, während die ausgewählte therapeutische Balneologie zugleich Menschen **und** reale Apparatetechnik erklärt.

Urteil: **KEEP als stärkster vollständig ausführbarer nichtmedizinischer Biological-Rivale; die ausgewählte iatromedizinische Apparate-Hybridfassung bleibt insgesamt knapp kohärenter.** Kein lokales Becken-, Wasser-, Rohr-, Filter- oder Personennomen wird ins Kartenwörterbuch übernommen.

## Artefakte

- `V65_R3_281_EVENT_WATERWORK_LEDGER.tsv`
- `V65_R3_115_FIELD_WATERWORK_EDITION.tsv`
- `V65_R3_97_STATEMENT_COMPARISON.tsv`
- `V65_R3_6_RECORD_WATERWORK_EDITION.tsv`
- `V65_R3_6_RECORD_PROCESS_STATE_GRAPHS.tsv`
- `V65_R3_12_RECORD_MODEL_ASSUMPTION_COSTS.tsv`
- `V65_R3_BUILD_WATERWORK_EDITION.py`
- `V65_R3_VALIDATE_WATERWORK_EDITION.py`

```bash
python3 V65_R3_BUILD_WATERWORK_EDITION.py
python3 V65_R3_VALIDATE_WATERWORK_EDITION.py
```
