#!/usr/bin/env python3
"""Give the 25 unresolved clauses the narrowest useful creative owner default."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BINDINGS = ROOT / "experiments/yolo/sidequest_semantic_clause_owner_binding_hundred_sixth_edition/HUNDRED_SIXTH_254_CLAUSE_OWNER_BINDING.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_116_STATEMENT_TRANSLATION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def resolution_for(unit: int) -> tuple[str, str, str, str, str]:
    if 125 <= unit <= 128:
        return (
            "B2_MIDDLE_RIGHT_RECLINING_FIGURE_VESSEL",
            "Posten der liegenden Figur im eigenständigen kleinen Trichter-/Liegebecken",
            "CREATIVE_VISIBLE_OWNER",
            "The reclining figure visibly occupies its own small vessel; the nearby horizontal line is not inherited.",
            "NO_CONNECTION_TO_HORIZONTAL_LINE",
        )
    if 172 <= unit <= 191:
        return (
            "B3_LOCAL_TRANSITION_BATCH_FROM_EXEMPLAR",
            "örtlicher Übergangsansatz zwischen Randstation und nächstem Hauptblock",
            "CREATIVE_REGISTER_BATCH",
            "No drawn edge crosses the margin-to-main gap; treat the long intervening text as its own learned work batch.",
            "NO_IMAGE_CONNECTION_CLAIM",
        )
    if unit == 192:
        return (
            "B3_MAIN_ARCH_LINKED_PAIR_WITH_INCOMING_BATCH",
            "eingehender Ansatz für das sichtbar gekoppelte Hauptpaar",
            "FORWARD_TO_NEXT_DIRECT_OWNER",
            "The source card lies in the gap, but its resolved forward attachment feeds the collection action in direct-visible F099.",
            "LOCAL_PAIR_CONNECTION_ONLY_NO_DIRECTION",
        )
    raise ValueError(unit)


def main() -> None:
    source = read_tsv(BINDINGS)
    statements = {row["statement_id"]: row for row in read_tsv(STATEMENTS)}
    revised: list[dict[str, object]] = []
    decisions: list[dict[str, object]] = []
    for row in source:
        unit = int(row["fusion_unit_order"])
        if row["owner_accessibility"] == "OWNER_UNRESOLVED":
            owner, noun, status, basis, connection = resolution_for(unit)
            decisions.append({
                "fusion_unit_id": row["fusion_unit_id"],
                "statement_id": row["statement_id"],
                "page": row["page"],
                "field_ids": row["field_ids"],
                "old_owner": row["selected_visible_owners"],
                "creative_owner": owner,
                "creative_primary_noun_de": noun,
                "resolution_status": status,
                "visual_or_attachment_basis": basis,
                "connection_ceiling": connection,
                "literal_workshop_clause_de": row["literal_workshop_clause_de"],
            })
            final_access = status
            final_owner = owner
            final_noun = noun
            expanded = f"Am Besitzer {noun}: {row['literal_workshop_clause_de']}"
        else:
            final_access = row["owner_accessibility"]
            final_owner = row["selected_visible_owners"]
            final_noun = row["silent_argument_defaults"]
            expanded = row["literal_workshop_clause_de"]
        revised.append({
            "fusion_unit_order": row["fusion_unit_order"],
            "fusion_unit_id": row["fusion_unit_id"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "field_ids": row["field_ids"],
            "final_owner_status": final_access,
            "final_owner": final_owner,
            "final_owner_noun_de": final_noun,
            "primary_noun_source": row["primary_noun_source"],
            "owner_expanded_literal_clause_de": expanded,
        })

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in revised:
        by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for statement_id, rows in sorted(by_statement.items(), key=lambda item: int(statements[item[0]]["statement_order"])):
        source_statement = statements[statement_id]
        statement_rows.append({
            "statement_order": source_statement["statement_order"],
            "statement_id": statement_id,
            "record_unit_id": source_statement["record_unit_id"],
            "page": source_statement["page"],
            "clause_count": len(rows),
            "creative_resolution_count": sum(row["final_owner_status"] in {"CREATIVE_VISIBLE_OWNER", "CREATIVE_REGISTER_BATCH", "FORWARD_TO_NEXT_DIRECT_OWNER"} for row in rows),
            "owner_expanded_literal_statement_de": ". ".join(str(row["owner_expanded_literal_clause_de"]) for row in rows) + ".",
            "current_concrete_source_expansion_de": source_statement["concrete_source_expansion_de"],
        })

    write_tsv(OUT / "HUNDRED_SEVENTH_25_CREATIVE_OWNER_RESOLUTIONS.tsv", list(decisions[0]), decisions)
    write_tsv(OUT / "HUNDRED_SEVENTH_254_REVISED_OWNER_BINDING.tsv", list(revised[0]), revised)
    write_tsv(OUT / "HUNDRED_SEVENTH_116_OWNER_RESOLVED_STATEMENTS.tsv", list(statement_rows[0]), statement_rows)

    counts = Counter(row["resolution_status"] for row in decisions)
    report = [
        "# Hundertsiebte Runde: Die letzten 25 Besitzer kreativ schließen", "",
        "## f82r", "",
        "Vier Klauseln bei f82r.19 gehören in der Arbeitsfassung zur sichtbar eigenständigen",
        "liegenden Figur im kleinen Trichter-/Liegebecken. Die nahe horizontale Linie wird",
        "nicht als Anschluss geerbt und keine Flussrichtung erfunden.", "",
        "## f83r", "",
        "Zwanzig Klauseln zwischen Randstapel und Hauptpaar werden als örtlicher",
        "Übergangsansatz des Werkstattexemplars gelesen. Das ist bewusst ein Registerbesitzer",
        "und keine unsichtbare Bildkante. Die letzte Klausel bindet ihren Ansatz vorwärts an",
        "die Sammelhandlung in F099 und gehört daher zum sichtbar gekoppelten Hauptpaar.", "",
        "Damit besitzt jede der 254 Klauseln einen brauchbaren Arbeitsbesitzer. Der Preis ist",
        "klar ausgewiesen: zwanzig Besitzer kommen aus dem lokalen Exemplar, nicht aus der",
        "Zeichnung. Das ist für ein bildadressiertes Werkstattregister glaubwürdiger als ein",
        "erfundener geschlossener Wasserlauf.", "",
        "Nur f82r/f83r der festen Auswahl und die vorhandene Bildinventur wurden benutzt;",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_SEVENTH_CREATIVE_OWNER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "decisions": len(decisions), "clauses": len(revised),
        "statements": len(statement_rows), "resolution_counts": dict(counts),
        "remaining_unresolved": sum(row["final_owner_status"] == "OWNER_UNRESOLVED" for row in revised),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
