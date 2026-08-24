#!/usr/bin/env python3
"""Project all eleven record openings onto the thirteen-root pocket core."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P680 = ROOT / "experiments/yolo/sidequest_semantic_owner_expanded_compact_edition_six_hundred_eightieth"
P688 = ROOT / "experiments/yolo/sidequest_semantic_all_record_core_six_hundred_eighty_eighth"
RECORDS = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PROMPTS = {
    "H1": "DIES kurz; Gang und Ansatz aus der Quelle; danach DIES fortsetzen, ansetzen und nach MASS weiterfuehren.",
    "H2": "DIES am Ansatz; denselben Gang nach MASS fortsetzen und DIES verfuegbar lassen.",
    "H3": "Am ZIEL fortsetzen; DIES nach MASS lang; den Gang schliessen.",
    "H4": "MASS ansetzen; DIES zudosieren; den Gang schliessen.",
    "H5": "Ansatz am ZIEL; DIES nach MASS fortsetzen, danach den Ansatz ansetzen und zum ZIEL fuehren.",
    "B1": "Kurz ansetzen; SCHLUSS.",
    "B2": "SCHLUSS; die Fachhandlung wird aus dem Spezialkasten eingesetzt.",
    "B3": "Lang; SCHLUSS; die Fachhandlung wird aus dem Spezialkasten eingesetzt.",
    "B4": "Lang ansetzen; SCHLUSS.",
    "B5": "DANACH; SCHLUSS; die Fachhandlung wird aus dem Spezialkasten eingesetzt.",
    "B6": "DIES lang und kurz fuehren; am ZIEL nach MASS fortsetzen und DIES beim Ansatz halten.",
}

ARCHETYPE = {
    "H1": "HERBAL_OWNER_CONTINUATION", "H2": "HERBAL_OWNER_CONTINUATION",
    "H3": "HERBAL_MEASURE_CLOSE", "H4": "HERBAL_MEASURE_CLOSE",
    "H5": "HERBAL_OWNER_CONTINUATION", "B1": "BIO_GRADED_SET_CLOSE",
    "B2": "BIO_SPECIALIST_CLOSE", "B3": "BIO_SPECIALIST_CLOSE",
    "B4": "BIO_GRADED_SET_CLOSE", "B5": "BIO_SPECIALIST_CLOSE",
    "B6": "BIO_GRADED_TARGET_SEQUENCE",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}
    ecology = read(P688 / "SIX_HUNDRED_EIGHTY_EIGHTH_39_ROOT_ECOLOGY.tsv")
    pocket = {row["component"] for row in ecology if int(row["records_used"]) >= 8}
    owners = {row["record"]: row for row in read(P680 / "SIX_HUNDRED_EIGHTIETH_11_CONTINUOUS_OWNER_RECORDS.tsv")}
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_record[event["record"]].append(event)

    projection_rows = []
    prompt_rows = []
    for record in RECORDS:
        first_sid = by_record[record][0]["statement_id"]
        opening = [event for event in by_record[record] if event["statement_id"] == first_sid]
        core_tokens = []
        specialist_tokens = []
        for event in opening:
            event_core = [token for token in event["component_recipe"].split("+") if token in pocket]
            event_special = [token for token in event["component_recipe"].split("+") if token not in pocket]
            core_tokens.extend(event_core)
            specialist_tokens.extend(event_special)
            projection_rows.append({
                "record": record,
                "page": event["page"],
                "opening_statement": first_sid,
                "event_id": event["event_id"],
                "surface": event["surface"],
                "full_recipe": event["component_recipe"],
                "pocket_core_projection": "+".join(event_core) if event_core else "OWNER_ONLY_SLOT",
                "specialist_residual": "+".join(event_special) if event_special else "NONE",
                "full_reading_de": event["compact_atomic_reading_de"],
            })
        prompt_rows.append({
            "record": record,
            "page": opening[0]["page"],
            "opening_statement": first_sid,
            "opening_events": len(opening),
            "owner_de": owners[record]["owners_in_order"].split(" -> ")[0],
            "prompt_archetype": ARCHETYPE[record],
            "pocket_core_tokens": " ".join(core_tokens),
            "pocket_core_token_count": len(core_tokens),
            "pocket_core_values_de": " · ".join(roots[token]["compact_table_value_de"] for token in core_tokens),
            "specialist_tokens": " ".join(specialist_tokens) if specialist_tokens else "NONE",
            "specialist_token_count": len(specialist_tokens),
            "simple_form_prompt_de": PROMPTS[record],
            "surface_sequence": " ".join(event["surface"] for event in opening),
        })

    archetype_rows = []
    for archetype in dict.fromkeys(ARCHETYPE.values()):
        members = [row for row in prompt_rows if row["prompt_archetype"] == archetype]
        archetype_rows.append({
            "archetype": archetype,
            "records": "|".join(str(row["record"]) for row in members),
            "instances": len(members),
            "teaching_formula_de": members[0]["simple_form_prompt_de"],
        })

    specialist_counts = Counter(token for row in prompt_rows for token in str(row["specialist_tokens"]).split() if token != "NONE")
    specialist_rows = [{
        "component": component,
        "value_de": roots[component]["compact_table_value_de"],
        "opening_token_uses": count,
        "records": "|".join(record for record in RECORDS if component in str(next(row for row in prompt_rows if row["record"] == record)["specialist_tokens"]).split()),
        "insertion_rule_de": "Nach dem pocket-core Prompt an der belegten Position einsetzen; keine neue Grundform erfinden.",
    } for component, count in sorted(specialist_counts.items(), key=lambda item: (-item[1], item[0]))]

    write("SIX_HUNDRED_EIGHTY_NINTH_11_RECORD_OPENING_PROMPTS.tsv", prompt_rows)
    write("SIX_HUNDRED_EIGHTY_NINTH_54_OPENING_EVENT_PROJECTIONS.tsv", projection_rows)
    write("SIX_HUNDRED_EIGHTY_NINTH_OPENING_ARCHETYPES.tsv", archetype_rows)
    write("SIX_HUNDRED_EIGHTY_NINTH_SPECIALIST_INSERTIONS.tsv", specialist_rows)

    summary = {
        "status": "PASS",
        "records": len(prompt_rows),
        "opening_events": len(projection_rows),
        "opening_component_tokens": sum(int(row["pocket_core_token_count"]) + int(row["specialist_token_count"]) for row in prompt_rows),
        "pocket_core_tokens": sum(int(row["pocket_core_token_count"]) for row in prompt_rows),
        "specialist_tokens": sum(int(row["specialist_token_count"]) for row in prompt_rows),
        "pocket_core_size": len(pocket),
        "opening_archetypes": len(archetype_rows),
        "specialist_components_in_openings": len(specialist_rows),
    }
    (HERE / "SIX_HUNDRED_EIGHTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
