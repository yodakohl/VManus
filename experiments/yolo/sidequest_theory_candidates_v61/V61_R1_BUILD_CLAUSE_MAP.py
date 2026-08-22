#!/usr/bin/env python3
"""Build the V61 R1 physical-line boundary inventory and clause map.

This is an explicitly creative segmentation of the selected V60 event ledger.
It adds no card meaning.  Physical loci, field closure, exact selected mnemonic
labels, and inherited local exemplars remain separate columns throughout.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
YOLO = ROOT / "experiments/yolo"
V59 = YOLO / "sidequest_theory_candidates_v59"
V60 = YOLO / "sidequest_theory_candidates_v60"
OUT = YOLO / "sidequest_theory_candidates_v61"

ROUTE = ROOT / "VOYNICH_CURRENT_ROUTE.md"
ROLES = YOLO / "SIDEQUEST_FOUR_AGENT_BACKGROUNDS.md"
PROTOCOL = YOLO / "SIDEQUEST_V60_V69_ITERATION_PROTOCOL.md"
SELECTION = V60 / "V60_FOUR_ROLE_SELECTION.md"
EVENT_SOURCE = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"
FIELD_SOURCE = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
RECORD_SOURCE = V59 / "V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv"

BOUNDARY_OUT = OUT / "V61_R1_46_LINE_BOUNDARY_INVENTORY.tsv"
CLAUSE_OUT = OUT / "V61_R1_116_STATEMENT_CLAUSE_MAP.tsv"
RECORD_OUT = OUT / "V61_R1_11_RECORD_CONTINUATION_SUMMARY.tsv"
VALIDATION_OUT = OUT / "V61_R1_VALIDATION.json"


CLASSES = {
    "CONTINUE_SAME_CLAUSE",
    "START_NEW_CLAUSE",
    "RESUME_ACTIVE_ITEM",
    "NEXT_PARALLEL_CELL",
    "UNRESOLVED",
}

SELECTED_DECK = {
    "MASS?",
    "ANWENDEN?",
    "BEREIT?",
    "ANSATZ?",
    "ZIEL?",
    "KLAR?",
    "VORIGES?",
    "ANTEIL?",
    "TEMPERIEREN?",
    "SPÜLEN?",
    "ABLASSEN?",
}


def D(
    record: str,
    from_locus: str,
    to_locus: str,
    classification: str,
    rationale: str,
    strongest_alternative: str,
) -> dict[str, str]:
    return {
        "record_unit_id": record,
        "from_locus": from_locus,
        "to_locus": to_locus,
        "classification": classification,
        "rationale": rationale,
        "strongest_alternative": strongest_alternative,
    }


# One frozen R1 judgment for every derived within-record physical-line boundary.
# The keyed fields and exact mnemonic labels are checked against the sources
# below; the prose is a local workflow rationale, never a new card gloss.
BOUNDARY_DECISIONS = [
    D("H1", "f10r.2", "f10r.5", "RESUME_ACTIVE_ITEM",
      "F001 bleibt OPEN; F002 greift die frisch bereitete und vorige Zubereitung wieder auf, beginnt aber einen zweiten Gebrauch.",
      "START_NEW_CLAUSE: F002 könnte ein unabhängiger zweiter Rezeptzusatz sein."),
    D("H2", "f10r.6", "f10r.8", "RESUME_ACTIVE_ITEM",
      "Beide Felder sind OPEN; F004 kehrt mit ANSATZ?, VORIGES? und MASS? zum in F003 begonnenen Arbeitsbestand zurück.",
      "NEXT_PARALLEL_CELL: die abweichende Sammelzeit kann eine zweite Erntevariante eröffnen."),
    D("H2", "f10r.8", "f10r.9", "NEXT_PARALLEL_CELL",
      "F004 nennt Sammeln vor der Blüte, F005 beginnt mit geöffneter Blüte und einem ANSATZ?-Doppel; das liest sich als Parallelcharge.",
      "CONTINUE_SAME_CLAUSE: beide OPEN-Felder könnten eine einzige lange Ernte-/Zubereitungsanweisung sein."),
    D("H3", "f11r.1", "f11r.4", "RESUME_ACTIVE_ITEM",
      "Nach dem terminalen Auszug bleibt F007 OPEN und hält die Blütenkrone zurück; F008 nimmt denselben Bildbesitzer als Portion wieder auf.",
      "START_NEW_CLAUSE: F008 kann eine eigenständige Anwendung des Simplex beginnen."),
    D("H3", "f11r.4", "f11r.7", "NEXT_PARALLEL_CELL",
      "F008 endet OPEN nach Maß und Aufbinden; F009 eröffnet eine eigens bereitete warme Auflage als parallele Anwendung.",
      "CONTINUE_SAME_CLAUSE: F009 könnte die in F008 nur knapp bezeichnete Auflage ausführen."),
    D("H4", "f55v.5", "f55v.11", "START_NEW_CLAUSE",
      "F011 ist TERMINAL; F012 beginnt ausdrücklich den zweiten Arzneigebrauch und schließt ebenfalls formal.",
      "NEXT_PARALLEL_CELL: beide Linien können als zwei gleichrangige Fraktionen desselben Blattes gelten."),
    D("H5", "f56r.5", "f56r.7", "CONTINUE_SAME_CLAUSE",
      "F014 bleibt nach Sammeln, Wurzel und MASS? OPEN; F015 setzt Zusatz, Auszug, ANWENDEN? und ZIEL? unmittelbar fort.",
      "RESUME_ACTIVE_ITEM: F015 könnte eine neue Klausel mit demselben Pflanzenteil beginnen."),
    D("H5", "f56r.7", "f56r.8", "RESUME_ACTIVE_ITEM",
      "F015 endet OPEN am Ziel; F016 identifiziert den Bild-Simplex erneut, setzt ANWENDEN? ein und schließt die Anwendung.",
      "CONTINUE_SAME_CLAUSE: der Zeilenreset kann bloßer Reflow innerhalb derselben Anwendung sein."),
    D("H5", "f56r.8", "f56r.12", "NEXT_PARALLEL_CELL",
      "F016 ist TERMINAL; F017 wechselt zu Samen-/Knospenkopf und getrocknetem Blatt als nächster Teilzelle.",
      "START_NEW_CLAUSE: die neue Linie kann statt einer Parallelzelle einen neuen Rezeptabschnitt eröffnen."),
    D("H5", "f56r.12", "f56r.13", "RESUME_ACTIVE_ITEM",
      "F017 bleibt nach dem Trocknen OPEN; F018 gebraucht eine frische Arznei und verwahrt den Rest desselben Bildbesitzers.",
      "START_NEW_CLAUSE: frisch und getrocknet können zwei unabhängige Zubereitungen bezeichnen."),
    D("H5", "f56r.13", "f56r.18", "NEXT_PARALLEL_CELL",
      "F018 endet OPEN, doch F019 beginnt erneut mit dem folgenden Zusatz und einer Honigbereitung; das setzt den Teilekatalog parallel fort.",
      "RESUME_ACTIVE_ITEM: F019 kann den in F018 verwahrten Rest wieder aufnehmen."),
    D("H5", "f56r.18", "f56r.19", "NEXT_PARALLEL_CELL",
      "Auf die Honigzubereitung folgt feldinitial ANTEIL? mit Blüte und MASS?; das ist die knappste Lesung als nächste Teilzelle.",
      "CONTINUE_SAME_CLAUSE: F020 könnte nur den Anteil der vorherigen Honigmischung spezifizieren."),
    D("B1", "f81v.2", "f81v.7", "CONTINUE_SAME_CLAUSE",
      "F022 bleibt OPEN am Öl; F023 startet mit VORIGES?, setzt zwei MASS?-Slots und die verbundenen Läufe ein und endet TERMINAL.",
      "RESUME_ACTIVE_ITEM: F023 kann eine neue Klausel mit demselben Ansatz sein."),
    D("B1", "f81v.7", "f81v.17", "CONTINUE_SAME_CLAUSE",
      "F024 besteht als OPEN-Feld nur aus der Wiederaufnahme der vorigen Zubereitung; F025 liefert das warme Halten und den Schluss.",
      "RESUME_ACTIVE_ITEM: die minimale F024 kann ein Verweisfeld vor einer neuen Klausel sein."),
    D("B1", "f81v.17", "f81v.18", "NEXT_PARALLEL_CELL",
      "F028 bleibt nach Füllen und Abkühlen OPEN; die nächste Linie beginnt eine Folge kurzer Heiz-, Stand- und Spülzellen ohne exakten Rückverweis.",
      "START_NEW_CLAUSE: statt Parallelzellen kann hier ein neuer Prozessabschnitt beginnen."),
    D("B1", "f81v.18", "f81v.21", "START_NEW_CLAUSE",
      "F033 bleibt zwar OPEN, beendet lokal aber die Anwendung; F034 beginnt ausdrücklich eine neue Spülung mit Warmwasser.",
      "NEXT_PARALLEL_CELL: Anwendung und Spülung können gleichrangige Workcells sein."),
    D("B1", "f81v.21", "f81v.24", "NEXT_PARALLEL_CELL",
      "F036 endet OPEN am unteren Ablauf; f81v.24 beginnt eine neue Suite aus Füllen, Temperieren und Zielstation.",
      "CONTINUE_SAME_CLAUSE: dieselbe Apparatur kann über den Zeilenreset weiterlaufen."),
    D("B1", "f81v.24", "f81v.27", "CONTINUE_SAME_CLAUSE",
      "F040 ist das offene Füllkommando; F041 setzt Anwendung, Klarheit und Absetzen fort und schließt den Vorgang.",
      "NEXT_PARALLEL_CELL: F041 kann eine neue Zielzelle nach dem Füllen sein."),
    D("B2", "f82r.2", "f82r.3", "CONTINUE_SAME_CLAUSE",
      "F048 bleibt nach dem Wechsel zum nächsten Becken OPEN; F049 temperiert und klärt genau diesen fortgesetzten Lauf bis TERMINAL.",
      "RESUME_ACTIVE_ITEM: F049 kann eine neue Klausel am zweiten Becken sein."),
    D("B2", "f82r.3", "f82r.4", "CONTINUE_SAME_CLAUSE",
      "F050 bleibt OPEN, fährt am zweiten Lauf fort und beginnt den nächsten Posten; F051 beginnt denselben Posten unter gleicher Einstellung und schließt ihn.",
      "RESUME_ACTIVE_ITEM: der doppelte Postenbeginn kann absichtliche Wiederaufnahme statt echter Satzfortsetzung sein."),
    D("B2", "f82r.4", "f82r.7", "START_NEW_CLAUSE",
      "F052 endet OPEN nach ANWENDEN?; F053 beginnt mit sauberem Wasser eine neue, terminale Nachfüllphase.",
      "NEXT_PARALLEL_CELL: Anwendung und Nachfüllen können benachbarte eigenständige Workcells sein."),
    D("B2", "f82r.7", "f82r.19", "UNRESOLVED",
      "F056 bleibt nach TEMPERIEREN?, ANWENDEN? und KLAR? OPEN; F057 beginnt einen gemessenen Badeposten, aber ohne exakten Rückverweis.",
      "CONTINUE_SAME_CLAUSE: die klare Flüssigkeit aus F056 kann unmittelbar in F057 dosiert werden."),
    D("B2", "f82r.19", "f82r.23", "CONTINUE_SAME_CLAUSE",
      "F058 zieht die klare Flüssigkeit in einem OPEN-Feld ab; F059 beginnt mit KLAR?, temperiert, misst und schließt den Tauchgang.",
      "RESUME_ACTIVE_ITEM: F059 kann eine neue Verwendung der zuvor abgezogenen Flüssigkeit sein."),
    D("B2", "f82r.23", "f82r.26", "START_NEW_CLAUSE",
      "F061 ist formal OPEN, lokal aber das Schließen des unteren Ablaufs; F062 beginnt ausdrücklich die nächste Spülung.",
      "CONTINUE_SAME_CLAUSE: die Apparaturhandlung kann trotz lokalem Phasenende ein durchgehender Zyklus sein."),
    D("B2", "f82r.26", "f82r.27", "CONTINUE_SAME_CLAUSE",
      "F063 bleibt nach ZIEL?, MASS?, neuem Posten und Warmwasser OPEN; F064 zieht den so vorbereiteten Bestand ab und schließt.",
      "NEXT_PARALLEL_CELL: F064 kann die erste von sieben unabhängigen Schlussvarianten sein."),
    D("B3", "f83r.3", "f83r.6", "RESUME_ACTIVE_ITEM",
      "F074 bleibt nach nächstem Posten, Ablauf und deiktischem Ansatz OPEN; F075 nimmt den aktiven Lauf mit einer Reinigung wieder auf.",
      "CONTINUE_SAME_CLAUSE: Reinigung kann der direkte nächste Bestandteil des begonnenen Postens sein."),
    D("B3", "f83r.6", "f83r.8", "RESUME_ACTIVE_ITEM",
      "F079 ist ein OPENes ANWENDEN?-Feld; F080 füllt und klärt den weiter aktiven Bestand in einer neuen Klausel.",
      "START_NEW_CLAUSE: F080 kann einen unabhängigen Gefäßposten beginnen."),
    D("B3", "f83r.8", "f83r.11", "RESUME_ACTIVE_ITEM",
      "F081 bleibt nach Anwendung, Rühren und Abkühlen OPEN; F082 nimmt den nun bereiteten Ansatz auf und lässt ihn stehen.",
      "CONTINUE_SAME_CLAUSE: F082 kann ohne Klauselreset der Schlusssatzteil von F081 sein."),
    D("B3", "f83r.11", "f83r.14", "CONTINUE_SAME_CLAUSE",
      "F086 lässt den Ablauf in einem OPEN-Feld schließen; F087 liefert Abkühlen und formalen Schluss derselben Phase.",
      "NEXT_PARALLEL_CELL: Abkühlen kann eine unabhängige kurze Zelle sein."),
    D("B3", "f83r.14", "f83r.15", "CONTINUE_SAME_CLAUSE",
      "F092 bleibt nach Postenbeginn, BEREIT?, ZIEL? und aktiver Portion OPEN; F093 setzt Maß, Zeit, Wasser, Ziel und Rückstand bis TERMINAL fort.",
      "RESUME_ACTIVE_ITEM: F093 kann dieselben Slots in einer neuen Chargenklausel wiederaufnehmen."),
    D("B3", "f83r.15", "f83r.16", "NEXT_PARALLEL_CELL",
      "F095 ist mit ABLASSEN? TERMINAL; die nächste Linie startet selbständige Reinigungs-, Heiz- und Mischzellen.",
      "START_NEW_CLAUSE: die neue Linie kann ein übergeordnetes Prozesskapitel statt eine Parallelzelle beginnen."),
    D("B3", "f83r.16", "f83r.20", "CONTINUE_SAME_CLAUSE",
      "F098 bleibt nach Becken, Mischen, Dosieren, BEREIT? und klarem Strom OPEN; F099 lässt denselben Bestand absetzen und schließt.",
      "NEXT_PARALLEL_CELL: F099 kann eine eigenständige Absetzzelle sein."),
    D("B3", "f83r.20", "f83r.22", "CONTINUE_SAME_CLAUSE",
      "F103 endet OPEN mit ANWENDEN? und MASS?; F104 zieht die klare Portion ab, mischt gleiche Teile und schließt.",
      "RESUME_ACTIVE_ITEM: F104 kann eine neue Klausel mit der abgemessenen Portion sein."),
    D("B3", "f83r.22", "f83r.24", "START_NEW_CLAUSE",
      "F107 ist TERMINAL; F108 bildet eine neue vollständige Bereitschafts-, Bearbeitungs- und Beckenanweisung.",
      "NEXT_PARALLEL_CELL: F108 kann die letzte gleichrangige Stationszelle sein."),
    D("B4", "f83r.25", "f83r.26", "CONTINUE_SAME_CLAUSE",
      "F111 bleibt nach Rühren und Richtung zum Ablauf OPEN; F112 entnimmt ANTEIL?, temperiert, wendet an und schließt die Phase.",
      "RESUME_ACTIVE_ITEM: F112 kann eine neue Anwendungsklausel am gleichen Bestand sein."),
    D("B4", "f83r.26", "f83r.27", "NEXT_PARALLEL_CELL",
      "F113 ist TERMINAL; F114 beginnt eine parallele Tuch-, Misch- und Badezelle, gefolgt von zwei weiteren Filterschlüssen.",
      "START_NEW_CLAUSE: f83r.27 kann ein eigener Filtrationsabschnitt sein."),
    D("B4", "f83r.27", "f83r.28", "NEXT_PARALLEL_CELL",
      "F116 ist TERMINAL; F117 startet mit MASS?, Wärme, erster Öffnung und SPÜLEN? eine neue kurze Workcell-Suite.",
      "START_NEW_CLAUSE: der neue Parametersatz kann eine neue Prozessphase eröffnen."),
    D("B4", "f83r.28", "f83r.35", "START_NEW_CLAUSE",
      "F119 schließt den Kochschritt TERMINAL; F120 beginnt einen neuen gemessenen warmen Gefäßposten und bleibt OPEN.",
      "NEXT_PARALLEL_CELL: F120 kann nur die nächste gleichrangige Charge sein."),
    D("B4", "f83r.35", "f83r.37", "CONTINUE_SAME_CLAUSE",
      "F120 bleibt nach Maß, Wärme, Gefäß, Zugabe und Rühren OPEN; F121 sagt ausdrücklich voriger Ansatz und schließt mit Waschen.",
      "RESUME_ACTIVE_ITEM: der explizite Rückgriff kann eine neue Klausel statt unmittelbare Fortsetzung markieren."),
    D("B4", "f83r.37", "f83r.38", "START_NEW_CLAUSE",
      "F123 ist TERMINAL; F124 beginnt mit ANSATZ? eine neue unmittelbare Anwendung und schließt wieder.",
      "NEXT_PARALLEL_CELL: beide können benachbarte Abschlusszellen desselben Durchgangs sein."),
    D("B4", "f83r.38", "f83r.39", "START_NEW_CLAUSE",
      "F124 ist TERMINAL; F125 eröffnet eine neue gemessene Klarheits-/Dauerklausel und bleibt OPEN.",
      "RESUME_ACTIVE_ITEM: F125 kann den soeben verwendeten Ansatz erneut prüfen."),
    D("B4", "f83r.39", "f83r.41", "CONTINUE_SAME_CLAUSE",
      "F125 bleibt nach KLAR?, Anteil und Dauer OPEN; F126 öffnet danach den oberen Lauf, lässt ab und schließt.",
      "NEXT_PARALLEL_CELL: F126 kann eine unabhängige Ablasszelle sein."),
    D("B4", "f83r.41", "f83r.44", "CONTINUE_SAME_CLAUSE",
      "F127 bleibt nach unterem Becken und ZIEL? OPEN; F128 gießt warmes Wasser ein und bringt genau diese Zielphase zum Schluss.",
      "RESUME_ACTIVE_ITEM: F128 kann eine neue Nachfüllklausel am gleichen Becken sein."),
    D("B5", "f83r.47", "f83r.48", "CONTINUE_SAME_CLAUSE",
      "F131 besteht als OPEN-Feld nur aus einer Dauer; F132 ergänzt Ziel, vorigen Bestand, Wärme und MASS? ohne formalen Schluss.",
      "RESUME_ACTIVE_ITEM: die Dauer kann als eigener Merkslot vor einer neuen Klausel stehen."),
    D("B5", "f83r.48", "f83r.49", "CONTINUE_SAME_CLAUSE",
      "F132 bleibt am vorgeschriebenen Maß OPEN; F133 beginnt mit der vorigen Zubereitung, nennt die zweite Öffnung und rührt weiter.",
      "RESUME_ACTIVE_ITEM: der Rückverweis kann einen neuen Stationssatz eröffnen."),
    D("B6", "f83r.52", "f83r.54", "CONTINUE_SAME_CLAUSE",
      "F134 bleibt nach erster Öffnung und voriger Zubereitung OPEN; F135 setzt MASS?, Weiterführung, Tuch, Portion und Ziel fort.",
      "RESUME_ACTIVE_ITEM: F135 kann die Ausführung einer vorher nur eingerichteten Station als neue Klausel sein."),
]


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


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _, events = read_tsv(EVENT_SOURCE)
    _, fields = read_tsv(FIELD_SOURCE)
    _, all_record_texts = read_tsv(RECORD_SOURCE)
    record_texts = [
        row
        for row in all_record_texts
        if row["module"] in {"HERBAL_RECORD", "BIOLOGICAL_RECORD"}
    ]

    assert len(events) == 381
    assert len(fields) == 135
    assert len(record_texts) == 11
    assert len({row["event_serial"] for row in events}) == 381
    assert len({row["field_id"] for row in fields}) == 135
    assert {row["unit_id"] for row in record_texts} == {
        "H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"
    }

    record_order = [row["unit_id"] for row in record_texts]
    record_rank = {record: index for index, record in enumerate(record_order)}
    fields.sort(key=lambda row: int(row["field_serial"]))
    events.sort(key=lambda row: int(row["event_serial"]))
    record_text_by_id = {row["unit_id"]: row for row in record_texts}
    field_by_id = {row["field_id"]: row for row in fields}

    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_field[event["field_id"]].append(event)
    assert set(events_by_field) == set(field_by_id)
    for field in fields:
        field_events = events_by_field[field["field_id"]]
        assert len(field_events) == int(field["event_count"])
        assert " ".join(row["surface"] for row in field_events) == field["surface_sequence"]

    selected_nonunknown = {
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        for row in events
        if row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
    }
    assert selected_nonunknown == SELECTED_DECK
    assert sum(
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN" for row in events
    ) == 85

    fields_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    fields_by_record_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for field in fields:
        fields_by_record[field["record_unit_id"]].append(field)
        fields_by_record_locus[(field["record_unit_id"], field["locus"])].append(field)

    derived_boundaries: list[dict[str, object]] = []
    for record in record_order:
        record_fields = fields_by_record[record]
        loci = unique([row["locus"] for row in record_fields])
        for ordinal, (from_locus, to_locus) in enumerate(zip(loci, loci[1:]), 1):
            from_fields = fields_by_record_locus[(record, from_locus)]
            to_fields = fields_by_record_locus[(record, to_locus)]
            derived_boundaries.append(
                {
                    "record_unit_id": record,
                    "boundary_ordinal_in_record": ordinal,
                    "from_locus": from_locus,
                    "to_locus": to_locus,
                    "from_fields": from_fields,
                    "to_fields": to_fields,
                    "from_last_field": from_fields[-1],
                    "to_first_field": to_fields[0],
                }
            )

    decision_by_key = {
        (row["record_unit_id"], row["from_locus"], row["to_locus"]): row
        for row in BOUNDARY_DECISIONS
    }
    derived_keys = {
        (row["record_unit_id"], row["from_locus"], row["to_locus"])
        for row in derived_boundaries
    }
    assert len(derived_boundaries) == 46
    assert len(decision_by_key) == 46
    assert derived_keys == set(decision_by_key)
    assert {row["classification"] for row in BOUNDARY_DECISIONS} == CLASSES

    def field_skeleton(field: dict[str, str]) -> str:
        mnemonics = [
            event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
            for event in events_by_field[field["field_id"]]
            if event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
        ]
        return " ".join(mnemonics) if mnemonics else "∅"

    # Union only line boundaries explicitly classified as one continuing
    # clause.  Every other boundary starts a fresh statement in this edition.
    parent = {field["field_id"]: field["field_id"] for field in fields}

    def find(field_id: str) -> str:
        while parent[field_id] != field_id:
            parent[field_id] = parent[parent[field_id]]
            field_id = parent[field_id]
        return field_id

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for boundary in derived_boundaries:
        key = (
            str(boundary["record_unit_id"]),
            str(boundary["from_locus"]),
            str(boundary["to_locus"]),
        )
        decision = decision_by_key[key]
        if decision["classification"] == "CONTINUE_SAME_CLAUSE":
            union(
                boundary["from_last_field"]["field_id"],  # type: ignore[index]
                boundary["to_first_field"]["field_id"],  # type: ignore[index]
            )

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for field in fields:
        groups[find(field["field_id"])].append(field)
    ordered_groups = sorted(groups.values(), key=lambda group: int(group[0]["field_serial"]))
    assert len(ordered_groups) == 116

    # Assign deterministic statement IDs in each record.
    statement_id_by_field: dict[str, str] = {}
    statement_groups: list[tuple[str, list[dict[str, str]]]] = []
    statement_counter: Counter[str] = Counter()
    for group in ordered_groups:
        records = {field["record_unit_id"] for field in group}
        assert len(records) == 1
        record = next(iter(records))
        statement_counter[record] += 1
        statement_id = f"{record}-S{statement_counter[record]:03d}"
        statement_groups.append((statement_id, group))
        for field in group:
            statement_id_by_field[field["field_id"]] = statement_id

    boundary_rows: list[dict[str, str]] = []
    boundary_meta_by_id: dict[str, dict[str, str]] = {}
    boundary_by_from_field: dict[str, dict[str, str]] = {}
    boundary_by_to_field: dict[str, dict[str, str]] = {}
    for boundary in derived_boundaries:
        record = str(boundary["record_unit_id"])
        ordinal = int(boundary["boundary_ordinal_in_record"])
        boundary_id = f"{record}-LB{ordinal:02d}"
        key = (record, str(boundary["from_locus"]), str(boundary["to_locus"]))
        decision = decision_by_key[key]
        from_fields = boundary["from_fields"]  # type: ignore[assignment]
        to_fields = boundary["to_fields"]  # type: ignore[assignment]
        from_last = boundary["from_last_field"]  # type: ignore[assignment]
        to_first = boundary["to_first_field"]  # type: ignore[assignment]
        from_statement = statement_id_by_field[from_last["field_id"]]
        to_statement = statement_id_by_field[to_first["field_id"]]
        if decision["classification"] == "CONTINUE_SAME_CLAUSE":
            assert from_statement == to_statement
        else:
            assert from_statement != to_statement

        row = {
            "boundary_id": boundary_id,
            "record_unit_id": record,
            "page": from_last["page"],
            "boundary_ordinal_in_record": str(ordinal),
            "from_locus": str(boundary["from_locus"]),
            "to_locus": str(boundary["to_locus"]),
            "from_locus_fields": "|".join(field["field_id"] for field in from_fields),
            "to_locus_fields": "|".join(field["field_id"] for field in to_fields),
            "from_locus_closure_pattern": "|".join(field["closure_status"] for field in from_fields),
            "to_locus_closure_pattern": "|".join(field["closure_status"] for field in to_fields),
            "from_last_field": from_last["field_id"],
            "from_last_field_closure": from_last["closure_status"],
            "from_last_field_selected_skeleton": field_skeleton(from_last),
            "from_last_field_local_reading": from_last["LOCAL_IATROMEDICAL_EXPANSION"],
            "to_first_field": to_first["field_id"],
            "to_first_field_closure": to_first["closure_status"],
            "to_first_field_selected_skeleton": field_skeleton(to_first),
            "to_first_field_local_reading": to_first["LOCAL_IATROMEDICAL_EXPANSION"],
            "classification": decision["classification"],
            "rationale": decision["rationale"],
            "strongest_alternative": decision["strongest_alternative"],
            "from_statement_id": from_statement,
            "to_statement_id": to_statement,
            "cross_line_statement_id": from_statement
            if from_statement == to_statement
            else "NONE",
            "apprentice_boundary_rule": (
                "Zeilenreset ignorieren und denselben Klauselzettel weiterführen."
                if decision["classification"] == "CONTINUE_SAME_CLAUSE"
                else "Am Zeilenreset neuen Klauselzettel beginnen; Besitzerstatus gemäß Klasse führen."
            ),
            "highlight_f82r_3_to_4": "YES"
            if key == ("B2", "f82r.3", "f82r.4")
            else "NO",
            "highlight_all_f83r_boundaries": "YES" if from_last["page"] == "f83r" else "NO",
            "status": "CREATIVE_SEGMENTATION;NO_NEW_CARD_MEANING",
        }
        boundary_rows.append(row)
        boundary_meta_by_id[boundary_id] = row
        boundary_by_from_field[from_last["field_id"]] = row
        boundary_by_to_field[to_first["field_id"]] = row

    statement_rows: list[dict[str, str]] = []
    for statement_id, group in statement_groups:
        record = group[0]["record_unit_id"]
        loci = unique([field["locus"] for field in group])
        group_events = [
            event
            for field in group
            for event in events_by_field[field["field_id"]]
        ]
        internal_boundaries = [
            row
            for row in boundary_rows
            if row["cross_line_statement_id"] == statement_id
        ]
        entry_boundary = boundary_by_to_field.get(group[0]["field_id"])
        exit_boundary = boundary_by_from_field.get(group[-1]["field_id"])
        entry_class = (
            "RECORD_START"
            if group[0] == fields_by_record[record][0]
            else entry_boundary["classification"]
            if entry_boundary is not None
            and entry_boundary["classification"] != "CONTINUE_SAME_CLAUSE"
            else "WITHIN_LOCUS_FIELD_BOUNDARY"
        )
        exit_class = (
            "RECORD_END"
            if group[-1] == fields_by_record[record][-1]
            else exit_boundary["classification"]
            if exit_boundary is not None
            and exit_boundary["classification"] != "CONTINUE_SAME_CLAUSE"
            else "WITHIN_LOCUS_FIELD_BOUNDARY"
        )

        if internal_boundaries:
            apprentice_rule = (
                "Bei "
                + ",".join(row["boundary_id"] for row in internal_boundaries)
                + " nicht am Zeilenreset stoppen: letztes OPEN-Feld und erstes Folgelinienfeld "
                "auf demselben Klauselzettel lesen; CLOSE bleibt stumm."
            )
            segmentation_alt = " | ".join(
                row["strongest_alternative"] for row in internal_boundaries
            )
        elif entry_class == "RESUME_ACTIVE_ITEM":
            apprentice_rule = (
                "Neue Klausel beginnen, aber den aktiven Gegenstand aus dem Vorfeldregister "
                "wiederaufnehmen; Klauseln nicht verschmelzen."
            )
            segmentation_alt = entry_boundary["strongest_alternative"]  # type: ignore[index]
        elif entry_class == "NEXT_PARALLEL_CELL":
            apprentice_rule = (
                "Nächste Parallelzelle beginnen: Bildbesitzer behalten, Aktions- und "
                "Parameterslots zurücksetzen."
            )
            segmentation_alt = entry_boundary["strongest_alternative"]  # type: ignore[index]
        elif entry_class == "START_NEW_CLAUSE":
            apprentice_rule = (
                "Neue Klausel beginnen und die vorige Prozessphase nicht grammatisch fortsetzen."
            )
            segmentation_alt = entry_boundary["strongest_alternative"]  # type: ignore[index]
        elif entry_class == "UNRESOLVED":
            apprentice_rule = (
                "Grenze sichtbar einklammern und vorläufig neu beginnen; keine fehlende "
                "Fortsetzung erfinden."
            )
            segmentation_alt = entry_boundary["strongest_alternative"]  # type: ignore[index]
        elif entry_class == "RECORD_START":
            apprentice_rule = "Recordbesitzer setzen und den ersten Klauselzettel beginnen."
            segmentation_alt = "Ein erstes Feld kann Überschrift oder Rubrik statt Klausel sein."
        else:
            apprentice_rule = (
                "Feldgrenze innerhalb derselben physischen Zeile lesen; die Zeile liefert "
                "weder Satzanfang noch Satzende."
            )
            segmentation_alt = "Benachbarte Felder könnten eine größere Exemplarklausel bilden."

        nonmedical = " || ".join(
            unique([field["NONMEDICAL_RIVAL"] for field in group])
        )
        skeleton = " > ".join(
            f"{field['field_id']}[{field_skeleton(field)}]" for field in group
        )
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": record,
                "page": group[0]["page"],
                "statement_ordinal_in_record": str(
                    int(statement_id.rsplit("S", 1)[1])
                ),
                "start_locus": group[0]["locus"],
                "start_field": group[0]["field_id"],
                "end_locus": group[-1]["locus"],
                "end_field": group[-1]["field_id"],
                "constituent_loci": "|".join(loci),
                "constituent_fields": "|".join(field["field_id"] for field in group),
                "physical_line_count": str(len(loci)),
                "event_count": str(len(group_events)),
                "event_serials": "|".join(event["event_serial"] for event in group_events),
                "closure_sequence": " > ".join(
                    f"{field['field_id']}:{field['closure_status']}" for field in group
                ),
                "entry_boundary_class": entry_class,
                "exit_boundary_class": exit_class,
                "internal_cross_line_boundaries": "|".join(
                    row["boundary_id"] for row in internal_boundaries
                )
                or "NONE",
                "selected_short_card_skeleton": skeleton,
                "concrete_workshop_reading": " || ".join(
                    field["LOCAL_IATROMEDICAL_EXPANSION"] for field in group
                ),
                "strongest_alternative": (
                    f"SEGMENTATION={segmentation_alt}; NONMEDICAL={nonmedical}"
                ),
                "apprentice_reading_rule": apprentice_rule,
                "record_flow_context": record_text_by_id[record][
                    "LOCAL_IATROMEDICAL_EXPANSION"
                ],
                "evidence_basis": (
                    "FIELD_CLOSURE+EXACT_SELECTED_MNEMONIC+LOCAL_EXEMPLAR_FLOW;"
                    "PHYSICAL_LINE_NOT_SENTENCE"
                ),
                "status": "CREATIVE_CLAUSE_MAP;NO_NEW_CARD_MEANING;EXEMPLAR_REQUIRED",
            }
        )

    # Complete coverage and line-spanning invariants.
    clause_fields = [
        field_id
        for row in statement_rows
        for field_id in row["constituent_fields"].split("|")
    ]
    clause_events = [
        event_serial
        for row in statement_rows
        for event_serial in row["event_serials"].split("|")
    ]
    assert len(statement_rows) == 116
    assert len(clause_fields) == 135 == len(set(clause_fields))
    assert set(clause_fields) == set(field_by_id)
    assert len(clause_events) == 381 == len(set(clause_events))
    assert set(clause_events) == {row["event_serial"] for row in events}

    line_span_counts = Counter(int(row["physical_line_count"]) for row in statement_rows)
    assert line_span_counts == {1: 98, 2: 17, 3: 1}
    cross_line_statements = [
        row for row in statement_rows if int(row["physical_line_count"]) > 1
    ]
    assert len(cross_line_statements) == 18

    # Record summaries preserve the complete selected V59 full-record reading.
    record_rows: list[dict[str, str]] = []
    for record in record_order:
        record_fields = fields_by_record[record]
        record_events = [row for row in events if row["record_unit_id"] == record]
        record_boundaries = [row for row in boundary_rows if row["record_unit_id"] == record]
        record_statements = [row for row in statement_rows if row["record_unit_id"] == record]
        loci = unique([row["locus"] for row in record_fields])
        counts = Counter(row["classification"] for row in record_boundaries)
        open_fields = sum(row["closure_status"] == "OPEN" for row in record_fields)
        terminal_fields = len(record_fields) - open_fields
        selected_skeleton = " > ".join(
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
            for row in record_events
            if row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
        ) or "∅"
        strongest_boundary = (
            next(
                (
                    row
                    for row in record_boundaries
                    if row["classification"] == "UNRESOLVED"
                ),
                None,
            )
            or next(
                (
                    row
                    for row in record_boundaries
                    if row["classification"] == "CONTINUE_SAME_CLAUSE"
                ),
                record_boundaries[0] if record_boundaries else None,
            )
        )
        record_rows.append(
            {
                "record_unit_id": record,
                "page": record_fields[0]["page"],
                "physical_loci": str(len(loci)),
                "fields": str(len(record_fields)),
                "events": str(len(record_events)),
                "line_boundaries": str(len(record_boundaries)),
                "statements": str(len(record_statements)),
                "open_fields": str(open_fields),
                "terminal_fields": str(terminal_fields),
                "boundary_class_counts": "|".join(
                    f"{name}:{counts[name]}" for name in sorted(CLASSES) if counts[name]
                ) or "NONE",
                "selected_short_card_skeleton": selected_skeleton,
                "complete_workshop_reading": record_text_by_id[record][
                    "LOCAL_IATROMEDICAL_EXPANSION"
                ],
                "strongest_nonmedical_alternative": record_text_by_id[record][
                    "NONMEDICAL_RIVAL"
                ],
                "strongest_segmentation_pressure": "NONE"
                if strongest_boundary is None
                else (
                    f"{strongest_boundary['boundary_id']}={strongest_boundary['classification']}; "
                    f"ALT={strongest_boundary['strongest_alternative']}"
                ),
                "apprentice_record_rule": (
                    "Felder und Klauselzettel zählen; Zeilenreset nur nach dem Grenzledger "
                    "behandeln; aktive Besitzer bei RESUME behalten; CLOSE nie sprechen."
                ),
                "inherited_record_contradiction": record_text_by_id[record][
                    "strongest_contradiction"
                ],
                "status": "COMPLETE_RECORD_FLOW;CREATIVE_NOT_TRANSLATION",
            }
        )

    boundary_fields = [
        "boundary_id", "record_unit_id", "page", "boundary_ordinal_in_record",
        "from_locus", "to_locus", "from_locus_fields", "to_locus_fields",
        "from_locus_closure_pattern", "to_locus_closure_pattern",
        "from_last_field", "from_last_field_closure",
        "from_last_field_selected_skeleton", "from_last_field_local_reading",
        "to_first_field", "to_first_field_closure",
        "to_first_field_selected_skeleton", "to_first_field_local_reading",
        "classification", "rationale", "strongest_alternative",
        "from_statement_id", "to_statement_id", "cross_line_statement_id",
        "apprentice_boundary_rule", "highlight_f82r_3_to_4",
        "highlight_all_f83r_boundaries", "status",
    ]
    clause_fields_header = [
        "statement_id", "record_unit_id", "page", "statement_ordinal_in_record",
        "start_locus", "start_field", "end_locus", "end_field",
        "constituent_loci", "constituent_fields", "physical_line_count",
        "event_count", "event_serials", "closure_sequence",
        "entry_boundary_class", "exit_boundary_class",
        "internal_cross_line_boundaries", "selected_short_card_skeleton",
        "concrete_workshop_reading", "strongest_alternative",
        "apprentice_reading_rule", "record_flow_context", "evidence_basis", "status",
    ]
    record_fields_header = [
        "record_unit_id", "page", "physical_loci", "fields", "events",
        "line_boundaries", "statements", "open_fields", "terminal_fields",
        "boundary_class_counts", "selected_short_card_skeleton",
        "complete_workshop_reading", "strongest_nonmedical_alternative",
        "strongest_segmentation_pressure", "apprentice_record_rule",
        "inherited_record_contradiction", "status",
    ]
    write_tsv(BOUNDARY_OUT, boundary_fields, boundary_rows)
    write_tsv(CLAUSE_OUT, clause_fields_header, statement_rows)
    write_tsv(RECORD_OUT, record_fields_header, record_rows)

    class_counts = Counter(row["classification"] for row in boundary_rows)
    assert class_counts == {
        "CONTINUE_SAME_CLAUSE": 19,
        "RESUME_ACTIVE_ITEM": 8,
        "NEXT_PARALLEL_CELL": 10,
        "START_NEW_CLAUSE": 8,
        "UNRESOLVED": 1,
    }
    f83_boundaries = [row for row in boundary_rows if row["page"] == "f83r"]
    assert len(f83_boundaries) == 21
    assert Counter(row["classification"] for row in f83_boundaries) == {
        "CONTINUE_SAME_CLAUSE": 11,
        "RESUME_ACTIVE_ITEM": 3,
        "NEXT_PARALLEL_CELL": 3,
        "START_NEW_CLAUSE": 4,
    }
    carry = [row for row in boundary_rows if row["highlight_f82r_3_to_4"] == "YES"]
    assert len(carry) == 1
    assert carry[0]["classification"] == "CONTINUE_SAME_CLAUSE"
    assert carry[0]["from_last_field"] == "F050"
    assert carry[0]["to_first_field"] == "F051"
    assert carry[0]["from_statement_id"] == carry[0]["to_statement_id"]
    assert len({row["page"] for row in fields}) == 7
    assert {row["page"] for row in fields} == {
        "f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"
    }
    assert sum(row["closure_status"] == "OPEN" for row in fields) == 45
    assert sum(row["closure_status"] == "TERMINAL" for row in fields) == 90
    assert sum(len(unique([row["locus"] for row in fields_by_record[record]])) for record in record_order) == 57

    validation = {
        "status": "PASS",
        "model": "V61_R1_PHYSICAL_LINE_IS_LAYOUT_CLAUSE_MAP",
        "counts": {
            "prose_records": 11,
            "physical_loci": 57,
            "within_record_physical_line_boundaries": 46,
            "fields": 135,
            "events": 381,
            "selected_mnemonic_occurrences": 85,
            "statements": 116,
            "cross_line_statements": 18,
            "continued_cross_line_boundaries": 19,
            "one_line_statements": line_span_counts[1],
            "two_line_statements": line_span_counts[2],
            "three_line_statements": line_span_counts[3],
            "open_fields": 45,
            "terminal_fields": 90,
            "f83r_boundaries": len(f83_boundaries),
            "f82r_3_to_4_carry_boundaries": len(carry),
        },
        "boundary_class_counts": dict(sorted(class_counts.items())),
        "f83r_boundary_class_counts": dict(
            sorted(Counter(row["classification"] for row in f83_boundaries).items())
        ),
        "statements_by_record": dict(statement_counter),
        "assertions": {
            "every_record_internal_locus_boundary_listed_once": "PASS",
            "all_five_requested_boundary_classes_used": "PASS",
            "all_f83r_boundaries_explicitly_flagged": "PASS",
            "f82r_3_to_4_is_one_continuing_statement_F050_F051": "PASS",
            "every_field_occurs_in_exactly_one_statement": "PASS",
            "every_event_occurs_in_exactly_one_statement": "PASS",
            "selected_short_card_skeleton_comes_only_from_V60_ledger": "PASS",
            "local_readings_remain_inherited_exemplar_prose": "PASS",
            "physical_line_is_not_statement_boundary": "PASS",
            "no_new_card_meaning_assigned": "PASS",
            "no_new_pages": "PASS",
        },
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [ROUTE, ROLES, PROTOCOL, SELECTION, EVENT_SOURCE, FIELD_SOURCE, RECORD_SOURCE]
        },
        "output_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [BOUNDARY_OUT, CLAUSE_OUT, RECORD_OUT]
        },
    }
    VALIDATION_OUT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "counts": validation["counts"]}))


if __name__ == "__main__":
    main()
