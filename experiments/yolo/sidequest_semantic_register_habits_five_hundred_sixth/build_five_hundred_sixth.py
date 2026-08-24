#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P503 = ROOT / "experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third"
P505 = ROOT / "experiments/yolo/sidequest_semantic_statement_automaton_five_hundred_fifth"
PRIMITIVES = [
    "ACTIVATE_CHARGE", "SOURCE_DRAW", "METER_CHECK", "TARGET_HANDOFF",
    "MOVE_PASS", "HOLD_STATE", "CONTINUE_USE", "CLOSE",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def domain(row: dict[str, str]) -> str:
    return "HERBAL" if row["record"].startswith("H") else "BIOLOGICAL"


def main() -> None:
    statements = read(P503 / "FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv")
    by_domain = {name: [row for row in statements if domain(row) == name] for name in ("HERBAL", "BIOLOGICAL")}
    token_counts: dict[str, Counter[str]] = {}
    edge_counts: dict[str, Counter[tuple[str, str]]] = {}
    starts: dict[str, Counter[str]] = {}
    ends: dict[str, Counter[str]] = {}
    profiles = []
    for name, rows in by_domain.items():
        token_counts[name] = Counter()
        edge_counts[name] = Counter()
        starts[name] = Counter()
        ends[name] = Counter()
        lengths = []
        for row in rows:
            seq = row["primitive_signature"].split(">")
            token_counts[name].update(seq); edge_counts[name].update(zip(seq, seq[1:]))
            starts[name][seq[0]] += 1; ends[name][seq[-1]] += 1; lengths.append(len(seq))
        profiles.append({
            "register": name,
            "statements": str(len(rows)),
            "emitted_tokens": str(sum(lengths)),
            "closed_statements": str(sum(row["closed"] == "YES" for row in rows)),
            "open_statements": str(sum(row["closed"] != "YES" for row in rows)),
            "closure_share": f"{sum(row['closed'] == 'YES' for row in rows) / len(rows):.6f}",
            "mean_tokens": f"{sum(lengths) / len(lengths):.6f}",
            "median_tokens": str(sorted(lengths)[len(lengths) // 2]),
            "max_tokens": str(max(lengths)),
            "distinct_programs": str(len({row["program_id"] for row in rows})),
            "dominant_start": starts[name].most_common(1)[0][0],
            "dominant_start_count": str(starts[name].most_common(1)[0][1]),
            "dominant_end": ends[name].most_common(1)[0][0],
            "dominant_end_count": str(ends[name].most_common(1)[0][1]),
            "workshop_habit_de": (
                "Langer, meist offener Artikelzug; häufig mit Ansetzen/Beschicken beginnen; Zeilenumbruch darf fortsetzen."
                if name == "HERBAL" else
                "Kurze, meist geschlossene Arbeitszelle; häufig mit Halte/Zustand oder Bewegung beginnen; Abschlusskarte bevorzugen."
            ),
        })
    write("FIVE_HUNDRED_SIXTH_TWO_REGISTER_PROFILES.tsv", profiles)

    primitive_rows = []
    for name in ("HERBAL", "BIOLOGICAL"):
        total = sum(token_counts[name].values())
        for primitive in PRIMITIVES:
            primitive_rows.append({
                "register": name,
                "primitive": primitive,
                "count": str(token_counts[name][primitive]),
                "share": f"{token_counts[name][primitive] / total:.6f}",
                "start_count": str(starts[name][primitive]),
                "end_count": str(ends[name][primitive]),
            })
    write("FIVE_HUNDRED_SIXTH_16_PRIMITIVE_REGISTER_PROFILE.tsv", primitive_rows)

    bigram_rows = []
    for row in read(P505 / "FIVE_HUNDRED_FIFTH_56_PRIMITIVE_BIGRAMS.tsv"):
        edge = (row["left_primitive"], row["right_primitive"])
        h = edge_counts["HERBAL"][edge]; b = edge_counts["BIOLOGICAL"][edge]
        bigram_rows.append({
            "left_primitive": edge[0], "right_primitive": edge[1],
            "herbal_count": str(h), "biological_count": str(b),
            "register_status": "SHARED" if h and b else "HERBAL_ONLY" if h else "BIOLOGICAL_ONLY" if b else "UNSEEN",
            "combined_count": str(h + b),
        })
    write("FIVE_HUNDRED_SIXTH_56_REGISTER_BIGRAMS.tsv", bigram_rows)

    assignments = []
    for row in statements:
        name = domain(row)
        if name == "HERBAL":
            habit = "HERBAL_COMMITTED_SUBSTEP" if row["closed"] == "YES" else "HERBAL_OPEN_ARTICLE_CHAIN"
        else:
            habit = "BIO_COMMITTED_CELL" if row["closed"] == "YES" else "BIO_OPEN_CARRY_OR_HEADER"
        assignments.append({
            "statement_id": row["statement_id"], "record": row["record"], "page": row["page"],
            "register": name, "primitive_signature": row["primitive_signature"],
            "token_count": str(len(row["primitive_signature"].split(">"))),
            "closed": row["closed"], "register_habit": habit,
            "shared_machine": "PASS505_FIVE_STATE_AUTOMATON",
        })
    write("FIVE_HUNDRED_SIXTH_116_REGISTER_WORKFLOW_ASSIGNMENTS.tsv", assignments)

    manual = read(P505 / "FIVE_HUNDRED_FIFTH_122_ITEM_AUTOMATON_MANUAL.tsv")
    insert_at = next(i for i, row in enumerate(manual) if row["layer"] == "L8_RENDERER_HABIT")
    manual[insert_at:insert_at] = [
        {"manual_order": "0", "layer": "L7_REGISTER_WORKFLOW", "item_id": "REG_HERBAL",
         "teaching_value_or_rule_de": profiles[0]["workshop_habit_de"], "scope": "HERBAL",
         "support_or_instances": "19 statements;104 tokens;4 closed", "source_artifact": "PASS506_REGISTER_HABITS"},
        {"manual_order": "0", "layer": "L7_REGISTER_WORKFLOW", "item_id": "REG_BIO",
         "teaching_value_or_rule_de": profiles[1]["workshop_habit_de"], "scope": "BIOLOGICAL",
         "support_or_instances": "97 statements;366 tokens;85 closed", "source_artifact": "PASS506_REGISTER_HABITS"},
    ]
    for index, row in enumerate(manual, 1): row["manual_order"] = str(index)
    write("FIVE_HUNDRED_SIXTH_124_ITEM_REGISTER_MANUAL.tsv", manual)

    summary = {
        "status": "PASS", "statements": len(statements),
        "herbal_statements": len(by_domain["HERBAL"]), "biological_statements": len(by_domain["BIOLOGICAL"]),
        "herbal_tokens": sum(token_counts["HERBAL"].values()), "biological_tokens": sum(token_counts["BIOLOGICAL"].values()),
        "herbal_closed": sum(row["closed"] == "YES" for row in by_domain["HERBAL"]),
        "biological_closed": sum(row["closed"] == "YES" for row in by_domain["BIOLOGICAL"]),
        "shared_bigrams": sum(row["register_status"] == "SHARED" for row in bigram_rows),
        "herbal_only_bigrams": sum(row["register_status"] == "HERBAL_ONLY" for row in bigram_rows),
        "biological_only_bigrams": sum(row["register_status"] == "BIOLOGICAL_ONLY" for row in bigram_rows),
        "manual_items": len(manual),
    }
    (HERE / "FIVE_HUNDRED_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__": main()
