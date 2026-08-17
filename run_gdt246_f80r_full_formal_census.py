#!/usr/bin/env python3
"""Build a complete, role-free f80r formal census on the corrected coordinate."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
CONS = "gdt002_grammar_consensus_projection.tsv"
COORD = "gdt244_f80r_paragraph_coordinate.tsv"
PRED = "gdt233_q13_label_predictions.tsv"
CORR = "gdt245_q13_role_artifact_status.tsv"
OUTS = [
    "gdt246_f80r_complete_locus_inventory.tsv",
    "gdt246_f80r_paragraph_coverage.tsv",
    "gdt246_f80r_label_prose_recurrence.tsv",
]
DOCS = ["GDT246_F80R_FULL_FORMAL_CENSUS_METHOD.md", "GDT246_F80R_FULL_FORMAL_CENSUS_REPORT.md"]


def sha(name): return hashlib.sha256((R / name).read_bytes()).hexdigest()
def read(name):
    with (R / name).open(encoding="utf-8") as f: return list(csv.DictReader(f, delimiter="\t"))
def num(locus): return int(locus.split(".")[1])
def write(name, rows):
    with (R / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main():
    cons = [r for r in read(CONS) if r["page"] == "f80r"]
    assert cons and all(not r["page"].startswith("f84") for r in cons)
    by = defaultdict(list)
    for r in cons: by[r["locus"]].append(r)
    assert len(by) == 53
    coord = {r["locus"]: r for r in read(COORD)}
    pred = {r["locus"]: r for r in read(PRED) if r["page"] == "f80r"}
    rows = []
    for locus in sorted(by, key=num):
        rr = by[locus]; base = rr[0]; state = base["coverage_state"]
        groups = [r for r in rr if r["consensus_group_id"]]
        families = [r["family_surface"] for r in groups]
        assert all(r["coverage_state"] == state and r["kind"] == base["kind"] for r in rr)
        if state == "STRICT_EXACT_FAMILY":
            assert groups and len(groups) == int(groups[0]["group_count"])
        else:
            assert not groups
        c = coord.get(locus); p = pred.get(locus)
        historical = "SUSPENDED_COORDINATE_INVALID" if base["kind"] == "P" else "NOT_APPLICABLE_LABEL"
        rows.append({
            "page": "f80r", "locus": locus, "kind": base["kind"], "grammar_scope": base["grammar_scope"],
            "paragraph_id": c["paragraph_id"] if c else "GRAPHICAL_LABEL",
            "paragraph_line_ordinal": c["paragraph_line_ordinal"] if c else "NA",
            "paragraph_line_count": c["paragraph_line_count"] if c else "NA",
            "coverage_state": state, "consensus_group_count": len(groups),
            "family_expression": "|".join(families) if families else "UNRESOLVED",
            "first_family": families[0] if families else "UNRESOLVED",
            "last_family": families[-1] if families else "UNRESOLVED",
            "transferred_label_prefix": p["strict_prefix"] if p and base["kind"] == "L" else "UNAVAILABLE",
            "transferred_label_residual": p["strict_residual"] if p and base["kind"] == "L" else "UNAVAILABLE",
            "transferred_label_prediction": p["predicted_label"] if p and base["kind"] == "L" else "UNAVAILABLE",
            "historical_role_state": historical, "semantic_value": "UNASSIGNED",
        })
    write(OUTS[0], rows)
    paragraph = []
    for pid in [f"P{i}" for i in range(1, 6)]:
        z = [r for r in rows if r["paragraph_id"] == pid]; cc = Counter(r["coverage_state"] for r in z)
        paragraph.append({
            "page": "f80r", "paragraph_id": pid, "physical_prose_loci": len(z),
            "strict_exact_family_loci": cc["STRICT_EXACT_FAMILY"],
            "alternative_bearing_loci": cc["EXACT_FAMILY_WITH_ALTERNATIVE"],
            "no_exact_consensus_loci": cc["NO_EXACT_FAMILY_CONSENSUS"],
            "strict_consensus_groups": sum(int(r["consensus_group_count"]) for r in z),
            "semantic_role_state": "UNASSIGNED_COORDINATE_CORRECTED",
        })
    write(OUTS[1], paragraph)
    labels, prose = defaultdict(list), defaultdict(list)
    for r in cons:
        if r["coverage_state"] != "STRICT_EXACT_FAMILY" or not r["consensus_group_id"]: continue
        (labels if r["kind"] == "L" else prose)[r["family_surface"]].append(r)
    recur = []
    for fam in sorted(set(labels) & set(prose)):
        ll, pp = labels[fam], prose[fam]
        label_loci = sorted({r["locus"] for r in ll}, key=num)
        prose_loci = sorted({r["locus"] for r in pp}, key=num)
        prefixes = sorted({pred[x]["strict_prefix"] for x in label_loci if x in pred})
        recur.append({
            "family_surface": fam, "label_loci": ",".join(label_loci), "label_occurrences": len(ll),
            "prose_loci": ",".join(prose_loci), "prose_group_occurrences": len(pp),
            "corrected_prose_paragraphs": ",".join(sorted({coord[x]["paragraph_id"] for x in prose_loci})),
            "transferred_label_prefix": ",".join(prefixes) or "NONE",
            "evidence_state": "EXACT_WHOLE_LABEL_FAMILY_RECURS_AS_INTERNAL_PROSE_GROUP",
            "semantic_value": "UNASSIGNED",
        })
    assert [r["family_surface"] for r in recur] == ["ABQA", "AQABA", "AQAC"]
    write(OUTS[2], recur)
    cov = Counter(r["coverage_state"] for r in rows)
    label_rows = [r for r in rows if r["kind"] == "L"]
    prose_rows = [r for r in rows if r["kind"] == "P"]
    result = {
        "experiment": "GDT246_F80R_FULL_FORMAL_CENSUS",
        "status": "F80R_COMPLETE_FORMAL_CENSUS_THREE_LABEL_FAMILIES_RECUR_IN_PROSE_NO_SEMANTIC_KEY",
        "loci": len(rows), "labels": len(label_rows), "prose": len(prose_rows),
        "coverage": dict(sorted(cov.items())),
        "prose_coverage": dict(sorted(Counter(r["coverage_state"] for r in prose_rows).items())),
        "label_coverage": dict(sorted(Counter(r["coverage_state"] for r in label_rows).items())),
        "paragraph_line_counts": [int(r["physical_prose_loci"]) for r in paragraph],
        "paragraph_strict_loci": [int(r["strict_exact_family_loci"]) for r in paragraph],
        "strict_label_prefix_hits": sum(r["transferred_label_prediction"] == "1" for r in label_rows),
        "strict_family_covered_labels": sum(r["coverage_state"] == "STRICT_EXACT_FAMILY" for r in label_rows),
        "cross_scope_exact_families": [r["family_surface"] for r in recur],
        "cross_scope_label_occurrences": sum(int(r["label_occurrences"]) for r in recur),
        "cross_scope_prose_group_occurrences": sum(int(r["prose_group_occurrences"]) for r in recur),
        "interpretation": "Three complete graphical-label family expressions recur as internal prose groups on corrected paragraphs, supporting a reusable graphical/prose code interface but no meaning.",
        "active_semantic_assignments": 0,
        "claim_ceiling": "Complete formal census and exact cross-scope recurrence only; no object, role, word, language, plaintext, or translation.",
        "f84": {"input": False, "retained": False, "joined": False, "scored": False, "new_access": False},
        "inputs": {name: sha(name) for name in [CONS, COORD, PRED, CORR]},
        "outputs": {name: sha(name) for name in OUTS}, "documents": {}, "implementation": {},
    }
    for name in DOCS:
        if (R / name).exists(): result["documents"][name] = sha(name)
    result["implementation"][Path(__file__).name] = sha(Path(__file__).name)
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (R / "gdt246_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "coverage", "prose_coverage", "label_coverage", "paragraph_strict_loci", "cross_scope_exact_families"]}, sort_keys=True))


if __name__ == "__main__": main()
