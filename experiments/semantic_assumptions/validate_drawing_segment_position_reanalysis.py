#!/usr/bin/env python3
"""Independent validation of drawing-segment exact-form position labels."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
SEGMENTS = RES / "drawing_reset_segment_atlas.tsv"; OLD = RES / "source_native_group_position_atlas.tsv"
ATLAS = RES / "drawing_segment_group_position_atlas.tsv"; RESULT = RES / "drawing_segment_group_position_atlas.json"
REPORT = RES / "drawing_segment_group_position_atlas_report.md"; SPEC = HERE / "DRAWING_SEGMENT_POSITION_REANALYSIS_SPEC.md"
PRODUCER = HERE / "build_drawing_segment_position_reanalysis.py"
OUT = RES / "drawing_segment_group_position_atlas_validation.json"; OUT_REPORT = RES / "drawing_segment_group_position_atlas_validation_report.md"
HASHES = {SEGMENTS: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
          OLD: "c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff",
          SPEC: "1c5725435a93cab88571a81ac16239b6b10eab97ef44eed38a8296d07e90810e",
          PRODUCER: "826193835ca77488a075ce2d0dbe1f8269a932269924c87b04e4233dc08fa8d9",
          ATLAS: "a36d15f9423d2c765962e4d41b683424c6fee1e72ba44b3f4da4cc8c0b34dc24",
          RESULT: "8420241428bb5905528b97a615f0e8a56450814e8e5375eb9b82de1609c711e4",
          REPORT: "2c04231d11dfb39c2a1adf932b38fe8d3d1dff4196c897889f09d4f28e56e85f"}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page):
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not match: raise AssertionError(page)
    return match.group(1)


def map_state(role, contrast):
    if contrast == "FIRST_LAST": return role if role in ("FIRST", "LAST") else None
    return "EDGE" if role in ("FIRST", "LAST") else "CORE" if role == "CORE" else None


def log_odds(a, b, c, d): return math.log((a + .5) / (b + .5)) - math.log((c + .5) / (d + .5))


def main():
    for path, wanted in HASHES.items():
        if sha(path) != wanted: raise SystemExit("input drift: " + path.name)
    with SEGMENTS.open(newline="") as handle:
        rows = [{"surface": row["family_surface"], "folio": physical_folio(row["page"]), "role": row["segment_position"], "old": row["factual_position"]}
                for row in csv.DictReader(handle, delimiter="\t") if row["grammar_scope"] == "CONFIRMED_PROSE"]
    with OLD.open(newline="") as handle: old = {row["family_surface"]: row for row in csv.DictReader(handle, delimiter="\t")}
    with ATLAS.open(newline="") as handle: stored_rows = {row["family_surface"]: row for row in csv.DictReader(handle, delimiter="\t")}
    stored_result = json.loads(RESULT.read_text())
    folios = sorted({row["folio"] for row in rows}); surfaces = sorted({row["surface"] for row in rows})
    global_count = {}; folio_count = {}; form_count = {}; form_folio = {}
    for name in ("FIRST_LAST", "EDGE_CORE"):
        global_count[name] = Counter(); folio_count[name] = defaultdict(Counter); form_count[name] = defaultdict(Counter); form_folio[name] = defaultdict(lambda: defaultdict(Counter))
        for row in rows:
            state = map_state(row["role"], name)
            if state is None: continue
            global_count[name][state] += 1; folio_count[name][row["folio"]][state] += 1
            form_count[name][row["surface"]][state] += 1; form_folio[name][row["surface"]][row["folio"]][state] += 1
    occurrences = defaultdict(list)
    for row in rows: occurrences[row["surface"]].append(row)
    errors = []; checks = 0; reconstructed = {}
    transitions = {name: Counter() for name in ("FIRST_LAST", "EDGE_CORE")}; changed_occurrences = {name: 0 for name in transitions}
    for surface in surfaces:
        observed = occurrences[surface]; roles = Counter(row["role"] for row in observed); nfolios = len({row["folio"] for row in observed})
        record = {"family_surface": surface, "total_count": len(observed), "physical_folios": nfolios,
                  "old_first_last_label": old[surface]["first_last_label"], "old_edge_core_label": old[surface]["edge_core_label"],
                  "first_count": roles["FIRST"], "last_count": roles["LAST"], "core_count": roles["CORE"], "single_count": roles["SINGLE"]}
        for name, positive, negative in (("FIRST_LAST", "FIRST", "LAST"), ("EDGE_CORE", "EDGE", "CORE")):
            cells, totals = form_count[name][surface], global_count[name]
            a, b = cells[positive], cells[negative]; c, d = totals[positive] - a, totals[negative] - b
            coefficient = log_odds(a, b, c, d); folds = []
            for held in folios:
                own, all_held = form_folio[name][surface][held], folio_count[name][held]
                folds.append(log_odds(a - own[positive], b - own[negative], c - (all_held[positive] - own[positive]), d - (all_held[negative] - own[negative])))
            positive_folds = sum(x > 0 for x in folds); negative_folds = sum(x < 0 for x in folds); support = a + b
            label = "INSUFFICIENT"
            if len(observed) >= 20 and nfolios >= 10 and support >= 20:
                label = positive + "_ASSOCIATED" if coefficient >= 1 and positive_folds >= 90 else negative + "_ASSOCIATED" if coefficient <= -1 and negative_folds >= 90 else "UNRESOLVED"
            prefix = name.lower(); record.update({"new_" + prefix + "_label": label, prefix + "_support": support,
                prefix + "_log_odds_ratio": coefficient, prefix + "_positive_folds": positive_folds, prefix + "_negative_folds": negative_folds})
            old_label = record["old_" + prefix + "_label"]; transitions[name][old_label + "->" + label] += 1
            if old_label != label: changed_occurrences[name] += len(observed)
        reconstructed[surface] = record
        actual = stored_rows.get(surface); checks += 1
        if actual is None: errors.append(surface + ":missing"); continue
        for field, value in record.items():
            checks += 1
            if field.endswith("log_odds_ratio"):
                if abs(float(actual[field]) - value) > 1e-15: errors.append(surface + ":" + field)
            elif actual[field] != str(value): errors.append(surface + ":" + field)
    checks += 1
    if set(stored_rows) != set(reconstructed): errors.append("surface set")
    old_roles = Counter(row["old"] for row in rows); new_roles = Counter(row["role"] for row in rows)
    changed_types = {name: sum(a.split("->")[0] != a.split("->")[1] for a, count in transitions[name].items() for _ in range(count)) for name in transitions}
    expected_counts = {"groups": len(rows), "forms": len(surfaces), "folios": len(folios), "old_roles": dict(sorted(old_roles.items())), "segment_roles": dict(sorted(new_roles.items())),
        "changed_form_types": changed_types, "changed_form_occurrences": changed_occurrences, "label_transitions": {name: dict(sorted(transitions[name].items())) for name in transitions}}
    checks += 1
    if stored_result["counts"] != expected_counts: errors.append("result counts")
    checks += 1
    if stored_result["atlas_sha256"] != sha(ATLAS): errors.append("result atlas hash")
    expected_report = "# Drawing-segment exact-form position reanalysis\n\n" f"Status: **{stored_result['status']}**.\n\n" f"The corrected **{len(rows):,}**-group universe has segment roles {dict(sorted(new_roles.items()))}, versus original physical-locus roles {dict(sorted(old_roles.items()))}. The unchanged classification rule changes **{changed_types['FIRST_LAST']}** of **{len(surfaces):,}** exact-form FIRST/LAST labels and **{changed_types['EDGE_CORE']}** EDGE/CORE labels.\n\n" "This updates descriptive structural tags only and supplies no word, POS, meaning, plaintext, or translation.\n"
    checks += 1
    if REPORT.read_text() != expected_report: errors.append("report")
    validation = {"experiment": "DRAWING_SEGMENT_GROUP_POSITION_REANALYSIS_VALIDATION", "status": "PASS" if not errors else "FAIL", "assertions": checks,
                  "discrepancies": errors, "reconstructed_counts": expected_counts, "atlas_sha256": sha(ATLAS),
                  "claim_ceiling": stored_result["claim_ceiling"]}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text("# Drawing-segment position reanalysis validation\n\n" f"Status: **{validation['status']}** with **{checks:,}** checks and **{len(errors)}** discrepancies.\n")
    print(json.dumps(validation, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
