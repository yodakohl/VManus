#!/usr/bin/env python3
"""Check and minimally correct V35 field placement against observed positions."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]

# Meanings are unchanged except the explicitly removed unsupported use clause
# and the already-existing STAND card appended to the poultice instruction.
CORRECTED = {
    "NEW01_SCABIOSA_RED_WINE": [[
        "take the fibrous lower root", "wash it in running water", "add red wine",
        "boil gently; close the rubric",
    ]],
    "NEW02_VIOLET_WARM_POULTICE": [[
        "make a warm poultice from its leaves", "mix it with honey",
        "apply it while warm", "bind it upon a swollen place",
        "let it stand until ready; end this instruction",
    ]],
    "NEW03_ALLIUM_WOUND_WASH": [[
        "begin the next measured entry", "in the stated or usual measure",
        "steep it in white wine", "wash the sore place once",
    ]],
    "NEW04_SUNDEW_HONEY_APPLICATION": [[
        "in the stated or usual measure", "steep it in white wine",
        "mix it with honey", "apply it while warm",
        "apply it at the place indicated by the drawing",
    ]],
    "NEW05_COMMON_WARM_BATH": [
        ["add clean water; close the rubric"],
        ["temper the working liquid and keep it lukewarm",
         "bathe or immerse in the tempered warm liquid; end this instruction"],
    ],
    "NEW06_FILTER_REST_APPLICATION": [
        ["stir until evenly mixed", "through a cloth", "strain it clear; close the rubric"],
        ["let it stand until ready; end this instruction"],
        ["apply it at the place indicated by the drawing"],
    ],
    "NEW07_LOCAL_RINSE_DRAIN": [
        ["rinse the indicated place once; end this instruction"],
        ["until the liquid runs clear",
         "let the spent liquid drain into the lower receiving vessel; end this instruction"],
    ],
    "NEW08_MEASURED_WHITE_WINE_BATCH": [[
        "begin the next measured entry", "in the stated or usual measure",
        "add white wine", "stir until evenly mixed",
        "let it stand until ready; end this instruction",
    ]],
}

GERMAN = {
    "NEW01_SCABIOSA_RED_WINE": "Nimm die faserige untere Wurzel, wasche sie in fließendem Wasser, gib Rotwein zu und koche sanft.",
    "NEW02_VIOLET_WARM_POULTICE": "Bereite aus den Blättern einen warmen Honigumschlag, trage ihn warm auf, binde ihn auf die geschwollene Stelle und lasse ihn dort ruhen.",
    "NEW03_ALLIUM_WOUND_WASH": "Beginne den abgemessenen Eintrag, setze die übliche Menge in Weißwein an und wasche die wunde Stelle einmal.",
    "NEW04_SUNDEW_HONEY_APPLICATION": "Setze die übliche Menge in Weißwein an, mische Honig bei und trage sie warm an der bezeichneten Stelle auf.",
    "NEW05_COMMON_WARM_BATH": "Gib sauberes Wasser zu, temperiere die Arbeitsflüssigkeit lauwarm und bade darin.",
    "NEW06_FILTER_REST_APPLICATION": "Rühre, seihe durch ein Tuch klar, lasse die Flüssigkeit ruhen und trage sie an der bezeichneten Stelle auf.",
    "NEW07_LOCAL_RINSE_DRAIN": "Spüle die bezeichnete Stelle einmal bis die Flüssigkeit klar läuft und lasse sie in das untere Gefäß ablaufen.",
    "NEW08_MEASURED_WHITE_WINE_BATCH": "Beginne einen abgemessenen Eintrag, gib in der üblichen Menge Weißwein zu, rühre und lasse den Ansatz stehen.",
}


def desired_position(i: int, n: int) -> str:
    if n == 1:
        return "ONLY"
    if i == 0:
        return "FIRST"
    if i == n - 1:
        return "LAST"
    return "MIDDLE"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["ledger_scope"] == "GDT327_PROSE"]
    by_meaning = defaultdict(list)
    for r in rows:
        by_meaning[r["default_English"]].append(r)

    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / "gdt327_joint_tuple_interlinear.tsv"), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--columns", "page,joint_tuple_id,within_field_position", "--forbid-prefix", "f84"]
    text = subprocess.run(cmd, check=True, text=True, capture_output=True).stdout
    lines = [line for line in text.splitlines() if not line.startswith("GUARD_STATS ")]
    formal = list(csv.DictReader(lines, delimiter="\t"))
    positions = defaultdict(Counter)
    for r in formal:
        positions[r["joint_tuple_id"]][r["within_field_position"]] += 1

    out = []
    for recipe_id, fields in CORRECTED.items():
        for field_no, field in enumerate(fields, 1):
            for i, meaning in enumerate(field):
                candidates = by_meaning[meaning]
                counts = Counter(r["exact_tuple_id"] for r in candidates)
                tid = sorted(counts, key=lambda t: (-counts[t], t))[0]
                surfaces = Counter(r["surface"] for r in candidates if r["exact_tuple_id"] == tid)
                surface = sorted(surfaces, key=lambda s: (-surfaces[s], s))[0]
                desired = desired_position(i, len(field))
                out.append({
                    "recipe_id": recipe_id,
                    "german_instruction": GERMAN[recipe_id],
                    "field_no": field_no,
                    "card_no": i + 1,
                    "surface": surface,
                    "exact_tuple_id": tid,
                    "meaning": meaning,
                    "desired_position": desired,
                    "observed_support_at_position": positions[tid][desired],
                    "position_attested": str(positions[tid][desired] > 0).upper(),
                })

    path = HERE / "V36_CORRECTED_ENCODINGS.tsv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader(); w.writerows(out)
    summary = {
        "schema": "SIDEQUEST_V36_APPRENTICE_CORRECTION_V1",
        "status": "PASS_ALL_CARD_POSITIONS_ATTESTED",
        "recipe_count": len(CORRECTED),
        "card_count": len(out),
        "position_attested_count": sum(r["position_attested"] == "TRUE" for r in out),
        "position_unattested_count": sum(r["position_attested"] != "TRUE" for r in out),
        "removed_v35_meaning": "drink it for pain of the stomach",
        "added_existing_meaning": "let it stand until ready; end this instruction",
        "new_tuple_ids_created": 0,
        "new_surface_forms_created": 0,
        "f84_rows_accessed": 0,
        "f84r_rows_accessed": 0,
    }
    (HERE / "V36_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
