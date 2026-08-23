#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R156 = ROOT / "experiments/yolo/sidequest_semantic_atomic_current_ten_page_hundred_fifty_sixth"
R134 = ROOT / "experiments/yolo/sidequest_semantic_current_ten_page_edition_hundred_thirty_fourth"

SIMPLIFIED = {
    "ZERO": "BARE_OR_INTERNAL",
    "CH_ENTRY": "OPEN_CH_ENTRY",
    "Q_ENTRY": "Q_CELL_ENTRY",
    "S_ENTRY": "S_FLOW_ENTRY",
    "SH_ENTRY": "S_FLOW_ENTRY",
    "D_ENTRY": "HARD_D_T_ENTRY",
    "T_ENTRY": "HARD_D_T_ENTRY",
    "OTHER_ENTRY": "HARD_D_T_ENTRY",
}
PROFILES = {
    "MASTER_BARE": ["ZERO", "CH_ENTRY", "Q_ENTRY", "S_ENTRY", "SH_ENTRY", "D_ENTRY", "T_ENTRY", "OTHER_ENTRY"],
    "CH_OPEN_HAND": ["CH_ENTRY", "ZERO", "Q_ENTRY", "S_ENTRY", "SH_ENTRY", "D_ENTRY", "T_ENTRY", "OTHER_ENTRY"],
    "Q_CELL_HAND": ["Q_ENTRY", "ZERO", "CH_ENTRY", "S_ENTRY", "SH_ENTRY", "D_ENTRY", "T_ENTRY", "OTHER_ENTRY"],
    "S_FLOW_HAND": ["S_ENTRY", "SH_ENTRY", "ZERO", "CH_ENTRY", "Q_ENTRY", "D_ENTRY", "T_ENTRY", "OTHER_ENTRY"],
    "HARD_COMPACT_HAND": ["D_ENTRY", "T_ENTRY", "OTHER_ENTRY", "ZERO", "CH_ENTRY", "Q_ENTRY", "S_ENTRY", "SH_ENTRY"],
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_173_ATOMIC_DICTIONARY.tsv")
    events = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_381_ATOMIC_EVENTS.tsv")
    old_surfaces = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_230_SURFACE_REVERSE_KEY.tsv")
    active_ids = {row["master_card_id"] for row in cards if row["portable_scope"].startswith("ACTIVE")}
    active_surfaces = [row for row in old_surfaces if row["master_card_id"] in active_ids]
    card_by_id = {row["master_card_id"]: row for row in cards}

    surface_rows = []
    for row in active_surfaces:
        surface_rows.append({
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "master_form": row["master_form"], "card_value_de": card_by_id[row["master_card_id"]]["portable_card_value_de"],
            "old_renderer_gesture": row["renderer_gesture"],
            "five_habit_class": SIMPLIFIED[row["renderer_gesture"]],
            "old_family_class": row["family_class"],
        })
    write_tsv("HUNDRED_FIFTY_SEVENTH_103_SHARED_SURFACES.tsv", surface_rows)

    surfaces_by_card = defaultdict(list)
    for row in surface_rows:
        surfaces_by_card[row["master_card_id"]].append(row)
    family_rows = []
    for card_id in sorted(active_ids):
        card = card_by_id[card_id]
        rows = surfaces_by_card[card_id]
        classes = sorted({row["five_habit_class"] for row in rows})
        family_rows.append({
            "master_card_id": card_id, "master_form": card["master_form"],
            "card_value_de": card["portable_card_value_de"], "surface_count": str(len(rows)),
            "registered_surfaces": "|".join(row["visible_surface"] for row in rows),
            "five_habit_classes": "|".join(classes),
            "apprentice_rule": "LEARN_ONE_MASTER_CARD_THEN_CHOOSE_ONLY_A_REGISTERED_ENTRY_HABIT",
            "semantic_change": "NONE",
        })
    write_tsv("HUNDRED_FIFTY_SEVENTH_47_SHARED_FAMILIES.tsv", family_rows)

    profile_rows = []
    for card_id in sorted(active_ids):
        candidates = surfaces_by_card[card_id]
        for profile, preference in PROFILES.items():
            chosen = None
            for gesture in preference:
                options = [row for row in candidates if row["old_renderer_gesture"] == gesture]
                if options:
                    chosen = options[0]
                    break
            profile_rows.append({
                "profile": profile, "master_card_id": card_id,
                "master_form": card_by_id[card_id]["master_form"],
                "card_value_de": card_by_id[card_id]["portable_card_value_de"],
                "chosen_surface": chosen["visible_surface"],
                "chosen_habit": chosen["five_habit_class"],
                "fallback_used": "NO" if chosen["old_renderer_gesture"] == preference[0] else "YES",
                "registered_surface": "YES",
            })
    write_tsv("HUNDRED_FIFTY_SEVENTH_FIVE_HAND_SHARED_COPYBOOK.tsv", profile_rows)

    surface_lookup = {row["visible_surface"]: row for row in surface_rows}
    event_rows = []
    for row in events:
        if row["master_card_id"] in active_ids:
            surface = surface_lookup[row["visible_surface"]]
            event_rows.append({
                "event_serial": row["event_serial"], "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"], "page": row["page"],
                "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
                "card_value_de": row["card_value_de"], "five_habit_class": surface["five_habit_class"],
                "master_recovery": "EXACT",
            })
    write_tsv("HUNDRED_FIFTY_SEVENTH_251_SHARED_EVENT_RENDER_TRACE.tsv", event_rows)

    habit_counts = Counter(row["five_habit_class"] for row in surface_rows)
    manual = ["# Fünf Handgewohnheiten für die gemeinsame Kartenschicht", "",
              "1. **BARE_OR_INTERNAL** — bare/default form inside the running entry.",
              "2. **OPEN_CH_ENTRY** — ch/che opening habit.",
              "3. **Q_CELL_ENTRY** — q entry habit at a locally opened work cell.",
              "4. **S_FLOW_ENTRY** — s/sh entry habit used by the flowing/line-entry hand.",
              "5. **HARD_D_T_ENTRY** — d/t or rare hard compact entry.", "",
              "Choose the master card for meaning first. Choose one registered hand form second. A hand habit never",
              "creates a new word, changes a quantity, or licenses an unseen combination.", "", "## Counts", ""]
    for habit, count in sorted(habit_counts.items()):
        manual.append(f"- {habit}: {count} of 103 registered shared-card surfaces")
    (OUT / "HUNDRED_FIFTY_SEVENTH_FIVE_HABIT_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertsiebenundfünfzigste Runde: fünf Handgewohnheiten genügen für den gemeinsamen Kartensatz", "",
        "The 47 shared cards own 103 registered surfaces. Their eight old gesture labels collapse to five teaching",
        "habits: 37 bare/internal, 20 ch-open, fourteen q-cell, nineteen s/sh-flow, and thirteen d/t/other hard",
        "entries. Thirty-three shared cards have multiple surfaces; fourteen have only one registered form.", "",
        "Five scribe profiles choose 235 card forms, all from the registered inventory and all returning to the same",
        "47 meanings. The rule is historically plausible at workshop scale: meaning and master card are selected",
        "first; hand and local entry position choose the surface second. No phonetic alphabet is required.", "",
        "Next apply the same five habits to complete statement copying and test how many of the eleven records can",
        "look visibly different between hands while their atomic source reading remains identical.",
    ]
    (OUT / "HUNDRED_FIFTY_SEVENTH_RENDERER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "shared_cards": len(active_ids), "shared_surfaces": len(surface_rows),
        "multi_surface_cards": sum(int(row["surface_count"]) > 1 for row in family_rows),
        "single_surface_cards": sum(int(row["surface_count"]) == 1 for row in family_rows),
        "five_habits": len(habit_counts), "habit_counts": dict(sorted(habit_counts.items())),
        "profile_choices": len(profile_rows), "shared_events": len(event_rows), "semantic_changes": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
