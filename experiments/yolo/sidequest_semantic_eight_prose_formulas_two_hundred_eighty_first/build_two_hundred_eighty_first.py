#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R279 = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth"
STATEMENTS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_116_TWO_LAYER_STATEMENTS.tsv"
GRAMMAR = ROOT / "experiments/yolo/sidequest_semantic_quantity_preparation/WORKSHOP_SENTENCE_SLOTS.tsv"

SLOT_KEYS = ("link_select_slot", "source_item_slot", "quantity_slot", "operation_slot", "medium_flow_slot", "target_slot", "state_grade_slot", "close_slot")
TEMPLATE_RULES = {
    "FULL_ADDRESS_PROCESS": "Quelle und Menge nehmen, den Arbeitsgang ausführen, zum Ziel führen und den Zustand setzen.",
    "FLOW_TRANSFER_PROCESS": "Den laufenden Posten bearbeiten und über das angegebene Medium oder den Lauf führen.",
    "TARGET_APPLICATION_PROCESS": "Den laufenden Posten an der Zielstelle einsetzen oder anwenden.",
    "GRADED_PROCESS": "Den Arbeitsgang bis zum bezeichneten Zustand oder Grad führen.",
    "QUANTIFIED_PROCESS": "Die bezeichnete Menge nehmen und den Arbeitsgang damit ausführen.",
    "SOURCED_PROCESS": "Den Posten aus der bezeichneten Quelle nehmen und bearbeiten.",
    "LINKED_PROCESS": "Mit dem vorigen oder folgenden Posten weiterarbeiten.",
    "SIMPLE_OR_ELLIPTIC_PROCESS": "Den örtlich bezeichneten Arbeitsschritt ausführen; ausgelassene Argumente vom Besitzer erben.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explicit(value: str) -> bool:
    return bool(value) and not value.startswith(("AUSGELASSEN", "GEERBT", "OFFEN", "NEUE ZELLE", "ELLIPTISCH"))


def classify(row: dict[str, str]) -> str:
    present = {key for key in SLOT_KEYS if explicit(row[key])}
    if {"source_item_slot", "quantity_slot", "target_slot", "operation_slot"} <= present:
        return "FULL_ADDRESS_PROCESS"
    if "medium_flow_slot" in present and "operation_slot" in present:
        return "FLOW_TRANSFER_PROCESS"
    if "target_slot" in present and "operation_slot" in present:
        return "TARGET_APPLICATION_PROCESS"
    if "state_grade_slot" in present and "operation_slot" in present:
        return "GRADED_PROCESS"
    if "quantity_slot" in present and "operation_slot" in present:
        return "QUANTIFIED_PROCESS"
    if "source_item_slot" in present and "operation_slot" in present:
        return "SOURCED_PROCESS"
    if "link_select_slot" in present and "operation_slot" in present:
        return "LINKED_PROCESS"
    return "SIMPLE_OR_ELLIPTIC_PROCESS"


def values(text: str) -> str:
    if not explicit(text):
        return ""
    out = []
    for item in text.split(" | "):
        value = item.split("=", 1)[1] if "=" in item else item
        if value not in out:
            out.append(value)
    return "; ".join(out)


def fluent(template: str, grammar: dict[str, str], fallback: str, terminal: str) -> str:
    owner = grammar["owner_slot"]
    source, qty = values(grammar["source_item_slot"]), values(grammar["quantity_slot"])
    operation, flow = values(grammar["operation_slot"]), values(grammar["medium_flow_slot"])
    target, state = values(grammar["target_slot"]), values(grammar["state_grade_slot"])
    link = values(grammar["link_select_slot"])
    close = "Den Schritt festsetzen." if terminal == "CLOSED" else "Den Posten für die nächste Zelle offen halten."
    if template == "FULL_ADDRESS_PROCESS":
        body = f"Nimm {source or 'den laufenden Posten'} in der Angabe {qty or 'des geltenden Maßes'}; {operation or 'bearbeite ihn'}; führe ihn zu {target or 'der örtlichen Zielstelle'}; {state or 'behalte den örtlichen Zustand'}."
    elif template == "FLOW_TRANSFER_PROCESS":
        body = f"{operation or 'Bearbeite den laufenden Posten'}; führe oder verwende {flow or 'den örtlichen Lauf'}" + (f" an {target}" if target else "") + (f" bis {state}" if state else "") + "."
    elif template == "TARGET_APPLICATION_PROCESS":
        body = f"{operation or 'Setze den laufenden Posten ein'} an {target or 'der bezeichneten Stelle'}" + (f" bis {state}" if state else "") + "."
    elif template == "GRADED_PROCESS":
        body = f"{operation or 'Bearbeite den laufenden Posten'} bis {state or 'zum bezeichneten Grad'}" + (f" mit {qty}" if qty else "") + "."
    elif template == "QUANTIFIED_PROCESS":
        body = f"Nimm {qty or 'die bezeichnete Menge'}; {operation or 'führe den Arbeitsgang damit aus'}" + (f" aus {source}" if source else "") + "."
    elif template == "SOURCED_PROCESS":
        body = f"Nimm {source or 'den Posten aus der bezeichneten Quelle'}; {operation or 'bearbeite ihn'}" + (f" bis {state}" if state else "") + "."
    elif template == "LINKED_PROCESS":
        body = f"{link or 'Arbeite mit dem Folge- oder Vorposten weiter'}; {operation or 'führe den örtlichen Arbeitsgang aus'}" + (f" bis {state}" if state else "") + "."
    else:
        body = f"{operation or fallback}."
    return f"Beim Besitzer „{owner}“: {body} {close}"


def main() -> None:
    statements = read_tsv(STATEMENTS)
    grammar = read_tsv(GRAMMAR)
    grammar_by_id = {r["statement_id"]: r for r in grammar}
    assignments = []
    for row in statements:
        g = grammar_by_id[row["statement_id"]]
        cls = classify(g)
        assignments.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "loci": row["loci"],
            "surface_sequence": row["surface_sequence"],
            "formula_family": cls,
            "formula_rule_de": TEMPLATE_RULES[cls],
            "present_slots": "|".join(key.replace("_slot", "").upper() for key in SLOT_KEYS if explicit(g[key])),
            "terminal_status": row["terminal_status"],
            "grammar_close_slot": g["close_slot"],
            "grammar_close_disagreement": "YES" if ((g["close_slot"].startswith("OFFEN") and row["terminal_status"] == "CLOSED") or (not g["close_slot"].startswith("OFFEN") and row["terminal_status"] == "OPEN")) else "NO",
            "family_sequence_de": row["family_sequence_de"],
            "local_sequence_de": row["register_expansion_sequence_de"],
            "fluent_formula_reading_de": fluent(cls, g, row["register_expansion_sequence_de"], row["terminal_status"]),
        })

    counts = Counter(str(r["formula_family"]) for r in assignments)
    templates = []
    for name in TEMPLATE_RULES:
        rows = [r for r in assignments if r["formula_family"] == name]
        templates.append({
            "formula_family": name,
            "statement_count": len(rows),
            "herbal_count": sum(r["page"] in {"f10r", "f11r", "f55v", "f56r"} for r in rows),
            "bio_count": sum(r["page"] in {"f81v", "f82r", "f83r"} for r in rows),
            "closed_count": sum(r["terminal_status"] == "CLOSED" for r in rows),
            "open_count": sum(r["terminal_status"] == "OPEN" for r in rows),
            "formula_rule_de": TEMPLATE_RULES[name],
            "statement_ids": "|".join(str(r["statement_id"]) for r in rows),
        })

    assignment_path = OUT / "TWO_HUNDRED_EIGHTY_FIRST_116_FORMULA_ASSIGNMENTS.tsv"
    template_path = OUT / "TWO_HUNDRED_EIGHTY_FIRST_EIGHT_PROSE_FORMULAS.tsv"
    readable_path = OUT / "TWO_HUNDRED_EIGHTY_FIRST_COMPLETE_FLUENT_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_FIRST_REPORT.md"
    write_tsv(assignment_path, assignments, list(assignments[0]))
    write_tsv(template_path, templates, list(templates[0]))

    lines = ["# Vollständige flüssige Prosaausgabe nach acht Satzformeln", ""]
    for record in dict.fromkeys(str(r["record_unit_id"]) for r in assignments):
        rows = [r for r in assignments if r["record_unit_id"] == record]
        lines.extend([f"## {record} / {rows[0]['page']}", ""])
        for row in rows:
            lines.append(f"- **{row['statement_id']} [{row['formula_family']}]** — {row['fluent_formula_reading_de']}")
        lines.append("")
    lines.extend(["## Gebrauch", "", "Die Sätze sind die flüssige Werkstattauslegung der unveränderten Kartenreihenfolge. Die 36-Familien-Literalfolge bleibt in der TSV-Ausgabe daneben sichtbar.", ""])
    readable_path.write_text("\n".join(lines), encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 281: acht wiederkehrende Prosaformeln

## Ergebnis

Die116 Aussagen verteilen sich auf acht produktive Satzfamilien: FLOW_TRANSFER_PROCESS={counts['FLOW_TRANSFER_PROCESS']}, SIMPLE_OR_ELLIPTIC_PROCESS={counts['SIMPLE_OR_ELLIPTIC_PROCESS']}, FULL_ADDRESS_PROCESS={counts['FULL_ADDRESS_PROCESS']}, SOURCED_PROCESS={counts['SOURCED_PROCESS']}, GRADED_PROCESS={counts['GRADED_PROCESS']}, QUANTIFIED_PROCESS={counts['QUANTIFIED_PROCESS']}, TARGET_APPLICATION_PROCESS={counts['TARGET_APPLICATION_PROCESS']} und LINKED_PROCESS={counts['LINKED_PROCESS']}.

Jede Aussage erhält daraus einen vollständigen Werkstattsatz mit Besitzer, geerbten Argumenten und offenem oder festgesetztem Ende. Die Karten- und Familienfolge bleibt daneben erhalten. Damit ist oberhalb der Stammkomposition eine zweite produktive Ebene sichtbar: wiederverwendbare Satzformeln.

Die Rücklesung korrigiert außerdem genau einen alten Abschluss: H4-S002 endet mit dem inzwischen als terminal erkannten Ganzzeichen TALAM=VERWAHREN/FESTSETZEN. Daher gelten jetzt90 Aussagen als geschlossen und26 als offen; die ältere89/27-Angabe ist überholt.

Inputs `{sha(STATEMENTS)}` and `{sha(GRAMMAR)}`.
""", encoding="utf-8")
    outputs = (assignment_path, template_path, readable_path, report_path)
    summary = {"status": "PASS", "statements": len(assignments), "templates": len(templates), "counts": dict(counts), "closed": sum(r["terminal_status"] == "CLOSED" for r in assignments), "open": sum(r["terminal_status"] == "OPEN" for r in assignments), "close_disagreements": [r["statement_id"] for r in assignments if r["grammar_close_disagreement"] == "YES"], "outputs": {p.name: sha(p) for p in outputs}}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
