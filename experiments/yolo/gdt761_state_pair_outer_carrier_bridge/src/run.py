#!/usr/bin/env python3
"""Build an outward carrier bridge around the four GDT760 state wholes."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
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
BASE_REL = Path("experiments/yolo/gdt761_state_pair_outer_carrier_bridge")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G760_RUN_REL = Path(
    "experiments/yolo/gdt760_quantity_bilateral_content_attachment/src/run.py"
)
G754_SIEVE_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
)
G758_PRIORS_REL = Path(
    "experiments/yolo/gdt758_ychor_follower_global_content_census/"
    "src/FOLLOWER_CANDIDATE_PRIORS.tsv"
)
G734_DICT_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/"
    "artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G737_QUARANTINE_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/"
    "artifacts/V99R7_HELD_WHOLE_QUARANTINE.tsv"
)
G738_HOLD_REL = Path(
    "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/"
    "artifacts/MANUAL_HOLD_AUDIT.tsv"
)
CURRENT_OVERRIDES_REL = BASE_REL / "src/CURRENT_WHOLE_ROLE_OVERRIDES.tsv"
OUTPUT_NAMES = (
    "TARGET_151_OUTWARD_CONTEXT_ATLAS.tsv",
    "DIRECT_224_CLEAN_EDGE_ATLAS.tsv",
    "DIRECT_173_SHARED_NEIGHBOR_DECK.tsv",
    "PAIR_SHARED_10_DIRECT_FRAME_ATLAS.tsv",
    "PAIR_SHARED_8_RADIUS2_FRAME_ATLAS.tsv",
    "CHOR_5_CARRIER_AND_SHOR_SHEOR_2_RIVAL_SPAN_ATLAS.tsv",
    "SOLVENT_7_CANDIDATE_AUDIT.tsv",
    "FIVE_WHOLE_WORKING_REVISION.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__151_STATE_WHOLE_OCCURRENCES__224_CLEAN_DIRECT_EXACT_EDGES__"
    "CHOR_UNIQUE_NONAMOUNT_NEIGHBOR_ACROSS_ALL4_TARGETS__5_CONTACTS_5_PAGES__"
    "5_CHOR_CONDITIONAL_PHRASES__2_SHOR_SHEOR_BASE_RIVAL_SPANS__10_SHARED_DIRECT_FRAMES__"
    "CTHY_RADIUS2_PREPARATION_RELAY_ONLY__ZERO_SOLVENT_IDENTITY__"
    "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)
PAIR_SPECS = (
    ("MATERIAL_PART", "cheor", "sheor"),
    ("PREPARATION", "cheo", "sheo"),
)
AXIS_ORDER = g_axis_order = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g760 = load_module("gdt760_builder_for_gdt761", ROOT / G760_RUN_REL)
clean_cell = g760.clean_cell
physical_folio = g760.physical_folio


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def fixed(number: float) -> str:
    return f"{number:.6f}"


def joined(values: Iterable[str]) -> str:
    selected = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in selected) or "NONE"


def compact_counts(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def line_position(ordinal: int, count: int) -> str:
    if count == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == count:
        return "LAST"
    return "MIDDLE"


def amount_surface_value(surface: str) -> str | None:
    if surface in g760.FUSED:
        head, value = g760.FUSED[surface]
        return g760.amount_candidate(head, value)[0]
    if surface in g760.VALUES:
        return f"Wert {g760.VALUE_LABEL[surface]}"
    if surface == "s":
        return "Mengen-/Gleichteileform"
    if surface == "or":
        return "Portionsform"
    if surface == "ar":
        return "Anteilsform"
    return None


def semantic_map(
    targets: dict[str, dict[str, str]],
    carriers: dict[str, dict[str, str]],
    overrides: dict[str, dict[str, str]],
    follower_rows: list[dict[str, str]],
    dictionary_rows: list[dict[str, str]],
) -> tuple[dict[str, str], dict[str, str]]:
    meanings: defaultdict[str, list[str]] = defaultdict(list)
    sources: defaultdict[str, list[str]] = defaultdict(list)
    for row in dictionary_rows:
        if row["unconditional_global_export_allowed"] != "1":
            continue
        value = row["v99r7_spoken_default_de"]
        if value and value not in meanings[row["surface"]]:
            meanings[row["surface"]].append(value)
            sources[row["surface"]].append("GDT734_COMPLETE_WHOLE")
    for row in follower_rows:
        meanings[row["surface"]] = [row["renderer_value_de"]]
        sources[row["surface"]] = ["GDT758_COMPLETE_WHOLE"]
    for surface, row in carriers.items():
        meanings[surface] = [row["working_candidate_de"]]
        sources[surface] = ["GDT761_CARRIER_PRIOR"]
    for surface, row in targets.items():
        meanings[surface] = [row["current_working_candidate_de"]]
        sources[surface] = ["GDT761_TARGET_PRIOR"]
    for surface, row in overrides.items():
        meanings[surface] = [row["working_candidate_de"]]
        sources[surface] = [row["basis"] + "_POST_G734_OVERRIDE"]
    for surface in g760.FUSED:
        value = amount_surface_value(surface)
        if value:
            meanings[surface] = [value]
            sources[surface] = ["GDT760_AMOUNT_FAMILY"]
    return (
        {surface: " || ".join(values) for surface, values in meanings.items()},
        {surface: "|".join(sorted(set(values))) for surface, values in sources.items()},
    )


def slot_record(
    context: object,
    locus: str,
    ordinal: int,
    target_surfaces: set[str],
    suspect_surfaces: set[str],
    meanings: dict[str, str],
    sources: dict[str, str],
) -> dict[str, object]:
    line = context.by_line[locus]
    if ordinal < 1 or ordinal > len(line):
        return {
            "ordinal": 0, "surface": "LINE_EDGE", "status": "EDGE",
            "axes": "NONE", "semantic_candidate_de": "NONE",
            "semantic_source": "LINE_EDGE", "unknown_cell": 1,
        }
    token, cell, axes = clean_cell(context, locus, ordinal)
    surface = str(token["eva"])
    exact = bool(context.exact[(locus, int(token["token_index"]))])
    if not exact:
        status = "NONEXACT"
    elif surface in suspect_surfaces:
        status = "SUSPECT"
        axes = set()
    elif surface in target_surfaces:
        status = "TARGET"
    else:
        status = "ELIGIBLE"
    amount_value = amount_surface_value(surface)
    semantic = amount_value or meanings.get(surface, str(cell["v99r7_semantic_value_de"]))
    source = "GDT760_AMOUNT_FAMILY" if amount_value else sources.get(surface, "GDT734_CELL")
    if status == "SUSPECT":
        semantic = "QUARANTINED_SOURCE_COMPOSITION"
        source = "GDT754_PROVENANCE_SIEVE"
    return {
        "ordinal": ordinal, "surface": surface, "status": status,
        "axes": joined(axes), "semantic_candidate_de": semantic,
        "semantic_source": source, "unknown_cell": int(cell["unknown_v99r7"]),
    }


def build_occurrences_and_contacts(
    context: object,
    line_meta: dict[str, dict[str, str]],
    targets: dict[str, dict[str, str]],
    suspect_surfaces: set[str],
    meanings: dict[str, str],
    sources: dict[str, str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_surfaces = set(targets)
    occurrences: list[dict[str, object]] = []
    direct_contacts: list[dict[str, object]] = []
    radius2_contacts: list[dict[str, object]] = []
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            target = str(token["eva"])
            if target not in target_surfaces:
                continue
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            ordinal = index + 1
            slots = {
                "l2": slot_record(context, locus, ordinal - 2, target_surfaces, suspect_surfaces, meanings, sources),
                "l1": slot_record(context, locus, ordinal - 1, target_surfaces, suspect_surfaces, meanings, sources),
                "r1": slot_record(context, locus, ordinal + 1, target_surfaces, suspect_surfaces, meanings, sources),
                "r2": slot_record(context, locus, ordinal + 2, target_surfaces, suspect_surfaces, meanings, sources),
            }
            prior = targets[target]
            meta = line_meta[locus]
            occurrence_id = ""
            row: dict[str, object] = {
                "target_occurrence_id": occurrence_id,
                "page": token["page"], "physical_folio": physical_folio(str(token["page"])),
                "locus": locus, "line_number": meta["line_number"],
                "section": token["section"], "language": token["language"],
                "hand": token["hand"], "target_surface": target,
                "target_ordinal": ordinal, "line_token_count": len(line),
                "target_line_position": line_position(ordinal, len(line)),
                "target_polarity": prior["polarity"],
                "target_carrier_role": prior["carrier_role"],
                "target_working_candidate_de": prior["current_working_candidate_de"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
            }
            for key in ("l2", "l1", "r1", "r2"):
                for field in (
                    "ordinal", "surface", "status", "axes",
                    "semantic_candidate_de", "semantic_source", "unknown_cell",
                ):
                    row[f"{key}_{field}"] = slots[key][field]
            occurrences.append(row)
    occurrences.sort(key=lambda row: (
        str(row["page"]), int(row["line_number"]), int(row["target_ordinal"]),
    ))
    for number, row in enumerate(occurrences, start=1):
        occurrence_id = f"G761-O{number:03d}"
        row["target_occurrence_id"] = occurrence_id
        for side, distance, key in (("L", 1, "l1"), ("R", 1, "r1"), ("L", 2, "l2"), ("R", 2, "r2")):
            if row[f"{key}_status"] != "ELIGIBLE":
                continue
            contact = {
                "contact_id": "",
                "target_occurrence_id": occurrence_id,
                "page": row["page"], "physical_folio": row["physical_folio"],
                "locus": row["locus"], "target_surface": row["target_surface"],
                "target_ordinal": row["target_ordinal"], "target_polarity": row["target_polarity"],
                "target_carrier_role": row["target_carrier_role"],
                "target_working_candidate_de": row["target_working_candidate_de"],
                "neighbor_side": side, "neighbor_distance": distance,
                "neighbor_surface": row[f"{key}_surface"],
                "neighbor_ordinal": row[f"{key}_ordinal"],
                "neighbor_axes": row[f"{key}_axes"],
                "neighbor_semantic_candidate_de": row[f"{key}_semantic_candidate_de"],
                "neighbor_semantic_source": row[f"{key}_semantic_source"],
                "intervening_surface": "NONE",
                "intervening_status": "NONE",
                "written_line_eva": row["written_line_eva"],
                "reader_exact_target_and_neighbor": 1,
                "component_export_credit": 0,
            }
            if distance == 2:
                inner_key = "l1" if side == "L" else "r1"
                contact["intervening_surface"] = row[f"{inner_key}_surface"]
                contact["intervening_status"] = row[f"{inner_key}_status"]
                radius2_contacts.append(contact)
            else:
                direct_contacts.append(contact)
    for prefix, rows in (("D", direct_contacts), ("R", radius2_contacts)):
        for number, row in enumerate(rows, start=1):
            row["contact_id"] = f"G761-{prefix}{number:03d}"
    return occurrences, direct_contacts, radius2_contacts


def role_class(
    surface: str,
    axes_text: str,
    carriers: dict[str, dict[str, str]],
    overrides: dict[str, dict[str, str]],
) -> str:
    if surface in carriers:
        return carriers[surface]["role_class"]
    if surface in overrides:
        return overrides[surface]["role_class"]
    if amount_surface_value(surface) is not None or surface in {
        "dain", "daiin", "dar", "air", "otaiin",
    }:
        return "AMOUNT_OR_VALUE_FORM"
    axes = {
        axis
        for variant in axes_text.split(" || ")
        for axis in variant.split("|")
    }
    if axes & {"MATERIAL", "PREPARATION"}:
        return "CONTENT_OR_PREPARATION_WHOLE"
    if axes & {"DRY", "MOIST", "HOT", "COLD"}:
        return "QUALITY_OR_STATE_WHOLE"
    if axes & {"PROCESS", "CLOSE"}:
        return "PROCESS_OR_CLOSE_WHOLE"
    return "OPEN_OR_OTHER_WHOLE"


def global_counts(
    context: object, suspect_surfaces: set[str], target_surfaces: set[str]
) -> tuple[Counter[str], defaultdict[str, set[str]], int]:
    counts: Counter[str] = Counter()
    pages: defaultdict[str, set[str]] = defaultdict(set)
    total = 0
    for locus, line in context.by_line.items():
        for token in line:
            surface = str(token["eva"])
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            if surface in suspect_surfaces or surface in target_surfaces:
                continue
            total += 1
            counts[surface] += 1
            pages[surface].add(str(token["page"]))
    return counts, pages, total


def build_neighbor_deck(
    context: object,
    contacts: list[dict[str, object]],
    targets: dict[str, dict[str, str]],
    carriers: dict[str, dict[str, str]],
    overrides: dict[str, dict[str, str]],
    suspect_surfaces: set[str],
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        by_surface[str(row["neighbor_surface"])].append(row)
    counts, pages, total = global_counts(context, suspect_surfaces, set(targets))
    output: list[dict[str, object]] = []
    for surface, rows in by_surface.items():
        target_counts = Counter(str(row["target_surface"]) for row in rows)
        polarity_counts = Counter(str(row["target_polarity"]) for row in rows)
        axes_text = " || ".join(sorted({str(row["neighbor_axes"]) for row in rows}))
        current_role = role_class(surface, axes_text, carriers, overrides)
        contact_share = len(rows) / len(contacts)
        background_share = counts[surface] / total if total else 0.0
        if surface == "chor":
            decision = "SELECT_REPRODUCTIVE_PART_CARRIER_CROSSING_ALL4_TARGETS"
            selected = 1
        elif surface == "oraiin":
            decision = "KNOWN_AMOUNT_FORMULA_CROSSING_ALL4_NOT_CARRIER"
            selected = 0
        elif surface == "ol":
            decision = "NEUTRAL_CARRIER_OR_PREPARATION_RIVAL_NOT_SOLVENT_IDENTITY"
            selected = 0
        elif len(target_counts) >= 3:
            decision = "SHARED_STRUCTURAL_CANDIDATE_RETAIN"
            selected = 0
        elif len(target_counts) == 2:
            decision = "PAIR_SHARED_NAVIGATION_CANDIDATE"
            selected = 0
        else:
            decision = "SINGLE_TARGET_NEIGHBOR"
            selected = 0
        output.append({
            "neighbor_surface": surface, "direct_contacts": len(rows),
            "direct_contact_pages": len({str(row["page"]) for row in rows}),
            "target_coverage": len(target_counts),
            "target_counts": "|".join(f"{key}:{target_counts[key]}" for key in sorted(target_counts)),
            "polarity_counts": "|".join(f"{key}:{polarity_counts[key]}" for key in sorted(polarity_counts)),
            "side_counts": compact_counts(str(row["neighbor_side"]) for row in rows),
            "global_reader_exact_occurrences": counts[surface],
            "global_reader_exact_pages": len(pages[surface]),
            "direct_contact_share": fixed(contact_share),
            "global_background_share": fixed(background_share),
            "descriptive_contact_lift": fixed(contact_share / background_share if background_share else 0.0),
            "current_semantic_candidate_de": " || ".join(sorted({str(row["neighbor_semantic_candidate_de"]) for row in rows})),
            "current_role_class": current_role,
            "decision": decision, "carrier_candidate_selected": selected,
            "specific_identity_confirmed": 0, "component_export_credit": 0,
        })
    output.sort(key=lambda row: (
        -int(row["target_coverage"]), -int(row["direct_contacts"]),
        -float(row["descriptive_contact_lift"]), str(row["neighbor_surface"]),
    ))
    return output


def build_shared_frames(
    contacts: list[dict[str, object]], distance: int
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for role, dry, moist in PAIR_SPECS:
        for side in ("L", "R"):
            dry_rows: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
            moist_rows: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
            for row in contacts:
                if int(row["neighbor_distance"]) != distance or row["neighbor_side"] != side:
                    continue
                if row["target_surface"] == dry:
                    dry_rows[str(row["neighbor_surface"])].append(row)
                elif row["target_surface"] == moist:
                    moist_rows[str(row["neighbor_surface"])].append(row)
            for surface in sorted(set(dry_rows) & set(moist_rows)):
                drows = dry_rows[surface]
                mrows = moist_rows[surface]
                if surface == "chor":
                    interpretation = "SAME_REPRODUCTIVE_PART_CARRIER"
                elif amount_surface_value(surface) is not None or surface in {"daiin", "aiin", "or"}:
                    interpretation = "SAME_AMOUNT_OR_VALUE_FRAME"
                elif surface == "al":
                    interpretation = "SAME_MATERIAL_I_CARRIER_FRAME"
                elif surface == "cthy":
                    interpretation = "SAME_LEAF_DRUG_RADIUS2_LEAD_NO_DIRECT_ATTACHMENT"
                else:
                    interpretation = "SAME_OUTER_WHOLE_FRAME"
                output.append({
                    "shared_frame_id": "",
                    "pair_role": role, "dry_target": dry, "moist_target": moist,
                    "neighbor_side": side, "neighbor_distance": distance,
                    "shared_neighbor_surface": surface,
                    "dry_target_contacts": len(drows), "moist_target_contacts": len(mrows),
                    "pages": len({str(row["page"]) for row in drows + mrows}),
                    "dry_loci": "|".join(sorted(str(row["locus"]) for row in drows)),
                    "moist_loci": "|".join(sorted(str(row["locus"]) for row in mrows)),
                    "intervening_surface_counts": compact_counts(
                        str(row["intervening_surface"]) for row in drows + mrows
                    ) if distance == 2 else "NONE",
                    "interpretation": interpretation,
                    "exact_composition_license": int(distance == 1 and surface == "chor"),
                    "component_export_credit": 0,
                })
    output.sort(key=lambda row: (
        str(row["pair_role"]), str(row["neighbor_side"]),
        str(row["shared_neighbor_surface"]),
    ))
    prefix = "D" if distance == 1 else "R"
    for number, row in enumerate(output, start=1):
        row["shared_frame_id"] = f"G761-{prefix}F{number:02d}"
    return output


def phrase_for(target: str, carrier: str) -> str:
    if carrier == "chor":
        return {
            "cheor": "getrockneter Blüten-/Samenstand",
            "sheor": "feuchter/eingeweichter Blüten-/Samenstand",
            "cheo": "trocken angesetzte Zubereitung aus Blüten-/Samenstand",
            "sheo": "Feuchtzubereitung aus Blüten-/Samenstand",
        }[target]
    return "Basis-/Feuchtform-Paar; als feuchte Blüte oder Fruchtstand lesbar"


def build_carrier_and_base_rival_spans(
    contacts: list[dict[str, object]]
) -> list[dict[str, object]]:
    selected = [row for row in contacts if row["neighbor_surface"] in {"chor", "shor"}]
    output: list[dict[str, object]] = []
    for number, row in enumerate(selected, start=1):
        carrier = str(row["neighbor_surface"])
        target = str(row["target_surface"])
        output.append({
            "phrase_id": f"G761-P{number:02d}", "contact_id": row["contact_id"],
            "page": row["page"], "locus": row["locus"],
            "carrier_surface": carrier, "state_whole_surface": target,
            "written_order": "CARRIER_TARGET" if row["neighbor_side"] == "L" else "TARGET_CARRIER",
            "exact_span_eva": (
                f"{carrier} {target}" if row["neighbor_side"] == "L"
                else f"{target} {carrier}"
            ),
            "working_phrase_de": phrase_for(target, carrier),
            "working_confidence": (
                "C1_CHOR_CROSS_FOUR_TARGET_EXACT_CONTACT"
                if carrier == "chor" else "C0_SHOR_SAME_FAMILY_BASE_RIVAL"
            ),
            "identity_rivals_de": (
                "Pflanzenteil ohne nähere Bestimmung || Blüten-/Fruchtstand"
                if carrier == "chor" else "SH+E+OR-Familienpaar || Blüte || Fruchtstand || feuchter Pflanzenteil"
            ),
            "written_line_eva": row["written_line_eva"],
            "scope": "THIS_EXACT_TWO_WHOLE_SPAN_ONLY",
            "exact_phrase_translation_license": int(carrier == "chor"),
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    output.sort(key=lambda row: (str(row["page"]), str(row["locus"]), str(row["exact_span_eva"])))
    for number, row in enumerate(output, start=1):
        row["phrase_id"] = f"G761-P{number:02d}"
    return output


def build_solvent_audit(
    deck: list[dict[str, object]]
) -> list[dict[str, object]]:
    rows = []
    for row in deck:
        counts = {
            key: int(value) for key, value in (
                item.split(":") for item in str(row["polarity_counts"]).split("|")
            )
        }
        if counts.get("MOIST", 0) >= 2 and counts.get("DRY", 0) == 0:
            rows.append(row)
    ol = next(row for row in deck if row["neighbor_surface"] == "ol")
    rows.append(ol)
    output: list[dict[str, object]] = []
    for number, row in enumerate(sorted(rows, key=lambda item: str(item["neighbor_surface"])), start=1):
        surface = str(row["neighbor_surface"])
        if surface == "ol":
            disposition = "NEUTRAL_CARRIER_NOT_MOIST_SELECTIVE_OIL_RIVAL_ONLY"
        elif surface == "ckhy":
            disposition = "MIXTURE_BEGIN_FIELD_NOT_SPECIFIC_MEDIUM"
        elif surface == "dar":
            disposition = "AMOUNT_PART_FIELD_NOT_SPECIFIC_MEDIUM"
        elif surface in {"sain"}:
            disposition = "AMOUNT_FORM_NOT_SPECIFIC_MEDIUM"
        elif surface == "shor":
            disposition = "REPRODUCTIVE_PART_RIVAL_NOT_MEDIUM"
        elif surface == "pcheey":
            disposition = "REPEATED_SHEO_COMPLEMENT_LEAD_OLD_PULVIS_LITERAL_QUARANTINED_NOT_SPECIFIC_MEDIUM"
        elif surface == "tor":
            disposition = "COLD_PORTION_WHOLE_NOT_MEDIUM"
        else:
            disposition = "NO_SPECIFIC_MEDIUM"
        output.append({
            "solvent_audit_id": f"G761-S{number:02d}",
            "surface": surface, "direct_contacts": row["direct_contacts"],
            "target_coverage": row["target_coverage"],
            "target_counts": row["target_counts"],
            "polarity_counts": row["polarity_counts"],
            "contact_pages": row["direct_contact_pages"],
            "global_reader_exact_occurrences": row["global_reader_exact_occurrences"],
            "current_semantic_candidate_de": row["current_semantic_candidate_de"],
            "current_role_class": row["current_role_class"],
            "descriptive_contact_lift": row["descriptive_contact_lift"],
            "water_rival": int(surface in {"ol", "ckhy"}),
            "wine_rival": int(surface in {"ol", "ckhy"}),
            "oil_rival": int(surface == "ol"),
            "disposition": disposition, "specific_solvent_selected": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return output


def build_revisions(
    targets: dict[str, dict[str, str]],
    carriers: dict[str, dict[str, str]],
    contacts: list[dict[str, object]],
    phrases: list[dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    chor_contacts = [row for row in contacts if row["neighbor_surface"] == "chor"]
    output.append({
        "surface": "chor", "old_working_candidate_de": carriers["chor"]["working_candidate_de"],
        "new_working_candidate_de": "Blüten-/Samenstand",
        "old_confidence": carriers["chor"]["prior_confidence"],
        "new_role_confidence": "C2_CROSS_CONSTRUCTION_PART_CARRIER",
        "specific_identity_confidence": "C1_REPRODUCTIVE_PART_LEAD",
        "new_exact_phrase_positions": len(chor_contacts),
        "evidence": "5 direkte Kontakte auf 5 Seiten, alle 4 Trocken/Feucht-Zielwörter; einziger Nicht-Mengen-Nachbar mit Zielabdeckung 4",
        "counterevidence": "Blüte gegen Samenstand gegen allgemeines Pflanzenteil bleibt offen; globale Bedeutung nur als ersetzbarer Ganzwortwert",
        "decision": "PROMOTE_ROLE_CONFIDENCE_KEEP_SPECIFIC_IDENTITY_C1",
        "global_component_export_allowed": 0, "confirmed_lexeme": 0,
    })
    phrase_counts = Counter(
        str(row["state_whole_surface"])
        for row in phrases
        if int(row["exact_phrase_translation_license"]) == 1
    )
    for surface in ("cheor", "sheor", "cheo", "sheo"):
        prior = targets[surface]
        output.append({
            "surface": surface, "old_working_candidate_de": prior["current_working_candidate_de"],
            "new_working_candidate_de": prior["current_working_candidate_de"],
            "old_confidence": prior["current_confidence"],
            "new_role_confidence": prior["current_confidence"],
            "specific_identity_confidence": "CONTEXT_BOUND_CARRIER_ONLY",
            "new_exact_phrase_positions": phrase_counts[surface],
            "evidence": f"{phrase_counts[surface]} exakte chor-carrier spans; Zielganzwortrolle bleibt erhalten",
            "counterevidence": "Außerhalb eines sichtbaren carrier whole bleibt der genaue Pflanzenteil oder das Medium offen",
            "decision": "KEEP_GLOBAL_WHOLE_ADD_EXACT_CARRIER_PHRASES",
            "global_component_export_allowed": 0, "confirmed_lexeme": 0,
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target_rows = read_tsv(SRC / "TARGET_WHOLE_PRIORS.tsv")
    carrier_rows = read_tsv(SRC / "CARRIER_CANDIDATE_PRIORS.tsv")
    override_rows = read_tsv(ROOT / CURRENT_OVERRIDES_REL)
    sieve_rows = read_tsv(ROOT / G754_SIEVE_REL)
    quarantine_rows = read_tsv(ROOT / G737_QUARANTINE_REL)
    hold_rows = read_tsv(ROOT / G738_HOLD_REL)
    follower_rows = read_tsv(ROOT / G758_PRIORS_REL)
    dictionary_rows = read_tsv(ROOT / G734_DICT_REL)
    if (
        len(target_rows) != 4 or len(carrier_rows) != 5
        or len(override_rows) != 7 or len(sieve_rows) != 172
        or len(quarantine_rows) != 82 or len(hold_rows) != 14
    ):
        raise AssertionError("fixed target carrier and quarantine decks required")
    targets = {row["target_surface"]: row for row in target_rows}
    carriers = {row["surface"]: row for row in carrier_rows}
    overrides = {row["surface"]: row for row in override_rows}
    retired_surfaces = {
        row["surface"] for row in quarantine_rows
        if row["gdt737_decision"] == "QUARANTINE_RETIRED_HEAD_NOUN_DERIVATION"
    }
    retired_salt_surfaces = {
        row["surface"] for row in hold_rows
        if row["decision"] == "HOLD_RETIRED_LITERAL_MATERIAL"
    }
    later_repaired_surfaces = (
        set(g760.FUSED) | set(targets) | set(carriers) | set(overrides)
        | {row["surface"] for row in follower_rows}
    )
    suspect_surfaces = (
        {row["surface"] for row in sieve_rows}
        | retired_surfaces | retired_salt_surfaces
    ) - later_repaired_surfaces
    meanings, sources = semantic_map(targets, carriers, overrides, follower_rows, dictionary_rows)
    context, line_meta, inherited_guard = g760.g759.g758.g756.g755.g753.g752.g751.load_context()
    occurrences, contacts, radius2_contacts = build_occurrences_and_contacts(
        context, line_meta, targets, suspect_surfaces, meanings, sources
    )
    deck = build_neighbor_deck(context, contacts, targets, carriers, overrides, suspect_surfaces)
    direct_frames = build_shared_frames(contacts, 1)
    radius2_frames = build_shared_frames(radius2_contacts, 2)
    phrases = build_carrier_and_base_rival_spans(contacts)
    solvent = build_solvent_audit(deck)
    revisions = build_revisions(targets, carriers, contacts, phrases)

    target_counts = Counter(str(row["target_surface"]) for row in occurrences)
    slot_status = Counter()
    radius2_status = Counter()
    for row in occurrences:
        slot_status.update((str(row["l1_status"]), str(row["r1_status"])))
        radius2_status.update((str(row["l2_status"]), str(row["r2_status"])))
    if target_counts != Counter({"cheor": 56, "sheor": 31, "cheo": 36, "sheo": 28}):
        raise AssertionError(f"target universe changed: {target_counts}")
    if slot_status != Counter({"ELIGIBLE": 224, "NONEXACT": 55, "EDGE": 9, "SUSPECT": 14}):
        raise AssertionError(f"direct slot universe changed: {slot_status}")
    if radius2_status != Counter({
        "ELIGIBLE": 176, "EDGE": 77, "NONEXACT": 41, "SUSPECT": 6, "TARGET": 2,
    }):
        raise AssertionError(f"radius2 slot universe changed: {radius2_status}")
    if len(occurrences) != 151 or len(contacts) != 224 or len(deck) != 173:
        raise AssertionError("occurrence direct-contact or candidate universe changed")
    if len(direct_frames) != 10 or len(radius2_frames) != 8:
        raise AssertionError("shared frame universe changed")
    if (
        len(phrases) != 7
        or Counter(row["carrier_surface"] for row in phrases) != Counter({"chor": 5, "shor": 2})
        or sum(int(row["exact_phrase_translation_license"]) for row in phrases) != 5
    ):
        raise AssertionError("chor carrier and shor base-rival span universe changed")
    if len(solvent) != 7 or any(int(row["specific_solvent_selected"]) for row in solvent):
        raise AssertionError("solvent candidate audit changed")
    chor = next(row for row in deck if row["neighbor_surface"] == "chor")
    oraiin = next(row for row in deck if row["neighbor_surface"] == "oraiin")
    if int(chor["target_coverage"]) != 4 or int(chor["direct_contacts"]) != 5:
        raise AssertionError("chor cross-target carrier lead changed")
    if int(oraiin["target_coverage"]) != 4 or oraiin["current_role_class"] != "AMOUNT_OR_VALUE_FORM":
        raise AssertionError("oraiin amount control changed")

    tables = (
        occurrences, contacts, deck, direct_frames, radius2_frames,
        phrases, solvent, revisions,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        write_tsv(output_dir / name, rows, list(rows[0]))

    result = {
        "schema": "GDT761_RESULT_V1", "status": STATUS,
        "scope": {
            "target_occurrences": len(occurrences),
            "target_loci": len({str(row["locus"]) for row in occurrences}),
            "target_pages": len({str(row["page"]) for row in occurrences}),
            "direct_clean_exact_edges": len(contacts),
            "direct_distinct_neighbor_positions": len({
                (str(row["locus"]), int(row["neighbor_ordinal"]))
                for row in contacts
            }),
            "direct_distinct_neighbor_surfaces": len(deck),
            "radius2_clean_exact_edges": len(radius2_contacts),
            "shared_direct_frame_types": len(direct_frames),
            "shared_radius2_frame_types": len(radius2_frames),
            "chor_conditional_exact_phrases": sum(
                int(row["exact_phrase_translation_license"]) for row in phrases
            ),
            "shor_sheor_repeated_base_rival_spans": sum(
                row["carrier_surface"] == "shor" for row in phrases
            ),
            "solvent_candidates_audited": len(solvent),
            "whole_revisions": len(revisions),
        },
        "carrier_result": {
            "chor_contacts": int(chor["direct_contacts"]),
            "chor_pages": int(chor["direct_contact_pages"]),
            "chor_target_coverage": int(chor["target_coverage"]),
            "chor_contact_lift": chor["descriptive_contact_lift"],
            "only_other_four_target_neighbor": "oraiin",
            "other_neighbor_role": "AMOUNT_OR_VALUE_FORM",
            "chor_role_decision": "PROMOTE_TO_C2_CROSS_CONSTRUCTION_PART_CARRIER",
            "chor_specific_identity": "KEEP_C1_FLOWER_OR_SEED_HEAD_LEAD",
            "chor_exact_phrases": 5,
            "shor_sheor_repeated_base_rival_spans": 2,
        },
        "pair_result": {
            "material_part_shared_direct_frames": sum(row["pair_role"] == "MATERIAL_PART" for row in direct_frames),
            "preparation_shared_direct_frames": sum(row["pair_role"] == "PREPARATION" for row in direct_frames),
            "cthy_radius2_preparation_pair_hits": sum(
                row["shared_neighbor_surface"] == "cthy" for row in radius2_frames
            ),
            "cthy_radius2_disposition": "LEAF_DRUG_RELAY_LEAD_NO_EXACT_COMPOSITION",
            "preparation_pair_direct_value_frame": "daiin",
            "preparation_pair_direct_material_frame": "al",
        },
        "solvent_result": {
            "specific_solvent_selected": 0,
            "water": "NO_DISTINGUISHING_WHOLE",
            "wine": "NO_DISTINGUISHING_WHOLE",
            "oil": "OL_NEUTRAL_CARRIER_RIVAL_NOT_MOIST_SELECTIVE",
            "best_cross_role_moist_medium_candidate": "ckhy",
            "ckhy_evidence": "2_EDGES_2_PAGES_SHEOR_AND_SHEO_RAW_LIFT_8.234286",
            "repeated_moist_preparation_complement": "pcheey",
            "pcheey_evidence": "2_SHEO_CONTACTS_2_PAGES_OF_3_GLOBAL_EXACT_OCCURRENCES",
            "pcheey_old_pulvis_literal": "QUARANTINED_ZERO_CREDIT",
            "next_solvent_route": "REQUIRES_SHARED_EXACT_MEDIUM_PLUS_MOIST_PREPARATION_CONSTRUCTION",
        },
        "guard": {"inherited_token_query": inherited_guard},
        "semantic_quarantine": {
            "gdt754_source_composed_surfaces": len(sieve_rows),
            "gdt737_retired_head_surfaces": len(retired_surfaces),
            "gdt738_retired_salt_surfaces": len(retired_salt_surfaces),
            "later_repaired_surface_exemptions": len(later_repaired_surfaces),
            "active_suspect_surface_union": len(suspect_surfaces),
        },
        "claim_boundary": {
            "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
            "confirmed_plant_identities": 0, "confirmed_solvents": 0,
            "component_values": 0, "new_pages": 0, "new_images": 0,
            "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
