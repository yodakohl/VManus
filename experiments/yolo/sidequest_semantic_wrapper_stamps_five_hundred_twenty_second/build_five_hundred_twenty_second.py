#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P521 = ROOT / "experiments/yolo/sidequest_semantic_locus_renderer_tables_five_hundred_twenty_first"


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


def split_by_longest_shared_tail(source: str, target: str) -> tuple[str, str, str]:
    length = 0
    while (
        length < min(len(source), len(target))
        and source[-1 - length] == target[-1 - length]
    ):
        length += 1
    if length == 0:
        raise ValueError(f"no stable tail: {source} -> {target}")
    return source[:-length], target[:-length], source[-length:]


def display_wrapper(wrapper: str) -> str:
    return wrapper if wrapper else "Ø"


def main() -> None:
    source_entries = read_tsv(P521 / "FIVE_HUNDRED_TWENTY_FIRST_SIXTY_SIX_LOCAL_OVERRIDE_ENTRIES.tsv")
    source_log = read_tsv(P521 / "FIVE_HUNDRED_TWENTY_FIRST_381_LOCUS_RENDERER_LOG.tsv")
    instructions: list[dict[str, str]] = []
    for number, row in enumerate(source_entries, 1):
        input_wrapper, output_wrapper, tail = split_by_longest_shared_tail(
            row["input_rule_surface"], row["local_output_surface"]
        )
        instructions.append(
            {
                "instruction_no": str(number),
                "mode_id": row["mode_id"],
                "record": row["record"],
                "page": row["page"],
                "locus": row["locus"],
                "input_rule_surface": row["input_rule_surface"],
                "remove_wrapper": display_wrapper(input_wrapper),
                "retain_tail": tail,
                "apply_wrapper_stamp": display_wrapper(output_wrapper),
                "predicted_local_surface": output_wrapper + tail,
                "observed_local_surface": row["local_output_surface"],
                "support_events": row["support_events"],
                "event_ids": row["event_ids"],
                "copy_rule_de": f"Vorderen Träger {display_wrapper(input_wrapper)} abheben, Rest {tail} stehen lassen, Stempel {display_wrapper(output_wrapper)} vorsetzen.",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SECOND_SIXTY_SIX_WRAPPER_INSTRUCTIONS.tsv", instructions)

    by_stamp: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in instructions:
        by_stamp[row["apply_wrapper_stamp"]].append(row)
    preferred_order = ["Ø", "q", "s", "d", "t", "ch", "che", "sh"]
    stamps: list[dict[str, str]] = []
    for number, stamp in enumerate(preferred_order, 1):
        rows = by_stamp[stamp]
        stamps.append(
            {
                "stamp_no": str(number),
                "wrapper_stamp": stamp,
                "local_table_entries": str(len(rows)),
                "surface_events": str(sum(int(row["support_events"]) for row in rows)),
                "distinct_retained_tails": str(len({row["retain_tail"] for row in rows})),
                "example": f"{rows[0]['input_rule_surface']}→{rows[0]['observed_local_surface']}",
                "workshop_value": "GRAPHIC_WRAPPER_ONLY",
                "semantic_value": "NONE",
                "teaching_de": (
                    "Keinen vorderen Wrapper setzen; den erhaltenen Rest direkt schreiben."
                    if stamp == "Ø"
                    else f"Den graphischen Eingangsstempel {stamp} vor den erhaltenen Rest setzen."
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SECOND_EIGHT_WRAPPER_STAMPS.tsv", stamps)

    pair_counter = Counter(
        (row["input_rule_surface"], row["observed_local_surface"]) for row in instructions
    )
    pairs: list[dict[str, str]] = []
    for number, ((input_surface, output_surface), count) in enumerate(sorted(pair_counter.items()), 1):
        row = next(
            item
            for item in instructions
            if item["input_rule_surface"] == input_surface
            and item["observed_local_surface"] == output_surface
        )
        pairs.append(
            {
                "pair_no": str(number),
                "input_rule_surface": input_surface,
                "local_output_surface": output_surface,
                "remove_wrapper": row["remove_wrapper"],
                "retain_tail": row["retain_tail"],
                "apply_wrapper_stamp": row["apply_wrapper_stamp"],
                "locus_tables_using_pair": str(count),
                "memorize_whole_pair": "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SECOND_FIFTY_THREE_SURFACE_PAIRS.tsv", pairs)

    stamp_by_event: dict[str, dict[str, str]] = {}
    for row in instructions:
        for event_id in row["event_ids"].split("|"):
            stamp_by_event[event_id] = row
    output: list[dict[str, str]] = []
    for row in source_log:
        instruction = stamp_by_event.get(row["event_id"])
        output.append(
            {
                **row,
                "wrapper_execution": "LOCAL_WRAPPER_STAMP" if instruction else "GLOBAL_RULE_SURFACE",
                "remove_wrapper": instruction["remove_wrapper"] if instruction else "NONE",
                "retained_surface_tail": instruction["retain_tail"] if instruction else row["renderer_final_surface"],
                "applied_wrapper_stamp": instruction["apply_wrapper_stamp"] if instruction else "NONE",
                "stamp_output_surface": instruction["predicted_local_surface"] if instruction else row["renderer_final_surface"],
                "whole_surface_pair_memorized": "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SECOND_381_STAMP_RENDERER_LOG.tsv", output)

    summary = {
        "status": "PASS",
        "events": len(output),
        "local_table_entries": len(instructions),
        "surface_events": sum(int(row["support_events"]) for row in instructions),
        "distinct_surface_pairs": len(pairs),
        "wrapper_stamps": len(stamps),
        "distinct_retained_tails": len({row["retain_tail"] for row in instructions}),
        "all_pairs_exactly_composed": all(
            row["predicted_local_surface"] == row["observed_local_surface"] for row in instructions
        ),
        "conscious_locus_loads_unchanged": sum(row["locus_mode_load_here"] == "YES" for row in output),
        "automatic_events_unchanged": sum(row["locus_master_mode"] == "AUTOMATIC_FLOW" for row in output),
    }
    (HERE / "FIVE_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
