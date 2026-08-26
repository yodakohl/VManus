#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = ROOT / "experiments/yolo/gdt412_chd_process_core_completion"
OUT = HERE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_715_statement_edition.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"
BASE_DICT = ROOT / "experiments/yolo/gdt411_provisional_core_process_position/artifacts/gdt411_final_19_core_dictionary.tsv"

ARGUMENT_OR_RELATION = {"Y", "AIIN", "AIN", "OR", "AL", "AR", "L", "AIR"}
REGISTERS = ("HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA", "SOURCE_SECTION_T")


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(recipe):
    atoms = recipe.split("+")
    if atoms == ["CHD", "Y"]:
        return "BARE_CHD_Y"
    if atoms[-1] == "DY":
        return "TERMINAL_DY"
    if any(atom in ARGUMENT_OR_RELATION for atom in atoms):
        return "OPEN_ARGUMENT_OR_RELATION"
    return "OTHER_OPEN"


def render(recipe, meanings):
    return " | ".join(" · ".join(meanings.get(atom, atom) for atom in card.split("+")) for card in recipe.split(" | "))


def replace_chd(recipe, value, meanings):
    local = dict(meanings)
    local["CHD"] = value
    return render(recipe, local)


def main():
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    atom_dictionary = read_tsv(ATOM_DICT)
    base_dictionary = read_tsv(BASE_DICT)
    statement_by_source = {row["source_statement_id"]: row for row in statements}

    final_dictionary = []
    for row in base_dictionary:
        updated = dict(row)
        if row["root"] == "CHD":
            updated["selected_minimal_value_de"] = "BEARBEITEN"
            updated["decision"] = "KEEP"
            updated["rival_a_de"] = "UMSETZEN"
            updated["rival_b_de"] = "ABSCHLIESSEN"
            updated["portable_use_rule_de"] = "als allgemeinen Arbeitsgang lesen; genaue Technik kommt von Hülle und Besitzer"
            updated["decision_reason_de"] = "207 offene gegen 94 terminale Vorkommen; CHD+Y allein 107-mal, daher Prozesskern statt Transfer- oder Schlusswort"
        final_dictionary.append(updated)

    meanings = {row["atom"]: row["locked_working_value_de"] for row in atom_dictionary}
    meanings.update({row["root"]: row["selected_minimal_value_de"] for row in final_dictionary})

    target_events = [row for row in events if "CHD" in row["component_recipe"].split("+")]
    occurrence_rows = []
    family_counts = Counter()
    family_surfaces = defaultdict(Counter)
    family_pages = defaultdict(Counter)
    family_registers = defaultdict(Counter)
    register_family = defaultdict(Counter)
    for row in target_events:
        family = classify(row["component_recipe"])
        statement = statement_by_source[row["source_statement_id"]]
        family_counts[row["component_recipe"]] += 1
        family_surfaces[row["component_recipe"]][row["surface"]] += 1
        family_pages[row["component_recipe"]][row["physical_page"]] += 1
        family_registers[row["component_recipe"]][row["register"]] += 1
        register_family[row["register"]][family] += 1
        occurrence_rows.append({
            "global_running_event_id": row["global_running_event_id"],
            "global_running_ordinal": row["global_running_ordinal"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "global_statement_id": statement["global_statement_id"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "family_class": family,
            "selected_event_reading_de": replace_chd(row["component_recipe"], "BEARBEITEN", meanings),
            "umsetzen_rival_reading_de": replace_chd(row["component_recipe"], "UMSETZEN", meanings),
            "abschliessen_rival_reading_de": replace_chd(row["component_recipe"], "ABSCHLIESSEN", meanings),
            "statement_end_mode": statement["end_mode"],
        })

    family_rows = []
    for recipe, count in sorted(family_counts.items(), key=lambda item: (-item[1], item[0])):
        family_rows.append({
            "component_recipe": recipe,
            "event_count": count,
            "family_class": classify(recipe),
            "surface_counts": "|".join(f"{surface}:{n}" for surface, n in family_surfaces[recipe].most_common()),
            "page_count": len(family_pages[recipe]),
            "pages": "|".join(sorted(family_pages[recipe])),
            "register_count": len(family_registers[recipe]),
            "register_counts": "|".join(f"{register}:{n}" for register, n in family_registers[recipe].most_common()),
            "selected_atomic_reading_de": replace_chd(recipe, "BEARBEITEN", meanings),
        })

    matrix_rows = []
    classes = ("BARE_CHD_Y", "TERMINAL_DY", "OPEN_ARGUMENT_OR_RELATION", "OTHER_OPEN")
    for register in REGISTERS:
        for family in classes:
            matrix_rows.append({
                "register": register,
                "family_class": family,
                "event_count": register_family[register][family],
                "register_total_chd_events": sum(register_family[register].values()),
            })

    score_rows = [
        {"candidate_value_de": "BEARBEITEN", "bare_chd_y_fit_0_3": 3, "open_complement_fit_0_3": 3, "terminal_wrapper_fit_0_3": 3, "cross_register_fit_0_3": 3, "total_0_12": 12, "selected": "YES", "reason_de": "CHD+Y heißt knapp Posten bearbeiten; Hüllen spezifizieren Richtung, Grad oder Schluss."},
        {"candidate_value_de": "UMSETZEN", "bare_chd_y_fit_0_3": 2, "open_complement_fit_0_3": 3, "terminal_wrapper_fit_0_3": 3, "cross_register_fit_0_3": 2, "total_0_12": 10, "selected": "NO", "reason_de": "Passt zu Transferhüllen, ist für 107 nackte CHD+Y und Mengenkomplemente zu eng."},
        {"candidate_value_de": "ABSCHLIESSEN", "bare_chd_y_fit_0_3": 1, "open_complement_fit_0_3": 1, "terminal_wrapper_fit_0_3": 3, "cross_register_fit_0_3": 2, "total_0_12": 7, "selected": "NO", "reason_de": "94 terminale Fälle passen, 207 offene und 46 erste Handlungsvorkommen widersprechen."},
    ]

    context_rows = []
    for register in REGISTERS:
        for family in classes:
            candidates = [row for row in target_events if row["register"] == register and classify(row["component_recipe"]) == family]
            if not candidates:
                continue
            chosen = min(candidates, key=lambda row: (int(statement_by_source[row["source_statement_id"]]["event_count"]), int(row["global_running_ordinal"])))
            statement = statement_by_source[chosen["source_statement_id"]]
            context_rows.append({
                "register": register,
                "family_class": family,
                "global_statement_id": statement["global_statement_id"],
                "physical_page": chosen["physical_page"],
                "owner_de": chosen["owner_de"],
                "target_surface": chosen["surface"],
                "target_recipe": chosen["component_recipe"],
                "statement_surface_sequence": statement["surface_sequence"],
                "statement_recipe_sequence": statement["recipe_sequence"],
                "selected_full_statement_reading_de": render(statement["recipe_sequence"], meanings),
                "local_expansion_rule": "BEARBEITEN bleibt Kern; Richtung, Material, Körperteil oder Himmelswert kommt aus Hülle/Besitzer",
            })

    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "occurrences": OUT / "gdt412_301_chd_occurrence_comparison.tsv",
        "families": OUT / "gdt412_78_chd_recipe_families.tsv",
        "matrix": OUT / "gdt412_20_register_family_matrix.tsv",
        "scores": OUT / "gdt412_candidate_scorecard.tsv",
        "contexts": OUT / "gdt412_cross_register_family_contexts.tsv",
        "dictionary": OUT / "gdt412_final_19_core_dictionary.tsv",
    }
    write_tsv(paths["occurrences"], occurrence_rows, list(occurrence_rows[0]))
    write_tsv(paths["families"], family_rows, list(family_rows[0]))
    write_tsv(paths["matrix"], matrix_rows, list(matrix_rows[0]))
    write_tsv(paths["scores"], score_rows, list(score_rows[0]))
    write_tsv(paths["contexts"], context_rows, list(context_rows[0]))
    write_tsv(paths["dictionary"], final_dictionary, list(final_dictionary[0]))

    class_counts = Counter(row["family_class"] for row in occurrence_rows)
    result = {
        "status": "NINETEEN_BROAD_WORKING_VALUES_COMPLETE__CHD_IS_PROCESS_NOT_CLOSE",
        "chd_event_count": len(target_events),
        "chd_recipe_family_count": len(family_rows),
        "family_class_counts": dict(sorted(class_counts.items())),
        "open_event_count": len(target_events) - class_counts["TERMINAL_DY"],
        "terminal_event_count": class_counts["TERMINAL_DY"],
        "selected_chd_value_de": "BEARBEITEN",
        "final_decision_counts": dict(sorted(Counter(row["decision"] for row in final_dictionary).items())),
        "context_count": len(context_rows),
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (EVENTS, STATEMENTS, ATOM_DICT, BASE_DICT)},
        "output_sha256": {name: sha256(path) for name, path in paths.items()},
    }
    (OUT / "gdt412_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
