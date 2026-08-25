#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_eighth_workshop_grammar_eight_hundred_thirty_first"
STATEMENTS = BASE / "EIGHT_HUNDRED_THIRTY_FIRST_116_STATEMENT_REPARSE.tsv"

CANDIDATES = [
    ("arbeitsgang", "O", "SPECIFIC_PROCESS_NOUN", "NOMINATE_O_TO_ARBEITSGANG"),
    ("schritt", "DY", "CLOSURE_OBJECT", "KEEP_AS_DY_OBJECT"),
    ("fluessigkeit", "AIR", "GENERAL_MATERIAL_NOUN", "KEEP_WATER_AS_MORE_CONCRETE_WORKING_BET"),
    ("fuehren", "L", "GUIDE_SYNONYM", "KEEP_AS_FLUENT_SYNONYM"),
    ("beibehalten", "SH", "HOLD_CONTINUE_SYNONYM", "KEEP_AS_COMBINATION_EXPANSION"),
    ("empfaenger", "P", "LOCAL_RECEIVER", "KEEP_AS_OWNER_OBJECT"),
    ("nehmen", "CH", "TAKE_SYNONYM", "KEEP_AS_FLUENT_SYNONYM"),
    ("wechseln", "OT", "NEXT_ADDRESS_OPERATION", "KEEP_AS_COMBINATION_EXPANSION"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(row: dict[str, str]) -> list[str]:
    return [token for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")]


def occurrences(text: str, stem: str) -> int:
    return len(re.findall(rf"\b{re.escape(stem)}\w*", text.lower()))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    statements = read(STATEMENTS)
    rows = []
    for stem, component, role, decision in CANDIDATES:
        word_rows = [row for row in statements if occurrences(row["working_reading_de"], stem)]
        component_rows = [row for row in statements if component in tokens(row)]
        both = [row for row in word_rows if component in tokens(row)]
        rows.append(
            {
                "hidden_stem": stem.upper(),
                "candidate_component": component,
                "tokens": sum(occurrences(row["working_reading_de"], stem) for row in statements),
                "statements": len(word_rows),
                "records": len({row["record"] for row in word_rows}),
                "component_statements": len(component_rows),
                "word_and_component_statements": len(both),
                "word_without_component": len(word_rows) - len(both),
                "component_without_word": len(component_rows) - len(both),
                "layer_role": role,
                "decision": decision,
            }
        )

    o_rows = []
    for row in statements:
        if "O" not in tokens(row):
            continue
        n = occurrences(row["working_reading_de"], "arbeitsgang")
        o_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "o_component_tokens": tokens(row).count("O"),
                "arbeitsgang_tokens": n,
                "arbeitsgang_present": "YES" if n else "NO",
                "surface_sequence": row["surface_sequence"],
                "working_reading_de": row["working_reading_de"],
            }
        )
    write("EIGHT_HUNDRED_THIRTY_SECOND_8_HIDDEN_WORD_CANDIDATES.tsv", rows, ["hidden_stem", "candidate_component", "tokens", "statements", "records", "component_statements", "word_and_component_statements", "word_without_component", "component_without_word", "layer_role", "decision"])
    write("EIGHT_HUNDRED_THIRTY_SECOND_17_O_STATEMENT_ALIGNMENT.tsv", o_rows, ["statement_id", "page", "record", "o_component_tokens", "arbeitsgang_tokens", "arbeitsgang_present", "surface_sequence", "working_reading_de"])
    summary = {
        "status": "PASS",
        "decision": "ARBEITSGANG_NOMINATED_AS_MORE_CONCRETE_O_VALUE",
        "candidate_stems": len(rows),
        "o_statements": len(o_rows),
        "o_statements_with_arbeitsgang": sum(row["arbeitsgang_present"] == "YES" for row in o_rows),
        "arbeitsgang_tokens": sum(int(row["arbeitsgang_tokens"]) for row in o_rows),
        "arbeitsgang_without_o": sum(occurrences(row["working_reading_de"], "arbeitsgang") > 0 and "O" not in tokens(row) for row in statements),
        "nominated_revision": "O=VORGANG -> O=ARBEITSGANG",
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
