#!/usr/bin/env python3
from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"
ART = BASE / "artifacts"

import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, sha256_file  # noqa: E402

TARGETS = [f"f101v2.{i}" for i in range(10, 19)]
FORMAL_TARGETS = [f"f101v.{i}" for i in range(10, 19)]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def main() -> None:
    obs = read(ART / "gdt362_visual_observations.tsv")
    reveal = read(ART / "gdt362_formal_reveal.tsv")
    result = json.loads((ART / "gdt362_result.json").read_text())
    checks: list[bool] = []
    checks += [len(obs) == 9, len(reveal) == 9,
               [r["locus"] for r in obs] == TARGETS,
               [r["visual_locus"] for r in reveal] == TARGETS,
               [r["formal_locus"] for r in reveal] == FORMAL_TARGETS]
    target_set = set(FORMAL_TARGETS)
    crosswalk = list(GuardedTSV(ROOT / "experiments/semantic_assumptions/results/existing_human_current_locus_crosswalk.tsv",
                                selector_column="source_page", allowed_values={"f101v2", "f101v1"},
                                forbidden_prefixes=("f84",), forbidden_action="skip"))
    checks.append(target_set <= {r["current_locus"] for r in crosswalk})
    groups = list(GuardedTSV(ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv",
                             selector_column="locus", allowed_values=target_set,
                             forbidden_prefixes=("f84",), forbidden_action="skip"))
    align = list(GuardedTSV(ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
                            selector_column="locus", allowed_values=target_set,
                            forbidden_prefixes=("f84",), forbidden_action="skip"))
    checks.append({r["locus"] for r in groups} == target_set - {"f101v.13", "f101v.14"})
    ed: dict[str, dict[str, str]] = defaultdict(dict)
    for r in align:
        if r["source_group_index"] == "1": ed[r["locus"]][r["edition"]] = r["primary_sta_families"]
    checks.append(all(set(v) == {"ZL3b", "IT2a", "RF1b"} for v in ed.values()))
    for r in reveal:
        primary = ed[r["formal_locus"]]["ZL3b"]
        checks += [r["first_group_family"] == primary,
                   (r["prefix2_aq"] == "True") == primary.startswith("AQ"),
                   (r["family_predicate_all_readings_stable"] == "True") == all(x.startswith("AQ") == primary.startswith("AQ") for x in ed[r["formal_locus"]].values())]
    merged = [{"state": o["visual_state"], "aq": r["prefix2_aq"] == "True"} for o, r in zip(obs, reveal)]
    hard = [r for r in merged if r["state"] in {"CONTACT", "CLEAR_GAP"}]
    contact = [r for r in hard if r["state"] == "CONTACT"]
    gap = [r for r in hard if r["state"] == "CLEAR_GAP"]
    cp, gp = sum(r["aq"] for r in contact), sum(r["aq"] for r in gap)
    effect = cp / len(contact) - gp / len(gap)
    worlds = extreme = 0
    for idx in itertools.combinations(range(len(hard)), len(contact)):
        chosen = set(idx)
        hit = sum(i in chosen and r["aq"] for i, r in enumerate(hard))
        worlds += 1; extreme += hit >= cp
    p = extreme / worlds
    out = result["primary_nine_loci_one_uncertain_missing"]
    checks += [Counter(r["state"] for r in merged) == Counter(CONTACT=3, CLEAR_GAP=5, UNCERTAIN=1),
               out["contact_aq"] == cp, out["gap_aq"] == gp,
               abs(out["contact_minus_gap_prevalence"] - effect) < 1e-12,
               abs(out["exact_one_sided_p"] - p) < 1e-12,
               out["exact_total_worlds"] == worlds,
               result["status"] == ("FROZEN_DIRECTION_SUPPORTED_EXPLORATORILY" if effect > 0 else "FROZEN_DIRECTION_TIED" if effect == 0 else "FROZEN_DIRECTION_CONTRADICTED"),
               result["access"]["f84_accessed"] is False]
    for rel, digest in result["inputs"].items(): checks.append(sha256_file(ROOT / rel) == digest)
    for rel, digest in result["outputs"].items(): checks.append(sha256_file(ROOT / rel) == digest)
    if not all(checks): raise SystemExit("FAIL")
    payload = {
        "schema": "GDT362_VALIDATION_V1", "status": "PASS",
        "checks_passed": sum(checks), "checks_total": len(checks),
        "reconstructed": {"contact_aq": cp, "gap_aq": gp, "effect": effect,
                            "exact_p": p, "worlds": worlds},
        "scope": "Independent guarded retained-row family join, exact score, accounting, and hashes; not a second visual review.",
        "result_sha256": sha256_file(ART / "gdt362_result.json"), "f84_accessed": False,
    }
    (ART / "gdt362_validation.json").write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
