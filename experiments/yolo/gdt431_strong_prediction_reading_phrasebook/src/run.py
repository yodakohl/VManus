#!/usr/bin/env python3
"""Turn GDT430's 47 dense missing recipes into a usable reading phrasebook."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook"
OUT = BASE / "artifacts"
PREDICTIONS = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_293_absent_multi_neighbor_predictions.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
REGISTER_ATLAS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_95_register_expansion_atlas.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
ACTION_ROOTS = {"CH", "S", "K", "OK", "P", "SH", "CHD", "T", "R"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}
ORDER_ROOTS = {"OL", "OT"}
GRADE_ROOTS = {"E", "EE", "EEE", "IIN", "DA"}
LOCAL_ROOTS = {
    "D_ADDR", "AM_ADDR", "A_ADDR", "S_ADDR", "LOCAL_CHAR_F", "D_LABEL", "S_LABEL",
    "M_LOCAL", "Z_ADDR", "G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B",
    "LOCAL_CHAR_J", "LOCAL_CHAR_Z", "HO", "AN", "OS", "RESUME_CARD",
}

GENERIC_OBJECTS = {"Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit"}
REGISTER_OBJECTS = {
    "SOURCE_SECTION_T": {"Y": "den laufenden Eintrag", "AIIN": "den Kennwert", "AIN": "den Teilwert", "OR": "die Eintragseinheit"},
    "HERBAL": {"Y": "den Pflanzenposten", "AIIN": "den Arbeitswert", "AIN": "den Materialanteil", "OR": "die Arbeitseinheit"},
    "BIOLOGICAL": {"Y": "den Stationsposten", "AIIN": "den Stationswert", "AIN": "den Stationsanteil", "OR": "die Stationseinheit"},
    "CELESTIAL": {"Y": "den Positionsposten", "AIIN": "den Positionswert", "AIN": "den Sektoranteil", "OR": "die Positionseinheit"},
    "PHARMA": {"Y": "den Drogenposten", "AIIN": "den Mengenwert", "AIN": "den Drogenanteil", "OR": "die Ansatzeinheit"},
}

GENITIVES = {
    "GENERIC": {"Y": "des Postens", "AIIN": "des Werts", "AIN": "des Anteils", "OR": "der Einheit"},
    "SOURCE_SECTION_T": {"Y": "des laufenden Eintrags", "AIIN": "des Kennwerts", "AIN": "des Teilwerts", "OR": "der Eintragseinheit"},
    "HERBAL": {"Y": "des Pflanzenpostens", "AIIN": "des Arbeitswerts", "AIN": "des Materialanteils", "OR": "der Arbeitseinheit"},
    "BIOLOGICAL": {"Y": "des Stationspostens", "AIIN": "des Stationswerts", "AIN": "des Stationsanteils", "OR": "der Stationseinheit"},
    "CELESTIAL": {"Y": "des Positionspostens", "AIIN": "des Positionswerts", "AIN": "des Sektoranteils", "OR": "der Positionseinheit"},
    "PHARMA": {"Y": "des Drogenpostens", "AIIN": "des Mengenwerts", "AIN": "des Drogenanteils", "OR": "der Ansatzeinheit"},
}

GENERIC_RELATIONS = {"AL": "am Zielort", "AR": "vom Ausgang", "L": "über die Verbindung", "AIR": "entlang der Bahn"}
REGISTER_RELATIONS = {
    "SOURCE_SECTION_T": {"AL": "an der Zielspalte", "AR": "von der Ausgangszeile", "L": "über die Eintragsverbindung", "AIR": "entlang der Lesebahn"},
    "HERBAL": {"AL": "an der Zielstelle", "AR": "vom Ausgangsmaterial", "L": "über die Verbindung im Pflanzenartikel", "AIR": "entlang der Verarbeitungsbahn"},
    "BIOLOGICAL": {"AL": "an der Zielstation", "AR": "von der Ausgangsstation", "L": "über die sichtbare Verbindung", "AIR": "entlang der Stationsbahn"},
    "CELESTIAL": {"AL": "an der Zielposition", "AR": "von der Ausgangsposition", "L": "über die Ringverbindung", "AIR": "entlang der Ringbahn"},
    "PHARMA": {"AL": "am Zielgefäß", "AR": "vom Ausgangsgefäß", "L": "über die Gefäßverbindung", "AIR": "entlang der Transferbahn"},
}

ACTION_TEMPLATES = {
    "SOURCE_SECTION_T": {"CH": "Entnimm {obj}", "S": "Wähle {obj}", "K": "Ordne {obj} zu", "OK": "Trage {obj} ein", "P": "Setze {obj} in den Eintrag ein", "SH": "Halte {obj} fest", "CHD": "Bearbeite {obj}", "T": "Lege {obj} fest", "R": "Kennzeichne {obj}"},
    "GENERIC": {"CH": "Nimm {obj}", "S": "Wähle {obj}", "K": "Gib {obj}", "OK": "Setze {obj}", "P": "Setze {obj} ein", "SH": "Halte {obj}", "CHD": "Bearbeite {obj}", "T": "Stelle {obj} ein", "R": "Markiere {obj}"},
    "HERBAL": {"CH": "Nimm {obj}", "S": "Wähle {obj}", "K": "Gib {obj} zu", "OK": "Setze {obj} im Arbeitsgang an", "P": "Setze {obj} ein", "SH": "Halte {obj}", "CHD": "Bearbeite {obj}", "T": "Stelle {obj} ein", "R": "Markiere {obj}"},
    "BIOLOGICAL": {"CH": "Entnimm {obj}", "S": "Wähle {obj}", "K": "Führe {obj} zu", "OK": "Setze {obj} im Stationsgang an", "P": "Setze {obj} ein", "SH": "Halte {obj}", "CHD": "Bearbeite {obj}", "T": "Stelle {obj} ein", "R": "Markiere {obj}"},
    "CELESTIAL": {"CH": "Nimm {obj} auf", "S": "Wähle {obj}", "K": "Ordne {obj} zu", "OK": "Setze {obj}", "P": "Setze {obj} ein", "SH": "Halte {obj}", "CHD": "Bearbeite {obj}", "T": "Stelle {obj} ein", "R": "Markiere {obj}"},
    "PHARMA": {"CH": "Nimm {obj}", "S": "Wähle {obj}", "K": "Gib {obj} zu", "OK": "Setze {obj} als Ansatz an", "P": "Setze {obj} ein", "SH": "Halte {obj}", "CHD": "Bearbeite {obj}", "T": "Stelle {obj} ein", "R": "Markiere {obj}"},
}

GRADE_PHRASES = {"E": "auf Grad I", "EE": "auf Grad II", "EEE": "auf Grad III", "IIN": "auf der bezeichneten Stufe", "DA": "auf der zweiten Stufe"}
ORDER_PHRASES = {"OL": "Weiter", "OT": "Danach"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def strip_article(noun: str) -> str:
    for article in ("den ", "die ", "das "):
        if noun.startswith(article):
            return noun[len(article):]
    return noun


def coordinated(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " und " + parts[-1]


def recipe_template(atoms: list[str]) -> str:
    actions = [atom for atom in atoms if atom in ACTION_ROOTS]
    arguments = [atom for atom in atoms if atom in ARGUMENT_ROOTS]
    relations = [atom for atom in atoms if atom in RELATION_ROOTS]
    orders = [atom for atom in atoms if atom in ORDER_ROOTS]
    grades = [atom for atom in atoms if atom in GRADE_ROOTS]
    if len(actions) > 1:
        return "MULTI_ACTION"
    if actions and orders:
        return "ORDERED_ACTION"
    if actions and arguments and relations:
        return "ACTION_ARGUMENT_RELATION"
    if actions and grades:
        return "GRADED_ACTION"
    if actions and relations:
        return "ACTION_RELATION"
    if actions and arguments:
        return "ACTION_ARGUMENT"
    if actions:
        return "ACTION_ONLY"
    if arguments and relations:
        return "REFERENCE_ARGUMENT_RELATION"
    if len(arguments) > 1:
        return "NESTED_ARGUMENT"
    if orders:
        return "ORDERED_REFERENCE"
    if "O" in atoms:
        return "EXECUTION_REFERENCE"
    return "REFERENCE_ONLY"


def render_action(register: str, action: str, object_phrase: str, relation_phrase: str) -> str:
    obj = object_phrase.strip()
    rel = relation_phrase.strip()
    middle = " ".join(part for part in (obj, rel) if part)
    if action == "P":
        if register == "SOURCE_SECTION_T":
            return " ".join(part for part in ("Setze", middle, "in den Eintrag ein") if part)
        return " ".join(part for part in ("Setze", middle, "ein") if part)
    if action == "T":
        return " ".join(part for part in (("Lege" if register == "SOURCE_SECTION_T" else "Stelle"), middle, ("fest" if register == "SOURCE_SECTION_T" else "ein")) if part)
    if register == "SOURCE_SECTION_T" and action == "K":
        return " ".join(part for part in ("Ordne", middle, "zu") if part)
    if action == "K" and register in {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}:
        heads = {"HERBAL": "Gib", "BIOLOGICAL": "Führe", "CELESTIAL": "Ordne", "PHARMA": "Gib"}
        return " ".join(part for part in (heads[register], middle, "zu") if part)
    if register == "SOURCE_SECTION_T" and action == "OK":
        return " ".join(part for part in ("Trage", middle, "ein") if part)
    if register == "SOURCE_SECTION_T" and action == "SH":
        return " ".join(part for part in ("Halte", middle, "fest") if part)
    if register == "CELESTIAL" and action == "CH":
        return " ".join(part for part in ("Nimm", middle, "auf") if part)
    if action == "OK" and register in {"HERBAL", "BIOLOGICAL", "PHARMA"}:
        tails = {"HERBAL": "im Arbeitsgang an", "BIOLOGICAL": "im Stationsgang an", "PHARMA": "als Ansatz an"}
        return " ".join(part for part in ("Setze", middle, tails[register]) if part)
    clause = ACTION_TEMPLATES[register][action].format(obj=obj).replace("  ", " ").strip()
    return " ".join(part for part in (clause, rel) if part)


def render_recipe(atoms: list[str], register: str = "GENERIC") -> str:
    objects = GENERIC_OBJECTS if register == "GENERIC" else REGISTER_OBJECTS[register]
    relations_table = GENERIC_RELATIONS if register == "GENERIC" else REGISTER_RELATIONS[register]
    action_table = ACTION_TEMPLATES[register]
    genitives = GENITIVES[register]
    actions = [atom for atom in atoms if atom in ACTION_ROOTS]
    arguments = [atom for atom in atoms if atom in ARGUMENT_ROOTS]
    relations = [relations_table[atom] for atom in atoms if atom in RELATION_ROOTS]
    grades = [GRADE_PHRASES[atom] for atom in atoms if atom in GRADE_ROOTS]
    orders = [ORDER_PHRASES[atom] for atom in atoms if atom in ORDER_ROOTS]
    locals_ = [atom for atom in atoms if atom in LOCAL_ROOTS]
    object_phrase = coordinated([objects[atom] for atom in arguments])
    relation_phrase = coordinated(relations)
    grade_phrase = coordinated(grades)

    segments: list[str] = []
    if not actions and "CARRIER_Q" in atoms and "O" in atoms and arguments:
        if len(arguments) == 1:
            segments.append("Beginne mit der Ausführung " + genitives[arguments[0]])
        else:
            segments.append("Beginne mit der bezeichneten Ausführung")
    elif actions:
        for index, action in enumerate(actions):
            segments.append(render_action(register, action, object_phrase, relation_phrase if index == len(actions) - 1 else ""))
    elif "O" in atoms and arguments:
        segments.append("Führe " + object_phrase + " aus")
        if relation_phrase:
            segments[-1] += " " + relation_phrase
    elif arguments and relations:
        noun = coordinated([strip_article(objects[atom]) for atom in arguments])
        first_argument = min(atoms.index(atom) for atom in arguments)
        first_relation = min(atoms.index(atom) for atom in atoms if atom in RELATION_ROOTS)
        if first_relation < first_argument:
            segments.append((relation_phrase[0].upper() + relation_phrase[1:]) + ": " + noun)
        else:
            segments.append(noun + " " + relation_phrase)
    elif len(arguments) == 2:
        if "Y" in arguments:
            other = next(atom for atom in arguments if atom != "Y")
            segments.append(strip_article(objects[other]) + " " + genitives["Y"])
        else:
            segments.append(strip_article(objects[arguments[0]]) + " " + genitives[arguments[1]])
    elif arguments:
        segments.append(strip_article(objects[arguments[0]]))
    elif relation_phrase:
        segments.append(relation_phrase[0].upper() + relation_phrase[1:])

    if grade_phrase:
        if segments:
            segments[-1] += " " + grade_phrase
        else:
            segments.append(grade_phrase[0].upper() + grade_phrase[1:])
    if "O" in atoms and actions:
        segments[-1] += " als Ausführung"
    if locals_:
        local_phrases = []
        for atom in locals_:
            if atom in {"OS", "RESUME_CARD"}:
                local_phrases.append("wie zuvor")
            elif atom in {"HO", "AN"}:
                local_phrases.append("in der bezeichneten Klasse")
            elif atom.startswith("G_") or atom.startswith("LOCAL_CHAR_"):
                local_phrases.append("mit der lokalen Variante")
            else:
                local_phrases.append("hier")
        if segments:
            segments[-1] += " " + coordinated(local_phrases)
        else:
            local_text = coordinated(local_phrases)
            segments.append(local_text[0].upper() + local_text[1:])
    if "CARRIER_Q" in atoms and not (not actions and "O" in atoms and arguments):
        if segments:
            segments[0] = "Beginne: " + segments[0][0].lower() + segments[0][1:]
        else:
            segments.append("Beginne den bezeichneten Gang")
    if "DY" in atoms:
        segments.append("Schließe den Schritt")
    if not segments:
        segments.append("Führe die bezeichnete Karte aus")
    normalized_segments = [segments[0]] + [segment[0].lower() + segment[1:] for segment in segments[1:]]
    phrase = "; ".join(normalized_segments)
    if orders:
        phrase = coordinated(orders) + ": " + phrase
    return phrase[0].upper() + phrase[1:] + "."


def literal(recipe: str, meanings: dict[str, str]) -> str:
    return " · ".join(meanings[atom] for atom in recipe.split("+"))


def changed_position(source: str, target: str) -> tuple[int, str, str]:
    source_atoms = source.split("+")
    target_atoms = target.split("+")
    differences = [(index + 1, left, right) for index, (left, right) in enumerate(zip(source_atoms, target_atoms)) if left != right]
    if len(source_atoms) != len(target_atoms) or len(differences) != 1:
        raise ValueError(f"Not a one-root neighbor: {source} -> {target}")
    return differences[0]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    predictions = [row for row in read_tsv(PREDICTIONS) if row["prediction_rank"] in {"AMBER_HIGH_PRIORITY", "AMBER_STRONG"}]
    components = read_tsv(COMPONENTS)
    clauses = read_tsv(CLAUSES)
    atlas = read_tsv(REGISTER_ATLAS)
    meanings = {row["atom"]: row["working_value_de"] for row in components}
    categories = {row["atom"]: row["factor_family"] for row in components}
    atlas_map = {(row["root"], row["register"]): row["owner_local_expansion_de"] for row in atlas}

    observed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        observed[row["component_recipe"]].append(row)

    card_rows: list[dict[str, object]] = []
    register_rows: list[dict[str, object]] = []
    neighbor_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(predictions, 1):
        recipe = row["candidate_recipe"]
        atoms = recipe.split("+")
        generic_phrase = render_recipe(atoms)
        source_recipes = row["source_recipes"].split(" | ")
        card_rows.append({
            "card_ordinal": ordinal,
            "prediction_rank": row["prediction_rank"],
            "candidate_recipe": recipe,
            "fixed_literal_reading_de": row["fixed_reading_de"],
            "short_workshop_phrase_de": generic_phrase,
            "template": recipe_template(atoms),
            "action_roots": "|".join(atom for atom in atoms if atom in ACTION_ROOTS) or "NONE",
            "argument_roots": "|".join(atom for atom in atoms if atom in ARGUMENT_ROOTS) or "NONE",
            "relation_roots": "|".join(atom for atom in atoms if atom in RELATION_ROOTS) or "NONE",
            "order_grade_control_roots": "|".join(atom for atom in atoms if atom not in ACTION_ROOTS | ARGUMENT_ROOTS | RELATION_ROOTS) or "NONE",
            "atom_categories": " | ".join(categories[atom] for atom in atoms),
            "source_neighbor_count": row["source_neighbor_count"],
            "source_recipes": row["source_recipes"],
            "minimum_root_pair_shared_frame_support": row["minimum_root_pair_shared_frame_support"],
            "source_page_count": row["source_page_count"],
            "source_pages": row["source_pages"],
            "source_register_count": row["source_register_count"],
            "surface_rule": row["surface_rule"],
            "meaning_status": "COMPOSITION_OF_FIXED_COMPONENT_VALUES",
        })
        for register in REGISTERS:
            local_atoms = [atlas_map.get((atom, register), meanings[atom]) for atom in atoms]
            register_rows.append({
                "card_ordinal": ordinal,
                "candidate_recipe": recipe,
                "register": register,
                "portable_literal_de": row["fixed_reading_de"],
                "owner_local_atom_expansion_de": " · ".join(local_atoms),
                "owner_local_workshop_phrase_de": render_recipe(atoms, register),
                "source_neighbor_count": row["source_neighbor_count"],
                "surface_rule": row["surface_rule"],
                "expansion_status": "LOCAL_NOUNS_AND_VERBS_ONLY__NO_ROOT_MEANING_CHANGE",
            })
        for source in source_recipes:
            position, source_atom, target_atom = changed_position(source, recipe)
            source_rows = observed[source]
            if not source_rows:
                raise ValueError(f"Missing observed source recipe: {source}")
            first = sorted(source_rows, key=lambda item: item["global_running_event_id"])[0]
            neighbor_rows.append({
                "card_ordinal": ordinal,
                "candidate_recipe": recipe,
                "candidate_phrase_de": generic_phrase,
                "source_neighbor_recipe": source,
                "source_neighbor_literal_de": literal(source, meanings),
                "changed_atom_position": position,
                "source_atom": source_atom,
                "predicted_atom": target_atom,
                "one_root_change": f"{source_atom}>{target_atom}@{position}",
                "source_event_count": len(source_rows),
                "source_statement_count": len({item["global_statement_id"] for item in source_rows}),
                "source_page_count": len({item["physical_page"] for item in source_rows}),
                "source_pages": "|".join(sorted({item["physical_page"] for item in source_rows})),
                "source_registers": "|".join(sorted({item["register"] for item in source_rows})),
                "sample_surface": first["surface"],
                "sample_existing_imperative_de": first["imperative_clause_de"],
                "neighbor_status": "OBSERVED_ONE_ROOT_SOURCE",
            })

    write_tsv(OUT / "gdt431_47_strong_prediction_phrasebook.tsv", card_rows, list(card_rows[0]))
    write_tsv(OUT / "gdt431_235_register_expansion_cards.tsv", register_rows, list(register_rows[0]))
    write_tsv(OUT / "gdt431_145_neighbor_exemplars.tsv", neighbor_rows, list(neighbor_rows[0]))

    markdown = [
        "# 47 lesbare Zukunftskarten", "",
        "Diese Karten sagen keine Voynich-Oberflächen voraus. Sie legen nur fest, wie eine später sichtbar passend segmentierte Komposition gelesen wird.", "",
        "Die fette Phrase ist eine kurze Werkstattparaphrase des ganzen Komponentenrezepts; sie ist **keine** neue Einwortbedeutung.", "",
    ]
    for card in card_rows:
        markdown += [
            f"## {card['card_ordinal']}. `{card['candidate_recipe']}`", "",
            f"- Wörtlich: `{card['fixed_literal_reading_de']}`",
            f"- Werkstatt: **{card['short_workshop_phrase_de']}**",
            f"- Nachbarn ({card['source_neighbor_count']}): `{card['source_recipes']}`",
            "",
        ]
    (OUT / "FORTY_SEVEN_FUTURE_READING_CARDS.md").write_text("\n".join(markdown), encoding="utf-8")

    template_counts = Counter(str(row["template"]) for row in card_rows)
    generic_phrase_counts = Counter(str(row["short_workshop_phrase_de"]) for row in card_rows)
    register_phrase_counts = Counter((str(row["register"]), str(row["owner_local_workshop_phrase_de"])) for row in register_rows)
    result = {
        "status": "FORTY_SEVEN_STRONG_PREDICTIONS_HAVE_FIXED_READABLE_PHRASES",
        "prediction_card_count": len(card_rows),
        "high_priority_count": sum(row["prediction_rank"] == "AMBER_HIGH_PRIORITY" for row in card_rows),
        "strong_count": sum(row["prediction_rank"] == "AMBER_STRONG" for row in card_rows),
        "register_expansion_count": len(register_rows),
        "neighbor_exemplar_count": len(neighbor_rows),
        "register_count": len(REGISTERS),
        "template_counts": dict(sorted(template_counts.items())),
        "generic_phrase_collision_count": sum(count - 1 for count in generic_phrase_counts.values() if count > 1),
        "within_register_phrase_collision_count": sum(count - 1 for count in register_phrase_counts.values() if count > 1),
        "surface_predictions": 0,
        "new_component_values": 0,
        "new_pages": 0,
    }
    (OUT / "gdt431_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
