#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P468 = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth"
P476 = ROOT / "experiments/yolo/sidequest_semantic_workflow_phases_four_hundred_seventy_sixth"
P477 = ROOT / "experiments/yolo/sidequest_semantic_sentence_templates_four_hundred_seventy_seventh"
P475 = ROOT / "experiments/yolo/sidequest_semantic_readable_compression_four_hundred_seventy_fifth"

WHOLE = {
    "df1098831679a8ad1b39": ("ARBEITSFACH", "REVISE", "single slot between MOVE and COLLECT; use the shared OS=FACH value rather than guessed vessel"),
    "bdad9f9ea8b80f141496": ("AUSWRINGEN", "RETAIN", "single learned PREPARE operation"),
    "b5df9126607030b95175": ("ERGEBNISPOSTEN", "REVISE", "four COLLECT slots across Herbal and Bio; broader and shorter than clear extract"),
    "e026af581c99322fbd46": ("VERWAHREN", "RETAIN", "single statement-final storage operation"),
    "db729b598e89e11452e0": ("TEILEN", "RETAIN", "single PREPARE slot between MOVE and MEASURE"),
    "fcc1deda9e24ec268eb0": ("STUFE II", "RETAIN", "single MEASURE slot between PREPARE and MOVE"),
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
    dictionary = read(P468 / "FOUR_HUNDRED_SIXTY_EIGHTH_173_CARD_COMMON_ACTION_DICTIONARY.tsv")
    events = read(P476 / "FOUR_HUNDRED_SEVENTY_SIXTH_381_EVENT_PHASES.tsv")
    occurrences = read(P477 / "FOUR_HUNDRED_SEVENTY_SEVENTH_MOTIF_OCCURRENCES.tsv")
    templates = read(P477 / "FOUR_HUNDRED_SEVENTY_SEVENTH_NINE_SENTENCE_TEMPLATES.tsv")
    astro = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_142_READABLE_ASTRO_LOCI.tsv")
    covered = {event for row in occurrences if row["selected_in_greedy_edition"] == "YES" for event in row["event_ids"].split("|")}
    remaining = [row for row in events if row["event_id"] not in covered]

    event_index = {row["event_id"]: i for i, row in enumerate(events)}
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in remaining:
        by_card[row["joint_tuple_id"]].append(row)
    profiles = []
    for card_id, rows in sorted(by_card.items(), key=lambda item: (-len(item[1]), item[0])):
        signatures = []
        for row in rows:
            i = event_index[row["event_id"]]
            prev = events[i-1]["action_phase"] if i and events[i-1]["statement_id"] == row["statement_id"] else "START"
            nxt = events[i+1]["action_phase"] if i + 1 < len(events) and events[i+1]["statement_id"] == row["statement_id"] else "END"
            signatures.append(f"{prev}>{row['action_phase']}>{nxt}")
        top_signature, top_n = Counter(signatures).most_common(1)[0]
        phases = Counter(row["action_phase"] for row in rows)
        profiles.append({
            "joint_tuple_id": card_id,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_parse": rows[0]["component_parse"],
            "lexicon_class": rows[0]["lexicon_class"],
            "remaining_events": len(rows),
            "statements": len({row["statement_id"] for row in rows}),
            "records": len({row["record_unit_id"] for row in rows}),
            "registers": "|".join(sorted({row["register"] for row in rows})),
            "phase_counts": "|".join(f"{phase}:{n}" for phase, n in sorted(phases.items())),
            "top_slot_signature": top_signature,
            "top_slot_events": top_n,
            "top_slot_fraction": f"{top_n/len(rows):.3f}",
            "slot_stable": "YES" if len(phases) == 1 and len(rows) >= 2 and top_n / len(rows) >= 0.5 else "NO",
            "current_value_de": rows[0]["compressed_event_de"],
        })
    write("FOUR_HUNDRED_SEVENTY_EIGHTH_130_REMAINDER_CARD_SLOT_PROFILES.tsv", profiles)

    whole_rows = []
    for card in dictionary:
        card_id = card["joint_tuple_id"]
        if card_id not in WHOLE:
            continue
        value, decision, reason = WHOLE[card_id]
        rows = [row for row in events if row["joint_tuple_id"] == card_id]
        profiles_for_card = [row for row in profiles if row["joint_tuple_id"] == card_id]
        whole_rows.append({
            "card_no": card["card_no"],
            "joint_tuple_id": card_id,
            "surfaces": card["surfaces"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "records": "|".join(sorted({row["record_unit_id"] for row in rows})),
            "registers": "|".join(sorted({row["register"] for row in rows})),
            "action_phases": "|".join(sorted({row["action_phase"] for row in rows})),
            "remainder_top_slot": profiles_for_card[0]["top_slot_signature"] if profiles_for_card else "TEMPLATE_COVERED",
            "old_wet_value_de": card["wet_context_value_de"],
            "selected_short_value_de": value,
            "decision": decision,
            "slot_reason": reason,
        })
    write("FOUR_HUNDRED_SEVENTY_EIGHTH_SIX_WHOLE_CARD_SLOT_DECISIONS.tsv", whole_rows)

    revised_dictionary = []
    for row in dictionary:
        out = dict(row)
        if row["joint_tuple_id"] in WHOLE:
            value, decision, reason = WHOLE[row["joint_tuple_id"]]
            out["template_slot_value_de"] = value
            out["pass478_decision"] = decision
            out["pass478_reason"] = reason
        else:
            out["template_slot_value_de"] = row["wet_context_value_de"]
            out["pass478_decision"] = "UNCHANGED_COMPOSITION"
            out["pass478_reason"] = "already built from productive components"
        revised_dictionary.append(out)
    write("FOUR_HUNDRED_SEVENTY_EIGHTH_173_SLOT_REVISED_DICTIONARY.tsv", revised_dictionary)

    revised_events = []
    for row in events:
        out = dict(row)
        if row["joint_tuple_id"] in WHOLE:
            old = row["compressed_event_de"]
            new = WHOLE[row["joint_tuple_id"]][0]
            out["pass478_old_event_de"] = old
            out["pass478_event_de"] = old.replace("Klarauszug", new).replace("Gefäß", new) if WHOLE[row["joint_tuple_id"]][1] == "REVISE" else old
            out["pass478_revision"] = WHOLE[row["joint_tuple_id"]][1]
        else:
            out["pass478_old_event_de"] = row["compressed_event_de"]
            out["pass478_event_de"] = row["compressed_event_de"]
            out["pass478_revision"] = "NO"
        revised_events.append(out)
    write("FOUR_HUNDRED_SEVENTY_EIGHTH_381_SLOT_REVISED_EVENTS.tsv", revised_events)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    statement_order = list(dict.fromkeys(row["statement_id"] for row in revised_events))
    for sid in statement_order:
        rows = by_statement[sid]
        statement_rows.append({
            "statement_id": sid,
            "register": rows[0]["register"],
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "whole_cards": "|".join(row["joint_tuple_id"] for row in rows if row["joint_tuple_id"] in WHOLE) or "NONE",
            "revised_whole_cards": sum(row["pass478_revision"] == "REVISE" for row in rows),
            "slot_revised_statement_de": "; ".join(row["pass478_event_de"] for row in rows) + ".",
        })
    write("FOUR_HUNDRED_SEVENTY_EIGHTH_116_SLOT_REVISED_STATEMENTS.tsv", statement_rows)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "continuous_slot_revised_de": " ".join(row["slot_revised_statement_de"] for row in rows),
        })
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": "ASTRO",
            "statements_or_loci": len(rows),
            "groups": sum(int(row["groups"]) for row in rows),
            "continuous_slot_revised_de": " ".join(row["readable_locus_de"] for row in rows),
        })
    write("FOUR_HUNDRED_SEVENTY_EIGHTH_14_SLOT_REVISED_UNIT_EDITIONS.tsv", units)

    md = ["# Slot-revised ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_slot_revised_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_EIGHTH_SLOT_REVISED_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "template_covered_events": len(covered),
        "remainder_events": len(remaining),
        "remainder_card_types": len(profiles),
        "slot_stable_remainder_card_types": sum(row["slot_stable"] == "YES" for row in profiles),
        "whole_card_types": len(whole_rows),
        "whole_card_events": sum(int(row["events"]) for row in whole_rows),
        "whole_values_revised": sum(row["decision"] == "REVISE" for row in whole_rows),
        "events_revised": sum(row["pass478_revision"] == "REVISE" for row in revised_events),
        "statements_revised": sum(int(row["revised_whole_cards"]) > 0 for row in statement_rows),
        "dictionary_cards": len(revised_dictionary),
        "prose_events": len(revised_events),
        "statements": len(statement_rows),
        "units": len(units),
        "groups": sum(int(row["groups"]) for row in units),
        "templates_carried": len(templates),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
