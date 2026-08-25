#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
WATER = ROOT / "sidequest_semantic_water_paradigm_eight_hundred_thirty_fifth"
PAIR = ROOT / "sidequest_semantic_source_target_paradigm_eight_hundred_thirty_sixth"
PREFIX = "EIGHT_HUNDRED_THIRTY_SEVENTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def components(row: dict[str, str]) -> list[str]:
    return [token for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")]


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    statements = read(WATER / "EIGHT_HUNDRED_THIRTY_FIFTH_116_WATER_ALIGNED_STATEMENTS.tsv")
    active_old = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_30_ACTIVE_PREDICTION_SURFACES.tsv")
    pair_top = read(PAIR / "EIGHT_HUNDRED_THIRTY_SIXTH_10_SOURCE_TARGET_PREDICTIONS.tsv")
    cards_by_id = {row["exact_card_id"]: row for row in cards}

    promoted = ["chdar", "lal", "kchoal"]
    active_sorted = sorted(active_old, key=lambda row: (promoted.index(row["predicted_surface"]) if row["predicted_surface"] in promoted else 100 + int(row["recipe_rank"]), row["predicted_surface"]))
    active = []
    for rank, row in enumerate(active_sorted, 1):
        item = dict(row)
        item["address_path_rank"] = str(rank)
        item["address_path_status"] = "PROMOTED_AR_AL_SWAP" if row["predicted_surface"] in promoted else "RETAINED_COMPACT_DECK"
        if row["predicted_surface"] in promoted:
            item["selection_reason"] = "paired AR/AL operator frame: " + item["selection_reason"]
        active.append(item)

    ckh_events = []
    ckh_card_ids = set()
    for event in events:
        if "CKH" not in event["component_recipe"].split("+"):
            continue
        ckh_card_ids.add(event["exact_card_id"])
        ckh_events.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "reading_de": event["ninth_grammar_reading_de"],
                "has_ar_source": "YES" if "AR" in event["component_recipe"].split("+") else "NO",
                "has_al_target": "YES" if "AL" in event["component_recipe"].split("+") else "NO",
                "path_role": "PASSAGE_OBJECT_BETWEEN_SOURCE_AND_TARGET",
            }
        )
    ckh_cards = []
    for card_id in sorted(ckh_card_ids):
        card = cards_by_id[card_id]
        ckh_cards.append(
            {
                "exact_card_id": card_id,
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "reading_de": card["ninth_grammar_reading_de"],
                "events": card["events"],
                "ckh_value": "DURCHLASS",
                "decision": "KEEP_AS_PATH_NOT_THIRD_ADDRESS_ENDPOINT",
            }
        )

    ckh_statements = []
    for row in statements:
        tokens = components(row)
        if "CKH" not in tokens:
            continue
        ckh_statements.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "ar_count": tokens.count("AR"),
                "ckh_count": tokens.count("CKH"),
                "al_count": tokens.count("AL"),
                "address_pattern": ("SOURCE+" if "AR" in tokens else "") + "PATH" + ("+TARGET" if "AL" in tokens else ""),
                "component_sequence": row["component_sequence"],
                "working_reading_de": row["working_reading_de"],
            }
        )

    next_path_predictions = []
    for row in pair_top:
        if "CKH" not in row["predicted_recipe"].split("+"):
            continue
        next_path_predictions.append(row)
    if not next_path_predictions:
        prediction_rows = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_76_UNATTESTED_PREDICTIONS.tsv")
        wanted = {"CH+CKH+AR", "SH+E+CKH+AR"}
        for row in prediction_rows:
            if row["component_recipe"] in wanted:
                next_path_predictions.append(
                    {
                        "rank": str(len(next_path_predictions) + 1),
                        "pair_id": "ARAL_PATH",
                        "predicted_surface": row["predicted_surface"],
                        "predicted_recipe": row["component_recipe"],
                        "predicted_reading_de": row["reading_de"],
                        "attested_counterpart_surface": "chckhal" if row["component_recipe"] == "CH+CKH+AR" else "sheckhal",
                        "attested_counterpart_events": "1",
                        "already_active_prediction": "NO",
                        "use": "SEARCH_AS_SOURCE_PATH_COUNTERPART",
                    }
                )

    write(f"{PREFIX}_30_REBALANCED_ACTIVE_SURFACES.tsv", active, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition", "recipe_rank", "selection_reason", "address_path_rank", "address_path_status"])
    write(f"{PREFIX}_9_CKH_CARDS.tsv", ckh_cards, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "ckh_value", "decision"])
    write(f"{PREFIX}_14_CKH_EVENTS.tsv", ckh_events, ["event_id", "page", "record", "statement_id", "surface", "component_recipe", "reading_de", "has_ar_source", "has_al_target", "path_role"])
    write(f"{PREFIX}_12_CKH_STATEMENTS.tsv", ckh_statements, ["statement_id", "page", "record", "ar_count", "ckh_count", "al_count", "address_pattern", "component_sequence", "working_reading_de"])
    write(f"{PREFIX}_2_SOURCE_PATH_PREDICTIONS.tsv", next_path_predictions, ["rank", "pair_id", "predicted_surface", "predicted_recipe", "predicted_reading_de", "attested_counterpart_surface", "attested_counterpart_events", "already_active_prediction", "use"])

    summary = {
        "status": "PASS",
        "decision": "CKH_IS_PASSAGE_BETWEEN_AR_SOURCE_AND_AL_TARGET",
        "active_prediction_surfaces": len(active),
        "active_prediction_recipes": len({row["component_recipe"] for row in active}),
        "promoted_address_surfaces": sum(row["address_path_status"] == "PROMOTED_AR_AL_SWAP" for row in active),
        "ckh_cards": len(ckh_cards),
        "ckh_events": len(ckh_events),
        "ckh_statements": len(ckh_statements),
        "ckh_statements_with_al": sum(int(row["al_count"]) > 0 for row in ckh_statements),
        "ckh_statements_with_ar_and_al": sum(int(row["ar_count"]) > 0 and int(row["al_count"]) > 0 for row in ckh_statements),
        "source_path_predictions": len(next_path_predictions),
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 837: address-path deck

The compact 24-recipe / 30-surface prediction deck is preserved, but its first
three searches are now the best AR/AL swaps: `chdar`, `lal`, and `kchoal`.
Nothing is added merely to make the deck larger.

CKH remains `DURCHLASS`. Nine exact cards produce 14 events in 12 statements.
Six of those statements also name an AL target, while the strongest long
statement B1-S002 contains AR source, CKH passage, and AL target together. CKH
therefore is not a third endpoint interchangeable with AR/AL; it is the route
object through which the current item is held, led, or taken.

The most useful next missing cells are the source counterparts of two attested
target-path cards: `chckhar = CH+CKH+AR` (“take through the passage from the
source”) and `sheckhar = SH+E+CKH+AR` (“hold briefly at the passage from the
source”). These remain predictions, not translated occurrences.

No dictionary value changes. The current local address grammar is now:

> AR source → CKH passage → AL target.

Next, pressure-test the quantity system in the same paired way: AIN portion,
AIIN prescribed measure, and IIN stage must combine predictably with the same
operators rather than merely decorate memorized cards.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
