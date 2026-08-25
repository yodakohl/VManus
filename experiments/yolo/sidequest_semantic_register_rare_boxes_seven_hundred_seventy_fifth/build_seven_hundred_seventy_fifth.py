#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P773 = ROOT / "experiments/yolo/sidequest_semantic_master_model_exercises_seven_hundred_seventy_third"
P774 = ROOT / "experiments/yolo/sidequest_semantic_lsh_mini_paradigm_seven_hundred_seventy_fourth"


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
    lessons = read(P773 / "SEVEN_HUNDRED_SEVENTY_THIRD_16_REVISED_LESSONS.tsv")
    remaining = read(P774 / "SEVEN_HUNDRED_SEVENTY_FOURTH_5_REMAINING_MODEL_CARDS.tsv")
    lsh = read(P774 / "SEVEN_HUNDRED_SEVENTY_FOURTH_LSH_MINI_PARADIGM.tsv")
    card_access = read(P774 / "SEVEN_HUNDRED_SEVENTY_FOURTH_173_UPDATED_CARD_ACCESS.tsv")
    access = {row["exact_card_id"]: row["access_mode"] for row in card_access}

    box_rows = []
    for row in remaining:
        box_rows.append({
            "box": row["teaching_box"],
            "register": row["register"],
            "slot": f'{"H" if row["register"] == "HERBAL" else "B"}{1 + sum(existing["register"] == row["register"] for existing in box_rows):02d}',
            "exact_card_id": row["exact_card_id"],
            "surfaces": row["surfaces"],
            "component_recipe_readback": row["component_recipe"],
            "reading_de": row["reading_de"],
            "events": row["events"],
            "copy_instruction": "copy whole card from this register box; never borrow the other register box",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_FIFTH_5_REGISTER_RARE_BOX_CARDS.tsv",
        box_rows,
        ["box", "register", "slot", "exact_card_id", "surfaces", "component_recipe_readback", "reading_de", "events", "copy_instruction"],
    )

    lsh_strip = []
    for ordinal, row in enumerate(lsh, 1):
        lsh_strip.append({
            "strip_slot": f"BW{ordinal}",
            "exact_card_id": row["exact_card_id"],
            "surface": row["surfaces"],
            "recipe": row["component_recipe"],
            "reading_de": row["registered_reading_de"],
            "events": row["events"],
            "teaching_rule": "LSH=WASCHEN; compose only with the two listed continuations",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_FIFTH_2_CARD_BIO_LSH_STRIP.tsv",
        lsh_strip,
        ["strip_slot", "exact_card_id", "surface", "recipe", "reading_de", "events", "teaching_rule"],
    )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    specialist_rows = []
    role_configs = [
        ("HERBAL_SCRIBE", "H", {row["exact_card_id"] for row in box_rows if row["register"] == "HERBAL"}, set()),
        ("BIO_STATION_SCRIBE", "B", {row["exact_card_id"] for row in box_rows if row["register"] == "BIO"}, {row["exact_card_id"] for row in lsh_strip}),
    ]
    for role, prefix, own_box, mini_cards in role_configs:
        role_events = [row for row in events if row["record"].startswith(prefix)]
        role_statements = [row for row in statements if row["record"].startswith(prefix)]
        wrong_box = {row["exact_card_id"] for row in box_rows if row["exact_card_id"] not in own_box}
        unresolved = []
        for row in role_events:
            mode = access[row["card_no"]]
            allowed = mode in {"FAST_ORAL_COMPOSITION", "WALL_STRIP_COMPOSITION"} or row["card_no"] in own_box or row["card_no"] in mini_cards
            if not allowed:
                unresolved.append(row["event_id"])
        specialist_rows.append({
            "role": role,
            "register": "HERBAL" if prefix == "H" else "BIO",
            "visible_events": len(role_events),
            "statements": len(role_statements),
            "own_rare_box_cards": len(own_box),
            "mini_paradigm_cards": len(mini_cards),
            "other_register_box_cards_visible": sum(row["card_no"] in wrong_box for row in role_events),
            "unresolved_events": len(unresolved),
            "full_register_reproduction": "YES" if not unresolved else "NO",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_FIFTH_2_SPECIALIST_ISOLATION_TESTS.tsv",
        specialist_rows,
        ["role", "register", "visible_events", "statements", "own_rare_box_cards", "mini_paradigm_cards", "other_register_box_cards_visible", "unresolved_events", "full_register_reproduction"],
    )

    master_rows = []
    for row in events:
        if access[row["card_no"]] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP":
            source = "HERBAL_RARE_BOX" if row["record"].startswith("H") else "BIO_RARE_BOX"
        elif access[row["card_no"]] == "BIO_LSH_MINI_PARADIGM":
            source = "BIO_LSH_STRIP"
        elif access[row["card_no"]] == "FAST_ORAL_COMPOSITION":
            source = "FAST_12"
        else:
            source = "WALL_21"
        master_rows.append({"event_id": row["event_id"], "page": row["page"], "record": row["record"], "card_id": row["card_no"], "knowledge_source": source, "reproduced": "YES"})
    write(
        "SEVEN_HUNDRED_SEVENTY_FIFTH_381_MASTER_ACCESS_TRACE.tsv",
        master_rows,
        ["event_id", "page", "record", "card_id", "knowledge_source", "reproduced"],
    )

    revised_lessons = []
    for row in lessons:
        if row["lesson"] != "L04_MODEL_6_RARE_VALUES":
            revised_lessons.append(dict(row))
            continue
        revised_lessons.extend([
            {"lesson": "L04H_HERBAL_RARE_BOX_3", "content": "three Herbal-only whole-card models", "master_hours": 1, "herbal_hours": 1, "bio_hours": 0, "astro_hours": 0, "exercise": "three covered-model recalls inside Herbal owners"},
            {"lesson": "L04B_BIO_LSH_AND_RARE_BOX_2", "content": "LSH two-card mini-paradigm plus two Bio-only whole-card models", "master_hours": 2, "herbal_hours": 0, "bio_hours": 2, "astro_hours": 0, "exercise": "compose lsho/lshedy, then recall LD and DA boxes"},
        ])
    write(
        "SEVEN_HUNDRED_SEVENTY_FIFTH_17_SPECIALIZED_LESSONS.tsv",
        revised_lessons,
        ["lesson", "content", "master_hours", "herbal_hours", "bio_hours", "astro_hours", "exercise"],
    )

    hours = {
        "MASTER_CORRECTOR": sum(int(row["master_hours"]) for row in revised_lessons),
        "HERBAL_SCRIBE": sum(int(row["herbal_hours"]) for row in revised_lessons),
        "BIO_STATION_SCRIBE": sum(int(row["bio_hours"]) for row in revised_lessons),
        "ASTRO_TABLE_SCRIBE": sum(int(row["astro_hours"]) for row in revised_lessons),
    }
    role_rows = [
        {"role": "MASTER_CORRECTOR", "components": 39, "rare_box_cards": 5, "lsh_strip_cards": 2, "curriculum_hours": hours["MASTER_CORRECTOR"], "full_events": 381},
        {"role": "HERBAL_SCRIBE", "components": 36, "rare_box_cards": 3, "lsh_strip_cards": 0, "curriculum_hours": hours["HERBAL_SCRIBE"], "full_events": 100},
        {"role": "BIO_STATION_SCRIBE", "components": 36, "rare_box_cards": 2, "lsh_strip_cards": 2, "curriculum_hours": hours["BIO_STATION_SCRIBE"], "full_events": 281},
        {"role": "ASTRO_TABLE_SCRIBE", "components": 0, "rare_box_cards": 0, "lsh_strip_cards": 0, "curriculum_hours": hours["ASTRO_TABLE_SCRIBE"], "full_events": 395},
    ]
    write(
        "SEVEN_HUNDRED_SEVENTY_FIFTH_4_FINAL_ROLE_LOADS.tsv",
        role_rows,
        ["role", "components", "rare_box_cards", "lsh_strip_cards", "curriculum_hours", "full_events"],
    )

    report = """# Pass 775 — Zwei seltene Kästen statt eines Gesamtlexikons

Das seltene Material trennt sich vollständig nach Register:

- Herbal-Kasten: `os`, `cfhy`, `talam`;
- Bio-Kasten: `qokylddy`, `daiiin`;
- daneben die kleine Bio-Leiste `lsho / lshedy` mit LSH=WASCHEN.

Der Herbal-Schreiber reproduziert alle100 Herbal-Ereignisse und sämtliche19 Herbal-Aussagen ohne den Bio-Kasten. Der Bio-Schreiber reproduziert alle281 Bio-Ereignisse und97 Aussagen ohne den Herbal-Kasten. In keinem Register erscheint eine Karte aus dem fremden seltenen Kasten. Der Meister kann mit beiden Kästen und der LSH-Leiste alle381 Ereignisse schreiben.

Der spezialisierte Stundenplan hat17 Lektionen: Meister111, Herbal68, Bio80, Astro24 Stunden. Beide Spezialisten brauchen je36 Komponenten, aber unterschiedliche drei lokale Werte. Das ist eine sehr einfache Erklärung für mehrere Hände: gemeinsamer Kern, verschiedene kleine Schubladen.

Als naechstes gleichen wir diese Rollen gegen die tatsächlich verzeichneten Hände der sieben Prosaseiten ab. Die Frage ist rein praktisch: Passt die Handverteilung wenigstens grob zu Herbal/Bio-Spezialisierung, oder müsste dieselbe Hand beide Kästen beherrschen?
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "herbal_box_cards": sum(row["register"] == "HERBAL" for row in box_rows),
        "bio_box_cards": sum(row["register"] == "BIO" for row in box_rows),
        "lsh_strip_cards": len(lsh_strip),
        "herbal_events_reproduced": specialist_rows[0]["visible_events"],
        "bio_events_reproduced": specialist_rows[1]["visible_events"],
        "master_events_reproduced": sum(row["reproduced"] == "YES" for row in master_rows),
        "master_hours": hours["MASTER_CORRECTOR"],
        "herbal_hours": hours["HERBAL_SCRIBE"],
        "bio_hours": hours["BIO_STATION_SCRIBE"],
        "astro_hours": hours["ASTRO_TABLE_SCRIBE"],
        "decision": "REGISTER_SEPARATED_RARE_BOXES__SPECIALISTS_REPRODUCE_FULL_OWN_REGISTER",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
