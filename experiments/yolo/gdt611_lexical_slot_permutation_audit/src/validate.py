#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXP_DIR = Path(__file__).resolve().parents[1]
OUT = EXP_DIR / "artifacts"
G606 = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
G608 = ROOT / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks = []


def check(name, condition, detail=""):
    checks.append({"name": name, "pass": bool(condition), "detail": str(detail)})


result = json.loads((OUT / "RESULT.json").read_text(encoding="utf-8"))
guarded = read_tsv(G606 / "guarded_rows.tsv")
seqdata = json.loads((G606 / "unit_sequences.json").read_text(encoding="utf-8"))
dictionary = read_tsv(OUT / "mini_dictionary_candidates.tsv")
families = read_tsv(OUT / "family_summary.tsv")
permutations = read_tsv(OUT / "label_permutation_witness.tsv")
nulls = read_tsv(OUT / "section_nulls.tsv")
witnesses = read_tsv(OUT / "transferred_frame_witnesses.tsv")
paragraph = read_tsv(OUT / "held_paragraph_witness.tsv")

expected_hashes = {
    "guarded_rows.tsv": "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9",
    "unit_sequences.json": "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf",
    "stable_stem_role_summary.tsv": "4c385f59520e4b9ebc9c75274eb1ff8a28efc340b12ccad29754e085d866012b",
    "merge_tree.tsv": "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a",
}
actual_paths = {
    "guarded_rows.tsv": G606 / "guarded_rows.tsv",
    "unit_sequences.json": G606 / "unit_sequences.json",
    "stable_stem_role_summary.tsv": G608 / "stable_stem_role_summary.tsv",
    "merge_tree.tsv": G608 / "merge_tree.tsv",
}
for name, expected in expected_hashes.items():
    actual = sha256(actual_paths[name])
    check(f"input_hash_{name}", actual == expected == result["input_hashes"][name], actual)

check("guarded_rows_4165", len(guarded) == 4165, len(guarded))
check("guarded_no_f84_page", all(not r["page"].lower().startswith("f84") for r in guarded))
check("guarded_no_f84_folio", all(not r["physical_folio"].lower().startswith("f84") for r in guarded))
all_seq_records = seqdata["sequences"]["train"] + seqdata["sequences"]["held"]
check("sequences_no_f84_page", all(not r["page"].lower().startswith("f84") for r in all_seq_records))
check("sequences_no_f84_folio", all(not r["physical_folio"].lower().startswith("f84") for r in all_seq_records))
check("split_68_23", (
    len({r["physical_folio"] for r in seqdata["sequences"]["train"]}),
    len({r["physical_folio"] for r in seqdata["sequences"]["held"]}),
) == (68, 23))

expected_labels = {
    "REIBEN", "KOCHEN_ERWAERMEN", "TROCKNEN", "EINWEICHEN",
    "WURZEL", "BLATT", "BLUETE", "SAMEN",
    "WASSER", "WEIN", "OEL", "SALZ",
    "GEFAESS", "BAD", "KRANKHEIT", "FRAU", "HEILUNG",
}
check("dictionary_17", len(dictionary) == 17, len(dictionary))
check("dictionary_unique_carriers", len({r["carrier"] for r in dictionary}) == 17)
check("dictionary_exact_labels", {r["label_default"] for r in dictionary} == expected_labels)
check("all_exact_lexeme_gates_zero", all(r["exact_lexeme_gate"] == "0" for r in dictionary))
check("all_default_only", all(r["status"] == "DEFAULT_ONLY__LABEL_PERMUTATION_IDENTICAL" for r in dictionary))
check("result_zero_lexemes", result["exact_lexeme_assignments_passed"] == 0)
check("decision_negative", result["decision"] == "NO_STABLE_LEXICAL_OR_FAMILY_SLOT")
check("eligible_200", result["eligible_carriers"] == 200)
check("graph_percolated_one_component", result["exchange_components"] == 1)
check("retained_edges_975", result["retained_exchange_edges"] == 975)

check("four_family_rows", len(families) == 4)
check("all_family_gates_zero", all(r["family_gate"] == "0" for r in families))
check("member_gates_zero", all(r["member_gates_passed"] == "0" for r in families))
expected_edges = {"operation": "0", "plant_part": "3", "liquid_material": "2", "record_entity": "1"}
check("family_transferred_edge_counts", {r["family"]: r["held_shared_pair_edges"] for r in families} == expected_edges)

by_family_perm = defaultdict(list)
for row in permutations:
    by_family_perm[row["family"]].append(row)
check("three_permutations_each", all(len(rows) == 3 for rows in by_family_perm.values()) and len(by_family_perm) == 4)
for family, rows in by_family_perm.items():
    check(f"permutation_signature_{family}", len({r["likelihood_signature"] for r in rows}) == 1)
    check(f"permutation_section_score_{family}", len({r["held_section_or_formal_objective"] for r in rows}) == 1)
    check(f"permutation_frame_score_{family}", len({r["held_frame_objective"] for r in rows}) == 1)
    check(f"permutation_delta_{family}", all(float(r["delta_from_original"]) == 0 for r in rows))

nonop_nulls = [r for r in nulls if r["family"] != "operation"]
check("section_null_rows_34", len(nulls) == 34, len(nulls))
check("section_null_1000_reps", all(r["replicates"] == "1000" for r in nonop_nulls))
check("section_null_p_formula", all(abs(float(r["p_one_sided"]) - (int(r["null_ge_count"]) + 1) / 1001) < 5e-10 for r in nonop_nulls))
check("no_held_section_gate", all(float(r["p_one_sided"]) > 0.05 for r in nonop_nulls if r["split"] == "held"))
check("mixed_train_exclusion", all(r["excluded_mixed_section_folios"] == "f66;f76;f86" for r in nulls if r["split"] == "train"))
check("mixed_held_exclusion", all(r["excluded_mixed_section_folios"] == "f85" for r in nulls if r["split"] == "held"))

# Reconstruct exact frames independently and verify every transfer witness.
frame_counts = {"train": defaultdict(Counter), "held": defaultdict(Counter)}
metadata = {r["locus"]: r for r in guarded}
for split in ("train", "held"):
    by_locus = defaultdict(list)
    for rec in seqdata["sequences"][split]:
        by_locus[rec["locus"]].append(rec)
    for locus, records in by_locus.items():
        records.sort(key=lambda r: int(r["chunk_index"]))
        forms = ["+".join(r["units"]) for r in records]
        for i, rec in enumerate(records):
            form = forms[i]
            units = rec["units"]
            frames = []
            if len(units) >= 2:
                for pos in range(len(units)):
                    masked = list(units)
                    masked[pos] = "*"
                    frames.append(("internal", f"{pos}/{len(units)}:" + "+".join(masked)))
            if i > 0:
                frames.append(("left", forms[i - 1]))
            if i + 1 < len(forms):
                frames.append(("right", forms[i + 1]))
            if i > 0 and i + 1 < len(forms):
                frames.append(("both", forms[i - 1] + "||" + forms[i + 1]))
            for key in frames:
                frame_counts[split][key][form] += 1

for index, row in enumerate(witnesses):
    key = (row["channel"], row["exact_frame"])
    a, b = row["carrier_a"], row["carrier_b"]
    reconstructed = (
        frame_counts["train"][key][a], frame_counts["train"][key][b],
        frame_counts["held"][key][a], frame_counts["held"][key][b],
    )
    recorded = tuple(int(row[x]) for x in ("train_count_a", "train_count_b", "held_count_a", "held_count_b"))
    check(f"transfer_witness_{index:02d}", reconstructed == recorded and min(reconstructed) > 0, f"{key}:{reconstructed}")
check("has_internal_eol_witness", any(r["carrier_a"] == "ok+eol" and r["carrier_b"] == "qok+eol" and r["exact_frame"] == "0/2:*+eol" for r in witnesses))

# Rebuild paragraph identifiers and deterministic ranking.
page_active = {}
page_counter = Counter()
paragraph_id = {}
paragraph_loci = defaultdict(list)
for row in guarded:
    starts = "<%>" in row["ivtff_raw"][:32]
    ends = "<$>" in row["ivtff_raw"]
    if starts or row["page"] not in page_active:
        page_counter[row["page"]] += 1
        page_active[row["page"]] = f"{row['page']}:p{page_counter[row['page']]}"
    pid = page_active[row["page"]]
    paragraph_id[row["locus"]] = pid
    paragraph_loci[pid].append(row["locus"])
    if ends:
        page_active.pop(row["page"], None)

selected_forms = {r["carrier"] for r in dictionary}
paragraph_forms = defaultdict(list)
paragraph_locus_sets = defaultdict(set)
for rec in seqdata["sequences"]["held"]:
    pid = paragraph_id[rec["locus"]]
    paragraph_forms[pid].append("+".join(rec["units"]))
    paragraph_locus_sets[pid].add(rec["locus"])
ranked = []
for pid, forms in paragraph_forms.items():
    hits = [f for f in forms if f in selected_forms]
    ranked.append((-len(hits), -len(set(hits)), -len(paragraph_locus_sets[pid]), pid))
best_pid = sorted(ranked)[0][3]
check("paragraph_id_reproduced", best_pid == result["held_paragraph"] == paragraph[0]["paragraph_id"], best_pid)
check("paragraph_complete_25_lines", len(paragraph) == 25, len(paragraph))
check("paragraph_all_same_id", {r["paragraph_id"] for r in paragraph} == {best_pid})
annotation_text = " ".join(r["candidate_annotation"] for r in paragraph)
check("paragraph_has_water_default", annotation_text.count("[WASSER?]") == 14, annotation_text.count("[WASSER?]"))
check("paragraph_18_total_hits", annotation_text.count("?]") == 18, annotation_text.count("?]"))

manifest = read_tsv(OUT / "ARTIFACT_MANIFEST.tsv")
for row in manifest:
    manifest_path = ROOT / row["path"]
    check(f"manifest_{manifest_path.name}", manifest_path.exists() and sha256(manifest_path) == row["sha256"])

status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
payload = {
    "status": status,
    "checks_passed": sum(row["pass"] for row in checks),
    "checks_total": len(checks),
    "checks": checks,
}
(OUT / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
raise SystemExit(0 if status == "PASS" else 1)
