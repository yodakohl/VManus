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
from tools.vmanus_experiment import GuardedTSV, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt361_aq_contact_prospective"
ART = BASE / "artifacts"
TARGETS = [f"f102v2.{i}" for i in range(10, 17)]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks = []
    obs = read(ART / "gdt361_visual_observations.tsv")
    reveal = read(ART / "gdt361_formal_reveal.tsv")
    result = json.loads((ART / "gdt361_result.json").read_text())
    checks += [len(obs) == 7, len(reveal) == 7]
    checks.append([r["locus"] for r in obs] == TARGETS == [r["locus"] for r in reveal])
    target_set = set(TARGETS)
    groups = list(GuardedTSV(
        ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv",
        selector_column="locus", allowed_values=target_set, forbidden_prefixes=("f84",), forbidden_action="skip"))
    align = list(GuardedTSV(
        ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
        selector_column="locus", allowed_values=target_set, forbidden_prefixes=("f84",), forbidden_action="skip"))
    first = {}
    for row in groups:
        if row["consensus_group_index"] == "1":
            first[row["locus"]] = row["family_surface"]
    checks.append(set(first) == target_set)
    for row in reveal:
        checks.append(row["first_group_family"] == first[row["locus"]])
        checks.append((row["prefix2_aq"] == "True") == first[row["locus"]].startswith("AQ"))
    ed: dict[str, dict[str, str]] = defaultdict(dict)
    for row in align:
        if row["source_group_index"] == "1":
            ed[row["locus"]][row["edition"]] = row["primary_sta_families"]
    checks.append(all(set(v) == {"ZL3b", "IT2a", "RF1b"} for v in ed.values()))
    merged = []
    for o, r in zip(obs, reveal):
        merged.append({"state": o["visual_state"], "eligible": o["prospective_score_eligible"] == "1", "aq": r["prefix2_aq"] == "True"})
    primary = [r for r in merged if r["eligible"]]
    hard = [r for r in primary if r["state"] in {"CONTACT", "CLEAR_GAP"}]
    c = [r for r in hard if r["state"] == "CONTACT"]
    g = [r for r in hard if r["state"] == "CLEAR_GAP"]
    cp, gp = sum(r["aq"] for r in c), sum(r["aq"] for r in g)
    effect = cp / len(c) - gp / len(g)
    observed = cp
    extreme = worlds = 0
    for idx in itertools.combinations(range(len(hard)), len(c)):
        contact = set(idx)
        hit = sum(i in contact and r["aq"] for i, r in enumerate(hard))
        worlds += 1
        extreme += hit >= observed
    p = extreme / worlds
    p0 = result["primary_six_unexposed_loci"]
    checks.append(Counter(r["state"] for r in primary) == Counter(CONTACT=3, CLEAR_GAP=2, UNCERTAIN=1))
    checks += [p0["contact_aq"] == cp, p0["gap_aq"] == gp]
    checks.append(abs(p0["contact_minus_gap_prevalence"] - effect) < 1e-12)
    checks.append(abs(p0["exact_one_sided_p"] - p) < 1e-12)
    checks.append(result["status"] == ("FROZEN_DIRECTION_SUPPORTED_EXPLORATORILY" if effect > 0 else "FROZEN_DIRECTION_TIED" if effect == 0 else "FROZEN_DIRECTION_CONTRADICTED"))
    checks.append(result["access"]["f84_accessed"] is False)
    for rel, digest in result["inputs"].items():
        checks.append(sha256_file(ROOT / rel) == digest)
    for rel, digest in result["outputs"].items():
        checks.append(sha256_file(ROOT / rel) == digest)
    if not all(checks):
        raise SystemExit("FAIL")
    payload = {
        "schema": "GDT361_VALIDATION_V1", "status": "PASS",
        "checks_passed": sum(checks), "checks_total": len(checks),
        "reconstructed": {"contact_aq": cp, "gap_aq": gp, "effect": effect, "exact_p": p, "worlds": worlds},
        "scope": "Independent retained-row family join, exact score, accounting, and hash validation; not a second visual review.",
        "result_sha256": sha256_file(ART / "gdt361_result.json"),
        "f84_accessed": False,
    }
    (ART / "gdt361_validation.json").write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
