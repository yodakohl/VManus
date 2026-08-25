#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_invariant_dictionary_nine_hundred_sixty_sixth/PASS966_1078_SURFACE_DICTIONARY.tsv"

PREFIX_RULES = {
    "q": ("Q_POST_CLOSE_ENTRY_SHELL", "Eintritt in eine neue Zelle, besonders nach einer Schließkarte; kein allgemeines Zeilenanfangszeichen."),
    "d": ("D_ADDRESS_SHELL", "bezeichneter Unter-/Adressrahmen; Kernwert bleibt unverändert."),
    "ch": ("CH_RENDERER_SHELL", "breiter ch-Renderer des gleichen Kartenkerns."),
    "s": ("S_SERIES_SHELL", "s-Reihen- oder Fortsetzungsrenderer."),
    "sh": ("SH_HOLD_SHELL", "sh-Halterenderer derselben Karte."),
    "t": ("T_ENTRY_SHELL", "seltener t-Eintrittsrenderer."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    surfaces = read_tsv(SURFACES)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in surfaces:
        groups[row["component_recipe"]].append(row)

    pair_rows: list[dict[str, object]] = []
    rules_by_recipe: dict[str, set[str]] = defaultdict(set)
    for recipe, members in groups.items():
        by_surface = {row["surface"]: row for row in members}
        for prefix, (rule_id, meaning) in PREFIX_RULES.items():
            for base in sorted(by_surface):
                marked = prefix + base
                if marked not in by_surface:
                    continue
                pair_rows.append({
                    "component_recipe": recipe,
                    "portable_core_de": members[0]["portable_core_de"],
                    "renderer_rule": rule_id,
                    "base_surface": base,
                    "marked_surface": marked,
                    "base_events": by_surface[base]["events"],
                    "marked_events": by_surface[marked]["events"],
                    "semantic_effect": "NONE",
                    "scribal_use_de": meaning,
                })
                rules_by_recipe[recipe].add(rule_id)
    write_tsv(OUT / "PASS967_82_SIMPLE_ALLOGRAPH_PAIRS.tsv", pair_rows)

    multi_rows: list[dict[str, object]] = []
    for recipe, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        ranked = sorted(members, key=lambda row: (-int(row["events"]), row["surface"]))
        simple_rules = sorted(rules_by_recipe[recipe])
        coverage_surfaces = {row["base_surface"] for row in pair_rows if row["component_recipe"] == recipe} | {row["marked_surface"] for row in pair_rows if row["component_recipe"] == recipe}
        residual = sorted(row["surface"] for row in members if row["surface"] not in coverage_surfaces)
        multi_rows.append({
            "component_recipe": recipe,
            "portable_core_de": members[0]["portable_core_de"],
            "primary_surface": ranked[0]["surface"],
            "primary_events": ranked[0]["events"],
            "surface_variants": "|".join(row["surface"] for row in ranked),
            "variant_count": len(ranked),
            "total_events": sum(int(row["events"]) for row in ranked),
            "simple_renderer_rules": "|".join(simple_rules) or "NONE",
            "residual_internal_or_ligature_variants": "|".join(residual) or "NONE",
            "writing_instruction_de": "Primärform verwenden; markierte Form nur in der belegten Eintritts-, Adress- oder Reihenstellung.",
        })
    write_tsv(OUT / "PASS967_97_MULTIFORM_RECIPES.tsv", multi_rows)

    rule_counts = Counter(row["renderer_rule"] for row in pair_rows)
    rule_rows: list[dict[str, object]] = []
    for prefix, (rule_id, meaning) in PREFIX_RULES.items():
        members = [row for row in pair_rows if row["renderer_rule"] == rule_id]
        rule_rows.append({
            "renderer_rule": rule_id,
            "visible_operation": f"{prefix}+BASE",
            "pair_instances": len(members),
            "distinct_component_recipes": len({row["component_recipe"] for row in members}),
            "events_in_pairs": sum(int(row["base_events"]) + int(row["marked_events"]) for row in members),
            "semantic_effect": "NONE",
            "scribal_use_de": meaning,
        })
    rule_rows.append({
        "renderer_rule": "INTERNAL_OR_LIGATURE_ALLOGRAPH",
        "visible_operation": "e-Einschub, Ligatur oder Kartenschale",
        "pair_instances": sum(row["residual_internal_or_ligature_variants"] != "NONE" for row in multi_rows),
        "distinct_component_recipes": sum(row["residual_internal_or_ligature_variants"] != "NONE" for row in multi_rows),
        "events_in_pairs": sum(int(row["total_events"]) for row in multi_rows if row["residual_internal_or_ligature_variants"] != "NONE"),
        "semantic_effect": "NONE",
        "scribal_use_de": "Als gelehrte Rendererform der ganzen Karte kopieren; nicht als neuen Stamm lesen.",
    })
    write_tsv(OUT / "PASS967_RENDERER_RULES.tsv", rule_rows)

    report = f"""# Pass 967 — so schreibt der Lehrling dieselbe Karte verschieden

Von 948 Komponentenfolgen besitzen **97** mehr als eine sichtbare Form. Diese
97 Folgen ergeben 227 Oberflächenvarianten; 851 Folgen sind bislang nur in
einer Form belegt.

Die größte produktive Schreibregel ist der **q-Zelleintrittsrahmen**: 49 direkte
Paare in 46 Komponentenfamilien, zusammen 575 Ereignisse. Es folgen der
`ch`-Renderer (18 Paare), der `d`-Adressrahmen (7), der `s`-Reihenrahmen (6)
und einzelne `sh`-/`t`-Formen. Keiner dieser Wechsel ändert den Kernwert.

Beispiele:

- `okain / qokain` = `SETZEN · EINHEIT`,
- `okal / qokal / chokal` = `SETZEN · ZIEL`,
- `ol / qol / sol / chol / ls` = `FORTSETZEN`,
- `y / dy / chy / chey / shy / sy` = `DIES`,
- `chedy / chdy / chedchy` = `UMSETZEN · DIES`.

## Schreibregel

Der Lehrling wählt zuerst die Komponentenkarte. Danach setzt er nur die
Stellungs- oder Handhülle: `q-` beim Eintritt in eine neue Zelle, besonders
nach einer Schließkarte, `d-` für einen
bezeichneten Adressrahmen, `s-` für die Reihenform und `ch-/sh-/t-` als
gelernte Renderer. Ein Hüllenwechsel erzeugt niemals ein neues Wort.

Damit ist das Modell nun bidirektional genug für die Werkstatt: Eine sichtbare
Form führt eindeutig zum Kern, und für 97 häufige Kerne gibt es eine konkrete
Liste zulässiger Schreibvarianten. Nicht belegte Varianten werden weiterhin
nicht frei erfunden.
"""
    (OUT / "PASS967_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS967_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "component_recipes": len(groups), "single_surface_recipes": sum(len(value) == 1 for value in groups.values()),
        "multiform_recipes": len(multi_rows), "multiform_surfaces": sum(int(row["variant_count"]) for row in multi_rows),
        "simple_pairs": len(pair_rows), "rule_counts": rule_counts, "outputs": outputs,
    }
    (OUT / "PASS967_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
