#!/usr/bin/env python3
"""Project every prose statement onto pocket-core and specialist components."""

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


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}
    ecology = read(P688 / "SIX_HUNDRED_EIGHTY_EIGHTH_39_ROOT_ECOLOGY.tsv")
    pocket = {row["component"] for row in ecology if int(row["records_used"]) >= 8}
    owner_rows = {row["statement_id"]: row for row in read(P680 / "SIX_HUNDRED_EIGHTIETH_116_COMPACT_OWNER_STATEMENTS.tsv")}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    event_rows = []
    statement_rows = []
    for sid, rows in by_statement.items():
        core_tokens: list[str] = []
        specialist_tokens: list[str] = []
        for event in rows:
            tokens = event["component_recipe"].split("+")
            event_core = [token for token in tokens if token in pocket]
            event_special = [token for token in tokens if token not in pocket]
            core_tokens.extend(event_core)
            specialist_tokens.extend(event_special)
            event_rows.append({
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": sid,
                "surface": event["surface"],
                "full_recipe": event["component_recipe"],
                "pocket_core_recipe": "+".join(event_core) if event_core else "NONE",
                "specialist_recipe": "+".join(event_special) if event_special else "NONE",
                "event_class": "CORE_CARD" if not event_special else "MIXED_OR_SPECIALIST_CARD",
                "full_reading_de": event["compact_atomic_reading_de"],
            })
        distinct_specialists = list(dict.fromkeys(specialist_tokens))
        if not distinct_specialists:
            statement_class = "POCKET_ONLY"
            plan = "Taschenkern allein diktieren und Karte nachschlagen."
        elif len(distinct_specialists) == 1:
            statement_class = "ONE_SPECIALIST_TYPE"
            plan = f"Taschenkern diktieren; Spezialkarte {distinct_specialists[0]} an den belegten Stellen einsetzen."
        else:
            statement_class = "MULTI_SPECIALIST"
            plan = f"Taschenkern diktieren; lokale Spezialfolge {'+'.join(distinct_specialists)} positionsgetreu einsetzen."
        statement_rows.append({
            "statement_id": sid,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "events": len(rows),
            "component_tokens": len(core_tokens) + len(specialist_tokens),
            "pocket_core_tokens": len(core_tokens),
            "specialist_tokens": len(specialist_tokens),
            "distinct_specialist_types": len(distinct_specialists),
            "statement_class": statement_class,
            "pocket_core_sequence": " ".join(core_tokens) if core_tokens else "NONE",
            "specialist_sequence": " ".join(specialist_tokens) if specialist_tokens else "NONE",
            "specialist_values_de": " · ".join(roots[token]["compact_table_value_de"] for token in specialist_tokens) if specialist_tokens else "NONE",
            "dictation_plan_de": plan,
            "owner_noun_de": owner_rows[sid]["owner_noun_de"],
            "surface_sequence": " ".join(row["surface"] for row in rows),
            "complete_owner_reading_de": owner_rows[sid]["compact_owner_reading_de"],
        })

    record_rows = []
    for record in RECORDS:
        statements = [row for row in statement_rows if row["record"] == record]
        record_rows.append({
            "record": record,
            "page": statements[0]["page"],
            "statements": len(statements),
            "events": sum(int(row["events"]) for row in statements),
            "component_tokens": sum(int(row["component_tokens"]) for row in statements),
            "pocket_core_tokens": sum(int(row["pocket_core_tokens"]) for row in statements),
            "specialist_tokens": sum(int(row["specialist_tokens"]) for row in statements),
            "pocket_only_statements": sum(row["statement_class"] == "POCKET_ONLY" for row in statements),
            "one_specialist_statements": sum(row["statement_class"] == "ONE_SPECIALIST_TYPE" for row in statements),
            "multi_specialist_statements": sum(row["statement_class"] == "MULTI_SPECIALIST" for row in statements),
        })

    specialist_counts = Counter(token for row in statement_rows for token in str(row["specialist_sequence"]).split() if token != "NONE")
    specialist_rows = [{
        "component": component,
        "value_de": roots[component]["compact_table_value_de"],
        "token_uses": count,
        "statements": sum(component in str(row["specialist_sequence"]).split() for row in statement_rows),
        "records": "|".join(record for record in RECORDS if any(component in str(row["specialist_sequence"]).split() for row in statement_rows if row["record"] == record)),
    } for component, count in sorted(specialist_counts.items(), key=lambda item: (-item[1], item[0]))]

    write("SIX_HUNDRED_NINETIETH_116_STATEMENT_CORE_PROJECTION.tsv", statement_rows)
    write("SIX_HUNDRED_NINETIETH_381_EVENT_CORE_PROJECTION.tsv", event_rows)
    write("SIX_HUNDRED_NINETIETH_11_RECORD_CORE_BURDEN.tsv", record_rows)
    write("SIX_HUNDRED_NINETIETH_26_SPECIALIST_USAGE.tsv", specialist_rows)

    class_counts = Counter(row["statement_class"] for row in statement_rows)
    event_classes = Counter(row["event_class"] for row in event_rows)
    summary = {
        "status": "PASS",
        "statements": len(statement_rows),
        "events": len(event_rows),
        "component_tokens": sum(int(row["component_tokens"]) for row in statement_rows),
        "pocket_core_tokens": sum(int(row["pocket_core_tokens"]) for row in statement_rows),
        "specialist_tokens": sum(int(row["specialist_tokens"]) for row in statement_rows),
        "statement_classes": dict(class_counts),
        "event_classes": dict(event_classes),
        "specialist_components_used": len(specialist_rows),
        "decision": "POCKET_CORE_IS_DOMINANT_SCAFFOLD_BUT_SPECIALIST_TOOLS_REMAIN_ESSENTIAL",
    }
    (HERE / "SIX_HUNDRED_NINETIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
