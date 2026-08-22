#!/usr/bin/env python3
"""Recover the exact-card core shared by both hands on the fixed prose pages."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]

TEACHING_FIELDS = [
    ["chol", "daiin"],
    ["otchey", "chor", "chty", "char", "shey"],
    ["cholor", "dy", "cthy", "oky", "dal"],
]


def desired(i: int, n: int) -> str:
    if n == 1:
        return "ONLY"
    return "FIRST" if i == 0 else "LAST" if i == n - 1 else "MIDDLE"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open(encoding="utf-8", newline="") as f:
        ledger = [r for r in csv.DictReader(f, delimiter="\t") if r["ledger_scope"] == "GDT327_PROSE"]
    by_tuple = {}; by_surface = {}
    for r in ledger:
        by_tuple.setdefault(r["exact_tuple_id"], r)
        by_surface.setdefault(r["surface"], r)

    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / "gdt327_joint_tuple_interlinear.tsv"), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--columns", "page,locus,hand,register,joint_tuple_id,observed_wrapper,within_field_position", "--forbid-prefix", "f84"]
    text = subprocess.run(cmd, check=True, text=True, capture_output=True).stdout
    lines = [line for line in text.splitlines() if not line.startswith("GUARD_STATS ")]
    formal = list(csv.DictReader(lines, delimiter="\t"))

    occurrence = defaultdict(list); positions = defaultdict(Counter)
    for r in formal:
        occurrence[r["joint_tuple_id"]].append(r)
        positions[r["joint_tuple_id"]][r["within_field_position"]] += 1

    shared = []
    for tid, rows in occurrence.items():
        hands = sorted({r["hand"] for r in rows})
        if len(hands) < 2:
            continue
        gloss = by_tuple[tid]
        shared.append({
            "exact_tuple_id": tid,
            "surface": gloss["surface"],
            "selected_default_English": gloss["default_English"],
            "source_class": gloss["source_class"],
            "events": len(rows),
            "hand_1_events": sum(r["hand"] == "1" for r in rows),
            "hand_2_events": sum(r["hand"] == "2" for r in rows),
            "hand_1_wrappers": "|".join(sorted({r["observed_wrapper"] or "BARE" for r in rows if r["hand"] == "1"})),
            "hand_2_wrappers": "|".join(sorted({r["observed_wrapper"] or "BARE" for r in rows if r["hand"] == "2"})),
            "registers": "|".join(sorted({r["register"] for r in rows})),
            "pages": "|".join(sorted({r["page"] for r in rows})),
            "positions": ";".join(f"{k}:{v}" for k, v in sorted(positions[tid].items())),
            "curriculum_level": "SHARED_APPRENTICE_CORE",
        })
    shared.sort(key=lambda r: (-int(r["events"]), r["surface"]))
    core = HERE / "V38_SHARED_WORKSHOP_CORE.tsv"
    with core.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(shared[0]), lineterminator="\n")
        w.writeheader(); w.writerows(shared)

    teaching = []
    for field_no, field in enumerate(TEACHING_FIELDS, 1):
        for i, surface in enumerate(field):
            gloss = by_surface[surface]; tid = gloss["exact_tuple_id"]; pos = desired(i, len(field))
            teaching.append({
                "field_no": field_no,
                "card_no": i + 1,
                "surface": surface,
                "exact_tuple_id": tid,
                "selected_default_English": gloss["default_English"],
                "desired_position": pos,
                "observed_position_support": positions[tid][pos],
                "position_attested": str(positions[tid][pos] > 0).upper(),
                "both_hands_attested": str(len({r["hand"] for r in occurrence[tid]}) >= 2).upper(),
            })
    teach = HERE / "V38_SHARED_CORE_TEACHING_SENTENCE.tsv"
    with teach.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(teaching[0]), lineterminator="\n")
        w.writeheader(); w.writerows(teaching)

    summary = {
        "schema": "SIDEQUEST_V38_SHARED_WORKSHOP_CORE_V1",
        "status": "SHARED_PROCESS_SCAFFOLD_PLUS_LOCAL_EXEMPLAR_TAIL_SELECTED",
        "events": len(formal),
        "exact_card_types": len(occurrence),
        "hands": sorted({r["hand"] for r in formal}),
        "shared_exact_card_types": len(shared),
        "shared_core_events": sum(int(r["events"]) for r in shared),
        "shared_core_event_share": sum(int(r["events"]) for r in shared) / len(formal),
        "local_tail_types": len(occurrence) - len(shared),
        "teaching_sentence_cards": len(teaching),
        "teaching_sentence_all_shared": all(r["both_hands_attested"] == "TRUE" for r in teaching),
        "teaching_sentence_all_positions_attested": all(r["position_attested"] == "TRUE" for r in teaching),
        "f84_rows_accessed": 0,
        "f84r_rows_accessed": 0,
    }
    (HERE / "V38_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
