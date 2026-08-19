#!/usr/bin/env python3
from __future__ import annotations

import csv
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt361_aq_contact_prospective"
OBS = BASE / "artifacts/gdt361_visual_observations.tsv"
VISUAL_FREEZE = BASE / "artifacts/gdt361_visual_freeze.json"
LOCI = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv"
GROUPS = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
ALIGN = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
REVEAL = BASE / "artifacts/gdt361_formal_reveal.tsv"
RESULT = BASE / "artifacts/gdt361_result.json"
TARGETS = [f"f102v2.{i}" for i in range(10, 17)]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def exact_tail(rows: list[dict[str, object]]) -> tuple[float | None, int, int]:
    hard = [r for r in rows if r["visual_state"] in {"CONTACT", "CLEAR_GAP"}]
    c = sum(r["visual_state"] == "CONTACT" for r in hard)
    if not hard or c == 0 or c == len(hard):
        return None, 0, 0
    observed = sum(r["visual_state"] == "CONTACT" and r["aq"] for r in hard)
    worlds = 0
    extreme = 0
    for contact_idx in itertools.combinations(range(len(hard)), c):
        contact = set(contact_idx)
        hit = sum(i in contact and bool(r["aq"]) for i, r in enumerate(hard))
        worlds += 1
        extreme += hit >= observed
    return extreme / worlds, extreme, worlds


def summary(rows: list[dict[str, object]]) -> dict[str, object]:
    hard = [r for r in rows if r["visual_state"] in {"CONTACT", "CLEAR_GAP"}]
    contacts = [r for r in hard if r["visual_state"] == "CONTACT"]
    gaps = [r for r in hard if r["visual_state"] == "CLEAR_GAP"]
    cp = sum(bool(r["aq"]) for r in contacts)
    gp = sum(bool(r["aq"]) for r in gaps)
    effect = cp / len(contacts) - gp / len(gaps) if contacts and gaps else None
    p, extreme, worlds = exact_tail(rows)
    return {
        "rows": len(rows),
        "hard_rows": len(hard),
        "state_counts": dict(sorted(Counter(str(r["visual_state"]) for r in rows).items())),
        "contact_aq": cp,
        "contact_total": len(contacts),
        "gap_aq": gp,
        "gap_total": len(gaps),
        "contact_minus_gap_prevalence": effect,
        "exact_one_sided_p": p,
        "exact_extreme_worlds": extreme,
        "exact_total_worlds": worlds,
    }


def main() -> None:
    observations = read(OBS)
    assert [r["locus"] for r in observations] == TARGETS
    target_set = set(TARGETS)
    loci = list(GuardedTSV(LOCI, selector_column="locus", allowed_values=target_set,
                           forbidden_prefixes=("f84",), forbidden_action="skip"))
    groups = list(GuardedTSV(GROUPS, selector_column="locus", allowed_values=target_set,
                             forbidden_prefixes=("f84",), forbidden_action="skip"))
    align = list(GuardedTSV(ALIGN, selector_column="locus", allowed_values=target_set,
                            forbidden_prefixes=("f84",), forbidden_action="skip"))
    assert {r["locus"] for r in loci} == target_set
    by_locus = {r["locus"]: r for r in loci}
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        by_group[row["locus"]].append(row)
    by_align: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in align:
        by_align[row["locus"]].append(row)

    rows: list[dict[str, object]] = []
    for obs in observations:
        locus = obs["locus"]
        gs = sorted(by_group[locus], key=lambda r: int(r["consensus_group_index"]))
        first = gs[0]["family_surface"]
        edition_first = {}
        for a in by_align[locus]:
            if int(a["source_group_index"]) == 1:
                edition_first[a["edition"]] = a["primary_sta_families"]
        assert set(edition_first) == {"ZL3b", "IT2a", "RF1b"}
        aq = first.startswith("AQ")
        aqa = first.startswith("AQA")
        row: dict[str, object] = {
            "target_id": obs["target_id"], "locus": locus,
            "visual_state": obs["visual_state"],
            "prospective_score_eligible": obs["prospective_score_eligible"] == "1",
            "family_expression": "|".join(g["family_surface"] for g in gs),
            "first_group_family": first,
            "prefix2_aq": aq, "prefix3_aqa": aqa,
            "strict_zero_alternative": by_locus[locus]["strict_zero_alternative"] == "1",
            "alternative_sites": int(by_locus[locus]["alternative_sites"]),
            "zl_first_group_family": edition_first["ZL3b"],
            "it_first_group_family": edition_first["IT2a"],
            "rf_first_group_family": edition_first["RF1b"],
            "family_predicate_all_readings_stable": all(v.startswith("AQ") == aq for v in edition_first.values()),
            "aq": aq,
        }
        rows.append(row)

    fieldnames = [
        "target_id", "locus", "visual_state", "prospective_score_eligible",
        "family_expression", "first_group_family", "prefix2_aq", "prefix3_aqa",
        "strict_zero_alternative", "alternative_sites", "zl_first_group_family",
        "it_first_group_family", "rf_first_group_family", "family_predicate_all_readings_stable",
    ]
    with REVEAL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: r[k] for k in fieldnames} for r in rows)

    primary_rows = [r for r in rows if bool(r["prospective_score_eligible"])]
    primary = summary(primary_rows)
    descriptive = summary(rows)
    effect = primary["contact_minus_gap_prevalence"]
    if primary["hard_rows"] < 2:
        decision = "UNSCORED_VISUAL_CAPACITY"
    elif primary["contact_total"] == 0 or primary["gap_total"] == 0:
        decision = "UNSCORED_ONE_SIDED_ARRAY"
    elif effect is not None and effect > 0:
        decision = "FROZEN_DIRECTION_SUPPORTED_EXPLORATORILY"
    elif effect == 0:
        decision = "FROZEN_DIRECTION_TIED"
    else:
        decision = "FROZEN_DIRECTION_CONTRADICTED"
    alias_identical = all(bool(r["prefix2_aq"]) == bool(r["prefix3_aqa"]) for r in primary_rows)
    result = {
        "schema": "GDT361_RESULT_V1",
        "status": decision,
        "question": "Does frozen first-group AQ enrichment transfer directionally to a new visual contact/gap array?",
        "primary_six_unexposed_loci": primary,
        "descriptive_all_seven_including_preexposed_locus": descriptive,
        "formal": {
            "predicate": "FIRST_GROUP_PREFIX_2:AQ",
            "aqa_alias_identical_on_primary": alias_identical,
            "all_rows_predicate_reading_stable": all(bool(r["family_predicate_all_readings_stable"]) for r in rows),
            "strict_rows": sum(bool(r["strict_zero_alternative"]) for r in rows),
            "alternative_bearing_rows": sum(not bool(r["strict_zero_alternative"]) for r in rows),
        },
        "gdt360_context": {
            "training_panel_contact_aq": 5, "training_panel_contact_total": 8,
            "training_panel_gap_aq": 2, "training_panel_gap_total": 18,
            "postselected": True,
        },
        "access": {
            "six_scored_formal_rows_revealed_only_after_visual_freeze": True,
            "single_ai_visual_observer": True,
            "correct_full_canvas_seen_before_visual_freeze": True,
            "source_surfaces_seen_before_visual_freeze": True,
            "f84_accessed": False,
        },
        "inputs": {
            str(OBS.relative_to(ROOT)): sha256_file(OBS),
            str(VISUAL_FREEZE.relative_to(ROOT)): sha256_file(VISUAL_FREEZE),
            str(LOCI.relative_to(ROOT)): sha256_file(LOCI),
            str(GROUPS.relative_to(ROOT)): sha256_file(GROUPS),
            str(ALIGN.relative_to(ROOT)): sha256_file(ALIGN),
            "experiments/yolo/gdt361_aq_contact_prospective/METHOD.md": sha256_file(BASE / "METHOD.md"),
            "experiments/yolo/gdt361_aq_contact_prospective/CORRECTION.md": sha256_file(BASE / "CORRECTION.md"),
            "experiments/yolo/gdt361_aq_contact_prospective/src/run.py": sha256_file(Path(__file__)),
        },
        "outputs": {str(REVEAL.relative_to(ROOT)): sha256_file(REVEAL)},
        "claim_ceiling": "ONE_NEW_ARRAY_DIRECTIONAL_CONTACT_ASSOCIATION_ONLY_NO_SEMANTIC_OR_TRANSLATION_CLAIM",
    }
    RESULT.write_bytes(canonical_json_bytes(result))
    print(json.dumps({"status": decision, "primary": primary, "alias": alias_identical}, indent=2))


if __name__ == "__main__":
    main()
