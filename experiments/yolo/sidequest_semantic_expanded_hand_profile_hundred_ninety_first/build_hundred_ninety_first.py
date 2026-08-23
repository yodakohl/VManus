#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_global_hand_profile_hundred_ninetieth/HUNDRED_NINETIETH_381_EVENT_GLOBAL_PROFILE.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


GROUPS = {
    "S1": ("EXTENDED_Q_FRAME", "Setze q vor weitere aktive Anfangs-, Mittel- oder Schlusskarten.", 7),
    "S2": ("CHED_E_EXPANSION", "Schreibe CHDY am Feldanfang und in der Feldmitte als CHEDY.", 2),
    "S3": ("L_R_CHAIN_BOUNDARY_FRAME", "Wähle bei L/R-Ketten den kurzen o-/d-/s-Rahmen nach Feldstellung.", 5),
    "S4": ("S_STATE_FRAME", "Nutze s-Rahmen für die gelehrten Zustands-/Stoffkarten an ihrer festen Stellung.", 3),
    "S5": ("S_MEASURE_INITIAL", "Schreibe AIIN am Feldanfang als SAIIN.", 1),
    "S6": ("KAIN_MEDIAL_DROP", "Lasse bei CHKAIN in der Feldmitte den ch-Rahmen weg.", 1),
}


MAPPINGS = {
    ("MC120", "INITIAL"): ("S1", "qokaiin"),
    ("MC002", "INITIAL"): ("S1", "qokeey"),
    ("MC017", "INITIAL"): ("S1", "qokain"),
    ("MC040", "INITIAL"): ("S1", "qokal"),
    ("MC026", "MEDIAL"): ("S1", "qoky"),
    ("MC026", "FINAL"): ("S1", "qoky"),
    ("MC028", "ONLY"): ("S1", "qolchedy"),
    ("MC074", "INITIAL"): ("S2", "chedy"),
    ("MC074", "MEDIAL"): ("S2", "chedy"),
    ("MC153", "MEDIAL"): ("S3", "ol"),
    ("MC153", "INITIAL"): ("S3", "sol"),
    ("MC154", "INITIAL"): ("S3", "dal"),
    ("MC154", "FINAL"): ("S3", "dal"),
    ("MC055", "FINAL"): ("S3", "dar"),
    ("MC128", "ONLY"): ("S4", "shedy"),
    ("MC119", "MEDIAL"): ("S4", "shey"),
    ("MC034", "INITIAL"): ("S4", "sho"),
    ("MC039", "INITIAL"): ("S5", "saiin"),
    ("MC105", "MEDIAL"): ("S6", "kain"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fieldnames = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = read(BASE)
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    rows: list[dict[str, object]] = []
    for row in base:
        key = (row["master_card_id"], row["position_class"])
        if key in MAPPINGS:
            group, surface = MAPPINGS[key]
        else:
            group, surface = "BASE_PROFILE", row["predicted_surface"]
        rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "field_id": row["field_id"],
                "position_class": row["position_class"],
                "master_card_id": row["master_card_id"],
                "portable_value_de": row["portable_value_de"],
                "observed_surface": row["observed_surface"],
                "base_profile_surface": row["predicted_surface"],
                "second_layer_rule": group,
                "expanded_profile_surface": surface,
                "base_match": row["profile_matches"],
                "expanded_match": "YES" if surface == row["observed_surface"] else "NO",
                "surface_registered": "YES" if surface in dictionary[row["master_card_id"]]["registered_surfaces"].split("|") else "NO",
            }
        )
    write(OUT / "HUNDRED_NINETY_FIRST_381_EVENT_EXPANDED_PROFILE.tsv", rows)

    mapping_rows: list[dict[str, object]] = []
    for (card_id, position), (group, surface) in MAPPINGS.items():
        selected = [row for row in rows if row["master_card_id"] == card_id and row["position_class"] == position]
        mapping_rows.append(
            {
                "rule_group": group,
                "master_card_id": card_id,
                "position_class": position,
                "base_surface": selected[0]["base_profile_surface"],
                "expanded_surface": surface,
                "opportunities": len(selected),
                "base_exact": sum(row["base_match"] == "YES" for row in selected),
                "expanded_exact": sum(row["expanded_match"] == "YES" for row in selected),
                "net_gain": sum(row["expanded_match"] == "YES" for row in selected) - sum(row["base_match"] == "YES" for row in selected),
                "observed_distribution": "|".join(f"{key}:{value}" for key, value in sorted(Counter(str(row["observed_surface"]) for row in selected).items())),
            }
        )
    write(OUT / "HUNDRED_NINETY_FIRST_19_POSITIONAL_MAPPINGS.tsv", mapping_rows)

    group_rows: list[dict[str, object]] = []
    for group, (name, rule_de, mapping_count) in GROUPS.items():
        selected = [row for row in rows if row["second_layer_rule"] == group]
        group_rows.append(
            {
                "rule_group": group,
                "rule_name": name,
                "apprentice_rule_de": rule_de,
                "mapping_count": mapping_count,
                "trigger_events": len(selected),
                "base_exact": sum(row["base_match"] == "YES" for row in selected),
                "expanded_exact": sum(row["expanded_match"] == "YES" for row in selected),
                "net_gain": sum(row["expanded_match"] == "YES" for row in selected) - sum(row["base_match"] == "YES" for row in selected),
            }
        )
    write(OUT / "HUNDRED_NINETY_FIRST_6_SECOND_LAYER_RULES.tsv", group_rows)

    residual_groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["expanded_match"] == "NO":
            residual_groups[(str(row["expanded_profile_surface"]), str(row["observed_surface"]), str(row["position_class"]))].append(row)
    residual_rows: list[dict[str, object]] = []
    for rank, ((predicted, observed, position), selected) in enumerate(sorted(residual_groups.items(), key=lambda item: (-len(item[1]), item[0])), 1):
        residual_rows.append(
            {
                "rank": rank,
                "predicted_to_observed": f"{predicted}>{observed}",
                "position_class": position,
                "events": len(selected),
                "cards": "|".join(sorted({str(row["master_card_id"]) for row in selected}, key=lambda value: int(value[2:]))),
                "pages": "|".join(sorted({str(row["page"]) for row in selected})),
                "event_ids": "|".join(str(row["event_id"]) for row in selected),
            }
        )
    write(
        OUT / "HUNDRED_NINETY_FIRST_REMAINING_RESIDUALS.tsv",
        residual_rows,
        ["rank", "predicted_to_observed", "position_class", "events", "cards", "pages", "event_ids"],
    )

    base_exact = sum(row["base_match"] == "YES" for row in rows)
    expanded_exact = sum(row["expanded_match"] == "YES" for row in rows)
    summary = {
        "base_profile_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "events": len(rows),
        "cards": len(dictionary),
        "base_exact": base_exact,
        "expanded_exact": expanded_exact,
        "net_gain": expanded_exact - base_exact,
        "expanded_accuracy": round(expanded_exact / len(rows), 6),
        "second_layer_groups": len(GROUPS),
        "positional_mappings": len(MAPPINGS),
        "trigger_events": sum(row["second_layer_rule"] != "BASE_PROFILE" for row in rows),
        "remaining_residual_events": len(rows) - expanded_exact,
        "remaining_residual_patterns": len(residual_rows),
        "all_surfaces_registered": all(row["surface_registered"] == "YES" for row in rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
