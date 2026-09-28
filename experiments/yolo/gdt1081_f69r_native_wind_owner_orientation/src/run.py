#!/usr/bin/env python3
"""Package a registered human visual observation; no transcription or decoder."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    obs = json.loads((BASE / "src/OBSERVATIONS.json").read_text())
    source = json.loads((BASE / "src/SOURCE.json").read_text())
    outer = obs["outer_text_sectors_clockwise_from_top"]
    spokes = obs["colored_spokes"]
    orientation = obs["orientation_candidates"]
    has_bearing = any(orientation[k] for k in (
        "independently_readable_cardinal_letter_or_word",
        "identified_sunrise_or_sunset_icon", "unique_pointer_or_start_mark"
    )) and spokes["independently_named_bearings_visible"]
    has_owner = any(row["unique_ink_leader_to_wind"] for row in outer) or obs["radial_text_loci_from_prior_GDT1068"]["singleton_label_to_one_colored_spoke"]
    result = {
        "decision": "BOTH_GATES_VISIBLE" if has_bearing and has_owner else "NO_LEXICAL_REOPENING",
        "orientation_gate": has_bearing,
        "singular_owner_gate": has_owner,
        "outer_sectors_inspected": len(outer),
        "outer_direct_leaders": sum(row["unique_ink_leader_to_wind"] for row in outer),
        "radial_loci_accounted_for": len(obs["radial_text_loci_from_prior_GDT1068"]["locus_numbers"]),
        "painted_spokes": spokes["count"],
        "source": source["canvas_id"],
        "claim_ceiling": "Native postexposure visual capacity only; no directional word, p-value or confirmed translation"
    }
    (BASE / "artifacts/RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(result["decision"])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
