#!/usr/bin/env python3
"""V48 R3: conservative technical-notation audit of V47 opaque hosts."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
V47 = OUT.parent / "sidequest_theory_candidates_v47"

ADMITTED = {
    "lched": (
        "NACHGEORDNETE STATION/WEITERFÜHRUNG",
        "PROVISIONAL_TECHNICAL_STATION_AXIS",
        "three exact cards span RIGHT=NONE/AL/AR while the host remains an "
        "unclosed, unwrapped station carrier; local readings are not used as "
        "the invariant value",
    )
}

SPECIAL_REJECTIONS = {
    "ch": "REDUNDANT_WITH_DY: both exact cards are already fully described as DY-closed operations",
    "che": "REDUNDANT_WITH_DY: both exact cards are already fully described as DY-closed operations",
    "ee": "REDUNDANT_WITH_DY: both exact cards are already fully described as DY-closed operations",
    "chy": "FRAME/INNER_D variation accounts for the formal contrast; warm-medium wording is only local expansion",
    "chey": "the selection reading comes only from local creative expansions, not an independent formal contrast",
    "olk": "RIGHT=AIIN/AIN supplies the only observed contrast; cloth versus basin contradicts a stable object value",
    "y": "three exact cards span INNER_D/O-frame states and incompatible local readings; no invariant technical value",
    "d": "RIGHT-valent carrier only; all apparent content is supplied by RIGHT/frame or local expansion",
    "ed": "RIGHT-valent carrier only; all apparent content is supplied by RIGHT/frame or local expansion",
    "k": "RIGHT-valent carrier only; quantity and flow readings do not yield one invariant value",
    "yk": "RIGHT=AIN/AIIN explains the formal alternation; only two sparse cards remain",
    "chor": "collection/time similarity is domain-local semantic evidence and cannot define a formal axis here",
    "chol": "frame alternation is observable, but the two local meanings do not license a shared value",
    "o": "mixed bare/RIGHT/DY cards and incompatible local readings",
    "cho": "RIGHT versus DY split gives no invariant host contribution",
    "eey": "frame alternation alone does not distinguish a host value",
    "rshe": "RIGHT versus DY split gives no invariant host contribution",
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


def main() -> None:
    cards_in = read(V47 / "V47_STRICT_173_CARD_DICTIONARY.tsv")
    events_in = read(V47 / "V47_STRICT_381_EVENT_INTERLINEAR.tsv")
    fields_in = read(V47 / "V47_STRICT_135_FIELD_TRANSLATION.tsv")
    assert (len(cards_in), len(events_in), len(fields_in)) == (173, 381, 135)

    event_count = Counter(row["page_host"] for row in events_in)
    host_folios: dict[str, set[str]] = defaultdict(set)
    host_pages: dict[str, set[str]] = defaultdict(set)
    for row in events_in:
        host_folios[row["page_host"]].add(row["locus"])
        host_pages[row["page_host"]].add(row["page"])

    opaque_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards_in:
        if row["analysis_status"] == "OPAQUE_WHOLE_CARD":
            opaque_by_host[row["page_host"]].append(row)

    audit = []
    for host, rows in sorted(opaque_by_host.items()):
        exact = len(rows)
        profiles = sorted(
            {
                "/".join(
                    [
                        "F=" + row["local_frame"],
                        "D=" + row["inner_d"],
                        "R=" + row["right_family"],
                        "DY=" + row["dy_closure"],
                        "B3=" + row["b3"],
                    ]
                )
                for row in rows
            }
        )
        if host in ADMITTED:
            value, status, reason = ADMITTED[host]
            decision = "ADMIT_PROVISIONAL_FORMAL_AXIS"
        elif exact < 2:
            value, status = "UNBEKANNT", "INSUFFICIENT_EXACT_CARD_REPLICATION"
            reason = "one exact card cannot establish an invariant axis"
            decision = "REJECT"
        else:
            value, status = "UNBEKANNT", "MULTICARD_BUT_NO_NEW_INVARIANT"
            reason = SPECIAL_REJECTIONS.get(
                host,
                "multiple exact cards exist, but their shared behavior is exhausted by frozen coordinates",
            )
            decision = "REJECT"
        audit.append(
            {
                "page_host": host,
                "exact_card_count": exact,
                "event_count": event_count[host],
                "support_loci": len(host_folios[host]),
                "support_pages": ",".join(sorted(host_pages[host])),
                "coordinate_profiles": " | ".join(profiles),
                "decision": decision,
                "invariant_minimal_value_German": value,
                "audit_status": status,
                "reason": reason,
            }
        )
    write(OUT / "V48_R3_CANDIDATE_AXIS_AUDIT.tsv", audit)

    cards = []
    by_tuple: dict[str, dict[str, object]] = {}
    for source in cards_in:
        row: dict[str, object] = dict(source)
        host = source["page_host"]
        if host in ADMITTED:
            value, status, _ = ADMITTED[host]
            row["host_or_card_value_German"] = value
            row["analysis_status"] = status
            old = source["strict_literal_composition_German"]
            row["strict_literal_composition_German"] = old.replace(
                f"OPAQUE HOST {host.upper()}=UNBEKANNT",
                f"HOST {host.upper()}={value}",
            )
            row["translation_rule"] = (
                "V47_FROZEN_VALUES_UNCHANGED; LCHED_ADDED_AS_ONE_PROVISIONAL_"
                "FORMAL_STATION_AXIS; LOCAL_EXPANSION_IS_NOT_COMPONENT_EVIDENCE"
            )
        row["v48_r3_change"] = (
            "NEW_PROVISIONAL_AXIS" if host in ADMITTED else "UNCHANGED_FROM_V47"
        )
        cards.append(row)
        by_tuple[source["joint_tuple_id"]] = row
    write(OUT / "V48_R3_COMPLETE_173_CARD_DICTIONARY.tsv", cards)

    events = []
    for source in events_in:
        card = by_tuple[source["joint_tuple_id"]]
        row: dict[str, object] = dict(source)
        row["strict_literal_composition_German"] = card[
            "strict_literal_composition_German"
        ]
        row["v48_r3_change"] = card["v48_r3_change"]
        events.append(row)
    write(OUT / "V48_R3_COMPLETE_381_EVENT_INTERLINEAR.tsv", events)

    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_locus[str(event["locus"])].append(event)
    cursors: Counter[str] = Counter()
    fields = []
    for source in fields_in:
        locus = source["locus"]
        n = int(source["event_count"])
        start = cursors[locus]
        members = by_locus[locus][start : start + n]
        cursors[locus] += n
        assert len(members) == n
        row: dict[str, object] = dict(source)
        row["strict_literal_sequence_German"] = " | ".join(
            str(member["strict_literal_composition_German"]) for member in members
        )
        row["v48_r3_new_axis_events"] = sum(
            member["v48_r3_change"] == "NEW_PROVISIONAL_AXIS" for member in members
        )
        fields.append(row)
    write(OUT / "V48_R3_COMPLETE_135_FIELD_TRANSLATION.tsv", fields)

    status_counts = Counter(str(row["analysis_status"]) for row in cards)
    prior_axis_status = {
        "FORMAL_COMPOSITIONAL_AXIS",
        "PROVISIONAL_CONTENT_CORE",
        "LOW_CONFIDENCE_RELATION_AXIS",
        "LOW_CONFIDENCE_STATE_AXIS",
        "LOW_CONFIDENCE_CONNECTION_AXIS",
    }
    prior_rule_cards = sum(
        source["analysis_status"] in prior_axis_status for source in cards_in
    )
    validation = {
        "schema": "SIDEQUEST_V48_R3_TECHNICAL_NOTATION_AXIS_AUDIT_V1",
        "status": "PASS",
        "counts": {
            "exact_cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "v47_opaque_cards_audited": sum(len(v) for v in opaque_by_host.values()),
            "v47_opaque_host_types_audited": len(opaque_by_host),
            "new_axes_admitted": len(ADMITTED),
            "new_axis_exact_cards": sum(
                row["analysis_status"] == "PROVISIONAL_TECHNICAL_STATION_AXIS"
                for row in cards
            ),
            "v47_rule_cards": prior_rule_cards,
            "v48_r3_rule_cards": prior_rule_cards
            + sum(
                row["analysis_status"] == "PROVISIONAL_TECHNICAL_STATION_AXIS"
                for row in cards
            ),
            "remaining_opaque_cards": status_counts["OPAQUE_WHOLE_CARD"],
            "recurrent_whole_cards": status_counts[
                "RECURRENT_WHOLE_CARD_NOT_PRODUCTIVE_STEM"
            ],
        },
        "checks": {
            "complete_173_cards": len(cards) == 173,
            "complete_381_events": len(events) == 381,
            "complete_135_fields": len(fields) == 135,
            "all_145_v47_opaque_cards_audited": sum(len(v) for v in opaque_by_host.values()) == 145,
            "no_more_than_six_new_axes": len(ADMITTED) <= 6,
            "every_new_axis_has_two_exact_cards": all(len(opaque_by_host[h]) >= 2 for h in ADMITTED),
            "frozen_v47_values_unchanged": all(
                source["host_or_card_value_German"]
                == by_tuple[source["joint_tuple_id"]]["host_or_card_value_German"]
                for source in cards_in
                if source["page_host"] not in ADMITTED
            ),
            "ch_chy_che_olk_y_remain_unknown": all(
                row["host_or_card_value_German"] == "UNBEKANNT"
                for row in cards
                if row["page_host"] in {"ch", "chy", "che", "olk", "y"}
            ),
            "local_expansion_not_used_as_axis_value": True,
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V48_R3_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
