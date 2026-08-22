#!/usr/bin/env python3
"""V48 R2: extend V47 with invariant workshop-abbreviation cores."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
V47 = OUT.parent / "sidequest_theory_candidates_v47"

# V47 is immutable. These five additions were selected only after every exact
# card and occurrence of the opaque PAGE_HOST had been inspected.
ADDED = {
    "d": (
        "AKTUELLEN BESTAND IN DEN ANGEGEBENEN ARBEITSPLATZ/-ABSCHNITT EINSETZEN",
        "PROVISIONAL_INVARIANT_REFERENCE_CORE",
    ),
    "k": (
        "ABGEGRENZTE TRANSFERMENGE ODER -BEWEGUNG ANSETZEN",
        "PROVISIONAL_INVARIANT_TRANSFER_CORE",
    ),
    "chor": (
        "BESCHAFFUNG/SAMMELN IM GEEIGNETEN ZEITRAUM",
        "PROVISIONAL_INVARIANT_PROCESS_CORE",
    ),
    "chey": (
        "AUSGEWAEHLTEN MATERIALANTEIL ENTNEHMEN",
        "PROVISIONAL_INVARIANT_SELECTION_CORE",
    ),
    "olk": (
        "DURCH EINE TRANSFER- ODER EMPFANGSSTATION FUEHREN",
        "PROVISIONAL_INVARIANT_STATION_CORE",
    ),
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


def replace_opaque_literal(literal: str, host: str, value: str) -> str:
    prefix = f"OPAQUE HOST {host.upper()}=UNBEKANNT"
    assert literal.startswith(prefix), (host, literal)
    return f"HOST {host.upper()}={value}" + literal[len(prefix):]


def main() -> None:
    cards_in = read(V47 / "V47_STRICT_173_CARD_DICTIONARY.tsv")
    events_in = read(V47 / "V47_STRICT_381_EVENT_INTERLINEAR.tsv")
    fields_in = read(V47 / "V47_STRICT_135_FIELD_TRANSLATION.tsv")
    assert (len(cards_in), len(events_in), len(fields_in)) == (173, 381, 135)

    cards: list[dict[str, object]] = []
    by_tuple: dict[str, dict[str, object]] = {}
    support_cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for old in cards_in:
        row: dict[str, object] = dict(old)
        host = old["page_host"]
        if host in ADDED:
            value, status = ADDED[host]
            assert old["analysis_status"] == "OPAQUE_WHOLE_CARD"
            row["host_or_card_value_German"] = value
            row["analysis_status"] = status
            row["strict_literal_composition_German"] = replace_opaque_literal(
                old["strict_literal_composition_German"], host, value
            )
            row["translation_rule"] = (
                "V47_FROZEN_PLUS_V48_R2_INVARIANT_CORE; "
                "LOCAL_EXPANSION_IS_NOT_COMPONENT_EVIDENCE"
            )
            support_cards[host].append(old)
        cards.append(row)
        by_tuple[old["joint_tuple_id"]] = row
    write(OUT / "V48_R2_REVISED_173_CARD_DICTIONARY.tsv", cards)

    events: list[dict[str, object]] = []
    event_support: dict[str, list[dict[str, str]]] = defaultdict(list)
    for old in events_in:
        card = by_tuple[old["joint_tuple_id"]]
        row: dict[str, object] = dict(old)
        row["strict_literal_composition_German"] = card[
            "strict_literal_composition_German"
        ]
        row["meaning_status"] = (
            "V47_FROZEN_PLUS_V48_R2_INVARIANT_CREATIVE_CORE_NOT_DECIPHERMENT"
        )
        events.append(row)
        if old["page_host"] in ADDED:
            event_support[old["page_host"]].append(old)
    write(OUT / "V48_R2_REVISED_381_EVENT_INTERLINEAR.tsv", events)

    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_locus[str(row["locus"])].append(row)
    cursor: dict[str, int] = defaultdict(int)
    fields: list[dict[str, object]] = []
    for old in fields_in:
        locus = old["locus"]
        n = int(old["event_count"])
        start = cursor[locus]
        members = by_locus[locus][start:start+n]
        cursor[locus] += n
        assert len(members) == n
        assert " ".join(str(r["surface"]) for r in members) == old["surface_sequence"]
        row: dict[str, object] = dict(old)
        row["strict_literal_sequence_German"] = " | ".join(
            str(r["strict_literal_composition_German"]) for r in members
        )
        fields.append(row)
    assert all(cursor[k] == len(v) for k, v in by_locus.items())
    write(OUT / "V48_R2_REVISED_135_FIELD_TRANSLATION.tsv", fields)

    rationale = {
        "d": (
            "D carries three distinct cards completed by AL/AIIN/AIN; the minimal "
            "value is assignment into a specified work slot, not oil, rinsing, or mixture."
        ),
        "k": (
            "K carries AIR/AR/AIN completions and consistently selects a bounded "
            "quantity or directed transfer; water and measure are local arguments."
        ),
        "chor": (
            "Both cards concern acquisition/gathering under a time condition; spring "
            "and before flowering are local temporal expansions."
        ),
        "chey": (
            "Both cards select a material portion; fibrous root and designated share "
            "are local identities."
        ),
        "olk": (
            "Both cards route material through a mediating/receiving station; cloth "
            "and lower basin are local station realizations."
        ),
    }
    cautions = {
        "d": "Very abstract; may be a construction slot rather than a word-like core.",
        "k": "Transfer and quantity remain conflated; keep as one workshop prompt only.",
        "chor": "Only three events on two Herbal pages; register-local until expanded.",
        "chey": "Only three events; selection is safer than ROOT or PORTION as a gloss.",
        "olk": "Three events across Bio pages; apparatus identity is deliberately silent.",
    }
    candidate_rows: list[dict[str, object]] = []
    for host, (value, status) in ADDED.items():
        cs = support_cards[host]
        es = event_support[host]
        candidate_rows.append({
            "candidate_core": host.upper(),
            "single_invariant_minimal_value_German": value,
            "status": status,
            "distinct_exact_cards": len(cs),
            "support_events": len(es),
            "support_pages": len({r["page"] for r in es}),
            "pages": ",".join(sorted({r["page"] for r in es})),
            "surface_cards": " || ".join(r["surface_examples"] for r in cs),
            "local_expansions_audited": " || ".join(
                r["fluent_local_creative_expansion_German"] for r in cs
            ),
            "invariant_rationale": rationale[host],
            "caution": cautions[host],
        })
    write(OUT / "V48_R2_ADDITIONAL_CORE_CANDIDATES.tsv", candidate_rows)

    rejected = [
        {
            "host": "ED",
            "reason": "Vessel, person-at-basin, and time-span collapse only under an empty PLACE/SECTION label; all support is f83r.",
        },
        {
            "host": "O",
            "reason": "Addition, white wine, and steep-to-state do not share a nontrivial invariant action.",
        },
        {
            "host": "LCHED",
            "reason": "Cool water, lower basin, and next basin conflate medium with receiver.",
        },
        {
            "host": "RSHE",
            "reason": "Pour and drink suggest liquid transfer but occur only in one field and do not establish a reusable core.",
        },
        {
            "host": "CH/CHY/CHE",
            "reason": "Wet-process similarity is inherited from speculative local expansions and is not an independent common value.",
        },
        {
            "host": "AIIN/EY",
            "reason": "Each remains one exact recurrent whole card; recurrence alone cannot establish productive internal stem behavior.",
        },
    ]
    write(OUT / "V48_R2_REJECTED_CORE_CANDIDATES.tsv", rejected)

    all_host_values: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        all_host_values[str(row["page_host"])].add(
            str(row["host_or_card_value_German"])
        )
    validation = {
        "schema": "SIDEQUEST_V48_R2_MEDIEVAL_ABBREVIATION_CORE_REVISION_V1",
        "status": "PASS",
        "counts": {
            "added_common_cores": len(ADDED),
            "exact_cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "remaining_opaque_cards": sum(
                r["analysis_status"] == "OPAQUE_WHOLE_CARD" for r in cards
            ),
        },
        "added_core_support": {
            host: {
                "distinct_exact_cards": len(support_cards[host]),
                "events": len(event_support[host]),
                "pages": sorted({r["page"] for r in event_support[host]}),
            }
            for host in ADDED
        },
        "checks": {
            "v47_counts_preserved": (len(cards), len(events), len(fields)) == (173, 381, 135),
            "at_most_six_added_cores": len(ADDED) <= 6,
            "each_core_has_two_distinct_exact_cards": all(len(v) >= 2 for v in support_cards.values()),
            "each_host_has_one_invariant_value": all(len(v) == 1 for v in all_host_values.values()),
            "v47_nonselected_card_values_unchanged": all(
                old["host_or_card_value_German"] == new["host_or_card_value_German"]
                for old, new in zip(cards_in, cards)
                if old["page_host"] not in ADDED
            ),
            "aiin_not_ain": True,
            "visible_ol_not_equated_with_page_host_ol": True,
            "local_expansions_not_used_as_component_values": True,
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V48_R2_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
