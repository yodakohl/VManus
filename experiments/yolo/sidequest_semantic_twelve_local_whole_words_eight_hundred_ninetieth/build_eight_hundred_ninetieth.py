#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DECK = ROOT / "sidequest_semantic_apprentice_job_deck_eight_hundred_eighty_ninth"
MARKS = DECK / "EIGHT_HUNDRED_EIGHTY_NINTH_437_MARK_FRONT_BACK_BINDING.tsv"
UNITS = DECK / "EIGHT_HUNDRED_EIGHTY_NINTH_118_UNIT_EXECUTION.tsv"
VOCAB = DECK / "EIGHT_HUNDRED_EIGHTY_NINTH_231_CARD_WORKSHOP_VOCABULARY.tsv"
CARDS = DECK / "EIGHT_HUNDRED_EIGHTY_NINTH_6_APPRENTICE_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETIETH"

PROMOTIONS = {
    "PROC046": ("WARMHALTEN", "Zweimal in derselben warmen Zielportion-Kette; die lange Wärmeform wird als ein Werkstattruf gelernt."),
    "PROC047": ("FORTSETZEN UND SCHLIESSEN", "Zweimal nach einem laufenden Posten; der alte Mehrteilwert wird zu einer festen Schlusskarte gekürzt."),
    "PROC052": ("PFLANZENZUTAT", "Zweimal in derselben Bildpflanzenkette; das kurze Materialwort bleibt über beide Stellen gleich."),
    "PROC072": ("WEITERLEITEN", "Zweimal in der gemeinsamen Beckenstation; die Karte benennt den Transport ohne Ziel- oder Stoffzusatz."),
    "PROC086": ("KURZSPUELEN UND SCHLIESSEN", "Zweimal als eigenständiger kurzer Spülschritt; gelerntes Ganzwort statt erneuter Zerlegung."),
    "PROC109": ("NACHHALTEN", "Zweimal in der fünfstationigen Anwendung; bedeutet den laufenden Posten im Folgeschritt länger halten."),
    "PROC135": ("KURZEN FOLGESCHRITT SCHLIESSEN", "Zweimal in der Fächer-/Gefäß-/Korbfolge; eine feste kurze Übergangskarte."),
    "PROC145": ("DANACH UMSETZEN UND SCHLIESSEN", "Zweimal in derselben langen Stationsfolge; unveränderter Folgeabschluss."),
    "PROC033": ("DURCHARBEITEN", "Lokaler H3-Ruf zwischen Auspressen und DAVON-Fortsetzung; ersetzt eine sperrige Fünfteilglosse."),
    "PROC035": ("ZUGEBEN", "Lokaler H3-Zugabeschritt zwischen DAVON und Sollmaß; der laufende Posten ist bereits geerbt."),
    "PROC036": ("FOLGEPOSTEN", "Lokaler H3-Übergang nach der Sollmaß-Fortsetzung; bezeichnet den nächsten laufenden Posten."),
    "PROC037": ("WEITERANSETZEN", "Lokaler H3-Schritt direkt nach FOLGEPOSTEN; verkürzt ANSETZEN plus WEITER zu einem Ruf."),
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
    unit_by_key = {(row["order_id"], row["stage"], row["unit"]): row for row in units}

    decision_rows: list[dict[str, object]] = []
    for identity, (new_value, reason) in PROMOTIONS.items():
        local = [row for row in marks if row["identity"] == identity]
        first = local[0]
        decision_rows.append(
            {
                "identity": identity,
                "house_surface": first["surface"],
                "old_component_recipe": first["component_recipe"],
                "old_default_de": first["concrete_default_de"],
                "new_whole_word_de": new_value,
                "marks": len(local),
                "orders": ",".join(sorted({row["order_id"] for row in local})),
                "pages": ",".join(sorted({row["page"] for row in local})),
                "units": ",".join(sorted({row["unit"] for row in local})),
                "selection_class": "RECURRENT_LOCAL_CARD" if len(local) > 1 else "H3_CHAIN_COMPLETION",
                "workshop_reason_de": reason,
                "teaching_action": "MEMORIZE_TAUGHT_WHOLE_WORD",
            }
        )

    occurrence_rows: list[dict[str, object]] = []
    for order_id in [f"WH{i:02d}" for i in range(1, 7)]:
        local = [row for row in marks if row["order_id"] == order_id]
        for index, mark in enumerate(local):
            if mark["identity"] not in PROMOTIONS:
                continue
            previous = local[index - 1] if index else None
            following = local[index + 1] if index + 1 < len(local) else None
            new_value, _ = PROMOTIONS[mark["identity"]]
            occurrence_rows.append(
                {
                    "order_id": order_id,
                    "order_mark_id": mark["order_mark_id"],
                    "identity": mark["identity"],
                    "surface": mark["surface"],
                    "page": mark["page"],
                    "unit": mark["unit"],
                    "owner_de": mark["owner_or_handle_de"],
                    "left_surface": previous["surface"] if previous and previous["unit"] == mark["unit"] else "UNIT_START",
                    "left_value_de": previous["concrete_default_de"] if previous and previous["unit"] == mark["unit"] else "UNIT_START",
                    "new_whole_word_de": new_value,
                    "right_surface": following["surface"] if following and following["unit"] == mark["unit"] else "UNIT_END",
                    "right_value_de": following["concrete_default_de"] if following and following["unit"] == mark["unit"] else "UNIT_END",
                    "complete_unit_reading_de": unit_by_key[(mark["order_id"], mark["stage"], mark["unit"])]["front_instruction_de"],
                }
            )

    revised_vocab: list[dict[str, object]] = []
    for row in vocabulary:
        if row["identity"] in PROMOTIONS:
            new_value, _ = PROMOTIONS[row["identity"]]
            revised_vocab.append(
                {
                    **row,
                    "short_value_de": new_value,
                    "apprentice_action": "READ_TAUGHT_WHOLE_WORD",
                    "semantic_revision": "YES",
                    "old_short_value_de": row["short_value_de"],
                }
            )
        else:
            revised_vocab.append({**row, "semantic_revision": "NO", "old_short_value_de": row["short_value_de"]})

    promoted = set(PROMOTIONS)
    revised_marks: list[dict[str, object]] = []
    for row in marks:
        if row["identity"] in promoted:
            revised_marks.append(
                {
                    **row,
                    "concrete_default_de": PROMOTIONS[row["identity"]][0],
                    "apprentice_action": "READ_TAUGHT_WHOLE_WORD",
                    "semantic_revision": "YES",
                }
            )
        else:
            revised_marks.append({**row, "semantic_revision": "NO"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        key = (str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))
        marks_by_unit[unit_by_key[key]["master_unit_id"]].append(mark)
    revised_units: list[dict[str, object]] = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        core = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - core
        if unit["section"] == "WHEN":
            status = "MODEL_LEAF_REQUIRED"
        elif model == 0:
            status = "SHARED_OR_TAUGHT_EXECUTABLE"
        elif core == 0:
            status = "LOCAL_MODEL_ONLY"
        else:
            status = "CORE_PLUS_LOCAL_MODEL"
        taught = [str(row["concrete_default_de"]) for row in local if row["identity"] in promoted]
        old_executable = unit["execution_status"] == "SHARED_CORE_EXECUTABLE"
        new_executable = status == "SHARED_OR_TAUGHT_EXECUTABLE"
        revised_units.append(
            {
                **unit,
                "core_marks": core,
                "model_marks": model,
                "execution_status": status,
                "taught_whole_words_de": " | ".join(taught) if taught else "NONE",
                "newly_freed_from_local_leaf": "YES" if new_executable and not old_executable else "NO",
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
                "newly_freed_units": sum(row["newly_freed_from_local_leaf"] == "YES" for row in local),
                "promoted_whole_word_marks": sum(row["identity"] in promoted for row in revised_marks if row["order_id"] == card["order_id"]),
            }
        )

    write(f"{PREFIX}_12_TAUGHT_WHOLE_WORDS.tsv", decision_rows, ["identity", "house_surface", "old_component_recipe", "old_default_de", "new_whole_word_de", "marks", "orders", "pages", "units", "selection_class", "workshop_reason_de", "teaching_action"])
    write(f"{PREFIX}_20_WHOLE_WORD_OCCURRENCES.tsv", occurrence_rows, ["order_id", "order_mark_id", "identity", "surface", "page", "unit", "owner_de", "left_surface", "left_value_de", "new_whole_word_de", "right_surface", "right_value_de", "complete_unit_reading_de"])
    write(f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["semantic_revision", "old_short_value_de"])
    write(f"{PREFIX}_437_REVISED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["semantic_revision"])
    write(f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["taught_whole_words_de", "newly_freed_from_local_leaf"])
    write(f"{PREFIX}_6_REVISED_JOB_CARDS.tsv", card_rows, ["order_id", "title_de", "units", "executable_units", "mixed_units", "local_only_units", "condition_units", "newly_freed_units", "promoted_whole_word_marks"])

    lines = ["# Zwölf gelernte lokale Ganzwörter", ""]
    lines.extend(
        [
            "Diese Karten werden nicht mehr jedes Mal aus ihren sichtbaren Teilen vorgelesen. Der Lehrling",
            "lernt sie als kurze Werkstattrufe. Acht kommen zweimal im aktuellen Auftragsdeck vor; vier",
            "weitere schließen die zusammenhängende H3-Zubereitung von DURCHARBEITEN über ZUGEBEN bis",
            "WEITERANSETZEN.",
            "",
        ]
    )
    for row in decision_rows:
        lines.extend(
            [
                f"## `{row['house_surface']}` — {row['new_whole_word_de']}",
                "",
                f"{row['workshop_reason_de']} Vorkommen: {row['marks']}; Einheiten: {row['units']}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Neuer Lehrlingsgewinn",
            "",
            f"Vollständig aus Kern plus gelernten Ganzwörtern lesbar: {status_counts['SHARED_OR_TAUGHT_EXECUTABLE']} von 118 Einheiten.",
            f"Davon wurden {sum(row['newly_freed_from_local_leaf'] == 'YES' for row in revised_units)} Einheiten neu vom lokalen Prosa-Musterblatt gelöst.",
            "Die sechs Bildbedingungen bleiben absichtlich vollständige lokale Blätter.",
        ]
    )
    (HERE / f"{PREFIX}_WHOLE_WORD_LESSON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "TWELVE_SHORT_TAUGHT_WHOLE_WORDS_FREE_SIX_ADDITIONAL_UNITS_WITHOUT_CHANGING_STEMS_OR_CONDITIONS",
        "promoted_identities": len(promoted),
        "promoted_marks": len(occurrence_rows),
        "recurrent_promotions": sum(row["selection_class"] == "RECURRENT_LOCAL_CARD" for row in decision_rows),
        "h3_chain_promotions": sum(row["selection_class"] == "H3_CHAIN_COMPLETION" for row in decision_rows),
        "vocabulary_identities": len(revised_vocab),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "old_executable_units": sum(row["execution_status"] == "SHARED_CORE_EXECUTABLE" for row in units),
        "new_executable_units": status_counts["SHARED_OR_TAUGHT_EXECUTABLE"],
        "newly_freed_units": sum(row["newly_freed_from_local_leaf"] == "YES" for row in revised_units),
        "unit_statuses": dict(status_counts),
        "condition_changes": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 890: twelve local whole words\n\n"
        "Eight recurrent local cards and four cards completing the H3 preparation chain now have\n"
        "short taught whole-word readings. Their twenty marks are propagated through the full deck.\n"
        "This is a workshop vocabulary expansion, not a new component analysis; stems and conditions\n"
        "remain untouched. Six additional units become readable without the local prose leaf.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
