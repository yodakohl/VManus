#!/usr/bin/env python3
"""Build Pass 722: rank current component and recipe glosses by compositional awkwardness."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P721 = ROOT / "experiments/yolo/sidequest_semantic_compact_apprentice_release_seven_hundred_twenty_first"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CANDIDATES = {
    "T": (6, "ANWENDEN", "EINTRAGEN ist in T+Y und Gradreihen zu buchhalterisch; ANWENDEN ergibt kurze Werkstattsaetze."),
    "CH": (5, "ENTNEHMEN", "ABNEHMEN schwankt zwischen Wegnehmen und Entfernen; ENTNEHMEN verbindet Quelle, Wasser und Teil."),
    "K": (5, "ZUGEBEN", "ZUDOSIEREN ist modern und sperrig; ZUGEBEN passt Portion, Mass, Zutat und Wasser."),
    "O": (4, "ARBEITSGANG", "GANG ist zu leer; ARBEITSGANG ist als Nomen in den O-Kompositionen klarer."),
    "AIR": (4, "WASSER", "LAUF benennt nur Form; die fuenf Karten lassen sich konkreter als Wasser lesen."),
    "CTH": (3, "BEREITEN", "BEREIT wechselt zwischen Zustand und Verb; BEREITEN macht CTH+Y handlungsfaehig."),
    "S": (3, "TEIL", "TEILEN ist in CH+E+S ein zweites Verb; TEIL ergibt ENTNEHMEN-KURZ-TEIL."),
}
SELECTED = {"T", "CH", "K"}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(P721 / "SEVEN_HUNDRED_TWENTY_FIRST_39_COMPONENT_SHEET.tsv")
    families = read(P721 / "SEVEN_HUNDRED_TWENTY_FIRST_163_RECIPE_INDEX.tsv")

    component_rows = []
    for component in components:
        token = component["component"]
        containing = [row for row in families if token in row["component_recipe"].split("+")]
        family_count = len(containing)
        family_events = sum(int(row["events"]) for row in containing)
        if token in CANDIDATES:
            severity, candidate, reason = CANDIDATES[token]
            status = "REVISE_NOW" if token in SELECTED else "NEXT_QUEUE"
        else:
            severity, candidate, reason, status = 0, component["short_value_de"], "Aktueller Kurzwert komponiert ausreichend klar.", "KEEP"
        pressure = severity * 10 + family_count + min(family_events, 20)
        component_rows.append({
            "component": token, "current_value_de": component["short_value_de"],
            "candidate_value_de": candidate, "families": family_count, "family_events": family_events,
            "severity": severity, "pressure_score": pressure, "decision": status,
            "composition_reason_de": reason,
        })
    component_rows.sort(key=lambda row: (-int(row["pressure_score"]), row["component"]))
    for rank, row in enumerate(component_rows, 1):
        row["pressure_rank"] = rank
    component_rows = [{"pressure_rank": row.pop("pressure_rank"), **row} for row in component_rows]

    pressure_by_component = {row["component"]: int(row["severity"]) for row in component_rows}
    family_rows = []
    for family in families:
        parts = family["component_recipe"].split("+")
        weak = [part for part in parts if pressure_by_component.get(part, 0)]
        score = sum(pressure_by_component.get(part, 0) for part in parts) + max(0, len(parts) - 4) + min(3, int(family["events"]) // 5)
        selected_parts = [part for part in parts if part in SELECTED]
        family_rows.append({
            "semantic_family": family["semantic_family"], "component_recipe": family["component_recipe"],
            "current_reading_de": family["working_reading_de"], "events": family["events"],
            "weak_components": "|".join(weak) if weak else "NONE",
            "awkwardness_score": score,
            "revision_wave": "NOW_T_CH_K" if selected_parts else "QUEUE" if weak else "KEEP",
            "selected_components": "|".join(selected_parts) if selected_parts else "NONE",
        })
    family_rows.sort(key=lambda row: (-int(row["awkwardness_score"]), -int(row["events"]), row["semantic_family"]))
    for rank, row in enumerate(family_rows, 1):
        row["awkwardness_rank"] = rank
    family_rows = [{"awkwardness_rank": row.pop("awkwardness_rank"), **row} for row in family_rows]

    write("SEVEN_HUNDRED_TWENTY_SECOND_39_COMPONENT_PRESSURE.tsv", component_rows)
    write("SEVEN_HUNDRED_TWENTY_SECOND_163_RECIPE_PRESSURE.tsv", family_rows)
    selected_families = [row for row in family_rows if row["revision_wave"] == "NOW_T_CH_K"]
    summary = {
        "status": "PASS", "components": len(component_rows), "semantic_families": len(family_rows),
        "candidate_components": len(CANDIDATES), "revise_now_components": sorted(SELECTED),
        "revise_now_families": len(selected_families),
        "revise_now_family_events": sum(int(row["events"]) for row in selected_families),
        "next_queue": ["O", "AIR", "CTH", "S"],
        "form_changes": 0,
        "decision": "REVISE_T_CH_K_FIRST__QUEUE_O_AIR_CTH_S__KEEP_FORM_MACHINE_FIXED",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
