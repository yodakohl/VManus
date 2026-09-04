#!/usr/bin/env python3
"""Build GDT794: complete-label multiform transfer over admitted circle arrays."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt794_complete_label_multiform_slot_transfer"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
LOCK = SRC / "SOURCE_LOCK.tsv"
MODEL_SPECS = SRC / "CANDIDATE_MODEL_SPECS.tsv"
G791 = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine"
SPINE = G791 / "artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
PAGE_SPECS = G791 / "src/PAGE_SELECTOR_SPECS.tsv"
CIRCLES = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
G793_SLOT4 = ROOT / "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/artifacts/GDT793_5_OUTER_SLOT4_SERIES.tsv"
V99R7 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"

OUTPUT_NAMES = (
    "GDT794_216_ADMITTED_CIRCLE_LABEL_ATLAS.tsv",
    "GDT794_15_REPEATED_COMPLETE_LABEL_DEFAULTS.tsv",
    "GDT794_CROSS_FOLIO_LOFO_PREDICTIONS.tsv",
    "GDT794_4_COORDINATE_MODEL_SCORES.tsv",
    "GDT794_KLUGE_A_LABEL_GRID.tsv",
    "GDT794_30_KLUGE_HOMOLOG_SUMMARY.tsv",
    "GDT794_5_RAW_SLOT4_CORRECTION.tsv",
    "GDT794_RELATIONAL_PAIR_CAPACITY.tsv",
    "GDT794_CANDIDATE_ADJUDICATION.tsv",
    "GDT794_4_OTODY_POSITION_RIVAL.tsv",
    "GDT794_15_REPEATED_CROSS_SCOPE_DICTIONARY_AUDIT.tsv",
    "GDT794_216_CIRCLE_LABEL_SEQUENCE_OVERRIDES.tsv",
    "RESULT.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    materialized = list(rows)
    fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source_lock() -> None:
    rows = read_tsv(LOCK)
    if not rows or len({row["path"] for row in rows}) != len(rows):
        raise RuntimeError("source lock missing, empty, or duplicated")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"invalid source-lock path: {row['path']}")
        path = ROOT / relative
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def parse_clock(comment: str) -> float | None:
    match = re.search(r"\bat\s+(\d{1,2})[:.](\d{2})", comment, flags=re.IGNORECASE)
    if not match:
        return None
    return (int(match.group(1)) % 12) + int(match.group(2)) / 60.0


def parse_kluge(comment: str) -> int | None:
    match = re.search(r"Kluge.s\s+(\d+)A", comment)
    return int(match.group(1)) if match else None


def parse_grove(comment: str) -> int | None:
    match = re.search(r"Grove.s\s+#(\d+)", comment)
    return int(match.group(1)) if match else None


def array_class(description: str) -> str:
    lower = description.lower()
    if "star/nymph" in lower:
        return "ZODIAC_STAR_NYMPH_BAND"
    if "moon" in lower:
        return "MOON_RING"
    if "logs" in lower:
        return "RADIAL_LOG_RING"
    if "star" in lower:
        return "STAR_OR_CENTRAL_RING"
    if "radial" in lower:
        return "RADIAL_RING"
    return "OTHER_CIRCLE_ARRAY"


def surface_family(surface: str) -> str:
    compact = surface.replace(" ", "")
    for prefix, name in (
        ("okal", "OKAL_PREFIX"),
        ("otal", "OTAL_PREFIX"),
        ("ok", "OTHER_OK_PREFIX"),
        ("ot", "OTHER_OT_PREFIX"),
        ("o", "OTHER_O_PREFIX"),
    ):
        if compact.startswith(prefix):
            return name
    return "OTHER_INITIAL"


def circular_distance(a: float, b: float, period: float) -> float:
    delta = abs((a - b) % period)
    return min(delta, period - delta)


def circular_mean(values: list[float], period: float) -> float:
    if not values:
        raise ValueError("circular mean needs values")
    x = sum(math.cos(2 * math.pi * value / period) for value in values)
    y = sum(math.sin(2 * math.pi * value / period) for value in values)
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return min(value % period for value in values)
    return (math.atan2(y, x) * period / (2 * math.pi)) % period


def circular_span(values: list[float], period: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    ordered = sorted(value % period for value in values)
    gaps = [ordered[index + 1] - ordered[index] for index in range(len(ordered) - 1)]
    gaps.append(ordered[0] + period - ordered[-1])
    return period - max(gaps)


def joined(values: Iterable[Any], numeric: bool = False) -> str:
    material = list(values)
    if numeric:
        return "|".join(f"{float(value):.6f}" for value in material) if material else "NONE"
    return "|".join(str(value) for value in material) if material else "NONE"


def f6(value: float | None) -> str:
    return "NA" if value is None else f"{value:.6f}"


def hypergeom_upper(population: int, successes: int, draws: int, observed: int) -> float:
    denominator = math.comb(population, draws)
    total = 0
    for hit in range(observed, min(successes, draws) + 1):
        misses = draws - hit
        if 0 <= misses <= population - successes:
            total += math.comb(successes, hit) * math.comb(population - successes, misses)
    return total / denominator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    page_specs = read_tsv(PAGE_SPECS)
    if len(page_specs) != 35 or len({row["physical_page"] for row in page_specs}) != 30:
        raise RuntimeError("GDT791 admitted page scope changed")

    spine = read_tsv(SPINE)
    circles = read_tsv(CIRCLES)
    slot4_predecessor = read_tsv(G793_SLOT4)
    dictionary_rows = read_tsv(V99R7)
    dictionary = {row["surface"]: row for row in dictionary_rows}
    licensed_dictionary_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary_rows:
        if row["unconditional_global_export_allowed"] == "1":
            licensed_dictionary_rows[row["surface"]].append(row)
    model_specs = {row["model_id"]: row for row in read_tsv(MODEL_SPECS)}

    local_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    running: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL":
            local_by_locus[row["locus"]].append(row)
        elif row["occurrence_kind"] == "RUNNING_EVENT":
            running[row["surface"]].append(row)
    for rows in local_by_locus.values():
        rows.sort(key=lambda row: (int(row["token_ordinal_in_line"]), int(row["occurrence_ordinal"])))

    atlas: list[dict[str, Any]] = []
    for circle in circles:
        cells = local_by_locus.get(circle["locus"], [])
        if not cells:
            continue
        selectors = {row["source_selector"] for row in cells}
        if selectors != {circle["page"]}:
            raise RuntimeError(f"selector mismatch at {circle['locus']}: {selectors}")
        surface = " ".join(row["surface"] for row in cells)
        clock = parse_clock(circle["local_comment"])
        kluge = parse_kluge(circle["local_comment"])
        grove = parse_grove(circle["local_comment"])
        slot_index = int(circle["slot_index"])
        slot_count = int(circle["slot_count"])
        atlas.append(
            {
                "admitted_slot_ordinal": len(atlas) + 1,
                "array_index": circle["array_index"],
                "array_id": circle["array_id"],
                "array_class": array_class(circle["unit_description"]),
                "physical_folio": circle["physical_folio"],
                "source_selector": circle["page"],
                "unit": circle["unit"],
                "locus": circle["locus"],
                "complete_label_surface": surface,
                "label_token_count": len(cells),
                "surface_family": surface_family(surface),
                "slot_index": slot_index,
                "slot_count": slot_count,
                "source_slot_fraction": f"{(slot_index - 1) / slot_count:.6f}",
                "visible_clock_hour": f6(clock),
                "axis_folded_clock_hour": f6(clock % 6.0 if clock is not None else None),
                "kluge_a_member": str(kluge) if kluge is not None else "NA",
                "grove_member": str(grove) if grove is not None else "NA",
                "unit_description": circle["unit_description"],
                "local_comment": circle["local_comment"],
                "coordinate_semantics": "SOURCE_ORDER__VISIBLE_ANGLE__AXIS_CLASS__KLUGE_HOMOLOG_SEPARATE",
                "component_export_credit": "ZERO",
            }
        )

    if len(atlas) != 216:
        raise RuntimeError(f"expected 216 admitted circle slots, found {len(atlas)}")
    write_tsv(out / OUTPUT_NAMES[0], atlas)

    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_array: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in atlas:
        by_surface[str(row["complete_label_surface"])].append(row)
        by_array[str(row["array_id"])].append(row)
    repeated = {surface: rows for surface, rows in by_surface.items() if len(rows) >= 2}
    if len(repeated) != 15:
        raise RuntimeError(f"expected 15 repeated complete labels, found {len(repeated)}")

    default_rows: list[dict[str, Any]] = []
    concrete_forms: list[str] = []
    for surface in sorted(repeated):
        rows = repeated[surface]
        arrays = sorted({str(row["array_id"]) for row in rows})
        folios = sorted({str(row["physical_folio"]) for row in rows})
        clocks = [float(row["visible_clock_hour"]) for row in rows if row["visible_clock_hour"] != "NA"]
        kluges = [float(int(str(row["kluge_a_member"])) % 30) for row in rows if row["kluge_a_member"] != "NA"]
        fractions = [float(row["source_slot_fraction"]) for row in rows]
        collision_arrays = sorted(
            array_id for array_id in arrays
            if sum(str(row["array_id"]) == array_id for row in rows) > 1
        )
        run_rows = running.get(surface, []) if " " not in surface else []
        clock_span = circular_span(clocks, 12.0)
        axis_span = circular_span([clock % 6.0 for clock in clocks], 6.0)
        kluge_span = circular_span(kluges, 30.0)
        fraction_span = max(fractions) - min(fractions)
        concrete = (
            len(folios) >= 2 and len(clocks) == len(rows)
            and clock_span is not None and clock_span <= 0.75 and not collision_arrays
        )

        if surface == "okal":
            model = "UPPER_SECTOR_ENTRY_CLASS_RIVAL"
            display = "KENNSTELLEN-/SYSTEMEINTRAGSCODE; oberer Kreissektor als Rival (11:30–1:15)"
            confidence = "C0_RETAINED_WHOLE_RIVAL"
            license_state = "GDT793_C0_RETAINED__NO_COMPONENT_EXPORT"
        elif concrete:
            mean_clock = circular_mean(clocks, 12.0)
            model = "NARROW_VISIBLE_TIME_OR_DEGREE_POSITION"
            display = f"oberes rechtes Zeit-/Gradfeld (sichtbar um {mean_clock:.2f} Uhr)"
            confidence = "C0_PRIORITY_COMPLETE_WHOLE_CANDIDATE"
            license_state = "C0_POSITION_RIVAL_EXACT_WHOLE_ONLY"
            concrete_forms.append(surface)
        elif surface == "otalaiin":
            model = "EARLY_INNER_FIVE_MEMBER_WINDOW"
            display = "früher innerer Fünfer-Zyklusplatz (sichtbar Stelle 2–3)"
            confidence = "C0_REPLACEABLE_COMPLETE_WHOLE"
            license_state = "NO_ACTIVE_RENDERER__CANDIDATE_ONLY"
        elif collision_arrays:
            model = "REPEATED_ENTRY_CLASS_NOT_UNIQUE_POSITION"
            display = "wiederkehrende Kreiseintragsklasse; kein einzelner Platz"
            confidence = "C0_STRUCTURAL_DEFAULT"
            license_state = "NO_ACTIVE_RENDERER__CLASS_DEFAULT_ONLY"
        elif len(folios) >= 2:
            model = "CROSS_FOLIO_LEARNED_ENTRY_NO_FIXED_POSITION"
            display = "gelernter Kreiseintrag; Position wechselt zwischen Folios"
            confidence = "C0_STRUCTURAL_DEFAULT"
            license_state = "NO_ACTIVE_RENDERER__CLASS_DEFAULT_ONLY"
        elif len(arrays) >= 2:
            model = "LOCAL_MULTI_ARRAY_ENTRY_NO_TRANSFER"
            display = "lokaler Kreiseintrag über mehrere Ringe; Transfer offen"
            confidence = "C0_STRUCTURAL_DEFAULT"
            license_state = "NO_ACTIVE_RENDERER__CLASS_DEFAULT_ONLY"
        else:
            model = "WITHIN_ARRAY_REPEATED_ENTRY"
            display = "wiederholter Eintrag innerhalb desselben Kreises"
            confidence = "C0_STRUCTURAL_DEFAULT"
            license_state = "NO_ACTIVE_RENDERER__CLASS_DEFAULT_ONLY"

        occurrence_evidence = joined(
            f"{row['physical_folio']}:{row['array_id']}:slot{row['slot_index']}:clock{row['visible_clock_hour']}:K{row['kluge_a_member']}"
            for row in rows
        )
        if collision_arrays:
            counter = "same-array collision at " + joined(collision_arrays)
        elif concrete:
            counter = "only two cross-folio labels; prose uses do not independently identify a coordinate"
        else:
            counter = "positions diverge or do not provide a cross-folio coordinate key"
        default_rows.append(
            {
                "complete_label_surface": surface,
                "circle_occurrence_count": len(rows),
                "array_count": len(arrays),
                "physical_folio_count": len(folios),
                "arrays": joined(arrays),
                "physical_folios": joined(folios),
                "clock_positions": joined(clocks, numeric=True),
                "smallest_clock_arc_hours": f6(clock_span),
                "smallest_axis_folded_arc_hours": f6(axis_span),
                "kluge_a_positions": joined(int(value) if value else 30 for value in kluges),
                "smallest_kluge_arc_members": f6(kluge_span),
                "source_slot_linear_range_fraction": f6(fraction_span),
                "same_array_collision": "YES" if collision_arrays else "NO",
                "collision_arrays": joined(collision_arrays),
                "running_occurrence_count": len(run_rows),
                "running_physical_pages": len({row["physical_page"] for row in run_rows}),
                "best_observed_model": model,
                "working_default_de": display,
                "confidence": confidence,
                "evidence": occurrence_evidence,
                "counterevidence": counter,
                "renderer_license": license_state,
                "component_export_credit": "ZERO",
                "confirmed_lexeme": "NO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[1], default_rows)

    defaults_by_surface = {row["complete_label_surface"]: row for row in default_rows}
    cross_scope_audit: list[dict[str, Any]] = []
    for surface in sorted(repeated):
        rows = repeated[surface]
        old = dictionary.get(surface)
        running_rows = running.get(surface, [])
        if surface == "okal":
            decision = "OLD_PHARMA_READING_ALREADY_SUPERSEDED_BY_GDT793"
        elif old and old["unconditional_global_export_allowed"] == "1":
            decision = "HOLD_UNIVERSAL_PHARMA_READING__STANDALONE_CELESTIAL_LABEL_CONFLICT"
        else:
            decision = "NO_UNIVERSAL_V99R7_READING_TO_QUARANTINE"
        cross_scope_audit.append(
            {
                "complete_label_surface": surface,
                "circle_label_occurrence_count": len(rows),
                "circle_physical_folio_count": len({row["physical_folio"] for row in rows}),
                "circle_arrays": joined(sorted({row["array_id"] for row in rows})),
                "released_running_occurrence_count": len(running_rows),
                "released_running_physical_pages": len({row["physical_page"] for row in running_rows}),
                "v99r7_entry_present": "YES" if old else "NO",
                "v99r7_previous_working_meaning_de": old["v99r7_spoken_default_de"] if old else "NONE",
                "v99r7_previous_confidence": old["working_model_level"] if old else "NONE",
                "v99r7_previous_positive_evidence": old["positive_evidence_de"] if old else "NONE",
                "v99r7_previous_counterevidence": old["counterevidence_de"] if old else "NONE",
                "v99r7_unconditional_global_export_allowed": old["unconditional_global_export_allowed"] if old else "0",
                "gdt794_cross_scope_decision": decision,
                "later_route_context": (
                    "GDT769_GDT770_OTAR_CONTEXT_BOUND_SEQUENCE_OR_NOMINAL_RIVAL"
                    if surface == "otar" else
                    "GDT251_OKALY_LABEL_RENDERER_FAMILY_DEMOTION"
                    if surface == "okaly" else
                    "GDT793_OKAL_SYSTEM_ENTRY_CODE"
                    if surface == "okal" else "NONE"
                ),
                "circle_context_default_de": defaults_by_surface[surface]["working_default_de"],
                "prose_scope_disposition": "PRESERVE_AS_HISTORICAL_CANDIDATE__REVIEW_BEFORE_ANY_GLOBAL_USE",
                "component_export_credit": "ZERO",
                "confirmed_lexeme": "NO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[10], cross_scope_audit)

    sequence_overrides: list[dict[str, Any]] = []
    for row in atlas:
        surface = str(row["complete_label_surface"])
        if surface in defaults_by_surface:
            sequence_default = str(defaults_by_surface[surface]["working_default_de"])
            default_source = "GDT794_REPEATED_COMPLETE_LABEL_DEFAULT"
        elif row["kluge_a_member"] != "NA":
            sequence_default = f"individuelle Kreisbezeichnung an Kluge {row['kluge_a_member']}A (Bedeutung offen)"
            default_source = "VISIBLE_KLUGE_MEMBER_CONTEXT"
        elif row["visible_clock_hour"] != "NA":
            sequence_default = f"individuelle Kreisbezeichnung bei sichtbarer Lage {row['visible_clock_hour']} Uhr (Bedeutung offen)"
            default_source = "VISIBLE_CLOCK_POSITION_CONTEXT"
        else:
            sequence_default = "individuelle Kreisbezeichnung (Bedeutung offen)"
            default_source = "RADIAL_LABEL_SEQUENCE_CONTEXT"
        tokens = surface.split()
        suppressed: list[str] = []
        for token in tokens:
            old_rows = licensed_dictionary_rows.get(token, [])
            if old_rows:
                meanings = sorted({old["v99r7_spoken_default_de"] for old in old_rows})
                suppressed.append(f"{token}={' / '.join(meanings)}")
        sequence_overrides.append(
            {
                "admitted_slot_ordinal": row["admitted_slot_ordinal"],
                "array_id": row["array_id"],
                "physical_folio": row["physical_folio"],
                "source_selector": row["source_selector"],
                "locus": row["locus"],
                "complete_label_surface": surface,
                "label_token_count": row["label_token_count"],
                "sequence_default_de": sequence_default,
                "sequence_working_display": f"⟦{surface}:{sequence_default}⟧",
                "default_source": default_source,
                "suppressed_unconditional_token_default_count": len(suppressed),
                "suppressed_unconditional_token_defaults": joined(suppressed),
                "tokenwise_pharmaceutical_composition_allowed": "NO",
                "renderer_precedence": "RADIAL_LABEL_SEQUENCE_OVERRIDE_GT_GLOBAL_TOKEN",
                "semantic_confidence": "C0_CONTEXT_OVERRIDE_NOT_PLAINTEXT",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[11], sequence_overrides)

    channels = {
        "SOURCE_SLOT_FRACTION": ("source_slot_fraction", 1.0, "fraction", "LINEAR_EDITORIAL_ORDER"),
        "VISIBLE_CLOCK_HOUR": ("visible_clock_hour", 12.0, "hours", "CIRCULAR"),
        "AXIS_FOLDED_CLOCK_HOUR": ("axis_folded_clock_hour", 6.0, "hours_modulo_opposition", "CIRCULAR"),
        "KLUGE_A_MEMBER": ("kluge_a_member", 30.0, "members", "CIRCULAR"),
    }
    prediction_rows: list[dict[str, Any]] = []
    cross_folio_forms = {
        surface for surface, rows in repeated.items()
        if len({str(row["physical_folio"]) for row in rows}) >= 2
    }
    for surface in sorted(cross_folio_forms):
        rows = repeated[surface]
        for target in rows:
            for channel, (field, period, units, geometry) in channels.items():
                target_raw = str(target[field])
                if target_raw == "NA":
                    continue
                target_value = float(target_raw)
                if geometry == "CIRCULAR":
                    target_value %= period
                training_values: list[float] = []
                training_loci: list[str] = []
                for train in rows:
                    if train["physical_folio"] == target["physical_folio"] or str(train[field]) == "NA":
                        continue
                    value = float(str(train[field]))
                    training_values.append(value % period if geometry == "CIRCULAR" else value)
                    training_loci.append(str(train["locus"]))
                if not training_values:
                    continue
                predicted = circular_mean(training_values, period) if geometry == "CIRCULAR" else sum(training_values) / len(training_values)
                actual_distance = circular_distance(target_value, predicted, period) if geometry == "CIRCULAR" else abs(target_value - predicted)
                opportunities = [
                    (float(str(candidate[field])) % period if geometry == "CIRCULAR" else float(str(candidate[field])))
                    for candidate in by_array[str(target["array_id"])]
                    if str(candidate[field]) != "NA"
                ]
                distances = [
                    circular_distance(value, predicted, period) if geometry == "CIRCULAR" else abs(value - predicted)
                    for value in opportunities
                ]
                smaller = sum(value < actual_distance - 1e-12 for value in distances)
                equal = sum(abs(value - actual_distance) <= 1e-12 for value in distances)
                rank = (smaller + 0.5 * equal) / len(distances)
                quartile_cut = sorted(distances)[max(0, math.ceil(len(distances) * 0.25) - 1)]
                prediction_rows.append(
                    {
                        "complete_label_surface": surface,
                        "held_physical_folio": target["physical_folio"],
                        "target_array_id": target["array_id"],
                        "target_locus": target["locus"],
                        "coordinate_channel": channel,
                        "coordinate_units": units,
                        "coordinate_geometry": geometry,
                        "training_physical_folios": joined(sorted({
                            str(row["physical_folio"]) for row in rows
                            if row["physical_folio"] != target["physical_folio"] and str(row[field]) != "NA"
                        })),
                        "training_loci": joined(training_loci),
                        "training_coordinate_count": len(training_values),
                        "predicted_coordinate": f"{predicted:.6f}",
                        "actual_coordinate": f"{target_value:.6f}",
                        "coordinate_absolute_error": f"{actual_distance:.6f}",
                        "target_array_opportunity_count": len(opportunities),
                        "within_array_midrank_percentile": f"{rank:.6f}",
                        "closest_quartile": "YES" if actual_distance <= quartile_cut + 1e-12 else "NO",
                        "interpretation_ceiling": "COMPLETE_WHOLE_COORDINATE_DIAGNOSTIC_ONLY",
                    }
                )
    write_tsv(out / OUTPUT_NAMES[2], prediction_rows)

    model_for_channel = {
        "SOURCE_SLOT_FRACTION": "SOURCE_ORDER_CODEBOOK",
        "VISIBLE_CLOCK_HOUR": "VISIBLE_CLOCK_CODEBOOK",
        "AXIS_FOLDED_CLOCK_HOUR": "AXIS_PHASE_CLASS",
        "KLUGE_A_MEMBER": "KLUGE_A_CODEBOOK",
    }
    score_rows: list[dict[str, Any]] = []
    for channel in channels:
        rows = [row for row in prediction_rows if row["coordinate_channel"] == channel]
        forms = {row["complete_label_surface"] for row in rows}
        ranks = [float(row["within_array_midrank_percentile"]) for row in rows]
        errors = [float(row["coordinate_absolute_error"]) for row in rows]
        top = sum(row["closest_quartile"] == "YES" for row in rows)
        pass_gate = bool(rows) and (
            len(rows) >= 8 and len(forms) >= 4
            and sum(ranks) / len(ranks) <= 0.35 and top / len(rows) >= 0.60
        )
        model_id = model_for_channel[channel]
        score_rows.append(
            {
                "model_id": model_id,
                "coordinate_channel": channel,
                "target_event_count": len(rows),
                "distinct_complete_forms": len(forms),
                "held_physical_folios": len({row["held_physical_folio"] for row in rows}),
                "mean_coordinate_absolute_error": f6(sum(errors) / len(errors) if errors else None),
                "mean_within_array_midrank_percentile": f6(sum(ranks) / len(ranks) if ranks else None),
                "closest_quartile_count": top,
                "closest_quartile_rate": f6(top / len(rows) if rows else None),
                "fixed_gate": model_specs[model_id]["pass_rule"],
                "gate_result": "PASS_JOINT_TRANSFER" if pass_gate else "FAIL_JOINT_TRANSFER",
                "claim_ceiling": model_specs[model_id]["allowed_interpretation"],
            }
        )
    write_tsv(out / OUTPUT_NAMES[3], score_rows)

    kluge_grid = sorted(
        [row for row in atlas if row["kluge_a_member"] != "NA"],
        key=lambda row: (int(str(row["kluge_a_member"])), str(row["physical_folio"]), int(str(row["array_index"])), int(str(row["slot_index"]))),
    )
    kluge_grid_rows: list[dict[str, Any]] = []
    for row in kluge_grid:
        kluge_grid_rows.append(
            {
                "kluge_a_member": row["kluge_a_member"],
                "physical_folio": row["physical_folio"],
                "source_selector": row["source_selector"],
                "array_id": row["array_id"],
                "array_class": row["array_class"],
                "slot_index": row["slot_index"],
                "slot_count": row["slot_count"],
                "visible_clock_hour": row["visible_clock_hour"],
                "complete_label_surface": row["complete_label_surface"],
                "surface_family": row["surface_family"],
                "literal_okal_prefix": "YES" if str(row["complete_label_surface"]).startswith("okal") else "NO",
                "homology_status": "TRUE_CATALOGUE_HOMOLOG__NOT_RAW_SLOT_EQUIVALENCE",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[4], kluge_grid_rows)

    kluge_summary: list[dict[str, Any]] = []
    for member in range(1, 31):
        rows = [row for row in kluge_grid_rows if int(str(row["kluge_a_member"])) == member]
        hits = [row for row in rows if row["literal_okal_prefix"] == "YES"]
        kluge_summary.append(
            {
                "kluge_a_member": member,
                "label_count": len(rows),
                "physical_folio_count": len({row["physical_folio"] for row in rows}),
                "complete_labels": joined(row["complete_label_surface"] for row in rows),
                "literal_okal_prefix_count": len(hits),
                "literal_okal_prefix_rate": f6(len(hits) / len(rows) if rows else None),
                "okal_prefix_labels": joined(row["complete_label_surface"] for row in hits),
                "interpretation": "POSTHOC_OKAL_FAMILY_CONCENTRATION_CANDIDATE" if member == 9 else "DESCRIPTIVE_TRUE_HOMOLOG_CENSUS",
            }
        )
    write_tsv(out / OUTPUT_NAMES[5], kluge_summary)

    atlas_by_locus = {str(row["locus"]): row for row in atlas}
    slot4_correction: list[dict[str, Any]] = []
    first_kluge: str | None = None
    for ordinal, predecessor in enumerate(slot4_predecessor, 1):
        current = atlas_by_locus[str(predecessor["locus"])]
        kluge = str(current["kluge_a_member"])
        if first_kluge is None and kluge != "NA":
            first_kluge = kluge
        same = "UNKNOWN_MISSING_KLUGE" if kluge == "NA" else "YES" if kluge == first_kluge else "NO"
        slot4_correction.append(
            {
                "series_ordinal": ordinal,
                "array_id": current["array_id"],
                "physical_folio": current["physical_folio"],
                "locus": current["locus"],
                "complete_label_surface": current["complete_label_surface"],
                "literal_okal_prefix": "YES" if str(current["complete_label_surface"]).startswith("okal") else "NO",
                "raw_slot_index": current["slot_index"],
                "slot_count": current["slot_count"],
                "visible_clock_hour": current["visible_clock_hour"],
                "kluge_a_member": kluge,
                "same_true_kluge_homolog_as_first_row": same,
                "corrected_interpretation": "RAW_SLOT4_SERIES__NOT_ONE_HOMOLOGOUS_CALENDAR_OR_DEGREE_SLOT",
            }
        )
    write_tsv(out / OUTPUT_NAMES[6], slot4_correction)

    cross_array_sets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    arrays_for_form = {surface: {str(row["array_id"]) for row in rows} for surface, rows in repeated.items()}
    forms = sorted(cross_folio_forms)
    for left_index, left in enumerate(forms):
        for right in forms[left_index + 1:]:
            shared_arrays = arrays_for_form[left] & arrays_for_form[right]
            if len(shared_arrays) >= 2:
                for array_id in sorted(shared_arrays):
                    left_row = next(row for row in repeated[left] if row["array_id"] == array_id)
                    right_row = next(row for row in repeated[right] if row["array_id"] == array_id)
                    cross_array_sets[(left, right)].append(
                        {
                            "array_id": array_id,
                            "physical_folio": left_row["physical_folio"],
                            "slot_distance_fraction": circular_distance(float(left_row["source_slot_fraction"]), float(right_row["source_slot_fraction"]), 1.0),
                            "clock_distance_hours": circular_distance(float(left_row["visible_clock_hour"]), float(right_row["visible_clock_hour"]), 12.0) if left_row["visible_clock_hour"] != "NA" and right_row["visible_clock_hour"] != "NA" else None,
                        }
                    )
    relational_rows: list[dict[str, Any]] = []
    for (left, right), rows in sorted(cross_array_sets.items()):
        relational_rows.append(
            {
                "left_complete_label": left,
                "right_complete_label": right,
                "shared_array_count": len(rows),
                "physical_folio_count": len({row["physical_folio"] for row in rows}),
                "arrays": joined(row["array_id"] for row in rows),
                "slot_distance_fractions": joined((row["slot_distance_fraction"] for row in rows), numeric=True),
                "clock_distance_hours": joined((row["clock_distance_hours"] for row in rows if row["clock_distance_hours"] is not None), numeric=True),
                "stable_relational_spacing": "NO",
                "interpretation": "ONLY_REPEATED_CROSS_ARRAY_PAIR__RELATIONAL_CALENDAR_SPACING_NOT_STABLE",
            }
        )
    write_tsv(out / OUTPUT_NAMES[7], relational_rows)

    k9 = next(row for row in kluge_summary if row["kluge_a_member"] == 9)
    total_kluge = len(kluge_grid_rows)
    total_okal = sum(row["literal_okal_prefix"] == "YES" for row in kluge_grid_rows)
    k9_hits = int(k9["literal_okal_prefix_count"])
    k9_total = int(k9["label_count"])
    k9_p = hypergeom_upper(total_kluge, total_okal, k9_total, k9_hits)

    adjudication: list[dict[str, Any]] = []
    score_by_model = {row["model_id"]: row for row in score_rows}
    for model_id in ("SOURCE_ORDER_CODEBOOK", "VISIBLE_CLOCK_CODEBOOK", "AXIS_PHASE_CLASS", "KLUGE_A_CODEBOOK"):
        score = score_by_model[model_id]
        adjudication.append(
            {
                "model_id": model_id,
                "evidence": f"{score['target_event_count']} held targets/{score['distinct_complete_forms']} forms; mean rank {score['mean_within_array_midrank_percentile']}; closest quartile {score['closest_quartile_rate']}",
                "counterevidence": "complete labels recur at conflicting coordinates and the working joint gate does not pass" if score["gate_result"].startswith("FAIL") else "small admitted panel and same-manuscript catalogue",
                "gate_result": score["gate_result"],
                "selected_working_model": "NO",
                "confidence": "C0_DIAGNOSTIC",
                "component_export_credit": "ZERO",
            }
        )
    adjudication.extend(
        [
            {
                "model_id": "OKAL_KLUGE09_FAMILY",
                "evidence": f"true Kluge 09A has {k9_hits}/{k9_total} literal okal* labels; descriptive one-sided hypergeometric p={k9_p:.6f}",
                "counterevidence": f"the other {k9_total-k9_hits}/{k9_total} Kluge-09A labels are non-okal; posthoc family scan; okal* occurs at other Kluge members",
                "gate_result": "RETAIN_POSTHOC_TEMPLATE_SLOT_CLASS_RIVAL",
                "selected_working_model": "NO",
                "confidence": "C0_REPLACEABLE",
                "component_export_credit": "ZERO",
            },
            {
                "model_id": "OTODY_NARROW_CLOCK_POSITION",
                "evidence": next(row["evidence"] for row in default_rows if row["complete_label_surface"] == "otody"),
                "counterevidence": "two circle labels only; two prose occurrences do not independently identify timing; exact value may be item/class identity",
                "gate_result": "RETAIN_CONCRETE_WHOLE_POSITION_RIVAL",
                "selected_working_model": "C0_PRIORITY_CANDIDATE_ONLY",
                "confidence": "C0_REPLACEABLE",
                "component_export_credit": "ZERO",
            },
            {
                "model_id": "OPAQUE_ENTRY_CLASS",
                "evidence": "no joint coordinate model passes; repeated exact wholes include remote same-array and cross-folio collisions",
                "counterevidence": "otody narrow-angle coincidence, opposite-axis repeats, and Kluge-09A okal-family concentration remain concrete rivals",
                "gate_result": "SURVIVES_AND_REMAINS_PRIMARY",
                "selected_working_model": "YES",
                "confidence": "C0_SELECTED_WORKING",
                "component_export_credit": "ZERO",
            },
        ]
    )
    write_tsv(out / OUTPUT_NAMES[8], adjudication)

    otody_atlas = [row for row in atlas if row["complete_label_surface"] == "otody"]
    otody_occurrences = sorted([row for row in spine if row["surface"] == "otody"], key=lambda row: int(row["occurrence_ordinal"]))
    if len(otody_atlas) != 2 or len(otody_occurrences) != 4:
        raise RuntimeError("otody expected two circle labels and four total exact occurrences")
    otody_local = {str(row["locus"]): row for row in otody_atlas}
    otody_renderer: list[dict[str, Any]] = []
    for row in otody_occurrences:
        local = otody_local.get(row["locus"])
        if local:
            display = f"⟦otody:oberes rechtes Zeit-/Gradfeld; sichtbar {local['visible_clock_hour']} Uhr⟧"
            evidence = f"circle label at {local['locus']} on {local['physical_folio']}"
        else:
            display = "⟦otody:Bezug auf oberes rechtes Zeit-/Gradfeld?⟧"
            evidence = "running-prose occurrence; coordinate reading imported only as candidate"
        otody_renderer.append(
            {
                "occurrence_id": row["occurrence_id"],
                "occurrence_kind": row["occurrence_kind"],
                "source_selector": row["source_selector"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "surface": row["surface"],
                "working_display": display,
                "semantic_confidence": "C0_PRIORITY_CANDIDATE_NOT_PLAINTEXT",
                "evidence": evidence,
                "counterevidence": "only two aligned labels; prose function unresolved",
                "renderer_license": "EXACT_WHOLE_CANDIDATE_ONLY__NOT_INTEGRATED_CACHE",
                "component_export_credit": "ZERO",
                "confirmed_lexeme": "NO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[9], otody_renderer)

    passed_models = [row["model_id"] for row in score_rows if row["gate_result"] == "PASS_JOINT_TRANSFER"]
    status = (
        "CORRECTION__216_ADMITTED_SLOTS__19_ARRAYS__6_FOLIOS__15_REPEATED_COMPLETE_LABELS__"
        f"{len(cross_folio_forms)}_CROSS_FOLIO_FORMS__RAW_SLOT4_NOT_TRUE_HOMOLOG__"
        f"TRUE_KLUGE09_OKAL_PREFIX_{k9_hits}_OF_{k9_total}__"
        f"JOINT_POSITION_MODELS_{'PASS_' + '_'.join(passed_models) if passed_models else 'ALL_FAIL'}__"
        "OTODY_ONE_OCLOCK_POSITION_RIVAL_C0__OPAQUE_ENTRY_CLASS_PRIMARY__"
        "ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
    )
    result = {
        "experiment_id": "GDT794",
        "status": status,
        "scope": {
            "released_physical_pages": 30,
            "source_selectors": 35,
            "admitted_circle_physical_folios": len({row["physical_folio"] for row in atlas}),
            "new_pages_or_images_opened": 0,
            "mixed_sources_queried": 0,
            "sealed_rows_materialized": 0,
        },
        "counts": {
            "admitted_circle_slots": len(atlas),
            "admitted_arrays": len({row["array_id"] for row in atlas}),
            "complete_label_surfaces": len(by_surface),
            "multi_token_complete_labels": sum(int(row["label_token_count"]) > 1 for row in atlas),
            "repeated_complete_labels": len(repeated),
            "repeated_complete_label_occurrences": sum(len(rows) for rows in repeated.values()),
            "cross_folio_repeated_forms": len(cross_folio_forms),
            "clock_coordinate_slots": sum(row["visible_clock_hour"] != "NA" for row in atlas),
            "kluge_a_coordinate_slots": total_kluge,
            "true_kluge09_labels": k9_total,
            "true_kluge09_okal_prefix_labels": k9_hits,
            "raw_slot4_rows": len(slot4_correction),
            "raw_slot4_distinct_kluge_values": len({row["kluge_a_member"] for row in slot4_correction if row["kluge_a_member"] != "NA"}),
            "stable_relational_form_pairs": sum(row["stable_relational_spacing"] == "YES" for row in relational_rows),
            "otody_exact_circle_labels": len(otody_atlas),
            "otody_exact_all_occurrences": len(otody_occurrences),
            "circle_label_sequence_overrides": len(sequence_overrides),
            "suppressed_unconditional_token_occurrences": sum(int(row["suppressed_unconditional_token_default_count"]) for row in sequence_overrides),
            "suppressed_unconditional_token_forms": len({
                token for row in atlas for token in str(row["complete_label_surface"]).split()
                if token in licensed_dictionary_rows
            }),
            "single_token_slots_with_suppressed_global": sum(
                int(row["label_token_count"]) == 1 and int(row["suppressed_unconditional_token_default_count"]) == 1
                for row in sequence_overrides
            ),
            "multi_token_slots_with_any_suppressed_global": sum(
                int(row["label_token_count"]) > 1 and int(row["suppressed_unconditional_token_default_count"]) > 0
                for row in sequence_overrides
            ),
            "multi_token_slots_with_all_tokens_suppressed": sum(
                int(row["label_token_count"]) > 1
                and int(row["suppressed_unconditional_token_default_count"]) == int(row["label_token_count"])
                for row in sequence_overrides
            ),
            "cross_scope_dictionary_holds": sum(row["gdt794_cross_scope_decision"].startswith("HOLD_") for row in cross_scope_audit),
            "component_exports": 0,
            "confirmed_lexemes": 0,
        },
        "coordinate_scores": {row["model_id"]: row for row in score_rows},
        "decision": {
            "raw_slot4_correction": "SOURCE_SLOT_INDEX_4_IS_NOT_ONE_KLUGE_OR_ANGLE_HOMOLOG",
            "joint_position_codebook": "SELECTED" if passed_models else "NOT_SELECTED",
            "selected_primary_model": "OPAQUE_ENTRY_CLASS",
            "concrete_whole_candidate": "otody = oberes rechtes Zeit-/Gradfeld, sichtbar ungefähr 1 Uhr (C0, replaceable)",
            "okal_update": f"true Kluge 09A has {k9_hits}/{k9_total} okal-prefix labels; retain template-slot/class rival, not number or fixed degree",
            "circle_renderer_update": "RADIAL_LABEL_SEQUENCE overrides unconditional token composition on all 216 admitted slots",
            "dictionary_update": "six universal pharmaceutical whole readings move to cross-scope HOLD; historical and later context-bound candidates remain preserved",
        },
        "claim_ceiling": (
            "Corrects raw source slot order versus true Kluge/angle homology and evaluates complete-whole positional transfer. "
            "All German readings are replaceable C0 working candidates. No word, component, calendar, day, degree, planet, "
            "sound, language, cipher, plaintext, object, substance, action, disease or treatment is confirmed."
        ),
    }
    (out / OUTPUT_NAMES[12]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
