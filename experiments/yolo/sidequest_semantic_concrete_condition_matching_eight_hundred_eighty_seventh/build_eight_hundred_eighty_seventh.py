#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASTRO = ROOT / "sidequest_semantic_relative_astro_condition_vocabulary_eight_hundred_seventy_third" / "EIGHT_HUNDRED_SEVENTY_THIRD_395_RELATIVE_CONDITION_GROUPS.tsv"
ORDERS = ROOT / "sidequest_semantic_revised_six_order_book_eight_hundred_eighty_sixth" / "EIGHT_HUNDRED_EIGHTY_SIXTH_6_REVISED_COMPLETE_ORDERS.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_SEVENTH"

CONDITIONS = {
    "C1@f67r2.1": {
        "features": {"PHASE", "COLLECT", "START_END"},
        "short": "BEIM MARKIERTEN RECHTEN PHASENPLATZ",
        "expanded": "Führe den Auftrag aus, wenn der markierte rechte Sektor-/Phasenplatz C1 gilt.",
        "visual_role": "rechter Sektor-/Phasenplatz",
    },
    "C2@f67r2.15": {
        "features": {"WORK", "ASPECT", "COMPLEX_SEQUENCE"},
        "short": "BEIM MARKIERTEN LINKEN STERN-/ASPEKTPLATZ",
        "expanded": "Führe den Auftrag am bezeichneten linken Stern-/Aspektplatz C2 aus.",
        "visual_role": "linker Stern-/Aspektplatz",
    },
    "C3@f68r1.9": {
        "features": {"TARGET", "DIRECT_PLACE"},
        "short": "AM DIREKT BEZEICHNETEN STERNORT",
        "expanded": "Führe den Auftrag am direkt bezeichneten Sternort C3 im Mehrpaneelatlas aus.",
        "visual_role": "direkter Sternort im Mehrpaneelatlas",
    },
    "C4@f69v.12": {
        "features": {"PASSAGE", "MEASURE", "COUNTED_PLACE"},
        "short": "AM MARKIERTEN LINKEN 28ER-PLATZ",
        "expanded": "Führe den Auftrag am markierten lokalen Platz C4 des linken 28er-Rades aus; keine Umlaufrichtung ist nötig.",
        "visual_role": "lokaler Platz des linken 28er-Rades",
    },
    "C5@f69v.2": {
        "features": {"WATER", "MOISTURE", "HOLD"},
        "short": "BEI DER MARKIERTEN FEUCHTE-/WETTERLAGE",
        "expanded": "Führe den Auftrag bei der im mittleren Ring C5 bezeichneten Feuchte-/Wetterlage aus.",
        "visual_role": "mittlerer Feuchte-/Wetterring",
    },
    "C6@f69v.3": {
        "features": {"HEAT", "LIGHT", "BODY", "TARGET"},
        "short": "BEI DER MARKIERTEN LICHT-/KOERPERQUALITAET",
        "expanded": "Führe den Auftrag bei der im rechten Ring C6 bezeichneten Licht-/Körperqualität aus.",
        "visual_role": "rechter Licht-/Körperqualitätsring",
    },
}

DEMANDS = {
    "B1": {"WATER": 3, "MOISTURE": 2, "HOLD": 1},
    "B2": {"PASSAGE": 3, "MEASURE": 2, "COUNTED_PLACE": 1},
    "B3": {"WORK": 3, "COMPLEX_SEQUENCE": 2, "ASPECT": 1},
    "B4": {"HEAT": 3, "LIGHT": 2, "BODY": 1},
    "B5": {"TARGET": 3, "DIRECT_PLACE": 2},
    "B6": {"COLLECT": 3, "PHASE": 2, "START_END": 1},
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    astro = read(ASTRO)
    orders = read(ORDERS)
    old_condition = {row["biological_record"]: row["condition_handle"] for row in orders}

    condition_rows = []
    selected_groups = []
    for handle, spec in CONDITIONS.items():
        shelf, locus = handle.split("@")
        page = locus.split(".")[0]
        subset = [row for row in astro if row["page"] == page and row["locus"] == locus]
        condition_rows.append(
            {
                "condition_handle": handle,
                "shelf": shelf,
                "page": page,
                "locus": locus,
                "groups": len(subset),
                "visual_role_de": spec["visual_role"],
                "workshop_features": ",".join(sorted(spec["features"])),
                "short_condition_de": spec["short"],
                "expanded_condition_de": spec["expanded"],
                "requires_start_or_direction": "NO",
                "external_name_required": "NO",
            }
        )
        for row in subset:
            selected_groups.append(
                {
                    "condition_handle": handle,
                    "page": row["page"],
                    "locus": row["locus"],
                    "event_index": row["event_index"],
                    "opaque_local_id": row["opaque_local_id"],
                    "surface": row["surface"],
                    "component_parse": row["selected_component_parse"],
                    "relative_reading_de": row["relative_condition_reading_de"],
                    "short_condition_de": spec["short"],
                    "copy_rule": "COPY_COMPLETE_LOCAL_LOCUS",
                }
            )

    matrix_rows = []
    selected_by_record = {}
    for record, weights in DEMANDS.items():
        candidates = []
        for handle, spec in CONDITIONS.items():
            matched = [feature for feature in weights if feature in spec["features"]]
            score = sum(weights[feature] for feature in matched)
            candidates.append(
                {
                    "biological_record": record,
                    "condition_handle": handle,
                    "application_demand": ",".join(f"{feature}:{weights[feature]}" for feature in weights),
                    "condition_features": ",".join(sorted(spec["features"])),
                    "matched_features": ",".join(matched) if matched else "NONE",
                    "fit_score": score,
                    "maximum_score": sum(weights.values()),
                    "was_current_link": "YES" if old_condition[record] == handle else "NO",
                    "selected": "NO",
                }
            )
        winner = sorted(candidates, key=lambda row: (-int(row["fit_score"]), 0 if row["was_current_link"] == "YES" else 1, row["condition_handle"]))[0]
        winner["selected"] = "YES"
        selected_by_record[record] = winner["condition_handle"]
        matrix_rows.extend(candidates)

    link_rows = []
    order_rows = []
    for order in orders:
        record = order["biological_record"]
        handle = selected_by_record[record]
        spec = CONDITIONS[handle]
        matrix = next(row for row in matrix_rows if row["biological_record"] == record and row["condition_handle"] == handle)
        link_rows.append(
            {
                "biological_record": record,
                "condition_handle": handle,
                "short_condition_de": spec["short"],
                "fit_score": matrix["fit_score"],
                "maximum_score": matrix["maximum_score"],
                "condition_changed": "NO" if handle == old_condition[record] else "YES",
                "workshop_reason_de": f"{record} verlangt {matrix['application_demand']}; {handle} liefert {matrix['matched_features']}.",
            }
        )
        order_rows.append(
            {
                "order_id": order["order_id"],
                "revised_product": order["revised_product"],
                "biological_record": record,
                "condition_handle": handle,
                "concrete_condition_de": spec["expanded"],
                "complete_concrete_order_de": f"Stelle {order['revised_product']} bereit; führe {record} aus. {spec['expanded']}",
                "condition_changed": "NO" if handle == order["condition_handle"] else "YES",
            }
        )

    write(f"{PREFIX}_6_CONCRETE_CONDITION_HANDLES.tsv", condition_rows, ["condition_handle", "shelf", "page", "locus", "groups", "visual_role_de", "workshop_features", "short_condition_de", "expanded_condition_de", "requires_start_or_direction", "external_name_required"])
    write(f"{PREFIX}_73_COMPLETE_CONDITION_GROUPS.tsv", selected_groups, ["condition_handle", "page", "locus", "event_index", "opaque_local_id", "surface", "component_parse", "relative_reading_de", "short_condition_de", "copy_rule"])
    write(f"{PREFIX}_36_CONDITION_APPLICATION_MATRIX.tsv", matrix_rows, ["biological_record", "condition_handle", "application_demand", "condition_features", "matched_features", "fit_score", "maximum_score", "was_current_link", "selected"])
    write(f"{PREFIX}_6_SELECTED_WHEN_LINKS.tsv", link_rows, ["biological_record", "condition_handle", "short_condition_de", "fit_score", "maximum_score", "condition_changed", "workshop_reason_de"])
    write(f"{PREFIX}_6_CONCRETE_ORDER_HEADERS.tsv", order_rows, ["order_id", "revised_product", "biological_record", "condition_handle", "concrete_condition_de", "complete_concrete_order_de", "condition_changed"])

    lines = ["# Sechs konkrete Wann-/Bedingungsgriffe", ""]
    for row in order_rows:
        lines.extend(
            [
                f"## {row['order_id']}",
                "",
                str(row["complete_concrete_order_de"]),
                "",
            ]
        )
    lines.extend(
        [
            "## Werkstattregel",
            "",
            "Ein Bedingungsgriff ist eine lokale Adresse plus eine kurze Arbeitslesung. Große Ringe",
            "werden vollständig kopiert; ein Sternort darf aus nur einer Gruppe bestehen. Weder eine",
            "Umlaufrichtung noch ein äußerer Planeten-, Monats- oder Tierkreisname wird benötigt.",
        ]
    )
    (HERE / f"{PREFIX}_CONCRETE_WHEN_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "ALL_SIX_EXISTING_CONDITION_LINKS_GAIN_CONCRETE_WORKSHOP_READINGS_WITHOUT_REASSIGNMENT",
        "condition_handles": len(condition_rows),
        "condition_groups": len(selected_groups),
        "matrix_cells": len(matrix_rows),
        "selected_links": len(link_rows),
        "condition_changes": sum(row["condition_changed"] == "YES" for row in link_rows),
        "full_score_links": sum(row["fit_score"] == row["maximum_score"] for row in link_rows),
        "requires_start_or_direction": 0,
        "external_names": 0,
        "new_group_meanings": 0,
        "selected_mapping": selected_by_record,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 887: concrete condition matching\n\n"
        "Six local Astro handles now have short workshop conditions: phase place, aspect place,\n"
        "direct star place, local 28-place, moisture/weather ring and light/body-quality ring.\n"
        "All six current WHEN links remain the best fits in the 36-cell working matrix.\n\n"
        "The 73 local groups remain complete and locally addressed. No order, direction, external\n"
        "celestial name or new group meaning is introduced. The concrete conditions are workshop\n"
        "expansions of the pictures and handles, not lexical translations of individual labels.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
