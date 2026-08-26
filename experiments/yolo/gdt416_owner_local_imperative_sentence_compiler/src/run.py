#!/usr/bin/env python3
"""Compile the reversible GDT415 readings into concise imperative clauses."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler"
OUT = BASE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_4576_event_owner_local_edition.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_715_statement_owner_local_edition.tsv"
CORES = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}
ORDER_ROOTS = {"OL", "OT"}
GRADE_ROOTS = {"E", "EE", "EEE", "IIN", "DA"}
LOCAL_ROOTS = {
    "D_ADDR", "AM_ADDR", "A_ADDR", "S_ADDR", "LOCAL_CHAR_F", "D_LABEL", "S_LABEL",
    "M_LOCAL", "Z_ADDR", "G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B",
    "LOCAL_CHAR_J", "LOCAL_CHAR_Z", "HO", "AN", "OS", "RESUME_CARD",
}

VERBS = {
    "SOURCE_SECTION_T": {"OK": "trage {obj} ein", "CH": "entnimm {obj}", "SH": "halte {obj} fest", "K": "ordne {obj} zu", "S": "wähle {obj}", "CHD": "bearbeite {obj}", "T": "lege {obj} fest", "R": "kennzeichne {obj}", "P": "setze {obj} ein"},
    "HERBAL": {"OK": "setze {obj} im Arbeitsgang an", "CH": "nimm {obj}", "SH": "halte {obj}", "K": "gib {obj} zu", "S": "wähle {obj}", "CHD": "bearbeite {obj}", "T": "stelle {obj} ein", "R": "markiere {obj}", "P": "setze {obj} ein"},
    "BIOLOGICAL": {"OK": "setze {obj} im Stationsgang an", "CH": "entnimm {obj}", "SH": "halte {obj}", "K": "führe {obj} zu", "S": "wähle {obj}", "CHD": "bearbeite {obj}", "T": "stelle {obj} ein", "R": "markiere {obj}", "P": "setze {obj} ein"},
    "CELESTIAL": {"OK": "setze {obj}", "CH": "nimm {obj} auf", "SH": "halte {obj}", "K": "ordne {obj} zu", "S": "wähle {obj}", "CHD": "bearbeite {obj}", "T": "stelle {obj} ein", "R": "markiere {obj}", "P": "setze {obj} ein"},
    "PHARMA": {"OK": "setze {obj} als Ansatz an", "CH": "nimm {obj}", "SH": "halte {obj}", "K": "gib {obj} zu", "S": "wähle {obj}", "CHD": "bearbeite {obj}", "T": "stelle {obj} ein", "R": "markiere {obj}", "P": "setze {obj} ein"},
}

NOUNS = {
    "SOURCE_SECTION_T": {"Y": "den laufenden Eintrag", "AIIN": "den Kennwert", "AIN": "den Teilwert", "OR": "die Eintragseinheit"},
    "HERBAL": {"Y": "den Pflanzenposten", "AIIN": "den Arbeitswert", "AIN": "den Materialanteil", "OR": "die Arbeitseinheit"},
    "BIOLOGICAL": {"Y": "den Stationsposten", "AIIN": "den Stationswert", "AIN": "den Stationsanteil", "OR": "die Stationseinheit"},
    "CELESTIAL": {"Y": "den Positionsposten", "AIIN": "den Positionswert", "AIN": "den Sektoranteil", "OR": "die Positionseinheit"},
    "PHARMA": {"Y": "den Drogenposten", "AIIN": "den Mengenwert", "AIN": "den Drogenanteil", "OR": "die Ansatzeinheit"},
}

RELATIONS = {
    "SOURCE_SECTION_T": {"AL": "zur Zielspalte", "AR": "von der Ausgangszeile", "L": "über die Eintragsverbindung", "AIR": "entlang der Lesebahn"},
    "HERBAL": {"AL": "zur Zielstelle", "AR": "vom Ausgangsmaterial", "L": "über die Verbindung im Pflanzenartikel", "AIR": "entlang der Verarbeitungsbahn"},
    "BIOLOGICAL": {"AL": "zur Zielstation", "AR": "von der Ausgangsstation", "L": "über die sichtbare Verbindung", "AIR": "entlang der Stationsbahn"},
    "CELESTIAL": {"AL": "zur Zielposition", "AR": "von der Ausgangsposition", "L": "über die Ringverbindung", "AIR": "entlang der Ringbahn"},
    "PHARMA": {"AL": "zum Zielgefäß", "AR": "vom Ausgangsgefäß", "L": "über die Gefäßverbindung", "AIR": "entlang der Transferbahn"},
}

ORDER = {"OT": "danach", "OL": "weiter"}
MODIFIERS = {
    "E": "auf Grad I", "EE": "auf Grad II", "EEE": "auf Grad III",
    "IIN": "auf der bezeichneten Stufe", "DA": "auf der zweiten Stufe",
    "O": "als Ausführung", "CARRIER_Q": "als neuen Einsatz",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def coordinated(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " und " + parts[-1]


def scoped_phrases(atoms: list[str], table: dict[str, str]) -> list[str]:
    counts = Counter(atom for atom in atoms if atom in table)
    seen: Counter[str] = Counter()
    phrases: list[str] = []
    for atom in atoms:
        if atom not in table:
            continue
        seen[atom] += 1
        phrase = table[atom]
        if counts[atom] > 1:
            level = "[außen]" if seen[atom] == 1 else "[innen]" if seen[atom] == 2 else f"[Stufe {seen[atom]}]"
            phrase = f"{phrase} {level}"
        phrases.append(phrase)
    return phrases


def local_phrase(atom: str) -> str:
    if atom in {"OS", "RESUME_CARD"}:
        return "wie zuvor"
    if atom in {"G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B", "LOCAL_CHAR_J", "LOCAL_CHAR_Z"}:
        return "mit der lokalen Variante"
    if atom in {"HO", "AN"}:
        return "in der bezeichneten Klasse"
    return "an der bezeichneten Stelle"


def template_name(explicit: list[str], inherited: str, atoms: list[str]) -> str:
    has_order = any(a in ORDER_ROOTS for a in atoms)
    has_arg = any(a in ARGUMENT_ROOTS for a in atoms)
    has_rel = any(a in RELATION_ROOTS for a in atoms)
    has_grade = any(a in GRADE_ROOTS for a in atoms)
    if len(explicit) > 1:
        return "MULTI_ACTION"
    if explicit and has_order:
        return "ORDERED_ACTION"
    if explicit and has_arg and has_rel:
        return "ACTION_ARGUMENT_RELATION"
    if explicit and has_grade:
        return "GRADED_ACTION"
    if explicit and has_rel:
        return "ACTION_RELATION"
    if explicit and has_arg:
        return "ACTION_ARGUMENT"
    if explicit:
        return "ACTION_ONLY"
    if atoms == ["DY"]:
        return "CLOSE_ONLY"
    if inherited and has_rel:
        return "INHERITED_RELATION"
    if inherited and has_grade:
        return "INHERITED_GRADE"
    if inherited:
        return "INHERITED_ARGUMENT_OR_CONTROL"
    return "CONTROL_ONLY"


def render_clause(register: str, atoms: list[str], explicit: list[str], inherited: str, inherited_argument: str) -> str:
    orders = [ORDER[a] for a in atoms if a in ORDER]
    objects = scoped_phrases(atoms, NOUNS[register])
    if not objects and inherited_argument:
        objects = [NOUNS[register][inherited_argument] + " [wie zuvor]"]
    object_phrase = coordinated(objects)
    actions = [" ".join(VERBS[register][a].format(obj=object_phrase).split()) for a in explicit]
    inherited_used = not actions and bool(inherited) and any(a != "DY" for a in atoms)
    if inherited_used:
        actions = [" ".join(VERBS[register][inherited].format(obj=object_phrase).split())]
    relations = scoped_phrases(atoms, RELATIONS[register])
    modifiers = [MODIFIERS[a] for a in atoms if a in MODIFIERS]
    locals_ = [local_phrase(a) for a in atoms if a in LOCAL_ROOTS]
    segments: list[str] = []
    if inherited_used:
        segments.append("im laufenden Gang " + coordinated(actions))
    elif actions:
        segments.append(coordinated(actions))
    elif objects:
        segments.append("Bezug: " + object_phrase)
    if relations:
        segments.append(coordinated(relations))
    if modifiers:
        segments.append(coordinated(modifiers))
    if locals_:
        segments.append(coordinated(locals_))
    if "DY" in atoms:
        segments.append("schließe den Schritt")
    if not segments:
        segments.append("führe das lokale Zeichen aus")
    clause = "; ".join(segments).strip()
    if orders:
        clause = coordinated(orders).capitalize() + " " + clause
    return clause[0].upper() + clause[1:] + "."


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = {row["global_running_event_id"]: row for row in read_tsv(EVENTS)}
    statements = read_tsv(STATEMENTS)
    component_rows = read_tsv(COMPONENTS)
    known_atoms = {r["atom"] for r in component_rows}
    core_values = {r["root"]: r["selected_minimal_value_de"] for r in read_tsv(CORES)}

    clause_rows: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []
    active_by_owner: dict[tuple[str, str], str] = {}
    active_argument_by_owner: dict[tuple[str, str], str] = {}
    template_counts: Counter[str] = Counter()
    inheritance_rows: list[dict[str, object]] = []
    argument_inheritance_rows: list[dict[str, object]] = []

    for statement in statements:
        event_ids = statement["event_ids"].split("|")
        key = (statement["physical_page"], statement["owner_de"])
        active = active_by_owner.get(key, "")
        active_argument = active_argument_by_owner.get(key, "")
        clauses: list[str] = []
        statement_templates: list[str] = []
        for card_ordinal, event_id in enumerate(event_ids, 1):
            event = events[event_id]
            atoms = event["component_recipe"].split("+")
            unknown = [a for a in atoms if a not in known_atoms]
            if unknown:
                raise RuntimeError(f"unmapped atoms in {event_id}: {unknown}")
            explicit = [a for a in atoms if a in ACTION_ROOTS]
            explicit_arguments = [a for a in atoms if a in ARGUMENT_ROOTS]
            inherited = ""
            if explicit:
                active = explicit[-1]
            elif active and any(a != "DY" for a in atoms):
                inherited = active
            inherited_argument = ""
            if explicit_arguments:
                active_argument = explicit_arguments[-1]
            elif active_argument and (explicit or inherited) and atoms != ["DY"]:
                inherited_argument = active_argument
            template = template_name(explicit, inherited, atoms)
            clause = render_clause(statement["register"], atoms, explicit, inherited, inherited_argument)
            template_counts[template] += 1
            statement_templates.append(template)
            clauses.append(clause)
            clause_rows.append({
                "global_running_event_id": event_id,
                "global_statement_id": statement["global_statement_id"],
                "card_ordinal_in_statement": card_ordinal,
                "physical_page": statement["physical_page"],
                "register": statement["register"],
                "owner_class": statement["owner_class"],
                "owner_de": statement["owner_de"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "explicit_action_roots": "|".join(explicit) or "NONE",
                "inherited_action_root": inherited or "NONE",
                "explicit_argument_roots": "|".join(explicit_arguments) or "NONE",
                "inherited_argument_root": inherited_argument or "NONE",
                "template": template,
                "imperative_clause_de": clause,
                "owner_local_atom_reading_de": event["owner_local_reading_de"],
                "portable_back_projection_de": event["back_projected_core_reading_de"],
                "roundtrip_exact": event["roundtrip_exact"],
            })
            if inherited:
                inheritance_rows.append({
                    "global_running_event_id": event_id,
                    "global_statement_id": statement["global_statement_id"],
                    "physical_page": statement["physical_page"],
                    "register": statement["register"],
                    "owner_de": statement["owner_de"],
                    "surface": event["surface"],
                    "component_recipe": event["component_recipe"],
                    "inherited_action_root": inherited,
                    "inherited_action_value_de": core_values[inherited],
                    "source": "SAME_OWNER_ACTIVE_ACTION",
                })
            if inherited_argument:
                argument_inheritance_rows.append({
                    "global_running_event_id": event_id,
                    "global_statement_id": statement["global_statement_id"],
                    "physical_page": statement["physical_page"],
                    "register": statement["register"],
                    "owner_de": statement["owner_de"],
                    "surface": event["surface"],
                    "component_recipe": event["component_recipe"],
                    "inherited_argument_root": inherited_argument,
                    "inherited_argument_value_de": core_values[inherited_argument],
                    "source": "SAME_OWNER_ACTIVE_ARGUMENT",
                })
        if active:
            active_by_owner[key] = active
        if active_argument:
            active_argument_by_owner[key] = active_argument
        statement_rows.append({
            "global_statement_ordinal": statement["global_statement_ordinal"],
            "global_statement_id": statement["global_statement_id"],
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_class": statement["owner_class"],
            "owner_de": statement["owner_de"],
            "event_count": statement["event_count"],
            "event_ids": statement["event_ids"],
            "surface_sequence": statement["surface_sequence"],
            "template_sequence": "|".join(statement_templates),
            "imperative_reading_de": " ".join(clauses),
            "portable_core_reading_de": statement["portable_core_reading_de"],
            "end_mode": statement["end_mode"],
            "claim_status": "FLÜSSIGE ARBEITSLESUNG AUS BESTEHENDEN KERNEN; KEIN KLARTEXTCLAIM",
        })

    template_rows = [
        {"template": name, "event_count": count, "rule_de": {
            "MULTI_ACTION": "mehrere sichtbare Handlungsköpfe in Quellreihenfolge",
            "ORDERED_ACTION": "Folge-/Fortsetzungssignal vor sichtbarer Handlung",
            "ACTION_ARGUMENT_RELATION": "Handlung mit Posten/Wert und Adresse/Bahn",
            "GRADED_ACTION": "sichtbare Handlung mit Grad oder Stufe",
            "ACTION_RELATION": "sichtbare Handlung mit Adresse oder Bahn",
            "ACTION_ARGUMENT": "sichtbare Handlung mit Posten/Wert/Anteil/Einheit",
            "ACTION_ONLY": "sichtbare Handlung ohne ausgeschriebenes Argument",
            "CLOSE_ONLY": "reiner lizenzierter Schluss",
            "INHERITED_RELATION": "aktive Besitzerhandlung mit neuer Adresse/Bahn",
            "INHERITED_GRADE": "aktive Besitzerhandlung mit neuem Grad",
            "INHERITED_ARGUMENT_OR_CONTROL": "aktive Besitzerhandlung mit neuem Posten oder Kontrollwert",
            "CONTROL_ONLY": "lokales Kontroll-/Kennzeichen ohne Handlungsneulesung",
        }[name]}
        for name, count in sorted(template_counts.items())
    ]

    write_tsv(OUT / "gdt416_4576_imperative_clauses.tsv", clause_rows, list(clause_rows[0]))
    write_tsv(OUT / "gdt416_715_imperative_statements.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(OUT / "gdt416_template_inventory.tsv", template_rows, ["template", "event_count", "rule_de"])
    write_tsv(OUT / "gdt416_inherited_action_audit.tsv", inheritance_rows, list(inheritance_rows[0]))
    write_tsv(OUT / "gdt416_inherited_argument_audit.tsv", argument_inheritance_rows, list(argument_inheritance_rows[0]))

    edition = ["# Vollständige imperative Arbeitslesung der 26-Seiten-Basis", ""]
    current_page = ""
    for row in statement_rows:
        if row["physical_page"] != current_page:
            current_page = str(row["physical_page"])
            edition += [f"## {current_page}", ""]
        edition += [
            f"### {row['global_statement_id']} — {row['owner_de']}", "",
            str(row["imperative_reading_de"]), "",
            f"Kernspur: `{row['portable_core_reading_de']}`", "",
        ]
    (OUT / "COMPLETE_26_PAGE_IMPERATIVE_WORKING_READING.md").write_text("\n".join(edition), encoding="utf-8")

    result = {
        "status": "OWNER_LOCAL_IMPERATIVE_EDITION_COMPLETE",
        "event_count": len(clause_rows),
        "statement_count": len(statement_rows),
        "template_count": len(template_rows),
        "inherited_action_event_count": len(inheritance_rows),
        "inherited_argument_event_count": len(argument_inheritance_rows),
        "page_count": len({r["physical_page"] for r in statement_rows}),
        "new_pages": 0,
        "new_roots": 0,
        "new_portable_meanings": 0,
        "roundtrip_exact_event_count": sum(r["roundtrip_exact"] == "YES" for r in clause_rows),
    }
    (OUT / "gdt416_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
