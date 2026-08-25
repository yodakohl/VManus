#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROSE = ROOT / "sidequest_semantic_prose_complete_workshop_edition_eight_hundred_ninety_sixth"
CONDITIONS = ROOT / "sidequest_semantic_concrete_condition_matching_eight_hundred_eighty_seventh"
PREFIX = "EIGHT_HUNDRED_NINETY_SEVENTH"

VOCAB_SOURCE = PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_231_COMPLETE_WORKSHOP_VOCABULARY.tsv"
MARK_SOURCE = PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_437_COMPLETE_MARK_DECK.tsv"
UNIT_SOURCE = PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_118_COMPLETE_UNIT_EXECUTION.tsv"
CARD_SOURCE = PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_6_PROSE_COMPLETE_JOB_CARDS.tsv"
GROUP_SOURCE = CONDITIONS / "EIGHT_HUNDRED_EIGHTY_SEVENTH_73_COMPLETE_CONDITION_GROUPS.tsv"
HANDLE_SOURCE = CONDITIONS / "EIGHT_HUNDRED_EIGHTY_SEVENTH_6_CONCRETE_CONDITION_HANDLES.tsv"


WORDS = {
    "C1@f67r2.1": [
        "PHASENPOSTEN EINTRAGEN",
        "PHASENZEICHEN",
        "VOM GEGENFELD",
    ],
    "C2@f67r2.15": [
        "ASPEKTWEG SCHLIESSEN",
    ],
    "C3@f68r1.9": [
        "STERNORT KURZ BEREITSETZEN",
    ],
    "C4@f69v.12": [
        "MARKIERTEN 28ER-PLATZ SCHLIESSEN",
    ],
    "C5@f69v.2": [
        "FEUCHTEPOSTEN EINTRAGEN",
        "FEUCHTELAGE FORTSETZEN",
        "FEUCHTE VON DER QUELLE",
        "AN DER FEUCHTESTELLE",
        "FEUCHTEPOSTEN ABSCHLIESSEN",
        "WETTERZEICHEN",
        "FEUCHTE LANGE HALTEN",
        "FEUCHTELAGE FORTSETZEN",
        "LAENGER AN DER FEUCHTESTELLE",
        "FEUCHTAUSZUG",
        "VOM WETTERURSPRUNG",
        "FEUCHTE DURCH DEN DURCHLASS",
        "FEUCHTE LAENGER HALTEN",
        "FEUCHTEMASS",
        "AKTUELLE FEUCHTELAGE",
        "FEUCHTESTUFE",
        "FEUCHTAUSZUG ABSCHLIESSEN",
        "AN DER FEUCHTESTELLE",
        "KURZE FEUCHTEPHASE",
        "KURZ VON DER FEUCHTEQUELLE",
        "AKTUELLE FEUCHTELAGE",
        "AKTUELLE FEUCHTELAGE",
        "FEUCHTE KURZ HALTEN",
        "FEUCHTE ENTNEHMEN",
        "AKTUELLE FEUCHTELAGE",
        "AKTUELLE FEUCHTELAGE",
        "FEUCHTELAGE FORTSETZEN",
        "FEUCHTE VON DER QUELLE",
        "WETTER FORTSETZEN",
        "AKTUELLE FEUCHTELAGE",
        "FEUCHTE LANG HALTEN UND SCHLIESSEN",
        "AKTUELLER FEUCHTEPOSTEN",
        "AN DER FEUCHTESTELLE",
        "FEUCHTEGANG SCHLIESSEN",
        "LAUFFEUCHTE",
        "FEUCHTEPOSTEN ANSETZEN",
        "DIESE FEUCHTELAGE",
        "AKTUELLER FEUCHTEPOSTEN",
    ],
    "C6@f69v.3": [
        "LICHTLAUF",
        "NAECHSTE DOPPELSTELLE",
        "KOERPERLICHT",
        "KOERPERZUSTAND UMSETZEN",
        "NAECHSTE LICHTQUELLE",
        "VON DER LICHTQUELLE",
        "AKTUELLE KOERPERQUALITAET",
        "KURZER FOLGEZUSTAND",
        "KOERPERTEIL",
        "NAECHSTER LICHTLAUF",
        "KOERPERSTELLE UMSETZEN",
        "LAENGER AN DER FOLGESTELLE",
        "KOERPERAUSZUG",
        "VON DER LICHTQUELLE",
        "LICHTLAUF",
        "KURZEN FOLGEZUSTAND SETZEN",
        "AKTUELLE KOERPERPHASE",
        "LICHTSTELLE",
        "AKTUELLE KOERPERSTELLE",
        "NAECHSTE QUALITAET FORTSETZEN",
        "KURZ AN DER LICHTSTELLE",
        "KURZ VON ZWEI QUELLEN",
        "KURZ LANG KURZ PRUEFEN",
        "KOERPERLICHT",
        "AKTUELLE KOERPERQUALITAET",
        "KOERPERQUALITAET ANSETZEN",
        "AN DER KOERPERSTELLE",
        "NAECHSTE QUALITAET LANG HALTEN",
        "NAECHSTE QUALITAET LANG HALTEN",
    ],
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    vocabulary = read(VOCAB_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)
    groups = read(GROUP_SOURCE)
    handles = read(HANDLE_SOURCE)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        grouped[row["condition_handle"]].append(row)
    assert set(grouped) == set(WORDS)
    for handle, rows in grouped.items():
        assert [int(row["event_index"]) for row in rows] == list(range(1, len(rows) + 1))
        assert len(rows) == len(WORDS[handle])

    condition_lexicon = []
    word_by_identity: dict[str, str] = {}
    for handle in [row["condition_handle"] for row in handles]:
        for row, word in zip(grouped[handle], WORDS[handle], strict=True):
            word_by_identity[row["opaque_local_id"]] = word
            condition_lexicon.append({
                "condition_handle": handle,
                "page": row["page"],
                "locus": row["locus"],
                "event_index": row["event_index"],
                "opaque_local_id": row["opaque_local_id"],
                "surface": row["surface"],
                "component_parse": row["component_parse"],
                "old_generic_reading_de": row["relative_reading_de"],
                "speakable_condition_word_de": word,
                "workshop_scope": "LOCAL_CONDITION_WORD",
            })
    assert len(condition_lexicon) == 73
    assert len(word_by_identity) == 73

    revised_vocab = []
    for row in vocabulary:
        if row["identity"] in word_by_identity:
            revised_vocab.append({
                **row,
                "short_value_de": word_by_identity[row["identity"]],
                "apprentice_action": "READ_LOCAL_CONDITION_WORD",
                "semantic_revision": "YES",
                "eighth_lesson": "SPEAKABLE_CONDITION_LEXICON",
            })
        else:
            revised_vocab.append({**row, "eighth_lesson": "NO_CHANGE"})

    revised_marks = []
    for row in marks:
        if row["source_id"] in word_by_identity:
            revised_marks.append({
                **row,
                "concrete_default_de": word_by_identity[row["source_id"]],
                "apprentice_action": "READ_LOCAL_CONDITION_WORD",
                "semantic_revision": "YES",
                "eighth_lesson": "SPEAKABLE_CONDITION_LEXICON",
            })
        else:
            revised_marks.append({**row, "eighth_lesson": "NO_CHANGE"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    for mark in revised_marks:
        unit = unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)

    revised_units = []
    condition_phrases = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        if unit["section"] == "WHEN":
            spoken = " -> ".join(str(row["concrete_default_de"]) for row in local)
            status = "LOCAL_CONDITION_LEXICON_EXECUTABLE"
            condition_phrases.append({
                "order_id": unit["order_id"],
                "master_unit_id": unit["master_unit_id"],
                "condition_handle": unit["stage"].removeprefix("CONDITION_"),
                "page": unit["page"],
                "locus": unit["unit"],
                "marks": len(local),
                "surface_sequence": " ".join(str(row["surface"]) for row in local),
                "speakable_sequence_de": spoken,
                "condition_instruction_de": unit["front_instruction_de"],
            })
        else:
            spoken = "NONE"
            status = "SHARED_OR_TAUGHT_EXECUTABLE"
        revised_units.append({
            **unit,
            "core_marks": len(local),
            "model_marks": 0,
            "execution_status": status,
            "speakable_condition_sequence_de": spoken,
            "condition_lexicon_closed": "YES" if unit["section"] == "WHEN" else "NOT_APPLICABLE",
        })

    revised_cards = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        when = next(row for row in local if row["section"] == "WHEN")
        revised_cards.append({
            **card,
            "condition_units": 1,
            "condition_marks": int(when["marks"]),
            "condition_handle": when["stage"].removeprefix("CONDITION_"),
            "condition_speakable": "YES",
            "all_units_readable": "YES",
        })

    write(f"{PREFIX}_73_SPEAKABLE_CONDITION_LEXICON.tsv", condition_lexicon, list(condition_lexicon[0]))
    write(f"{PREFIX}_6_SPEAKABLE_CONDITION_PHRASES.tsv", condition_phrases, list(condition_phrases[0]))
    write(f"{PREFIX}_231_COMPLETE_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["eighth_lesson"])
    write(f"{PREFIX}_437_ALL_SPEAKABLE_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["eighth_lesson"])
    write(f"{PREFIX}_118_ALL_EXECUTABLE_UNITS.tsv", revised_units, list(units[0]) + ["speakable_condition_sequence_de", "condition_lexicon_closed"])
    write(f"{PREFIX}_6_COMPLETE_JOB_CARDS.tsv", revised_cards, list(revised_cards[0]))

    lines = [
        "# Sprechbares Bedingungsbuch",
        "",
        "Alle 73 Zeichen der sechs WHEN-Blätter haben nun kurze lokale Werkstattwerte.",
        "Das sind Bedingungen und Adressen innerhalb der sechs Diagramme, keine Planeten-, Zeichen- oder Monatsnamen.",
        "",
    ]
    handle_by_id = {row["condition_handle"]: row for row in handles}
    for phrase in condition_phrases:
        meta = handle_by_id[phrase["condition_handle"]]
        lines.extend([
            f"## {phrase['condition_handle']} — {meta['visual_role_de']}",
            "",
            f"**Oberfläche:** `{phrase['surface_sequence']}`",
            "",
            f"**Werkstattfolge:** {phrase['speakable_sequence_de']}.",
            "",
            f"**Verwendung:** {phrase['condition_instruction_de']}",
            "",
        ])
    (HERE / f"{PREFIX}_SPEAKABLE_CONDITION_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    statuses = Counter(str(row["execution_status"]) for row in revised_units)
    actions = Counter(str(row["apprentice_action"]) for row in revised_marks)
    summary = {
        "status": "PASS",
        "decision": "ALL_SEVENTY_THREE_CONDITION_MARKS_GAIN_SHORT_SPEAKABLE_LOCAL_WORDS_AND_COMPLETE_THE_ONE_HUNDRED_EIGHTEEN_UNIT_DECK",
        "condition_handles": len(condition_phrases),
        "condition_marks": len(condition_lexicon),
        "vocabulary_identities": len(revised_vocab),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "unit_statuses": dict(statuses),
        "mark_actions": dict(actions),
        "copy_local_model_marks": actions["COPY_LOCAL_MODEL"],
        "external_celestial_names": 0,
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 897: sprechbares Bedingungslexikon\n\n"
        "Die letzten 73 Modellkopien werden zu kurzen lokalen Werkstattwörtern. "
        "C1 liest Phasenposten, C2 einen Aspektweg, C3 einen direkten Sternort, C4 einen markierten 28er-Platz, "
        "C5 Feuchte- und Wetterlagen und C6 Licht- und Körperqualitäten. "
        "Damit sind alle 437 Marken und alle 118 Einheiten sprechbar; die Diagrammwörter bleiben lokal und erhalten keine externen Himmelsnamen.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
