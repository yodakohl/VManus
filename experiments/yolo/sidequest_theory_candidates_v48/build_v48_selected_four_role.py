#!/usr/bin/env python3
"""Select only the bounded V48 additions surviving the four-role comparison."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "sidequest_theory_candidates_v47"
FIELDS = OUT.parent / "sidequest_theory_candidates_v42/V42_R2_135_FIELD_MEDICAL_EDITION.tsv"

SELECTED = {
    "chey": ("AUSGEWÄHLTEN MATERIALANTEIL AUFNEHMEN", "ACTIVE_EXPLORATORY_CONTENT_CORE"),
    "chor": ("PFLANZENMATERIAL ZEITGEBUNDEN BESCHAFFEN", "ACTIVE_EXPLORATORY_CONTENT_CORE"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_cards = read(BASE / "V47_STRICT_173_CARD_DICTIONARY.tsv")
    base_events = read(BASE / "V47_STRICT_381_EVENT_INTERLINEAR.tsv")
    field_source = read(FIELDS)
    cards = []
    by_tuple = {}
    for row in base_cards:
        new = dict(row)
        host = row["page_host"]
        if host in SELECTED:
            value, status = SELECTED[host]
            prefix = f"OPAQUE HOST {host.upper()}=UNBEKANNT"
            assert new["strict_literal_composition_German"].startswith(prefix)
            new["host_or_card_value_German"] = value
            new["analysis_status"] = status
            new["strict_literal_composition_German"] = new["strict_literal_composition_German"].replace(
                prefix, f"HOST {host.upper()}={value}", 1
            )
        cards.append(new)
        by_tuple[new["joint_tuple_id"]] = new
    write(OUT / "V48_SELECTED_173_CARD_DICTIONARY.tsv", cards)

    events = []
    for row in base_events:
        new = dict(row)
        new["strict_literal_composition_German"] = by_tuple[row["joint_tuple_id"]]["strict_literal_composition_German"]
        events.append(new)
    write(OUT / "V48_SELECTED_381_EVENT_INTERLINEAR.tsv", events)

    by_locus = defaultdict(list)
    for row in events:
        by_locus[row["locus"]].append(row)
    cursors = defaultdict(int)
    fields = []
    for source in field_source:
        locus = source["locus"]
        n = int(source["card_count"])
        start = cursors[locus]
        members = by_locus[locus][start : start + n]
        cursors[locus] += n
        assert [r["surface"] for r in members] == source["visible_field"].split()
        fields.append({
            "page": source["page"],
            "record": source["record_ordinal"],
            "locus": locus,
            "field_ordinal": source["source_field_ordinal"],
            "event_count": n,
            "surface_sequence": source["visible_field"],
            "strict_literal_sequence_German": " | ".join(r["strict_literal_composition_German"] for r in members),
            "fluent_local_creative_translation_German": "; ".join(r["fluent_local_creative_expansion_German"] for r in members),
        })
    write(OUT / "V48_SELECTED_135_FIELD_TRANSLATION.tsv", fields)

    values = defaultdict(set)
    for row in cards:
        values[row["page_host"]].add(row["host_or_card_value_German"])
    validation = {
        "schema": "SIDEQUEST_V48_SELECTED_FOUR_ROLE_COMPONENT_EXTENSION_V1",
        "status": "PASS",
        "selection": {
            "active_exploratory_additions": ["chey", "chor"],
            "no_new_formal_axis_promoted": True,
            "all_other_v48_candidates_rejected_or_held": ["ch", "chy", "olk", "rshe", "d", "k", "o", "chol", "lched"],
        },
        "counts": {
            "cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "cards_under_v47_or_selected_host_axes": sum(r["analysis_status"] in {
                "FORMAL_COMPOSITIONAL_AXIS", "PROVISIONAL_CONTENT_CORE", "LOW_CONFIDENCE_RELATION_AXIS",
                "LOW_CONFIDENCE_STATE_AXIS", "LOW_CONFIDENCE_CONNECTION_AXIS", "ACTIVE_EXPLORATORY_CONTENT_CORE"
            } for r in cards),
            "selected_new_cards": sum(r["analysis_status"] == "ACTIVE_EXPLORATORY_CONTENT_CORE" for r in cards),
            "opaque_whole_cards": sum(r["analysis_status"] == "OPAQUE_WHOLE_CARD" for r in cards),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "same_host_same_value": all(len(v) == 1 for v in values.values()),
            "chey_two_cards_one_value": sum(r["page_host"] == "chey" for r in cards) == 2 and len(values["chey"]) == 1,
            "chor_two_cards_one_value": sum(r["page_host"] == "chor" for r in cards) == 2 and len(values["chor"]) == 1,
            "ch_chy_che_olk_y_remain_unknown": all(r["host_or_card_value_German"] == "UNBEKANNT" for r in cards if r["page_host"] in {"ch", "chy", "che", "olk", "y"}),
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V48_SELECTED_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
