#!/usr/bin/env python3
"""Recompute exact-form position tendencies on DIC001 drawing segments."""

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
SPEC = HERE / "DRAWING_SEGMENT_POSITION_REANALYSIS_SPEC.md"; SCRIPT = Path(__file__).resolve()
OUT = RES / "drawing_segment_group_position_atlas.tsv"; OUT_JSON = RES / "drawing_segment_group_position_atlas.json"
REPORT = RES / "drawing_segment_group_position_atlas_report.md"
SEGMENT_SHA = "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486"
OLD_SHA = "c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff"
CONTRASTS = {"FIRST_LAST": ("FIRST", "LAST"), "EDGE_CORE": ("EDGE", "CORE")}
FIELDS = ["family_surface", "total_count", "physical_folios", "old_first_last_label", "new_first_last_label",
          "first_last_support", "first_last_log_odds_ratio", "first_last_positive_folds", "first_last_negative_folds",
          "old_edge_core_label", "new_edge_core_label", "edge_core_support", "edge_core_log_odds_ratio",
          "edge_core_positive_folds", "edge_core_negative_folds", "first_count", "last_count", "core_count", "single_count"]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page):
    found = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not found: raise ValueError(page)
    return found.group(1)


def contrast(position, name):
    if name == "FIRST_LAST": return position if position in {"FIRST", "LAST"} else None
    if position in {"FIRST", "LAST"}: return "EDGE"
    return "CORE" if position == "CORE" else None


def odds(a, b, c, d): return math.log((a + .5) / (b + .5)) - math.log((c + .5) / (d + .5))


def main():
    if sha(SEGMENTS) != SEGMENT_SHA or sha(OLD) != OLD_SHA: raise SystemExit("position reanalysis input drift")
    with SEGMENTS.open(newline="") as handle: source = [row for row in csv.DictReader(handle, delimiter="\t") if row["grammar_scope"] == "CONFIRMED_PROSE"]
    with OLD.open(newline="") as handle: old = {row["family_surface"]: row for row in csv.DictReader(handle, delimiter="\t")}
    rows = [{"surface": row["family_surface"], "folio": folio(row["page"]), "role": row["segment_position"],
             "old_role": row["factual_position"]} for row in source]
    if len(rows) != 21899 or len(old) != 2856: raise SystemExit("position universe drift")
    folios = sorted({row["folio"] for row in rows}); surfaces = sorted({row["surface"] for row in rows})
    global_cells = {}; folio_cells = {}; surface_cells = {}; surface_folio = {}
    for name in CONTRASTS:
        global_cells[name] = Counter(); folio_cells[name] = defaultdict(Counter); surface_cells[name] = defaultdict(Counter)
        surface_folio[name] = defaultdict(lambda: defaultdict(Counter))
        for row in rows:
            state = contrast(row["role"], name)
            if state is None: continue
            global_cells[name][state] += 1; folio_cells[name][row["folio"]][state] += 1
            surface_cells[name][row["surface"]][state] += 1; surface_folio[name][row["surface"]][row["folio"]][state] += 1
    by_surface = defaultdict(list)
    for row in rows: by_surface[row["surface"]].append(row)
    output = []
    for surface in surfaces:
        observed = by_surface[surface]; roles = Counter(row["role"] for row in observed); nfolios = len({row["folio"] for row in observed})
        record = {"family_surface": surface, "total_count": len(observed), "physical_folios": nfolios,
                  "old_first_last_label": old[surface]["first_last_label"], "old_edge_core_label": old[surface]["edge_core_label"],
                  "first_count": roles["FIRST"], "last_count": roles["LAST"], "core_count": roles["CORE"], "single_count": roles["SINGLE"]}
        eligible = len(observed) >= 20 and nfolios >= 10
        for name, (positive, negative) in CONTRASTS.items():
            cells = surface_cells[name][surface]; totals = global_cells[name]
            a, b = cells[positive], cells[negative]; c, d = totals[positive] - a, totals[negative] - b
            coefficient = odds(a, b, c, d); folds = []
            for held in folios:
                own = surface_folio[name][surface][held]; all_held = folio_cells[name][held]
                folds.append(odds(a - own[positive], b - own[negative], c - (all_held[positive] - own[positive]), d - (all_held[negative] - own[negative])))
            pos = sum(value > 0 for value in folds); neg = sum(value < 0 for value in folds); support = a + b
            label = "INSUFFICIENT"
            if eligible and support >= 20:
                label = positive + "_ASSOCIATED" if coefficient >= 1 and pos >= 90 else negative + "_ASSOCIATED" if coefficient <= -1 and neg >= 90 else "UNRESOLVED"
            prefix = name.lower(); record.update({f"new_{prefix}_label": label, f"{prefix}_support": support,
                f"{prefix}_log_odds_ratio": coefficient, f"{prefix}_positive_folds": pos, f"{prefix}_negative_folds": neg})
        output.append(record)
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(output)
    role_old = Counter(row["old_role"] for row in rows); role_new = Counter(row["role"] for row in rows)
    transitions = {name: Counter() for name in CONTRASTS}; changed_occurrences = {name: 0 for name in CONTRASTS}
    for record in output:
        for name in CONTRASTS:
            a = record["old_" + name.lower() + "_label"]; b = record["new_" + name.lower() + "_label"]
            transitions[name][a + "->" + b] += 1
            if a != b: changed_occurrences[name] += int(record["total_count"])
    changed = {name: [record for record in output if record["old_" + name.lower() + "_label"] != record["new_" + name.lower() + "_label"]] for name in CONTRASTS}
    result = {
        "experiment": "DRAWING_SEGMENT_GROUP_POSITION_REANALYSIS", "status": "PASS_COMPLETE_POSITION_TAG_CORRECTION_AUDIT",
        "inputs": {path.name: sha(path) for path in (SEGMENTS, OLD, SPEC, SCRIPT)},
        "counts": {"groups": len(rows), "forms": len(output), "folios": len(folios), "old_roles": dict(sorted(role_old.items())), "segment_roles": dict(sorted(role_new.items())),
                   "changed_form_types": {name: len(changed[name]) for name in CONTRASTS}, "changed_form_occurrences": changed_occurrences,
                   "label_transitions": {name: dict(sorted(transitions[name].items())) for name in CONTRASTS}},
        "changed_first_last": changed["FIRST_LAST"], "changed_edge_core": changed["EDGE_CORE"], "atlas_sha256": sha(OUT),
        "separately_confirmatory": False, "english_glosses": 0,
        "claim_ceiling": "Drawing-segment correction of exact-form position tendencies only; no word, POS, sentence role, meaning, plaintext, language, cipher, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Drawing-segment exact-form position reanalysis\n\n" f"Status: **{result['status']}**.\n\n"
        f"The corrected **{len(rows):,}**-group universe has segment roles {dict(sorted(role_new.items()))}, versus original physical-locus roles {dict(sorted(role_old.items()))}. The unchanged classification rule changes **{len(changed['FIRST_LAST'])}** of **{len(output):,}** exact-form FIRST/LAST labels and **{len(changed['EDGE_CORE'])}** EDGE/CORE labels.\n\n"
        "This updates descriptive structural tags only and supplies no word, POS, meaning, plaintext, or translation.\n")
    print(json.dumps({"old_roles": dict(role_old), "new_roles": dict(role_new), "changed_types": {name: len(changed[name]) for name in CONTRASTS}, "changed_occurrences": changed_occurrences,
                      "transitions": {name: dict(transitions[name]) for name in CONTRASTS}}, indent=2, sort_keys=True))


if __name__ == "__main__": main()
