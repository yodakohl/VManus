#!/usr/bin/env python3
"""Adjudicate GDT741's five exposed radius-two collision targets."""

from __future__ import annotations

import argparse
import csv
import hashlib
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
BASE_REL = Path("experiments/yolo/gdt742_r2_open_collision_adjudication")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G741_REL = Path("experiments/yolo/gdt741_local_attachment_boundary_relay_grammar")
G741 = ROOT / G741_REL
G741_ART = G741 / "artifacts"
COMPACT_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/"
    "artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
)
COMPACT = ROOT / COMPACT_REL

CARRIER_ORDER = ("PREPARATION", "MATERIAL", "PART")
DECISION_FIELDS = (
    "distance", "selected_roles", "formal_role_direction_match",
    "guarded_reader_exact_full_frame_occurrences", "middle_reader_exact",
    "middle_known", "intervening_emits_own_unit",
    "intervening_strict_initial_head", "intervening_another_gdt738_target",
    "middle_barrier", "target_wanted_carrier_set", "host_carrier_set",
    "middle_carrier_set", "axis_continuity",
)
CLASS_FIELDS = (
    "selected_roles", "formal_role_direction_match",
    "guarded_reader_exact_full_frame_occurrences", "middle_reader_exact",
    "middle_known", "intervening_emits_own_unit",
    "intervening_strict_initial_head", "intervening_another_gdt738_target",
    "middle_barrier", "axis_continuity", "carrier_continuity",
)
STATUS = (
    "PARTIAL__ROLE_SEPARATED_CARRIER_RELAY_ADDS_TWO_TARGETS__"
    "FOUR_OF_EIGHT_R2_CANDIDATE_ROLES_ACTIVE__FOUR_OPEN_ROLES_ON_THREE_TARGETS__"
    "45_CARRIER_BOUND__58_SPECIFIC__144_OPEN__ZERO_NEW_AXIS__"
    "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv",
    "R2_32_FEATURE_CLASS_CENSUS.tsv",
    "CANDIDATE_8_ROLE_ADJUDICATION.tsv",
    "TARGET_202_RENDERER_PATCH_V4.tsv",
    "FOCUS_7_CACHED_LINE_REVIEW.tsv",
    "GDT742_GDT388_TWO_CARRIER_RELAY_EDGE_PACKET.tsv",
    "GDT742_ROLE_SEPARATION_READER.md",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="ignore",
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


def values(value: object, separator: str = "|") -> set[str]:
    text = str(value)
    if text in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(text.split(separator))


def common_frame(feature: dict[str, str]) -> bool:
    return bool(
        feature["distance"] == "2"
        and int(feature["guarded_reader_exact_full_frame_occurrences"]) >= 1
        and feature["middle_reader_exact"] == "1"
        and feature["middle_known"] == "1"
        and feature["intervening_emits_own_unit"] == "1"
        and feature["intervening_strict_initial_head"] == "0"
        and feature["intervening_another_gdt738_target"] == "0"
    )


def adjudicate_r2(feature: dict[str, str]) -> dict[str, object]:
    """Return radius-two roles from an identity- and predecessor-outcome-free record."""
    if set(feature) != set(DECISION_FIELDS):
        raise AssertionError("radius-two decision record changed")
    selected = values(feature["selected_roles"], "+")
    wanted = values(feature["target_wanted_carrier_set"])
    host_carriers = values(feature["host_carrier_set"])
    middle_carriers = values(feature["middle_carrier_set"])
    frame = common_frame(feature)
    open_direction = bool(
        frame and feature["middle_barrier"] == "OPEN"
        and feature["formal_role_direction_match"] == "1"
    )
    exact_axis = feature["axis_continuity"] == "EXACT_SINGLE"
    axis_relay = bool(open_direction and selected == {"AXIS"} and exact_axis)
    full_carrier = bool(wanted and wanted <= host_carriers and wanted <= middle_carriers)
    role_separated_carrier = bool(
        open_direction and full_carrier
        and (
            selected == {"CARRIER"}
            or selected == {"AXIS", "CARRIER"}
            and feature["axis_continuity"] == "NONE"
        )
    )
    if axis_relay:
        trace = "STRICT_AXIS_RELAY"
    elif role_separated_carrier and selected == {"CARRIER"}:
        trace = "STRICT_CARRIER_RELAY"
    elif role_separated_carrier:
        trace = "ROLE_SEPARATED_CARRIER_RELAY"
    else:
        trace = "R2_HOLD"
    return {
        "axis_role_retained": int(axis_relay),
        "carrier_role_retained": int(role_separated_carrier),
        "common_frame": int(frame),
        "full_carrier_continuity_recomputed": int(full_carrier),
        "rule_trace": trace,
    }


def contact_dispatch(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in source_rows:
        row: dict[str, object] = dict(source)
        if source["distance"] == "2":
            decision = adjudicate_r2({field: source[field] for field in DECISION_FIELDS})
            new_axis = int(decision["axis_role_retained"])
            new_carrier = int(decision["carrier_role_retained"])
            trace = str(decision["rule_trace"])
            frame = int(decision["common_frame"])
            full_carrier = int(decision["full_carrier_continuity_recomputed"])
        else:
            new_axis = int(source["predicted_axis_role_retained"])
            new_carrier = int(source["predicted_carrier_role_retained"])
            trace = "GDT741_DIRECT_INHERITED"
            frame = 0
            full_carrier = int(source["single_host_covers_requested_carrier"])
        old_axis = int(source["predicted_axis_role_retained"])
        old_carrier = int(source["predicted_carrier_role_retained"])
        row.update({
            "gdt742_axis_role_retained": new_axis,
            "gdt742_carrier_role_retained": new_carrier,
            "gdt742_renderer_role_retained": int(new_axis or new_carrier),
            "gdt742_rule_trace": trace,
            "common_frame_recomputed": frame,
            "full_carrier_continuity_recomputed": full_carrier,
            "axis_changed_from_gdt741": int(new_axis != old_axis),
            "carrier_changed_from_gdt741": int(new_carrier != old_carrier),
            "role_changed_from_gdt741": int(new_axis != old_axis or new_carrier != old_carrier),
            "dispatcher_uses_dispatch_id_or_locus": 0,
            "literal_plaintext_claimed": 0,
            "component_export_credit": 0,
        })
        output.append(row)
    return output


def feature_classes(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        if row["distance"] == "2":
            grouped[tuple(str(row[field]) for field in CLASS_FIELDS)].append(row)
    output: list[dict[str, object]] = []
    for key in sorted(grouped):
        rows = grouped[key]
        new_promotions = sum(int(row["carrier_changed_from_gdt741"]) for row in rows)
        active = sum(int(row["gdt742_renderer_role_retained"]) for row in rows)
        if new_promotions:
            class_status = "REPEATED_ROLE_SEPARATION_PROMOTION"
        elif active:
            class_status = "ACTIVE_STRICT_CLASS"
        elif len(rows) > 1:
            class_status = "REPEATED_HOLD_CLASS"
        else:
            class_status = "SINGLETON_HOLD_CLASS"
        output.append({
            "feature_class_id": f"G742-K{len(output) + 1:02d}",
            "feature_signature": ";".join(
                f"{field}={value}" for field, value in zip(CLASS_FIELDS, key, strict=True)
            ),
            "contacts": len(rows),
            "targets": len({str(row["dispatch_id"]) for row in rows}),
            "member_contact_ids_audit_only": "|".join(str(row["attachment_contact_id"]) for row in rows),
            "member_dispatch_ids_audit_only": "|".join(str(row["dispatch_id"]) for row in rows),
            "gdt741_role_patterns": "|".join(sorted({
                f"A{row['predicted_axis_role_retained']}C{row['predicted_carrier_role_retained']}"
                for row in rows
            })),
            "gdt742_role_patterns": "|".join(sorted({
                f"A{row['gdt742_axis_role_retained']}C{row['gdt742_carrier_role_retained']}"
                for row in rows
            })),
            "new_carrier_promotions": new_promotions,
            "class_status": class_status,
            "repeated_feature_class": int(len(rows) > 1),
            "literal_plaintext_claimed": 0,
        })
    return output


def candidate_adjudication(
    source_rows: list[dict[str, str]], contacts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in source_rows:
        contact = contacts[source["attachment_contact_id"]]
        role = source["candidate_role"]
        old_active = int(
            contact["predicted_axis_role_retained"]
            if role == "AXIS" else contact["predicted_carrier_role_retained"]
        )
        new_active = int(
            contact["gdt742_axis_role_retained"]
            if role == "AXIS" else contact["gdt742_carrier_role_retained"]
        )
        changed = int(new_active != old_active)
        if changed and new_active:
            status = "PROMOTE_ROLE_SEPARATED_CARRIER"
            reason = (
                "formal direction and open exact frame agree; carrier is complete in host "
                "and middle while the selected axis has no continuity"
            )
        elif changed:
            status = "DEACTIVATE_INCONSISTENT_RELAY"
            reason = "the role-separated rule no longer licenses an inherited active role"
        elif new_active:
            status = "ACTIVE_INHERITED_STRICT_RELAY"
            reason = "replays the GDT741 strict single-role relay"
        else:
            status = "HOLD_OPEN_COLLISION"
            failures: list[str] = []
            if contact["formal_role_direction_match"] != "1":
                failures.append("formal direction reverses")
            if contact["middle_barrier"] != "OPEN":
                failures.append(f"middle barrier is {contact['middle_barrier']}")
            if role == "AXIS" and contact["axis_continuity"] != "EXACT_SINGLE":
                failures.append(f"axis continuity is {contact['axis_continuity']}")
            if role == "CARRIER" and contact["carrier_continuity"] != "FULL_WANTED":
                failures.append(f"carrier continuity is {contact['carrier_continuity']}")
            if role == "CARRIER" and contact["axis_continuity"] != "NONE" and contact["selected_roles"] == "AXIS+CARRIER":
                failures.append("mixed contact also carries an unresolved axis")
            reason = "; ".join(failures) or "does not satisfy the role-separated relay rule"
        output.append({
            "adjudication_id": f"G742-C{len(output) + 1:02d}",
            "gdt741_sensitivity_id": source["sensitivity_id"],
            "attachment_contact_id": source["attachment_contact_id"],
            "gdt739_dispatch_id": source["gdt739_dispatch_id"],
            "page": source["page"], "locus": source["locus"],
            "target_surface": source["target_surface"],
            "candidate_role": role,
            "selected_roles": contact["selected_roles"],
            "formal_direction_match": contact["formal_role_direction_match"],
            "middle_barrier": contact["middle_barrier"],
            "axis_continuity": contact["axis_continuity"],
            "carrier_continuity": contact["carrier_continuity"],
            "gdt741_role_active": old_active,
            "gdt742_role_active": new_active,
            "changed_from_gdt741": changed,
            "gdt742_status": status,
            "working_reason": reason,
            "renderer_license": new_active,
            "literal_plaintext_claimed": 0,
            "component_export_credit": 0,
        })
    return output


def carrier_name(row: dict[str, object]) -> str:
    carriers = values(row["target_wanted_carrier_set"])
    return "_".join(carrier for carrier in CARRIER_ORDER if carrier in carriers) or "OPEN"


def render_open_scalar(source: dict[str, str], carrier: str) -> str:
    """Render the only promotion shape admitted in the fixed GDT742 deck."""
    if source["family"] != "SCALAR" or source["gdt741_dimension_dispatch"] != "OPEN_SCALAR":
        raise AssertionError("GDT742 carrier promotion is not an open scalar")
    genitive = {
        "PREPARATION": "der Zubereitung",
        "MATERIAL": "des Materials",
        "PART": "der Teilfraktion",
        "PREPARATION_MATERIAL": "des Zubereitungsmaterials",
        "PREPARATION_PART": "der Zubereitungsfraktion",
        "MATERIAL_PART": "des Materialteils",
        "PREPARATION_MATERIAL_PART": "der Zubereitungsfraktion",
    }[carrier]
    render = f"Skalarstufe {source['level']} {genitive}; Dimension offen"
    if source["surface"] == "sain" and source["line_position"] == "FIRST":
        render += "; Eintrag"
    elif source["surface"] == "rain":
        render += "; Abschlussbezug" if source["line_position"] == "LAST" else "; interner Rückbezug"
    elif source["surface"] == "lain":
        render = "interne " + render
    elif source["surface"] == "skaiin" and source["line_position"] == "FIRST":
        render += "; Eintrag"
    return render


def renderer_patches(
    source_rows: list[dict[str, str]], contacts: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_dispatch: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        by_dispatch[str(row["dispatch_id"])].append(row)
    output: list[dict[str, object]] = []
    for source in source_rows:
        dispatch_id = source["gdt739_dispatch_id"]
        rows = by_dispatch.get(dispatch_id, [])
        carrier_rows = [row for row in rows if int(row["gdt742_carrier_role_retained"])]
        carrier = source["gdt741_carrier_dispatch"]
        if carrier == "OPEN" and carrier_rows:
            candidate_carriers = {carrier_name(row) for row in carrier_rows}
            if len(candidate_carriers) != 1:
                raise AssertionError(f"ambiguous new carrier for {dispatch_id}")
            carrier = next(iter(candidate_carriers))
        dimension = source["gdt741_dimension_dispatch"]
        mode = source["gdt741_state_mode"]
        render = source["gdt741_working_render_de"]
        if carrier != source["gdt741_carrier_dispatch"]:
            render = render_open_scalar(source, carrier)
        changed = int(
            carrier != source["gdt741_carrier_dispatch"]
            or render != source["gdt741_working_render_de"]
        )
        specific = int(
            int(source["axis_specific_dispatch_retained"])
            or carrier != "OPEN" or mode == "PROCESS_RESULT"
        )
        output.append({
            "gdt742_patch_id": f"G742-R{len(output) + 1:04d}",
            "gdt741_patch_id": source["gdt741_patch_id"],
            **{field: source[field] for field in (
                "gdt739_dispatch_id", "patch_id", "occurrence_id", "page", "locus",
                "token_index", "token_ordinal", "surface", "body", "opaque_head_id",
                "line_position", "family", "level",
            )},
            "gdt742_rule_trace": (
                "ROLE_SEPARATED_CARRIER_RELAY"
                if changed else "GDT741_RENDER_INHERITED"
            ),
            "gdt741_dimension_dispatch": source["gdt741_dimension_dispatch"],
            "gdt742_dimension_dispatch": dimension,
            "gdt741_carrier_dispatch": source["gdt741_carrier_dispatch"],
            "gdt742_carrier_dispatch": carrier,
            "gdt741_state_mode": source["gdt741_state_mode"],
            "gdt742_state_mode": mode,
            "gdt741_working_render_de": source["gdt741_working_render_de"],
            "gdt742_working_render_de": render,
            "axis_specific_dispatch_retained": source["axis_specific_dispatch_retained"],
            "carrier_locally_bound_retained": int(carrier != "OPEN"),
            "specific_local_dispatch_retained": specific,
            "active_radius_two_carrier_contacts": sum(
                row["distance"] == "2" and int(row["gdt742_carrier_role_retained"])
                for row in rows
            ),
            "changed_from_gdt741": changed,
            "dispatcher_uses_dispatch_id_or_locus": 0,
            "scope": "EXACT_COMPLETE_SURFACE_AT_THIS_ENUMERATED_OCCURRENCE",
            "literal_patient_or_species_claimed": 0,
            "literal_plaintext_claimed": 0,
            "unconditional_global_export": 0,
            "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
        })
    return output


def focus_reviews(
    candidates: list[dict[str, object]], contacts: dict[str, dict[str, object]],
    patches: dict[str, dict[str, object]], compact_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    candidate_by_dispatch: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidates:
        candidate_by_dispatch[str(row["gdt739_dispatch_id"])].append(row)
    loci = {str(rows[0]["locus"]) for rows in candidate_by_dispatch.values()}
    compact_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in compact_rows:
        if row["locus"] in loci:
            compact_by_locus[row["locus"]].append(row)
    output: list[dict[str, object]] = []
    for dispatch_id in sorted(candidate_by_dispatch):
        candidate_rows = candidate_by_dispatch[dispatch_id]
        contact = contacts[str(candidate_rows[0]["attachment_contact_id"])]
        locus = str(contact["locus"])
        line = sorted(compact_by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        if not line:
            raise AssertionError(f"missing cached line {locus}")
        ordinals = {int(row["token_ordinal"]): row["surface"] for row in line}
        start = min(int(contact["target_ordinal"]), int(contact["neighbor_ordinal"]))
        stop = max(int(contact["target_ordinal"]), int(contact["neighbor_ordinal"]))
        frame = " ".join(ordinals[ordinal] for ordinal in range(start, stop + 1))
        target_patch = patches[dispatch_id]
        statuses = {str(row["gdt742_status"]) for row in candidate_rows}
        if "PROMOTE_ROLE_SEPARATED_CARRIER" in statuses:
            decision = "PROMOTE_CARRIER_ONLY"
        elif statuses == {"ACTIVE_INHERITED_STRICT_RELAY"}:
            decision = "INHERIT_STRICT_RELAY"
        else:
            decision = "HOLD_OPEN_COLLISION"
        output.append({
            "focus_id": f"G742-F{len(output) + 1:02d}",
            "gdt739_dispatch_id": dispatch_id,
            "page": contact["page"], "locus": locus,
            "target_ordinal": contact["target_ordinal"],
            "target_surface": contact["target_surface"],
            "candidate_roles": "+".join(sorted(str(row["candidate_role"]) for row in candidate_rows)),
            "line_eva_cached": " ".join(row["surface"] for row in line),
            "radius_two_frame_manuscript_order": frame,
            "gdt741_target_render_de": target_patch["gdt741_working_render_de"],
            "gdt742_target_render_de": target_patch["gdt742_working_render_de"],
            "focus_decision": decision,
            "working_reason": " | ".join(str(row["working_reason"]) for row in candidate_rows),
            "reader_note": "cached line and target-level audit only; no plaintext clause or free attachment is implied",
            "new_page_or_transcription": 0,
        })
    return output


def physical_folio(page: str) -> str:
    digits = "".join(character for character in page[1:] if character.isdigit())
    return f"f{digits}" if digits else page


def edge_packet(
    candidates: list[dict[str, object]], contacts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for candidate in candidates:
        if not int(candidate["changed_from_gdt741"]):
            continue
        contact = contacts[str(candidate["attachment_contact_id"])]
        output.append({
            "edge_id": f"G742E{len(output) + 1:03d}",
            "batch_id": "GDT742_ROLE_SEPARATED_CARRIER_RELAY",
            "page": contact["page"],
            "physical_folio": physical_folio(str(contact["page"])),
            "diagram_unit_id": "CACHED_TEXT_LINE",
            "pivot_visual_id": f"TARGET_TOKEN_{contact['target_ordinal']}",
            "pivot_locus": f"{contact['locus']}@{contact['target_ordinal']}",
            "target_visual_id": f"R2_HOST_TOKEN_{contact['neighbor_ordinal']}",
            "target_locus": f"{contact['locus']}@{contact['neighbor_ordinal']}",
            "relation_type": "ROLE_SEPARATED_CARRIER_RELAY",
            "direction_basis": "FORMAL_ROLE_DIRECTION_PLUS_OPEN_EXACT_FRAME",
            "ownership_basis": "FULL_CARRIER_WITH_ZERO_AXIS_CONTINUITY",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT742",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT742_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "B_REPEATED_FEATURE_CLASS_WORKING",
            "ambiguity_state": "PROVISIONAL_ROLE_SEPARATION",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_ATTACHMENT_EDGE",
        })
    return output


def reader_markdown(
    classes: list[dict[str, object]], candidates: list[dict[str, object]],
    focus: list[dict[str, object]], patches: list[dict[str, object]],
) -> str:
    promoted = [row for row in candidates if int(row["changed_from_gdt741"])]
    lines = [
        "# GDT742 role-separated carrier-relay reader", "",
        "Two in-sample contacts share one reduced, role-isomorphic and outcome-free",
        "radius-two signature and gain only their carrier role. Concrete carrier identity",
        "is intentionally abstracted by that signature, so this is not independent",
        "confirmation. Their quality axis remains open. This is an occurrence-scoped",
        "working renderer change, not a word translation. MATERIAL and PREPARATION are",
        "broad model tags, not identified manuscript words or ingredients.", "",
        "## Candidate roles", "",
        "| target | role | direction | axis continuity | carrier continuity | decision |", "|---|---|---:|---|---|---|",
    ]
    for row in candidates:
        lines.append(
            f"| `{row['gdt739_dispatch_id']}` `{row['target_surface']}` | {row['candidate_role']} | "
            f"{row['formal_direction_match']} | {row['axis_continuity']} | "
            f"{row['carrier_continuity']} | {row['gdt742_status']} |"
        )
    lines.extend([
        "", "## Promoted carrier-only targets", "",
    ])
    patch_map = {str(row["gdt739_dispatch_id"]): row for row in patches}
    for row in promoted:
        patch = patch_map[str(row["gdt739_dispatch_id"])]
        inherited_position = (
            "Abschlussbezug" if patch["line_position"] == "LAST"
            else "Eintragsbezug" if patch["line_position"] == "FIRST"
            else "interner Positionsbezug"
        )
        lines.append(
            f"- `{row['locus']}` `{row['target_surface']}`: "
            f"**[Carrier={patch['gdt742_carrier_dispatch']}; Achse offen; "
            f"geerbte Stufe {patch['level']}; geerbter {inherited_position}]**"
        )
    lines.extend([
        "", "## Seven cached focus lines", "",
    ])
    for row in focus:
        lines.extend([
            f"### {row['focus_id']} — {row['locus']}", "",
            f"`{row['line_eva_cached']}`", "",
            f"Frame: `{row['radius_two_frame_manuscript_order']}`", "",
            f"Arbeitsrenderer (Metatags, kein Klartext): "
            f"**{row['gdt742_target_render_de']}** — {row['focus_decision']}", "",
        ])
    promoted_classes = [row for row in classes if int(row["new_carrier_promotions"])]
    lines.extend([
        "## Feature-class summary", "",
        f"Under the declared reduced role-isomorphic signature, the 41 radius-two "
        f"contacts form {len(classes)} outcome-free feature classes; "
        f"{sum(int(row['repeated_feature_class']) for row in classes)} repeat. Exactly "
        f"{len(promoted_classes)} repeated class supplies the two new carrier roles.", "",
        "## Ceiling", "",
        "No new axis, component, lexeme, plaintext clause, patient, species, unit, page,",
        "image or transcription is claimed.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    source_contacts = read_tsv(G741_ART / "CONTACT_103_GRAMMAR_DISPATCH.tsv")
    source_candidates = read_tsv(G741_ART / "R2_8_STRICT_AND_OPEN_COLLISION_CANDIDATES.tsv")
    source_patches = read_tsv(G741_ART / "TARGET_202_RENDERER_PATCH_V3.tsv")
    if len(source_contacts) != 103 or len(source_candidates) != 8 or len(source_patches) != 202:
        raise AssertionError("GDT741 source boundary changed")
    compact = read_tsv(COMPACT)
    source_decks = (source_contacts, source_candidates, source_patches, compact)
    if any(
        row.get("page", "").startswith("f84") or row.get("locus", "").startswith("f84")
        for deck in source_decks for row in deck
    ):
        raise AssertionError("sealed page entered GDT742")
    if (
        len({row["attachment_contact_id"] for row in source_contacts}) != len(source_contacts)
        or len({row["sensitivity_id"] for row in source_candidates}) != len(source_candidates)
        or len({(row["attachment_contact_id"], row["candidate_role"]) for row in source_candidates})
        != len(source_candidates)
        or len({row["gdt739_dispatch_id"] for row in source_patches}) != len(source_patches)
        or len({(row["locus"], row["token_ordinal"]) for row in compact}) != len(compact)
    ):
        raise AssertionError("source key uniqueness changed")

    contacts = contact_dispatch(source_contacts)
    if any(
        int(row["gdt742_axis_role_retained"]) < int(row["predicted_axis_role_retained"])
        or int(row["gdt742_carrier_role_retained"]) < int(row["predicted_carrier_role_retained"])
        for row in contacts
    ):
        raise AssertionError("GDT742 promotion-only renderer cannot encode a role deactivation")
    contact_map = {str(row["attachment_contact_id"]): row for row in contacts}
    if len(contact_map) != len(contacts):
        raise AssertionError("contact map would overwrite a duplicate")
    classes = feature_classes(contacts)
    candidates = candidate_adjudication(source_candidates, contact_map)
    patches = renderer_patches(source_patches, contacts)
    patch_map = {str(row["gdt739_dispatch_id"]): row for row in patches}
    focus = focus_reviews(candidates, contact_map, patch_map, compact)
    edges = edge_packet(candidates, contact_map)
    reader = reader_markdown(classes, candidates, focus, patches)

    write_tsv(output_dir / "CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv", contacts, (
        "attachment_contact_id", "window_id", "dispatch_id", "patch_id", "page", "locus",
        "target_ordinal", "target_surface", "opaque_head_id", "line_position",
        "target_family", "target_level", "target_favored_axis", "target_dimension",
        "target_prior_state_mode",
        "selected_roles", "side", "signed_offset", "distance", "neighbor_ordinal",
        "neighbor_surface", "formal_role_direction_match",
        "guarded_reader_exact_pair_occurrences", "guarded_reader_exact_full_frame_occurrences",
        "intervening_surface", "intervening_emits_own_unit",
        "intervening_strict_initial_head", "intervening_another_gdt738_target",
        "target_wanted_carrier_set", "host_quality_set", "host_carrier_set",
        "host_scalar_class_set", "host_boundary_set", "host_axis_signature",
        "middle_quality_set", "middle_carrier_set", "middle_scalar_class_set",
        "middle_boundary_set", "middle_axis_signature",
        "middle_reader_exact", "middle_known", "middle_positive_host_eligible",
        "middle_ineligibility_reasons", "middle_barrier", "axis_continuity",
        "carrier_continuity", "predicted_axis_role_retained",
        "predicted_carrier_role_retained", "gdt742_axis_role_retained",
        "gdt742_carrier_role_retained", "gdt742_renderer_role_retained",
        "common_frame_recomputed", "full_carrier_continuity_recomputed",
        "gdt742_rule_trace", "axis_changed_from_gdt741",
        "carrier_changed_from_gdt741", "role_changed_from_gdt741",
        "dispatcher_uses_dispatch_id_or_locus", "literal_plaintext_claimed",
        "component_export_credit",
    ))
    write_tsv(output_dir / "R2_32_FEATURE_CLASS_CENSUS.tsv", classes, classes[0].keys())
    write_tsv(output_dir / "CANDIDATE_8_ROLE_ADJUDICATION.tsv", candidates, candidates[0].keys())
    write_tsv(output_dir / "TARGET_202_RENDERER_PATCH_V4.tsv", patches, patches[0].keys())
    write_tsv(output_dir / "FOCUS_7_CACHED_LINE_REVIEW.tsv", focus, focus[0].keys())
    write_tsv(output_dir / "GDT742_GDT388_TWO_CARRIER_RELAY_EDGE_PACKET.tsv", edges, (
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
        "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
        "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
        "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256",
        "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
        "relation_confidence", "ambiguity_state", "formal_access_state",
        "fold_assignment", "eligibility_status",
    ))
    (output_dir / "GDT742_ROLE_SEPARATION_READER.md").write_text(reader, encoding="utf-8")

    artifact_hashes = {
        str(BASE_REL / "artifacts" / name): sha256(output_dir / name)
        for name in OUTPUT_NAMES
    }
    r2 = [row for row in contacts if row["distance"] == "2"]
    result = {
        "schema": "GDT742_R2_OPEN_COLLISION_ADJUDICATION_V1",
        "status": STATUS,
        "scope": {
            "inherited_allowlist_pages": 179,
            "renderer_positions": len(patches),
            "radius_two_contacts": len(r2),
            "candidate_roles": len(candidates),
            "candidate_targets": len({row["gdt739_dispatch_id"] for row in candidates}),
            "focus_cached_lines": len(focus),
            "new_pages_used": 0, "f84_used": False, "f84r_used": False,
        },
        "feature_classes": {
            "radius_two_classes": len(classes),
            "repeated_classes": sum(int(row["repeated_feature_class"]) for row in classes),
            "promotion_classes": sum(int(row["new_carrier_promotions"]) > 0 for row in classes),
            "promoted_class_members": sum(int(row["new_carrier_promotions"]) for row in classes),
        },
        "roles": {
            "gdt741_active_candidate_roles": sum(int(row["gdt741_role_active"]) for row in candidates),
            "gdt742_active_candidate_roles": sum(int(row["gdt742_role_active"]) for row in candidates),
            "new_carrier_roles": sum(int(row["changed_from_gdt741"]) for row in candidates),
            "open_candidate_roles": sum(not int(row["gdt742_role_active"]) for row in candidates),
            "open_candidate_targets": len({
                row["gdt739_dispatch_id"] for row in candidates if not int(row["gdt742_role_active"])
            }),
            "axis_role_changes": sum(int(row["axis_changed_from_gdt741"]) for row in contacts),
            "carrier_role_changes": sum(int(row["carrier_changed_from_gdt741"]) for row in contacts),
        },
        "renderer": {
            "axis_specific_occurrences": sum(int(row["axis_specific_dispatch_retained"]) for row in patches),
            "carrier_bound_occurrences": sum(int(row["carrier_locally_bound_retained"]) for row in patches),
            "specific_occurrences": sum(int(row["specific_local_dispatch_retained"]) for row in patches),
            "fully_open_occurrences": sum(not int(row["specific_local_dispatch_retained"]) for row in patches),
            "changed_from_gdt741": sum(int(row["changed_from_gdt741"]) for row in patches),
        },
        "edge_intake": {"expected_status": "INVALID_PACKET", "packet_rows": len(edges), "score_ready": False},
        "claims": {
            "new_axes": 0, "components_exported": 0, "lexemes_identified": 0,
            "plaintext_clauses": 0, "literal_patients_or_species": 0,
            "unseen_forms_licensed": 0, "new_pages": 0,
        },
        "artifact_hashes": artifact_hashes,
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": STATUS,
        "roles": result["roles"],
        "renderer": result["renderer"],
        "feature_classes": result["feature_classes"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
