#!/usr/bin/env python3
"""Consolidate the GDT515 new forms into reusable thirty-page families.

This is a workshop consolidation pass. It asks how much of the 159 genuinely
new running surfaces is carried by complete older recipes, portable skeletons,
and context-local signs. It also writes an explicit context policy for the ten
surfaces that touched an older local label reading.
"""

from __future__ import annotations

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
BASE = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation"
ART = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G427 = ROOT / "experiments/yolo/gdt427_typed_prediction_specificity_repair/artifacts"
G473 = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"

NEW_IN = G515 / "gdt515_159_genuinely_new_surface_audit.tsv"
RUNNING_ABSENT_IN = G515 / "gdt515_169_running_absent_surface_audit.tsv"
EVENT_IN = G515 / "gdt515_597_complete_event_edition.tsv"
RUNNING30_IN = G515 / "gdt515_5122_running_event_edition.tsv"
UNIFIED30_IN = G515 / "gdt515_5866_unified_group_ledger.tsv"
OLD_RUNNING_IN = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_LOCAL_IN = G407 / "gdt407_693_local_group_edition.tsv"
DICT_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
PAIR_IN = G421 / "gdt421_81_ordered_pair_profiles.tsv"
ABSENT_PAIR_IN = G427 / "gdt427_17_absent_pair_negative_controls.tsv"
ADDRESS_IN = G473 / "gdt473_183_unified_address_working_edition.tsv"

FAMILY_OUT = ART / "gdt516_159_new_surface_family_atlas.tsv"
PORTABLE_FAMILY_OUT = ART / "gdt516_20_recurrent_portable_skeleton_families.tsv"
EXACT_CARRIER_OUT = ART / "gdt516_10_exact_old_recipe_carriers.tsv"
CROSS_PAGE_OUT = ART / "gdt516_3_cross_new_page_recurrences.tsv"
CONTEXT_OUT = ART / "gdt516_10_old_local_new_context_decisions.tsv"
OPEN_OUT = ART / "gdt516_6_open_parse_decisions.tsv"
LOCAL_TAG_OUT = ART / "gdt516_4_local_tag_registry.tsv"
DY_PAIR_OUT = ART / "gdt516_110_dy_y_pair_atlas.tsv"
DY_SUMMARY_OUT = ART / "gdt516_dy_ending_summary.tsv"
ACTION_OUT = ART / "gdt516_31_new_action_transition_atlas.tsv"
EVENT_OUT = ART / "gdt516_597_contextualized_event_edition.tsv"
UNIFIED_OUT = ART / "gdt516_5866_contextualized_unified_group_ledger.tsv"
BOOK_OUT = ART / "GDT516_THIRTY_PAGE_FAMILY_BOOK.md"
RESULT_OUT = ART / "gdt516_result.json"

STATUS = "PASS_NEW_FORMS_COMPRESSED_WITH_FINITE_CONTEXT_POLICY"
GUARD = "EXPLORATORY_WORKING_COMPOSITION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT"
PORTABLE_ATOMS: set[str] = set()
ACTION_HEADS: set[str] = set()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path,
    rows: list[dict[str, object]],
    fields: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty TSV: {path}")
    if fields is None:
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def joined(values) -> str:
    material = sorted({str(value) for value in values if str(value)})
    return "|".join(material) if material else "NONE"


def contains_tuple(haystack: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    width = len(needle)
    return any(haystack[i : i + width] == needle for i in range(len(haystack) - width + 1))


def best_old_recipe_tiles(
    recipe: tuple[str, ...],
    old_complete_recipes: set[tuple[str, ...]],
) -> tuple[int, tuple[str, ...]]:
    """Maximise atom coverage by disjoint complete old recipes of length >=2."""

    states: list[tuple[int, tuple[str, ...]]] = [(-1, tuple())] * (len(recipe) + 1)
    states[0] = (0, tuple())

    def rank(state: tuple[int, tuple[str, ...]]) -> tuple[object, ...]:
        return state[0], -len(state[1]), tuple(reversed(state[1]))

    for start in range(len(recipe)):
        covered, tiles = states[start]
        if covered < 0:
            continue
        skip = (covered, tiles)
        if rank(skip) > rank(states[start + 1]):
            states[start + 1] = skip
        for end in range(start + 2, len(recipe) + 1):
            chunk = recipe[start:end]
            if chunk not in old_complete_recipes:
                continue
            candidate = (covered + len(chunk), tiles + ("+".join(chunk),))
            if rank(candidate) > rank(states[end]):
                states[end] = candidate
    return states[-1]


def longest_old_complete_carriers(
    recipe: tuple[str, ...],
    old_complete_recipes: set[tuple[str, ...]],
) -> tuple[int, list[str]]:
    matches: list[tuple[str, ...]] = []
    for start in range(len(recipe)):
        for end in range(start + 2, len(recipe) + 1):
            chunk = recipe[start:end]
            if chunk in old_complete_recipes:
                matches.append(chunk)
    if not matches:
        return 0, []
    width = max(map(len, matches))
    return width, sorted({"+".join(value) for value in matches if len(value) == width})


LOCAL_VALUES = {
    "LOCAL_X": "[LOKALES_X:ZEICHEN_ODER_NAMENSKERN]",
    "LOCAL_C": "[LOKALES_C:ZEICHEN]",
    "LOCAL_NAME_CORE_D": "[LOKALER_NAME:d]",
    "LOCAL_NAME_CORE_YD": "[LOKALER_NAME:yd]",
}


def literal(recipe: str, dictionary: dict[str, str]) -> str:
    readings: list[str] = []
    for atom in atoms(recipe):
        if atom in LOCAL_VALUES:
            readings.append(LOCAL_VALUES[atom])
        elif atom in dictionary:
            value = dictionary[atom]
            readings.append(value if atom in PORTABLE_ATOMS else f"[{atom}:STEUERUNG={value}]")
        else:
            readings.append(f"[{atom}:LOKAL]")
    return " · ".join(readings)


def contextual_recipe(row: dict[str, str]) -> tuple[str, str, str]:
    """Return recipe, policy label, and short basis for a unified group."""

    surface = row["surface"]
    original = row.get("component_recipe", row.get("visible_recipe", ""))
    source_layer = row.get("source_layer", "")
    group_kind = row.get("group_kind", "")
    is_old_local = source_layer == "ORIGINAL22_LOCAL_ADDRESS"
    is_selected_local = source_layer == "GDT515_SECOND_RANDOM4_LOCAL"
    is_local = is_old_local or is_selected_local or group_kind == "LOCAL_ADDRESS_OR_LABEL"

    if surface == "chekey":
        return (
            "CH+K+E+Y",
            "COMMON_VISIBLE_RECIPE_PROMOTION",
            "two new prose pages plus old cheky carrier dissolve the old CHK label macro",
        )
    if surface == "saiir":
        return (
            "S+IIN+R",
            "COMMON_VISIBLE_RECIPE_PROMOTION",
            "daiir/okaiir/saiis family favours IIN over the old label-only AIIN split",
        )
    if surface == "doly":
        return (
            "LOCAL_NAME_CORE_D+OL+Y",
            "LEARNED_LABEL_SHELL_REPLAY",
            "GDT473 reads learned d plus the portable OL+Y label suffix",
        )
    if surface == "okyd":
        if is_old_local:
            return (
                "OK+LOCAL_NAME_CORE_YD",
                "ROLE_CONDITIONED_LABEL_RECIPE",
                "GDT473 celestial label: portable OK plus learned yd",
            )
        return (
            "OK+Y+D_ADDR",
            "ROLE_CONDITIONED_PROSE_RECIPE",
            "f66r prose retains visible Y plus local D address sign",
        )
    if surface == "sos":
        if is_old_local:
            return (
                "S_ADDR+O+S_ADDR",
                "ROLE_CONDITIONED_LABEL_RECIPE",
                "old celestial label keeps two address signs",
            )
        return (
            "S+O+S",
            "ROLE_CONDITIONED_PROSE_RECIPE",
            "herbal prose keeps the two portable S heads",
        )
    if surface == "ykady":
        if is_old_local:
            return (
                "Y+K+A_ADDR+Y",
                "ROLE_CONDITIONED_LABEL_RECIPE",
                "old celestial label keeps terminal Y",
            )
        return (
            "Y+K+A_ADDR+DY",
            "ROLE_CONDITIONED_PROSE_RECIPE",
            "f66r prose keeps terminal close DY",
        )
    if surface == "ykeeody":
        if is_old_local:
            return (
                "Y+K+EE+O+Y",
                "ROLE_CONDITIONED_LABEL_RECIPE",
                "old celestial label keeps terminal Y",
            )
        return (
            "Y+K+EE+O+DY",
            "ROLE_CONDITIONED_PROSE_RECIPE",
            "two f66r prose events keep terminal close DY",
        )
    if surface in {"daiir", "odair", "ykees"}:
        return (
            original,
            "EXACT_OLD_LOCAL_NEW_CONTEXT_AGREEMENT",
            "old local and selected-page recipes already agree exactly",
        )
    if surface in {"x", "axor", "chxar"}:
        revised = {
            "x": "LOCAL_X",
            "axor": "A_ADDR+LOCAL_X+OR",
            "chxar": "CH+LOCAL_X+AR",
        }[surface]
        return (
            revised,
            "F66R_LOCAL_X_UNIFICATION",
            "one page-local X tag now covers standalone and embedded x",
        )
    if surface == "c" and is_local:
        return (
            "LOCAL_C",
            "F66R_LOCAL_C_NORMALIZATION",
            "standalone marginal c remains a page-local sign",
        )
    return original, "UNCHANGED_THIRTY_PAGE_REPLAY", "no contextual collision"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    new_rows = read_tsv(NEW_IN)
    running_absent_rows = read_tsv(RUNNING_ABSENT_IN)
    selected_events = read_tsv(EVENT_IN)
    running30 = read_tsv(RUNNING30_IN)
    unified30 = read_tsv(UNIFIED30_IN)
    old_running = read_tsv(OLD_RUNNING_IN)
    old_local = read_tsv(OLD_LOCAL_IN)
    dictionary_rows = read_tsv(DICT_IN)
    pair_profiles = read_tsv(PAIR_IN)
    absent_pair_rows = read_tsv(ABSENT_PAIR_IN)
    address_rows = read_tsv(ADDRESS_IN)

    if len(new_rows) != 159 or len(selected_events) != 597:
        raise RuntimeError("GDT515 input counts changed")
    if len(running30) != 5122 or len(unified30) != 5866:
        raise RuntimeError("GDT515 thirty-page decks changed")

    global PORTABLE_ATOMS, ACTION_HEADS
    PORTABLE_ATOMS = {
        row["atom"]
        for row in dictionary_rows
        if row["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE"
    }
    ACTION_HEADS = {
        row["atom"] for row in dictionary_rows if row["factor_family"] == "ACTION_HEAD"
    }
    dictionary = {row["atom"]: row["working_value_de"] for row in dictionary_rows}
    if len(PORTABLE_ATOMS) != 19 or len(ACTION_HEADS) != 9:
        raise RuntimeError("current component inventory changed")

    old_recipe_rows: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in old_running:
        old_recipe_rows[atoms(row["component_recipe"])].append(row)
    old_complete_recipes = set(old_recipe_rows)

    new_event_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_events:
        if row["genuinely_new_to_old_26_pages"] == "YES":
            new_event_rows[row["surface"]].append(row)

    family_rows: list[dict[str, object]] = []
    portable_groups: dict[str, list[str]] = defaultdict(list)
    action_groups: dict[str, list[str]] = defaultdict(list)
    for row in new_rows:
        event_material = new_event_rows[row["surface"]]
        new_is_local = all(
            event["content_role"] != "ORDERED_INSTRUCTION_CARD"
            for event in event_material
        )
        recipe, policy, basis = contextual_recipe(
            {
                "surface": row["surface"],
                "component_recipe": row["direct_visible_recipe"],
                "source_layer": (
                    "GDT515_SECOND_RANDOM4_LOCAL"
                    if new_is_local
                    else "GDT515_SECOND_RANDOM4_RUNNING"
                ),
                "group_kind": (
                    "LOCAL_ADDRESS_OR_LABEL" if new_is_local else "RUNNING_EVENT"
                ),
            }
        )
        sequence = atoms(recipe)
        old_exact = old_recipe_rows.get(sequence, [])
        longest_width, longest_recipes = longest_old_complete_carriers(
            sequence, old_complete_recipes
        )
        tile_coverage, tiles = best_old_recipe_tiles(sequence, old_complete_recipes)
        portable = tuple(atom for atom in sequence if atom in PORTABLE_ATOMS)
        actions = tuple(atom for atom in sequence if atom in ACTION_HEADS)
        portable_skeleton = "+".join(portable) if portable else "NONE"
        action_skeleton = "+".join(actions) if actions else "NONE"
        portable_groups[portable_skeleton].append(row["surface"])
        action_groups[action_skeleton].append(row["surface"])
        if old_exact:
            tier = "FULL_OLD_RECIPE_CARRIER"
        elif tile_coverage == len(sequence):
            tier = "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"
        elif longest_width >= 2:
            tier = "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"
        else:
            tier = "ATOMS_AND_FACTORS_ONLY"
        family_rows.append(
            {
                "surface": row["surface"],
                "occurrence_count": row["occurrence_count"],
                "physical_pages": row["physical_pages"],
                "gdt515_recipe": row["direct_visible_recipe"],
                "gdt516_context_recipe": recipe,
                "recipe_atom_count": len(sequence),
                "support_tier": tier,
                "old_exact_recipe_event_count": len(old_exact),
                "old_exact_recipe_surface_count": len({x["surface"] for x in old_exact}),
                "old_exact_recipe_pages": joined(x["physical_page"] for x in old_exact),
                "old_exact_recipe_surfaces": joined(x["surface"] for x in old_exact),
                "longest_old_complete_recipe_fragment_atoms": longest_width,
                "longest_old_complete_recipe_fragments": joined(longest_recipes),
                "max_disjoint_old_recipe_coverage_atoms": tile_coverage,
                "max_disjoint_old_recipe_coverage_fraction": f"{tile_coverage / len(sequence):.6f}",
                "max_disjoint_old_recipe_tiles": joined(tiles),
                "portable_skeleton": portable_skeleton,
                "portable_skeleton_family_size": 0,
                "action_skeleton": action_skeleton,
                "action_skeleton_family_size": 0,
                "cross_selected_page_recurrence": (
                    "YES" if len({x["physical_page"] for x in event_material}) > 1 else "NO"
                ),
                "context_policy": policy,
                "context_basis": basis,
                "new_portable_atom_count": row["new_portable_atom_count"],
                "guard": GUARD,
            }
        )

    for row in family_rows:
        row["portable_skeleton_family_size"] = len(
            portable_groups[str(row["portable_skeleton"])]
        )
        row["action_skeleton_family_size"] = len(
            action_groups[str(row["action_skeleton"])]
        )
    family_rows.sort(key=lambda row: str(row["surface"]))
    write_tsv(FAMILY_OUT, family_rows)

    exact_carrier_rows = [
        dict(row) for row in family_rows if int(row["old_exact_recipe_event_count"]) > 0
    ]
    write_tsv(EXACT_CARRIER_OUT, exact_carrier_rows)

    portable_family_rows: list[dict[str, object]] = []
    family_by_surface = {str(row["surface"]): row for row in family_rows}
    for skeleton, surfaces in sorted(
        portable_groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        if skeleton == "NONE" or len(surfaces) < 2:
            continue
        members = [family_by_surface[surface] for surface in sorted(surfaces)]
        portable_family_rows.append(
            {
                "portable_skeleton": skeleton,
                "portable_reading_de": " → ".join(dictionary[atom] for atom in atoms(skeleton)),
                "surface_count": len(members),
                "event_count": sum(int(row["occurrence_count"]) for row in members),
                "physical_pages": joined(
                    page
                    for row in members
                    for page in str(row["physical_pages"]).split("|")
                ),
                "surfaces": joined(row["surface"] for row in members),
                "recipes": joined(row["gdt516_context_recipe"] for row in members),
                "old_exact_carrier_member_count": sum(
                    int(row["old_exact_recipe_event_count"]) > 0 for row in members
                ),
                "interpretive_use": "REUSABLE_PORTABLE_FAMILY__CONTROL_SHELLS_REMAIN_VISIBLE",
                "guard": GUARD,
            }
        )
    if len(portable_family_rows) != 20:
        raise RuntimeError(f"expected 20 recurrent nonempty portable families, got {len(portable_family_rows)}")
    write_tsv(PORTABLE_FAMILY_OUT, portable_family_rows)

    cross_page_rows = [
        dict(row) for row in family_rows if row["cross_selected_page_recurrence"] == "YES"
    ]
    if {row["surface"] for row in cross_page_rows} != {"keody", "qokees", "shain"}:
        raise RuntimeError("cross-page new-surface anchors changed")
    write_tsv(CROSS_PAGE_OUT, cross_page_rows)

    contact_input = {
        row["surface"]: row
        for row in running_absent_rows
        if row["old_local_surface_contact"] == "YES"
    }
    if len(contact_input) != 10:
        raise RuntimeError(f"expected ten old-local contacts, got {len(contact_input)}")
    old_local_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old_local:
        old_local_by_surface[row["surface"]].append(row)

    context_decision_names = {
        "chekey": "COMMON_VISIBLE_RECIPE_PROMOTION",
        "daiir": "EXACT_RECIPE_AGREEMENT",
        "doly": "LEARNED_LABEL_SHELL_REPLAY",
        "odair": "EXACT_RECIPE_AGREEMENT",
        "okyd": "ROLE_CONDITIONED_HOMOGRAPH",
        "saiir": "COMMON_VISIBLE_RECIPE_PROMOTION",
        "sos": "ROLE_CONDITIONED_HOMOGRAPH",
        "ykady": "ROLE_CONDITIONED_HOMOGRAPH",
        "ykeeody": "ROLE_CONDITIONED_HOMOGRAPH",
        "ykees": "EXACT_RECIPE_AGREEMENT",
    }
    context_rows: list[dict[str, object]] = []
    for surface in sorted(contact_input):
        audit = contact_input[surface]
        old_material = old_local_by_surface[surface]
        new_material = [row for row in selected_events if row["surface"] == surface]
        old_probe = {
            "surface": surface,
            "component_recipe": old_material[0]["component_recipe"],
            "source_layer": "ORIGINAL22_LOCAL_ADDRESS",
            "source_local_role": old_material[0]["source_local_role"],
            "group_kind": "LOCAL_ADDRESS_OR_LABEL",
        }
        new_is_local = all(
            row["content_role"] != "ORDERED_INSTRUCTION_CARD" for row in new_material
        )
        new_probe = {
            "surface": surface,
            "component_recipe": audit["direct_visible_recipe"],
            "source_layer": (
                "GDT515_SECOND_RANDOM4_LOCAL"
                if new_is_local
                else "GDT515_SECOND_RANDOM4_RUNNING"
            ),
            "source_local_role": new_material[0]["content_role"],
            "group_kind": "LOCAL_ADDRESS_OR_LABEL" if new_is_local else "RUNNING_EVENT",
        }
        old_recipe, old_policy, old_basis = contextual_recipe(old_probe)
        new_recipe, new_policy, new_basis = contextual_recipe(new_probe)
        context_rows.append(
            {
                "surface": surface,
                "old_local_event_count": len(old_material),
                "old_local_pages": joined(row["physical_page"] for row in old_material),
                "old_local_source_recipe": joined(row["component_recipe"] for row in old_material),
                "new_event_count": len(new_material),
                "new_pages": joined(row["physical_page"] for row in new_material),
                "new_source_roles": joined(row["content_role"] for row in new_material),
                "new_source_recipe": audit["direct_visible_recipe"],
                "decision": context_decision_names[surface],
                "old_context_recipe": old_recipe,
                "new_context_recipe": new_recipe,
                "old_policy": old_policy,
                "new_policy": new_policy,
                "portable_meaning_change": "NO",
                "basis": old_basis if old_basis == new_basis else f"{old_basis} / {new_basis}",
                "guard": GUARD,
            }
        )
    write_tsv(CONTEXT_OUT, context_rows)

    address_by_surface = {row["surface"]: row for row in address_rows}
    if address_by_surface["doly"]["working_recipe"] != "OL+Y":
        raise RuntimeError("GDT473 doly function shell changed")
    if address_by_surface["okyd"]["working_recipe"] != "OK":
        raise RuntimeError("GDT473 okyd function shell changed")

    def sequence_support(
        sequence: tuple[str, ...], rows: list[dict[str, str]]
    ) -> tuple[int, int, str]:
        hits = [
            row
            for row in rows
            if contains_tuple(atoms(row["component_recipe"]), sequence)
        ]
        return len(hits), len({row["surface"] for row in hits}), joined(row["surface"] for row in hits)

    running_without_okedam = [row for row in running30 if row["surface"] != "okedam"]
    ok_prefix = sequence_support(("OK", "E", "D_ADDR"), running_without_okedam)
    ok_suffix = sequence_support(("D_ADDR", "AM_ADDR"), running_without_okedam)
    cthy_rows = [row for row in running30 if row["surface"] == "cthy"]
    qocthey_rows = [row for row in running30 if row["surface"] == "qocthey"]
    x_rows = [row for row in selected_events if row["surface"] == "x"]
    open_rows: list[dict[str, object]] = [
        {
            "surface": "axor",
            "gdt515_recipe": "A_ADDR+LOCAL_NAME_CORE_X+OR",
            "considered_alternate": "A_ADDR+LOCAL_SIGN_X+OR",
            "gdt516_recipe": "A_ADDR+LOCAL_X+OR",
            "decision": "UNIFY_LOCAL_X_WITHOUT_PORTABLE_VALUE",
            "support": f"{len(x_rows)} standalone x signs plus embedded x on f66r",
            "confidence": "AMBER_LOCAL",
            "portable_meaning_change": "NO",
            "guard": GUARD,
        },
        {
            "surface": "chxar",
            "gdt515_recipe": "CH+LOCAL_NAME_CORE_X+AR",
            "considered_alternate": "CH+LOCAL_SIGN_X+AR",
            "gdt516_recipe": "CH+LOCAL_X+AR",
            "decision": "UNIFY_LOCAL_X_WITHOUT_PORTABLE_VALUE",
            "support": f"{len(x_rows)} standalone x signs plus embedded x on f66r",
            "confidence": "AMBER_LOCAL",
            "portable_meaning_change": "NO",
            "guard": GUARD,
        },
        {
            "surface": "cthdy",
            "gdt515_recipe": "CH+T+D_ADDR+Y",
            "considered_alternate": "CH+T+DY",
            "gdt516_recipe": "CH+T+D_ADDR+Y",
            "decision": "KEEP_VISIBLE_D_ADDRESS_INSERTION",
            "support": f"cthy has {len(cthy_rows)} events with CH+T+Y; cthdy supplies the visible D_ADDR contrast",
            "confidence": "GREEN_CONTEXTUAL",
            "portable_meaning_change": "NO",
            "guard": GUARD,
        },
        {
            "surface": "okedam",
            "gdt515_recipe": "OK+E+D_ADDR+AM_ADDR",
            "considered_alternate": "OK+E+DA+M_LOCAL",
            "gdt516_recipe": "OK+E+D_ADDR+AM_ADDR",
            "decision": "KEEP_COMPOSITIONAL_ADDRESS_CHAIN",
            "support": (
                f"excluding okedam, OK+E+D_ADDR occurs in {ok_prefix[0]} events/{ok_prefix[1]} surfaces "
                f"({ok_prefix[2]}); D_ADDR+AM_ADDR in {ok_suffix[0]} events/{ok_suffix[1]} surfaces ({ok_suffix[2]})"
            ),
            "confidence": "GREEN_CONTEXTUAL",
            "portable_meaning_change": "NO",
            "guard": GUARD,
        },
        {
            "surface": "qocthedy",
            "gdt515_recipe": "CARRIER_Q+O+CH+T+E+Y",
            "considered_alternate": "CARRIER_Q+O+CH+T+E+DY",
            "gdt516_recipe": "CARRIER_Q+O+CH+T+E+Y",
            "decision": "KEEP_EXACT_OLD_RECIPE_ALLOGRAPH",
            "support": f"qocthey has {len(qocthey_rows)} old event with the exact same complete recipe",
            "confidence": "GREEN_CONTEXTUAL",
            "portable_meaning_change": "NO",
            "guard": GUARD,
        },
        {
            "surface": "ykady",
            "gdt515_recipe": "Y+K+A_ADDR+DY",
            "considered_alternate": "Y+K+A_ADDR+Y",
            "gdt516_recipe": "Y+K+A_ADDR+DY",
            "decision": "KEEP_ROLE_CONDITIONED_PROSE_CLOSE",
            "support": "old f69v celestial label keeps final Y; f66r prose keeps final DY",
            "confidence": "AMBER_ROLE_CONDITIONED",
            "portable_meaning_change": "NO",
            "guard": GUARD,
        },
    ]
    write_tsv(OPEN_OUT, open_rows)

    local_tag_rows: list[dict[str, object]] = [
        {
            "local_tag": "LOCAL_X",
            "visible_material": "x",
            "scope": "f66r only",
            "surface_count": 3,
            "surfaces": "axor|chxar|x",
            "working_role": "neutral page-local sign or learned core",
            "portable_value": "NONE",
            "prediction_rule": "reuse only where f66r-style local x evidence exists",
            "guard": GUARD,
        },
        {
            "local_tag": "LOCAL_C",
            "visible_material": "c",
            "scope": "f66r marginal sign sequence only",
            "surface_count": 1,
            "surfaces": "c",
            "working_role": "standalone page-local sign",
            "portable_value": "NONE",
            "prediction_rule": "do not export as portable CH or CARRIER_Q",
            "guard": GUARD,
        },
        {
            "local_tag": "LOCAL_NAME_CORE_D",
            "visible_material": "d",
            "scope": "learned-label slot in doly",
            "surface_count": 1,
            "surfaces": "doly",
            "working_role": "learned object-name core before OL+Y",
            "portable_value": "NONE",
            "prediction_rule": "only inside an independently identified learned-name slot",
            "guard": GUARD,
        },
        {
            "local_tag": "LOCAL_NAME_CORE_YD",
            "visible_material": "yd",
            "scope": "learned-label slot in old local okyd",
            "surface_count": 1,
            "surfaces": "okyd",
            "working_role": "learned star/ring-position name core after OK",
            "portable_value": "NONE",
            "prediction_rule": "label-only; prose okyd remains OK+Y+D_ADDR",
            "guard": GUARD,
        },
    ]
    write_tsv(LOCAL_TAG_OUT, local_tag_rows)

    running_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running30:
        running_by_surface[row["surface"]].append(row)
    dy_surfaces = sorted(surface for surface in running_by_surface if surface.endswith("dy"))
    dy_class_counts: Counter[str] = Counter()
    dy_event_counts: Counter[str] = Counter()
    for surface in dy_surfaces:
        last_atoms = {
            atoms(row["component_recipe"])[-1] for row in running_by_surface[surface]
        }
        if last_atoms == {"DY"}:
            category = "RECIPE_END_DY"
        elif last_atoms == {"Y"}:
            category = "RECIPE_END_Y"
        else:
            category = "OTHER_OR_MIXED"
        dy_class_counts[category] += 1
        dy_event_counts[category] += len(running_by_surface[surface])

    dy_pair_rows: list[dict[str, object]] = []
    for dy_surface in dy_surfaces:
        y_surface = dy_surface[:-2] + "y"
        if y_surface not in running_by_surface:
            continue
        dy_material = running_by_surface[dy_surface]
        y_material = running_by_surface[y_surface]
        dy_recipes = {row["component_recipe"] for row in dy_material}
        y_recipes = {row["component_recipe"] for row in y_material}
        relation = "SAME_RECIPE" if dy_recipes == y_recipes else "DIFFERENT_RECIPE"
        dy_pair_rows.append(
            {
                "dy_surface": dy_surface,
                "y_surface": y_surface,
                "dy_event_count": len(dy_material),
                "y_event_count": len(y_material),
                "dy_pages": joined(row["physical_page"] for row in dy_material),
                "y_pages": joined(row["physical_page"] for row in y_material),
                "dy_recipes": joined(dy_recipes),
                "y_recipes": joined(y_recipes),
                "recipe_relation": relation,
                "interpretive_rule": (
                    "VISIBLE_D_MAY_BE_ALLOGRAPHIC_UNDER_THIS_SURFACE_PAIR"
                    if relation == "SAME_RECIPE"
                    else "VISIBLE_D_CARRIES_A_RECIPE_CONTRAST_IN_THIS_PAIR"
                ),
                "guard": GUARD,
            }
        )
    if len(dy_pair_rows) != 110:
        raise RuntimeError(f"expected 110 dy/y pairs, got {len(dy_pair_rows)}")
    write_tsv(DY_PAIR_OUT, dy_pair_rows)

    dy_summary_rows = [
        {
            "category": category,
            "surface_type_count": dy_class_counts[category],
            "event_count": dy_event_counts[category],
            "interpretation": {
                "RECIPE_END_DY": "visible dy parsed as close DY",
                "RECIPE_END_Y": "visible dy parsed with final portable Y",
                "OTHER_OR_MIXED": "visible dy absorbed by another recipe ending",
            }[category],
            "guard": GUARD,
        }
        for category in ("RECIPE_END_DY", "RECIPE_END_Y", "OTHER_OR_MIXED")
    ]
    write_tsv(DY_SUMMARY_OUT, dy_summary_rows)

    def ordered_adjacent_action_pairs(recipe: str) -> list[tuple[str, str]]:
        heads = [atom for atom in atoms(recipe) if atom in ACTION_HEADS]
        return list(zip(heads, heads[1:]))

    def directly_adjacent_action_pairs(recipe: str) -> list[tuple[str, str]]:
        material = atoms(recipe)
        return [
            (material[i], material[i + 1])
            for i in range(len(material) - 1)
            if material[i] in ACTION_HEADS and material[i + 1] in ACTION_HEADS
        ]

    old_order_events: Counter[tuple[str, str]] = Counter()
    old_order_surfaces: dict[tuple[str, str], set[str]] = defaultdict(set)
    old_direct_events: Counter[tuple[str, str]] = Counter()
    for row in old_running:
        for pair in set(ordered_adjacent_action_pairs(row["component_recipe"])):
            old_order_events[pair] += 1
            old_order_surfaces[pair].add(row["surface"])
        for pair in set(directly_adjacent_action_pairs(row["component_recipe"])):
            old_direct_events[pair] += 1

    new_order_events: Counter[tuple[str, str]] = Counter()
    new_order_surfaces: dict[tuple[str, str], set[str]] = defaultdict(set)
    new_order_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    new_direct_events: Counter[tuple[str, str]] = Counter()
    for row in family_rows:
        recipe = str(row["gdt516_context_recipe"])
        count = int(row["occurrence_count"])
        pages = str(row["physical_pages"]).split("|")
        for pair in set(ordered_adjacent_action_pairs(recipe)):
            new_order_events[pair] += count
            new_order_surfaces[pair].add(str(row["surface"]))
            new_order_pages[pair].update(pages)
        for pair in set(directly_adjacent_action_pairs(recipe)):
            new_direct_events[pair] += count

    old_pair_profiles = {row["ordered_pair"]: row for row in pair_profiles}
    absent_pairs = {row["ordered_pair"]: row for row in absent_pair_rows}
    transition_rows: list[dict[str, object]] = []
    for pair in sorted(new_order_events):
        label = ">".join(pair)
        plus_label = "+".join(pair)
        old_count = old_order_events[pair]
        old_direct = old_direct_events[pair]
        if old_count == 0:
            decision = (
                "NEW_ORDER__PREVIOUSLY_AMBER_ALLOWED"
                if label in absent_pairs
                else "NEW_ORDER__NO_PRIOR_CONTROL"
            )
        elif old_direct == 0 and new_direct_events[pair] > 0:
            decision = "NEW_DIRECT_ADJACENCY__OLD_ORDER_ATTESTED"
        else:
            decision = "OLD_ORDER_REUSED"
        profile = old_pair_profiles.get(plus_label, {})
        control = absent_pairs.get(label, {})
        transition_rows.append(
            {
                "ordered_pair": label,
                "working_reading_de": f"{dictionary[pair[0]]} → {dictionary[pair[1]]}",
                "new_event_count": new_order_events[pair],
                "new_surface_count": len(new_order_surfaces[pair]),
                "new_surfaces": joined(new_order_surfaces[pair]),
                "new_pages": joined(new_order_pages[pair]),
                "new_direct_adjacency_event_count": new_direct_events[pair],
                "old_order_event_count": old_count,
                "old_order_surface_count": len(old_order_surfaces[pair]),
                "old_direct_adjacency_event_count": old_direct,
                "gdt421_pair_status": profile.get("status", "PAIR_ABSENT"),
                "gdt427_negative_control_result": control.get(
                    "negative_control_result", "NOT_A_GDT427_ABSENT_CONTROL"
                ),
                "gdt427_typed_transition": control.get("typed_transition", "NONE"),
                "gdt427_support_pages": control.get("transition_support_pages", "NONE"),
                "thirty_page_decision": decision,
                "guard": GUARD,
            }
        )
    if len(transition_rows) != 31:
        raise RuntimeError(f"expected 31 new ordered action pairs, got {len(transition_rows)}")
    write_tsv(ACTION_OUT, transition_rows)

    contextual_events: list[dict[str, object]] = []
    for row in selected_events:
        is_running = row["content_role"] == "ORDERED_INSTRUCTION_CARD"
        probe = {
            "surface": row["surface"],
            "component_recipe": row["visible_recipe"],
            "source_layer": (
                "GDT515_SECOND_RANDOM4_RUNNING"
                if is_running
                else "GDT515_SECOND_RANDOM4_LOCAL"
            ),
            "source_local_role": row["content_role"],
            "group_kind": "RUNNING_EVENT" if is_running else "LOCAL_ADDRESS_OR_LABEL",
        }
        recipe, policy, basis = contextual_recipe(probe)
        material: dict[str, object] = dict(row)
        material.update(
            {
                "gdt516_context_recipe": recipe,
                "gdt516_literal_reading_de": literal(recipe, dictionary),
                "gdt516_context_policy": policy,
                "gdt516_context_basis": basis,
                "gdt516_recipe_changed": "YES" if recipe != row["visible_recipe"] else "NO",
                "gdt516_guard": GUARD,
            }
        )
        contextual_events.append(material)
    write_tsv(EVENT_OUT, contextual_events)

    contextual_unified: list[dict[str, object]] = []
    for row in unified30:
        recipe, policy, basis = contextual_recipe(row)
        material = dict(row)
        material.update(
            {
                "gdt516_context_recipe": recipe,
                "gdt516_literal_reading_de": literal(recipe, dictionary),
                "gdt516_context_policy": policy,
                "gdt516_context_basis": basis,
                "gdt516_recipe_changed": "YES" if recipe != row["component_recipe"] else "NO",
                "gdt516_guard": GUARD,
            }
        )
        contextual_unified.append(material)
    write_tsv(UNIFIED_OUT, contextual_unified)

    exact_count = len(exact_carrier_rows)
    fully_tiled = sum(
        int(row["max_disjoint_old_recipe_coverage_atoms"]) == int(row["recipe_atom_count"])
        for row in family_rows
    )
    covered_atoms = sum(
        int(row["max_disjoint_old_recipe_coverage_atoms"]) for row in family_rows
    )
    total_atoms = sum(int(row["recipe_atom_count"]) for row in family_rows)
    fragment_plus_atoms_count = sum(
        row["support_tier"] == "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"
        for row in family_rows
    )
    nonexact_fragment_count = sum(
        int(row["old_exact_recipe_event_count"]) == 0
        and int(row["longest_old_complete_recipe_fragment_atoms"]) >= 2
        for row in family_rows
    )
    atom_only_count = sum(
        row["support_tier"] == "ATOMS_AND_FACTORS_ONLY" for row in family_rows
    )
    same_dy_pairs = sum(row["recipe_relation"] == "SAME_RECIPE" for row in dy_pair_rows)
    different_dy_pairs = len(dy_pair_rows) - same_dy_pairs
    new_order_rows = [
        row for row in transition_rows if str(row["thirty_page_decision"]).startswith("NEW_ORDER")
    ]
    new_direct_rows = [
        row
        for row in transition_rows
        if row["thirty_page_decision"] == "NEW_DIRECT_ADJACENCY__OLD_ORDER_ATTESTED"
    ]
    action_skeleton_recurrent = {
        skeleton: surfaces
        for skeleton, surfaces in action_groups.items()
        if skeleton != "NONE" and len(surfaces) >= 2
    }

    result = {
        "experiment_id": "GDT516",
        "status": STATUS,
        "guard": GUARD,
        "inputs": {
            "gdt515_new_surface_rows": len(new_rows),
            "gdt515_selected_events": len(selected_events),
            "running_events_30_pages": len(running30),
            "unified_groups_30_pages": len(unified30),
        },
        "family_compression": {
            "distinct_new_recipes": len({row["gdt516_context_recipe"] for row in family_rows}),
            "exact_old_complete_recipe_carriers": exact_count,
            "nonexact_surfaces_with_old_complete_recipe_fragment": nonexact_fragment_count,
            "partial_fragment_plus_atoms_surfaces": fragment_plus_atoms_count,
            "atoms_and_factors_only_surfaces": atom_only_count,
            "fully_tiled_by_old_multicomponent_recipes": fully_tiled,
            "covered_recipe_atoms": covered_atoms,
            "total_recipe_atoms": total_atoms,
            "covered_recipe_atom_fraction": round(covered_atoms / total_atoms, 6),
            "recurrent_nonempty_portable_skeleton_families": len(portable_family_rows),
            "surfaces_in_recurrent_portable_skeleton_families": sum(
                int(row["surface_count"]) for row in portable_family_rows
            ),
            "recurrent_nonempty_action_skeleton_families": len(action_skeleton_recurrent),
            "surfaces_in_recurrent_action_skeleton_families": sum(
                len(values) for values in action_skeleton_recurrent.values()
            ),
            "cross_selected_page_new_surfaces": [row["surface"] for row in cross_page_rows],
        },
        "context_policy": {
            "old_local_new_context_contacts": len(context_rows),
            "exact_agreements": sum(row["decision"] == "EXACT_RECIPE_AGREEMENT" for row in context_rows),
            "common_recipe_promotions": sum(
                row["decision"] == "COMMON_VISIBLE_RECIPE_PROMOTION" for row in context_rows
            ),
            "learned_label_shell_replays": sum(
                row["decision"] == "LEARNED_LABEL_SHELL_REPLAY" for row in context_rows
            ),
            "role_conditioned_homographs": sum(
                row["decision"] == "ROLE_CONDITIONED_HOMOGRAPH" for row in context_rows
            ),
            "new_portable_values": 0,
            "local_tags": len(local_tag_rows),
        },
        "dy_landscape": {
            "visible_dy_surface_types": len(dy_surfaces),
            "recipe_end_DY_surface_types": dy_class_counts["RECIPE_END_DY"],
            "recipe_end_Y_surface_types": dy_class_counts["RECIPE_END_Y"],
            "other_or_mixed_surface_types": dy_class_counts["OTHER_OR_MIXED"],
            "exact_dy_y_surface_pairs": len(dy_pair_rows),
            "same_recipe_pairs": same_dy_pairs,
            "different_recipe_pairs": different_dy_pairs,
        },
        "action_transitions": {
            "new_ordered_pair_occurrences": sum(new_order_events.values()),
            "new_ordered_pair_types": len(new_order_events),
            "new_direct_pair_occurrences": sum(new_direct_events.values()),
            "new_direct_pair_types": len(new_direct_events),
            "new_order_rows": new_order_rows,
            "new_direct_rows": new_direct_rows,
        },
        "interpretation": (
            "The four-page novelty is mostly productive recombination: ten full old recipe carriers, "
            "120 further surfaces containing a proper complete old recipe fragment, and only 29 "
            "requiring atom/factor support alone. The ten old-local contacts resolve with two common "
            "recipe promotions, one learned-label replay, four explicit role homographs, and three exact "
            "agreements. No new portable value is needed."
        ),
    }
    write_json(RESULT_OUT, result)

    family_lines = [
        "| portable skeleton | reading | surfaces | forms |",
        "|---|---|---:|---|",
    ]
    for row in portable_family_rows:
        family_lines.append(
            f"| `{row['portable_skeleton']}` | {row['portable_reading_de']} | "
            f"{row['surface_count']} | {row['surfaces']} |"
        )
    context_lines = [
        "| surface | decision | old context | new context |",
        "|---|---|---|---|",
    ]
    for row in context_rows:
        context_lines.append(
            f"| `{row['surface']}` | {row['decision']} | `{row['old_context_recipe']}` | "
            f"`{row['new_context_recipe']}` |"
        )
    open_lines = [
        "| surface | current recipe | decision |",
        "|---|---|---|",
    ]
    for row in open_rows:
        open_lines.append(
            f"| `{row['surface']}` | `{row['gdt516_recipe']}` | {row['decision']} |"
        )
    BOOK_OUT.write_text(
        "\n".join(
            [
                "# GDT516 thirty-page family book",
                "",
                "This is the compact working basis after admitting f31r, f66r, f20v and f4r. "
                "It is a compositional reading aid, not claimed plaintext.",
                "",
                "## Compression result",
                "",
                f"- 159 genuinely new surfaces, {exact_count} with a complete old recipe carrier.",
                f"- 120 more contain a proper complete old recipe as a contiguous fragment; {atom_only_count} use atom/factor support only.",
                f"- {fully_tiled} forms are fully tileable by disjoint older multi-atom recipes.",
                f"- {covered_atoms}/{total_atoms} recipe atoms ({covered_atoms / total_atoms:.2%}) receive that stronger old-recipe coverage.",
                f"- 20 recurrent nonempty portable skeletons cover {sum(int(row['surface_count']) for row in portable_family_rows)} forms.",
                f"- Cross-page anchors inside the new batch: {', '.join(row['surface'] for row in cross_page_rows)}.",
                "",
                "## Recurrent portable families",
                "",
                *family_lines,
                "",
                "## Old-local/new-context policy",
                "",
                *context_lines,
                "",
                "The four role-conditioned forms are finite homographs: the label and prose recipes "
                "remain explicit. They do not license a portable double meaning.",
                "",
                "## Six formerly open parses",
                "",
                *open_lines,
                "",
                "`LOCAL_X` deliberately unifies standalone and embedded x on f66r while assigning it "
                "no word meaning. `cthdy`, `okedam`, and `qocthedy` now have direct family support; "
                "`ykady` remains a transparent role-conditioned close choice.",
                "",
                "## Visible dy is not one automatic suffix",
                "",
                f"There are {len(dy_surfaces)} thirty-page surface types ending in visible `dy`: "
                f"{dy_class_counts['RECIPE_END_DY']} end in recipe atom `DY`, "
                f"{dy_class_counts['RECIPE_END_Y']} end in `Y`, and "
                f"{dy_class_counts['OTHER_OR_MIXED']} end otherwise. The 110 exact `…dy`/`…y` "
                f"surface pairs split into {same_dy_pairs} same-recipe and {different_dy_pairs} "
                "different-recipe pairs. Therefore a visible d before y must be decided by family/context.",
                "",
                "## New transition information",
                "",
                "After non-action slots are removed, the 159 forms contain 90 neighbouring action-head "
                "occurrences in 31 ordered pair types. Only `CHD→R` was absent from the old 26-page "
                "running deck; it now occurs in `chedaiir` and `fchedyr`. GDT427 had already marked "
                "that absent pair amber-allowed from typed f89r support. `SH→S` is the only newly direct "
                "adjacency, while its ordered relation was already established.",
                "",
                "## Default carried forward",
                "",
                "Use exact old complete recipes first; otherwise use the longest compatible old complete "
                "recipe fragments plus the visible control shell. Keep learned/local cores owner-bound. "
                "Apply the ten-row context table before treating a repeated surface as invariant. No new "
                "portable atom or lexical meaning is introduced here.",
                "",
                f"Status: `{STATUS}`.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
