#!/usr/bin/env python3
"""Run the frozen GDT279 native-order/compiler block decomposition."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import run_gdt276_residual_channel_world_comparison as g276
import run_gdt277_signature_calibration as g277
import run_gdt278_magnitude_calibration as g278

R = Path(__file__).resolve().parent
DESIGN = R / "gdt279_design.json"
DESIGN_VALID = R / "gdt279_design_validation.json"
METHOD = R / "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_METHOD.md"
REPORT = R / "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_REPORT.md"
RESULT = R / "gdt279_result.json"
OUT_INTERMEDIATE = R / "gdt279_intermediate_event_inventory.tsv"
OUT_SCORES = R / "gdt279_view_scores.tsv"
OUT_SHAPLEY = R / "gdt279_block_shapley.tsv"
OUT_CONTRASTS = R / "gdt279_view_contrasts.tsv"
OUT_FOLDS = R / "gdt279_folio_scores.tsv"
OUT_NULL = R / "gdt279_null_results.tsv"
OUT_COUNTER = R / "gdt279_counterexamples.tsv"

BLOCKS = ("OPPORTUNITY", "EDGE_COMPILER", "CLOSURE_BOUNDARY")
BLOCK_BIT = {name: 1 << i for i, name in enumerate(BLOCKS)}
FIELDS = (
    ("register", "OPPORTUNITY", str),
    ("record_ordinal", "OPPORTUNITY", int),
    ("field_ordinal", "OPPORTUNITY", int),
    ("within_field_position", "OPPORTUNITY", str),
    ("wrapper", "EDGE_COMPILER", str),
    ("q_flag", "EDGE_COMPILER", int),
    ("local_frame", "EDGE_COMPILER", str),
    ("inner_d", "EDGE_COMPILER", str),
    ("right_family", "EDGE_COMPILER", str),
    ("dy_closure", "CLOSURE_BOUNDARY", str),
    ("b3", "CLOSURE_BOUNDARY", str),
    ("line_close", "CLOSURE_BOUNDARY", int),
    ("paragraph_close", "CLOSURE_BOUNDARY", int),
    ("known_label_renderer", "EDGE_COMPILER", str),
)
MODEL = "ABBREVIATION_HEAVY_LANGUAGE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def result_csha(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
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


def h12(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def subset_name(mask: int) -> str:
    if mask == 0:
        return "EMPTY"
    return "+".join(name for name in BLOCKS if mask & BLOCK_BIT[name])


def canonical_value(row: dict, name: str, converter):
    value = row[name]
    return converter(value)


def subset_key(row: dict, mask: int) -> tuple:
    if mask == 0:
        return ()
    return tuple(
        canonical_value(row, name, converter)
        for name, block, converter in FIELDS
        if mask & BLOCK_BIT[block]
    )


def bucket_maps(events: list[dict]) -> dict[int, list[int]]:
    out = {
        mask: [g276.bucket("COMPILER", subset_key(row, mask)) for row in events]
        for mask in range(8)
    }
    for row, value in zip(events, out[7]):
        assert int(row["compiler_bucket"]) == value, (row["observation_id"], value, row["compiler_bucket"])
    return out


def permutation_indices(events: list[dict], world: int) -> list[int]:
    strata: dict[tuple, list[int]] = defaultdict(list)
    for i, row in enumerate(events):
        strata[(
            row["register"],
            int(row["record_ordinal"]),
            row["within_field_position"],
            int(row["host_length"]),
        )].append(i)
    rng = random.Random(
        int(hashlib.sha256(f"GDT276_MATCHED_CONTEXT_V1|{world}|{MODEL}".encode()).hexdigest()[:16], 16)
    )
    source = list(range(len(events)))
    for ids in strata.values():
        values = list(ids)
        rng.shuffle(values)
        for dest, src in zip(ids, values):
            source[dest] = src
    return source


def score_buckets(events: list[dict], buckets: list[int]) -> tuple[float, dict[str, float]]:
    """Exact GDT276 LOFO character score, avoiding repeated train scans."""
    design = json.loads((R / "gdt276_design.json").read_text())
    alphabet = design["alphabet"]
    K = len(alphabet)
    prior = design["capacity"]["character_context_prior_mass"]
    folds: dict[str, list[int]] = defaultdict(list)
    global_all: dict[str, Counter] = defaultdict(Counter)
    global_fold: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    context_all: dict[tuple[int, str], Counter] = defaultdict(Counter)
    context_fold: dict[str, dict[tuple[int, str], Counter]] = defaultdict(lambda: defaultdict(Counter))
    triples: list[list[tuple[str, str, str]]] = []
    for i, row in enumerate(events):
        fold = row["physical_folio"]
        folds[fold].append(i)
        z = g276.chars(row["page_host"])
        triples.append(z)
        b = buckets[i]
        for hist, char, _component in z:
            global_all[hist][char] += 1
            global_fold[fold][hist][char] += 1
            context_all[(b, hist)][char] += 1
            context_fold[fold][(b, hist)][char] += 1
    fold_bits: dict[str, float] = {}
    for held, ids in sorted(folds.items()):
        page_counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
        bits = 0.0
        for i in ids:
            row = events[i]
            b = buckets[i]
            for hist, char, _component in triples[i]:
                ga = global_all[hist]
                gf = global_fold[held][hist]
                gn = sum(ga.values()) - sum(gf.values())
                gc = ga[char] - gf[char]
                pb = (gc + 0.5) / (gn + 0.5 * K)
                pc = page_counts[row["page"]][hist]
                pp = (pc[char] + prior * pb) / (sum(pc.values()) + prior)
                ca = context_all[(b, hist)]
                cf = context_fold[held][(b, hist)]
                cn = sum(ca.values()) - sum(cf.values())
                cc = ca[char] - cf[char]
                probability = (cc + prior * pp) / (cn + prior)
                bits -= math.log2(probability)
                pc[char] += 1
        fold_bits[held] = bits
    return sum(fold_bits.values()), fold_bits


def summarize(events: list[dict], observed: float, null: list[float] | None) -> dict:
    row = {
        "events": len(events),
        "scoring_folds": len({x["physical_folio"] for x in events}),
        "observed_bits": f"{observed:.12f}",
    }
    if null is None:
        row.update({
            "null_worlds": 0,
            "null_mean_bits": "NA",
            "null_sd_bits": "NA",
            "saving_bits": "NA",
            "saving_bits_per_event": "NA",
            "null_z": "NA",
        })
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


def shapley(values: dict[int, float]) -> dict[str, float]:
    assert set(values) == set(range(8))
    answer = {}
    factorial = math.factorial
    for i, block in enumerate(BLOCKS):
        bit = 1 << i
        total = 0.0
        for mask in range(8):
            if mask & bit:
                continue
            size = mask.bit_count()
            weight = factorial(size) * factorial(3 - size - 1) / factorial(3)
            total += weight * (values[mask | bit] - values[mask])
        answer[block] = total
    assert math.isclose(sum(answer.values()), values[7] - values[0], rel_tol=0, abs_tol=2e-10)
    return answer


def published_job(item: tuple[str, str, list[dict]]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    control, view, events = item
    maps = bucket_maps(events)
    observed: dict[int, float] = {}
    folio: dict[int, dict[str, float]] = {}
    for mask in range(8):
        observed[mask], folio[mask] = score_buckets(events, maps[mask])
    null_values = {mask: [] for mask in range(8)}
    null_rows = []
    for world in range(64):
        source = permutation_indices(events, world)
        for mask in range(8):
            values = [maps[mask][j] for j in source]
            bits, _ = score_buckets(events, values)
            null_values[mask].append(bits)
            null_rows.append({
                "control_id": control,
                "view": view,
                "representation": "PUBLISHED_FROZEN_GDT278",
                "subset_mask": mask,
                "subset": subset_name(mask),
                "world_index": world,
                "held_bits": f"{bits:.12f}",
            })
    score_rows = []
    t_values = {}
    for mask in range(8):
        q = {
            "control_id": control,
            "view": view,
            "representation": "PUBLISHED_FROZEN_GDT278",
            "subset_mask": mask,
            "subset": subset_name(mask),
        }
        q.update(summarize(events, observed[mask], null_values[mask]))
        score_rows.append(q)
        t_values[mask] = float(q["saving_bits_per_event"])
    phi = shapley(t_values)
    shape_rows = [{
        "control_id": control,
        "view": view,
        "representation": "PUBLISHED_FROZEN_GDT278",
        "allocation_target": "NULL_ADJUSTED_SAVING_BITS_PER_EVENT",
        "block": block,
        "shapley_bits_per_event": f"{value:.12f}",
        "full_value_bits_per_event": f"{t_values[7]:.12f}",
    } for block, value in phi.items()]
    fold_rows = [{
        "control_id": control,
        "view": view,
        "representation": "PUBLISHED_FROZEN_GDT278",
        "subset": "FULL",
        "held_folio": held,
        "events": sum(x["physical_folio"] == held for x in events),
        "held_bits": f"{bits:.12f}",
    } for held, bits in sorted(folio[7].items())]
    return score_rows, shape_rows, null_rows, fold_rows


def safe_observed_job(item: tuple[str, str, list[dict], list[str], bool]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    control, view, events, target, compute_null = item
    folded = sorted({x["physical_folio"] for x in events})
    observed = {mask: 0.0 for mask in range(8)}
    null = [0.0] * 64 if compute_null else None
    full_fold_rows = []
    changed = 0
    for held in folded:
        safe = g278.safe_reparse(events, control, held, target)
        changed += sum(
            a["page_host"] != b["page_host"] or int(a["compiler_bucket"]) != int(b["compiler_bucket"])
            for a, b in zip(safe, events)
        )
        train = [x for x in safe if x["physical_folio"] != held]
        test = [x for x in safe if x["physical_folio"] == held]
        maps = bucket_maps(safe)
        fold_full = 0.0
        for mask in range(8):
            bm = {x["observation_id"]: value for x, value in zip(safe, maps[mask])}
            bits = g278.fold_char(train, test, bm)
            observed[mask] += bits
            if mask == 7:
                fold_full = bits
        full_fold_rows.append({
            "control_id": control,
            "view": view,
            "representation": "LOFO_SAFE",
            "subset": "FULL",
            "held_folio": held,
            "events": len(test),
            "held_bits": f"{fold_full:.12f}",
        })
        if compute_null:
            for world in range(64):
                bm = g276.random_buckets(safe, world)[MODEL]
                null[world] += g278.fold_char(train, test, bm)
    score_rows = []
    improvement = {mask: (observed[0] - observed[mask]) / len(events) for mask in range(8)}
    for mask in range(8):
        q = {
            "control_id": control,
            "view": view,
            "representation": "LOFO_SAFE",
            "subset_mask": mask,
            "subset": subset_name(mask),
            "representation_changes_across_folds": changed,
            "observed_empty_minus_model_bits_per_event": f"{improvement[mask]:.12f}",
        }
        q.update(summarize(events, observed[mask], null if mask == 7 and compute_null else None))
        score_rows.append(q)
    phi = shapley(improvement)
    shape_rows = [{
        "control_id": control,
        "view": view,
        "representation": "LOFO_SAFE",
        "allocation_target": "OBSERVED_EMPTY_MINUS_SUBSET_BITS_PER_EVENT",
        "block": block,
        "shapley_bits_per_event": f"{value:.12f}",
        "full_value_bits_per_event": f"{improvement[7]:.12f}",
    } for block, value in phi.items()]
    null_rows = [] if null is None else [{
        "control_id": control,
        "view": view,
        "representation": "LOFO_SAFE",
        "subset_mask": 7,
        "subset": "OPPORTUNITY+EDGE_COMPILER+CLOSURE_BOUNDARY",
        "world_index": world,
        "held_bits": f"{bits:.12f}",
    } for world, bits in enumerate(null)]
    return score_rows, shape_rows, null_rows, full_fold_rows


def public_fingerprint(rows: list[dict]) -> str:
    fields = [
        "page", "physical_folio", "locus", "group_index", "group_count",
        "register", "record_ordinal", "field_ordinal", "within_field_position", "wrapper",
        "q_flag", "local_frame", "inner_d", "right_family", "dy_closure", "b3",
        "line_close", "paragraph_close", "known_label_renderer", "page_host",
        "source_observation_id",
    ]
    return csha([[str(row.get(key, "")) for key in fields] for row in rows])


def build_intermediate(control: str, matched: list[dict], pool: list[dict] | None, full_vms: list[dict] | None = None) -> list[dict]:
    if control == "VOYNICH_REFERENCE":
        assert full_vms is not None
        source = {x["observation_id"]: x for x in full_vms}
        out = []
        for m in matched:
            s = source[m["source_observation_id"]]
            x = dict(s)
            x.update({k: m[k] for k in (
                "page_host", "wrapper", "q_flag", "local_frame", "inner_d", "right_family",
                "dy_closure", "b3", "known_label_renderer", "_surface",
                "_primary_unmapped_host", "_parser_style",
            )})
            x.update({
                "observation_id": "GDT279I:" + s["observation_id"],
                "control_id": control,
                "ground_truth_architecture": "UNKNOWN_VOYNICH_ARCHITECTURE",
                "source_observation_id": s["observation_id"],
                "source_folio_hash": m["source_folio_hash"],
                "source_line_hash": m["source_line_hash"],
                "source_surface_sha256": m["source_surface_sha256"],
            })
            out.append(x)
        out = g277.rebuild_context(out)
        return out

    assert pool is not None
    by_id = {x["source_observation_id"]: x for x in pool}
    assert len(by_id) == len(pool)
    selected = [(m, by_id[m["source_observation_id"]]) for m in matched]
    selected.sort(key=lambda pair: int(pair[1]["source_order"]))
    record_maps: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    out = []
    for m, s in selected:
        page_key = (s["source_folio"], s["source_page"])
        rmap = record_maps[page_key]
        if s["source_record"] not in rmap:
            rmap[s["source_record"]] = len(rmap) + 1
        gi = int(s["source_group_index"])
        gc = int(s["source_group_count"])
        position = "ONLY" if gc == 1 else "FIRST" if gi == 1 else "LAST" if gi == gc else "MIDDLE"
        x = {
            "observation_id": f"GDT279I:{control}:{s['source_observation_id']}",
            "control_id": control,
            "ground_truth_architecture": m["ground_truth_architecture"],
            "page": f"P:{control}:{h12(s['source_page'])}",
            "physical_folio": f"F:{control}:{s['source_folio']}",
            "locus": f"L:{control}:{h12(s['source_line'])}",
            "group_index": gi,
            "group_count": gc,
            "register": s["source_register"],
            "section": m["ground_truth_architecture"],
            "currier": "CONTROL",
            "hand": "CONTROL",
            "record_ordinal": rmap[s["source_record"]],
            "field_ordinal": 1,
            "within_field_position": position,
            "wrapper": m["wrapper"],
            "q_flag": int(m["q_flag"]),
            "local_frame": m["local_frame"],
            "inner_d": m["inner_d"],
            "right_family": m["right_family"],
            "dy_closure": m["dy_closure"],
            "b3": m["b3"],
            "line_close": int(gi == gc),
            "paragraph_close": int(gi == gc and int(s["source_paragraph_end"])),
            "known_label_renderer": m["known_label_renderer"],
            "page_host": m["page_host"],
            "raw_token": s["surface"],
            "previous_page_host": "",
            "host_length": len(m["page_host"]),
            "source_observation_id": s["source_observation_id"],
            "source_folio_hash": h12(s["source_folio"]),
            "source_line_hash": h12(s["source_line"]),
            "source_surface_sha256": hashlib.sha256(s["surface"].encode()).hexdigest(),
            "_surface": s["surface"],
            "_primary_unmapped_host": s["host"],
            "_parser_style": m["_parser_style"],
        }
        out.append(x)
    return g277.rebuild_context(out)


def public_event(row: dict) -> dict:
    return {
        key: value for key, value in row.items()
        if not key.startswith("_") and key not in ("raw_token", "compiler_key")
    }


def build_panels() -> tuple[dict[tuple[str, str], list[dict]], list[dict], list[str]]:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_GDT279_BLOCK_SCORING"
    for row in read(R / "gdt279_gdt278_freeze_manifest.tsv"):
        assert sha(R / row["artifact"]) == row["frozen_sha256"]
    parent = json.loads((R / "gdt278_result.json").read_text())
    assert parent["status"] == "VOYNICH_MAGNITUDE_ORDER_OR_MATCHING_SENSITIVE"
    full = g278.read(g278.VMS)
    assert len(full) == 8448
    assert not any(x["page"].startswith("f84") or x["locus"].startswith("f84") for x in full)
    target = sorted(set("".join(x["page_host"] for x in full)))
    assert len(target) == 20
    scaffold, _ = g277.scaffold(json.loads((R / "gdt277_design.json").read_text()))
    manifest = read(R / "gdt278_control_manifest.tsv")
    ground = {x["control_id"]: x["ground_truth_basis"] for x in manifest}
    pools = g278.load_pools()
    assert set(pools) == set(ground)
    panels: dict[tuple[str, str], list[dict]] = {}
    matched_vms, native_vms = g278.vms_panels(scaffold, full)
    panels[("VOYNICH_REFERENCE", "LENGTH_MATCHED_OVERLAY")] = matched_vms
    panels[("VOYNICH_REFERENCE", "MATCHED_SAMPLE_NATIVE_LAYOUT")] = build_intermediate(
        "VOYNICH_REFERENCE", matched_vms, None, full
    )
    panels[("VOYNICH_REFERENCE", "NATIVE_ORDER")] = native_vms
    for control in [x["control_id"] for x in manifest]:
        matched, cap = g278.make_matched(control, ground[control], pools[control], scaffold, target)
        if matched is not None:
            panels[(control, "LENGTH_MATCHED_OVERLAY")] = matched
            panels[(control, "MATCHED_SAMPLE_NATIVE_LAYOUT")] = build_intermediate(
                control, matched, pools[control]
            )
        native, _ = g278.make_native(control, ground[control], pools[control], target)
        panels[(control, "NATIVE_ORDER")] = native

    # Reconstruct the two parent inventories before allowing the new view.
    parent_match = read(R / "gdt278_matched_event_inventory.tsv")
    parent_native = read(R / "gdt278_native_event_inventory.tsv")
    by_parent_match: dict[str, list[dict]] = defaultdict(list)
    by_parent_native: dict[str, list[dict]] = defaultdict(list)
    for row in parent_match:
        key = "VOYNICH_REFERENCE" if row["control_id"] == "VOYNICH_MATCHED_REFERENCE" else row["control_id"]
        row = dict(row)
        row["control_id"] = key
        by_parent_match[key].append(row)
    for row in parent_native:
        by_parent_native[row["control_id"]].append(row)
    for (control, view), rows in panels.items():
        if view == "LENGTH_MATCHED_OVERLAY":
            assert public_fingerprint(rows) == public_fingerprint(by_parent_match[control]), (control, view)
        if view == "NATIVE_ORDER":
            assert public_fingerprint(rows) == public_fingerprint(by_parent_native[control]), (control, view)
    intermediate = [public_event(row) for (control, view), rows in panels.items() if view == "MATCHED_SAMPLE_NATIVE_LAYOUT" for row in rows]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in intermediate)
    return panels, intermediate, target


def inherited_safe_full() -> tuple[dict[tuple[str, str], dict], dict[tuple[str, str], list[float]]]:
    scores = {}
    for row in read(R / "gdt278_magnitude_scores.tsv"):
        if row["representation"] == "LOFO_SAFE":
            scores[(row["control_id"], row["view"])] = row
    nulls: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in read(R / "gdt278_null_results.tsv"):
        if row["representation"] == "LOFO_SAFE":
            nulls[(row["control_id"], row["view"])].append(float(row["held_bits"]))
    assert set(scores) == set(nulls)
    assert all(len(values) == 64 for values in nulls.values())
    return scores, nulls


def main() -> None:
    panels, intermediate, target = build_panels()
    write(OUT_INTERMEDIATE, intermediate)
    print(json.dumps({
        "panels": len(panels),
        "intermediate_panels": sum(view == "MATCHED_SAMPLE_NATIVE_LAYOUT" for _, view in panels),
        "intermediate_events": len(intermediate),
    }, sort_keys=True), flush=True)

    score_rows: list[dict] = []
    shapley_rows: list[dict] = []
    null_rows: list[dict] = []
    fold_rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=min(16, len(panels))) as executor:
        jobs = {
            executor.submit(published_job, (control, view, rows)): (control, view)
            for (control, view), rows in panels.items()
        }
        for future in as_completed(jobs):
            a, b, c, d = future.result()
            score_rows.extend(a)
            shapley_rows.extend(b)
            null_rows.extend(c)
            fold_rows.extend(d)
            print(json.dumps({"published_scored": jobs[future]}, sort_keys=True), flush=True)

    # The FULL model and all null worlds must be exact GDT278 anchors.
    old_scores = {
        (x["control_id"], x["view"]): x
        for x in read(R / "gdt278_magnitude_scores.tsv")
        if x["representation"] == "PUBLISHED_FULL_INVENTORY"
    }
    old_null: dict[tuple[str, str], list[float]] = defaultdict(list)
    for x in read(R / "gdt278_null_results.tsv"):
        if x["representation"] == "PUBLISHED_FULL_INVENTORY":
            old_null[(x["control_id"], x["view"])].append(float(x["held_bits"]))
    for key, old in old_scores.items():
        row = next(x for x in score_rows if (x["control_id"], x["view"]) == key and int(x["subset_mask"]) == 7)
        assert math.isclose(float(row["observed_bits"]), float(old["observed_bits"]), rel_tol=0, abs_tol=2e-8), key
        assert math.isclose(float(row["saving_bits"]), float(old["saving_bits"]), rel_tol=0, abs_tol=2e-8), key
        current = [float(x["held_bits"]) for x in null_rows if (x["control_id"], x["view"]) == key and int(x["subset_mask"]) == 7]
        assert len(current) == 64 and all(math.isclose(a, b, rel_tol=0, abs_tol=2e-8) for a, b in zip(current, old_null[key])), key

    # Mandatory safe observed-subset sensitivity. Existing views inherit only
    # the exact full null; the new intermediate view computes it afresh.
    inherited_scores, inherited_nulls = inherited_safe_full()
    safe_jobs = []
    with ProcessPoolExecutor(max_workers=min(16, len(panels))) as executor:
        futures = {}
        for (control, view), rows in panels.items():
            future = executor.submit(
                safe_observed_job,
                (control, view, rows, target, view == "MATCHED_SAMPLE_NATIVE_LAYOUT"),
            )
            futures[future] = (control, view)
        for future in as_completed(futures):
            control, view = futures[future]
            a, b, c, d = future.result()
            if view != "MATCHED_SAMPLE_NATIVE_LAYOUT":
                old = inherited_scores[(control, view)]
                full = next(x for x in a if int(x["subset_mask"]) == 7)
                assert math.isclose(float(full["observed_bits"]), float(old["observed_bits"]), rel_tol=0, abs_tol=3e-8), (control, view)
                values = inherited_nulls[(control, view)]
                summary = summarize(panels[(control, view)], float(full["observed_bits"]), values)
                full.update(summary)
                c = [{
                    "control_id": control,
                    "view": view,
                    "representation": "LOFO_SAFE",
                    "subset_mask": 7,
                    "subset": subset_name(7),
                    "world_index": world,
                    "held_bits": f"{bits:.12f}",
                } for world, bits in enumerate(values)]
            score_rows.extend(a)
            shapley_rows.extend(b)
            null_rows.extend(c)
            fold_rows.extend(d)
            print(json.dumps({"safe_scored": (control, view)}, sort_keys=True), flush=True)

    score_rows.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], int(x["subset_mask"])))
    shapley_rows.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], BLOCKS.index(x["block"])))
    null_rows.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], int(x["subset_mask"]), int(x["world_index"])))
    fold_rows.sort(key=lambda x: (x["control_id"], x["view"], x["representation"], x["held_folio"]))

    contrasts = []
    controls = sorted({control for control, _view in panels})
    for representation in ("PUBLISHED_FROZEN_GDT278", "LOFO_SAFE"):
        for control in controls:
            available = {view for cid, view in panels if cid == control}
            if "MATCHED_SAMPLE_NATIVE_LAYOUT" not in available:
                continue
            row = {"control_id": control, "representation": representation}
            block_values: dict[str, dict[str, float]] = {}
            for view in ("LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT", "NATIVE_ORDER"):
                full = next(x for x in score_rows if x["control_id"] == control and x["view"] == view and x["representation"] == representation and int(x["subset_mask"]) == 7)
                assert full["saving_bits_per_event"] != "NA"
                row[view.lower() + "_saving_bits_per_event"] = full["saving_bits_per_event"]
                block_values[view] = {
                    x["block"]: float(x["shapley_bits_per_event"])
                    for x in shapley_rows
                    if x["control_id"] == control and x["view"] == view and x["representation"] == representation
                }
            matched = float(row["length_matched_overlay_saving_bits_per_event"])
            middle = float(row["matched_sample_native_layout_saving_bits_per_event"])
            native = float(row["native_order_saving_bits_per_event"])
            row["layout_delta_bits_per_event"] = f"{middle - matched:.12f}"
            row["selection_delta_bits_per_event"] = f"{native - middle:.12f}"
            layout_blocks = {
                block: block_values["MATCHED_SAMPLE_NATIVE_LAYOUT"][block] - block_values["LENGTH_MATCHED_OVERLAY"][block]
                for block in BLOCKS
            }
            for block in BLOCKS:
                row["layout_delta_" + block.lower()] = f"{layout_blocks[block]:.12f}"
            row["layout_leading_block"] = max(BLOCKS, key=lambda block: (layout_blocks[block], -BLOCKS.index(block)))
            row["block_allocation_target"] = (
                "NULL_ADJUSTED_SAVING_BITS_PER_EVENT" if representation == "PUBLISHED_FROZEN_GDT278"
                else "OBSERVED_EMPTY_MINUS_SUBSET_BITS_PER_EVENT"
            )
            contrasts.append(row)

    positive = set(json.loads((R / "gdt278_result.json").read_text())["native_safe_reproductions"])
    eligible_positive = [x for x in contrasts if x["control_id"] in positive and x["representation"] == "PUBLISHED_FROZEN_GDT278"]
    assert {x["control_id"] for x in eligible_positive} == {"LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC"}
    leaders = {x["layout_leading_block"] for x in eligible_positive if float(x["layout_delta_bits_per_event"]) > 0}
    if len(leaders) == 1 and len(leaders) == len({x["layout_leading_block"] for x in eligible_positive}) and all(float(x["layout_delta_bits_per_event"]) > 0 for x in eligible_positive):
        lead = next(iter(leaders))
        status = {
            "EDGE_COMPILER": "NATIVE_EXCESS_SHARED_EDGE_COMPILER_LEAD",
            "CLOSURE_BOUNDARY": "NATIVE_EXCESS_SHARED_CLOSURE_BOUNDARY_LEAD",
            "OPPORTUNITY": "NATIVE_EXCESS_SHARED_OPPORTUNITY_INTERACTION_LEAD",
        }[lead]
    else:
        status = "NATIVE_EXCESS_MECHANISM_HETEROGENEOUS"

    counterexamples = [
        {"counterexample": "FULL_MODEL_IDENTIFIES_ARCHITECTURE", "evidence": "GDT278 native Latin exceeds Voynich but matched overlay does not", "impact": "GDT279 allocates an order-sensitive compressor score only"},
        {"counterexample": "MATCHED_AND_NATIVE_USE_THE_SAME_EVENTS", "evidence": "GDT278 used different deterministic source selections", "impact": "the new intermediate view isolates exact matched selection from layout; selection delta remains separate"},
        {"counterexample": "OPPORTUNITY_IS_AN_UNCONDITIONED_SIGNAL", "evidence": "the inherited null conditions register record ordinal position and host length", "impact": "pure opportunity is mostly conditioned out; only remaining fields and interactions are measurable"},
        {"counterexample": "SHAPLEY_IS_A_CAUSAL_SEMANTIC_EFFECT", "evidence": "values allocate fixed hashed compression gains and may contain interactions/collisions", "impact": "no block receives a meaning"},
        {"counterexample": "PUBLISHED_PARSE_IS_LEAKAGE_FREE", "evidence": "the parent full inventory was learned globally", "impact": "mandatory LOFO-safe observed-block and full-null sensitivity is reported"},
        {"counterexample": "SOURCE_SELECTED_NATIVE_LAYOUT_IS_A_COMPLETE_MANUSCRIPT", "evidence": "it contains exact length-selected source occurrences and may skip intervening groups", "impact": "it identifies layout sensitivity of the selected sample, not native corpus entropy"},
        {"counterexample": "GDT159_NATIVE_IS_THE_COMPLETE_SOURCE", "evidence": "native order is restored only within the already-frozen GDT159 sampled source-unit corpus", "impact": "do not generalize to whole Latin manuscript traditions"},
        {"counterexample": "F84_USED", "evidence": "only the frozen f84-free GDT276 inventory supplies Voynich rows", "impact": "no f84 access"},
    ]

    write(OUT_SCORES, score_rows)
    write(OUT_SHAPLEY, shapley_rows)
    write(OUT_CONTRASTS, contrasts)
    write(OUT_FOLDS, fold_rows)
    write(OUT_NULL, null_rows)
    write(OUT_COUNTER, counterexamples)

    report = [
        "# GDT279 — native-order compiler decomposition",
        "",
        f"Status: **{status}**.",
        "",
        "GDT278 and its endpoint remain frozen. No new corpus, host substring, semantic field, or score threshold was added.",
        "",
        "## Exact matched-sample bridge",
        "",
        "| control | matched | same sample/native layout | native sample | layout delta | selection delta | leading layout block |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in contrasts:
        if row["representation"] != "PUBLISHED_FROZEN_GDT278":
            continue
        report.append(
            f"| {row['control_id']} | {float(row['length_matched_overlay_saving_bits_per_event']):+.4f} | "
            f"{float(row['matched_sample_native_layout_saving_bits_per_event']):+.4f} | "
            f"{float(row['native_order_saving_bits_per_event']):+.4f} | "
            f"{float(row['layout_delta_bits_per_event']):+.4f} | {float(row['selection_delta_bits_per_event']):+.4f} | "
            f"{row['layout_leading_block']} |"
        )
    report += [
        "",
        "`matched` and `same sample/native layout` use exactly the same source occurrences, mapped host strings, and host-length distribution. The second column restores only source order and layout. `native sample` uses the parent GDT278 native selection.",
        "",
        "## Block allocation on the two eligible native-positive Latin panels",
        "",
        "| control | layout delta | opportunity | edge compiler | closure/boundary |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in eligible_positive:
        report.append(
            f"| {row['control_id']} | {float(row['layout_delta_bits_per_event']):+.4f} | "
            f"{float(row['layout_delta_opportunity']):+.4f} | {float(row['layout_delta_edge_compiler']):+.4f} | "
            f"{float(row['layout_delta_closure_boundary']):+.4f} |"
        )
    report += [
        "",
        "For the **native full model itself**, however, the published Shapley allocation is edge-compiler dominated on all three Latin native reproductions:",
        "",
        "| native control | opportunity | edge compiler | closure/boundary | full saving |",
        "|---|---:|---:|---:|---:|",
    ]
    for control in ("LATIN_SCHOLASTIC_GRAPHEMATIC", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC"):
        values = {
            x["block"]: float(x["shapley_bits_per_event"])
            for x in shapley_rows
            if x["control_id"] == control and x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_FROZEN_GDT278"
        }
        full = sum(values.values())
        report.append(f"| {control} | {values['OPPORTUNITY']:+.4f} | {values['EDGE_COMPILER']:+.4f} | {values['CLOSURE_BOUNDARY']:+.4f} | {full:+.4f} |")
    report += [
        "",
        "The first table is an exact Shapley allocation of the *change* in the fixed null-adjusted compressor score. `OPPORTUNITY` leads that layout-restoration change by removing a negative opportunity×edge mismatch on the overlay; it is not the largest native predictor. The second table shows that source-edge compiler structure carries most native saving, while closure is secondary. Neither table is a semantic decomposition. The Latin scholastic panel lacked GDT278 exact-length capacity, so it has no layout bridge.",
        "",
        "## LOFO-safe full-model sensitivity",
        "",
        "| control | matched | same sample/native layout | native sample | safe layout delta |",
        "|---|---:|---:|---:|---:|",
    ]
    safe_contrasts = {x["control_id"]: x for x in contrasts if x["representation"] == "LOFO_SAFE"}
    for control in ("VOYNICH_REFERENCE", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC"):
        row = safe_contrasts[control]
        report.append(
            f"| {control} | {float(row['length_matched_overlay_saving_bits_per_event']):+.4f} | "
            f"{float(row['matched_sample_native_layout_saving_bits_per_event']):+.4f} | "
            f"{float(row['native_order_saving_bits_per_event']):+.4f} | {float(row['layout_delta_bits_per_event']):+.4f} |"
        )
    report += [
        "",
        "The representation-safe bridge preserves the two Latin layout gains. Alternate readings are not samples; no Voynich transcription replication is claimed.",
        "",
        "## Interpretation",
        "",
        "Native diplomatic excess can arise from authentic document order and boundary-conditioned graphematic regularity. This pass states exactly which frozen compiler block carries that difference and whether the same mechanism recurs across the two comparable positive Latin panels. It does not turn the magnitude into evidence for a particular language or abbreviation system.",
        "",
        "Every inherited FULL score and every inherited FULL null world reproduced GDT278 before the new rows were accepted. LOFO-safe full magnitudes and observed block allocations are exported separately. No f84 source was opened, parsed, retained, joined, or scored.",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf8")

    outputs = [
        OUT_INTERMEDIATE, OUT_SCORES, OUT_SHAPLEY, OUT_CONTRASTS, OUT_FOLDS,
        OUT_NULL, OUT_COUNTER, REPORT,
    ]
    inputs = [
        "gdt279_design.json", "gdt279_design_validation.json",
        "gdt279_gdt278_freeze_manifest.tsv", "gdt278_result.json",
        "gdt278_magnitude_scores.tsv", "gdt278_null_results.tsv",
        "gdt278_folio_scores.tsv", "gdt278_matched_event_inventory.tsv",
        "gdt278_native_event_inventory.tsv", "gdt278_control_manifest.tsv",
        "gdt276_event_inventory.tsv",
    ]
    parent = json.loads((R / "gdt278_result.json").read_text())
    result = {
        "schema": "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_RESULT_V1",
        "status": status,
        "panels": len(panels),
        "intermediate_panels": sum(view == "MATCHED_SAMPLE_NATIVE_LAYOUT" for _control, view in panels),
        "intermediate_events": len(intermediate),
        "blocks": list(BLOCKS),
        "subset_count": 8,
        "null_worlds": 64,
        "native_parent_reproductions": sorted(positive),
        "layout_bridge_native_reproductions": [x["control_id"] for x in eligible_positive],
        "headline_layout_leaders": {x["control_id"]: x["layout_leading_block"] for x in eligible_positive},
        "threshold_tuned": False,
        "composite_score": False,
        "new_control_corpora": 0,
        "semantic_assignments": 0,
        "hpr1_semantics_used": 0,
        "voynich_substrings_mined": 0,
        "claim_ceiling": "Exposed compiler-context compression decomposition only; no language abbreviation code notation meaning plaintext or translation.",
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "gdt278_immutable": all(sha(R / x["artifact"]) == x["frozen_sha256"] for x in read(R / "gdt279_gdt278_freeze_manifest.tsv")),
        "parent_source_bindings": parent["inputs"],
        "parent_external_source": parent["external_source"],
        "inputs": {name: sha(R / name) for name in inputs},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = result_csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "headline_layout_leaders": result["headline_layout_leaders"]}, sort_keys=True))


if __name__ == "__main__":
    main()
