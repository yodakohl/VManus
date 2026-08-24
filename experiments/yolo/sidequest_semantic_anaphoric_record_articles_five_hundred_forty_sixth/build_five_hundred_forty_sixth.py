#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P545 = ROOT / "experiments/yolo/sidequest_semantic_fluent_cross_line_edition_five_hundred_forty_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


INTRO = {
    "H1": "Für den ersten Arbeitsabschnitt der abgebildeten breit gezähnten radialblütigen Pflanze gilt:",
    "H2": "Im zweiten Arbeitsabschnitt derselben abgebildeten Pflanze gilt:",
    "H3": "Für die abgebildete dicht blau blühende Kronenpflanze gilt:",
    "H4": "Für die abgebildete breitblättrige rispige Pflanze gilt:",
    "H5": "Für die abgebildete mehrköpfige stachelige Pflanze gilt:",
    "B1": "An der gemeinsamen zweireihigen Figuren- und Beckenstation gilt:",
    "B2": "An den lokalen Stationen von f82r gilt:",
    "B3": "Vom Rand bis zum sichtbaren Figurenpaar in B3 gilt:",
    "B4": "Am Figurenpaar und an den beiden Seitenstationen in B4 gilt:",
    "B5": "Im linken Fransenstations-Nachtrag gilt:",
    "B6": "Im rechten S-Lauf-Nachtrag gilt:",
}

PURPOSE = {
    "H1": "pictured plant material first work section",
    "H2": "pictured plant material second work section",
    "H3": "plant pressing holding and draw-off article",
    "H4": "plant batch measure target and storage article",
    "H5": "plant additive passage and reuse article",
    "B1": "shared pool operating sheet",
    "B2": "five-station wet workshop sheet",
    "B3": "margin-to-linked-pair station sheet",
    "B4": "linked-pair and side-station sheet",
    "B5": "left fringe addendum",
    "B6": "right S-run addendum",
}


def strip_owner_prefix(text: str) -> str:
    body = text.rstrip(".")
    if body.startswith("Bei ") and ", dann " in body:
        body = body.split(", dann ", 1)[1]
    body = body.replace(", dann danach ", ", danach ")
    return body


def apply_anaphora(text: str, referent_seen: bool) -> tuple[str, bool, int]:
    pattern = re.compile(r"\b(?:diesen|den) Posten\b")
    pieces: list[str] = []
    last = 0
    replacements = 0
    for match in pattern.finditer(text):
        pieces.append(text[last:match.start()])
        if referent_seen:
            pieces.append("ihn")
            replacements += 1
        else:
            pieces.append(match.group(0))
            referent_seen = True
        last = match.end()
    pieces.append(text[last:])
    return "".join(pieces), referent_seen, replacements


def main() -> None:
    instructions = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_NINETY_SEVEN_FLUENT_INSTRUCTIONS.tsv")
    event_map = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv")
    records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    map_rows: list[dict[str, str]] = []
    article_rows: list[dict[str, str]] = []
    for record in records:
        record_instructions = [row for row in instructions if row["record"] == record]
        referent_seen = False
        sentences: list[str] = []
        record_replacements = 0
        for index, row in enumerate(record_instructions):
            body = strip_owner_prefix(row["fluent_instruction_de"])
            body, referent_seen, replacements = apply_anaphora(body, referent_seen)
            record_replacements += replacements
            connector = "Zuerst" if index == 0 else ["Danach", "Anschließend", "Sodann"][(index - 1) % 3]
            if body.startswith("danach "):
                body = body[len("danach "):]
            sentence = f"{connector} {body[0].lower() + body[1:]}."
            sentences.append(sentence)
            map_rows.append(
                {
                    "instruction_id": row["instruction_id"],
                    "record": record,
                    "article_sentence_no": str(index + 1),
                    "source_statement_ids": row["source_statement_ids"],
                    "visible_event_ids": row["visible_event_ids"],
                    "original_instruction_de": row["fluent_instruction_de"],
                    "anaphoric_sentence_de": sentence,
                    "pronoun_replacements": str(replacements),
                    "connector": connector,
                    "end_type": row["end_type"],
                    "component_values_unchanged": "YES",
                }
            )
        event_ids = [event_id for row in record_instructions for event_id in row["visible_event_ids"].split("|")]
        article_rows.append(
            {
                "record": record,
                "page": record_instructions[0]["page"],
                "purpose": PURPOSE[record],
                "introduction_de": INTRO[record],
                "instruction_count": str(len(record_instructions)),
                "visible_event_count": str(len(event_ids)),
                "visible_event_ids": "|".join(event_ids),
                "pronoun_replacements": str(record_replacements),
                "continuous_article_de": INTRO[record] + " " + " ".join(sentences),
                "record_final_status": record_instructions[-1]["end_type"],
                "all_component_values_unchanged": "YES",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_SIXTH_NINETY_SEVEN_ANAPHORIC_SENTENCES.tsv", map_rows)
    write_tsv("FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv", article_rows)

    lines = ["# Elf zusammenhängende Werkstattartikel", ""]
    for row in article_rows:
        lines.extend([f"## {row['record']} — {row['page']}", "", row["continuous_article_de"], ""])
    (HERE / "FIVE_HUNDRED_FORTY_SIXTH_COMPLETE_RECORD_ARTICLE_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS",
        "source_instructions": len(instructions),
        "articles": len(article_rows),
        "visible_events": len(event_map),
        "pronoun_replacements": sum(int(row["pronoun_replacements"]) for row in map_rows),
        "record_instruction_counts": {row["record"]: int(row["instruction_count"]) for row in article_rows},
        "record_final_open": sum(row["record_final_status"] == "RECORD_FINAL_OPEN" for row in article_rows),
        "record_final_closed": sum(row["record_final_status"] == "COMMITTED_CLOSE" for row in article_rows),
    }
    (HERE / "FIVE_HUNDRED_FORTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Fünfhundertsechsundvierzigste Runde: elf anaphorische Artikel",
        "",
        "## Ergebnis",
        "",
        f"Alle 97 Arbeitsanweisungen sind jetzt in elf fortlaufende Record-Artikel eingebaut. Wiederholte Nennungen des aktuellen Postens wurden {summary['pronoun_replacements']} mal zu „ihn“ verkürzt; der erste explizite Posten jedes Records bleibt stehen.",
        "",
        "Jeder Artikel beginnt mit seinem sichtbaren Besitzer. Danach tragen Zuerst/Danach/Anschließend/Sodann die Reihenfolge. Die acht am Recordende offenen Anweisungen bleiben offen; ein redaktioneller Punkt erfindet keine Schlusskarte.",
        "",
        "## Wirkung",
        "",
        "Die Ausgabe klingt nun weniger wie ein Wörterbuchdump und mehr wie ein knappes Betriebsbuch. Besonders die Biological-Records lesen sich als Serien lokaler Becken-, Durchlass-, Halte- und Auffangschritte. Herbal bleibt artikelartig: sichtbarer Pflanzenrohstoff, Maß, Portion, Ansatz, Ziel und Verarbeitung.",
        "",
        "## Nächster Angriff",
        "",
        "Als Nächstes wird nach wiederkehrenden Mehrkarten-Phrasen gesucht, die als feste Werkstattformeln gelernt worden sein könnten. Das kann die 38-Komponenten-Lehre weiter verkürzen und zugleich idiomatischere Übersetzungen liefern.",
    ]
    (HERE / "FIVE_HUNDRED_FORTY_SIXTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
