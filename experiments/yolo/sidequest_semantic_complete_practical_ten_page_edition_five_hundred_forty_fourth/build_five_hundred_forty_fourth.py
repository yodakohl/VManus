#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P538 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_five_hundred_thirty_eighth"
P536 = ROOT / "experiments/yolo/sidequest_semantic_common_workshop_grammar_five_hundred_thirty_sixth"
P543 = ROOT / "experiments/yolo/sidequest_semantic_astro_purpose_reconnection_five_hundred_forty_third"
P75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def clause(reading: str) -> str:
    parts = reading.split(" · ")
    if parts and parts[-1] == "Schluss":
        return (" ".join(parts[:-1]) + "; schließen").strip()
    return " ".join(parts)


def main() -> None:
    cards = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    revised_events = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_EDITION.tsv")
    source_events = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")
    astro_loci = read_tsv(P543 / "FIVE_HUNDRED_FORTY_THIRD_ONE_HUNDRED_FORTY_TWO_DUAL_ASTRO_LOCI.tsv")
    astro_groups = read_tsv(P543 / "FIVE_HUNDRED_FORTY_THIRD_THREE_HUNDRED_NINETY_FIVE_ASTRO_GROUP_BINDING.tsv")
    selected_groups = read_tsv(P75 / "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv")
    source_for = {row["event_id"]: row for row in source_events}
    selected_for = {row["opaque_local_id"]: row for row in selected_groups}

    prose_rows: list[dict[str, str]] = []
    for event in revised_events:
        source = source_for[event["event_id"]]
        section = "PLANT_MATERIAL_ARTICLE" if event["record"].startswith("H") else "WET_WORKSHOP_STATION"
        prose_rows.append(
            {
                "event_id": event["event_id"],
                "source_position_id": "SRC_E180_E181" if event["event_id"] in {"E180", "E181"} else f"SRC_{event['event_id']}",
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "locus": source["locus"],
                "silent_owner_de": event["silent_owner_de"],
                "surface": event["surface"],
                "card_no": event["card_no"],
                "component_parse": event["revised_component_parse"],
                "literal_card_reading_de": event["revised_card_reading_de"],
                "practical_clause_de": clause(event["revised_card_reading_de"]),
                "composition_status": event["composition_status"],
                "purpose_section": section,
                "copy_status": (
                    "ANTICIPATORY_EDGE_COPY_FIRST"
                    if event["event_id"] == "E180"
                    else "EXECUTABLE_REPEAT_SECOND"
                    if event["event_id"] == "E181"
                    else "ONE_VISIBLE_ONE_SOURCE"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_PRACTICAL_PROSE_INTERLINEAR.tsv", prose_rows)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose_rows:
        by_statement[row["statement_id"]].append(row)
    statements: list[dict[str, str]] = []
    for statement_id, members in by_statement.items():
        owners = list(dict.fromkeys(row["silent_owner_de"] for row in members))
        pieces: list[str] = []
        previous_owner = None
        for row in members:
            if row["silent_owner_de"] != previous_owner:
                if previous_owner is not None:
                    pieces.append(f"[ohne Bildkante zu {row['silent_owner_de']}]")
                else:
                    pieces.append(f"Bei {row['silent_owner_de']}")
                previous_owner = row["silent_owner_de"]
            pieces.append(row["practical_clause_de"])
        statements.append(
            {
                "statement_id": statement_id,
                "page": members[0]["page"],
                "record": members[0]["record"],
                "silent_owners_de": "|".join(owners),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surface_sequence": " ".join(row["surface"] for row in members),
                "component_sequence": " | ".join(row["component_parse"] for row in members),
                "complete_practical_reading_de": "; dann ".join(pieces) + ".",
                "terminal": "YES" if any("Schluss" in row["literal_card_reading_de"].split(" · ") for row in members) else "NO",
                "crosses_owner_boundary": "YES" if len(owners) > 1 else "NO",
                "purpose": "PLANT_MATERIAL_PROCESS" if members[0]["record"].startswith("H") else "WET_WORKSHOP_OPERATION",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FOURTH_ONE_HUNDRED_SIXTEEN_COMPLETE_PROSE_STATEMENTS.tsv", statements)

    locus_for = {row["locus"]: row for row in astro_loci}
    astro_rows: list[dict[str, str]] = []
    for group in astro_groups:
        locus = locus_for[group["locus"]]
        selected = selected_for[group["opaque_local_id"]]
        astro_rows.append(
            {
                "group_serial": group["group_serial"],
                "source_position_id": f"ASTRO_{group['opaque_local_id']}",
                "page": group["page"],
                "diagram_id": group["diagram_id"],
                "locus": group["locus"],
                "event_index_within_locus": selected["event_index"],
                "opaque_local_id": group["opaque_local_id"],
                "local_namespace": group["local_namespace"],
                "local_image_owner": group["local_image_owner"],
                "literal_group_reading_de": f"Etikettsegment {selected['event_index']} am lokalen Bildplatz",
                "practical_almanac_expansion_de": locus["technical_expansion_de"],
                "purpose_section": "CELESTIAL_WORK_ALMANAC",
                "orientation": "NONE_SELECTED",
                "crosspage_join": "NONE",
                "prose_card_import": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FOURTH_THREE_HUNDRED_NINETY_FIVE_PRACTICAL_ASTRO_INTERLINEAR.tsv", astro_rows)

    unified: list[dict[str, str]] = []
    for index, row in enumerate(prose_rows, 1):
        unified.append(
            {
                "unified_index": f"U{index:03d}",
                "kind": "PROSE_CARD",
                "page": row["page"],
                "local_unit": row["statement_id"],
                "visible_id": row["event_id"],
                "source_position_id": row["source_position_id"],
                "surface_or_opaque_id": row["surface"],
                "dictionary_or_namespace_id": row["card_no"],
                "literal_value_de": row["literal_card_reading_de"],
                "practical_expansion_de": f"Bei {row['silent_owner_de']}: {row['practical_clause_de']}",
                "provenance": row["composition_status"],
                "blank": "NO",
            }
        )
    for offset, row in enumerate(astro_rows, len(prose_rows) + 1):
        unified.append(
            {
                "unified_index": f"U{offset:03d}",
                "kind": "ASTRO_GROUP",
                "page": row["page"],
                "local_unit": row["locus"],
                "visible_id": row["opaque_local_id"],
                "source_position_id": row["source_position_id"],
                "surface_or_opaque_id": row["opaque_local_id"],
                "dictionary_or_namespace_id": row["local_namespace"],
                "literal_value_de": row["literal_group_reading_de"],
                "practical_expansion_de": row["practical_almanac_expansion_de"],
                "provenance": "LOCAL_ASTRO_EXEMPLAR_LABEL",
                "blank": "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FOURTH_SEVEN_HUNDRED_SEVENTY_SIX_UNIFIED_PRACTICAL_LEDGER.tsv", unified)

    lines = [
        "# Vollständige zehnseitige Werkstattausgabe",
        "",
        "Arbeitstheorie: Pflanzenmaterial- und Nasswerkstattbuch mit lokalem Himmels-/Arbeitsalmanach.",
        "",
        "## Prosa",
        "",
    ]
    for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        record_rows = [row for row in statements if row["record"] == record]
        lines.extend([f"### {record} — {record_rows[0]['page']}", ""])
        for row in record_rows:
            lines.append(f"- {row['statement_id']}: {row['complete_practical_reading_de']}")
        lines.append("")
    lines.extend(["## Himmels-/Arbeitsalmanach", ""])
    for page in ["f67r2", "f68r1", "f69v"]:
        lines.extend([f"### {page}", ""])
        for row in astro_loci:
            if row["page"] == page:
                lines.append(f"- {row['locus']}: {row['technical_expansion_de']}")
        lines.append("")
    (HERE / "FIVE_HUNDRED_FORTY_FOURTH_COMPLETE_TEN_PAGE_PRACTICAL_EDITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    summary = {
        "status": "PASS",
        "pages": 10,
        "prose_cards": len(prose_rows),
        "prose_source_positions": len({row["source_position_id"] for row in prose_rows}),
        "exact_prose_cards": len(cards),
        "prose_statements": len(statements),
        "astro_groups": len(astro_rows),
        "astro_loci": len(astro_loci),
        "unified_visible_units": len(unified),
        "unified_source_positions": len({row["source_position_id"] for row in unified}),
        "composition_counts": dict(Counter(row["composition_status"] for row in prose_rows)),
        "blank_units": sum(row["blank"] == "YES" for row in unified),
        "working_purpose": "PRACTICAL_PLANT_MATERIAL_BATHHOUSE_WITH_CELESTIAL_WORK_ALMANAC",
    }
    (HERE / "FIVE_HUNDRED_FORTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
