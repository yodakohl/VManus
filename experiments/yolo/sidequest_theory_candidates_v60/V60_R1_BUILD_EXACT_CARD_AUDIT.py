#!/usr/bin/env python3
"""Build the V60 R1 exact-card audit from the canonical V59 R1 release.

The semantic lookup key is always the complete opaque joint-tuple ID.  Surface
spellings, formula components, and host coordinates are copied for audit only
and never participate in selection of a mnemonic.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V59 = ROOT / "experiments/yolo/sidequest_theory_candidates_v59"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v60"

CARD_SOURCE = V59 / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv"
EVENT_SOURCE = V59 / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_SOURCE = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
THEORY_SOURCE = V59 / "V59_R1_FINAL_WORKSHOP_EDITION_REPORT.md"

CARD_OUT = OUT / "V60_R1_REVISED_173_CARD_DICTIONARY.tsv"
EVENT_OUT = OUT / "V60_R1_REVISED_381_EVENT_LEDGER.tsv"
DECISION_OUT = OUT / "V60_R1_11_CARD_DECISIONS.tsv"
OCCURRENCE_OUT = OUT / "V60_R1_85_OCCURRENCE_AUDIT.tsv"
VALIDATION_OUT = OUT / "V60_R1_VALIDATION.json"


# The order is the frozen order in the V60 question.  Every entry is bound to
# exactly one complete V59 tuple ID; no other column is consulted for lookup.
DECISIONS = [
    {
        "canonical_card": "AIIN",
        "joint_tuple_id": "2f1c5e56e8f0ff459065",
        "selected_default_de": "Maß",
        "revised_mnemonic": "MASS?",
        "source_class": "Parameter",
        "rival_1_de": "Portion",
        "rival_2_de": "Vorgabe",
        "context_pressure": (
            "20 Vorkommen auf 7 Seiten und in allen 11 Prosarecords; "
            "6× FIRST, 9× MIDDLE, 5× LAST, stets NONCLOSE; zweimal OKY→AIIN. "
            "Der breite Anschlussdruck begünstigt einen frei einsetzbaren Parameter."
        ),
        "teaching_rule": (
            "Beim vollständigen Tuple nur ‚Maß‘ sagen; Einheit und Zahl aus dem "
            "bezeichneten Exemplar übernehmen, niemals aus einer sichtbaren Variante."
        ),
        "strongest_contradiction": (
            "Keines der 20 Ereignisse trägt selbst eine sichtbare Einheit oder Zahl; "
            "alle gleichlautenden Maß-Expansionen sind aus V59 geerbt und daher nicht unabhängig."
        ),
        "confidence_numeric": "0.78",
        "confidence_label": "EXPLORATORY_MEDIUM_HIGH",
        "revision_decision": "RETAIN",
    },
    {
        "canonical_card": "OKY",
        "joint_tuple_id": "276a7c2d74d1143446f4",
        "selected_default_de": "verwenden",
        "revised_mnemonic": "VERWENDEN?",
        "source_class": "Verb",
        "rival_1_de": "anwenden",
        "rival_2_de": "fortsetzen",
        "context_pressure": (
            "10 Vorkommen auf 5 Seiten/6 Records; 6× MIDDLE, 2× LAST, 1× FIRST, "
            "1× ONLY; zweimal OKEEY→OKY, zweimal OKY→AIIN und einmal OKY→AL. "
            "Das Tuple sitzt plausibel als ausführbarer Handlungspivot."
        ),
        "teaching_rule": (
            "‚verwenden‘ ist der ganze Kartenprompt; Material, Ziel und Art der Anwendung "
            "kommen ausschließlich aus dem lokalen Exemplar."
        ),
        "strongest_contradiction": (
            "Ein isoliertes und drei feldabschließende Vorkommen lassen ebenso eine "
            "Fortsetzungs- oder Freigabefunktion zu; die technische Rivalprosa ist nicht einheitlich."
        ),
        "confidence_numeric": "0.68",
        "confidence_label": "EXPLORATORY_MEDIUM",
        "revision_decision": "RETAIN",
    },
    {
        "canonical_card": "CTHY",
        "joint_tuple_id": "e0b630cb1b5df5e7105b",
        "selected_default_de": "bereit",
        "revised_mnemonic": "BEREIT?",
        "source_class": "Zustand",
        "rival_1_de": "fertig",
        "rival_2_de": "reif",
        "context_pressure": (
            "7 Vorkommen auf 3 Seiten/4 Records; 6× MIDDLE und 1× LAST, alle NONCLOSE; "
            "je einmal vor OR und AL sowie einmal nach AL. Der Zustandswert ist lokal anschlussfähig."
        ),
        "teaching_rule": (
            "‚bereit‘ als Zustand prüfen, nicht als Befehl lesen; was bereit ist, bestimmt das Exemplar."
        ),
        "strongest_contradiction": (
            "Nur ein Vorkommen steht unmittelbar vor OR; das feldletzte offene Vorkommen "
            "kann auch bloß eine Abschnittsmarke oder ein anderer Zustand sein."
        ),
        "confidence_numeric": "0.62",
        "confidence_label": "EXPLORATORY_MEDIUM",
        "revision_decision": "RETAIN",
    },
    {
        "canonical_card": "OR",
        "joint_tuple_id": "7a4bb8136330ee4e6e56",
        "selected_default_de": "Zubereitung",
        "revised_mnemonic": "ZUBEREITUNG?",
        "source_class": "Nomen",
        "rival_1_de": "Ansatz",
        "rival_2_de": "Flüssigkeit",
        "context_pressure": (
            "7 Vorkommen auf 3 Seiten/4 Records; 5× MIDDLE, 2× FIRST, alle NONCLOSE; "
            "ein CTHY→OR-Anschluss und ein OR→OR-Doppel. Ein wiederaufnehmbares Arbeitsnomen passt."
        ),
        "teaching_rule": (
            "Nur ‚Zubereitung‘ benennen; Zusammensetzung, Gefäß und Zustand bleiben im Exemplar. "
            "Das OR→OR-Doppel wird zweimal kopiert, nicht zu einer neuen Form verschmolzen."
        ),
        "strongest_contradiction": (
            "Die direkte Doppelung ergibt bei wörtlicher Komposition ‚Zubereitung Zubereitung‘; "
            "zwei Bio-Vorkommen stehen zudem feldinitial ohne sichtbare Wiederaufnahme."
        ),
        "confidence_numeric": "0.55",
        "confidence_label": "EXPLORATORY_MEDIUM_LOW",
        "revision_decision": "REVISE",
    },
    {
        "canonical_card": "AL",
        "joint_tuple_id": "dd0ecaf5e27d81befffc",
        "selected_default_de": "dorthin",
        "revised_mnemonic": "DORTHIN?",
        "source_class": "Relation",
        "rival_1_de": "hinein",
        "rival_2_de": "weiter",
        "context_pressure": (
            "10 Vorkommen auf 4 Seiten/6 Records; 4× FIRST, 3× MIDDLE, 2× LAST, 1× ONLY, "
            "alle NONCLOSE. Fünf Feldanfänge und Anschlüsse an OKY, CTHY und LCHE stützen eine Deixis."
        ),
        "teaching_rule": (
            "Bei der Exact-Card ‚dorthin‘ sagen und auf den im Exemplar aktiven Besitzer zeigen; "
            "kein Zielnomen in die Karte hineinlesen."
        ),
        "strongest_contradiction": (
            "Das Ziel ist in keinem der zehn Tuple-Ereignisse unabhängig identifiziert; "
            "besonders das ONLY-Feld kann ebenso eine selbständige Übergabeformel sein."
        ),
        "confidence_numeric": "0.60",
        "confidence_label": "EXPLORATORY_MEDIUM",
        "revision_decision": "REVISE",
    },
    {
        "canonical_card": "EY",
        "joint_tuple_id": "b5df9126607030b95175",
        "selected_default_de": "klar",
        "revised_mnemonic": "KLAR?",
        "source_class": "Zustand",
        "rival_1_de": "rein",
        "rival_2_de": "fertig",
        "context_pressure": (
            "4 Vorkommen auf 3 Seiten/3 Records, verteilt auf FIRST/MIDDLE/LAST und stets NONCLOSE. "
            "Die fehlende Schlussbindung erlaubt einen echten Zwischenzustand."
        ),
        "teaching_rule": (
            "‚klar‘ nur als prüfbaren Zustand merken; Flüssigkeit, Strom oder Ergebnis nicht mitsprechen."
        ),
        "strongest_contradiction": (
            "Vier geerbte Lokalexpansionen unterscheiden Transparenz, Reinheit und Fertigsein nicht; "
            "es fehlt ein unabhängiges Kontrastpaar."
        ),
        "confidence_numeric": "0.53",
        "confidence_label": "EXPLORATORY_MEDIUM_LOW",
        "revision_decision": "RETAIN",
    },
    {
        "canonical_card": "OLOR",
        "joint_tuple_id": "dec401773c1f0347793d",
        "selected_default_de": "vom Vorigen",
        "revised_mnemonic": "VOM VORIGEN?",
        "source_class": "Relation",
        "rival_1_de": "daraus",
        "rival_2_de": "zuvor",
        "context_pressure": (
            "2 Vorkommen auf 2 Seiten/2 Registern; einmal MIDDLE, einmal FIRST, beide NONCLOSE; "
            "beide werden unmittelbar von einer lokalen Weiterführungsform gefolgt."
        ),
        "teaching_rule": (
            "‚vom Vorigen‘ sprechen und den Antezedenten im Recordregister suchen; "
            "keinen Stoffnamen und keine Entnahmehandlung in der Karte ergänzen."
        ),
        "strongest_contradiction": (
            "Nur zwei Fälle tragen die Entscheidung; ob die Relation anaphorisch, räumlich oder "
            "zeitlich ist, wird allein durch die kreative V59-Prosa unterschieden."
        ),
        "confidence_numeric": "0.42",
        "confidence_label": "EXPLORATORY_LOW",
        "revision_decision": "REVISE",
    },
    {
        "canonical_card": "OTCHEY",
        "joint_tuple_id": "faf321940aed922846a9",
        "selected_default_de": "Anteil",
        "revised_mnemonic": "ANTEIL?",
        "source_class": "Nomen",
        "rival_1_de": "Portion",
        "rival_2_de": "Probe",
        "context_pressure": (
            "2 Vorkommen auf 2 Seiten/2 Registern; beide feldinitial und NONCLOSE. "
            "Danach folgen einmal ein konkreter Pflanzenteil und einmal OKEEY."
        ),
        "teaching_rule": (
            "Nur ‚Anteil‘ merken; ‚nimm‘ ist eine lokale Exemplaranweisung und kein stilles Verb der Karte."
        ),
        "strongest_contradiction": (
            "Zwei feldinitiale Fälle reichen nicht, um Anteil gegen Probe oder bloßen Abschnittsanfang "
            "zu trennen; die Auswahlhandlung ist unsichtbar."
        ),
        "confidence_numeric": "0.45",
        "confidence_label": "EXPLORATORY_LOW",
        "revision_decision": "REVISE",
    },
    {
        "canonical_card": "OKEEY",
        "joint_tuple_id": "0275fbf14e07935b0a45",
        "selected_default_de": "lauwarm",
        "revised_mnemonic": "LAUWARM?",
        "source_class": "Zustand",
        "rival_1_de": "warm",
        "rival_2_de": "temperiert",
        "context_pressure": (
            "7 rein biologische Vorkommen auf 3 Seiten/4 Records; 3× FIRST, 4× MIDDLE, alle NONCLOSE; "
            "zweimal vor OKY, zweimal vor OKE und einmal nach OTCHEY. Das bildet einen Zustands-Pivot."
        ),
        "teaching_rule": (
            "‚lauwarm‘ als lokalen Bio-Zustand lesen; weder Erwärmen noch Halten ist Teil des Kartenworts."
        ),
        "strongest_contradiction": (
            "Es gibt keinen unabhängigen Heiß/Kalt-Kontrast, und die nichtmedizinischen Lokalschritte "
            "tragen keine einheitliche Temperatur; die sieben V59-Expansionen sind vorgeprägt."
        ),
        "confidence_numeric": "0.58",
        "confidence_label": "EXPLORATORY_MEDIUM_LOW",
        "revision_decision": "REVISE",
    },
    {
        "canonical_card": "OKE",
        "joint_tuple_id": "7db18b2f0fb7ed0fcfd3",
        "selected_default_de": "spülen",
        "revised_mnemonic": "SPÜLEN?",
        "source_class": "Verb",
        "rival_1_de": "reinigen",
        "rival_2_de": "beenden",
        "context_pressure": (
            "8 rein biologische Vorkommen auf 2 Seiten/3 Records; 3× ONLY, 5× LAST und 8× TERMINAL; "
            "zweimal OKEEY→OKE, einmal nach einer lokalen Erstspülung. Das Prozessmotiv ist kohärent."
        ),
        "teaching_rule": (
            "‚spülen‘ nur als unsicheren Bio-Prompt sprechen; den formalen Feldschluss getrennt ausführen."
        ),
        "strongest_contradiction": (
            "Alle 8/8 Fälle sind vollständig mit CLOSE konfundiert; ‚beenden‘ erklärt die Position ohne "
            "jede Spülsemantik und ist formal sparsamer."
        ),
        "confidence_numeric": "0.35",
        "confidence_label": "EXPLORATORY_LOW",
        "revision_decision": "RETAIN",
    },
    {
        "canonical_card": "LCHE",
        "joint_tuple_id": "de7321bface5628e35d6",
        "selected_default_de": "ablassen",
        "revised_mnemonic": "ABLASSEN?",
        "source_class": "Verb",
        "rival_1_de": "sammeln",
        "rival_2_de": "beenden",
        "context_pressure": (
            "8 rein biologische Vorkommen auf 2 Seiten/3 Records; 5× ONLY, 3× LAST und 8× TERMINAL; "
            "einmal folgt LCHE auf AL, einmal stimmt der technische Ganzdefault ‚unten ablassen‘ überein."
        ),
        "teaching_rule": (
            "‚ablassen‘ nur im Bio-Deck merken; Zielgefäß und Richtung aus dem Exemplar nehmen und "
            "CLOSE weiterhin stumm halten."
        ),
        "strongest_contradiction": (
            "Alle 8/8 Fälle sind CLOSE-konfundiert, fünf sogar isoliert; OKE zeigt dieselbe Position mit "
            "anderer kreativer Lesung, ohne unabhängiges Merkmal zur Trennung."
        ),
        "confidence_numeric": "0.36",
        "confidence_label": "EXPLORATORY_LOW",
        "revision_decision": "RETAIN",
    },
]


EXPECTED_OCCURRENCES = {
    "AIIN": 20,
    "OKY": 10,
    "CTHY": 7,
    "OR": 7,
    "AL": 10,
    "EY": 4,
    "OLOR": 2,
    "OTCHEY": 2,
    "OKEEY": 7,
    "OKE": 8,
    "LCHE": 8,
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        assert reader.fieldnames is not None
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def field_position(index: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if index == 0:
        return "FIRST"
    if index == length - 1:
        return "LAST"
    return "MIDDLE"


def register_for(page: str) -> str:
    return "HERBAL" if page in {"f10r", "f11r", "f55v", "f56r"} else "BIOLOGICAL"


def compact_counts(counter: Counter[str], order: list[str] | None = None) -> str:
    keys = order if order is not None else sorted(counter)
    return "|".join(f"{key}:{counter[key]}" for key in keys if counter[key]) or "NONE"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    card_fields, cards = read_tsv(CARD_SOURCE)
    event_fields, events = read_tsv(EVENT_SOURCE)
    field_fields, fields = read_tsv(FIELD_SOURCE)

    assert len(cards) == 173
    assert len(events) == 381
    assert len(fields) == 135
    assert len({row["joint_tuple_id"] for row in cards}) == 173
    assert len({row["event_serial"] for row in events}) == 381
    assert len({row["field_id"] for row in fields}) == 135

    decision_by_id = {row["joint_tuple_id"]: row for row in DECISIONS}
    label_by_id = {row["joint_tuple_id"]: row["canonical_card"] for row in DECISIONS}
    assert len(decision_by_id) == 11
    assert [row["canonical_card"] for row in DECISIONS] == list(EXPECTED_OCCURRENCES)
    assert set(decision_by_id) <= {row["joint_tuple_id"] for row in cards}
    assert {row["source_class"] for row in DECISIONS} <= {
        "Nomen", "Verb", "Zustand", "Relation", "Parameter"
    }
    for row in DECISIONS:
        assert 1 <= len(row["selected_default_de"].split()) <= 2
        assert 1 <= len(row["rival_1_de"].split()) <= 2
        assert 1 <= len(row["rival_2_de"].split()) <= 2
        assert row["rival_1_de"].casefold() != row["selected_default_de"].casefold()
        assert row["rival_2_de"].casefold() != row["selected_default_de"].casefold()
        assert row["rival_1_de"].casefold() != row["rival_2_de"].casefold()

    cards_by_id = {row["joint_tuple_id"]: row for row in cards}
    fields_by_id = {row["field_id"]: row for row in fields}
    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)
        events_by_record[row["record_unit_id"]].append(row)
    assert set(events_by_field) == set(fields_by_id)
    for field_id, field_events in events_by_field.items():
        source_field = fields_by_id[field_id]
        assert len(field_events) == int(source_field["event_count"])
        assert " ".join(row["surface"] for row in field_events) == source_field["surface_sequence"]

    # Create strict V59-derived releases.  Among inherited columns, only the
    # exact-card mnemonic cell may differ.
    revised_cards: list[dict[str, str]] = []
    for source in cards:
        target = dict(source)
        if source["joint_tuple_id"] in decision_by_id:
            target["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = decision_by_id[
                source["joint_tuple_id"]
            ]["revised_mnemonic"]
        revised_cards.append(target)

    revised_events: list[dict[str, str]] = []
    for source in events:
        target = dict(source)
        if source["joint_tuple_id"] in decision_by_id:
            target["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = decision_by_id[
                source["joint_tuple_id"]
            ]["revised_mnemonic"]
        revised_events.append(target)

    write_tsv(CARD_OUT, card_fields, revised_cards)
    write_tsv(EVENT_OUT, event_fields, revised_events)

    revised_event_by_serial = {row["event_serial"]: row for row in revised_events}
    decision_rows: list[dict[str, str]] = []
    occurrence_rows: list[dict[str, str]] = []

    for decision in DECISIONS:
        tuple_id = decision["joint_tuple_id"]
        source_card = cards_by_id[tuple_id]
        card_events = [row for row in events if row["joint_tuple_id"] == tuple_id]
        expected = EXPECTED_OCCURRENCES[decision["canonical_card"]]
        assert len(card_events) == expected == int(source_card["occurrences"])

        positions: Counter[str] = Counter()
        terminals: Counter[str] = Counter()
        registers: Counter[str] = Counter()
        predecessor_classes: Counter[str] = Counter()
        successor_classes: Counter[str] = Counter()
        pages = sorted({row["page"] for row in card_events})
        records = sorted({row["record_unit_id"] for row in card_events})

        for event in card_events:
            field_events = events_by_field[event["field_id"]]
            event_index = next(
                index
                for index, candidate in enumerate(field_events)
                if candidate["event_serial"] == event["event_serial"]
            )
            record_events = events_by_record[event["record_unit_id"]]
            record_index = next(
                index
                for index, candidate in enumerate(record_events)
                if candidate["event_serial"] == event["event_serial"]
            )
            position = field_position(event_index, len(field_events))
            predecessor = field_events[event_index - 1] if event_index else None
            successor = (
                field_events[event_index + 1]
                if event_index + 1 < len(field_events)
                else None
            )
            positions[position] += 1
            terminals[event["terminal_status"]] += 1
            registers[register_for(event["page"])] += 1
            predecessor_classes[
                "BOUNDARY"
                if predecessor is None
                else label_by_id.get(predecessor["joint_tuple_id"], "OTHER_EXACT")
            ] += 1
            successor_classes[
                "BOUNDARY"
                if successor is None
                else label_by_id.get(successor["joint_tuple_id"], "OTHER_EXACT")
            ] += 1

            field_source = fields_by_id[event["field_id"]]
            occurrence_pressure = ";".join(
                [
                    f"REGISTER={register_for(event['page'])}",
                    f"FIELD_POSITION={position}",
                    f"FIELD_LENGTH={len(field_events)}",
                    f"TERMINAL={event['terminal_status']}",
                    "PREDECESSOR="
                    + (
                        "BOUNDARY"
                        if predecessor is None
                        else label_by_id.get(predecessor["joint_tuple_id"], "OTHER_EXACT")
                    ),
                    "SUCCESSOR="
                    + (
                        "BOUNDARY"
                        if successor is None
                        else label_by_id.get(successor["joint_tuple_id"], "OTHER_EXACT")
                    ),
                ]
            )
            occurrence_rows.append(
                {
                    "canonical_card": decision["canonical_card"],
                    "joint_tuple_id": tuple_id,
                    "selected_default_de": decision["selected_default_de"],
                    "source_class": decision["source_class"],
                    "event_serial": event["event_serial"],
                    "page": event["page"],
                    "register": register_for(event["page"]),
                    "locus": event["locus"],
                    "record": event["record"],
                    "record_unit_id": event["record_unit_id"],
                    "record_event_position": str(record_index + 1),
                    "record_event_count": str(len(record_events)),
                    "field_id": event["field_id"],
                    "field_position": position,
                    "field_event_position": str(event_index + 1),
                    "field_event_count": str(len(field_events)),
                    "terminal_status": event["terminal_status"],
                    "surface_audit_only": event["surface"],
                    "formal_formula_audit_only": event["formal_formula_opaque"],
                    "v59_mnemonic": event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                    "v60_mnemonic": revised_event_by_serial[event["event_serial"]][
                        "ATOMIC_OR_WHOLE_CARD_MNEMONIC"
                    ],
                    "predecessor_event_serial": "BOUNDARY"
                    if predecessor is None
                    else predecessor["event_serial"],
                    "predecessor_joint_tuple_id": "BOUNDARY"
                    if predecessor is None
                    else predecessor["joint_tuple_id"],
                    "predecessor_canonical_card": "BOUNDARY"
                    if predecessor is None
                    else label_by_id.get(predecessor["joint_tuple_id"], "OTHER_EXACT"),
                    "predecessor_local_expansion": "BOUNDARY"
                    if predecessor is None
                    else predecessor["LOCAL_IATROMEDICAL_EXPANSION"],
                    "current_local_iatromedical_expansion": event[
                        "LOCAL_IATROMEDICAL_EXPANSION"
                    ],
                    "current_nonmedical_rival": event["NONMEDICAL_RIVAL"],
                    "successor_event_serial": "BOUNDARY"
                    if successor is None
                    else successor["event_serial"],
                    "successor_joint_tuple_id": "BOUNDARY"
                    if successor is None
                    else successor["joint_tuple_id"],
                    "successor_canonical_card": "BOUNDARY"
                    if successor is None
                    else label_by_id.get(successor["joint_tuple_id"], "OTHER_EXACT"),
                    "successor_local_expansion": "BOUNDARY"
                    if successor is None
                    else successor["LOCAL_IATROMEDICAL_EXPANSION"],
                    "whole_field_local_expansion": field_source[
                        "LOCAL_IATROMEDICAL_EXPANSION"
                    ],
                    "whole_field_nonmedical_rival": field_source["NONMEDICAL_RIVAL"],
                    "occurrence_pressure": occurrence_pressure,
                    "card_context_pressure_summary": decision["context_pressure"],
                    "strongest_contradiction": decision["strongest_contradiction"],
                    "binding_rule": "EXACT_JOINT_TUPLE_ID_ONLY",
                }
            )

        revision_cost = (
            "ZERO: mnemonic label retained; 0 inherited dictionary/event cells changed"
            if decision["revision_decision"] == "RETAIN"
            else (
                f"LOW: 1 dictionary mnemonic cell + {expected} event mnemonic cells changed; "
                "formal values, scopes, expansions, rivals and statuses unchanged"
            )
        )
        decision_rows.append(
            {
                "canonical_card": decision["canonical_card"],
                "joint_tuple_id": tuple_id,
                "v59_mnemonic": source_card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                "selected_default_de": decision["selected_default_de"],
                "v60_mnemonic": decision["revised_mnemonic"],
                "source_class": decision["source_class"],
                "rival_1_de": decision["rival_1_de"],
                "rival_2_de": decision["rival_2_de"],
                "occurrences": str(len(card_events)),
                "pages": "|".join(pages),
                "page_count": str(len(pages)),
                "records": "|".join(records),
                "record_count": str(len(records)),
                "register_counts": compact_counts(
                    registers, ["HERBAL", "BIOLOGICAL"]
                ),
                "field_position_counts": compact_counts(
                    positions, ["FIRST", "MIDDLE", "LAST", "ONLY"]
                ),
                "terminal_status_counts": compact_counts(
                    terminals, ["NONCLOSE", "TERMINAL"]
                ),
                "predecessor_pressure": compact_counts(predecessor_classes),
                "successor_pressure": compact_counts(successor_classes),
                "context_pressure": decision["context_pressure"],
                "teaching_rule": decision["teaching_rule"],
                "strongest_contradiction": decision["strongest_contradiction"],
                "confidence_numeric": decision["confidence_numeric"],
                "confidence_label": decision["confidence_label"],
                "revision_decision": decision["revision_decision"],
                "revision_cost": revision_cost,
                "semantic_binding": "EXACT_JOINT_TUPLE_ID_ONLY",
            }
        )

    decision_fields = [
        "canonical_card",
        "joint_tuple_id",
        "v59_mnemonic",
        "selected_default_de",
        "v60_mnemonic",
        "source_class",
        "rival_1_de",
        "rival_2_de",
        "occurrences",
        "pages",
        "page_count",
        "records",
        "record_count",
        "register_counts",
        "field_position_counts",
        "terminal_status_counts",
        "predecessor_pressure",
        "successor_pressure",
        "context_pressure",
        "teaching_rule",
        "strongest_contradiction",
        "confidence_numeric",
        "confidence_label",
        "revision_decision",
        "revision_cost",
        "semantic_binding",
    ]
    occurrence_fields = [
        "canonical_card",
        "joint_tuple_id",
        "selected_default_de",
        "source_class",
        "event_serial",
        "page",
        "register",
        "locus",
        "record",
        "record_unit_id",
        "record_event_position",
        "record_event_count",
        "field_id",
        "field_position",
        "field_event_position",
        "field_event_count",
        "terminal_status",
        "surface_audit_only",
        "formal_formula_audit_only",
        "v59_mnemonic",
        "v60_mnemonic",
        "predecessor_event_serial",
        "predecessor_joint_tuple_id",
        "predecessor_canonical_card",
        "predecessor_local_expansion",
        "current_local_iatromedical_expansion",
        "current_nonmedical_rival",
        "successor_event_serial",
        "successor_joint_tuple_id",
        "successor_canonical_card",
        "successor_local_expansion",
        "whole_field_local_expansion",
        "whole_field_nonmedical_rival",
        "occurrence_pressure",
        "card_context_pressure_summary",
        "strongest_contradiction",
        "binding_rule",
    ]
    occurrence_rows.sort(key=lambda row: int(row["event_serial"]))
    write_tsv(DECISION_OUT, decision_fields, decision_rows)
    write_tsv(OCCURRENCE_OUT, occurrence_fields, occurrence_rows)

    # Exact delta audit: every inherited cell except the mnemonic is frozen.
    card_differences: list[dict[str, str]] = []
    for before, after in zip(cards, revised_cards, strict=True):
        assert before["joint_tuple_id"] == after["joint_tuple_id"]
        changed = [field for field in card_fields if before[field] != after[field]]
        assert set(changed) <= {"ATOMIC_OR_WHOLE_CARD_MNEMONIC"}
        if changed:
            card_differences.append(
                {
                    "joint_tuple_id": before["joint_tuple_id"],
                    "from": before["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                    "to": after["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                }
            )
    event_differences: list[dict[str, str]] = []
    for before, after in zip(events, revised_events, strict=True):
        assert before["event_serial"] == after["event_serial"]
        changed = [field for field in event_fields if before[field] != after[field]]
        assert set(changed) <= {"ATOMIC_OR_WHOLE_CARD_MNEMONIC"}
        if changed:
            event_differences.append(
                {
                    "event_serial": before["event_serial"],
                    "joint_tuple_id": before["joint_tuple_id"],
                    "from": before["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                    "to": after["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                }
            )

    target_source_events = [
        row for row in events if row["joint_tuple_id"] in decision_by_id
    ]
    assert len(target_source_events) == 85
    assert len(occurrence_rows) == 85
    assert {row["event_serial"] for row in occurrence_rows} == {
        row["event_serial"] for row in target_source_events
    }
    assert Counter(row["canonical_card"] for row in occurrence_rows) == Counter(
        EXPECTED_OCCURRENCES
    )
    assert len(card_differences) == 5
    assert len(event_differences) == 28
    assert sum(row["revision_decision"] == "RETAIN" for row in DECISIONS) == 6
    assert sum(row["revision_decision"] == "REVISE" for row in DECISIONS) == 5
    assert sum(
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
        for row in revised_events
    ) == 85
    assert sum(
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
        for row in revised_cards
    ) == 11
    audited_fields = {row["field_id"] for row in occurrence_rows}
    audited_records = {row["record_unit_id"] for row in occurrence_rows}
    audited_pages = {row["page"] for row in occurrence_rows}
    audited_registers = Counter(row["register"] for row in occurrence_rows)
    audited_positions = Counter(row["field_position"] for row in occurrence_rows)
    audited_terminal_status = Counter(
        row["terminal_status"] for row in occurrence_rows
    )
    assert len(audited_fields) == 57
    assert len(audited_records) == 11
    assert len(audited_pages) == 7
    assert audited_registers == {"HERBAL": 24, "BIOLOGICAL": 61}
    assert audited_positions == {"FIRST": 20, "MIDDLE": 36, "LAST": 19, "ONLY": 10}
    assert audited_terminal_status == {"NONCLOSE": 69, "TERMINAL": 16}
    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    assert {row["page"] for row in revised_events} == allowed_pages
    assert {row["page"] for row in fields} == allowed_pages

    validation = {
        "status": "PASS",
        "model": "V60_R1_EXACT_JOINT_TUPLE_MNEMONIC_AUDIT",
        "counts": {
            "canonical_exact_cards_audited": 11,
            "canonical_occurrences_audited": 85,
            "revised_dictionary_rows": len(revised_cards),
            "revised_event_rows": len(revised_events),
            "frozen_field_rows_used_for_context": len(fields),
            "retained_mnemonics": 6,
            "revised_mnemonics": 5,
            "changed_dictionary_mnemonic_cells": len(card_differences),
            "changed_event_mnemonic_cells": len(event_differences),
            "unchanged_dictionary_rows": len(cards) - len(card_differences),
            "unchanged_event_rows": len(events) - len(event_differences),
            "nonunknown_mnemonic_dictionary_rows": 11,
            "nonunknown_mnemonic_event_rows": 85,
            "audited_fields": len(audited_fields),
            "audited_records": len(audited_records),
            "audited_pages": len(audited_pages),
            "audited_herbal_occurrences": audited_registers["HERBAL"],
            "audited_biological_occurrences": audited_registers["BIOLOGICAL"],
            "audited_nonclose_occurrences": audited_terminal_status["NONCLOSE"],
            "audited_terminal_occurrences": audited_terminal_status["TERMINAL"],
        },
        "occurrences_by_card": EXPECTED_OCCURRENCES,
        "selected_defaults": {
            row["canonical_card"]: row["selected_default_de"] for row in DECISIONS
        },
        "changed_cards": card_differences,
        "assertions": {
            "semantic_lookup_uses_complete_joint_tuple_id_only": "PASS",
            "surface_is_audit_only": "PASS",
            "formal_components_do_not_transfer_meaning": "PASS",
            "all_85_occurrences_listed_once": "PASS",
            "one_short_default_and_two_distinct_rivals_per_card": "PASS",
            "source_class_is_one_of_five_requested_classes": "PASS",
            "all_inherited_cells_except_mnemonic_are_identical": "PASS",
            "all_other_v59_card_and_event_values_remain_frozen": "PASS",
            "v59_field_context_is_read_only_and_unchanged": "PASS",
            "no_new_pages": "PASS",
            "creative_defaults_are_not_semantic_proof": "PASS",
        },
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [CARD_SOURCE, EVENT_SOURCE, FIELD_SOURCE, THEORY_SOURCE]
        },
        "output_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [CARD_OUT, EVENT_OUT, DECISION_OUT, OCCURRENCE_OUT]
        },
    }
    VALIDATION_OUT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "counts": validation["counts"]}))


if __name__ == "__main__":
    main()
