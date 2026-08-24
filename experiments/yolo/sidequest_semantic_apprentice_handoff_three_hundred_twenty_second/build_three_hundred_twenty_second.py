#!/usr/bin/env python3
"""Build five apprentice handoff dialogues from the shared exact-card lexicon."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_handoff_lexicon_three_hundred_twentieth/THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_sequences_three_hundred_eighteenth/THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv"

LESSONS = [
    {
        "lesson": "L1",
        "herbal_record": "H1",
        "bio_unit": "B1-S002-M03",
        "pictured_material": "Wurzel der abgebildeten Pflanze",
        "pictured_station": "gemeinsames zweireihiges Becken",
        "spoken_handoff": "Der bemessene Wurzelauszug und sein Rest gehören zum selben fortgesetzten Beckengang.",
        "apprentice_action": "Aus demselben Vorrat zerkleinern, einsetzen, abmessen und bereitstellen; am Becken als Fortsetzungsansatz weiterführen.",
    },
    {
        "lesson": "L2",
        "herbal_record": "H2",
        "bio_unit": "B1-S002-M04",
        "pictured_material": "zweiter Auszugsansatz der abgebildeten Pflanze",
        "pictured_station": "Mess- und Halteplatz im gemeinsamen Becken",
        "spoken_handoff": "Dieser Folgeansatz ist bereits auf seine Arbeitsstufe gebracht; vor und nach dem Halten dasselbe Sollmaß prüfen.",
        "apprentice_action": "Ansatz aus gleichem Vorrat fortsetzen, Sollmaß setzen, am Becken halten und nochmals dasselbe Maß lesen.",
    },
    {
        "lesson": "L3",
        "herbal_record": "H3",
        "bio_unit": "B2-S012-M02",
        "pictured_material": "klarer kalter Sud der abgebildeten Pflanze",
        "pictured_station": "unteres Mehrplatzbecken",
        "spoken_handoff": "Nur der geklärte Auszug wird übergeben; Trub und ausgewrungenes Pflanzenmaterial bleiben zurück.",
        "apprentice_action": "Klarauszug übernehmen, am lokalen Platz kurz vorbereiten, länger einwirken lassen und den klaren Anteil abziehen.",
    },
    {
        "lesson": "L4",
        "herbal_record": "H4",
        "bio_unit": "B4-S008",
        "pictured_material": "bemessener gekühlter Blattauszug",
        "pictured_station": "f83r-Anwendungs-/Durchlasspaar",
        "spoken_handoff": "Die Vorratszubereitung ist kalt; erst die abgemessene Anwendungsportion wird wieder länger warm gehalten.",
        "apprentice_action": "Sollmaß nehmen, Langwärme ausführen, an der ersten Öffnung kurz ansetzen und den Schritt schließen.",
    },
    {
        "lesson": "L5",
        "herbal_record": "H5",
        "bio_unit": "B4-S003-M02",
        "pictured_material": "Stängel-/Zusatzauszug für mehrere Einsätze",
        "pictured_station": "f83r-Anwendungs-/Durchlasspaar",
        "spoken_handoff": "Nicht alles auf einmal verbrauchen; der nächste Posten ist eine weitere Anwendung desselben hergestellten Guts.",
        "apprentice_action": "Folgeposten wählen, länger behandeln, einsetzen, fortsetzen und kurz absetzen.",
    },
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compress(seq: list[str]) -> list[str]:
    result = []
    for item in seq:
        if not result or result[-1] != item:
            result.append(item)
    return result


def main() -> None:
    ledger = read(LEDGER)
    atom = {x["joint_tuple_id"]: x["handoff_atomic_value_de"] for x in read(LEXICON)}
    units = {x["station_work_unit_id"]: x for x in read(UNITS)}
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_event = {}
    for row in ledger:
        by_record[row["record_unit_id"]].append(row)
        by_event[row["event_id"]] = row

    dialogues = []
    channel_rows = []
    for lesson in LESSONS:
        herbal = by_record[lesson["herbal_record"]]
        bio = [by_event[e] for e in units[lesson["bio_unit"]]["event_ids"].split("|")]
        hseq = [atom[x["joint_tuple_id"]] for x in herbal if x["joint_tuple_id"] in atom]
        bseq = [atom[x["joint_tuple_id"]] for x in bio if x["joint_tuple_id"] in atom]
        handshake = [x for x in compress(hseq) if x in set(bseq)]
        dialogues.append(
            {
                **lesson,
                "herbal_portable_sequence": " → ".join(hseq),
                "herbal_compressed_sequence": " → ".join(compress(hseq)),
                "bio_portable_sequence": " → ".join(bseq),
                "exact_handshake_words": "|".join(handshake),
                "direct_cross_page_pointer": "NONE",
            }
        )
        for channel, value, status in [
            ("PORTABLE_CARDS", " → ".join(compress(hseq + bseq)), "WRITTEN_IN_SHARED_CARD_LAYER"),
            ("MATERIAL_OWNER", lesson["pictured_material"], "SUPPLIED_BY_HERBAL_PICTURE"),
            ("STATION_OWNER", lesson["pictured_station"], "SUPPLIED_BY_BIO_PICTURE"),
            ("HANDOFF_MATCH", lesson["spoken_handoff"], "TAUGHT_OR_INFERRED_WORKSHOP_LINK"),
            ("FULL_ACTION", lesson["apprentice_action"], "EXPANDED_BY_APPRENTICE"),
        ]:
            channel_rows.append(
                {
                    "lesson": lesson["lesson"],
                    "herbal_record": lesson["herbal_record"],
                    "bio_unit": lesson["bio_unit"],
                    "information_channel": channel,
                    "content_de": value,
                    "status": status,
                }
            )

    write("THREE_HUNDRED_TWENTY_SECOND_FIVE_APPRENTICE_DIALOGUES.tsv", dialogues)
    write("THREE_HUNDRED_TWENTY_SECOND_25_INFORMATION_CHANNELS.tsv", channel_rows)
    names = [
        "THREE_HUNDRED_TWENTY_SECOND_FIVE_APPRENTICE_DIALOGUES.tsv",
        "THREE_HUNDRED_TWENTY_SECOND_25_INFORMATION_CHANNELS.tsv",
    ]
    summary = {
        "status": "PASS",
        "lessons": len(dialogues),
        "channel_rows": len(channel_rows),
        "written_card_channels": 5,
        "picture_owner_channels": 10,
        "taught_handoff_channels": 5,
        "expanded_action_channels": 5,
        "direct_cross_page_pointers": 0,
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
