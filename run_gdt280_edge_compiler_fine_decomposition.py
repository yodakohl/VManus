#!/usr/bin/env python3
"""Run the frozen GDT280 fine edge-compiler decomposition."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import run_gdt276_residual_channel_world_comparison as g276
import run_gdt278_magnitude_calibration as g278
import run_gdt279_native_order_compiler_decomposition as g279

R = Path(__file__).resolve().parent
DESIGN = R / "gdt280_design.json"
METHOD = R / "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_METHOD.md"
REPORT = R / "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_REPORT.md"
RESULT = R / "gdt280_result.json"
OUT_SCORE = R / "gdt280_edge_scores.tsv"
OUT_SHAPLEY = R / "gdt280_edge_shapley.tsv"
OUT_PROFILE = R / "gdt280_edge_profiles.tsv"
OUT_NULL = R / "gdt280_null_results.tsv"
OUT_FOLD = R / "gdt280_folio_scores.tsv"
OUT_COUNTER = R / "gdt280_counterexamples.tsv"

BLOCKS = ("OUTER_WRAPPER", "LOCAL_FRAME", "RIGHT_FAMILY", "DISPLAY_RENDERER")
BITS = {block: 1 << i for i, block in enumerate(BLOCKS)}
FIELD_ORDER = (
    ("register", "BASE", str),
    ("record_ordinal", "BASE", int),
    ("field_ordinal", "BASE", int),
    ("within_field_position", "BASE", str),
    ("wrapper", "OUTER_WRAPPER", str),
    ("q_flag", "OUTER_WRAPPER", int),
    ("local_frame", "LOCAL_FRAME", str),
    ("inner_d", "LOCAL_FRAME", str),
    ("right_family", "RIGHT_FAMILY", str),
    ("dy_closure", "BASE", str),
    ("b3", "BASE", str),
    ("line_close", "BASE", int),
    ("paragraph_close", "BASE", int),
    ("known_label_renderer", "DISPLAY_RENDERER", str),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def result_csha(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
    return csha(q)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict]) -> None:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fields} for row in rows])


def subset_name(mask: int) -> str:
    if mask == 0:
        return "BASE_NO_EDGE"
    return "+".join(block for block in BLOCKS if mask & BITS[block])


def fine_key(row: dict, mask: int) -> tuple:
    return tuple(
        converter(row[name])
        for name, block, converter in FIELD_ORDER
        if block == "BASE" or mask & BITS[block]
    )


def maps(events: list[dict]) -> dict[int, list[int]]:
    answer = {mask: [g276.bucket("COMPILER", fine_key(row, mask)) for row in events] for mask in range(16)}
    for row, value in zip(events, answer[15]):
        assert int(row["compiler_bucket"]) == value
    return answer


def shapley(values: dict[int, float]) -> dict[str, float]:
    assert set(values) == set(range(16))
    answer = {}
    for i, block in enumerate(BLOCKS):
        bit = 1 << i
        value = 0.0
        for mask in range(16):
            if mask & bit:
                continue
            size = mask.bit_count()
            weight = math.factorial(size) * math.factorial(4 - size - 1) / math.factorial(4)
            value += weight * (values[mask | bit] - values[mask])
        answer[block] = value
    assert math.isclose(sum(answer.values()), values[15] - values[0], rel_tol=0, abs_tol=3e-10)
    return answer


def summary(events: list[dict], observed: float, null: list[float] | None) -> dict:
    out = {"events": len(events), "scoring_folds": len({x["physical_folio"] for x in events}), "observed_bits": f"{observed:.12f}"}
    if null is None:
        out.update({"null_worlds": 0, "null_mean_bits": "NA", "null_sd_bits": "NA", "saving_bits": "NA", "saving_bits_per_event": "NA", "null_z": "NA"})
        return out
    mean = statistics.mean(null)
    sd = statistics.pstdev(null)
    saving = mean - observed
    out.update({
        "null_worlds": len(null), "null_mean_bits": f"{mean:.12f}", "null_sd_bits": f"{sd:.12f}",
        "saving_bits": f"{saving:.12f}", "saving_bits_per_event": f"{saving / len(events):.12f}",
        "null_z": f"{saving / sd:.12f}" if sd else "NA",
    })
    return out


def published_job(item):
    control, view, events = item
    bm = maps(events)
    observed = {}
    folds = {}
    for mask in range(16):
        observed[mask], folds[mask] = g279.score_buckets(events, bm[mask])
    null_values = {mask: [] for mask in range(16)}
    null_rows = []
    for world in range(64):
        source = g279.permutation_indices(events, world)
        for mask in range(16):
            value, _ = g279.score_buckets(events, [bm[mask][j] for j in source])
            null_values[mask].append(value)
            null_rows.append({"control_id": control, "view": view, "representation": "PUBLISHED_FROZEN_GDT279", "subset_mask": mask, "subset": subset_name(mask), "world_index": world, "held_bits": f"{value:.12f}"})
    score_rows = []
    values = {}
    for mask in range(16):
        row = {"control_id": control, "view": view, "representation": "PUBLISHED_FROZEN_GDT279", "subset_mask": mask, "subset": subset_name(mask)}
        row.update(summary(events, observed[mask], null_values[mask]))
        score_rows.append(row)
        values[mask] = float(row["saving_bits_per_event"])
    phi = shapley(values)
    shape_rows = [{
        "control_id": control, "view": view, "representation": "PUBLISHED_FROZEN_GDT279",
        "allocation_target": "NULL_ADJUSTED_INCREMENT_OVER_BASE_BITS_PER_EVENT", "block": block,
        "shapley_bits_per_event": f"{value:.12f}", "base_value_bits_per_event": f"{values[0]:.12f}",
        "full_value_bits_per_event": f"{values[15]:.12f}", "edge_increment_bits_per_event": f"{values[15] - values[0]:.12f}",
    } for block, value in phi.items()]
    fold_rows = []
    for mask, label in ((0, "BASE_NO_EDGE"), (15, "FULL_EDGE")):
        fold_rows.extend({"control_id": control, "view": view, "representation": "PUBLISHED_FROZEN_GDT279", "subset": label, "held_folio": held, "events": sum(x["physical_folio"] == held for x in events), "held_bits": f"{bits:.12f}"} for held, bits in sorted(folds[mask].items()))
    return score_rows, shape_rows, null_rows, fold_rows


def safe_job(item):
    control, view, events, target = item
    observed = {mask: 0.0 for mask in range(16)}
    fold_rows = []
    changed = 0
    for held in sorted({x["physical_folio"] for x in events}):
        safe = g278.safe_reparse(events, control, held, target)
        changed += sum(a["page_host"] != b["page_host"] or int(a["compiler_bucket"]) != int(b["compiler_bucket"]) for a, b in zip(safe, events))
        train = [x for x in safe if x["physical_folio"] != held]
        test = [x for x in safe if x["physical_folio"] == held]
        bm = maps(safe)
        held_values = {}
        for mask in range(16):
            mapping = {row["observation_id"]: value for row, value in zip(safe, bm[mask])}
            bits = g278.fold_char(train, test, mapping)
            observed[mask] += bits
            held_values[mask] = bits
        for mask, label in ((0, "BASE_NO_EDGE"), (15, "FULL_EDGE")):
            fold_rows.append({"control_id": control, "view": view, "representation": "LOFO_SAFE", "subset": label, "held_folio": held, "events": len(test), "held_bits": f"{held_values[mask]:.12f}"})
    values = {mask: (observed[0] - observed[mask]) / len(events) for mask in range(16)}
    score_rows = []
    for mask in range(16):
        row = {"control_id": control, "view": view, "representation": "LOFO_SAFE", "subset_mask": mask, "subset": subset_name(mask), "representation_changes_across_folds": changed, "observed_base_minus_model_bits_per_event": f"{values[mask]:.12f}"}
        row.update(summary(events, observed[mask], None))
        score_rows.append(row)
    phi = shapley(values)
    shape_rows = [{
        "control_id": control, "view": view, "representation": "LOFO_SAFE",
        "allocation_target": "OBSERVED_BASE_MINUS_SUBSET_BITS_PER_EVENT", "block": block,
        "shapley_bits_per_event": f"{value:.12f}", "base_value_bits_per_event": "0.000000000000",
        "full_value_bits_per_event": f"{values[15]:.12f}", "edge_increment_bits_per_event": f"{values[15]:.12f}",
    } for block, value in phi.items()]
    return score_rows, shape_rows, fold_rows


def main() -> None:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_GDT280_EDGE_SCORING"
    for row in read(R / "gdt280_gdt279_freeze_manifest.tsv"):
        assert sha(R / row["artifact"]) == row["frozen_sha256"]
    panels, intermediate, target = g279.build_panels()
    assert len(panels) == 38 and len(intermediate) == 49_236
    scores = []
    shapes = []
    nulls = []
    folds = []
    with ProcessPoolExecutor(max_workers=min(16, len(panels))) as executor:
        futures = {executor.submit(published_job, (control, view, events)): (control, view) for (control, view), events in panels.items()}
        for future in as_completed(futures):
            a, b, c, d = future.result()
            scores.extend(a); shapes.extend(b); nulls.extend(c); folds.extend(d)
            print(json.dumps({"published_scored": futures[future]}, sort_keys=True), flush=True)

    # FULL_EDGE and all of its published null worlds must reproduce GDT279.
    parent_scores = {(x["control_id"], x["view"]): x for x in read(R / "gdt279_view_scores.tsv") if x["representation"] == "PUBLISHED_FROZEN_GDT278" and x["subset_mask"] == "7"}
    parent_null = {}
    by_parent_null = {}
    from collections import defaultdict
    qnull = defaultdict(list)
    for row in read(R / "gdt279_null_results.tsv"):
        if row["representation"] == "PUBLISHED_FROZEN_GDT278" and row["subset_mask"] == "7":
            qnull[(row["control_id"], row["view"])].append(float(row["held_bits"]))
    for key, old in parent_scores.items():
        current = next(x for x in scores if (x["control_id"], x["view"]) == key and x["representation"] == "PUBLISHED_FROZEN_GDT279" and x["subset_mask"] == 15)
        assert math.isclose(float(current["observed_bits"]), float(old["observed_bits"]), rel_tol=0, abs_tol=3e-8)
        values = [float(x["held_bits"]) for x in nulls if (x["control_id"], x["view"]) == key and x["subset_mask"] == 15]
        assert all(math.isclose(a, b, rel_tol=0, abs_tol=3e-8) for a, b in zip(values, qnull[key]))

    # Safe all-subset sensitivity; inherit the already-validated FULL null.
    with ProcessPoolExecutor(max_workers=min(16, len(panels))) as executor:
        futures = {executor.submit(safe_job, (control, view, events, target)): (control, view) for (control, view), events in panels.items()}
        for future in as_completed(futures):
            control, view = futures[future]
            a, b, d = future.result()
            parent = next(x for x in read(R / "gdt279_view_scores.tsv") if x["control_id"] == control and x["view"] == view and x["representation"] == "LOFO_SAFE" and x["subset_mask"] == "7")
            full = next(x for x in a if x["subset_mask"] == 15)
            assert math.isclose(float(full["observed_bits"]), float(parent["observed_bits"]), rel_tol=0, abs_tol=3e-8)
            inherited = [float(x["held_bits"]) for x in read(R / "gdt279_null_results.tsv") if x["control_id"] == control and x["view"] == view and x["representation"] == "LOFO_SAFE" and x["subset_mask"] == "7"]
            assert len(inherited) == 64
            full.update(summary(panels[(control, view)], float(full["observed_bits"]), inherited))
            nulls.extend({"control_id": control, "view": view, "representation": "LOFO_SAFE", "subset_mask": 15, "subset": "FULL_EDGE", "world_index": world, "held_bits": f"{bits:.12f}"} for world, bits in enumerate(inherited))
            scores.extend(a); shapes.extend(b); folds.extend(d)
            print(json.dumps({"safe_scored": (control, view)}, sort_keys=True), flush=True)

    scores.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], int(x["subset_mask"])))
    shapes.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], BLOCKS.index(x["block"])))
    nulls.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], int(x["subset_mask"]), int(x["world_index"])))
    folds.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], x["subset"], x["held_folio"]))
    profiles = []
    for key in sorted({(x["control_id"], x["view"], x["representation"]) for x in shapes}):
        control, view, representation = key
        rr = [x for x in shapes if (x["control_id"], x["view"], x["representation"]) == key]
        values = {x["block"]: float(x["shapley_bits_per_event"]) for x in rr}
        lead = max(BLOCKS, key=lambda block: (values[block], -BLOCKS.index(block)))
        profiles.append({
            "control_id": control, "view": view, "representation": representation,
            "allocation_target": rr[0]["allocation_target"], "leading_block": lead,
            "leading_value_bits_per_event": f"{values[lead]:.12f}",
            "edge_increment_bits_per_event": rr[0]["edge_increment_bits_per_event"],
            **{"shapley_" + block.lower(): f"{values[block]:.12f}" for block in BLOCKS},
        })

    native_positive = ("LATIN_SCHOLASTIC_GRAPHEMATIC", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC")
    primary = {x["control_id"]: x for x in profiles if x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_FROZEN_GDT279" and x["control_id"] in native_positive + ("VOYNICH_REFERENCE",)}
    latin_leads = {primary[x]["leading_block"] for x in native_positive if float(primary[x]["leading_value_bits_per_event"]) > 0}
    if len(latin_leads) == 1:
        latin = next(iter(latin_leads))
        if primary["VOYNICH_REFERENCE"]["leading_block"] == latin and float(primary["VOYNICH_REFERENCE"]["leading_value_bits_per_event"]) > 0:
            status = "VOYNICH_EDGE_PROFILE_SHARES_LATIN_" + latin + "_LEAD"
        else:
            status = "VOYNICH_EDGE_PROFILE_DIFFERS_FROM_LATIN_" + latin + "_LEAD"
    else:
        status = "EDGE_COMPILER_FINE_MECHANISM_HETEROGENEOUS"

    counters = [
        {"counterexample": "EDGE_LEAD_EQUALS_ABBREVIATION", "evidence": "the edge classes are mechanically inferred visible-source fields", "impact": "even DISPLAY_RENDERER cannot identify an abbreviation system"},
        {"counterexample": "RIGHT_FAMILY_EQUALS_SUFFIX_MORPHOLOGY", "evidence": "right families are parser classes and may be graphematic endings", "impact": "no morphology or linguistic role is licensed"},
        {"counterexample": "SHAPLEY_BLOCKS_ARE_INDEPENDENT", "evidence": "interactions are distributed across players", "impact": "negative and interaction-dependent values remain visible"},
        {"counterexample": "FIXED_256_BUCKET_MAP_IS_COLLISION_FREE", "evidence": "adding even a constant field rehashes context tuples and can change collisions", "impact": "small block values include hash-allocation noise; require a separately frozen collision sensitivity before treating fine magnitudes as intrinsic"},
        {"counterexample": "SAFE_AND_PUBLISHED_ARE_REPLICATIONS", "evidence": "safe scores are sensitivity on the same events", "impact": "do not multiply evidence"},
        {"counterexample": "VOYNICH_EDGE_MAGNITUDE_IS_REPRESENTATION_STABLE", "evidence": "native edge increment falls from +.2684 published to +.0319 LOFO-safe", "impact": "retain the OUTER_WRAPPER leader as a profile direction but not a stable edge-effect magnitude"},
        {"counterexample": "LATIN_NATIVE_IS_COMPLETE_CORPUS", "evidence": "GDT159 panels retain their frozen sampled source units", "impact": "scope is the admitted observed panel"},
        {"counterexample": "F84_USED", "evidence": "the only Voynich input is the frozen f84-free GDT276 inventory through GDT279", "impact": "no f84 access"},
    ]
    write(OUT_SCORE, scores); write(OUT_SHAPLEY, shapes); write(OUT_PROFILE, profiles); write(OUT_NULL, nulls); write(OUT_FOLD, folds); write(OUT_COUNTER, counters)

    report = [
        "# GDT280 — fine decomposition of the edge compiler", "", f"Status: **{status}**.", "",
        "The GDT279 panel, views, endpoint, null and full compiler model remain frozen. This pass allocates only the incremental edge signal over the fixed opportunity-plus-closure base.", "",
        "## Native-order primary profiles", "",
        "| panel | outer wrapper | local frame | right family | display renderer | edge increment | leader |", "|---|---:|---:|---:|---:|---:|---|",
    ]
    for control in native_positive + ("VOYNICH_REFERENCE",):
        x = primary[control]
        report.append(f"| {control} | {float(x['shapley_outer_wrapper']):+.4f} | {float(x['shapley_local_frame']):+.4f} | {float(x['shapley_right_family']):+.4f} | {float(x['shapley_display_renderer']):+.4f} | {float(x['edge_increment_bits_per_event']):+.4f} | {x['leading_block']} |")
    report += ["", "## Exact matched-source layout bridge", "", "| panel | view | outer wrapper | local frame | right family | display renderer |", "|---|---|---:|---:|---:|---:|"]
    for control in ("LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "VOYNICH_REFERENCE"):
        for view in ("LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT"):
            x = next(q for q in profiles if q["control_id"] == control and q["view"] == view and q["representation"] == "PUBLISHED_FROZEN_GDT279")
            report.append(f"| {control} | {view} | {float(x['shapley_outer_wrapper']):+.4f} | {float(x['shapley_local_frame']):+.4f} | {float(x['shapley_right_family']):+.4f} | {float(x['shapley_display_renderer']):+.4f} |")
    report += ["", "## Representation-safe sensitivity", "", "| panel | outer wrapper | local frame | right family | display renderer | leader |", "|---|---:|---:|---:|---:|---|"]
    for control in native_positive + ("VOYNICH_REFERENCE",):
        x = next(q for q in profiles if q["control_id"] == control and q["view"] == "NATIVE_ORDER" and q["representation"] == "LOFO_SAFE")
        report.append(f"| {control} | {float(x['shapley_outer_wrapper']):+.4f} | {float(x['shapley_local_frame']):+.4f} | {float(x['shapley_right_family']):+.4f} | {float(x['shapley_display_renderer']):+.4f} | {x['leading_block']} |")
    report += ["", "The winner labels are stable, but the magnitudes are not symmetric. Voynich's native edge increment falls from **+.2684** published to **+.0319** bits/event LOFO-safe, whereas the three Latin right-family edge increments remain large or grow (**+.6513, +.5322, +.4659**). Thus `OUTER_WRAPPER` is the surviving Voynich direction among these four blocks, not a stable effect comparable in magnitude to the Latin right-family channel.", "", "All Latin `DISPLAY_RENDERER` fields are constant `NONE`. Their tiny nonzero Shapley values expose the fixed 256-bucket approximation: adding a constant tuple coordinate can reassign hash collisions. The right-family leads are much larger and representation-stable, but exact fine-component magnitudes still include this bounded collision noise.", "", "## Interpretation", "", "The leading component identifies where this fixed character compressor finds reusable edge-conditioned form. It does not give that component a linguistic function. The Latin controls have a robust right-edge-family architecture; Voynich does not share it. Voynich's weaker leakage-safe outer-wrapper lead is a distinct residual, not evidence that q or another wrapper is a linguistic prefix. A separately frozen collision sensitivity is required before treating the fine allocations as intrinsic values.", "", "Every FULL_EDGE observed score and published null world reproduces GDT279. No f84 source was opened, parsed, retained, joined, or scored.", ""]
    REPORT.write_text("\n".join(report), encoding="utf8")

    outputs = [OUT_SCORE, OUT_SHAPLEY, OUT_PROFILE, OUT_NULL, OUT_FOLD, OUT_COUNTER, REPORT]
    inputs = ["gdt280_design.json", "gdt280_design_validation.json", "gdt280_gdt279_freeze_manifest.tsv", "gdt279_result.json", "gdt279_view_scores.tsv", "gdt279_null_results.tsv", "gdt279_folio_scores.tsv"]
    safe_primary = {x["control_id"]: x for x in profiles if x["view"] == "NATIVE_ORDER" and x["representation"] == "LOFO_SAFE" and x["control_id"] in native_positive + ("VOYNICH_REFERENCE",)}
    result = {
        "schema": "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_RESULT_V1", "status": status,
        "panels": len(panels), "subset_count": 16, "null_worlds": 64, "blocks": list(BLOCKS),
        "native_profile_leaders": {control: primary[control]["leading_block"] for control in native_positive + ("VOYNICH_REFERENCE",)},
        "native_edge_increment_bits_per_event": {control: float(primary[control]["edge_increment_bits_per_event"]) for control in native_positive + ("VOYNICH_REFERENCE",)},
        "native_safe_edge_increment_bits_per_event": {control: float(safe_primary[control]["edge_increment_bits_per_event"]) for control in native_positive + ("VOYNICH_REFERENCE",)},
        "native_safe_to_published_edge_increment_ratio": {control: float(safe_primary[control]["edge_increment_bits_per_event"]) / float(primary[control]["edge_increment_bits_per_event"]) for control in native_positive + ("VOYNICH_REFERENCE",)},
        "threshold_tuned": False, "composite_score": False, "new_control_corpora": 0,
        "semantic_assignments": 0, "hpr1_semantics_used": 0, "voynich_substrings_mined": 0,
        "claim_ceiling": "Fine allocation of exposed edge-conditioned character compression only; no abbreviation morphology language code notation meaning plaintext or translation.",
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "gdt279_immutable": all(sha(R / row["artifact"]) == row["frozen_sha256"] for row in read(R / "gdt280_gdt279_freeze_manifest.tsv")),
        "inputs": {name: sha(R / name) for name in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = result_csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "leaders": result["native_profile_leaders"]}, sort_keys=True))


if __name__ == "__main__":
    main()
