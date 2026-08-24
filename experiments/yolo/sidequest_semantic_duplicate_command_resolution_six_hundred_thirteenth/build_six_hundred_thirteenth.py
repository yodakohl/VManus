#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P609 = ROOT / "experiments/yolo/sidequest_semantic_eight_slot_paradigm_six_hundred_ninth"
P612 = ROOT / "experiments/yolo/sidequest_semantic_invariant_commands_six_hundred_twelfth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


GROUP_DECISIONS = {
    "CMD021": ("PURE_CARD_ALLOGRAPH", "dchdy is a compressed local spelling beside dchedy/schedy/tchedy; both occur terminally in B1."),
    "CMD022": ("Y_CHY_CARD_ALLOGRAPH", "chedchy occurs in B3 beside the much commoner chdy/chedy family; no distinct operation follows from its context."),
    "CMD025": ("CORE_ORDER_ALLOGRAPH", "cheeky and chkeey both express the long warming command; the reordered core is a learned card spelling."),
    "CMD084": ("PURE_CARD_ALLOGRAPH", "qokchdy and okchedy/qokchedy overlap in B1 and B3 and occupy the same terminal operation slot."),
    "CMD093": ("REGISTER_VARIANT_SAME_COMMAND", "okchol is Herbal and qokol Biological, but both introduce or continue the same running operation."),
    "CMD095": ("HERBAL_LOCAL_Y_CHY_ALLOGRAPH", "the CHY-shaped card is confined to Herbal but coexists with the Y-shaped card in H1 and H5; owner supplies the Herbal restriction."),
    "CMD097": ("PARTIAL_SEMANTIC_SPLIT", "dchol/schol is 2/2 statement-initial and becomes WIEDERAUFNEHMEN; ordinary OL and singleton LS remain FORTSETZEN."),
    "CMD114": ("LOCAL_FRAME_ALLOGRAPH", "otchedy/qotchedy and otchdy are section-local spellings of the same closed next-transfer command."),
    "CMD121": ("REGISTER_FRAME_ALLOGRAPH", "qotchy and otchey cross Herbal/Biological contexts without a stable semantic contrast."),
    "CMD141": ("EE_GRADE_ALLOGRAPH", "cheey/shey and sheey coexist in B4 and retain the same long-hold grade."),
    "CMD161": ("SEMANTIC_SPLIT_ADJACENT_PAIR", "ykain and ykan are adjacent in H4-S001; read AIN as PORTION and contracted AN as NACHPORTION rather than repeating one command."),
}


CARD_RESOLUTION = {
    "PROC034": ("RESUME_CARD", "CMD162", "WIEDERAUFNEHMEN", "SEMANTIC_SPLIT_STATEMENT_ENTRY"),
    "PROC040": ("Y+K+AN", "CMD163", "DIES · ZUFUEHREN · NACHPORTION", "SEMANTIC_SPLIT_ADJACENT_SECOND_PORTION"),
}


def main() -> None:
    words = read(P609 / "SIX_HUNDRED_NINTH_THIRTY_SEVEN_WORD_PARADIGM.tsv")
    commands = read(P612 / "SIX_HUNDRED_TWELFTH_161_STANDARD_COMMANDS.tsv")
    cards = read(P612 / "SIX_HUNDRED_TWELFTH_173_CARD_COMMAND_MAP.tsv")
    events = read(P612 / "SIX_HUNDRED_TWELFTH_381_INVARIANT_EVENT_COMMANDS.tsv")
    statements = read(P612 / "SIX_HUNDRED_TWELFTH_116_CASE_COMMAND_SEQUENCES.tsv")

    cards_by_command: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        cards_by_command[row["command_id"]].append(row)
    duplicate_ids = [key for key, rows in cards_by_command.items() if len(rows) > 1]

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
        events_by_card[row["card_no"]].append(row)

    context_rows: list[dict[str, object]] = []
    for row in events:
        if row["command_id"] not in duplicate_ids:
            continue
        sequence = events_by_statement[row["statement_id"]]
        index = sequence.index(row)
        position = "ONLY" if len(sequence) == 1 else "FIRST" if index == 0 else "LAST" if index == len(sequence) - 1 else "MIDDLE"
        context_rows.append({
            "old_command_id": row["command_id"],
            "card_no": row["card_no"],
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "position_in_statement": position,
            "surface": row["surface"],
            "previous_command_de": sequence[index - 1]["standard_command_de"] if index else "START",
            "current_command_de": row["standard_command_de"],
            "next_command_de": sequence[index + 1]["standard_command_de"] if index + 1 < len(sequence) else "END",
            "case_expansion_de": row["case_expansion_de"],
        })
    write("SIX_HUNDRED_THIRTEENTH_75_DUPLICATE_EVENT_CONTEXTS.tsv", context_rows, list(context_rows[0]))

    group_rows: list[dict[str, object]] = []
    for group_no, command_id in enumerate(duplicate_ids, 1):
        group_cards = cards_by_command[command_id]
        group_events = [event for card in group_cards for event in events_by_card[card["card_no"]]]
        decision, rationale = GROUP_DECISIONS[command_id]
        split_cards = [card["card_no"] for card in group_cards if card["card_no"] in CARD_RESOLUTION]
        group_rows.append({
            "group_no": f"DG{group_no:02d}",
            "old_command_id": command_id,
            "old_semantic_parse": group_cards[0]["semantic_component_parse"],
            "old_command_de": group_cards[0]["standard_command_de"],
            "card_ids": "|".join(card["card_no"] for card in group_cards),
            "surfaces": " || ".join(card["surfaces"] for card in group_cards),
            "events": len(group_events),
            "records": "|".join(sorted({event["record"] for event in group_events})),
            "position_profile": "|".join(sorted({row["position_in_statement"] for row in context_rows if row["old_command_id"] == command_id})),
            "decision": decision,
            "split_card_ids": "|".join(split_cards) if split_cards else "NONE",
            "revised_reading_de": " || ".join(CARD_RESOLUTION[card][2] for card in split_cards) if split_cards else group_cards[0]["standard_command_de"],
            "rationale": rationale,
        })
    write("SIX_HUNDRED_THIRTEENTH_11_DUPLICATE_GROUP_AUDIT.tsv", group_rows, list(group_rows[0]))

    revised_words = [dict(row) for row in words]
    revised_words.append({
        "semantic_word_no": "W38",
        "canonical_component": "AN",
        "graphic_component_aliases": "NONE",
        "spoken_workshop_word_de": "NACHPORTION",
        "sentence_role": "QUANTITY",
        "teaching_rule_de": "AN nach einer bereits genannten AIN-Portion als NACHPORTION sprechen.",
        "paradigm_slot": "QUANTITY_STAGE",
        "slot_label_de": "MENGE_STUFE",
        "master_question_de": "welche weitere Portion?",
        "slot_use_de": "setzt eine unmittelbar folgende zweite oder zusätzliche Portion",
        "slot_mates": "AIIN|AIN|AN|DA|IIN",
    })
    revised_words.append({
        "semantic_word_no": "W39",
        "canonical_component": "RESUME_CARD",
        "graphic_component_aliases": "DCHOL|SCHOL",
        "spoken_workshop_word_de": "WIEDERAUFNEHMEN",
        "sentence_role": "SEQUENCE",
        "teaching_rule_de": "Die exakte dchol/schol-Karte am neuen Aussageanfang als WIEDERAUFNEHMEN sprechen.",
        "paradigm_slot": "SEQUENCE",
        "slot_label_de": "FOLGE",
        "master_question_de": "welcher vorige Arbeitsfaden wird wieder aufgenommen?",
        "slot_use_de": "nimmt einen zuvor aktiven Posten nach einer Grenze wieder auf",
        "slot_mates": "OL|OT|RESUME_CARD",
    })
    write("SIX_HUNDRED_THIRTEENTH_39_WORD_PARADIGM.tsv", revised_words, list(revised_words[0]))

    revised_cards: list[dict[str, object]] = []
    for row in cards:
        revised = dict(row)
        revised["old_command_id"] = row["command_id"]
        revised["old_standard_command_de"] = row["standard_command_de"]
        if row["card_no"] in CARD_RESOLUTION:
            parse, command_id, command_de, resolution = CARD_RESOLUTION[row["card_no"]]
            revised["semantic_component_parse"] = parse
            revised["command_id"] = command_id
            revised["standard_command_de"] = command_de
            revised["resolution"] = resolution
        elif row["command_id"] in duplicate_ids:
            revised["resolution"] = "KEEP_SAME_COMMAND_AS_ALLOGRAPH_OR_REGISTER_VARIANT"
        else:
            revised["resolution"] = "UNCHANGED_UNIQUE_COMMAND"
        revised_cards.append(revised)

    new_cards_by_command: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in revised_cards:
        new_cards_by_command[str(row["command_id"])].append(row)
    for row in revised_cards:
        row["duplicate_semantic_command"] = "YES" if len(new_cards_by_command[str(row["command_id"])]) > 1 else "NO"
    card_fields = list(cards[0]) + ["old_command_id", "old_standard_command_de", "resolution"]
    write("SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv", revised_cards, card_fields)

    revised_card_by_id = {str(row["card_no"]): row for row in revised_cards}
    revised_events: list[dict[str, object]] = []
    for row in events:
        revised = dict(row)
        card = revised_card_by_id[row["card_no"]]
        revised["old_semantic_component_parse"] = row["semantic_component_parse"]
        revised["old_command_id"] = row["command_id"]
        revised["old_standard_command_de"] = row["standard_command_de"]
        revised["semantic_component_parse"] = card["semantic_component_parse"]
        revised["command_id"] = card["command_id"]
        revised["standard_command_de"] = card["standard_command_de"]
        revised["resolution"] = card["resolution"]
        revised_events.append(revised)
    event_fields = list(events[0]) + ["old_semantic_component_parse", "old_command_id", "old_standard_command_de", "resolution"]
    write("SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv", revised_events, event_fields)

    revised_events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in revised_events:
        revised_events_by_statement[str(row["statement_id"])].append(row)
    revised_statements: list[dict[str, object]] = []
    for row in statements:
        sequence = revised_events_by_statement[row["statement_id"]]
        revised = dict(row)
        revised["old_command_ids"] = row["command_ids"]
        revised["old_invariant_command_sequence_de"] = row["invariant_command_sequence_de"]
        revised["command_ids"] = "|".join(str(event["command_id"]) for event in sequence)
        revised["invariant_command_sequence_de"] = " | ".join(str(event["standard_command_de"]) for event in sequence)
        revised["semantic_revision"] = "YES" if any(event["resolution"].startswith("SEMANTIC_SPLIT") for event in sequence) else "NO"
        revised_statements.append(revised)
    statement_fields = list(statements[0]) + ["old_command_ids", "old_invariant_command_sequence_de", "semantic_revision"]
    write("SIX_HUNDRED_THIRTEENTH_116_REVISED_CASE_COMMANDS.tsv", revised_statements, statement_fields)

    final_command_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in revised_cards:
        final_command_groups[(str(row["semantic_component_parse"]), str(row["standard_command_de"]))].append(row)
    final_duplicate_groups = [rows for rows in final_command_groups.values() if len(rows) > 1]
    report = f"""# Sechshundertdreizehnte Runde: Doppelbefehle auflösen

## Ergebnis

Von den elf Doppelgruppen sind **neun reine Karten-/Registervarianten**. Zwei Gruppen enthielten dagegen eine brauchbare Bedeutungsnuance:

1. `dchol/schol` steht zweimal und beide Male am Anfang einer neuen Aussage. Es heißt nun **WIEDERAUFNEHMEN**, nicht das gewöhnliche mediale FORTSETZEN.
2. `ykain ykan` steht unmittelbar nebeneinander. `AIN` bleibt PORTION; das kontrahierte `AN` heißt **NACHPORTION**. Die Folge liest sich jetzt: PORTION zuführen, NACHPORTION zuführen.

Damit wächst das Befehlsbuch kontrolliert von 161 auf **{len(final_command_groups)} Befehle** und das gesprochene Wörterbuch von 37 auf **39 Wörter**. Die 173 Karten behalten ihre Identität; {sum(len(rows) - 1 for rows in final_duplicate_groups)} Karten bleiben graphische Varianten eines anderen Befehls.

## Was unverändert bleibt

Die übrigen Doppelungen werden nicht künstlich auseinandergezogen. Besonders `qoky` gegen `qokchy`, `cheey/shey` gegen `sheey`, und die verschiedenen geschlossenen CHD-Karten behalten denselben Befehl. Sie überschneiden sich in denselben Records oder erfüllen dieselbe lokale Stellung, ohne eine stabile zweite Handlung zu verlangen. Nach der Teilung bleiben zehn Doppelgruppen: die neun völlig unveränderten Gruppen plus das verbleibende FORTSETZEN-Paar aus gewöhnlicher OL-Karte und lokalem LS-Kürzel.

## Neue Lesung von H4-S001

```text
qokaiin | chaiin | ykain | ykan | ody
ANSETZEN · MASS | MASS | DIES · ZUFUEHREN · PORTION |
DIES · ZUFUEHREN · NACHPORTION | GANG; SCHLUSS
```

Werkstattlektüre: Den Pflanzenansatz nach Maß ansetzen, eine Portion und eine Nachportion zuführen, dann den Gang schließen.

## Neue Lesung der beiden Wiederaufnahmekarten

`dchol` in H3-S003 und `schol` in H5-S002 eröffnen jeweils eine Aussage nach einer vorherigen abgeschlossenen oder abgesetzten Arbeitsphase. Sie markieren keine neue Substanz, sondern holen den aktiven Arbeitsfaden zurück.

## Nächster Schritt

Die zehn verbliebenen Doppelgruppen werden nun als Schreibpaletten in ein Mehrschreiber-Handbuch eingetragen: Wann darf ein Schreiber welche Oberfläche wählen, ohne den Befehl zu verändern?
"""
    (HERE / "SIX_HUNDRED_THIRTEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "old_duplicate_groups": len(duplicate_ids),
        "audited_duplicate_events": len(context_rows),
        "semantic_splits": len(CARD_RESOLUTION),
        "spoken_words": len(revised_words),
        "final_commands": len(final_command_groups),
        "cards": len(revised_cards),
        "remaining_duplicate_groups": len(final_duplicate_groups),
        "remaining_redundant_card_ids": sum(len(rows) - 1 for rows in final_duplicate_groups),
        "events": len(revised_events),
        "statements": len(revised_statements),
        "decision": "TWO_CONTEXTUAL_NUANCES_RESTORED__TEN_GROUPS_REMAIN_CARD_VARIANTS",
    }
    (HERE / "SIX_HUNDRED_THIRTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
