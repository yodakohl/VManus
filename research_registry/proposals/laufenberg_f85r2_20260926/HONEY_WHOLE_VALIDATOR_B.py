#!/usr/bin/env python3
"""Independent literal replay of HONEY_WHOLE_DRAFT against GDT1042 safe projection.

This checks provenance/hash, exact reader-block inventory, clause partition,
assigned-value census, outside-block rows, and the declared qod/Product/chol
construction spans. It intentionally does not import producer code or read any
mixed source TSV. Structural PASS says nothing about lexical truth or semantic
coherence.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECTION = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv"
METHOD = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/METHOD.md"
LOCK = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/src/PREREG_LOCK.json"
DRAFT = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926/HONEY_WHOLE_DRAFT.json"
OUT = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926/HONEY_WHOLE_VALIDATOR_B.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_for(locus: str) -> str:
    line = int(locus.rsplit(".", 1)[1])
    if 2 <= line <= 6:
        return "N"
    if 7 <= line <= 11:
        return "E"
    if 12 <= line <= 17:
        return "S"
    if 18 <= line <= 23:
        return "W"
    return "OUTSIDE"


lock = json.loads(LOCK.read_text())
draft = json.loads(DRAFT.read_text())
with PROJECTION.open(newline="", encoding="utf-8") as f:
    projection = list(csv.DictReader(f, delimiter="\t"))

failures: list[str] = []
if sha(METHOD) != lock["sha256"]:
    failures.append("METHOD hash differs from preregistration lock")
if sha(PROJECTION) != "489c3960116c88f76de39187eef3d2f9d3dd68d3c2e514f54abe7a2294d185e9":
    failures.append("guarded projection hash differs from independently recorded task input")
if len(projection) != 473:
    failures.append(f"safe projection row count {len(projection)} != 473")
if draft.get("freeze_receipt", {}).get("frozen_utc") != "2026-09-26T23:38:47Z":
    failures.append("frozen timestamp differs from specified draft freeze")
if sha(DRAFT) != "30e20e160e20cdd09931e44135b36668afa6cd1885d04663c2190c496e7d30bc":
    failures.append("draft hash differs from specified frozen hash")

lex = draft["lexicon"]
expected_block_rows = [r for r in projection if block_for(r["locus"]) != "OUTSIDE"]
provided_block_rows = draft["all_four_block_occurrences"]
source_by_id = {r["source_group_id"]: r for r in projection}
expected_block_ids = {r["source_group_id"] for r in expected_block_rows}
provided_block_ids = [r["source_group_id"] for r in provided_block_rows]
if len(provided_block_ids) != 324 or len(set(provided_block_ids)) != 324:
    failures.append("block rows are not 324 unique source IDs")
if set(provided_block_ids) != expected_block_ids:
    failures.append("block source-ID set differs from 4-block safe-projection set")

block_mismatches = []
expected_fields = ["edition", "locus", "source_group_id", "source_group_index", "source_group_count",
                   "paragraph_start", "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw"]
for row in provided_block_rows:
    src = source_by_id.get(row["source_group_id"])
    if src is None:
        block_mismatches.append({"id": row["source_group_id"], "error": "not in projection"})
        continue
    exp_block = block_for(src["locus"])
    idx, count = int(src["source_group_index"]), int(src["source_group_count"])
    position = ("first_last" if count == 1 else "first" if idx == 1 else
                "last" if idx == count else "interior")
    for field in expected_fields:
        if row.get(field) != src[field]:
            block_mismatches.append({"id": src["source_group_id"], "field": field,
                                     "expected": src[field], "actual": row.get(field)})
    if row.get("block") != exp_block:
        block_mismatches.append({"id": src["source_group_id"], "field": "block",
                                 "expected": exp_block, "actual": row.get("block")})
    if row.get("within_line_position") != position:
        block_mismatches.append({"id": src["source_group_id"], "field": "within_line_position",
                                 "expected": position, "actual": row.get("within_line_position")})
    assigned = src["ivtff_group_raw"] in lex
    want_status = ("ZL_AUTHORED_ONCE" if src["edition"] == "ZL3b" else
                   "EXACT_SHARED_VALUE_ALTERNATE_CONTEXT_PENDING" if assigned else
                   "UNASSIGNED_LITERAL_ALTERNATIVE")
    if row.get("status") != want_status:
        block_mismatches.append({"id": src["source_group_id"], "field": "status",
                                 "expected": want_status, "actual": row.get("status")})
    if row.get("lexicon_ref") != (src["ivtff_group_raw"] if assigned else None):
        block_mismatches.append({"id": src["source_group_id"], "field": "lexicon_ref",
                                 "expected": src["ivtff_group_raw"] if assigned else None,
                                 "actual": row.get("lexicon_ref")})
if block_mismatches:
    failures.append(f"{len(block_mismatches)} exact block-row discrepancies")

# All 108 ZL occurrences must be represented once and in the authored literal sequence.
zl = {r["source_group_id"]: r for r in provided_block_rows if r["edition"] == "ZL3b"}
clause_refs = [gid for clause in draft["ZL_clauses"] for gid in clause["source_group_ids"]]
if len(clause_refs) != 108 or len(set(clause_refs)) != 108 or set(clause_refs) != set(zl):
    failures.append("ZL authored clauses do not partition all 108 ZL block IDs exactly once")
clause_mismatches = []
for c in draft["ZL_clauses"]:
    ids = c["source_group_ids"]
    raw = [zl.get(g, {}).get("ivtff_group_raw") for g in ids]
    if raw != c["literal_groups"]:
        clause_mismatches.append({"clause": c["id"], "expected_raw": raw, "declared": c["literal_groups"]})
    if any(g not in zl or zl[g].get("ZL_clause") != c["id"] for g in ids):
        clause_mismatches.append({"clause": c["id"], "error": "row/clause backlinks disagree"})
if len(draft["ZL_clauses"]) != 18 or clause_mismatches:
    failures.append("ZL clause count or exact literal/backlink check failed")

# Alternate and outside contexts reconstructed directly from the safe projection.
edition_block_counts = {}
for edition in ("ZL3b", "IT2a", "RF1b"):
    rows = [r for r in expected_block_rows if r["edition"] == edition]
    groups = len(rows)
    assigned = sum(r["ivtff_group_raw"] in lex for r in rows)
    edition_block_counts[edition] = {"groups": groups, "assigned_by_exact_whole": assigned,
                                     "unassigned": groups - assigned}
    declared = draft["counts"].get(edition, {})
    if declared != {"groups": groups, "assigned": assigned, "unassigned": groups - assigned}:
        failures.append(f"alternate count mismatch for {edition}")

expected_assigned_index = defaultdict(list)
expected_outside = []
for r in projection:
    raw = r["ivtff_group_raw"]
    b = block_for(r["locus"])
    if raw in lex:
        expected_assigned_index[raw].append({"source_group_id": r["source_group_id"], "block": b,
                                             "left_separator": r["left_separator"],
                                             "right_separator": r["right_separator"]})
        if b == "OUTSIDE":
            idx, count = int(r["source_group_index"]), int(r["source_group_count"])
            expected_outside.append({
                "edition": r["edition"], "block": "OUTSIDE", "locus": r["locus"],
                "source_group_id": r["source_group_id"], "source_group_index": r["source_group_index"],
                "source_group_count": r["source_group_count"],
                "within_line_position": "first" if idx == 1 else "last" if idx == count else "interior",
                "paragraph_start": r["paragraph_start"], "paragraph_end": r["paragraph_end"],
                "left_separator": r["left_separator"], "right_separator": r["right_separator"],
                "ivtff_group_raw": raw,
                "status": "VALUE_FIXED_OUTSIDE_FOUR_BLOCKS_CONTEXT_NOT_FULLY_AUTHORED",
                "lexicon_ref": raw})

index_mismatches = []
declared_index = draft["all24_locus_assignment_index"]
if set(declared_index) != set(expected_assigned_index):
    index_mismatches.append("assigned-form keys differ")
for raw, exp in expected_assigned_index.items():
    got = declared_index.get(raw, [])
    if sorted(got, key=lambda x: x["source_group_id"]) != sorted(exp, key=lambda x: x["source_group_id"]):
        index_mismatches.append(f"occurrence list mismatch for {raw}")
if index_mismatches:
    failures.append("all24-locus assigned-form index differs from projection")

outside_got = draft["outside_four_block_occurrences"]
outside_mismatches = []
if len(outside_got) != len(expected_outside) or {r["source_group_id"] for r in outside_got} != {r["source_group_id"] for r in expected_outside}:
    outside_mismatches.append("outside source-ID coverage differs")
else:
    expected_out_by_id = {r["source_group_id"]: r for r in expected_outside}
    for row in outside_got:
        exp = expected_out_by_id[row["source_group_id"]]
        if row != exp:
            outside_mismatches.append(row["source_group_id"])
if outside_mismatches:
    failures.append("outside assigned occurrence rows differ from safe projection")

# Check actual complete spans for the reused qod, Product shedy, and chol values.
zl_order = sorted((r for r in expected_block_rows if r["edition"] == "ZL3b"),
                  key=lambda r: (int(r["locus"].rsplit(".", 1)[1]), int(r["source_group_index"])))
zl_by_raw = defaultdict(list)
for r in zl_order:
    zl_by_raw[r["ivtff_group_raw"]].append(r)
construction_uses = {
    "qodar": [("f85r2.10", "2")],
    "qodaiin": [("f85r2.16", "2"), ("f85r2.21", "5")],
    "qodain": [("f85r2.19", "2")],
}
qod_observed = {}
for raw, uses in construction_uses.items():
    rows = zl_by_raw.get(raw, [])
    actual = [(r["locus"], r["source_group_index"]) for r in rows]
    if sorted(actual) != sorted(uses):
        failures.append(f"qod compound span mismatch for {raw}: {actual}")
    qod_observed[raw] = [{"locus": r["locus"], "index": int(r["source_group_index"]),
                          "id": r["source_group_id"], "left": r["left_separator"],
                          "right": r["right_separator"]} for r in rows]

product_rows = zl_by_raw.get("shedy", [])
product_spans = [{"locus": r["locus"], "index": int(r["source_group_index"]),
                  "id": r["source_group_id"], "raw": r["ivtff_group_raw"]} for r in product_rows]
expected_product_spans = [("f85r2.13", "2"), ("f85r2.20", "8"), ("f85r2.21", "4"), ("f85r2.22", "3")]
if sorted((r["locus"], str(r["index"])) for r in product_spans) != sorted(expected_product_spans):
    failures.append("shedy Product literal spans differ from frozen receipt")

chol_rows = zl_by_raw.get("chol", [])
chol_spans = [{"locus": r["locus"], "index": int(r["source_group_index"]),
               "id": r["source_group_id"], "raw": r["ivtff_group_raw"]} for r in chol_rows]
expected_chol_spans = [("f85r2.4", "4"), ("f85r2.23", "3")]
if sorted((r["locus"], str(r["index"])) for r in chol_spans) != sorted(expected_chol_spans):
    failures.append("chol BECOME literal spans differ from independently reconstructed locations")

special_contexts = {}
for raw in ("qodar", "qodaiin", "qodain", "shedy", "chol"):
    special_contexts[raw] = [
        {"edition": r["edition"], "locus": r["locus"], "index": int(r["source_group_index"]),
         "source_group_id": r["source_group_id"], "left_separator": r["left_separator"],
         "right_separator": r["right_separator"]}
        for r in projection if r["ivtff_group_raw"] == raw
    ]

# Independently inspect that exact component cuts consume the declared words.
parts = draft["component_lexicon"]
cuts = draft["licensed_cuts"]
cut_products = ["".join(c) for c in cuts]
if len(cuts) != 3 or set(cut_products) != {"qodar", "qodaiin", "qodain"}:
    failures.append("qod component cuts do not exactly yield the three claimed forms")
if parts["qod"]["type"] != "ContainerKind -> LocativeExpression":
    failures.append("qod component type differs from declared locative function")

result = {
    "schema": "honey_whole_validator_b_v1",
    "validation_scope": "Independent literal replay from GDT1042 artifacts/guarded_projection.tsv only; no producer import; no mixed source TSV read.",
    "inputs": {
        "projection": str(PROJECTION.relative_to(ROOT)), "projection_sha256": sha(PROJECTION),
        "method": str(METHOD.relative_to(ROOT)), "method_sha256": sha(METHOD),
        "lock": str(LOCK.relative_to(ROOT)), "draft": str(DRAFT.relative_to(ROOT)), "draft_sha256": sha(DRAFT)
    },
    "result": "STRUCTURAL_PASS" if not failures else "DISCREPANCY",
    "failures": failures,
    "projection_rows": len(projection),
    "reader_groups_by_projection": {e: sum(r["edition"] == e for r in projection) for e in ("ZL3b", "IT2a", "RF1b")},
    "expected_block_rows": len(expected_block_rows),
    "exact_block_row_mismatches": len(block_mismatches),
    "edition_block_counts_reconstructed": edition_block_counts,
    "ZL_clause_count": len(draft["ZL_clauses"]),
    "ZL_clause_group_refs": len(clause_refs),
    "ZL_unique_clause_group_refs": len(set(clause_refs)),
    "ZL_clause_literal_mismatches": clause_mismatches,
    "assigned_whole_types": len(lex),
    "all24_index_types": len(declared_index),
    "all24_index_mismatches": index_mismatches,
    "expected_outside_assigned_occurrences": len(expected_outside),
    "outside_mismatches": outside_mismatches,
    "reused_literal_spans": {"qod_compounds": qod_observed, "shedy_Product": product_spans, "chol_BECOME": chol_spans},
    "all_safe_projection_contexts_for_reused_literals": special_contexts,
    "independent_manual_grammar_review": {
        "qod": "All three cuts are explicitly licensed; qod is consistently a ContainerKind-to-LocativeExpression function and each suffix maps to recipient/body/food. The W19 food case is not interchangeable with body cases. No literal type clash found in those four uses.",
        "shedy_Product": "The four listed occurrences are distinct written product constructions (S1, W2, W3, W4) with declared SVO/SOV/plural-lift rules. This is a large authored grammar and W4's set-valued plural lift is tailored, but it is declared and no single occurrence requires changing input/output roles. No literal type clash found.",
        "chol_BECOME": "The two occurrences N4 and W5 use the same typed transition over a physical portion/property and discourse object/epistemic property, respectively. The domain extension is an explicit assumption and does not entail material KindChange. No literal type clash found.",
        "prompted_followup_odain": "In S2 the literal sequence is am oteey qodaiin odain an chey ...; odain is declared BY(production,process), while an is a ChangePredicate/KIND_CHANGE relation with lineage endpoints. G12 uses the process-like wording 'by kind change' and types KindChange(z,y,c), but introduces no distinct Process/Event individual. If BY requires an entity of Process type, that argument is not supplied; if BY relates predicate/event descriptions at higher order, the coercion/type rule is underspecified. This is a formalization gap, not a forced contradiction, because that higher-order reading is possible but not explicitly declared.",
        "semantic_limit": "Coverage and type-role checks do not validate guessed meanings, source identity, unique parsing, historical truth, or execution."
    },
    "row_discrepancy_examples": block_mismatches[:10]
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT)
print(json.dumps({"result": result["result"], "failures": failures,
                  "edition_block_counts": edition_block_counts,
                  "outside": len(expected_outside), "qod": qod_observed,
                  "shedy": product_spans, "chol": chol_spans}, ensure_ascii=False, indent=2))
