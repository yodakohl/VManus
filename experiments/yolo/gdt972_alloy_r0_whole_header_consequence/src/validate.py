#!/usr/bin/env python3
"""Independent validator for GDT972.

No target cache is opened unless --full is used after public registration.
Default operation is registration-only, so a manifest can run safely before
PARAGRAPHS/RESULT are available or approved for inspection.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[2]
PREREG = ROOT / "PREREGISTRATION.md"
GRAMMAR = REPO_ROOT / "research_registry/work_batches/ten_hours_20260915/ALLOY_FINITE_GRAMMAR.json"
# Relative repository path only; no private machine path is embedded.
PARAGRAPHS = REPO_ROOT / "experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json"
RESULT = ROOT / "artifacts" / "RESULT.json"

ATOM_COUNT = 38
ATOM_MIN, ATOM_MAX = 1, 8
NUM_MIN, NUM_MAX = 2, 32
HEADER_ATOMIC = (0, 1, 3, 5, 7, 9, 11)
HEADER_NUMERIC = (2, 4, 6, 8, 10)
GRADE_TARGET = (2, 4, 6, 8)
CRITERIA = ("MIN_GROUPS", "ATOMIC_WIDTH", "ATOMIC_DISTINCT", "ATOMIC_PREFIX_FREE",
            "NUMERIC_WIDTH", "GRADE_DISTINCT", "NUM_PREFIX_DOMAIN")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def is_prefix(a: str, b: str) -> bool:
    return b.startswith(a)


def candidate_num_prefixes(words: list[str], atomic: list[str]):
    if len(words) != 5 or any(not isinstance(w, str) for w in words):
        return []
    out = []
    for n in range(ATOM_MIN, ATOM_MAX + 1):
        prefix = words[0][:n]
        if len(prefix) != n or not all(w.startswith(prefix) for w in words):
            continue
        if not all(n < len(w) for w in words):
            continue
        if any(is_prefix(prefix, a) or is_prefix(a, prefix) for a in atomic):
            continue
        # Retain every candidate; no candidate is selected by score or order.
        out.append({"prefix": prefix, "length": n,
                    "suffix_lengths": [len(w[n:]) for w in words],
                    "suffix_chunk_counts": [list(range(max(1, (len(w[n:]) + 7) // 8), min(3, len(w[n:])) + 1)) for w in words]})
    return out


def evaluate_header(groups, eligible):
    nulls = {c: None for c in CRITERIA}
    if not eligible or not isinstance(groups, list):
        return {"criteria": nulls, "candidates": [], "overall": None, "first_failure": "UNKNOWN_NONLITERAL_COMPLETE"}
    words = groups[:12]
    criteria = {c: None for c in CRITERIA}
    criteria["MIN_GROUPS"] = len(groups) >= 14
    if len(words) < 12:
        return {"criteria": criteria, "candidates": [], "overall": False, "first_failure": "MIN_GROUPS",
                "header_words": words, "atomic_positions": list(HEADER_ATOMIC), "numeric_positions": list(HEADER_NUMERIC)}
    atomic = [words[i] for i in HEADER_ATOMIC]
    numeric = [words[i] for i in HEADER_NUMERIC]
    criteria["ATOMIC_WIDTH"] = all(isinstance(w, str) and ATOM_MIN <= len(w) <= ATOM_MAX for w in atomic)
    criteria["ATOMIC_DISTINCT"] = len(set(atomic)) == len(atomic)
    criteria["ATOMIC_PREFIX_FREE"] = all(isinstance(a, str) and isinstance(b, str) and not is_prefix(a, b) and not is_prefix(b, a) for i, a in enumerate(atomic) for b in atomic[i+1:])
    criteria["NUMERIC_WIDTH"] = all(isinstance(w, str) and NUM_MIN <= len(w) <= NUM_MAX for w in numeric)
    criteria["GRADE_DISTINCT"] = len({numeric[i] for i in range(4)}) == 4
    candidates = candidate_num_prefixes(numeric, atomic)
    criteria["NUM_PREFIX_DOMAIN"] = bool(candidates)
    false_rules = [c for c in CRITERIA if criteria[c] is False]
    first_failure = false_rules[0] if false_rules else "NECESSARY_HEADER_ONLY"
    return {"criteria": criteria, "candidates": candidates, "overall": all(criteria.values()), "first_failure": first_failure,
            "header_words": words, "atomic_positions": list(HEADER_ATOMIC), "numeric_positions": list(HEADER_NUMERIC)}


def row_groups(row):
    """Reconstruct groups and require full_text/flattened-line agreement."""
    if not isinstance(row, dict):
        return None
    full = row.get("full_text")
    full_groups = full.split(" ") if isinstance(full, str) else None
    lines = row.get("lines")
    line_groups = None
    if isinstance(lines, list):
        flattened = []
        for line in lines:
            if not isinstance(line, dict) or not isinstance(line.get("words"), list):
                return None
            if not all(isinstance(word, str) for word in line["words"]):
                return None
            flattened.extend(line["words"])
        line_groups = flattened
    if full_groups is not None and line_groups is not None and full_groups != line_groups:
        raise ValueError("full_text does not equal flattened line words")
    return full_groups if full_groups is not None else line_groups


def normalize_rows(payload):
    if isinstance(payload, list):
        return [(None, row) for row in payload], []
    if isinstance(payload, dict):
        for key in ("paragraphs", "rows", "records", "items"):
            if isinstance(payload.get(key), list):
                return [(None, row) for row in payload[key]], []
        # GDT970's frozen packaging is edition -> paragraph-list. Preserve
        # insertion order, including an empty edition such as RF.
        pairs = []
        editions = []
        for edition, values in payload.items():
            if not isinstance(values, list):
                raise ValueError("edition mapping contains a non-list value")
            editions.append(edition)
            pairs.extend((edition, row) for row in values)
        if editions:
            return pairs, editions
    raise ValueError("PARAGRAPHS schema has no recognized row list")


def independent_rows(payload):
    pairs, editions = normalize_rows(payload)
    out = []
    for idx, (edition, row) in enumerate(pairs):
        groups = row_groups(row)
        raw_eligible = row.get("literal_eligible") if isinstance(row, dict) else None
        if isinstance(raw_eligible, bool):
            eligible = raw_eligible
        else:
            eligible = False
        ev = evaluate_header(groups, eligible)
        cond = ev["criteria"]
        rec = {"edition": edition if edition is not None else (row.get("edition") if isinstance(row, dict) else None),
               "id": row.get("id") if isinstance(row, dict) else None,
               "page": row.get("page") if isinstance(row, dict) else None,
               "leaf": row.get("leaf") if isinstance(row, dict) else None,
               "eligible": eligible,
               "defects": row.get("defects", []) if isinstance(row, dict) and isinstance(row.get("defects", []), list) else [],
               "group_count": len(groups) if groups is not None else 0,
               "header": ev.get("header_words") if eligible and groups is not None else None,
               "conditions": cond,
               "num_prefixes": [x["prefix"] for x in ev["candidates"]],
               "contradictions": [c for c in CRITERIA if cond[c] is False],
               "decision": ev["first_failure"]}
        out.append(rec)
    return out, editions


def summary(rows, panel_editions=()):
    survivors = [r["id"] for r in rows if r["decision"] == "NECESSARY_HEADER_ONLY"]
    panels = {}
    leaf_sets = {edition: set() for edition in panel_editions}
    for edition in panel_editions:
        panels[edition] = {"complete_paragraphs": 0, "literal_paragraphs": 0,
                           "literal_leaves": 0, "unknown_nonliteral": 0,
                           "first_failure_or_survival_counts": {},
                           "all_failure_counts": {}, "survivors": [],
                           "independent_confirmation_capacity": 0}
    for r in rows:
        p = panels.setdefault(r["edition"], {"complete_paragraphs": 0, "literal_paragraphs": 0,
                                             "literal_leaves": 0, "unknown_nonliteral": 0,
                                             "first_failure_or_survival_counts": {},
                                             "all_failure_counts": {}, "survivors": [],
                                             "independent_confirmation_capacity": 0})
        p["complete_paragraphs"] += 1
        if r["eligible"]:
            p["literal_paragraphs"] += 1
            if r["leaf"] is not None:
                leaf_sets.setdefault(r["edition"], set()).add(r["leaf"])
            p["first_failure_or_survival_counts"][r["decision"]] = p["first_failure_or_survival_counts"].get(r["decision"], 0) + 1
        else:
            p["unknown_nonliteral"] += 1
        for c in CRITERIA:
            if r["conditions"].get(c) is False:
                p["all_failure_counts"][c] = p["all_failure_counts"].get(c, 0) + 1
        if r["decision"] == "NECESSARY_HEADER_ONLY":
            p["survivors"].append(r["id"])
    for edition, leaves in leaf_sets.items():
        panels[edition]["literal_leaves"] = len(leaves)
    return {"panels": panels, "complete_rows": len(rows), "literal_rows": sum(r["eligible"] for r in rows),
            "survivors": len(survivors), "independent_confirmation_capacity": 0,
            "full_code_or_arithmetic_tested": False, "translated_words": 0, "reserve_access": False,
            "status": "NECESSARY_HEADER_SURVIVORS_NO_FULL_READING" if survivors else "ALL_LITERAL_R0_HEADERS_CONTRADICTED"}


def registration_checks():
    checks = {"prereg_exists": PREREG.exists(),
              "grammar_path": str(GRAMMAR.relative_to(REPO_ROOT)), "grammar_exists": GRAMMAR.exists(),
              "bound_paragraphs_path": str(PARAGRAPHS.relative_to(REPO_ROOT)), "target_cache_opened": False}
    grammar = json.loads(GRAMMAR.read_text(encoding="utf-8")) if GRAMMAR.exists() else {}
    renderer = grammar.get("renderer", {})
    atoms = renderer.get("atoms", [])
    checks["prereg_sha256"] = sha256(PREREG) if PREREG.exists() else None
    checks["grammar_sha256"] = sha256(GRAMMAR) if GRAMMAR.exists() else None
    checks["atom_count"] = len(atoms) == ATOM_COUNT
    checks["atom_set_unique"] = len(atoms) == len(set(atoms))
    checks["atom_bounds"] = renderer.get("min_atom_code_length") == 1 and renderer.get("max_atom_code_length") == 8
    checks["prefix_free_declared"] = renderer.get("one_global_prefix_free_code") is True
    checks["shared_digits_declared"] = renderer.get("digit_codes_shared_across_numerals_and_references") is True
    checks["grammar_limits"] = grammar.get("limits", {}) == {"branches": 3, "statements_per_branch": 20, "registers_per_type": 8, "expression_depth": 6, "numeric_literal_max": 400, "rational_denominator_max": 400}
    checks["status"] = "PASS_REGISTRATION_ONLY" if all(checks[k] for k in ("prereg_exists", "grammar_exists", "atom_count", "atom_set_unique", "atom_bounds", "prefix_free_declared", "shared_digits_declared", "grammar_limits")) else "FAIL_REGISTRATION_ONLY"
    return checks


def compare_primary(independent, primary, panel_editions=()):
    """Compare exact rows/summaries when the public result has been opened."""
    # The comparison intentionally requires the primary's explicit row list;
    # no expected count, survivor or success status is hardcoded.
    pred_path = ROOT / "artifacts" / "PREDICTIONS.json"
    if not pred_path.exists():
        return {"status": "FAIL", "reason": "PREDICTIONS.json_missing"}
    primary_rows = json.loads(pred_path.read_text(encoding="utf-8"))
    rows_equal = primary_rows == independent
    expected_summary = summary(independent, panel_editions)
    fields = {k: primary.get(k) == v for k, v in expected_summary.items() if k in primary}
    required = set(expected_summary)
    tab = io.StringIO()
    writer = csv.writer(tab, delimiter='\t', lineterminator='\n')
    writer.writerow(['edition','paragraph','page','physical_leaf','eligibility','groups','header',*CRITERIA,'NUM_prefixes','all_contradictions','decision','independent_confirmation'])
    compact = lambda x: json.dumps(x, separators=(',', ':'))
    for row in independent:
        writer.writerow([row['edition'],row['id'],row['page'],row['leaf'],'LITERAL' if row['eligible'] else compact(row['defects']),row['group_count'],compact(row['header']),*[str(row['conditions'][c]) for c in CRITERIA],compact(row['num_prefixes']),compact(row['contradictions']),row['decision'],0])
    table = ROOT / 'artifacts/CANDIDATE_PREDICTIONS.tsv'
    fields['table_exact'] = table.exists() and table.read_bytes() == tab.getvalue().encode()
    fields["predictions_exact"] = rows_equal
    fields["result_fields_present"] = required.issubset(primary)
    return {"status": "PASS" if rows_equal and fields["result_fields_present"] and all(fields[k] for k in fields if k not in ("result_fields_present",)) else "FAIL",
            "prediction_rows": [len(independent), len(primary_rows)], "fields": fields}


def write_validation(registration, independent, comparison):
    """Persist a compact, machine-readable independent validation receipt."""
    artifact = ROOT / "artifacts" / "VALIDATION.json"
    receipt = {
        "validator": "GDT972 independent header validator",
        "registration": registration,
        "target_cache_opened": True,
        "independent_row_count": len(independent),
        "comparison": comparison,
        "status": comparison.get("status", "FAIL"),
    }
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return artifact


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="read bound PARAGRAPHS, enumerate every row, then compare public RESULT")
    ap.add_argument("--registration-only", action="store_true", help="check only prereg/grammar bindings; never open target cache")
    args = ap.parse_args()
    reg = registration_checks()
    do_full = args.full or (not args.registration_only and RESULT.exists())
    if not do_full:
        print(json.dumps(reg, ensure_ascii=False, indent=2))
        return 0 if reg["status"] == "PASS_REGISTRATION_ONLY" else 1
    if reg['status'] != 'PASS_REGISTRATION_ONLY':
        print(json.dumps(reg)); return 1
    lock = json.loads((ROOT / 'PREREG_LOCK.json').read_text())
    for name, digest in lock['files'].items():
        assert sha256(REPO_ROOT / name) == digest, name
    spec = json.loads((REPO_ROOT / 'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json').read_text())
    allowed = set(spec['allowed_selectors'])
    assert len(allowed) == 179 and not any(x.startswith('f84') or x == 'f116v' for x in allowed)
    # Target access is intentionally after independent code and registration
    # checks.  No fields are repaired, normalized or selected.
    if not PARAGRAPHS.exists():
        print(json.dumps({"registration": reg, "status": "FAIL", "reason": "bound_PARAGRAPHS_missing"}, ensure_ascii=False, indent=2))
        return 1
    independent, panel_editions = independent_rows(json.loads(PARAGRAPHS.read_text(encoding="utf-8")))
    assert all(r['page'] in allowed and not r['page'].startswith('f84') and r['page'] != 'f116v' for r in independent)
    assert all(not r['eligible'] or all(w and all('a' <= c <= 'z' for c in w) for w in row_groups(row)) for (_, row), r in zip(normalize_rows(json.loads(PARAGRAPHS.read_text()))[0], independent))
    out = {"registration": reg, "row_count": len(independent),
           **summary(independent, panel_editions)}
    if not RESULT.exists():
        out["comparison"] = {"status": "PRIMARY_RESULT_MISSING"}
    else:
        primary = json.loads(RESULT.read_text(encoding="utf-8"))
        out["comparison"] = compare_primary(independent, primary, panel_editions)
        write_validation(reg, independent, out["comparison"])
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["comparison"]["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
