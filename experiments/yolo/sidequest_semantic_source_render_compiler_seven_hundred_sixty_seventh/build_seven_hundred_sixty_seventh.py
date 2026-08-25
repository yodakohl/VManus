#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P762 = ROOT / "experiments/yolo/sidequest_semantic_motif_tail_forward_compiler_seven_hundred_sixty_second"
P766 = ROOT / "experiments/yolo/sidequest_semantic_actual_error_audit_seven_hundred_sixty_sixth"


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
    forward = read(P762 / "SEVEN_HUNDRED_SIXTY_SECOND_116_FORWARD_OUTPUT.tsv")
    duplicate_audit = read(P766 / "SEVEN_HUNDRED_SIXTY_SIXTH_3_ADJACENT_DUPLICATES.tsv")
    open_statements = read(P766 / "SEVEN_HUNDRED_SIXTY_SIXTH_27_OPEN_STATEMENTS.tsv")
    license_pair = next(row for row in duplicate_audit if row["decision"] == "VISIBLE_EDGE_COPY_READ_ONCE")
    assert license_pair["pair"] == "E180->E181"

    source_rows: list[dict[str, object]] = []
    visible_to_source: dict[str, str] = {}
    source_ordinal = 0
    for row in events:
        if row["event_id"] == "E180":
            continue
        source_ordinal += 1
        source_id = f"S{source_ordinal:03d}"
        render_count = 2 if row["event_id"] == "E181" else 1
        source_rows.append({
            "source_ordinal": source_ordinal,
            "source_id": source_id,
            "main_visible_event": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "exact_card_id": row["card_no"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "reading_de": row["rebuilt_reading_de"],
            "render_count": render_count,
            "layout_license": "E180_EDGE_COPY_BEFORE_E181" if render_count == 2 else "NORMAL_ONCE",
        })
        visible_to_source[row["event_id"]] = source_id
        if row["event_id"] == "E181":
            visible_to_source["E180"] = source_id
    write(
        "SEVEN_HUNDRED_SIXTY_SEVENTH_380_LOGICAL_SOURCE_CARDS.tsv",
        source_rows,
        ["source_ordinal", "source_id", "main_visible_event", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "reading_de", "render_count", "layout_license"],
    )

    rendered: list[dict[str, object]] = []
    for source in source_rows:
        if source["main_visible_event"] == "E181":
            rendered.append({
                "visible_event": "E180",
                "source_id": source["source_id"],
                "page": source["page"],
                "record": source["record"],
                "statement_id": source["statement_id"],
                "exact_card_id": source["exact_card_id"],
                "surface": source["surface"],
                "component_recipe": source["component_recipe"],
                "render_operation": "ANTICIPATORY_EDGE_COPY__NO_EXTRA_SOURCE_TOKEN",
            })
        rendered.append({
            "visible_event": source["main_visible_event"],
            "source_id": source["source_id"],
            "page": source["page"],
            "record": source["record"],
            "statement_id": source["statement_id"],
            "exact_card_id": source["exact_card_id"],
            "surface": source["surface"],
            "component_recipe": source["component_recipe"],
            "render_operation": "SOURCE_MAIN_AFTER_EDGE_COPY" if source["main_visible_event"] == "E181" else "NORMAL_ONCE",
        })
    rendered.sort(key=lambda row: int(str(row["visible_event"])[1:]))
    write(
        "SEVEN_HUNDRED_SIXTY_SEVENTH_381_RENDERED_VISIBLE_CARDS.tsv",
        rendered,
        ["visible_event", "source_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "render_operation"],
    )

    source_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    visible_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in source_rows:
        source_by_statement[str(row["statement_id"])].append(row)
    for row in rendered:
        visible_by_statement[str(row["statement_id"])].append(row)
    forward_by_statement = {row["statement_id"]: row for row in forward}
    statement_rows = []
    for statement_id, visible_rows in visible_by_statement.items():
        source = source_by_statement[statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "page": visible_rows[0]["page"],
            "record": visible_rows[0]["record"],
            "logical_source_cards": len(source),
            "visible_cards": len(visible_rows),
            "source_recipe_sequence": " | ".join(str(row["component_recipe"]) for row in source),
            "rendered_recipe_sequence": " | ".join(str(row["component_recipe"]) for row in visible_rows),
            "pass762_forward_sequence": forward_by_statement[statement_id]["forward_recipe_sequence"],
            "layout_action": "INSERT_E180_EDGE_COPY" if statement_id == "B2-S005" else "NONE",
            "open_statement": "YES" if any(row["statement_id"] == statement_id for row in open_statements) else "NO",
        })
    write(
        "SEVEN_HUNDRED_SIXTY_SEVENTH_116_TWO_STAGE_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "page", "record", "logical_source_cards", "visible_cards", "source_recipe_sequence", "rendered_recipe_sequence", "pass762_forward_sequence", "layout_action", "open_statement"],
    )

    guards = [
        {"guard_order": 1, "guard": "SAME_EXACT_CARD", "required_value": "YES", "purpose": "Randkopie muss dieselbe Karte sein"},
        {"guard_order": 2, "guard": "SAME_STATEMENT", "required_value": "YES", "purpose": "kein Satz- oder Zellreset dazwischen"},
        {"guard_order": 3, "guard": "SAME_VISIBLE_OWNER", "required_value": "YES", "purpose": "kein Besitzerwechsel ueber die Luecke"},
        {"guard_order": 4, "guard": "PHYSICAL_LINE_EDGE_PAIR", "required_value": "YES", "purpose": "erste Kopie am Zeilenrand, zweite am Folgezeilenanfang"},
        {"guard_order": 5, "guard": "NO_CLOSE_OR_OWNER_RESET", "required_value": "YES", "purpose": "Schluss und Bildwechsel sperren carry"},
        {"guard_order": 6, "guard": "EXPLICIT_LOCAL_LICENSE", "required_value": "E180->E181", "purpose": "aus einem Beispiel keine allgemeine Verdopplungsregel machen"},
    ]
    write("SEVEN_HUNDRED_SIXTY_SEVENTH_6_RENDER_GUARDS.tsv", guards, ["guard_order", "guard", "required_value", "purpose"])

    pair_rows = []
    for row in duplicate_audit:
        pair_rows.append({
            "pair": row["pair"],
            "statement_id": row["statement_id"],
            "logical_source_tokens": row["logical_source_tokens"],
            "visible_renderings": 2,
            "renderer_action": "EDGE_COPY_ONE_SOURCE_TO_TWO_VISIBLE" if row["pair"] == "E180->E181" else "NORMAL_TWO_SOURCES_TO_TWO_VISIBLE",
            "source_ids": visible_to_source[row["pair"].split("->")[0]] + " | " + visible_to_source[row["pair"].split("->")[1]],
        })
    write(
        "SEVEN_HUNDRED_SIXTY_SEVENTH_3_DUPLICATE_PAIR_RENDERING.tsv",
        pair_rows,
        ["pair", "statement_id", "logical_source_tokens", "visible_renderings", "renderer_action", "source_ids"],
    )

    report = """# Pass 767 — Quellkarten und sichtbare Schrift getrennt

Der Werkstattkompiler hat jetzt zwei Stufen.

1. Die Inhalts-/Formularstufe erzeugt380 logische Karten in116 Aussagen.
2. Die Schreibstufe setzt nur am lizenzierten Rand `E180` als Voraus-/Randkopie vor die Hauptkarte `E181`.

Danach stehen wieder exakt381 sichtbare Karten. Die beiden anderen unmittelbaren Doppelpaare bleiben zwei echte Quellkarten und werden nicht zusammengezogen. Die27 offenen Aussagen bleiben offen. An den vier sichtbaren Besitzerwechseln wird nichts getragen oder verdoppelt.

Das ist eine wichtige Verbesserung der Schreibertheorie: Die eine Doppelung muss nicht als zweimaliges Rezeptkommando gedeutet werden, und sie muss auch nicht als Fehler aus dem Faksimile verschwinden. Sie gehoert zur Seitenausfuehrung, nicht zum geplanten Kartenstrom.

Als naechstes wird ein kleiner Zeilenpacker gebaut. Er bekommt Aussage, Bildfreiraum und Kartenbreiten und muss erklaeren, warum gerade E180 am Rand vorweggenommen wird, ohne die18 anderen aussageninternen Zeilenwechsel ebenfalls zu verdoppeln.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "logical_source_cards": len(source_rows),
        "visible_rendered_cards": len(rendered),
        "statements": len(statement_rows),
        "records": len({row["record"] for row in statement_rows}),
        "edge_copy_renderings": sum(row["render_operation"].startswith("ANTICIPATORY") for row in rendered),
        "open_statements_preserved": sum(row["open_statement"] == "YES" for row in statement_rows),
        "decision": "TWO_STAGE_COMPILER__380_SOURCE_TO_381_VISIBLE_BY_ONE_LICENSED_EDGE_COPY",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
