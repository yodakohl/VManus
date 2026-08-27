#!/usr/bin/env python3
"""Compile a complete current working reading for the 510 untreated local groups."""

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
BASE = ROOT / "experiments/yolo/gdt513_remaining_local_group_semantic_census"
ART = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G408 = ROOT / "experiments/yolo/gdt408_twenty_six_page_leave_one_page_transfer/artifacts"
G405 = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G473 = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts"

LOCAL_IN = G407 / "gdt407_693_local_group_edition.tsv"
GROUP_IN = G407 / "gdt407_5269_unified_group_ledger.tsv"
LEAVEOUT_IN = G408 / "gdt408_693_local_leaveout.tsv"
DICT_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
ADDRESS_IN = G473 / "gdt473_183_unified_address_working_edition.tsv"
LOCK_IN = G405 / "gdt405_426_locked_surface_dictionary.tsv"

EDITION_OUT = ART / "gdt513_510_remaining_local_working_edition.tsv"
RECIPE_OUT = ART / "gdt513_342_remaining_local_recipe_dictionary.tsv"
PAGE_OUT = ART / "gdt513_10_page_summary.tsv"
HYPOTHESIS_OUT = ART / "gdt513_5_hypothesis_scorecard.tsv"
EXPECTATION_OUT = ART / "gdt513_5_new_page_expectations.tsv"
COLLISION_OUT = ART / "gdt513_18_surface_parse_collision_audit.tsv"
READING_OUT = ART / "GDT513_REMAINING_LOCAL_READING_BOOK.md"
RESULT_OUT = ART / "gdt513_result.json"

STATUS = "ALL_510_REMAINING_LOCAL_GROUPS_RECEIVE_DEFAULTS__MIXED_RECORD_MODEL_SELECTED"
GUARD = "WORKING_COMPONENT_AND_STRUCTURAL_DEFAULTS_ONLY__NO_CONFIRMED_LEXEME"

ACTION_HEADS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ORDER_CONTROLS = {"OL", "OT"}
RELATIONS = {"AL", "AR", "L", "AIR"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}

# These six cards already had explicit owner-local structural values in GDT407.
# They stay visibly bracketed tags and are not added to the portable dictionary.
LEGACY_STRUCTURAL = {
    "CHEO": "LOKALER EINTRAG",
    "CTH": "BEREITSCHAFTSKLASSE",
    "CHK": "BEDINGUNGSKLASSE",
    "CPH": "GEGENPLATZ",
    "CKH": "VERBINDUNGSWEG",
    "CFH": "TRENNKLASSE",
}

EVIDENCE_ORDER = {
    "A_EXACT_RUNNING_SURFACE_RECIPE": 1,
    "B_RUNNING_RECIPE_NEW_SURFACE": 2,
    "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE": 3,
    "D_EXACT_LOCAL_SURFACE_OTHER_PAGE": 4,
    "E_LOCAL_RECIPE_OTHER_PAGE": 5,
    "F_PAGE_PRIVATE_VISIBLE_COMPOSITION": 6,
    "G_SECTION_MARKER": 7,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def join_sorted(values: set[str] | list[str]) -> str:
    cleaned = {value for value in values if value and value != "NONE"}
    return "|".join(sorted(cleaned)) if cleaned else "NONE"


def atom_trace(atom: str, dictionary: dict[str, dict[str, str]]) -> str:
    if atom in LEGACY_STRUCTURAL:
        return f"[{atom}:LOKALSTRUKTUR={LEGACY_STRUCTURAL[atom]}]"
    if atom == "SECTION_MARKER":
        return "[ABSCHNITTSMARKE]"
    entry = dictionary[atom]
    value = entry["working_value_de"]
    if entry["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE":
        return value
    if entry["factor_family"] in {"GRADE", "FORMAL_CONTROL"}:
        return f"[{atom}:STEUERUNG={value}]"
    return f"[{atom}:LOKALSTRUKTUR={value}]"


def record_role(atoms: list[str]) -> str:
    aset = set(atoms)
    if atoms == ["SECTION_MARKER"]:
        return "SECTION_MARKER"
    if aset & ACTION_HEADS:
        return "ORDERED_INSTRUCTION_CARD"
    if aset & ORDER_CONTROLS:
        return "ITINERARY_OR_ADDRESS_CARD"
    if aset & (RELATIONS | ARGUMENTS):
        return "COORDINATE_OR_CATALOGUE_CARD"
    return "LOCAL_CLASS_OR_NAME_CARD"


def default_reading(role: str, owner: str, surface: str, trace: str) -> str:
    if role == "SECTION_MARKER":
        return f"ABSCHNITTSMARKE {surface}"
    prefix = {
        "ORDERED_INSTRUCTION_CARD": "ANWEISUNG",
        "ITINERARY_OR_ADDRESS_CARD": "ADRESSE/FORTSETZUNG",
        "COORDINATE_OR_CATALOGUE_CARD": "KOORDINATE/KATALOGEINTRAG",
        "LOCAL_CLASS_OR_NAME_CARD": "LOKALE KENNUNG",
    }[role]
    return f"{prefix} BEI {owner}: {trace}"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    local_rows = read_tsv(LOCAL_IN)
    group_rows = read_tsv(GROUP_IN)
    leaveout_rows = read_tsv(LEAVEOUT_IN)
    dictionary_rows = read_tsv(DICT_IN)
    address_rows = read_tsv(ADDRESS_IN)
    lock_rows = read_tsv(LOCK_IN)
    if (len(local_rows), len(group_rows), len(leaveout_rows), len(dictionary_rows), len(address_rows), len(lock_rows)) != (693, 5269, 693, 46, 183, 426):
        raise ValueError("source row-count drift")

    dictionary = {row["atom"]: row for row in dictionary_rows}
    locked_surface = {row["surface"]: row for row in lock_rows}
    completed_address_ids = {row["source_event_id"] for row in address_rows}
    remaining = [row for row in local_rows if row["source_event_id"] not in completed_address_ids]
    if len(remaining) != 510:
        raise ValueError("remaining local complement is not 510 rows")

    leaveout = {row["source_event_id"]: row for row in leaveout_rows}
    running_surface_recipes: dict[str, set[str]] = defaultdict(set)
    running_surface_events: Counter[str] = Counter()
    running_recipe_surfaces: dict[str, set[str]] = defaultdict(set)
    running_recipe_events: Counter[str] = Counter()
    running_recipe_pages: dict[str, set[str]] = defaultdict(set)
    for row in group_rows:
        if row["group_kind"] != "RUNNING_EVENT":
            continue
        surface = row["surface"]
        recipe = row["component_recipe"]
        running_surface_recipes[surface].add(recipe)
        running_surface_events[surface] += 1
        running_recipe_surfaces[recipe].add(surface)
        running_recipe_events[recipe] += 1
        running_recipe_pages[recipe].add(row["physical_page"])

    edition: list[dict[str, object]] = []
    for ordinal, row in enumerate(remaining, start=1):
        event_id = row["source_event_id"]
        recipe = row["component_recipe"]
        atoms = recipe.split("+")
        if recipe == "SECTION_MARKER":
            atoms = ["SECTION_MARKER"]
        unknown = [atom for atom in atoms if atom not in dictionary and atom not in LEGACY_STRUCTURAL and atom != "SECTION_MARKER"]
        if unknown:
            raise ValueError(f"unresolved atoms for {event_id}: {unknown}")

        surface = row["surface"]
        if atoms == ["SECTION_MARKER"]:
            evidence = "G_SECTION_MARKER"
        elif recipe in running_surface_recipes.get(surface, set()):
            evidence = "A_EXACT_RUNNING_SURFACE_RECIPE"
        elif recipe in running_recipe_events:
            evidence = "B_RUNNING_RECIPE_NEW_SURFACE"
        elif surface in running_surface_recipes:
            evidence = "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE"
        elif leaveout[event_id]["leave_one_page_replay_class"] == "EXACT_LOCAL_SURFACE_OTHER_PAGE":
            evidence = "D_EXACT_LOCAL_SURFACE_OTHER_PAGE"
        elif leaveout[event_id]["leave_one_page_replay_class"] == "LOCAL_RECIPE_SHAPE_OTHER_PAGE":
            evidence = "E_LOCAL_RECIPE_OTHER_PAGE"
        else:
            evidence = "F_PAGE_PRIVATE_VISIBLE_COMPOSITION"

        role = record_role(atoms)
        trace = " · ".join(atom_trace(atom, dictionary) for atom in atoms)
        portable_atoms = [atom for atom in atoms if atom in dictionary and dictionary[atom]["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE"]
        formal_atoms = [atom for atom in atoms if atom in dictionary and dictionary[atom]["semantic_layer"] != "PORTABLE_BROAD_WORKING_CORE"]
        legacy_atoms = [atom for atom in atoms if atom in LEGACY_STRUCTURAL]
        page_private = leaveout[event_id]["leave_one_page_replay_class"] == "PAGE_PRIVATE_LOCAL_COPY_ALLOWED"
        nomenclator_signal = page_private or bool(legacy_atoms) or role == "LOCAL_CLASS_OR_NAME_CARD"
        renderer_signal = evidence in {"B_RUNNING_RECIPE_NEW_SURFACE", "E_LOCAL_RECIPE_OTHER_PAGE"}
        locked = locked_surface.get(surface)
        if locked is None:
            lock_alignment = "NOT_IN_GDT405_LOCK"
            future_policy = "NEW_SURFACE_USE_VISIBLE_LOCKED_ATOMS"
            locked_recipe = "NONE"
        elif locked["locked_recipe"] == recipe:
            lock_alignment = "MATCHES_GDT405_LOCK"
            future_policy = "REPLAY_GDT405_LOCKED_RECIPE"
            locked_recipe = locked["locked_recipe"]
        elif role == "SECTION_MARKER":
            lock_alignment = "ROLE_BOUND_SECTION_MARKER_DIFFERS_FROM_RUNNING_LOCK"
            future_policy = "CURRENT_MARKER_STAYS_STRUCTURAL__FUTURE_RUNNING_FORM_REPLAYS_GDT405_LOCK"
            locked_recipe = locked["locked_recipe"]
        else:
            lock_alignment = "LOCAL_ONLY_PARSE_DIFFERS_FROM_GDT405_LOCK"
            future_policy = "CURRENT_LOCAL_PARSE_STAYS_LOCAL__FUTURE_BATCH_REPLAYS_GDT405_LOCK"
            locked_recipe = locked["locked_recipe"]
        edition.append({
            "gdt513_local_id": f"G513-L{ordinal:03d}",
            "source_event_id": event_id,
            "physical_page": row["physical_page"],
            "source_panel": row["source_panel"],
            "register": row["register"],
            "locus": row["locus"],
            "source_order": row["source_order"],
            "owner_de": row["owner_de"],
            "surface": surface,
            "component_recipe": recipe,
            "component_atom_count": len(atoms),
            "portable_core_atoms": "+".join(portable_atoms) if portable_atoms else "NONE",
            "formal_or_local_atoms": "+".join(formal_atoms + legacy_atoms) if formal_atoms or legacy_atoms else "NONE",
            "legacy_structural_atoms": "+".join(legacy_atoms) if legacy_atoms else "NONE",
            "unresolved_atoms": "NONE",
            "component_trace_de": trace,
            "record_role": role,
            "default_working_reading_de": default_reading(role, row["owner_de"], surface, trace),
            "running_support_tier": evidence,
            "running_surface_event_count": running_surface_events[surface],
            "running_surface_recipe_count": len(running_surface_recipes.get(surface, set())),
            "running_surface_recipes": join_sorted(running_surface_recipes.get(surface, set())),
            "running_recipe_event_count": running_recipe_events[recipe],
            "running_recipe_surface_count": len(running_recipe_surfaces.get(recipe, set())),
            "running_recipe_pages": join_sorted(running_recipe_pages.get(recipe, set())),
            "local_leaveout_class": leaveout[event_id]["leave_one_page_replay_class"],
            "other_local_surface_pages": leaveout[event_id]["other_surface_pages"],
            "other_local_recipe_pages": leaveout[event_id]["other_recipe_pages"],
            "gdt405_lock_contact": "YES" if locked else "NO",
            "gdt405_locked_recipe": locked_recipe,
            "gdt405_lock_alignment": lock_alignment,
            "future_batch_recipe_policy": future_policy,
            "formula_hypothesis_signal": "YES" if role != "SECTION_MARKER" else "NO",
            "nomenclator_hypothesis_signal": "YES" if nomenclator_signal else "NO",
            "record_hypothesis_signal": "YES",
            "renderer_hypothesis_signal": "YES" if renderer_signal else "NO",
            "mixed_model_assignment": role,
            "meaning_status": "SECTION_MARKER_DEFAULT" if role == "SECTION_MARKER" else "COMPLETE_WORKING_COMPONENT_READING",
            "portable_meaning_changed": "NO",
            "structural_tag_promoted_to_word": "NO",
            "guard": GUARD,
        })

    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in edition:
        recipe_groups[str(row["component_recipe"])].append(row)
    recipe_rows: list[dict[str, object]] = []
    for ordinal, recipe in enumerate(sorted(recipe_groups), start=1):
        rows = recipe_groups[recipe]
        best = min((str(row["running_support_tier"]) for row in rows), key=lambda tier: EVIDENCE_ORDER[tier])
        recipe_rows.append({
            "gdt513_recipe_id": f"G513-R{ordinal:03d}",
            "component_recipe": recipe,
            "event_count": len(rows),
            "surface_count": len({str(row["surface"]) for row in rows}),
            "surfaces": join_sorted({str(row["surface"]) for row in rows}),
            "physical_page_count": len({str(row["physical_page"]) for row in rows}),
            "physical_pages": join_sorted({str(row["physical_page"]) for row in rows}),
            "registers": join_sorted({str(row["register"]) for row in rows}),
            "record_roles": join_sorted({str(row["record_role"]) for row in rows}),
            "component_trace_de": rows[0]["component_trace_de"],
            "best_support_tier": best,
            "running_recipe_event_count": max(int(row["running_recipe_event_count"]) for row in rows),
            "running_recipe_surface_count": max(int(row["running_recipe_surface_count"]) for row in rows),
            "page_private_event_count": sum(row["local_leaveout_class"] == "PAGE_PRIVATE_LOCAL_COPY_ALLOWED" for row in rows),
            "meaning_complete_for_every_event": "YES",
            "guard": GUARD,
        })

    page_rows: list[dict[str, object]] = []
    for page in sorted({str(row["physical_page"]) for row in edition}):
        rows = [row for row in edition if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "registers": join_sorted({str(row["register"]) for row in rows}),
            "owners_de": " | ".join(sorted({str(row["owner_de"]) for row in rows})),
            "local_group_count": len(rows),
            "distinct_surface_count": len({str(row["surface"]) for row in rows}),
            "distinct_recipe_count": len({str(row["component_recipe"]) for row in rows}),
            "exact_running_surface_recipe_count": sum(row["running_support_tier"] == "A_EXACT_RUNNING_SURFACE_RECIPE" for row in rows),
            "running_recipe_new_surface_count": sum(row["running_support_tier"] == "B_RUNNING_RECIPE_NEW_SURFACE" for row in rows),
            "running_surface_different_parse_count": sum(row["running_support_tier"] == "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE" for row in rows),
            "local_cross_page_support_count": sum(row["running_support_tier"] in {"D_EXACT_LOCAL_SURFACE_OTHER_PAGE", "E_LOCAL_RECIPE_OTHER_PAGE"} for row in rows),
            "page_private_visible_composition_count": sum(row["running_support_tier"] == "F_PAGE_PRIVATE_VISIBLE_COMPOSITION" for row in rows),
            "section_marker_count": sum(row["record_role"] == "SECTION_MARKER" for row in rows),
            "instruction_card_count": sum(row["record_role"] == "ORDERED_INSTRUCTION_CARD" for row in rows),
            "itinerary_or_address_count": sum(row["record_role"] == "ITINERARY_OR_ADDRESS_CARD" for row in rows),
            "coordinate_or_catalogue_count": sum(row["record_role"] == "COORDINATE_OR_CATALOGUE_CARD" for row in rows),
            "local_class_or_name_count": sum(row["record_role"] == "LOCAL_CLASS_OR_NAME_CARD" for row in rows),
            "complete_default_count": len(rows),
            "guard": GUARD,
        })

    evidence_counts = Counter(str(row["running_support_tier"]) for row in edition)
    role_counts = Counter(str(row["record_role"]) for row in edition)
    page_private_count = sum(row["local_leaveout_class"] == "PAGE_PRIVATE_LOCAL_COPY_ALLOWED" for row in edition)
    local_macro_count = sum(row["legacy_structural_atoms"] != "NONE" for row in edition)
    lock_contacts = sum(row["gdt405_lock_contact"] == "YES" for row in edition)
    lock_matches = sum(row["gdt405_lock_alignment"] == "MATCHES_GDT405_LOCK" for row in edition)
    lock_local_mismatches = sum(row["gdt405_lock_alignment"] == "LOCAL_ONLY_PARSE_DIFFERS_FROM_GDT405_LOCK" for row in edition)
    lock_marker_mismatches = sum(row["gdt405_lock_alignment"] == "ROLE_BOUND_SECTION_MARKER_DIFFERS_FROM_RUNNING_LOCK" for row in edition)
    nomenclator_support = sum(row["nomenclator_hypothesis_signal"] == "YES" for row in edition)
    renderer_support = sum(row["renderer_hypothesis_signal"] == "YES" for row in edition)
    locus_bundles = len({(str(row["physical_page"]), str(row["locus"]), str(row["owner_de"])) for row in edition})
    hypothesis_rows = [
        {
            "working_rank": 1,
            "hypothesis_id": "H5_MIXED_FORMULA_RECORD_NOMENCLATOR",
            "hypothesis_de": "Ein gemischtes Mikroregister verbindet Formeln, Adressen, Katalogkarten, lokale Kennungen und Abschnittsmarken.",
            "direct_support_event_count": len(edition),
            "pressure_event_count": 0,
            "decisive_observation_de": f"Alle 510 Karten erhalten ohne neuen portablen Kern eine von {len(role_counts)} sichtbaren Rollen; {evidence_counts['A_EXACT_RUNNING_SURFACE_RECIPE'] + evidence_counts['B_RUNNING_RECIPE_NEW_SURFACE']} besitzen direkten Laufrezeptanschluss.",
            "working_decision": "SELECT_AS_BEST_CURRENT_ARCHITECTURE",
            "statistical_score": "NOT_APPLICABLE_EXPLORATORY_COMPARISON",
        },
        {
            "working_rank": 2,
            "hypothesis_id": "H3_DATASET_OR_RECORD_CARDS",
            "hypothesis_de": "Die lokalen Gruppen sind positionsgebundene Datensatzkarten und keine fortlaufenden Satzwörter.",
            "direct_support_event_count": len(edition),
            "pressure_event_count": 0,
            "decisive_observation_de": f"Alle 510 Karten besitzen Seite, locus und Besitzer; sie bilden {locus_bundles} sichtbare locus/Besitzer-Bündel und enthalten neun echte Abschnittsmarken.",
            "working_decision": "RETAIN_AS_CONTAINER_MODEL",
            "statistical_score": "NOT_APPLICABLE_EXPLORATORY_COMPARISON",
        },
        {
            "working_rank": 3,
            "hypothesis_id": "H1_PRODUCTIVE_FORMULA_LAYER",
            "hypothesis_de": "Nichtmarker sind sichtbare Zusammensetzungen der bekannten Funktions- und Strukturkomponenten.",
            "direct_support_event_count": len(edition) - role_counts["SECTION_MARKER"],
            "pressure_event_count": page_private_count,
            "decisive_observation_de": f"501/501 Nichtmarker besitzen vollständige Komponentenrezepte; {evidence_counts['A_EXACT_RUNNING_SURFACE_RECIPE']} sind exakte Laufkarten und {evidence_counts['B_RUNNING_RECIPE_NEW_SURFACE']} weitere alte Laufrezepte. {page_private_count} bleiben als ganze lokale Formen seitenprivat.",
            "working_decision": "RETAIN_AS_FUNCTION_LAYER__NOT_COMPLETE_CONTAINER",
            "statistical_score": "NOT_APPLICABLE_EXPLORATORY_COMPARISON",
        },
        {
            "working_rank": 4,
            "hypothesis_id": "H4_OWNER_CONDITIONED_RENDERER",
            "hypothesis_de": "Alte Funktionsrezepte können in lokalen Registern unter anderen sichtbaren Oberflächen erscheinen.",
            "direct_support_event_count": renderer_support,
            "pressure_event_count": evidence_counts["C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE"],
            "decisive_observation_de": f"{renderer_support} Karten tragen dasselbe Lauf- oder Lokalrezept unter anderer Oberfläche; {evidence_counts['C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE']} gleichlautende Karten mit anderer lokaler Zerlegung mahnen vor freier Umrechnung.",
            "working_decision": "RETAIN_AS_BOUNDED_RENDERING_EFFECT",
            "statistical_score": "NOT_APPLICABLE_EXPLORATORY_COMPARISON",
        },
        {
            "working_rank": 5,
            "hypothesis_id": "H2_PURE_NOMENCLATOR",
            "hypothesis_de": "Jede lokale Oberfläche ist primär ein gelernter Eigenname oder Einzelbezeichner.",
            "direct_support_event_count": nomenclator_support,
            "pressure_event_count": evidence_counts["A_EXACT_RUNNING_SURFACE_RECIPE"] + evidence_counts["B_RUNNING_RECIPE_NEW_SURFACE"],
            "decisive_observation_de": f"{page_private_count} seitenprivate Formen und {local_macro_count} Karten mit alten Lokalmakros stützen lokale Individualität; {evidence_counts['A_EXACT_RUNNING_SURFACE_RECIPE'] + evidence_counts['B_RUNNING_RECIPE_NEW_SURFACE']} direkte Laufrezeptanschlüsse widersprechen aber einem reinen Namenbuch.",
            "working_decision": "REJECT_AS_SINGLE_GLOBAL_MODEL__KEEP_LOCAL_NAME_TAIL",
            "statistical_score": "NOT_APPLICABLE_EXPLORATORY_COMPARISON",
        },
    ]

    expectation_rows = [
        {"expectation_id": "G513-P1", "new_page_expectation_de": "Ein merklicher Teil der laufenden oder lokalen Karten wiederholt eine bekannte Oberfläche mit demselben Rezept.", "current_reference": f"{evidence_counts['A_EXACT_RUNNING_SURFACE_RECIPE']}/510 verbleibende Lokalgruppen", "interpretation_if_seen": "FORMELWIEDERKEHR", "interpretation_if_absent": "SEITENTYP ODER RENDERER STÄRKER ALS ERWARTET"},
        {"expectation_id": "G513-P2", "new_page_expectation_de": "Neue Oberflächen verwenden überwiegend bekannte Atome und alte Rezepte oder sichtbar neue Kombinationen.", "current_reference": "501/501 Nichtmarker vollständig komponentenlesbar", "interpretation_if_seen": "PRODUKTIVE FUNKTIONSSCHICHT", "interpretation_if_absent": "NEUER LOKALER NAMEN- ODER ZEICHENBLOCK"},
        {"expectation_id": "G513-P3", "new_page_expectation_de": "Lokale Gruppen teilen sich in Anweisung, Adresse/Fortsetzung, Koordinate/Katalog und Kennung statt nur Eigennamen.", "current_reference": "Fünf Rollen einschließlich Abschnittsmarke", "interpretation_if_seen": "GEMISCHTES MIKROREGISTER", "interpretation_if_absent": "EINHEITLICHERER SEITENTYP"},
        {"expectation_id": "G513-P4", "new_page_expectation_de": "Bildbesitzer liefert das konkrete Sachnomen; die neunzehn breiten Funktionswerte bleiben stabil.", "current_reference": "510/510 ohne neuen portablen Kern", "interpretation_if_seen": "BESITZERGESTEUERTE FACHLESUNG", "interpretation_if_absent": "KERNBEDEUTUNG ODER BESITZERZUORDNUNG MUSS NEU GEPRÜFT WERDEN"},
        {"expectation_id": "G513-P5", "new_page_expectation_de": "Echte neue Namenkerne dürfen stehen bleiben, doch Abschnitts- und Klassenzeichen werden nicht zu Wörtern befördert; eine GDT405-Oberfläche behält im neuen Batch ihr gesperrtes Rezept.", "current_reference": f"{page_private_count} seitenprivate Formen; sechs alte Lokalmakrotypen; neun Abschnittsmarken; {lock_contacts} GDT405-Kontakte mit {lock_matches} Rezepttreffern", "interpretation_if_seen": "MISCHUNG AUS FUNKTIONSRAHMEN UND GELERNTEM INHALT", "interpretation_if_absent": "LOKALE SCHICHT IST KOMPOSITIONELLER ALS ERWARTET"},
    ]

    collision_rows: list[dict[str, object]] = []
    for row in [item for item in edition if item["running_support_tier"] == "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE"]:
        atoms = str(row["component_recipe"]).split("+")
        if row["legacy_structural_atoms"] != "NONE":
            explanation = "LEGACY_OWNER_LOCAL_STRUCTURAL_MACRO"
        elif any(atom in dictionary and dictionary[atom]["factor_family"] == "LOCAL_OR_CLASS_SIGN" for atom in atoms):
            explanation = "OWNER_LOCAL_CLASS_OR_VARIANT_SIGN"
        elif any(recipe.endswith("+DY") for recipe in str(row["running_surface_recipes"]).split("|")) and str(row["component_recipe"]).endswith("+Y"):
            explanation = "OWNER_LOCAL_SCOPE_OR_CLOSE_SPLIT"
        else:
            explanation = "UNRESOLVED_OWNER_CONDITIONED_PARSE_WARNING"
        collision_rows.append({
            "gdt513_collision_id": f"G513-C{len(collision_rows) + 1:02d}",
            "source_event_id": row["source_event_id"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "local_component_recipe": row["component_recipe"],
            "local_component_trace_de": row["component_trace_de"],
            "running_surface_recipes": row["running_surface_recipes"],
            "collision_explanation": explanation,
            "gdt405_lock_alignment": row["gdt405_lock_alignment"],
            "future_batch_rule": row["future_batch_recipe_policy"],
            "portable_polysemy_inferred": "NO",
            "structural_tag_promoted_to_word": "NO",
            "guard": GUARD,
        })

    write_tsv(EDITION_OUT, edition)
    write_tsv(RECIPE_OUT, recipe_rows)
    write_tsv(PAGE_OUT, page_rows)
    write_tsv(HYPOTHESIS_OUT, hypothesis_rows)
    write_tsv(EXPECTATION_OUT, expectation_rows)
    write_tsv(COLLISION_OUT, collision_rows)

    reading = [
        "# GDT513 — Vollständige Lesefassung der 510 übrigen Lokalgruppen",
        "",
        f"Status: `{STATUS}`",
        "",
        "Die 510 Karten waren in GDT413 semantisch zurückgestellt, aber nicht strukturlos: 501 besitzen bereits ein sichtbares Komponentenrezept, neun sind Abschnittsmarken. Portable Arbeitswerte stehen als normale Wörter; formale und lokale Werte bleiben eckig geklammerte Struktur-Tags.",
        "",
        "## Fünf Arbeitshypothesen",
        "",
        "| Rang | Hypothese | Entscheidung |",
        "|---:|---|---|",
    ]
    for row in hypothesis_rows:
        reading.append(f"| {row['working_rank']} | {row['hypothesis_de']} | `{row['working_decision']}` |")
    for page_row in page_rows:
        page = str(page_row["physical_page"])
        reading.extend(["", f"## {page}", ""])
        for row in [item for item in edition if item["physical_page"] == page]:
            reading.append(f"- `{row['locus']}` `{row['surface']}` → {row['default_working_reading_de']}")
            reading.append(f"  - Rezept `{row['component_recipe']}` · `{row['running_support_tier']}`")
    reading.extend([
        "",
        "## Grenze",
        "",
        "Dies ist eine vollständige Default-Lesung innerhalb des kreativen Mischmodells. Die sechs alten Lokalmakros und alle Formalkontrollen bleiben Struktur-Tags. Keine Zeile bestätigt ein deutsches Wort, einen Eigennamen, eine Sprache oder Klartext.",
    ])
    READING_OUT.write_text("\n".join(reading) + "\n", encoding="utf-8")

    result = {
        "status": STATUS,
        "remaining_local_groups": len(edition),
        "physical_pages": len(page_rows),
        "distinct_surfaces": len({str(row['surface']) for row in edition}),
        "distinct_recipes": len(recipe_rows),
        "complete_component_readings": sum(row["meaning_status"] == "COMPLETE_WORKING_COMPONENT_READING" for row in edition),
        "section_marker_defaults": role_counts["SECTION_MARKER"],
        "unresolved_atoms": 0,
        "evidence_tier_counts": dict(sorted(evidence_counts.items())),
        "record_role_counts": dict(sorted(role_counts.items())),
        "direct_running_recipe_support": evidence_counts["A_EXACT_RUNNING_SURFACE_RECIPE"] + evidence_counts["B_RUNNING_RECIPE_NEW_SURFACE"],
        "page_private_visible_compositions": evidence_counts["F_PAGE_PRIVATE_VISIBLE_COMPOSITION"],
        "leaveout_page_private_events": page_private_count,
        "surface_parse_collisions": len(collision_rows),
        "surface_parse_collisions_with_named_structural_explanation": sum(row["collision_explanation"] != "UNRESOLVED_OWNER_CONDITIONED_PARSE_WARNING" for row in collision_rows),
        "gdt405_lock_contacts": lock_contacts,
        "gdt405_lock_recipe_matches": lock_matches,
        "gdt405_local_only_recipe_mismatches": lock_local_mismatches,
        "gdt405_section_marker_role_mismatches": lock_marker_mismatches,
        "hypotheses_compared": len(hypothesis_rows),
        "selected_architecture": "H5_MIXED_FORMULA_RECORD_NOMENCLATOR",
        "new_page_expectations": len(expectation_rows),
        "portable_meanings_changed": 0,
        "new_portable_atoms": 0,
        "structural_tags_promoted_to_words": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
