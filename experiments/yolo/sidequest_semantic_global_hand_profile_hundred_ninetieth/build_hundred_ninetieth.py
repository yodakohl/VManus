#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


RULE_META = {
    "R1": ("Q_ACTIVE_FRAME", "Aktive OK/OT-Karten erhalten in der gelehrten Anfangs- oder Mittelstellung q-Rahmen."),
    "R2": ("D_MEASURE_POSITION", "AIIN erscheint medial oder final als daiin."),
    "R3": ("BARE_TARGET_MEDIAL", "Die AL-Zielkarte erscheint medial als nacktes al."),
    "R4": ("BOUNDARY_FRAME_REDUCTION", "CHOR am Feldanfang und CHEOL am Feldende verlieren ihren ch/che-Rahmen."),
    "R5": ("S_FINAL_CLOSE", "Die beiden gelehrten CHEDY-Schlussfamilien verwenden feldfinal ihre s-Form."),
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


def position_class(position: int, size: int) -> str:
    if size == 1:
        return "ONLY"
    if position == 1:
        return "INITIAL"
    if position == size:
        return "FINAL"
    return "MEDIAL"


def apply_profile(card_id: str, canonical: str, position: str) -> tuple[str, str]:
    q_forms = {
        "MC007": "qokey",
        "MC013": "qotchor",
        "MC093": "qotal",
        "MC120": "qokaiin",
        "MC002": "qokeey",
    }
    if card_id in {"MC007", "MC093", "MC120", "MC002"} and position == "MEDIAL":
        return "R1", q_forms[card_id]
    if card_id == "MC013" and position == "INITIAL":
        return "R1", q_forms[card_id]
    if card_id == "MC039" and position in {"MEDIAL", "FINAL"}:
        return "R2", "daiin"
    if card_id == "MC154" and position == "MEDIAL":
        return "R3", "al"
    if card_id == "MC080" and position == "INITIAL":
        return "R4", "or"
    if card_id == "MC153" and position == "FINAL":
        return "R4", "ol"
    if card_id == "MC025" and position == "FINAL":
        return "R5", "schedy"
    if card_id == "MC128" and position == "FINAL":
        return "R5", "shedy"
    return "DEFAULT_KEEP", canonical


def main() -> None:
    events = read(EVENTS)
    dictionary_rows = read(DICTIONARY)
    dictionary = {row["master_card_id"]: row for row in dictionary_rows}
    field_sizes = Counter(row["field_id"] for row in events)

    predictions: list[dict[str, object]] = []
    for row in events:
        card_id = row["master_card_id"]
        canonical = dictionary[card_id]["master_form"]
        pos = position_class(int(row["field_position"]), field_sizes[row["field_id"]])
        rule, predicted = apply_profile(card_id, canonical, pos)
        actual = row["surface"]
        predictions.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "field_id": row["field_id"],
                "field_position": row["field_position"],
                "field_size": field_sizes[row["field_id"]],
                "position_class": pos,
                "master_card_id": card_id,
                "portable_value_de": dictionary[card_id]["portable_card_value_de"],
                "canonical_surface": canonical,
                "observed_surface": actual,
                "rule_applied": rule,
                "predicted_surface": predicted,
                "canonical_matches": "YES" if canonical == actual else "NO",
                "profile_matches": "YES" if predicted == actual else "NO",
                "predicted_surface_registered": "YES" if predicted in dictionary[card_id]["registered_surfaces"].split("|") else "NO",
            }
        )
    write(OUT / "HUNDRED_NINETIETH_381_EVENT_GLOBAL_PROFILE.tsv", predictions)

    rule_rows: list[dict[str, object]] = []
    for rule_id, (name, text) in RULE_META.items():
        rows = [row for row in predictions if row["rule_applied"] == rule_id]
        rule_rows.append(
            {
                "rule_id": rule_id,
                "rule_name": name,
                "apprentice_rule_de": text,
                "global_triggers": len(rows),
                "correct_predictions": sum(row["profile_matches"] == "YES" for row in rows),
                "incorrect_predictions": sum(row["profile_matches"] == "NO" for row in rows),
                "baseline_matches_on_triggers": sum(row["canonical_matches"] == "YES" for row in rows),
                "net_exact_match_change": sum(row["profile_matches"] == "YES" for row in rows) - sum(row["canonical_matches"] == "YES" for row in rows),
                "cards": "|".join(sorted({str(row["master_card_id"]) for row in rows}, key=lambda value: int(value[2:]))),
            }
        )
    write(OUT / "HUNDRED_NINETIETH_5_RULE_GLOBAL_AUDIT.tsv", rule_rows)

    card_rows: list[dict[str, object]] = []
    for card in dictionary_rows:
        card_id = card["master_card_id"]
        rows = [row for row in predictions if row["master_card_id"] == card_id]
        card_rows.append(
            {
                "master_card_id": card_id,
                "master_form": card["master_form"],
                "registered_surfaces": card["registered_surfaces"],
                "event_count": len(rows),
                "observed_surfaces": "|".join(sorted({str(row["observed_surface"]) for row in rows})),
                "canonical_exact": sum(row["canonical_matches"] == "YES" for row in rows),
                "five_rule_exact": sum(row["profile_matches"] == "YES" for row in rows),
                "net_exact_match_change": sum(row["profile_matches"] == "YES" for row in rows) - sum(row["canonical_matches"] == "YES" for row in rows),
                "triggered_rules": "|".join(sorted({str(row["rule_applied"]) for row in rows if row["rule_applied"] != "DEFAULT_KEEP"})) or "NONE",
                "residual_events": sum(row["profile_matches"] == "NO" for row in rows),
            }
        )
    write(OUT / "HUNDRED_NINETIETH_173_CARD_ACCURACY.tsv", card_rows)

    residual_groups: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in predictions:
        if row["profile_matches"] == "NO":
            key = (
                str(row["canonical_surface"]),
                str(row["observed_surface"]),
                str(row["position_class"]),
                str(row["rule_applied"]),
            )
            residual_groups[key].append(row)
    residual_rows: list[dict[str, object]] = []
    ordered = sorted(residual_groups.items(), key=lambda item: (-len(item[1]), item[0]))
    for index, ((canonical, observed, pos, rule), rows) in enumerate(ordered, 1):
        residual_rows.append(
            {
                "residual_rank": index,
                "canonical_to_observed": f"{canonical}>{observed}",
                "canonical_surface": canonical,
                "observed_surface": observed,
                "position_class": pos,
                "rule_applied": rule,
                "event_count": len(rows),
                "card_count": len({row["master_card_id"] for row in rows}),
                "cards": "|".join(sorted({str(row["master_card_id"]) for row in rows}, key=lambda value: int(value[2:]))),
                "pages": "|".join(sorted({str(row["page"]) for row in rows})),
                "events": "|".join(str(row["event_id"]) for row in rows),
            }
        )
    write(
        OUT / "HUNDRED_NINETIETH_RESIDUAL_TRANSFORMATIONS.tsv",
        residual_rows,
        ["residual_rank", "canonical_to_observed", "canonical_surface", "observed_surface", "position_class", "rule_applied", "event_count", "card_count", "cards", "pages", "events"],
    )

    baseline_exact = sum(row["canonical_matches"] == "YES" for row in predictions)
    profile_exact = sum(row["profile_matches"] == "YES" for row in predictions)
    triggers = sum(row["rule_applied"] != "DEFAULT_KEEP" for row in predictions)
    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "events": len(predictions),
        "fields": len(field_sizes),
        "cards": len(dictionary_rows),
        "canonical_exact": baseline_exact,
        "canonical_accuracy": round(baseline_exact / len(predictions), 6),
        "five_rule_triggers": triggers,
        "five_rule_exact": profile_exact,
        "five_rule_accuracy": round(profile_exact / len(predictions), 6),
        "net_exact_match_change": profile_exact - baseline_exact,
        "remaining_residual_events": len(predictions) - profile_exact,
        "remaining_residual_patterns": len(residual_rows),
        "all_predictions_registered": all(row["predicted_surface_registered"] == "YES" for row in predictions),
        "pages": sorted({row["page"] for row in events}),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
