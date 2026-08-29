#!/usr/bin/env python3
"""Build GDT627: quality degrees, value-head roles, and the free d measure."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
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
BASE_REL = Path("experiments/yolo/gdt627_value_head_role_atlas")
ART = ROOT / BASE_REL / "artifacts"
G626 = Path("experiments/yolo/gdt626_mobile_operation_lexicon/artifacts")
ALLOWLIST_REL = G626 / "PAGE_ALLOWLIST.tsv"
OCC_REL = G626 / "MINIM_SUFFIX_OCCURRENCES.tsv"
FAMILY_REL = G626 / "MINIM_FAMILY_SUMMARY.tsv"
MIXED_REL = G626 / "MIXED_VALUE_LINES.tsv"
G626_RESULT_REL = G626 / "RESULT.json"
G623_DICT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv")
G624_READER_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PRODUCTIVE_READER.tsv")
HISTORICAL_REL = BASE_REL / "artifacts/HISTORICAL_SYNTAX_COMPARATORS.tsv"
VISUAL_REL = BASE_REL / "artifacts/MANUAL_VISUAL_JUDGMENTS.tsv"

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "roles": BASE_REL / "artifacts/HEAD_ROLE_ATLAS.tsv",
    "axis_occurrences": BASE_REL / "artifacts/QUALITY_AXIS_DEGREE_OCCURRENCES.tsv",
    "axis_matrix": BASE_REL / "artifacts/QUALITY_AXIS_DEGREE_MATRIX.tsv",
    "axis_pairs": BASE_REL / "artifacts/LOCAL_THERMAL_MOISTURE_DEGREE_PAIRS.tsv",
    "fixed_frames": BASE_REL / "artifacts/FIXED_VALUE_FRAMES.tsv",
    "d_frames": BASE_REL / "artifacts/D_VALUE_FIXED_FRAMES.tsv",
    "d_chol": BASE_REL / "artifacts/D_CHOL_TERMINAL_WITNESSES.tsv",
    "d_part": BASE_REL / "artifacts/D_PART_CONTACTS.tsv",
    "d_brackets": BASE_REL / "artifacts/D_PART_BRACKETS.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V4.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_READINGS_V2.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

ROMAN_ORDER = {"I": 1, "II": 2, "III": 3, "IV": 4}
ROMAN = {value: key for key, value in ROMAN_ORDER.items()}
CORE_AXIS_ROOTS = ("k", "t", "ch", "sh", "ok", "ot", "qok", "qot")
EXTENDED_AXIS_ROOTS = {"och", "osh", "qoch", "qosh"}
THERMAL_ROOTS = {"k", "t", "ok", "ot", "qok", "qot"}
MOISTURE_ROOTS = {"ch", "sh", "och", "osh", "qoch", "qosh"}
PART_ROOTS = ("cth", "chor", "shor", "dair", "sair")
PART_TERMS = {"cthy", "chor", "shor", "dair", "sair"}
AXIS_DE = {
    "k": "heiß", "t": "kalt", "ch": "trocken", "sh": "feucht",
    "ok": "heiß im o-Rahmen", "ot": "kalt im o-Rahmen",
    "qok": "heiß im qo-Qualitätsrahmen", "qot": "kalt im qo-Qualitätsrahmen",
    "och": "trocken im o-Rahmen", "osh": "feucht im o-Rahmen",
    "qoch": "trocken im qo-Rahmen", "qosh": "feucht im qo-Rahmen",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "NONE") if row.get(name, "") != "" else "NONE" for name in names})


def position(row: dict[str, str]) -> str:
    index, length = int(row["token_index"]), len(row["surface_line"].split())
    if index == 1:
        return "FIRST"
    if index == length:
        return "LAST"
    return "MIDDLE"


def normalized_mi(rows: list[dict[str, str]], field: str) -> float:
    if not rows:
        return 0.0
    values = [row["working_roman"] for row in rows]
    contexts = [position(row) if field == "position" else row[field] for row in rows]
    value_counts, context_counts = Counter(values), Counter(contexts)
    joint = Counter(zip(values, contexts))
    total = len(rows)
    entropy = -sum(count / total * math.log2(count / total) for count in value_counts.values())
    if entropy == 0:
        return 0.0
    mutual = sum(
        count / total * math.log2(count * total / (value_counts[value] * context_counts[context]))
        for (value, context), count in joint.items()
    )
    return mutual / entropy


def head_role(head: str) -> tuple[str, str]:
    root = head[:-1]
    if root in set(CORE_AXIS_ROOTS) | EXTENDED_AXIS_ROOTS:
        return "QUALITY_AXIS_DEGREE", f"{AXIS_DE[root]}, Grad I-IV"
    quality_match = re.fullmatch(r".*?(?P<thermal>[kt])(?P<moisture>ch|sh)[ed]*", root)
    if quality_match:
        thermal = "heiß" if quality_match.group("thermal") == "k" else "kalt"
        moisture = "trocken" if quality_match.group("moisture") == "ch" else "feucht"
        return "QUALITY_BUNDLE_DEGREE", f"{thermal}-{moisture}, Grad I-IV"
    if any(root.endswith(part) for part in PART_ROOTS):
        return "PLANT_PART_VALUE", "Pflanzenteil, Menge/Dosis/Grad/Klasse I-IV"
    if root == "d":
        return "FREE_MEASURE_OR_DEGREE_HEAD", "freie Maß-/Gradangabe I-IV; nach Pflanzenteil standardmäßig Portion"
    if root == "":
        return "BARE_VALUE", "nackter Wert I-IV"
    return "OPEN_VALUE_HEAD", "Kopfbedeutung offen; Wertslot I-IV als Default"


def immediate_context(row: dict[str, str]) -> tuple[str, str]:
    words, index = row["surface_line"].split(), int(row["token_index"]) - 1
    return (words[index - 1] if index else "<START>", words[index + 1] if index + 1 < len(words) else "<END>")


def make_fixed_frames(occurrences: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, int]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        left, right = immediate_context(row)
        grouped[row["head"], left, right].append(row)
    rows: list[dict[str, object]] = []
    frame_counts: Counter[str] = Counter()
    for (head, left, right), selected in grouped.items():
        values = sorted({row["working_roman"] for row in selected}, key=ROMAN_ORDER.get)
        if len(values) < 2:
            continue
        selected.sort(key=lambda row: (ROMAN_ORDER[row["working_roman"]], row["page"], row["locus"], int(row["token_index"])))
        frame_counts[head] += 1
        by_value: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in selected:
            by_value[row["working_roman"]].append(row)
        rows.append({
            "head": head, "root_before_a": head[:-1] or "BARE", "left_surface": left, "right_surface": right,
            "values": "|".join(values), "distinct_values": len(values), "occurrences": len(selected),
            "all_value_tokens_triple_stable": int(all(int(row["triple_reading_token_stable"]) for row in selected)),
            "surfaces_by_value": ";".join(f"{value}:{','.join(sorted({row['surface'] for row in by_value[value]}))}" for value in values),
            "loci_by_value": ";".join(f"{value}:{','.join(row['locus'] for row in by_value[value])}" for value in values),
            "sections": "|".join(sorted({row["section"] for row in selected})),
            "example_lines": " / ".join(dict.fromkeys(row["surface_line"] for row in selected[:4])),
        })
    rows.sort(key=lambda row: (-int(row["distinct_values"]), str(row["head"]), str(row["left_surface"]), str(row["right_surface"])))
    for index, row in enumerate(rows, 1):
        row["frame_id"] = f"G627-F{index:03d}"
    return rows, dict(frame_counts)


def make_roles(families: list[dict[str, str]], occurrences: list[dict[str, str]], mixed: list[dict[str, str]], frame_counts: dict[str, int]) -> list[dict[str, object]]:
    by_head: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        by_head[row["head"]].append(row)
    mixed_counts = Counter(row["head"] for row in mixed)
    rows: list[dict[str, object]] = []
    for family in families:
        head = family["head"]
        selected = by_head[head]
        role, reading = head_role(head)
        positions = Counter(position(row) for row in selected)
        stable = sum(int(row["triple_reading_token_stable"]) for row in selected)
        rows.append({
            "head": head, "root_before_a": head[:-1] or "BARE", "role": role, "working_role_de": reading,
            "occurrences": len(selected), "pages": len({row["page"] for row in selected}),
            "values": family["present_values"], "distinct_values": family["distinct_values"],
            "count_I": family["count_I"], "count_II": family["count_II"], "count_III": family["count_III"], "count_IV": family["count_IV"],
            "triple_stable_occurrences": stable, "herbal_occurrences": sum(row["section"] == "H" for row in selected),
            "fixed_multi_value_frames": frame_counts.get(head, 0), "mixed_value_lines": mixed_counts[head],
            "line_first": positions["FIRST"], "line_middle": positions["MIDDLE"], "line_last": positions["LAST"],
            "section_value_nmi": f"{normalized_mi(selected, 'section'):.6f}",
            "hand_value_nmi": f"{normalized_mi(selected, 'hand'):.6f}",
            "position_value_nmi": f"{normalized_mi(selected, 'position'):.6f}",
            "default_policy": "COMPOSE" if role != "OPEN_VALUE_HEAD" else "KEEP_HEAD_OPEN__COMPOSE_VALUE_ONLY",
        })
    return rows


def make_axis_occurrences(occurrences: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    allowed = set(CORE_AXIS_ROOTS) | EXTENDED_AXIS_ROOTS
    for occurrence in occurrences:
        root = occurrence["head"][:-1]
        if root not in allowed:
            continue
        rows.append({
            "axis_id": f"G627-A{len(rows) + 1:04d}", "page": occurrence["page"], "locus": occurrence["locus"],
            "token_index": occurrence["token_index"], "surface": occurrence["surface"], "quality_root": root,
            "working_axis_de": AXIS_DE[root], "working_roman": occurrence["working_roman"],
            "working_degree_de": f"{AXIS_DE[root]}, Grad {occurrence['working_roman']}",
            "section": occurrence["section"], "hand": occurrence["hand"],
            "triple_reading_token_stable": occurrence["triple_reading_token_stable"], "surface_line": occurrence["surface_line"],
        })
    return rows


def make_axis_matrix(axis_occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for root in CORE_AXIS_ROOTS:
        for value in range(1, 5):
            selected = [row for row in axis_occurrences if row["quality_root"] == root and ROMAN_ORDER[str(row["working_roman"])] == value]
            rows.append({
                "quality_root": root, "working_axis_de": AXIS_DE[root], "working_value": value, "working_roman": ROMAN[value],
                "predicted_surface": root + "a" + "i" * (value - 1) + "n", "occurrences": len(selected),
                "pages": len({str(row["page"]) for row in selected}),
                "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
                "occupied": int(bool(selected)), "working_reading_de": f"{AXIS_DE[root]}, Grad {ROMAN[value]}",
            })
    return rows


def make_axis_pairs(axis_occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    by_line: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in axis_occurrences:
        by_line[str(row["locus"])].append(row)
    rows: list[dict[str, object]] = []
    for locus, line in by_line.items():
        for thermal in line:
            if thermal["quality_root"] not in THERMAL_ROOTS:
                continue
            for moisture in line:
                if moisture["quality_root"] not in MOISTURE_ROOTS:
                    continue
                distance = abs(int(thermal["token_index"]) - int(moisture["token_index"]))
                if not 1 <= distance <= 3:
                    continue
                order = "THERMAL_THEN_MOISTURE" if int(thermal["token_index"]) < int(moisture["token_index"]) else "MOISTURE_THEN_THERMAL"
                rows.append({
                    "pair_id": f"G627-P{len(rows) + 1:03d}", "page": thermal["page"], "locus": locus,
                    "thermal_surface": thermal["surface"], "thermal_axis_de": thermal["working_axis_de"], "thermal_roman": thermal["working_roman"],
                    "moisture_surface": moisture["surface"], "moisture_axis_de": moisture["working_axis_de"], "moisture_roman": moisture["working_roman"],
                    "token_distance": distance, "order": order, "same_degree": int(thermal["working_roman"] == moisture["working_roman"]),
                    "both_triple_token_stable": int(int(thermal["triple_reading_token_stable"]) and int(moisture["triple_reading_token_stable"])),
                    "working_pair_de": f"{thermal['working_axis_de']} Grad {thermal['working_roman']}; {moisture['working_axis_de']} Grad {moisture['working_roman']}",
                    "surface_line": thermal["surface_line"],
                })
    rows.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["token_distance"]), str(row["thermal_surface"]), str(row["moisture_surface"])))
    for index, row in enumerate(rows, 1):
        row["pair_id"] = f"G627-P{index:03d}"
    return rows


def make_d_chol(occurrences: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        if occurrence["head"] != "da":
            continue
        left, right = immediate_context(occurrence)
        if left != "chol" or right != "<END>":
            continue
        rows.append({
            "witness_id": f"G627-C{len(rows) + 1:02d}", "page": occurrence["page"], "locus": occurrence["locus"],
            "surface": occurrence["surface"], "working_roman": occurrence["working_roman"],
            "working_reading_de": f"nach chol: Maß-/Portionswert {occurrence['working_roman']} am Zeilenende",
            "section": occurrence["section"], "hand": occurrence["hand"],
            "triple_reading_token_stable": occurrence["triple_reading_token_stable"], "surface_line": occurrence["surface_line"],
        })
    rows.sort(key=lambda row: (ROMAN_ORDER[str(row["working_roman"])], str(row["page"]), str(row["locus"])))
    for index, row in enumerate(rows, 1):
        row["witness_id"] = f"G627-C{index:02d}"
    return rows


def make_d_part_contacts(occurrences: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        if occurrence["head"] != "da":
            continue
        left, right = immediate_context(occurrence)
        if left not in PART_TERMS and right not in PART_TERMS:
            continue
        if left in PART_TERMS and right in PART_TERMS:
            direction = "PART_D_PART"
            local = f"{left}; Portion/Maß {occurrence['working_roman']}; {right}"
        elif left in PART_TERMS:
            direction = "PART_THEN_D"
            local = f"{left}, Portion/Maß {occurrence['working_roman']}"
        else:
            direction = "D_THEN_PART"
            local = f"Portion/Maß {occurrence['working_roman']}; {right}"
        rows.append({
            "contact_id": f"G627-D{len(rows) + 1:03d}", "page": occurrence["page"], "locus": occurrence["locus"],
            "d_surface": occurrence["surface"], "working_roman": occurrence["working_roman"],
            "left_surface": left, "right_surface": right, "direction": direction,
            "working_local_de": local, "d_token_triple_stable": occurrence["triple_reading_token_stable"],
            "surface_line": occurrence["surface_line"],
        })
    return rows


def make_d_brackets(occurrences: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        if occurrence["head"] != "da":
            continue
        words, index = occurrence["surface_line"].split(), int(occurrence["token_index"]) - 1
        left = next(((pos, words[pos]) for pos in range(index - 1, max(-1, index - 9), -1) if words[pos] in PART_TERMS), None)
        right = next(((pos, words[pos]) for pos in range(index + 1, min(len(words), index + 9)) if words[pos] in PART_TERMS), None)
        if left is None or right is None or right[0] - left[0] > 8:
            continue
        rows.append({
            "bracket_id": f"G627-B{len(rows) + 1:02d}", "page": occurrence["page"], "locus": occurrence["locus"],
            "left_part": left[1], "d_surface": occurrence["surface"], "working_roman": occurrence["working_roman"],
            "right_part": right[1], "part_span": right[0] - left[0],
            "distance_left_to_d": index - left[0], "distance_d_to_right": right[0] - index,
            "working_local_de": f"{left[1]}, Portion/Maß {occurrence['working_roman']}; {right[1]}",
            "d_token_triple_stable": occurrence["triple_reading_token_stable"], "surface_line": occurrence["surface_line"],
        })
    return rows


def make_dictionary() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {"entry": "a", "kind": "VALUE_SLOT_LINKER", "working_meaning_de": "öffnet nach einem Kopf eine Grad-/Maßstelle; in Übersetzung meist Doppelpunkt oder null", "composition": "KOPF+a+(n|in|iin|iiin)", "scope": "produktiv", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "n/in/iin/iiin", "kind": "VALUE_MINIMS", "working_meaning_de": "I/II/III/IV", "composition": "terminaler Schlussstrich mit 0/1/2/3 inneren i-Minims", "scope": "nach a", "status": "INHERITED_PRIMARY_DEFAULT"},
        {"entry": "d", "kind": "FREE_VALUE_HEAD", "working_meaning_de": "freie Maß-/Gradangabe; nach Stoff oder Pflanzenteil standardmäßig Portion/Menge", "composition": "d+a+Wert", "scope": "alle Register; linksbindend als lokaler Default", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "dan/dain/daiin/daiiin", "kind": "FREE_MEASURE_SERIES", "working_meaning_de": "Maß-/Portionswert I/II/III/IV", "composition": "d+a+I/II/III/IV", "scope": "nach Teil/Stoff: eine/zwei/drei/vier Portionen als Arbeitslesung", "status": "NEW_COMPOSITIONAL_DEFAULT"},
    ]
    for root in CORE_AXIS_ROOTS:
        surfaces = "/".join(root + "a" + "i" * (value - 1) + "n" for value in range(1, 5))
        rows.append({
            "entry": surfaces, "kind": "QUALITY_DEGREE_SERIES", "working_meaning_de": f"{AXIS_DE[root]}, Grad I/II/III/IV",
            "composition": f"{root}+a+I/II/III/IV", "scope": "Qualitätscode", "status": "NEW_PRIMARY_DEFAULT",
        })
    rows.extend([
        {"entry": "cthan/cthain/cthaiin", "kind": "PART_VALUE_SERIES", "working_meaning_de": "Blatt-/oberirdisches Drogengut, Menge/Grad/Klasse I/II/III", "composition": "cth+a+Wert", "scope": "Herbal", "status": "INHERITED_WITH_VALUE_READER"},
        {"entry": "chorain/choraiin", "kind": "PART_VALUE_SERIES", "working_meaning_de": "Blüten-/Pflanzenteil, Menge/Grad/Klasse II/III", "composition": "chor+a+Wert", "scope": "vor allem Herbal", "status": "INHERITED_WITH_VALUE_READER"},
        {"entry": "daiin", "kind": "FREE_MEASURE_FORM", "working_meaning_de": "Maß-/Portionswert III; nach Pflanzenteil Arbeitsdefault drei Portionen", "composition": "d+a+III", "scope": "nicht und/item/Operation", "status": "REVISED_CONCRETE_DEFAULT"},
    ])
    return rows


def make_cases(axis_pairs: list[dict[str, object]], d_chol: list[dict[str, object]], d_part: list[dict[str, object]]) -> list[dict[str, object]]:
    pair_by_locus = defaultdict(list)
    for row in axis_pairs:
        pair_by_locus[str(row["locus"])].append(row)
    d_chol_by = {(str(row["locus"]), str(row["surface"])): row for row in d_chol}
    d_part_by = defaultdict(list)
    for row in d_part:
        d_part_by[str(row["locus"])].append(row)
    return [
        {"case_id": "HOT_DRY_I", "page": "f111v", "locus": "f111v.33", "surface": "qokan chan", "segmentation": "qok+a+I | ch+a+I", "working_reading_de": "heiß ersten Grades; trocken ersten Grades", "reading_type": "PAIRED_QUALITY_DEGREES", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "HOT_DRY_II", "page": "f107v", "locus": "f107v.7", "surface": "chain qokain", "segmentation": "ch+a+II | qok+a+II", "working_reading_de": "trocken zweiten Grades; heiß zweiten Grades", "reading_type": "PAIRED_QUALITY_DEGREES", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "HOT_MOIST_III", "page": "f106r", "locus": "f106r.20", "surface": "qokaiin shaiin", "segmentation": "qok+a+III | sh+a+III", "working_reading_de": "heiß dritten Grades; feucht dritten Grades", "reading_type": "PAIRED_QUALITY_DEGREES", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "HOT_DRY_III", "page": "f112v", "locus": "f112v.39", "surface": "okaiin chaiin", "segmentation": "ok+a+III | ch+a+III", "working_reading_de": "im o-Rahmen heiß dritten Grades; trocken dritten Grades", "reading_type": "PAIRED_QUALITY_DEGREES", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "D_I_TERMINAL", "page": "f2r", "locus": "f2r.7", "surface": d_chol_by["f2r.7", "dan"]["surface_line"], "segmentation": "... chol | d+a+I", "working_reading_de": "... chol; eine Portion/ein Maß", "reading_type": "FIXED_D_MEASURE_FRAME", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "D_II_TERMINAL", "page": "f47v", "locus": "f47v.9", "surface": d_chol_by["f47v.9", "dain"]["surface_line"], "segmentation": "... chol | d+a+II", "working_reading_de": "... chol; zwei Portionen/zwei Maße", "reading_type": "FIXED_D_MEASURE_FRAME", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "D_III_TERMINAL", "page": "f37v", "locus": "f37v.23", "surface": d_chol_by["f37v.23", "daiin"]["surface_line"], "segmentation": "... chol | d+a+III", "working_reading_de": "... chol; drei Portionen/drei Maße", "reading_type": "FIXED_D_MEASURE_FRAME", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "D_IV_TERMINAL", "page": "f17r", "locus": "f17r.11", "surface": d_chol_by["f17r.11", "daiiin"]["surface_line"], "segmentation": "... chol | d+a+IV", "working_reading_de": "... chol; vier Portionen/vier Maße", "reading_type": "FIXED_D_MEASURE_FRAME", "status": "PRIMARY_WORKING_READING"},
        {"case_id": "F45_PART_DOSE", "page": "f45v", "locus": "f45v.2", "surface": d_part_by["f45v.2"][0]["surface_line"], "segmentation": "chor | d+a+III | cthy", "working_reading_de": "Blüten-/Pflanzenteil, drei Portionen/Maße; Blattgut", "reading_type": "PART_MEASURE_NEXT_PART", "status": "PRIMARY_LOCAL_DEFAULT__UNIT_OPEN"},
        {"case_id": "F18_PART_VALUE", "page": "f18r", "locus": "f18r.5", "surface": "tchor shor cthaiin cthol chlol chom", "segmentation": "tchor | shor | cth+a+III | cthol ...", "working_reading_de": "Blüten-/Fruchtstand; Blatt-/Oberirdischgut, Wert III; weitere Teilformen", "reading_type": "PART_VALUE_SERIES", "status": "PRIMARY_LOCAL_DEFAULT__UNIT_OPEN"},
    ]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    allowlist = read_tsv(ROOT / ALLOWLIST_REL)
    occurrences = read_tsv(ROOT / OCC_REL)
    families = read_tsv(ROOT / FAMILY_REL)
    mixed = read_tsv(ROOT / MIXED_REL)
    if len(allowlist) != 179 or "f1r" in {row["page"] for row in allowlist} or any(row["page"].startswith("f84") for row in allowlist):
        raise RuntimeError("unsafe inherited allow-list")
    if len(occurrences) != 5176 or any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences):
        raise RuntimeError("unsafe or incomplete occurrence atlas")

    fixed_frames, frame_counts = make_fixed_frames(occurrences)
    roles = make_roles(families, occurrences, mixed, frame_counts)
    axis_occurrences = make_axis_occurrences(occurrences)
    axis_matrix = make_axis_matrix(axis_occurrences)
    axis_pairs = make_axis_pairs(axis_occurrences)
    d_frames = [row for row in fixed_frames if row["head"] == "da"]
    d_chol = make_d_chol(occurrences)
    d_part = make_d_part_contacts(occurrences)
    d_brackets = make_d_brackets(occurrences)
    dictionary = make_dictionary()
    cases = make_cases(axis_pairs, d_chol, d_part)

    write_tsv(ROOT / OUTPUTS["allowlist"], allowlist, ("page",))
    write_tsv(ROOT / OUTPUTS["roles"], roles, ("head", "root_before_a", "role", "working_role_de", "occurrences", "pages", "values", "distinct_values", "count_I", "count_II", "count_III", "count_IV", "triple_stable_occurrences", "herbal_occurrences", "fixed_multi_value_frames", "mixed_value_lines", "line_first", "line_middle", "line_last", "section_value_nmi", "hand_value_nmi", "position_value_nmi", "default_policy"))
    write_tsv(ROOT / OUTPUTS["axis_occurrences"], axis_occurrences, ("axis_id", "page", "locus", "token_index", "surface", "quality_root", "working_axis_de", "working_roman", "working_degree_de", "section", "hand", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["axis_matrix"], axis_matrix, ("quality_root", "working_axis_de", "working_value", "working_roman", "predicted_surface", "occurrences", "pages", "triple_stable_occurrences", "occupied", "working_reading_de"))
    write_tsv(ROOT / OUTPUTS["axis_pairs"], axis_pairs, ("pair_id", "page", "locus", "thermal_surface", "thermal_axis_de", "thermal_roman", "moisture_surface", "moisture_axis_de", "moisture_roman", "token_distance", "order", "same_degree", "both_triple_token_stable", "working_pair_de", "surface_line"))
    write_tsv(ROOT / OUTPUTS["fixed_frames"], fixed_frames, ("frame_id", "head", "root_before_a", "left_surface", "right_surface", "values", "distinct_values", "occurrences", "all_value_tokens_triple_stable", "surfaces_by_value", "loci_by_value", "sections", "example_lines"))
    write_tsv(ROOT / OUTPUTS["d_frames"], d_frames, ("frame_id", "head", "root_before_a", "left_surface", "right_surface", "values", "distinct_values", "occurrences", "all_value_tokens_triple_stable", "surfaces_by_value", "loci_by_value", "sections", "example_lines"))
    write_tsv(ROOT / OUTPUTS["d_chol"], d_chol, ("witness_id", "page", "locus", "surface", "working_roman", "working_reading_de", "section", "hand", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["d_part"], d_part, ("contact_id", "page", "locus", "d_surface", "working_roman", "left_surface", "right_surface", "direction", "working_local_de", "d_token_triple_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["d_brackets"], d_brackets, ("bracket_id", "page", "locus", "left_part", "d_surface", "working_roman", "right_part", "part_span", "distance_left_to_d", "distance_d_to_right", "working_local_de", "d_token_triple_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "scope", "status"))
    write_tsv(ROOT / OUTPUTS["cases"], cases, ("case_id", "page", "locus", "surface", "segmentation", "working_reading_de", "reading_type", "status"))

    role_counts = Counter(row["role"] for row in roles)
    role_occurrences = Counter()
    for row in roles:
        role_occurrences[str(row["role"])] += int(row["occurrences"])
    d_role = next(row for row in roles if row["head"] == "da")
    historical, visual = read_tsv(ROOT / HISTORICAL_REL), read_tsv(ROOT / VISUAL_REL)
    result = {
        "schema": "GDT627_VALUE_HEAD_ROLE_ATLAS_RESULT_V1", "experiment_id": "GDT627",
        "status": "QUALITY_DEGREE_SERIES_PROMOTED__D_FREE_MEASURE_HEAD_PROMOTED__A_VALUE_LINKER",
        "claim_boundary": "The inherited hot/cold/dry/moist primitives each realize all four minim values, and their scoped forms occupy 31 of 32 core cells. This promotes a as a value-slot linker and I-IV as degree defaults on quality heads. The d head is the only head observed with all four values in one identical left/right frame; in part lists it defaults to a free measure or portion head, binding left. Its absolute unit remains unknown, and grammatical or table-index uses remain possible outside part contexts.",
        "guard": {"f1r": "EXCLUDED_IN_INHERITED_ATLAS", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "safe_pages": len(allowlist), "safe_occurrences": len(occurrences), "new_source_queries": 0, "new_image_pages": 0},
        "head_roles": {"heads": len(roles), "role_head_counts": dict(sorted(role_counts.items())), "role_occurrence_counts": dict(sorted(role_occurrences.items())), "composed_or_bare_value_occurrences": sum(role_occurrences[role] for role in ("QUALITY_AXIS_DEGREE", "QUALITY_BUNDLE_DEGREE", "PLANT_PART_VALUE", "FREE_MEASURE_OR_DEGREE_HEAD", "BARE_VALUE"))},
        "quality_axis_degrees": {"occurrences": len(axis_occurrences), "surfaces": len({str(row["surface"]) for row in axis_occurrences}), "pages": len({str(row["page"]) for row in axis_occurrences}), "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in axis_occurrences), "core_matrix_cells": len(axis_matrix), "occupied_core_cells": sum(int(row["occupied"]) for row in axis_matrix), "primitive_cells": sum(int(row["occupied"]) for row in axis_matrix if row["quality_root"] in {"k", "t", "ch", "sh"}), "local_thermal_moisture_pairs": len(axis_pairs), "adjacent_pairs": sum(int(row["token_distance"]) == 1 for row in axis_pairs), "same_degree_pairs": sum(int(row["same_degree"]) for row in axis_pairs), "adjacent_same_degree_pairs": sum(int(row["token_distance"]) == 1 and int(row["same_degree"]) for row in axis_pairs), "stable_pairs": sum(int(row["both_triple_token_stable"]) for row in axis_pairs)},
        "fixed_value_frames": {"frames": len(fixed_frames), "heads": len({str(row["head"]) for row in fixed_frames}), "all_stable_frames": sum(int(row["all_value_tokens_triple_stable"]) for row in fixed_frames), "four_value_frames": sum(int(row["distinct_values"]) == 4 for row in fixed_frames), "d_frames": len(d_frames)},
        "d_free_measure": {"occurrences": int(d_role["occurrences"]), "pages": int(d_role["pages"]), "mixed_value_lines": int(d_role["mixed_value_lines"]), "fixed_multi_value_frames": int(d_role["fixed_multi_value_frames"]), "section_value_nmi": float(d_role["section_value_nmi"]), "hand_value_nmi": float(d_role["hand_value_nmi"]), "position_value_nmi": float(d_role["position_value_nmi"]), "chol_terminal_witnesses": len(d_chol), "chol_terminal_values": sorted({str(row["working_roman"]) for row in d_chol}, key=ROMAN_ORDER.get), "part_contacts": len(d_part), "part_brackets": len(d_brackets), "working_default": "d=freie Maß-/Gradangabe; nach Teil/Stoff Portion; dan/dain/daiin/daiiin=I/II/III/IV"},
        "working_lexicon_updates": {"a": "Grad-/Maßstellen-Binder; meist Doppelpunkt oder null", "kan_kain_kaiin_kaiiin": "heiß Grad I/II/III/IV", "tan_tain_taiin_taiiin": "kalt Grad I/II/III/IV", "chan_chain_chaiin_chaiiin": "trocken Grad I/II/III/IV", "shan_shain_shaiin_shaiiin": "feucht Grad I/II/III/IV", "d": "freie Maß-/Gradangabe; nach Pflanzenteil Portion/Menge", "daiin": "Maß-/Portionswert III; im Part-Kontext drei Portionen als Default"},
        "manual_sources": {"historical_syntax_comparators": len(historical), "visual_judgments": len(visual), "concrete_readings": len(cases)},
        "inputs": {str(path): sha256(ROOT / path) for path in (ALLOWLIST_REL, OCC_REL, FAMILY_REL, MIXED_REL, G626_RESULT_REL, G623_DICT_REL, G624_READER_REL, HISTORICAL_REL, VISUAL_REL)},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GDT627 built: heads={len(roles)} axis={len(axis_occurrences)} matrix={sum(int(row['occupied']) for row in axis_matrix)}/32 pairs={len(axis_pairs)} fixed={len(fixed_frames)} dframes={len(d_frames)} dpart={len(d_part)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
