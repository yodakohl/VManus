#!/usr/bin/env python3
"""Build the selected, stem-consistent ten-page sidequest edition.

This is a creative dictionary revision.  It merges the independently written
OK, CHD~CHED and E-grade paradigm tables into the already selected 173-card /
381-event working edition.  It does not read manuscript or sealed data.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_stem_search"

DICT_IN = SOURCE / "SELECTED_173_COMPOSITIONAL_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_CONCRETE_INTERLINEAR.tsv"
OK_IN = HERE / "OK_PARADIGM.tsv"
CHED_IN = HERE / "CHED_PARADIGM.tsv"
E_IN = HERE / "E_GRADE_PARADIGM.tsv"

DICT_OUT = HERE / "SELECTED_173_STEM_CONSISTENT_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_STEM_CONSISTENT_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_STEM_CONSISTENT_STATEMENTS.tsv"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"

E_SELECTED_STATUSES = {
    "SELECTED_PRODUCTIVE",
    "SELECTED_PRODUCTIVE_WEAK_TOP_GRADE",
    "SELECTED_DERIVED_PREDICTION",
    "SELECTED_PROVISIONAL_COMPOSITION",
    "TRANSFER_PROVISIONAL",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def ok_overrides() -> dict[str, dict[str, str]]:
    overrides: dict[str, dict[str, str]] = {}
    for row in read_tsv(OK_IN):
        joint = row["joint_tuple_id"]
        overrides[joint] = {
            "semantic_segmentation": row["selected_parse"],
            "stable_concrete_nucleus_de": (
                "OK=in den laufenden Arbeitsgang setzen; "
                + row["argument_contribution"]
            ),
            "concrete_word_reading_de": row["new_default_reading_de"],
            "reading_type": "PARADIGM_OK__" + row["composition_status"],
            "revision_source": "OK_PARADIGM",
            "revision_strength": row["composition_status"],
            "revision_note": row["old_gloss_revision"],
        }
    return overrides


def ched_overrides() -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(CHED_IN):
        grouped[row["joint_tuple_id"]].append(row)

    overrides: dict[str, dict[str, str]] = {}
    for joint, rows in grouped.items():
        glosses = uniq([row["short_default_gloss_de"] for row in rows])
        if len(glosses) != 1:
            raise ValueError(f"Conflicting CHED glosses for {joint}: {glosses}")
        parses = uniq([row["selected_parse"] for row in rows])
        strengths = uniq([row["confidence"] for row in rows])
        hulls = uniq([row["left_hull_value_de"] for row in rows])
        arguments = uniq([row["right_argument_or_terminal"] for row in rows])
        overrides[joint] = {
            "semantic_segmentation": " / ".join(parses),
            "stable_concrete_nucleus_de": (
                "CHD~CHED=umsetzen/in einen Arbeitsgang führen; "
                + "; ".join(uniq(hulls + arguments))
            ),
            "concrete_word_reading_de": glosses[0],
            "reading_type": "PARADIGM_CHD_CHED",
            "revision_source": "CHED_PARADIGM",
            "revision_strength": " / ".join(strengths),
            "revision_note": " / ".join(
                uniq([row["counterexample_or_limit"] for row in rows])
            ),
        }
    return overrides


def e_overrides() -> dict[str, dict[str, str]]:
    overrides: dict[str, dict[str, str]] = {}
    for row in read_tsv(E_IN):
        if row["status"] not in E_SELECTED_STATUSES:
            continue
        joint = row["joint_tuple_id"]
        candidate = {
            "semantic_segmentation": row["parse"],
            "stable_concrete_nucleus_de": (
                f"E-Grad={row['e_grade_value']}; Zustand={row['y_dy_value']}"
            ),
            "concrete_word_reading_de": row["minimal_working_gloss_de"],
            "reading_type": "PARADIGM_E_GRADE__" + row["status"],
            "revision_source": "E_GRADE_PARADIGM",
            "revision_strength": row["status"],
            "revision_note": row["evidence_note"],
        }
        if joint in overrides and overrides[joint] != candidate:
            raise ValueError(f"Conflicting selected E-grade rows for {joint}")
        overrides[joint] = candidate
    return overrides


def build_overrides() -> dict[str, dict[str, str]]:
    # Later layers are more specific: CHED resolves ambiguous OK+CHD cards;
    # the selected E grid resolves particular OK/OT contact grades.
    overrides = ok_overrides()
    overrides.update(ched_overrides())
    overrides.update(e_overrides())
    return overrides


def sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    overrides = build_overrides()

    dict_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(overrides) - set(dict_by_id))
    if missing:
        raise ValueError(f"Paradigm IDs absent from selected dictionary: {missing}")

    dict_fields = list(dictionary[0]) + [
        "previous_semantic_segmentation",
        "previous_stable_concrete_nucleus_de",
        "previous_concrete_word_reading_de",
        "paradigm_revision",
        "revision_strength",
        "revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source_row in dictionary:
        row = dict(source_row)
        override = overrides.get(row["joint_tuple_id"])
        if override:
            row["previous_semantic_segmentation"] = row["semantic_segmentation"]
            row["previous_stable_concrete_nucleus_de"] = row[
                "stable_concrete_nucleus_de"
            ]
            row["previous_concrete_word_reading_de"] = row[
                "concrete_word_reading_de"
            ]
            for field in (
                "semantic_segmentation",
                "stable_concrete_nucleus_de",
                "concrete_word_reading_de",
                "reading_type",
            ):
                row[field] = override[field]
            row["local_expansion_examples_de"] = (
                "Stammkonsistente Werkstattlektüre: "
                + override["concrete_word_reading_de"]
            )
            row["variation_note"] = (
                f"{source_row['variation_note']}; Revision: "
                f"{override['revision_note']}"
            )
            row["paradigm_revision"] = override["revision_source"]
            row["revision_strength"] = override["revision_strength"]
            row["revision_note"] = override["revision_note"]
        else:
            row["previous_semantic_segmentation"] = ""
            row["previous_stable_concrete_nucleus_de"] = ""
            row["previous_concrete_word_reading_de"] = ""
            row["paradigm_revision"] = "UNCHANGED"
            row["revision_strength"] = "UNCHANGED"
            row["revision_note"] = "NOT_APPLICABLE"
        revised_dictionary.append(row)

    revised_by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}
    event_fields = list(events[0]) + [
        "previous_semantic_segmentation",
        "previous_stable_concrete_nucleus_de",
        "previous_concrete_word_reading_de",
        "previous_contextual_event_reading_de",
        "paradigm_revision",
        "revision_strength",
    ]
    revised_events: list[dict[str, str]] = []
    for source_row in events:
        row = dict(source_row)
        revised_card = revised_by_id[row["joint_tuple_id"]]
        override = overrides.get(row["joint_tuple_id"])
        if override:
            row["previous_semantic_segmentation"] = row["semantic_segmentation"]
            row["previous_stable_concrete_nucleus_de"] = row[
                "stable_concrete_nucleus_de"
            ]
            row["previous_concrete_word_reading_de"] = row[
                "concrete_word_reading_de"
            ]
            row["previous_contextual_event_reading_de"] = row[
                "contextual_event_reading_de"
            ]
            row["semantic_segmentation"] = revised_card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = revised_card[
                "stable_concrete_nucleus_de"
            ]
            row["concrete_word_reading_de"] = revised_card[
                "concrete_word_reading_de"
            ]
            row["contextual_event_reading_de"] = sentence_case(
                revised_card["concrete_word_reading_de"]
            )
            row["paradigm_revision"] = override["revision_source"]
            row["revision_strength"] = override["revision_strength"]
        else:
            row["previous_semantic_segmentation"] = ""
            row["previous_stable_concrete_nucleus_de"] = ""
            row["previous_concrete_word_reading_de"] = ""
            row["previous_contextual_event_reading_de"] = ""
            row["paradigm_revision"] = "UNCHANGED"
            row["revision_strength"] = "UNCHANGED"
        revised_events.append(row)

    statement_fields = [
        "statement_id",
        "record_unit_id",
        "page",
        "loci",
        "field_ids",
        "event_ids",
        "event_count",
        "revised_event_count",
        "surface_sequence",
        "stem_consistent_card_sequence_de",
        "compact_stem_consistent_reading_de",
        "physical_line_note",
    ]
    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statements: list[dict[str, str]] = []
    for statement_id, rows in grouped.items():
        changed = sum(row["paradigm_revision"] != "UNCHANGED" for row in rows)
        glosses = [row["concrete_word_reading_de"] for row in rows]
        statements.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(uniq([row["field_id"] for row in rows])),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "revised_event_count": str(changed),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "stem_consistent_card_sequence_de": " · ".join(glosses),
                "compact_stem_consistent_reading_de": sentence_case(
                    "; ".join(glosses)
                ),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)

    changed_cards = [
        row for row in revised_dictionary if row["paradigm_revision"] != "UNCHANGED"
    ]
    changed_events = [
        row for row in revised_events if row["paradigm_revision"] != "UNCHANGED"
    ]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_PARADIGM_CLOSURE_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "changed_cards": len(changed_cards),
        "unchanged_cards": len(revised_dictionary) - len(changed_cards),
        "changed_events": len(changed_events),
        "unchanged_events": len(revised_events) - len(changed_events),
        "changed_statements": sum(
            int(row["revised_event_count"]) > 0 for row in statements
        ),
        "revision_source_card_counts": {
            source: sum(row["paradigm_revision"] == source for row in changed_cards)
            for source in ("OK_PARADIGM", "CHED_PARADIGM", "E_GRADE_PARADIGM")
        },
        "revision_source_event_counts": {
            source: sum(row["paradigm_revision"] == source for row in changed_events)
            for source in ("OK_PARADIGM", "CHED_PARADIGM", "E_GRADE_PARADIGM")
        },
        "inputs": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (DICT_IN, EVENT_IN, OK_IN, CHED_IN, E_IN)
        },
        "outputs": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (DICT_OUT, EVENT_OUT, STATEMENT_OUT)
        },
    }
    SUMMARY_OUT.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
