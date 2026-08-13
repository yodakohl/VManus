#!/usr/bin/env python3
"""Register the compact boundary/source follow-up in the branch-local ledger."""

import csv, hashlib, json
from pathlib import Path

from gdt001_core import canonical

ROOT = Path(__file__).resolve().parent
PREFIXES = ("boundaryrule_", "rolesource_", "metasource_", "sparsemeta_", "contextaxis_")


def row(run_id, model_class, system, seed, config, total, bps, key, latent, reconstruction, decoder, notes):
    return {"run_id": run_id, "model_class": model_class, "language_or_system": system, "seed": str(seed),
            "config_hash": hashlib.sha256(canonical(config)).hexdigest(), "total_bits": f"{total:.6f}",
            "bits_per_symbol": f"{bps:.9f}", "key_bits": f"{key:.6f}", "latent_bits": f"{latent:.6f}",
            "reconstruction_bits": f"{reconstruction:.6f}", "exception_bits": "0.000000",
            "convergence_status": "CONVERGED", "decoder_hash": decoder, "notes": notes}


def main():
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open(newline="", encoding="utf-8") as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    ledger = [r for r in ledger if not r["run_id"].startswith(PREFIXES)]
    b = json.loads((ROOT / "gdt001_boundary_rule_results.json").read_text())
    for r in b["rows"]:
        candidate = "null" if r["model"] == "MATCHED_BOUNDARY_NULL" else r["language"]
        rid = f"boundaryrule_{r['scheme'].lower()}_{candidate}_s{r['seed']:05d}"
        ledger.append(row(rid, "NONSEMANTIC_GENERATOR" if candidate == "null" else "ABBR_LANG",
                          f"BOUNDARY_{r['scheme']}_{candidate}", r["seed"], {"model": r["model"], "scheme": r["scheme"]},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"] + r["boundary_side_bits"], r["fixed_bits"],
                          r["decoder_hash"], "EXPLORATORY; CONTEXTUAL_BOUNDARY_RULE"))
    rdata = json.loads((ROOT / "gdt001_role_conditioned_source_results.json").read_text())
    for r in rdata["rows"]:
        rid = f"rolesource_{'shared' if r['shared_process'] else 'split'}_o{r['order']}"
        ledger.append(row(rid, "NONSEMANTIC_GENERATOR", "LINE_ROLE_SOURCE", 0,
                          {"shared": r["shared_process"], "order": r["order"]}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["structure_bits"] + r["payload_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; REVERSIBLE_LINE_ROLE_SOURCE"))
    mdata = json.loads((ROOT / "gdt001_metadata_conditioned_source_results.json").read_text())
    for r in mdata["rows"]:
        rid = f"metasource_{r['variant'].lower()}_{r['conditioning'].lower()}_o{r['order']}"
        ledger.append(row(rid, "NONSEMANTIC_GENERATOR", f"METADATA_{r['variant']}_{r['conditioning']}", 0,
                          {"variant": r["variant"], "conditioning": r["conditioning"], "order": r["order"]},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"] + r["side_channel_bits"],
                          r["fixed_bits"], r["decoder_hash"], "EXPLORATORY; METADATA_CONDITIONED_SOURCE"))
    sdata = json.loads((ROOT / "gdt001_sparse_metadata_source_results.json").read_text())
    for r in sdata["rows"]:
        rid = f"sparsemeta_{r['axis'].lower()}_o{r['order']}"
        ledger.append(row(rid, "NONSEMANTIC_GENERATOR", f"SPARSE_{r['axis']}_SOURCE", 0,
                          {"axis": r["axis"], "order": r["order"]}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"] + r["side_channel_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; SPARSE_METADATA_SOURCE"))
    cdata = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())
    for r in cdata["rows"]:
        rid = f"contextaxis_o{r['order']}"
        ledger.append(row(rid, "NONSEMANTIC_GENERATOR", "SPARSE_CONTEXT_AXIS_SOURCE", 0, {"order": r["order"]},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"] + r["side_channel_bits"],
                          r["fixed_bits"], r["decoder_hash"], "EXPLORATORY; SPARSE_PER_CONTEXT_METADATA_AXIS"))
    fields = list(ledger[0])
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(sorted(ledger, key=lambda r: r["run_id"]))
    print(json.dumps({"runs": len(ledger)}))


if __name__ == "__main__":
    main()
