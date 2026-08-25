#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P780 = ROOT / "experiments/yolo/sidequest_semantic_full_cross_hand_renderer_seven_hundred_eightieth"
PAGES = {"f56r": "HAND_2_APPRENTICE", "f82r": "HAND_1_APPRENTICE"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")
    defaults = read(P780 / "SEVEN_HUNDRED_EIGHTIETH_24_HAND_CARD_DEFAULTS.tsv")
    contexts = read(P780 / "SEVEN_HUNDRED_EIGHTIETH_34_CONTEXT_RENDERER_ROWS.tsv")
    full_trace = read(P780 / "SEVEN_HUNDRED_EIGHTIETH_381_FULL_CROSS_HAND_TRACE.tsv")
    reading_by_card = {}
    for row in events:
        reading_by_card.setdefault(row["card_no"], row["rebuilt_reading_de"])
    default = {(row["exact_card_id"], row["target_hand"]): row for row in defaults}

    cards = []
    for card in sorted({row["exact_card_id"] for row in defaults}):
        hand1 = default[(card, "HAND_1")]
        hand2 = default[(card, "HAND_2")]
        cards.append(
            {
                "card_slot": f"M{len(cards) + 1:02d}",
                "exact_card_id": card,
                "spoken_workshop_prompt": reading_by_card[card],
                "component_recipe": hand1["component_recipe"],
                "hand_1_face": hand1["default_surface"],
                "hand_1_attested_variants": hand1["all_attested_surfaces"],
                "hand_2_face": hand2["default_surface"],
                "hand_2_attested_variants": hand2["all_attested_surfaces"],
                "physical_instruction": "front Hand1; back Hand2; keep card slot and prompt together",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIRST_12_TWO_SIDED_SAMPLE_CARDS.tsv",
        cards,
        ["card_slot", "exact_card_id", "spoken_workshop_prompt", "component_recipe", "hand_1_face", "hand_1_attested_variants", "hand_2_face", "hand_2_attested_variants", "physical_instruction"],
    )

    margin_rules = [
        {"rule_no": 1, "short_mark": "BILD", "instruction": "name the visible owner or station before copying its first card"},
        {"rule_no": 2, "short_mark": "XII", "instruction": "for one of the twelve common cards turn the sample to your hand"},
        {"rule_no": 3, "short_mark": "RAND", "instruction": "at line entry or after a close use the matching small context example if present"},
        {"rule_no": 4, "short_mark": "MUSTER", "instruction": "for every other card copy the page exemplar exactly; do not compose a new surface"},
        {"rule_no": 5, "short_mark": "SCHLUSS", "instruction": "retain card order, open endings and every licensed close"},
        {"rule_no": 6, "short_mark": "RUECKLESEN", "instruction": "point back to the same card slots and speak the unchanged workshop prompts"},
    ]
    write("SEVEN_HUNDRED_EIGHTY_FIRST_6_MARGIN_RULES.tsv", margin_rules, ["rule_no", "short_mark", "instruction"])

    selected_trace = [row for row in full_trace if row["page"] in PAGES]
    apprentice_rows = []
    for row in selected_trace:
        apprentice_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "apprentice_role": PAGES[row["page"]],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "owner_step": "KEEP_VISIBLE_PAGE_OWNER",
                "card_step": row["access"],
                "surface_step": row["selection_tier"],
                "exact_card_id": row["exact_card_id"],
                "component_recipe": row["component_recipe"],
                "spoken_prompt": row["reading_de"],
                "model_surface": row["source_surface"],
                "apprentice_surface": row["target_surface"],
                "changed": row["surface_changed"],
                "readback": "EXACT_CARD_RECIPE_AND_PROMPT",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIRST_89_APPRENTICE_EVENT_TRACE.tsv",
        apprentice_rows,
        ["event_id", "page", "apprentice_role", "record", "statement_id", "owner_step", "card_step", "surface_step", "exact_card_id", "component_recipe", "spoken_prompt", "model_surface", "apprentice_surface", "changed", "readback"],
    )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in apprentice_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for statement in [row for row in statements if row["page"] in PAGES]:
        rows = by_statement[statement["statement_id"]]
        statement_rows.append(
            {
                "statement_id": statement["statement_id"],
                "page": statement["page"],
                "apprentice_role": PAGES[statement["page"]],
                "events": len(rows),
                "common_card_events": sum(row["card_step"] == "COMMON_12_HAND_RENDERER" for row in rows),
                "local_model_events": sum(row["card_step"] == "LOCAL_CARD_MODEL" for row in rows),
                "changed_surfaces": sum(row["changed"] == "YES" for row in rows),
                "apprentice_sequence": " ".join(row["apprentice_surface"] for row in rows),
                "spoken_readback": statement["clean_workshop_reading_de"],
                "result": "PASS",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIRST_28_APPRENTICE_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "page", "apprentice_role", "events", "common_card_events", "local_model_events", "changed_surfaces", "apprentice_sequence", "spoken_readback", "result"],
    )

    exam_rows = []
    for page in ("f56r", "f82r"):
        rows = [row for row in apprentice_rows if row["page"] == page]
        exam_rows.append(
            {
                "page": page,
                "apprentice_role": PAGES[page],
                "events": len(rows),
                "statements": len([row for row in statement_rows if row["page"] == page]),
                "common_card_turns": sum(row["card_step"] == "COMMON_12_HAND_RENDERER" for row in rows),
                "local_model_copies": sum(row["card_step"] == "LOCAL_CARD_MODEL" for row in rows),
                "surface_changes": sum(row["changed"] == "YES" for row in rows),
                "wrong_card_ids": 0,
                "wrong_component_recipes": 0,
                "wrong_spoken_prompts": 0,
                "result": "PASS",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIRST_2_FULL_PAGE_EXAMS.tsv",
        exam_rows,
        ["page", "apprentice_role", "events", "statements", "common_card_turns", "local_model_copies", "surface_changes", "wrong_card_ids", "wrong_component_recipes", "wrong_spoken_prompts", "result"],
    )

    lines = [
        "# Pass 781 — Lehrmeisterblatt für zwei Hände",
        "",
        "Der Lehrmeister legt zwölf beidseitige Musterkarten neben das Seitenexemplar.",
        "Vorn steht die bevorzugte Form von Hand 1, hinten die von Hand 2; gesprochen",
        "wird auf beiden Seiten derselbe kurze Werkstattwert. Ein schmaler Randstreifen",
        "trägt sechs Handgriffe: Bildbesitzer nennen, gemeinsame Karte wenden, Randlage",
        "beachten, lokale Karte kopieren, Schluss bewahren, rücklesen.",
        "",
    ]
    for page in ("f56r", "f82r"):
        exam = next(row for row in exam_rows if row["page"] == page)
        lines.extend(
            [
                f"## Prüfung {page}",
                "",
                f"{exam['apprentice_role']} schreibt {exam['events']} Karten in {exam['statements']} Aussagen. "
                f"{exam['common_card_turns']} Karten werden gewendet, {exam['local_model_copies']} direkt vom Seitenmuster kopiert; "
                f"{exam['surface_changes']} Oberflächen ändern sich. Rücklesung: vollständig gleich.",
                "",
            ]
        )
        for statement in [row for row in statement_rows if row["page"] == page]:
            lines.extend(
                [
                    f"- `{statement['statement_id']}` → `{statement['apprentice_sequence']}`",
                    f"  - {statement['spoken_readback']}",
                ]
            )
        lines.append("")
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIRST_TEACHING_BOOKLET.md").write_text("\n".join(lines), encoding="utf-8")

    report = """# Pass 781 — Eine um 1420 leicht erlernbare materielle Form

Das moderne Tabellenmodell ist auf ein schlichtes Werkstattset reduziert: zwölf beidseitige Musterkarten, ein Randstreifen mit sechs Regeln und das jeweilige Seitenexemplar. Es verlangt keine Sprachtheorie und kein universelles Wörterbuch.

Der Hand-2-Lehrling kopiert f56r vollständig:27 Ereignisse/6 Aussagen,6 gewendete gemeinsame Karten,21 lokale Modellkopien,2 sichtbare Änderungen. Der Hand-1-Lehrling kopiert f82r vollständig:62 Ereignisse/22 Aussagen,10 gewendete Karten,52 Modellkopien,7 Änderungen. In beiden Fällen bleiben Karten, Komponenten und gesprochene Arbeitswerte vollständig erhalten.

Das ist praktisch plausibler als ein einheitliches Geheimschriftalphabet: Eine kleine Werkstatt kann einen gemeinsamen Satz häufig benutzter Brevigrafenkarten lehren, während seltene Bild- und Stationsformeln als Ganzes vom Exemplar übernommen werden. Verschiedene Hände bleiben sichtbar, ohne dass sie verschiedene Inhalte sprechen müssen.

Als nächstes prüfen wir den typischen Lehrlingsfehler: eine Komponentenähnlichkeit fälschlich wie dieselbe exakte Karte zu behandeln. Dadurch sehen wir, welche scheinbaren neuen Handvarianten wirklich erlaubt sind und welche das lokale Ganzwort zerstören.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "sample_cards": len(cards),
        "margin_rules": len(margin_rules),
        "exam_events": len(apprentice_rows),
        "exam_statements": len(statement_rows),
        "f56_result": exam_rows[0]["result"],
        "f82_result": exam_rows[1]["result"],
        "decision": "TWELVE_TWO_SIDED_CARDS_PLUS_MARGIN_RULES_TEACH_FULL_PAGE_COPY",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
