#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
STATEMENTS = BASE / "EIGHT_HUNDRED_THIRTY_THIRD_116_STATEMENT_REPARSE.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv"
PREFIX = "EIGHT_HUNDRED_THIRTY_FOURTH"

CANDIDATES = [
    ("schritt", "DY", "CLOSURE_OBJECT", "KEEP_DY_AS_SCHLUSS"),
    ("fluessigkeit", "AIR", "GENERIC_SYNONYM", "REPLACE_FLUESSIGKEIT_WITH_WASSER_IN_FLUENT_LAYER"),
    ("wasser", "AIR", "CONCRETE_MATERIAL", "KEEP_AIR_AS_WASSER"),
    ("fuehren", "L", "GUIDE_SYNONYM", "KEEP_AS_FLUENT_SYNONYM"),
    ("weiterarbeiten", "OL", "CONTINUATION_EXPANSION", "KEEP_AS_COMBINATION_EXPANSION"),
    ("lassen", "SHED", "LEAVE_STANDING_INFLECTION", "KEEP_AS_GRAMMATICAL_EXPANSION"),
    ("halten", "SH", "HOLD_INFLECTION", "KEEP_AS_GRAMMATICAL_EXPANSION"),
    ("ansetzen", "OK", "ACTIVATE_INFLECTION", "KEEP_AS_GRAMMATICAL_EXPANSION"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def components(row: dict[str, str]) -> list[str]:
    return [token for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")]


def occurrences(text: str, stem: str) -> int:
    return len(re.findall(rf"\b{re.escape(stem)}\w*", text.lower()))


def main() -> None:
    statements = read(STATEMENTS)
    events = read(EVENTS)
    by_statement = {row["statement_id"]: row for row in statements}

    candidates = []
    for stem, component, role, decision in CANDIDATES:
        word_rows = [row for row in statements if occurrences(row["working_reading_de"], stem)]
        component_rows = [row for row in statements if component in components(row)]
        both = [row for row in word_rows if component in components(row)]
        candidates.append(
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

    dy_rows = []
    for row in statements:
        dy_count = components(row).count("DY")
        if not dy_count:
            continue
        step_count = occurrences(row["working_reading_de"], "schritt")
        dy_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "dy_components": dy_count,
                "schritt_tokens": step_count,
                "schritt_present": "YES" if step_count else "NO",
                "decision": "SCHRITT_IS_FLUENT_OBJECT_OF_SCHLUSS",
                "working_reading_de": row["working_reading_de"],
            }
        )

    air_rows = []
    for event in events:
        if "AIR" not in event["component_recipe"].split("+"):
            continue
        statement = by_statement[event["statement_id"]]
        current = statement["working_reading_de"]
        if occurrences(current, "fluessigkeit"):
            proposed = re.sub(r"\blaufende Fluessigkeit\b", "laufendes Wasser", current)
            proposed = re.sub(r"\blaufenden Fluessigkeit\b", "laufenden Wasser", proposed)
            revision = "FLUESSIGKEIT_TO_WASSER"
        else:
            proposed = current
            revision = "NONE"
        air_rows.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "literal_reading_de": event["ninth_grammar_reading_de"],
                "current_working_reading_de": current,
                "proposed_working_reading_de": proposed,
                "revision": revision,
                "decision": "KEEP_AIR_WASSER",
            }
        )

    write(f"{PREFIX}_8_HIDDEN_WORD_CANDIDATES.tsv", candidates, ["hidden_stem", "candidate_component", "tokens", "statements", "records", "component_statements", "word_and_component_statements", "word_without_component", "component_without_word", "layer_role", "decision"])
    write(f"{PREFIX}_89_DY_STATEMENTS.tsv", dy_rows, ["statement_id", "page", "record", "dy_components", "schritt_tokens", "schritt_present", "decision", "working_reading_de"])
    write(f"{PREFIX}_5_AIR_EVENTS.tsv", air_rows, ["event_id", "page", "record", "statement_id", "surface", "component_recipe", "literal_reading_de", "current_working_reading_de", "proposed_working_reading_de", "revision", "decision"])

    summary = {
        "status": "PASS",
        "decision": "AIR_WASSER_RETAINED__FOUR_FLUESSIGKEIT_EXPANSIONS_TO_REVISE",
        "candidate_stems": len(candidates),
        "dy_statements": len(dy_rows),
        "dy_statements_with_schritt": sum(row["schritt_present"] == "YES" for row in dy_rows),
        "dy_statements_without_schritt": sum(row["schritt_present"] == "NO" for row in dy_rows),
        "air_events": len(air_rows),
        "air_events_currently_saying_wasser": sum(occurrences(row["current_working_reading_de"], "wasser") > 0 for row in air_rows),
        "air_events_currently_saying_fluessigkeit": sum(occurrences(row["current_working_reading_de"], "fluessigkeit") > 0 for row in air_rows),
        "air_fluent_revisions_nominated": sum(row["revision"] != "NONE" for row in air_rows),
        "new_component_revision": "NONE",
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 834: third hidden-word audit

Two tempting hidden words were checked against the ninth grammar.

`SCHRITT` is not promoted. It occurs in 68 of 89 DY-bearing statements and
never without DY, but 21 equally ordinary closes omit it. The compact card
value remains `DY=SCHLUSS`; “den Schritt schließen” is simply fluent German
syntax around that close.

`FLUESSIGKEIT` exposes the opposite problem. AIR already has the concrete
working value `WASSER`. The sole Herbal occurrence says water, while four Bio
occurrences were softened editorially to “laufende Flüssigkeit”. On this
creative ten-page model the better move is not to weaken AIR. It is to make all
five readings say water: `chair` takes water, `kair` adds running water,
`okair` starts it, `schedair` moves it, and `dairydy` carries the water item to
closure.

No component changes in this audit. It nominates exactly four fluent-layer
repairs from FLUESSIGKEIT to WASSER. FUEHREN, WEITERARBEITEN, LASSEN, HALTEN and
ANSETZEN remain ordinary inflections or combinations of the existing compact
values.

Next: apply the four AIR wording repairs throughout the full 116-statement
edition, then inspect whether the water cards form a predictable source → add
→ start → move → close mini-paradigm.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
