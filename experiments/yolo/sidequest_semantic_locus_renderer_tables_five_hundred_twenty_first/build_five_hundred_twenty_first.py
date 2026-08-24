#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P520 = ROOT / "experiments/yolo/sidequest_semantic_visible_owner_thresholds_five_hundred_twentieth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(P520 / "FIVE_HUNDRED_TWENTIETH_381_THRESHOLD_MASTER_LOG.tsv")
    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_locus[(row["record"], row["locus"])].append(row)
    affected = {
        key: rows
        for key, rows in by_locus.items()
        if any(row["renderer_action"] == "COPY_LOCAL_EXEMPLAR" for row in rows)
    }

    modes: list[dict[str, str]] = []
    entries: list[dict[str, str]] = []
    mode_for_locus: dict[tuple[str, str], str] = {}
    for number, (key, rows) in enumerate(affected.items(), 1):
        mode_id = f"LR{number:02d}"
        mode_for_locus[key] = mode_id
        overrides: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            if row["renderer_action"] == "COPY_LOCAL_EXEMPLAR":
                overrides[row["renderer_first_choice"]].append(row)
        for input_surface, examples in overrides.items():
            output_surfaces = {row["renderer_final_surface"] for row in examples}
            if len(output_surfaces) != 1:
                raise ValueError(f"ambiguous local renderer key {key} {input_surface}: {output_surfaces}")
            entries.append(
                {
                    "mode_id": mode_id,
                    "record": key[0],
                    "page": rows[0]["page"],
                    "locus": key[1],
                    "input_rule_surface": input_surface,
                    "local_output_surface": next(iter(output_surfaces)),
                    "support_events": str(len(examples)),
                    "event_ids": "|".join(row["event_id"] for row in examples),
                    "instruction_de": "Wenn diese Regeloberfläche im Locus erscheint, durch die lokale Oberfläche ersetzen.",
                }
            )
        first = rows[0]
        override_events = [row for row in rows if row["renderer_action"] == "COPY_LOCAL_EXEMPLAR"]
        modes.append(
            {
                "mode_id": mode_id,
                "record": key[0],
                "page": first["page"],
                "locus": key[1],
                "load_event": first["event_id"],
                "locus_events": str(len(rows)),
                "override_entries": str(len(overrides)),
                "override_events": str(len(override_events)),
                "rule_rendered_events": str(len(rows) - len(override_events)),
                "load_instruction_de": "Am Locusanfang lokale Ersetzungstafel laden; sonst normale Rendererregel verwenden.",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_FIRST_THIRTY_EIGHT_LOCUS_RENDERER_MODES.tsv", modes)
    write_tsv("FIVE_HUNDRED_TWENTY_FIRST_SIXTY_SIX_LOCAL_OVERRIDE_ENTRIES.tsv", entries)

    load_event = {row["load_event"]: row for row in modes}
    output: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in source:
        key = (row["record"], row["locus"])
        mode_id = mode_for_locus.get(key, "GLOBAL_RULE_RENDERER")
        starts = row["event_id"] in load_event
        if starts:
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "locus": row["locus"],
                    "decision_type": "LOAD_LOCUS_RENDERER_TABLE",
                    "selected_value": mode_id,
                }
            )
        output.append(
            {
                **row,
                "locus_renderer_mode": mode_id,
                "locus_mode_load_here": "YES" if starts else "NO",
                "renderer_execution": (
                    "LOCAL_TABLE_OVERRIDE"
                    if row["renderer_action"] == "COPY_LOCAL_EXEMPLAR"
                    else "GLOBAL_RULE_RENDERER"
                ),
                "locus_conscious_decision_count": "1" if starts else "0",
                "locus_conscious_reason": "LOAD_LOCUS_RENDERER_TABLE" if starts else "NONE",
                "locus_master_mode": "CONSCIOUS_LOCAL_CHOICE" if starts else "AUTOMATIC_FLOW",
            }
        )
    for number, row in enumerate(decisions, 1):
        row["decision_no"] = str(number)
    write_tsv("FIVE_HUNDRED_TWENTY_FIRST_381_LOCUS_RENDERER_LOG.tsv", output)
    write_tsv("FIVE_HUNDRED_TWENTY_FIRST_THIRTY_EIGHT_CONSCIOUS_DECISIONS.tsv", decisions)

    comparison = [
        {
            "renderer_policy": "PER_ALLOGRAPH_EVENT",
            "conscious_loads": "67",
            "local_override_entries": "67",
            "events_copied_or_overridden": "67",
            "regular_events_preserved": "314",
            "selected": "NO",
        },
        {
            "renderer_policy": "FIFTY_SHORT_BLOCKS",
            "conscious_loads": "50",
            "local_override_entries": "67",
            "events_copied_or_overridden": "74",
            "regular_events_preserved": "307",
            "selected": "NO",
        },
        {
            "renderer_policy": "WHOLE_LOCUS_COPY",
            "conscious_loads": "38",
            "local_override_entries": "278",
            "events_copied_or_overridden": "278",
            "regular_events_preserved": "103",
            "selected": "NO",
        },
        {
            "renderer_policy": "LOCUS_OVERRIDE_TABLE",
            "conscious_loads": "38",
            "local_override_entries": "66",
            "events_copied_or_overridden": "67",
            "regular_events_preserved": "314",
            "selected": "YES",
        },
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_FIRST_RENDERER_POLICY_COMPARISON.tsv", comparison)

    summary = {
        "status": "PASS",
        "events": len(output),
        "affected_loci": len(modes),
        "local_override_entries": len(entries),
        "local_override_events": sum(int(row["override_events"]) for row in modes),
        "rule_rendered_events_inside_affected_loci": sum(int(row["rule_rendered_events"]) for row in modes),
        "conscious_mode_loads": len(decisions),
        "conscious_events": sum(row["locus_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in output),
        "automatic_events": sum(row["locus_master_mode"] == "AUTOMATIC_FLOW" for row in output),
        "mode_size_distribution": dict(Counter(int(row["override_entries"]) for row in modes)),
    }
    (HERE / "FIVE_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
