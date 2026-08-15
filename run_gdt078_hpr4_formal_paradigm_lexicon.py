#!/usr/bin/env python3
"""GDT078: freeze concrete HPR4 PAGE_HOST renderer classes and paradigms."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PAIR_RATES = ROOT / "gdt076_register_host_rates.tsv"
METHOD = ROOT / "GDT078_HPR4_FORMAL_PARADIGM_LEXICON_METHOD.md"
REPORT = ROOT / "GDT078_HPR4_FORMAL_PARADIGM_LEXICON_REPORT.md"
ATLAS = ROOT / "gdt078_page_host_class_atlas.tsv"
CELLS = ROOT / "gdt078_paradigm_cells.tsv"
PREDICTIONS = ROOT / "gdt078_hpr4_predictions.tsv"
MODEL = ROOT / "gdt078_hpr4_model.json"
RESULT = ROOT / "gdt078_result.json"

RIGHT_FAMILIES = ("aiin", "air", "ain", "ar", "al")


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def entropy(counts):
    total = sum(counts.values())
    return -sum((value / total) * math.log2(value / total) for value in counts.values() if value) if total else 0.0


def main():
    source = read(SOURCE)
    pairs = read(PAIR_RATES)
    assert len(source) == 15592 and len(pairs) == 229
    assert not any(row["locus"].startswith("f84r") for row in source)
    source_by_host = defaultdict(list)
    pairs_by_host = defaultdict(list)
    for row in source:
        source_by_host[row["page_host"]].append(row)
    for row in pairs:
        pairs_by_host[row["page_host"]].append(row)
    atlas_rows = []
    stable_hosts = []
    for page_host, host_pairs in sorted(pairs_by_host.items()):
        rows = source_by_host[page_host]
        eligible_folds = len(host_pairs)
        training_high = sum(int(row["training_aiin_high"]) for row in host_pairs)
        held_high = sum(int(row["held_aiin_high"]) for row in host_pairs)
        agreement = sum(row["training_aiin_high"] == row["held_aiin_high"] for row in host_pairs)
        stable_high = (
            eligible_folds >= 3
            and training_high / eligible_folds >= 0.60
            and held_high / eligible_folds >= 0.60
            and agreement / eligible_folds >= 0.60
        )
        right_counts = Counter(row["right_family"] for row in rows)
        wrapper_counts = Counter(row["wrapper"] for row in rows)
        explicit_counts = {family: right_counts[family] for family in RIGHT_FAMILIES}
        explicit_total = sum(explicit_counts.values())
        dominant_explicit = max(RIGHT_FAMILIES, key=lambda family: (explicit_counts[family], family))
        atlas_rows.append(
            {
                "page_host": page_host,
                "occurrences": len(rows),
                "physical_folios": len({row["physical_folio"] for row in rows}),
                "registers": len({row["register"] for row in rows}),
                "eligible_register_folds": eligible_folds,
                "training_aiin_high_folds": training_high,
                "held_aiin_high_folds": held_high,
                "binary_agreement_folds": agreement,
                "training_high_fraction": training_high / eligible_folds,
                "held_high_fraction": held_high / eligible_folds,
                "agreement_fraction": agreement / eligible_folds,
                "global_aiin_rate": right_counts["aiin"] / len(rows),
                "explicit_right_occurrences": explicit_total,
                "explicit_right_entropy": entropy(Counter(explicit_counts)),
                "dominant_explicit_right": dominant_explicit,
                "dominant_wrapper": max(wrapper_counts, key=lambda wrapper: (wrapper_counts[wrapper], wrapper)),
                "dominant_wrapper_rate": max(wrapper_counts.values()) / len(rows),
                "formal_class": "AIIN_STABLE_HIGH" if stable_high else "AIIN_UNSTABLE_OR_LOW",
            }
        )
        if stable_high:
            stable_hosts.append(page_host)
    cell_rows = []
    registers = sorted({row["register"] for row in source})
    for page_host in stable_hosts:
        for register in registers:
            for right_family in RIGHT_FAMILIES:
                rows = [
                    row for row in source_by_host[page_host]
                    if row["register"] == register and row["right_family"] == right_family
                ]
                cell_rows.append(
                    {
                        "page_host": page_host,
                        "register": register,
                        "right_family": right_family,
                        "occurrences": len(rows),
                        "physical_folios": len({row["physical_folio"] for row in rows}),
                        "wrappers": ";".join(sorted({row["wrapper"] for row in rows})) if rows else "NONE_OBSERVED",
                        "example_token": rows[0]["token"] if rows else "NONE_OBSERVED",
                        "example_locus": rows[0]["locus"] if rows else "NONE_OBSERVED",
                        "cell_state": "OBSERVED" if rows else "ABSENT_IN_REGISTER",
                    }
                )
    predictions = [
        {
            "prediction_id": "HPR4_P01",
            "future_target": "FRESH_NON_F84_ENCLOSURE_CONTRAST_PANEL",
            "formal_predictor": "PAGE_HOST in frozen AIIN_STABLE_HIGH set {" + ",".join(stable_hosts) + "}",
            "predicted_relation": "positive association with provenance-native REL_ENCLOSURE",
            "capacity": "at least 30 mapped loci; >=3 positive and negative; >=2 positive and negative folios; at least two stable-high feature hosts",
            "primary_test": "folio-by-human-unit conditional effect > 0 with host-set frozen",
            "kill": "effect <= 0 or driven by one exact host",
            "status": "FROZEN_NOT_RUN",
        }
    ]
    model = {
        "schema": "GDT078_HPR4_FORMAL_PARADIGM_MODEL_V1",
        "name": "HPR4_HOST_COMPATIBILITY_RECORD_COMPILER",
        "generator": {
            "page": "choose register-conditioned PAGE_HOST inventory and record architecture",
            "line": "Q2_ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?",
            "field": "WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?",
            "page_host": "select a reusable formal key with a stable renderer-propensity vector",
            "wrapper": "host-licensed construction selected before right rendering",
            "right_family": "select from {aiin,air,ain,ar,al,NONE} conditional on PAGE_HOST, register, and weakly WRAPPER",
            "dy_checkpoint": "predict following-wrapper ecology; independent content transition not supported",
            "b3_close": "probabilistic line closer; content neutrality unknown",
        },
        "stable_aiin_high_hosts": stable_hosts,
        "complete_manuscript_wide_five_renderer_hosts": [
            page_host for page_host in stable_hosts
            if all(any(row["page_host"] == page_host and row["right_family"] == family for row in source) for family in RIGHT_FAMILIES)
        ],
        "evidence": {
            "formal_reuse": "SUPPORTED",
            "right_propensity_cross_register": "SUPPORTED_GDT076",
            "wrapper_to_right_dependency": "WEAK_REGISTER_DEPENDENT_GDT077",
            "external_content_class": "PROSPECTIVE_UNCONFIRMED",
            "linguistic_morphology_over_string_baseline": "NOT_DISTINGUISHABLE_GDT003",
        },
        "f84r": "SEALED_NOT_TARGETED",
    }
    write(ATLAS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in atlas_rows], list(atlas_rows[0]))
    write(CELLS, cell_rows, list(cell_rows[0]))
    write(PREDICTIONS, predictions, list(predictions[0]))
    MODEL.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n")
    observed_cells = sum(row["cell_state"] == "OBSERVED" for row in cell_rows)
    complete_hosts = model["complete_manuscript_wide_five_renderer_hosts"]
    status = "HPR4_FORMAL_PAGE_HOST_PARADIGM_CLASSES_FROZEN" if stable_hosts == ["d", "ok", "yk", "yt"] and complete_hosts == stable_hosts else "HPR4_STABLE_CLASS_INVENTORY_DIFFERENT_FROM_EXPECTED"
    report = f"""# GDT078 — HPR4 formal paradigm lexicon

## Outcome

**{status}**

The preregistered cross-register stability rule selects exactly four
PAGE_HOSTs: `{', '.join(stable_hosts)}`.  All four realize every explicit
RIGHT_FAMILY (`aiin`, `air`, `ain`, `ar`, `al`) somewhere in the manuscript.
The atlas contains {len(cell_rows)} host×register×renderer cells, of which
{observed_cells} are observed and {len(cell_rows)-observed_cells} are explicit
register absences.

Representative source-native parses include the formal sets
`d+aiin/d+air/d+ain/d+ar/d+al`,
`ok+aiin/ok+air/ok+ain/ok+ar/ok+al`, and parallel `yk` and `yt` sets.  The same
hosts also occur under multiple wrappers; GDT077 places weak register-dependent
WRAPPER conditioning before RIGHT_FAMILY selection.

This is the first concrete HPR4 formal paradigm lexicon, not a translation.
GDT003 remains controlling negative evidence: general transformation-algebra
prediction did not beat string baselines, so the coordinates cannot yet be
called linguistic roots or suffixes.  The class can nevertheless generate and
score exact formal alternatives.  One narrower fresh non-f84 visual prediction
is frozen and unrun.  No semantic class, role, gloss, word, morpheme, POS,
sound, language, plaintext, meaning, or translation is assigned.  f84r was
excluded and not opened, retained, queried, joined, scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT078_HPR4_FORMAL_PARADIGM_LEXICON_RESULT_V1",
        "status": status,
        "groups": len(source),
        "atlas_hosts": len(atlas_rows),
        "stable_aiin_high_hosts": stable_hosts,
        "complete_five_renderer_hosts": complete_hosts,
        "paradigm_cells": len(cell_rows),
        "observed_paradigm_cells": observed_cells,
        "frozen_predictions": len(predictions),
        "leading_theory": "PAGE_HOST is a reusable formal key with stable renderer propensities; RIGHT_FAMILY is selected conditional on PAGE_HOST, register and weakly WRAPPER.",
        "negative_evidence": "GDT003 remains NOT_DISTINGUISHABLE_FROM_STRING_STATISTICS; no linguistic morphology promotion.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {SOURCE.name: sha(SOURCE), PAIR_RATES.name: sha(PAIR_RATES), "gdt003_results.json": sha(ROOT / "gdt003_results.json"), "gdt003_nested_result.json": sha(ROOT / "gdt003_nested_result.json"), "gdt072_result.json": sha(ROOT / "gdt072_result.json"), "gdt076_result.json": sha(ROOT / "gdt076_result.json"), "gdt077_result.json": sha(ROOT / "gdt077_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {ATLAS.name: sha(ATLAS), CELLS.name: sha(CELLS), PREDICTIONS.name: sha(PREDICTIONS), MODEL.name: sha(MODEL)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "stable_hosts": stable_hosts, "complete_hosts": complete_hosts, "cells": len(cell_rows), "observed": observed_cells}, sort_keys=True))


if __name__ == "__main__":
    main()
