#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def read_events() -> list[dict[str, str]]:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read_events()
    by_id = {row["event_id"]: row for row in events}

    comparison_spec = {
        "E161": {
            "owner": "B1_SHARED_TWO_ROW_POOL",
            "before": "Empfangsgefäß > einreiben",
            "after": "länger auffangen; Schluss",
            "local_expansion": "bis zum vorgeschriebenen Empfangsstand",
            "complete_reading": "Empfangsgefäß vorbereiten, den laufenden Posten einreiben, bis zum Sollstand auffangen und den Schritt schließen.",
        },
        "E309": {
            "owner": "B3_MAIN_ARCH_LINKED_PAIR",
            "before": "Aussagebeginn",
            "after": "bereit > bearbeiten > Folgemaß > untere Stelle > absetzen; Schluss",
            "local_expansion": "auf den vorgeschriebenen Arbeitsstand einstellen",
            "complete_reading": "Auf Sollstand einstellen, freigeben, bearbeiten, das Folgemaß an der unteren Stelle einsetzen, absetzen lassen und schließen.",
        },
    }
    comparison = []
    for event_id, spec in comparison_spec.items():
        row = by_id[event_id]
        comparison.append({
            "event_id": event_id,
            "record": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface_display"],
            "joint_tuple_id": row["joint_tuple_id"],
            "visible_owner": spec["owner"],
            "preceding_cards": spec["before"],
            "following_cards": spec["after"],
            "shared_small_value_de": "Sollstand",
            "local_expansion_de": spec["local_expansion"],
            "complete_statement_de": spec["complete_reading"],
        })
    write("FOUR_HUNDRED_ELEVENTH_TWO_BARE_IIN_ROUTINES.tsv", comparison)

    models = [
        {"candidate": "FÜLLHÖHE", "B1_fit": 4, "B3_fit": 1, "H2_fit": 1, "B5_fit": 2, "total": 8, "decision": "REJECT_TOO_LIQUID_SPECIFIC"},
        {"candidate": "KONSISTENZ", "B1_fit": 1, "B3_fit": 3, "H2_fit": 4, "B5_fit": 1, "total": 9, "decision": "REJECT_CANNOT_NAME_OPENING_POSITION"},
        {"candidate": "FREIGABESTUFE", "B1_fit": 2, "B3_fit": 4, "H2_fit": 2, "B5_fit": 2, "total": 10, "decision": "REJECT_DUPLICATES_CTH_READY_GATE"},
        {"candidate": "SOLLSTAND", "B1_fit": 4, "B3_fit": 4, "H2_fit": 4, "B5_fit": 4, "total": 16, "decision": "SELECT"},
    ]
    write("FOUR_HUNDRED_ELEVENTH_FOUR_IIN_MODELS.tsv", models)

    family_spec = {
        "E036": ("K+IIN", "weicher Sollstand", "K specifies the kind of required state"),
        "E161": ("IIN", "Sollstand", "receiver reaches its prescribed local stand"),
        "E309": ("IIN", "Sollstand", "working charge reaches its prescribed local stand"),
        "E371": ("DA+IIN", "zweite Öffnungsstellung", "DA specifies the opening whose setting is selected"),
    }
    family = []
    for event_id, (composition, value, note) in family_spec.items():
        row = by_id[event_id]
        family.append({
            "event_id": event_id,
            "record": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface_display"],
            "composition": composition,
            "iin_invariant_de": "Sollstand",
            "selected_card_value_de": value,
            "composition_note": note,
        })
    write("FOUR_HUNDRED_ELEVENTH_FOUR_IIN_FAMILY_MEMBERS.tsv", family)

    statements = [
        {
            "statement_id": "B1-S018",
            "owner": "gemeinsames zweireihiges Becken-/Figurenfeld",
            "exact_sequence": "LY > DSHEOL > IIN > SOLK+EE+DY",
            "card_reading_de": "Empfangsgefäß > einreiben > Sollstand > länger auffangen; Schluss",
            "continuous_reading_de": comparison_spec["E161"]["complete_reading"],
            "strongest_rival": "IIN=Füllhöhe",
            "why_rival_loses": "would not transfer to B3 before ready/work/settle",
        },
        {
            "statement_id": "B3-S034",
            "owner": "sichtbar gekoppeltes Paar unter ungerichtetem Bogen",
            "exact_sequence": "IIN > CTH > CH > OT+AIIN > OLS+AL+Y > SHED+E+DY",
            "card_reading_de": "Sollstand > bereit > bearbeiten > Folgemaß > untere Stelle > absetzen; Schluss",
            "continuous_reading_de": comparison_spec["E309"]["complete_reading"],
            "strongest_rival": "IIN=Konsistenz",
            "why_rival_loses": "would not transfer to B1 receiver level or B5 opening setting",
        },
    ]
    write("FOUR_HUNDRED_ELEVENTH_TWO_REWRITTEN_STATEMENTS.tsv", statements)

    summary = {
        "status": "PASS",
        "bare_iin_occurrences": len(comparison),
        "iin_family_occurrences": len(family),
        "models_compared": len(models),
        "rewritten_statements": len(statements),
        "decision": "IIN_REQUIRED_WORKING_SETPOINT_OR_STAND",
        "small_value_de": "SOLLSTAND",
    }
    (HERE / "FOUR_HUNDRED_ELEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
