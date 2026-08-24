#!/usr/bin/env python3
"""Build Pass 706: one continuous seven-statement apprentice commission."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P704 = ROOT / "experiments/yolo/sidequest_semantic_statement_phrasebook_seven_hundred_fourth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


STATEMENTS = [
    ("C01", "PLANT_OWNER", "PROC009|PROC008", "Vorgeschriebenes Mass; diesen Teil der abgebildeten Pflanze ansetzen."),
    ("C02", "PLANT_OWNER", "PROC056|PROC016", "Diese Pflanzenzutat nehmen; daraus den Ansatz bereithalten."),
    ("C03", "PLANT_OWNER", "PROC084|PROC031", "Waschgang; diesen Pflanzenteil laenger darin halten."),
    ("C04", "PLANT_OWNER", "PROC028|PROC078", "Diesen Teil auswringen; absetzen lassen und den ersten Arbeitsschritt schliessen."),
    ("C05", "BASIN_STATION", "PROC009|PROC048", "Vorgeschriebenes Mass; den Ansatz an der bezeichneten Beckenstelle ansetzen."),
    ("C06", "BASIN_STATION", "PROC147|PROC150", "Nach vorgeschriebenem Mass weiterleiten; den Lauf in die naechste Station umsetzen."),
    ("C07", "BASIN_STATION", "PROC083|PROC041", "Diesen Stationsposten kurz waermen; den Arbeitsgang schliessen."),
]

OWNER = {
    "PLANT_OWNER": "abgebildete breitblaettrige Pflanze und ihr entnommener Teil",
    "BASIN_STATION": "lokale Becken-/Leitungsstation, die den vorbereiteten Ansatz uebernimmt",
}


def role(card: dict[str, str]) -> str:
    if card["card_class"] == "MEMORIZED_WHOLE_COMMAND":
        return "WHOLE_COMMAND"
    final = card["component_recipe"].split("+")[-1]
    return {
        "DY": "CLOSE_STEP", "Y": "CURRENT_ITEM", "AIN": "QUANTITY_STAGE",
        "AIIN": "QUANTITY_STAGE", "IIN": "QUANTITY_STAGE", "AN": "QUANTITY_STAGE",
        "DA": "QUANTITY_STAGE", "AL": "TARGET", "AR": "SOURCE", "AIR": "FLOW",
        "OR": "PREPARATION", "OL": "CONTINUE", "S": "BOUND_RESULT",
    }.get(final, "OPEN_ACTION")


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    role_pairs = read(P704 / "SEVEN_HUNDRED_FOURTH_55_ROLE_BIGRAMS.tsv")
    card_by_no = {row["card_no"]: row for row in cards}
    role_support = {(row["left_role"], row["right_role"]): int(row["token_count"]) for row in role_pairs}

    surface_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for event in events:
        surface_counts[event["card_no"]][event["observed_surface"]] += 1

    statement_rows = []
    trace_rows = []
    all_surfaces = []
    global_index = 0
    for statement_no, owner_id, card_sequence, fluent in STATEMENTS:
        selected = [card_by_no[number] for number in card_sequence.split("|")]
        roles = [role(card) for card in selected]
        surfaces = [surface_counts[card["card_no"]].most_common(1)[0][0] for card in selected]
        statement_rows.append({
            "statement_no": statement_no, "owner_id": owner_id, "silent_owner_de": OWNER[owner_id],
            "card_sequence": card_sequence, "role_template": ">".join(roles),
            "role_template_support": role_support[(roles[0], roles[1])],
            "component_sequence": " | ".join(card["component_recipe"] for card in selected),
            "practice_surface_sequence": " ".join(surfaces),
            "literal_backreading_de": " ; ".join(card["compact_atomic_reading_de"] for card in selected),
            "fluent_owner_filled_reading_de": fluent,
            "ends_work_step": "YES" if roles[-1] == "CLOSE_STEP" else "NO",
        })
        for local_index, (card, surface) in enumerate(zip(selected, surfaces), 1):
            global_index += 1
            all_surfaces.append(surface)
            trace_rows.append({
                "commission_event": f"CE{global_index:02d}", "statement_no": statement_no,
                "statement_card_position": local_index, "owner_id": owner_id,
                "silent_owner_de": OWNER[owner_id], "card_no": card["card_no"],
                "component_recipe": card["component_recipe"], "role": role(card),
                "selected_existing_surface": surface, "all_existing_surface_options": card["surfaces"],
                "atomic_backreading_de": card["compact_atomic_reading_de"],
                "new_card": "NO", "new_surface": "NO",
            })

    line_slices = [(1, 1, 5), (2, 6, 11), (3, 12, 14)]
    line_rows = []
    for line_no, first, last in line_slices:
        statement_ids = []
        for row in trace_rows[first - 1:last]:
            if row["statement_no"] not in statement_ids:
                statement_ids.append(row["statement_no"])
        line_rows.append({
            "physical_line": f"L{line_no}", "first_event": f"CE{first:02d}", "last_event": f"CE{last:02d}",
            "surface_line": " ".join(all_surfaces[first - 1:last]),
            "statements_touched": "|".join(statement_ids),
            "line_boundary_rule": "PHYSICAL_WRAP_ONLY__NOT_SENTENCE_BOUNDARY",
        })

    owner_rows = [
        {"owner_id": "PLANT_OWNER", "active_events": "CE01-CE08", "owner_de": OWNER["PLANT_OWNER"], "entry_rule_de": "Bild setzt den Pflanzenbesitzer vor CE01."},
        {"owner_id": "BASIN_STATION", "active_events": "CE09-CE14", "owner_de": OWNER["BASIN_STATION"], "entry_rule_de": "Expliziter Werkstatthandoff nach C04; Beckenstation uebernimmt denselben Ansatz."},
    ]

    write("SEVEN_HUNDRED_SIXTH_7_STATEMENT_COMMISSION.tsv", statement_rows)
    write("SEVEN_HUNDRED_SIXTH_14_CARD_FORWARD_BACKWARD_TRACE.tsv", trace_rows)
    write("SEVEN_HUNDRED_SIXTH_3_PHYSICAL_LINES.tsv", line_rows)
    write("SEVEN_HUNDRED_SIXTH_2_OWNER_STATES.tsv", owner_rows)

    readable = [
        "# Zusammenhaengender Werkstattauftrag", "",
        "## Sichtbare Praxisabschrift", "",
        *[f"{row['physical_line']}: `{row['surface_line']}`" for row in line_rows], "",
        "Die Zeilen sind nur Platzumbruch. C03 laeuft von L1 nach L2; C06 von L2 nach L3.", "",
        "## Kontinuierliche Ruecklesung", "",
    ]
    for row in statement_rows:
        readable.extend([f"{row['statement_no']} ({row['owner_id']}): {row['fluent_owner_filled_reading_de']}", ""])
    readable.extend([
        "Handoff: Nach C04 wechselt nur der sichtbare Besitzer. Der in C01-C04 bereitete Ansatz wird an die Becken-/Leitungsstation uebergeben.", "",
        "Fluessig gelesen: Nimm von der gezeichneten Pflanze das vorgeschriebene Mass und setze den Teil an. Nimm die Zutat in den Ansatz, fuehre den Waschgang aus, halte sie laenger darin, wringe sie aus und lass sie absetzen. Uebergib den bereiteten Ansatz an die bezeichnete Beckenstelle, leite ihn nach Mass in die naechste Station, waerme ihn kurz und schliesse den Gang.",
    ])
    (HERE / "SEVEN_HUNDRED_SIXTH_CONTINUOUS_COMMISSION.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "statements": len(statement_rows), "cards": len(trace_rows),
        "physical_lines": len(line_rows), "owner_states": len(owner_rows),
        "cross_line_statements": 2, "owner_handoffs": 1,
        "attested_role_templates": sum(int(row["role_template_support"]) >= 1 for row in statement_rows),
        "work_step_closures": sum(row["ends_work_step"] == "YES" for row in statement_rows),
        "new_cards": 0, "new_surfaces": 0,
        "decision": "ONE_CONTINUOUS_OWNER_AWARE_COMMISSION_RUNS_FROM_PICTURED_MATERIAL_TO_LOCAL_STATION_AND_CLOSE",
    }
    (HERE / "SEVEN_HUNDRED_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
