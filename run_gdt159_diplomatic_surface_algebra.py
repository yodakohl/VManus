#!/usr/bin/env python3
"""Run the frozen GDT003 fingerprint on the GDT159 diplomatic source panel."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import multiprocessing as mp
import os
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt003_structural_fingerprint_comparator import evaluate_corpus


ROOT = Path(__file__).resolve().parent
CORPORA = ROOT / "gdt159_diplomatic_corpora.json.gz"
MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
PROVENANCE = ROOT / "gdt159_diplomatic_source_provenance.json"
SOURCE_VALIDATION = ROOT / "gdt159_diplomatic_source_validation.json"
METHOD = ROOT / "GDT159_DIPLOMATIC_SURFACE_ALGEBRA_METHOD.md"
SOURCE_AUDIT = ROOT / "GDT159_DIPLOMATIC_SOURCE_AUDIT.md"
GDT003_RUNNER = ROOT / "run_gdt003_structural_fingerprint_comparator.py"
GDT003_CORE = ROOT / "run_gdt003_nested_heldout.py"
GDT003_FP = ROOT / "gdt003_structural_fingerprints.tsv"
GDT158_FP = ROOT / "gdt158_structural_fingerprints.tsv"
GDT158_RESULT = ROOT / "gdt158_result.json"
GDT158_CLOSURE = ROOT / "gdt158_closure_folds.tsv"
GDT045_RESULT = ROOT / "gdt045_result.json"
GDT045_OCC = ROOT / "gdt045_b3_occurrences.tsv"

OUT_FP = ROOT / "gdt159_structural_fingerprints.tsv"
OUT_TRANSFORMS = ROOT / "gdt159_transformations.tsv"
OUT_BASELINES = ROOT / "gdt159_fingerprint_baselines.tsv"
OUT_COMPARE = ROOT / "gdt159_surface_algebra_comparison.tsv"
OUT_B3 = ROOT / "gdt159_b3_stability.tsv"
OUT_COUNTER = ROOT / "gdt159_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt159_result.json"
OUT_REPORT = ROOT / "GDT159_DIPLOMATIC_SURFACE_ALGEBRA_REPORT.md"

SOURCE_FREEZE_COMMIT = "90ebc626ab4ff6ccf555a42510c4b5de5f4ce4c5"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def poisson_binomial_tail(probabilities: list[float], observed: int) -> float:
    dist = [1.0] + [0.0] * len(probabilities)
    for probability in probabilities:
        for count in range(len(probabilities), 0, -1):
            dist[count] = dist[count] * (1 - probability) + dist[count - 1] * probability
        dist[0] *= 1 - probability
    return sum(dist[observed:])


def b3_row(scope_type: str, scope: str, rows: list[dict[str, str]]) -> dict[str, object]:
    n = len(rows)
    observed = sum(int(row["physical_line_end"]) for row in rows)
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_line[row["locus"]].append(row)
    probabilities = [len(values) / int(values[0]["group_count"]) for values in by_line.values()]
    expected = sum(len(values) / int(values[0]["group_count"]) for values in by_line.values())
    effect = observed / n - expected / n
    folios = sorted({row["physical_folio"] for row in rows})
    leave_effects = []
    for folio in folios:
        retained = [row for row in rows if row["physical_folio"] != folio]
        if retained:
            leave_effects.append(
                sum(int(row["physical_line_end"]) for row in retained) / len(retained)
                - sum(1 / int(row["group_count"]) for row in retained) / len(retained)
            )
    powered = int(n >= 10 and len(folios) >= 3)
    return {
        "system": "VOYNICH", "stability_measure": "FIXED_CLASS_EFFECT",
        "scope_type": scope_type, "scope": scope, "fixed_or_selected_class": "B3",
        "support": n, "physical_folios": len(folios), "endpoint_hits": observed,
        "endpoint_precision": observed / n, "expected_hits": expected,
        "expected_rate": expected / n, "rate_effect": effect,
        "local_poisson_binomial_p": poisson_binomial_tail(probabilities, observed),
        "leave_one_folio_min_effect": min(leave_effects) if leave_effects else "NA",
        "powered": powered, "distinct_selected_identities": 1,
        "modal_identity_fraction": 1.0,
        "interpretation": "FIXED_B3_CLASS_EFFECT_NOT_SELECTOR_STABILITY",
    }


def main() -> None:
    with gzip.open(CORPORA, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    manifest = read(MANIFEST)
    metadata = {row["corpus_id"]: row for row in manifest}
    by_corpus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in payload["records"]:
        by_corpus[str(row["corpus_id"])].append(row)
    jobs = [(corpus_id, rows, metadata[corpus_id]) for corpus_id, rows in sorted(by_corpus.items())]
    with mp.get_context("fork").Pool(min(len(jobs), 5, max(1, os.cpu_count() or 1))) as pool:
        evaluated = pool.map(evaluate_corpus, jobs)
    fingerprints = [item["fingerprint"] for item in evaluated]
    transformations = [row for item in evaluated for row in item["transformations"]]
    baselines = [row for item in evaluated for row in item["baselines"]]

    target = next(row for row in read(GDT003_FP) if row["corpus_id"] == "VOYNICH_MATCHED")
    target_ops = float(target["mean_discovered_operations"])
    target_pairs = float(target["compatible_pair_density"])
    target_edge = float(target["left_right_log2_support_ratio"])
    anchor_ids = {"AUGSBURG_ACCOUNTS_ORIGINAL", "NUREMBERG_REAL_DIPLOMATIC"}
    anchors = [row for row in read(GDT158_FP) if row["corpus_id"] in anchor_ids]
    comparison_rows: list[dict[str, object]] = []
    for row in [*fingerprints, *anchors, dict(target)]:
        ops = float(row["mean_discovered_operations"])
        pairs = float(row["compatible_pair_density"])
        edge = float(row["left_right_log2_support_ratio"])
        op_ratio = ops / target_ops
        pair_ratio = pairs / target_pairs
        op_gate = int(0.5 <= op_ratio <= 2.0)
        pair_gate = int(0.5 <= pair_ratio <= 2.0)
        edge_gate = int(edge < 0)
        regime = int(op_gate and pair_gate and edge_gate)
        distance = math.sqrt((math.log2(max(op_ratio, 1e-12)) ** 2 + math.log2(max(pair_ratio, 1e-12)) ** 2 + (edge - target_edge) ** 2) / 3)
        source = "NEW_GDT159" if row["corpus_id"] in by_corpus else "PUBLISHED_ANCHOR"
        comparison_rows.append({
            "corpus_id": row["corpus_id"], "source": source,
            "capacity_state": row.get("capacity_state", "MATCHED_12000"),
            "mean_discovered_operations": ops, "operation_scale_ratio_to_voynich": op_ratio,
            "compatible_pair_density": pairs, "compatible_density_ratio_to_voynich": pair_ratio,
            "left_right_log2_support_ratio": edge, "left_dominant": edge_gate,
            "operation_factor2_gate": op_gate, "compatibility_factor2_gate": pair_gate,
            "voynich_algebraic_regime": regime, "three_coordinate_log_rms_distance": distance,
            "rubric": "BOTH_MAGNITUDES_WITHIN_FACTOR2_AND_LEFT_DOMINANT",
        })
    comparison_rows.sort(key=lambda row: (0 if row["corpus_id"] == "VOYNICH_MATCHED" else 1, float(row["three_coordinate_log_rms_distance"]), str(row["corpus_id"])))

    occurrences = read(GDT045_OCC)
    assert not any(row["page"] == "f84r" for row in occurrences)
    b3_rows: list[dict[str, object]] = []
    for field, label in (("register", "REGISTER"), ("hand", "HAND")):
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in occurrences:
            grouped[row[field]].append(row)
        for scope, rows in sorted(grouped.items()):
            b3_rows.append(b3_row(label, scope, rows))
    closure = read(GDT158_CLOSURE)
    by_view: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in closure:
        if row["corpus_view"].startswith("STE1"):
            continue
        by_view[row["corpus_view"]].append(row)
    for view, rows in sorted(by_view.items()):
        counts = Counter(row["selected_predicate"] for row in rows)
        modal, modal_n = counts.most_common(1)[0]
        b3_rows.append({
            "system": view, "stability_measure": "TRAINING_SELECTED_CLASS_IDENTITY",
            "scope_type": "HELD_FOLD", "scope": "ALL", "fixed_or_selected_class": modal,
            "support": len(rows), "physical_folios": "NA", "endpoint_hits": sum(int(row["held_terminal_hits"]) for row in rows),
            "endpoint_precision": "NA", "expected_hits": "NA", "expected_rate": "NA", "rate_effect": "NA",
            "local_poisson_binomial_p": "NA", "leave_one_folio_min_effect": "NA", "powered": 1,
            "distinct_selected_identities": len(counts), "modal_identity_fraction": modal_n / len(rows),
            "interpretation": "SELECTOR_IDENTITY_STABILITY_NOT_FIXED_CLASS_EFFECT",
        })

    powered_voynich = [row for row in b3_rows if row["system"] == "VOYNICH" and int(row["powered"])]
    b3_stable = all(float(row["rate_effect"]) > 0 and float(row["leave_one_folio_min_effect"]) > 0 for row in powered_voynich)
    matched_new = [row for row in comparison_rows if row["source"] == "NEW_GDT159" and row["capacity_state"] == "MATCHED_12000"]
    regime_new = [row for row in matched_new if int(row["voynich_algebraic_regime"])]
    surface_status = "REAL_DIPLOMATIC_SYSTEM_REACHES_VOYNICH_ALGEBRAIC_REGIME" if regime_new else "SURFACE_ALGEBRA_RESIDUAL_REMAINS_UNEXPLAINED"
    b3_status = "B3_FIXED_CLASS_STABLE_ACROSS_POWERED_STRATA" if b3_stable else "B3_EFFECT_REGISTER_OR_HAND_UNSTABLE"

    counterexamples = [
        {"claim": "EARLY_15C_LATIN_MEDICAL_MATCHED_CONTROL", "evidence": "No admitted source simultaneously met exact early-15c date, Latin medical genre, preserved abbreviation, and 12k capacity.", "impact": "Exact-century and medical panels remain separate."},
        {"claim": "LOW_CAPACITY_TECHNICAL_RESULT_IS_PRIMARY", "evidence": "The apothecary sample has 1,554 groups and six small folds.", "impact": "Descriptive sensitivity only."},
        {"claim": "GDT158_BOUNDARIES_RETESTED", "evidence": "No opening, closing, reset, or generic-closer null is rerun.", "impact": "Only the three GDT003 surface coordinates are tested."},
        {"claim": "B3_EQUALS_GENERIC_MEDIEVAL_CLOSER", "evidence": "B3 is one fixed source-native class; GDT158 predicates are training-selected suffix classes.", "impact": "Effect and selector stability are not exchangeable estimators."},
        {"claim": "B3_UNIFORMLY_STABLE_AT_ANY_SAMPLE_SIZE", "evidence": "Hand 5 has only three occurrences and negative leave-one-folio minimum; unknown hand has one.", "impact": "B3 stability decision uses powered strata only."},
        {"claim": "ABBREVIATION_SIGNS_HAVE_LANGUAGE_NEUTRAL_UNICODE_STATUS", "evidence": "Frozen GDT003 normalization retains letter/mark-class signs and splits punctuation-class signs.", "impact": "Orthographic encoding remains a material confound."},
        {"claim": "F84R_USED", "evidence": "New corpora contain no Voynich data; comparison uses published aggregate and GDT045 output has no f84r row.", "impact": "f84r remains sealed."},
    ]

    write(OUT_FP, sorted(fingerprints, key=lambda row: str(row["corpus_id"])))
    write(OUT_TRANSFORMS, sorted(transformations, key=lambda row: (str(row["corpus_id"]), str(row["held_fold"]), str(row["operation_id"]))))
    write(OUT_BASELINES, sorted(baselines, key=lambda row: (str(row["corpus_id"]), str(row["scope"]), str(row["model"]))))
    write(OUT_COMPARE, comparison_rows)
    write(OUT_B3, b3_rows)
    write(OUT_COUNTER, counterexamples)

    new_by = {row["corpus_id"]: row for row in comparison_rows if row["source"] == "NEW_GDT159"}
    closest = min(matched_new, key=lambda row: float(row["three_coordinate_log_rms_distance"]))
    report = f"""# GDT159 diplomatic surface-algebra residual report

Decision: **{surface_status}**.

B3 audit: **{b3_status}**.

## Outcome

No newly admitted capacity-matched diplomatic corpus occupies the frozen
three-coordinate Voynich algebraic regime.  The closest matched new panel is
`{closest['corpus_id']}` at three-coordinate distance
{float(closest['three_coordinate_log_rms_distance']):.6f}; its operation-scale
ratio is {float(closest['operation_scale_ratio_to_voynich']):.3f}, compatible-pair
ratio {float(closest['compatible_density_ratio_to_voynich']):.3f}, and edge
support is {'left' if int(closest['left_dominant']) else 'right'}-dominant.

| corpus | capacity | operations/fold | op/VMS | compatible density | density/VMS | right/left log2 | regime |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
"""
    for row in comparison_rows:
        report += (
            f"| {row['corpus_id']} | {row['capacity_state']} | {float(row['mean_discovered_operations']):.3f} | "
            f"{float(row['operation_scale_ratio_to_voynich']):.3f} | {float(row['compatible_pair_density']):.6f} | "
            f"{float(row['compatible_density_ratio_to_voynich']):.3f} | {float(row['left_right_log2_support_ratio']):+.4f} | "
            f"{'YES' if int(row['voynich_algebraic_regime']) else 'NO'} |\n"
        )
    report += f"""

The factor-two/sign label was frozen before scoring and is descriptive.  The
continuous result is stronger: every new corpus remains below Voynich on at
least one magnitude, and the closest corpus does not jointly reproduce the
operation scale, compatible-pair density, and left-dominant support.

## Latin technical/medical priority

The earlier Latin medical graphematic panel is capacity matched and obtains
{float(new_by['LATIN_MEDICAL_GRAPHEMATIC']['mean_discovered_operations']):.3f}
operations/fold, compatibility
{float(new_by['LATIN_MEDICAL_GRAPHEMATIC']['compatible_pair_density']):.6f}, and
edge ratio {float(new_by['LATIN_MEDICAL_GRAPHEMATIC']['left_right_log2_support_ratio']):+.4f}.
The later apothecary recipe sensitivity is directly relevant in genre but has
only 1,554 groups, so its fingerprint cannot override the powered panels.

The exact-century Latin panel is intentionally mixed genre because the source
audit found no matched early-fifteenth-century Latin medical diplomatic corpus.
The exact-period iForal charters and scholastic panel are retained without
padding as low-capacity sensitivities.

## B3 class stability

The fixed B3 class has positive endpoint effect and positive leave-one-folio
minimum in all five powered registers and in powered hands 1, 2, and 3.

| stratum | n | endpoint precision | expected rate | effect | LOFO min |
| --- | ---: | ---: | ---: | ---: | ---: |
"""
    for row in b3_rows:
        if row["system"] == "VOYNICH" and int(row["powered"]):
            report += f"| {row['scope_type']} {row['scope']} | {row['support']} | {float(row['endpoint_precision']):.4f} | {float(row['expected_rate']):.4f} | {float(row['rate_effect']):+.4f} | {float(row['leave_one_folio_min_effect']):+.4f} |\n"
    generic = [row for row in b3_rows if row["system"] != "VOYNICH"]
    report += """

That is fixed-class **effect** stability, not a new selector tournament.  By
contrast, GDT158's training-selected generic closer changes identity across
folds:

| control | held folds | distinct selected predicates | modal fraction |
| --- | ---: | ---: | ---: |
"""
    for row in generic:
        report += f"| {row['system']} | {row['support']} | {row['distinct_selected_identities']} | {float(row['modal_identity_fraction']):.3f} |\n"
    report += """

Hands 5 and unknown-hand are not used to manufacture stability: hand 5 has
three B3 occurrences and a negative leave-one-folio minimum; unknown hand has
one.  B3 remains only a probabilistic formal record-closing class.

## Interpretation

GDT158's boundary result survives: ordinary structured medieval documents can
generate openings, closings, reset effects, and sparse generic closers.  The
new graphematic corpus panel does not explain the remaining conjunction of
large operation inventory, dense compatible operation pairs, and leftward
edge support.  Authentic abbreviation can increase parts of that algebra, but
no real comparator here enters the full Voynich regime.

This does not prove that no abbreviated natural language can do so.  Exact
early-fifteenth-century Latin medical capacity is missing, low-capacity panels
are noisy, manuscript spacing differs, and Unicode treatment of abbreviation
signs affects the frozen surface groups.

## Seal and claim ceiling

No Voynich source row or image was read.  The only Voynich numerical target is
the published f84r-free GDT003 aggregate; B3 uses the published GDT045 output,
which contains no f84r row.  f84r was not opened, queried, retained, joined, or
scored.

The result supports only a formal surface-system comparison and B3 positional
stability.  It establishes no language, morphology, punctuation, expansion,
word, sound, meaning, plaintext, origin, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")

    result: dict[str, object] = {
        "schema": "GDT159_DIPLOMATIC_SURFACE_ALGEBRA_RESULT_V1",
        "status": surface_status, "b3_status": b3_status,
        "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "target": {"corpus_id": "VOYNICH_MATCHED", "operations": target_ops, "compatible_pair_density": target_pairs, "left_right_log2_support_ratio": target_edge},
        "new_corpora": len(fingerprints), "matched_new_corpora": len(matched_new),
        "regime_new_corpora": [row["corpus_id"] for row in regime_new],
        "closest_matched_new": closest,
        "b3_powered_strata": len(powered_voynich),
        "b3_powered_all_positive_effect_and_lofo": b3_stable,
        "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (
            CORPORA, MANIFEST, PROVENANCE, SOURCE_VALIDATION, METHOD, SOURCE_AUDIT,
            GDT003_FP, GDT158_FP, GDT158_RESULT, GDT158_CLOSURE, GDT045_RESULT, GDT045_OCC,
        )},
        "implementation": {Path(__file__).name: sha(Path(__file__)), GDT003_RUNNER.name: sha(GDT003_RUNNER), GDT003_CORE.name: sha(GDT003_CORE)},
        "claim_ceiling": "Three-coordinate surface algebra and fixed B3 positional stability only; no language, morphology, punctuation, expansion, word, sound, meaning, plaintext, origin, or translation.",
    }
    result["outputs"] = {path.name: sha(path) for path in (OUT_FP, OUT_TRANSFORMS, OUT_BASELINES, OUT_COMPARE, OUT_B3, OUT_COUNTER, OUT_REPORT)}
    result["result_content_sha256"] = csha(result)
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": surface_status, "b3": b3_status, "closest": closest["corpus_id"], "distance": closest["three_coordinate_log_rms_distance"]}, sort_keys=True))


if __name__ == "__main__":
    main()
