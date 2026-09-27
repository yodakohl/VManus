"""Bounded literal replay of the frozen IDEA582 first-contract packet."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926"
PROJ = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
CONTRACT = BASE / "WIND_TRANSIT_AUTHOR_CONTRACT.json"
OUT = BASE / "WIND_TRANSIT_REPLAY_B.json"
FIELDS = ["edition", "block", "locus", "source_group_id", "source_group_index",
          "source_group_count", "within_line_position", "paragraph_start",
          "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw"]

src = list(csv.DictReader(PROJ.open(), delimiter="\t"))
doc = json.loads(CONTRACT.read_text())
rows = doc["all473_literal_obligations"]
lex = doc["lexicon"]
errors = []
src_by_id = {r["source_group_id"]: r for r in src}
out_by_id = {r["source_group_id"]: r for r in rows}
if len(src) != 473 or len(rows) != 473:
    errors.append(f"row counts source={len(src)} packet={len(rows)}")
if len(src_by_id) != 473 or len(out_by_id) != 473:
    errors.append("duplicate source_group_id")
if set(src_by_id) != set(out_by_id):
    errors.append("source_group_id set mismatch")
for gid, native in src_by_id.items():
    target = out_by_id.get(gid, {})
    for f in FIELDS:
        if native[f] != target.get(f):
            errors.append(f"{gid}: native field {f} differs")

# Each exact literal token in the frozen lexicon names the complete list of
# its assigned group IDs. Reconstruct this independently from the entries.
gid_to_value = {}
for token, entry in lex.items():
    for gid in entry["all_owned_occurrence_ids"]:
        if gid in gid_to_value:
            errors.append(f"duplicate lexicon assignment for {gid}")
        gid_to_value[gid] = entry["value"]
for row in rows:
    gid = row["source_group_id"]
    if row["fixed_binding"] != gid_to_value.get(gid):
        errors.append(f"binding/list disagreement at {gid}")
    if row["fixed_binding"] is not None and row["status"] not in {
        "first_contract_manual_derivation", "assigned_literal_occurrence_not_yet_parsed"
    }:
        errors.append(f"assigned status mismatch at {gid}")
    if row["fixed_binding"] is None and row["status"] != "unassigned":
        errors.append(f"unassigned status mismatch at {gid}")

local = doc["local_rows"]
local_ids = {r["source_group_id"] for r in local}
if len(local) != 36 or len(local_ids) != 36:
    errors.append("local row count/uniqueness mismatch")
for r in local:
    n = src_by_id.get(r["source_group_id"])
    if n is None or any(r[f] != n[f] for f in FIELDS):
        errors.append(f"local row differs from projection: {r['source_group_id']}")
    if r["status"] != "first_contract_manual_derivation":
        errors.append(f"local status mismatch: {r['source_group_id']}")

spans = {
    "W1": [("f85r2.18", 1, 5)], "W2": [("f85r2.19", 1, 2)],
    "W3": [("f85r2.19", 3, 5)], "W4": [("f85r2.20", 1, 3)],
    "W5": [("f85r2.20", 4, 8)],
    "W6": [("f85r2.21", 1, 5), ("f85r2.22", 1, 8)],
    "W7": [("f85r2.23", 1, 5)],
}
manual = {x["id"]: x for x in doc["manual_clauses"]}
raw_spans = {}
for clause_id, pieces in spans.items():
    actual_ids, raw = [], []
    for locus, lo, hi in pieces:
        for i in range(lo, hi + 1):
            gid = f"ZL3b|{locus}|G{i:03d}"
            actual_ids.append(gid)
            raw.append(src_by_id[gid]["ivtff_group_raw"])
    declared_ids = []
    for s in manual[clause_id]["contiguous_spans"]:
        locus, rg = s.split(":")
        lo, hi = map(int, rg.split("-"))
        declared_ids += [f"ZL3b|{locus}|G{i:03d}" for i in range(lo, hi + 1)]
    if actual_ids != declared_ids:
        errors.append(f"manual span differs for {clause_id}")
    raw_spans[clause_id] = raw

status_counts = Counter(r["status"] for r in rows)
reader_counts = Counter(r["edition"] for r in rows)
value_counts = Counter(r["fixed_binding"] for r in rows if r["fixed_binding"] is not None)
result = {
    "status": "PASS_LITERAL_ROW_AND_SPAN_REPLAY" if not errors else "FAIL",
    "input_hashes": {
        "native_groups.tsv": hashlib.sha256(PROJ.read_bytes()).hexdigest(),
        "author_contract.json": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
    },
    "checks": {
        "all_473_ids_and_12_native_fields": len(src) == 473 and len(rows) == 473 and not any("native field" in e or "source_group_id" in e for e in errors),
        "all_162_lexicon_occurrences_accounted": len(gid_to_value) == 162 and not any("lexicon assignment" in e or "binding/list" in e for e in errors),
        "36_local_rows_exact": len(local_ids) == 36 and not any("local row" in e for e in errors),
        "seven_manual_spans_match_projection": len(spans) == 7 and not any("manual span" in e for e in errors),
        "row_statuses_consistent": sum(status_counts.values()) == 473 and not any("status mismatch" in e for e in errors),
    },
    "counts": {
        "rows": len(rows), "local_rows": len(local), "lexicon_entries": len(lex),
        "lexicon_occurrence_ids": len(gid_to_value), "row_statuses": dict(status_counts),
        "reader_rows": dict(reader_counts), "binding_occurrences": dict(value_counts),
    },
    "local_span_raw_groups": raw_spans,
    "errors": errors,
    "interpretive_limit": "Literal/occurrence/span replay only; no meaning confirmation or whole-page parse. Manual report is informed by prior source/plan exposure.",
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
