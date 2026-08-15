#!/usr/bin/env python3
"""GDT134: test Q20 raw/host/compiler arity transfer on general continuations."""
from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

import run_gdt131_q20_cross_line_field_onset as q
import run_gdt132_cross_register_continuation_arity as g
import run_gdt133_raw_surface_transfer_decomposition as d

ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "gdt134_prediction.json"
CORRECTION = ROOT / "gdt134_scope_correction.json"
METHOD = ROOT / "GDT134_GENERAL_ADJACENT_CONTINUATION_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT134_GENERAL_ADJACENT_CONTINUATION_TRANSFER_REPORT.md"
INVENTORY = ROOT / "gdt134_general_continuation_inventory.tsv"
SCORES = ROOT / "gdt134_general_continuation_scores.tsv"
FOLDS = ROOT / "gdt134_general_continuation_folds.tsv"
NULL = ROOT / "gdt134_general_continuation_null.tsv"
CHAIN = ROOT / "gdt134_general_continuation_chain_sensitivity.tsv"
COUNTER = ROOT / "gdt134_general_continuation_counterexamples.tsv"
RESULT = ROOT / "gdt134_result.json"
MODES = ("RAW_CHAR3", "HOST_CHAR3", "COMPILER12")
WORLDS = 4096


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def seed(*value):
    return int(hashlib.sha256("|".join(map(str, value)).encode()).hexdigest()[:16], 16)


def write(path, rows):
    keys = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with Path(path).open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=keys, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def guarded_rows(path):
    """Reject f84 rows before retaining formal fields or passing them to HPR2."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\r\n").split("\t")
        locus_i = header.index("locus")
        page_i = header.index("page")
        for line in handle:
            cells = line.rstrip("\r\n").split("\t")
            if cells[locus_i].startswith("f84") or cells[page_i].startswith("f84"):
                continue
            yield dict(zip(header, cells))


def external():
    raw = list(guarded_rows(g.SOURCE))
    parsed, _ = g.hpr2_parser(raw)
    by = defaultdict(list)
    for row in raw:
        if row["section"] not in g.SECTIONS or row["physical_folio"] in g.Q20_FOLIOS:
            continue
        by[row["locus"]].append(row)
    complete = {}
    for locus, rows in by.items():
        rows.sort(key=lambda row: int(row["group_index"]))
        count = int(rows[0]["group_count"])
        if len(rows) == count and [int(row["group_index"]) for row in rows] == list(range(1, count + 1)):
            complete[locus] = rows
    frames = {row["locus"]: row for row in guarded_rows(g.FRAMES)}
    out = []
    for locus, rows in complete.items():
        if locus not in frames:
            continue
        position = g.numeric(locus)
        if not position:
            continue
        next_locus = f"{position[0]}.{position[1] + 1}"
        if next_locus not in complete or next_locus not in frames:
            continue
        if frames[next_locus]["paragraph_start"] != "0":
            continue
        source = g.parsed(rows, parsed)
        target = g.parsed(complete[next_locus], parsed)
        source_fields = g.fields(source)
        target_fields = g.fields(target)
        assert source_fields and target_fields
        out.append(
            {
                "locus": locus,
                "next_locus": next_locus,
                "page": rows[0]["page"],
                "physical_folio": rows[0]["physical_folio"],
                "section": rows[0]["section"],
                "currier": rows[0]["currier"],
                "hand": rows[0]["hand"],
                "first_start": int(frames[locus]["paragraph_start"]),
                "source_line_number": position[1],
                "groups": source,
                "last": source_fields[-1],
                "target": target_fields[0],
                "member_count": sum(len(row["family_surface"]) for row in rows),
            }
        )
    assert out
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in out)
    return sorted(out, key=lambda row: (row["physical_folio"], row["page"], row["source_line_number"]))


def strata_for(target, indices, exact):
    strata = defaultdict(list)
    for i in indices:
        row = target[i]
        key = [row["section"], row["currier"], row["hand"], len(row["groups"])]
        if exact:
            key.extend(
                [
                    len(row["last"]),
                    sum(len(cell["page_host"]) for cell in row["last"]),
                    sum(len(cell["token"]) for cell in row["last"]),
                ]
            )
        strata[tuple(key)].append(i)
    return strata


def capacity(strata, target_bins):
    swappable = sum(len(ids) for ids in strata.values() if len(ids) > 1)
    mobile = sum(len(ids) for ids in strata.values() if len(ids) > 1 and len({target_bins[i] for i in ids}) > 1)
    return swappable, mobile


def main():
    freeze = json.loads(FREEZE.read_text())
    correction = json.loads(CORRECTION.read_text())
    assert freeze["status"] == "FROZEN_BEFORE_GENERAL_ADJACENT_PAIR_ENUMERATION"
    assert correction["status"] == "POST_ENUMERATION_SCOPE_AND_NULL_CORRECTION_BEFORE_FINAL_RESCORING"

    train_x, train_y, train_repr = d.training()
    target = external()
    target_ref = np.vstack([g.ref(row["groups"], row["last"], row["member_count"]) for row in target])
    target_y = np.vstack([g.count_vec(len(row["target"])) for row in target])
    primitive = [d.primitive(row["last"]) for row in target]
    target_repr = {mode: np.vstack([row[mode] for row in primitive]) for mode in MODES}

    x, tx, _, _ = q.standardize(train_x, target_ref)
    y, ty, ymu, ysd = q.standardize(train_y, target_y)
    reference_coef = q.fit(x, y)
    reference_pred = q.predict(tx, reference_coef)
    models = {}
    predictions = {}
    for mode in MODES:
        representation, target_representation, mean, scale = q.standardize(train_repr[mode], target_repr[mode])
        models[mode] = (q.fit(np.c_[x, representation], y), mean, scale)
        predictions[mode] = q.predict(np.c_[tx, target_representation], models[mode][0])

    actual = np.argmax(target_y, axis=1)
    reference_rank = np.argsort(-(reference_pred * ysd + ymu), axis=1)
    primary = [i for i, row in enumerate(target) if row["first_start"] == 0]
    exposed = [i for i, row in enumerate(target) if row["first_start"] == 1]
    all_indices = list(range(len(target)))
    even = [i for i in primary if target[i]["source_line_number"] % 2 == 0]
    odd = [i for i in primary if target[i]["source_line_number"] % 2 == 1]
    scopes = {
        "ALL_DESCRIPTIVE": all_indices,
        "PRIMARY_CONTINUATION_TO_CONTINUATION": primary,
        "EXPOSED_START_TO_NEXT": exposed,
        "PRIMARY_NONOVERLAP_EVEN_SOURCE_LINE": even,
        "PRIMARY_NONOVERLAP_ODD_SOURCE_LINE": odd,
    }
    for section in sorted({row["section"] for row in target}):
        scopes[f"PRIMARY_SECTION_{section}"] = [i for i in primary if target[i]["section"] == section]

    scores = []
    folds = []
    chain = []
    for mode in MODES:
        rank = np.argsort(-(predictions[mode] * ysd + ymu), axis=1)
        for scope, indices in scopes.items():
            score = {
                "model": mode,
                "scope": scope,
                "pairs": len(indices),
                "gain_bits": q.bits(ty[indices], reference_pred[indices], predictions[mode][indices]),
                "reference_top1": sum(actual[i] in reference_rank[i, :1] for i in indices),
                "model_top1": sum(actual[i] in rank[i, :1] for i in indices),
                "reference_top3": sum(actual[i] in reference_rank[i, :3] for i in indices),
                "model_top3": sum(actual[i] in rank[i, :3] for i in indices),
            }
            scores.append(score)
            if scope.startswith("PRIMARY_NONOVERLAP"):
                chain.append(score)
        for folio in sorted({target[i]["physical_folio"] for i in primary}):
            indices = [i for i in primary if target[i]["physical_folio"] == folio]
            gain = q.bits(ty[indices], reference_pred[indices], predictions[mode][indices])
            folds.append(
                {
                    "model": mode,
                    "scope": "PRIMARY_CONTINUATION_TO_CONTINUATION",
                    "physical_folio": folio,
                    "pairs": len(indices),
                    "gain_bits": gain,
                    "positive": int(gain > 0),
                }
            )

    exact = strata_for(target, primary, True)
    coarse = strata_for(target, primary, False)
    exact_capacity, exact_mobile = capacity(exact, actual)
    coarse_capacity, coarse_mobile = capacity(coarse, actual)
    null = []
    primary_set = set(primary)
    score_map = {(row["model"], row["scope"]): row for row in scores}
    for null_id, strata in (("EXACT_OPPORTUNITY_PRIMARY", exact), ("COARSE_EXACT_SOURCE_COUNT_PRIMARY", coarse)):
        rng = random.Random(seed("GDT134_CORRECTED", null_id))
        worlds = {mode: [] for mode in MODES}
        maximum = []
        for _ in range(WORLDS):
            assignment = list(range(len(target)))
            for ids in strata.values():
                if len(ids) > 1:
                    shuffled = ids[:]
                    rng.shuffle(shuffled)
                    for i, j in zip(ids, shuffled):
                        assignment[i] = j
            assert all(assignment[i] in primary_set for i in primary)
            values = {}
            for mode in MODES:
                coefficient, mean, scale = models[mode]
                permuted = q.predict(np.c_[tx, (target_repr[mode][assignment] - mean) / scale], coefficient)
                values[mode] = q.bits(ty[primary], reference_pred[primary], permuted[primary])
                worlds[mode].append(values[mode])
            maximum.append(max(values.values()))
        for mode in MODES:
            observed = score_map[mode, "PRIMARY_CONTINUATION_TO_CONTINUATION"]["gain_bits"]
            cap = exact_capacity if null_id.startswith("EXACT") else coarse_capacity
            mobile = exact_mobile if null_id.startswith("EXACT") else coarse_mobile
            null.append(
                {
                    "null_id": null_id,
                    "scope": "PRIMARY_CONTINUATION_TO_CONTINUATION",
                    "model": mode,
                    "worlds": WORLDS,
                    "swappable_pairs": cap,
                    "target_mobile_pairs": mobile,
                    "true_gain_bits": observed,
                    "null_mean_bits": float(np.mean(worlds[mode])),
                    "local_p": (1 + sum(value >= observed - 1e-12 for value in worlds[mode])) / (WORLDS + 1),
                    "max_three_p": (1 + sum(value >= observed - 1e-12 for value in maximum)) / (WORLDS + 1),
                }
            )

    null_map = {(row["null_id"], row["model"]): row for row in null}
    raw_all = score_map["RAW_CHAR3", "ALL_DESCRIPTIVE"]
    raw_primary = score_map["RAW_CHAR3", "PRIMARY_CONTINUATION_TO_CONTINUATION"]
    primary_folios = len({target[i]["physical_folio"] for i in primary})
    raw_positive_folios = sum(row["positive"] for row in folds if row["model"] == "RAW_CHAR3")
    gates = {
        "raw_gain_positive_all": raw_all["gain_bits"] > 0,
        "raw_gain_positive_primary_subset": raw_primary["gain_bits"] > 0,
        "raw_beats_host_primary": raw_primary["gain_bits"] > score_map["HOST_CHAR3", "PRIMARY_CONTINUATION_TO_CONTINUATION"]["gain_bits"],
        "raw_beats_compiler_primary": raw_primary["gain_bits"] > score_map["COMPILER12", "PRIMARY_CONTINUATION_TO_CONTINUATION"]["gain_bits"],
        "majority_primary_folios_positive": raw_positive_folios > primary_folios / 2,
        "exact_capacity_at_least_50": exact_capacity >= 50,
        "exact_max_three_p_le_005": exact_capacity >= 50
        and null_map["EXACT_OPPORTUNITY_PRIMARY", "RAW_CHAR3"]["max_three_p"] <= 0.05,
    }
    status = (
        "GENERAL_RAW_CONTINUATION_TRANSFER_SUPPORTED"
        if all(gates.values())
        else "INSUFFICIENT_EXACT_NULL_CAPACITY"
        if exact_capacity < 50
        else "RAW_RESIDUAL_DOES_NOT_GENERALIZE_TO_ORDINARY_CONTINUATIONS"
    )
    directional_outcome = (
        "RAW_RESIDUAL_REVERSES_ON_NEW_ORDINARY_CONTINUATIONS"
        if raw_primary["gain_bits"] < 0 < score_map["RAW_CHAR3", "EXPOSED_START_TO_NEXT"]["gain_bits"]
        else "NO_START_CONTINUATION_SIGN_REVERSAL"
    )

    inventory = [
        {
            "locus": row["locus"],
            "next_locus": row["next_locus"],
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "section": row["section"],
            "currier": row["currier"],
            "hand": row["hand"],
            "first_paragraph_start": row["first_start"],
            "primary_continuation_pair": int(row["first_start"] == 0),
            "source_line_number": row["source_line_number"],
            "source_group_count": len(row["groups"]),
            "source_member_count": row["member_count"],
            "last_field_group_count": len(row["last"]),
            "last_field_host_length": sum(len(cell["page_host"]) for cell in row["last"]),
            "last_field_raw_length": sum(len(cell["token"]) for cell in row["last"]),
            "target_first_field_group_count": len(row["target"]),
            "selection": "POST_ENUMERATION_CORRECTED_ALL_F84_EXCLUDED",
        }
        for row in target
    ]
    counterexamples = [
        {"counterexample": "EXACT_NULL_CAPACITY_PRIMARY", "detail": str(exact_capacity)},
        {"counterexample": "EXACT_NULL_TARGET_MOBILE_PRIMARY", "detail": str(exact_mobile)},
        {"counterexample": "COARSE_NULL_CAPACITY_PRIMARY", "detail": str(coarse_capacity)},
        {"counterexample": "PRIMARY_RAW_GAIN", "detail": f"{raw_primary['gain_bits']:+.6f}"},
        {
            "counterexample": "EXPOSED_START_RAW_GAIN",
            "detail": f"{score_map['RAW_CHAR3', 'EXPOSED_START_TO_NEXT']['gain_bits']:+.6f}",
        },
        {
            "counterexample": "OVERLAPPING_CHAIN_DEPENDENCE",
            "detail": "Primary adjacent pairs overlap within runs; even/odd source-line nonoverlap sensitivities are descriptive.",
        },
        {
            "counterexample": "F84_SCOPE_CORRECTION",
            "detail": "Inputs contain f84v rows, but final guarded loaders reject all f84* rows before formal retention/HPR2 parsing; no f84r row exists in either input.",
        },
        {
            "counterexample": "EXPOSED_DUPLICATE",
            "detail": "The 31 start-to-next pairs exactly duplicate corrected GDT132 and are sensitivity-only.",
        },
    ]

    format_rows = lambda rows: [
        {key: (f"{value:.12f}" if isinstance(value, float) else value) for key, value in row.items()} for row in rows
    ]
    write(INVENTORY, inventory)
    write(SCORES, format_rows(scores))
    write(FOLDS, format_rows(folds))
    write(NULL, format_rows(null))
    write(CHAIN, format_rows(chain))
    write(COUNTER, counterexamples)

    lines = [
        "# GDT134 — general adjacent-continuation transfer",
        "",
        f"Status: **{status}**",
        "",
        f"Directional result: **{directional_outcome}**.",
        "",
        (
            f"After the post-enumeration scope correction, the panel has {len(target)} pairs on "
            f"{len({row['physical_folio'] for row in target})} folios. The genuinely new primary has "
            f"{len(primary)} continuation-to-continuation pairs on {primary_folios} folios; the "
            f"{len(exposed)} start-to-next pairs are the already exposed GDT132 panel."
        ),
        "",
        (
            f"Exact opportunity strata retain {exact_capacity} swappable primary records, only "
            f"{exact_mobile} of them in target-variable strata. Coarse exact-source-count strata "
            f"retain {coarse_capacity} records ({coarse_mobile} target-mobile). The exact gate "
            "therefore cannot pass; coarse p-values are diagnostics only."
        ),
        "",
        "| model | all descriptive gain | new continuation gain | exposed start gain | positive primary folios | exact max-3 p | coarse max-3 p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for mode in MODES:
        lines.append(
            f"| `{mode}` | {score_map[mode, 'ALL_DESCRIPTIVE']['gain_bits']:+.3f} | "
            f"{score_map[mode, 'PRIMARY_CONTINUATION_TO_CONTINUATION']['gain_bits']:+.3f} | "
            f"{score_map[mode, 'EXPOSED_START_TO_NEXT']['gain_bits']:+.3f} | "
            f"{sum(row['positive'] for row in folds if row['model'] == mode)}/{primary_folios} | "
            f"{null_map['EXACT_OPPORTUNITY_PRIMARY', mode]['max_three_p']:.4f} | "
            f"{null_map['COARSE_EXACT_SOURCE_COUNT_PRIMARY', mode]['max_three_p']:.4f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "The positive all-panel raw-string aggregate is supplied by the exposed paragraph-start "
            "subset and reverses sign on the new ordinary-continuation panel. This is stronger evidence "
            "for a paragraph-entry-local texture than for a transferable general continuation law. "
            f"COMPILER12 is an exploratory {score_map['COMPILER12', 'PRIMARY_CONTINUATION_TO_CONTINUATION']['gain_bits']:+.3f}-bit "
            f"lead, but it is concentrated in section B ({score_map['COMPILER12', 'PRIMARY_SECTION_B']['gain_bits']:+.3f}) "
            f"and reverses in Herbal H ({score_map['COMPILER12', 'PRIMARY_SECTION_H']['gain_bits']:+.3f}). It was not the "
            "frozen raw-transfer prediction and cannot rescue that prediction; it nominates a narrow register-conditioned "
            "continuation test rather than a manuscript-general rule."
        ),
        "",
        (
            "Adjacent pairs overlap within line runs, so the nominal pair count is not an independence "
            "count. The exported even/odd source-line sensitivities contain no overlapping pairs within "
            "each parity and are descriptive rather than newly preregistered tests."
        ),
        "",
        "## Correction and f84 handling",
        "",
        (
            "The frozen method described nominally f84r-free inputs. A post-enumeration audit found f84v "
            "rows in both inputs and a bucketed source-count implementation. The superseded 261-pair run "
            "is hash-bound in `gdt134_scope_correction.json`. The final guarded loaders reject every f84* "
            "row before formal retention or HPR2 parsing and use exact source-group count. This correction "
            "is post-enumeration, not a pristine second freeze. No f84r row exists in either final source "
            "file, and no new f84r access occurred."
        ),
        "",
        f"Frozen gates: `{json.dumps(gates, sort_keys=True)}`.",
        "",
        (
            "No content host, record semantics, heading, recipe, semantic role, word, morpheme, POS, "
            "sound, language, plaintext, meaning, or translation is inferred."
        ),
    ]
    REPORT.write_text("\n".join(lines) + "\n")

    result = {
        "schema": "GDT134_GENERAL_ADJACENT_CONTINUATION_TRANSFER_RESULT_V2",
        "status": status,
        "directional_outcome": directional_outcome,
        "correction_status": correction["status"],
        "pairs": len(target),
        "physical_folios": len({row["physical_folio"] for row in target}),
        "subsets": {
            "ALL_DESCRIPTIVE": len(all_indices),
            "PRIMARY_CONTINUATION_TO_CONTINUATION": len(primary),
            "EXPOSED_START_TO_NEXT": len(exposed),
            "PRIMARY_NONOVERLAP_EVEN_SOURCE_LINE": len(even),
            "PRIMARY_NONOVERLAP_ODD_SOURCE_LINE": len(odd),
        },
        "scores": scores,
        "null_capacity": {
            "exact_swappable": exact_capacity,
            "exact_target_mobile": exact_mobile,
            "coarse_swappable": coarse_capacity,
            "coarse_target_mobile": coarse_mobile,
        },
        "gates": gates,
        "interpretation": (
            "The exposed GDT132 raw-string lead reverses on the genuinely new ordinary-continuation "
            "primary panel; exact null capacity is insufficient."
        ),
        "claim_ceiling": (
            "Raw/formal next-field extent dependence only; no content host, record semantics, heading, "
            "recipe, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation."
        ),
        "f84": {
            "f84r_rows_in_actual_sources": 0,
            "all_f84_rows_stream_rejected_before_formal_retention_or_hpr2_parse": True,
            "new_f84r_access": False,
            "prior_limited_f84r_audit_exposure_inherited": True,
        },
        "inputs": {
            name: sha(ROOT / name)
            for name in (
                "gdt134_prediction.json",
                "gdt134_scope_correction.json",
                "gdt132_result.json",
                "gdt133_result.json",
                "gdt016_group_state_inventory.tsv",
                "gdt046_line_frames.tsv",
                "gdt127_q20_field_inventory.tsv",
                "q20ob001_source_panel.tsv",
            )
        },
        "implementation": {
            Path(__file__).name: sha(Path(__file__)),
            "freeze_gdt134_scope_correction.py": sha(ROOT / "freeze_gdt134_scope_correction.py"),
            "run_gdt131_q20_cross_line_field_onset.py": sha(ROOT / "run_gdt131_q20_cross_line_field_onset.py"),
            "run_gdt132_cross_register_continuation_arity.py": sha(ROOT / "run_gdt132_cross_register_continuation_arity.py"),
            "run_gdt133_raw_surface_transfer_decomposition.py": sha(ROOT / "run_gdt133_raw_surface_transfer_decomposition.py"),
        },
        "outputs": {
            path.name: sha(path) for path in (INVENTORY, SCORES, FOLDS, NULL, CHAIN, COUNTER)
        },
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": status,
                "directional_outcome": directional_outcome,
                "pairs": len(target),
                "primary_pairs": len(primary),
                "folios": result["physical_folios"],
                "capacity": result["null_capacity"],
                "gates": gates,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
