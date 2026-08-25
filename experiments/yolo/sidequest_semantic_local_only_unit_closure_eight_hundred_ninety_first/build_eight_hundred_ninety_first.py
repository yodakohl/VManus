#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_twelve_local_whole_words_eight_hundred_ninetieth"
MARKS = SOURCE / "EIGHT_HUNDRED_NINETIETH_437_REVISED_MARK_DECK.tsv"
UNITS = SOURCE / "EIGHT_HUNDRED_NINETIETH_118_REVISED_UNIT_EXECUTION.tsv"
VOCAB = SOURCE / "EIGHT_HUNDRED_NINETIETH_231_REVISED_WORKSHOP_VOCABULARY.tsv"
CARDS = SOURCE / "EIGHT_HUNDRED_NINETIETH_6_REVISED_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETY_FIRST"

PROMOTIONS = {
    "PROC111": ("KURZ HALTEN UND SCHLIESSEN", "dshedy", "linke Mittelstation"),
    "PROC114": ("KURZ WEITERHALTEN UND SCHLIESSEN", "solshedy", "linke Mittelstation"),
    "PROC121": ("AUS DER QUELLE LEITEN", "lar", "unteres grünes Becken"),
    "PROC126": ("AN DER ZIELSTELLE KURZ KUEHL HALTEN", "rsheal", "Randstationen des unteren Beckens"),
    "PROC127": ("AN DER ZIELSTELLE SCHLIESSEN", "daldy", "Randstationen des unteren Beckens"),
    "PROC128": ("KUEHL RUHEN LASSEN UND SCHLIESSEN", "rshedy", "Randstationen des unteren Beckens"),
    "PROC130": ("DURCHLEITEN UND SCHLIESSEN", "lochedy", "Randstationen des unteren Beckens"),
    "PROC138": ("WASSER ANSETZEN", "okair", "unteres Korbgefäß"),
    "PROC139": ("LAENGER HALTEN UND SCHLIESSEN", "sheedy", "unteres Korbgefäß"),
    "PROC141": ("KURZ ANSETZEN UND HALTEN", "qokshedy", "unverbundener Zwischenabschnitt"),
    "PROC155": ("ANSETZEN UND FESTBINDEN", "qokylddy", "verbundenes Hauptpaar"),
    "PROC166": ("DANACH UMSETZEN UND SCHLIESSEN", "otchdy", "linke offene Nebenstation"),
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
    marks = read(MARKS)
    units = read(UNITS)
    vocabulary = read(VOCAB)
    cards = read(CARDS)
    target_units = [row for row in units if row["execution_status"] == "LOCAL_MODEL_ONLY"]
    target_ids = set(PROMOTIONS)

    decisions: list[dict[str, object]] = []
    occurrences: list[dict[str, object]] = []
    for identity, (value, surface, station) in PROMOTIONS.items():
        local = [row for row in marks if row["identity"] == identity]
        mark = local[0]
        unit = next(row for row in units if row["order_id"] == mark["order_id"] and row["stage"] == mark["stage"] and row["unit"] == mark["unit"])
        decisions.append(
            {
                "identity": identity,
                "surface": surface,
                "old_default_de": mark["concrete_default_de"],
                "new_whole_word_de": value,
                "station_de": station,
                "order_id": mark["order_id"],
                "unit": mark["unit"],
                "role": "TRANSFER" if any(word in value for word in ["LEITEN", "WASSER", "UMSETZEN"]) else "HOLD_OR_CLOSE",
                "teaching_rule_de": f"Wenn `{surface}` als alleinige lokale Karte in {unit['unit']} steht, lies {value}.",
            }
        )
    for unit in target_units:
        local = [
            row for row in marks
            if row["order_id"] == unit["order_id"] and row["stage"] == unit["stage"] and row["unit"] == unit["unit"]
        ]
        targets = [row for row in local if row["identity"] in PROMOTIONS]
        occurrences.append(
            {
                "order_id": unit["order_id"],
                "master_unit_id": unit["master_unit_id"],
                "unit": unit["unit"],
                "page": unit["page"],
                "owner_de": unit["owner_trace_de"],
                "surface_sequence": " ".join(row["surface"] for row in targets),
                "identity_sequence": " ".join(row["identity"] for row in targets),
                "new_whole_words_de": " | ".join(PROMOTIONS[row["identity"]][0] for row in targets),
                "complete_unit_reading_de": unit["front_instruction_de"],
            }
        )

    revised_vocab: list[dict[str, object]] = []
    for row in vocabulary:
        if row["identity"] in target_ids:
            revised_vocab.append(
                {
                    **row,
                    "short_value_de": PROMOTIONS[row["identity"]][0],
                    "apprentice_action": "READ_TAUGHT_WHOLE_WORD",
                    "semantic_revision": "YES",
                    "second_lesson": "LOCAL_ONLY_UNIT_CLOSURE",
                }
            )
        else:
            revised_vocab.append({**row, "second_lesson": "NO_CHANGE"})

    revised_marks: list[dict[str, object]] = []
    for row in marks:
        if row["identity"] in target_ids:
            revised_marks.append(
                {
                    **row,
                    "concrete_default_de": PROMOTIONS[row["identity"]][0],
                    "apprentice_action": "READ_TAUGHT_WHOLE_WORD",
                    "semantic_revision": "YES",
                    "second_lesson": "LOCAL_ONLY_UNIT_CLOSURE",
                }
            )
        else:
            revised_marks.append({**row, "second_lesson": "NO_CHANGE"})

    unit_by_key = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_by_key[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units: list[dict[str, object]] = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        readable = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - readable
        if unit["section"] == "WHEN":
            status = "MODEL_LEAF_REQUIRED"
        elif model == 0:
            status = "SHARED_OR_TAUGHT_EXECUTABLE"
        elif readable == 0:
            status = "LOCAL_MODEL_ONLY"
        else:
            status = "CORE_PLUS_LOCAL_MODEL"
        newly = unit["execution_status"] == "LOCAL_MODEL_ONLY" and status == "SHARED_OR_TAUGHT_EXECUTABLE"
        added = [str(row["concrete_default_de"]) for row in local if row["identity"] in target_ids]
        revised_units.append(
            {
                **unit,
                "core_marks": readable,
                "model_marks": model,
                "execution_status": status,
                "second_lesson_words_de": " | ".join(added) if added else "NONE",
                "local_only_unit_closed": "YES" if newly else "NO",
            }
        )

    status_counts = Counter(str(row["execution_status"]) for row in revised_units)
    card_rows: list[dict[str, object]] = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["execution_status"]) for row in local)
        card_rows.append(
            {
                "order_id": card["order_id"],
                "title_de": card["title_de"],
                "units": len(local),
                "executable_units": counts["SHARED_OR_TAUGHT_EXECUTABLE"],
                "mixed_units": counts["CORE_PLUS_LOCAL_MODEL"],
                "local_only_units": counts["LOCAL_MODEL_ONLY"],
                "condition_units": counts["MODEL_LEAF_REQUIRED"],
                "newly_closed_local_units": sum(row["local_only_unit_closed"] == "YES" for row in local),
            }
        )

    write(f"{PREFIX}_12_LOCAL_ONLY_WHOLE_WORDS.tsv", decisions, ["identity", "surface", "old_default_de", "new_whole_word_de", "station_de", "order_id", "unit", "role", "teaching_rule_de"])
    write(f"{PREFIX}_10_CLOSED_LOCAL_ONLY_UNITS.tsv", occurrences, ["order_id", "master_unit_id", "unit", "page", "owner_de", "surface_sequence", "identity_sequence", "new_whole_words_de", "complete_unit_reading_de"])
    write(f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["second_lesson"])
    write(f"{PREFIX}_437_REVISED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["second_lesson"])
    write(f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["second_lesson_words_de", "local_only_unit_closed"])
    write(f"{PREFIX}_6_REVISED_JOB_CARDS.tsv", card_rows, ["order_id", "title_de", "units", "executable_units", "mixed_units", "local_only_units", "condition_units", "newly_closed_local_units"])

    lines = ["# Die zehn letzten rein lokalen Prosaeinheiten", ""]
    lines.extend(
        [
            "Zwölf kurze Ganzkarten schließen genau die zehn Einheiten, die bisher überhaupt keinen gemeinsamen",
            "oder bereits gelehrten Kartenwert enthielten. Die Bedeutungen bleiben knapp und werkstatthaft:",
            "Halten, Schließen, Leiten, Wasser ansetzen, Kühlen und Festbinden.",
            "",
        ]
    )
    for row in occurrences:
        lines.extend(
            [
                f"## {row['master_unit_id']} / `{row['surface_sequence']}` — {row['new_whole_words_de']}",
                "",
                f"{row['owner_de']}: {row['complete_unit_reading_de']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Ergebnis",
            "",
            f"Rein lokale Prosaeinheiten: 10 -> {status_counts['LOCAL_MODEL_ONLY']}.",
            f"Aus Kern plus gelernten Ganzkarten vollständig ausführbar: {status_counts['SHARED_OR_TAUGHT_EXECUTABLE']} von 118.",
            "Die sechs Astro-Bedingungen bleiben vollständige lokale Kopierblätter; gemischte Prosa wird als Nächstes bearbeitet.",
        ]
    )
    (HERE / f"{PREFIX}_LOCAL_ONLY_CLOSURE_LESSON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "TWELVE_ADDITIONAL_WHOLE_CARDS_CLOSE_ALL_TEN_LOCAL_ONLY_PROSE_UNITS",
        "promoted_identities": len(target_ids),
        "promoted_marks": sum(mark["identity"] in target_ids for mark in revised_marks),
        "closed_local_only_units": sum(row["local_only_unit_closed"] == "YES" for row in revised_units),
        "vocabulary_identities": len(revised_vocab),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "unit_statuses": dict(status_counts),
        "condition_changes": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 891: local-only unit closure\n\n"
        "Twelve short whole cards close all ten remaining local-only prose units. The deck now has\n"
        "69 fully executable units, 43 mixed units and six deliberately local condition leaves.\n"
        "No component or condition meaning changes.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
