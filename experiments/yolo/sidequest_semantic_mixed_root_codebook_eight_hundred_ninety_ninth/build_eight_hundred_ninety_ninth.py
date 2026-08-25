#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_cross_register_stem_unification_eight_hundred_ninety_eighth"
PREFIX = "EIGHT_HUNDRED_NINETY_NINTH"

VOCAB_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_231_UNIFIED_WORKSHOP_VOCABULARY.tsv"
MARK_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_437_UNIFIED_MARK_DECK.tsv"
UNIT_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_118_UNIFIED_UNIT_EDITION.tsv"
CARD_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_6_UNIFIED_JOB_CARDS.tsv"
CONDITION_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_73_PORTABLE_CONDITION_READINGS.tsv"
SURFACE_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_EIGHTH_8_EXACT_SURFACE_BRIDGES.tsv"

ROOTS = {
    "AIIN": ("MASS", "ARGUMENT", "CROSS_REGISTER_ABBREVIATION"),
    "AIN": ("PORTION", "ARGUMENT", "LEARNED_WORKSHOP_ROOT"),
    "AIR": ("LAUF", "PATH", "CROSS_REGISTER_ABBREVIATION"),
    "AL": ("ZIELSTELLE", "ADDRESS", "CROSS_REGISTER_ABBREVIATION"),
    "AN": ("NACHGABE", "ARGUMENT", "LEARNED_WORKSHOP_ROOT"),
    "AR": ("QUELLE", "ADDRESS", "CROSS_REGISTER_ABBREVIATION"),
    "CH": ("ENTNEHMEN", "OPERATION", "CROSS_REGISTER_ABBREVIATION"),
    "CHD": ("UMSETZEN", "OPERATION", "CROSS_REGISTER_ABBREVIATION"),
    "CHK": ("WAERMEN", "OPERATION", "LEARNED_WORKSHOP_ROOT"),
    "CKH": ("DURCHLASS", "PATH", "CROSS_REGISTER_ABBREVIATION"),
    "CTH": ("BEREIT", "STATE", "CROSS_REGISTER_ABBREVIATION"),
    "DA": ("ZWEITE", "GRADE", "LEARNED_WORKSHOP_ROOT"),
    "DY": ("SCHLIESSEN", "ENDPOINT", "CROSS_REGISTER_ABBREVIATION"),
    "E": ("KURZ", "GRADE", "CROSS_REGISTER_ABBREVIATION"),
    "EE": ("LANG", "GRADE", "CROSS_REGISTER_ABBREVIATION"),
    "EEE": ("VOLLSTAENDIG", "GRADE", "LEARNED_WORKSHOP_ROOT"),
    "HO": ("TEIL", "MATERIAL", "CROSS_REGISTER_ABBREVIATION"),
    "IIN": ("STUFE", "STATE", "LEARNED_WORKSHOP_ROOT"),
    "K": ("ZUGEBEN", "OPERATION", "CROSS_REGISTER_ABBREVIATION"),
    "L": ("LEITEN", "PATH", "LEARNED_WORKSHOP_ROOT"),
    "LD": ("FESTBINDEN", "OPERATION", "LEARNED_WORKSHOP_ROOT"),
    "LSH": ("SPUELEN", "OPERATION", "LEARNED_WORKSHOP_ROOT"),
    "O": ("ARBEITSGANG", "PROCESS", "CROSS_REGISTER_ABBREVIATION"),
    "OK": ("ANSETZEN", "OPERATION", "CROSS_REGISTER_ABBREVIATION"),
    "OL": ("FORTSETZEN", "ORDER", "CROSS_REGISTER_ABBREVIATION"),
    "OR": ("ANSATZ", "MATERIAL", "CROSS_REGISTER_ABBREVIATION"),
    "OT": ("DANACH", "ORDER", "CROSS_REGISTER_ABBREVIATION"),
    "P": ("EINBRINGEN", "OPERATION", "LEARNED_WORKSHOP_ROOT"),
    "R": ("KUEHL", "STATE", "CROSS_REGISTER_ABBREVIATION"),
    "S": ("PROBE", "OPERATION", "LEARNED_WORKSHOP_ROOT"),
    "SH": ("HALTEN", "STATE", "CROSS_REGISTER_ABBREVIATION"),
    "SHED": ("RUHEN", "STATE", "LEARNED_WORKSHOP_ROOT"),
    "SOLK": ("SAMMELN", "OPERATION", "LEARNED_WORKSHOP_ROOT"),
    "T": ("BEARBEITEN", "OPERATION", "CROSS_REGISTER_ABBREVIATION"),
    "TALAM": ("BEISEITESTELLEN", "WHOLE_ROOT", "LEARNED_WORKSHOP_ROOT"),
    "Y": ("POSTEN", "REFERENT", "CROSS_REGISTER_ABBREVIATION"),
}

LOCAL_ROOTS = {
    "A_ADDR": "STELLE",
    "AM_ADDR": "GEGENFELD",
    "D_ADDR": "TEILSTELLE",
    "D_LABEL": "PHASE",
    "S_ADDR": "STERNBEZUG",
    "S_LABEL": "PHASENZEICHEN",
    "CHEO": "AUSZUG",
    "WHOLE[cheey|shey]": "LANG HALTEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def recipe_tokens(recipe: str) -> list[str]:
    if recipe in {"NONE", "WHOLE[cheey|shey]"}:
        return [recipe]
    return recipe.split("+")


def compose(recipe: str) -> str:
    values = []
    for token in recipe_tokens(recipe):
        if token in ROOTS:
            values.append(ROOTS[token][0])
        elif token in LOCAL_ROOTS:
            values.append(LOCAL_ROOTS[token])
        else:
            raise AssertionError(f"unmapped component: {token}")
    return " · ".join(values)


def main() -> None:
    vocabulary = read(VOCAB_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)
    conditions = read(CONDITION_SOURCE)
    surface_bridges = read(SURFACE_SOURCE)
    surface_roots = {row["surface"]: row["portable_root_de"] for row in surface_bridges}

    root_counts: dict[tuple[str, str], int] = Counter()
    root_examples: dict[str, list[str]] = defaultdict(list)
    for row in marks:
        register = "CONDITION" if row["master_section"] == "WHEN" else "PROSE"
        for token in recipe_tokens(row["component_recipe"]):
            if token in ROOTS:
                root_counts[(token, register)] += 1
                if len(root_examples[token]) < 5:
                    root_examples[token].append(row["surface"])
    root_rows = []
    for root, (meaning, role, root_class) in ROOTS.items():
        root_rows.append({
            "root": root,
            "atomic_value_de": meaning,
            "role": role,
            "root_class": root_class,
            "prose_marks": root_counts[(root, "PROSE")],
            "condition_marks": root_counts[(root, "CONDITION")],
            "total_marks": root_counts[(root, "PROSE")] + root_counts[(root, "CONDITION")],
            "surface_examples": " | ".join(root_examples[root]),
            "teaching_rule": f"SPRICH {root} ALS {meaning}; KOMBINIEREN IN SICHTBARER REIHENFOLGE",
        })

    taught_vocab = [row for row in vocabulary if row["apprentice_action"] == "READ_TAUGHT_WHOLE_WORD"]
    decomposition_rows = []
    selected_by_identity: dict[str, tuple[str, str]] = {}
    for row in taught_vocab:
        if row["house_surface"] in surface_roots:
            selected = surface_roots[row["house_surface"]]
            status = "FUSED_CROSS_REGISTER_WHOLE_FORM"
            action = "READ_FUSED_WHOLE_WORD"
        elif row["component_recipe"] == "TALAM":
            selected = ROOTS["TALAM"][0]
            status = "LEARNED_WHOLE_ROOT"
            action = "READ_LEARNED_WHOLE_ROOT"
        else:
            selected = compose(row["component_recipe"])
            status = "PREDICTED_ROOT_COMPOSITION"
            action = "READ_ROOT_COMPOSITION"
        selected_by_identity[row["identity"]] = (selected, action)
        decomposition_rows.append({
            "identity": row["identity"],
            "surface": row["house_surface"],
            "component_recipe": row["component_recipe"],
            "root_sequence_de": compose(row["component_recipe"]),
            "selected_short_value_de": selected,
            "local_fluent_expansion_de": row["short_value_de"],
            "marks": row["marks"],
            "orders": row["orders"],
            "composition_status": status,
            "apprentice_action": action,
        })

    portable_conditions = []
    condition_values: dict[str, str] = {}
    for row in conditions:
        recipe = row["component_parse"]
        if row["surface"] in surface_roots:
            selected = surface_roots[row["surface"]]
            source = "FUSED_CROSS_REGISTER_WHOLE_FORM"
        elif recipe == "NONE":
            selected = row["portable_workshop_reading_de"]
            source = "LOCAL_WHOLE_WORD"
        else:
            selected = compose(recipe)
            source = "MIXED_ROOT_COMPOSITION"
        condition_values[row["opaque_local_id"]] = selected
        portable_conditions.append({
            **row,
            "mixed_codebook_reading_de": selected,
            "mixed_codebook_source": source,
            "root_revision": "R=KUEHL" if "R" in recipe_tokens(recipe) else "NONE",
        })

    revised_marks = []
    for row in marks:
        if row["identity"] in selected_by_identity:
            value, action = selected_by_identity[row["identity"]]
            lesson = "TAUGHT_CARD_REANALYSED"
        elif row["source_id"] in condition_values:
            value = condition_values[row["source_id"]]
            action = row["apprentice_action"]
            lesson = "CONDITION_ROOT_SEQUENCE_UPDATED" if value != row["concrete_default_de"] else "NO_CHANGE"
        else:
            value = row["concrete_default_de"]
            action = row["apprentice_action"]
            lesson = "NO_CHANGE"
        revised_marks.append({
            **row,
            "concrete_default_de": value,
            "apprentice_action": action,
            "tenth_lesson": lesson,
            "pre_compression_local_expansion_de": row["concrete_default_de"],
        })

    identity_values: dict[str, set[str]] = defaultdict(set)
    identity_actions: dict[str, set[str]] = defaultdict(set)
    identity_expansions: dict[str, set[str]] = defaultdict(set)
    for row in revised_marks:
        identity_values[row["identity"]].add(row["concrete_default_de"])
        identity_actions[row["identity"]].add(row["apprentice_action"])
        identity_expansions[row["identity"]].add(row["pre_compression_local_expansion_de"])
    assert all(len(values) == 1 for values in identity_values.values())
    assert all(len(values) == 1 for values in identity_actions.values())
    revised_vocab = []
    for row in vocabulary:
        revised_vocab.append({
            **row,
            "short_value_de": next(iter(identity_values[row["identity"]])),
            "apprentice_action": next(iter(identity_actions[row["identity"]])),
            "tenth_lesson": "TAUGHT_CARD_REANALYSED" if row["identity"] in selected_by_identity else "NO_CHANGE",
            "local_fluent_expansions_de": " | ".join(sorted(identity_expansions[row["identity"]])),
        })

    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        revised_units.append({
            **unit,
            "literal_sequence_de": "; ".join(str(row["concrete_default_de"]) for row in local),
            "speakable_condition_sequence_de": " -> ".join(str(row["concrete_default_de"]) for row in local) if unit["section"] == "WHEN" else "NONE",
            "root_composed_marks": sum(row["apprentice_action"] == "READ_ROOT_COMPOSITION" for row in local),
            "fused_whole_form_marks": sum(row["apprentice_action"] == "READ_FUSED_WHOLE_WORD" for row in local),
            "learned_whole_root_marks": sum(row["apprentice_action"] == "READ_LEARNED_WHOLE_ROOT" for row in local),
        })

    revised_cards = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        revised_cards.append({
            **card,
            "root_composed_marks": sum(int(row["root_composed_marks"]) for row in local),
            "fused_whole_form_marks": sum(int(row["fused_whole_form_marks"]) for row in local),
            "learned_whole_root_marks": sum(int(row["learned_whole_root_marks"]) for row in local),
            "mixed_codebook_readable": "YES",
        })

    write(f"{PREFIX}_36_MIXED_ROOT_CODEBOOK.tsv", root_rows, list(root_rows[0]))
    write(f"{PREFIX}_105_TAUGHT_CARD_DECOMPOSITIONS.tsv", decomposition_rows, list(decomposition_rows[0]))
    write(f"{PREFIX}_73_MIXED_CODEBOOK_CONDITIONS.tsv", portable_conditions, list(portable_conditions[0]))
    write(f"{PREFIX}_231_MIXED_CODEBOOK_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["tenth_lesson", "local_fluent_expansions_de"])
    write(f"{PREFIX}_437_MIXED_CODEBOOK_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["tenth_lesson", "pre_compression_local_expansion_de"])
    write(f"{PREFIX}_118_MIXED_CODEBOOK_UNITS.tsv", revised_units, list(units[0]) + ["root_composed_marks", "fused_whole_form_marks", "learned_whole_root_marks"])
    write(f"{PREFIX}_6_MIXED_CODEBOOK_JOB_CARDS.tsv", revised_cards, list(revised_cards[0]))

    lines = [
        "# Gemischtes Wurzel-Codebuch der Werkstatt",
        "",
        "Das System besteht nun aus 22 registerübergreifenden Fachkürzeln, 14 zusätzlich gelernten Werkstattwurzeln, vier verschmolzenen Ganzformen und einer echten Ganzwurzel.",
        "Die Wurzeln werden in sichtbarer Reihenfolge gelesen; die ältere flüssige Kartenbedeutung bleibt als Werkstattexpansion daneben stehen.",
        "",
        "## Die 36 Wurzeln",
        "",
    ]
    for row in root_rows:
        lines.append(f"- `{row['root']}` = **{row['atomic_value_de']}** ({row['role']}; {row['root_class']})")
    lines.extend(["", "## Ausgewählte neu vorhersagbare Karten", ""])
    for row in decomposition_rows[:40]:
        lines.append(f"- `{row['surface']}` = {row['root_sequence_de']} → **{row['local_fluent_expansion_de']}**")
    lines.extend(["", "## Die sechs vollständigen Aufträge", ""])
    for card in revised_cards:
        lines.append(f"- **{card['order_id']}**: {card['root_composed_marks']} zusammengesetzte, {card['fused_whole_form_marks']} verschmolzene, {card['learned_whole_root_marks']} Ganzwurzel-Marken.")
    (HERE / f"{PREFIX}_MIXED_CODEBOOK_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    action_counts = Counter(row["apprentice_action"] for row in revised_marks)
    decomposition_counts = Counter(row["composition_status"] for row in decomposition_rows)
    summary = {
        "status": "PASS",
        "decision": "ONE_HUNDRED_FIVE_TAUGHT_IDENTITIES_REDUCE_TO_ONE_HUNDRED_ROOT_COMPOSITIONS_FOUR_FUSED_WHOLE_FORMS_AND_ONE_WHOLE_ROOT",
        "roots": len(root_rows),
        "cross_register_roots": sum(row["root_class"] == "CROSS_REGISTER_ABBREVIATION" for row in root_rows),
        "learned_workshop_roots": sum(row["root_class"] == "LEARNED_WORKSHOP_ROOT" for row in root_rows),
        "reanalyzed_identities": len(decomposition_rows),
        "reanalyzed_marks": sum(int(row["marks"]) for row in decomposition_rows),
        "decomposition_statuses": dict(decomposition_counts),
        "mark_actions": dict(action_counts),
        "condition_R_repairs": sum(row["root_revision"] == "R=KUEHL" for row in portable_conditions),
        "vocabulary_identities": len(revised_vocab),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 899: gemischtes Wurzel-Codebuch\n\n"
        "Die 105 zuvor einzeln gelernten Kartenidentitäten werden mit 36 kurzen Wurzeln neu gelesen. "
        "100 sind reguläre Kompositionen, vier bleiben verschmolzene registerübergreifende Ganzformen und TALAM bleibt die eine echte Ganzwurzel BEISEITESTELLEN. "
        "Damit entsteht genau die gesuchte Mischung aus produktiven Fachkürzeln und wenigen gelernten Ganzen. R wird von BEZUG zu KUEHL korrigiert.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
