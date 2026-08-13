#!/usr/bin/env python3
"""Frozen counterfactual refits of the causal context mixer."""

import csv, json, random

from gdt001_controls import CONTROL_NAMES, seed_for, transform
from gdt001_core import ROOT, LETTERS, canonical, load_lattice
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_online_context_mixer import fit


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); share = json.loads((ROOT / "gdt001_online_context_mixer_results.json").read_text())["best"]["share"]
    rows = [{"manuscript": "REAL", **{key:value for key,value in fit(lines, paths, share).items() if key != "decoder"}}]
    alphabet = list(LETTERS); permuted = list(alphabet); random.Random(seed_for("BOUNDARY_PRESERVING_IDENTITY_PERMUTATION", "GLOBAL", 9401)).shuffle(permuted); rename = dict(zip(alphabet, permuted))
    for name in CONTROL_NAMES:
        rare = "".join(sorted(rename[char] for char in "juz")) if name == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION" else "juz"
        rows.append({"manuscript": name, **{key:value for key,value in fit(lines, transform(lines, paths, name), share, rare).items() if key != "decoder"}})
    # Compare mixer to the already matched variable-context refit in controls
    # where available; exact real comparison is in every row itself.
    old = json.loads((ROOT / "gdt001_variable_context_control_results.json").read_text())
    old_by = {"REAL": old["real"]["total_bits"], **{row["manuscript"]: row["total_bits"] for row in old["controls"]}}
    for row in rows: row["gain_vs_matched_variable_context_bits"] = old_by[row["manuscript"]] - row["total_bits"]
    best_control = max(row["gain_vs_matched_variable_context_bits"] for row in rows[1:])
    decision = "CONTINUE_REAL_SPECIFIC_CONTEXT_MIXER" if rows[0]["gain_vs_matched_variable_context_bits"] > best_control else "STOP_CONTROL_MATCHES_CONTEXT_MIXER"
    output = {"schema": "GDT001_ONLINE_CONTEXT_MIXER_CONTROLS_V1", "status": "EXPLORATORY_CONTROL", "decision": decision,
              "real": rows[0], "controls": rows[1:], "claim_ceiling": "Counterfactual source-compression specificity only; no language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_online_context_mixer_control_results.json").write_bytes(canonical(output))
    with (ROOT / "gdt001_online_context_mixer_control_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "rows": [(row["manuscript"], round(row["gain_vs_matched_variable_context_bits"], 3)) for row in rows]}))


if __name__ == "__main__": main()
