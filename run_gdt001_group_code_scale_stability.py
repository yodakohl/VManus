#!/usr/bin/env python3
"""Independent restart stability for the selected 512-form Czech scale."""

import json

from gdt001_core import ROOT, canonical, fixed_costs, load_lattice
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_code_high_order import dense_costs, lm
from run_gdt001_group_code_scale import one


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(word) for path in paths for word in path.words); costs = dense_costs(lm("medieval_czech", 4), 4)
    leader = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]["total_bits"]
    existing = next(row for row in json.loads((ROOT / "gdt001_group_code_scale_results.json").read_text())["rows"] if row["k"] == 512)
    rows = [existing, one(512, 36104, paths, fixed, symbols, costs, leader), one(512, 36105, paths, fixed, symbols, costs, leader)]
    stable = len({row["decoder_hash"] for row in rows}) == 1
    output = {"schema": "GDT001_GROUP_CODE_SCALE_STABILITY_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": "CONTINUE_SCALE_STABLE" if stable else "STOP_SCALE_UNSTABLE", "rows": rows,
              "claim_ceiling": "Restart diagnostic only; no group has an established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_scale_stability.json").write_bytes(canonical(output))
    print(json.dumps({"decision": output["decision"], "rows": [{"seed": row["seed"], "total_bits": row["total_bits"], "gain": row["gain_vs_matched_null_bits"], "hash": row["decoder_hash"]} for row in rows]}))


if __name__ == "__main__": main()
