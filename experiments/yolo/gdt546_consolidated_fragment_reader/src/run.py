#!/usr/bin/env python3
"""Compile GDT543--GDT545 into one exact surface-keyed fragment reader."""

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
BASE = ROOT / "experiments/yolo/gdt546_consolidated_fragment_reader"
OUT = BASE / "artifacts"
G543 = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames/artifacts"
G544 = ROOT / "experiments/yolo/gdt544_flagged_equal_length_anchor_availability/artifacts"
G545 = ROOT / "experiments/yolo/gdt545_shorter_secondary_fragment_bridges/artifacts"

CARD_IN = G543 / "gdt543_81_fragment_extension_cards.tsv"
ARM_IN = G543 / "gdt543_93_directional_extension_arms.tsv"
FAMILY_IN = G543 / "gdt543_16_recurrent_anchor_families.tsv"
FLAG_IN = G544 / "gdt544_16_flagged_target_anchor_availability.tsv"
BRIDGE_IN = G545 / "gdt545_4_secondary_bridge_cards.tsv"
UNREPAIRED_IN = G545 / "gdt545_12_unrepaired_flagged_cards.tsv"

READER_OUT = OUT / "gdt546_81_consolidated_fragment_reader.tsv"
SUMMARY_OUT = OUT / "gdt546_fragment_reader_summary.tsv"
BOOK_OUT = OUT / "GDT546_81_CARD_FRAGMENT_READER.md"
RESULT_OUT = OUT / "gdt546_result.json"

STATUS = "PASS_81_CARD_FRAGMENT_READER__4_DUAL_BRIDGES__12_EXPLICIT_DEFAULTS"
NONE = "NONE"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def key_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    keyed = {row[field]: row for row in rows}
    if len(keyed) != len(rows):
        raise RuntimeError(f"Duplicate {field} in source table")
    return keyed


def formula(left: str, anchor: str, right: str) -> str:
    parts = []
    if left != NONE:
        parts.append(left)
    parts.append(f"[{anchor}]")
    if right != NONE:
        parts.append(right)
    return "+".join(parts)


def visible_formula(left: str, stem: str, right: str, status: str) -> str:
    parts = []
    if left != NONE:
        parts.append(left)
    if stem == NONE:
        parts.append("[NO_EXACT_OLD_VISIBLE_STEM]")
    elif status == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM":
        parts.append(f"[~{stem}]")
    else:
        parts.append(f"[{stem}]")
    if right != NONE:
        parts.append(right)
    return "+".join(parts)


def context_compatible(relation: str) -> bool:
    return relation in {"TARGET_MODE_SET_EQUAL", "TARGET_MODE_SET_INCLUDED"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARD_IN)
    arms = read_tsv(ARM_IN)
    families = read_tsv(FAMILY_IN)
    flags = read_tsv(FLAG_IN)
    bridges = read_tsv(BRIDGE_IN)
    unrepaired = read_tsv(UNREPAIRED_IN)
    observed = tuple(map(len, (cards, arms, families, flags, bridges, unrepaired)))
    if observed != (81, 93, 16, 16, 4, 12):
        raise RuntimeError(f"Input inventory drift: {observed}")

    flag_by_surface = key_by(flags, "surface")
    bridge_by_surface = key_by(bridges, "surface")
    unrepaired_by_surface = key_by(unrepaired, "surface")
    family_by_anchor = key_by(families, "anchor_recipe")
    arm_by_key = {(row["target_surface"], row["side"]): row for row in arms}
    if len(arm_by_key) != 93:
        raise RuntimeError("Duplicate GDT543 target-side arm")
    if set(bridge_by_surface) | set(unrepaired_by_surface) != set(flag_by_surface):
        raise RuntimeError("GDT545 bridge/default partition drift")
    if set(bridge_by_surface) & set(unrepaired_by_surface):
        raise RuntimeError("GDT545 bridge/default overlap")

    output_rows: list[dict[str, object]] = []
    for card in sorted(cards, key=lambda row: int(row["target_ordinal"])):
        surface = card["surface"]
        left = arm_by_key.get((surface, "LEFT"))
        right = arm_by_key.get((surface, "RIGHT"))
        flag = flag_by_surface.get(surface)
        bridge = bridge_by_surface.get(surface)
        residual = unrepaired_by_surface.get(surface)
        family = family_by_anchor.get(card["anchor_recipe"])

        expected_sides = {
            "LEFT_EXTENSION": {"LEFT"},
            "RIGHT_EXTENSION": {"RIGHT"},
            "BOTH_SIDES": {"LEFT", "RIGHT"},
        }[card["extension_direction"]]
        actual_sides = {
            side for side, arm in (("LEFT", left), ("RIGHT", right)) if arm is not None
        }
        if expected_sides != actual_sides:
            raise RuntimeError(f"Arm inventory drift for {surface}: {actual_sides}")

        if bridge:
            resolution = "SECONDARY_BRIDGE_ADDED__PRIMARY_RETAINED"
            current_caution = (
                "SECONDARY_DIRECTION_MISMATCH__KEEP_PRIMARY"
                if bridge["secondary_visible_stem_status"]
                == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM"
                else "DUAL_DERIVATION__NO_PRIMARY_CHANGE"
            )
        elif residual:
            resolution = "EXPLICIT_WORKING_DEFAULT__NO_QUALIFIED_SECONDARY"
            current_caution = residual["flag_reasons"]
        else:
            resolution = "NOT_FLAGGED"
            current_caution = "NONE"

        secondary_left = bridge["secondary_left_extension_recipe"] if bridge else NONE
        secondary_right = bridge["secondary_right_extension_recipe"] if bridge else NONE
        secondary_anchor = bridge["secondary_anchor_recipe"] if bridge else NONE
        secondary_visible = bridge["secondary_visible_stem_surface"] if bridge else NONE
        secondary_visible_status = bridge["secondary_visible_stem_status"] if bridge else NONE

        output_rows.append(
            {
                "target_ordinal": card["target_ordinal"],
                "surface": surface,
                "reader_decision": "READ_KNOWN_FRAGMENT_WORKING_CARD",
                "final_recipe": card["final_recipe"],
                "observed_requirement_modes": card["observed_requirement_modes"],
                "neutral_component_reading_de": card["neutral_surface_phrase_de"],
                "known_contextual_readings_de": card["known_contextual_readings_de"],
                "primary_structural_formula": formula(
                    card["left_extension_recipe"],
                    card["anchor_recipe"],
                    card["right_extension_recipe"],
                ),
                "primary_visible_formula": visible_formula(
                    card["visible_left_extension"],
                    card["visible_stem_surface"],
                    card["visible_right_extension"],
                    card["visible_stem_status"],
                ),
                "primary_anchor_recipe": card["anchor_recipe"],
                "primary_anchor_start_atom": card["anchor_start_atom"],
                "primary_anchor_atom_count": card["anchor_atom_count"],
                "primary_anchor_old_event_count": card["old_anchor_event_count"],
                "primary_anchor_old_surfaces": card["old_anchor_surfaces"],
                "primary_visible_stem_status": card["visible_stem_status"],
                "primary_visible_stem_surface": card["visible_stem_surface"],
                "extension_direction": card["extension_direction"],
                "left_extension_recipe": card["left_extension_recipe"],
                "left_visible_affix": card["visible_left_extension"],
                "left_channel_class": left["visible_channel_class"] if left else NONE,
                "left_channel_observation_count": left["visible_channel_observation_count"] if left else 0,
                "left_channel_recipe_variants": left["visible_channel_recipe_variants"] if left else NONE,
                "left_interface_pair": left["interface_pair"] if left else NONE,
                "left_interface_old_event_count": left["old_interface_event_count"] if left else 0,
                "right_extension_recipe": card["right_extension_recipe"],
                "right_visible_affix": card["visible_right_extension"],
                "right_channel_class": right["visible_channel_class"] if right else NONE,
                "right_channel_observation_count": right["visible_channel_observation_count"] if right else 0,
                "right_channel_recipe_variants": right["visible_channel_recipe_variants"] if right else NONE,
                "right_interface_pair": right["interface_pair"] if right else NONE,
                "right_interface_old_event_count": right["old_interface_event_count"] if right else 0,
                "primary_old_supported_interfaces": card["old_supported_interface_count"],
                "primary_interface_count": card["interface_count"],
                "primary_full_arm_joint_count": card["full_arm_joint_count"],
                "primary_repeated_invariant_channel_count": card["repeated_invariant_visible_channel_count"],
                "primary_anchor_context_modes": card["anchor_context_modes"],
                "primary_anchor_context_relation": card["anchor_context_relation"],
                "primary_context_compatible": "YES" if context_compatible(card["anchor_context_relation"]) else "NO",
                "old_supercard_recipe_count": card["old_supercard_recipe_count"],
                "old_supercard_recipes": card["old_supercard_recipes"],
                "old_supercard_context_relation": card["old_supercard_context_relation"],
                "primary_structural_support_class": card["structural_support_class"],
                "recurrent_primary_anchor_family_target_count": family["target_count"] if family else 1,
                "initial_flag_reasons": flag["flag_reasons"] if flag else NONE,
                "secondary_bridge_present": "YES" if bridge else "NO",
                "secondary_structural_formula": formula(secondary_left, secondary_anchor, secondary_right) if bridge else NONE,
                "secondary_anchor_recipe": secondary_anchor,
                "secondary_visible_stem_status": secondary_visible_status,
                "secondary_visible_stem_surface": secondary_visible,
                "secondary_context_relation": bridge["secondary_context_relation"] if bridge else NONE,
                "secondary_supported_interfaces": bridge["secondary_supported_interfaces"] if bridge else 0,
                "secondary_interface_count": bridge["secondary_interface_count"] if bridge else 0,
                "secondary_repaired_dimension": bridge["repaired_dimension"] if bridge else NONE,
                "flag_resolution": resolution,
                "current_caution": current_caution,
                "working_default": card["working_default"],
                "reading_scope": "GERMAN_WORKING_READING__NOT_PLAINTEXT",
                "guard": "EXACT_SURFACE_KEY_ONLY__NO_FUZZY_EXTENSION_OR_NEW_MEANING",
            }
        )

    surface_counts = Counter(row["surface"] for row in output_rows)
    if len(output_rows) != 81 or any(count != 1 for count in surface_counts.values()):
        raise RuntimeError("Output surface inventory drift")

    result = {
        "status": STATUS,
        "reader_card_count": len(output_rows),
        "exact_surface_key_count": len(surface_counts),
        "directional_arm_count": len(arms),
        "aligned_primary_visible_stem_count": sum(
            row["primary_visible_stem_status"] == "ALIGNED_EXACT_OLD_SURFACE_STEM"
            for row in output_rows
        ),
        "direction_mismatch_primary_visible_stem_count": sum(
            row["primary_visible_stem_status"]
            == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM"
            for row in output_rows
        ),
        "no_exact_primary_visible_stem_count": sum(
            row["primary_visible_stem_status"] == "NO_EXACT_OLD_SURFACE_STEM"
            for row in output_rows
        ),
        "primary_context_compatible_count": sum(
            row["primary_context_compatible"] == "YES" for row in output_rows
        ),
        "primary_context_default_count": sum(
            row["primary_context_compatible"] == "NO" for row in output_rows
        ),
        "primary_old_supported_interface_count": sum(
            int(row["primary_old_supported_interfaces"]) for row in output_rows
        ),
        "primary_interface_count": sum(int(row["primary_interface_count"]) for row in output_rows),
        "targets_with_recurrent_invariant_channel_count": sum(
            int(row["primary_repeated_invariant_channel_count"]) > 0 for row in output_rows
        ),
        "targets_in_recurrent_primary_anchor_family_count": sum(
            int(row["recurrent_primary_anchor_family_target_count"]) > 1 for row in output_rows
        ),
        "old_supercard_target_count": sum(
            int(row["old_supercard_recipe_count"]) > 0 for row in output_rows
        ),
        "initial_flagged_card_count": len(flag_by_surface),
        "secondary_bridge_card_count": len(bridge_by_surface),
        "unresolved_explicit_default_count": len(unrepaired_by_surface),
        "known_surface_read_count": len(output_rows),
        "unknown_surface_policy": "STOP_UNKNOWN_FRAGMENT_SURFACE",
        "primary_anchor_changes": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "new_pages": 0,
    }
    expected = {
        "reader_card_count": 81,
        "exact_surface_key_count": 81,
        "directional_arm_count": 93,
        "aligned_primary_visible_stem_count": 72,
        "direction_mismatch_primary_visible_stem_count": 1,
        "no_exact_primary_visible_stem_count": 8,
        "primary_context_compatible_count": 69,
        "primary_context_default_count": 12,
        "primary_old_supported_interface_count": 87,
        "primary_interface_count": 93,
        "targets_with_recurrent_invariant_channel_count": 34,
        "targets_in_recurrent_primary_anchor_family_count": 34,
        "old_supercard_target_count": 8,
        "initial_flagged_card_count": 16,
        "secondary_bridge_card_count": 4,
        "unresolved_explicit_default_count": 12,
        "known_surface_read_count": 81,
    }
    drift = {key: (result[key], value) for key, value in expected.items() if result[key] != value}
    if drift:
        raise RuntimeError(f"Consolidated reader inventory drift: {drift}")

    write_tsv(READER_OUT, output_rows)
    write_tsv(
        SUMMARY_OUT,
        [{"metric": key, "value": value} for key, value in result.items() if key != "status"],
    )

    bridge_rows = [row for row in output_rows if row["secondary_bridge_present"] == "YES"]
    default_rows = [
        row
        for row in output_rows
        if row["flag_resolution"] == "EXPLICIT_WORKING_DEFAULT__NO_QUALIFIED_SECONDARY"
    ]
    bridge_lines = [
        f"| `{row['surface']}` | `{row['primary_structural_formula']}` | "
        f"`{row['secondary_structural_formula']}` | {row['secondary_repaired_dimension']} | "
        f"{row['neutral_component_reading_de']} |"
        for row in bridge_rows
    ]
    default_names = ", ".join(f"`{row['surface']}`" for row in default_rows)
    BOOK_OUT.write_text(
        f"""# GDT546 — ausführbarer Reader für 81 Fragmentkarten

Status: `{STATUS}`

Der Reader zieht die bisher verstreuten Angaben pro Oberfläche in genau eine
Karte zusammen: vollständiges Rezept, deutsche Komponentenlesung,
Hauptstamm, sichtbare Stammform, gerichtete linke/rechte Erweiterungen,
Kürzelkanäle, alte Andockkanten, Satzkontext und gegebenenfalls eine zweite
Herleitung. Alle 81 bekannten Oberflächen liefern eine Karte; unbekannte
Oberflächen stoppen, statt durch Ähnlichkeit stillschweigend zu erben.

## Die vier Karten mit zwei Herleitungen

| Oberfläche | Hauptzerlegung | zusätzliche Zerlegung | repariert | Arbeitslesung |
| --- | --- | --- | --- | --- |
{chr(10).join(bridge_lines)}

Die zweite Herleitung ändert weder Hauptstamm noch Rezept noch Bedeutung.
Bei `chckhedy` bleibt ihre sichtbare Richtung ausdrücklich abweichend.

## Die zwölf expliziten Defaults

{default_names}

Diese Karten werden weiterhin vollständig gelesen. Ihr Kontext oder eine
Andockkante ist aber nicht durch eine qualifizierte zweite Stammbrücke
abgesichert. Das ist eine benannte Arbeitslücke und kein leeres Wort.

## Bedienung

```bash
python3 experiments/yolo/gdt546_consolidated_fragment_reader/src/read_fragment.py \\
  --surface chepakeo
```

Die Ausgabe bleibt zweikanalig: Komponentenfolge und strukturelle Herleitung
sind beobachtbare Arbeitskarten; der deutsche Satz ist die heutige
Arbeitslesung und kein behaupteter Klartext.
""",
        encoding="utf-8",
    )
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
