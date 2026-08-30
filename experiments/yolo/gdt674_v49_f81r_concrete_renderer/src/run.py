#!/usr/bin/env python3
"""Build GDT674: a concrete, source-preserving f81r V49 working reader."""
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
BASE_REL = Path("experiments/yolo/gdt674_v49_f81r_concrete_renderer")
BASE = ROOT / BASE_REL
SRC = BASE / "src"
ART = BASE / "artifacts"
V48 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G673 = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
STATUS = "PASS_F81R_210_TOKEN_CONCRETE_READER__27_REVIEW_POSITIONS__24_GAPS_CLOSED"

OUTPUT_NAMES = (
    "F81R_SOURCE_ALIGNMENT.tsv",
    "F81R_TOKEN_READINGS.tsv",
    "F81R_COMPONENT_TRACES.tsv",
    "F81R_REVIEW_CARDS.tsv",
    "F81R_READER_VARIANT_AUDIT.tsv",
    "F81R_LINE_READER.tsv",
    "F81R_EXPLICIT_ACTION_AUDIT.tsv",
    "F81R_VALUE_ATTACHMENT_AUDIT.tsv",
    "F81R_COVERAGE_OVERLAY.tsv",
    "F81R_PAGE_ARCHITECTURE.tsv",
    "LEGACY_TOKEN_RENDERER_AUDIT.tsv",
    "LEGACY_STATEMENT_BASELINE.tsv",
    "RENDERER_RULE_CARDS.tsv",
    "GDT674_F81R_CONCRETE_WORKING_READER.md",
    "RESULT.json",
)

GENERIC_FILLER = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|Aktiver Posten|laufender Eintrag|work item|working material|"
    r"worksite|work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)
BROAD_CARRIER = re.compile(
    r"\b(?:\w*Ansatz\w*|\w*Kompositum\w*|\w*Species\w*|Drogenstoff|"
    r"Trockengut|Feuchtmaterial|Materialmaß|Grundauszug)\b",
    re.IGNORECASE,
)
ACTION_RE = re.compile(
    r"\b(?:abkühlen|abmessen|abseihen|abteilen|abschließen|ansetzen|einweichen|"
    r"erhitzen|fertigstellen|kühlen|nehmen|nimm|ruhen|schließen|seihen|trocknen|"
    r"zugeben|führe|miss|stelle|weiche)\w*\b",
    re.IGNORECASE,
)
QUANTITY_RE = re.compile(
    r"\b(?:ein(?:e[mnrs]?)?|zwei|drei|vier|Teil(?:e)?|Maß(?:e)?|Dosis|Dosen|"
    r"Portion|Menge|Fraktion|Pfund|Charge|Klasse)\b",
    re.IGNORECASE,
)
STAGE_RE = re.compile(
    r"\b(?:Grad\w*|Stufe\w*|Mittelstufe|Endstufe|Grundstufe|Gradanfang|Gradmitte)\b",
    re.IGNORECASE,
)

ROLE_SPELLING = {
    "A_PART_OR_LINK": "a",
    "AL_RAW_I": "al",
    "AM_UNIT_I": "am",
    "AR_FRACTION_I": "ar",
    "CH_DRY": "ch",
    "CPH_COMPOSITE": "cph",
    "D_MEASURE": "d",
    "D_TERM_CLOSE": "d",
    "DY_FINISHED": "dy",
    "EE_END": "ee",
    "EEE_LONG_OR_FINAL": "eee",
    "E_MIDDLE": "e",
    "F_FLOWER": "f",
    "I_FORM_I": "i",
    "K_HOT": "k",
    "L_WOOD": "l",
    "OL_MATERIAL": "ol",
    "OR_PORTION": "or",
    "O_PREP": "o",
    "P_POWDER": "p",
    "QOL_ADD": "qol",
    "QO_COMMAND": "qo",
    "SH_MOIST": "sh",
    "S_SEED": "s",
    "S_TERM_SPECIES": "s",
    "T_COLD": "t",
    "Y_START_OR_CLOSE": "y",
}


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
    completed = subprocess.run(
        [
            str(ROOT / "vmanus-exp"), "query-tsv", str(rel),
            "--selector", "page", "--allow", "f81r", "--columns", columns,
            "--forbid-prefix", "f84",
        ],
        cwd=ROOT, check=True, text=True, capture_output=True,
    )
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("guarded f81r query emitted no GUARD_STATS")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return rows, {str(key): int(value) for key, value in json.loads(match.group(1)).items()}


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
    if re.search(r"Droge|Species|Ansatz|Kraut|Blatt|Wurzel|Samen|Pulver|Kompositum|Stoff|Holz", text, re.I):
        features.append("MATERIAL")
    if re.search(r"heiß|kalt|trocken|feucht|eingeweicht|abgeschlossen|fertig|gekühlt|erhitzt", text, re.I):
        features.append("STATE")
    return "+".join(features) or "DESCRIPTOR"


def parse_components(surface: str, composition: str) -> list[tuple[int, int, str, str]]:
    result: list[tuple[int, int, str, str]] = []
    cursor = 0
    for role in composition.split("+"):
        literal = ROLE_SPELLING.get(role)
        if literal is None:
            raise RuntimeError(f"no literal spelling for productive role {role}")
        end = cursor + len(literal)
        if surface[cursor:end] != literal:
            raise RuntimeError(f"component trace does not cover {surface}: {role}@{cursor}")
        result.append((cursor, end, literal, role))
        cursor = end
    if cursor != len(surface):
        raise RuntimeError(f"component trace leaves residue in {surface}")
    return result


def align_reader_tokens(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
    """Use GDT671's exact-token/low-cost-boundary dynamic program."""
    n, m = len(source), len(alternate)
    cells: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = (0, 0, [])

    def offer(
        i: int, j: int, cost: int, steps: int,
        path: list[tuple[str, tuple[int, ...], str]],
        operation: tuple[str, tuple[int, ...], str],
    ) -> None:
        candidate = (cost, steps, [*path, operation])
        previous = cells[i][j]
        if previous is None or candidate[:2] < previous[:2]:
            cells[i][j] = candidate

    for i in range(n + 1):
        for j in range(m + 1):
            cell = cells[i][j]
            if cell is None:
                continue
            cost, steps, path = cell
            if i < n and j < m:
                offer(
                    i + 1, j + 1, cost + (0 if source[i] == alternate[j] else 10),
                    steps + 1, path, ("ONE", (i,), alternate[j]),
                )
            if i + 1 < n and j < m and source[i] + source[i + 1] == alternate[j]:
                offer(i + 2, j + 1, cost + 1, steps + 1, path, ("MERGE_2", (i, i + 1), alternate[j]))
            if i + 2 < n and j < m and source[i] + source[i + 1] + source[i + 2] == alternate[j]:
                offer(i + 3, j + 1, cost + 1, steps + 1, path, ("MERGE_3", (i, i + 1, i + 2), alternate[j]))
            if i < n and j + 1 < m and source[i] == alternate[j] + alternate[j + 1]:
                offer(i + 1, j + 2, cost + 1, steps + 1, path, ("SPLIT_2", (i,), source[i]))
            if i < n:
                offer(i + 1, j, cost + 10, steps + 1, path, ("DELETE", (i,), ""))
            if j < m:
                offer(i, j + 1, cost + 10, steps + 1, path, ("INSERT", (), alternate[j]))
    final = cells[n][m]
    if final is None:
        raise RuntimeError("reader token alignment unexpectedly has no path")
    return final[2]


def reader_operations(source: list[str], alternate: list[str]) -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    for operation, indices, rendered in align_reader_tokens(source, alternate):
        for index in indices:
            label = "EXACT" if operation == "ONE" and rendered == source[index] else operation
            result[index] = (label, rendered or "EMPTY")
    if set(result) != set(range(len(source))):
        raise RuntimeError("reader alignment did not cover every ZL3b position")
    return result


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    transfer_cards = read_tsv(SRC / "F81R_TRANSFER_CARDS.tsv")
    context_cards = read_tsv(SRC / "F81R_CONTEXT_CARDS.tsv")
    line_specs = read_tsv(SRC / "F81R_LINE_SPECS.tsv")
    value_specs = read_tsv(SRC / "F81R_VALUE_ATTACHMENTS.tsv")
    action_specs = read_tsv(SRC / "F81R_EXPLICIT_ACTIONS.tsv")
    rule_cards = read_tsv(SRC / "RENDERER_RULES.tsv")
    if len(transfer_cards) != 23 or len({row["surface"] for row in transfer_cards}) != 23:
        raise RuntimeError("f81r transfer deck must contain 23 raw-unknown surfaces")
    if sum(int(row["count"]) for row in transfer_cards) != 24:
        raise RuntimeError("f81r transfer deck must cover 24 raw unknown positions")
    if len(context_cards) != 3 or {(r["locus"], r["token_index"]) for r in context_cards} != {
        ("f81r.17", "1"), ("f81r.25", "8"), ("f81r.29", "1"),
    }:
        raise RuntimeError("f81r context recheck deck drifted")
    if len(line_specs) != 31 or [row["locus"] for row in line_specs] != [f"f81r.{i}" for i in range(1, 32)]:
        raise RuntimeError("f81r line spec order drifted")
    if len(value_specs) != 10 or len(action_specs) != 18 or len(rule_cards) != 13:
        raise RuntimeError("f81r auxiliary source deck dimensions drifted")

    token_rows, token_guard = guarded_query(
        TOKENS_REL, "page,locus,token_index,eva,kind,section,language,hand",
    )
    cross_rows, cross_guard = guarded_query(
        CROSS_REL, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    if len(token_rows) != 210 or len(cross_rows) != 31:
        raise RuntimeError("guarded f81r source census drifted")
    if any(row["page"] != "f81r" or row["page"].startswith("f84") for row in token_rows + cross_rows):
        raise RuntimeError("guarded source materialized a forbidden or non-f81r row")
    expected_order = sorted(token_rows, key=lambda row: (locus_number(row["locus"]), int(row["token_index"])))
    if token_rows != expected_order:
        raise RuntimeError("guarded f81r token order is not physical line order")
    if len({(row["locus"], row["token_index"]) for row in token_rows}) != 210:
        raise RuntimeError("guarded f81r source keys are not unique")

    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        by_line[row["locus"]].append(row)
    if list(by_line) != [f"f81r.{i}" for i in range(1, 32)]:
        raise RuntimeError("f81r line set drifted")
    for locus, rows in by_line.items():
        if [int(row["token_index"]) for row in rows] != list(range(1, len(rows) + 1)):
            raise RuntimeError(f"nonconsecutive token indices at {locus}")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    if list(cross_by_locus) != [f"f81r.{i}" for i in range(1, 32)]:
        raise RuntimeError("f81r cross-reader line order drifted")
    for locus, rows in by_line.items():
        if " ".join(row["eva"] for row in rows) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"token/cross-reader mismatch at {locus}")
    if sum(int(row["all_three_present"]) for row in cross_rows) != 31:
        raise RuntimeError("not every f81r line has all three readers")
    if sum(int(row["all_present_exact"]) for row in cross_rows) != 7:
        raise RuntimeError("f81r exact three-reader line count drifted")

    coverage_rows = [
        row for row in read_tsv(V48 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv")
        if row["page"] == "f81r"
    ]
    coverage_rows.sort(key=lambda row: locus_number(row["locus"]))
    if len(coverage_rows) != 31:
        raise RuntimeError("V48 f81r coverage line census drifted")
    baseline: dict[tuple[str, str], dict[str, str]] = {}
    for row in coverage_rows:
        surfaces = row["zl3b_line"].split()
        glosses = row["token_glosses_de"].split(" | ")
        sources = row["gloss_sources"].split(" | ")
        states = row["scope_states"].split(" | ")
        if not (len(surfaces) == len(glosses) == len(sources) == len(states) == int(row["token_count"])):
            raise RuntimeError(f"V48 line vector drift at {row['locus']}")
        if surfaces != [source["eva"] for source in by_line[row["locus"]]]:
            raise RuntimeError(f"V48 source line drift at {row['locus']}")
        for index, (surface, gloss, source, state) in enumerate(zip(surfaces, glosses, sources, states), 1):
            baseline[(row["locus"], str(index))] = {
                "surface": surface, "gloss": gloss, "source": source, "state": state,
            }

    transfer = {row["surface"]: row for row in transfer_cards}
    source_counts = Counter(row["eva"] for row in token_rows)
    raw_unknown_keys = {
        key for key, row in baseline.items() if row["state"] == "UNKNOWN_SURFACE"
    }
    raw_unknown_surfaces = {baseline[key]["surface"] for key in raw_unknown_keys}
    if len(raw_unknown_keys) != 24 or raw_unknown_surfaces != set(transfer):
        raise RuntimeError("24-position V48 raw-unknown frontier drifted")
    if any(source_counts[surface] != int(card["count"]) for surface, card in transfer.items()):
        raise RuntimeError("transfer card source counts drifted")

    context_by_key = {(row["locus"], row["token_index"]): row for row in context_cards}
    if len(context_by_key) != 3 or set(context_by_key) & raw_unknown_keys:
        raise RuntimeError("context review keys overlap or duplicate the raw frontier")
    for key, row in context_by_key.items():
        if baseline[key]["surface"] != row["surface"] or baseline[key]["gloss"] != row["working_meaning_de"]:
            raise RuntimeError(f"context review does not replay V48 at {key}")
    review_keys = raw_unknown_keys | set(context_by_key)
    review_surfaces = {baseline[key]["surface"] for key in review_keys}
    if len(review_keys) != 27 or len(review_surfaces) != 25:
        raise RuntimeError("27-position/25-surface review frontier drifted")
    unchanged_keys = set(baseline) - review_keys
    if len(unchanged_keys) != 183 or len({baseline[key]["surface"] for key in unchanged_keys}) != 103:
        raise RuntimeError("183-position/103-surface inherited V48 layer drifted")

    y_rules = [
        row for row in read_tsv(G673 / "O_CONTEXT_RULES.tsv")
        if row["surface"] == "y" and row["reason_code"] == "Y_ENTRY_OR_LABEL_OUTSIDE_CARD"
    ]
    if len(y_rules) != 1 or y_rules[0]["occurrences"] != "70":
        raise RuntimeError("GDT673 contextual y split drifted")
    g673_result = json.loads((G673 / "RESULT.json").read_text(encoding="utf-8"))
    if g673_result["coverage_overlay"]["unknown_positions_after"] != 8018:
        raise RuntimeError("GDT673 overlay basis drifted")

    stem_roles = {row["structural_role"] for row in read_tsv(V48 / "STEM_MODEL_V48.tsv")}
    for card in transfer_cards:
        if card["class"] == "P":
            components = card["composition"].split("+")
            if any(role not in stem_roles for role in components):
                raise RuntimeError(f"unknown V48 role in {card['surface']}: {card['composition']}")
            parse_components(card["surface"], card["composition"])
        elif card["class"] != "W":
            raise RuntimeError(f"raw unknown card must be P or W: {card['surface']}")
    transfer_class_positions = Counter(
        transfer[baseline[key]["surface"]]["class"] for key in raw_unknown_keys
    )
    if transfer_class_positions != {"P": 21, "W": 3}:
        raise RuntimeError(f"review transfer class profile drifted: {transfer_class_positions}")

    attachment_by_key = {(row["locus"], row["token_index"]): row for row in value_specs}
    action_by_key = {(row["locus"], row["token_index"]): row for row in action_specs}
    if len(attachment_by_key) != 10 or len(action_by_key) != 18:
        raise RuntimeError("duplicate value attachment or action row")
    source_by_key = {(row["locus"], row["token_index"]): row for row in token_rows}
    for key, row in {**attachment_by_key, **action_by_key}.items():
        if key not in source_by_key or source_by_key[key]["eva"] != row["surface"]:
            raise RuntimeError(f"auxiliary source row mismatch at {key}")
    action_lines = {key[0] for key in action_by_key}
    if len(action_lines) != 15:
        raise RuntimeError("explicit V48 actions must occupy 15 physical lines")

    global_by_key: dict[tuple[str, str], int] = {}
    alignment_rows: list[dict[str, Any]] = []
    token_rows_out: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    tokens_by_line: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for global_ordinal, source in enumerate(token_rows, 1):
        key = (source["locus"], source["token_index"])
        global_by_key[key] = global_ordinal
        base = baseline[key]
        attachment = attachment_by_key.get(key)
        action = action_by_key.get(key)
        if key in raw_unknown_keys:
            card = transfer[source["eva"]]
            card_class = card["class"]
            route = "ROLE_COMPOSED_REVIEW" if card_class == "P" else "LOCAL_WHOLE_REVIEW"
            meaning = card["working_meaning_de"]
            composition = card["composition"]
            confidence = card["confidence"]
            source_label = "GDT674_RAW_UNKNOWN_REVIEW_CARD"
            scope = "PAGE_LOCAL_REVIEW_NOT_PROMOTED"
            raw_unknown = 1
            review_position = 1
        elif key in context_by_key:
            card = context_by_key[key]
            card_class = "O"
            route = "OCCURRENCE_CONTEXT_REVIEW"
            meaning = card["working_meaning_de"]
            composition = card["composition"]
            confidence = card["confidence"]
            source_label = "GDT674_CONTEXT_RECHECK_OF_V48"
            scope = "OCCURRENCE_ONLY_NOT_PROMOTED"
            raw_unknown = 0
            review_position = 1
        else:
            card_class = "E"
            route = "INHERITED_V48"
            meaning = base["gloss"]
            composition = "INHERITED_V48_LINE_CARD"
            confidence = base["state"]
            source_label = base["source"]
            scope = base["state"]
            raw_unknown = 0
            review_position = 0
        contextual = attachment["contextual_render_de"] if attachment else meaning
        alignment_rows.append({
            "global_ordinal": global_ordinal,
            "line_ordinal": locus_number(source["locus"]),
            "page": source["page"],
            "locus": source["locus"],
            "token_index": source["token_index"],
            "eva": source["eva"],
            "section": source["section"],
            "language": source["language"],
            "hand": source["hand"],
            "v48_line_surface_match": 1,
        })
        reading = {
            **alignment_rows[-1],
            "route": route,
            "review_class": card_class,
            "review_position": review_position,
            "raw_v48_unknown_before": raw_unknown,
            "working_meaning_de": meaning,
            "contextual_render_de": contextual,
            "composition": composition,
            "semantic_features": semantic_features(contextual),
            "confidence": confidence,
            "meaning_source": source_label,
            "scope_state": scope,
            "baseline_v48_gloss_de": base["gloss"],
            "baseline_v48_source": base["source"],
            "baseline_v48_scope_state": base["state"],
            "value_attachment": 1 if attachment else 0,
            "explicit_action": 1 if action else 0,
            "explicit_action_de": action["action_de"] if action else "NONE",
        }
        token_rows_out.append(reading)
        tokens_by_line[source["locus"]].append(reading)
        if route == "ROLE_COMPOSED_REVIEW":
            pieces = parse_components(source["eva"], composition)
            for component_ordinal, (start, end, literal, role) in enumerate(pieces, 1):
                component_rows.append({
                    "global_ordinal": global_ordinal,
                    "locus": source["locus"], "token_index": source["token_index"],
                    "eva": source["eva"], "route": route,
                    "component_ordinal": component_ordinal,
                    "char_start": start, "char_end": end,
                    "surface_segment": literal, "component_role": role,
                    "productive": 1,
                })
        else:
            component_rows.append({
                "global_ordinal": global_ordinal,
                "locus": source["locus"], "token_index": source["token_index"],
                "eva": source["eva"], "route": route,
                "component_ordinal": 1, "char_start": 0,
                "char_end": len(source["eva"]), "surface_segment": source["eva"],
                "component_role": composition, "productive": 0,
            })

    token_by_key = {(row["locus"], row["token_index"]): row for row in token_rows_out}
    review_card_rows: list[dict[str, Any]] = []
    card_drafts: list[dict[str, Any]] = []
    for card in transfer_cards:
        keys = [key for key in raw_unknown_keys if baseline[key]["surface"] == card["surface"]]
        card_drafts.append({
            **card,
            "positions": "|".join(f"{key[0]}:{key[1]}" for key in sorted(keys, key=lambda k: global_by_key[k])),
            "first_global_ordinal": min(global_by_key[key] for key in keys),
            "origin": "RAW_V48_UNKNOWN",
            "raw_unknown_positions": len(keys),
            "context_recheck_positions": 0,
            "candidate_for_panel_scan": 1,
        })
    context_grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in context_cards:
        context_grouped[row["surface"]].append(row)
    for surface, rows in context_grouped.items():
        keys = [(row["locus"], row["token_index"]) for row in rows]
        if len({(row["composition"], row["working_meaning_de"], row["strongest_rival_de"], row["confidence"]) for row in rows}) != 1:
            raise RuntimeError(f"context surface {surface} has incompatible occurrence cards")
        first = rows[0]
        card_drafts.append({
            "surface": surface, "count": len(rows), "class": "O",
            "composition": first["composition"],
            "working_meaning_de": first["working_meaning_de"],
            "strongest_rival_de": first["strongest_rival_de"],
            "confidence": first["confidence"],
            "rationale": " | ".join(row["rationale"] for row in rows),
            "positions": "|".join(f"{key[0]}:{key[1]}" for key in sorted(keys, key=lambda k: global_by_key[k])),
            "first_global_ordinal": min(global_by_key[key] for key in keys),
            "origin": "CONTEXT_RECHECK",
            "raw_unknown_positions": 0,
            "context_recheck_positions": len(rows),
            "candidate_for_panel_scan": 0,
        })
    card_drafts.sort(key=lambda row: int(row["first_global_ordinal"]))
    for ordinal, row in enumerate(card_drafts, 1):
        review_card_rows.append({
            "card_id": f"GDT674-F81R-{ordinal:02d}", **row,
            "semantic_features": semantic_features(str(row["working_meaning_de"])),
            "promoted_to_v48": 0,
        })
    if len(review_card_rows) != 25:
        raise RuntimeError("review card surface count drifted")

    reader_rows: list[dict[str, Any]] = []
    operations_cache: dict[tuple[str, str], dict[int, tuple[str, str]]] = {}
    for key in sorted(review_keys, key=lambda item: global_by_key[item]):
        locus, token_index = key
        index = int(token_index) - 1
        cross = cross_by_locus[locus]
        source_line = cross["zl3b_clean"].split()
        for reader_field, reader_name in (("it2a_clean", "IT2a"), ("rf1b_clean", "RF1b")):
            operations_cache[(locus, reader_name)] = reader_operations(source_line, cross[reader_field].split())
        it_op, it_form = operations_cache[(locus, "IT2a")][index]
        rf_op, rf_form = operations_cache[(locus, "RF1b")][index]
        if it_op == "EXACT" and rf_op == "EXACT":
            support = "BOTH_EXACT"
        elif it_op == "EXACT" or rf_op == "EXACT":
            support = "ONE_EXACT"
        else:
            support = "NEITHER_EXACT"
        token = token_by_key[key]
        decision = {
            "P": "HOLD_EXPLORATORY_COMPOSITION",
            "W": "HOLD_LOCAL_WHOLE",
            "O": "HOLD_OCCURRENCE_CONTEXT_ONLY",
        }[token["review_class"]]
        reader_rows.append({
            "global_ordinal": global_by_key[key],
            "locus": locus, "token_index": token_index,
            "surface": token["eva"], "review_class": token["review_class"],
            "working_meaning_de": token["working_meaning_de"],
            "it2a_operation": it_op, "it2a_form": it_form,
            "rf1b_operation": rf_op, "rf1b_form": rf_form,
            "reader_support": support, "decision": decision,
            "zl3b_line": cross["zl3b_clean"],
            "it2a_line": cross["it2a_clean"],
            "rf1b_line": cross["rf1b_clean"],
        })
    reader_profile = Counter(row["reader_support"] for row in reader_rows)
    if reader_profile != {"BOTH_EXACT": 11, "ONE_EXACT": 13, "NEITHER_EXACT": 3}:
        raise RuntimeError(f"review reader profile drifted: {reader_profile}")

    line_spec_by_locus = {row["locus"]: row for row in line_specs}
    line_rows: list[dict[str, Any]] = []
    for locus, readings in tokens_by_line.items():
        spec = line_spec_by_locus[locus]
        cross = cross_by_locus[locus]
        line_review = [row for row in readings if int(row["review_position"])]
        line_unknown = [row for row in readings if int(row["raw_v48_unknown_before"])]
        line_actions = [row for row in readings if int(row["explicit_action"])]
        literal = " | ".join(f"{row['eva']} = {row['working_meaning_de']}" for row in readings)
        contextual = " | ".join(f"{row['eva']} = {row['contextual_render_de']}" for row in readings)
        if GENERIC_FILLER.search(spec["working_translation_de"]):
            raise RuntimeError(f"generic filler in curated f81r line {locus}")
        line_rows.append({
            "line_ordinal": locus_number(locus),
            "page": "f81r", "locus": locus,
            "visual_block": "F81R_UPPER_POOL" if locus_number(locus) <= 15 else "F81R_LOWER_POOL",
            "line_mode": "INHERITED_ACTION_ANCHOR" if locus in action_lines else "NO_INHERITED_ACTION_ANCHOR",
            "token_count": len(readings),
            "zl3b_line": cross["zl3b_clean"],
            "it2a_line": cross["it2a_clean"],
            "rf1b_line": cross["rf1b_clean"],
            "all_present_exact": cross["all_present_exact"],
            "inherited_v48_tokens": len(readings) - len(line_review),
            "review_tokens": len(line_review),
            "raw_unknown_before": len(line_unknown),
            "unknown_after": 0,
            "newly_complete": 1 if line_unknown else 0,
            "composed_review_tokens": sum(row["review_class"] == "P" for row in line_review),
            "learned_review_tokens": sum(row["review_class"] == "W" for row in line_review),
            "context_review_tokens": sum(row["review_class"] == "O" for row in line_review),
            "explicit_action_tokens": len(line_actions),
            "explicit_action_token_indices": ",".join(row["token_index"] for row in line_actions) or "NONE",
            "review_token_indices": ",".join(row["token_index"] for row in line_review) or "NONE",
            "value_attachment_token_indices": ",".join(row["token_index"] for row in readings if int(row["value_attachment"])) or "NONE",
            "literal_token_glosses_de": literal,
            "contextual_token_values_de": contextual,
            "frame": spec["frame"],
            "working_translation_de": spec["working_translation_de"],
            "uncertainty_note": spec["uncertainty_note"],
        })
    if len(line_rows) != 31 or sum(int(row["newly_complete"]) for row in line_rows) != 12:
        raise RuntimeError("f81r page completion profile drifted")
    if Counter(row["line_mode"] for row in line_rows) != {"INHERITED_ACTION_ANCHOR": 15, "NO_INHERITED_ACTION_ANCHOR": 16}:
        raise RuntimeError("f81r action/nominal line architecture drifted")

    action_audit_rows = []
    for ordinal, row in enumerate(action_specs, 1):
        key = (row["locus"], row["token_index"])
        token = token_by_key[key]
        action_audit_rows.append({
            "action_id": f"GDT674-A{ordinal:02d}", **row,
            "global_ordinal": global_by_key[key],
            "working_meaning_de": token["working_meaning_de"],
            "meaning_source": token["meaning_source"],
            "source_match": 1,
        })
    attachment_rows = []
    for ordinal, row in enumerate(value_specs, 1):
        key = (row["locus"], row["token_index"])
        attachment_rows.append({
            "attachment_id": f"GDT674-V{ordinal:02d}", **row,
            "global_ordinal": global_by_key[key],
            "source_match": 1,
            "changes_base_card": 0,
        })

    legacy_token_rows = [
        row for row in read_tsv(G416 / "gdt416_4576_imperative_clauses.tsv")
        if row["physical_page"] == "f81r"
    ]
    if len(legacy_token_rows) != 210 or [row["surface"] for row in legacy_token_rows] != [row["eva"] for row in token_rows]:
        raise RuntimeError("GDT416 f81r token sequence does not replay guarded source")
    legacy_audit_rows: list[dict[str, Any]] = []
    for ordinal, (legacy, new) in enumerate(zip(legacy_token_rows, token_rows_out), 1):
        legacy_audit_rows.append({
            "global_ordinal": ordinal,
            "locus": new["locus"], "token_index": new["token_index"], "surface": new["eva"],
            "gdt416_imperative_clause_de": legacy["imperative_clause_de"],
            "gdt416_generic_station_or_entry": 1 if re.search(r"Stations|laufenden Eintrag", legacy["imperative_clause_de"], re.I) else 0,
            "gdt416_inherited_action": 1 if legacy["inherited_action_root"] != "NONE" else 0,
            "gdt416_inherited_argument": 1 if legacy["inherited_argument_root"] != "NONE" else 0,
            "gdt674_route": new["route"],
            "gdt674_token_meaning_de": new["working_meaning_de"],
            "comparison_only_not_meaning_input": 1,
        })
    if sum(int(row["gdt416_generic_station_or_entry"]) for row in legacy_audit_rows) != 208:
        raise RuntimeError("GDT416 generic token-row baseline drifted")
    if sum(int(row["gdt416_inherited_action"]) for row in legacy_audit_rows) != 89:
        raise RuntimeError("GDT416 inherited action baseline drifted")
    if sum(int(row["gdt416_inherited_argument"]) for row in legacy_audit_rows) != 114:
        raise RuntimeError("GDT416 inherited argument baseline drifted")

    legacy_statements = [
        row for row in read_tsv(G407 / "gdt407_715_statement_edition.tsv")
        if row["physical_page"] == "f81r"
    ]
    if len(legacy_statements) != 48:
        raise RuntimeError("GDT407 f81r statement count drifted")
    flattened_legacy = [surface for row in legacy_statements for surface in row["surface_sequence"].split()]
    if flattened_legacy != [row["eva"] for row in token_rows]:
        raise RuntimeError("GDT407 f81r statement sequence does not replay guarded source")
    statement_rows = []
    owner_by_global: dict[int, str] = {}
    cursor = 1
    for row in legacy_statements:
        count = len(row["surface_sequence"].split())
        for global_ordinal in range(cursor, cursor + count):
            owner_by_global[global_ordinal] = row["owner_de"]
        hits = len(GENERIC_FILLER.findall(row["literal_core_sequence_de"]))
        statement_rows.append({
            "global_statement_id": row["global_statement_id"],
            "token_start": cursor, "token_end": cursor + count - 1,
            "token_count": count, "owner_de": row["owner_de"],
            "surface_sequence": row["surface_sequence"],
            "gdt407_literal_core_sequence_de": row["literal_core_sequence_de"],
            "generic_filler_hits": hits,
            "comparison_only_not_meaning_input": 1,
        })
        cursor += count
    if cursor != 211 or sum(int(row["generic_filler_hits"]) for row in statement_rows) != 71:
        raise RuntimeError("GDT407 generic statement baseline drifted")
    if set(owner_by_global[index] for index in range(1, 95)) != {"F81R_UPPER_POOL"}:
        raise RuntimeError("f81r upper visual owner boundary drifted")
    if set(owner_by_global[index] for index in range(95, 211)) != {"F81R_LOWER_POOL"}:
        raise RuntimeError("f81r lower visual owner boundary drifted")

    coverage_overlay_rows = []
    for row in line_rows:
        coverage_overlay_rows.append({
            "page": "f81r", "locus": row["locus"],
            "visual_block": row["visual_block"], "line_mode": row["line_mode"],
            "token_count": row["token_count"],
            "unknown_before": row["raw_unknown_before"],
            "review_positions": row["review_tokens"],
            "unknown_after": 0,
            "newly_complete": row["newly_complete"],
            "working_translation_de": row["working_translation_de"],
        })
    architecture_rows = []
    for block_id, start_line, end_line in (("F81R_UPPER_POOL", 1, 15), ("F81R_LOWER_POOL", 16, 31)):
        members = [row for row in line_rows if start_line <= int(row["line_ordinal"]) <= end_line]
        architecture_rows.append({
            "block_id": block_id, "first_line": f"f81r.{start_line}", "last_line": f"f81r.{end_line}",
            "physical_lines": len(members), "tokens": sum(int(row["token_count"]) for row in members),
            "inherited_action_anchor_lines": sum(row["line_mode"] == "INHERITED_ACTION_ANCHOR" for row in members),
            "lines_without_inherited_action_anchor": sum(row["line_mode"] == "NO_INHERITED_ACTION_ANCHOR" for row in members),
            "review_positions": sum(int(row["review_tokens"]) for row in members),
            "raw_unknown_before": sum(int(row["raw_unknown_before"]) for row in members),
            "newly_complete_lines": sum(int(row["newly_complete"]) for row in members),
            "interpretation": "BIOLOGICAL_PREPARATION_OR_BATCH_REGISTER_BLOCK",
        })
    if [(row["tokens"], row["review_positions"]) for row in architecture_rows] != [(94, 12), (116, 15)]:
        raise RuntimeError("f81r two-block architecture drifted")

    reader_lines = [
        "# GDT674 — f81r concrete V49 working reader",
        "",
        "Exploratory working reading, not confirmed plaintext. Every ZL3b token remains visible. The page is read as a two-block biological preparation/batch register: 15 lines have inherited exact V48 action anchors; 16 do not and remain primarily material/state/quantity records unless a review card supplies a candidate process.",
        "",
        "Coverage: 183 positions inherit V48 unchanged. Twenty-seven positions are reviewed explicitly: 24 former UNKNOWN positions, two line-initial y entry markers and one line-final dy field close. The review layer has 21 composed, 3 learned-whole and 3 occurrence-context positions.",
        "",
        "No vessel, bath, carrier liquid, patient, disease or cure word is supplied because f81r has no such card in the current layer.",
        "",
    ]
    for row in line_rows:
        reader_lines.extend([
            f"## {row['locus']} · {row['visual_block']} · {row['line_mode']}",
            "",
            f"**ZL3b:** `{row['zl3b_line']}`",
            "",
            f"**IT2a:** `{row['it2a_line']}`",
            "",
            f"**RF1b:** `{row['rf1b_line']}`",
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

    new_generic_hits = sum(len(GENERIC_FILLER.findall(row["working_translation_de"])) for row in line_rows)
    new_broad_hits = sum(len(BROAD_CARRIER.findall(row["working_translation_de"])) for row in line_rows)
    g673_overlay = g673_result["coverage_overlay"]
    one_unknown_lines_closed = sum(int(row["raw_unknown_before"]) == 1 for row in line_rows)
    result: dict[str, Any] = {
        "experiment_id": "GDT674",
        "status": STATUS,
        "page": "f81r",
        "basis": {
            "v48_guarded_panel_sides": 179,
            "f81r_already_admitted_in_v48_panel": True,
            "new_page_opened": False,
            "gdt407_and_gdt416_used_as_meaning_input": False,
            "gdt407_and_gdt416_used_as_comparison_baselines": True,
            "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
        },
        "source": {
            "tokens": 210, "physical_lines": 31,
            "section": "B", "language": "B", "hand": "2",
            "cross_reader_lines": 31, "cross_reader_all_exact": 7,
            "token_guard": token_guard, "cross_guard": cross_guard,
            "upper_block_tokens": 94, "lower_block_tokens": 116,
        },
        "coverage": {
            "inherited_v48_positions": 183,
            "inherited_v48_surface_types": 103,
            "review_positions": 27, "review_surface_types": 25,
            "raw_v48_unknown_positions_before": 24,
            "raw_v48_unknown_surface_types_before": 23,
            "composed_review_positions": transfer_class_positions["P"],
            "composed_review_surface_types": sum(row["class"] == "P" for row in transfer_cards),
            "learned_review_positions": transfer_class_positions["W"],
            "learned_review_surface_types": sum(row["class"] == "W" for row in transfer_cards),
            "context_review_positions": len(context_cards),
            "context_review_surface_types": len(context_grouped),
            "unassigned_positions": 0,
            "page_complete_lines_before": 19,
            "page_complete_lines_after": 31,
            "newly_complete_lines": 12,
        },
        "reader": {
            "review_both_exact": reader_profile["BOTH_EXACT"],
            "review_one_exact": reader_profile["ONE_EXACT"],
            "review_neither_exact": reader_profile["NEITHER_EXACT"],
        },
        "architecture": {
            "visual_blocks": 2,
            "inherited_action_positions": len(action_specs),
            "inherited_action_anchor_lines": len(action_lines),
            "lines_without_inherited_action_anchor": 31 - len(action_lines),
            "value_attachments": len(value_specs),
            "working_model": "MIXED_BIOLOGICAL_PHARMACEUTICAL_PREPARATION_AND_BATCH_REGISTER",
        },
        "renderer_comparison": {
            "gdt407_statements": len(statement_rows),
            "gdt407_generic_core_hits": sum(int(row["generic_filler_hits"]) for row in statement_rows),
            "gdt416_token_rows": len(legacy_audit_rows),
            "gdt416_rows_with_generic_station_or_entry": sum(int(row["gdt416_generic_station_or_entry"]) for row in legacy_audit_rows),
            "gdt416_rows_with_inherited_action": sum(int(row["gdt416_inherited_action"]) for row in legacy_audit_rows),
            "gdt416_rows_with_inherited_argument": sum(int(row["gdt416_inherited_argument"]) for row in legacy_audit_rows),
            "gdt674_generic_filler_hits": new_generic_hits,
            "gdt674_broad_carrier_hits": new_broad_hits,
        },
        "global_overlay": {
            "unknown_positions_before": g673_overlay["unknown_positions_after"],
            "unknown_positions_after": g673_overlay["unknown_positions_after"] - 24,
            "complete_lines_before": g673_overlay["complete_lines_after"],
            "complete_lines_after": g673_overlay["complete_lines_after"] + 12,
            "multi_token_complete_before": g673_overlay["multi_token_complete_after"],
            "multi_token_complete_after": g673_overlay["multi_token_complete_after"] + 12,
            "multi_token_one_unknown_before": g673_overlay["multi_token_one_unknown_after"],
            "multi_token_one_unknown_after": g673_overlay["multi_token_one_unknown_after"] - one_unknown_lines_closed,
        },
        "claim_ceiling": (
            "A complete exploratory f81r working reader on the already admitted V48 panel: 183/210 positions "
            "inherit V48 unchanged and 27/210 are explicit review positions. The 24 former unknown positions "
            "receive replaceable page cards; none is silently promoted manuscript-wide. This does not establish "
            "plaintext, language, phonetics, a historical codebook, a plant identity, a disease, a patient, a cure, "
            "a vessel, a carrier liquid, or manuscript-wide meanings."
        ),
    }
    if new_generic_hits != 0:
        raise RuntimeError("new f81r working translations contain generic renderer filler")
    if result["global_overlay"]["unknown_positions_after"] != 7994:
        raise RuntimeError("global V49 overlay count drifted")

    write_text(output_dir / "F81R_SOURCE_ALIGNMENT.tsv", tsv_text(alignment_rows))
    write_text(output_dir / "F81R_TOKEN_READINGS.tsv", tsv_text(token_rows_out))
    write_text(output_dir / "F81R_COMPONENT_TRACES.tsv", tsv_text(component_rows))
    write_text(output_dir / "F81R_REVIEW_CARDS.tsv", tsv_text(review_card_rows))
    write_text(output_dir / "F81R_READER_VARIANT_AUDIT.tsv", tsv_text(reader_rows))
    write_text(output_dir / "F81R_LINE_READER.tsv", tsv_text(line_rows))
    write_text(output_dir / "F81R_EXPLICIT_ACTION_AUDIT.tsv", tsv_text(action_audit_rows))
    write_text(output_dir / "F81R_VALUE_ATTACHMENT_AUDIT.tsv", tsv_text(attachment_rows))
    write_text(output_dir / "F81R_COVERAGE_OVERLAY.tsv", tsv_text(coverage_overlay_rows))
    write_text(output_dir / "F81R_PAGE_ARCHITECTURE.tsv", tsv_text(architecture_rows))
    write_text(output_dir / "LEGACY_TOKEN_RENDERER_AUDIT.tsv", tsv_text(legacy_audit_rows))
    write_text(output_dir / "LEGACY_STATEMENT_BASELINE.tsv", tsv_text(statement_rows))
    write_text(output_dir / "RENDERER_RULE_CARDS.tsv", tsv_text(rule_cards))
    write_text(output_dir / "GDT674_F81R_CONCRETE_WORKING_READER.md", reader)
    write_text(output_dir / "RESULT.json", json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return result


def render_docs(result: dict[str, Any]) -> None:
    coverage = result["coverage"]
    reader = result["reader"]
    comparison = result["renderer_comparison"]
    overlay = result["global_overlay"]
    report = f"""# GDT674 — f81r als konkretes V49-Mischregister

## Ergebnis

f81r ist jetzt auf allen 210 sichtbaren Tokens und allen 31 physischen Zeilen lesbar. 183 Positionen bzw. 103 Oberflächen bleiben unverändert aus V48. Die 27 Review-Positionen bzw. 25 Oberflächen bestehen aus 24 echten V48-Lücken, zwei zeileninitialen `y`-Eintragsmarkern und einem zeilenfinalen `dy`-Feldschluss. Davon sind {coverage['composed_review_positions']} Positionen vollständig aus vorhandenen Rollen zusammengesetzt, {coverage['learned_review_positions']} gelernte Ganzwörter und {coverage['context_review_positions']} occurrence-spezifische Kontextwerte.

Die beste Seitenarchitektur ist kein durchgehender Imperativtext. Der obere Bildblock f81r.1–15 hat 94 Tokens, der untere f81r.16–31 hat 116. Fünfzehn Zeilen besitzen achtzehn bereits in V48 explizit lizenzierte Aktionsanker; sechzehn besitzen keinen solchen geerbten Anker und bleiben primär Stoff-, Zustands- oder Mengenregister, sofern nicht eine neue Review-Komposition einen Prozess vorschlägt. Der Arbeitswortschatz ist konkret: Saatgut, Holz-, Kraut-/Blatt-, Wurzel- und Blütendroge, Pulver und Arzneikomposita; Trocknen, Einweichen, Erhitzen, Kühlen, Abmessen, Zugeben und Abseihen; Grad-, Form-, Portions- und Fraktionswerte.

## Warum dieser Renderer besser ist

GDT416 machte alle 210 Token zu Imperativsätzen. {comparison['gdt416_rows_with_generic_station_or_entry']}/210 Zeilen enthielten generische Stations- oder Eintragsobjekte, {comparison['gdt416_rows_with_inherited_action']} erbten eine nicht sichtbare Aktion und {comparison['gdt416_rows_with_inherited_argument']} ein nicht sichtbares Argument. GDT407s 48 alte f81r-Sätze enthalten {comparison['gdt407_generic_core_hits']} harte Füllworttreffer. Die neue Arbeitslesung enthält {comparison['gdt674_generic_filler_hits']} solche Treffer und erfindet keine Carry-Aktion.

Sie bleibt trotzdem nicht künstlich präzise: {comparison['gdt674_broad_carrier_hits']} breite Träger wie Ansatz, Drogenstoff oder Species sind sichtbar. f81r besitzt derzeit keine Karte für ein bestimmtes Gefäß, Bad, Wasser, Wein, Öl, Salz, Patientin, Krankheit oder Heilung; diese Wörter werden daher nicht aus dem Bildkontext ergänzt.

## Leser- und Abdeckungstest

Von den 27 Review-Positionen sind {reader['review_both_exact']} in IT2a und RF1b positionsgenau identisch, {reader['review_one_exact']} in genau einem Leser und {reader['review_neither_exact']} in keinem. Die drei härtesten Leserstellen bleiben als Rivalen sichtbar. Die 24 echten Lücken schließen zwölf f81r-Zeilen; im globalen Overlay sinkt unbekannt {overlay['unknown_positions_before']}→{overlay['unknown_positions_after']} und vollständig {overlay['complete_lines_before']}→{overlay['complete_lines_after']}.

## Grenze

{result['claim_ceiling']}

## Nächster Hebel

Die zwanzig atomdeckenden Review-Oberflächen werden als Nächstes an allen exakten Vorkommen der übrigen zugelassenen Panel-Seiten geprüft. Die drei Ganzwörter bleiben getrennt, und `y`/`dy` werden nicht globalisiert. Erst danach wird eine weitere bereits freigegebene Seite gerendert.

## Provenienzkorrektur

Ein paralleler Leser öffnete einmal versehentlich die rohe gemischte Cross-Transkriptionsdatei. Der gesamte Output wurde verworfen und speist weder Karte noch Zahl noch Hypothese. Der Builder und Validator materialisieren ausschließlich f81r über den Guard-Wrapper mit verbotenem f84-Präfix.
"""
    method = """# Method

1. Materialize f81r tokens and the three-reader lines only through `./vmanus-exp query-tsv`, with selector `page`, allow-value `f81r`, explicit output columns and forbidden prefix `f84`.
2. Replay all 210 source tokens against the 31 frozen V48 f81r coverage rows. Preserve 183 positions unchanged.
3. Define the 27-position review frontier exactly: 24 V48 `UNKNOWN_SURFACE` positions, line-initial `y` at f81r.17.1 and f81r.29.1, and line-final `dy` at f81r.25.8.
4. Require every `P` card to concatenate byte-exactly from V48 roles. Keep `lshl`, `eses` and `lchl` as explicit learned wholes. Keep `y` and `dy` occurrence-scoped.
5. Align each review position against IT2a and RF1b using GDT671's minimum `(cost, steps)` dynamic program: exact ONE cost 0, substitution cost 10, exact merge/split cost 1, insertion/deletion cost 10.
6. Preserve the two cached visual owners, all physical lines, all tokens and all reader variants. Render only eighteen explicitly listed action positions as action anchors; leave the other sixteen lines nominal.
7. Use ten explicit value-to-head bindings. Add no vessel, liquid, patient, disease or cure term without a card.
8. Compare GDT407/GDT416 only as generic-renderer baselines, never as meaning input. Reject generic filler, replay all source/card/count invariants and require byte-identical fresh rebuilds.
"""
    readme = """# GDT674 — V49 f81r concrete renderer

Start with `artifacts/GDT674_F81R_CONCRETE_WORKING_READER.md` for the complete page. `REPORT.md` summarizes the result and limits; `METHOD.md` gives the executable route. The experiment uses only the already admitted f81r page and keeps f84/f84r forbidden.
"""
    artifact_readme = """# Artifact map

- `GDT674_F81R_CONCRETE_WORKING_READER.md`: complete four-layer, 31-line f81r reader.
- `F81R_TOKEN_READINGS.tsv`: all 210 token values, routes, scope and provenance.
- `F81R_LINE_READER.tsv`: source lines, three readers, literal values and curated readings.
- `F81R_REVIEW_CARDS.tsv`: 25 explicit cards for the 27 review positions.
- `F81R_COMPONENT_TRACES.tsv`: byte-covering component traces for every token.
- `F81R_READER_VARIANT_AUDIT.tsv`: position-specific IT2a/RF1b audit for all review positions.
- `F81R_EXPLICIT_ACTION_AUDIT.tsv`: the eighteen licensed action anchors.
- `F81R_VALUE_ATTACHMENT_AUDIT.tsv`: ten explicit value-to-head attachments.
- `F81R_PAGE_ARCHITECTURE.tsv`: upper/lower blocks and action/nominal line counts.
- `F81R_COVERAGE_OVERLAY.tsv`: all 31 local coverage transitions.
- `LEGACY_TOKEN_RENDERER_AUDIT.tsv`, `LEGACY_STATEMENT_BASELINE.tsv`: comparison-only generic-renderer audit.
- `RENDERER_RULE_CARDS.tsv`: thirteen executable rendering constraints.
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
