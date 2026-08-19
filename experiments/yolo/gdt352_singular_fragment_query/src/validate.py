#!/usr/bin/env python3
"""Independent guarded reconstruction of GDT352."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt352_singular_fragment_query"
ART = EXP / "artifacts"
BASE = ROOT / "experiments/semantic_assumptions/results"
PAGES = {"f96v", "f99r", "f100r"}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> None:
    result = json.loads((ART / "gdt352_result.json").read_text(encoding="utf-8"))
    inv = read_tsv(ART / "gdt352_query_inventory.tsv")
    scores = read_tsv(ART / "gdt352_scores.tsv")
    checks = []
    def ck(name, ok, detail=""):
        checks.append({"name": name, "pass": bool(ok), "detail": detail})

    exact_guard = GuardedTSV(BASE / "existing_human_exact_locus_annotations.tsv", selector_column="page", allowed_values=PAGES)
    exact = list(exact_guard)
    loci_guard = GuardedTSV(BASE / "source_sta_family_consensus_loci.tsv", selector_column="page", allowed_values=PAGES)
    loci = list(loci_guard)
    groups_guard = GuardedTSV(BASE / "source_sta_family_consensus_groups.tsv", selector_column="page", allowed_values=PAGES)
    groups = list(groups_guard)
    allowed_loci = {r["locus"] for r in loci}
    align_guard = GuardedTSV(BASE / "source_sta_group_alignment.tsv", selector_column="locus", allowed_values=allowed_loci)
    align = list(align_guard)

    r46 = next(r for r in exact if r["locus"] == "f99r.46")
    ck("singular_source_exact", "only one plant and one label" in r46["local_comment"].lower())
    ck("inventory_two_relations", len(inv) == 2)
    ck("one_singular", sum(r["ownership_state"] == "SINGULAR_ONE_PLANT_ONE_LABEL" for r in inv) == 1)
    ck("one_ambiguous", sum(r["ownership_state"] == "AMBIGUOUS_SHIFTED_ROW" for r in inv) == 1)

    label_loci = {r["locus"] for r in exact if r["page"] == "f99r" and r["normalized_code"] == "@Lf"}
    family = {r["locus"]: r["family_sequence"] for r in loci}
    f96_family = [r["family_surface"] for r in groups if r["page"] == "f96v"]
    family_cmp = []
    for locus in label_loci:
        if locus not in family:
            continue
        value = family[locus]
        best = max(SequenceMatcher(None, value, target).ratio() for target in f96_family)
        family_cmp.append((best, locus, value in f96_family))
    fq = next(r for r in family_cmp if r[1] == "f99r.46")
    family_score = next(r for r in scores if r["query_locus"] == "f99r.46" and r["representation"] == "CONSENSUS_FAMILY")
    ck("primary_family_no_exact", not fq[2] and family_score["exact_match"] == "0")
    ck("primary_family_rank", int(family_score["matched_rank"]) == 1 + sum(r[0] > fq[0] for r in family_cmp))
    ck("primary_family_denominator", int(family_score["matched_denominator"]) == len(family_cmp) == 26)

    for edition in ("ZL3b", "IT2a", "RF1b"):
        surfaces = {}
        for row in align:
            if row["edition"] == edition:
                surfaces.setdefault(row["locus"], []).append(row["nearest_basic_eva_primary"].replace(" ", ""))
        target = [v for locus, values in surfaces.items() if locus.startswith("f96v.") for v in values]
        cmp = []
        for locus in label_loci:
            if locus not in surfaces:
                continue
            value = "|".join(surfaces[locus])
            best = max(SequenceMatcher(None, value, t).ratio() for t in target)
            cmp.append((best, locus, value in target))
        q = next(r for r in cmp if r[1] == "f99r.46")
        row = next(r for r in scores if r["query_locus"] == "f99r.46" and r["edition"] == edition)
        ck(f"surface_no_exact_{edition}", not q[2] and row["exact_match"] == "0")
        ck(f"surface_rank_{edition}", int(row["matched_rank"]) == 1 + sum(r[0] > q[0] for r in cmp))

    f100r3 = next(r for r in scores if r["query_locus"] == "f100r.3" and r["representation"] == "CONSENSUS_FAMILY")
    ck("ambiguous_aqjac_exact", f100r3["query_value"] == "AQJAC" and f100r3["exact_match"] == "1")
    ck("ambiguous_not_promoted", f100r3["ownership_state"] == "AMBIGUOUS_CANDIDATE")
    ck("status", result["status"] == "SINGULAR_QUERY_NEGATIVE_WITH_AMBIGUOUS_COMMON_FORM_LEAD")
    ck("post_exposure", result["exposure"] == "POST_EXPOSURE_EXPLORATORY")
    ck("counts", result["counts"]["primary_exact_surface_readings"] == 0 and result["counts"]["primary_exact_family"] == 0)
    ck("aqjac_prevalence", result["counts"]["aqjac_non_f84_group_rows"] == 56 and result["counts"]["aqjac_non_f84_pages"] == 44)
    for rel, digest in result["outputs"].items(): ck("output_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items(): ck("document_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items(): ck("implementation_hash:" + rel, sha(ROOT / rel) == digest)
    content = dict(result); claimed = content.pop("result_content_sha256")
    ck("content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)
    ck("no_f84_artifact", all("f84" not in "\t".join(r.values()).lower() for r in inv + scores))
    ck("guards_skipped_f84", all(g.stats.skipped_forbidden > 0 for g in (exact_guard, loci_guard, groups_guard, align_guard)))

    validation = {
        "experiment": "GDT352",
        "schema": "GDT352_VALIDATION_V1",
        "status": "PASS" if all(r["pass"] for r in checks) else "FAIL",
        "scope": "Independent guarded reconstruction of ownership, query ranks, exact matches, common-family prevalence, accounting, and hashes; not an independent visual or semantic review.",
        "checks_passed": sum(r["pass"] for r in checks),
        "checks_failed": sum(not r["pass"] for r in checks),
        "checks": checks,
        "result_sha256": sha(ART / "gdt352_result.json"),
        "implementation_sha256": sha(Path(__file__)),
    }
    (ART / "gdt352_validation.json").write_bytes(stable(validation))
    print(validation["status"], validation["checks_passed"], validation["checks_failed"])
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
