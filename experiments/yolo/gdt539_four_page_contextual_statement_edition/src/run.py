#!/usr/bin/env python3
"""Compile the four admitted pages into contextual statements and local cards."""

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
BASE = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition"
OUT = BASE / "artifacts"
G516 = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
G538 = ROOT / "experiments/yolo/gdt538_final_159_phrase_consistency_edition/artifacts"

EVENTS_IN = G516 / "gdt516_597_contextualized_event_edition.tsv"
STATEMENTS_IN = G515 / "gdt515_prose_statement_edition.tsv"
PHRASES_IN = G538 / "gdt538_159_complete_phrase_dictionary.tsv"
ATOMS_IN = G538 / "gdt538_34_atom_phrase_lexicon.tsv"

PROSE_OUT = OUT / "gdt539_546_contextual_prose_events.tsv"
STATEMENT_OUT = OUT / "gdt539_78_contextual_statements.tsv"
LOCAL_OUT = OUT / "gdt539_51_local_role_retention.tsv"
ROLE_OUT = OUT / "gdt539_159_surface_role_scopes.tsv"
LOCAL_DEFAULT_OUT = OUT / "gdt539_14_local_surface_defaults.tsv"
ELLIPSIS_OUT = OUT / "gdt539_ellipsis_summary.tsv"
PAGE_OUT = OUT / "gdt539_4_page_summary.tsv"
BOOK_OUT = OUT / "GDT539_FOUR_PAGE_CONTEXTUAL_WORKING_EDITION.md"
RESULT_OUT = OUT / "gdt539_result.json"
STATUS = "PASS_78_STATEMENTS_COMPLETE__145_PROSE_AND_14_LOCAL_SURFACES_SEPARATED"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}
ORDER_ROOTS = {"OL", "OT"}

VERBS = {
    "SOURCE_SECTION_T": {
        "OK": "trage {obj} ein", "CH": "entnimm {obj}", "SH": "halte {obj} fest",
        "K": "ordne {obj} zu", "S": "wähle {obj}", "CHD": "bearbeite {obj}",
        "T": "lege {obj} fest", "R": "kennzeichne {obj}", "P": "setze {obj} ein",
    },
    "HERBAL": {
        "OK": "setze {obj} im Arbeitsgang an", "CH": "nimm {obj}",
        "SH": "halte {obj}", "K": "gib {obj} zu", "S": "wähle {obj}",
        "CHD": "bearbeite {obj}", "T": "stelle {obj} ein",
        "R": "markiere {obj}", "P": "setze {obj} ein",
    },
}
NOUNS = {
    "SOURCE_SECTION_T": {
        "Y": "den laufenden Eintrag", "AIIN": "den Kennwert",
        "AIN": "den Teilwert", "OR": "die Eintragseinheit",
    },
    "HERBAL": {
        "Y": "den Pflanzenposten", "AIIN": "den Arbeitswert",
        "AIN": "den Materialanteil", "OR": "die Arbeitseinheit",
    },
}
RELATIONS = {
    "SOURCE_SECTION_T": {
        "AL": "zur Zielspalte", "AR": "von der Ausgangszeile",
        "L": "über die Eintragsverbindung", "AIR": "entlang der Lesebahn",
    },
    "HERBAL": {
        "AL": "zur Zielstelle", "AR": "vom Ausgangsmaterial",
        "L": "über die Verbindung im Pflanzenartikel",
        "AIR": "entlang der Verarbeitungsbahn",
    },
}
MODIFIERS = {
    "E": "auf Grad I", "EE": "auf Grad II", "EEE": "auf Grad III",
    "IIN": "auf der bezeichneten Stufe", "DA": "auf der zweiten Stufe",
    "O": "zur Ausführung", "CARRIER_Q": "mit Beginnmarker",
}
LOCAL_PHRASES = {
    "D_ADDR": "an der bezeichneten Stelle",
    "AM_ADDR": "an der bezeichneten Stelle",
    "A_ADDR": "an der bezeichneten Stelle",
    "S_ADDR": "an der bezeichneten Stelle",
    "LOCAL_CHAR_F": "an der bezeichneten Stelle",
    "M_LOCAL": "an der bezeichneten Stelle",
    "HO": "in der bezeichneten Klasse",
    "LOCAL_CHAR_I": "mit der lokalen Variante i",
    "LOCAL_CHAR_G": "mit der lokalen Variante g",
    "LOCAL_X": "mit dem lokalen X-Zeichen-/Namenskern",
    "LOCAL_C": "am lokalen c-Zeichen",
    "LOCAL_NAME_CORE_D": "mit dem lokalen Namenkern d",
}
EXTRA_CONTROLLED = {
    "HO": "[Klasse]",
    "LOCAL_CHAR_I": "[lokale Variante i]",
    "S_ADDR": "[hier: S-Adresse]",
    "LOCAL_CHAR_G": "[lokale Variante g]",
    "LOCAL_NAME_CORE_D": "[lokaler Namenkern d]",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
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


def scoped(atoms: list[str], mapping: dict[str, str]) -> list[str]:
    totals = Counter(atom for atom in atoms if atom in mapping)
    seen: Counter[str] = Counter()
    phrases: list[str] = []
    for atom in atoms:
        if atom not in mapping:
            continue
        seen[atom] += 1
        phrase = mapping[atom]
        if totals[atom] > 1:
            suffix = "[außen]" if seen[atom] == 1 else "[innen]" if seen[atom] == 2 else f"[Stufe {seen[atom]}]"
            phrase = f"{phrase} {suffix}"
        phrases.append(phrase)
    return phrases


def contextual_clause(
    register: str,
    atoms: list[str],
    explicit_actions: list[str],
    inherited_action: str,
    explicit_arguments: list[str],
    inherited_argument: str,
) -> str:
    arguments = scoped(atoms, NOUNS[register])
    if not arguments and inherited_argument:
        arguments = [NOUNS[register][inherited_argument] + " [wie zuvor]"]
    object_phrase = coordinated(arguments)
    actions = [
        " ".join(VERBS[register][atom].format(obj=object_phrase).split())
        for atom in explicit_actions
    ]
    if not actions and inherited_action:
        actions = [
            "im laufenden Satz "
            + " ".join(VERBS[register][inherited_action].format(obj=object_phrase).split())
        ]

    segments: list[str] = []
    if actions:
        segments.append(coordinated(actions))
    elif arguments:
        segments.append("Bezug: " + object_phrase)

    relations = scoped(atoms, RELATIONS[register])
    if relations:
        segments.append(coordinated(relations))
    modifiers = scoped(atoms, MODIFIERS)
    if modifiers:
        segments.append(coordinated(modifiers))
    local_parts = scoped(atoms, LOCAL_PHRASES)
    if local_parts:
        segments.append(coordinated(local_parts))
    if "OL" in atoms:
        count = atoms.count("OL")
        segments.append("führe fort" if count == 1 else f"führe {count}-mal fort")
    if "DY" in atoms:
        segments.append("schließe den Schritt")

    if not segments:
        segments.append("lokale Kontrollangabe")
    clause = "; ".join(segments)
    if "OT" in atoms:
        clause = "danach: " + clause
    return clause[0].upper() + clause[1:] + "."


def ellipsis_status(inherited_action: str, inherited_argument: str) -> str:
    if inherited_action and inherited_argument:
        return "INHERITED_ACTION_AND_ARGUMENT"
    if inherited_action:
        return "INHERITED_ACTION_ONLY"
    if inherited_argument:
        return "INHERITED_ARGUMENT_ONLY"
    return "NO_INHERITANCE"


def local_phrase(role: str, controlled: str) -> str:
    label = {
        "MARGINAL_LABEL_CARD": "Randkennung",
        "MARGINAL_SIGN_CARD": "Lokales Randzeichen",
        "LATE_ADDITION_CARD": "Später Zusatz",
    }.get(role, "Lokale Karte")
    return f"{label}: {controlled}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS_IN)
    statements = read_tsv(STATEMENTS_IN)
    phrase_rows = read_tsv(PHRASES_IN)
    atom_rows = read_tsv(ATOMS_IN)
    if (len(events), len(statements), len(phrase_rows), len(atom_rows)) != (597, 78, 159, 34):
        raise RuntimeError("Input count drift")

    final_by_surface = {row["surface"]: row for row in phrase_rows}
    controlled = {row["atom"]: row["controlled_realization_de"] for row in atom_rows}
    controlled.update(EXTRA_CONTROLLED)

    prose_source = [row for row in events if row["statement_id"] != "NONE"]
    local_source = [row for row in events if row["statement_id"] == "NONE"]
    if (len(prose_source), len(local_source)) != (546, 51):
        raise RuntimeError("GDT516 prose/local split drift")
    target_prose = [row for row in prose_source if row["surface"] in final_by_surface]
    target_local = [row for row in local_source if row["surface"] in final_by_surface]
    if (len(target_prose), len(target_local)) != (149, 19):
        raise RuntimeError("GDT538 occurrence role split drift")

    prose_surfaces = {row["surface"] for row in target_prose}
    local_surfaces = {row["surface"] for row in target_local}
    if len(prose_surfaces) != 145 or len(local_surfaces) != 14 or prose_surfaces & local_surfaces:
        raise RuntimeError("Expected disjoint 145 prose / 14 local surface partition")
    if prose_surfaces | local_surfaces != set(final_by_surface):
        raise RuntimeError("Role partition does not cover all final surfaces")

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in prose_source:
        events_by_statement[event["statement_id"]].append(event)
    for material in events_by_statement.values():
        material.sort(key=lambda row: int(row["card_ordinal_in_statement"]))

    prose_rows: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []
    inherited_action_counts: Counter[str] = Counter()
    inherited_argument_counts: Counter[str] = Counter()
    for statement in statements:
        statement_id = statement["statement_id"]
        material = events_by_statement[statement_id]
        if len(material) != int(statement["event_count"]):
            raise RuntimeError(f"Statement event mismatch: {statement_id}")
        active_action = ""
        active_action_source = ""
        active_argument = ""
        active_argument_source = ""
        clauses: list[str] = []
        final_recipes: list[str] = []
        controlled_chains: list[str] = []
        statement_event_ids: list[str] = []
        target_count = 0
        recipe_change_count = 0
        statement_inherited_action_count = 0
        statement_inherited_argument_count = 0
        for event in material:
            target = final_by_surface.get(event["surface"])
            recipe = target["final_working_recipe"] if target else event["gdt516_context_recipe"]
            atoms = recipe.split("+")
            unknown = [atom for atom in atoms if atom not in controlled]
            if unknown:
                raise RuntimeError(f"Unmapped atoms in {event['event_id']}: {unknown}")
            explicit_actions = [atom for atom in atoms if atom in ACTION_ROOTS]
            explicit_arguments = [atom for atom in atoms if atom in ARGUMENT_ROOTS]
            inherited_action = ""
            inherited_action_source = ""
            if explicit_actions:
                active_action = explicit_actions[-1]
                active_action_source = event["event_id"]
            elif active_action and atoms != ["DY"]:
                inherited_action = active_action
                inherited_action_source = active_action_source
                inherited_action_counts[active_action] += 1
                statement_inherited_action_count += 1
            inherited_argument = ""
            inherited_argument_source = ""
            if explicit_arguments:
                active_argument = explicit_arguments[-1]
                active_argument_source = event["event_id"]
            elif active_argument and (explicit_actions or inherited_action) and atoms != ["DY"]:
                inherited_argument = active_argument
                inherited_argument_source = active_argument_source
                inherited_argument_counts[active_argument] += 1
                statement_inherited_argument_count += 1

            chain = " → ".join(controlled[atom] for atom in atoms) + "."
            clause = contextual_clause(
                statement["register"], atoms, explicit_actions, inherited_action,
                explicit_arguments, inherited_argument,
            )
            target_count += bool(target)
            changed = recipe != event["gdt516_context_recipe"]
            recipe_change_count += changed
            final_recipes.append(recipe)
            controlled_chains.append(chain)
            clauses.append(clause)
            statement_event_ids.append(event["event_id"])
            prose_rows.append({
                "context_event_ordinal": len(prose_rows) + 1,
                "event_id": event["event_id"],
                "statement_id": statement_id,
                "card_ordinal_in_statement": event["card_ordinal_in_statement"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "owner_id": event["owner_id"],
                "owner_de": event["owner_de"],
                "locus": event["locus"],
                "surface": event["surface"],
                "content_role": event["content_role"],
                "gdt516_context_recipe": event["gdt516_context_recipe"],
                "final_context_recipe": recipe,
                "recipe_source": "GDT538_FINAL_SURFACE" if target else "GDT516_CONTEXT_REPLAY",
                "recipe_changed_after_gdt516": "YES" if changed else "NO",
                "controlled_order_reading_de": chain,
                "gdt538_neutral_phrase_de": target["canonical_workshop_phrase_de"] if target else "NOT_IN_GDT538_159",
                "explicit_action_roots": "|".join(explicit_actions) or "NONE",
                "inherited_action_root": inherited_action or "NONE",
                "inherited_action_source_event_id": inherited_action_source or "NONE",
                "explicit_argument_roots": "|".join(explicit_arguments) or "NONE",
                "inherited_argument_root": inherited_argument or "NONE",
                "inherited_argument_source_event_id": inherited_argument_source or "NONE",
                "ellipsis_status": ellipsis_status(inherited_action, inherited_argument),
                "contextual_clause_de": clause,
                "exact_recipe_roundtrip": "+".join(atoms),
                "same_statement_inheritance_only": "YES",
                "cross_statement_inheritance": "NO",
                "guard": "CONTEXTUAL_EDITORIAL_READING__NO_RECIPE_OR_ROOT_RETUNING",
            })

        statement_rows.append({
            "statement_ordinal": statement["statement_ordinal"],
            "statement_id": statement_id,
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "prose_block_id": statement["prose_block_id"],
            "owner_id": statement["owner_id"],
            "owner_de": statement["image_local_expansion_de"].removeprefix("BILDLOKAL: "),
            "locus_start": statement["locus_start"],
            "locus_end": statement["locus_end"],
            "event_count": len(material),
            "event_ids": "|".join(statement_event_ids),
            "surface_sequence": " ".join(event["surface"] for event in material),
            "final_recipe_sequence": " | ".join(final_recipes),
            "controlled_order_sequence_de": " || ".join(controlled_chains),
            "target_event_count": target_count,
            "final_recipe_change_count": recipe_change_count,
            "inherited_action_event_count": statement_inherited_action_count,
            "inherited_argument_event_count": statement_inherited_argument_count,
            "contextual_working_reading_de": " ".join(clauses),
            "end_mode": statement["end_mode"],
            "all_events_backprojected": "YES",
            "cross_statement_inheritance": "NO",
            "guard": "COMPLETE_FOUR_PAGE_WORKING_STATEMENT__NO_PLAINTEXT_CLAIM",
        })

    local_rows: list[dict[str, object]] = []
    for event in local_source:
        target = final_by_surface.get(event["surface"])
        recipe = event["gdt516_context_recipe"]
        atoms = recipe.split("+")
        unknown = [atom for atom in atoms if atom not in controlled]
        if unknown:
            raise RuntimeError(f"Unmapped local atoms in {event['event_id']}: {unknown}")
        chain = " → ".join(controlled[atom] for atom in atoms) + "."
        local_rows.append({
            "local_ordinal": len(local_rows) + 1,
            "event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "locus": event["locus"],
            "surface": event["surface"],
            "owner_id": event["owner_id"],
            "owner_de": event["owner_de"],
            "content_role": event["content_role"],
            "local_recipe": recipe,
            "controlled_order_reading_de": chain,
            "local_working_phrase_de": local_phrase(event["content_role"], chain),
            "gdt538_surface_member": "YES" if target else "NO",
            "gdt538_recipe_match": (
                "YES" if target and target["final_working_recipe"] == recipe
                else "NOT_APPLICABLE" if not target else "NO"
            ),
            "gdt538_prose_phrase_applied": "NO",
            "retention_reason": "LOCAL_RECORD_ROLE_PRECEDES_SURFACE_PHRASE",
            "exact_recipe_roundtrip": "+".join(atoms),
            "guard": "LOCAL_ROLE_RETAINED__NO_PROSE_COERCION",
        })

    roles_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        if event["surface"] in final_by_surface:
            roles_by_surface[event["surface"]].append(event)
    role_rows: list[dict[str, object]] = []
    for ordinal, phrase in enumerate(phrase_rows, 1):
        material = roles_by_surface[phrase["surface"]]
        domains = {
            "LOCAL_RECORD" if event["statement_id"] == "NONE" else "PROSE_STREAM"
            for event in material
        }
        if len(domains) != 1:
            raise RuntimeError(f"Role collision for {phrase['surface']}: {domains}")
        domain = next(iter(domains))
        role_rows.append({
            "role_ordinal": ordinal,
            "surface": phrase["surface"],
            "final_working_recipe": phrase["final_working_recipe"],
            "event_count": len(material),
            "physical_pages": "|".join(sorted({event["physical_page"] for event in material})),
            "event_ids": "|".join(event["event_id"] for event in material),
            "content_roles": "|".join(sorted({event["content_role"] for event in material})),
            "observed_domain": domain,
            "corrected_lock_scope": domain + "_ONLY",
            "gdt538_old_lock_scope": phrase["lock_scope"],
            "scope_changed_from_gdt538": "YES" if domain == "LOCAL_RECORD" else "NO",
            "canonical_workshop_phrase_de": phrase["canonical_workshop_phrase_de"],
            "controlled_order_reading_de": phrase["controlled_order_reading_de"],
            "role_collision_count": 0,
            "guard": "OBSERVED_FOUR_PAGE_ROLE_ONLY__NO_FUTURE_ROLE_PREDICTION",
        })

    local_defaults: list[dict[str, object]] = []
    for role in role_rows:
        if role["observed_domain"] != "LOCAL_RECORD":
            continue
        material = [row for row in local_rows if row["surface"] == role["surface"]]
        phrases = sorted({str(row["local_working_phrase_de"]) for row in material})
        local_defaults.append({
            "local_surface_ordinal": len(local_defaults) + 1,
            "surface": role["surface"],
            "local_recipe": role["final_working_recipe"],
            "event_count": role["event_count"],
            "physical_pages": role["physical_pages"],
            "content_roles": role["content_roles"],
            "controlled_order_reading_de": role["controlled_order_reading_de"],
            "local_surface_default_de": phrases[0] if len(phrases) == 1 else " || ".join(phrases),
            "reading_variant_count": len(phrases),
            "lock_scope": "LOCAL_RECORD_ONLY",
        })

    ellipsis_counts = Counter(row["ellipsis_status"] for row in prose_rows)
    ellipsis_rows = [
        {
            "ellipsis_status": status,
            "event_count": count,
            "target_event_count": sum(
                row["ellipsis_status"] == status and row["recipe_source"] == "GDT538_FINAL_SURFACE"
                for row in prose_rows
            ),
            "rule_de": {
                "NO_INHERITANCE": "Karte spricht sichtbare Handlung/Argumente oder reine Kontrolle aus",
                "INHERITED_ACTION_ONLY": "nur die aktive Handlung stammt aus demselben Satz",
                "INHERITED_ARGUMENT_ONLY": "nur das aktive Argument stammt aus demselben Satz",
                "INHERITED_ACTION_AND_ARGUMENT": "Handlung und Argument stammen aus demselben Satz",
            }[status],
        }
        for status, count in sorted(ellipsis_counts.items())
    ]

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in events}):
        page_prose = [row for row in prose_rows if row["physical_page"] == page]
        page_local = [row for row in local_rows if row["physical_page"] == page]
        page_statements = [row for row in statement_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "register": page_prose[0]["register"] if page_prose else "SOURCE_SECTION_T",
            "statement_count": len(page_statements),
            "prose_event_count": len(page_prose),
            "target_prose_event_count": sum(row["recipe_source"] == "GDT538_FINAL_SURFACE" for row in page_prose),
            "local_event_count": len(page_local),
            "target_local_event_count": sum(row["gdt538_surface_member"] == "YES" for row in page_local),
            "final_recipe_change_count": sum(row["recipe_changed_after_gdt516"] == "YES" for row in page_prose),
            "complete_statement_reading_count": len(page_statements),
        })

    write_tsv(PROSE_OUT, prose_rows)
    write_tsv(STATEMENT_OUT, statement_rows)
    write_tsv(LOCAL_OUT, local_rows)
    write_tsv(ROLE_OUT, role_rows)
    write_tsv(LOCAL_DEFAULT_OUT, local_defaults)
    write_tsv(ELLIPSIS_OUT, ellipsis_rows)
    write_tsv(PAGE_OUT, page_rows)

    result = {
        "status": STATUS,
        "page_count": 4,
        "statement_count": len(statement_rows),
        "prose_event_count": len(prose_rows),
        "local_event_count": len(local_rows),
        "complete_event_count": len(prose_rows) + len(local_rows),
        "target_surface_count": len(role_rows),
        "target_prose_surface_count": sum(row["observed_domain"] == "PROSE_STREAM" for row in role_rows),
        "target_local_surface_count": sum(row["observed_domain"] == "LOCAL_RECORD" for row in role_rows),
        "target_prose_event_count": sum(row["recipe_source"] == "GDT538_FINAL_SURFACE" for row in prose_rows),
        "target_local_event_count": sum(row["gdt538_surface_member"] == "YES" for row in local_rows),
        "target_touched_statement_count": sum(int(row["target_event_count"]) > 0 for row in statement_rows),
        "role_collision_count": sum(int(row["role_collision_count"]) for row in role_rows),
        "scope_correction_surface_count": sum(row["scope_changed_from_gdt538"] == "YES" for row in role_rows),
        "final_recipe_change_event_count": sum(row["recipe_changed_after_gdt516"] == "YES" for row in prose_rows),
        "inherited_action_event_count": sum(row["inherited_action_root"] != "NONE" for row in prose_rows),
        "inherited_argument_event_count": sum(row["inherited_argument_root"] != "NONE" for row in prose_rows),
        "cross_statement_inheritance_count": 0,
        "exact_event_backprojection_count": sum(row["exact_recipe_roundtrip"] == row["final_context_recipe"] for row in prose_rows),
        "exact_local_backprojection_count": sum(row["exact_recipe_roundtrip"] == row["local_recipe"] for row in local_rows),
        "new_pages": 0,
        "root_meaning_changes": 0,
        "new_recipes": 0,
    }
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GDT539 — kontextuelle Arbeitslesung der vier Seiten",
        "",
        "Die Ausgabe trennt 546 Prosakarten in 78 Aussagen von 51 lokalen Rand-/Kennkarten. Jede Prosaklausel besitzt eine exakte Rezept- und Lesekettenrückseite; Ellipsen dürfen nur aus derselben Aussage erben.",
        "",
    ]
    current_page = ""
    for row in statement_rows:
        if row["physical_page"] != current_page:
            current_page = str(row["physical_page"])
            lines.extend([f"## {current_page}", ""])
        lines.extend([
            f"### {row['statement_id']} · {row['owner_de']}",
            "",
            str(row["contextual_working_reading_de"]),
            "",
            f"Oberflächen: `{row['surface_sequence']}`",
            "",
        ])
    lines.extend([
        "## Lokales Deck",
        "",
        "Die 51 lokalen Karten bleiben außerhalb der Satzlesung. Vierzehn der 159 neuen Oberflächen liegen ausschließlich hier; keine der 159 wechselt auf den vier Seiten zwischen Prosa und Lokalrolle.",
        "",
    ])
    for row in local_defaults:
        lines.append(f"- `{row['surface']}` — {row['local_surface_default_de']}")
    lines.append("")
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
