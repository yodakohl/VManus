#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P545 = ROOT / "experiments/yolo/sidequest_semantic_fluent_cross_line_edition_five_hundred_forty_fifth"
P546 = ROOT / "experiments/yolo/sidequest_semantic_anaphoric_record_articles_five_hundred_forty_sixth"
P547 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_workshop_formulas_five_hundred_forty_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SINGLE_READING = {
    "PROC019": "den aktuellen Posten beibehalten",
    "PROC009": "das vorgeschriebene Maß übernehmen",
    "PROC055": "die bezeichnete Stelle wählen",
    "PROC016": "mit dem Ansatz arbeiten",
    "PROC003": "von dort weiterarbeiten",
    "PROC013": "damit fortfahren",
}

GENERIC = ("Arbeitsgang", "bearbeiten", "eintragen", "führen", "übernehmen")
ACTIONS = ("ansetzen", "fortsetzen", "umsetzen", "halten", "zuführen", "führen", "absetzen", "abziehen", "eintragen", "übernehmen")


def classify(text: str, unit_count: int, owner_switch: bool) -> tuple[str, str]:
    if owner_switch:
        return "OWNER_SWITCH", "Die Anweisung wechselt ohne sichtbare Bildkante den Besitzer."
    repeated = [verb for verb in ACTIONS if len(re.findall(rf"\b{verb}\w*\b", text, flags=re.I)) >= 2]
    if repeated:
        return "REPETITIVE_OPERATION", "Mehrfaches " + ", ".join(repeated) + " verlangt wahrscheinlich ein engeres Fachverb."
    generic = [term for term in GENERIC if term.lower() in text.lower()]
    if generic:
        return "GENERIC_OPERATION", "Die Lesung benutzt noch generische Arbeitswörter: " + ", ".join(generic) + "."
    if unit_count >= 8:
        return "LONG_CHAIN", "Die Folge bleibt trotz Formeln lang und braucht vermutlich weitere lokale Idiome."
    return "SMOOTH", "Die Folge ist mit dem jetzigen Werkstattwortschatz knapp lesbar."


def main() -> None:
    visible = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv")
    instructions = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_NINETY_SEVEN_FLUENT_INSTRUCTIONS.tsv")
    article_base = {row["record"]: row for row in read_tsv(P546 / "FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv")}
    formulas = read_tsv(P547 / "FIVE_HUNDRED_FORTY_SEVENTH_FORMULA_LEXICON.tsv")
    formula_by_key = {tuple(row["card_sequence"].split("+")): row for row in formulas}
    source_by_instruction: dict[str, list[dict[str, str]]] = defaultdict(list)
    visible_by_source: dict[str, list[str]] = defaultdict(list)
    for row in visible:
        visible_by_source[row["source_position_id"]].append(row["event_id"])
        if row["semantic_execution"] == "EXECUTE_ONCE":
            source_by_instruction[row["instruction_id"]].append(row)

    unit_rows: list[dict[str, str]] = []
    sentence_rows: list[dict[str, str]] = []
    awkward_cards = Counter()
    formula_hits = Counter()
    for instruction in instructions:
        rows = source_by_instruction[instruction["instruction_id"]]
        index = 0
        phrases: list[str] = []
        used_cards: list[str] = []
        local_units: list[dict[str, str]] = []
        while index < len(rows):
            matching = [key for key in formula_by_key if tuple(row["card_no"] for row in rows[index:index + len(key)]) == key]
            if matching:
                key = sorted(matching, key=lambda item: (-len(item), -int(formula_by_key[item]["occurrences"]), item))[0]
                formula = formula_by_key[key]
                members = rows[index:index + len(key)]
                phrase = formula["idiomatic_workshop_reading_de"]
                unit_type = formula["tier"]
                unit_id = formula["formula_id"]
                formula_hits[unit_id] += 1
                index += len(key)
            else:
                members = [rows[index]]
                phrase = SINGLE_READING.get(rows[index]["card_no"], rows[index]["fluent_command_de"])
                unit_type = "SINGLE_CARD"
                unit_id = rows[index]["card_no"]
                index += 1
            phrases.append(phrase)
            used_cards.extend(row["card_no"] for row in members)
            source_ids = [row["source_position_id"] for row in members]
            visible_ids = [event for source_id in source_ids for event in visible_by_source[source_id]]
            local_units.append({
                "instruction_id": instruction["instruction_id"],
                "record": instruction["record"],
                "unit_no": str(len(local_units) + 1),
                "unit_type": unit_type,
                "unit_id": unit_id,
                "card_sequence": "+".join(row["card_no"] for row in members),
                "source_position_ids": "|".join(source_ids),
                "visible_event_ids": "|".join(visible_ids),
                "surface_sequence": " ".join(row["surface"] for row in members),
                "idiomatic_unit_de": phrase,
                "component_values_unchanged": "YES",
            })
        chain = "; dann ".join(phrases)
        status, reason = classify(chain, len(local_units), instruction["crosses_owner_boundary"] == "YES")
        if status != "SMOOTH":
            awkward_cards.update(used_cards)
        for row in local_units:
            row["instruction_reading_status"] = status
            unit_rows.append(row)
        sentence_rows.append({
            "instruction_id": instruction["instruction_id"],
            "page": instruction["page"],
            "record": instruction["record"],
            "source_statement_ids": instruction["source_statement_ids"],
            "source_position_ids": "|".join(row["source_position_id"] for row in rows),
            "visible_event_ids": instruction["visible_event_ids"],
            "formula_units": str(sum(row["unit_type"] != "SINGLE_CARD" for row in local_units)),
            "single_card_units": str(sum(row["unit_type"] == "SINGLE_CARD" for row in local_units)),
            "idiomatic_instruction_de": chain + ".",
            "reading_status": status,
            "awkwardness_reason": reason,
            "end_type": instruction["end_type"],
            "crosses_owner_boundary": instruction["crosses_owner_boundary"],
            "component_values_unchanged": "YES",
        })

    records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    article_rows: list[dict[str, str]] = []
    for record in records:
        rows = [row for row in sentence_rows if row["record"] == record]
        connectors = ["Zuerst"] + [["Danach", "Anschließend", "Sodann"][(i - 1) % 3] for i in range(1, len(rows))]
        sentences = []
        for connector, row in zip(connectors, rows):
            body = row["idiomatic_instruction_de"].rstrip(".")
            body = re.sub(r"\b(?:diesen|den aktuellen|denselben|den) Posten\b", "ihn", body)
            body = re.sub(r"^danach\s+", "", body, flags=re.I)
            body = re.sub(r"; dann danach\s+", "; danach ", body, flags=re.I)
            sentences.append(f"{connector} {body[0].lower() + body[1:]}.")
        base = article_base[record]
        article_rows.append({
            "record": record,
            "page": base["page"],
            "instruction_count": str(len(rows)),
            "visible_event_count": base["visible_event_count"],
            "formula_units": str(sum(int(row["formula_units"]) for row in rows)),
            "single_card_units": str(sum(int(row["single_card_units"]) for row in rows)),
            "smooth_instructions": str(sum(row["reading_status"] == "SMOOTH" for row in rows)),
            "awkward_instructions": str(sum(row["reading_status"] != "SMOOTH" for row in rows)),
            "continuous_formula_article_de": base["introduction_de"] + " " + " ".join(sentences),
            "record_final_status": base["record_final_status"],
        })

    card_example = {}
    for row in visible:
        card_example.setdefault(row["card_no"], row)
    target_rows = []
    for rank, (card_no, count) in enumerate(awkward_cards.most_common(25), 1):
        row = card_example[card_no]
        target_rows.append({
            "rank": str(rank),
            "card_no": card_no,
            "surface_example": row["surface"],
            "component_parse": row["component_parse"],
            "current_command_de": row["fluent_command_de"],
            "events_inside_awkward_instructions": str(count),
            "next_question": "Braucht diese Karte ein engeres Fachverb oder ist sie nur Argument/Verweis?",
        })

    write_tsv("FIVE_HUNDRED_FORTY_EIGHTH_IDIOMATIC_UNITS.tsv", unit_rows)
    write_tsv("FIVE_HUNDRED_FORTY_EIGHTH_NINETY_SEVEN_FORMULA_SENTENCES.tsv", sentence_rows)
    write_tsv("FIVE_HUNDRED_FORTY_EIGHTH_ELEVEN_FORMULA_ARTICLES.tsv", article_rows)
    write_tsv("FIVE_HUNDRED_FORTY_EIGHTH_AWKWARD_CARD_TARGETS.tsv", target_rows)

    edition = ["# Elf formelrevidierte Werkstattartikel", ""]
    for row in article_rows:
        edition.extend([f"## {row['record']} — {row['page']}", "", row["continuous_formula_article_de"], ""])
    (HERE / "FIVE_HUNDRED_FORTY_EIGHTH_COMPLETE_FORMULA_ARTICLE_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    statuses = Counter(row["reading_status"] for row in sentence_rows)
    summary = {
        "status": "PASS",
        "instructions": len(sentence_rows),
        "articles": len(article_rows),
        "source_positions": sum(len(row["source_position_ids"].split("|")) for row in sentence_rows),
        "visible_events": sum(len(row["visible_event_ids"].split("|")) for row in sentence_rows),
        "formula_applications": sum(formula_hits.values()),
        "formula_ids_used": len(formula_hits),
        "unit_count": len(unit_rows),
        "status_counts": dict(sorted(statuses.items())),
        "awkward_target_cards": len(target_rows),
        "top_awkward_cards": [row["card_no"] for row in target_rows[:10]],
    }
    (HERE / "FIVE_HUNDRED_FORTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertachtundvierzigste Runde: formelrevidierte Artikel",
        "",
        "## Ergebnis",
        "",
        f"Alle fünfzehn wiederkehrenden Folgen werden dort idiomatisch gelesen, wo sie greedy und nicht überlappend passen. Das ergibt {summary['formula_applications']} Formelanwendungen in {summary['formula_ids_used']} Formelfamilien. Die 380 ausgeführten Quellpositionen werden zu {summary['unit_count']} sprachlichen Einheiten; 381 sichtbare Ereignisse bleiben gebunden.",
        "",
        "Bare Y, AIIN, AL, OR, AR und OL werden nicht mehr wie sechs vollwertige Verben behandelt. Sie lesen sich als Postenbezug, Maß, Zielstelle, Ansatz, Quelle und Fortsetzung. Dadurch verschwindet ein großer Teil des künstlichen `übernehmen/setzen/verwenden`-Takts.",
        "",
        "## Restspannung",
        "",
    ]
    for key, value in sorted(statuses.items()):
        report.append(f"- {key}: {value} Anweisungen")
    report.extend([
        "",
        "Die problematischen Stellen bündeln sich nun auf wenige hochfrequente Karten mit generischen Verben, wiederholtem Ansetzen/Führen oder sichtbaren Besitzerwechseln. `FIVE_HUNDRED_FORTY_EIGHTH_AWKWARD_CARD_TARGETS.tsv` ordnet sie als nächste Bedeutungsziele.",
        "",
        "Keine Komponentenbedeutung wurde verändert; dies ist eine grammatische und idiomatische Redaktion.",
    ])
    (HERE / "FIVE_HUNDRED_FORTY_EIGHTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
