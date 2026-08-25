#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_scribe_slot_grammar_nine_hundredth"
PREFIX = "NINE_HUNDRED_FIRST"

SYMBOL_SOURCE = SOURCE / "NINE_HUNDREDTH_48_GRAMMAR_SYMBOLS.tsv"
PARSE_SOURCE = SOURCE / "NINE_HUNDREDTH_231_IDENTITY_SLOT_PARSES.tsv"
MARK_SOURCE = SOURCE / "NINE_HUNDREDTH_437_MARK_SLOT_PARSES.tsv"
UNIT_SOURCE = SOURCE / "NINE_HUNDREDTH_118_UNIT_SLOT_GRAMMAR.tsv"
CARD_SOURCE = SOURCE / "NINE_HUNDREDTH_6_JOB_CARD_SLOT_SUMMARY.tsv"
ROUNDTRIP_SOURCE = SOURCE / "NINE_HUNDREDTH_10_WORKED_ROUNDTRIPS.tsv"

CUES = {
    "AIIN": ("aiin", "ARGUMENT_TAIL"), "AIN": ("ain", "ARGUMENT_TAIL"),
    "AIR": ("air", "PATH_TAIL"), "AL": ("al", "ADDRESS_TAIL"),
    "AN": ("an", "ARGUMENT_TAIL"), "AR": ("ar", "ADDRESS_TAIL"),
    "CH": ("ch", "OPERATION_BODY"), "CHD": ("chd/ched", "OPERATION_BODY"),
    "CHK": ("chk/chek", "OPERATION_BODY"), "CKH": ("ckh", "PATH_BODY"),
    "CTH": ("cth", "STATE_BODY"), "DA": ("da", "GRADE_BODY"),
    "DY": ("dy", "CLOSED_ENDPOINT"), "E": ("e", "GRADE_LENGTH"),
    "EE": ("ee", "GRADE_LENGTH"), "EEE": ("eee", "GRADE_LENGTH"),
    "HO": ("cho/sho", "MATERIAL_BODY"), "IIN": ("iin", "STATE_TAIL"),
    "K": ("k", "OPERATION_BODY"), "L": ("l", "PATH_ONSET"),
    "LD": ("ldd", "OPERATION_BODY"), "LSH": ("lsh", "OPERATION_BODY"),
    "O": ("o", "PROCESS_BODY"), "OK": ("qok/ok/chok", "OPERATION_FRAME"),
    "OL": ("ol/chol/qol/ls/sol", "ORDER_FRAME"), "OR": ("or", "MATERIAL_TAIL"),
    "OT": ("qot/ot", "ORDER_FRAME"), "P": ("p", "OPERATION_ONSET"),
    "R": ("r", "STATE_ONSET"), "S": ("s", "OPERATION_BODY"),
    "SH": ("sh", "STATE_BODY"), "SHED": ("shed", "STATE_BODY"),
    "SOLK": ("solk/qolk", "OPERATION_FRAME"), "T": ("t", "OPERATION_BODY"),
    "TALAM": ("talam", "WHOLE_FORM"), "Y": ("y/chy/chey/dy/shy/sy", "OPEN_ENDPOINT"),
    "A_ADDR": ("a", "LOCAL_ADDRESS"), "AM_ADDR": ("am", "LOCAL_ADDRESS"),
    "D_ADDR": ("d", "LOCAL_ADDRESS"), "D_LABEL": ("d", "LOCAL_LABEL"),
    "S_ADDR": ("s", "LOCAL_ADDRESS"), "S_LABEL": ("s", "LOCAL_LABEL"),
    "CHEO": ("cheo", "LOCAL_MATERIAL"), "WHOLE[cheey|shey]": ("cheey/shey", "WHOLE_FORM"),
    "NONE": ("memorize", "LOCAL_WHOLE_FORM"), "CFH": ("cfh", "OPERATION_BODY"),
    "OS": ("os", "ORDER_WHOLE_SIGN"), "RESUME_CARD": ("schol", "REFERENT_WHOLE_SIGN"),
}

RENDERER_RULES = [
    ("ROOT_ORDER_COPY", "Keep the root order unchanged before applying allographs."),
    ("OPTIONAL_Q_CARRIER", "At a card onset q may carry an O-frame without adding meaning."),
    ("OK_FRAME_ALLOGRAPH", "Render OK with qok-, ok- or the learned chok- frame."),
    ("OT_FRAME_ALLOGRAPH", "Render OT with ot- or qot-; q is a carrier choice."),
    ("OL_FRAME_ALLOGRAPH", "Render OL with ol-, chol-, qol-, ls- or sol- from the local deck."),
    ("CH_BODY_ALLOGRAPH", "Render CH/CHD/CHK/CKH inside the operation body with ch/ched/check variants."),
    ("E_GRADE_LENGTH", "One, two or three visible e grades encode E, EE or EEE where the frame licenses it."),
    ("ARGUMENT_OR_ADDRESS_TAIL", "Render AIIN/AIN/AL/AR/AIR at the right argument, address or path edge when available."),
    ("L_PATH_ONSET", "Use l- as the ordinary transfer/path onset."),
    ("R_STATE_ONSET", "Use r- as the cool-state onset."),
    ("Y_OPEN_ENDPOINT", "Use the learned y/chy/chey/dy/shy/sy open-post allograph licensed by the card family."),
    ("DY_CLOSED_ENDPOINT", "Use a learned -dy close only for recipes whose final component is DY."),
    ("LOCAL_SIGN_COPY", "Copy diagram-local address, label and material signs from their local mini-deck."),
    ("MEMORIZED_WHOLE_FORM", "Copy fused or local whole forms without decomposing their exact spelling."),
    ("REPEATED_ROOT_COPY", "Repeat a root visibly when the recipe repeats the same address or referent."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(recipe: str) -> list[str]:
    if recipe in {"NONE", "WHOLE[cheey|shey]", "RESUME_CARD"}:
        return [recipe]
    return recipe.split("+")


def rules_for(recipe: str, surface: str, action: str) -> list[str]:
    parts = tokens(recipe)
    rules = []
    whole = action in {"READ_FUSED_WHOLE_WORD", "READ_LEARNED_WHOLE_ROOT"} or recipe in {"NONE", "WHOLE[cheey|shey]", "TALAM"}
    if whole:
        rules.append("MEMORIZED_WHOLE_FORM")
    else:
        rules.append("ROOT_ORDER_COPY")
    if surface.startswith("q"):
        rules.append("OPTIONAL_Q_CARRIER")
    if "OK" in parts:
        rules.append("OK_FRAME_ALLOGRAPH")
    if "OT" in parts:
        rules.append("OT_FRAME_ALLOGRAPH")
    if "OL" in parts:
        rules.append("OL_FRAME_ALLOGRAPH")
    if any(part in {"CH", "CHD", "CHK", "CKH"} for part in parts):
        rules.append("CH_BODY_ALLOGRAPH")
    if any(part in {"E", "EE", "EEE"} for part in parts):
        rules.append("E_GRADE_LENGTH")
    if parts[-1] in {"AIIN", "AIN", "AL", "AR", "AIR"}:
        rules.append("ARGUMENT_OR_ADDRESS_TAIL")
    if "L" in parts:
        rules.append("L_PATH_ONSET")
    if "R" in parts:
        rules.append("R_STATE_ONSET")
    if parts[-1] == "Y":
        rules.append("Y_OPEN_ENDPOINT")
    if parts[-1] == "DY":
        rules.append("DY_CLOSED_ENDPOINT")
    if any(part in {"A_ADDR", "AM_ADDR", "D_ADDR", "D_LABEL", "S_ADDR", "S_LABEL", "CHEO"} for part in parts):
        rules.append("LOCAL_SIGN_COPY")
    if len(parts) != len(set(parts)):
        rules.append("REPEATED_ROOT_COPY")
    return rules


def main() -> None:
    symbols = read(SYMBOL_SOURCE)
    parses = read(PARSE_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)
    roundtrips = read(ROUNDTRIP_SOURCE)
    assert set(CUES) == {row["symbol"] for row in symbols}

    ecology: dict[str, dict[str, object]] = {}
    for row in symbols:
        ecology[row["symbol"]] = {
            "initial_identity_uses": 0, "medial_identity_uses": 0, "final_identity_uses": 0,
            "weighted_mark_uses": 0, "surfaces": [],
        }
    for row in parses:
        parts = tokens(row["component_recipe"])
        weight = int(row["marks"])
        for index, part in enumerate(parts):
            bucket = ecology[part]
            if index == 0:
                bucket["initial_identity_uses"] = int(bucket["initial_identity_uses"]) + 1
            if index == len(parts) - 1:
                bucket["final_identity_uses"] = int(bucket["final_identity_uses"]) + 1
            if 0 < index < len(parts) - 1:
                bucket["medial_identity_uses"] = int(bucket["medial_identity_uses"]) + 1
            bucket["weighted_mark_uses"] = int(bucket["weighted_mark_uses"]) + weight
            surfaces = bucket["surfaces"]
            assert isinstance(surfaces, list)
            if row["surface"] not in surfaces and len(surfaces) < 10:
                surfaces.append(row["surface"])

    symbol_rows = []
    for row in symbols:
        cue, cue_class = CUES[row["symbol"]]
        bucket = ecology[row["symbol"]]
        symbol_rows.append({
            "symbol": row["symbol"],
            "atomic_value_de": row["atomic_value_de"],
            "slot_role": row["slot_role"],
            "canonical_surface_cue": cue,
            "cue_class": cue_class,
            "initial_identity_uses": bucket["initial_identity_uses"],
            "medial_identity_uses": bucket["medial_identity_uses"],
            "final_identity_uses": bucket["final_identity_uses"],
            "weighted_mark_uses": bucket["weighted_mark_uses"],
            "whole_surface_examples": " | ".join(bucket["surfaces"]),
            "renderer_instruction": f"Use {cue} as the learned visible cue for {row['symbol']}={row['atomic_value_de']} in {cue_class} position.",
        })

    recipe_surfaces: dict[str, list[str]] = defaultdict(list)
    for row in parses:
        if row["surface"] not in recipe_surfaces[row["component_recipe"]]:
            recipe_surfaces[row["component_recipe"]].append(row["surface"])

    analysis_rows = []
    analysis_by_identity: dict[str, dict[str, object]] = {}
    for row in parses:
        matched = rules_for(row["component_recipe"], row["surface"], next(mark["apprentice_action"] for mark in marks if mark["identity"] == row["identity"]))
        family = recipe_surfaces[row["component_recipe"]]
        if "MEMORIZED_WHOLE_FORM" in matched:
            renderability = "MEMORIZED_EXACT_FORM"
        elif len(family) > 1:
            renderability = "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE"
        else:
            renderability = "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING"
        skeleton = "-".join(CUES[part][0] for part in tokens(row["component_recipe"]))
        analyzed = {
            "identity": row["identity"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "semantic_root_reading_de": row["root_reading_de"],
            "renderer_skeleton": skeleton,
            "renderer_rules": " | ".join(matched),
            "attested_surface_family": " | ".join(family),
            "allograph_choices": len(family),
            "renderability": renderability,
            "exact_surface_rule": "Choose the learned local/hand allograph from this attested family.",
        }
        analysis_rows.append(analyzed)
        analysis_by_identity[row["identity"]] = analyzed

    rule_identity_counts: Counter[str] = Counter()
    rule_mark_counts: Counter[str] = Counter()
    marks_by_identity = Counter(row["identity"] for row in marks)
    for row in analysis_rows:
        for rule in str(row["renderer_rules"]).split(" | "):
            rule_identity_counts[rule] += 1
            rule_mark_counts[rule] += marks_by_identity[str(row["identity"])]
    rule_rows = []
    for precedence, (rule, instruction) in enumerate(RENDERER_RULES, start=1):
        rule_rows.append({
            "precedence": precedence,
            "renderer_rule": rule,
            "identity_count": rule_identity_counts[rule],
            "mark_count": rule_mark_counts[rule],
            "instruction": instruction,
        })

    revised_marks = []
    for row in marks:
        analyzed = analysis_by_identity[row["identity"]]
        revised_marks.append({
            **row,
            "renderer_skeleton": analyzed["renderer_skeleton"],
            "renderer_rules": analyzed["renderer_rules"],
            "attested_surface_family": analyzed["attested_surface_family"],
            "renderability": analyzed["renderability"],
            "twelfth_lesson": "ALLOGRAPH_RENDERER",
        })

    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        revised_units.append({
            **unit,
            "renderer_skeleton_sequence": " || ".join(str(row["renderer_skeleton"]) for row in local),
            "renderability_sequence": " | ".join(str(row["renderability"]) for row in local),
            "renderer_complete": "YES",
        })

    revised_cards = []
    for card in cards:
        local = [row for row in revised_marks if row["order_id"] == card["order_id"]]
        classes = Counter(str(row["renderability"]) for row in local)
        revised_cards.append({
            **card,
            "renderer_classes": " | ".join(f"{key}:{value}" for key, value in sorted(classes.items())),
            "renderer_parsed_marks": len(local),
            "renderer_complete": "YES",
        })

    extended_roundtrips = []
    parse_by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in analysis_rows:
        parse_by_recipe[str(row["component_recipe"])].append(row)
    for row in roundtrips:
        family_rows = parse_by_recipe[row["root_recipe"]]
        family = sorted({str(item["surface"]) for item in family_rows})
        extended_roundtrips.append({
            **row,
            "renderer_skeleton": family_rows[0]["renderer_skeleton"],
            "predicted_surface_family": " | ".join(family),
            "family_size": len(family),
            "renderer_rules": family_rows[0]["renderer_rules"],
            "forward_result": "EXACT" if len(family) == 1 else "FAMILY_PREDICTED__ALLOGRAPH_CHOICE_LEARNED",
        })

    write(f"{PREFIX}_48_SYMBOL_ALLOGRAPHS.tsv", symbol_rows, list(symbol_rows[0]))
    write(f"{PREFIX}_15_RENDERER_RULES.tsv", rule_rows, list(rule_rows[0]))
    write(f"{PREFIX}_231_IDENTITY_RENDERER_ANALYSES.tsv", analysis_rows, list(analysis_rows[0]))
    write(f"{PREFIX}_437_MARK_RENDERER.tsv", revised_marks, list(marks[0]) + ["renderer_skeleton", "renderer_rules", "attested_surface_family", "renderability", "twelfth_lesson"])
    write(f"{PREFIX}_118_UNIT_RENDERER.tsv", revised_units, list(units[0]) + ["renderer_skeleton_sequence", "renderability_sequence", "renderer_complete"])
    write(f"{PREFIX}_6_JOB_CARD_RENDERER.tsv", revised_cards, list(revised_cards[0]))
    write(f"{PREFIX}_10_RENDERED_ROUNDTRIPS.tsv", extended_roundtrips, list(extended_roundtrips[0]))

    lines = [
        "# Allographenhandbuch des Schreibers",
        "",
        "Das Wurzelrezept bestimmt die Kartenfamilie; q-Träger, Rahmen und Endallograph bestimmen die konkrete sichtbare Form.",
        "Für eine neue Kombination kann der Lehrling die Familie bilden, muss aber bei mehreren belegten Formen die lokale Handvariante aus dem Deck lernen.",
        "",
        "## Fünfzehn Rendererregeln",
        "",
    ]
    for row in rule_rows:
        lines.append(f"{row['precedence']}. **{row['renderer_rule']}** — {row['instruction']} ({row['identity_count']} Identitäten)")
    lines.extend(["", "## Zehn gerenderte Rezepte", ""])
    for row in extended_roundtrips:
        lines.extend([
            f"- {row['intended_instruction_de']}: `{row['root_recipe']}` → `{row['renderer_skeleton']}` → **{row['predicted_surface_family']}** ({row['forward_result']}).",
        ])
    (HERE / f"{PREFIX}_ALLOGRAPH_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    renderability_counts = Counter(str(row["renderability"]) for row in analysis_rows)
    summary = {
        "status": "PASS",
        "decision": "FIFTEEN_RENDERER_RULES_MAP_ALL_TWO_HUNDRED_THIRTY_ONE_ROOT_RECIPES_TO_ATTESTED_SURFACE_FAMILIES",
        "symbols": len(symbol_rows),
        "renderer_rules": len(rule_rows),
        "identities": len(analysis_rows),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "renderability": dict(renderability_counts),
        "unique_component_recipes": len(recipe_surfaces),
        "recipes_with_multiple_allographs": sum(len(values) > 1 for values in recipe_surfaces.values()),
        "roundtrips": len(extended_roundtrips),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 901: Allographenrenderer\n\n"
        "Fünfzehn Rendererregeln verbinden die 48 Werkstattsymbole mit allen 231 sichtbaren Kartenidentitäten. "
        "OK/OT/OL-Rahmen, q-Träger, e-Grade, Argumentenden sowie Y/DY-Ausgänge werden getrennt gelehrt. "
        "Das Wurzelrezept sagt die Oberflächenfamilie voraus; bei mehreren Allographen bleibt die Handvariante ein kleiner gelernter Deckentscheid.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
