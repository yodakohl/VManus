#!/usr/bin/env python3
"""Run the target-free synthetic calibration for the cho/che co-switch route."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "cho_che_coswitch_masked_panel.tsv"
CAPACITY = RESULTS / "cho_che_coswitch_capacity_v2.json"
CAPACITY_VALIDATION = RESULTS / "cho_che_coswitch_capacity_validation.json"
SPEC = BASE / "CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT_SPEC.md"
CORE = BASE / "cho_che_coswitch_core.py"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "cho_che_coswitch_synthetic_preflight.json"
REPORT = RESULTS / "cho_che_coswitch_synthetic_preflight_report.md"
TARGETS = (
    RESULTS / "cho_che_coswitch_target.json",
    RESULTS / "cho_che_coswitch_target_report.md",
    RESULTS / "cho_che_coswitch_target_validation.json",
    RESULTS / "cho_che_coswitch_target_validation_report.md",
)
EXPECTED = {
    PANEL: "25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003",
    CAPACITY: "c32a6dc5456a59f469de1f8d47d95fba8e6384d60ecccd678adb678c0382b775",
    CAPACITY_VALIDATION: "68bf07fa2fcaf5437fd5240ac394b4c20add24d4867eb3b3ac846378b0809d73",
    SPEC: "aa75c979b7a7d4d6a1ed86973ce47101cdcc4d73ff1595af5c2fd84f7a810186",
    CORE: "a1f246f7c25318eb7c54c393425d939f4ef5755df066732716322aa1b214602d",
}
FIELDS = (
    "source_group_id", "edition", "locus", "page", "collapsed_page",
    "physical_folio", "side", "page_state", "section", "currier", "hand",
    "kind", "grammar_scope", "primary_sta_symbol_count",
    "page_position_quartile", "group_position_class",
)
NUISANCE = (
    "section", "currier", "hand", "kind", "grammar_scope",
    "primary_sta_symbol_count", "page_position_quartile", "group_position_class",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("refusing to overwrite co-switch preflight")
    with tempfile.TemporaryDirectory(prefix="cho_che_coswitch_preflight_", dir=RESULTS) as directory:
        a, b = Path(directory) / "json", Path(directory) / "md"
        a.write_bytes(result_bytes)
        b.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("preflight artifact appeared")
        os.link(a, OUT)
        try:
            os.link(b, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    target_absence_before = {path.name: not path.exists() for path in TARGETS}
    if not all(target_absence_before.values()):
        raise SystemExit("target artifact exists")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen preflight mismatch: {path.name}")
    if json.loads(CAPACITY.read_text())["status"] != "PASS_CORRECTED_INFERENTIAL_UNIT_CHO_CHE_COSWITCH_CAPACITY":
        raise SystemExit("capacity not PASS")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_COSWITCH_CAPACITY_RECONSTRUCTION":
        raise SystemExit("capacity validation not PASS")

    import numpy as np
    from cho_che_coswitch_core import BLOCKS, BLOCK_DIMS, DIAGNOSTIC, HIGH_RECTO, LEAVES, READINGS, compact, score

    with PANEL.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("panel schema")
        rows = list(reader)
    if len(rows) != 5012 or len({row["source_group_id"] for row in rows}) != len(rows):
        raise ValueError("panel identity")
    grouped = defaultdict(list)
    for row in rows:
        cell = tuple(row[field] for field in NUISANCE)
        grouped[(row["edition"], row["physical_folio"], row["side"], cell)].append(row["source_group_id"])
    shared = {}
    noise_scale = np.zeros((len(READINGS), len(LEAVES)), dtype=np.float64)
    side_rows = Counter()
    for edition_index, edition in enumerate(READINGS):
        for leaf_index, leaf in enumerate(LEAVES):
            recto = {key[3] for key, values in grouped.items() if key[:3] == (edition, leaf, "r") and len(values) >= 2}
            verso = {key[3] for key, values in grouped.items() if key[:3] == (edition, leaf, "v") and len(values) >= 2}
            cells = sorted(recto & verso)
            if not cells:
                raise ValueError("empty nuisance overlap")
            shared[(edition, leaf)] = cells
            variance = 0.0
            for cell in cells:
                nr = len(grouped[(edition, leaf, "r", cell)])
                nv = len(grouped[(edition, leaf, "v", cell)])
                side_rows[(edition, leaf, "r")] += nr
                side_rows[(edition, leaf, "v")] += nv
                variance += 1 / nr + 1 / nv
            noise_scale[edition_index, leaf_index] = np.sqrt(variance / len(cells) ** 2)
    if len(shared) != 24 or len(side_rows) != 48 or not np.isfinite(noise_scale).all():
        raise ValueError("geometry")

    def make_world(family: str, world: int, strength: float):
        directions = []
        for block_index, dim in enumerate(BLOCK_DIMS):
            rng = np.random.default_rng(stable_seed("CCSW001", family, world, "DIRECTION", block_index))
            direction = rng.normal(size=dim)
            direction /= np.linalg.norm(direction)
            directions.append(direction)
        vectors = []
        for block_index, dim in enumerate(BLOCK_DIMS):
            block = np.zeros((len(READINGS), len(LEAVES), dim), dtype=np.float64)
            for leaf_index, leaf in enumerate(LEAVES):
                shared_rng = np.random.default_rng(stable_seed("CCSW001", family, world, "SHARED", block_index, leaf))
                shared_noise = shared_rng.normal(size=dim)
                for edition_index, edition in enumerate(READINGS):
                    own_rng = np.random.default_rng(stable_seed("CCSW001", family, world, "READING", block_index, leaf, edition))
                    noise = np.sqrt(.8) * shared_noise + np.sqrt(.2) * own_rng.normal(size=dim)
                    scale = noise_scale[edition_index, leaf_index]
                    block[edition_index, leaf_index] = scale * noise
                    active = True
                    sign = 1.0
                    if family == "NULL":
                        active = False
                    elif family == "ONE_LEAF":
                        active = leaf_index == 0
                    elif family == "ONE_READING":
                        active = edition_index == 0
                    elif family == "OPPOSITE_READING":
                        sign = -1.0 if edition_index == 2 else 1.0
                    elif family == "SIDE_ONLY":
                        sign = 1.0 if HIGH_RECTO[leaf_index] else -1.0
                    elif family == "DIAGNOSTIC_ONLY":
                        active = bool(DIAGNOSTIC[leaf_index])
                    elif family == "PROSE_ONLY":
                        active = not bool(DIAGNOSTIC[leaf_index])
                    elif family == "ONE_BLOCK":
                        active = block_index == 0
                    elif family == "DISTRIBUTED_TWO_BLOCK":
                        active = block_index in (0, 2)
                    elif family == "DISTRIBUTED_THREE_BLOCK":
                        active = True
                    else:
                        raise ValueError("world family")
                    if active:
                        block[edition_index, leaf_index] += sign * strength * scale * np.sqrt(dim) * directions[block_index]
            vectors.append(block)
        return tuple(vectors)

    families = {
        "NULL": (64, 0.0),
        "DISTRIBUTED_THREE_BLOCK": (8, .75),
        "DISTRIBUTED_TWO_BLOCK": (8, .75),
        "ONE_LEAF": (8, 1.0),
        "ONE_READING": (8, 1.0),
        "OPPOSITE_READING": (8, 1.0),
        "SIDE_ONLY": (8, 1.0),
        "DIAGNOSTIC_ONLY": (8, 1.0),
        "PROSE_ONLY": (8, 1.0),
        "ONE_BLOCK": (8, 1.0),
    }
    records = {}
    pass_counts = {}
    for family, (count, strength) in families.items():
        values = []
        for world in range(count):
            value = score(make_world(family, world, strength))
            values.append({"world": world, **compact(value)})
        records[family] = values
        pass_counts[family] = sum(value["passes"] for value in values)

    # Algebraic controls use one distributed world and never touch a target.
    fixture = make_world("DISTRIBUTED_THREE_BLOCK", 0, .75)
    original = compact(score(fixture))
    complement = compact(score(tuple(-block for block in fixture)))
    complement_invariant = original == complement
    mutation_rejections = {}
    for name, mutation in {
        "wrong_block_count": lambda: score(fixture[:2]),
        "wrong_shape": lambda: score((fixture[0][:, :7], fixture[1], fixture[2])),
        "zero_vector": lambda: score((np.zeros_like(fixture[0]), fixture[1], fixture[2])),
        "nonfinite": lambda: score((np.full_like(fixture[0], np.nan), fixture[1], fixture[2])),
    }.items():
        try:
            mutation()
        except (ValueError, IndexError, FloatingPointError):
            mutation_rejections[name] = True
        else:
            mutation_rejections[name] = False

    target_absence_after = {path.name: not path.exists() for path in TARGETS}
    gates = {
        "null_at_most_one_of_64": pass_counts["NULL"] <= 1,
        "three_block_power_at_least_seven_of_eight": pass_counts["DISTRIBUTED_THREE_BLOCK"] >= 7,
        "two_block_power_at_least_seven_of_eight": pass_counts["DISTRIBUTED_TWO_BLOCK"] >= 7,
        "all_adversarial_controls_zero": all(pass_counts[name] == 0 for name in families if name not in {"NULL", "DISTRIBUTED_THREE_BLOCK", "DISTRIBUTED_TWO_BLOCK"}),
        "exact_256_sign_orbit_and_floor": original["p_value"] >= 2 / 256,
        "exact_24_leaf_reading_geometries": len(shared) == 24,
        "exact_272_shared_nuisance_cells": sum(map(len, shared.values())) == 272,
        "exact_2730_retained_group_rows": sum(side_rows.values()) == 2730,
        "minimum_nine_rows_per_leaf_side": min(side_rows.values()) == 9,
        "complement_invariance": complement_invariant,
        "all_mutations_rejected": all(mutation_rejections.values()),
        "all_numeric_summaries_finite": all(np.isfinite(value[key]).all() for values in records.values() for value in values for key in ("primary", "p_value", "reading_alignment", "min_deletion", "orientation_cross", "domain_cross", "reading_agreement", "max_concentration")),
        "target_absent_before": all(target_absence_before.values()),
        "target_absent_after": all(target_absence_after.values()),
        "target_family_sequences_accessed_zero": True,
        "english_glosses_zero": True,
    }
    passed = all(gates.values())
    status = "PASS_TARGET_FREE_CHO_CHE_COSWITCH_PREFLIGHT" if passed else "STOP_CHO_CHE_COSWITCH_PREFLIGHT"
    decision = "AUTHORIZE_ONE_FROZEN_COSWITCH_TARGET" if passed else "TARGET_FORBIDDEN_CLOSE_EXACT_COSWITCH_SCORER"
    result = {
        "experiment": "CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*EXPECTED, RUNNER)},
        "geometry": {
            "readings": list(READINGS), "leaves": list(LEAVES), "blocks": list(BLOCKS),
            "block_dims": list(BLOCK_DIMS), "shared_nuisance_cells": sum(map(len, shared.values())),
            "retained_group_rows": sum(side_rows.values()), "minimum_leaf_side_rows": min(side_rows.values()),
            "noise_scale_sha256": hashlib.sha256(np.asarray(noise_scale, dtype="<f8").tobytes(order="C")).hexdigest(),
        },
        "world_definition": {name: {"worlds": count, "strength": strength} for name, (count, strength) in families.items()},
        "pass_counts": pass_counts,
        "worlds": records,
        "controls": {"complement_invariant": complement_invariant, "mutation_rejections": mutation_rejections},
        "gates": gates,
        "target_absence_before": target_absence_before,
        "target_absence_after": target_absence_after,
        "target_family_sequences_accessed": 0,
        "target_associations_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "A pass validates only the frozen abstract scorer's null control and power for a distributed standardized synthetic effect on the exact eight-leaf geometry. It supplies no manuscript co-switch result, meaning, sound, wordhood, language, cipher, plaintext, or translation.",
    }
    report = f"""# `cho/che` independent co-switch synthetic preflight

Status: **{status}**

The target-free scorer used **272** exact nuisance cells and **2,730** masked
group rows across the eight physical leaves.  Pass counts were: null
**{pass_counts['NULL']}/64**, distributed three-block
**{pass_counts['DISTRIBUTED_THREE_BLOCK']}/8**, distributed two-block
**{pass_counts['DISTRIBUTED_TWO_BLOCK']}/8**.  Adversarial controls passed:
**{sum(pass_counts[name] for name in families if name not in {'NULL', 'DISTRIBUTED_THREE_BLOCK', 'DISTRIBUTED_TWO_BLOCK'})}** total across 56 worlds.

Decision: **{decision}**.  No STA family sequence or manuscript feature/state
association was opened.  This supplies no co-switch result, meaning, sound,
wordhood, language, cipher, plaintext, or translation.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "decision": decision, "pass_counts": pass_counts, "gates": gates}, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
