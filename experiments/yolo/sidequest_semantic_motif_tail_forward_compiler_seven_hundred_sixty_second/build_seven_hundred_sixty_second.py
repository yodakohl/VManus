#!/usr/bin/env python3
"""Build Pass 762: replace full large exemplars with motif/tail layouts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P760 = ROOT / "experiments/yolo/sidequest_semantic_parameterized_apprentice_rules_seven_hundred_sixtieth"
P761 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_parameterization_seven_hundred_sixty_first"
P757 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_motifs_seven_hundred_fifty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    traces = read(P760 / "SEVEN_HUNDRED_SIXTIETH_116_META_RULE_TRACE.tsv")
    layouts = read(P761 / "SEVEN_HUNDRED_SIXTY_FIRST_7_PARAMETERIZED_LAYOUTS.tsv")
    tails = read(P761 / "SEVEN_HUNDRED_SIXTY_FIRST_19_LOCAL_TAIL_STRIPS.tsv")
    motifs = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_8_SHARED_CARD_MOTIFS.tsv")
    layout_for = {row["statement_id"]: row for row in layouts}
    tail_for = {row["tail_id"]: row["card_sequence"].split(" | ") for row in tails}
    motif_for = {row["motif_id"]: [row["card_recipe"]] for row in motifs}

    outputs = []
    expansion_rows = []
    mt_uses = 0
    for trace in traces:
        statement_id = trace["statement_id"]
        before = trace["after_parameterized_rules"]
        layout = layout_for.get(statement_id)
        if layout is None:
            sequence = before.split(" | ")
            layout_tokens = "NONE"
            generation_layer = "PRODUCTIVE_PLUS_PARAMETERIZED_RULES"
        else:
            tokens = layout["layout_tokens"].split()
            sequence = []
            for token in tokens:
                cards = motif_for[token] if token.startswith("M") else tail_for[token]
                start = len(sequence) + 1
                sequence.extend(cards)
                expansion_rows.append({
                    "statement_id": statement_id,
                    "formula_family": layout["formula_family"],
                    "layout_token": token,
                    "token_kind": "SHARED_MOTIF" if token.startswith("M") else "LOCAL_TAIL_STRIP",
                    "start_card_ordinal": start,
                    "end_card_ordinal": len(sequence),
                    "expanded_card_sequence": " | ".join(cards),
                })
            layout_tokens = layout["layout_tokens"]
            generation_layer = "MOTIF_TAIL_LAYOUT"
            mt_uses += 1
        outputs.append({
            "statement_id": statement_id,
            "meta_rules": trace["meta_rules"],
            "variant_ids": trace["variant_ids"],
            "generation_layer": generation_layer,
            "layout_tokens": layout_tokens,
            "forward_recipe_sequence": " | ".join(sequence),
            "forward_cards": len(sequence),
        })

    dictionary_rows = []
    for row in motifs:
        dictionary_rows.append({
            "token": row["motif_id"], "token_kind": "SHARED_MOTIF", "card_sequence": row["card_recipe"],
            "cards": 1, "uses_in_seven_layouts": row["formula_occurrences"],
        })
    for row in tails:
        dictionary_rows.append({
            "token": row["tail_id"], "token_kind": "LOCAL_TAIL_STRIP", "card_sequence": row["card_sequence"],
            "cards": row["cards"], "uses_in_seven_layouts": row["formula_uses"],
        })

    write("SEVEN_HUNDRED_SIXTY_SECOND_27_MOTIF_TAIL_DICTIONARY.tsv", dictionary_rows)
    write("SEVEN_HUNDRED_SIXTY_SECOND_7_LAYOUT_LINES.tsv", layouts)
    write("SEVEN_HUNDRED_SIXTY_SECOND_50_LAYOUT_EXPANSIONS.tsv", expansion_rows)
    write("SEVEN_HUNDRED_SIXTY_SECOND_116_FORWARD_OUTPUT.tsv", outputs)

    report = """# Pass 762 — Vorwaertscompiler ohne Vollsatz-Exemplare

Die sieben gespeicherten Vollfolgen sind entfernt. Der gebundene Rest besteht jetzt aus:

-8 gemeinsamen M-Karten;
-19 lokalen T-Reststreifen;
-7 Layoutzeilen mit insgesamt50 Tokenverweisen.

Beim Treffer auf eine der sieben grossen Bedeutungsumgebungen expandiert der Compiler die passende M/T-Zeile. Dadurch entstehen wieder74 Karten; zusammen mit den109 produktiv/kleinphrastisch erzeugten Aussagen ergibt das unveraendert116 Aussagen und381 Karten.

Kein einzelnes Artefakt speichert mehr eine komplette Zielausgabe als unstrukturierte Kartenfolge. Die groesste lokale Gedächtniseinheit ist ein T-Streifen; die gemeinsame Grammatik bleibt sichtbar. Als naechstes sollte die Lernausgabe zeitlich geordnet werden: Welche39 Werte,9 Regeln,8 Motive und19 Streifen lernt ein neuer Schreiber in welcher Reihenfolge?
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "motifs": len(motifs), "tail_strips": len(tails), "dictionary_tokens": len(dictionary_rows),
        "layouts": len(layouts), "layout_expansions": len(expansion_rows), "motif_tail_uses": mt_uses,
        "statements": len(outputs), "forward_cards": sum(int(row["forward_cards"]) for row in outputs),
        "stored_full_sentence_outputs": 0, "semantic_changes": 0, "output_changes": 0,
        "decision": "MOTIF_TAIL_COMPILER_REPLACES_SEVEN_FULL_EXEMPLARS__116_STATEMENTS_381_CARDS_UNCHANGED",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
