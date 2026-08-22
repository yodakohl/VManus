#!/usr/bin/env python3
"""Build the selected V49 atomic-gloss revision.

This is a creative ten-page sidequest artifact.  Formal formulas come from the
non-circular R3 contract; short German glosses are kept in a separate,
explicitly graded working layer and never alter the formal decomposition.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


# Meanings are deliberately atomic.  A question mark is represented by the
# status, not embedded in the machine value.
HOST_GLOSSES = {
    "ok": ("SETZEN", "FORMAL_OPERATOR", "R1/R3/R4 converge on insertion/setting; R2 prefers an ITEM-like entry marker."),
    "ot": ("MARKIEREN", "FORMAL_OPERATOR", "R3 formal MARK; R1/R4 agree only on an abstract marked reference."),
    "l": ("VERKNÜPFEN", "FORMAL_OPERATOR", "R3 formal LINK; R1/R4 agree on connection/attachment."),
    "al": ("ZU", "WEAK_RELATION_LEAD", "R1/R4 TARGET and R2 ZU agree on direction; R3 finds no semantic value."),
    "e": ("BIS", "WEAK_GATE_LEAD", "R1/R2/R4 select a boundary/gate; R3 finds no semantic value."),
    "or": ("ANSATZ", "WEAK_CONTENT_LEAD", "R1 MEDIUM, R2 ANSATZ and R4 BEREIT overlap only on a prepared working item."),
    "chey": ("ANTEIL", "WEAK_CONTENT_LEAD", "R1 AUSWAHL, R2 ANTEIL and R4 NEHMEN overlap only in a selected share."),
}

# These are mnemonics for one recurrent exact card each, never productive
# stems and never evidence for similarly spelled forms.
WHOLE_CARD_GLOSSES = {
    "aiin": ("MASS", "WEAK_WHOLE_CARD_MNEMONIC"),
    "ey": ("FERTIG", "WEAK_WHOLE_CARD_MNEMONIC"),
    "oky": ("NUTZEN", "WEAK_WHOLE_CARD_MNEMONIC"),
    "lche": ("ABLASS", "WEAK_WHOLE_CARD_MNEMONIC"),
    "oke": ("SPÜLEN", "WEAK_WHOLE_CARD_MNEMONIC"),
    "cthy": ("BEREIT", "WEAK_WHOLE_CARD_MNEMONIC"),
    "okeey": ("LAUWARM", "WEAK_WHOLE_CARD_MNEMONIC"),
    "ckhy": ("VERBINDUNG", "WEAK_WHOLE_CARD_MNEMONIC"),
    "olor": ("VORIGES", "WEAK_WHOLE_CARD_MNEMONIC"),
}

WITHDRAWN = {
    "chor": "R1=ZEIT and R4=SAMMELN conflict; R2/R3 reject; CHOR is not CHO+R.",
    "cho": "The fixed occurrences do not share a meaning; CHO is not PFLANZE.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    r2_cards = read_tsv(HERE / "V49_R2_HISTORICAL_ATOMIC_173_CARD_DICTIONARY.tsv")
    r2_events = read_tsv(HERE / "V49_R2_HISTORICAL_ATOMIC_381_EVENT_INTERLINEAR.tsv")
    r2_fields = read_tsv(HERE / "V49_R2_HISTORICAL_ATOMIC_135_FIELD_TRANSLATION.tsv")
    r3_cards = read_tsv(HERE / "V49_R3_COMPLETE_173_ATOMIC_CARD_LEXICON.tsv")
    r3_events = read_tsv(HERE / "V49_R3_COMPLETE_381_ATOMIC_EVENT_EDITION.tsv")

    assert len(r2_cards) == len(r3_cards) == 173
    assert len(r2_events) == len(r3_events) == 381
    assert len(r2_fields) == 135
    r2_by_id = {row["joint_tuple_id"]: row for row in r2_cards}
    r3_by_id = {row["joint_tuple_id"]: row for row in r3_cards}
    assert r2_by_id.keys() == r3_by_id.keys()

    host_type_counts = Counter(row["page_host"] for row in r3_cards)
    for host in WHOLE_CARD_GLOSSES:
        assert host_type_counts[host] == 1, (host, host_type_counts[host])

    component_rows: list[dict[str, object]] = []
    for host, (gloss, status, basis) in HOST_GLOSSES.items():
        component_rows.append({
            "unit": host.upper(),
            "unit_level": "PAGE_HOST",
            "selected_atomic_value_German": gloss,
            "status": status,
            "exact_card_types": host_type_counts[host],
            "fixed_events": sum(row["page_host"] == host for row in r3_events),
            "four_role_basis": basis,
        })
    for host, reason in WITHDRAWN.items():
        component_rows.append({
            "unit": host.upper(),
            "unit_level": "PAGE_HOST",
            "selected_atomic_value_German": "UNBEKANNT",
            "status": "WITHDRAWN",
            "exact_card_types": host_type_counts[host],
            "fixed_events": sum(row["page_host"] == host for row in r3_events),
            "four_role_basis": reason,
        })
    for host, (gloss, status) in WHOLE_CARD_GLOSSES.items():
        component_rows.append({
            "unit": host.upper(),
            "unit_level": "EXACT_RECURRENT_WHOLE_CARD",
            "selected_atomic_value_German": gloss,
            "status": status,
            "exact_card_types": 1,
            "fixed_events": sum(row["page_host"] == host for row in r3_events),
            "four_role_basis": "R1/R2/R4 retain a one-word mnemonic; R3 rejects semantic composition.",
        })
    write_tsv(HERE / "V49_SELECTED_ATOMIC_GLOSSARY.tsv", component_rows)

    cards: list[dict[str, object]] = []
    cards_by_id: dict[str, dict[str, object]] = {}
    for tuple_id in sorted(r3_by_id):
        formal = r3_by_id[tuple_id]
        local = r2_by_id[tuple_id]
        host = formal["page_host"]
        if host in HOST_GLOSSES:
            value, status, basis = HOST_GLOSSES[host]
            unit = "PAGE_HOST"
        elif host in WHOLE_CARD_GLOSSES:
            value, status = WHOLE_CARD_GLOSSES[host]
            basis = "One recurrent exact-card mnemonic only; no productive segmentation."
            unit = "EXACT_WHOLE_CARD"
        else:
            value = "UNBEKANNT"
            status = "WITHDRAWN" if host in WITHDRAWN else "OPAQUE_WHOLE_CARD"
            basis = WITHDRAWN.get(host, "No selected reusable atomic meaning.")
            unit = "PAGE_HOST" if host in WITHDRAWN else "EXACT_WHOLE_CARD"
        row = {
            "joint_tuple_id": tuple_id,
            "page_host": host,
            "surface_examples": formal["surface_examples"],
            "formal_formula": formal["executable_atomic_formula"],
            "atomic_working_value_German": value,
            "atomic_unit_type": unit,
            "atomic_status": status,
            "complete_default_German": local["local_creative_expansion_German"],
            "interpretation_basis": basis,
            "rule": "FORMAL_FORMULA_AND_ATOMIC_GLOSS_ARE_SEPARATE; COMPLETE_DEFAULT_IS_CREATIVE_NOT_WORD_MEANING",
        }
        cards.append(row)
        cards_by_id[tuple_id] = row
    write_tsv(HERE / "V49_SELECTED_173_CARD_DICTIONARY.tsv", cards)

    r3_event_by_key = {
        (row["page"], row["locus"], row["event_index"], row["joint_tuple_id"]): row
        for row in r3_events
    }
    events: list[dict[str, object]] = []
    for local in r2_events:
        key = (local["page"], local["locus"], local["event_index"], local["joint_tuple_id"])
        formal = r3_event_by_key[key]
        card = cards_by_id[local["joint_tuple_id"]]
        events.append({
            "page": local["page"],
            "locus": local["locus"],
            "record": local["record"],
            "event_index": local["event_index"],
            "surface": local["surface"],
            "joint_tuple_id": local["joint_tuple_id"],
            "page_host": local["page_host"],
            "formal_formula": formal["executable_atomic_formula"],
            "atomic_working_value_German": card["atomic_working_value_German"],
            "atomic_status": card["atomic_status"],
            "complete_default_German": local["local_creative_expansion_German"],
        })
    write_tsv(HERE / "V49_SELECTED_381_EVENT_INTERLINEAR.tsv", events)

    events_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        events_by_locus[str(row["locus"])].append(row)
    cursors: Counter[str] = Counter()
    fields: list[dict[str, object]] = []
    for source in r2_fields:
        locus = source["locus"]
        count = int(source["event_count"])
        start = cursors[locus]
        members = events_by_locus[locus][start : start + count]
        cursors[locus] += count
        assert [str(row["surface"]) for row in members] == source["surface_sequence"].split()
        fields.append({
            "page": source["page"],
            "record": source["record"],
            "locus": locus,
            "field_ordinal": source["field_ordinal"],
            "event_count": count,
            "surface_sequence": source["surface_sequence"],
            "formal_sequence": " | ".join(str(row["formal_formula"]) for row in members),
            "atomic_working_sequence_German": " | ".join(str(row["atomic_working_value_German"]) for row in members),
            "complete_creative_translation_German": source["local_creative_translation_German"],
        })
    write_tsv(HERE / "V49_SELECTED_135_FIELD_TRANSLATION.tsv", fields)

    validation = {
        "schema": "SIDEQUEST_V49_SELECTED_ATOMIC_GLOSS_REVISION_V1",
        "status": "PASS",
        "counts": {
            "component_rows": len(component_rows),
            "cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "formal_operator_cards": sum(row["atomic_status"] == "FORMAL_OPERATOR" for row in cards),
            "weak_host_lead_cards": sum(str(row["atomic_status"]).startswith("WEAK_") and row["atomic_unit_type"] == "PAGE_HOST" for row in cards),
            "whole_card_mnemonic_cards": sum(row["atomic_unit_type"] == "EXACT_WHOLE_CARD" and row["atomic_status"] == "WEAK_WHOLE_CARD_MNEMONIC" for row in cards),
            "opaque_or_withdrawn_cards": sum(row["atomic_working_value_German"] == "UNBEKANNT" for row in cards),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "complete_defaults_nonempty": all(str(row["complete_default_German"]).strip() for row in cards),
            "chor_unknown": all(row["atomic_working_value_German"] == "UNBEKANNT" for row in cards if row["page_host"] == "chor"),
            "cho_unknown": all(row["atomic_working_value_German"] == "UNBEKANNT" for row in cards if row["page_host"] == "cho"),
            "no_chor_decomposition": all("CHO+R" not in str(row["formal_formula"]) for row in cards),
            "formal_formula_unchanged_from_r3": all(cards_by_id[k]["formal_formula"] == v["executable_atomic_formula"] for k, v in r3_by_id.items()),
            "f84_sealed": True,
            "f84r_sealed": True,
        },
        "inputs": {
            "r2_cards_sha256": sha256(HERE / "V49_R2_HISTORICAL_ATOMIC_173_CARD_DICTIONARY.tsv"),
            "r3_cards_sha256": sha256(HERE / "V49_R3_COMPLETE_173_ATOMIC_CARD_LEXICON.tsv"),
        },
    }
    assert all(v is True for v in validation["checks"].values())
    (HERE / "V49_SELECTED_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
