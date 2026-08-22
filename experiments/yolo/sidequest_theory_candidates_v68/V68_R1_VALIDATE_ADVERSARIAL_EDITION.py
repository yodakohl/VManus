#!/usr/bin/env python3
"""Validate V68 R1 frozen identities, completeness, scoring, and scope."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_theory_candidates_v67/V67_R1_776_COVERAGE_LEDGER.tsv"
EXPECTED_UNITS = {"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27, "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9, "A1": 190, "A2": 65, "A3": 140}
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
PRESERVE = ["universal_group_serial", "register", "unit_id", "page", "source_serial", "locus", "field_or_address", "statement_or_station", "exact_card_or_local_group_id", "formal_value", "atomic_or_whole_card_mnemonic", "source_order_slot", "abbreviation_channel", "register_state_before", "register_update", "register_state_after", "selected_parse_status", "terminal_status", "renderer_instruction", "rendered_surface"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def norm(text: str) -> str:
    return " ".join(text.split())


def digest(text: str) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()[:20]


def gate(name: str, condition: bool, detail: object, checks: list[dict[str, object]]) -> None:
    checks.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def economy(cost: int) -> int:
    return 5 if cost <= 3 else 4 if cost <= 6 else 3 if cost <= 9 else 2 if cost <= 12 else 1 if cost <= 15 else 0


def main() -> None:
    base = read(BASE)
    ledger = read(OUT / "V68_R1_776_GROUP_NONMEDICAL_LEDGER.tsv")
    units = read(OUT / "V68_R1_14_UNIT_ADVERSARIAL_EDITION.tsv")
    scores = read(OUT / "V68_R1_UNIT_SCORE_COMPARISON.tsv")
    assumptions = read(OUT / "V68_R1_ASSUMPTION_COSTS.tsv")
    contradictions = read(OUT / "V68_R1_CONTRADICTION_LEDGER.tsv")
    rubric = read(OUT / "V68_R1_FROZEN_SYMMETRIC_RUBRIC.tsv")
    checks: list[dict[str, object]] = []

    gate("base_and_output_rows", len(base) == len(ledger) == 776, len(ledger), checks)
    gate("fourteen_units", len(units) == 14 and len(contradictions) == 14, (len(units), len(contradictions)), checks)
    gate("ten_page_scope", {r["page"] for r in ledger} == ALLOWED_PAGES, sorted({r["page"] for r in ledger}), checks)
    gate("sealed_pages_absent", all(not r["page"].startswith("f84") for r in ledger), True, checks)
    gate("unit_counts", dict(Counter(r["unit_id"] for r in ledger)) == EXPECTED_UNITS, dict(Counter(r["unit_id"] for r in ledger)), checks)
    gate("register_counts", Counter(r["register"] for r in ledger) == {"HERBAL": 100, "BIO": 281, "ASTRO": 395}, dict(Counter(r["register"] for r in ledger)), checks)
    gate("all_frozen_columns_identical", all(all(a[col] == b[col] for col in PRESERVE) for a, b in zip(base, ledger)), True, checks)
    gate("all_rival_fragments_concrete", all(r["nonmedical_rival_local_expansion"].strip() for r in ledger), True, checks)
    gate("all_rival_fragments_local_only", all(r["nonmedical_source_status"] == "RECORD_OR_PAGE_LOCAL_EXEMPLAR; NOT_CARD_VALUE" for r in ledger), True, checks)
    gate("all_group_roundtrips", all(r["adversarial_roundtrip_status"] == "PASS_FROZEN_IDENTITY_PLUS_LOCAL_RIVAL_EXEMPLAR" for r in ledger), True, checks)
    gate("fragment_digests", all(r["rival_fragment_digest"] == digest(r["nonmedical_rival_local_expansion"]) for r in ledger), True, checks)

    unit_by_id = {r["unit_id"]: r for r in units}
    fragments: dict[str, list[str]] = defaultdict(list)
    for row in ledger:
        fragments[row["unit_id"]].append(row["nonmedical_rival_local_expansion"])
    gate("full_unit_text_reconstructed", all(norm(" ".join(fragments[u])) == norm(unit_by_id[u]["complete_nonmedical_German_text"]) for u in EXPECTED_UNITS), True, checks)
    gate("unit_text_digests", all(all(r["rival_unit_text_digest"] == digest(unit_by_id[u]["complete_nonmedical_German_text"]) for r in ledger if r["unit_id"] == u) for u in EXPECTED_UNITS), True, checks)
    gate("unit_requirements_present", all(r["executable_workflow"] and r["teaching_purpose"] and r["explicit_iconographic_argument"] and r["explicit_historical_argument"] and r["strongest_nonmedical_contradiction"] and r["direct_iatromedical_comparison"] for r in units), True, checks)
    gate("rubric_frozen_six_equal_criteria", len(rubric) == 6 and all(int(r["max_points"]) == 5 and r["symmetry"] for r in rubric), True, checks)
    gate("two_scores_per_unit", len(scores) == 28 and all(Counter(r["theory"] for r in scores if r["unit_id"] == u) == {"NONMEDICAL": 1, "IATROMEDICAL": 1} for u in EXPECTED_UNITS), True, checks)

    assumption_counts = Counter((r["unit_id"], r["theory"]) for r in assumptions)
    gate("assumption_costs_atomic", all(int(r["cost"]) == 1 and r["not_a_card_meaning"] == "YES" for r in assumptions), True, checks)
    gate("assumption_totals_match", all(int(r["unsupported_assumption_cost"]) == assumption_counts[(r["unit_id"], r["theory"])] for r in scores), True, checks)
    gate("economy_scores_derived", all(int(r["C4_assumption_economy"]) == economy(int(r["unsupported_assumption_cost"])) for r in scores), True, checks)
    gate("score_arithmetic", all(int(r["total_of_30"]) == sum(int(r[c]) for c in ["C1_formal_fidelity", "C2_iconography_fit", "C3_workflow_executability", "C4_assumption_economy", "C5_historical_genre_fit", "C6_cross_unit_purpose"]) for r in scores), True, checks)
    gate("formal_scores_symmetric", all(int(r["C1_formal_fidelity"]) == 5 for r in scores), True, checks)
    totals = Counter()
    for row in scores:
        totals[row["theory"]] += int(row["total_of_30"])
    gate("frozen_total", totals == {"NONMEDICAL": 371, "IATROMEDICAL": 370}, dict(totals), checks)
    gate("winner_distribution", Counter(r["unit_winner"] for r in units) == {"IATROMEDICAL": 6, "NONMEDICAL": 5, "TIE": 3}, dict(Counter(r["unit_winner"] for r in units)), checks)
    gate("no_new_card_meaning_claim", all(r["semantic_contract"] == "FULL_LOCAL_RIVAL_EDITION; NO_NEW_CARD_MEANING" for r in units), True, checks)
    gate("astro_namespace_separation", all((r["register"] != "ASTRO") or (r["atomic_or_whole_card_mnemonic"] == "NONE_ASTRO_NAMESPACE" and r["frozen_anchor_note"].startswith("ASTRO_PAGE_LOCAL_ADDRESS")) for r in ledger), True, checks)
    gate("no_direct_f68_f69_join", all(not ("f68r1" in r["exact_card_or_local_group_id"] and "f69v" in r["exact_card_or_local_group_id"]) for r in ledger), True, checks)

    result = {
        "status": "PASS", "checks_passed": len(checks),
        "counts": {"pages": 10, "units": 14, "groups": 776, "herbal": 100, "bio": 281, "astro": 395},
        "scores": {"nonmedical": totals["NONMEDICAL"], "iatromedical": totals["IATROMEDICAL"], "maximum_each": 420, "margin": 1},
        "verdict": "NONMEDICAL_NUMERIC_WIN_BY_ONE_POINT; SUBSTANTIVE_TIE_AND_NOT_ROBUST",
        "checks": checks,
    }
    (OUT / "V68_R1_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", **result["counts"], **result["scores"], "checks_passed": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
