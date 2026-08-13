#!/usr/bin/env python3
"""Register the compact boundary/source follow-up in the branch-local ledger."""

import csv, hashlib, json
from pathlib import Path

from gdt001_core import canonical

ROOT = Path(__file__).resolve().parent
PREFIXES = ("boundaryrule_", "rolesource_", "metasource_", "sparsemeta_", "contextaxis_", "currierallograph_", "entrysource_", "latentline_", "exactcopy_", "wordtranspose_", "variablecontext_", "scaffoldlang_", "groupexpand_", "contexttree_", "latinscholastic_", "residualpayload_", "ranknomen_", "groupcodeho_", "groupcodeo4ref_", "groupcodescale_", "groupcodeanon_", "rootcode_")


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
    adata = json.loads((ROOT / "gdt001_currier_allography_results.json").read_text())
    for r in adata["rows"]:
        ledger.append(row(f"currierallograph_s{r['seed']}", "NONSEMANTIC_GENERATOR", "CURRIER_SOURCE_PERMUTATION", r["seed"],
                          {"model": "CURRIER_ALLOGRAPHY", "seed": r["seed"]}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"] + r["side_channel_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; REVERSIBLE_CURRIER_ALPHABET_PERMUTATION; UNSTABLE"))
    edata = json.loads((ROOT / "gdt001_entry_conditioned_source_results.json").read_text())
    for r in edata["rows"]:
        ledger.append(row(f"entrysource_{r['scheme'].lower()}_o{r['order']}", "RECORD_NOTATION", f"ENTRY_{r['scheme']}_SOURCE", 0,
                          {"scheme": r["scheme"], "order": r["order"]}, r["total_bits"], r["bits_per_symbol"], r["key_bits"],
                          r["payload_bits"] + r["side_channel_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; ENTRY_CONDITIONED_RECORD_GENERATOR"))
    ldata = json.loads((ROOT / "gdt001_latent_line_state_results.json").read_text())
    for r in ldata["rows"]:
        ledger.append(row(f"latentline_k{r['requested_k']}_s{r['seed']}", "RECORD_NOTATION", f"LATENT_LINE_STATES_K{r['requested_k']}", r["seed"],
                          {"requested_k": r["requested_k"], "seed": r["seed"]}, r["total_bits"], r["bits_per_symbol"], r["key_bits"],
                          r["state_assignment_bits"] + r["emission_bits"] + r["side_channel_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; GPU_PROPOSAL_CPU_EXACT; LATENT_LINE_STATES"))
    xdata = json.loads((ROOT / "gdt001_exact_copy_cache_results.json").read_text())
    for r in xdata["rows"]:
        ledger.append(row(f"exactcopy_w{r['window']}_m{r['minimum_copy_length']}_o{r['literal_order']}", "NONSEMANTIC_GENERATOR", "EXACT_PAGE_COPY_CACHE", 0,
                          {"window": r["window"], "minimum": r["minimum_copy_length"], "order": r["literal_order"]},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["structure_and_index_bits"] + r["literal_bits"],
                          r["fixed_bits"], r["decoder_hash"], "EXPLORATORY; REVERSIBLE_EXACT_COPY_CACHE"))
    tdata = json.loads((ROOT / "gdt001_within_word_transposition_results.json").read_text())
    for r in tdata["rows"]:
        candidate = "null" if r["model"] == "MATCHED_TRANSPOSITION_NULL" else r["language"]
        ledger.append(row(f"wordtranspose_{r['scheme'].lower()}_{candidate}_s{r['seed']}",
                          "NONSEMANTIC_GENERATOR" if candidate == "null" else "HOMOPHONIC_CIPHER",
                          f"WORD_TRANSPOSITION_{r['scheme']}_{candidate}", r["seed"],
                          {"scheme": r["scheme"], "candidate": candidate}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; REVERSIBLE_WITHIN_WORD_TRANSPOSITION"))
    vdata = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())
    r = vdata["best"]
    ledger.append(row("variablecontext_o2", "NONSEMANTIC_GENERATOR", "VARIABLE_HISTORY_OR_METADATA_SOURCE", 0,
                      {"predictors": "HISTORY3_OR_METADATA", "base_order": 2}, r["total_bits"], r["bits_per_symbol"],
                      r["key_bits"], r["payload_bits"] + r["side_channel_bits"], r["fixed_bits"], r["decoder_hash"],
                      "EXPLORATORY; VARIABLE_CONTEXT_SOURCE; CONTROL_NOT_SPECIFIC"))
    scdata = json.loads((ROOT / "gdt001_scaffold_language_results.json").read_text())
    for r in scdata["rows"]:
        ledger.append(row(f"scaffoldlang_{r['language']}_s{r['seed']}", "ABBR_LANG", f"SCAFFOLD_CORE_{r['language']}", r["seed"],
                          {"language": r["language"], "scaffold": "PREFIX_CORE_SUFFIX"}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["scaffold_bits"] + r["language_bits"] + r["reverse_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; SHARED_SCAFFOLD_MULTILINGUAL"))
    gedata = json.loads((ROOT / "gdt001_group_expansion_results.json").read_text())
    for r in gedata["rows"]:
        candidate = "null" if r["model"] == "MATCHED_GROUP_NULL" else r["language"]
        ledger.append(row(f"groupexpand_k{r['k']}_{candidate}_s{r['seed']}",
                          "NONSEMANTIC_GENERATOR" if candidate == "null" else "ABBR_LANG",
                          f"GROUP_EXPANSION_K{r['k']}_{candidate}", r["seed"], {"k": r["k"], "candidate": candidate},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"], r["fixed_bits"],
                          r["decoder_hash"], "EXPLORATORY; COMPLETE_GROUP_ONE_OR_TWO_LETTER_EXPANSION"))
    ctdata = json.loads((ROOT / "gdt001_context_tree_source_results.json").read_text())
    for r in ctdata["rows"]:
        ledger.append(row(f"contexttree_{r['variant'].lower()}_d{r['maximum_depth']}", "NONSEMANTIC_GENERATOR",
                          f"VARIABLE_ORDER_TREE_{r['variant']}", 0, {"variant": r["variant"], "maximum_depth": r["maximum_depth"]},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"] + r["side_channel_bits"],
                          r["fixed_bits"], r["decoder_hash"], "EXPLORATORY; EXACT_CONTEXT_TREE_SOURCE"))
    lsdata = json.loads((ROOT / "gdt001_latin_scholastic_results.json").read_text())
    for r in lsdata["rows"]:
        ledger.append(row(f"latinscholastic_{r['model'].lower()}_s{r['seed']}", "ABBR_LANG", f"LATIN_SCHOLASTIC_{r['model']}", r["seed"],
                          {"model": r["model"], "pack": lsdata["pack_sha256"]}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; PINNED_MEDIEVAL_SCHOLASTIC_LATIN"))
    rpdata = json.loads((ROOT / "gdt001_residual_payload_language_results.json").read_text())
    for r in rpdata["rows"]:
        ledger.append(row(f"residualpayload_{r['language']}_s{r['seed']}", "HYBRID", f"EXCEPTIONAL_CONTEXT_PAYLOAD_{r['language']}", r["seed"],
                          {"language": r["language"], "selector": "VARIABLE_CONTEXT_EXCEPTIONS"}, r["total_bits"], r["bits_per_symbol"],
                          r["base_key_bits"] + r["payload_key_bits"], r["other_source_bits"] + r["language_and_reverse_bits"] + r["rare_side_bits"],
                          r["fixed_bits"], r["decoder_hash"], "EXPLORATORY; LANGUAGE_ONLY_AT_EXCEPTIONAL_SOURCE_CONTEXTS"))
    rndata = json.loads((ROOT / "gdt001_rank_nomenclator_results.json").read_text())
    for r in rndata["rows"]:
        candidate = "null" if r["model"] == "MATCHED_RANK_NULL" else r["language"]
        ledger.append(row(f"ranknomen_k{r['k']}_{candidate}", "NONSEMANTIC_GENERATOR" if candidate == "null" else "HOMOPHONIC_CIPHER",
                          f"RANK_NOMENCLATOR_K{r['k']}_{candidate}", 0, {"k": r["k"], "candidate": candidate},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; ZERO_PERMUTATION_FREQUENCY_RANK_CODE"))
    ghdata = json.loads((ROOT / "gdt001_group_code_high_order_results.json").read_text())
    for r in ghdata["rows"]:
        candidate = "null" if r["model"] == "MATCHED_GROUP_NULL" else r["language"]
        ledger.append(row(f"groupcodeho_o{r['order']}_{candidate}_s{r['seed']}",
                          "NONSEMANTIC_GENERATOR" if candidate == "null" else "ABBR_LANG",
                          f"GROUP_CHARACTER_ORDER{r['order']}_{candidate}", r["seed"],
                          {"k": r["k"], "order": r["order"], "candidate": candidate}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; COMPLETE_GROUP_CHARACTER_HIGH_ORDER"))
    grdata = json.loads((ROOT / "gdt001_group_code_order4_refine_results.json").read_text())
    for r in grdata["rows"]:
        ledger.append(row(f"groupcodeo4ref_{r['language']}_s{r['seed']}", "ABBR_LANG", "GROUP_CHARACTER_ORDER4_REFINED", r["seed"],
                          {"k": r["k"], "order": r["order"], "language": r["language"], "refiner": "GPU_EXACT_COORDINATE"},
                          r["total_bits"], r["bits_per_symbol"], r["key_bits"], r["payload_bits"], r["fixed_bits"],
                          r["decoder_hash"], "EXPLORATORY; MATCHED_NULL_CROSSOVER; UNSTABLE; CONTROL_SCREENED"))
    gsdata = json.loads((ROOT / "gdt001_group_code_scale_stability.json").read_text())
    for r in gsdata["rows"]:
        ledger.append(row(f"groupcodescale_k{r['k']}_{r['language']}_s{r['seed']}", "ABBR_LANG", "GROUP_CHARACTER_ORDER4_SCALE", r["seed"],
                          {"k": r["k"], "order": r["order"], "language": r["language"]}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"], r["fixed_bits"], r["decoder_hash"],
                          "EXPLORATORY; SELECTION_CORRECT_GAIN_5880_BITS; PARTITION_UNSTABLE"))
    gadata = json.loads((ROOT / "gdt001_group_code_anonymous_null_results.json").read_text())
    for r in gadata["rows"]:
        ledger.append(row(f"groupcodeanon_k512_s{r['seed']}", "NONSEMANTIC_GENERATOR", "ANONYMOUS_27_STATE_GROUP_CODE", r["seed"],
                          {"k": 512, "states": 27, "model": "INTEGRATED_UNIGRAM"}, r["total_bits"], r["bits_per_symbol"],
                          r["key_bits"], r["payload_bits"], r["fixed_bits"], r["decoder_hash"], "EXPLORATORY; MATCHED_ANONYMOUS_BOTTLENECK"))
    rtdata = json.loads((ROOT / "gdt001_root_character_code_results.json").read_text())["result"]
    ledger.append(row(f"rootcode_k{rtdata['k']}_{rtdata['language']}_s{rtdata['seed']}", "ABBR_LANG", "CONSTRUCTION_ROOT_CHARACTER_CODE", rtdata["seed"],
                      {"k": rtdata["k"], "order": rtdata["order"], "language": rtdata["language"]}, rtdata["total_bits"], rtdata["bits_per_symbol"],
                      rtdata["key_bits"], rtdata["payload_bits"], rtdata["fixed_bits"], rtdata["decoder_hash"], "EXPLORATORY; ROOT_LEVEL_CODE; SINGLE_RESTART"))
    fields = list(ledger[0])
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(sorted(ledger, key=lambda r: r["run_id"]))
    print(json.dumps({"runs": len(ledger)}))


if __name__ == "__main__":
    main()
