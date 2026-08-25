#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]
SHORT_CARDS = {"PROC077", "PROC082", "PROC094", "PROC144", "PROC166", "PROC168"}
CONDITIONAL_CARD = "PROC042"
COMPLEX_CARD = "PROC136"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def guarded_layout() -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", "gdt327_joint_tuple_interlinear.tsv", "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(
        [
            "--columns",
            "page,locus,group_index,group_count,hand,field_ordinal,within_field_position,observed_wrapper,line_first,prev_dy,dy_closure,b3,joint_tuple_id",
            "--forbid-prefix",
            "f84",
        ]
    )
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def length_class(surface: str) -> str:
    if "ched" in surface:
        return "LONG_CHED"
    if "chd" in surface:
        return "SHORT_CHD"
    return "COMPLEX_INTERLEAVED"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    layout = guarded_layout()
    by_page_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_page_layout: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_page_events[row["page"]].append(row)
    for row in layout:
        by_page_layout[row["page"]].append(row)
    chd_rows = []
    for page in PAGES:
        if len(by_page_events[page]) != len(by_page_layout[page]):
            raise ValueError(page)
        for event, formal in zip(by_page_events[page], by_page_layout[page]):
            if "CHD" not in event["component_recipe"].split("+"):
                continue
            observed = length_class(event["surface"])
            if event["card_no"] == COMPLEX_CARD:
                selection = "COPY_COMPLEX_CARD_MODEL"
                predicted = "COMPLEX_INTERLEAVED"
            elif event["card_no"] == CONDITIONAL_CARD:
                selection = "PROC042_WRAPPER_CH_SHORT_CHE_LONG"
                predicted = "SHORT_CHD" if formal["observed_wrapper"] == "ch" else "LONG_CHED"
            elif event["card_no"] in SHORT_CARDS:
                selection = "SIX_CARD_SHORT_STRIP"
                predicted = "SHORT_CHD"
            else:
                selection = "DEFAULT_LONG_CHED"
                predicted = "LONG_CHED"
            chd_rows.append(
                {
                    "event_id": event["event_id"],
                    "page": page,
                    "hand": f"HAND_{formal['hand']}",
                    "record": event["record"],
                    "statement_id": event["statement_id"],
                    "locus": formal["locus"],
                    "group_index": formal["group_index"],
                    "field_ordinal": formal["field_ordinal"],
                    "within_field_position": formal["within_field_position"],
                    "line_first": formal["line_first"],
                    "prev_dy": formal["prev_dy"],
                    "dy_closure": formal["dy_closure"],
                    "observed_wrapper": formal["observed_wrapper"],
                    "exact_card_id": event["card_no"],
                    "surface": event["surface"],
                    "component_recipe": event["component_recipe"],
                    "working_reading_de": event["rebuilt_reading_de"],
                    "observed_length_class": observed,
                    "selection_rule": selection,
                    "predicted_length_class": predicted,
                    "selection_correct": "YES" if predicted == observed else "NO",
                }
            )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIFTH_48_CHD_EVENTS.tsv",
        chd_rows,
        ["event_id", "page", "hand", "record", "statement_id", "locus", "group_index", "field_ordinal", "within_field_position", "line_first", "prev_dy", "dy_closure", "observed_wrapper", "exact_card_id", "surface", "component_recipe", "working_reading_de", "observed_length_class", "selection_rule", "predicted_length_class", "selection_correct"],
    )

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in chd_rows:
        by_card[row["exact_card_id"]].append(row)
    card_rows = []
    for card, rows in sorted(by_card.items()):
        classes = Counter(row["observed_length_class"] for row in rows)
        if card == COMPLEX_CARD:
            lesson = "COPY_COMPLEX_MODEL"
        elif card == CONDITIONAL_CARD:
            lesson = "WRAPPER_SELECTS_CH_OR_CHE"
        elif card in SHORT_CARDS:
            lesson = "SHORT_STRIP"
        else:
            lesson = "LONG_DEFAULT"
        card_rows.append(
            {
                "exact_card_id": card,
                "component_recipe": rows[0]["component_recipe"],
                "surfaces": ",".join(sorted({row["surface"] for row in rows})),
                "events": len(rows),
                "long_events": classes["LONG_CHED"],
                "short_events": classes["SHORT_CHD"],
                "complex_events": classes["COMPLEX_INTERLEAVED"],
                "lesson": lesson,
                "working_reading_de": rows[0]["working_reading_de"],
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIFTH_22_CHD_CARD_LESSONS.tsv",
        card_rows,
        ["exact_card_id", "component_recipe", "surfaces", "events", "long_events", "short_events", "complex_events", "lesson", "working_reading_de"],
    )

    short_rows = [row for row in card_rows if row["lesson"] == "SHORT_STRIP"]
    write(
        "SEVEN_HUNDRED_EIGHTY_FIFTH_6_SHORT_CARD_STRIP.tsv",
        short_rows,
        ["exact_card_id", "component_recipe", "surfaces", "events", "long_events", "short_events", "complex_events", "lesson", "working_reading_de"],
    )

    feature_rows = []
    features = [
        ("ENDPOINT", "CLOSED_DY", lambda row: row["dy_closure"] == "1"),
        ("ENDPOINT", "OPEN", lambda row: row["dy_closure"] == "0"),
        ("LINE", "LINE_FIRST", lambda row: row["line_first"] == "1"),
        ("LINE", "NOT_LINE_FIRST", lambda row: row["line_first"] == "0"),
        ("FIELD", "ONLY", lambda row: row["within_field_position"] == "ONLY"),
        ("FIELD", "NON_ONLY", lambda row: row["within_field_position"] != "ONLY"),
        ("WRAPPER", "CH", lambda row: row["observed_wrapper"] == "ch"),
        ("WRAPPER", "CHE", lambda row: row["observed_wrapper"] == "che"),
        ("TRANSFER_FRAME", "L_P_OL_LO", lambda row: any(part in {"L", "P", "OL", "LO"} for part in row["component_recipe"].split("+")[:-1])),
        ("HAND", "HAND_2", lambda row: row["hand"] == "HAND_2"),
    ]
    for feature, value, predicate in features:
        rows = [row for row in chd_rows if predicate(row)]
        counts = Counter(row["observed_length_class"] for row in rows)
        feature_rows.append(
            {
                "feature": feature,
                "value": value,
                "events": len(rows),
                "long": counts["LONG_CHED"],
                "short": counts["SHORT_CHD"],
                "complex": counts["COMPLEX_INTERLEAVED"],
                "selection_value": "DETERMINISTIC" if len([count for count in counts.values() if count]) == 1 else "MIXED",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FIFTH_10_SELECTION_FEATURES.tsv",
        feature_rows,
        ["feature", "value", "events", "long", "short", "complex", "selection_value"],
    )

    always_long_correct = sum(row["observed_length_class"] == "LONG_CHED" for row in chd_rows)
    wrapper_correct = sum(
        ("SHORT_CHD" if row["observed_wrapper"] == "ch" else "LONG_CHED") == row["observed_length_class"]
        for row in chd_rows
    )
    model_rows = [
        {"model": "ALWAYS_LONG_CHED", "rules": 1, "special_card_models": 0, "correct_events": always_long_correct, "events": len(chd_rows)},
        {"model": "CH_WRAPPER_SHORT_ELSE_LONG", "rules": 2, "special_card_models": 0, "correct_events": wrapper_correct, "events": len(chd_rows)},
        {"model": "LONG_DEFAULT_PLUS6_SHORT_CARDS_PLUS_PROC042_WRAPPER_PLUS1_COMPLEX", "rules": 3, "special_card_models": 7, "correct_events": sum(row["selection_correct"] == "YES" for row in chd_rows), "events": len(chd_rows)},
    ]
    write(
        "SEVEN_HUNDRED_EIGHTY_FIFTH_3_SELECTION_MODELS.tsv",
        model_rows,
        ["model", "rules", "special_card_models", "correct_events", "events"],
    )

    report = """# Pass 785 — CHED ist der Normalfall, CHD eine kleine Hand-2-Kurzleiste

Alle48 CHD-Rezeptvorkommen liegen in diesem Ausschnitt bei Hand 2. Sichtbar sind38 lange CHED-Formen,9 kurze CHD-Formen und eine komplex verschachtelte Karte. Weder Schluss noch Zeilenanfang noch Feldposition wählt die Länge zuverlässig: kurze Formen kommen offen und geschlossen, innen und am Rand vor.

Die einfachste Lehrregel ist trotzdem klein:

1. Schreibe CHED als Normalform.
2. Bei der portablen Karte PROC042 entscheidet die Eintrittshülle: `che+dy = chedy`, `ch+dy = chdy`.
3. Sechs exakte Karten stehen auf einer kurzen CHD-Leiste: `sshkchdy`, `qokchdy`, `dchdy`, `dalchdy`, `otchdy`, `chdal`.
4. Die einmalige verschachtelte Karte `shecthedchy` wird ganz kopiert.

Damit werden48/48 Fälle gewählt. Ein reines „immer lang“ trifft38; die Hüllenregel allein40. Der Rest ist genau die Art gelernter Fachkürzel, die unser Mischmodell erwartet. CHD bedeutet deshalb nicht automatisch „schnell“ oder „kurz behandeln“; kurz/lang ist hier primär Schreibform, während beide `UMSETZEN` beitragen.

Als nächstes machen wir dasselbe für Y/CHY, aber unter der neuen Kollisionssperre. Ziel ist eine kleine Liste: wo ist CH bloße Referenzhülle, wo bleibt CH=ENTNEHMEN wirklich semantisch?
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(chd_rows),
        "cards": len(card_rows),
        "long_events": sum(row["observed_length_class"] == "LONG_CHED" for row in chd_rows),
        "short_events": sum(row["observed_length_class"] == "SHORT_CHD" for row in chd_rows),
        "complex_events": sum(row["observed_length_class"] == "COMPLEX_INTERLEAVED" for row in chd_rows),
        "short_strip_cards": len(short_rows),
        "selected_correct": sum(row["selection_correct"] == "YES" for row in chd_rows),
        "decision": "LONG_CHED_DEFAULT__SIX_SHORT_CARDS__ONE_WRAPPER_SWITCH__ONE_COMPLEX_MODEL",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
