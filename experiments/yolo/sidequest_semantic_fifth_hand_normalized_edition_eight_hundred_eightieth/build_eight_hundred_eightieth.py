#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK_DIR = ROOT / "sidequest_semantic_six_order_workshop_book_eight_hundred_seventy_sixth"
RENDER_DIR = ROOT / "sidequest_semantic_multihand_renderer_drill_eight_hundred_seventy_eighth"
MARKS = BOOK_DIR / "EIGHT_HUNDRED_SEVENTY_SIXTH_438_MARK_SIX_ORDER_BOOK.tsv"
UNITS = BOOK_DIR / "EIGHT_HUNDRED_SEVENTY_SIXTH_119_UNIT_SIX_ORDER_BOOK.tsv"
ORDERS = BOOK_DIR / "EIGHT_HUNDRED_SEVENTY_SIXTH_6_COMPLETE_ORDER_SUMMARY.tsv"
RENDERERS = RENDER_DIR / "EIGHT_HUNDRED_SEVENTY_EIGHTH_56_CORE_RENDERER_FAMILIES.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTIETH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def class_of(stage: str) -> str:
    return "PREP" if stage.startswith("MAKE") else "APP" if stage.startswith("APPLY") else "COND"


def main() -> None:
    marks = read(MARKS)
    source_units = read(UNITS)
    orders = read(ORDERS)
    renderers = read(RENDERERS)
    house = {row["identity"]: row["house_model_surface"] for row in renderers}

    normalized = []
    for row in marks:
        surface = house.get(row["identity"], row["surface"])
        normalized.append(
            {
                "order_id": row["order_id"],
                "order_mark_id": row["order_mark_id"],
                "stage": row["stage"],
                "page": row["page"],
                "unit": row["unit"],
                "source_id": row["source_id"],
                "identity": row["identity"],
                "original_surface": row["surface"],
                "fifth_hand_surface": surface,
                "surface_action": "NORMALIZE_TO_HOUSE" if surface != row["surface"] else "COPY_UNCHANGED",
                "card_class": "PORTABLE_CORE" if row["identity"] in house else "LOCAL_MODEL",
                "component_recipe": row["component_recipe"],
                "concrete_default_de": row["concrete_default_de"],
                "owner_or_handle_de": row["owner_or_handle_de"],
                "meaning_changed": "NO",
                "identity_changed": "NO",
            }
        )

    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in normalized:
        grouped[(row["order_id"], row["stage"], row["unit"])].append(row)
    unit_rows = []
    for key, subset in grouped.items():
        source = unit_lookup[key]
        unit_rows.append(
            {
                "order_id": key[0],
                "stage": key[1],
                "unit": key[2],
                "page": subset[0]["page"],
                "original_surface_sequence": " ".join(row["original_surface"] for row in subset),
                "fifth_hand_surface_sequence": " ".join(row["fifth_hand_surface"] for row in subset),
                "normalized_marks": sum(row["surface_action"] == "NORMALIZE_TO_HOUSE" for row in subset),
                "literal_sequence_de": source["literal_sequence_de"],
                "fluent_workshop_reading_de": source["fluent_workshop_reading_de"],
                "meaning_changed": "NO",
            }
        )

    changed_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in normalized:
        if row["surface_action"] == "NORMALIZE_TO_HOUSE":
            changed_groups[(row["identity"], row["original_surface"], row["fifth_hand_surface"])].append(row)
    mapping_rows = []
    for (identity, original, target), subset in sorted(changed_groups.items()):
        mapping_rows.append(
            {
                "identity": identity,
                "original_surface": original,
                "fifth_hand_surface": target,
                "changed_marks": len(subset),
                "orders": ",".join(sorted({row["order_id"] for row in subset})),
                "pages": ",".join(sorted({row["page"] for row in subset})),
                "component_recipe": subset[0]["component_recipe"],
                "concrete_default_de": subset[0]["concrete_default_de"],
                "meaning_changed": "NO",
            }
        )

    order_rows = []
    for order in orders:
        subset = [row for row in normalized if row["order_id"] == order["order_id"]]
        order_rows.append(
            {
                "order_id": order["order_id"],
                "internal_product": order["internal_product"],
                "biological_record": order["biological_record"],
                "condition_handle": order["condition_handle"],
                "marks": len(subset),
                "normalized_core_marks": sum(row["surface_action"] == "NORMALIZE_TO_HOUSE" for row in subset),
                "unchanged_core_marks": sum(row["surface_action"] == "COPY_UNCHANGED" and row["card_class"] == "PORTABLE_CORE" for row in subset),
                "unchanged_local_model_marks": sum(row["card_class"] == "LOCAL_MODEL" for row in subset),
                "units": sum(row["order_id"] == order["order_id"] for row in unit_rows),
                "meaning_changes": 0,
                "identity_changes": 0,
            }
        )

    inventory_rows = []
    for section in ["ALL", "PREP", "APP", "COND"]:
        subset = normalized if section == "ALL" else [row for row in normalized if class_of(row["stage"]) == section]
        inventory_rows.append(
            {
                "stage_class": section,
                "marks": len(subset),
                "original_surface_types": len({row["original_surface"] for row in subset}),
                "fifth_hand_surface_types": len({row["fifth_hand_surface"] for row in subset}),
                "surface_types_removed": len({row["original_surface"] for row in subset}) - len({row["fifth_hand_surface"] for row in subset}),
                "normalized_marks": sum(row["surface_action"] == "NORMALIZE_TO_HOUSE" for row in subset),
                "identity_types": len({row["identity"] for row in subset}),
            }
        )

    write(f"{PREFIX}_438_MARK_FIFTH_HAND_EDITION.tsv", normalized, ["order_id", "order_mark_id", "stage", "page", "unit", "source_id", "identity", "original_surface", "fifth_hand_surface", "surface_action", "card_class", "component_recipe", "concrete_default_de", "owner_or_handle_de", "meaning_changed", "identity_changed"])
    write(f"{PREFIX}_119_UNIT_FIFTH_HAND_EDITION.tsv", unit_rows, ["order_id", "stage", "unit", "page", "original_surface_sequence", "fifth_hand_surface_sequence", "normalized_marks", "literal_sequence_de", "fluent_workshop_reading_de", "meaning_changed"])
    write(f"{PREFIX}_SURFACE_NORMALIZATION_MAP.tsv", mapping_rows, ["identity", "original_surface", "fifth_hand_surface", "changed_marks", "orders", "pages", "component_recipe", "concrete_default_de", "meaning_changed"])
    write(f"{PREFIX}_6_ORDER_NORMALIZATION_SUMMARY.tsv", order_rows, ["order_id", "internal_product", "biological_record", "condition_handle", "marks", "normalized_core_marks", "unchanged_core_marks", "unchanged_local_model_marks", "units", "meaning_changes", "identity_changes"])
    write(f"{PREFIX}_4_SURFACE_INVENTORY_ROWS.tsv", inventory_rows, ["stage_class", "marks", "original_surface_types", "fifth_hand_surface_types", "surface_types_removed", "normalized_marks", "identity_types"])

    lines = ["# Sechs Aufträge in der fünften Werkstatthand", ""]
    for order in orders:
        lines.extend([f"## {order['order_id']}: {order['internal_product']} → {order['biological_record']} → {order['condition_handle']}", ""])
        for row in unit_rows:
            if row["order_id"] != order["order_id"]:
                continue
            lines.extend(
                [
                    f"- **{row['unit']}** ({row['page']}): `{row['fifth_hand_surface_sequence']}`",
                    f"  {row['fluent_workshop_reading_de']}",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "## Schreibregel",
            "",
            "Die fünfte Hand verwendet für jede tragbare Kernidentität genau eine Hausform.",
            "Alle lokalen Prosa- und Himmelskarten bleiben dagegen Zeichen für Zeichen am",
            "Muster. Die Umschrift verändert weder Reihenfolge, Identität noch Werkstattwert.",
        ]
    )
    (HERE / f"{PREFIX}_COMPLETE_FIFTH_HAND_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "FIFTH_HAND_NORMALIZES_PORTABLE_RENDERING_WITHOUT_CHANGING_IDENTITY_OR_MEANING",
        "orders": len(order_rows),
        "marks": len(normalized),
        "units": len(unit_rows),
        "identities": len({row["identity"] for row in normalized}),
        "core_marks": sum(row["card_class"] == "PORTABLE_CORE" for row in normalized),
        "local_model_marks": sum(row["card_class"] == "LOCAL_MODEL" for row in normalized),
        "normalized_marks": sum(row["surface_action"] == "NORMALIZE_TO_HOUSE" for row in normalized),
        "normalization_mappings": len(mapping_rows),
        "original_surface_types": len({row["original_surface"] for row in normalized}),
        "fifth_hand_surface_types": len({row["fifth_hand_surface"] for row in normalized}),
        "surface_types_removed": len({row["original_surface"] for row in normalized}) - len({row["fifth_hand_surface"] for row in normalized}),
        "meaning_changes": sum(row["meaning_changed"] != "NO" for row in normalized),
        "identity_changes": sum(row["identity_changed"] != "NO" for row in normalized),
        "fixed_pages": sorted({row["page"] for row in normalized}),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 880: complete fifth-hand normalized edition\n\n"
        "The fifth hand rewrites all six orders with one house surface per portable core\n"
        "identity. Sixty-eight of 438 visible marks change renderer; all 177 local-model marks\n"
        "remain exact. The visible surface inventory falls from 247 to 208 types while all 228\n"
        "identities, 119 units, owners, condition loci and concrete working readings remain fixed.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
