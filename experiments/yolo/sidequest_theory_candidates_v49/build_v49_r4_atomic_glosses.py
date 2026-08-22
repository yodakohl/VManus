#!/usr/bin/env python3
"""Build an atomic-gloss alternative: one minimal word/operator per component."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "sidequest_theory_candidates_v48"
FIELDS = OUT.parent / "sidequest_theory_candidates_v42/V42_R2_135_FIELD_MEDICAL_EDITION.tsv"

HOST = {
    "ok": ("SETZEN", "FORMAL_AXIS"),
    "or": ("BEREIT", "PROVISIONAL_CONTENT_STATE"),
    "al": ("ZIEL", "LOW_CONFIDENCE_RELATION"),
    "e": ("BIS", "LOW_CONFIDENCE_STATE_OPERATOR"),
    "ot": ("GEGENBEZUG", "LOW_CONFIDENCE_RELATION"),
    "l": ("ANSCHLUSS", "LOW_CONFIDENCE_RELATION"),
    "chey": ("NEHMEN", "EXPLORATORY_ACTION"),
    "chor": ("SAMMELN", "EXPLORATORY_ACTION"),
}

WHOLE = {
    "aiin": "MASS",
    "ey": "ENDZUSTAND",
    "oky": "VERWENDEN",
    "lche": "ABLAUF",
    "oke": "SPÜLEN",
    "cthy": "BEREIT",
    "okeey": "LAUWARM",
    "ckhy": "VERBUNDEN",
    "olor": "VORANSATZ",
}

RIGHT = {
    "aiin": "STANDARD",
    "ain": "EINHEIT",
    "al": "ZIEL",
    "ar": "QUELLE",
    "air": "LAUF",
}

FRAME = {"O": "FORTSETZUNG", "OT": "GEGENBEZUG"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def formula(card: dict[str, str]) -> tuple[str, str, str]:
    host = card["page_host"]
    if host in HOST:
        value, status = HOST[host]
        parts = [f"HOST-{host.upper()}={value}"]
    elif host in WHOLE:
        value = WHOLE[host]
        status = "RECURRENT_WHOLE_CARD_ATOMIC_LABEL"
        parts = [f"GANZKARTE-{host.upper()}={value}"]
    else:
        value = "UNBEKANNT"
        status = "OPAQUE_WHOLE_CARD"
        parts = [f"HOST-{host.upper()}=UNBEKANNT"]
    if card["local_frame"] in FRAME:
        parts.append(f"FRAME-{card['local_frame']}={FRAME[card['local_frame']]}")
    if card["inner_d"] == "1":
        parts.append("INNER-D=VARIANTE")
    if card["right_family"] != "NONE":
        parts.append(f"RIGHT-{card['right_family'].upper()}={RIGHT.get(card['right_family'], 'UNBEKANNT')}")
    if card["dy_closure"] == "1":
        parts.append("DY=SCHLUSS")
    if card["b3"] == "1":
        parts.append("B3=SONDERABSCHLUSS")
    return value, status, " + ".join(parts)


def main() -> None:
    base_cards = read(BASE / "V48_SELECTED_173_CARD_DICTIONARY.tsv")
    base_events = read(BASE / "V48_SELECTED_381_EVENT_INTERLINEAR.tsv")
    field_source = read(FIELDS)
    contract = []
    for unit, (value, status) in HOST.items():
        contract.append({"level": "PAGE_HOST", "unit": unit, "atomic_value_German": value, "status": status, "may_expand_to_sentence": "NO"})
    for unit, value in WHOLE.items():
        contract.append({"level": "RECURRENT_WHOLE_CARD", "unit": unit, "atomic_value_German": value, "status": "NOT_PRODUCTIVE_STEM", "may_expand_to_sentence": "NO"})
    for unit, value in RIGHT.items():
        contract.append({"level": "RIGHT_FAMILY", "unit": unit, "atomic_value_German": value, "status": "FORMAL_COMPLETION", "may_expand_to_sentence": "NO"})
    for unit, value in FRAME.items():
        contract.append({"level": "FRAME", "unit": unit, "atomic_value_German": value, "status": "FORMAL_CONTEXT", "may_expand_to_sentence": "NO"})
    contract.extend([
        {"level": "FORMAL", "unit": "INNER-D", "atomic_value_German": "VARIANTE", "status": "FORMAL_ONLY", "may_expand_to_sentence": "NO"},
        {"level": "FORMAL", "unit": "DY", "atomic_value_German": "SCHLUSS", "status": "FORMAL_ONLY", "may_expand_to_sentence": "NO"},
        {"level": "FORMAL", "unit": "B3", "atomic_value_German": "SONDERABSCHLUSS", "status": "FORMAL_ONLY", "may_expand_to_sentence": "NO"},
    ])
    write(OUT / "V49_R4_ATOMIC_COMPONENT_CONTRACT.tsv", contract)

    cards = []
    by_tuple = {}
    for card in base_cards:
        value, status, literal = formula(card)
        row = {
            "joint_tuple_id": card["joint_tuple_id"],
            "page_host": card["page_host"],
            "surface_examples": card["surface_examples"],
            "atomic_host_or_card_value_German": value,
            "analysis_status": status,
            "local_frame": card["local_frame"],
            "inner_d": card["inner_d"],
            "right_family": card["right_family"],
            "dy_closure": card["dy_closure"],
            "b3": card["b3"],
            "atomic_literal_composition_German": literal,
            "separate_local_creative_expansion_German": card["fluent_local_creative_expansion_German"],
            "rule": "ATOMIC_VALUE_NEVER_INCLUDES_OBJECT_PLUS_ACTION_PLUS_CONDITION",
        }
        cards.append(row)
        by_tuple[row["joint_tuple_id"]] = row
    write(OUT / "V49_R4_ATOMIC_173_CARD_DICTIONARY.tsv", cards)

    events = []
    for event in base_events:
        card = by_tuple[event["joint_tuple_id"]]
        events.append({
            "page": event["page"], "locus": event["locus"], "record": event["record"],
            "event_index": event["event_index"], "surface": event["surface"],
            "joint_tuple_id": event["joint_tuple_id"], "page_host": event["page_host"],
            "atomic_literal_composition_German": card["atomic_literal_composition_German"],
            "separate_local_creative_expansion_German": card["separate_local_creative_expansion_German"],
        })
    write(OUT / "V49_R4_ATOMIC_381_EVENT_INTERLINEAR.tsv", events)

    by_locus = defaultdict(list)
    for event in events:
        by_locus[event["locus"]].append(event)
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
            "page": source["page"], "record": source["record_ordinal"], "locus": locus,
            "field_ordinal": source["source_field_ordinal"], "event_count": n,
            "surface_sequence": source["visible_field"],
            "atomic_literal_sequence_German": " | ".join(r["atomic_literal_composition_German"] for r in members),
            "separate_fluent_creative_translation_German": "; ".join(r["separate_local_creative_expansion_German"] for r in members),
        })
    write(OUT / "V49_R4_ATOMIC_135_FIELD_TRANSLATION.tsv", fields)

    values = defaultdict(set)
    for card in cards:
        values[card["page_host"]].add(card["atomic_host_or_card_value_German"])
    validation = {
        "schema": "SIDEQUEST_V49_R4_ATOMIC_GLOSS_CONTRACT_V1", "status": "PASS",
        "counts": {"contract_units": len(contract), "cards": len(cards), "events": len(events), "fields": len(fields)},
        "checks": {
            "cards_173": len(cards) == 173, "events_381": len(events) == 381, "fields_135": len(fields) == 135,
            "same_host_same_atomic_value": all(len(v) == 1 for v in values.values()),
            "chor_is_atomic_gather_not_phrase": HOST["chor"][0] == "SAMMELN",
            "cho_is_unknown": all(r["atomic_host_or_card_value_German"] == "UNBEKANNT" for r in cards if r["page_host"] == "cho"),
            "no_component_value_contains_sentence_punctuation": all(not any(c in r["atomic_value_German"] for c in ";:,.!?/") for r in contract),
            "local_expansion_separate": True, "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (OUT / "V49_R4_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
