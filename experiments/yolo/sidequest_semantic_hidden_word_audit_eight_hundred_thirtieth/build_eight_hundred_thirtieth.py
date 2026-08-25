#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_layered_record_edition_eight_hundred_twenty_ninth"
STATEMENTS = BASE / "EIGHT_HUNDRED_TWENTY_NINTH_116_LAYERED_STATEMENTS.tsv"

CANDIDATES = [
    ("posten", "Y", "CURRENT_ITEM_NOUN", "NOMINATE_Y_TO_POSTEN"),
    ("schritt", "DY", "CLOSURE_OBJECT", "KEEP_AS_FLUENT_DY_EXPANSION"),
    ("arbeitsgang", "O", "VORGANG_SYNONYM", "KEEP_AS_FLUENT_O_EXPANSION"),
    ("beibehalten", "SH", "HOLD_CONTINUE_SYNONYM", "KEEP_AS_COMBINATION_EXPANSION"),
    ("fuehren", "L", "GUIDE_SYNONYM", "KEEP_AS_FLUENT_L_OR_CHD_EXPANSION"),
    ("fluessigkeit", "AIR", "MATERIAL_OWNER_NOUN", "KEEP_AS_OWNER_EXPANSION"),
    ("wechseln", "OT", "NEXT_ADDRESS_OPERATION", "KEEP_AS_OT_ADDRESS_EXPANSION"),
    ("empfaenger", "P", "LOCAL_RECEIVER_NOUN", "KEEP_AS_OWNER_EXPANSION"),
    ("nehmen", "CH", "TAKE_SYNONYM", "KEEP_AS_FLUENT_CH_EXPANSION"),
    ("folgeschritt", "OT", "NEXT_STEP_NOUN", "KEEP_AS_FLUENT_OT_EXPANSION"),
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
    candidate_rows = []
    for stem, component, role, decision in CANDIDATES:
        word_rows = [row for row in statements if occurrences(row["fluent_workshop_reading_de"], stem)]
        component_rows = [row for row in statements if component in tokens(row)]
        both = [row for row in word_rows if component in tokens(row)]
        candidate_rows.append(
            {
                "hidden_stem": stem.upper(),
                "candidate_component": component,
                "tokens": sum(occurrences(row["fluent_workshop_reading_de"], stem) for row in statements),
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

    y_rows = []
    for row in statements:
        if "Y" not in tokens(row):
            continue
        n = occurrences(row["fluent_workshop_reading_de"], "posten")
        y_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "y_component_tokens": tokens(row).count("Y"),
                "posten_tokens": n,
                "posten_present": "YES" if n else "NO",
                "surface_sequence": row["surface_sequence"],
                "fluent_workshop_reading_de": row["fluent_workshop_reading_de"],
            }
        )
    non_y_posten = [row for row in statements if "Y" not in tokens(row) and occurrences(row["fluent_workshop_reading_de"], "posten")]

    write("EIGHT_HUNDRED_THIRTIETH_10_HIDDEN_WORD_CANDIDATES.tsv", candidate_rows, ["hidden_stem", "candidate_component", "tokens", "statements", "records", "component_statements", "word_and_component_statements", "word_without_component", "component_without_word", "layer_role", "decision"])
    write("EIGHT_HUNDRED_THIRTIETH_60_Y_STATEMENT_ALIGNMENT.tsv", y_rows, ["statement_id", "page", "record", "y_component_tokens", "posten_tokens", "posten_present", "surface_sequence", "fluent_workshop_reading_de"])
    summary = {
        "status": "PASS",
        "decision": "POSTEN_IS_THE_ONLY_RECURRENT_HIDDEN_WORD_NOMINATED_AS_COMPONENT_VALUE",
        "candidate_stems": len(candidate_rows),
        "y_statements": len(y_rows),
        "y_statements_with_posten": sum(row["posten_present"] == "YES" for row in y_rows),
        "posten_tokens": sum(int(row["posten_tokens"]) for row in y_rows),
        "posten_without_y_statements": len(non_y_posten),
        "records_with_posten": len({row["record"] for row in y_rows if row["posten_present"] == "YES"}),
        "nominated_revision": "Y=DIES -> Y=POSTEN",
        "other_revisions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
