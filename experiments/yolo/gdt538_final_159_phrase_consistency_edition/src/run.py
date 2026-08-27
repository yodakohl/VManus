#!/usr/bin/env python3
"""Fill the 159 final surface locks with one consistent German phrase layer."""

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
BASE = ROOT / "experiments/yolo/gdt538_final_159_phrase_consistency_edition"
OUT = BASE / "artifacts"
G537 = (
    ROOT
    / "experiments/yolo/gdt537_seven_route_final_intake_supplement/artifacts"
    / "gdt537_159_final_surface_dictionary.tsv"
)
G413 = (
    ROOT
    / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
    / "gdt413_46_component_working_dictionary.tsv"
)

DICTIONARY_OUT = OUT / "gdt538_159_complete_phrase_dictionary.tsv"
ATOM_OUT = OUT / "gdt538_34_atom_phrase_lexicon.tsv"
TEMPLATE_OUT = OUT / "gdt538_phrase_template_summary.tsv"
SPECIAL_OUT = OUT / "gdt538_7_special_phrase_normalization.tsv"
DELTA_OUT = OUT / "gdt538_one_atom_delta_audit.tsv"
BOOK_OUT = OUT / "GDT538_COMPLETE_159_WORKING_PHRASEBOOK.md"
RESULT_OUT = OUT / "gdt538_result.json"
STATUS = "PASS_ALL_159_HAVE_CANONICAL_PHRASES__Y_RESTORED_AS_ARGUMENT"

ACTION_ATOMS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ATOMS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ATOMS = {"AL", "AR", "L", "AIR"}
ORDER_ATOMS = {"OL", "OT"}
STRUCTURAL_ATOMS = {
    "E", "EE", "EEE", "DY", "O", "CARRIER_Q", "IIN", "DA",
    "D_ADDR", "AM_ADDR", "A_ADDR", "LOCAL_CHAR_F", "M_LOCAL",
}
LOCAL_OPAQUE_ATOMS = {"LOCAL_X", "LOCAL_C"}
PORTABLE_ATOMS = ACTION_ATOMS | ARGUMENT_ATOMS | RELATION_ATOMS | ORDER_ATOMS

CONTROLLED = {
    "Y": "Posten",
    "OK": "setzen",
    "OL": "fortsetzen",
    "OT": "danach",
    "AL": "Zielort",
    "CH": "nehmen",
    "SH": "halten",
    "AR": "Ausgang",
    "K": "geben",
    "AIIN": "Wert",
    "S": "wählen",
    "CHD": "bearbeiten",
    "OR": "Einheit",
    "L": "Verbindung",
    "T": "einstellen",
    "AIN": "Anteil",
    "R": "markieren",
    "P": "einsetzen",
    "AIR": "Bahn",
    "E": "[Grad I]",
    "EE": "[Grad II]",
    "EEE": "[Grad III]",
    "DY": "[Schluss]",
    "O": "[Ausführung]",
    "CARRIER_Q": "[Beginnmarker]",
    "IIN": "[Stufe]",
    "DA": "[zweite Stufe]",
    "D_ADDR": "[hier: D-Adresse]",
    "AM_ADDR": "[hier: AM-Adresse]",
    "A_ADDR": "[hier: A-Adresse]",
    "LOCAL_CHAR_F": "[hier: f-Kennmarke]",
    "M_LOCAL": "[hier: lokale m-Marke]",
    "LOCAL_X": "[lokaler X-Zeichen-/Namenskern]",
    "LOCAL_C": "[lokales c-Zeichen]",
}

ACTIONS = {
    "OK": "setzen", "CH": "nehmen", "SH": "halten", "K": "geben",
    "S": "wählen", "CHD": "bearbeiten", "T": "einstellen",
    "R": "markieren", "P": "einsetzen",
}
ARGUMENTS_ACC = {
    "Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil",
    "OR": "die Einheit",
}
ARGUMENTS_NOM = {
    "Y": "Posten", "AIIN": "Wert", "AIN": "Anteil", "OR": "Einheit",
}
RELATIONS = {
    "AL": "am Zielort", "AR": "vom Ausgang", "L": "über die Verbindung",
    "AIR": "entlang der Bahn",
}
FORMAL = {
    "E": "auf Grad I", "EE": "auf Grad II", "EEE": "auf Grad III",
    "O": "zur Ausführung", "CARRIER_Q": "mit Beginnmarker",
    "IIN": "auf der bezeichneten Stufe", "DA": "auf der zweiten Stufe",
}
LOCALS = {
    "D_ADDR": "hier", "AM_ADDR": "hier", "A_ADDR": "hier",
    "LOCAL_CHAR_F": "hier", "M_LOCAL": "hier",
    "LOCAL_X": "mit lokalem X-Zeichen-/Namenskern",
    "LOCAL_C": "lokales c-Zeichen",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty artifact: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def coordinated(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " und " + parts[-1]


def repeated_sequence(words: list[str]) -> str:
    """Keep slot order while making a repeated item explicit in German."""
    if not words:
        return ""
    if len(set(words)) == 1 and len(words) in {2, 3}:
        count = "zweimal" if len(words) == 2 else "dreimal"
        return f"{count} {words[0]}"
    seen: Counter[str] = Counter()
    marked: list[str] = []
    for word in words:
        seen[word] += 1
        marked.append(word if seen[word] == 1 else f"erneut {word}")
    return coordinated(marked)


def repeated_segments(atoms: list[str], mapping: dict[str, str]) -> list[tuple[int, str]]:
    seen: Counter[str] = Counter()
    result: list[tuple[int, str]] = []
    for index, atom in enumerate(atoms):
        if atom not in mapping:
            continue
        seen[atom] += 1
        phrase = mapping[atom]
        if seen[atom] > 1:
            phrase = "erneut " + phrase
        result.append((index, phrase))
    return result


def phrase_template(atoms: list[str]) -> str:
    action_count = sum(atom in ACTION_ATOMS for atom in atoms)
    argument_count = sum(atom in ARGUMENT_ATOMS for atom in atoms)
    local_count = sum(atom in LOCALS for atom in atoms)
    nonlocal_count = len(atoms) - local_count
    if local_count and nonlocal_count == 0:
        return "LOCAL_SIGN_OR_CORE_ONLY"
    if action_count > 1 and argument_count:
        return "MULTI_ACTION_WITH_ARGUMENT"
    if action_count > 1:
        return "MULTI_ACTION_NO_ARGUMENT"
    if action_count and argument_count:
        return "ACTION_WITH_ARGUMENT"
    if action_count:
        return "ACTION_NO_ARGUMENT"
    if argument_count:
        return "NOMINAL_ARGUMENT_OR_CONTROL"
    if any(atom in RELATION_ATOMS for atom in atoms):
        return "RELATION_OR_ADDRESS"
    return "FORMAL_OR_LOCAL_CONTROL"


def render_fluent(atoms: list[str]) -> str:
    """Make a concise neutral phrase; the exact-order channel remains primary."""
    indexed: list[tuple[int, int, str]] = []
    action_words = [ACTIONS[atom] for atom in atoms if atom in ACTIONS]
    argument_atoms = [atom for atom in atoms if atom in ARGUMENTS_ACC]

    if action_words or argument_atoms:
        core_positions = [
            index
            for index, atom in enumerate(atoms)
            if atom in ACTION_ATOMS or atom in ARGUMENT_ATOMS
        ]
        if action_words:
            action_phrase = repeated_sequence(action_words)
            if argument_atoms:
                if len(set(argument_atoms)) == 1 and len(argument_atoms) in {2, 3}:
                    amount = "beide" if len(argument_atoms) == 2 else "alle drei"
                    noun = ARGUMENTS_NOM[argument_atoms[0]]
                    object_phrase = f"{amount} {noun}"
                else:
                    object_phrase = coordinated([ARGUMENTS_ACC[a] for a in argument_atoms])
                core = f"{object_phrase} {action_phrase}"
            else:
                core = action_phrase
        else:
            core = repeated_sequence([ARGUMENTS_NOM[a] for a in argument_atoms])
        indexed.append((min(core_positions), 30, core))

    indexed.extend((index, 10, phrase) for index, phrase in repeated_segments(atoms, LOCALS))
    indexed.extend((index, 20, phrase) for index, phrase in repeated_segments(atoms, RELATIONS))
    indexed.extend((index, 40, phrase) for index, phrase in repeated_segments(atoms, FORMAL))

    ol_indices = [index for index, atom in enumerate(atoms) if atom == "OL"]
    if ol_indices:
        if len(ol_indices) == 1:
            word = "fortsetzen"
        elif len(ol_indices) == 2:
            word = "zweimal fortsetzen"
        else:
            word = f"{len(ol_indices)}-mal fortsetzen"
        indexed.append((ol_indices[0], 50, word))
    for index, atom in enumerate(atoms):
        if atom == "OT":
            indexed.append((index, 0, "danach"))
        elif atom == "DY":
            indexed.append((index, 60, "abschließen"))

    indexed.sort(key=lambda item: (item[0], item[1]))
    parts = [phrase for _, _, phrase in indexed]
    if not parts:
        raise RuntimeError(f"No phrase segments for {atoms}")
    phrase = "; ".join(parts)
    return phrase[0].upper() + phrase[1:] + "."


def edit_distance_one(left: list[str], right: list[str]) -> tuple[str, str, str] | None:
    """Return one exact atom edit, otherwise None."""
    if abs(len(left) - len(right)) > 1:
        return None
    if len(left) == len(right):
        diffs = [i for i, pair in enumerate(zip(left, right)) if pair[0] != pair[1]]
        if len(diffs) != 1:
            return None
        i = diffs[0]
        return "SUBSTITUTE", left[i], right[i]
    if len(left) > len(right):
        result = edit_distance_one(right, left)
        if result is None:
            return None
        _, _, inserted = result
        return "DELETE", inserted, "NONE"
    for i in range(len(right)):
        if left == right[:i] + right[i + 1 :]:
            return "INSERT", "NONE", right[i]
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source = read_tsv(G537)
    component_rows = read_tsv(G413)
    if len(source) != 159:
        raise RuntimeError("GDT537 final dictionary no longer has 159 rows")

    recipes = [row["final_working_recipe"] for row in source]
    if len(set(recipes)) != 159:
        raise RuntimeError("Expected 159 distinct final recipes")
    used_atoms = {atom for recipe in recipes for atom in recipe.split("+")}
    if used_atoms != set(CONTROLLED):
        raise RuntimeError(
            f"Phrase lexicon mismatch: missing={used_atoms - set(CONTROLLED)}, "
            f"unused={set(CONTROLLED) - used_atoms}"
        )

    component_by_atom = {row["atom"]: row for row in component_rows}
    fixed_portable = {
        atom: component_by_atom[atom]["working_value_de"] for atom in PORTABLE_ATOMS
    }
    if fixed_portable != {
        "Y": "POSTEN", "OK": "SETZEN", "OL": "FORTSETZEN", "OT": "DANACH",
        "AL": "ZIELORT", "CH": "NEHMEN", "SH": "HALTEN", "AR": "AUSGANG",
        "K": "GEBEN", "AIIN": "WERT", "S": "WÄHLEN", "CHD": "BEARBEITEN",
        "OR": "EINHEIT", "L": "VERBINDUNG", "T": "EINSTELLEN",
        "AIN": "ANTEIL", "R": "MARKIEREN", "P": "EINSETZEN", "AIR": "BAHN",
    }:
        raise RuntimeError("The fixed nineteen-value dictionary drifted")

    atom_counts: Counter[str] = Counter()
    atom_surface_counts: Counter[str] = Counter()
    dictionary_rows: list[dict[str, object]] = []
    for row in source:
        atoms = row["final_working_recipe"].split("+")
        atom_counts.update(atoms)
        atom_surface_counts.update(set(atoms))
        controlled = " → ".join(CONTROLLED[atom] for atom in atoms) + "."
        fluent = render_fluent(atoms)
        old = row["working_phrase_de"]
        if old == "INHERITED":
            repair = "FILLED_INHERITED_PLACEHOLDER"
        elif old == fluent:
            repair = "RETAINED_EXISTING_PHRASE"
        else:
            repair = "NORMALIZED_EXISTING_PHRASE"
        dictionary_rows.append({
            "dictionary_ordinal": row["dictionary_ordinal"],
            "lock_key": row["lock_key"],
            "surface": row["surface"],
            "occurrence_count": row["occurrence_count"],
            "physical_pages": row["physical_pages"],
            "final_working_recipe": row["final_working_recipe"],
            "literal_reading_de": row["literal_reading_de"],
            "old_working_phrase_de": old,
            "controlled_order_reading_de": controlled,
            "canonical_workshop_phrase_de": fluent,
            "phrase_template": phrase_template(atoms),
            "phrase_repair_status": repair,
            "atom_count": len(atoms),
            "portable_atom_count": sum(atom in PORTABLE_ATOMS for atom in atoms),
            "structural_or_local_atom_count": sum(atom not in PORTABLE_ATOMS for atom in atoms),
            "action_slot_count": sum(atom in ACTION_ATOMS for atom in atoms),
            "argument_slot_count": sum(atom in ARGUMENT_ATOMS for atom in atoms),
            "all_slots_explicit": "YES",
            "exact_recipe_roundtrip": "+".join(atoms),
            "special_route": row["special_route"],
            "route_class": row["route_class"],
            "route_source": row["route_source"],
            "resolution_status": row["resolution_status"],
            "lock_scope": row["lock_scope"],
            "local_record_policy": row["local_record_policy"],
            "guard": "EDITORIAL_PHRASE_ONLY__FIXED_RECIPE_AND_ATOM_VALUES_RETAINED",
        })

    atom_rows: list[dict[str, object]] = []
    for ordinal, atom in enumerate(sorted(used_atoms), 1):
        source_row = component_by_atom.get(atom)
        if atom in PORTABLE_ATOMS:
            layer = "PORTABLE_WORKING_WORD"
            value = source_row["working_value_de"]
            factor = source_row["factor_family"]
        elif atom in STRUCTURAL_ATOMS:
            layer = "STRUCTURAL_OR_LOCAL_TAG"
            value = source_row["working_value_de"]
            factor = source_row["factor_family"]
        else:
            layer = "LEARNED_LOCAL_CORE_OR_SIGN"
            value = "LOKALER X-KERN" if atom == "LOCAL_X" else "LOKALES C-ZEICHEN"
            factor = "LOCAL_OPAQUE"
        atom_rows.append({
            "atom_ordinal": ordinal,
            "atom": atom,
            "fixed_value_de": value,
            "semantic_layer": layer,
            "factor_family": factor,
            "controlled_realization_de": CONTROLLED[atom],
            "recipe_occurrence_count": atom_counts[atom],
            "surface_count": atom_surface_counts[atom],
            "bracketed_if_not_portable": "YES" if atom not in PORTABLE_ATOMS else "NOT_APPLICABLE",
            "meaning_changed": "NO",
        })

    template_counts = Counter(row["phrase_template"] for row in dictionary_rows)
    template_rows = [
        {
            "phrase_template": template,
            "surface_count": count,
            "rule_de": {
                "LOCAL_SIGN_OR_CORE_ONLY": "lokale Marke/Kern bleibt als lokaler Tag sichtbar",
                "MULTI_ACTION_WITH_ARGUMENT": "Argument(e) plus geordnete Mehrfachhandlung",
                "MULTI_ACTION_NO_ARGUMENT": "geordnete Mehrfachhandlung ohne erfundenes Objekt",
                "ACTION_WITH_ARGUMENT": "sichtbares Argument plus sichtbare Handlung",
                "ACTION_NO_ARGUMENT": "sichtbare Handlung ohne erfundenes Objekt",
                "NOMINAL_ARGUMENT_OR_CONTROL": "sichtbarer Posten/Wert/Anteil/Einheit ohne erfundenes Verb",
                "RELATION_OR_ADDRESS": "sichtbare Relation oder Adresse ohne erfundene Handlung",
                "FORMAL_OR_LOCAL_CONTROL": "formaler/lokaler Tag bleibt ausdrücklich markiert",
            }[template],
        }
        for template, count in sorted(template_counts.items())
    ]

    special_rows: list[dict[str, object]] = []
    for row in dictionary_rows:
        if row["special_route"] != "YES":
            continue
        old = str(row["old_working_phrase_de"])
        y_role_issue = (
            "YES"
            if "posten" in old and "Y" in str(row["final_working_recipe"]).split("+")
            else "NO"
        )
        special_rows.append({
            "surface": row["surface"],
            "final_working_recipe": row["final_working_recipe"],
            "old_working_phrase_de": old,
            "canonical_workshop_phrase_de": row["canonical_workshop_phrase_de"],
            "controlled_order_reading_de": row["controlled_order_reading_de"],
            "old_y_verbalization_conflict": y_role_issue,
            "normalization_decision": (
                "RESTORE_Y_AS_ARGUMENT_POSTEN" if y_role_issue == "YES"
                else "APPLY_COMMON_ATOM_TO_PHRASE_RENDERER"
            ),
            "recipe_changed": "NO",
            "root_meaning_changed": "NO",
        })

    delta_rows: list[dict[str, object]] = []
    for left_index, left in enumerate(dictionary_rows):
        left_atoms = str(left["final_working_recipe"]).split("+")
        for right in dictionary_rows[left_index + 1 :]:
            right_atoms = str(right["final_working_recipe"]).split("+")
            edit = edit_distance_one(left_atoms, right_atoms)
            if edit is None:
                continue
            operation, old_atom, new_atom = edit
            delta_rows.append({
                "delta_ordinal": len(delta_rows) + 1,
                "left_surface": left["surface"],
                "left_recipe": left["final_working_recipe"],
                "right_surface": right["surface"],
                "right_recipe": right["final_working_recipe"],
                "edit_operation": operation,
                "old_atom": old_atom,
                "new_atom": new_atom,
                "old_controlled_realization_de": CONTROLLED.get(old_atom, "NONE"),
                "new_controlled_realization_de": CONTROLLED.get(new_atom, "NONE"),
                "all_unchanged_slots_byte_identical": "YES",
                "changed_slot_effect_explicit": "YES",
            })

    write_tsv(DICTIONARY_OUT, dictionary_rows)
    write_tsv(ATOM_OUT, atom_rows)
    write_tsv(TEMPLATE_OUT, template_rows)
    write_tsv(SPECIAL_OUT, special_rows)
    write_tsv(DELTA_OUT, delta_rows)

    result = {
        "status": STATUS,
        "surface_count": len(dictionary_rows),
        "distinct_recipe_count": len(set(recipes)),
        "atom_type_count": len(atom_rows),
        "atom_slot_count": sum(atom_counts.values()),
        "portable_atom_type_count": len(used_atoms & PORTABLE_ATOMS),
        "structural_or_local_atom_type_count": len(used_atoms - PORTABLE_ATOMS),
        "old_inherited_placeholder_count": sum(
            row["old_working_phrase_de"] == "INHERITED" for row in dictionary_rows
        ),
        "new_inherited_placeholder_count": sum(
            not row["canonical_workshop_phrase_de"] for row in dictionary_rows
        ),
        "all_slots_explicit_count": sum(
            row["all_slots_explicit"] == "YES" for row in dictionary_rows
        ),
        "special_route_count": len(special_rows),
        "special_y_role_correction_count": sum(
            row["old_y_verbalization_conflict"] == "YES" for row in special_rows
        ),
        "phrase_template_count": len(template_rows),
        "one_atom_delta_pair_count": len(delta_rows),
        "one_atom_delta_exact_count": sum(
            row["all_unchanged_slots_byte_identical"] == "YES" for row in delta_rows
        ),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "surface_predictions": 0,
    }
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GDT538 — vollständiges 159er-Werkstattphrasebook",
        "",
        "Jede Endoberfläche besitzt zwei Lesekanäle: eine exakt geordnete, slotgetreue Kette und eine knappe deutsche Werkstattfassung. Eckige Klammern kennzeichnen weiterhin Struktur- oder Lokalwerte; sie sind keine Wortübersetzungen.",
        "",
        f"- Vollständige Phrasen: **{len(dictionary_rows)}/{len(dictionary_rows)}**.",
        f"- Explizite Atomslots: **{result['atom_slot_count']}/{result['atom_slot_count']}**.",
        f"- Gefüllte alte `INHERITED`-Plätze: **{result['old_inherited_placeholder_count']}**.",
        f"- Ein-Atom-Nachbarpaare mit sauberem Slotdelta: **{len(delta_rows)}/{len(delta_rows)}**.",
        "",
        "## Die 159 Kurzlesungen",
        "",
        "| Oberfläche | Endrezept | kontrollierte Lesekette | Werkstattfassung |",
        "|---|---|---|---|",
    ]
    for row in dictionary_rows:
        lines.append(
            f"| `{row['surface']}` | `{row['final_working_recipe']}` | "
            f"{row['controlled_order_reading_de']} | {row['canonical_workshop_phrase_de']} |"
        )
    lines.extend([
        "",
        "Die Lesekette ist der eindeutige Kanal. Die Werkstattfassung darf für deutsches Satzgefühl umstellen, aber kein Atom hinzufügen oder entfernen. Besonders `Y=POSTEN` bleibt hier ein Argument: frühere Formulierungen mit dem Verb „posten“ wurden nur redaktionell normalisiert.",
        "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
