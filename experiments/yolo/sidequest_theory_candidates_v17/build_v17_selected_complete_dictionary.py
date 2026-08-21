#!/usr/bin/env python3
"""Build the selected V17 recurrent deck and propagate it through all V16 rows."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
V16 = HERE.parent / "sidequest_theory_candidates_v16"

# Frozen after all four independent candidates were complete. These are
# contextual source-language expansions, never glyph-by-glyph readings.
SELECTED = {
    "2f1c5e56e8f0ff459065": ("in the stated or usual measure", ".66", "MEASURE_REFERENCE"),
    "dcda95c81a5460feb191": ("with the foregoing preparation", ".67", "PREPARATION_REFERENCE"),
    "b921a237be883a820352": ("this present portion", ".56", "CURRENT_PORTION"),
    "bc4f1f5c006c74a4d26d": ("let it stand until ready; end this instruction", ".48", "SETTLE_READY_CLOSE"),
    "6f7ff8287eddf4da9fdb": ("stir until evenly mixed", ".62", "MIXING_ACTION"),
    "276a7c2d74d1143446f4": ("apply or use this portion", ".61", "APPLICATION_ACTION"),
    "7d25241b0e56c836372a": ("bathe or immerse in the tempered warm liquid; end this instruction", ".52", "TEMPERED_IMMERSION_CLOSE"),
    "dd0ecaf5e27d81befffc": ("at the place indicated by the drawing", ".58", "PICTURE_LOCAL_REFERENCE"),
    "b5fcea1eaed06b2f2291": ("take up the next portion or instruction", ".68", "NEXT_PORTION_HEAD"),
    "7db18b2f0fb7ed0fcfd3": ("rinse the indicated place once; end this instruction", ".50", "LOCAL_RINSE_CLOSE"),
    "de7321bface5628e35d6": ("leave it standing in the lower vessel; end this instruction", ".38", "LOWER_VESSEL_STAND_CLOSE"),
    "0275fbf14e07935b0a45": ("keep it lukewarm", ".46", "LUKEWARM_CONDITION"),
    "1645e612504fcef59ced": ("add one measured portion to the vessel", ".55", "MEASURED_ADDITION"),
    "7a4bb8136330ee4e6e56": ("the prepared decoction or working liquid", ".53", "PREPARED_LIQUID"),
    "e0b630cb1b5df5e7105b": ("when the preparation is ready", ".55", "READINESS_CONDITION"),
    "308e8ea2d5d190c498e8": ("mix the two portions together", ".54", "COMBINE_PORTIONS"),
    "4d4559019a961b834aa1": ("from the same batch", ".40", "SAME_BATCH_REFERENCE"),
    "259b2b3b0bf859882e2c": ("finish this treatment; end this instruction", ".37", "TREATMENT_FINISH_CLOSE"),
    "2cc054357a929df85f64": ("thereafter take the following detail", ".40", "DOSSIER_CONTINUATION"),
    "2cc8bb3c2af19607888f": ("through the connected channels", ".52", "CHANNEL_ROUTE"),
    "b5df9126607030b95175": ("until the liquid runs clear", ".57", "CLARITY_GATE"),
    "28ffbc88b97772a75f1e": ("reserve the mixed liquid; end this instruction", ".39", "RESERVE_MIXTURE_CLOSE"),
    "3b70942557b3a40e8030": ("let the liquid settle; end this instruction", ".52", "SETTLE_LIQUID_CLOSE"),
    "54d0e228ca346110af05": ("for the same interval as before", ".50", "DURATION_REFERENCE"),
    "87411f84689b4f93a303": ("heat it once; end this instruction", ".49", "HEAT_ONCE_CLOSE"),
    "90bcf0a9ec0ef56399e6": ("toward the lower outlet", ".57", "LOWER_OUTLET_DIRECTION"),
    "9ad66e67803a12e745de": ("use the freshly prepared remedy", ".52", "FRESH_PREPARATION"),
    "9da1b6ac2c929daea697": ("one measured portion", ".54", "MEASURED_PORTION"),
    "d68bc8de3bcee09db23c": ("strain it once through cloth; end this instruction", ".54", "CLOTH_STRAIN_CLOSE"),
    "d904bf7b044dd3922781": ("over a gentle heat", ".55", "GENTLE_HEAT"),
}

DECISION_INPUTS = {
    "R1": (HERE / "V17_R1_RECURRENT_CARD_DECISIONS.tsv", "exact_tuple_id", "selected_default"),
    "R2": (HERE / "V17_R2_RECURRENT_CARD_DECISIONS.tsv", "exact_tuple_id", "selected_meaning"),
    "R3": (HERE / "V17_R3_RECURRENT_CARD_DECISIONS.tsv", "exact_tuple_id", "selected_default"),
    "R4": (HERE / "V17_R4_RECURRENT_CARD_DECISIONS.tsv", "tuple_id", "selected_default"),
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, fieldnames: list[str], data: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    candidates: dict[str, dict[str, str]] = {}
    surfaces: dict[str, str] = {}
    events: dict[str, str] = {}
    pages: dict[str, str] = {}
    for role, (path, id_column, meaning_column) in DECISION_INPUTS.items():
        for row in rows(path):
            key = row[id_column]
            candidates.setdefault(key, {})[role] = row[meaning_column]
            surfaces.setdefault(key, row.get("surface_examples") or row.get("surface_forms") or "")
            events.setdefault(key, row["events"])
            pages.setdefault(key, row.get("pages") or row.get("folios") or "")
    assert set(candidates) == set(SELECTED)
    assert all(set(value) == set(DECISION_INPUTS) for value in candidates.values())

    decisions = []
    for key, (meaning, confidence, source_class) in SELECTED.items():
        decisions.append({
            "exact_tuple_id": key,
            "surface_examples": surfaces[key],
            "events": events[key],
            "pages": pages[key],
            "r1_selected": candidates[key]["R1"],
            "r2_selected": candidates[key]["R2"],
            "r3_selected": candidates[key]["R3"],
            "r4_selected": candidates[key]["R4"],
            "v17_selected_default": meaning,
            "confidence": confidence,
            "source_class": source_class,
            "selection_rule": "four-perspective consensus; R4 whole-passage tie-break",
        })
    decision_fields = list(decisions[0])
    write(HERE / "V17_SELECTED_RECURRENT_DECK.tsv", decision_fields, decisions)

    lexicon_path = V16 / "V16_R4_COMPLETE_DEFAULT_LEXICON.tsv"
    lexicon = rows(lexicon_path)
    lex_fields = list(lexicon[0])
    changed_lexicon = 0
    for row in lexicon:
        key = row["lexicon_id"]
        if key in SELECTED and row["scope"] == "PROSE_EXACT_CARD":
            meaning, confidence, source_class = SELECTED[key]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V17 recurrent-deck consensus; use one core expansion across all fixed-page occurrences."
            )
            changed_lexicon += 1
    assert changed_lexicon == 30
    write(HERE / "V17_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", lex_fields, lexicon)

    ledger_path = V16 / "V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv"
    ledger = rows(ledger_path)
    ledger_fields = list(ledger[0])
    changed_events = 0
    for row in ledger:
        key = row["exact_tuple_id"]
        if key in SELECTED and row["ledger_scope"] == "GDT327_PROSE":
            meaning, confidence, source_class = SELECTED[key]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V17 recurrent-deck consensus; picture/rubric supplies omitted arguments."
            )
            changed_events += 1
    assert changed_events == 217
    assert len(ledger) == 776
    assert all(row["default_English"].strip() for row in ledger)
    assert not any(row["page"].startswith("f84") for row in ledger)
    write(HERE / "V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", ledger_fields, ledger)

    print(f"selected_cards={len(SELECTED)} changed_events={changed_events} total_events={len(ledger)}")


if __name__ == "__main__":
    main()
