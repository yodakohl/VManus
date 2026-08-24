#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_combined_prose_manual_four_hundred_fifty_sixth/FOUR_HUNDRED_FIFTY_SIXTH_381_EVENT_COMBINED_EDITION.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_combined_prose_manual_four_hundred_fifty_sixth/FOUR_HUNDRED_FIFTY_SIXTH_173_CARD_COMBINED_DICTIONARY.tsv"

REVISIONS = {
    "4d4559019a961b834aa1": ("AR", "von dort", "PROMOTE_COMPONENT", "all surfaces are wrappers around PAGE_HOST AR; same/source is anaphoric AR"),
    "53cd0637c6820ba5e91f": ("AIN", "Portion", "PROMOTE_COMPONENT", "both DAIN occurrences are wrapper-d realizations of PAGE_HOST AIN"),
    "8c97dfde96fbc78e3355": ("L+OL", "weiterfuehren", "PROMOTE_COMPONENT", "L plus continue is sufficient; invisible warmth removed"),
    "43eb9aa12959b4d5cdc9": ("E+K+E+Y", "dies kurz zuführen", "PROMOTE_COMPONENT", "visible grade-supply-current sequence; invisible raw state removed"),
}

TOURNAMENT = {
    "4d4559019a961b834aa1": ("von dort", "dasselbe", "aus derselben Charge"),
    "df1098831679a8ad1b39": ("Gefäß", "Arbeitszustand", "Behälterstelle"),
    "bdad9f9ea8b80f141496": ("auswringen", "dies abziehen", "pressen"),
    "b5df9126607030b95175": ("Klarauszug", "länger halten", "Ablauf"),
    "e026af581c99322fbd46": ("verwahren", "an der Stelle fuellen", "zurückstellen"),
    "db729b598e89e11452e0": ("teilen", "kurz abziehen", "Trennstelle"),
    "53cd0637c6820ba5e91f": ("Portion", "Tuch", "abgeteilte Einheit"),
    "8c97dfde96fbc78e3355": ("weiterfuehren", "warm", "noch einmal fortsetzen"),
    "fcc1deda9e24ec268eb0": ("zweite Stufe", "Sollstufe", "zweites Maß"),
    "43eb9aa12959b4d5cdc9": ("dies kurz zuführen", "roh", "dies länger zuführen"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_events = read(EVENTS)
    source_cards = read(CARDS)
    whole_cards = [row for row in source_cards if row["lexicon_class"] == "MEMORIZED_WHOLE_CARD"]
    if {row["joint_tuple_id"] for row in whole_cards} != set(TOURNAMENT):
        raise ValueError("whole inventory changed")

    decision_rows = []
    for row in whole_cards:
        joint_id = row["joint_tuple_id"]
        selected, rival1, rival2 = TOURNAMENT[joint_id]
        if joint_id in REVISIONS:
            parse, value, action, reason = REVISIONS[joint_id]
        else:
            parse, value, action, reason = row["component_parse"], row["small_value_de"], "KEEP_WHOLE", "candidate composition leaves an unexplained sign or breaks the contexts"
        decision_rows.append({
            "joint_tuple_id": joint_id, "surfaces": row["surfaces"], "events": row["events"], "event_ids": row["event_ids"],
            "old_parse": row["component_parse"], "old_value_de": row["small_value_de"],
            "candidate_1": selected, "candidate_2": rival1, "candidate_3": rival2,
            "selected_parse": parse, "selected_value_de": value, "decision": action, "reason": reason,
        })
    write("FOUR_HUNDRED_FIFTY_EIGHTH_TEN_WHOLE_CARD_TOURNAMENT.tsv", decision_rows)

    cards = []
    for row in source_cards:
        out = dict(row)
        if row["joint_tuple_id"] in REVISIONS:
            parse, value, _, reason = REVISIONS[row["joint_tuple_id"]]
            out.update({"component_parse": parse, "small_value_de": value, "lexicon_class": "PRODUCTIVE_COMPOSITION", "rule_source": "PASS458_WHOLE_REDUCTION", "pass458_note": reason})
        else:
            out["pass458_note"] = "unchanged"
        cards.append(out)
    write("FOUR_HUNDRED_FIFTY_EIGHTH_173_CARD_REVISED_DICTIONARY.tsv", cards)
    card_by_id = {row["joint_tuple_id"]: row for row in cards}

    events = []
    occurrence_audit = []
    for row in source_events:
        out = dict(row)
        card = card_by_id[row["joint_tuple_id"]]
        if row["joint_tuple_id"] in TOURNAMENT:
            occurrence_audit.append({
                "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "locus": row["locus"],
                "statement_id": row["statement_id"], "surface": row["surface"], "joint_tuple_id": row["joint_tuple_id"],
                "previous_value_de": row["small_value_de"], "selected_value_de": card["small_value_de"],
                "selected_parse": card["component_parse"], "decision": "PROMOTE_COMPONENT" if row["joint_tuple_id"] in REVISIONS else "KEEP_WHOLE",
            })
        out.update({"component_parse": card["component_parse"], "small_value_de": card["small_value_de"], "lexicon_class": card["lexicon_class"]})
        events.append(out)
    write("FOUR_HUNDRED_FIFTY_EIGHTH_381_EVENT_REVISED_EDITION.tsv", events)
    write("FOUR_HUNDRED_FIFTY_EIGHTH_18_WHOLE_OCCURRENCE_AUDIT.tsv", occurrence_audit)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        statements.append({
            "statement_id": statement_id, "register": rows[0]["register"], "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "owner_zones": "|".join(dict.fromkeys(row["owner_zone"] for row in rows)),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "component_chain": " > ".join(row["component_parse"] for row in rows),
            "literal_reading_de": "; ".join(row["small_value_de"] for row in rows) + ".",
        })
    write("FOUR_HUNDRED_FIFTY_EIGHTH_116_STATEMENT_REVISED_EDITION.tsv", statements)

    by_value: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        by_value[row["small_value_de"]].append(row)
    aliases = []
    for value, rows in sorted(by_value.items()):
        if len(rows) < 2:
            continue
        aliases.append({
            "small_value_de": value, "cards": len(rows), "joint_tuple_ids": "|".join(row["joint_tuple_id"] for row in rows),
            "surfaces": " || ".join(row["surfaces"] for row in rows),
            "events": sum(int(row["events"]) for row in rows),
        })
    write("FOUR_HUNDRED_FIFTY_EIGHTH_ELEVEN_ALIAS_FAMILIES.tsv", aliases)

    remaining_wholes = [row for row in cards if row["lexicon_class"] == "MEMORIZED_WHOLE_CARD"]
    write("FOUR_HUNDRED_FIFTY_EIGHTH_SIX_REMAINING_WHOLE_CARDS.tsv", remaining_wholes)
    summary = {
        "status": "PASS", "cards": len(cards), "events": len(events), "statements": len(statements),
        "promoted_whole_cards": len(REVISIONS), "promoted_events": sum(int(row["events"]) for row in decision_rows if row["decision"] == "PROMOTE_COMPONENT"),
        "productive_cards": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in cards),
        "productive_events": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in events),
        "remaining_whole_cards": len(remaining_wholes),
        "remaining_whole_events": sum(row["lexicon_class"] == "MEMORIZED_WHOLE_CARD" for row in events),
        "alias_families_after_revision": len(aliases),
    }
    (HERE / "FOUR_HUNDRED_FIFTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
