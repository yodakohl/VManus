#!/usr/bin/env python3
"""Locate every unused equal-length anchor relative to GDT543's flagged cards."""

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
BASE = ROOT / "experiments/yolo/gdt544_flagged_equal_length_anchor_availability"
OUT = BASE / "artifacts"
G543 = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames/artifacts"
CARD_IN = G543 / "gdt543_81_fragment_extension_cards.tsv"
CANDIDATE_IN = G543 / "gdt543_104_longest_anchor_candidates.tsv"
ARM_IN = G543 / "gdt543_93_directional_extension_arms.tsv"
FLAGGED_OUT = OUT / "gdt544_16_flagged_target_anchor_availability.tsv"
UNUSED_OUT = OUT / "gdt544_23_unused_candidate_owners.tsv"
SUMMARY_OUT = OUT / "gdt544_anchor_availability_summary.tsv"
BOOK_OUT = OUT / "GDT544_EQUAL_LENGTH_ANCHOR_AVAILABILITY.md"
RESULT_OUT = OUT / "gdt544_result.json"
STATUS = "ZERO_FLAGGED_TARGETS_HAVE_ALTERNATIVE_LONGEST_ANCHOR__23_UNUSED_BELONG_TO_20_CLEAN_TARGETS"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def join(values) -> str:
    material = sorted({str(value) for value in values if str(value)})
    return "|".join(material) if material else "NONE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARD_IN)
    candidates = read_tsv(CANDIDATE_IN)
    arms = read_tsv(ARM_IN)
    if (len(cards), len(candidates), len(arms)) != (81, 104, 93):
        raise RuntimeError("GDT543 input inventory drift")

    cards_by_surface = {row["surface"]: row for row in cards}
    candidates_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        candidates_by_surface[row["surface"]].append(row)
    context_flags = {
        row["surface"]
        for row in cards
        if row["anchor_context_relation"] == "TARGET_MODE_SET_DISJOINT"
    }
    interface_flags = {
        row["target_surface"]
        for row in arms
        if int(row["old_interface_event_count"]) == 0
    }
    flagged = context_flags | interface_flags

    flagged_rows = []
    for surface in sorted(flagged, key=lambda value: int(cards_by_surface[value]["target_ordinal"])):
        card = cards_by_surface[surface]
        options = candidates_by_surface[surface]
        selected = [row for row in options if row["selected"] == "YES"]
        unused = [row for row in options if row["selected"] == "NO"]
        reasons = []
        if surface in context_flags:
            reasons.append("ANCHOR_CONTEXT_MODE_DIFFERENCE")
        if surface in interface_flags:
            reasons.append("NEW_ATOM_INTERFACE")
        flagged_rows.append(
            {
                "target_ordinal": card["target_ordinal"],
                "surface": surface,
                "final_recipe": card["final_recipe"],
                "flag_reasons": "|".join(reasons),
                "selected_anchor_recipe": card["anchor_recipe"],
                "selected_visible_stem_status": card["visible_stem_status"],
                "selected_context_relation": card["anchor_context_relation"],
                "selected_supported_interfaces": card["old_supported_interface_count"],
                "selected_interface_count": card["interface_count"],
                "equal_length_candidate_count": len(options),
                "selected_candidate_count": len(selected),
                "unused_equal_length_candidate_count": len(unused),
                "unused_equal_length_anchor_recipes": join(row["anchor_recipe"] for row in unused),
                "decision": "NO_EQUAL_LENGTH_REANCHOR_AVAILABLE" if not unused else "ALTERNATIVE_AVAILABLE",
                "next_route": "SEARCH_SHORTER_EXACT_OLD_RECIPE_STEMS_WITH_NONWORSE_VISIBLE_DIRECTION",
                "guard": "AVAILABILITY_AUDIT_ONLY__GDT543_CARD_UNCHANGED",
            }
        )

    unused_rows = []
    for row in candidates:
        if row["selected"] != "NO":
            continue
        card = cards_by_surface[row["surface"]]
        unused_rows.append(
            {
                "target_ordinal": row["target_ordinal"],
                "surface": row["surface"],
                "final_recipe": row["final_recipe"],
                "unused_anchor_recipe": row["anchor_recipe"],
                "anchor_start_atom": row["anchor_start_atom"],
                "extension_direction": row["extension_direction"],
                "aligned_visible_match_count": row["aligned_visible_match_count"],
                "all_interfaces_old": row["all_interfaces_old"],
                "old_anchor_event_count": row["old_anchor_event_count"],
                "target_has_context_flag": "YES" if row["surface"] in context_flags else "NO",
                "target_has_interface_flag": "YES" if row["surface"] in interface_flags else "NO",
                "target_is_flagged": "YES" if row["surface"] in flagged else "NO",
                "selected_anchor_recipe": card["anchor_recipe"],
                "ownership_class": "CLEAN_TARGET_UNUSED_OPTION" if row["surface"] not in flagged else "FLAGGED_TARGET_UNUSED_OPTION",
                "guard": "UNSELECTED_GDT543_EQUAL_LENGTH_CANDIDATE__NO_REANCHOR",
            }
        )
    unused_rows.sort(key=lambda row: (int(row["target_ordinal"]), int(row["anchor_start_atom"]), row["unused_anchor_recipe"]))

    result = {
        "status": STATUS,
        "context_flag_target_count": len(context_flags),
        "new_interface_target_count": len(interface_flags),
        "overlap_target_count": len(context_flags & interface_flags),
        "union_flagged_target_count": len(flagged),
        "flagged_target_with_unused_equal_length_anchor_count": sum(int(row["unused_equal_length_candidate_count"]) > 0 for row in flagged_rows),
        "flagged_unused_equal_length_candidate_count": sum(int(row["unused_equal_length_candidate_count"]) for row in flagged_rows),
        "total_unused_equal_length_candidate_count": len(unused_rows),
        "unused_candidate_owner_target_count": len({row["surface"] for row in unused_rows}),
        "unused_candidate_clean_owner_count": len({row["surface"] for row in unused_rows if row["target_is_flagged"] == "NO"}),
        "unused_candidate_flagged_owner_count": len({row["surface"] for row in unused_rows if row["target_is_flagged"] == "YES"}),
        "all_flagged_candidate_multiplicity": dict(sorted(Counter(int(row["equal_length_candidate_count"]) for row in flagged_rows).items())),
        "clean_multioption_target_multiplicity": dict(sorted(Counter(len(candidates_by_surface[surface]) for surface in {row["surface"] for row in unused_rows}).items())),
        "new_pages": 0,
        "card_changes": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    expected = {
        "context_flag_target_count": 12,
        "new_interface_target_count": 6,
        "overlap_target_count": 2,
        "union_flagged_target_count": 16,
        "flagged_target_with_unused_equal_length_anchor_count": 0,
        "flagged_unused_equal_length_candidate_count": 0,
        "total_unused_equal_length_candidate_count": 23,
        "unused_candidate_owner_target_count": 20,
        "unused_candidate_clean_owner_count": 20,
        "unused_candidate_flagged_owner_count": 0,
    }
    drift = {key: (result[key], value) for key, value in expected.items() if result[key] != value}
    if drift:
        raise RuntimeError(f"Availability inventory drift: {drift}")

    write_tsv(FLAGGED_OUT, flagged_rows)
    write_tsv(UNUSED_OUT, unused_rows)
    write_tsv(SUMMARY_OUT, [
        {"metric": key, "value": json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, dict) else value}
        for key, value in result.items() if key != "status"
    ])
    flagged_names = ", ".join(f"`{row['surface']}`" for row in flagged_rows)
    owner_lines = []
    for surface in sorted({row["surface"] for row in unused_rows}, key=lambda value: int(cards_by_surface[value]["target_ordinal"])):
        options = [row["unused_anchor_recipe"] for row in unused_rows if row["surface"] == surface]
        owner_lines.append(f"- `{surface}`: {', '.join(f'`{value}`' for value in options)}")
    BOOK_OUT.write_text(f"""# GDT544 — die markierten Karten haben keinen zweiten längsten Stamm

Status: `{STATUS}`

GDT543 markiert zwölf Kontextunterschiede und sechs neue Atomgrenzen. Weil
`chady` und `chap` in beiden Mengen liegen, sind das sechzehn verschiedene
Ziele: {flagged_names}.

Alle sechzehn besitzen genau **einen** längsten alten Ganzrezeptstamm. Damit
gibt es unter den23 unbenutzten gleich langen Kandidaten keinen einzigen
Reparaturkandidaten für diese Gruppe. Ein Umranken wäre keine Auswahl, sondern
müsste Evidenz erfinden.

## Wo die23 Alternativen tatsächlich liegen

Sie gehören vollständig zu20 bereits unmarkierten Zielen:

{chr(10).join(owner_lines)}

Die GDT543-Auswahl bleibt daher unverändert. Der nächste sinnvolle Griff geht
nicht seitwärts zu gleich langen Stämmen, sondern eine Stufe kürzer: nur echte
alte Ganzrezepte, weiterhin exakte sichtbare Richtung, und nur ein konkreter
Kontext- oder Grenzgewinn zählt.
""", encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
