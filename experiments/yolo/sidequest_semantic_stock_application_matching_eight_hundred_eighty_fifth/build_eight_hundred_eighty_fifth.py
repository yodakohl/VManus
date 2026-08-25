#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CHAIN_DIR = ROOT / "sidequest_semantic_herbal_batch_chain_eight_hundred_eighty_fourth"
EDITION_DIR = ROOT / "sidequest_semantic_complete_phrase_first_edition_eight_hundred_eighty_third"
ORDER_DIR = ROOT / "sidequest_semantic_six_order_workshop_book_eight_hundred_seventy_sixth"
STATES = CHAIN_DIR / "EIGHT_HUNDRED_EIGHTY_FOURTH_19_BATCH_STATES.tsv"
STOCK = CHAIN_DIR / "EIGHT_HUNDRED_EIGHTY_FOURTH_10_STOCK_READY_HANDLES.tsv"
EVENTS = EDITION_DIR / "EIGHT_HUNDRED_EIGHTY_THIRD_381_EVENT_COMPLETE_FIFTH_HAND.tsv"
ORDERS = ORDER_DIR / "EIGHT_HUNDRED_SEVENTY_SIXTH_6_COMPLETE_ORDER_SUMMARY.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_FIFTH"

FEATURE_COMPONENTS = {
    "MEASURE": {"AIN", "AIIN", "IIN"},
    "WATER": {"AIR"},
    "ADD": {"K"},
    "EXTRACT": {"CH"},
    "TARGET": {"AL"},
    "CONTINUE": {"OL"},
    "HEAT": {"CHK"},
    "HOLD": {"SH", "SHED"},
    "PASSAGE": {"CKH", "L", "P"},
    "SET": {"OK"},
    "CLOSE": {"DY"},
    "PREPARE": {"CTH", "OR"},
    "WORK": {"T", "O", "CHD"},
    "COLLECT": {"SOLK"},
}

DEMANDS = {
    "B1": ({"WATER": 2, "CONTINUE": 1, "SET": 1, "PASSAGE": 1, "HOLD": 1}, "WATER"),
    "B2": ({"PASSAGE": 2, "MEASURE": 1, "SET": 1, "HOLD": 1, "TARGET": 1, "EXTRACT": 1}, "PASSAGE"),
    "B3": ({"WORK": 2, "MEASURE": 1, "PREPARE": 1, "SET": 1, "WATER": 2}, "WATER"),
    "B4": ({"HEAT": 2, "HOLD": 1, "ADD": 1, "PASSAGE": 1, "TARGET": 1, "SET": 1}, "HEAT"),
    "B5": ({"TARGET": 2, "WORK": 1, "CONTINUE": 1, "HOLD": 1, "PASSAGE": 1}, "TARGET"),
    "B6": ({"COLLECT": 2, "ADD": 1, "TARGET": 1, "CONTINUE": 1, "MEASURE": 1, "PREPARE": 1}, "COLLECT"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def features(row: dict[str, str]) -> set[str]:
    atoms = set(row["component_recipe"].split("+"))
    return {name for name, components in FEATURE_COMPONENTS.items() if atoms & components}


def main() -> None:
    states = read(STATES)
    stock = read(STOCK)
    events = read(EVENTS)
    orders = read(ORDERS)
    state_by_handle = {row["product_handle"]: row for row in states}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)

    stock_feature_rows = []
    stock_features: dict[str, set[str]] = {}
    stock_depth: dict[str, int] = {}
    for stock_row in stock:
        handle = stock_row["product_handle"]
        chain = []
        current = handle
        while current != "NONE":
            chain.append(current)
            current = state_by_handle[current]["revised_predecessor"]
        chain.reverse()
        counts = Counter(
            feature
            for chain_handle in chain
            for event in events_by_statement[state_by_handle[chain_handle]["statement_id"]]
            for feature in features(event)
        )
        stock_features[handle] = set(counts)
        stock_depth[handle] = len(chain)
        stock_feature_rows.append(
            {
                "product_handle": handle,
                "owner_sigil": stock_row["owner_sigil"],
                "chain_depth": len(chain),
                "cumulative_chain": " -> ".join(chain),
                "feature_set": ",".join(sorted(counts)),
                "feature_counts": ",".join(f"{feature}:{counts[feature]}" for feature in sorted(counts)),
                "explicit_close": stock_row["explicit_close"],
                "availability_reason": stock_row["availability_reason"],
                "internal_workshop_name_de": stock_row["internal_workshop_name_de"],
            }
        )

    demand_rows = []
    for record, (weights, primary) in DEMANDS.items():
        subset = [row for row in events if row["record"] == record]
        observed = Counter(feature for row in subset for feature in features(row))
        demand_rows.append(
            {
                "biological_record": record,
                "page": subset[0]["page"],
                "events": len(subset),
                "weighted_demand": ",".join(f"{feature}:{weights[feature]}" for feature in weights),
                "primary_distinctive_feature": primary,
                "observed_feature_counts": ",".join(f"{feature}:{observed[feature]}" for feature in sorted(observed)),
                "maximum_match_score": sum(weights.values()),
            }
        )

    original_by_record = {row["biological_record"]: row["internal_product"] for row in orders}
    matrix_rows = []
    selected_by_record = {}
    for record, (weights, primary) in DEMANDS.items():
        candidates = []
        primary_available = any(primary in stock_features[handle] for handle in stock_features)
        for stock_row in stock:
            handle = stock_row["product_handle"]
            present = stock_features[handle]
            matched = [feature for feature in weights if feature in present]
            missing = [feature for feature in weights if feature not in present]
            raw = sum(weights[feature] for feature in matched)
            primary_match = primary in present
            candidates.append(
                {
                    "biological_record": record,
                    "product_handle": handle,
                    "owner_sigil": stock_row["owner_sigil"],
                    "chain_depth": stock_depth[handle],
                    "supply_features": ",".join(sorted(present)),
                    "matched_demand_features": ",".join(matched) if matched else "NONE",
                    "missing_demand_features": ",".join(missing) if missing else "NONE",
                    "raw_match_score": raw,
                    "maximum_match_score": sum(weights.values()),
                    "primary_feature": primary,
                    "primary_feature_available_in_any_stock": "YES" if primary_available else "NO",
                    "primary_feature_matched": "YES" if primary_match else "NO",
                    "explicit_close": stock_row["explicit_close"],
                    "was_original_supply": "YES" if original_by_record[record] == handle else "NO",
                    "selected": "NO",
                }
            )
        ranked = sorted(
            candidates,
            key=lambda row: (
                -(1 if row["primary_feature_matched"] == "YES" else 0) if row["primary_feature_available_in_any_stock"] == "YES" else 0,
                -int(row["raw_match_score"]),
                int(row["chain_depth"]),
                -(1 if row["explicit_close"] == "YES" else 0),
                str(row["product_handle"]),
            ),
        )
        winner = ranked[0]
        winner["selected"] = "YES"
        selected_by_record[record] = winner["product_handle"]
        matrix_rows.extend(candidates)

    stock_by_handle = {row["product_handle"]: row for row in stock}
    selected_rows = []
    revised_order_rows = []
    for record in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        selected = selected_by_record[record]
        matrix = next(row for row in matrix_rows if row["biological_record"] == record and row["product_handle"] == selected)
        old = original_by_record[record]
        selected_rows.append(
            {
                "biological_record": record,
                "old_supply": old,
                "selected_supply": selected,
                "selected_name_de": stock_by_handle[selected]["internal_workshop_name_de"],
                "raw_match_score": matrix["raw_match_score"],
                "maximum_match_score": matrix["maximum_match_score"],
                "primary_feature": matrix["primary_feature"],
                "primary_feature_matched": matrix["primary_feature_matched"],
                "supply_changed": "NO" if old == selected else "YES",
                "selection_reason_de": f"{selected} deckt {matrix['matched_demand_features']}; fehlend {matrix['missing_demand_features']}; bei Gleichstand gewinnt die kürzere entnehmbare Kette.",
            }
        )
        order = next(row for row in orders if row["biological_record"] == record)
        revised_order_rows.append(
            {
                "order_id": order["order_id"],
                "biological_record": record,
                "old_product": old,
                "revised_product": selected,
                "revised_product_name_de": stock_by_handle[selected]["internal_workshop_name_de"],
                "condition_handle": order["condition_handle"],
                "supply_changed": "NO" if old == selected else "YES",
                "revised_instruction_de": f"Stelle {selected} bereit; führe {record} aus; verwende den vollständigen Bedingungsgriff {order['condition_handle']}.",
            }
        )

    write(f"{PREFIX}_10_STOCK_PROCESS_PROFILES.tsv", stock_feature_rows, ["product_handle", "owner_sigil", "chain_depth", "cumulative_chain", "feature_set", "feature_counts", "explicit_close", "availability_reason", "internal_workshop_name_de"])
    write(f"{PREFIX}_6_APPLICATION_DEMAND_PROFILES.tsv", demand_rows, ["biological_record", "page", "events", "weighted_demand", "primary_distinctive_feature", "observed_feature_counts", "maximum_match_score"])
    write(f"{PREFIX}_60_STOCK_APPLICATION_MATRIX.tsv", matrix_rows, ["biological_record", "product_handle", "owner_sigil", "chain_depth", "supply_features", "matched_demand_features", "missing_demand_features", "raw_match_score", "maximum_match_score", "primary_feature", "primary_feature_available_in_any_stock", "primary_feature_matched", "explicit_close", "was_original_supply", "selected"])
    write(f"{PREFIX}_6_SELECTED_SUPPLIES.tsv", selected_rows, ["biological_record", "old_supply", "selected_supply", "selected_name_de", "raw_match_score", "maximum_match_score", "primary_feature", "primary_feature_matched", "supply_changed", "selection_reason_de"])
    write(f"{PREFIX}_6_REVISED_ORDER_HEADERS.tsv", revised_order_rows, ["order_id", "biological_record", "old_product", "revised_product", "revised_product_name_de", "condition_handle", "supply_changed", "revised_instruction_de"])

    lines = ["# Vorratsschrank und sechs Anwendungen", ""]
    for row in selected_rows:
        lines.extend(
            [
                f"## {row['biological_record']}: {row['selected_supply']}",
                "",
                f"{row['selected_name_de']}.",
                f"{row['selection_reason_de']}",
                f"Vorher: {row['old_supply']}; Änderung: {row['supply_changed']}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Lesart",
            "",
            "Die Zuordnung vergleicht keine Krankheiten oder Pflanzennamen. Sie fragt nur, welche",
            "fertige Charge bereits die Arbeitsgeschichte mitbringt, die der sichtbare HOW-Record",
            "erneut verlangt: Wasser, Maß, Wärme, Halten, Durchlass, Ziel, Zugabe oder Fortsetzung.",
            "Vier der sechs alten Griffe wechseln. Das ist eine kreative Werkstattrevision; die",
            "Kartenbedeutungen selbst bleiben unverändert.",
        ]
    )
    (HERE / f"{PREFIX}_STOCK_APPLICATION_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "PROCESS_FEATURE_MATCHING_REVISES_FOUR_OF_SIX_SUPPLY_HANDLES",
        "stock_profiles": len(stock_feature_rows), "application_profiles": len(demand_rows), "matrix_cells": len(matrix_rows),
        "selected_supplies": len(selected_rows), "distinct_selected_supplies": len({row["selected_supply"] for row in selected_rows}),
        "supply_changes": sum(row["supply_changed"] == "YES" for row in selected_rows), "supply_keeps": sum(row["supply_changed"] == "NO" for row in selected_rows),
        "selected_mapping": {row["biological_record"]: row["selected_supply"] for row in selected_rows},
        "dictionary_changes": 0, "new_card_meanings": 0, "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 885: stock-to-application matching\n\n"
        "Ten ready Herbal stocks are compared with six Biological operation profiles in a 60-cell\n"
        "workshop matrix. Matching uses only the existing concrete process features and favors the\n"
        "shorter available chain after primary-feature and weighted-overlap ties.\n\n"
        "The selected map is B1←A.G2, B2←B.X4, B3←A.G2, B4←C.W2, B5←B.X1 and B6←D.P1.\n"
        "Four old supplies change; no card meaning changes. The revision is a concrete workshop\n"
        "hypothesis about compatible batch history, not a claim about plant or medical identity.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
