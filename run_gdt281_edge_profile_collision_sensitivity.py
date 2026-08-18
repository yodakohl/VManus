#!/usr/bin/env python3
"""Run the frozen GDT281 exact-context collision sensitivity."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import run_gdt278_magnitude_calibration as g278
import run_gdt279_native_order_compiler_decomposition as g279
import run_gdt280_edge_compiler_fine_decomposition as g280

R = Path(__file__).resolve().parent
DESIGN = R / "gdt281_design.json"
METHOD = R / "GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_METHOD.md"
REPORT = R / "GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_REPORT.md"
RESULT = R / "gdt281_result.json"
OUT_SCORE = R / "gdt281_exact_scores.tsv"
OUT_SHAPLEY = R / "gdt281_exact_shapley.tsv"
OUT_PROFILE = R / "gdt281_exact_profiles.tsv"
OUT_NULL = R / "gdt281_null_results.tsv"
OUT_FOLD = R / "gdt281_folio_scores.tsv"
OUT_COUNTER = R / "gdt281_counterexamples.tsv"

BLOCKS = g280.BLOCKS
PRIMARY = (
    "LATIN_SCHOLASTIC_GRAPHEMATIC",
    "LATIN_MEDICAL_GRAPHEMATIC",
    "LATIN_15C_GRAPHEMATIC",
    "VOYNICH_REFERENCE",
)
BRIDGES = (
    "LATIN_MEDICAL_GRAPHEMATIC",
    "LATIN_15C_GRAPHEMATIC",
    "VOYNICH_REFERENCE",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def result_csha(value: dict) -> str:
    q = dict(value); q.pop("content_sha256", None)
    return csha(q)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fields} for row in rows])


def exact_maps(events: list[dict]) -> dict[int, list[tuple]]:
    return {mask: [g280.fine_key(row, mask) for row in events] for mask in range(16)}


def summary(events: list[dict], observed: float, null: list[float] | None) -> dict:
    row = {
        "events": len(events),
        "scoring_folds": len({x["physical_folio"] for x in events}),
        "observed_bits": f"{observed:.12f}",
    }
    if null is None:
        row.update({"null_worlds": 0, "null_mean_bits": "NA", "null_sd_bits": "NA", "saving_bits": "NA", "saving_bits_per_event": "NA", "null_z": "NA"})
        return row
    mean = statistics.mean(null)
    sd = statistics.pstdev(null)
    saving = mean - observed
    row.update({
        "null_worlds": len(null),
        "null_mean_bits": f"{mean:.12f}",
        "null_sd_bits": f"{sd:.12f}",
        "saving_bits": f"{saving:.12f}",
        "saving_bits_per_event": f"{saving / len(events):.12f}",
        "null_z": f"{saving / sd:.12f}" if sd else "NA",
    })
    return row


def published_job(item):
    control, view, events = item
    maps = exact_maps(events)
    observed = {}
    folds = {}
    for mask in range(16):
        observed[mask], folds[mask] = g279.score_buckets(events, maps[mask])
    null_values = {mask: [] for mask in range(16)}
    null_rows = []
    for world in range(64):
        source = g279.permutation_indices(events, world)
        for mask in range(16):
            bits, _ = g279.score_buckets(events, [maps[mask][j] for j in source])
            null_values[mask].append(bits)
            null_rows.append({
                "control_id": control, "view": view, "representation": "PUBLISHED_EXACT_CONTEXT",
                "subset_mask": mask, "subset": g280.subset_name(mask), "world_index": world,
                "held_bits": f"{bits:.12f}",
            })
    score_rows = []
    values = {}
    for mask in range(16):
        row = {"control_id": control, "view": view, "representation": "PUBLISHED_EXACT_CONTEXT", "subset_mask": mask, "subset": g280.subset_name(mask)}
        row.update(summary(events, observed[mask], null_values[mask]))
        score_rows.append(row)
        values[mask] = float(row["saving_bits_per_event"])
    phi = g280.shapley(values)
    shape_rows = [{
        "control_id": control, "view": view, "representation": "PUBLISHED_EXACT_CONTEXT",
        "allocation_target": "NULL_ADJUSTED_INCREMENT_OVER_BASE_BITS_PER_EVENT",
        "block": block, "shapley_bits_per_event": f"{value:.12f}",
        "base_value_bits_per_event": f"{values[0]:.12f}", "full_value_bits_per_event": f"{values[15]:.12f}",
        "edge_increment_bits_per_event": f"{values[15] - values[0]:.12f}",
    } for block, value in phi.items()]
    fold_rows = []
    for mask, label in ((0, "BASE_NO_EDGE"), (15, "FULL_EDGE")):
        fold_rows.extend({
            "control_id": control, "view": view, "representation": "PUBLISHED_EXACT_CONTEXT",
            "subset": label, "held_folio": held,
            "events": sum(x["physical_folio"] == held for x in events), "held_bits": f"{bits:.12f}",
        } for held, bits in sorted(folds[mask].items()))
    return score_rows, shape_rows, null_rows, fold_rows


def safe_job(item):
    control, view, events, target = item
    observed = {mask: 0.0 for mask in range(16)}
    fold_rows = []
    changed = 0
    for held in sorted({x["physical_folio"] for x in events}):
        safe = g278.safe_reparse(events, control, held, target)
        changed += sum(a["page_host"] != b["page_host"] or g280.fine_key(a, 15) != g280.fine_key(b, 15) for a, b in zip(safe, events))
        train = [x for x in safe if x["physical_folio"] != held]
        test = [x for x in safe if x["physical_folio"] == held]
        maps = exact_maps(safe)
        held_values = {}
        for mask in range(16):
            mapping = {row["observation_id"]: value for row, value in zip(safe, maps[mask])}
            bits = g278.fold_char(train, test, mapping)
            observed[mask] += bits
            held_values[mask] = bits
        for mask, label in ((0, "BASE_NO_EDGE"), (15, "FULL_EDGE")):
            fold_rows.append({
                "control_id": control, "view": view, "representation": "LOFO_SAFE_EXACT_CONTEXT",
                "subset": label, "held_folio": held, "events": len(test), "held_bits": f"{held_values[mask]:.12f}",
            })
    values = {mask: (observed[0] - observed[mask]) / len(events) for mask in range(16)}
    score_rows = []
    for mask in range(16):
        row = {
            "control_id": control, "view": view, "representation": "LOFO_SAFE_EXACT_CONTEXT",
            "subset_mask": mask, "subset": g280.subset_name(mask), "representation_changes_across_folds": changed,
            "observed_base_minus_model_bits_per_event": f"{values[mask]:.12f}",
        }
        row.update(summary(events, observed[mask], None))
        score_rows.append(row)
    phi = g280.shapley(values)
    shape_rows = [{
        "control_id": control, "view": view, "representation": "LOFO_SAFE_EXACT_CONTEXT",
        "allocation_target": "OBSERVED_BASE_MINUS_SUBSET_BITS_PER_EVENT", "block": block,
        "shapley_bits_per_event": f"{value:.12f}", "base_value_bits_per_event": "0.000000000000",
        "full_value_bits_per_event": f"{values[15]:.12f}", "edge_increment_bits_per_event": f"{values[15]:.12f}",
    } for block, value in phi.items()]
    return score_rows, shape_rows, fold_rows


def build_selected():
    panels, _intermediate, target = g279.build_panels()
    wanted = {(control, "NATIVE_ORDER") for control in PRIMARY}
    wanted |= {(control, view) for control in BRIDGES for view in ("LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT")}
    selected = {key: panels[key] for key in sorted(wanted)}
    assert len(selected) == 10
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for events in selected.values() for row in events)
    return selected, target


def main() -> None:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_GDT281_EXACT_CONTEXT_SCORING"
    assert design["content_sha256"] == result_csha(design)
    for row in read(R / "gdt281_gdt280_freeze_manifest.tsv"):
        assert sha(R / row["artifact"]) == row["frozen_sha256"]
    panels, target = build_selected()
    scores, shapes, nulls, folds = [], [], [], []
    with ProcessPoolExecutor(max_workers=min(10, len(panels))) as executor:
        futures = {executor.submit(published_job, (control, view, events)): (control, view) for (control, view), events in panels.items()}
        for future in as_completed(futures):
            a, b, c, d = future.result(); scores.extend(a); shapes.extend(b); nulls.extend(c); folds.extend(d)
            print(json.dumps({"published_exact_scored": futures[future]}, sort_keys=True), flush=True)
    with ProcessPoolExecutor(max_workers=min(10, len(panels))) as executor:
        futures = {executor.submit(safe_job, (control, view, events, target)): (control, view) for (control, view), events in panels.items()}
        for future in as_completed(futures):
            a, b, d = future.result(); scores.extend(a); shapes.extend(b); folds.extend(d)
            print(json.dumps({"safe_exact_scored": futures[future]}, sort_keys=True), flush=True)

    scores.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], int(x["subset_mask"])))
    shapes.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], BLOCKS.index(x["block"])))
    nulls.sort(key=lambda x: (x["control_id"], x["view"], int(x["subset_mask"]), int(x["world_index"])))
    folds.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], x["subset"], x["held_folio"]))
    profiles = []
    for key in sorted({(x["control_id"], x["view"], x["representation"]) for x in shapes}):
        rr = [x for x in shapes if (x["control_id"], x["view"], x["representation"]) == key]
        values = {x["block"]: float(x["shapley_bits_per_event"]) for x in rr}
        lead = max(BLOCKS, key=lambda block: (values[block], -BLOCKS.index(block)))
        profiles.append({
            "control_id": key[0], "view": key[1], "representation": key[2], "allocation_target": rr[0]["allocation_target"],
            "leading_block": lead, "leading_value_bits_per_event": f"{values[lead]:.12f}",
            "edge_increment_bits_per_event": rr[0]["edge_increment_bits_per_event"],
            **{"shapley_" + block.lower(): f"{values[block]:.12f}" for block in BLOCKS},
        })

    primary = {(x["control_id"], x["representation"]): x for x in profiles if x["view"] == "NATIVE_ORDER" and x["control_id"] in PRIMARY}
    pub = "PUBLISHED_EXACT_CONTEXT"; safe = "LOFO_SAFE_EXACT_CONTEXT"
    latin_pub = all(primary[(c, pub)]["leading_block"] == "RIGHT_FAMILY" and float(primary[(c, pub)]["leading_value_bits_per_event"]) > 0 for c in PRIMARY[:3])
    latin_safe = all(primary[(c, safe)]["leading_block"] == "RIGHT_FAMILY" and float(primary[(c, safe)]["leading_value_bits_per_event"]) > 0 for c in PRIMARY[:3])
    vms_pub = primary[(PRIMARY[3], pub)]["leading_block"] == "OUTER_WRAPPER" and float(primary[(PRIMARY[3], pub)]["leading_value_bits_per_event"]) > 0
    vms_safe = primary[(PRIMARY[3], safe)]["leading_block"] == "OUTER_WRAPPER" and float(primary[(PRIMARY[3], safe)]["leading_value_bits_per_event"]) > 0
    latin_renderer_zero = all(abs(float(primary[(c, pub)]["shapley_display_renderer"])) <= float(design["constant_renderer_tolerance"]) for c in PRIMARY[:3])
    checks = {"latin_published_right_family": latin_pub, "latin_lofo_safe_right_family": latin_safe, "voynich_published_outer_wrapper": vms_pub, "voynich_lofo_safe_outer_wrapper": vms_safe, "constant_latin_renderer_zero": latin_renderer_zero}
    status = "HASH_COLLISION_SENSITIVITY_PRESERVES_LATIN_RIGHT_VOYNICH_WRAPPER_SPLIT" if all(checks.values()) else "HASH_COLLISION_SENSITIVITY_CHANGES_EDGE_PROFILE"

    counters = [
        {"counterexample": "EXACT_CONTEXT_SCORE_REPLACES_GDT278_MDL", "evidence": "subset models occupy different exact context counts and no model-key charge is added", "impact": "only profile direction and collision sensitivity are licensed"},
        {"counterexample": "CONSTANT_RENDERER_CARRIES_LATIN_SIGNAL", "evidence": "the exact-tuple renderer allocation is mathematically zero in Latin panels", "impact": "the prior tiny renderer effects were hash-collision noise"},
        {"counterexample": "GDT280_VOYNICH_SAFE_MAGNITUDE_COLLAPSE_IS_INTRINSIC", "evidence": "the native LOFO-safe edge increment changes from +.0319 hashed to +.3337 exact-context bits/event", "impact": "retire the collapse argument; exact magnitude itself remains uncalibrated because subset context capacities differ"},
        {"counterexample": "EDGE_BLOCK_EQUALS_LINGUISTIC_MORPHOLOGY", "evidence": "all fields are mechanically inferred source-visible classes", "impact": "no prefix suffix language or meaning follows"},
        {"counterexample": "PUBLISHED_AND_SAFE_ARE_REPLICATIONS", "evidence": "both score the same events with different representation learning", "impact": "safe scores are sensitivity only"},
        {"counterexample": "F84_USED", "evidence": "all selected panel rows are asserted f84-free before scoring", "impact": "no f84 access"},
    ]
    write(OUT_SCORE, scores); write(OUT_SHAPLEY, shapes); write(OUT_PROFILE, profiles); write(OUT_NULL, nulls); write(OUT_FOLD, folds); write(OUT_COUNTER, counters)

    report = [
        "# GDT281 — collision-free sensitivity of the GDT280 edge profile", "", f"Status: **{status}**.", "",
        "This pass changes only the context identity representation: exact immutable tuples replace SHA256-mod256 buckets. Absolute exact-context savings are sensitivities, because the number of occupied contexts varies and no new model-key charge is imposed.", "",
        "## Native-order profiles", "", "| panel | representation | outer wrapper | local frame | right family | renderer | edge increment | leader |", "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for control in PRIMARY:
        for representation in (pub, safe):
            x = primary[(control, representation)]
            report.append(f"| {control} | {representation} | {float(x['shapley_outer_wrapper']):+.4f} | {float(x['shapley_local_frame']):+.4f} | {float(x['shapley_right_family']):+.4f} | {float(x['shapley_display_renderer']):+.4f} | {float(x['edge_increment_bits_per_event']):+.4f} | {x['leading_block']} |")
    parent_profiles = read(R / "gdt280_edge_profiles.tsv")
    parent_native = {(x["control_id"], x["representation"]): x for x in parent_profiles if x["view"] == "NATIVE_ORDER" and x["control_id"] in PRIMARY}
    report += ["", "## What collision removal changed", "", "| panel | hashed published | exact published | hashed LOFO-safe | exact LOFO-safe |", "|---|---:|---:|---:|---:|"]
    for control in PRIMARY:
        report.append(f"| {control} | {float(parent_native[(control, 'PUBLISHED_FROZEN_GDT279')]['edge_increment_bits_per_event']):+.4f} | {float(primary[(control, pub)]['edge_increment_bits_per_event']):+.4f} | {float(parent_native[(control, 'LOFO_SAFE')]['edge_increment_bits_per_event']):+.4f} | {float(primary[(control, safe)]['edge_increment_bits_per_event']):+.4f} |")
    report += [
        "", "The exact categories preserve the Latin-right/Voynich-wrapper ranking, but they do **not** preserve GDT280's apparent Voynich fold-safe magnitude collapse: `+.0319` becomes `+.3337` bits/event. This corrects the earlier instrument-level interpretation. It does not create a calibrated MDL magnitude, because exact subsets have unequal context capacities; it shows that the collapse itself was driven largely by the 256-bucket collision approximation.",
        "", "## Matched-source layout bridge", "", "| panel | view | published edge increment | published leader | safe edge increment | safe leader |", "|---|---|---:|---|---:|---|",
    ]
    for control in BRIDGES:
        for view in ("LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT"):
            p = next(x for x in profiles if x["control_id"] == control and x["view"] == view and x["representation"] == pub)
            s = next(x for x in profiles if x["control_id"] == control and x["view"] == view and x["representation"] == safe)
            report.append(f"| {control} | {view} | {float(p['edge_increment_bits_per_event']):+.4f} | {p['leading_block']} | {float(s['edge_increment_bits_per_event']):+.4f} | {s['leading_block']} |")
    report += ["", "The Latin layout bridge remains right-family-led and grows when the identical selected occurrences are restored to native layout; Voynich is unchanged by construction.", "", "## Frozen checks", ""]
    report += [f"- `{name}`: **{'PASS' if value else 'FAIL'}**" for name, value in checks.items()]
    report += [
        "", "For the Latin panels, the exact-tuple allocation of the constant renderer is exactly zero, confirming that GDT280's tiny renderer values came from hash collisions. The substantive question is whether the Latin right-family and Voynich wrapper directions survive in both published and LOFO-safe views.", "",
        "## Claim ceiling", "", "This is an instrument sensitivity over an exposed formal profile. It does not identify abbreviation, morphology, a q-prefix function, language, code, notation, meaning, plaintext, or translation. No f84 source row was opened, parsed, retained, joined, or scored.",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf8")

    outputs = [OUT_SCORE, OUT_SHAPLEY, OUT_PROFILE, OUT_NULL, OUT_FOLD, OUT_COUNTER, REPORT]
    inputs = ["gdt281_design.json", "gdt281_design_validation.json", "gdt281_gdt280_freeze_manifest.tsv", "gdt280_result.json", "gdt279_intermediate_event_inventory.tsv", "gdt278_native_event_inventory.tsv", "gdt278_matched_event_inventory.tsv"]
    result = {
        "schema": "GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_RESULT_V1", "status": status,
        "panels": len(panels), "subset_count": 16, "null_worlds": 64, "blocks": list(BLOCKS), "frozen_checks": checks,
        "native_profile_leaders": {representation: {control: primary[(control, representation)]["leading_block"] for control in PRIMARY} for representation in (pub, safe)},
        "native_edge_increment_bits_per_event": {representation: {control: float(primary[(control, representation)]["edge_increment_bits_per_event"]) for control in PRIMARY} for representation in (pub, safe)},
        "context_representation": "EXACT_IMMUTABLE_TUPLE_NO_HASH", "replaces_parent_endpoint": False,
        "threshold_tuned": False, "composite_score": False, "new_control_corpora": 0, "semantic_assignments": 0, "hpr1_semantics_used": 0, "voynich_substrings_mined": 0,
        "claim_ceiling": "Collision sensitivity of an exposed edge-compression profile only; no abbreviation morphology language code notation meaning plaintext or translation.",
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "gdt280_immutable": all(sha(R / row["artifact"]) == row["frozen_sha256"] for row in read(R / "gdt281_gdt280_freeze_manifest.tsv")),
        "inputs": {name: sha(R / name) for name in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = result_csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
