#!/usr/bin/env python3
from __future__ import annotations

import csv
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"
ART = BASE / "artifacts"
OBS = ART / "gdt362_visual_observations.tsv"
VISUAL_FREEZE = ART / "gdt362_visual_freeze.json"
LOCI = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv"
GROUPS = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
ALIGN = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
CROSSWALK = ROOT / "experiments/semantic_assumptions/results/existing_human_current_locus_crosswalk.tsv"
REVEAL = ART / "gdt362_formal_reveal.tsv"
RESULT = ART / "gdt362_result.json"
TARGETS = [f"f101v2.{i}" for i in range(10, 19)]
FORMAL_TARGETS = [f"f101v.{i}" for i in range(10, 19)]
FORMAL_FOR_VISUAL = dict(zip(TARGETS, FORMAL_TARGETS))


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    hard = [r for r in rows if r["visual_state"] in {"CONTACT", "CLEAR_GAP"}]
    contact = [r for r in hard if r["visual_state"] == "CONTACT"]
    gap = [r for r in hard if r["visual_state"] == "CLEAR_GAP"]
    cp = sum(bool(r["aq"]) for r in contact)
    gp = sum(bool(r["aq"]) for r in gap)
    effect = cp / len(contact) - gp / len(gap) if contact and gap else None
    worlds = extreme = 0
    if contact and gap:
        for idx in itertools.combinations(range(len(hard)), len(contact)):
            chosen = set(idx)
            hit = sum(i in chosen and bool(r["aq"]) for i, r in enumerate(hard))
            worlds += 1
            extreme += hit >= cp
    return {
        "rows": len(rows), "hard_rows": len(hard),
        "state_counts": dict(sorted(Counter(str(r["visual_state"]) for r in rows).items())),
        "contact_aq": cp, "contact_total": len(contact),
        "gap_aq": gp, "gap_total": len(gap),
        "contact_minus_gap_prevalence": effect,
        "exact_one_sided_p": extreme / worlds if worlds else None,
        "exact_extreme_worlds": extreme, "exact_total_worlds": worlds,
    }


def main() -> None:
    obs = read(OBS)
    assert [r["locus"] for r in obs] == TARGETS
    target_set = set(FORMAL_TARGETS)
    crosswalk = list(GuardedTSV(CROSSWALK, selector_column="source_page", allowed_values={"f101v2", "f101v1"},
                                forbidden_prefixes=("f84",), forbidden_action="skip"))
    assert target_set <= {r["current_locus"] for r in crosswalk}
    loci = list(GuardedTSV(LOCI, selector_column="locus", allowed_values=target_set,
                           forbidden_prefixes=("f84",), forbidden_action="skip"))
    groups = list(GuardedTSV(GROUPS, selector_column="locus", allowed_values=target_set,
                             forbidden_prefixes=("f84",), forbidden_action="skip"))
    align = list(GuardedTSV(ALIGN, selector_column="locus", allowed_values=target_set,
                            forbidden_prefixes=("f84",), forbidden_action="skip"))
    # Two loci have no exact all-reading family consensus, but their
    # first-group AQ predicate remains observable in all three readings.
    assert {r["locus"] for r in loci} == target_set - {"f101v.13", "f101v.14"}
    locus_row = {r["locus"]: r for r in loci}
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_align: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in groups: by_group[r["locus"]].append(r)
    for r in align: by_align[r["locus"]].append(r)

    rows: list[dict[str, object]] = []
    for o in obs:
        locus = o["locus"]
        formal_locus = FORMAL_FOR_VISUAL[locus]
        gs = sorted(by_group[formal_locus], key=lambda r: int(r["consensus_group_index"]))
        ed = {r["edition"]: r["primary_sta_families"] for r in by_align[formal_locus]
              if int(r["source_group_index"]) == 1}
        assert set(ed) == {"ZL3b", "IT2a", "RF1b"}
        first = ed["ZL3b"]
        aq = first.startswith("AQ")
        lr = locus_row.get(formal_locus)
        rows.append({
            "target_id": o["target_id"], "visual_locus": locus, "formal_locus": formal_locus,
            "visual_state": o["visual_state"],
            "family_expression": "|".join(g["family_surface"] for g in gs) if gs else "NO_EXACT_FAMILY_CONSENSUS",
            "first_group_family": first, "prefix2_aq": aq, "prefix3_aqa": first.startswith("AQA"),
            "exact_family_consensus": lr is not None,
            "strict_zero_alternative": lr is not None and lr["strict_zero_alternative"] == "1",
            "alternative_sites": int(lr["alternative_sites"]) if lr is not None else max(int(r["alternative_site_count"]) for r in by_align[formal_locus]),
            "zl_first_group_family": ed["ZL3b"], "it_first_group_family": ed["IT2a"],
            "rf_first_group_family": ed["RF1b"],
            "family_predicate_all_readings_stable": all(v.startswith("AQ") == aq for v in ed.values()),
            "aq": aq,
        })
    fields = ["target_id", "visual_locus", "formal_locus", "visual_state", "family_expression", "first_group_family",
              "prefix2_aq", "prefix3_aqa", "exact_family_consensus", "strict_zero_alternative", "alternative_sites",
              "zl_first_group_family", "it_first_group_family", "rf_first_group_family",
              "family_predicate_all_readings_stable"]
    with REVEAL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows({k: r[k] for k in fields} for r in rows)

    score = summarize(rows)
    effect = score["contact_minus_gap_prevalence"]
    if score["contact_total"] == 0 or score["gap_total"] == 0:
        decision = "UNSCORED_ONE_SIDED_ARRAY"
    elif effect is not None and effect > 0:
        decision = "FROZEN_DIRECTION_SUPPORTED_EXPLORATORILY"
    elif effect == 0:
        decision = "FROZEN_DIRECTION_TIED"
    else:
        decision = "FROZEN_DIRECTION_CONTRADICTED"
    result = {
        "schema": "GDT362_RESULT_V1", "status": decision,
        "question": "Does the frozen first-group AQ/contact direction transfer to the exhaustive remaining complete human-source array?",
        "primary_nine_loci_one_uncertain_missing": score,
        "formal": {
            "predicate": "FIRST_GROUP_PREFIX_2:AQ",
            "aqa_alias_identical": all(bool(r["prefix2_aq"]) == bool(r["prefix3_aqa"]) for r in rows),
            "all_rows_predicate_reading_stable": all(bool(r["family_predicate_all_readings_stable"]) for r in rows),
            "exact_family_consensus_rows": sum(bool(r["exact_family_consensus"]) for r in rows),
            "no_exact_family_consensus_rows": sum(not bool(r["exact_family_consensus"]) for r in rows),
            "strict_rows": sum(bool(r["strict_zero_alternative"]) for r in rows),
            "non_strict_or_no_consensus_rows": sum(not bool(r["strict_zero_alternative"]) for r in rows),
            "rows_with_alternative_sites": sum(int(r["alternative_sites"]) > 0 for r in rows),
        },
        "prior_context": {
            "gdt360_contact_aq": 5, "gdt360_contact_total": 8,
            "gdt360_gap_aq": 2, "gdt360_gap_total": 18,
            "gdt361_contact_aq": 1, "gdt361_contact_total": 3,
            "gdt361_gap_aq": 0, "gdt361_gap_total": 2,
            "discovery_predicate_postselected": True,
        },
        "access": {
            "nine_target_formal_rows_revealed_only_after_visual_freeze_commit": True,
            "single_ai_visual_observer": True,
            "source_descriptions_seen_before_visual_freeze": True,
            "f84_accessed": False,
        },
        "inputs": {
            str(OBS.relative_to(ROOT)): sha256_file(OBS),
            str(VISUAL_FREEZE.relative_to(ROOT)): sha256_file(VISUAL_FREEZE),
            str(LOCI.relative_to(ROOT)): sha256_file(LOCI),
            str(GROUPS.relative_to(ROOT)): sha256_file(GROUPS),
            str(ALIGN.relative_to(ROOT)): sha256_file(ALIGN),
            str(CROSSWALK.relative_to(ROOT)): sha256_file(CROSSWALK),
            "experiments/yolo/gdt362_remaining_complete_array/CORRECTION.md": sha256_file(BASE / "CORRECTION.md"),
            "experiments/yolo/gdt362_remaining_complete_array/src/run.py": sha256_file(Path(__file__)),
        },
        "outputs": {str(REVEAL.relative_to(ROOT)): sha256_file(REVEAL)},
        "claim_ceiling": "ONE_COMPLETE_NEW_FOLIO_ARRAY_DIRECTION_ONLY_NO_SEMANTIC_OR_TRANSLATION_CLAIM",
    }
    RESULT.write_bytes(canonical_json_bytes(result))
    print(json.dumps({"status": decision, "score": score}, indent=2))


if __name__ == "__main__":
    main()
