#!/usr/bin/env python3
"""Run the frozen target-blind SNPL002 synthetic preflight."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from snpl002_core import (
    LABEL_LOCI, READINGS, TARGET_PAGES, edge_mutation, family_only, load_panel, score_world,
)


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SPEC = BASE / "SNPL002_SOURCE_NATIVE_LOCAL_QUERY_PREFLIGHT_SPEC.md"
CORE = BASE / "snpl002_core.py"
OUT = RESULTS / "snpl002_source_native_local_query_preflight.json"
OUT_MD = RESULTS / "snpl002_source_native_local_query_preflight.md"
_WORKER_PANEL = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose(seed: str, values: list[str], count: int) -> list[str]:
    ranked = sorted(values, key=lambda value: hashlib.sha256(f"{seed}|{value}".encode()).digest())
    return ranked[:count]


def selected(panel, world: int) -> tuple[str, str, str, str]:
    b = choose(f"SNPL002|B|{world}", sorted(panel.background[("B", "5")]["ZL3b"]), 1)
    a = choose(f"SNPL002|A|{world}", sorted(panel.background[("A", "1")]["ZL3b"]), 3)
    return tuple(b + a)


def inserts(panel, family: str, world: int) -> dict[str, dict[int, tuple[str, ...]]]:
    answer = {reading: {} for reading in READINGS}
    if family == "NULL":
        return answer
    if family == "GLOBAL_EDGE_MUTATION":
        for reading in READINGS:
            for index, locus in enumerate(LABEL_LOCI):
                answer[reading][index] = edge_mutation(panel.labels[locus][reading], panel.member_inventory)
    elif family == "ONE_LABEL":
        index = world % 4
        for reading in READINGS:
            answer[reading][index] = edge_mutation(panel.labels[LABEL_LOCI[index]][reading], panel.member_inventory)
    elif family == "WRONG_PAIRING":
        for reading in READINGS:
            for index in range(4):
                source = (index - 1) % 4
                answer[reading][index] = edge_mutation(panel.labels[LABEL_LOCI[source]][reading], panel.member_inventory)
    elif family == "ONE_READING":
        reading = READINGS[world % len(READINGS)]
        for index, locus in enumerate(LABEL_LOCI):
            answer[reading][index] = edge_mutation(panel.labels[locus][reading], panel.member_inventory)
    elif family == "FAMILY_ONLY":
        for reading in READINGS:
            for index, locus in enumerate(LABEL_LOCI):
                answer[reading][index] = family_only(panel.labels[locus][reading], panel.member_inventory)
    else:
        raise ValueError(family)
    return answer


def compact(world: dict, family: str, index: int) -> dict:
    return {
        "family": family,
        "world": index,
        "selected_pages": world["selected_pages"],
        "matrix": world["matrix"],
        "matrix_sha256": world["matrix_sha256"],
        "assignments": world["assignments"],
        "gates": world["gates"],
        "passes": world["passes"],
    }


def run_task(task: tuple[str, int]) -> tuple[str, int, dict]:
    family, index = task
    if _WORKER_PANEL is None:
        raise RuntimeError("worker panel unavailable")
    world = score_world(
        _WORKER_PANEL,
        selected(_WORKER_PANEL, index),
        inserts(_WORKER_PANEL, family, index),
    )
    return family, index, compact(world, family, index)


def main() -> None:
    global _WORKER_PANEL
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("preflight output already exists")
    panel = load_panel(GROUPS)
    _WORKER_PANEL = panel
    families = {"NULL": 64, "GLOBAL_EDGE_MUTATION": 8, "ONE_LABEL": 8, "WRONG_PAIRING": 8, "ONE_READING": 8, "FAMILY_ONLY": 8}
    tasks = [(family, index) for family, count in families.items() for index in range(count)]
    workers = min(32, os.cpu_count() or 1, len(tasks))
    context = multiprocessing.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        completed = list(executor.map(run_task, tasks, chunksize=1))
    records = {family: [] for family in families}
    for family, index, record in completed:
        if index != len(records[family]):
            raise RuntimeError((family, index, len(records[family])))
        records[family].append(record)
    pass_counts = {family: sum(row["passes"] for row in rows) for family, rows in records.items()}

    gates = {
        "null_at_most_2_of_64": pass_counts["NULL"] <= 2,
        "global_edge_mutation_at_least_7_of_8": pass_counts["GLOBAL_EDGE_MUTATION"] >= 7,
        "one_label_0_of_8": pass_counts["ONE_LABEL"] == 0,
        "wrong_pairing_0_of_8": pass_counts["WRONG_PAIRING"] == 0,
        "one_reading_0_of_8": pass_counts["ONE_READING"] == 0,
        "family_only_0_of_8": pass_counts["FAMILY_ONLY"] == 0,
        "target_pages_excluded_before_group_retention": all(
            target not in panel.background[stratum][reading]
            for target in TARGET_PAGES for stratum in panel.background for reading in READINGS
        ),
        "target_scores_computed": False,
        "ocr_or_automated_vision_used": False,
    }
    positive = [name for name in gates if name not in {"target_scores_computed", "ocr_or_automated_vision_used"}]
    passed = all(gates[name] for name in positive) and not gates["target_scores_computed"] and not gates["ocr_or_automated_vision_used"]
    decision = "GO_FREEZE_SNPL002_TARGET" if passed else "STOP_SNPL002_PREFLIGHT_FAILED_TARGET_FORBIDDEN"
    result = {
        "experiment": "SNPL002_SOURCE_NATIVE_LOCAL_QUERY_PREFLIGHT",
        "status": decision,
        "frozen_files": {"spec_sha256": sha(SPEC), "core_sha256": sha(CORE), "groups_sha256": panel.source_sha256},
        "world_counts": families,
        "workers": workers,
        "pass_counts": pass_counts,
        "records": records,
        "gates": gates,
        "decision": decision,
        "target_pages": list(TARGET_PAGES),
        "target_rows_accessed": False,
        "target_scores_computed": False,
        "claim_ceiling": (
            "A pass validates only the frozen source-native local member-window scorer on target-blind "
            "synthetic controls. It can authorize one separately frozen four-pair target and supplies "
            "no plant name, word meaning, sound, language, cipher, plaintext, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# SNPL002 source-native local-query preflight\n\n"
        f"Decision: **{decision}**.\n\n"
        + "Pass counts: " + ", ".join(f"{key} {value}/{families[key]}" for key, value in pass_counts.items()) + ".\n\n"
        "No target Herbal row or target score was opened. This result supplies no plant name, "
        "word meaning, sound, language, cipher, plaintext, or translation.\n"
    )


if __name__ == "__main__":
    main()
