#!/usr/bin/env python3
"""Inventory the terminal card palette on the fixed prose pages."""

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


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open(encoding="utf-8", newline="") as f:
        ledger = [r for r in csv.DictReader(f, delimiter="\t") if r["ledger_scope"] == "GDT327_PROSE"]
    by_tuple = {}
    for r in ledger:
        by_tuple.setdefault(r["exact_tuple_id"], r)

    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / "gdt327_joint_tuple_interlinear.tsv"), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--columns", "page,locus,record_ordinal,field_ordinal,within_field_position,joint_tuple_id,host_id,dy_closure,b3", "--forbid-prefix", "f84"]
    text = subprocess.run(cmd, check=True, text=True, capture_output=True).stdout
    lines = [line for line in text.splitlines() if not line.startswith("GUARD_STATS ")]
    formal = list(csv.DictReader(lines, delimiter="\t"))

    positions = defaultdict(Counter)
    pages = defaultdict(set)
    predecessors = defaultdict(set)
    fields = defaultdict(list)
    for r in formal:
        positions[r["joint_tuple_id"]][r["within_field_position"]] += 1
        pages[r["joint_tuple_id"]].add(r["page"])
        fields[(r["page"], r["record_ordinal"], r["locus"], r["field_ordinal"])].append(r)
    for field in fields.values():
        for i, row in enumerate(field):
            if i:
                predecessors[row["joint_tuple_id"]].add(field[i - 1]["joint_tuple_id"])

    output = []
    for tid, count in positions.items():
        terminal = count["LAST"] + count["ONLY"]
        if not terminal:
            continue
        gloss = by_tuple[tid]
        examples = [r for r in formal if r["joint_tuple_id"] == tid]
        closure = Counter((r["dy_closure"], r["b3"]) for r in examples)
        output.append({
            "exact_tuple_id": tid,
            "surface": gloss["surface"],
            "selected_default_English": gloss["default_English"],
            "source_class": gloss["source_class"],
            "terminal_events": terminal,
            "last_events": count["LAST"],
            "only_events": count["ONLY"],
            "nonterminal_events": count["FIRST"] + count["MIDDLE"],
            "support_pages": len(pages[tid]),
            "distinct_predecessors": len(predecessors[tid]),
            "closure_states": ";".join(f"DY{d}_B3{b}:{n}" for (d, b), n in sorted(closure.items())),
            "workshop_use": "LICENSED_TERMINAL_CARD_NOT_FREE_PUNCTUATION",
        })
    output.sort(key=lambda r: (-int(r["terminal_events"]), r["surface"], r["exact_tuple_id"]))
    path = HERE / "V37_TERMINAL_CARD_PALETTE.tsv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(output[0]), lineterminator="\n")
        w.writeheader(); w.writerows(output)

    terminal_events = [r for r in formal if r["within_field_position"] in {"LAST", "ONLY"}]
    closure = Counter((r["dy_closure"], r["b3"]) for r in terminal_events)
    top4 = sum(int(r["terminal_events"]) for r in output[:4])
    summary = {
        "schema": "SIDEQUEST_V37_TERMINAL_PALETTE_V1",
        "status": "CONTENT_BEARING_TERMINAL_PALETTE_SELECTED",
        "events": len(formal),
        "fields_and_terminal_events": len(terminal_events),
        "terminal_exact_card_types": len(output),
        "closure_bearing_terminal_types": sum("DY1_" in r["closure_states"] or "B31" in r["closure_states"] for r in output),
        "terminal_only_types": sum(int(r["nonterminal_events"]) == 0 for r in output),
        "recurrent_terminal_only_types": sum(int(r["nonterminal_events"]) == 0 and int(r["terminal_events"]) >= 2 for r in output),
        "top_four_terminal_events": top4,
        "top_four_terminal_share": top4 / len(terminal_events),
        "terminal_DY1_B30": closure[("1", "0")],
        "terminal_DY0_B30": closure[("0", "0")],
        "terminal_DY0_B31": closure[("0", "1")],
        "nonterminal_with_DY_or_B3": sum(r["dy_closure"] == "1" or r["b3"] == "1" for r in formal if r["within_field_position"] not in {"LAST", "ONLY"}),
        "universal_free_closer_selected": False,
        "repaired_drinking_close": "rshedy = drink the stated portion; close the rubric",
        "f84_rows_accessed": 0,
        "f84r_rows_accessed": 0,
    }
    (HERE / "V37_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
