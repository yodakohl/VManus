#!/usr/bin/env python3
"""Corrector pass: test a bounded extension of V47's invariant components."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "sidequest_theory_candidates_v47"
FIELDS = OUT.parent / "sidequest_theory_candidates_v42/V42_R2_135_FIELD_MEDICAL_EDITION.tsv"

PROPOSALS = {
    "o": ("NÄCHSTEN ZUBEREITUNGSPOSTEN ODER -SCHRITT EINSETZEN", "PROMOTE_FORMAL_SEQUENCE_AXIS", "3 Karten/6 Ereignisse: nächsten Zusatz wählen, spezifizierten Wein zugeben, anschließenden Ziehschritt ausführen"),
    "chol": ("GEZEIGTEN SIMPLEX ODER SEINE AKTIVE ZUBEREITUNG WIEDERAUFNEHMEN", "PROMOTE_PROVISIONAL_REFERENCE_AXIS", "2 Karten/3 Ereignisse: Bezug auf abgebildeten Simplex und warme Anwendung seiner Zubereitung"),
    "k": ("UNBEKANNT", "REJECT", "Rückstrom, Wasserzugabe und Maßanteil teilen keinen ausreichend bestimmten Minimalwert"),
    "lched": ("UNBEKANNT", "REJECT", "kühles Wasser, unteres Becken und nächstes Becken ergeben nur recordlokale Badeassoziation"),
    "cho": ("UNBEKANNT", "REJECT", "Abkühlen und schattiger Waldort liefern mit zwei Belegen nur eine attraktive Bildassoziation"),
    "rshe": ("UNBEKANNT", "REJECT", "Trinken und warmes Wasser eingießen teilen nur die zu breite Kategorie Flüssigkeitsgebrauch"),
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
    event_count_by_tuple = defaultdict(int)
    for event in base_events:
        event_count_by_tuple[event["joint_tuple_id"]] += 1
    candidates = []
    for host, (value, decision, reason) in PROPOSALS.items():
        members = [r for r in base_cards if r["page_host"] == host]
        candidates.append({
            "page_host": host,
            "candidate_invariant_value_German": value,
            "decision": decision,
            "exact_cards": len(members),
            "fixed_events": sum(event_count_by_tuple[r["joint_tuple_id"]] for r in members),
            "surface_examples": " || ".join(r["surface_examples"] for r in members),
            "local_expansions": " || ".join(r["fluent_local_creative_expansion_German"] for r in members),
            "reason": reason,
        })
    write(OUT / "V48_R4_CANDIDATE_EXTENSION_AUDIT.tsv", candidates)

    cards = []
    by_tuple = {}
    for row in base_cards:
        new = dict(row)
        host = row["page_host"]
        if host in PROPOSALS and PROPOSALS[host][1].startswith("PROMOTE_"):
            value, decision, _ = PROPOSALS[host]
            new["host_or_card_value_German"] = value
            new["analysis_status"] = decision
            old_prefix = f"OPAQUE HOST {host.upper()}=UNBEKANNT"
            assert new["strict_literal_composition_German"].startswith(old_prefix)
            new["strict_literal_composition_German"] = new["strict_literal_composition_German"].replace(
                old_prefix, f"HOST {host.upper()}={value}", 1
            )
        cards.append(new)
        by_tuple[new["joint_tuple_id"]] = new
    write(OUT / "V48_R4_COMPLETE_173_CARD_LEXICON.tsv", cards)

    events = []
    for row in base_events:
        card = by_tuple[row["joint_tuple_id"]]
        new = dict(row)
        new["strict_literal_composition_German"] = card["strict_literal_composition_German"]
        events.append(new)
    write(OUT / "V48_R4_COMPLETE_381_EVENT_TRANSLATION.tsv", events)

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
    write(OUT / "V48_R4_COMPLETE_135_FIELD_TRANSLATION.tsv", fields)

    values = defaultdict(set)
    for row in cards:
        values[row["page_host"]].add(row["host_or_card_value_German"])
    validation = {
        "schema": "SIDEQUEST_V48_R4_BOUNDED_COMPONENT_EXTENSION_V1",
        "status": "PASS",
        "counts": {
            "candidates": len(candidates),
            "promoted_candidates": sum(r["decision"].startswith("PROMOTE_") for r in candidates),
            "cards": len(cards),
            "events": len(events),
            "fields": len(fields),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "same_host_same_value": all(len(v) == 1 for v in values.values()),
            "v47_values_unchanged_outside_promotions": all(
                by_tuple[r["joint_tuple_id"]]["host_or_card_value_German"] == r["host_or_card_value_German"]
                for r in base_cards if r["page_host"] not in {"o", "chol"}
            ),
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V48_R4_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
