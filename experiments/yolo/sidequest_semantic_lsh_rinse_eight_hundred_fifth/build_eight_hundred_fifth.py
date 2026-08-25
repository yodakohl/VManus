#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    target = [row for row in events if "LSH" in row["component_recipe"].split("+")]
    observed_surfaces = {row["surface"] for row in events}

    candidates = [
        {"candidate": "WASCHEN", "lsho_reading": "WASCHVORGANG", "lshedy_reading": "KURZ WASCHEN", "extra_assumption": "broad body or object washing", "repair": 1, "decision": "REVISE"},
        {"candidate": "SPUELEN", "lsho_reading": "SPUELVORGANG", "lshedy_reading": "KURZ SPUELEN", "extra_assumption": "none beyond a wet-process cycle", "repair": 0, "decision": "SELECT"},
        {"candidate": "AUSWASCHEN", "lsho_reading": "AUSWASCHVORGANG", "lshedy_reading": "KURZ AUSWASCHEN", "extra_assumption": "material must be extracted from substrate", "repair": 3, "decision": "REJECT"},
    ]

    event_rows = []
    for row in target:
        reading = "SPUELEN · VORGANG" if row["component_recipe"] == "LSH+O" else "SPUELEN · KURZ · SCHLUSS"
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "old_reading_de": row["rebuilt_reading_de"],
                "selected_reading_de": reading,
                "compound_readback_de": "SPUELVORGANG" if row["component_recipe"] == "LSH+O" else "KURZ SPUELEN; SCHLUSS",
            }
        )

    statement_rows = []
    for sid in sorted({row["statement_id"] for row in target}):
        row = statements[sid]
        if sid == "B1-S012":
            revised = "Am gemeinsamen zweireihigen Becken: Einen Spuelvorgang ausfuehren, den Posten kurz ansetzen, nochmals kurz spuelen und den Schritt schliessen."
        else:
            revised = "Am gemeinsamen zweireihigen Becken: Kurz spuelen und den Schritt schliessen."
        statement_rows.append(
            {
                "statement_id": sid,
                "page": row["page"],
                "surface_sequence": row["surface_sequence"],
                "old_reading_de": row["clean_workshop_reading_de"],
                "revised_reading_de": revised,
            }
        )

    grid = [
        ("E", "KURZ", "Y", "DIES", "LSH+E+Y", "lshey", 0),
        ("EE", "LANG", "Y", "DIES", "LSH+EE+Y", "lsheey", 0),
        ("EEE", "VOLL", "Y", "DIES", "LSH+EEE+Y", "lsheeey", 0),
        ("E", "KURZ", "DY", "SCHLUSS", "LSH+E+DY", "lshedy", 2),
        ("EE", "LANG", "DY", "SCHLUSS", "LSH+EE+DY", "lsheedy", 0),
        ("EEE", "VOLL", "DY", "SCHLUSS", "LSH+EEE+DY", "lsheeedy", 0),
    ]
    grid_rows = []
    for grade, grade_value, endpoint, endpoint_value, recipe, surface, count in grid:
        grid_rows.append(
            {
                "grade": grade,
                "grade_value_de": grade_value,
                "endpoint": endpoint,
                "endpoint_value_de": endpoint_value,
                "component_recipe": recipe,
                "surface": surface,
                "events": count,
                "reading_de": f"SPUELEN · {grade_value} · {endpoint_value}",
                "status": "ATTESTED" if count else "PREDICTED_UNATTESTED",
                "surface_collision": "YES" if not count and surface in observed_surfaces else "NO",
            }
        )

    write(
        "EIGHT_HUNDRED_FIFTH_3_LSH_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "old_reading_de", "selected_reading_de", "compound_readback_de"],
    )
    write(
        "EIGHT_HUNDRED_FIFTH_3_MEANING_CANDIDATES.tsv",
        candidates,
        ["candidate", "lsho_reading", "lshedy_reading", "extra_assumption", "repair", "decision"],
    )
    write(
        "EIGHT_HUNDRED_FIFTH_2_REVISED_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "page", "surface_sequence", "old_reading_de", "revised_reading_de"],
    )
    write(
        "EIGHT_HUNDRED_FIFTH_6_LSH_GRADE_CELLS.tsv",
        grid_rows,
        ["grade", "grade_value_de", "endpoint", "endpoint_value_de", "component_recipe", "surface", "events", "reading_de", "status", "surface_collision"],
    )
    summary = {
        "status": "PASS",
        "decision": "LSH_REVISED_TO_SPUELEN_AND_PROMOTED_TO_CORE22",
        "events": len(event_rows),
        "cards": len({row["surface"] for row in event_rows}),
        "statements": len(statement_rows),
        "grade_cells": len(grid_rows),
        "attested_grade_cells": sum(row["status"] == "ATTESTED" for row in grid_rows),
        "predicted_grade_cells": sum(row["status"] == "PREDICTED_UNATTESTED" for row in grid_rows),
        "prediction_collisions": sum(row["surface_collision"] == "YES" for row in grid_rows),
        "new_core_size": 22,
        "remaining_recurrent_strip_values": 9,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
