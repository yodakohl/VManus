#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = ROOT / "experiments/yolo/sidequest_semantic_astro_component_transfer_four_hundred_sixty_first/FOUR_HUNDRED_SIXTY_FIRST_395_ASTRO_GROUP_TRANSFER.tsv"

OPERATION_COMPONENTS = {"OK", "K", "L", "CH", "CHD", "CHK", "CKH", "CKHE", "CTH", "DY", "LDDY", "LS", "LSH", "P", "R", "SH", "SHED", "SOLK", "T"}


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
    groups = read(GROUPS)
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        by_locus[row["locus"]].append(row)

    loci = []
    for locus, rows in by_locus.items():
        components = [component for row in rows if row["selected_component_parse"] != "NONE" for component in row["selected_component_parse"].split("+") if not component.startswith("WHOLE[")]
        transferred = [row for row in rows if row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"}]
        residual = [row for row in rows if row not in transferred]
        has_operation = bool(set(components) & OPERATION_COMPONENTS)
        if not transferred:
            instruction_class = "LOCAL_NAME_ONLY"
        elif has_operation and residual:
            instruction_class = "MIXED_LOCAL_NAME_AND_OPERATION"
        elif has_operation:
            instruction_class = "OPERATIONAL_INSTRUCTION"
        elif residual:
            instruction_class = "MIXED_LOCAL_NAME_AND_PARAMETER"
        else:
            instruction_class = "PARAMETER_OR_ADDRESS"
        if instruction_class == "LOCAL_NAME_ONLY":
            reading = "Kopiere die lokale Etikette «" + " ".join(row["surface"] for row in rows) + "» am sichtbaren Besitzer; Wert aus dem lokalen Exemplar."
        else:
            rendered = []
            for row in rows:
                if row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"}:
                    rendered.append(row["candidate_workshop_value_de"])
                elif row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE":
                    rendered.append(f"«{row['surface']}»[mehrdeutig]")
                else:
                    rendered.append(f"«{row['surface']}»[lokaler Name]")
            reading = "Am sichtbaren Besitzer: " + "; ".join(rendered) + "."
        loci.append({
            "locus_row": len(loci) + 1, "diagram_id": rows[0]["diagram_id"], "page": rows[0]["page"],
            "locus": locus, "local_namespace": rows[0]["local_namespace"],
            "visible_owners": "|".join(dict.fromkeys(row["visible_owner"] for row in rows)),
            "groups": len(rows), "group_serials": "|".join(row["group_serial"] for row in rows),
            "transferred_groups": len(transferred), "residual_groups": len(residual),
            "components": "+".join(components) if components else "NONE",
            "operation_components": "+".join(component for component in components if component in OPERATION_COMPONENTS) or "NONE",
            "instruction_class": instruction_class, "controlled_reading_de": reading,
            "orientation": "UNSPECIFIED", "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_SECOND_142_LOCUS_INSTRUCTION_GRAMMAR.tsv", loci)

    instruments = []
    titles = {"A1": "Zwei getrennte sektorierte Regelräder", "A2": "Mehrpaneel-Sternstationsinstrument", "A3": "Drei getrennte radiale Arbeitstafeln"}
    for diagram_id, page in (("A1", "f67r2"), ("A2", "f68r1"), ("A3", "f69v")):
        rows = [row for row in loci if row["diagram_id"] == diagram_id]
        counts = Counter(row["instruction_class"] for row in rows)
        instruments.append({
            "diagram_id": diagram_id, "page": page, "title_de": titles[diagram_id], "loci": len(rows),
            "operational_instruction": counts["OPERATIONAL_INSTRUCTION"],
            "mixed_local_operation": counts["MIXED_LOCAL_NAME_AND_OPERATION"],
            "parameter_or_address": counts["PARAMETER_OR_ADDRESS"],
            "mixed_local_parameter": counts["MIXED_LOCAL_NAME_AND_PARAMETER"],
            "local_name_only": counts["LOCAL_NAME_ONLY"],
            "working_reading_de": "Lokale Himmels- oder Diagrammidentität am Bildplatz; soweit vorhanden folgen Arbeitsoperator, Parameter und Adressierung aus dem gemeinsamen Kartensatz.",
            "orientation": "UNSPECIFIED", "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_SECOND_THREE_CONTROLLED_INSTRUMENTS.tsv", instruments)

    pressure = [
        ("AIR", "Wasser", "Lauf oder Fluss", "Wasser is too narrow for celestial wheels"),
        ("HO", "Zutat", "Gabe oder Eintrag", "ingredient is too narrow for sector labels"),
        ("OS", "Gefäß", "Fach oder Gefäß", "container appears twice on f67r2"),
        ("T", "fuellen", "eintragen oder fuellen", "same operator occurs in diagram slots"),
        ("CHEEY_SHEY", "Klarauszug", "Ergebnis oder Freigabe", "exact whole card occurs on f68r1 and f69v"),
        ("OR", "Ansatz", "Ansatz", "setup/batch already transfers without forced revision"),
    ]
    pressure_rows = []
    for component, current, candidate, reason in pressure:
        if component == "CHEEY_SHEY":
            astro_events = sum(row["candidate_workshop_value_de"] == "Klarauszug" for row in groups)
        else:
            astro_events = sum(component in row["selected_component_parse"].split("+") for row in groups if row["selected_component_parse"] != "NONE")
        pressure_rows.append({
            "component_or_card": component, "current_value_de": current, "broader_candidate_de": candidate,
            "astro_events": astro_events, "pressure_reason": reason, "revision_now": "NO_NEXT_PASS",
        })
    write("FOUR_HUNDRED_SIXTY_SECOND_SIX_CROSS_REGISTER_WORD_PRESSURES.tsv", pressure_rows)

    md = ["# Three controlled Astro instrument readings", ""]
    for instrument in instruments:
        md.extend([f"## {instrument['diagram_id']} — {instrument['page']}", "", instrument["working_reading_de"], ""])
        for row in loci:
            if row["diagram_id"] == instrument["diagram_id"]:
                md.append(f"- **{row['locus']} · {row['instruction_class']}**: {row['controlled_reading_de']}")
        md.append("")
    (HERE / "FOUR_HUNDRED_SIXTY_SECOND_THREE_CONTROLLED_INSTRUMENTS.md").write_text("\n".join(md), encoding="utf-8")

    classes = Counter(row["instruction_class"] for row in loci)
    summary = {
        "status": "PASS", "loci": len(loci), "instruments": len(instruments),
        "operational_instruction": classes["OPERATIONAL_INSTRUCTION"],
        "mixed_local_operation": classes["MIXED_LOCAL_NAME_AND_OPERATION"],
        "parameter_or_address": classes["PARAMETER_OR_ADDRESS"],
        "mixed_local_parameter": classes["MIXED_LOCAL_NAME_AND_PARAMETER"],
        "local_name_only": classes["LOCAL_NAME_ONLY"],
        "loci_with_operation": classes["OPERATIONAL_INSTRUCTION"] + classes["MIXED_LOCAL_NAME_AND_OPERATION"],
        "loci_with_parameter_or_address": classes["PARAMETER_OR_ADDRESS"] + classes["MIXED_LOCAL_NAME_AND_PARAMETER"],
    }
    (HERE / "FOUR_HUNDRED_SIXTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
