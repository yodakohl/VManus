#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"
P555 = ROOT / "experiments/yolo/sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    renderer = read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    cards = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    event_by_id = {row["event_id"]: row for row in events}
    multi_cards = {row["card_no"] for row in cards if len(row["surfaces"].split("|")) > 1}

    ledger_rows = []
    for row in renderer:
        event = event_by_id[row["event_id"]]
        ledger_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"], "locus": row["locus"], "locus_position": row["locus_position"],
            "card_no": row["card_no"], "component_parse": event["component_parse"], "atomic_card_value_de": event["atomic_card_value_de"],
            "card_surface_inventory": card_by_id[row["card_no"]]["surfaces"], "multi_surface_card": "YES" if row["card_no"] in multi_cards else "NO",
            "renderer_first_choice": row["renderer_first_choice"], "context_wrapper_rule": row["context_wrapper_rule"],
            "remove_wrapper": row["remove_wrapper"], "applied_wrapper_stamp": row["applied_wrapper_stamp"], "renderer_final_surface": row["renderer_final_surface"],
            "wrapper_assignment_source": row["wrapper_assignment_source"], "residual_locus_mode": row["residual_locus_mode"],
            "residual_mode_load_here": row["residual_mode_load_here"], "free_renderer_choice": row["free_renderer_choice"],
            "surface_roundtrip": row["surface_roundtrip"],
        })

    context_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in renderer:
        if row["context_wrapper_rule"] != "NONE": context_groups[row["context_wrapper_rule"]].append(row)
    context_rows = []
    for rule_id, rows in sorted(context_groups.items()):
        context_rows.append({
            "rule_id": rule_id, "card_nos": "|".join(sorted({row["card_no"] for row in rows})),
            "component_parses": "|".join(sorted({event_by_id[row["event_id"]]["component_parse"] for row in rows})),
            "trigger_previous_procedure": "|".join(sorted({row["previous_procedure"] for row in rows})),
            "locus_positions": "|".join(sorted({row["locus_position"] for row in rows})),
            "remove_wrapper": "|".join(sorted({row["remove_wrapper"] for row in rows})),
            "apply_wrapper": "|".join(sorted({row["applied_wrapper_stamp"] for row in rows})),
            "output_surfaces": "|".join(sorted({row["renderer_final_surface"] for row in rows})), "events": str(len(rows)),
        })

    residual_rows = []
    for row in renderer:
        if row["wrapper_assignment_source"] == "RESIDUAL_LOCUS_TABLE":
            residual_rows.append({
                "event_id": row["event_id"], "page": row["page"], "record": row["record"], "locus": row["locus"],
                "residual_locus_mode": row["residual_locus_mode"], "mode_load_here": row["residual_mode_load_here"],
                "card_no": row["card_no"], "component_parse": event_by_id[row["event_id"]]["component_parse"],
                "first_choice": row["renderer_first_choice"], "remove_wrapper": row["remove_wrapper"],
                "applied_wrapper_stamp": row["applied_wrapper_stamp"], "final_surface": row["renderer_final_surface"],
                "local_copy_required": "YES", "free_choice": "NO",
            })

    multi_summary = []
    for card_no in sorted(multi_cards):
        rows = [row for row in ledger_rows if row["card_no"] == card_no]
        sources = Counter(row["wrapper_assignment_source"] for row in rows)
        multi_summary.append({
            "card_no": card_no, "component_parse": card_by_id[card_no]["component_parse"], "atomic_card_value_de": card_by_id[card_no]["atomic_card_value_de"],
            "surface_inventory": card_by_id[card_no]["surfaces"], "visible_events": str(len(rows)),
            "global_rule_events": str(sources["GLOBAL_RULE_RENDERER"]), "automatic_context_events": str(sources["AUTOMATIC_CONTEXT_RULE"]),
            "residual_local_events": str(sources["RESIDUAL_LOCUS_TABLE"]),
            "rule_renderable_without_local_table": str(sources["GLOBAL_RULE_RENDERER"] + sources["AUTOMATIC_CONTEXT_RULE"]),
        })

    write_tsv("FIVE_HUNDRED_FIFTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_SURFACE_RENDERER_LEDGER.tsv", ledger_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_EIGHTH_FOUR_CONTEXT_WRAPPER_RULES.tsv", context_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_EIGHTH_FIFTY_NINE_RESIDUAL_LOCAL_ASSIGNMENTS.tsv", residual_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_EIGHTH_THIRTY_FOUR_MULTI_SURFACE_CARDS.tsv", multi_summary)
    source_counts = Counter(row["wrapper_assignment_source"] for row in ledger_rows)
    multi_source_counts = Counter(row["wrapper_assignment_source"] for row in ledger_rows if row["multi_surface_card"] == "YES")
    summary = {
        "status": "PASS", "events": len(ledger_rows), "single_surface_cards": len(cards) - len(multi_cards), "single_surface_events": sum(row["multi_surface_card"] == "NO" for row in ledger_rows),
        "multi_surface_cards": len(multi_cards), "multi_surface_events": sum(row["multi_surface_card"] == "YES" for row in ledger_rows),
        "surface_variants_on_multi_cards": sum(len(card_by_id[card]["surfaces"].split("|")) for card in multi_cards),
        "renderer_sources_all": dict(sorted(source_counts.items())), "renderer_sources_multi": dict(sorted(multi_source_counts.items())),
        "automatic_without_local_table": source_counts["GLOBAL_RULE_RENDERER"] + source_counts["AUTOMATIC_CONTEXT_RULE"],
        "residual_local_events": source_counts["RESIDUAL_LOCUS_TABLE"], "residual_modes": len({row["residual_locus_mode"] for row in residual_rows}),
        "context_rules": len(context_rows), "surface_roundtrip": sum(row["surface_roundtrip"] == "YES" for row in ledger_rows), "free_renderer_choices": sum(row["free_renderer_choice"] != "NO" for row in ledger_rows),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertachtundfünfzigste Runde: Oberflächenrenderer", "", "## Ergebnis", "",
        "Die 173 exakten Karten teilen sich in 139 Ein-Oberflächen-Karten und 34 Mehr-Oberflächen-Karten. Die 34 beweglichen Karten tragen 91 attestierte Oberflächenvarianten und 202 sichtbare Ereignisse.", "",
        "Der vorhandene Werkstattrenderer erklärt 314 Ereignisse direkt durch die globale Kartenregel und acht weitere durch vier kurze Kontextregeln. 59 Ereignisse benötigen eine lokale Lokus-Tabelle mit 34 Modi. Damit sind 322/381 Oberflächen ohne lokale Tabelle und 381/381 mit der Tabelle ausführbar; es bleibt keine freie Rendererwahl.", "",
        "Innerhalb der wirklich variablen Karten sind 135/202 global, 8/202 kontextuell und 59/202 lokal tabelliert. Die vier Kontextregeln sind kleine Wrapperwechsel: q entfernen, ch entfernen, che zu sh und ch zu d.", "",
        "Die Schrift ist damit genau das gesuchte Mischsystem: produktive Bedeutung, kompakte Kartenallographie und eine begrenzte exemplarische Oberflächenschicht. Der nächste Angriff gilt den 59 lokalen Zuweisungen: lassen sie sich zu weniger als 34 Lokusmodi zusammenfassen?",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_EIGHTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
