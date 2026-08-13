#!/usr/bin/env python3
"""Exact total-accounting allocation and edition-sensitivity diagnostics."""

from __future__ import annotations

import csv
import json
from collections import defaultdict

from gdt001_core import ROOT, fixed_costs, load_lattice, source_symbol_count, train_ngram_logprob
from gdt001_nonsemantic_models import predictive_path_bits


def main():
    _, lines = load_lattice(); index = json.loads((ROOT / "candidates/index.json").read_text())["candidates"]
    rows = []
    for item in index:
        run = json.loads((ROOT / ".gdt001/runs" / f"{item['candidate_id']}.json").read_text())
        chosen = dict(zip((line.locus for line in lines), run["selected_path_ids"])); selected = [next(path for path in line.paths if path.path_id == chosen[line.locus]) for line in lines]
        fixed_total = sum(fixed_costs(selected).values()); symbols_total = source_symbol_count(selected)
        variable = run["latent_bits"] + run["reconstruction_bits"] + run["exception_bits"] - fixed_total
        for kind, getter in (("CURRIER", lambda line: line.currier or "UNASSIGNED"), ("SECTION", lambda line: line.section or "UNASSIGNED")):
            buckets = defaultdict(list)
            for line, path in zip(lines, selected): buckets[getter(line)].append(path)
            for scope, paths in sorted(buckets.items()):
                fixed = sum(fixed_costs(paths).values()); symbols = source_symbol_count(paths); allocated = variable * symbols / symbols_total
                rows.append({"candidate_id": run["candidate_id"], "scope_type": kind, "scope": scope, "source_symbols": symbols, "fixed_observation_bits": fixed, "allocated_variable_bits": allocated, "global_model_key_bits": 0.0, "accounted_total_bits": fixed + allocated, "interpretation": "global variable code allocated proportional to source-symbol count; not a refit"})
        rows.append({"candidate_id": run["candidate_id"], "scope_type": "GLOBAL", "scope": "MODEL_CLASS_AND_KEY", "source_symbols": 0, "fixed_observation_bits": 0.0, "allocated_variable_bits": 0.0, "global_model_key_bits": run["model_class_bits"] + run["key_bits"], "accounted_total_bits": run["model_class_bits"] + run["key_bits"], "interpretation": "global nonlocal code cost"})
    with (ROOT / "gdt001_score_breakdown.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    leader = json.loads((ROOT / ".gdt001/runs/nonsemantic_ngram_o2.json").read_text()); chosen = dict(zip((line.locus for line in lines), leader["selected_path_ids"])); selected = [next(path for path in line.paths if path.path_id == chosen[line.locus]) for line in lines]
    table = train_ngram_logprob([path.source_ids for path in selected], 26, 2)
    diagnostics = []
    for edition in ("ZL3b", "IT2a", "RF1b"):
        candidates = []
        for line in lines:
            eligible = [path for path in line.paths if edition in path.editions]
            if not eligible: eligible = list(line.paths)
            candidates.append(min(eligible, key=lambda path: (predictive_path_bits(path, table, 2) + path.fixed_bits, path.path_id)))
        diagnostics.append({"edition": edition, "frozen_leader_predictive_plus_observation_bits": sum(predictive_path_bits(path, table, 2) + path.fixed_bits for path in candidates), "source_symbols": source_symbol_count(candidates), "path_digest_input_count": len(candidates), "diagnostic_only": True})
    (ROOT / "gdt001_edition_sensitivity.json").write_text(json.dumps({"schema": "GDT001_EDITION_SENSITIVITY_V1", "status": "EXPLORATORY_DIAGNOSTIC_NOT_MDL_REFIT", "leader": leader["candidate_id"], "editions": diagnostics}, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"breakdown_rows": len(rows), "edition_rows": len(diagnostics)}))


if __name__ == "__main__": main()
