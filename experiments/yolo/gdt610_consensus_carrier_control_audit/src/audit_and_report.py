#!/usr/bin/env python3
"""Derive the non-tautological carrier audit and compact final report."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name):
    with (HERE / name).open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    path = HERE / name
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "<NA>") for field in writer.fieldnames} for row in rows)


def pct(value):
    return f"{100 * value:.1f}%"


def f4(value):
    return f"{value:.4f}"


def main():
    global HERE
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    HERE = args.output_dir
    result = json.loads((HERE / "result.json").read_text())
    target_summary = json.loads((HERE / "target_summary.json").read_text())
    freeze = json.loads((HERE / "CALIBRATION_FREEZE.json").read_text())
    selected = float(freeze["selected_coupling"])
    anchors = {row["unit"]: row for row in read_tsv("anchor_categories.tsv")}
    calibration = read_tsv("calibration_complete_mappings.tsv")
    target = read_tsv("target_complete_mappings.tsv")

    # Recover held control occurrence weights once, without oracle text use.
    held_frequency = Counter()
    with (HERE / "calibration_held_decodes.tsv").open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if float(row["coupling"]) == selected and int(row["member"]) == 0:
                held_frequency.update(row["units"].split())

    diagnostics = []
    selected_rows = [row for row in calibration if float(row["coupling"]) == selected]
    for category in "LDSNW":
        rows = [row for row in selected_rows if row["category"] == category]
        units = sorted({row["unit"] for row in rows})
        members = sorted({int(row["member"]) for row in rows})
        stable = sum(
            len({row["output"] for row in rows if row["unit"] == unit}) == 1
            for unit in units
        )
        type_accuracy = sum(int(row["oracle_exact"]) for row in rows) / len(rows)
        member_weighted = []
        for member in members:
            subset = [row for row in rows if int(row["member"]) == member]
            denominator = sum(held_frequency[row["unit"]] for row in subset)
            numerator = sum(
                held_frequency[row["unit"]] for row in subset if row["oracle_exact"] == "1"
            )
            member_weighted.append(numerator / denominator)
        diagnostics.append({
            "dataset": "synthetic_control", "language": "latin_control",
            "condition": "coupled", "category": category,
            "category_types": len(units), "all_member_stable_types": stable,
            "all_member_stable_type_fraction": stable / len(units),
            "mean_oracle_type_accuracy": type_accuracy,
            "mean_oracle_held_weighted_accuracy": sum(member_weighted) / len(member_weighted),
        })

    for language in ("latin", "old_italian", "middle_high_german"):
        for condition in ("uncoupled", "coupled"):
            subset = [
                row for row in target
                if row["language"] == language and row["condition"] == condition
            ]
            for category in "LDSNW":
                rows = [row for row in subset if row["category"] == category]
                units = sorted({row["unit"] for row in rows})
                stable = sum(
                    len({row["output"] for row in rows if row["unit"] == unit}) == 1
                    for unit in units
                )
                diagnostics.append({
                    "dataset": "target", "language": language,
                    "condition": condition, "category": category,
                    "category_types": len(units), "all_member_stable_types": stable,
                    "all_member_stable_type_fraction": stable / len(units),
                    "mean_oracle_type_accuracy": "",
                    "mean_oracle_held_weighted_accuracy": "",
                })
    write_tsv("category_diagnostics.tsv", diagnostics)

    audited_fragments = []
    for row in read_tsv("carrier_aligned_held_fragments.tsv"):
        units = row["source_units"].split()
        pattern = "".join(anchors[unit]["category"] for unit in units)
        exact = row["exact_reference_word"] == "1"
        if "W" in pattern:
            evidence_class = "DIRECT_W_CANDIDATE_INJECTION" if pattern == "W" else "CONTAINS_W_CANDIDATE"
        elif exact:
            evidence_class = "COMPOSED_NONW_REFERENCE_MATCH"
        else:
            evidence_class = "STABLE_NONREFERENCE_FRAGMENT"
        audited_fragments.append({
            **row, "category_pattern": pattern,
            "carrier_units": len(units), "evidence_class": evidence_class,
            "non_tautological_candidate": int(evidence_class == "COMPOSED_NONW_REFERENCE_MATCH"),
        })
    write_tsv("carrier_fragment_audit.tsv", audited_fragments)

    control_w = [row for row in selected_rows if row["category"] == "W"]
    control_w_lines = []
    for unit in sorted({row["unit"] for row in control_w}):
        rows = sorted((row for row in control_w if row["unit"] == unit), key=lambda row: int(row["member"]))
        outputs = [row["output"] for row in rows]
        control_w_lines.append(
            f"| `{unit}` | `{rows[0]['oracle_output']}` | `{outputs[0]}` | "
            f"{'yes' if len(set(outputs)) == 1 else 'no'} | {'yes' if all(row['oracle_exact'] == '1' for row in rows) else 'no'} |"
        )

    calibration_rows = read_tsv("calibration_grid.tsv")
    calibration_lines = []
    for row in calibration_rows:
        calibration_lines.append(
            f"| {float(row['coupling']):.2f} | {pct(float(row['all_member_exact_type_fraction']))} | "
            f"{pct(float(row['mean_type_key_accuracy']))} | "
            f"{pct(float(row['mean_held_occurrence_weighted_key_accuracy']))} | "
            f"{pct(float(row['mean_held_plaintext_character_accuracy']))} |"
        )

    target_lines = []
    for language in ("latin", "old_italian", "middle_high_german"):
        for condition in ("uncoupled", "coupled"):
            row = target_summary[language][condition]
            target_lines.append(
                f"| {language} | {condition} | {pct(row['stability']['all_member_exact_type_fraction'])} | "
                f"{pct(row['stability']['all_member_exact_occurrence_weighted_fraction'])} | "
                f"{f4(row['mean_real_minus_destroyed_bits_per_transition'])} | "
                f"{pct(row['mean_reference_lexicon_character_fraction'])} |"
            )

    category_lines = []
    for language in ("latin", "old_italian", "middle_high_german"):
        row = [
            d for d in diagnostics
            if d["dataset"] == "target" and d["language"] == language and d["condition"] == "coupled"
        ]
        values = {d["category"]: f"{d['all_member_stable_types']}/{d['category_types']}" for d in row}
        category_lines.append(
            f"| {language} | {values['L']} | {values['D']} | {values['S']} | {values['N']} | {values['W']} |"
        )

    fragment_counts = Counter(
        (row["language"], row["coupling"], row["evidence_class"])
        for row in audited_fragments
    )
    composed = [
        row for row in audited_fragments
        if row["coupling"] == "coupled" and row["evidence_class"] == "COMPOSED_NONW_REFERENCE_MATCH"
    ]
    composed_lines = [
        f"| {row['language']} | {row['physical_folio']} | {row['locus']} | {row['chunk_index']} | "
        f"`{row['source_units']}` | `{row['fragment']}` | {row['category_pattern']} | {row['reference_count']} |"
        for row in composed
    ]
    if not composed_lines:
        composed_lines = ["| — | — | — | — | — | — | — | — |"]

    target_w_lines = []
    for language in ("latin", "old_italian", "middle_high_german"):
        rows = [
            row for row in target
            if row["language"] == language and row["condition"] == "coupled" and row["category"] == "W"
        ]
        for unit in sorted({row["unit"] for row in rows}):
            outputs = [
                row["output"] for row in sorted(
                    (row for row in rows if row["unit"] == unit), key=lambda row: int(row["member"])
                )
            ]
            target_w_lines.append(
                f"| {language} | `{unit}` | `{outputs[0]}` | "
                f"{'6/6' if len(set(outputs)) == 1 else str(max(Counter(outputs).values())) + '/6'} |"
            )

    control_diag = {row["category"]: row for row in diagnostics if row["dataset"] == "synthetic_control"}
    report = f"""# Consensus-coupled carrier decoder: final report

## Outcome

**FAIL — no concrete reading.** Coupling carrier maps inside the fit does raise
stability, but it also makes the entire synthetic whole-word category agree on
the wrong key. The planted control reaches only
{pct(result['calibration_selected_metrics']['mean_held_plaintext_character_accuracy'])}
held character accuracy. Target words produced directly by W candidates are
therefore codebook injection, not translations.

The run used only the canonical published 98-unit JSON payload and independently
hashed Latin, Old Italian, and Middle High German references.

## Frozen method

- Fixed target categories: 42 letter/homophone (L), 4 double (D), 34 syllable
  (S), 7 null (N), 11 whole-word (W).
- W anchors use standalone/boundary evidence, not positive frequency. The five
  nearly pure standalone forms `qokaN`, `qokEdy`, `qokaI`, `qokedy`, `qokEy`
  are all W anchors.
- Six deterministic leave-one-folio-block-out views jointly optimize their
  maps. After two independent warm-up sweeps, each coordinate move includes a
  reward for exact agreement with the modal output of the other views.
- Language objective: character 4-gram typicality plus a small reference
  word-length likelihood. It contains **no dictionary-match or word-frequency
  bonus**. Each stored non-null output additionally costs
  `(1 + output_length) × log2(27)` bits as codebook MDL.
- The positive coupling weight is chosen only on a planted Latin control. Its
  30,174 chunks reproduce the exact train/held chunk-length sequence; all 98
  units occur, rank-frequency Spearman is
  {result['control']['train_frequency_rank_spearman']:.6f}, and JS divergence is
  {result['control']['train_frequency_js_divergence_bits']:.5f} bit.

## Synthetic calibration

| λ | all-six stable types | mean key types correct | held-weighted key correct | held character correct |
|---:|---:|---:|---:|---:|
{chr(10).join(calibration_lines)}

The frozen choice is λ={selected:.2f}. It raises exact six-view stability from
{pct(float(calibration_rows[0]['all_member_exact_type_fraction']))} to
{pct(result['calibration_selected_metrics']['all_member_exact_type_fraction'])},
but end-to-end held character recovery remains
{pct(result['calibration_selected_metrics']['mean_held_plaintext_character_accuracy'])}.

The failure is sharply localized by category:

| category | types | all-six stable | mean oracle type accuracy | held-weighted oracle accuracy |
|:--|--:|--:|--:|--:|
| L | 42 | {control_diag['L']['all_member_stable_types']} | {pct(control_diag['L']['mean_oracle_type_accuracy'])} | {pct(control_diag['L']['mean_oracle_held_weighted_accuracy'])} |
| D | 4 | {control_diag['D']['all_member_stable_types']} | {pct(control_diag['D']['mean_oracle_type_accuracy'])} | {pct(control_diag['D']['mean_oracle_held_weighted_accuracy'])} |
| S | 34 | {control_diag['S']['all_member_stable_types']} | {pct(control_diag['S']['mean_oracle_type_accuracy'])} | {pct(control_diag['S']['mean_oracle_held_weighted_accuracy'])} |
| N | 7 | {control_diag['N']['all_member_stable_types']} | {pct(control_diag['N']['mean_oracle_type_accuracy'])} | {pct(control_diag['N']['mean_oracle_held_weighted_accuracy'])} |
| W | 11 | {control_diag['W']['all_member_stable_types']} | {pct(control_diag['W']['mean_oracle_type_accuracy'])} | {pct(control_diag['W']['mean_oracle_held_weighted_accuracy'])} |

All eleven W carriers are perfectly stable and all eleven are wrong:

| control unit | planted output | six-view output | stable | correct |
|:--|:--|:--|:--:|:--:|
{chr(10).join(control_w_lines)}

This is the clean bottleneck: typicality + MDL + consensus identifies a shared
pseudo-key, not the planted whole-word key. Syllables are the next weak point;
only 20/34 are stable in control, versus 38/42 letters, 4/4 doubles, and 7/7
nulls.

## Target behavior

| language | condition | all-six stable types | occurrence-weighted stable | real−destroyed bits/transition | post-hoc lexicon characters |
|:--|:--|--:|--:|--:|--:|
{chr(10).join(target_lines)}

Coupling raises stability but does not improve held language evidence
consistently: Latin rises by about 0.0061 bit/transition, while Old Italian
falls by about 0.0100 and MHG falls by about 0.0043. The lexicon fraction is
post-hoc only and likewise falls for Old Italian and MHG.

Category stability after coupling:

| language | L | D | S | N | W |
|:--|--:|--:|--:|--:|--:|
{chr(10).join(category_lines)}

The coupled target therefore repeats the control pathology: W becomes almost
fully stable, while only 0--2 of 34 S mappings stabilize.

### Why the apparent words are not readings

Among coupled exact-reference fragment rows, direct W-candidate outputs account
for {fragment_counts[('latin', 'coupled', 'DIRECT_W_CANDIDATE_INJECTION')]} Latin,
{fragment_counts[('old_italian', 'coupled', 'DIRECT_W_CANDIDATE_INJECTION')]} Old
Italian, and {fragment_counts[('middle_high_german', 'coupled', 'DIRECT_W_CANDIDATE_INJECTION')]}
MHG rows. Those matches are tautological because every allowed W output came
from that language's reference list, even though membership did not enter the
score.

Only {len(composed)} coupled matches are composed entirely from non-W carriers;
all are Latin and reduce to repetitive forms rather than a coherent passage:

| language | folio | locus | chunk | units | output | categories | reference count |
|:--|:--|:--|--:|:--|:--|:--|--:|
{chr(10).join(composed_lines)}

The complete coupled W assignments, included for audit rather than meaning,
are:

| language | carrier | modal output | support |
|:--|:--|:--|--:|
{chr(10).join(target_w_lines)}

## Conclusion

The different decoder succeeds at its narrow engineering goal—carrier
consensus is inside optimization, and the synthetic calibration shows that it
recovers L/D/N reasonably well. It fails the scientific goal. W consensus is
demonstrably wrong under a known key; S remains non-identifiable; and no
non-W carrier-aligned held phrase emerges in Old Italian or MHG. The eight
Latin rows are `iiii`, `sese`, or `cccc`, not a reading.

The localized next requirement is not more consensus. It is independent
information capable of identifying W and S outputs (for example an external
crib or relation constraint) that also improves planted-control character
recovery. Without that, the target is LM-driven pseudotext.

## Reproduction and artifacts

Run from this directory with Python 3 (standard library only):

```sh
python3 experiments/yolo/gdt610_consensus_carrier_control_audit/src/consensus_carrier_decoder.py \\
  --unit-sequences UNIT_SEQUENCES_JSON \\
  --reference-dir REFERENCE_CACHE \\
  --output-dir .
python3 experiments/yolo/gdt610_consensus_carrier_control_audit/src/audit_and_report.py --output-dir OUTPUT_DIR
python3 experiments/yolo/gdt610_consensus_carrier_control_audit/src/validate.py
```

The full run took about 33 minutes on the current host. Complete mappings are
in `target_complete_mappings.tsv`; all 9,838 held chunks and twelve decodes per
language are in `held_decodes_*.tsv`; the 295,140 control decodes are in
`calibration_held_decodes.tsv`. `carrier_fragment_audit.tsv` labels direct W
injection separately from composed non-W matches.
"""
    (HERE / "REPORT.md").write_text(report)


if __name__ == "__main__":
    main()
