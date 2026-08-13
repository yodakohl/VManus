#!/usr/bin/env python3
"""Independent integrity and scope checks for the current ten decoder packets."""

import csv, hashlib, json, math
from pathlib import Path

from gdt001_core import ROOT, canonical, load_lattice, sha256_file

FILES = ("model_spec.json", "mapping.tsv", "segmentation.tsv",
         "candidate_plaintext.tsv", "lexicon.tsv", "reverse_generation.tsv",
         "structural_explanation.md", "failure_analysis.md", "risky_predictions.md")
EXPECTED = {
    "contextmixer_s0_015625", "nonsemantic_ngram_o2",
    "nonsemantic_neural_gru_h48_s0072", "record_notation_fields",
    "lineinitial_old_italian_tuscan_o2_s64101", "latentline_k2_s28104",
    "sparse_payload_che_prefix_mhg_s2301",
    "groupcodescale_k512_medieval_czech_s36105",
    "groupchar_group_character_language_k128_medieval_czech_s19103",
    "wordnom_word_nomenclator_k032_o1_middle_high_german_s13101",
}


def main():
    checks = []
    def need(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    index = json.load(open(ROOT / "candidates/index.json")); _, lines = load_lattice()
    loci = [line.locus for line in lines]
    need(index["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "status")
    need(len(index["candidates"]) == 10, "ten_candidates")
    need({row["candidate_id"] for row in index["candidates"]} == EXPECTED, "diverse_current_set")
    need(index["candidates"][0]["candidate_id"] == "contextmixer_s0_015625", "current_leader")
    packet_loci = None
    finite_reverse_failures = {}
    for item in index["candidates"]:
        directory = ROOT / "candidates" / item["candidate_id"]
        need({path.name for path in directory.iterdir()} == set(FILES), f"files:{item['candidate_id']}")
        need(set(item["artifact_sha256"]) == set(FILES), f"hash_schema:{item['candidate_id']}")
        for name in FILES:
            need(item["artifact_sha256"][name] == sha256_file(directory / name), f"hash:{item['candidate_id']}:{name}")
        spec = json.load(open(directory / "model_spec.json"))
        need(spec["decoder_hash"] == hashlib.sha256(canonical(spec["decoder"])).hexdigest() == item["decoder_hash"], f"decoder_hash:{item['candidate_id']}")
        with (directory / "mapping.tsv").open() as handle:
            mappings = list(csv.DictReader(handle, delimiter="\t"))
        need(mappings and all(row["source_unit"] and row["latent_or_plaintext_unit"] for row in mappings), f"nonblank_mapping:{item['candidate_id']}")
        with (directory / "candidate_plaintext.tsv").open() as handle:
            plaintext = list(csv.DictReader(handle, delimiter="\t"))
        need([row["locus"] for row in plaintext] == loci, f"complete_lines:{item['candidate_id']}")
        need(all(row["confidence"] == "EXPLORATORY" and row["uncertainty_reason"] for row in plaintext), f"uncertainty:{item['candidate_id']}")
        with (directory / "segmentation.tsv").open() as handle:
            segmentation = list(csv.DictReader(handle, delimiter="\t"))
        need([row["locus"] for row in segmentation] == loci, f"segmentation:{item['candidate_id']}")
        if item["candidate_id"].startswith("latentline_"):
            state_by_locus = {row["locus"]: row["state"] for row in spec["decoder"]["line_states"]}
            need(len(state_by_locus) == len(loci) and all(row["normalized_plaintext_or_record"].startswith(f"STATE_{state_by_locus[row['locus']]} :: ") for row in plaintext), "latentline_assignments_visible")
        if item["candidate_id"].startswith("lineinitial_"):
            scope = {line.locus: line.grammar_scope for line in lines}
            need(all((row["normalized_plaintext_or_record"].startswith("LINE_INITIAL=")
                      if scope[row["locus"]] == "CONFIRMED_PROSE"
                      else row["normalized_plaintext_or_record"].startswith("OUT_OF_SCOPE_NONPROSE ::"))
                     for row in plaintext), "lineinitial_scope_visible")
        with (directory / "reverse_generation.tsv").open() as handle:
            reverse = list(csv.DictReader(handle, delimiter="\t"))
        current_packet = [row["locus"] for row in reverse]
        need(len(current_packet) == len(set(current_packet)) == 199, f"packet_unique:{item['candidate_id']}")
        if packet_loci is None: packet_loci = current_packet
        need(current_packet == packet_loci, f"packet_same:{item['candidate_id']}")
        need({row["packet"] for row in reverse} == {"HERBAL_CURRIER_A", "CURRIER_B_PROSE", "BIOLOGICAL_LABEL_RICH_AND_F75V", "F57V", "F67R2", "CIRCULAR_RADIAL", "F116V_STRESS"}, f"packet_roles:{item['candidate_id']}")
        if all(row["actual_source_bits"] != "NOT_COMPUTED" for row in reverse):
            need(all(math.isfinite(float(row["actual_source_bits"])) and math.isfinite(float(row["wrong_source_bits"])) for row in reverse), f"finite_reverse:{item['candidate_id']}")
            finite_reverse_failures[item["candidate_id"]] = sum(float(row["wrong_source_bits"]) <= float(row["actual_source_bits"]) for row in reverse)
        else:
            need(all(row["reverse_generation_mode"] == "REVERSE_GENERATION_NOT_IMPLEMENTED_CANDIDATE_FAILS_REQUIREMENT" and row["actual_source_bits"] == row["wrong_source_bits"] == row["actual_advantage_bits"] == "NOT_COMPUTED" for row in reverse), f"reverse_failure_explicit:{item['candidate_id']}")
        predictions = (directory / "risky_predictions.md").read_text().splitlines()
        numbered = [line for line in predictions if line[:1].isdigit()]
        need(len(numbered) == 10 and all(f"`{locus}`" in row and "kills this prediction" in row for locus, row in zip(packet_loci[:10], numbered)), f"predictions:{item['candidate_id']}")
        need("not a translation" in (directory / "failure_analysis.md").read_text().lower(), f"ceiling:{item['candidate_id']}")
    need(finite_reverse_failures == {"contextmixer_s0_015625": 11, "nonsemantic_ngram_o2": 10, "nonsemantic_neural_gru_h48_s0072": 14}, "finite_reverse_failures_disclosed")
    output = {"schema": "GDT001_CANDIDATE_EXPORT_VALIDATION_V2", "status": "PASS_CURRENT_DIVERSE_TEN_PACKET_INTEGRITY",
              "check_count": len(checks), "checks": checks, "candidate_count": 10,
              "packet_unique_loci": len(packet_loci), "finite_reverse_failure_counts": finite_reverse_failures,
              "claim_ceiling": "Artifact integrity and coverage only; no candidate output is a confirmed reading or translation."}
    (ROOT / "gdt001_candidate_export_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "packet_loci": len(packet_loci)}))


if __name__ == "__main__": main()
