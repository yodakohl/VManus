#!/usr/bin/env python3
"""Build the practical 173-card multi-scribe teaching chart."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_173_GLOBAL_DICTIONARY.tsv"

CATEGORY_RULES = {
    "INVARIANT_TEACHING_CORE": "Kompositionsregel lernen und die eine registrierte Oberfläche gemeinsam schreiben.",
    "HAND_VARIABLE_ALLOGRAPH_CARD": "Identität und Wert gemeinsam lernen; die eigene Hand wählt nur aus der registrierten Palette.",
    "STABLE_MEMORIZED_TECHNICAL_CARD": "Die unteilbare technische Karte mit ihrer einzigen Form auswendig lernen.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def hand_candidates(forms: list[str]) -> dict[str, str]:
    shortest = min(forms, key=lambda x: (len(x), x))
    q_forms = [x for x in forms if x.startswith("q")]
    s_forms = [x for x in forms if x.startswith(("s", "sh"))]
    expanded = [x for x in forms if x.startswith(("ch", "t"))]
    longest = max(forms, key=lambda x: (len(x), x))
    return {
        "hand_a_bare": shortest,
        "hand_b_q_operational": min(q_forms, key=lambda x: (len(x), x)) if q_forms else shortest,
        "hand_c_s_entry": min(s_forms, key=lambda x: (len(x), x)) if s_forms else shortest,
        "hand_d_expanded": max(expanded, key=lambda x: (len(x), x)) if expanded else longest,
    }


def main() -> None:
    source = read_tsv(SOURCE)
    chart = []
    category_counts = Counter()
    category_events = Counter()
    for row in source:
        forms = row["surface_family"].split("|")
        if len(forms) > 1:
            category = "HAND_VARIABLE_ALLOGRAPH_CARD"
        elif row["deck_class"] == "MEMORIZED_WHOLE_CARD":
            category = "STABLE_MEMORIZED_TECHNICAL_CARD"
        else:
            category = "INVARIANT_TEACHING_CORE"
        candidates = hand_candidates(forms)
        category_counts[category] += 1
        category_events[category] += int(row["occurrences"])
        chart.append({
            "joint_tuple_id": row["joint_tuple_id"],
            "teaching_category": category,
            "atomic_value_de": row["atomic_value_de"],
            "component_formula": row["component_formula"],
            "deck_class": row["deck_class"],
            "registered_surface_palette": row["surface_family"],
            "surface_count": len(forms),
            "occurrences": row["occurrences"],
            "records": row["records"],
            "pages": row["pages"],
            "hand_a_bare": candidates["hand_a_bare"],
            "hand_b_q_operational": candidates["hand_b_q_operational"],
            "hand_c_s_entry": candidates["hand_c_s_entry"],
            "hand_d_expanded": candidates["hand_d_expanded"],
            "apprentice_rule_de": CATEGORY_RULES[category],
        })

    summaries = []
    for category in CATEGORY_RULES:
        rows = [row for row in chart if row["teaching_category"] == category]
        summaries.append({
            "teaching_category": category,
            "card_count": len(rows),
            "event_count": sum(int(row["occurrences"]) for row in rows),
            "productive_card_count": sum(row["deck_class"] == "PRODUCTIVE_COMPOSITION" for row in rows),
            "memorized_card_count": sum(row["deck_class"] == "MEMORIZED_WHOLE_CARD" for row in rows),
            "teaching_rule_de": CATEGORY_RULES[category],
            "example_values": "|".join(row["atomic_value_de"] for row in sorted(rows, key=lambda x: (-int(x["occurrences"]), x["atomic_value_de"]))[:8]),
        })

    write_tsv(HERE / "THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv", chart,
              ["joint_tuple_id", "teaching_category", "atomic_value_de", "component_formula", "deck_class", "registered_surface_palette", "surface_count", "occurrences", "records", "pages", "hand_a_bare", "hand_b_q_operational", "hand_c_s_entry", "hand_d_expanded", "apprentice_rule_de"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_EIGHTH_THREE_TEACHING_LAYERS.tsv", summaries,
              ["teaching_category", "card_count", "event_count", "productive_card_count", "memorized_card_count", "teaching_rule_de", "example_values"])

    variable_memorized = [row for row in chart if row["teaching_category"] == "HAND_VARIABLE_ALLOGRAPH_CARD" and row["deck_class"] == "MEMORIZED_WHOLE_CARD"]
    lines = [
        "# Gemeinsame Lehrtafel für mehrere Schreiber",
        "",
        "## 1. Feste produktive Lehrkarten",
        "",
        f"{category_counts['INVARIANT_TEACHING_CORE']} Karten / {category_events['INVARIANT_TEACHING_CORE']} Ereignisse.",
        "Jeder lernt dieselbe Komponentenregel und dieselbe beobachtete Oberfläche.",
        "",
        "## 2. Handvariable Allographkarten",
        "",
        f"{category_counts['HAND_VARIABLE_ALLOGRAPH_CARD']} Karten / {category_events['HAND_VARIABLE_ALLOGRAPH_CARD']} Ereignisse.",
        "Identität und kurzer Wert bleiben gleich; die Hand wählt aus der eingetragenen Palette.",
        "",
        "Die beiden variablen Ganzkarten sind:",
    ]
    for row in variable_memorized:
        lines.append(f"- `{row['registered_surface_palette']}` = {row['atomic_value_de']}.")
    lines.extend([
        "",
        "## 3. Stabile technische Merkkarten",
        "",
        f"{category_counts['STABLE_MEMORIZED_TECHNICAL_CARD']} Karten / {category_events['STABLE_MEMORIZED_TECHNICAL_CARD']} Ereignisse.",
        "Diese seltenen Ganzkarten werden unverändert aus dem Meisterexemplar gelernt.",
        "",
        "## Werkstattregel",
        "",
        "Der Lehrmeister prüft Kartenidentität, Bedeutung und Platzfolge. Er korrigiert eine",
        "Handform nur dann, wenn sie nicht in der Palette derselben Karte steht. So können",
        "vier Schreiber verschieden aussehen, ohne vier getrennte Grammatiken zu besitzen.",
    ])
    (HERE / "THREE_HUNDRED_THIRTY_EIGHTH_MULTI_SCRIBE_CHART.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cards": len(chart),
        "events": sum(int(row["occurrences"]) for row in chart),
        "invariant_teaching_cards": category_counts["INVARIANT_TEACHING_CORE"],
        "hand_variable_cards": category_counts["HAND_VARIABLE_ALLOGRAPH_CARD"],
        "stable_memorized_cards": category_counts["STABLE_MEMORIZED_TECHNICAL_CARD"],
        "variable_memorized_cards": len(variable_memorized),
    }
    (HERE / "THREE_HUNDRED_THIRTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
