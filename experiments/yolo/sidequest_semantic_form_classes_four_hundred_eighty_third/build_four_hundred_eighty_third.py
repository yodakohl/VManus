#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P482 = ROOT / "experiments/yolo/sidequest_semantic_ellipsis_matrix_four_hundred_eighty_second"
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"


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


def phase_chain(rows: list[dict[str, str]]) -> str:
    phases = []
    for row in rows:
        if not phases or phases[-1] != row["action_phase"]:
            phases.append(row["action_phase"])
    if any(row["closes_step"] == "YES" for row in rows):
        phases.append("CLOSE")
    return ">".join(phases)


def teaching_rule(chain: str, statuses: tuple[str, str, str, str]) -> str:
    source, quantity, path, target = statuses
    if chain == "HOLD>CLOSE":
        return "Führe den örtlich bestimmten Halteschritt aus und schließe die Zelle."
    if chain == "MEASURE>HOLD>CLOSE":
        return "Setze den ausgeschriebenen Wert, halte den laufenden Posten entsprechend und schließe."
    if chain == "PREPARE>HOLD>CLOSE":
        return "Bearbeite den übernommenen Bestand, halte ihn bis zum örtlichen Zustand und schließe."
    if chain == "MOVE>CLOSE":
        if path == "OWNER_VISIBLE":
            return "Führe den laufenden Bestand über den sichtbaren Lauf zur sichtbaren Station und schließe."
        if path == "RECORD_INHERITED":
            return "Führe den laufenden Bestand auf dem bisherigen Weg zur sichtbaren Station und schließe."
        return "Führe den gesetzten Bestand über den lokal gelernten Weg zur sichtbaren Station und schließe."
    return "Führe die Phasenkette aus und übernimm nur die in der Klasse bezeichneten Slots."


def main() -> None:
    matrix = read(P482 / "FOUR_HUNDRED_EIGHTY_SECOND_116_ELLIPSIS_MATRIX.tsv")
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    astro = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_395_DIRECTION_REVISED_ASTRO_GROUPS.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    class_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    assignment_seed = []
    for row in matrix:
        chain = phase_chain(by_statement[row["statement_id"]])
        statuses = tuple(row[f"{slot}_status"] for slot in ("source", "quantity", "path", "target"))
        signature = chain + "||" + "|".join(statuses)
        class_members[signature].append(row)
        assignment_seed.append((row, chain, statuses, signature))

    recurring = [(signature, rows) for signature, rows in class_members.items() if len(rows) >= 2]
    recurring.sort(key=lambda item: (-len(item[1]), item[0]))
    class_id = {signature: f"F{index+1:02d}" for index, (signature, _) in enumerate(recurring)}
    form_rows = []
    for signature, rows in recurring:
        chain, status_text = signature.split("||")
        statuses = tuple(status_text.split("|"))
        form_rows.append({
            "form_class_id": class_id[signature],
            "phase_chain": chain,
            "source_supply": statuses[0],
            "quantity_supply": statuses[1],
            "path_supply": statuses[2],
            "target_supply": statuses[3],
            "statements": len(rows),
            "herbal_statements": sum(row["register"] == "HERBAL" for row in rows),
            "biological_statements": sum(row["register"] == "BIOLOGICAL" for row in rows),
            "records": len({row["record_unit_id"] for row in rows}),
            "statement_ids": "|".join(row["statement_id"] for row in rows),
            "apprentice_rule_de": teaching_rule(chain, statuses),
        })
    write("FOUR_HUNDRED_EIGHTY_THIRD_SEVEN_RECURRENT_FORM_CLASSES.tsv", form_rows)

    assignments = []
    singleton_rows = []
    for row, chain, statuses, signature in assignment_seed:
        recurrent = signature in class_id
        assignment = {
            **row,
            "phase_chain": chain,
            "form_signature": signature,
            "form_class_id": class_id.get(signature, "LOCAL_FORM"),
            "form_status": "RECURRENT_APPRENTICE_FORM" if recurrent else "LOCAL_FORM",
            "apprentice_rule_de": next((form["apprentice_rule_de"] for form in form_rows if form["form_class_id"] == class_id.get(signature)), "Aus dem lokalen Artikel-/Stationsmuster kopieren."),
        }
        assignments.append(assignment)
        if not recurrent:
            singleton_rows.append({"statement_id": row["statement_id"], "register": row["register"], "record_unit_id": row["record_unit_id"], "page": row["page"], "phase_chain": chain, "source_supply": statuses[0], "quantity_supply": statuses[1], "path_supply": statuses[2], "target_supply": statuses[3], "reason_local": "phase-chain plus slot-supply signature occurs once on the fixed pages", "complete_expansion_de": row["complete_expansion_de"]})
    write("FOUR_HUNDRED_EIGHTY_THIRD_116_FORM_CLASS_ASSIGNMENTS.tsv", assignments)
    write("FOUR_HUNDRED_EIGHTY_THIRD_65_LOCAL_FORMS.tsv", singleton_rows)

    phase_only: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        phase_only[row["phase_chain"]].append(row)
    phase_rows = []
    for chain, rows in sorted(phase_only.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(rows) < 2:
            continue
        phase_rows.append({"phase_chain": chain, "statements": len(rows), "herbal": sum(row["register"] == "HERBAL" for row in rows), "biological": sum(row["register"] == "BIOLOGICAL" for row in rows), "slot_supply_variants": len({"|".join(row[f"{slot}_status"] for slot in ("source", "quantity", "path", "target")) for row in rows}), "statement_ids": "|".join(row["statement_id"] for row in rows)})
    write("FOUR_HUNDRED_EIGHTY_THIRD_EIGHT_RECURRENT_PHASE_SKELETONS.tsv", phase_rows)

    astro_loci: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        astro_loci[(row["diagram_id"], row["page"], row["locus"])].append(row)
    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in assignments if row["record_unit_id"] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": rows[0]["page"], "domain": rows[0]["register"], "statements_or_loci": len(rows), "groups": sum(int(row["events"]) for row in rows), "recurrent_form_statements": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" for row in rows), "continuous_form_edition_de": " ".join(f"[{row['form_class_id']}] {row['apprentice_rule_de']} {row['complete_expansion_de']}" for row in rows)})
    for unit in ("A1", "A2", "A3"):
        loci = [(key, rows) for key, rows in astro_loci.items() if key[0] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": loci[0][0][1], "domain": "ASTRO", "statements_or_loci": len(loci), "groups": sum(len(rows) for _, rows in loci), "recurrent_form_statements": 0, "continuous_form_edition_de": " ".join("[LOCATE-READ-RECORD] " + "; ".join(row["pass481_celestial_reading_de"] for row in rows) + "." for _, rows in loci)})
    write("FOUR_HUNDRED_EIGHTY_THIRD_14_FORM_CLASS_UNIT_EDITIONS.tsv", units)

    md = ["# Form-class ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_form_edition_de"], ""])
    (HERE / "FOUR_HUNDRED_EIGHTY_THIRD_FORM_CLASS_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {"status": "PASS", "recurrent_form_classes": len(form_rows), "recurrent_phase_skeletons": len(phase_rows), "statements": len(assignments), "recurrent_form_statements": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" for row in assignments), "local_form_statements": len(singleton_rows), "herbal_recurrent_form_statements": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" and row["register"] == "HERBAL" for row in assignments), "biological_recurrent_form_statements": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" and row["register"] == "BIOLOGICAL" for row in assignments), "prose_events": sum(int(row["events"]) for row in assignments), "units": len(units), "groups": sum(int(row["groups"]) for row in units)}
    (HERE / "FOUR_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
