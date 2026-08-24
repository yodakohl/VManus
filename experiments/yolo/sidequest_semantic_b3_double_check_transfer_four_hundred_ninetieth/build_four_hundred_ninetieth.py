#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P489 = ROOT / "experiments/yolo/sidequest_semantic_b1_double_charge_macro_four_hundred_eighty_ninth"

TARGET = "B3-S021"
MACRO = "UEBERGABE MIT DOPPELTER SOLLPRUEFUNG"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    target = [row for row in events if row["statement_id"] == TARGET]
    manual = read(P489 / "FOUR_HUNDRED_EIGHTY_NINTH_169_ITEM_MACRO_MANUAL.tsv")
    ledger = read(P489 / "FOUR_HUNDRED_EIGHTY_NINTH_776_MACRO_REVISED_LEDGER.tsv")
    phases = {
        "E270": ("P1_ERSTE_SOLLPRUEFUNG", "Ersten Sollwert für den laufenden Stationsansatz setzen."),
        "E271": ("P1_ERSTE_SOLLPRUEFUNG", "Den Ansatz als bereit feststellen."),
        "E272": ("P1_ERSTE_SOLLPRUEFUNG", "Den ungezeichneten Übergabepunkt adressieren."),
        "E273": ("P1_ERSTE_SOLLPRUEFUNG", "Denselben Stationsansatz weiterführen."),
        "E274": ("P2_ABSETZEN_UND_ZWEITPRUEFEN", "Den Sollwert am Übergabepunkt erneut setzen."),
        "E275": ("P2_ABSETZEN_UND_ZWEITPRUEFEN", "Den Ansatz am Übergabepunkt absetzen."),
        "E276": ("P2_ABSETZEN_UND_ZWEITPRUEFEN", "Den Ansatz dort kurz im bereiten Zustand halten."),
        "E277": ("P3_UEBERGEBEN", "Denselben Stationsansatz wieder aufnehmen."),
        "E278": ("P3_UEBERGEBEN", "Den Übergabepunkt erneut adressieren."),
        "E279": ("P3_UEBERGEBEN", "Bereitschaft unmittelbar vor der Übergabe feststellen."),
        "E280": ("P3_UEBERGEBEN", "Den Ansatz am Übergabepunkt überführen und den Schritt schließen."),
    }
    trace = []
    for row in target:
        phase, revised = phases[row["event_id"]]
        trace.append({
            "event_order": len(trace) + 1, "event_id": row["event_id"], "locus": row["locus"],
            "field_id": row["field_id"], "surface": row["surface"], "component_parse": row["component_parse"],
            "macro_phase": phase, "old_event_reading_de": row["pass481_event_de"],
            "revised_event_reading_de": revised, "state_transition": row["state_transition"],
            "active_object_de": "derselbe laufende Stationsansatz", "owner_code": row["owner_code"],
            "closes_step": row["closes_step"],
        })
    write("FOUR_HUNDRED_NINETIETH_11_EVENT_TRANSFER_TRACE.tsv", trace)

    nodes = [
        {"node_id": "N1", "state_de": "laufender Stationsansatz vor dem Übergang", "entered_at": "RECORD_STATE"},
        {"node_id": "N2", "state_de": "erstmals sollgeprüfter und bereiter Ansatz", "entered_at": "E271"},
        {"node_id": "N3", "state_de": "am Übergabepunkt abgesetzter Ansatz", "entered_at": "E275"},
        {"node_id": "N4", "state_de": "kurz bereit gehaltener Ansatz", "entered_at": "E276"},
        {"node_id": "N5", "state_de": "unmittelbar vor Übergabe erneut bereiter Ansatz", "entered_at": "E279"},
        {"node_id": "N6", "state_de": "überführter und geschlossener Ansatz", "entered_at": "E280"},
    ]
    write("FOUR_HUNDRED_NINETIETH_SIX_TRANSFER_STATES.tsv", nodes)
    edges = [
        ("E270", "N1", "N1", "ERSTE_SOLLSETZUNG"), ("E271", "N1", "N2", "BEREITSCHAFT_1"),
        ("E272", "N2", "N2", "UEBERGABEPUNKT_ADRESSIEREN"), ("E273", "N2", "N2", "WEITERFUEHREN"),
        ("E274", "N2", "N2", "ZWEITE_SOLLSETZUNG"), ("E275", "N2", "N3", "ABSETZEN"),
        ("E276", "N3", "N4", "KURZ_BEREIT_HALTen"), ("E277", "N4", "N4", "WIEDERAUFNEHMEN"),
        ("E278", "N4", "N4", "UEBERGABEPUNKT_ADRESSIEREN"), ("E279", "N4", "N5", "BEREITSCHAFT_2"),
        ("E280", "N5", "N6", "UEBERFUEHREN_UND_SCHLIESSEN"),
    ]
    edge_rows = [{"edge_order": index + 1, "event_id": event, "source_state": source, "target_state": target_state, "operation": operation} for index, (event, source, target_state, operation) in enumerate(edges)]
    write("FOUR_HUNDRED_NINETIETH_11_TRANSFER_EDGES.tsv", edge_rows)

    comparison = [
        {"feature": "new_flow_created", "B1_S002_DOUBLE_CHARGE": "YES", "B3_S021_DOUBLE_CHECK": "NO", "same_macro": "NO"},
        {"feature": "new_portions_created", "B1_S002_DOUBLE_CHARGE": "TWO", "B3_S021_DOUBLE_CHECK": "ZERO", "same_macro": "NO"},
        {"feature": "new_batch_created", "B1_S002_DOUBLE_CHARGE": "YES", "B3_S021_DOUBLE_CHECK": "NO", "same_macro": "NO"},
        {"feature": "measure_occurrences", "B1_S002_DOUBLE_CHARGE": "FIVE", "B3_S021_DOUBLE_CHECK": "TWO", "same_macro": "PARTIAL"},
        {"feature": "readiness_checks", "B1_S002_DOUBLE_CHARGE": "ZERO_EXPLICIT_CTH", "B3_S021_DOUBLE_CHECK": "THREE_CTH_BEARING", "same_macro": "NO"},
        {"feature": "visible_owner", "B1_S002_DOUBLE_CHARGE": "SHARED_POOL_VISIBLE", "B3_S021_DOUBLE_CHECK": "MARGIN_TO_MAIN_GAP_UNRESOLVED", "same_macro": "NO"},
        {"feature": "selected_procedure", "B1_S002_DOUBLE_CHARGE": "DOUBLE_CHARGE_AND_TEMPER", "B3_S021_DOUBLE_CHECK": "DOUBLE_CHECK_AND_TRANSFER", "same_macro": "NO"},
    ]
    write("FOUR_HUNDRED_NINETIETH_B1_B3_MACRO_COMPARISON.tsv", comparison)

    candidates = [
        {"candidate": "A", "macro_name_de": MACRO, "measure_ready_target_fit": 6, "object_graph_fit": 6, "owner_fit": 4, "invented_content_cost": 1, "total": 15, "decision": "SELECT"},
        {"candidate": "B", "macro_name_de": "ANSATZ ABSETZEN UND ALS BEHANDLUNG ANWENDEN", "measure_ready_target_fit": 3, "object_graph_fit": 3, "owner_fit": 2, "invented_content_cost": 3, "total": 5, "decision": "RIVAL"},
        {"candidate": "C", "macro_name_de": "B1 DOPPELBESCHICKUNG WIEDERHOLEN", "measure_ready_target_fit": 2, "object_graph_fit": 0, "owner_fit": 1, "invented_content_cost": 4, "total": -1, "decision": "REJECT"},
    ]
    write("FOUR_HUNDRED_NINETIETH_THREE_TRANSFER_READINGS.tsv", candidates)

    revised_manual = []
    for row in manual:
        new = dict(row)
        if row["item_id"] == "W:B3-S021":
            new["teaching_value_or_rule_de"] = MACRO + ": " + " ".join(item["revised_event_reading_de"] for item in trace)
            new["source_artifact"] = "PASS490_B3_DOUBLE_CHECK_TRANSFER"
        revised_manual.append(new)
    write("FOUR_HUNDRED_NINETIETH_169_ITEM_TWO_MACRO_MANUAL.tsv", revised_manual)

    trace_map = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in trace_map:
            item = trace_map[row["item_id"]]
            new["semantic_layer"] = "LOCAL_NOMENCLATOR_MACRO"
            new["syntax_item"] = "W:B3-S021"
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        revised_ledger.append(new)
    write("FOUR_HUNDRED_NINETIETH_776_TWO_MACRO_LEDGER.tsv", revised_ledger)

    translation = (
        "Setze den Sollwert des laufenden Stationsansatzes und stelle seine Bereitschaft fest. "
        "Führe ihn an den Übergabepunkt, setze dort den Sollwert erneut, setze den Ansatz ab und halte ihn kurz bereit. "
        "Nimm denselben Ansatz wieder auf, adressiere den Übergabepunkt nochmals, stelle die Bereitschaft unmittelbar vor der Übergabe fest und überführe ihn. Schluss."
    )
    (HERE / "FOUR_HUNDRED_NINETIETH_COMPLETE_B3_S021_READING.md").write_text(
        f"# {MACRO}\n\n{translation}\n\nDer lokale Besitzer bleibt ungezeichnet; deshalb bezeichnet der Makroname eine Übergabefunktion, kein behauptetes sichtbares Gerät.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "phases": len({row["macro_phase"] for row in trace}),
        "states": len(nodes), "edges": len(edge_rows), "object_changes": 0, "explicit_measure_events": 2,
        "readiness_bearing_events": 3, "selected_macro": MACRO, "same_as_b1_macro": False,
        "manual_items": len(revised_manual), "ledger_groups": len(revised_ledger), "macro_events_total": sum(row["local_macro"] != "NONE" for row in revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_NINETIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
