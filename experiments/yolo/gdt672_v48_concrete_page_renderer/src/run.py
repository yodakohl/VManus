#!/usr/bin/env python3
"""Build GDT672: a concrete V48 transfer reader for the held-out f1r page."""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt672_v48_concrete_page_renderer")
BASE = ROOT / BASE_REL
SRC = BASE / "src"
ART = BASE / "artifacts"
V48_REL = Path("experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts")
V48 = ROOT / V48_REL
G589_REL = Path("experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts")
G589 = ROOT / G589_REL
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
STATUS = "PASS_F1R_214_POSITION_CONCRETE_TRANSFER__129_V48_EXACT__85_EXPLICIT_TRANSFER"

OUTPUT_NAMES = (
    "F1R_SOURCE_ALIGNMENT.tsv",
    "F1R_TOKEN_READINGS.tsv",
    "F1R_COMPONENT_TRACES.tsv",
    "F1R_COMPOSITION_RIVALS.tsv",
    "F1R_CLAUSE_FRAMES.tsv",
    "F1R_LINE_READER.tsv",
    "F1R_GDT589_COMPARISON.tsv",
    "F1R_TRANSFER_CARDS.tsv",
    "F1R_OCCURRENCE_AUDIT.tsv",
    "F1R_VALUE_ATTACHMENT_AUDIT.tsv",
    "RENDERER_RULE_CARDS.tsv",
    "REGISTER_DIVERSE_RENDER_AUDIT.tsv",
    "GDT672_F1R_CONCRETE_WORKING_READER.md",
    "RESULT.json",
)

GENERIC_FILLER = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|work item|working material|worksite|"
    r"work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)
ACTION_RE = re.compile(
    r"\b(?:abmessen|abteilen|abkühlen|abschließen|ansetzen|einweichen|erhitzen|"
    r"erwärmen|fertigstellen|filtrieren|hinzugeben|kühlen|mahlen|nehmen|reiben|"
    r"schließen|seihen|trocknen|waschen|zugeben|zerstoßen|kühle|trockne|erhitze|"
    r"weiche|nimm|gib|führe|seihe|schließe|miss)\b",
    re.IGNORECASE,
)
QUANTITY_RE = re.compile(
    r"\b(?:ein(?:e[mnrs]?)?|zwei|drei|vier|Teil(?:e)?|Maß(?:e)?|Dosis|Dosen|"
    r"Portion|Menge|Fraktion|Pfund|Handvoll|Gran)\b",
    re.IGNORECASE,
)
STAGE_RE = re.compile(r"\b(?:Grad\w*|Stufe\w*|Mittelstufe|Endstufe|Gradanfang|Gradmitte)\b", re.IGNORECASE)
FORM_RE = re.compile(r"\b(?:Form|Klasse)\b", re.IGNORECASE)
REFERENCE_RE = re.compile(r"\b(?:davon|daraus|darin|dazu|hierzu|hiervon)\b", re.IGNORECASE)
BROAD_CARRIER = re.compile(
    r"\b(?:\w*Ansatz\w*|\w*Kompositum\w*|Trockengut|Heißgut|Kaltgut|"
    r"Zubereitungsgut|Drogenstoffposten|\w*Species\w*)\b",
    re.IGNORECASE,
)

ROLE_SPELLING = {
    "AIIN_III": "aiin", "AIIR_FRACTION_III": "aiir", "AIN_II": "ain",
    "AIR_FRACTION_II": "air", "AL_RAW_I": "al", "AM_UNIT_I": "am",
    "AN_I": "an", "AR_FRACTION_I": "ar", "A_PART_OR_LINK": "a",
    "CH_DRY": "ch", "CKH_COMPOSITE": "ckh", "CPH_COMPOSITE": "cph",
    "CTH_HERB": "cth", "D_MEASURE": "d", "D_TERM_CLOSE": "d",
    "EE_END": "ee", "E_MIDDLE": "e", "IN_FORM_II": "in",
    "KNOWN_SHOR": "shor", "KNOWN_SOR": "sor", "K_HOT": "k",
    "L_WOOD": "l", "OL_MATERIAL": "ol", "OR_PORTION": "or",
    "OY_PREP_BASE": "oy", "O_PREP": "o", "P_POWDER": "p",
    "R_ROOT": "r", "SH_MOIST": "sh", "S_SEED": "s",
    "S_TERM_SPECIES": "s", "T_COLD": "t", "Y_REFERENCE": "y",
    "Y_START_OR_CLOSE": "y",
}
INHERITED_FAMILY_ROLES = {"KNOWN_SHOR", "KNOWN_SOR"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_text(rows: list[dict[str, Any]], fields: Iterable[str] | None = None) -> str:
    if not rows:
        raise RuntimeError("cannot serialize an empty TSV")
    names = list(fields or rows[0].keys())
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=names, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({name: row.get(name, "") for name in names})
    return out.getvalue()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def guarded_query(rel: Path, columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(rel), "--selector", "page",
        "--allow", "f1r", "--columns", columns, "--forbid-prefix", "f84",
    ]
    completed = subprocess.run(
        command, cwd=ROOT, check=True, text=True, capture_output=True,
    )
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("guarded query did not emit GUARD_STATS")
    stats = json.loads(match.group(1))
    return rows, {str(key): int(value) for key, value in stats.items()}


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def semantic_features(text: str) -> str:
    features: list[str] = []
    if ACTION_RE.search(text):
        features.append("ACTION")
    if QUANTITY_RE.search(text):
        features.append("QUANTITY")
    if STAGE_RE.search(text):
        features.append("STAGE")
    if FORM_RE.search(text):
        features.append("FORM")
    if REFERENCE_RE.search(text):
        features.append("REFERENCE")
    if re.search(r"Droge|Species|Ansatz|Kraut|Blatt|Wurzel|Samen|Pulver|Kompositum|Stoff|Gut", text, re.I):
        features.append("MATERIAL")
    if re.search(r"heiß|kalt|trocken|feucht|eingeweicht|abgeschlossen|fertig", text, re.I):
        features.append("STATE")
    return "+".join(features) or "DESCRIPTOR"


def parse_productive_components(surface: str, composition: str) -> list[tuple[int, int, str, str]]:
    components: list[tuple[int, int, str, str]] = []
    cursor = 0
    for role in composition.split("+"):
        literal = ROLE_SPELLING.get(role)
        if literal is None:
            raise RuntimeError(f"no literal spelling for productive role {role}")
        end = cursor + len(literal)
        if surface[cursor:end] != literal:
            raise RuntimeError(f"component trace does not cover {surface}: {role}@{cursor}")
        components.append((cursor, end, literal, role))
        cursor = end
    if cursor != len(surface):
        raise RuntimeError(f"component trace leaves residue in {surface}")
    return components


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    transfer_cards = read_tsv(SRC / "F1R_TRANSFER_CARDS.tsv")
    overrides = read_tsv(SRC / "F1R_OCCURRENCE_OVERRIDES.tsv")
    value_attachments = read_tsv(SRC / "F1R_VALUE_ATTACHMENTS.tsv")
    line_specs = read_tsv(SRC / "F1R_LINE_SPECS.tsv")
    control_specs = read_tsv(SRC / "CONTROL_PASSAGE_SPECS.tsv")
    rule_cards = read_tsv(SRC / "RENDERER_RULES.tsv")
    stem_model = read_tsv(V48 / "STEM_MODEL_V48.tsv")
    if len(transfer_cards) != 80 or len({row["surface"] for row in transfer_cards}) != 80:
        raise RuntimeError("f1r transfer deck must contain 80 unique surfaces")
    if sum(int(row["count"]) for row in transfer_cards) != 85:
        raise RuntimeError("f1r transfer deck must cover 85 positions")
    if len(line_specs) != 28 or [row["locus"] for row in line_specs] != [f"f1r.{i}" for i in range(1, 29)]:
        raise RuntimeError("f1r line specs must be the ordered 28-line page")
    if len(control_specs) != 6 or len(stem_model) != 56 or len(rule_cards) != 12 or len(value_attachments) != 17:
        raise RuntimeError("source deck dimensions drifted")

    token_rows, token_guard = guarded_query(
        TOKENS_REL, "page,locus,token_index,eva,kind,section,language,hand",
    )
    cross_rows, cross_guard = guarded_query(
        CROSS_REL,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    if len(token_rows) != 214 or len(cross_rows) != 28:
        raise RuntimeError("guarded f1r source census drift")
    if any(row["page"] != "f1r" or row["page"].startswith("f84") for row in token_rows + cross_rows):
        raise RuntimeError("guarded source materialized a forbidden or non-f1r row")
    expected_order = sorted(token_rows, key=lambda row: (locus_number(row["locus"]), int(row["token_index"])))
    if token_rows != expected_order:
        raise RuntimeError("guarded f1r token order is not physical line order")
    if len({(row["locus"], row["token_index"]) for row in token_rows}) != 214:
        raise RuntimeError("f1r source keys are not unique")

    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        by_line[row["locus"]].append(row)
    if list(by_line) != [f"f1r.{i}" for i in range(1, 29)]:
        raise RuntimeError("f1r physical line set drifted")
    for locus, rows in by_line.items():
        indices = [int(row["token_index"]) for row in rows]
        if indices != list(range(1, len(rows) + 1)):
            raise RuntimeError(f"nonconsecutive token indices at {locus}")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    if list(cross_by_locus) != [f"f1r.{i}" for i in range(1, 29)]:
        raise RuntimeError("f1r cross-reader line set drifted")
    for locus, rows in by_line.items():
        if " ".join(row["eva"] for row in rows) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"token/cross-reader mismatch at {locus}")
    if sum(int(row["all_three_present"]) for row in cross_rows) != 28:
        raise RuntimeError("not every f1r line has all three readers")
    if sum(int(row["all_present_exact"]) for row in cross_rows) != 5:
        raise RuntimeError("f1r exact three-reader line count drifted")

    glossary_rows = read_tsv(V48 / "V48_WORKING_TOKEN_GLOSSARY.tsv")
    glossary = {row["surface"]: row for row in glossary_rows}
    transfer = {row["surface"]: row for row in transfer_cards}
    source_surfaces = Counter(row["eva"] for row in token_rows)
    exact_surfaces = set(source_surfaces) & set(glossary)
    open_surfaces = set(source_surfaces) - set(glossary)
    if open_surfaces != set(transfer):
        missing = sorted(open_surfaces - set(transfer))
        extra = sorted(set(transfer) - open_surfaces)
        raise RuntimeError(f"transfer surface mismatch missing={missing} extra={extra}")
    if any(source_surfaces[surface] != int(transfer[surface]["count"]) for surface in transfer):
        raise RuntimeError("transfer card position count drift")
    exact_positions = sum(source_surfaces[surface] for surface in exact_surfaces)
    if (exact_positions, len(exact_surfaces), 214 - exact_positions, len(open_surfaces)) != (129, 84, 85, 80):
        raise RuntimeError("V48 f1r transfer dimensions drifted")
    exact_scope_counts = Counter(
        glossary[row["eva"]]["scope_state"] for row in token_rows if row["eva"] in glossary
    )
    if exact_scope_counts != {"KNOWN_EXACT_WHOLE": 89, "KNOWN_CONTEXT_LICENSED": 40}:
        raise RuntimeError(f"V48 exact-scope profile drifted: {exact_scope_counts}")
    if set(transfer) & set(glossary):
        raise RuntimeError("transfer deck overwrites a V48 surface")

    stem_roles = {row["structural_role"] for row in stem_model}
    for card in transfer_cards:
        if card["class"] == "P":
            roles = card["composition"].split("+")
            if any(role not in stem_roles | INHERITED_FAMILY_ROLES for role in roles):
                raise RuntimeError(f"unknown productive role in {card['surface']}")
            parse_productive_components(card["surface"], card["composition"])
        elif card["class"] not in {"W", "O"}:
            raise RuntimeError(f"unknown transfer class {card['class']}")

    override_by_key = {(row["locus"], row["token_index"]): row for row in overrides}
    if len(override_by_key) != len(overrides):
        raise RuntimeError("duplicate occurrence override")
    for key, row in override_by_key.items():
        source = next((item for item in token_rows if (item["locus"], item["token_index"]) == key), None)
        if source is None or source["eva"] != row["surface"] or row["surface"] not in transfer:
            raise RuntimeError(f"bad occurrence override {key}")
    attachment_by_key = {(row["locus"], row["token_index"]): row for row in value_attachments}
    if len(attachment_by_key) != len(value_attachments):
        raise RuntimeError("duplicate value attachment")
    for key, row in attachment_by_key.items():
        source = next((item for item in token_rows if (item["locus"], item["token_index"]) == key), None)
        if source is None or source["eva"] != row["surface"]:
            raise RuntimeError(f"bad value attachment {key}")

    statement_source = [
        row for row in read_tsv(G589 / "gdt589_793_count_overlay_statement_reader.tsv")
        if row["physical_page"] == "f1r"
    ]
    statement_source.sort(key=lambda row: int(row["reader_statement_ordinal"]))
    if len(statement_source) != 7:
        raise RuntimeError("GDT589 f1r statement count drifted")
    flattened_g589 = [
        surface for row in statement_source for surface in row["surface_sequence"].split()
    ]
    flattened_source = [row["eva"] for row in token_rows]
    if flattened_g589 != flattened_source:
        raise RuntimeError("GDT589 and guarded f1r source sequences differ")
    statement_for_ordinal: dict[int, dict[str, str]] = {}
    cursor = 0
    for statement in statement_source:
        for _surface in statement["surface_sequence"].split():
            cursor += 1
            statement_for_ordinal[cursor] = statement

    line_number_by_locus = {f"f1r.{i}": i for i in range(1, 29)}
    alignment_rows: list[dict[str, Any]] = []
    token_readings: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    token_by_line: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for global_ordinal, source in enumerate(token_rows, 1):
        surface = source["eva"]
        statement = statement_for_ordinal[global_ordinal]
        alignment = {
            "token_ordinal_global": global_ordinal,
            "line_ordinal": line_number_by_locus[source["locus"]],
            "page": source["page"],
            "locus": source["locus"],
            "token_index": source["token_index"],
            "eva": surface,
            "statement_ordinal": statement["reader_statement_ordinal"],
            "statement_id": statement["statement_id"],
            "gdt589_surface_match": 1,
        }
        alignment_rows.append(alignment)
        override = override_by_key.get((source["locus"], source["token_index"]))
        attachment = attachment_by_key.get((source["locus"], source["token_index"]))
        if surface in glossary:
            card = glossary[surface]
            route = "EXACT_V48"
            meaning = card["working_meaning_de"]
            composition = "EXACT_V48_CARD"
            confidence = card["strength"]
            transfer_class = "E"
            v48_source = card["source"]
            v48_scope = card["scope_state"]
            v48_priority = card["priority"]
        else:
            card = transfer[surface]
            transfer_class = card["class"]
            route = {
                "P": "ROLE_COMPOSED_TRANSFER",
                "W": "LOCAL_WHOLE_HYPOTHESIS",
                "O": "OCCURRENCE_SCOPED_TRANSFER",
            }[transfer_class]
            meaning = override["working_meaning_de"] if override else card["working_meaning_de"]
            composition = card["composition"]
            confidence = card["confidence"]
            v48_source = "NONE"
            v48_scope = "TRANSFER_NOT_PROMOTED_TO_V48"
            v48_priority = "NONE"
        reading = {
            **alignment,
            "route": route,
            "transfer_class": transfer_class,
            "working_meaning_de": meaning,
            "contextual_render_de": attachment["contextual_render_de"] if attachment else meaning,
            "composition": composition,
            "semantic_features": semantic_features(meaning),
            "contextual_semantic_features": semantic_features(attachment["contextual_render_de"] if attachment else meaning),
            "confidence": confidence,
            "v48_source": v48_source,
            "v48_scope_state": v48_scope,
            "v48_priority": v48_priority,
            "occurrence_override": 1 if override else 0,
            "join_direction": override["join_direction"] if override else "NONE",
            "join_surface": override["join_surface"] if override else "NONE",
            "value_attachment": 1 if attachment else 0,
        }
        token_readings.append(reading)
        token_by_line[source["locus"]].append(reading)
        if route == "ROLE_COMPOSED_TRANSFER":
            pieces = parse_productive_components(surface, composition)
            for component_ordinal, (start, end, literal, role) in enumerate(pieces, 1):
                component_rows.append({
                    "token_ordinal_global": global_ordinal,
                    "locus": source["locus"],
                    "token_index": source["token_index"],
                    "eva": surface,
                    "route": route,
                    "component_ordinal": component_ordinal,
                    "char_start": start,
                    "char_end": end,
                    "surface_segment": literal,
                    "component_role": role,
                    "productive": 1,
                })
        else:
            component_rows.append({
                "token_ordinal_global": global_ordinal,
                "locus": source["locus"],
                "token_index": source["token_index"],
                "eva": surface,
                "route": route,
                "component_ordinal": 1,
                "char_start": 0,
                "char_end": len(surface),
                "surface_segment": surface,
                "component_role": composition,
                "productive": 0,
            })

    card_output = []
    for ordinal, card in enumerate(transfer_cards, 1):
        card_output.append({
            "card_id": f"GDT672-F1R-{ordinal:03d}",
            **card,
            "scope": "F1R_EXACT_SURFACE_ONLY" if card["class"] in {"W", "O"} else "F1R_CURATED_ROLE_COMPOSITION",
            "semantic_features": semantic_features(card["working_meaning_de"]),
        })
    rival_rows = []
    for card in card_output:
        if card["class"] == "W":
            issue = "OPEN_INTERNAL_ANALYSIS"
            decision = "KEEP_AS_LOCAL_WHOLE_HYPOTHESIS"
        elif card["class"] == "O":
            issue = "POSITION_OR_READER_DEPENDENT"
            decision = "KEEP_OCCURRENCE_SCOPED"
        else:
            issue = "NONE"
            decision = "ACCEPT_CURATED_FULL_SURFACE_COMPOSITION"
        rival_rows.append({
            "card_id": card["card_id"],
            "surface": card["surface"],
            "class": card["class"],
            "confidence": card["confidence"],
            "composition": card["composition"],
            "rival_or_issue": issue,
            "decision": decision,
            "promoted_to_v48": 0,
        })

    line_spec_by_locus = {row["locus"]: row for row in line_specs}
    line_rows: list[dict[str, Any]] = []
    clause_rows: list[dict[str, Any]] = []
    for locus in by_line:
        readings = token_by_line[locus]
        spec = line_spec_by_locus[locus]
        cross = cross_by_locus[locus]
        action_ordinals = [row["token_index"] for row in readings if "ACTION" in row["contextual_semantic_features"].split("+")]
        quantity_ordinals = [row["token_index"] for row in readings if "QUANTITY" in row["contextual_semantic_features"].split("+")]
        reference_ordinals = [row["token_index"] for row in readings if "REFERENCE" in row["contextual_semantic_features"].split("+")]
        attachment_ordinals = [row["token_index"] for row in readings if int(row["value_attachment"])]
        learned_ordinals = [row["token_index"] for row in readings if row["transfer_class"] == "W"]
        occurrence_ordinals = [row["token_index"] for row in readings if row["transfer_class"] == "O"]
        routes = Counter(row["route"] for row in readings)
        literal = " | ".join(f"{row['eva']} = {row['working_meaning_de']}" for row in readings)
        contextual = " | ".join(f"{row['eva']} = {row['contextual_render_de']}" for row in readings)
        if GENERIC_FILLER.search(spec["working_translation_de"]):
            raise RuntimeError(f"generic filler in f1r line {locus}")
        line_row = {
            "line_ordinal": line_number_by_locus[locus],
            "page": "f1r",
            "locus": locus,
            "token_count": len(readings),
            "zl3b_line": cross["zl3b_clean"],
            "it2a_line": cross["it2a_clean"],
            "rf1b_line": cross["rf1b_clean"],
            "all_present_exact": cross["all_present_exact"],
            "exact_v48_tokens": routes["EXACT_V48"],
            "composed_transfer_tokens": routes["ROLE_COMPOSED_TRANSFER"],
            "learned_transfer_tokens": routes["LOCAL_WHOLE_HYPOTHESIS"],
            "occurrence_transfer_tokens": routes["OCCURRENCE_SCOPED_TRANSFER"],
            "literal_token_glosses_de": literal,
            "contextual_token_values_de": contextual,
            "frame": spec["frame"],
            "working_translation_de": spec["working_translation_de"],
            "uncertainty_note": spec["uncertainty_note"],
            "learned_token_indices": ",".join(learned_ordinals) or "NONE",
            "occurrence_token_indices": ",".join(occurrence_ordinals) or "NONE",
            "value_attachment_token_indices": ",".join(attachment_ordinals) or "NONE",
        }
        line_rows.append(line_row)
        clause_rows.append({
            "line_ordinal": line_number_by_locus[locus],
            "locus": locus,
            "frame": spec["frame"],
            "action_token_indices": ",".join(action_ordinals) or "NONE",
            "quantity_token_indices": ",".join(quantity_ordinals) or "NONE",
            "reference_token_indices": ",".join(reference_ordinals) or "NONE",
            "learned_token_indices": ",".join(learned_ordinals) or "NONE",
            "occurrence_token_indices": ",".join(occurrence_ordinals) or "NONE",
            "value_attachment_token_indices": ",".join(attachment_ordinals) or "NONE",
            "renderer_rules": "R01_THREE_LAYER+R02_ACTION_GATE+R06_VALUE_TYPING+R07_PROCESS_ORDER+R09_NOMINAL_LINE+R10_UNCERTAINTY+R11_NO_SUPPRESSION+R12_NO_FILLER",
            "working_translation_de": spec["working_translation_de"],
        })

    complete_rows = {row["locus"]: row for row in read_tsv(V48 / "COMPLETE_PASSAGES_V48.tsv")}
    coverage_rows = {row["locus"]: row for row in read_tsv(V48 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv")}
    control_rows: list[dict[str, Any]] = []
    for control_id, spec in enumerate(control_specs, 1):
        coverage = coverage_rows.get(spec["locus"])
        if coverage is None:
            raise RuntimeError(f"missing V48 control locus {spec['locus']}")
        complete = complete_rows.get(spec["locus"])
        unknown = int(coverage["unknown_tokens"])
        if control_id <= 5 and (complete is None or unknown != 0):
            raise RuntimeError("first five controls must be V48-complete")
        if control_id == 6 and unknown != 1:
            raise RuntimeError("sixth control must be the one-hole abstinence line")
        if GENERIC_FILLER.search(spec["working_translation_de"]):
            raise RuntimeError(f"generic filler in control {spec['locus']}")
        control_rows.append({
            "control_id": f"GDT672-C{control_id:02d}",
            "selection_reason": spec["purpose"],
            "register": spec["register"],
            "page": coverage["page"],
            "locus": coverage["locus"],
            "section": coverage["section"],
            "language": coverage["language"],
            "hand": coverage["hand"],
            "token_count": coverage["token_count"],
            "strict_complete": complete["strict_complete"] if complete else 0,
            "unknown_tokens": unknown,
            "zl3b_line": coverage["zl3b_line"],
            "v48_token_glosses_de": coverage["token_glosses_de"],
            "v48_gloss_sources": coverage["gloss_sources"],
            "v48_scope_states": coverage["scope_states"],
            "inherited_v48_translation_de": complete["working_translation_de"] if complete else "OPEN_ONE_TOKEN",
            "new_working_translation_de": spec["working_translation_de"],
            "mandatory_note": spec["mandatory_note"],
        })
    if (
        len({row["section"] for row in control_rows}) < 6
        or len({row["language"] for row in control_rows}) < 2
        or len({row["hand"] for row in control_rows}) < 3
    ):
        raise RuntimeError("control passage diversity drifted")

    comparison_rows: list[dict[str, Any]] = []
    readings_by_ordinal = {int(row["token_ordinal_global"]): row for row in token_readings}
    line_reader_by_locus = {row["locus"]: row for row in line_rows}
    start = 1
    for statement in statement_source:
        count = len(statement["surface_sequence"].split())
        ordinals = range(start, start + count)
        segment = [readings_by_ordinal[index] for index in ordinals]
        loci = list(dict.fromkeys(row["locus"] for row in segment))
        old = statement["gdt589_primary_reader_de"]
        new_literal = " | ".join(f"{row['eva']}={row['contextual_render_de']}" for row in segment)
        new_lines = " || ".join(line_reader_by_locus[locus]["working_translation_de"] for locus in loci)
        comparison_rows.append({
            "statement_ordinal": statement["reader_statement_ordinal"],
            "statement_id": statement["statement_id"],
            "token_start": start,
            "token_end": start + count - 1,
            "token_count": count,
            "covered_loci": ",".join(loci),
            "gdt589_generic_reader_de": old,
            "gdt589_generic_filler_hits": len(GENERIC_FILLER.findall(old)),
            "gdt672_concrete_token_sequence_de": new_literal,
            "gdt672_curated_line_readings_de": new_lines,
            "gdt672_generic_filler_hits": len(GENERIC_FILLER.findall(new_literal + " " + new_lines)),
            "comparison_only_not_meaning_input": 1,
        })
        start += count
    if start != 215:
        raise RuntimeError("GDT589 statement alignment did not consume 214 tokens")

    reader_lines = [
        "# GDT672 — f1r concrete V48 working reader",
        "",
        "This is an exploratory working reading, not a confirmed decipherment. Every source token is shown. Exact V48 cards remain unchanged; composed, learned, and occurrence-scoped f1r transfers are labeled separately.",
        "",
        "The 179-side panel contributes through the frozen V48 glossary. f1r itself was not in that panel and is rendered here as a transfer page. GDT589 appears only as a comparison baseline.",
        "",
    ]
    for row in line_rows:
        reader_lines.extend([
            f"## {row['locus']}",
            "",
            f"**ZL3b:** `{row['zl3b_line']}`",
            "",
            f"**Wörtlich:** {row['literal_token_glosses_de']}",
            "",
            f"**Gebunden:** {row['contextual_token_values_de']}",
            "",
            f"**Arbeitslesung:** {row['working_translation_de']}",
            "",
            f"**Restunsicherheit:** {row['uncertainty_note']}",
            "",
        ])
    reader = "\n".join(reader_lines).rstrip() + "\n"

    class_positions = Counter(row["transfer_class"] for row in token_readings)
    learned_lines = sum(int(row["learned_transfer_tokens"]) != 0 for row in line_rows)
    occurrence_lines = sum(int(row["occurrence_transfer_tokens"]) != 0 for row in line_rows)
    old_filler_hits = sum(int(row["gdt589_generic_filler_hits"]) for row in comparison_rows)
    new_filler_hits = sum(int(row["gdt672_generic_filler_hits"]) for row in comparison_rows)
    broad_counter = Counter(
        match.group(0).lower()
        for row in line_rows
        for match in BROAD_CARRIER.finditer(row["working_translation_de"])
    )
    result: dict[str, Any] = {
        "experiment_id": "GDT672",
        "status": STATUS,
        "page": "f1r",
        "basis": {
            "v48_guarded_panel_sides": 179,
            "f1r_in_v48_panel": False,
            "gdt589_used_as_meaning_input": False,
            "gdt600_used_as_wording_source": False,
            "gdt600_relational_principles_reexpressed_as_rules": True,
        },
        "source": {
            "tokens": len(token_rows),
            "physical_lines": len(by_line),
            "gdt589_statements": len(statement_source),
            "cross_reader_lines": len(cross_rows),
            "cross_reader_all_exact": sum(int(row["all_present_exact"]) for row in cross_rows),
            "token_guard": token_guard,
            "cross_guard": cross_guard,
        },
        "coverage": {
            "exact_v48_positions": exact_positions,
            "exact_v48_surface_types": len(exact_surfaces),
            "exact_whole_positions": exact_scope_counts["KNOWN_EXACT_WHOLE"],
            "context_licensed_positions": exact_scope_counts["KNOWN_CONTEXT_LICENSED"],
            "transfer_positions": 214 - exact_positions,
            "transfer_surface_types": len(open_surfaces),
            "composed_transfer_positions": class_positions["P"],
            "learned_transfer_positions": class_positions["W"],
            "occurrence_scoped_positions": class_positions["O"],
            "unassigned_positions": 0,
            "lines_with_learned_transfer": learned_lines,
            "lines_without_learned_transfer": 28 - learned_lines,
            "lines_with_occurrence_scoped_transfer": occurrence_lines,
        },
        "renderer": {
            "rules": len(rule_cards),
            "line_frames": dict(Counter(row["frame"] for row in line_rows)),
            "generic_filler_hits_new": new_filler_hits,
            "generic_filler_hits_gdt589_baseline": old_filler_hits,
            "control_passages": len(control_rows),
            "complete_controls": sum(int(row["unknown_tokens"]) == 0 for row in control_rows),
            "abstinence_controls": sum(int(row["unknown_tokens"]) > 0 for row in control_rows),
            "value_attachments": len(value_attachments),
            "broad_carrier_hits_new": sum(broad_counter.values()),
            "broad_carrier_profile": dict(sorted(broad_counter.items())),
        },
        "claim_ceiling": (
            "A complete exploratory f1r working reader: 129/214 positions inherit exact V48 cards; "
            "85/214 positions use explicit f1r transfer cards, of which learned and occurrence-scoped "
            "cards are not promoted to V48. This does not establish plaintext, language, phonetics, "
            "a historical codebook, a plant identity, a disease, a patient, a cure, or manuscript-wide meanings."
        ),
    }
    if new_filler_hits or any(GENERIC_FILLER.search(row["working_translation_de"]) for row in line_rows):
        raise RuntimeError("new f1r output contains generic filler")
    if learned_lines != 19 or 28 - learned_lines != 9:
        raise RuntimeError("learned-transfer line profile drifted")

    occurrence_audit = []
    for ordinal, row in enumerate(overrides, 1):
        occurrence_audit.append({
            "override_id": f"GDT672-O{ordinal:02d}", **row,
            "source_card_class": transfer[row["surface"]]["class"],
            "promoted_to_v48": 0,
        })
    attachment_audit = []
    for ordinal, row in enumerate(value_attachments, 1):
        attachment_audit.append({
            "attachment_id": f"GDT672-V{ordinal:02d}", **row,
            "source_match": 1,
            "changes_v48_card": 0,
        })

    write_text(output_dir / "F1R_SOURCE_ALIGNMENT.tsv", tsv_text(alignment_rows))
    write_text(output_dir / "F1R_TOKEN_READINGS.tsv", tsv_text(token_readings))
    write_text(output_dir / "F1R_COMPONENT_TRACES.tsv", tsv_text(component_rows))
    write_text(output_dir / "F1R_COMPOSITION_RIVALS.tsv", tsv_text(rival_rows))
    write_text(output_dir / "F1R_CLAUSE_FRAMES.tsv", tsv_text(clause_rows))
    write_text(output_dir / "F1R_LINE_READER.tsv", tsv_text(line_rows))
    write_text(output_dir / "F1R_GDT589_COMPARISON.tsv", tsv_text(comparison_rows))
    write_text(output_dir / "F1R_TRANSFER_CARDS.tsv", tsv_text(card_output))
    write_text(output_dir / "F1R_OCCURRENCE_AUDIT.tsv", tsv_text(occurrence_audit))
    write_text(output_dir / "F1R_VALUE_ATTACHMENT_AUDIT.tsv", tsv_text(attachment_audit))
    write_text(output_dir / "RENDERER_RULE_CARDS.tsv", tsv_text(rule_cards))
    write_text(output_dir / "REGISTER_DIVERSE_RENDER_AUDIT.tsv", tsv_text(control_rows))
    write_text(output_dir / "GDT672_F1R_CONCRETE_WORKING_READER.md", reader)
    write_text(output_dir / "RESULT.json", json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return result


def render_docs(result: dict[str, Any]) -> None:
    coverage = result["coverage"]
    renderer = result["renderer"]
    report = f"""# GDT672 — konkreter V48-Seitenrenderer

## Ergebnis

f1r ist jetzt vollständig vierstufig lesbar: 214/214 EVA-Token, 214/214 unveränderte Kartenwerte, siebzehn explizite Mengenbindungen und 28/28 vorsichtige Zeilenlesungen. 129 Positionen bzw. 84 Oberflächen kommen unverändert aus V48. Die übrigen 85 Positionen bzw. 80 Oberflächen erhalten explizite lokale Transferkarten: {coverage['composed_transfer_positions']} kompositionelle, {coverage['learned_transfer_positions']} gelernte und {coverage['occurrence_scoped_positions']} occurrence-spezifische Stellen.

Die gelernte Schicht wird nicht heimlich als V48-Erfolg gezählt: {coverage['lines_with_learned_transfer']}/28 Zeilen enthalten mindestens ein lokales Ganzwort; {coverage['lines_without_learned_transfer']}/28 kommen ohne ein solches Ganzwort aus. GDT589s 214-Token-Folge stimmt bytegenau mit der guarded f1r-Quelle überein, dient aber ausschließlich als Vergleich. Seine generische Prosa hat {renderer['generic_filler_hits_gdt589_baseline']} harte Füllworttreffer; die neue Ausgabe hat {renderer['generic_filler_hits_new']}. Sie enthält jedoch weiterhin {renderer['broad_carrier_hits_new']} breite Trägerwörter wie Ansatz, Kompositum oder Species. Das ist sichtbare Restunbestimmtheit, kein verschwundener Befund.

## Was der Renderer tatsächlich tut

V48 liefert Stoff-, Prozess-, Zustands-, Mengen- und Formwerte. Zwölf explizite Regeln binden nur vorhandene Slots: ein Imperativ braucht eine Aktionskarte, Mengen werden am Kopf typisiert, Prozessreihenfolge bleibt erhalten, nominale Zeilen bleiben Katalogzeilen und Unsicherheit bleibt sichtbar. Aus dem lokalen GDT600-Entwurf wurden nur diese Valenz- und Ordnungsprinzipien neu formuliert; seine Wörter `Stationsansatz`, `Arbeitsgang` und `Arbeitsstelle` werden nicht importiert.

Sechs Kontrollpassagen decken sechs Register, zwei Sprachen und drei Hände ab. Fünf sind in V48 vollständig; die sechste hält `dsheody` absichtlich offen. Damit prüft die Ausgabe sowohl konkrete Flüssigkeit als auch Abstinenz.

## Grenze

{result['claim_ceiling']}
"""
    method = """# Method

1. Read f1r only through `./vmanus-exp query-tsv`, with selector `page`, allow-value `f1r`, explicit columns, and forbidden prefix `f84`.
2. Replay the 214 guarded ZL3b tokens against the seven published GDT589 f1r statement surface sequences. GDT589 text is comparison-only.
3. Resolve exact surfaces first against the frozen V48 glossary. Exact V48 rows are never overwritten.
4. Resolve the remaining 80 surfaces through the explicit f1r transfer deck. `P` cards have a complete character-covering sequence of V48 roles; `W` cards are local learned wholes; `O` cards require an occurrence or reader boundary. None is promoted to V48.
5. Emit an interlinear, contextual quantity bindings, component traces, clause frames, and a curated working reading for all 28 lines. Every token remains visible even across a bilateral reader join.
6. Replay five complete V48 controls across H/P/B/S/T plus one C-register abstinence control.
7. Reject generic filler and validate all source counts, V48 invariants, card coverage, joins, controls, and deterministic rebuilds independently.
"""
    readme = """# GDT672 — V48 concrete page renderer

Start with `artifacts/GDT672_F1R_CONCRETE_WORKING_READER.md` for the complete f1r reading. `REPORT.md` gives the result and limits; `METHOD.md` gives the executable route. Run the builder and validator with the commands sealed in `experiment.json`.
"""
    artifact_readme = """# Artifact map

- `GDT672_F1R_CONCRETE_WORKING_READER.md`: complete four-level f1r reader.
- `F1R_TOKEN_READINGS.tsv`: all 214 token values and provenance routes.
- `F1R_LINE_READER.tsv`: all 28 source lines, literal values, and working readings.
- `F1R_COMPONENT_TRACES.tsv`: character-covering component traces.
- `F1R_TRANSFER_CARDS.tsv`: the 80 explicit f1r transfer cards.
- `F1R_OCCURRENCE_AUDIT.tsv`: the seven occurrence/reader-boundary realizations.
- `F1R_VALUE_ATTACHMENT_AUDIT.tsv`: seventeen explicit quantity-to-head attachments.
- `F1R_GDT589_COMPARISON.tsv`: comparison-only old generic reader versus V48 output.
- `REGISTER_DIVERSE_RENDER_AUDIT.tsv`: five complete controls and one abstinence control.
- `RESULT.json`, `VALIDATION.json`: compact result and independent validation.
"""
    write_text(BASE / "REPORT.md", report)
    write_text(BASE / "METHOD.md", method)
    write_text(BASE / "README.md", readme)
    write_text(ART / "README.md", artifact_readme)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ART)
    parser.add_argument("--no-docs", action="store_true")
    args = parser.parse_args()
    result = build(args.output_dir)
    if not args.no_docs and args.output_dir.resolve() == ART.resolve():
        render_docs(result)
    print(json.dumps({"status": result["status"], "coverage": result["coverage"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
