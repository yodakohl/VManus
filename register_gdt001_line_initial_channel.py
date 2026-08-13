#!/usr/bin/env python3
"""Idempotently register the stopped literal line-initial language screen."""

import csv
import hashlib
import json

from gdt001_core import ROOT, canonical


PREFIX = "lineinitial_"


def main():
    path = ROOT / "GDT001_YOLO_LEDGER.tsv"
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames
        rows = [row for row in reader if not row["run_id"].startswith(PREFIX)]
    result = json.loads((ROOT / "gdt001_line_initial_channel_results.json").read_text())
    for item in result["rows"]:
        config = {"schema": result["schema"], "language": item["language"],
                  "order": item["order"], "seed": item["seed"],
                  "scope": result["scope"], "initial_stream_sha256": result["initial_stream_sha256"]}
        rows.append({
            "run_id": f"{PREFIX}{item['language']}_o{item['order']}_s{item['seed']}",
            "model_class": "HYBRID",
            "language_or_system": f"LITERAL_PROSE_LINE_INITIAL_{item['language'].upper()}",
            "seed": str(item["seed"]),
            "config_hash": hashlib.sha256(canonical(config)).hexdigest(),
            "total_bits": f"{item['total_bits']:.6f}",
            "bits_per_symbol": f"{item['bits_per_symbol']:.9f}",
            "key_bits": f"{item['key_bits']:.6f}",
            "latent_bits": f"{item['initial_payload_and_reverse_bits'] + item['body_bits'] + item['rare_side_bits']:.6f}",
            "reconstruction_bits": f"{item['fixed_bits']:.6f}",
            "exception_bits": "0.000000",
            "convergence_status": "CONVERGED",
            "decoder_hash": item["decoder_hash"],
            "notes": "EXPLORATORY; CONFIRMED_PROSE_LITERAL_LINE_INITIAL_CHANNEL; EXACT_RETAINED_MAP_SCORE; HEURISTIC_SEARCH; MATCHED_ANONYMOUS_LOSS; UNSTABLE_SUPPORTED_MAP",
        })
    if len({row["run_id"] for row in rows}) != len(rows):
        raise AssertionError("duplicate run id")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "registered": len(result["rows"])}))


if __name__ == "__main__":
    main()
