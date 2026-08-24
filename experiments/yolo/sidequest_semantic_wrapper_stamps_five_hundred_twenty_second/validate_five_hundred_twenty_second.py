#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    instructions = read("FIVE_HUNDRED_TWENTY_SECOND_SIXTY_SIX_WRAPPER_INSTRUCTIONS.tsv")
    stamps = read("FIVE_HUNDRED_TWENTY_SECOND_EIGHT_WRAPPER_STAMPS.tsv")
    pairs = read("FIVE_HUNDRED_TWENTY_SECOND_FIFTY_THREE_SURFACE_PAIRS.tsv")
    log = read("FIVE_HUNDRED_TWENTY_SECOND_381_STAMP_RENDERER_LOG.tsv")
    checks = {
        "instructions66": len(instructions) == 66,
        "surface_events67": sum(int(row["support_events"]) for row in instructions) == 67,
        "pairs53": len(pairs) == 53,
        "stamps8": len(stamps) == 8
        and [row["wrapper_stamp"] for row in stamps] == ["Ø", "q", "s", "d", "t", "ch", "che", "sh"],
        "stamp_counts": Counter(row["apply_wrapper_stamp"] for row in instructions)
        == Counter({"Ø": 16, "s": 11, "q": 9, "d": 9, "sh": 6, "ch": 6, "t": 5, "che": 4}),
        "shared_tail_everywhere": all(row["retain_tail"] for row in instructions),
        "exact_composition": all(
            row["predicted_local_surface"] == row["observed_local_surface"] for row in instructions
        ),
        "no_whole_pair_memory": all(row["memorize_whole_pair"] == "NO" for row in pairs),
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "stamp_events67": sum(row["wrapper_execution"] == "LOCAL_WRAPPER_STAMP" for row in log) == 67,
        "surface_roundtrip": all(row["stamp_output_surface"] == row["renderer_final_surface"] for row in log),
        "loads38": sum(row["locus_mode_load_here"] == "YES" for row in log) == 38,
        "automatic343": sum(row["locus_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 343,
        "semantic_none": all(row["semantic_value"] == "NONE" for row in stamps),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in instructions + log),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
