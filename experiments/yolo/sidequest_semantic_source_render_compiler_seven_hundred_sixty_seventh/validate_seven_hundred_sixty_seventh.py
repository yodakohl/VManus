#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth/SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source = read(HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_380_LOGICAL_SOURCE_CARDS.tsv")
    rendered = read(HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_381_RENDERED_VISIBLE_CARDS.tsv")
    statements = read(HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_116_TWO_STAGE_STATEMENTS.tsv")
    guards = read(HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_6_RENDER_GUARDS.tsv")
    pairs = read(HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_3_DUPLICATE_PAIR_RENDERING.tsv")
    target = read(TARGET)
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    rendered_projection = [(r["visible_event"], r["exact_card_id"], r["surface"], r["component_recipe"]) for r in rendered]
    target_projection = [(r["event_id"], r["card_no"], r["surface"], r["component_recipe"]) for r in target]
    pair = {row["pair"]: row for row in pairs}
    checks = {
        "counts_380_381_116_6_3": (len(source), len(rendered), len(statements), len(guards), len(pairs)) == (380, 381, 116, 6, 3),
        "render_exact_target": rendered_projection == target_projection,
        "source_ordinals_complete": [int(row["source_ordinal"]) for row in source] == list(range(1, 381)),
        "visible_events_complete": [row["visible_event"] for row in rendered] == [f"E{i:03d}" for i in range(1, 382)],
        "one_edge_copy": sum(row["render_operation"] == "ANTICIPATORY_EDGE_COPY__NO_EXTRA_SOURCE_TOKEN" for row in rendered) == 1,
        "e180_e181_share_source": rendered[179]["source_id"] == rendered[180]["source_id"] and rendered[179]["visible_event"] == "E180" and rendered[180]["visible_event"] == "E181",
        "other_duplicates_separate_sources": pair["E020->E021"]["source_ids"].split(" | ")[0] != pair["E020->E021"]["source_ids"].split(" | ")[1] and pair["E033->E034"]["source_ids"].split(" | ")[0] != pair["E033->E034"]["source_ids"].split(" | ")[1],
        "all_forward_statements_exact": all(row["rendered_recipe_sequence"] == row["pass762_forward_sequence"] for row in statements),
        "open_27_preserved": sum(row["open_statement"] == "YES" for row in statements) == 27,
        "no_copy_on_owner_resets": all(next(row for row in rendered if row["visible_event"] == event)["render_operation"] == "NORMAL_ONCE" for event in ("E203", "E264", "E291", "E356")),
        "summary_pass": summary["status"] == "PASS" and summary["logical_source_cards"] == 380 and summary["visible_rendered_cards"] == 381,
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (source, rendered, statements, guards, pairs) for row in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
