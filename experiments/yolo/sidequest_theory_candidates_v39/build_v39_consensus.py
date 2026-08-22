#!/usr/bin/env python3
"""Build the V39 four-role consensus and validate the selected teaching line."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CORE = ROOT / "experiments/yolo/sidequest_theory_candidates_v38/V38_SHARED_WORKSHOP_CORE.tsv"

SELECTED = [
    ("daiin", "ein vorgeschriebenes Maß", "PARAMETER", "R1/R2/R3/R4 consensus"),
    ("chol", "mit der vorigen Zubereitung weiter", "BACK_REFERENCE", "R1/R2/R3/R4 consensus"),
    ("dy", "diese aktive Portion", "CURRENT_ITEM", "medical concrete value over generic current-unit rival"),
    ("dal", "an die bezeichnete Zielstelle führen", "DESTINATION", "all four roles remove independent APPLY meaning"),
    ("oky", "die aktive Portion verwenden", "EXECUTE_USE", "shared action separated from DAL destination"),
    ("chor", "die bereitete Arbeitsflüssigkeit", "WORKING_MATERIAL", "medical concrete value with generic material rival"),
    ("cthy", "sobald die Zubereitung gebrauchsfertig ist", "READINESS_GATE", "medical realization of shared state gate"),
    ("char", "daraus, aus demselben Ansatz", "SAME_SOURCE", "replaces modern-sounding separate charge"),
    ("shey", "bis die Flüssigkeit klar abläuft", "VISIBLE_THRESHOLD", "strongest R2 medical card; generic pass-gate rival retained"),
    ("cholor", "aus dem vorigen Ansatz entnehmen", "PRIOR_SOURCE_WITHDRAWAL", "weakest card but all roles retain explicit prior-source value"),
    ("chty", "gleichmäßig bearbeiten", "PROCESS_TO_UNIFORMITY", "broadens narrow homogenize/mix"),
    ("otchey", "nimm den bezeichneten Anteil", "TAKE_SELECTED_PART", "three roles remove unsupported FINAL value"),
]

FIELDS = [
    ["otchey", "daiin"],
    ["chol", "chor", "char", "chty", "shey"],
    ["cholor", "dy", "cthy", "oky", "dal"],
]


def wanted_position(i: int, n: int) -> str:
    return "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MIDDLE"


def main() -> None:
    core = list(csv.DictReader(CORE.open(encoding="utf-8"), delimiter="\t"))
    by_surface = {r["surface"]: r for r in core}
    assert set(by_surface) == {x[0] for x in SELECTED}

    rows = []
    for surface, meaning, role, reason in SELECTED:
        src = by_surface[surface]
        rows.append({
            "surface": surface,
            "exact_tuple_id": src["exact_tuple_id"],
            "selected_concrete_default_German": meaning,
            "anonymous_workshop_role": role,
            "events": src["events"],
            "hand_1_events": src["hand_1_events"],
            "hand_2_events": src["hand_2_events"],
            "selection_reason": reason,
            "meaning_status": "CREATIVE_V39_DEFAULT_NOT_DECIPHERMENT",
        })
    out = HERE / "V39_SELECTED_SHARED_CARD_LEXICON.tsv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    sequence = []
    for field_no, field in enumerate(FIELDS, 1):
        for i, surface in enumerate(field):
            src = by_surface[surface]
            positions = {part.split(":")[0]: int(part.split(":")[1]) for part in src["positions"].split(";")}
            pos = wanted_position(i, len(field))
            meaning = next(x[1] for x in SELECTED if x[0] == surface)
            sequence.append({
                "field_no": field_no,
                "card_no": i + 1,
                "surface": surface,
                "selected_concrete_default_German": meaning,
                "desired_position": pos,
                "observed_position_support": positions.get(pos, 0),
                "position_attested": str(positions.get(pos, 0) > 0).upper(),
            })
    seq = HERE / "V39_SELECTED_TEACHING_SENTENCE.tsv"
    with seq.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(sequence[0]), lineterminator="\n")
        w.writeheader(); w.writerows(sequence)

    candidate_files = [
        "V39_R1_SHARED_CARD_LEXICON.tsv", "V39_R2_MEDICAL_CARD_REVIEW.tsv",
        "R3_COMMON_CARD_REVISION.tsv", "V39_R4_CORRECTOR_CORE.tsv",
    ]
    candidate_counts = {}
    for name in candidate_files:
        candidate_counts[name] = sum(1 for _ in csv.DictReader((HERE / name).open(encoding="utf-8"), delimiter="\t"))
    assert all(n == 12 for n in candidate_counts.values())
    summary = {
        "schema": "SIDEQUEST_V39_FOUR_ROLE_CONSENSUS_V1",
        "status": "GENERIC_REFERENCE_GRAMMAR_WITH_CONCRETE_MEDICAL_DEFAULTS_SELECTED",
        "candidate_roles": 4,
        "candidate_card_counts": candidate_counts,
        "selected_cards": len(rows),
        "selected_sentence_cards": len(sequence),
        "all_cards_cross_hand": all(int(r["hand_1_events"]) > 0 and int(r["hand_2_events"]) > 0 for r in rows),
        "all_sentence_positions_attested": all(r["position_attested"] == "TRUE" for r in sequence),
        "new_tuple_ids_created": 0,
        "new_surface_forms_created": 0,
        "f84_rows_accessed": 0,
        "f84r_rows_accessed": 0,
    }
    (HERE / "V39_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
