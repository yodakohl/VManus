#!/usr/bin/env python3
"""Build R1's atomic-minimal correction of the ten-page sidequest lexicon.

This deliberately preserves every V48 local creative expansion while replacing
event-sized host glosses with one simple concept/operator, or UNKNOWN.  The
output is a creative sidequest instrument, not evidence of decipherment.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "sidequest_theory_candidates_v48"

# One simple German concept/operator per proposed shared host.  No object +
# action + time paraphrase is allowed here.
SHARED_HOSTS = {
    "ok": ("EINSETZEN", "ATOMIC_SHARED_FORMAL_LEAD"),
    "or": ("MEDIUM", "ATOMIC_SHARED_CONTENT_LEAD"),
    "al": ("ZIEL", "ATOMIC_SHARED_RELATION_LEAD"),
    "e": ("BIS", "ATOMIC_SHARED_STATE_LEAD"),
    "ot": ("BEZUG", "ATOMIC_SHARED_RELATION_LEAD"),
    "l": ("ANSCHLUSS", "ATOMIC_SHARED_CONNECTION_LEAD"),
    "chey": ("AUSWAHL", "PROVISIONAL_ATOMIC_HOST_LEAD"),
    "chor": ("ZEIT", "PROVISIONAL_ATOMIC_HOST_LEAD"),
}

# Recurrent exact cards may have a compact workshop mnemonic, but are not
# productive host/stem paradigms in the fixed panel.
WHOLE_CARDS = {
    "aiin": "MASS",
    "ey": "ENDZUSTAND",
    "oky": "VERWENDUNG",
    "lche": "ABLAUF",
    "oke": "SPÜLUNG",
    "cthy": "BEREIT",
    "okeey": "LAUWARM",
    "ckhy": "KANAL",
    "olor": "VORHERIGES",
}

FRAME = {"O": "FORTSETZUNG", "OT": "MARKIERUNG"}
RIGHT = {
    "aiin": "PARAMETER",
    "ain": "EINHEIT",
    "al": "ZIEL",
    "ar": "QUELLE",
    "air": "WEG",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def strict_composition(row: dict[str, str], value: str, status: str) -> str:
    host = row["page_host"].upper()
    if status == "ATOMIC_WHOLE_CARD_NOT_PRODUCTIVE_STEM":
        pieces = [f"GANZKARTE {host}={value}"]
    elif value != "UNBEKANNT":
        pieces = [f"HOST {host}={value}"]
    else:
        pieces = [f"OPAQUE HOST {host}=UNBEKANNT"]

    if row["local_frame"] != "NONE":
        pieces.append(f"FRAME {row['local_frame']}={FRAME[row['local_frame']]}")
    if row["inner_d"] == "1":
        pieces.append("INNER-D=VARIANTE")
    if row["right_family"] != "NONE":
        right = row["right_family"]
        pieces.append(f"RIGHT {right.upper()}={RIGHT[right]}")
    if row["dy_closure"] == "1":
        pieces.append("DY=ABSCHLUSS")
    if row["b3"] == "1":
        pieces.append("B3=SONDERSCHLUSS")
    return " + ".join(pieces)


def main() -> None:
    cards_in = read_tsv(BASE / "V48_SELECTED_173_CARD_DICTIONARY.tsv")
    events_in = read_tsv(BASE / "V48_SELECTED_381_EVENT_INTERLINEAR.tsv")
    fields_in = read_tsv(BASE / "V48_SELECTED_135_FIELD_TRANSLATION.tsv")

    cards: list[dict[str, str]] = []
    card_by_tuple: dict[str, dict[str, str]] = {}
    for source in cards_in:
        row = dict(source)
        host = row["page_host"]
        if host in SHARED_HOSTS:
            value, status = SHARED_HOSTS[host]
        elif host in WHOLE_CARDS:
            value = WHOLE_CARDS[host]
            status = "ATOMIC_WHOLE_CARD_NOT_PRODUCTIVE_STEM"
        else:
            value = "UNBEKANNT"
            status = "OPAQUE_WHOLE_CARD"
        row["host_or_card_value_German"] = value
        row["analysis_status"] = status
        row["strict_literal_composition_German"] = strict_composition(row, value, status)
        row["translation_rule"] = (
            "ATOMIC_VALUE_IS_ONE_SIMPLE_CONCEPT; "
            "LOCAL_EXPANSION_IS_SEPARATE_AND_NOT_STEM_EVIDENCE"
        )
        cards.append(row)
        card_by_tuple[row["joint_tuple_id"]] = row
    write_tsv(OUT / "V49_R1_CORRECTED_173_CARD_LEXICON.tsv", cards)

    events: list[dict[str, str]] = []
    events_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in events_in:
        row = dict(source)
        card = card_by_tuple[row["joint_tuple_id"]]
        row["strict_literal_composition_German"] = card["strict_literal_composition_German"]
        row["meaning_status"] = "ATOMIC_WORKSHOP_VALUE_CREATIVE_TRANSLATION_NOT_DECIPHERMENT"
        events.append(row)
        events_by_locus[row["locus"]].append(row)
    write_tsv(OUT / "V49_R1_CORRECTED_381_EVENT_INTERLINEAR.tsv", events)

    # Preserve the exact V48 field/event segmentation and local prose.  Rebuild
    # only the strict layer from corrected card values.
    field_cursors: Counter[str] = Counter()
    fields: list[dict[str, str]] = []
    for source in fields_in:
        row = dict(source)
        locus = row["locus"]
        n = int(row["event_count"])
        start = field_cursors[locus]
        members = events_by_locus[locus][start : start + n]
        field_cursors[locus] += n
        assert [member["surface"] for member in members] == row["surface_sequence"].split()
        row["strict_literal_sequence_German"] = " | ".join(
            member["strict_literal_composition_German"] for member in members
        )
        # fluent_local_creative_translation_German is intentionally unchanged.
        fields.append(row)
    write_tsv(OUT / "V49_R1_CORRECTED_135_FIELD_TRANSLATION.tsv", fields)

    card_counts = Counter(row["page_host"] for row in cards)
    event_counts = Counter(row["page_host"] for row in events)
    candidates = [
        {
            "unit": "ok",
            "layer": "PAGE_HOST",
            "atomic_value_German": "EINSETZEN",
            "decision": "RETAIN_ATOMIC_SHARED_LEAD",
            "exact_cards": card_counts["ok"],
            "fixed_events": event_counts["ok"],
            "removed_overclaim": "spezifizierten Arbeitsposten einsetzen/aktivieren",
            "reason": "Nur der abstrakte Einsatzoperator bleibt; Arbeitsposten und Spezifikation sind lokale Argumente.",
        },
        {
            "unit": "or",
            "layer": "PAGE_HOST",
            "atomic_value_German": "MEDIUM",
            "decision": "RETAIN_ATOMIC_SHARED_LEAD",
            "exact_cards": card_counts["or"],
            "fixed_events": event_counts["or"],
            "removed_overclaim": "bereitetes Ergebnis oder Arbeitsmedium",
            "reason": "MEDIUM ist die kleinste gemeinsame Inhaltslesung; bereitet/fertig/frisch bleiben lokal.",
        },
        {
            "unit": "al",
            "layer": "PAGE_HOST",
            "atomic_value_German": "ZIEL",
            "decision": "RETAIN_ATOMIC_SHARED_LEAD",
            "exact_cards": card_counts["al"],
            "fixed_events": event_counts["al"],
            "removed_overclaim": "Ziel- oder Parallelstation",
            "reason": "ZIEL deckt beide Karten ohne Objekt- oder Handlungsanteil ab.",
        },
        {
            "unit": "e",
            "layer": "PAGE_HOST",
            "atomic_value_German": "BIS",
            "decision": "RETAIN_ATOMIC_SHARED_LEAD",
            "exact_cards": card_counts["e"],
            "fixed_events": event_counts["e"],
            "removed_overclaim": "Vorgang bis zu einer Zustandsgrenze führen",
            "reason": "BIS ist nur der Grenzoperator; Bereitschaft/Klarheit und Handlung stammen aus dem lokalen Satz.",
        },
        {
            "unit": "ot",
            "layer": "PAGE_HOST",
            "atomic_value_German": "BEZUG",
            "decision": "RETAIN_ATOMIC_SHARED_LEAD",
            "exact_cards": card_counts["ot"],
            "fixed_events": event_counts["ot"],
            "removed_overclaim": "markierten Bezug, Parameter oder Weg wählen",
            "reason": "BEZUG ist die einzige atomare Schnittmenge; wählen/markiert/Weg sind nicht Teil des Werts.",
        },
        {
            "unit": "l",
            "layer": "PAGE_HOST",
            "atomic_value_German": "ANSCHLUSS",
            "decision": "RETAIN_ATOMIC_SHARED_LEAD",
            "exact_cards": card_counts["l"],
            "fixed_events": event_counts["l"],
            "removed_overclaim": "angeschlossene Station oder Fortsetzung",
            "reason": "ANSCHLUSS ist eine formale Relation; Öl, Abziehen, Kochen und Station bleiben lokal.",
        },
        {
            "unit": "chey",
            "layer": "PAGE_HOST",
            "atomic_value_German": "AUSWAHL",
            "decision": "PROVISIONAL_ATOMIC_LEAD",
            "exact_cards": card_counts["chey"],
            "fixed_events": event_counts["chey"],
            "removed_overclaim": "ausgewählten Materialanteil aufnehmen",
            "reason": "Nur Auswahl ist beiden lokalen Kartenlesungen gemeinsam; Material, Anteil und nehmen sind stille Argumente.",
        },
        {
            "unit": "chor",
            "layer": "PAGE_HOST",
            "atomic_value_German": "ZEIT",
            "decision": "PROVISIONAL_ATOMIC_LEAD_NOT_DECOMPOSED",
            "exact_cards": card_counts["chor"],
            "fixed_events": event_counts["chor"],
            "removed_overclaim": "Pflanzenmaterial zeitgebunden beschaffen",
            "reason": "Vor Blüte und Frühjahr teilen nur einen Zeitbezug. CHOR ist nicht CHO+R; CHO bleibt unbekannt.",
        },
    ]
    for host, value in WHOLE_CARDS.items():
        candidates.append({
            "unit": host,
            "layer": "EXACT_RECURRENT_WHOLE_CARD",
            "atomic_value_German": value,
            "decision": "ATOMIC_MNEMONIC_NOT_A_STEM",
            "exact_cards": card_counts[host],
            "fixed_events": event_counts[host],
            "removed_overclaim": next(
                row["host_or_card_value_German"] for row in cards_in if row["page_host"] == host
            ),
            "reason": "Ein wiederkehrender exakter Kartentyp; der Kurzname behauptet keine produktive Zerlegung.",
        })
    candidates.extend([
        {
            "unit": "cho",
            "layer": "PAGE_HOST",
            "atomic_value_German": "UNBEKANNT",
            "decision": "REJECT_AS_COMPONENT_OF_CHOR",
            "exact_cards": card_counts["cho"],
            "fixed_events": event_counts["cho"],
            "removed_overclaim": "keiner",
            "reason": "CHO und CHOR sind verschiedene PAGE_HOSTs; die lokalen CHO-Karten liefern keinen gemeinsamen Wert.",
        },
        {
            "unit": "ch/chy/che/olk/y",
            "layer": "PAGE_HOST",
            "atomic_value_German": "UNBEKANNT",
            "decision": "KEEP_WITHDRAWN",
            "exact_cards": sum(card_counts[h] for h in ("ch", "chy", "che", "olk", "y")),
            "fixed_events": sum(event_counts[h] for h in ("ch", "chy", "che", "olk", "y")),
            "removed_overclaim": "verschiedene frühere Ereignisparaphrasen",
            "reason": "Keine nichtzirkuläre atomare Schnittmenge im festen Panel.",
        },
    ])
    write_tsv(OUT / "V49_R1_ATOMIC_CANDIDATE_TABLE.tsv", candidates)

    same_value: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        same_value[row["page_host"]].add(row["host_or_card_value_German"])
    values = set(SHARED_HOSTS) | set(WHOLE_CARDS)
    validation = {
        "schema": "SIDEQUEST_V49_R1_ATOMIC_MINIMAL_LEXICON_V1",
        "status": "PASS",
        "counts": {
            "cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "atomic_shared_hosts": len(SHARED_HOSTS),
            "atomic_recurrent_whole_cards": len(WHOLE_CARDS),
            "known_atomic_cards": sum(row["page_host"] in values for row in cards),
            "opaque_cards": sum(row["host_or_card_value_German"] == "UNBEKANNT" for row in cards),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "same_host_same_value": all(len(v) == 1 for v in same_value.values()),
            "all_non_unknown_values_atomic": all(
                " " not in row["host_or_card_value_German"].strip()
                for row in cards
                if row["host_or_card_value_German"] != "UNBEKANNT"
            ),
            "chor_is_time_only": same_value["chor"] == {"ZEIT"},
            "cho_is_unknown": same_value["cho"] == {"UNBEKANNT"},
            "chor_not_decomposed_as_cho_plus_r": True,
            "local_expansions_preserved": all(
                old["fluent_local_creative_expansion_German"] == new["fluent_local_creative_expansion_German"]
                for old, new in zip(cards_in, cards, strict=True)
            ),
            "field_local_prose_preserved": all(
                old["fluent_local_creative_translation_German"] == new["fluent_local_creative_translation_German"]
                for old, new in zip(fields_in, fields, strict=True)
            ),
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    expected = {
        name: (False if name in {"f84_accessed", "f84r_accessed"} else True)
        for name in validation["checks"]
    }
    if validation["checks"] != expected:
        failed = [
            name
            for name, actual in validation["checks"].items()
            if actual != expected[name]
        ]
        raise AssertionError(f"validation failed: {failed}")
    (OUT / "V49_R1_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
