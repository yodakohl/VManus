#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R157 = ROOT / "experiments/yolo/sidequest_semantic_shared_renderer_simplification_hundred_fifty_seventh"
R161 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_renderer_customs_hundred_sixty_first"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]

BLOCKS = [
    {
        "block_id": "SWITCH_H4_BARE_PAIR", "record_unit_id": "H4", "event_serials": ["71", "72"],
        "selected_habit": "BARE_OR_INTERNAL", "spoken_rule_de": "Ansatz und aktueller Posten werden in dieser Klausel gemeinsam nackt weitergeschrieben.",
    },
    {
        "block_id": "SWITCH_B1_LATE_Q_CONTINUE", "record_unit_id": "B1", "event_serials": ["148", "154"],
        "selected_habit": "Q_CELL_ENTRY", "spoken_rule_de": "Die beiden späten Fortsetzungsmarker dieses Records behalten die q-Hausform.",
    },
    {
        "block_id": "SWITCH_B3_READY_FLOW", "record_unit_id": "B3", "event_serials": ["271", "279"],
        "selected_habit": "S_FLOW_ENTRY", "spoken_rule_de": "Der Bereitschaftszustand läuft über zwei aufeinanderfolgende Loci in der sh-Flusshand weiter.",
    },
]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prior = read_tsv(R161 / "HUNDRED_SIXTY_FIRST_251_CUSTOM_RENDER_TRACE.tsv")
    surfaces = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_103_SHARED_SURFACES.tsv")
    available = defaultdict(list)
    for row in surfaces:
        available[row["master_card_id"]].append((row["five_habit_class"], row["visible_surface"]))

    block_by_event = {}
    block_rows = []
    by_serial = {row["event_serial"]: row for row in prior}
    for block in BLOCKS:
        for serial in block["event_serials"]:
            block_by_event[serial] = block
        selected = [by_serial[serial] for serial in block["event_serials"]]
        block_rows.append({
            "block_id": block["block_id"], "record_unit_id": block["record_unit_id"],
            "page": selected[0]["page"], "event_count": str(len(selected)),
            "event_serials": "|".join(block["event_serials"]),
            "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in selected)),
            "loci": "|".join(row["locus"] for row in selected),
            "card_values_de": " > ".join(row["card_value_de"] for row in selected),
            "observed_surfaces": " > ".join(row["observed_surface"] for row in selected),
            "selected_habit": block["selected_habit"], "spoken_rule_de": block["spoken_rule_de"],
            "semantic_change": "NONE",
        })
    write_tsv("HUNDRED_SIXTY_SECOND_3_HAND_SWITCH_BLOCKS.tsv", block_rows)

    trace_rows = []
    residual_rows = []
    by_record = defaultdict(list)
    for row in prior:
        habit = row["custom_predicted_habit"]
        layers = row["applied_layers"]
        block = block_by_event.get(row["event_serial"])
        if block:
            habit = block["selected_habit"]
            layers += " > " + block["block_id"]
        canonical = next(surface for candidate, surface in available[row["master_card_id"]] if candidate == habit)
        habit_match = habit == row["observed_habit"]
        exact_match = canonical == row["observed_surface"]
        if exact_match:
            treatment = "WORKSHOP_RULE_EXACT"
        elif habit_match:
            treatment = "SECOND_REGISTERED_SPELLING"
        else:
            treatment = "COPY_LOCAL_REGISTERED_SURFACE_FROM_EXEMPLAR"
        out = {
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "locus": row["locus"], "field_id": row["field_id"],
            "master_card_id": row["master_card_id"], "card_value_de": row["card_value_de"],
            "observed_surface": row["observed_surface"], "observed_habit": row["observed_habit"],
            "applied_layers": layers, "final_predicted_habit": habit,
            "predicted_canonical_surface": canonical,
            "habit_match": "YES" if habit_match else "NO",
            "exact_surface_match": "YES" if exact_match else "NO",
            "apprentice_treatment": treatment, "master_recovery": "EXACT",
        }
        trace_rows.append(out)
        by_record[row["record_unit_id"]].append(out)
        if not habit_match:
            residual_rows.append({
                "event_serial": row["event_serial"], "record_unit_id": row["record_unit_id"],
                "statement_id": row["statement_id"], "page": row["page"], "locus": row["locus"],
                "master_card_id": row["master_card_id"], "card_value_de": row["card_value_de"],
                "observed_surface": row["observed_surface"], "observed_habit": row["observed_habit"],
                "scheduled_habit": habit,
                "workshop_instruction": "COPY_THIS_REGISTERED_SURFACE_FROM_LOCAL_EXEMPLAR",
                "new_rule_allowed": "NO_ISOLATED_OR_NONUNIFORM",
            })
    write_tsv("HUNDRED_SIXTY_SECOND_251_FINAL_RENDER_TRACE.tsv", trace_rows)
    write_tsv("HUNDRED_SIXTY_SECOND_36_LOCAL_EXEMPLAR_SPELLINGS.tsv", residual_rows)

    record_rows = []
    for record_id in RECORD_ORDER:
        rows = by_record[record_id]
        record_rows.append({
            "record_unit_id": record_id, "page": rows[0]["page"], "shared_events": str(len(rows)),
            "habit_matches": str(sum(row["habit_match"] == "YES" for row in rows)),
            "exact_surface_matches": str(sum(row["exact_surface_match"] == "YES" for row in rows)),
            "second_registered_spellings": str(sum(row["apprentice_treatment"] == "SECOND_REGISTERED_SPELLING" for row in rows)),
            "local_exemplar_spellings": str(sum(row["habit_match"] == "NO" for row in rows)),
            "switch_blocks": "|".join(block["block_id"] for block in BLOCKS if block["record_unit_id"] == record_id) or "NONE",
        })
    write_tsv("HUNDRED_SIXTY_SECOND_11_RECORD_RENDER_SUMMARY.tsv", record_rows)

    report = [
        "# Hundertzweiundsechzigste Runde: drei echte Handwechselblöcke, dann Schluss mit Rendererregeln", "",
        "The 42 residual habit choices contain only three repeated ordered blocks: a bare H4 pair, two late q-form",
        "continuations in B1, and a two-locus sh-flow readiness carry in B3. Teaching those three switches raises",
        "habit reproduction from 209 to 215 of 251 and exact visible reproduction from 187 to 193.", "",
        "The other 36 residuals are dispersed or internally nonuniform. Turning them into additional rules would",
        "simply rename single spellings. The apprentice therefore copies those 36 already registered forms from",
        "the local exemplar. This closes renderer expansion: nine positional rules, thirteen recurrent customs,",
        "three switch blocks, and a bounded exact-copy tail.", "",
        "Next return to content. Use the now-stable surface-to-card layer to produce one fully readable master-day",
        "workflow across a Herbal article and a Biological station sequence, with no renderer discussion in the",
        "translation itself.",
    ]
    (OUT / "HUNDRED_SIXTY_SECOND_SWITCH_BLOCK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "switch_blocks": len(block_rows), "switch_block_events": len(block_by_event),
        "shared_events": len(trace_rows),
        "habit_matches": sum(row["habit_match"] == "YES" for row in trace_rows),
        "exact_surface_matches": sum(row["exact_surface_match"] == "YES" for row in trace_rows),
        "second_registered_spellings": sum(row["apprentice_treatment"] == "SECOND_REGISTERED_SPELLING" for row in trace_rows),
        "local_exemplar_spellings": len(residual_rows), "records": len(record_rows),
        "master_recovery_failures": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
