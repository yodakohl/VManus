#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"
P527 = ROOT / "experiments/yolo/sidequest_semantic_h3_reverse_recipe_five_hundred_twenty_seventh"
P528 = ROOT / "experiments/yolo/sidequest_semantic_h4_parallel_recipe_five_hundred_twenty_eighth"
P529 = ROOT / "experiments/yolo/sidequest_semantic_h5_formulary_five_hundred_twenty_ninth"
P530 = ROOT / "experiments/yolo/sidequest_semantic_f10_two_section_article_five_hundred_thirtieth"


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


def main() -> None:
    all_events = read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    herbal = [row for row in all_events if row["record"].startswith("H")]
    semantic_sources = (
        read_tsv(P530 / "FIVE_HUNDRED_THIRTIETH_F10_THIRTY_EIGHT_EVENT_ARTICLE.tsv")
        + read_tsv(P527 / "FIVE_HUNDRED_TWENTY_SEVENTH_H3_SEVENTEEN_EVENT_REVERSE_BUILD.tsv")
        + read_tsv(P528 / "FIVE_HUNDRED_TWENTY_EIGHTH_H4_EIGHTEEN_EVENT_REVERSE_BUILD.tsv")
        + read_tsv(P529 / "FIVE_HUNDRED_TWENTY_NINTH_H5_TWENTY_SEVEN_EVENT_REVERSE_BUILD.tsv")
    )
    semantic_by_event = {row["event_id"]: row for row in semantic_sources}

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in herbal:
        by_card[row["card_no"]].append(row)
    dictionary: list[dict[str, str]] = []
    for card_no, rows in by_card.items():
        readings = {row["apprentice_spoken_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"non-invariant card reading {card_no}: {readings}")
        dictionary.append(
            {
                "card_no": card_no,
                "component_parse": rows[0]["component_parse"],
                "invariant_card_reading_de": next(iter(readings)),
                "occurrences": str(len(rows)),
                "records": "|".join(dict.fromkeys(row["record"] for row in rows)),
                "pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
                "visible_surfaces": "|".join(dict.fromkeys(row["renderer_final_surface"] for row in rows)),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "cross_record": "YES" if len({row["record"] for row in rows}) > 1 else "NO",
                "default_policy": "ONE_CARD_ONE_WORKSHOP_READING",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIRST_SIXTY_SIX_CARD_HERBAL_DICTIONARY.tsv", dictionary)

    interlinear: list[dict[str, str]] = []
    for row in herbal:
        semantic = semantic_by_event[row["event_id"]]
        interlinear.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "invariant_card_reading_de": row["apprentice_spoken_reading_de"],
                "minimum_source_clause_de": semantic["minimum_source_clause_de"],
                "visible_owner_de": semantic.get("visible_owner_de", semantic.get("owner_noun_de", "")),
                "primitive": row["procedure_tokens"],
                "terminal": "YES" if "CLOSE" in row["procedure_tokens"].split(">") else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIRST_ONE_HUNDRED_EVENT_INTERLINEAR.tsv", interlinear)

    statement_sources = (
        read_tsv(P530 / "FIVE_HUNDRED_THIRTIETH_FIVE_F10_STATEMENTS.tsv")
        + read_tsv(P527 / "FIVE_HUNDRED_TWENTY_SEVENTH_FOUR_H3_STATEMENTS.tsv")
        + read_tsv(P528 / "FIVE_HUNDRED_TWENTY_EIGHTH_FOUR_H4_STATEMENTS.tsv")
        + read_tsv(P529 / "FIVE_HUNDRED_TWENTY_NINTH_SIX_H5_STATEMENTS.tsv")
    )
    statement_rows: list[dict[str, str]] = []
    for row in statement_sources:
        members = [item for item in interlinear if item["statement_id"] == row["statement_id"]]
        statement_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": members[0]["page"],
                "record": members[0]["record"],
                "loci": row.get("loci", "|".join(dict.fromkeys(item["locus"] for item in members))),
                "event_ids": row["event_ids"],
                "surfaces": row["surfaces"],
                "card_literal_de": row.get("card_licensed_literal_de", row.get("card_sequence_literal_de", "")),
                "fluent_working_reading_de": row["workshop_expanded_reading_de"],
                "visible_owner_de": row.get("visible_owner_de", row.get("section_owner", members[0]["visible_owner_de"])),
                "terminal": "YES" if any(item["terminal"] == "YES" for item in members) else "NO",
                "physical_line_is_sentence_boundary": "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIRST_NINETEEN_STATEMENT_EDITION.tsv", statement_rows)

    articles = [
        {
            "article_id": "A01_F10R",
            "page": "f10r",
            "records": "H1|H2",
            "events": "38",
            "statements": "5",
            "visible_owner": "one pictured plant; H1 root/storage axis, H2 upper stem/flower/bud/leaf set",
            "fluent_working_article_de": "Vom sichtbaren Wurzel-/Speicherposten kurz abziehen und den bereiten Ansatz aktivieren. Davon den Posten ins Arbeitsfach eintragen und durch den Lauf führen; danach weiter abziehen, nach Maß ansetzen und kurz eintragen. Diesen Posten ansetzen, danach weiter abziehen und ihn bereit halten. Nun vom sichtbaren oberen Sprossposten kurz aus dem Ansatz abziehen und ihn bereit halten. Den Ansatz auf das Bereitschaftsmaß bringen, weiterführen, abmessen und an die Zielstelle geben. Danach aus dem Ansatz abziehen, den Ansatz weiterführen und nach Maß davon nehmen. Den laufenden Posten dem Ansatz zuführen, ihn bis zur Sollstufe bringen und das Arbeitsmaß abziehen.",
            "process_emphasis": "ROOT_TO_UPPER_PART_TWO_SECTION_PROCESS",
        },
        {
            "article_id": "A02_F11R",
            "page": "f11r",
            "records": "H3",
            "events": "17",
            "statements": "4",
            "visible_owner": "whole pictured dense-crown plant",
            "fluent_working_article_de": "Die abgebildete Pflanze an der Arbeitsstelle weiter bearbeiten und auswringen. Den gewonnenen Posten für das vorgeschriebene Maß stehen lassen, in den Empfänger geben und den Empfangsbestand abziehen. Den abgezogenen Bestand zurückhalten. Davon die vorgeschriebene Menge weiter zuführen. Danach den laufenden Arbeitsgang fortsetzen und den Posten bis zur Bereitschaft halten.",
            "process_emphasis": "EXPRESS_HOLD_RECEIVE_DRAW_REINTRODUCE_READY",
        },
        {
            "article_id": "A03_F55V",
            "page": "f55v",
            "records": "H4",
            "events": "18",
            "statements": "4",
            "visible_owner": "whole pictured broad-leaf plant",
            "fluent_working_article_de": "Für die abgebildete Pflanze das vorgeschriebene Maß setzen, zwei Portionen zuführen und den Schritt schließen. Eine weitere Menge abmessen, den Posten umsetzen und verwahren. Die vorgeschriebene Menge zuführen, kurz aus dem Arbeitsbestand abziehen, länger wärmen und den Schritt schließen. Danach nach Maß an der Zielstelle ansetzen, den Posten weiter eintragen und eine Portion des Ansatzes zuführen.",
            "process_emphasis": "METER_PORTION_STORE_HEAT_TARGET",
        },
        {
            "article_id": "A04_F56R",
            "page": "f56r",
            "records": "H5",
            "events": "27",
            "statements": "6",
            "visible_owner": "whole pictured multihead coiled plant",
            "fluent_working_article_de": "Eine Gabe aus dem Ansatz nehmen und nach Maß an der Zielstelle ansetzen. Eine weitere Gabe zuführen; danach erneut aus dem Ansatz nehmen und an der Zielstelle ansetzen. Die Anwendung fortsetzen, diese Gabe ansetzen und den Posten länger durch den Durchlass führen; schließen. Eine Gabe halten, kurz zuführen und am laufenden Posten erneut ansetzen. Den Posten und den Auszug ansetzen, dann zur Zielstelle zuführen. Eine weitere Gabe aus derselben Quelle zuführen und danach eine Arbeitsportion nehmen. Danach den Posten kurz weiter zuführen, nach dem vorgeschriebenen Maß.",
            "process_emphasis": "REPEATED_DOSE_TARGET_PASSAGE_EXTRACT",
        },
    ]
    write_tsv("FIVE_HUNDRED_THIRTY_FIRST_FOUR_COMPLETE_HERBAL_ARTICLES.tsv", articles)

    cross = [row for row in dictionary if row["cross_record"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_FIRST_TEN_CROSS_RECORD_CARDS.tsv", cross)

    primitive_counts: list[dict[str, str]] = []
    for primitive in ["SOURCE_DRAW", "ACTIVATE_CHARGE", "TARGET_HANDOFF", "METER_CHECK", "MOVE_PASS", "HOLD_STATE", "CONTINUE_USE", "CLOSE"]:
        primitive_counts.append(
            {
                "primitive": primitive,
                **{
                    record.lower() + "_count": str(
                        sum(
                            primitive in row["primitive"].split(">")
                            for row in interlinear
                            if row["record"] == record
                        )
                    )
                    for record in ("H1", "H2", "H3", "H4", "H5")
                },
                "total": str(sum(primitive in row["primitive"].split(">") for row in interlinear)),
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIRST_HERBAL_PRIMITIVE_PROFILE.tsv", primitive_counts)

    lines = [
        "# Vollständige Herbal-Arbeitsausgabe",
        "",
        "Diese Ausgabe umfasst exakt die vier festen Herbal-Seiten und fünf formalen Records.",
        "Pflanzenarten, Krankheiten und ungenannte Flüssigkeiten werden nicht ergänzt.",
        "",
    ]
    for article in articles:
        lines.extend(
            [
                f"## {article['page']} — {article['records']}",
                "",
                f"Bildbesitzer: {article['visible_owner']}.",
                "",
                article["fluent_working_article_de"],
                "",
            ]
        )
    (HERE / "FIVE_HUNDRED_THIRTY_FIRST_COMPLETE_HERBAL_EDITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    summary = {
        "status": "PASS",
        "pages": 4,
        "records": 5,
        "articles": 4,
        "events": len(interlinear),
        "statements": len(statement_rows),
        "exact_cards": len(dictionary),
        "cross_record_cards": len(cross),
        "measure_card_proc009_occurrences": next(int(row["occurrences"]) for row in dictionary if row["card_no"] == "PROC009"),
        "blank_readings": sum(not row["minimum_source_clause_de"] for row in interlinear),
    }
    (HERE / "FIVE_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
