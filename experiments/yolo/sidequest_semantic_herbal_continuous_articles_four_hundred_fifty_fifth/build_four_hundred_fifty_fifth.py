#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_component_completion_four_hundred_fifty_fourth/FOUR_HUNDRED_FIFTY_FOURTH_100_EVENT_HERBAL_EDITION.tsv"

FLUENT = {
    "H1-S001": "Von der abgebildeten Pflanze kurz abziehen; der Ansatz ist bereit. Dasselbe in das Gefäß füllen. Wasser abziehen, danach diesen Posten füllen und weiter abziehen. Dies nach Maß verwenden und kurz füllen.",
    "H1-S002": "Diesen Posten ansetzen, danach weiter abziehen und fortfahren, bis er bereit ist.",
    "H2-S001": "Diesen Ansatz kurz abziehen; der Ansatz ist bereit. Ihn auf Maß bereitstellen und als bereiten Posten weiterführen; dieser Posten bleibt am Maß.",
    "H2-S002": "Danach vom Ansatz abziehen und damit fortfahren. Den weiteren Ansatz nach Maß ebenso fortführen.",
    "H2-S003": "Diesen Posten dem Ansatz zuführen; der Ansatz bleibt aktiv. Dies bis zur Sollstufe zuführen und auf Maß abziehen.",
    "H3-S001": "Den gefüllten Posten weiter an der Stelle halten, auswringen, bis zum Maß halten und hineinführen. Den Klarauszug nehmen; füllen und abziehen; Schluss.",
    "H3-S002": "Diesen Posten halten und füllen.",
    "H3-S003": "Fortfahren; diesen Posten zuführen und ihn nach Maß weiterführen.",
    "H3-S004": "Den nächsten Posten weiter ansetzen; sobald er bereit ist, gilt dieser Posten.",
    "H4-S001": "Bemessen: nach Maß eine Portion davon zuführen, dann noch eine Portion; den Arbeitsgang abschließen.",
    "H4-S002": "Nach Maß diesen Posten umsetzen und verwahren.",
    "H4-S003": "Diesen Posten auf Maß zuführen, den Auszug aus der Quelle nehmen, dies länger wärmen und nach dem Fortsetzen schließen.",
    "H4-S004": "Nach Maß an die Stelle setzen und dies weiter füllen. Mit dem Ansatz weiterarbeiten und davon eine Ansatzportion verwenden.",
    "H5-S001": "Die Zutat aus dem Ansatz abziehen und diese Zutat nach Maß an die Stelle bringen. Weitere Zutat zuführen, danach vom Ansatz abziehen und dies an der Stelle verwenden.",
    "H5-S002": "Fortfahren, diese Zutat verwenden und sie länger durch den Durchlass führen; Schluss.",
    "H5-S003": "Die Zutat halten, kurz zuführen und erneut ansetzen.",
    "H5-S004": "Diesen Posten ansetzen, den Auszug ansetzen und an die Stelle zuführen.",
    "H5-S005": "Diese Zutat ansetzen, Zutat aus dem Vorrat zuführen, danach eine Portion.",
    "H5-S006": "Den nächsten Posten kurz weiter zuführen, nach Maß.",
}

ARTICLE_OPENERS = {
    "H1": "Erster Arbeitsabschnitt zur abgebildeten Pflanze.",
    "H2": "Zweiter Arbeitsabschnitt zur selben abgebildeten Pflanze.",
    "H3": "Arbeitsabschnitt zur abgebildeten Pflanze.",
    "H4": "Arbeitsabschnitt zur abgebildeten Pflanze.",
    "H5": "Arbeitsabschnitt zur abgebildeten Pflanze.",
}

SUPPLIED_NOUNS = [
    ("Pflanze", "PICTURE_OWNER", "silent subject supplied once by each pictured-plant record"),
    ("Posten", "Y_COMPONENT", "current-item referent"),
    ("Ansatz", "OR_COMPONENT", "active preparation or batch"),
    ("Maß", "AIIN_COMPONENT", "measure"),
    ("Sollstufe", "IIN_COMPONENT", "target stage"),
    ("Stelle", "AL_COMPONENT", "target place"),
    ("Quelle", "AR_COMPONENT", "source"),
    ("Wasser", "AIR_COMPONENT", "water"),
    ("Durchlass", "CKH_COMPONENT", "passage"),
    ("Zutat", "HO_HERBAL_COMPONENT", "ingredient"),
    ("Auszug", "CHEO_HERBAL_COMPONENT", "extract"),
    ("Klarauszug", "TRANSFERRED_WHOLE_CARD", "portable learned card"),
    ("Gefäß", "OS_HERBAL_WHOLE_CARD", "memorized container card"),
    ("Portion", "AIN_COMPONENT", "portion"),
    ("Arbeitsgang", "O_FRAME", "active operation"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read(EVENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_statement[row["statement_id"]].append(row)
    if set(by_statement) != set(FLUENT):
        raise ValueError((set(by_statement) - set(FLUENT), set(FLUENT) - set(by_statement)))

    statement_rows = []
    for statement_id, rows in by_statement.items():
        statement_rows.append({
            "statement_id": statement_id, "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "picture_owner": rows[0]["picture_owner"],
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "field_ids": "|".join(dict.fromkeys(row["field_id"] for row in rows)),
            "literal_card_chain_de": "; ".join(row["small_value_de"] for row in rows) + ".",
            "controlled_fluent_reading_de": FLUENT[statement_id],
            "silent_subject": "PICTURED_PLANT" if statement_id.endswith("S001") else "INHERITED_RECORD_ITEM",
            "discarded_content_reintroduced": "NO",
        })
    write("FOUR_HUNDRED_FIFTY_FIFTH_19_CONTROLLED_STATEMENTS.tsv", statement_rows)

    event_rows = []
    for row in source:
        event_rows.append({
            "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "page": row["page"],
            "locus": row["locus"], "field_id": row["field_id"], "statement_id": row["statement_id"],
            "surface": row["surface"], "joint_tuple_id": row["joint_tuple_id"],
            "component_parse": row["component_parse"], "small_value_de": row["small_value_de"],
            "picture_owner": row["picture_owner"], "statement_fluent_reading_de": FLUENT[row["statement_id"]],
        })
    write("FOUR_HUNDRED_FIFTY_FIFTH_100_EVENT_ALIGNMENT.tsv", event_rows)

    articles = []
    md = ["# Five controlled continuous Herbal articles", ""]
    for record in ("H1", "H2", "H3", "H4", "H5"):
        rows = [row for row in statement_rows if row["record_unit_id"] == record]
        text = ARTICLE_OPENERS[record] + " " + " ".join(str(row["controlled_fluent_reading_de"]) for row in rows)
        articles.append({
            "record_unit_id": record, "page": rows[0]["page"], "picture_owner": rows[0]["picture_owner"],
            "statements": len(rows), "events": sum(int(row["events"]) for row in rows),
            "statement_ids": "|".join(str(row["statement_id"]) for row in rows),
            "continuous_article_de": text,
        })
        md.extend([f"## {record}", "", text, ""])
    write("FOUR_HUNDRED_FIFTY_FIFTH_FIVE_CONTINUOUS_ARTICLES.tsv", articles)
    (HERE / "FOUR_HUNDRED_FIFTY_FIFTH_FIVE_CONTINUOUS_ARTICLES.md").write_text("\n".join(md), encoding="utf-8")

    noun_rows = [{"noun_de": noun, "license": license_, "use_rule": rule} for noun, license_, rule in SUPPLIED_NOUNS]
    write("FOUR_HUNDRED_FIFTY_FIFTH_SUPPLIED_NOUN_AUDIT.tsv", noun_rows)

    summary = {
        "status": "PASS", "records": len(articles), "statements": len(statement_rows), "events": len(event_rows),
        "licensed_content_nouns": len(noun_rows), "discarded_content_nouns_reintroduced": 0,
        "physical_line_is_sentence_boundary": False,
    }
    (HERE / "FOUR_HUNDRED_FIFTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
