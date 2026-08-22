# V63 R3 — Deterministischer begrenzter Slot-Parser

## Ergebnis

Der eingefrorene Parser bildet alle **381 Ereignisse**, **135 Felder** und **116 Aussagen** ab, ohne eine neue Kartenbedeutung einzuführen. Er erkennt 119 Ereignisse (31,23 %) durch bereits ausgewählte exakte Merkwörter oder strikte formale Prompts; 262 Ereignisse bleiben ehrlich `EXEMPLAR_ONLY`. Auf Feldebene sind 14/135 Parses vollständig bestimmt, 56/135 gemischt und 65/135 ungeparst. Auf Aussageebene sind es 12/116, 49/116 und 55/116.

Damit ist die Slot-Theorie als kleiner, deterministischer **Teilparser** ausführbar, aber nicht als selbständig semantisch vollständiger Decoder bestätigt. Die vollständige technische Lesung stammt weiterhin aus den ausgewählten lokalen V61/V62-Artefakten. Der Parser darf sie transportieren, aber nicht als Evidenz für seine Schablonen zurückverwenden.

## Eingefrorener Vertrag

Der Parser liest pro Ereignis genau drei voneinander getrennte Kanäle:

1. die atomare exakte `joint_tuple_id` als opake Identität,
2. ein in V60 ausgewähltes exaktes Merkwort, falls vorhanden,
3. einen bereits vorhandenen strikten formalen Prompt, falls vorhanden.

Weder Oberfläche, Kartenkomponenten, Substrings, `PAGE_HOST`, lokale Prosa noch der sichtbare Abschluss erzeugen eine Bedeutung. Ein formaler Prompt liefert nur eine formale Slotoperation mit opakem Wert. Die einzige Überlappung beider lizenzierten Kanäle sind elf `MASS?`/`VORGABEPARAMETER?`-Ereignisse; beide bestimmen unabhängig dieselbe Schablonenklasse, ihre Payloads bleiben getrennt.

Die primitive Zuordnung ist vollständig vor dem Lauf fixiert:

| bereits lizenzierter Trigger | primitive Schablone | Registerwirkung |
|---|---|---|
| `MASS?`; formal `VORGABEPARAMETER?` oder `STANDARDSLOT_SETZEN` | `PARAMETER_ASSIGN` | opaken Parameter setzen; vier Register tragen |
| `ZIEL?`; formal `LOKALEN_RELATIONSSLOT_SETZEN` | `TARGET_ASSIGN` | exaktes Ziel oder formalen Relationsslot getrennt setzen |
| `ANSATZ?`; formal `AKTIVEN_ARBEITSSTAND_VERKNÜPFEN` | `LINK_ACTIVE` | aktiven Stand aufnehmen/verknüpfen |
| `BEREIT?`, `KLAR?` | `STATE_GATE` | Zustand des aktiven Gegenstands setzen |
| `ANWENDEN?` | `ACTION_APPLY` | aktiven Gegenstand am Ziel anwenden |
| `TEMPERIEREN?` | `ACTION_TEMPER` | aktiven Gegenstand temperieren |
| `SPÜLEN?` | `TERMINAL_FLUSH` | spülen und abschließen |
| `ABLASSEN?` | `TERMINAL_DRAIN` | ablassen und abschließen |
| `ANTEIL?` | `SELECT_PART` | aktiven Gegenstand als vorigen sichern, Teil wählen |
| `VORIGES?` | `SELECT_PREVIOUS` | tiefen-eins gespeicherten vorigen Gegenstand aufnehmen |

`COMPOSITE_SEQUENCE` bezeichnet nur eine mehrstellige Quellfolge mit mindestens einer lizenzierten primitiven Schablone. Es füllt keine unbekannte Stelle. `EXEMPLAR_ONLY` kopiert die opake Ereignisidentität und übernimmt den ausgewählten V62-Zustandsumschlag, liefert aber keine semantische Analyse.

Deterministische Priorität je Ereignis:

```text
if exact_trigger and formal_trigger:
    require same template; retain both payloads separately
elif exact_trigger:
    use exact template
elif formal_trigger:
    use formal template with SEMANTIC_VALUE=NONE
else:
    EXEMPLAR_ONLY
```

Ein Feld beziehungsweise eine Aussage ist `UNIQUE`, wenn jedes enthaltene Ereignis eine primitive Schablone hat, `AMBIGUOUS`, wenn bekannte und `EXEMPLAR_ONLY`-Positionen gemischt sind, und `UNPARSED`, wenn keine Position erkannt wird. „Eindeutig“ meint hier ausschließlich Determinismus unter dem eingefrorenen Wörterbuch, nicht historische oder semantische Wahrheit.

## Ereignis- und Einheitenabdeckung

| Ebene | erkannt/eindeutig | gemischt | ungeparst | Gesamt |
|---|---:|---:|---:|---:|
| Ereignisse | 119 | — | 262 | 381 |
| Felder | 14 | 56 | 65 | 135 |
| Aussagen | 12 | 49 | 55 | 116 |

Die 119 erkannten Ereignisse verteilen sich auf `PARAMETER_ASSIGN` 29, `LINK_ACTIVE` 26, `TARGET_ASSIGN` 16, `STATE_GATE` 11, `ACTION_APPLY` 10, `TERMINAL_FLUSH` 8, `TERMINAL_DRAIN` 8, `ACTION_TEMPER` 7, `SELECT_PART` 2 und `SELECT_PREVIOUS` 2. Darin liegen 85 V60-Merkwortvorkommen und 45 formale Promptvorkommen bei elf konvergenten Überlappungen.

Die Abschlussregel ist streng: Alle acht `TERMINAL_FLUSH`- und acht `TERMINAL_DRAIN`-Vorkommen sind tatsächlich terminal; `CLOSE` allein kann jedoch keine der beiden Klassen wählen. Die formale Achse erzeugt daher weder „spülen“ noch „ablassen“.

## Vier Register und Round-trip

Jede Aussage beginnt mit dem ausgewählten V62-Zustand von `OWNER`, `ACTIVE_ITEM/PREPARATION`, `TARGET/STATION` und `PREVIOUS_ITEM`. Danach werden die beobachteten primitiven Schablonen in Ereignisreihenfolge als symbolische Wirkungen protokolliert; der ausgewählte V62-Postzustand ist die verbindliche Zustandsgrenze. Bei mehrfeldrigen Aussagen werden keine nicht beobachteten Zwischenzustände erfunden. Feldzeilen kennzeichnen deshalb ausdrücklich `NO_UNLICENSED_WITHIN_STATEMENT_STATE;USE_STATEMENT_ENVELOPE`.

Beispiele aus f82r zeigen die drei Ergebnisse:

- `B2-S013` / F060 / E210: allein `TERMINAL_DRAIN`, daher `UNIQUE`.
- `B2-S004` / E172–176: `TARGET_ASSIGN > EXEMPLAR_ONLY > EXEMPLAR_ONLY > ACTION_TEMPER > EXEMPLAR_ONLY`, daher `AMBIGUOUS`.
- `B2-S001` / F045 / E167: allein `EXEMPLAR_ONLY`, daher `UNPARSED`; nur der ausgewählte V62-Umschlag führt von leerem Zustand zu den anonymen B2-Registern.

Für jedes Feld und jede Aussage speichert der Parser die geordnete Folge `E<serial>@<joint_tuple_id>` sowie einen SHA-256-Identitätsdigest. Die Rückdekodierung rekonstruiert dadurch alle 135 Feld- und 116 Aussagefolgen exakt. Dieser Erfolg ist **Identitäts-Round-trip**, nicht Bedeutungs-Round-trip: Entfernt man die opaken IDs, kollabieren unbekannte Exemplare und viele Einheiten werden ununterscheidbar.

## Baselines

| Ebene / Modell | primitive Ereignisse | eindeutig / gemischt / ungeparst | Primärschablone wie Parser | lookup-eindeutige Einheiten | größte Kollision |
|---|---:|---:|---:|---:|---:|
| Feld / begrenzter Parser | 119 | 14 / 56 / 65 | 135/135 | 135/135 | 1 |
| Feld / Merkwortbeutel | 85 | 13 / 44 / 78 | 122/135 | 15/135 | 78 |
| Feld / nur Form | 45 | 1 / 34 / 100 | 100/135 | 39/135 | 44 |
| Aussage / begrenzter Parser | 119 | 12 / 49 / 55 | 116/116 | 116/116 | 1 |
| Aussage / Merkwortbeutel | 85 | 12 / 41 / 63 | 108/116 | 16/116 | 63 |
| Aussage / nur Form | 45 | 0 / 31 / 85 | 86/116 | 34/116 | 40 |

Der `MNEMONIC_BAG` verwirft Reihenfolge, 45 formale Vorkommen und sämtliche opake Exemplaridentität. `FORM_ONLY` behält die geordnete Prompt-/Terminalgestalt, verliert aber exakte Kartenaktionen und kann insbesondere Spülen und Ablassen nicht unterscheiden. Der begrenzte Parser gewinnt gegenüber beiden, weil er die zwei lizenzierten Kanäle getrennt vereint; seine perfekte Lookup-Eindeutigkeit wird jedoch durch die opaken IDs erkauft und ist kein semantischer Gewinn.

## Stärkster Widerspruch und Urteil

Der stärkste Widerspruch ist quantitativ: 262/381 Ereignisse und 55/116 vollständige Aussagen besitzen überhaupt keinen lizenzierten primitiven Trigger. Weitere 49 Aussagen enthalten Lücken. Die ausgewählten kreativen Lesungen sind daher nicht aus diesen zwölf Schablonen allein generierbar. Zudem werden V62-Zustandsübergänge als ausgewählte Umschläge übernommen, nicht aus den 119 erkannten Ereignissen vollständig hergeleitet.

Urteil: **KEEP als deterministischer, begrenzter Strukturparser; WITHDRAW als vollständiger Bedeutungsdecoder.** Er ist reproduzierbar, verhindert String-/Komponentenvererbung und macht die Restunsicherheit sichtbar. Seine belastbare Leistung ist die verlustfreie Quelladressierung, die geordnete Ausführung lizenzierter Prompts und die kontrollierte Übergabe an die V62-Zustandsmaschine.

## Artefakte und Reproduktion

- `V63_R3_TEMPLATE_DEFINITIONS.tsv`: zwölf erlaubte Schablonen und Bindungsregeln.
- `V63_R3_381_EVENT_TEMPLATE_LEDGER.tsv`: vollständige Ereigniszuordnung.
- `V63_R3_135_FIELD_SLOT_PARSE.tsv`: vollständige Feldzuordnung und Zustandsumschläge.
- `V63_R3_116_STATEMENT_SLOT_PARSE.tsv`: vollständige Aussagezuordnung und Registerupdates.
- `V63_R3_BASELINE_COMPARISON.tsv`: eingefrorener Vergleich mit Merkwortbeutel und Form-only.
- `V63_R3_BUILD_BOUNDED_SLOT_PARSER.py`: deterministischer Builder.
- `V63_R3_VALIDATE_BOUNDED_SLOT_PARSER.py`: Quellen-, Zählungs-, Vertrags-, Zustands- und Round-trip-Prüfung.

Ausführung im Artefaktordner:

```bash
python3 V63_R3_BUILD_BOUNDED_SLOT_PARSER.py
python3 V63_R3_VALIDATE_BOUNDED_SLOT_PARSER.py
```

Der Validator erwartet exakt sieben zugelassene Seiten, elf Prosa-Records, 381 Ereignisse, 135 Felder, 116 Aussagen, vier Register und keine `PAGE_HOST`-Ableitung.
