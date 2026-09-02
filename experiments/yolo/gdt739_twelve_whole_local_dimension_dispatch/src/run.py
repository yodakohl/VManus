#!/usr/bin/env python3
"""Build GDT739's host-first local-dimension renderer.

Only complete GDT738 wholes at their 202 enumerated positions may render.  An
eligible neighbor within two cells may bind a scalar axis, favored state axis,
or broad carrier.  Distance three to five is retained as sensitivity evidence
but cannot change the spoken renderer.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G734 = Path("experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch")
COMPACT_REL = G734 / "artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
LINE_REL = G734 / "artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
G737 = Path("experiments/yolo/gdt737_held_body_record_role_transfer")
HELD_OCC_REL = G737 / "artifacts/HELD_811_OCCURRENCE_CONTEXTS.tsv"
G738 = Path("experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication")
G738_RUN_REL = G738 / "src/run.py"
PATCH_REL = G738 / "artifacts/OCCURRENCE_RENDERER_PATCH.tsv"
CARD_REL = G738 / "artifacts/ADJUDICATED_17_WHOLE_CARDS.tsv"

module_spec = importlib.util.spec_from_file_location("gdt738_builder", ROOT / G738_RUN_REL)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("cannot load GDT738 guarded cache helpers")
g738 = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(g738)

LICENSED_FORMS = (
    "lain", "lcheedy", "lcheol", "lkaiin", "lkain", "lkar", "lsheedy", "pcheol",
    "rain", "rsheedy", "sain", "skaiin",
)
SCALAR_FORMS = {"lain", "lkaiin", "lkain", "lkar", "rain", "sain", "skaiin"}
STATE_FORMS = set(LICENSED_FORMS) - SCALAR_FORMS
RETIRED_PATIENT_WORDS = ("pulver", "samen", "saat", "wurzel", "holz")
QUALITY_AXES = ("HOT", "COLD", "DRY", "MOIST")
CARRIER_AXES = ("PREPARATION", "MATERIAL", "PART")
SCALAR_CLASSES = ("QUALITY_DEGREE", "AMOUNT_DOSE", "PROCESS_PASS")
OUTPUT_NAMES = (
    "WINDOW_202_TOKEN_AUDIT.tsv",
    "DIMENSION_202_DISPATCH.tsv",
    "FORM_12_DISPATCH_PROFILE.tsv",
    "REPRESENTATIVE_PASSAGES.tsv",
    "GDT739_LOCAL_DIMENSION_READER.md",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_axis_specs() -> tuple[list[dict[str, str]], dict[str, re.Pattern[str]]]:
    rows = read_tsv(SRC / "ANCHOR_AXIS_SPECS.tsv")
    expected = [
        "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART", "MATERIAL",
        "PREPARATION", "PROCESS", "CLOSE", "PASS",
    ]
    if [row["axis_id"] for row in rows] != expected:
        raise AssertionError("anchor-axis specification changed")
    compiled = {
        row["axis_id"]: re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.IGNORECASE)
        for row in rows
    }
    return rows, compiled


def axes_for(text: str, patterns: dict[str, re.Pattern[str]]) -> tuple[str, ...]:
    return tuple(axis for axis, pattern in patterns.items() if pattern.search(text))


def retired_hits(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    return tuple(word for word in RETIRED_PATIENT_WORDS if word in lowered)


def strict_initial_head(surface: str) -> bool:
    return len(surface) > 1 and surface[0] in "psrl" and not surface.startswith("sh")


def ordinal_part(text: str) -> bool:
    lowered = text.lower()
    return bool(
        re.search(r"\b(?:erste|erster|erstes|zweite|zweiter|zweites|dritte|dritter|drittes|zwei|drei|i|ii|iii|iv)\b", lowered)
        and re.search(r"(?:teil|fraktion|portion)", lowered)
    )


def host_scalar_types(axis_tags: tuple[str, ...], text: str) -> tuple[str, ...]:
    tags = set(axis_tags)
    selected: list[str] = []
    if tags.intersection(QUALITY_AXES) and "VALUE" in tags:
        selected.append("QUALITY_DEGREE")
    if "AMOUNT" in tags or ordinal_part(text):
        selected.append("AMOUNT_DOSE")
    if "PASS" in tags:
        selected.append("PROCESS_PASS")
    return tuple(selected)


def min_distance(
    contacts: list[dict[str, object]], axis: str, radius: int = 2,
) -> int | None:
    values = [
        int(row["distance"])
        for row in contacts
        if int(row["eligible_local_anchor"]) and int(row["distance"]) <= radius
        and axis in str(row["axis_tags"]).split("|")
    ]
    return min(values) if values else None


def at_distance(
    contacts: list[dict[str, object]], axes: Iterable[str], distance: int | None,
) -> list[dict[str, object]]:
    wanted = set(axes)
    if distance is None:
        return []
    return [
        row for row in contacts
        if int(row["eligible_local_anchor"]) and int(row["distance"]) == distance
        and wanted.intersection(str(row["axis_tags"]).split("|"))
    ]


def evidence_text(rows: list[dict[str, object]], limit: int = 4) -> str:
    unique: list[str] = []
    for row in sorted(rows, key=lambda item: (int(item["distance"]), str(item["side"]), int(item["neighbor_ordinal"]))):
        value = (
            f"{row['side']}{row['distance']} {row['neighbor_surface']}="
            f"{row['neighbor_semantic_value_de']} [{row['axis_tags']}]"
        )
        if value not in unique:
            unique.append(value)
    return " || ".join(unique[:limit]) or "NONE"


def carrier_choice(
    contacts: list[dict[str, object]], radius: int = 2,
) -> tuple[str, int | None, list[dict[str, object]]]:
    distances = {axis: min_distance(contacts, axis, radius) for axis in CARRIER_AXES}
    present = {axis: value for axis, value in distances.items() if value is not None}
    if not present:
        return "OPEN", None, []
    distance = min(present.values())
    selected = tuple(axis for axis in CARRIER_AXES if present.get(axis) == distance)
    return "_".join(selected), distance, at_distance(contacts, selected, distance)


def carrier_genitive(carrier: str) -> str:
    return {
        "PREPARATION": "der Zubereitung",
        "MATERIAL": "des Materials",
        "PART": "der Teilfraktion",
        "PREPARATION_MATERIAL": "des Zubereitungsmaterials",
        "PREPARATION_PART": "der Zubereitungsfraktion",
        "MATERIAL_PART": "des Materialteils",
        "PREPARATION_MATERIAL_PART": "der Zubereitungsfraktion",
        "OPEN": "",
    }[carrier]


def bind_genitive(base: str, genitive: str) -> str:
    if not genitive:
        return base
    if "; " not in base:
        return f"{base} {genitive}"
    head, tail = base.split("; ", 1)
    return f"{head} {genitive}; {tail}"


def scalar_dispatch(
    contacts: list[dict[str, object]], radius: int = 2,
) -> tuple[str, int | None, list[dict[str, object]], tuple[str, ...]]:
    for distance in range(1, radius + 1):
        ring = [
            row for row in contacts
            if int(row["eligible_local_anchor"]) and int(row["distance"]) == distance
            and str(row["scalar_host_types"]) != "NONE"
        ]
        classes = tuple(sorted({
            dispatch for row in ring for dispatch in str(row["scalar_host_types"]).split("|")
        }))
        if not classes:
            continue
        if len(classes) == 1:
            return classes[0], distance, ring, classes
        return "OPEN_SCALAR_CONFLICT", distance, ring, classes
    return "OPEN_SCALAR", None, [], ()


def local_tier(distance: int | None) -> str:
    if distance == 1:
        return "DIRECT_R1"
    if distance == 2:
        return "NEAR_R2"
    return "OPEN_NO_SELECTING_R1_R2"


def quality_axes_from_rows(rows: list[dict[str, object]]) -> tuple[str, ...]:
    return tuple(
        axis for axis in QUALITY_AXES
        if any(axis in str(row["axis_tags"]).split("|") for row in rows)
    )


def quality_phrase(axes: tuple[str, ...], level: str) -> str:
    single = {
        "HOT": "Heißgrad", "COLD": "Kältegrad", "DRY": "Trockenheitsgrad", "MOIST": "Feuchtegrad",
    }
    if len(axes) == 1:
        return f"{single[axes[0]]} {level}"
    labels = {"HOT": "heiß", "COLD": "kalt", "DRY": "trocken", "MOIST": "feucht"}
    joined = "/".join(labels[axis] for axis in axes)
    return f"Qualitätsstufe {level} im {joined}-Feld"


def render_scalar(
    surface: str, position: str, level: str, dispatch: str,
    selecting_rows: list[dict[str, object]], carrier: str,
) -> str:
    if dispatch == "QUALITY_DEGREE":
        base = quality_phrase(quality_axes_from_rows(selecting_rows), level)
    elif dispatch == "AMOUNT_DOSE":
        base = f"Mengen-/Portionsstufe {level}"
    elif dispatch == "PROCESS_PASS":
        base = f"Verarbeitungsgang {level}"
    else:
        base = f"Skalarstufe {level}; Dimension offen"
    genitive = carrier_genitive(carrier)
    base = bind_genitive(base, genitive)
    if surface == "sain" and position == "FIRST":
        base += "; Eintrag"
    elif surface == "rain":
        base += "; Abschlussbezug" if position == "LAST" else "; interner Rückbezug"
    elif surface == "lain":
        prefix = "interner " if ("grad " in base.lower() or "gang " in base.lower()) else "interne "
        base = prefix + base
    elif surface == "skaiin" and position == "FIRST":
        base += "; Eintrag"
    return base


def state_mode(
    surface: str, locus: str, overrides: dict[tuple[str, str], dict[str, str]],
) -> tuple[str, str, str]:
    override = overrides.get((surface, locus))
    if override:
        return override["state_mode"], override["evidence_tier"], override["manual_reason"]
    if surface in ("lcheedy", "lsheedy", "rsheedy"):
        return "QUALITY_STATE", "DEFAULT_STATE", "no occurrence-specific result override"
    return "QUALITY_STATE", "DESCRIPTIVE_WHOLE", "cheol-family descriptive state field"


def render_state(
    surface: str, position: str, mode: str, favored_axis: str,
    axis_supported: bool, carrier: str,
) -> str:
    genitive = carrier_genitive(carrier)
    if surface in ("pcheol", "lcheol"):
        if axis_supported:
            base = "Trockenstatus"
        else:
            base = "Statusfeld; Zustandsachse offen"
        if position == "FIRST":
            base = "Trockenstatus-Eintrag" if axis_supported else "Status-Eintrag; Zustandsachse offen"
    else:
        if mode == "PROCESS_RESULT":
            if axis_supported and favored_axis == "DRY":
                base = "Trocken-Endstufe II"
            elif axis_supported:
                base = "Feucht-/Einweich-Endstufe II"
            else:
                base = "Resultat-/Endstufe II; Zustandsachse offen"
        else:
            if axis_supported and favored_axis == "DRY":
                base = "Trockenstufe II"
            elif axis_supported:
                base = "Feuchtstufe II"
            else:
                base = "Zustandsstufe II; Zustandsachse offen"
        if surface == "rsheedy":
            base += "; interner Rückbezug"
    if genitive:
        base = bind_genitive(base, genitive)
    elif surface in STATE_FORMS:
        base += "; Träger offen"
    return base


def make_window_rows(
    patches: list[dict[str, str]], occurrence_map: dict[str, dict[str, str]],
    by_line: dict[str, list[dict[str, str]]], exact: dict[tuple[str, int], int],
    cells: dict[tuple[str, int], dict[str, str]], patterns: dict[str, re.Pattern[str]],
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    targets = {
        (occurrence_map[row["occurrence_id"]]["locus"], int(occurrence_map[row["occurrence_id"]]["token_ordinal"]))
        for row in patches
    }
    rows: list[dict[str, object]] = []
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for patch in patches:
        occurrence = occurrence_map[patch["occurrence_id"]]
        locus = occurrence["locus"]
        ordinal = int(occurrence["token_ordinal"])
        line = by_line[locus]
        if line[ordinal - 1]["eva"] != patch["surface"] or cells[(locus, ordinal)]["surface"] != patch["surface"]:
            raise AssertionError(f"target surface mismatch: {patch['patch_id']}")
        for delta in (*range(-5, 0), *range(1, 6)):
            neighbor_ordinal = ordinal + delta
            if not 1 <= neighbor_ordinal <= len(line):
                continue
            token = line[neighbor_ordinal - 1]
            cell = cells[(locus, neighbor_ordinal)]
            if token["eva"] != cell["surface"]:
                raise AssertionError(f"raw/cache mismatch at {locus}:{neighbor_ordinal}")
            semantic = cell["v99r7_semantic_value_de"]
            tags = axes_for(semantic, patterns)
            scalar_types = host_scalar_types(tags, semantic)
            hits = retired_hits(semantic)
            reader_exact = exact[(locus, int(token["token_index"]))]
            initial_head = int(strict_initial_head(cell["surface"]))
            another_target = int((locus, neighbor_ordinal) in targets)
            known = int(cell["unknown_v99r7"] == "0")
            w23 = int(cell["gdt734_confidence_level"].startswith(("W2", "W3")))
            zero_composition = int(cell["gdt734_composition_semantic_credit"] == "0")
            eligible = int(
                reader_exact and not initial_head and not another_target and known and w23
                and zero_composition and not hits and bool(tags)
            )
            failures: list[str] = []
            if not reader_exact:
                failures.append("READER_VARIANT")
            if initial_head:
                failures.append("OPAQUE_INITIAL_HEAD")
            if another_target:
                failures.append("TARGET_CARD_CANNOT_SELF_ANCHOR")
            if not known:
                failures.append("UNKNOWN")
            if not w23:
                failures.append("BELOW_W2_OR_NA")
            if not zero_composition:
                failures.append("COMPOSITION_CREDIT")
            if hits:
                failures.append("RETIRED_LITERAL_PATIENT")
            if not tags:
                failures.append("NO_SELECTING_AXIS")
            row: dict[str, object] = {
                "window_id": f"G739-N{len(rows) + 1:05d}", "patch_id": patch["patch_id"],
                "occurrence_id": patch["occurrence_id"], "page": patch["page"], "locus": locus,
                "target_ordinal": ordinal, "target_surface": patch["surface"],
                "target_position": patch["line_position"], "side": "L" if delta < 0 else "R",
                "signed_offset": delta, "distance": abs(delta), "neighbor_ordinal": neighbor_ordinal,
                "neighbor_surface": cell["surface"], "neighbor_reader_exact": reader_exact,
                "neighbor_semantic_value_de": semantic,
                "neighbor_confidence_level": cell["gdt734_confidence_level"],
                "neighbor_unknown_v99r7": cell["unknown_v99r7"],
                "neighbor_composition_semantic_credit": cell["gdt734_composition_semantic_credit"],
                "strict_initial_head_neighbor": initial_head, "another_gdt738_target": another_target,
                "retired_patient_words": "|".join(hits) or "NONE",
                "axis_tags": "|".join(tags) or "NONE",
                "scalar_host_types": "|".join(scalar_types) or "NONE",
                "eligible_local_anchor": eligible, "ineligibility_reasons": "|".join(failures) or "NONE",
                "head_or_body_lexeme_credit": 0, "component_export_credit": 0,
            }
            rows.append(row)
            grouped[patch["patch_id"]].append(row)
    return rows, grouped


def dispatch_rows(
    patches: list[dict[str, str]], occurrence_map: dict[str, dict[str, str]],
    grouped: dict[str, list[dict[str, object]]], whole_specs: dict[str, dict[str, str]],
    overrides: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for patch in patches:
        occurrence = occurrence_map[patch["occurrence_id"]]
        contacts = grouped[patch["patch_id"]]
        surface = patch["surface"]
        spec = whole_specs[surface]
        carrier, carrier_distance, carrier_rows = carrier_choice(contacts)
        state_class = "NOT_APPLICABLE"
        state_grade = "NOT_APPLICABLE"
        state_reason = "NOT_APPLICABLE"
        favored_axis = spec["favored_axis_not_automatic"]
        axis_supported = 0
        scalar_rivals: tuple[str, ...] = ()

        if surface in SCALAR_FORMS:
            dispatch, selecting_distance, selecting_rows, scalar_rivals = scalar_dispatch(contacts)
            render = render_scalar(
                surface, patch["line_position"], spec["level"], dispatch, selecting_rows, carrier
            )
            axis_specific = int(dispatch in SCALAR_CLASSES)
        else:
            state_class, state_grade, state_reason = state_mode(surface, patch["locus"], overrides)
            favored_distance = min_distance(contacts, favored_axis)
            favored_rows = at_distance(contacts, (favored_axis,), favored_distance)
            axis_supported = int(favored_distance is not None)
            dispatch = (
                f"{state_class}_{favored_axis}_LOCAL" if axis_supported
                else f"{state_class}_AXIS_OPEN"
            )
            selecting_distance = favored_distance
            selecting_rows = favored_rows
            render = render_state(
                surface, patch["line_position"], state_class, favored_axis, bool(axis_supported), carrier
            )
            axis_specific = axis_supported

        eligible = [row for row in contacts if int(row["eligible_local_anchor"])]
        radius_flags = {
            radius: int(any(int(row["distance"]) <= radius for row in eligible))
            for radius in (1, 2, 3, 5)
        }
        axis_counts = Counter(
            axis for row in eligible if int(row["distance"]) <= 2
            for axis in str(row["axis_tags"]).split("|")
        )
        relevant_distance = min(
            [value for value in (selecting_distance, carrier_distance) if value is not None], default=None
        )
        tier = local_tier(relevant_distance)
        if relevant_distance is None and state_class == "PROCESS_RESULT":
            tier = state_grade
        selecting_union = list({str(row["window_id"]): row for row in selecting_rows + carrier_rows}.values())
        competing = [
            row for row in eligible if int(row["distance"]) <= 2
            and str(row["window_id"]) not in {str(item["window_id"]) for item in selecting_union}
        ]
        specific = int(axis_specific or carrier != "OPEN" or state_class == "PROCESS_RESULT")
        output.append({
            "dispatch_id": f"G739-D{len(output) + 1:04d}", "patch_id": patch["patch_id"],
            "occurrence_id": patch["occurrence_id"], "page": patch["page"], "locus": patch["locus"],
            "token_index": patch["token_index"], "token_ordinal": occurrence["token_ordinal"],
            "surface": surface, "body": patch["body"], "opaque_head_id": patch["opaque_head_id"],
            "line_position": patch["line_position"], "family": spec["family"], "level": spec["level"],
            "favored_axis_not_automatic": favored_axis,
            "gdt738_render_de": patch["gdt738_scoped_whole_render_de"],
            "dimension_dispatch": dispatch,
            "scalar_rival_classes": "|".join(scalar_rivals) or "NONE",
            "state_mode": state_class, "state_mode_evidence_tier": state_grade,
            "state_mode_reason": state_reason, "favored_axis_locally_supported": axis_supported,
            "carrier_dispatch": carrier,
            "selecting_anchor_distance": selecting_distance if selecting_distance is not None else "NA",
            "carrier_anchor_distance": carrier_distance if carrier_distance is not None else "NA",
            "dispatch_evidence_tier": tier,
            "eligible_anchor_r1": radius_flags[1], "eligible_anchor_r2": radius_flags[2],
            "eligible_anchor_r3": radius_flags[3], "eligible_anchor_r5": radius_flags[5],
            "eligible_anchor_count_r2": sum(int(row["distance"]) <= 2 for row in eligible),
            "eligible_anchor_count_r3": sum(int(row["distance"]) <= 3 for row in eligible),
            "eligible_anchor_count_r5": len(eligible),
            "r2_axis_counts": "|".join(f"{key}:{axis_counts[key]}" for key in sorted(axis_counts)) or "NONE",
            "selecting_evidence": evidence_text(selecting_union),
            "competing_local_evidence": evidence_text(competing),
            "gdt739_working_render_de": render, "specific_local_dispatch": specific,
            "axis_specific_dispatch": axis_specific, "carrier_locally_bound": int(carrier != "OPEN"),
            "scope": "EXACT_COMPLETE_SURFACE_AT_THIS_ENUMERATED_OCCURRENCE",
            "literal_patient_or_species_claimed": 0, "literal_plaintext_claimed": 0,
            "unconditional_global_export": 0, "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0, "unseen_form_export": 0,
        })
    return output


def profile_rows(
    dispatches: list[dict[str, object]], cards: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dispatches:
        grouped[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in LICENSED_FORMS:
        rows = grouped[surface]
        decisions = Counter(str(row["dimension_dispatch"]) for row in rows)
        carriers = Counter(str(row["carrier_dispatch"]) for row in rows)
        tiers = Counter(str(row["dispatch_evidence_tier"]) for row in rows)
        renders = Counter(str(row["gdt739_working_render_de"]) for row in rows)
        card = cards[surface]
        output.append({
            "surface": surface, "opaque_head_id": card["opaque_head_id"], "body": card["body"],
            "gdt738_card_confidence": card["confidence"], "patched_occurrences": len(rows),
            "specific_local_dispatches": sum(int(row["specific_local_dispatch"]) for row in rows),
            "axis_specific_dispatches": sum(int(row["axis_specific_dispatch"]) for row in rows),
            "carrier_bound_dispatches": sum(int(row["carrier_locally_bound"]) for row in rows),
            "fully_open_dispatches": sum(not int(row["specific_local_dispatch"]) for row in rows),
            "direct_r1": tiers["DIRECT_R1"], "near_r2": tiers["NEAR_R2"],
            "manual_endpoint_best_fit": tiers["ENDPOINT_BEST_FIT"],
            "open_no_selecting_r1_r2": tiers["OPEN_NO_SELECTING_R1_R2"],
            "dimension_dispatch_counts": "|".join(f"{key}:{decisions[key]}" for key in sorted(decisions)),
            "carrier_dispatch_counts": "|".join(f"{key}:{carriers[key]}" for key in sorted(carriers)),
            "distinct_occurrence_renders": len(renders),
            "most_common_render_de": renders.most_common(1)[0][0],
            "positive_evidence": card["positive_evidence"], "counterevidence": card["counterevidence"],
            "global_lexeme_export": 0, "component_export_credit": 0,
        })
    return output


def safe_line_render(
    locus: str, cells_by_locus: dict[str, list[dict[str, str]]],
    dispatch_by_position: dict[tuple[str, int], dict[str, object]],
) -> str:
    units: list[str] = []
    for cell in cells_by_locus[locus]:
        key = (locus, int(cell["token_ordinal"]))
        if key in dispatch_by_position:
            units.append(str(dispatch_by_position[key]["gdt739_working_render_de"]))
            continue
        role = cell["practical_unit_role"]
        if role == "SPAN_COMPANION_SUPPRESSED":
            continue
        if role == "ATTACH_PREVIOUS_NO_UNIT":
            if units:
                units[-1] += cell["surface"]
            continue
        value = cell["v99r7_practical_render_once_de"]
        safe = (
            cell["unknown_v99r7"] == "0"
            and cell["gdt734_confidence_level"].startswith(("W2", "W3"))
            and cell["gdt734_composition_semantic_credit"] == "0"
            and not retired_hits(value)
            and not strict_initial_head(cell["surface"])
        )
        units.append(value if safe else f"[{cell['surface']}:?]")
    return "; ".join(units)


def representative_passages(
    dispatches: list[dict[str, object]], line_map: dict[str, dict[str, str]],
    cells_by_locus: dict[str, list[dict[str, str]]], specs: list[dict[str, str]],
) -> list[dict[str, object]]:
    dispatch_by_position = {
        (str(row["locus"]), int(row["token_ordinal"])): row for row in dispatches
    }
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dispatches:
        by_locus[str(row["locus"])].append(row)
    output: list[dict[str, object]] = []
    for spec in specs:
        wanted = spec["focal_surfaces"].split("|")
        targets = [row for row in by_locus[spec["locus"]] if str(row["surface"]) in wanted]
        if Counter(str(row["surface"]) for row in targets) != Counter(wanted):
            raise AssertionError(f"representative target mismatch: {spec['passage_id']}")
        targets.sort(key=lambda row: int(row["token_ordinal"]))
        line = line_map[spec["locus"]]
        output.append({
            "passage_id": spec["passage_id"], "page": line["page"], "locus": spec["locus"],
            "section": line["section"], "language": line["language"],
            "focal_surfaces": spec["focal_surfaces"], "selection_reason": spec["selection_reason"],
            "zl3b_line": line["zl3b_line"],
            "gdt739_target_renders_de": " || ".join(
                f"{row['surface']} → {row['gdt739_working_render_de']}" for row in targets
            ),
            "dimension_dispatches": " || ".join(
                f"{row['surface']}={row['dimension_dispatch']}" for row in targets
            ),
            "selecting_evidence": " || ".join(
                f"{row['surface']}: {row['selecting_evidence']}" for row in targets
            ),
            "gdt739_safe_line_render_de": safe_line_render(spec["locus"], cells_by_locus, dispatch_by_position),
            "reader_note": "unsupported, opaque-head or retired-patient cells are shown as [surface:?]",
        })
    return output


def write_reader(path: Path, passages: list[dict[str, object]], profiles: list[dict[str, object]]) -> None:
    lines = [
        "# GDT739 local-dimension reader", "",
        "These are occurrence-scoped working renders, not plaintext translations. The invariant",
        "core is a form class and, where available, an ordered level. A quality, amount, process",
        "or broad carrier is spoken only from an eligible host within two cells. Unsupported",
        "or retired powder/seed/root/wood patients are printed as `[surface:?]`.", "",
        "## Twelve-form profile", "",
        "| whole | occurrences | axis-specific | carrier-bound | fully open | common render |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in profiles:
        lines.append(
            f"| `{row['surface']}` | {row['patched_occurrences']} | {row['axis_specific_dispatches']} | "
            f"{row['carrier_bound_dispatches']} | {row['fully_open_dispatches']} | {row['most_common_render_de']} |"
        )
    lines.extend(["", "## Twenty representative cached lines", ""])
    for row in passages:
        lines.extend([
            f"### {row['passage_id']} — {row['locus']} ({row['section']}/{row['language']})", "",
            f"- EVA line: `{row['zl3b_line']}`",
            f"- Targets: **{row['gdt739_target_renders_de']}**",
            f"- Local evidence: {row['selecting_evidence']}",
            f"- Safe line render: {row['gdt739_safe_line_render_de']}", "",
        ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    _, patterns = load_axis_specs()
    whole_rows = read_tsv(SRC / "WHOLE_DISPATCH_SPECS.tsv")
    whole_specs = {row["surface"]: row for row in whole_rows}
    if len(whole_specs) != 12 or set(whole_specs) != set(LICENSED_FORMS):
        raise AssertionError("whole-dispatch specification must equal the twelve GDT738 forms")
    overrides_rows = read_tsv(SRC / "STATE_RESULT_OVERRIDES.tsv")
    overrides = {(row["surface"], row["locus"]): row for row in overrides_rows}
    if len(overrides) != 8 or Counter(row["surface"] for row in overrides_rows) != Counter({"lcheedy": 4, "lsheedy": 3, "rsheedy": 1}):
        raise AssertionError("state-result override deck changed")
    passage_specs = read_tsv(SRC / "PASSAGE_SELECTION_SPECS.tsv")
    if len(passage_specs) != 20 or len({row["passage_id"] for row in passage_specs}) != 20:
        raise AssertionError("representative-passage deck changed")

    patches = read_tsv(ROOT / PATCH_REL)
    occurrences = read_tsv(ROOT / HELD_OCC_REL)
    occurrence_map = {row["occurrence_id"]: row for row in occurrences}
    card_rows = [row for row in read_tsv(ROOT / CARD_REL) if row["w23_renderer_license"] == "1"]
    cards = {row["surface"]: row for row in card_rows}
    if len(patches) != 202 or set(cards) != set(LICENSED_FORMS) or set(row["surface"] for row in patches) != set(LICENSED_FORMS):
        raise AssertionError("GDT738 twelve-form/202-patch boundary changed")
    if Counter(row["surface"] in SCALAR_FORMS for row in patches) != Counter({True: 172, False: 30}):
        raise AssertionError("172 scalar / 30 state occurrence boundary changed")
    if any(row["page"].startswith("f84") for row in patches):
        raise AssertionError("sealed page entered GDT739 target")

    by_line, exact, guards = g738.token_context()
    cells = g738.compact_cells()
    compact_rows = list(cells.values())
    cells_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in compact_rows:
        cells_by_locus[row["locus"]].append(row)
    for rows in cells_by_locus.values():
        rows.sort(key=lambda item: int(item["token_ordinal"]))
    line_rows = read_tsv(ROOT / LINE_REL)
    line_map = {row["locus"]: row for row in line_rows}

    windows, grouped = make_window_rows(patches, occurrence_map, by_line, exact, cells, patterns)
    dispatches = dispatch_rows(patches, occurrence_map, grouped, whole_specs, overrides)
    profiles = profile_rows(dispatches, cards)
    passages = representative_passages(dispatches, line_map, cells_by_locus, passage_specs)

    write_tsv(output_dir / "WINDOW_202_TOKEN_AUDIT.tsv", windows, list(windows[0]))
    write_tsv(output_dir / "DIMENSION_202_DISPATCH.tsv", dispatches, list(dispatches[0]))
    write_tsv(output_dir / "FORM_12_DISPATCH_PROFILE.tsv", profiles, list(profiles[0]))
    write_tsv(output_dir / "REPRESENTATIVE_PASSAGES.tsv", passages, list(passages[0]))
    write_reader(output_dir / "GDT739_LOCAL_DIMENSION_READER.md", passages, profiles)

    scalar_rows = [row for row in dispatches if row["surface"] in SCALAR_FORMS]
    state_rows = [row for row in dispatches if row["surface"] in STATE_FORMS]
    scalar_counts = Counter(str(row["dimension_dispatch"]) for row in scalar_rows)
    state_mode_counts = Counter(str(row["state_mode"]) for row in state_rows)
    tier_counts = Counter(str(row["dispatch_evidence_tier"]) for row in dispatches)
    carrier_counts = Counter(str(row["carrier_dispatch"]) for row in dispatches)
    eligible = [row for row in windows if int(row["eligible_local_anchor"])]
    target_radius = {
        str(radius): sum(
            any(int(row["eligible_local_anchor"]) and int(row["distance"]) <= radius for row in grouped[patch["patch_id"]])
            for patch in patches
        )
        for radius in (1, 2, 3, 5)
    }
    result: dict[str, object] = {
        "schema": "GDT739_TWELVE_WHOLE_LOCAL_DIMENSION_DISPATCH_V1",
        "status": (
            "PARTIAL__202_HOST_FIRST_OCCURRENCE_DISPATCHES__FORM_CLASS_AND_LEVEL_CORE__"
            "RADIUS_TWO_AXIS_OR_CARRIER_BINDING__RADIUS_THREE_TO_FIVE_DISCOVERY_ONLY__"
            "CHEEDY_SHEEDY_RESULT_DEFAULT_DOWNGRADED__EIGHT_LOCAL_RESULT_OVERRIDES__"
            "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
        ),
        "scope": {
            "inherited_allowlist_pages": guards["allowed_pages"], "target_pages": len({row["page"] for row in patches}),
            "target_loci": len({row["locus"] for row in patches}), "new_pages_used": 0,
            "f84_used": False, "f84r_used": False,
            "guard_stats": {"tokens": guards["tokens"], "cross": guards["cross"]},
        },
        "target": {
            "licensed_complete_forms": 12, "position_scoped_occurrences": 202,
            "scalar_occurrences": len(scalar_rows), "state_occurrences": len(state_rows),
        },
        "window": {
            "audited_radius": 5, "active_dispatch_radius": 2,
            "audited_neighbor_tokens": len(windows), "eligible_anchor_contacts": len(eligible),
            "targets_with_anchor_by_radius": target_radius,
        },
        "dispatch": {
            "scalar_classes": dict(sorted(scalar_counts.items())),
            "state_mode_counts": dict(sorted(state_mode_counts.items())),
            "favored_state_axis_locally_supported": sum(int(row["favored_axis_locally_supported"]) for row in state_rows),
            "carrier_classes": dict(sorted(carrier_counts.items())),
            "evidence_tiers": dict(sorted(tier_counts.items())),
            "axis_specific_occurrences": sum(int(row["axis_specific_dispatch"]) for row in dispatches),
            "carrier_bound_occurrences": sum(int(row["carrier_locally_bound"]) for row in dispatches),
            "fully_open_occurrences": sum(not int(row["specific_local_dispatch"]) for row in dispatches),
            "strong_local_result_overrides": 2, "endpoint_best_fit_result_overrides": 6,
        },
        "interpretive_update": {
            "invariant_core": "complete-whole field class and ordered level only",
            "scalar": "quality degree, amount/portion, or counted process passage only from an eligible radius-two host",
            "heat_dry_moist_part": "GDT738 family orientations remain candidate priors but are no longer spoken automatically",
            "cheol": "descriptive state field; dry is spoken only with a local dry host",
            "cheedy_sheedy": "state level II by default; result/end level only at eight enumerated loci",
            "carrier": "broad material/preparation/part class only; no substance or species name",
        },
        "claims": {
            "confirmed_lexemes": 0, "plaintext_translations_claimed": 0, "species_or_substances_named": 0,
            "head_or_body_lexeme_credit": 0, "component_export_credit": 0, "unseen_forms_predicted": 0,
        },
        "artifact_rows": {
            "WINDOW_202_TOKEN_AUDIT.tsv": len(windows), "DIMENSION_202_DISPATCH.tsv": len(dispatches),
            "FORM_12_DISPATCH_PROFILE.tsv": len(profiles), "REPRESENTATIVE_PASSAGES.tsv": len(passages),
            "GDT739_LOCAL_DIMENSION_READER.md": len(passages),
        },
        "artifact_hashes": {
            str(BASE_REL / "artifacts" / name): sha256(output_dir / name) for name in OUTPUT_NAMES
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "schema": result["schema"], "status": result["status"], "window": result["window"],
        "dispatch": result["dispatch"], "artifact_rows": result["artifact_rows"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
