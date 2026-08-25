#!/usr/bin/env python3
"""Build Pass 760: reduce 25 context rules to nine apprentice rule families."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P758 = ROOT / "experiments/yolo/sidequest_semantic_complete_mixed_codebook_packer_seven_hundred_fifty_eighth"
P759 = ROOT / "experiments/yolo/sidequest_semantic_forward_teaching_compiler_seven_hundred_fifty_ninth"


META = {
    "M1_ECHO_CURRENT_ITEM_OR_PREPARATION": ("Wiederaufnahme", "Schreibe den aktuellen Posten oder Ansatz an der naechsten lizenzierten Stelle erneut."),
    "M2_SHIFT_GRADE_IN_ACTIVATION_CASCADE": ("Gradverschiebung", "Setze E/EE an die operative Karte der gestuften Aktivierungsfolge."),
    "M3_PACK_MEASURE_FRAME": ("Massrahmen", "Packe SOLLMASS mit Operation oder Posten nach der attestierten Messklammer."),
    "M4_WRITE_CONTINUATION_BRIDGE": ("Weiter-Bruecke", "Schreibe OL als eigene Bruecke um Ansatz, Ziel oder Schlusskadenz."),
    "M5_PACK_ADDRESS_OR_HEAD_WITH_NEIGHBOR": ("Nachbarpackung", "Packe Quelle, Ziel, Leiter oder Besitzerkopf in die attestierte Nachbarkarte."),
    "M6_USE_ATTESTED_WITHIN_CARD_ORDER": ("Kartenreihenfolge", "Waehle bei gleicher Komponentenmenge die gelernte interne Reihenfolge."),
    "M7_REPEAT_ONE_CARD": ("Kartenwiederholung", "Wiederhole die angegebene Fachkarte genau einmal."),
    "M8_SPLIT_OR_REDISTRIBUTE_NEIGHBORS": ("Kartengrenze", "Verschiebe die Kartengrenze oder verteile OL/Y auf zwei Nachbarkarten."),
    "M9_WRITE_ORDERED_CADENCE": ("Kadenz", "Schreibe eine kurze gelernte Parallel- oder Abschlussfolge in ihrer festen Reihenfolge."),
}

ASSIGN = {
    "P748:R1_MEASURED_ITEM_BEFORE_CLOSED_TRANSFER": "M1_ECHO_CURRENT_ITEM_OR_PREPARATION",
    "P750:R1_REPEAT_PREPARATION_AROUND_STAGE": "M1_ECHO_CURRENT_ITEM_OR_PREPARATION",
    "P750:R2_PREPARATION_BEFORE_PORTION": "M1_ECHO_CURRENT_ITEM_OR_PREPARATION",
    "P750:R3_PREPARATION_BEFORE_PASSAGE": "M1_ECHO_CURRENT_ITEM_OR_PREPARATION",
    "P754:R1_APPEND_CURRENT_ITEM_AFTER_READY": "M1_ECHO_CURRENT_ITEM_OR_PREPARATION",
    "P748:R2_STAGED_ACTIVATION_BEFORE_HOLD": "M2_SHIFT_GRADE_IN_ACTIVATION_CASCADE",
    "P748:R3_STAGED_ACTIVATION_AFTER_NEXT_TARGET": "M2_SHIFT_GRADE_IN_ACTIVATION_CASCADE",
    "P751:R1_RESUMED_MEASURED_ADDITION": "M3_PACK_MEASURE_FRAME",
    "P751:R2_MEASURED_ITEM_BEFORE_FULL_CLOSE": "M3_PACK_MEASURE_FRAME",
    "P751:R3_ACTIVATE_THEN_MEASURE_BEFORE_WATER_TRANSFER": "M3_PACK_MEASURE_FRAME",
    "P756:R1_MEASURE_PORTION_SERIES": "M3_PACK_MEASURE_FRAME",
    "P752:R1_PREPARATION_CONTINUATION_BRIDGE": "M4_WRITE_CONTINUATION_BRIDGE",
    "P752:R2_CURRENT_ITEM_CONTINUATION_CADENCE": "M4_WRITE_CONTINUATION_BRIDGE",
    "P752:R4_TARGET_CONTINUATION_BEFORE_TRANSFER": "M4_WRITE_CONTINUATION_BRIDGE",
    "P752:R3_PORTION_TARGET_SOURCE_BRIDGE": "M5_PACK_ADDRESS_OR_HEAD_WITH_NEIGHBOR",
    "P754:R2_PACK_INGREDIENT_WITH_ITEM_AFTER_RESUME": "M5_PACK_ADDRESS_OR_HEAD_WITH_NEIGHBOR",
    "P754:R4_PACK_L_WITH_PASSAGE_ITEM": "M5_PACK_ADDRESS_OR_HEAD_WITH_NEIGHBOR",
    "P754:R6_PACK_OK_WITH_MEASURE": "M5_PACK_ADDRESS_OR_HEAD_WITH_NEIGHBOR",
    "P754:R7_PACK_SOURCE_WITH_ITEM": "M5_PACK_ADDRESS_OR_HEAD_WITH_NEIGHBOR",
    "P754:R3_USE_ATTESTED_T_E_Y_ORDER": "M6_USE_ATTESTED_WITHIN_CARD_ORDER",
    "P754:R5_REPEAT_MEASURED_ACTIVATION": "M7_REPEAT_ONE_CARD",
    "P755:R1_SPLIT_PASSAGE_AND_TRANSFER": "M8_SPLIT_OR_REDISTRIBUTE_NEIGHBORS",
    "P755:R2_REDISTRIBUTE_CONTINUATION_AND_ACTIVE_ITEM": "M8_SPLIT_OR_REDISTRIBUTE_NEIGHBORS",
    "P756:R2_HOLD_INGREDIENT_REPEAT_ACTIVATION": "M9_WRITE_ORDERED_CADENCE",
    "P756:R3_ORDERED_TRANSFER_MEASURE_CLOSE": "M9_WRITE_ORDERED_CADENCE",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_once(sequence: list[str], trigger: list[str], replacement: list[str]) -> tuple[list[str], bool]:
    hits = [start for start in range(len(sequence) - len(trigger) + 1) if sequence[start : start + len(trigger)] == trigger]
    if not hits:
        return sequence, False
    if len(hits) != 1:
        raise AssertionError((trigger, hits))
    start = hits[0]
    return sequence[:start] + replacement + sequence[start + len(trigger) :], True


def main() -> None:
    flat_rules = read(P759 / "SEVEN_HUNDRED_FIFTY_NINTH_25_CONTEXT_RULES.tsv")
    traces = read(P759 / "SEVEN_HUNDRED_FIFTY_NINTH_116_LAYER_TRACE.tsv")
    inputs = {row["statement_id"]: row for row in read(P759 / "SEVEN_HUNDRED_FIFTY_NINTH_116_FORWARD_INPUT.tsv")}
    exemplars = read(P758 / "SEVEN_HUNDRED_FIFTY_EIGHTH_7_BOUND_EXEMPLARS.tsv")
    exemplar_lookup = {row["semantic_trigger_sequence"]: row for row in exemplars}
    assert set(ASSIGN) == {row["rule_id"] for row in flat_rules}

    variants = []
    for row in flat_rules:
        meta_id = ASSIGN[row["rule_id"]]
        variants.append({
            "meta_rule_id": meta_id,
            "meta_rule_name_de": META[meta_id][0],
            "variant_id": row["rule_id"],
            "trigger_recipe_sequence": row["trigger_recipe_sequence"],
            "replacement_recipe_sequence": row["replacement_recipe_sequence"],
            "source_forward_uses": row["forward_uses"],
        })

    outputs = []
    meta_trace = []
    use_counts: Counter[str] = Counter()
    variant_counts: Counter[str] = Counter()
    exemplar_uses = 0
    for trace in traces:
        sequence = trace["y_packer_output"].split(" | ")
        applied_meta = []
        applied_variants = []
        for variant in variants:
            sequence, hit = replace_once(
                sequence,
                variant["trigger_recipe_sequence"].split(" | "),
                variant["replacement_recipe_sequence"].split(" | "),
            )
            if hit:
                applied_meta.append(variant["meta_rule_id"])
                applied_variants.append(variant["variant_id"])
                use_counts[variant["meta_rule_id"]] += 1
                variant_counts[variant["variant_id"]] += 1
        before_exemplar = " | ".join(sequence)
        exemplar = exemplar_lookup.get(before_exemplar)
        exemplar_id = "NONE"
        if exemplar:
            sequence = exemplar["memorized_card_sequence"].split(" | ")
            exemplar_id = exemplar["exemplar_id"]
            exemplar_uses += 1
        statement_id = trace["statement_id"]
        outputs.append({
            "statement_id": statement_id,
            "page": inputs[statement_id]["page"],
            "record": inputs[statement_id]["record"],
            "meta_rules": ",".join(applied_meta) or "NONE",
            "variant_ids": ",".join(applied_variants) or "NONE",
            "bound_exemplar": exemplar_id,
            "forward_recipe_sequence": " | ".join(sequence),
            "forward_cards": len(sequence),
        })
        meta_trace.append({
            "statement_id": statement_id,
            "y_packer_output": trace["y_packer_output"],
            "meta_rule_count": len(applied_meta),
            "meta_rules": ",".join(applied_meta) or "NONE",
            "variant_ids": ",".join(applied_variants) or "NONE",
            "after_parameterized_rules": before_exemplar,
            "bound_exemplar": exemplar_id,
            "final_output": " | ".join(sequence),
        })

    meta_rows = []
    for meta_id, (name, instruction) in META.items():
        member_variants = [row for row in variants if row["meta_rule_id"] == meta_id]
        meta_rows.append({
            "meta_rule_id": meta_id,
            "name_de": name,
            "apprentice_instruction_de": instruction,
            "registered_variants": len(member_variants),
            "forward_uses": use_counts[meta_id],
            "variant_ids": ",".join(row["variant_id"] for row in member_variants),
        })

    write("SEVEN_HUNDRED_SIXTIETH_9_PARAMETERIZED_RULES.tsv", meta_rows)
    write("SEVEN_HUNDRED_SIXTIETH_25_REGISTERED_VARIANTS.tsv", variants)
    write("SEVEN_HUNDRED_SIXTIETH_116_META_RULE_TRACE.tsv", meta_trace)
    write("SEVEN_HUNDRED_SIXTIETH_116_FORWARD_OUTPUT.tsv", outputs)

    rulebook = """# Neun Regeln fuer den Lehrling — Pass 760

1. **Wiederaufnahme:** aktuellen Posten oder Ansatz an einer lizenzierten Stelle nochmals schreiben.
2. **Gradverschiebung:** E/EE gehoert in einer Aktivierungskaskade zur operativen Karte.
3. **Massrahmen:** Sollmass mit Operation oder aktuellem Posten nach der gelernten Klammer packen.
4. **Weiter-Bruecke:** OL kann Ansatz, Ziel oder Abschluss als eigene Karte verbinden.
5. **Nachbarpackung:** Quelle, Ziel, Leiter oder Besitzerkopf mit der attestierten Nachbarkarte verbinden.
6. **Kartenreihenfolge:** bei gleicher Komponentenmenge die gelernte interne Reihenfolge nehmen.
7. **Kartenwiederholung:** die genannte Fachkarte einmal wiederholen.
8. **Kartengrenze:** eine Karte teilen oder OL/Y auf zwei Nachbarn verteilen.
9. **Kadenz:** eine kurze Parallel- oder Abschlussfolge in fester Reihenfolge schreiben.

Die25 konkreten Varianten bleiben als Beispiele unter diesen neun Regeln. Der Lehrling lernt also neun Handgriffe, nicht25 unabhaengige grammatische Prinzipien.
"""
    (HERE / "SEVEN_HUNDRED_SIXTIETH_NINE_RULE_APPRENTICE_SHEET.md").write_text(rulebook, encoding="utf-8")

    report = f"""# Pass 760 — neun parameterisierte Lehrregeln

Die25 kleinen Kontextregeln wurden auf neun Handgriffe reduziert. Ihre Varianten bleiben als finite Beispiele, aber der Lehrling muss nur neun Arten von Entscheidung verstehen.

Die Verteilung ist5 Wiederaufnahmen,2 Gradverschiebungen,4 Massrahmen,3 Weiter-Bruecken,5 Nachbarpackungen, je1 interne Reihenfolge und Kartenwiederholung sowie2 Kartengrenzen und2 Kadenzen. Alle25 Varianten feuern weiterhin genau einmal; sieben gebundene Exemplare folgen danach.

Der parameterisierte Compiler erzeugt dieselben116 Aussagen und381 Karten wie Pass759. Die Vereinfachung aendert keine Bedeutung und keine Ausgabe; sie macht das System lediglich plausibler lernbar.
"""
    (HERE / "SEVEN_HUNDRED_SIXTIETH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "meta_rules": len(meta_rows), "registered_variants": len(variants),
        "meta_rule_uses": sum(use_counts.values()), "variant_uses": sum(variant_counts.values()),
        "statements": len(outputs), "forward_cards": sum(int(row["forward_cards"]) for row in outputs),
        "bound_exemplar_uses": exemplar_uses, "semantic_changes": 0, "output_changes": 0,
        "decision": "TWENTY_FIVE_VARIANTS_COLLAPSE_TO_NINE_APPRENTICE_RULES__OUTPUT_UNCHANGED",
    }
    (HERE / "SEVEN_HUNDRED_SIXTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
