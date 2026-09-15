#!/usr/bin/env python3
"""Independent arithmetic/source audit for GDT957; no run.py import."""
from __future__ import annotations
import csv, gzip, hashlib, itertools, json, re
from collections import Counter
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
EDITIONS = ["ZL3b", "IT2a", "RF1b"]
DIRECTIONS = ["TOP_DOWN", "BOTTOM_UP"]
EVAL = {e: f"experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_EVALUATION_{e}.json" for e in EDITIONS}

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def err(errors, kind, **kw): errors.append({"kind": kind, **kw})

def chart(m):
    # Four mother figures, then four transposed rows, then seven XOR parents.
    out = list(m)
    for row in range(4):
        value = 0
        for col, figure in enumerate(m): value |= ((figure >> (3 - row)) & 1) << (3 - col)
        out.append(value)
    for a, b in ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 14)):
        out.append(out[a - 1] ^ out[b - 1])
    return tuple(out)

def all_charts(): return [chart(m) for m in itertools.product(range(16), repeat=4)]

def source_targets(errors):
    rows = []
    expected_unknown = {"ZL3b": {2, 3}, "IT2a": set(), "RF1b": {4, 10}}
    for edition in EDITIONS:
        path = ROOT / EVAL[edition]
        if not path.is_file(): err(errors, "SOURCE_MISSING", edition=edition); continue
        data = load(path); found = {}
        for line in data.get("lines", []):
            meta = line.get("metadata", {})
            if meta.get("page") != "f66r" or meta.get("locus") not in {f"f66r.{i}" for i in range(1, 16)}: continue
            locus = meta["locus"]
            if locus in found: err(errors, "TARGET_DUPLICATE", edition=edition, locus=locus)
            groups = [dict(zip(data.get("group_columns", []), g)) for g in line.get("groups", [])]
            if len(groups) != 1: state = "NO_CAPACITY"
            else:
                raw = groups[0].get("ivtff_group_raw", "")
                state = "KNOWN" if re.fullmatch(r"[a-z]+", raw) and groups[0].get("left_separator") == "LINE_START" and groups[0].get("right_separator") == "LINE_END" else "UNKNOWN"
            pos = int(locus.rsplit(".", 1)[1])
            found[locus] = {"edition": edition, "page": "f66r", "physical_leaf": "f66", "position_top_down": pos, "locus": locus, "state": state, "groups": groups, "raw": " | ".join(g.get("ivtff_group_raw", "") for g in groups), "source": EVAL[edition]}
        if set(found) != {f"f66r.{i}" for i in range(1, 16)}: err(errors, "TARGET_POSITION_SET", edition=edition, actual=sorted(found))
        for i in range(1, 16):
            row = found.get(f"f66r.{i}")
            if row is None: continue
            if row["state"] == "NO_CAPACITY" or (i in expected_unknown[edition]) != (row["state"] == "UNKNOWN"): err(errors, "TARGET_STATE", edition=edition, position=i, state=row["state"])
            rows.append(row)
    return rows

def compare_targets(artifact, expected, errors):
    if artifact != expected: err(errors, "TARGET_RECORDS_MISMATCH", expected_count=len(expected), actual_count=len(artifact))
    else:
        for row, exp in zip(artifact, expected):
            if row != exp: err(errors, "TARGET_RECORD_MISMATCH", edition=exp["edition"], locus=exp["locus"])

def solve(charts, targets, direction):
    ordered = targets if direction == "TOP_DOWN" else list(reversed(targets))
    keep = []
    constraints = []
    for idx, c in enumerate(charts):
        ok = True
        for j in range(15):
            if ordered[j]["state"] != "KNOWN": continue
            for i in range(j):
                if ordered[i]["state"] != "KNOWN": continue
                want_equal = ordered[i]["raw"] == ordered[j]["raw"]
                if (c[i] == c[j]) != want_equal:
                    ok = False
        if ok: keep.append(idx)
    # Cumulative elimination is calculated independently for the witness field.
    active = list(range(len(charts))); first = None; step = 0
    for j in range(15):
        if ordered[j]["state"] != "KNOWN": continue
        for i in range(j):
            if ordered[i]["state"] != "KNOWN": continue
            step += 1; before = len(active); eq = ordered[i]["raw"] == ordered[j]["raw"]
            active = [idx for idx in active if (charts[idx][i] == charts[idx][j]) == eq]
            if before and not active and first is None:
                first = {"case": None, "step": step, "position_a": i + 1, "position_b": j + 1, "locus_a": ordered[i]["locus"], "locus_b": ordered[j]["locus"], "raw_a": ordered[i]["raw"], "raw_b": ordered[j]["raw"], "required": "EQUAL" if eq else "DIFFERENT", "before": before, "after": 0}
    return ordered, keep, first

def read_tsv_gz(path):
    with gzip.open(path, "rt", newline="") as fh: return list(csv.DictReader(fh, delimiter="\t"))

def main():
    errors = []
    prereg = load(E / "PREREG_LOCK.json")
    for rel, expected in prereg.get("files", {}).items():
        path = ROOT / rel
        if not path.is_file(): err(errors, "LOCK_FILE_MISSING", file=rel)
        elif digest(path) != expected: err(errors, "LOCK_HASH_MISMATCH", file=rel)
    source = load(E / "src/SOURCE.json")
    if source.get("pairs_1based") != [[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13,14]]: err(errors, "PAIR_PROGRAM_MISMATCH")
    charts = all_charts()
    if len(charts) != 65536 or len(set(charts)) != 65536: err(errors, "CHART_ENUMERATION", count=len(charts), distinct=len(set(charts)))
    target_expected = source_targets(errors)
    target_path = E / "artifacts/TARGET_RECORDS.json"
    if target_path.is_file(): compare_targets(load(target_path), target_expected, errors)
    else: err(errors, "TARGET_ARTIFACT_MISSING")
    by_ed = {ed: sorted([r for r in target_expected if r["edition"] == ed], key=lambda r: r["position_top_down"]) for ed in EDITIONS}
    cases = []
    for ed in EDITIONS:
        for direction in DIRECTIONS:
            ordered, survivors, first = solve(charts, by_ed[ed], direction)
            known = sum(x["state"] == "KNOWN" for x in ordered); unknown = sum(x["state"] == "UNKNOWN" for x in ordered); no_cap = any(x["state"] == "NO_CAPACITY" for x in ordered)
            status = "NO_CAPACITY" if no_cap else "CONTRADICTED" if not survivors else "UNRESOLVED_ONLY" if unknown else "COMPATIBLE_HYPOTHETICAL_CALCULATIONS"
            if first: first["case"] = f"{ed}_{direction}"
            cases.append({"case": f"{ed}_{direction}", "edition": ed, "direction": direction, "status": status, "surviving_calculations": len(survivors), "known_positions": known, "unknown_positions": unknown, "known_types": len({x["raw"] for x in ordered if x["state"] == "KNOWN"}), "physical_leaves": 1, "independent_confirmation_leaves": 0, "first_elimination": first, "surviving_ids": survivors})
    cases_path = E / "artifacts/ALL_CASES.json"
    if cases_path.is_file() and load(cases_path) != cases: err(errors, "ALL_CASES_MISMATCH")
    elif not cases_path.is_file(): err(errors, "ALL_CASES_MISSING")
    # Complete per-position domains, independently generated from survivors.
    expected_domains = []
    names = {x["value"]: x["name"] for x in source.get("figures", [])}
    for case in cases:
        ordered = by_ed[case["edition"]] if case["direction"] == "TOP_DOWN" else list(reversed(by_ed[case["edition"]]))
        for pos, target in enumerate(ordered, 1):
            vals = sorted({charts[i][pos-1] for i in case["surviving_ids"]})
            expected_domains.append({"case": case["case"], "model_position": pos, "target_locus": target["locus"], "target_raw": target["raw"], "target_state": target["state"], "possible_figures": ",".join(map(str, vals)), "possible_names": " | ".join(names[v] for v in vals), "candidate_count": len(case["surviving_ids"]), "independent_confirmation_leaves": 0})
    pos_path = E / "artifacts/POSITION_CONSEQUENCES.tsv"
    if pos_path.is_file():
        actual = list(csv.DictReader(pos_path.open(encoding="utf-8"), delimiter="\t"))
        if actual != [{k: str(v) for k,v in row.items()} for row in expected_domains]: err(errors, "POSITION_DOMAINS_MISMATCH", expected=len(expected_domains), actual=len(actual))
    else: err(errors, "POSITION_DOMAINS_MISSING")
    # Exhaustive chart gzip and surviving-row gzip are checked without a runner.
    pred_path = E / "artifacts/ALL_SOURCE_PREDICTIONS.tsv.gz"
    if pred_path.is_file():
        rows = read_tsv_gz(pred_path)
        if len(rows) != 65536 or any(int(r["candidate_id"]) != i or tuple(int(r[f"figure_{j}"]) for j in range(1,16)) != charts[i] for i,r in enumerate(rows)): err(errors, "SOURCE_PREDICTIONS_MISMATCH", rows=len(rows))
    else: err(errors, "SOURCE_PREDICTIONS_MISSING")
    surv_expected = [(c["case"], idx, *charts[idx]) for c in cases for idx in c["surviving_ids"]]
    surv_path = E / "artifacts/ALL_SURVIVING_CALCULATIONS.tsv.gz"
    if surv_path.is_file():
        rows = read_tsv_gz(surv_path); actual = [(r["case"], int(r["candidate_id"]), *[int(r[f"figure_{j}"]) for j in range(1,16)]) for r in rows]
        if actual != surv_expected: err(errors, "SURVIVING_CALCULATIONS_MISMATCH", expected=len(surv_expected), actual=len(actual))
    else: err(errors, "SURVIVING_CALCULATIONS_MISSING")
    # Equality/inequality constraints are invariant under every injective
    # renaming of the observed labels.  Check several deterministic renamings.
    rename_ok = True
    for c in cases:
        ordered = by_ed[c["edition"]] if c["direction"] == "TOP_DOWN" else list(reversed(by_ed[c["edition"]]))
        labels = [x["raw"] if x["state"] == "KNOWN" else None for x in ordered]
        distinct = list(dict.fromkeys(x for x in labels if x is not None))
        for perm in (list(reversed(distinct)), distinct[1:] + distinct[:1] if distinct else []):
            mapping = dict(zip(distinct, perm)); renamed = [mapping.get(x) for x in labels]
            a = [i for i, chart_row in enumerate(charts) if all((renamed[i0] is None or renamed[j] is None or ((chart_row[i0] == chart_row[j]) == (renamed[i0] == renamed[j]))) for j in range(15) for i0 in range(j))]
            # Use the same known-position solver relation; renamed labels must
            # preserve survivor count (and here, the exact IDs).
            if len(a) != len(c["surviving_ids"]): rename_ok = False
    if not rename_ok: err(errors, "AGNOSTIC_RENAMING_INVARIANCE")
    result = {"experiment": "GDT957", "status": "PASS" if not errors else "FAIL", "independent": True, "charts": len(charts), "target_records": len(target_expected), "cases": [{k:v for k,v in c.items() if k != "first_elimination"} for c in cases], "agnostic_renaming_invariant": rename_ok, "it16_all15_unique": all(c["edition"] == "IT2a" and c["surviving_calculations"] == 16 and c["known_positions"] == 15 and c["unknown_positions"] == 0 for c in cases if c["edition"] == "IT2a"), "errors": errors, "meaning_validated": False, "confirmed_words": 0, "significance": "NOT_ASSESSED_NO_GLOBAL_SEARCH_NULL"}
    out = E / "artifacts/VALIDATION.json"; out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if not errors else 1

if __name__ == "__main__": raise SystemExit(main())
