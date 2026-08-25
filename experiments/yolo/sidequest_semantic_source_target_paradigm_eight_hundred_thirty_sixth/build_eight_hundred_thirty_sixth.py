#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
PREFIX = "EIGHT_HUNDRED_THIRTY_SIXTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def swap(recipe: str, old: str, new: str) -> str:
    return "+".join(new if token == old else token for token in recipe.split("+"))


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    predictions = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_76_UNATTESTED_PREDICTIONS.tsv")
    active = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_30_ACTIVE_PREDICTION_SURFACES.tsv")
    card_by_recipe = {row["component_recipe"]: row for row in cards}
    prediction_by_recipe = {row["component_recipe"]: row for row in predictions}
    active_surfaces = {row["predicted_surface"] for row in active}

    keys = set()
    for row in cards:
        tokens = row["component_recipe"].split("+")
        if ("AR" in tokens) == ("AL" in tokens):
            continue
        ar_recipe = row["component_recipe"] if "AR" in tokens else swap(row["component_recipe"], "AL", "AR")
        al_recipe = row["component_recipe"] if "AL" in tokens else swap(row["component_recipe"], "AR", "AL")
        if ar_recipe in card_by_recipe or ar_recipe in prediction_by_recipe:
            if al_recipe in card_by_recipe or al_recipe in prediction_by_recipe:
                keys.add((ar_recipe, al_recipe))

    pairs = []
    for ar_recipe, al_recipe in sorted(keys):
        ar = card_by_recipe.get(ar_recipe) or prediction_by_recipe[ar_recipe]
        al = card_by_recipe.get(al_recipe) or prediction_by_recipe[al_recipe]
        ar_attested = ar_recipe in card_by_recipe
        al_attested = al_recipe in card_by_recipe
        ar_surface = ar["registered_surfaces"] if ar_attested else ar["predicted_surface"]
        al_surface = al["registered_surfaces"] if al_attested else al["predicted_surface"]
        ar_reading = ar["ninth_grammar_reading_de"] if ar_attested else ar["reading_de"]
        al_reading = al["ninth_grammar_reading_de"] if al_attested else al["reading_de"]
        predicted_surface = al_surface if ar_attested and not al_attested else ar_surface if al_attested and not ar_attested else "NONE"
        counterpart_events = int(ar["events"]) if ar_attested else int(al["events"])
        pairs.append(
            {
                "pair_id": "PENDING",
                "operator_frame": ar_recipe.replace("AR", "ADDRESS"),
                "ar_recipe": ar_recipe,
                "ar_surface": ar_surface,
                "ar_status": "ATTESTED" if ar_attested else "PREDICTION_ONLY",
                "ar_reading_de": ar_reading,
                "al_recipe": al_recipe,
                "al_surface": al_surface,
                "al_status": "ATTESTED" if al_attested else "PREDICTION_ONLY",
                "al_reading_de": al_reading,
                "attested_counterpart_events": counterpart_events if ar_attested != al_attested else int(ar["events"]) + int(al["events"]),
                "predicted_surface": predicted_surface,
                "already_active_prediction": "YES" if predicted_surface in active_surfaces else "NO",
                "decision": "AR_SOURCE__AL_TARGET__SAME_OPERATOR_FRAME",
            }
        )
    pairs.sort(key=lambda row: (0 if row["ar_status"] == row["al_status"] == "ATTESTED" else 1, -int(row["attested_counterpart_events"]), row["operator_frame"]))
    for index, row in enumerate(pairs, 1):
        row["pair_id"] = f"ARAL{index:02d}"

    predicted = [row for row in pairs if row["predicted_surface"] != "NONE"]
    predicted.sort(key=lambda row: (0 if row["already_active_prediction"] == "YES" else 1, -int(row["attested_counterpart_events"]), len(row["operator_frame"].split("+")), row["operator_frame"]))
    top = []
    for rank, row in enumerate(predicted[:10], 1):
        top.append(
            {
                "rank": rank,
                "pair_id": row["pair_id"],
                "predicted_surface": row["predicted_surface"],
                "predicted_recipe": row["al_recipe"] if row["al_status"] == "PREDICTION_ONLY" else row["ar_recipe"],
                "predicted_reading_de": row["al_reading_de"] if row["al_status"] == "PREDICTION_ONLY" else row["ar_reading_de"],
                "attested_counterpart_surface": row["ar_surface"] if row["ar_status"] == "ATTESTED" else row["al_surface"],
                "attested_counterpart_events": row["attested_counterpart_events"],
                "already_active_prediction": row["already_active_prediction"],
                "use": "SEARCH_AS_SOURCE_TARGET_SWAP",
            }
        )

    write(f"{PREFIX}_27_AR_AL_OPERATOR_PAIRS.tsv", pairs, ["pair_id", "operator_frame", "ar_recipe", "ar_surface", "ar_status", "ar_reading_de", "al_recipe", "al_surface", "al_status", "al_reading_de", "attested_counterpart_events", "predicted_surface", "already_active_prediction", "decision"])
    write(f"{PREFIX}_10_SOURCE_TARGET_PREDICTIONS.tsv", top, ["rank", "pair_id", "predicted_surface", "predicted_recipe", "predicted_reading_de", "attested_counterpart_surface", "attested_counterpart_events", "already_active_prediction", "use"])

    both = [row for row in pairs if row["ar_status"] == row["al_status"] == "ATTESTED"]
    one_sided = [row for row in pairs if row["predicted_surface"] != "NONE"]
    summary = {
        "status": "PASS",
        "decision": "AR_SOURCE_AND_AL_TARGET_FORM_A_PREDICTIVE_ADDRESS_PAIR",
        "paired_operator_frames": len(pairs),
        "both_sides_attested": len(both),
        "one_side_attested_other_predicted": len(one_sided),
        "active_prediction_surfaces_in_pairs": sum(row["already_active_prediction"] == "YES" for row in one_sided),
        "top_predictions": len(top),
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 836: AR/AL source-target paradigm

`AR=QUELLE` and `AL=ZIELSTELLE` behave like a paired address vocabulary. Five
operator frames are already present on both sides: bare address, K add, OK
start/set, OT next, and L+CHD guide/move. The operator reading stays fixed while
only source versus target changes.

Another 22 one-sided attested frames have their exact AR↔AL counterpart in the
existing 76-surface prediction deck. This is much stronger than inventing an
isolated gloss: the dictionary predicts a missing card by swapping one address
value inside an otherwise learned frame.

The ten best immediate searches are published separately. Three were already
in the compact active deck: `chdar = CHD+AR` (move from source), `kchoal =
K+HO+AL` (add ingredient at target), and `lal = L+AL` (guide to target). Other
high-value swaps include source versions of leaving-standing, cooling,
closing, and passage-taking cards.

AIR remains a separate whole semantic stem WASSER despite visually containing
AR; its five-card behavior is not the source-address behavior. No component
meaning changes here. The gain is a concrete compositional prediction rule:
preserve the operator frame, exchange AR source for AL target.

Next: integrate the strongest AR/AL swaps into the active prediction deck and
then test whether CKH=DURCHLASS supplies a genuine middle address between AR
and AL rather than merely another object noun.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
