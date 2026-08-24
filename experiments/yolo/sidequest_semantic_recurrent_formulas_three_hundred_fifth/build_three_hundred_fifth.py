#!/usr/bin/env python3
"""Inventory recurrent card chains and turn stable ones into a recipe copybook."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_ten_weak_cards_three_hundred_fourth/THREE_HUNDRED_FOURTH_173_REVISED_IMPERATIVE_LEXICON.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_ten_weak_cards_three_hundred_fourth/THREE_HUNDRED_FOURTH_116_REVISED_STATEMENTS.tsv"


SELECTED = {
    ("MC123", "MC039", "MC123"): ("F01", "POSTEN–MASS–POSTEN", "Bearbeite diesen Posten nach dem vorgeschriebenen Maß und halte ihn aktiv"),
    ("MC153", "MC128"): ("F02", "FORTSETZEN–ABSETZEN", "Führe den laufenden Gang weiter und lass ihn kurz absetzen"),
    ("MC080", "MC123"): ("F03", "ANSATZ–POSTEN", "Verwende diesen laufenden Ansatz"),
    ("MC002", "MC026"): ("F04", "LANG EINWIRKEN–EINSETZEN", "Lass ihn länger einwirken und setze ihn danach ein"),
    ("MC002", "MC083"): ("F05", "LANG–KURZ ABSCHLUSS", "Lass ihn länger einwirken und schließe mit kurzem Einwirken"),
    ("MC026", "MC039"): ("F06", "EINSETZEN–MASS", "Setze den Posten nach dem vorgeschriebenen Maß ein"),
    ("MC074", "MC082"): ("F07", "ÜBERFÜHREN–LANG EINWIRKEN", "Führe ihn über und lass ihn dort lange einwirken"),
    ("MC097", "MC154"): ("F08", "WEITERER ANTEIL–ZIEL", "Nimm einen weiteren Anteil und führe ihn dorthin"),
    ("MC154", "MC153"): ("F09", "ZIEL–FORTSETZEN", "Führe ihn dorthin und arbeite dort weiter"),
    ("MC157", "MC153"): ("F10", "GLEICHER ANSATZ–FORTSETZEN", "Verwende denselben Ansatz weiter"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = read(RAW)
    lexicon = {r["master_card_id"]: r for r in read(LEXICON)}
    statements = read(STATEMENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in raw:
        if event["event_id"] == "E181":
            continue
        by_statement[event["statement_id"]].append(event)

    recurrent = []
    all_chains: dict[tuple[str, ...], list[tuple[str, int, list[dict[str, str]]]]] = defaultdict(list)
    for statement_id, selected in by_statement.items():
        for n in (2, 3, 4):
            for index in range(len(selected) - n + 1):
                window = selected[index:index + n]
                key = tuple(r["master_card_id"] for r in window)
                all_chains[key].append((statement_id, index, window))
    recurrent_keys = [key for key, hits in all_chains.items() if len(hits) >= 2]
    recurrent_keys.sort(key=lambda key: (len(key), -len(all_chains[key]), key))
    for key in recurrent_keys:
        hits = all_chains[key]
        same_field = sum(len({r["field_id"] for r in window}) == 1 for _, _, window in hits)
        selected_formula = SELECTED.get(key)
        formula_status = "TEACHABLE_RECIPE_FORMULA" if selected_formula else "RECURRENT_CHAIN_NOT_PROMOTED"
        contexts = []
        for statement_id, _index, window in hits:
            contexts.append(f"{statement_id}:{window[0]['event_id']}-{window[-1]['event_id']}:{'/'.join(r['field_id'] for r in window)}")
        recurrent.append({
            "chain_length": len(key),
            "master_card_chain": "+".join(key),
            "surface_chain": " · ".join(hits[0][2][i]["visible_surface"] for i in range(len(key))),
            "short_value_chain_de": " + ".join(lexicon[card]["source_short_value_de"] for card in key),
            "occurrence_count": len(hits),
            "same_field_occurrences": same_field,
            "cross_field_occurrences": len(hits) - same_field,
            "formula_status": formula_status,
            "formula_id": selected_formula[0] if selected_formula else "",
            "formula_name_de": selected_formula[1] if selected_formula else "",
            "formula_reading_de": selected_formula[2] if selected_formula else "",
            "contexts": " | ".join(contexts),
            "promotion_rule_de": "gleiche Reihenfolge, mindestens zwei Belege und dieselbe ausführbare Lesung" if selected_formula else "Subkette, Feldsprung oder keine zusätzliche Lehrersparnis",
        })
    recurrent_path = HERE / "THREE_HUNDRED_FIFTH_RECURRENT_CHAINS.tsv"
    write(recurrent_path, recurrent)

    formula_rows = []
    formula_hits_by_statement: dict[str, list[tuple[int, str, tuple[str, ...]]]] = defaultdict(list)
    for key, (formula_id, name, reading) in SELECTED.items():
        hits = all_chains[key]
        for statement_id, index, _window in hits:
            formula_hits_by_statement[statement_id].append((index, formula_id, key))
        formula_rows.append({
            "formula_id": formula_id,
            "formula_name_de": name,
            "master_card_chain": "+".join(key),
            "surface_chain": " · ".join(lexicon[card]["master_form"] for card in key),
            "component_imperatives_de": " + ".join(lexicon[card]["imperative_clause_de"] for card in key),
            "formula_reading_de": reading,
            "occurrence_count": len(hits),
            "same_field_occurrences": sum(len({r["field_id"] for r in window}) == 1 for _, _, window in hits),
            "statement_ids": "|".join(statement_id for statement_id, _, _ in hits),
            "teaching_rule_de": "als feste Reihenfolge lesen; Einzelkarten behalten außerhalb der Formel ihren Wert",
        })
    formula_rows.sort(key=lambda r: r["formula_id"])
    formula_path = HERE / "THREE_HUNDRED_FIFTH_TEN_TEACHING_FORMULAS.tsv"
    write(formula_path, formula_rows)

    annotated = []
    for row in statements:
        hits = sorted(formula_hits_by_statement.get(row["statement_id"], []))
        annotated.append({
            **row,
            "formula_hit_count": len(hits),
            "formula_ids": "|".join(hit[1] for hit in hits) if hits else "NONE",
            "formula_start_indices_zero_based": "|".join(str(hit[0]) for hit in hits) if hits else "NONE",
            "formula_readings_de": " | ".join(SELECTED[hit[2]][2] for hit in hits) if hits else "NONE",
        })
    statement_path = HERE / "THREE_HUNDRED_FIFTH_116_FORMULA_ANNOTATED_STATEMENTS.tsv"
    write(statement_path, annotated)

    lines = ["# Zehn feste Rezeptformeln für den Lehrling", "", "Die Formeln sind keine neuen Wörter. Sie sind wiederkehrende Kartenfolgen, die wie Rezeptphrasen als Einheit gesprochen werden können, während jede Karte außerhalb der Formel ihren Einzelwert behält.", ""]
    for row in formula_rows:
        lines += [
            f"## {row['formula_id']} — {row['formula_name_de']}", "",
            f"**Karten:** `{row['surface_chain']}`", "",
            f"**Lies:** {row['formula_reading_de']}.", "",
            f"**Belege:** {row['occurrence_count']} ({row['statement_ids']}).", "",
        ]
    lines += ["# Aussagen mit Formeltreffern", ""]
    for row in annotated:
        if int(row["formula_hit_count"]):
            lines += [f"**{row['statement_id']} [{row['formula_ids']}]:** {row['fluent_imperative_de']}", ""]
    copybook_path = HERE / "THREE_HUNDRED_FIFTH_RECIPE_FORMULA_COPYBOOK.md"
    copybook_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_FIFTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 305: wiederkehrende Kartenfolgen werden Rezeptformeln\n\n"
        f"Die sieben Prosaseiten enthalten {len(recurrent)} wiederkehrende exakte Ketten: vierzehn Paare und ein Tripel. Zehn davon werden als lehrbare Rezeptformeln gelesen; zusammen haben sie {sum(int(r['occurrence_count']) for r in formula_rows)} Treffer. Die stärkste ist die viermalige Folge FORTSETZEN→KURZ ABSETZEN. Das zweimalige POSTEN→MASS→POSTEN bleibt bewusst eine formale Parameterklammer und wird nicht als Gleichheit oder semantischer Operator überdeutet.\n\n"
        "Die Formeln sparen dem Lehrling Sprech- und Lesearbeit, nicht Zeichen: Im Manuskript bleiben alle Karten sichtbar. Als nächstes kann eine Formelausgabe die betroffenen Aussagen glätten und prüfen, ob sich daraus wiederkehrende vollständige Prozedurblöcke über mehrere Aussagen ergeben.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "recurrent_chains": len(recurrent), "recurrent_bigrams": sum(int(r["chain_length"]) == 2 for r in recurrent),
        "recurrent_trigrams": sum(int(r["chain_length"]) == 3 for r in recurrent), "recurrent_fourgrams": sum(int(r["chain_length"]) == 4 for r in recurrent),
        "teaching_formulas": len(formula_rows), "formula_occurrences": sum(int(r["occurrence_count"]) for r in formula_rows),
        "statements_with_formula": sum(int(r["formula_hit_count"]) > 0 for r in annotated),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [RAW, LEXICON, STATEMENTS]},
        "output_hashes": {p.name: sha(p) for p in [recurrent_path, formula_path, statement_path, copybook_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
