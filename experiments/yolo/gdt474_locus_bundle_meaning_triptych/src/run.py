#!/usr/bin/env python3
"""Render every GDT473 locus bundle as address, instruction, and catalogue."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych"
OUT = BASE / "artifacts"
EDITION = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts/gdt473_183_unified_address_working_edition.tsv"
CORES = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
G416_PATH = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/src/run.py"

EVENTS_OUT = OUT / "gdt474_183_event_meaning_triptych.tsv"
BUNDLES_OUT = OUT / "gdt474_146_locus_bundle_meaning_triptych.tsv"
ROOTS_OUT = OUT / "gdt474_19_root_grammatical_recasts.tsv"
PAGES_OUT = OUT / "gdt474_6_page_model_profile.tsv"
PATTERNS_OUT = OUT / "gdt474_6_choice_pattern_summary.tsv"
READABLE_OUT = OUT / "GDT474_LOCUS_BUNDLE_READING_BOOK.md"
RESULT_OUT = OUT / "gdt474_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}
ORDER_ROOTS = {"OL", "OT"}
COORDINATE_RECAST_CONTROLS = {"O", "DY"}

NAME_RE = re.compile(r"\[(PFLANZENNAME|STERNSTELLENNAME|BADSTATIONSNAME|DROGENNAME):([^\]]+)\]")
FAMILY_RE = re.compile(r"([^ ·:]+):(PFLANZENFAMILIE|STERNSTELLENFAMILIE|BADSTATIONSFAMILIE|DROGENFAMILIE)")

NAME_NOMINATIVE = {
    "PFLANZENNAME": "Pflanzenname",
    "STERNSTELLENNAME": "Sternstelle",
    "BADSTATIONSNAME": "Badstation",
    "DROGENNAME": "Droge",
}

NAME_ACCUSATIVE = {
    "PFLANZENNAME": "den Pflanzeneintrag",
    "STERNSTELLENNAME": "den Sternstelleneintrag",
    "BADSTATIONSNAME": "die Badstation",
    "DROGENNAME": "den Drogeneintrag",
}

COORDINATE_ACTION = {
    "SETZEN": "Setzpunkt",
    "NEHMEN": "Entnahmepunkt",
    "HALTEN": "Haltepunkt",
    "GEBEN": "Zuweisepunkt",
    "WÄHLEN": "Auswahlpunkt",
    "BEARBEITEN": "Bearbeitungsstelle",
    "EINSTELLEN": "Einstellpunkt",
    "MARKIEREN": "Marke",
    "EINSETZEN": "Einsatzstelle",
}

CATALOGUE_ACTION = {
    "SETZEN": "Setzvermerk",
    "NEHMEN": "Entnahmevermerk",
    "HALTEN": "Haltevermerk",
    "GEBEN": "Zuweisungsvermerk",
    "WÄHLEN": "Auswahlvermerk",
    "BEARBEITEN": "Bearbeitungsvermerk",
    "EINSTELLEN": "Einstellvermerk",
    "MARKIEREN": "Markierungsvermerk",
    "EINSETZEN": "Einsatzvermerk",
}

COORDINATE_ARGUMENTS = {
    "HERBAL": {"POSTEN": "Pflanzenposten", "WERT": "Arbeitswert", "ANTEIL": "Materialanteil", "EINHEIT": "Arbeitseinheit"},
    "CELESTIAL": {"POSTEN": "Positionsposten", "WERT": "Positionswert", "ANTEIL": "Sektoranteil", "EINHEIT": "Positionseinheit"},
    "BIOLOGICAL": {"POSTEN": "Stationsposten", "WERT": "Stationswert", "ANTEIL": "Stationsanteil", "EINHEIT": "Stationseinheit"},
    "PHARMA": {"POSTEN": "Drogenposten", "WERT": "Mengenwert", "ANTEIL": "Drogenanteil", "EINHEIT": "Ansatzeinheit"},
}

COORDINATE_RELATIONS = {
    "HERBAL": {"ZIELORT": "Zielstelle", "AUSGANG": "Ausgangsmaterial", "VERBINDUNG": "Pflanzenverbindung", "BAHN": "Verarbeitungsbahn"},
    "CELESTIAL": {"ZIELORT": "Zielposition", "AUSGANG": "Ausgangsposition", "VERBINDUNG": "Ringverbindung", "BAHN": "Ringbahn"},
    "BIOLOGICAL": {"ZIELORT": "Zielstation", "AUSGANG": "Ausgangsstation", "VERBINDUNG": "sichtbare Verbindung", "BAHN": "Stationsbahn"},
    "PHARMA": {"ZIELORT": "Zielgefäß", "AUSGANG": "Ausgangsgefäß", "VERBINDUNG": "Gefäßverbindung", "BAHN": "Transferbahn"},
}

CATALOGUE_VALUES = {
    "POSTEN": "Postenangabe",
    "WERT": "Wertangabe",
    "ANTEIL": "Anteilsangabe",
    "EINHEIT": "Einheitsangabe",
    "ZIELORT": "Zielzuordnung",
    "AUSGANG": "Ausgangszuordnung",
    "VERBINDUNG": "Verbindungsvermerk",
    "BAHN": "Bahnvermerk",
    "FORTSETZEN": "Fortsetzungsvermerk",
    "DANACH": "Folgevermerk",
    "GRAD I": "Grad I",
    "GRAD II": "Grad II",
    "GRAD III": "Grad III",
    "STUFE": "Stufenvermerk",
    "ZWEITE STUFE": "zweite Stufe",
    "AUSFÜHRUNG": "Ausführungsvermerk",
    "HIER": "Hier-Vermerk",
    "SCHLUSS": "Schlussvermerk",
}

COORDINATE_OTHER = {
    "FORTSETZEN": "weiter",
    "DANACH": "danach",
    "GRAD I": "Grad I",
    "GRAD II": "Grad II",
    "GRAD III": "Grad III",
    "STUFE": "Stufe",
    "ZWEITE STUFE": "zweite Stufe",
    "AUSFÜHRUNG": "Ausführungspunkt",
    "HIER": "hier",
    "SCHLUSS": "Endpunkt",
}

ROOT_RECAST = {
    "Y": ("Postenposition", "den Posten", "Postenangabe"),
    "OK": ("Setzpunkt", "setze", "Setzvermerk"),
    "OL": ("Fortsetzungsrichtung", "weiter", "Fortsetzungsvermerk"),
    "OT": ("Folgestelle", "danach", "Folgevermerk"),
    "AL": ("Zieladresse", "zum Zielort", "Zielzuordnung"),
    "CH": ("Entnahmepunkt", "nimm", "Entnahmevermerk"),
    "SH": ("Haltepunkt", "halte", "Haltevermerk"),
    "AR": ("Ausgangsadresse", "vom Ausgang", "Ausgangszuordnung"),
    "K": ("Zuweisepunkt", "gib/ordne zu", "Zuweisungsvermerk"),
    "AIIN": ("Wertposition", "den Wert", "Wertangabe"),
    "S": ("Auswahlpunkt", "wähle", "Auswahlvermerk"),
    "CHD": ("Bearbeitungsstelle", "bearbeite", "Bearbeitungsvermerk"),
    "OR": ("Einheitsposition", "die Einheit", "Einheitsangabe"),
    "L": ("Verbindungsadresse", "über die Verbindung", "Verbindungsvermerk"),
    "T": ("Einstellpunkt", "stelle ein", "Einstellvermerk"),
    "AIN": ("Anteilsposition", "den Anteil", "Anteilsangabe"),
    "R": ("Marke", "markiere", "Markierungsvermerk"),
    "P": ("Einsatzstelle", "setze ein", "Einsatzvermerk"),
    "AIR": ("Bahnadresse", "entlang der Bahn", "Bahnvermerk"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atoms(row: dict[str, str]) -> list[str]:
    return [] if row["working_recipe"] == "NONE" else row["working_recipe"].split("+")


def names(reading: str, grammatical_case: str = "nominative") -> list[str]:
    table = NAME_NOMINATIVE if grammatical_case == "nominative" else NAME_ACCUSATIVE
    return [f"{table[kind]} »{value}«" for kind, value in NAME_RE.findall(reading)]


def families(reading: str) -> list[str]:
    return [f"{kind.replace('FAMILIE', '').title()}familie »{stem}«" for stem, kind in FAMILY_RE.findall(reading)]


def reading_parts(reading: str) -> list[str]:
    return reading.split(" · ")


def coordinate_token(token: str, register: str) -> str:
    name_match = NAME_RE.fullmatch(token)
    if name_match:
        return f"{NAME_NOMINATIVE[name_match.group(1)]} »{name_match.group(2)}«"
    family_match = FAMILY_RE.fullmatch(token)
    if family_match:
        return f"{family_match.group(2).replace('FAMILIE', '').title()}familie »{family_match.group(1)}«"
    if token in COORDINATE_ACTION:
        return COORDINATE_ACTION[token]
    if token in COORDINATE_ARGUMENTS[register]:
        return COORDINATE_ARGUMENTS[register][token]
    if token in COORDINATE_RELATIONS[register]:
        return COORDINATE_RELATIONS[register][token]
    return COORDINATE_OTHER.get(token, token.title())


def catalogue_token(token: str) -> str:
    if NAME_RE.fullmatch(token) or FAMILY_RE.fullmatch(token):
        return ""
    if token in CATALOGUE_ACTION:
        return CATALOGUE_ACTION[token]
    return CATALOGUE_VALUES.get(token, token.title())


def coordinate_event(row: dict[str, str]) -> str:
    trace = " → ".join(coordinate_token(part, row["register"]) for part in reading_parts(row["working_reading_de"]))
    return f"Adressspur: {trace}."


def catalogue_event(row: dict[str, str]) -> str:
    event_names = names(row["working_reading_de"], "nominative")
    event_families = families(row["working_reading_de"])
    head = " / ".join(event_names) if event_names else f"Eintrag »{row['surface']}«"
    qualifiers = [catalogue_token(part) for part in reading_parts(row["working_reading_de"])]
    qualifiers = [item for item in qualifiers if item]
    qualifiers.extend(event_families)
    return head + (" — " + ", ".join(qualifiers) if qualifiers else "") + "."


def sentence_case(text: str) -> str:
    text = " ".join(text.split()).strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def instruction_event(row: dict[str, str], g416, active_action: str, active_argument: str) -> tuple[str, str, str]:
    event_atoms = atoms(row)
    explicit_actions = [atom for atom in event_atoms if atom in ACTION_ROOTS]
    explicit_arguments = [atom for atom in event_atoms if atom in ARGUMENT_ROOTS]
    object_parts = names(row["working_reading_de"], "accusative")
    object_parts.extend(g416.scoped_phrases(event_atoms, g416.NOUNS[row["register"]]))
    if explicit_arguments:
        active_argument = explicit_arguments[-1]
    elif not object_parts and active_argument and (explicit_actions or active_action):
        object_parts.append(g416.NOUNS[row["register"]][active_argument] + " [wie zuvor]")
    object_phrase = g416.coordinated(object_parts) if object_parts else "den Eintrag"

    inherited = False
    if explicit_actions:
        action = explicit_actions[-1]
        active_action = action
        action_parts = [g416.VERBS[row["register"]][atom].format(obj=object_phrase) for atom in explicit_actions]
        main = g416.coordinated([" ".join(part.split()) for part in action_parts])
    elif active_action:
        inherited = True
        main = "im selben Gang " + " ".join(g416.VERBS[row["register"]][active_action].format(obj=object_phrase).split())
    elif event_atoms:
        main = "beziehe " + object_phrase
    else:
        pure_names = names(row["working_reading_de"], "accusative")
        main = "verwende " + (g416.coordinated(pure_names) if pure_names else "den bezeichneten Eintrag")

    relations = g416.scoped_phrases(event_atoms, g416.RELATIONS[row["register"]])
    if relations:
        main += " " + g416.coordinated(relations)
    modifiers = [g416.MODIFIERS[atom] for atom in event_atoms if atom in g416.MODIFIERS]
    if modifiers:
        main += ", " + g416.coordinated(modifiers)
    locals_ = [g416.local_phrase(atom) for atom in event_atoms if atom in g416.LOCAL_ROOTS]
    if locals_:
        main += " " + g416.coordinated(locals_)
    family_parts = families(row["working_reading_de"])
    if family_parts:
        main += ", aus der " + g416.coordinated(family_parts)
    if "DY" in event_atoms:
        main += ", und schließe den Schritt"
    orders = [g416.ORDER[atom] for atom in event_atoms if atom in g416.ORDER]
    if orders:
        main = g416.coordinated(orders) + " " + main
    return sentence_case(main) + ".", active_action, active_argument


def coordinate_cost(rows: list[dict[str, str]]) -> int:
    return sum(atom in ACTION_ROOTS or atom in COORDINATE_RECAST_CONTROLS for row in rows for atom in atoms(row))


def instruction_cost(rows: list[dict[str, str]]) -> int:
    active = False
    repairs = 0
    for row in rows:
        if any(atom in ACTION_ROOTS for atom in atoms(row)):
            active = True
        elif not active:
            repairs += 1
    return repairs


def catalogue_cost(rows: list[dict[str, str]]) -> int:
    action_recasts = sum(atom in ACTION_ROOTS for row in rows for atom in atoms(row))
    named = sum(bool(names(row["working_reading_de"])) for row in rows)
    unnamed = len(rows) - named
    implicit_headwords = max(0, unnamed - named)
    return action_recasts + implicit_headwords


def join_clauses(clauses: list[str]) -> str:
    if len(clauses) == 1:
        return clauses[0]
    return " ".join(f"{index}. {clause}" for index, clause in enumerate(clauses, start=1))


def choose_model(scores: dict[str, int], rows: list[dict[str, str]]) -> tuple[list[str], str, str]:
    minimum = min(scores.values())
    best = [model for model in ("COORDINATE", "INSTRUCTION", "CATALOGUE") if scores[model] == minimum]
    if len(best) == 1:
        return best, best[0], "UNIQUE_LOWEST_REPAIR"
    has_name = any(names(row["working_reading_de"]) for row in rows)
    has_action = any(atom in ACTION_ROOTS for row in rows for atom in atoms(row))
    if "CATALOGUE" in best and has_name:
        return best, "CATALOGUE", "VISIBLE_NAME_BREAKS_TIE_TO_CATALOGUE"
    if "INSTRUCTION" in best and has_action:
        return best, "INSTRUCTION", "EXPLICIT_ACTION_BREAKS_TIE_TO_INSTRUCTION"
    return best, "COORDINATE", "ADDRESS_DEFAULT_BREAKS_TIE_TO_COORDINATE"


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_reading_book(bundle_rows: list[dict[str, object]], root_rows: list[dict[str, object]], result: dict[str, object]) -> str:
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in bundle_rows:
        by_page[str(row["physical_page"])].append(row)
    lines = [
        "# GDT474 — Lesedreieck der lokalen Locus-Bündel",
        "",
        "Jedes der 146 sichtbaren Bündel steht hier gleichzeitig als Adressspur, Arbeitsanweisung und Katalogeintrag. Die Zahlen in Klammern zählen nur die nötigen grammatischen Hilfsannahmen: Handlung zum Ortsnomen machen, ein fehlendes Verb einsetzen oder ein unsichtbares Katalogstichwort ergänzen. Niedriger bedeutet flüssiger, nicht wahrer.",
        "",
        "| Modell | nötige Hilfsannahmen über alle Bündel | als Arbeitswahl benutzt |",
        "|---|---:|---:|",
        f"| Koordinate/Adresse | {result['universal_repair_totals']['COORDINATE']} | {result['selected_model_counts']['COORDINATE']} |",
        f"| Arbeitsanweisung | {result['universal_repair_totals']['INSTRUCTION']} | {result['selected_model_counts']['INSTRUCTION']} |",
        f"| Katalogqualifikation | {result['universal_repair_totals']['CATALOGUE']} | {result['selected_model_counts']['CATALOGUE']} |",
        f"| sichtbares Mischmodell | {result['mixed_selected_repair_total']} | 146 |",
        "",
        "## Die neunzehn Wortstämme in den drei Grammatiken",
        "",
        "| Stamm | Arbeitswert | als Adresse | als Anweisung | als Katalogfeld |",
        "|---|---|---|---|---|",
    ]
    for row in root_rows:
        lines.append(
            f"| `{row['root']}` | {markdown_escape(row['working_value_de'])} | {markdown_escape(row['coordinate_recast_de'])} | {markdown_escape(row['instruction_recast_de'])} | {markdown_escape(row['catalogue_recast_de'])} |"
        )
    lines.append("")
    for page, rows in by_page.items():
        lines.extend([f"## {page}", ""])
        for row in rows:
            lines.extend([
                f"### {row['locus']} — `{str(row['surface_sequence']).replace('|', ' · ')}`",
                "",
                f"Wörtlich: {row['literal_working_reading_de']}",
                "",
                f"- Adresse ({row['coordinate_repair_count']}): {row['coordinate_bundle_reading_de']}",
                f"- Anweisung ({row['instruction_repair_count']}): {row['instruction_bundle_reading_de']}",
                f"- Katalog ({row['catalogue_repair_count']}): {row['catalogue_bundle_reading_de']}",
                f"- **Arbeitswahl {row['selected_model']}**: {row['selected_bundle_reading_de']}",
                "",
            ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    g416 = load_module("gdt474_g416", G416_PATH)
    edition = read_tsv(EDITION)
    core_rows_source = read_tsv(CORES)
    component_values = {row["atom"]: row["working_value_de"] for row in read_tsv(COMPONENTS)}
    if len(edition) != 183 or len(core_rows_source) != 19:
        raise RuntimeError("Input deck size drift")
    if set(ROOT_RECAST) != {row["root"] for row in core_rows_source}:
        raise RuntimeError("Nineteen-root recast deck drift")
    observed_atoms = {atom for row in edition for atom in atoms(row)}
    if not observed_atoms <= set(component_values):
        raise RuntimeError(f"Unknown edition atoms: {sorted(observed_atoms - set(component_values))}")

    root_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(core_rows_source, start=1):
        coordinate, instruction, catalogue = ROOT_RECAST[row["root"]]
        root_rows.append({
            "root_ordinal": ordinal,
            "root": row["root"],
            "structural_category": row["structural_category"],
            "working_value_de": row["selected_minimal_value_de"],
            "coordinate_recast_de": coordinate,
            "instruction_recast_de": instruction,
            "catalogue_recast_de": catalogue,
            "coordinate_nominalization_cost": int(row["root"] in ACTION_ROOTS),
            "instruction_direct_cost": 0,
            "catalogue_nominalization_cost": int(row["root"] in ACTION_ROOTS),
            "semantic_change": "NO__GRAMMATICAL_RECAST_ONLY",
        })

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in edition:
        grouped.setdefault((row["physical_page"], row["locus"], row["owner_de"]), []).append(row)

    bundle_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    selected_counts: Counter[str] = Counter()
    choice_patterns: Counter[str] = Counter()
    universal_totals: Counter[str] = Counter()
    mixed_total = 0

    for bundle_ordinal, ((page, locus, owner), rows) in enumerate(grouped.items(), start=1):
        coordinate_clauses = [coordinate_event(row) for row in rows]
        catalogue_clauses = [catalogue_event(row) for row in rows]
        instruction_clauses: list[str] = []
        active_action = ""
        active_argument = ""
        for row in rows:
            clause, active_action, active_argument = instruction_event(row, g416, active_action, active_argument)
            instruction_clauses.append(clause)
        scores = {
            "COORDINATE": coordinate_cost(rows),
            "INSTRUCTION": instruction_cost(rows),
            "CATALOGUE": catalogue_cost(rows),
        }
        universal_totals.update(scores)
        best, selected, reason = choose_model(scores, rows)
        mixed_total += scores[selected]
        selected_counts[selected] += 1
        pattern = "|".join(best)
        choice_patterns[pattern] += 1
        readings = {
            "COORDINATE": join_clauses(coordinate_clauses),
            "INSTRUCTION": join_clauses(instruction_clauses),
            "CATALOGUE": join_clauses(catalogue_clauses),
        }
        bundle_id = f"G474-B{bundle_ordinal:03d}"
        bundle_rows.append({
            "bundle_id": bundle_id,
            "bundle_ordinal": bundle_ordinal,
            "physical_page": page,
            "register": rows[0]["register"],
            "locus": locus,
            "owner_de": owner,
            "event_count": len(rows),
            "source_event_ids": "|".join(row["source_event_id"] for row in rows),
            "surface_sequence": "|".join(row["surface"] for row in rows),
            "recipe_sequence": " / ".join(row["working_recipe"] for row in rows),
            "literal_working_reading_de": " / ".join(row["working_reading_de"] for row in rows),
            "learned_name_event_count": sum(bool(names(row["working_reading_de"])) for row in rows),
            "explicit_action_root_count": sum(atom in ACTION_ROOTS for row in rows for atom in atoms(row)),
            "coordinate_repair_count": scores["COORDINATE"],
            "instruction_repair_count": scores["INSTRUCTION"],
            "catalogue_repair_count": scores["CATALOGUE"],
            "best_models": pattern,
            "selected_model": selected,
            "selection_reason": reason,
            "coordinate_bundle_reading_de": readings["COORDINATE"],
            "instruction_bundle_reading_de": readings["INSTRUCTION"],
            "catalogue_bundle_reading_de": readings["CATALOGUE"],
            "selected_bundle_reading_de": readings[selected],
            "claim_status": "EXPLORATORY_GRAMMATICAL_RECAST__ROOTS_AND_NAMES_UNCHANGED",
        })
        for event_index, (row, coordinate, instruction, catalogue) in enumerate(zip(rows, coordinate_clauses, instruction_clauses, catalogue_clauses), start=1):
            event_rows.append({
                "triptych_event_id": f"G474-E{int(row['edition_ordinal']):03d}",
                "bundle_id": bundle_id,
                "event_ordinal_in_bundle": event_index,
                "source_event_id": row["source_event_id"],
                "physical_page": page,
                "register": row["register"],
                "locus": locus,
                "surface": row["surface"],
                "working_recipe": row["working_recipe"],
                "literal_working_reading_de": row["working_reading_de"],
                "coordinate_event_reading_de": coordinate,
                "instruction_event_reading_de": instruction,
                "catalogue_event_reading_de": catalogue,
                "bundle_selected_model": selected,
                "selected_event_reading_de": {"COORDINATE": coordinate, "INSTRUCTION": instruction, "CATALOGUE": catalogue}[selected],
                "component_meaning_change": "NO",
                "learned_name_change": "NO",
            })

    page_rows: list[dict[str, object]] = []
    page_order = list(dict.fromkeys(str(row["physical_page"]) for row in bundle_rows))
    for page in page_order:
        selected = [row for row in bundle_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "bundle_count": len(selected),
            "event_count": sum(int(row["event_count"]) for row in selected),
            "multi_event_bundle_count": sum(int(row["event_count"]) > 1 for row in selected),
            "coordinate_selected_count": sum(row["selected_model"] == "COORDINATE" for row in selected),
            "instruction_selected_count": sum(row["selected_model"] == "INSTRUCTION" for row in selected),
            "catalogue_selected_count": sum(row["selected_model"] == "CATALOGUE" for row in selected),
            "coordinate_repair_total": sum(int(row["coordinate_repair_count"]) for row in selected),
            "instruction_repair_total": sum(int(row["instruction_repair_count"]) for row in selected),
            "catalogue_repair_total": sum(int(row["catalogue_repair_count"]) for row in selected),
            "mixed_selected_repair_total": sum(int(row[f"{str(row['selected_model']).lower()}_repair_count"]) for row in selected),
        })

    pattern_rows: list[dict[str, object]] = []
    for rank, (pattern, count) in enumerate(sorted(choice_patterns.items(), key=lambda item: (-item[1], item[0])), start=1):
        selected = [row for row in bundle_rows if row["best_models"] == pattern]
        pattern_rows.append({
            "pattern_rank": rank,
            "best_models": pattern,
            "bundle_count": count,
            "event_count": sum(int(row["event_count"]) for row in selected),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in selected})),
            "selected_model_counts": "|".join(f"{model}:{sum(row['selected_model'] == model for row in selected)}" for model in ("COORDINATE", "INSTRUCTION", "CATALOGUE")),
        })

    size_counts = Counter(int(row["event_count"]) for row in bundle_rows)
    unique_wins = Counter(row["best_models"] for row in bundle_rows if "|" not in str(row["best_models"]))
    result = {
        "status": "MIXED_LOCUS_GRAMMAR_REQUIRES_FEWEST_WORKING_REPAIRS__COORDINATE_BEST_SINGLE_DEFAULT",
        "event_count": len(event_rows),
        "bundle_count": len(bundle_rows),
        "bundle_size_counts": {str(size): count for size, count in sorted(size_counts.items())},
        "multi_event_bundle_count": sum(size > 1 for size in (int(row["event_count"]) for row in bundle_rows)),
        "multi_event_bundle_event_count": sum(int(row["event_count"]) for row in bundle_rows if int(row["event_count"]) > 1),
        "universal_repair_totals": dict(universal_totals),
        "best_universal_model": min(universal_totals, key=universal_totals.get),
        "mixed_selected_repair_total": mixed_total,
        "selected_model_counts": dict(selected_counts),
        "unique_lowest_repair_counts": dict(unique_wins),
        "tied_bundle_count": sum("|" in str(row["best_models"]) for row in bundle_rows),
        "choice_pattern_count": len(choice_patterns),
        "root_recast_count": len(root_rows),
        "component_meaning_change_count": 0,
        "learned_name_change_count": 0,
        "new_page_count": 0,
        "interpretation": "ONE_UNIVERSAL_SENTENCE_TYPE_IS_TOO_RIGID__USE_VISIBLE_MIX_OF_ADDRESS_INSTRUCTION_AND_CATALOGUE",
    }

    write_tsv(EVENTS_OUT, event_rows)
    write_tsv(BUNDLES_OUT, bundle_rows)
    write_tsv(ROOTS_OUT, root_rows)
    write_tsv(PAGES_OUT, page_rows)
    write_tsv(PATTERNS_OUT, pattern_rows)
    READABLE_OUT.write_text(build_reading_book(bundle_rows, root_rows, result), encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
