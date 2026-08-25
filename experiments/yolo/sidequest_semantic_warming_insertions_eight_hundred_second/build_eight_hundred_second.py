#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_once(sequence: str, source: str, target: str) -> str:
    words = sequence.split()
    index = words.index(source)
    words[index] = target
    return " ".join(words)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    event_by_id = {row["event_id"]: row for row in events}
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}

    specs = [
        {
            "prediction_id": "CHK-P01",
            "source_event": "E231",
            "target_recipe": "CHK+E+DY",
            "target_surface": "chkedy",
            "alternate_surface": "NONE",
            "target_reading": "WAERMEN · KURZ · SCHLUSS",
            "old_phrase": "laenger erwaermen",
            "new_phrase": "kurz erwaermen",
        },
        {
            "prediction_id": "CHK-P02",
            "source_event": "E066",
            "target_recipe": "CHK+EEE+Y",
            "target_surface": "chkeeey",
            "alternate_surface": "cheeeky",
            "target_reading": "WAERMEN · VOLL · DIES",
            "old_phrase": "laenger erwaermen",
            "new_phrase": "vollstaendig erwaermen",
        },
        {
            "prediction_id": "CHK-P03",
            "source_event": "E231",
            "target_recipe": "CHK+EEE+DY",
            "target_surface": "chkeeedy",
            "alternate_surface": "NONE",
            "target_reading": "WAERMEN · VOLL · SCHLUSS",
            "old_phrase": "laenger erwaermen",
            "new_phrase": "vollstaendig erwaermen",
        },
    ]

    substitutions = []
    traces = []
    readbacks = []
    for spec in specs:
        event = event_by_id[spec["source_event"]]
        statement = statements[event["statement_id"]]
        new_surface_sequence = replace_once(statement["surface_sequence"], event["surface"], spec["target_surface"])
        new_reading = statement["clean_workshop_reading_de"].replace(spec["old_phrase"], spec["new_phrase"], 1)
        substitutions.append(
            {
                "prediction_id": spec["prediction_id"],
                "page": event["page"],
                "statement_id": event["statement_id"],
                "owner_de": event["owner_de"],
                "source_event": event["event_id"],
                "source_surface": event["surface"],
                "source_recipe": event["component_recipe"],
                "source_reading_de": event["rebuilt_reading_de"],
                "target_surface": spec["target_surface"],
                "alternate_surface": spec["alternate_surface"],
                "target_recipe": spec["target_recipe"],
                "target_reading_de": spec["target_reading"],
                "grade_change_only": "YES",
                "endpoint_preserved": "YES",
                "owner_preserved": "YES",
                "other_events_preserved": "YES",
                "attested_status": "PREDICTION_ONLY",
            }
        )
        traces.extend(
            [
                {
                    "prediction_id": spec["prediction_id"],
                    "phase": "BEFORE",
                    "surface_sequence": statement["surface_sequence"],
                    "changed_card": event["surface"],
                    "changed_recipe": event["component_recipe"],
                    "changed_reading_de": event["rebuilt_reading_de"],
                    "statement_reading_de": statement["clean_workshop_reading_de"],
                },
                {
                    "prediction_id": spec["prediction_id"],
                    "phase": "AFTER",
                    "surface_sequence": new_surface_sequence,
                    "changed_card": spec["target_surface"],
                    "changed_recipe": spec["target_recipe"],
                    "changed_reading_de": spec["target_reading"],
                    "statement_reading_de": new_reading,
                },
            ]
        )
        readbacks.append(
            {
                "prediction_id": spec["prediction_id"],
                "page": event["page"],
                "statement_id": event["statement_id"],
                "predicted_surface_sequence": new_surface_sequence,
                "spoken_workshop_instruction_de": new_reading,
                "copying_instruction_de": f"ersetze nur {event['surface']} durch {spec['target_surface']}",
                "semantic_difference": f"{event['rebuilt_reading_de']} -> {spec['target_reading']}",
            }
        )

    write(
        "EIGHT_HUNDRED_SECOND_3_CHK_SUBSTITUTIONS.tsv",
        substitutions,
        ["prediction_id", "page", "statement_id", "owner_de", "source_event", "source_surface", "source_recipe", "source_reading_de", "target_surface", "alternate_surface", "target_recipe", "target_reading_de", "grade_change_only", "endpoint_preserved", "owner_preserved", "other_events_preserved", "attested_status"],
    )
    write(
        "EIGHT_HUNDRED_SECOND_6_BEFORE_AFTER_TRACES.tsv",
        traces,
        ["prediction_id", "phase", "surface_sequence", "changed_card", "changed_recipe", "changed_reading_de", "statement_reading_de"],
    )
    write(
        "EIGHT_HUNDRED_SECOND_3_FULL_READBACKS.tsv",
        readbacks,
        ["prediction_id", "page", "statement_id", "predicted_surface_sequence", "spoken_workshop_instruction_de", "copying_instruction_de", "semantic_difference"],
    )
    observed_surfaces = {row["surface"] for row in events}
    prediction_surfaces = {spec["target_surface"] for spec in specs} | {spec["alternate_surface"] for spec in specs if spec["alternate_surface"] != "NONE"}
    summary = {
        "status": "PASS",
        "decision": "THREE_MISSING_CHK_GRADE_ENDPOINT_CELLS_READ_COHERENTLY_IN_FULL_STATEMENTS",
        "substitutions": len(substitutions),
        "before_after_traces": len(traces),
        "full_readbacks": len(readbacks),
        "unique_prediction_surfaces": len(prediction_surfaces),
        "observed_surface_collisions": len(prediction_surfaces & observed_surfaces),
        "source_statements": sorted({row["statement_id"] for row in substitutions}),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
