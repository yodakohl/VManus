#!/usr/bin/env python3
"""Fit representative GDT001 model families to five frozen counterfactuals."""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path

from gdt001_core import ROOT, canonical, load_lattice
from gdt001_controls import CONTROL_NAMES, manifest, transform
from gdt001_language_models import fit_language_candidate
from gdt001_nonsemantic_models import fit_ngram
from gdt001_record_models import fit_record_notation


OUT = ROOT / "gdt001_counterfactual_results.json"
TSV = ROOT / "gdt001_counterfactual_results.tsv"
MANIFEST = ROOT / "gdt001_counterfactual_manifest.json"
CACHE = ROOT / ".gdt001/control_runs_v2"


def main() -> None:
    _, lines = load_lattice()
    flat_lines = [line for line in lines for _ in line.paths]
    flat_paths = [path for line in lines for path in line.paths]
    MANIFEST.write_bytes(canonical(manifest(flat_lines, flat_paths)))
    CACHE.mkdir(parents=True, exist_ok=True)
    results = []
    for control in CONTROL_NAMES:
        paths = transform(flat_lines, flat_paths, control)
        offset = 0; control_lines = []
        for line in lines:
            count = len(line.paths)
            control_lines.append(replace(line, paths=tuple(paths[offset:offset + count])))
            offset += count
        if offset != len(paths):
            raise AssertionError("counterfactual lattice regrouping drift")
        models = [
            ("NONSEMANTIC_2GRAM", lambda: fit_ngram(control_lines, 2)),
            ("RECORD_NOTATION", lambda: fit_record_notation(control_lines, False)),
            ("ABBR_LANG_MHG", lambda: fit_language_candidate(
                control_lines, "middle_high_german", "ABBR_LANG", 7301,
                population_size=32768, generations=30, cuda=True,
            )),
            ("HOMOPHONIC_MHG", lambda: fit_language_candidate(
                control_lines, "middle_high_german", "HOMOPHONIC_CIPHER", 7301,
                population_size=32768, generations=30, cuda=True,
            )),
        ]
        for label, function in models:
            cache = CACHE / f"{control.lower()}__{label.lower()}.json"
            if cache.exists():
                result = json.loads(cache.read_text())
            else:
                result = function()
                cache.write_bytes(canonical(result))
            results.append({
                "control": control, "model": label, "candidate_id": result["candidate_id"],
                "total_bits": result["total_bits"], "bits_per_symbol": result["bits_per_symbol"],
                "key_bits": result["key_bits"], "latent_bits": result["latent_bits"],
                "reconstruction_bits": result["reconstruction_bits"], "decoder_hash": result["decoder_hash"],
            })
    payload = {
        "schema": "GDT001_COUNTERFACTUAL_RESULTS_V2", "status": "EXPLORATORY_CONTROL",
        "manifest_sha256": __import__("hashlib").sha256(MANIFEST.read_bytes()).hexdigest(),
        "results": results,
        "interpretation": "Lower bits are better. Language-like behavior on controls comparable to the real manuscript is evidence against decipherment specificity.",
    }
    OUT.write_bytes(canonical(payload))
    fields = list(results[0])
    with TSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(results)
    print(json.dumps({"rows": len(results), "result_sha256": __import__("hashlib").sha256(OUT.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
