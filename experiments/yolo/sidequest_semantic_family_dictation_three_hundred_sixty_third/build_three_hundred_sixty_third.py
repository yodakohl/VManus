#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P362 = ROOT / "experiments/yolo/sidequest_semantic_workshop_thesaurus_three_hundred_sixty_second"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (P362 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FEATURES = [
    ("FOLGE", ("folge", "fortsetz", "weiter", "anschluss")),
    ("QUELLE", ("quell", "vor")),
    ("ZIEL", ("ziel", "stelle", "marke")),
    ("POSTEN", ("posten", "dies")),
    ("KURZ", ("kurz",)),
    ("LANG", ("lang",)),
    ("VOLL", ("voll", "end")),
    ("RÜCK", ("rück", "zurück")),
    ("NACH", ("nach",)),
    ("BEREIT", ("bereit",)),
    ("ZUGABE", ("zutat", "zusatz", "zugabe", "einlage")),
    ("BINDEN", ("bind", "befest")),
    ("WASCHEN", ("wasser", "wasch", "spül")),
    ("KLÄREN", ("klar", "seih", "trenn")),
    ("ABSETZEN", ("absetz", "stand")),
    ("ABFÜHREN", ("abführ", "abzug", "abzieh", "auslass")),
    ("DURCHGANG", ("passage", "durchgang", "durchlass", "durchleit", "beckenlauf")),
    ("TRANSFER", ("transfer", "zuführ", "überführ", "umsetz", "ausguss")),
    ("PORTION", ("portion", "teil", "anteil")),
    ("MASS", ("maß", "soll")),
    ("WÄRME", ("warm",)),
    ("KONTAKT", ("kontakt",)),
    ("HALTEN", ("halt",)),
    ("ANSATZ", ("ansatz", "vorbereitung", "zubereitung")),
    ("GEFÄSS", ("gefäß",)),
    ("PFLANZENTEIL", ("wurzel", "blüten", "pflanze", "stoff")),
    ("PRESSEN", ("wring",)),
    ("GEBRAUCH", ("gebrauch",)),
    ("REST", ("rest",)),
]


def cues(value: str) -> tuple[str, ...]:
    low = value.lower()
    result = tuple(name for name, pieces in FEATURES if any(piece in low for piece in pieces))
    return result or ("OHNE_ZUSATZ",)


def main() -> None:
    phrases = read_tsv("THREE_HUNDRED_SIXTY_SECOND_159_PHRASE_INDEX.tsv")
    cards = read_tsv("THREE_HUNDRED_SIXTY_SECOND_380_FAMILY_TAGGED_CARDS.tsv")
    families = {row["family_id"]: row for row in read_tsv("THREE_HUNDRED_SIXTY_SECOND_33_FAMILY_THESAURUS.tsv")}

    groups: dict[tuple[str, tuple[str, ...]], list[dict[str, str]]] = defaultdict(list)
    for row in phrases:
        groups[(row["family_id"], cues(row["atomic_value_de"]))].append(row)

    drill_rows = []
    phrase_status = {}
    for row in phrases:
        key = (row["family_id"], cues(row["atomic_value_de"]))
        candidates = groups[key]
        unique = len(candidates) == 1
        spoken = f"{families[row['family_id']]['family_head_de']} + {'+'.join(key[1])}"
        phrase_status[row["controlled_phrase"]] = "COMPOSED_UNIQUE" if unique else "MASTER_CARD_REQUIRED"
        drill_rows.append({
            "family_id": row["family_id"],
            "spoken_dictation_de": spoken,
            "semantic_cues": "+".join(key[1]),
            "candidate_count": len(candidates),
            "candidate_controlled_phrases": "|".join(sorted(item["controlled_phrase"] for item in candidates)),
            "target_controlled_phrase": row["controlled_phrase"],
            "target_joint_tuple_ids": row["joint_tuple_ids"],
            "apprentice_action": row["fixed_reverse_formula"] if unique else f"MASTER_CARD::{row['controlled_phrase']}",
            "status": phrase_status[row["controlled_phrase"]],
            "teaching_note_de": "aus Familie und Zusätzen gebaut" if unique else "als Ganzform vom Brett nehmen; Familie reicht nicht",
        })
    drill_rows.sort(key=lambda row: (row["status"], row["family_id"], row["target_controlled_phrase"]))

    event_rows = []
    for row in cards:
        status = phrase_status[row["controlled_phrase"]]
        event_rows.append({
            "source_position_id": row["source_position_id"],
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "family_id": row["family_id"],
            "controlled_phrase": row["controlled_phrase"],
            "dictation_status": status,
            "setting_route": "COMPOSE_FROM_CUES" if status == "COMPOSED_UNIQUE" else "FETCH_WHOLE_CARD_FROM_BOARD",
        })

    ambiguous_rows = []
    for (fid, bundle), members in sorted(groups.items()):
        if len(members) == 1:
            continue
        ambiguous_rows.append({
            "family_id": fid,
            "family_head_de": families[fid]["family_head_de"],
            "semantic_cues": "+".join(bundle),
            "candidate_count": len(members),
            "controlled_phrases": "|".join(sorted(row["controlled_phrase"] for row in members)),
            "atomic_values_de": "|".join(sorted(row["atomic_value_de"] for row in members)),
            "source_events": sum(int(row["event_count"]) for row in members),
            "next_teaching_move": "WHOLE_CARD_PAIR" if len(members) == 2 else "WHOLE_CARD_ROW",
        })

    write_tsv("THREE_HUNDRED_SIXTY_THIRD_159_DICTATION_DRILLS.tsv", drill_rows)
    write_tsv("THREE_HUNDRED_SIXTY_THIRD_380_EVENT_SETTING_ROUTES.tsv", event_rows)
    write_tsv("THREE_HUNDRED_SIXTY_THIRD_AMBIGUOUS_BUNDLES.tsv", ambiguous_rows)

    unique_phrases = sum(row["status"] == "COMPOSED_UNIQUE" for row in drill_rows)
    unique_events = sum(row["dictation_status"] == "COMPOSED_UNIQUE" for row in event_rows)
    dialogue = [
        "# Pass 363 — Diktat des Lehrmeisters",
        "",
        f"Von 159 Formeln lassen sich {unique_phrases} allein aus Familienkopf und kurzen Zusätzen setzen; {159-unique_phrases} bleiben gelernte Ganzformen. Auf Ereignisebene sind das {unique_events} von 380 Quellkarten kompositionell und {380-unique_events} Brettabrufe.",
        "",
        "## Arbeitsregel",
        "",
        "1. Der Meister nennt den Familienkopf.",
        "2. Er nennt nur sichtbare Zusätze wie QUELLE, ZIEL, KURZ, LANG oder FOLGE.",
        "3. Ergibt das genau eine Formel, setzt der Lehrling sie.",
        "4. Bleiben mehrere Formeln, greift er zur ganzen Karte auf dem Brett; er erfindet keinen weiteren Stamm.",
        "",
        "## Beispielturns",
        "",
    ]
    for row in drill_rows[:8] + [row for row in drill_rows if row["status"] == "MASTER_CARD_REQUIRED"][:8]:
        dialogue += [
            f"- Meister: **{row['spoken_dictation_de']}**",
            f"  Lehrling: `{row['apprentice_action']}` — {row['teaching_note_de']}.",
        ]
    (HERE / "THREE_HUNDRED_SIXTY_THIRD_MASTER_APPRENTICE_DIALOGUE.md").write_text("\n".join(dialogue) + "\n", encoding="utf-8")

    report = f"""# Pass 363 — Familien-Diktat

Ein Lehrmeister diktiert nur Familienkopf plus kurze semantische Zusätze. Das
reicht für {unique_phrases}/159 Formeln und {unique_events}/380 Quellkarten. Die
restlichen {159-unique_phrases} Formeln ({380-unique_events} Karten) werden ehrlich als
gelernte Ganzformen vom Brett genommen.

Das ist die gesuchte Mischung: produktive Fachkürzel tragen den größeren Teil,
doch dicht benachbarte Formen werden nicht mit immer neuen Bedeutungsstämmen
gerettet. {len(ambiguous_rows)} konkrete Mehrdeutigkeitsbündel zeigen, wo die
nächste Runde paarweise Kontraste lehren muss.
"""
    (HERE / "THREE_HUNDRED_SIXTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "phrases": 159,
        "composed_unique_phrases": unique_phrases,
        "whole_card_phrases": 159 - unique_phrases,
        "source_cards": 380,
        "composed_unique_source_cards": unique_events,
        "whole_card_source_cards": 380 - unique_events,
        "ambiguous_bundles": len(ambiguous_rows),
        "largest_ambiguous_bundle": max(int(row["candidate_count"]) for row in ambiguous_rows),
    }
    (HERE / "THREE_HUNDRED_SIXTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
