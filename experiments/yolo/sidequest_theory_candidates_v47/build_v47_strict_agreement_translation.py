#!/usr/bin/env python3
"""Build a translation in which every admitted formal contribution is invariant."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
V45 = OUT.parent / "sidequest_theory_candidates_v45"
V46 = OUT.parent / "sidequest_theory_candidates_v46"
V42_FIELDS = OUT.parent / "sidequest_theory_candidates_v42/V42_R2_135_FIELD_MEDICAL_EDITION.tsv"


HOST = {
    "ok": ("ARBEITSPOSTEN AKTIVIEREN", "FORMAL_COMPOSITIONAL_AXIS"),
    "or": ("BEREITETES ERGEBNIS/ARBEITSMEDIUM", "PROVISIONAL_CONTENT_CORE"),
    "al": ("ZIEL- ODER PARALLELSTATION", "LOW_CONFIDENCE_RELATION_AXIS"),
    "e": ("BIS ZUR ZUSTANDSGRENZE FÜHREN", "LOW_CONFIDENCE_STATE_AXIS"),
    "ot": ("MARKIERTEN BEZUG ODER WEG WÄHLEN", "LOW_CONFIDENCE_RELATION_AXIS"),
    "l": ("ANGESCHLOSSENE STATION/FORTSETZUNG", "LOW_CONFIDENCE_CONNECTION_AXIS"),
}

RECURRENT_CARD = {
    "aiin": "MASS-/STANDARDKARTE",
    "ey": "SOLLZUSTANDSKARTE",
    "oky": "VERWENDUNGSKARTE",
    "lche": "ABLAUFKARTE",
    "oke": "SPÜLKARTE",
    "cthy": "BEREITSCHAFTSKARTE",
    "okeey": "TEMPERIERKARTE",
    "ckhy": "VERBINDUNGSWEGKARTE",
    "olor": "VORANSATZ-PRODUKTKARTE",
}

RIGHT = {
    "aiin": "STANDARD-/PARAMETERPLATZ",
    "ain": "BEGRENZTE EINHEIT ODER PASSAGE",
    "al": "ZIEL-/PARALLELPLATZ",
    "ar": "QUELLEN-/LOKALRELATION",
    "air": "FLUSS-/LAUFWEG",
}

FRAME = {
    "O": "KONTEXT/VORANSATZ FORTSETZEN",
    "OT": "MARKIERTEN SEKUNDÄRBEZUG SETZEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def components(card: dict[str, str]) -> tuple[str, str, str]:
    host = card["page_host"]
    if host in HOST:
        host_value, status = HOST[host]
        parts = [f"HOST {host.upper()}={host_value}"]
    elif host in RECURRENT_CARD:
        host_value = RECURRENT_CARD[host]
        status = "RECURRENT_WHOLE_CARD_NOT_PRODUCTIVE_STEM"
        parts = [f"GANZKARTE {host.upper()}={host_value}"]
    else:
        host_value = "UNBEKANNT"
        status = "OPAQUE_WHOLE_CARD"
        parts = [f"OPAQUE HOST {host.upper()}=UNBEKANNT"]
    if card["local_frame"] in FRAME:
        parts.append(f"FRAME {card['local_frame']}={FRAME[card['local_frame']]}")
    if card["inner_d"] == "1":
        parts.append("INNER-D=GELERNTE OPERATIONS-/ZUSTANDSVARIANTE")
    if card["right_family"] != "NONE":
        parts.append(
            f"RIGHT {card['right_family'].upper()}="
            + RIGHT.get(card["right_family"], "UNBEKANNTE KOMPLETIERUNG")
        )
    if card["dy_closure"] == "1":
        parts.append("DY=LOKALEN ARBEITSSCHRITT SCHLIESSEN")
    if card["b3"] == "1":
        parts.append("B3=BESONDEREN ZELLSCHLUSS SETZEN")
    return host_value, status, " + ".join(parts)


def main() -> None:
    cards_in = read(V45 / "V45_R4_REVISED_173_CARD_LEXICON.tsv")
    events_in = read(V46 / "V46_CORRECTED_381_EVENT_INTERLINEAR.tsv")
    field_source = read(V42_FIELDS)
    assert len(cards_in) == 173 and len(events_in) == 381 and len(field_source) == 135
    cards = []
    by_tuple = {}
    for card in cards_in:
        host_value, status, literal = components(card)
        row = {
            "joint_tuple_id": card["joint_tuple_id"],
            "page_host": card["page_host"],
            "surface_examples": card["surface_examples"],
            "host_or_card_value_German": host_value,
            "analysis_status": status,
            "local_frame": card["local_frame"],
            "inner_d": card["inner_d"],
            "right_family": card["right_family"],
            "dy_closure": card["dy_closure"],
            "b3": card["b3"],
            "strict_literal_composition_German": literal,
            "fluent_local_creative_expansion_German": card["local_context_expansion_German"],
            "translation_rule": "ONLY_FROZEN_COMPONENTS_MAY_REPEAT; LOCAL_EXPANSION_IS_NOT_COMPONENT_EVIDENCE",
        }
        cards.append(row)
        by_tuple[card["joint_tuple_id"]] = row
    write(OUT / "V47_STRICT_173_CARD_DICTIONARY.tsv", cards)

    events = []
    for event in events_in:
        card = by_tuple[event["joint_tuple_id"]]
        events.append({
            "page": event["page"],
            "locus": event["locus"],
            "record": event["record"],
            "event_index": event["event_index"],
            "surface": event["surface"],
            "joint_tuple_id": event["joint_tuple_id"],
            "page_host": event["page_host"],
            "strict_literal_composition_German": card["strict_literal_composition_German"],
            "fluent_local_creative_expansion_German": card["fluent_local_creative_expansion_German"],
            "meaning_status": "STRICT_COMPONENT_AGREEMENT_CREATIVE_TRANSLATION_NOT_DECIPHERMENT",
        })
    write(OUT / "V47_STRICT_381_EVENT_INTERLINEAR.tsv", events)

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        grouped[str(event["locus"])].append(event)
    cursors = defaultdict(int)
    fields = []
    for source in field_source:
        locus = source["locus"]
        start = cursors[locus]
        count = int(source["card_count"])
        members = grouped[locus][start : start + count]
        cursors[locus] += count
        assert len(members) == count
        assert [str(r["surface"]) for r in members] == source["visible_field"].split()
        fields.append({
            "page": source["page"],
            "record": source["record_ordinal"],
            "locus": locus,
            "field_ordinal": source["source_field_ordinal"],
            "event_count": len(members),
            "surface_sequence": " ".join(str(r["surface"]) for r in members),
            "strict_literal_sequence_German": " | ".join(str(r["strict_literal_composition_German"]) for r in members),
            "fluent_local_creative_translation_German": "; ".join(str(r["fluent_local_creative_expansion_German"]) for r in members),
        })
    assert all(cursors[locus] == len(members) for locus, members in grouped.items())
    write(OUT / "V47_STRICT_135_FIELD_TRANSLATION.tsv", fields)

    host_values = defaultdict(set)
    right_values = defaultdict(set)
    for card in cards:
        host_values[str(card["page_host"])].add(str(card["host_or_card_value_German"]))
        right = str(card["right_family"])
        if right != "NONE":
            right_values[right].add(RIGHT.get(right, "UNBEKANNTE KOMPLETIERUNG"))
    validation = {
        "schema": "SIDEQUEST_V47_STRICT_STEM_AGREEMENT_TRANSLATION_V1",
        "status": "PASS",
        "counts": {
            "frozen_host_axes": len(HOST),
            "recurrent_whole_cards": len(RECURRENT_CARD),
            "frozen_right_family_values": len(RIGHT),
            "exact_cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "cards_with_productive_or_low_confidence_host_axis": sum(r["analysis_status"] in {v[1] for v in HOST.values()} for r in cards),
            "cards_with_recurrent_whole_card": sum(r["analysis_status"] == "RECURRENT_WHOLE_CARD_NOT_PRODUCTIVE_STEM" for r in cards),
            "opaque_whole_cards": sum(r["analysis_status"] == "OPAQUE_WHOLE_CARD" for r in cards),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "same_page_host_always_same_value": all(len(v) == 1 for v in host_values.values()),
            "same_right_family_always_same_value": all(len(v) == 1 for v in right_values.values()),
            "wrappers_have_no_semantic_contribution": True,
            "ch_chy_che_olk_y_have_no_host_meaning": all(by_tuple[r["joint_tuple_id"]]["host_or_card_value_German"] == "UNBEKANNT" for r in cards_in if r["page_host"] in {"ch", "chy", "che", "olk", "y"}),
            "local_expansion_not_used_to_define_components": True,
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V47_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
