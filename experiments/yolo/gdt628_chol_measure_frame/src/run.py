#!/usr/bin/env python3
"""Build GDT628: the OL quality carrier and contextual d-value readings."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
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
BASE_REL = Path("experiments/yolo/gdt628_chol_measure_frame")
ART = ROOT / BASE_REL / "artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
G627 = Path("experiments/yolo/gdt627_value_head_role_atlas/artifacts")
ALLOWLIST_REL = G627 / "PAGE_ALLOWLIST.tsv"
G627_RESULT_REL = G627 / "RESULT.json"
G627_DICT_REL = G627 / "WORKING_DICTIONARY_V4.tsv"
G627_AXIS_REL = G627 / "QUALITY_AXIS_DEGREE_OCCURRENCES.tsv"
G627_HISTORICAL_REL = G627 / "HISTORICAL_SYNTAX_COMPARATORS.tsv"
G627_VISUAL_REL = G627 / "MANUAL_VISUAL_JUDGMENTS.tsv"
G623_DICT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv")
G624_READER_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PRODUCTIVE_READER.tsv")
G625_CTH_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/CTH_ROOT_FAMILY.tsv")

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "matrix": BASE_REL / "artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv",
    "occurrences": BASE_REL / "artifacts/OL_OR_CARRIER_OCCURRENCES.tsv",
    "contrasts": BASE_REL / "artifacts/LOCAL_CARRIER_CONTRASTS.tsv",
    "contrast_summary": BASE_REL / "artifacts/LOCAL_CARRIER_CONTRAST_SUMMARY.tsv",
    "chol": BASE_REL / "artifacts/CHOL_OCCURRENCES.tsv",
    "extensions": BASE_REL / "artifacts/CHOL_EXTENSION_PROFILE.tsv",
    "value_grid": BASE_REL / "artifacts/VALUE_REALIZATION_PATHS.tsv",
    "value_summary": BASE_REL / "artifacts/VALUE_REALIZATION_SUMMARY.tsv",
    "chol_values": BASE_REL / "artifacts/CHOL_VALUE_REALIZATIONS.tsv",
    "terminal": BASE_REL / "artifacts/CHOL_D_TERMINAL_WITNESSES.tsv",
    "ol_phrases": BASE_REL / "artifacts/OL_QUALITY_D_VALUE_PHRASES.tsv",
    "or_phrases": BASE_REL / "artifacts/OR_CARRIER_D_VALUE_PHRASES.tsv",
    "ranking": BASE_REL / "artifacts/CHOL_ROLE_RANKING.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V5.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_READINGS_V3.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

WRAPPERS = ("", "o", "qo")
CORES = ("", "k", "t", "ch", "sh", "kch", "ksh", "tch", "tsh")
ENDINGS = ("ol", "or")
CORE_DE = {
    "": "Kern offen",
    "k": "heiß",
    "t": "kalt",
    "ch": "trocken",
    "sh": "feucht",
    "kch": "heiß-trocken",
    "ksh": "heiß-feucht",
    "tch": "kalt-trocken",
    "tsh": "kalt-feucht",
}
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}
ROMAN_ORDER = {roman: value for value, roman in ROMAN.items()}
VALUE_TAIL = {value: "a" + "i" * (value - 1) + "n" for value in ROMAN}
D_VALUE = {value: "d" + VALUE_TAIL[value] for value in ROMAN}
PART_TERMS = {"cthy", "cthar", "chor", "shor", "dair", "sair"}
LATTICE_PARSE = {
    wrapper + core + ending: (wrapper, core, ending)
    for wrapper in WRAPPERS
    for core in CORES
    for ending in ENDINGS
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


def guarded_query(relative_path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(relative_path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guard statistics missing")
    stats = {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"] == "f1r" or row["page"].startswith("f84") for row in rows):
        raise RuntimeError("forbidden page materialized")
    return rows, stats


def line_number(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    if match is None:
        raise ValueError(locus)
    return int(match.group(1))


def token_sort_key(row: dict[str, object]) -> tuple[str, int, int]:
    return str(row["page"]), line_number(str(row["locus"])), int(row["token_index"])


def stable_capacities(cross_rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    stable: dict[str, Counter[str]] = {}
    for row in cross_rows:
        readings = [Counter(row[field].split()) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        universe = set().union(*(reading.keys() for reading in readings))
        stable[row["locus"]] = Counter({
            word: min(reading[word] for reading in readings)
            for word in universe
            if min(reading[word] for reading in readings) > 0
        })
    return stable


def stable_pair_capacities(cross_rows: list[dict[str, str]]) -> dict[str, Counter[tuple[str, str]]]:
    stable: dict[str, Counter[tuple[str, str]]] = {}
    for row in cross_rows:
        readings = []
        for field in ("zl3b_clean", "it2a_clean", "rf1b_clean"):
            words = row[field].split()
            readings.append(Counter(zip(words, words[1:])))
        universe = set().union(*(reading.keys() for reading in readings))
        stable[row["locus"]] = Counter({
            pair: min(reading[pair] for reading in readings)
            for pair in universe
            if min(reading[pair] for reading in readings) > 0
        })
    return stable


def annotate_stability(tokens: list[dict[str, str]], capacities: dict[str, Counter[str]]) -> list[dict[str, object]]:
    ordinals: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, object]] = []
    for source in sorted(tokens, key=token_sort_key):
        row: dict[str, object] = dict(source)
        key = source["locus"], source["eva"]
        ordinals[key] += 1
        row["triple_reading_token_stable"] = int(ordinals[key] <= capacities.get(source["locus"], Counter())[source["eva"]])
        rows.append(row)
    return rows


def line_maps(tokens: list[dict[str, object]]) -> tuple[dict[str, list[dict[str, object]]], dict[str, str]]:
    by_line: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        by_line[str(row["locus"])].append(row)
    for rows in by_line.values():
        rows.sort(key=lambda row: int(row["token_index"]))
    return by_line, {locus: " ".join(str(row["eva"]) for row in rows) for locus, rows in by_line.items()}


def annotate_pair_stability(
    by_line: dict[str, list[dict[str, object]]],
    capacities: dict[str, Counter[tuple[str, str]]],
) -> None:
    for locus, line in by_line.items():
        ordinals: Counter[tuple[str, str]] = Counter()
        for left, right in zip(line, line[1:]):
            pair = str(left["eva"]), str(right["eva"])
            ordinals[pair] += 1
            left["right_pair_triple_stable"] = int(ordinals[pair] <= capacities.get(locus, Counter())[pair])
        if line:
            line[-1]["right_pair_triple_stable"] = 0


def wrapper_de(wrapper: str) -> str:
    return {"": "unmarkiert", "o": "im o-Rahmen", "qo": "im qo-Qualitätsrahmen"}[wrapper]


def quality_reading(wrapper: str, core: str) -> str:
    if not core:
        return "Qualitäts-/Zustands-/Materialträger; lexikalischer Kern offen"
    return f"{wrapper_de(wrapper)}: {CORE_DE[core]}"


def carrier_role(surface: str, core: str, ending: str) -> tuple[str, str]:
    if not core and ending == "ol":
        return "BASE_CARRIER", "Eigenschafts-/Zustands-/Materialträger; genaue Wortbedeutung offen"
    if not core:
        return "BASE_NOMINAL_PART_CARRIER", "Teil-/Nominalträger; genaue Wortbedeutung offen"
    if ending == "ol":
        return "QUALITY_STATE_CARRIER", f"{CORE_DE[core]}e Zustands-/Materialform; flüssig meist {CORE_DE[core]}"
    if surface == "chor":
        return "PART_TERM__QUALITY_RIVAL", "Pflanzen-/Reproduktionsteil; ch-Qualitätskomposition bleibt Nebenlesung"
    if surface == "shor":
        return "PART_TERM__QUALITY_RIVAL", "Blüten-/Fruchtstand; sh-Qualitätskomposition bleibt Nebenlesung"
    return "OR_NOMINAL_OR_PART_CARRIER", f"or-Träger mit {CORE_DE[core]}-Kern; Teil-/Nominalform gegen Qualitätsallomorph offen"


def make_matrix(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        by_surface[str(row["eva"])].append(row)
    rows: list[dict[str, object]] = []
    for wrapper in WRAPPERS:
        for core in CORES:
            for ending in ENDINGS:
                surface = wrapper + core + ending
                selected = by_surface[surface]
                role, meaning = carrier_role(surface, core, ending)
                rows.append({
                    "wrapper": wrapper or "BARE", "quality_core": core or "NONE", "ending": ending.upper(),
                    "surface": surface, "composition": f"{wrapper or 'BARE'}+{core or 'NONE'}+{ending}",
                    "role": role, "working_meaning_de": meaning, "occurrences": len(selected),
                    "pages": len({str(row["page"]) for row in selected}),
                    "loci": len({str(row["locus"]) for row in selected}),
                    "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
                    "occupied": int(bool(selected)),
                })
    return rows


def make_carrier_occurrences(tokens: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for token in tokens:
        surface = str(token["eva"])
        if surface not in LATTICE_PARSE:
            continue
        wrapper, core, ending = LATTICE_PARSE[surface]
        line = by_line[str(token["locus"])]
        index = int(token["token_index"]) - 1
        role, meaning = carrier_role(surface, core, ending)
        rows.append({
            "occurrence_id": "", "page": token["page"], "locus": token["locus"], "token_index": token["token_index"],
            "surface": surface, "wrapper": wrapper or "BARE", "quality_core": core or "NONE", "ending": ending.upper(),
            "role": role, "working_meaning_de": meaning,
            "left_surface": line[index - 1]["eva"] if index else "<START>",
            "right_surface": line[index + 1]["eva"] if index + 1 < len(line) else "<END>",
            "position": "FIRST" if index == 0 else "LAST" if index + 1 == len(line) else "MIDDLE",
            "section": token["section"], "hand": token["hand"],
            "triple_reading_token_stable": token["triple_reading_token_stable"], "surface_line": line_text[str(token["locus"])],
        })
    rows.sort(key=token_sort_key)
    for index, row in enumerate(rows, 1):
        row["occurrence_id"] = f"G628-O{index:04d}"
    return rows


def contrast_specs() -> list[tuple[str, str, str]]:
    specs: list[tuple[str, str, str]] = []
    for wrapper in WRAPPERS:
        for core in CORES:
            specs.append(("ENDING_OL_OR", wrapper + core + "ol", wrapper + core + "or"))
    thermal = (("k", "t"), ("kch", "tch"), ("ksh", "tsh"))
    moisture = (("ch", "sh"), ("kch", "ksh"), ("tch", "tsh"))
    for wrapper in WRAPPERS:
        for ending in ENDINGS:
            for left, right in thermal:
                specs.append(("THERMAL_K_T", wrapper + left + ending, wrapper + right + ending))
            for left, right in moisture:
                specs.append(("MOISTURE_CH_SH", wrapper + left + ending, wrapper + right + ending))
    for core in CORES:
        for ending in ENDINGS:
            specs.extend((
                ("WRAPPER_BARE_O", core + ending, "o" + core + ending),
                ("WRAPPER_O_QO", "o" + core + ending, "qo" + core + ending),
                ("WRAPPER_BARE_QO", core + ending, "qo" + core + ending),
            ))
    return specs


def make_contrasts(by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for locus, line in by_line.items():
        surfaces = {str(row["eva"]) for row in line}
        positions: dict[str, list[dict[str, object]]] = defaultdict(list)
        stable = defaultdict(int)
        for row in line:
            surface = str(row["eva"])
            positions[surface].append(row)
            stable[surface] += int(row["triple_reading_token_stable"])
        for kind, left, right in contrast_specs():
            if left not in surfaces or right not in surfaces:
                continue
            pairs = [(a, b) for a in positions[left] for b in positions[right]]
            minimum_distance = min(abs(int(a["token_index"]) - int(b["token_index"])) for a, b in pairs)
            stable_adjacent = any(
                abs(int(a["token_index"]) - int(b["token_index"])) == 1
                and int(a["right_pair_triple_stable"] if int(a["token_index"]) < int(b["token_index"]) else b["right_pair_triple_stable"])
                for a, b in pairs
            )
            rows.append({
                "contrast_id": "", "page": line[0]["page"], "locus": locus, "contrast_type": kind,
                "left_surface": left, "right_surface": right,
                "minimum_token_distance": minimum_distance, "adjacent": int(minimum_distance == 1),
                "both_have_stable_token": int(stable[left] > 0 and stable[right] > 0),
                "both_have_adjacent_stable_tokens": int(stable_adjacent),
                "section": line[0]["section"], "surface_line": line_text[locus],
            })
    rows.sort(key=lambda row: (str(row["contrast_type"]), str(row["page"]), str(row["locus"]), str(row["left_surface"]), str(row["right_surface"])))
    for index, row in enumerate(rows, 1):
        row["contrast_id"] = f"G628-C{index:04d}"
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["contrast_type"]), str(row["left_surface"]), str(row["right_surface"])].append(row)
    summary = [{
        "contrast_type": key[0], "left_surface": key[1], "right_surface": key[2],
        "lines": len(selected), "pages": len({str(row["page"]) for row in selected}),
        "stable_lines": sum(int(row["both_have_stable_token"]) for row in selected),
        "adjacent_lines": sum(int(row["adjacent"]) for row in selected),
        "stable_adjacent_lines": sum(int(row["both_have_adjacent_stable_tokens"]) for row in selected),
        "example_loci": "|".join(str(row["locus"]) for row in selected[:8]),
    } for key, selected in grouped.items()]
    summary.sort(key=lambda row: (str(row["contrast_type"]), -int(row["lines"]), str(row["left_surface"])))
    return rows, summary


def make_chol(tokens: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for token in tokens:
        if token["eva"] != "chol":
            continue
        line, index = by_line[str(token["locus"])], int(token["token_index"]) - 1
        rows.append({
            "chol_id": "", "page": token["page"], "locus": token["locus"], "token_index": token["token_index"],
            "surface": "chol", "composition": "ch+ol", "working_meaning_de": "trocken; nominal trockenes Gut/Material",
            "left_surface": line[index - 1]["eva"] if index else "<START>",
            "right_surface": line[index + 1]["eva"] if index + 1 < len(line) else "<END>",
            "position": "FIRST" if index == 0 else "LAST" if index + 1 == len(line) else "MIDDLE",
            "section": token["section"], "hand": token["hand"],
            "triple_reading_token_stable": token["triple_reading_token_stable"], "surface_line": line_text[str(token["locus"])],
        })
    rows.sort(key=token_sort_key)
    for index, row in enumerate(rows, 1):
        row["chol_id"] = f"G628-H{index:03d}"
    return rows


def extension_parse(surface: str) -> str:
    if surface in LATTICE_PARSE:
        return "QUALITY_CARRIER_LATTICE"
    if re.fullmatch(r"chola(?:i{0,3})n", surface):
        return "CHOL_DIRECT_VALUE"
    if re.fullmatch(r"cholda(?:i{0,3})n", surface):
        return "CHOL_FUSED_D_VALUE"
    if surface in {"choly", "choldy"}:
        return "CHOL_CLOSURE_FORM"
    return "PRODUCTIVE_EXTENSION_OPEN"


def make_extensions(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        if "chol" in str(row["eva"]):
            by_surface[str(row["eva"])].append(row)
    rows: list[dict[str, object]] = []
    for surface, selected in by_surface.items():
        if surface == "chol":
            extension_class, left, right = "EXACT", "NONE", "NONE"
        elif surface.startswith("chol") and not surface.endswith("chol"):
            extension_class, left, right = "RIGHT_EXTENSION", "NONE", surface[4:]
        elif surface.endswith("chol") and not surface.startswith("chol"):
            extension_class, left, right = "LEFT_EXTENSION", surface[:-4], "NONE"
        else:
            extension_class, left, right = "BOTH_OR_INTERNAL", "OPEN", "OPEN"
        rows.append({
            "surface": surface, "extension_class": extension_class, "left_extension": left,
            "right_extension": right, "working_parse": extension_parse(surface),
            "occurrences": len(selected), "pages": len({str(row["page"]) for row in selected}),
            "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
            "example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in selected[:8])),
        })
    rows.sort(key=lambda row: (-int(row["occurrences"]), str(row["surface"])))
    return rows


def make_value_paths(tokens: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        by_surface[str(row["eva"])].append(row)
    rows: list[dict[str, object]] = []
    for base, (wrapper, core, ending) in LATTICE_PARSE.items():
        for value, roman in ROMAN.items():
            direct, fused = base + VALUE_TAIL[value], base + D_VALUE[value]
            separate = base + " " + D_VALUE[value]
            candidates: dict[str, list[dict[str, object]]] = {
                "DIRECT_A_VALUE": by_surface[direct],
                "FUSED_D_VALUE": by_surface[fused],
                "SEPARATE_D_VALUE": [],
            }
            for line in by_line.values():
                for left, right in zip(line, line[1:]):
                    if left["eva"] == base and right["eva"] == D_VALUE[value]:
                        candidates["SEPARATE_D_VALUE"].append({
                            **left,
                            "triple_reading_token_stable": int(left["right_pair_triple_stable"]),
                        })
            for mode, selected in candidates.items():
                predicted = {"DIRECT_A_VALUE": direct, "FUSED_D_VALUE": fused, "SEPARATE_D_VALUE": separate}[mode]
                rows.append({
                    "base_surface": base, "wrapper": wrapper or "BARE", "quality_core": core or "NONE",
                    "ending": ending.upper(), "working_value": value, "working_roman": roman,
                    "realization_mode": mode, "predicted_surface": predicted, "occurrences": len(selected),
                    "pages": len({str(row["page"]) for row in selected}),
                    "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
                    "occupied": int(bool(selected)),
                })
    summary: list[dict[str, object]] = []
    for mode in ("DIRECT_A_VALUE", "FUSED_D_VALUE", "SEPARATE_D_VALUE"):
        selected = [row for row in rows if row["realization_mode"] == mode]
        summary.append({
            "realization_mode": mode, "registered_cells": len(selected),
            "occupied_cells": sum(int(row["occupied"]) for row in selected),
            "occurrences": sum(int(row["occurrences"]) for row in selected),
            "triple_stable_occurrences": sum(int(row["triple_stable_occurrences"]) for row in selected),
            "bases_with_occurrence": len({str(row["base_surface"]) for row in selected if int(row["occupied"])}),
        })
    return rows, summary


def make_chol_values(tokens: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        by_surface[str(row["eva"])].append(row)
    for value, roman in ROMAN.items():
        for mode, surface in (("DIRECT_A_VALUE", "chol" + VALUE_TAIL[value]), ("FUSED_D_VALUE", "chol" + D_VALUE[value])):
            for token in by_surface[surface]:
                line, index = by_line[str(token["locus"])], int(token["token_index"]) - 1
                rows.append({
                    "realization_id": "", "page": token["page"], "locus": token["locus"], "token_index": token["token_index"],
                    "realization_mode": mode, "surface_expression": surface,
                    "segmentation": f"chol+{'a' if mode == 'DIRECT_A_VALUE' else 'd+a'}+{roman}",
                    "working_value": value, "working_roman": roman, "working_reading_de": f"trocken, Grad {roman}",
                    "phrase_line_end": int(index + 1 == len(line)),
                    "all_expression_tokens_stable": token["triple_reading_token_stable"],
                    "section": token["section"], "surface_line": line_text[str(token["locus"])],
                })
        for locus, line in by_line.items():
            for index, (left, right) in enumerate(zip(line, line[1:])):
                if left["eva"] != "chol" or right["eva"] != D_VALUE[value]:
                    continue
                rows.append({
                    "realization_id": "", "page": left["page"], "locus": locus, "token_index": left["token_index"],
                    "realization_mode": "SEPARATE_D_VALUE", "surface_expression": f"chol {D_VALUE[value]}",
                    "segmentation": f"chol | d+a+{roman}", "working_value": value, "working_roman": roman,
                    "working_reading_de": f"trocken, Grad {roman}", "phrase_line_end": int(index + 2 == len(line)),
                    "all_expression_tokens_stable": int(left["right_pair_triple_stable"]),
                    "section": left["section"], "surface_line": line_text[locus],
                })
    rows.sort(key=lambda row: (int(row["working_value"]), str(row["realization_mode"]), str(row["page"]), str(row["locus"]), int(row["token_index"])))
    for index, row in enumerate(rows, 1):
        row["realization_id"] = f"G628-V{index:03d}"
    return rows


def make_d_phrases(tokens: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str], ending: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    allowed = {surface for surface, (_wrapper, core, cell_ending) in LATTICE_PARSE.items() if core and cell_ending == ending}
    inverse_value = {surface: value for value, surface in D_VALUE.items()}
    for locus, line in by_line.items():
        for index, (left, right) in enumerate(zip(line, line[1:])):
            base, value_surface = str(left["eva"]), str(right["eva"])
            if base not in allowed or value_surface not in inverse_value:
                continue
            wrapper, core, _cell_ending = LATTICE_PARSE[base]
            value, roman = inverse_value[value_surface], ROMAN[inverse_value[value_surface]]
            if ending == "ol":
                role = "QUALITY_DEGREE"
                reading = f"{quality_reading(wrapper, core)}, Grad {roman}"
            else:
                role = "PART_AMOUNT_OR_QUALITY_DEGREE"
                noun = "Pflanzenteil" if base == "chor" else "reproduktiver Teil" if base == "shor" else f"{base}-Träger"
                reading = f"{noun}: {value} Maß/Portion oder Grad {roman}"
            rows.append({
                "phrase_id": "", "page": left["page"], "locus": locus, "token_index": left["token_index"],
                "carrier_surface": base, "quality_core": core, "d_value_surface": value_surface,
                "working_value": value, "working_roman": roman, "contextual_role": role,
                "working_reading_de": reading, "phrase_line_end": int(index + 2 == len(line)),
                "all_expression_tokens_stable": int(left["right_pair_triple_stable"]),
                "surface_line": line_text[locus],
            })
    rows.sort(key=token_sort_key)
    prefix = "L" if ending == "ol" else "R"
    for index, row in enumerate(rows, 1):
        row["phrase_id"] = f"G628-{prefix}{index:03d}"
    return rows


def make_terminal(chol_values: list[dict[str, object]], quality_surfaces: set[str]) -> list[dict[str, object]]:
    context_classes = {
        "f17r.11": ("QUALITY_ANCHORED", "trockenes Material, vier Portionen bleibt Nebenlesung"),
        "f51v.6": ("QUALITY_ANCHORED", "Transkriptionsstabilität der ganzen Paarung eingeschränkt"),
        "f14v.2": ("QUALITY_ANCHORED", "Trockenheitswiederholung kann mehrere lokale Zellen anzeigen"),
        "f49v.26": ("QUALITY_ANCHORED", "thermischer Anker steht mit Abstand"),
        "f2r.7": ("QUALITY_OR_DOSE", "trocken Grad I oder eine Portion Trockenmaterial"),
        "f2v.5": ("QUALITY_OR_DOSE", "kein sicherer unmittelbarer Stoffträger"),
        "f35v.19": ("QUALITY_OR_DOSE", "elliptischer Kontext"),
        "f37v.23": ("QUALITY_OR_DOSE", "kurze Qualitäts- und Dosislesung gleich möglich"),
        "f85r2.4": ("QUALITY_OR_DOSE", "Wurzelteil trocken Grad III oder drei Portionen"),
        "f96r.8": ("QUALITY_OR_DOSE", "elliptischer Kontext"),
        "f18r.2": ("MULTI_CLAUSE_REQUIRED", "mehrere gegensätzliche Qualitätsformen; Wert II instabil"),
        "f47v.9": ("MULTI_CLAUSE_REQUIRED", "chol-Wiederholung verlangt Zell- oder Klauselgrenze"),
        "f56v.16": ("MULTI_CLAUSE_REQUIRED", "dreifache chol-Familie verlangt mehrere Zellen"),
    }
    rows: list[dict[str, object]] = []
    for value in chol_values:
        if value["realization_mode"] != "SEPARATE_D_VALUE" or not int(value["phrase_line_end"]):
            continue
        prefix = str(value["surface_line"]).split()[:-2]
        evidence_class, local_caution = context_classes[str(value["locus"])]
        rows.append({
            "witness_id": "", "page": value["page"], "locus": value["locus"],
            "d_value_surface": str(value["surface_expression"]).split()[1], "working_roman": value["working_roman"],
            "working_reading_de": value["working_reading_de"],
            "earlier_quality_surfaces": "|".join(word for word in prefix if word in quality_surfaces) or "NONE",
            "earlier_part_surfaces": "|".join(word for word in prefix if word in PART_TERMS) or "NONE",
            "local_evidence_class": evidence_class, "local_caution": local_caution,
            "all_expression_tokens_stable": value["all_expression_tokens_stable"],
            "surface_line": value["surface_line"],
        })
    rows.sort(key=lambda row: (ROMAN_ORDER[str(row["working_roman"])], str(row["page"]), str(row["locus"])))
    for index, row in enumerate(rows, 1):
        row["witness_id"] = f"G628-T{index:02d}"
    return rows


def make_ranking() -> list[dict[str, object]]:
    return [
        {"rank": 1, "model": "CH_PLUS_OL_DRY_QUALITY_CARRIER", "working_reading_de": "chol=trocken; chol d-Wert=trocken in Grad I-IV", "support": "23/24 kernhaltige OL-Zellen; alle Qualitätsatome; direkte/fusionierte/getrennte Werte; historische Gradsyntax", "counterevidence": "ol kann Material zusätzlich nominalisieren", "disposition": "PRIMARY_DEFAULT"},
        {"rank": 2, "model": "DRY_MATERIAL_PLUS_PORTION", "working_reading_de": "chol=Trockenmaterial; d-Wert=Anzahl Portionen", "support": "ol behaves like a reusable head and d is a value carrier", "counterevidence": "complete I-IV terminal frame and other quality-rich lines fit Galenic degree more directly", "disposition": "LIVE_NOMINAL_RIVAL"},
        {"rank": 3, "model": "CHOL_AS_MEASURE_UNIT", "working_reading_de": "chol=Maßeinheit; d-Wert=number", "support": "unit before numeral is historically ordinary", "counterevidence": "chol liegt im heiß/kalt/trocken/feucht-OL-Gitter und hat 314 Rand-Erweiterungen plus 33 interne Substring-Treffer", "disposition": "DOWNGRADED"},
        {"rank": 4, "model": "CHOL_AS_SPECIFIC_PLANT_PART", "working_reading_de": "chol=specific organ or ingredient", "support": "many Herbal occurrences", "counterevidence": "125 pages and all six sections plus complete quality composition are too broad", "disposition": "DOWNGRADED"},
        {"rank": 5, "model": "CHOL_AS_SEPARATOR_OR_CLOSURE_ONLY", "working_reading_de": "chol=punctuation or line closure", "support": "high frequency", "counterevidence": "320/343 exact tokens are medial and the form accepts both left and right extensions", "disposition": "REJECTED_AS_DEFAULT"},
    ]


def make_dictionary() -> list[dict[str, object]]:
    inherited: list[dict[str, object]] = []
    for source in read_tsv(ROOT / G627_DICT_REL):
        row: dict[str, object] = {
            "entry": source["entry"], "kind": source["kind"],
            "working_meaning_de": source["working_meaning_de"],
            "composition": source["composition"], "context_rule": source["scope"],
            "status": source["status"],
        }
        if source["entry"] == "d":
            row.update({
                "kind": "DETACHED_VALUE_HEAD", "working_meaning_de": "freier Wert-/Gradträger",
                "composition": "d+a+Wert", "context_rule": "nach OL-Qualität Grad; nach OR-/Partterm Maß/Portion oder Grad",
                "status": "REVISED_CONTEXTUAL_DEFAULT",
            })
        elif source["entry"] == "dan/dain/daiin/daiiin":
            row.update({
                "kind": "CONTEXTUAL_VALUE_SERIES", "working_meaning_de": "Grad- oder Maßwert I/II/III/IV",
                "context_rule": "nach OL-Qualität Grad I-IV; nach OR-/Partterm Menge oder Grad I-IV",
                "status": "REVISED_CONTEXTUAL_DEFAULT",
            })
        elif source["entry"] == "daiin":
            row.update({
                "kind": "CONTEXTUAL_VALUE_III", "working_meaning_de": "Grad- oder Maßwert III",
                "context_rule": "nach OL-Qualität Grad III; nach OR-/Partterm drei Portionen oder Grad III",
                "status": "REVISED_CONTEXTUAL_DEFAULT",
            })
        inherited.append(row)
    additions: list[dict[str, object]] = [
        {"entry": "ol", "kind": "QUALITY_STATE_MATERIAL_CARRIER", "working_meaning_de": "Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz", "composition": "QUALITY_CORE+ol", "context_rule": "mit Qualitätskern flüssig meist ohne eigenes deutsches Wort", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "or", "kind": "NOMINAL_PART_CARRIER", "working_meaning_de": "Teil-/Nominalträger; genaue Basisbedeutung offen", "composition": "ROOT+or", "context_rule": "chor/shor behalten konkrete Partlesungen", "status": "NEW_CONTEXT_SPLIT"},
        {"entry": "chol", "kind": "DRY_OL_FORM", "working_meaning_de": "trocken; nominal trockenes Gut/Material", "composition": "ch+ol", "context_rule": "vor d-Wert: trocken in Grad I-IV", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "shol", "kind": "MOIST_OL_FORM", "working_meaning_de": "feucht; nominal feuchtes Gut/Material", "composition": "sh+ol", "context_rule": "vor d-Wert: feucht in Grad II/III", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "kol", "kind": "HOT_OL_FORM", "working_meaning_de": "heiß; nominal heißes Gut/Material", "composition": "k+ol", "context_rule": "vor d-Wert: heiß in diesem Grad", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "tol", "kind": "COLD_OL_FORM", "working_meaning_de": "kalt; nominal kaltes Gut/Material", "composition": "t+ol", "context_rule": "vor d-Wert: kalt in diesem Grad", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "kchol/kshol/tchol/tshol", "kind": "PAIRED_QUALITY_OL_FORMS", "working_meaning_de": "heiß-trocken/heiß-feucht/kalt-trocken/kalt-feucht", "composition": "k|t + ch|sh + ol", "context_rule": "d-Wert danach ist Qualitätsgrad", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "o-/qo- + OL-Form", "kind": "SCOPED_QUALITY_OL_FORM", "working_meaning_de": "dieselbe Qualität im o-/qo-Rahmen", "composition": "o|qo + QUALITY_CORE + ol", "context_rule": "Wrapper bleibt hörbar nur wenn nötig", "status": "NEW_PRIMARY_DEFAULT"},
        {"entry": "cholaiin", "kind": "DIRECT_QUALITY_VALUE", "working_meaning_de": "trocken, Grad III", "composition": "chol+a+III", "context_rule": "direkter Wertanschluss", "status": "NEW_CONCRETE_READING"},
        {"entry": "choldaiin", "kind": "FUSED_FREE_VALUE", "working_meaning_de": "trocken, Grad III", "composition": "chol+d+a+III", "context_rule": "expliziter d-Träger im selben Token", "status": "NEW_CONCRETE_READING"},
        {"entry": "chol dan/dain/daiin/daiiin", "kind": "SEPARATE_QUALITY_DEGREE", "working_meaning_de": "trocken, Grad I/II/III/IV", "composition": "chol | d+a+I/II/III/IV", "context_rule": "expliziter d-Träger als eigenes Token", "status": "NEW_CONCRETE_READING"},
        {"entry": "chor", "kind": "PART_OR_FORM", "working_meaning_de": "Pflanzen-/Reproduktionsteil", "composition": "gelernte Partform; ch+or Qualitätsrival", "context_rule": "vor d-Wert standardmäßig lokale Menge/Grad, nicht chol-Trockenphrase", "status": "INHERITED_CONTEXT_SPLIT"},
        {"entry": "shor", "kind": "PART_OR_FORM", "working_meaning_de": "Blüten-/Fruchtstand; reproduktiver Teil", "composition": "gelernte Partform; sh+or Qualitätsrival", "context_rule": "vor d-Wert standardmäßig lokale Menge/Grad", "status": "INHERITED_CONTEXT_SPLIT"},
    ]
    return inherited + additions


def contains_sequence(words: list[str], target: list[str]) -> bool:
    return any(words[index:index + len(target)] == target for index in range(len(words) - len(target) + 1))


def make_cases(line_text: dict[str, str], cross_by_locus: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    specs = [
        ("DRY_I", "f2r", "f2r.7", "chol dan", "ch+ol | d+a+I", "trocken, ersten Grades", "QUALITY_DEGREE"),
        ("DRY_II", "f47v", "f47v.9", "chol dain", "ch+ol | d+a+II", "trocken, zweiten Grades", "QUALITY_DEGREE"),
        ("DRY_III", "f37v", "f37v.23", "chol daiin", "ch+ol | d+a+III", "trocken, dritten Grades", "QUALITY_DEGREE"),
        ("DRY_IV", "f17r", "f17r.11", "chol daiiin", "ch+ol | d+a+IV", "trocken, vierten Grades", "QUALITY_DEGREE"),
        ("HOT_II", "f102r1", "f102r1.5", "qokol dain", "qo+k+ol | d+a+II", "heiß im qo-Rahmen, zweiten Grades", "QUALITY_DEGREE"),
        ("HOT_III", "f3r", "f3r.16", "qokol daiin", "qo+k+ol | d+a+III", "heiß im qo-Rahmen, dritten Grades", "QUALITY_DEGREE"),
        ("HOT_IV", "f53v", "f53v.4", "qokol daiiin", "qo+k+ol | d+a+IV", "heiß im qo-Rahmen, vierten Grades", "QUALITY_DEGREE"),
        ("COLD_III", "f19v", "f19v.4", "qotol daiin", "qo+t+ol | d+a+III", "kalt im qo-Rahmen, dritten Grades", "QUALITY_DEGREE"),
        ("MOIST_II", "f27r", "f27r.2", "shol dain", "sh+ol | d+a+II", "feucht, zweiten Grades", "QUALITY_DEGREE"),
        ("MOIST_III", "f20v", "f20v.4", "shol daiin", "sh+ol | d+a+III", "feucht, dritten Grades", "QUALITY_DEGREE"),
        ("HOT_DRY_III", "f11r", "f11r.2", "kchol daiin", "k+ch+ol | d+a+III", "heiß-trocken, dritten Grades", "QUALITY_DEGREE"),
        ("COLD_DRY_II", "f47r", "f47r.10", "tchol dain", "t+ch+ol | d+a+II", "kalt-trocken, zweiten Grades", "QUALITY_DEGREE"),
        ("COLD_DRY_III", "f21v", "f21v.2", "tchol daiin", "t+ch+ol | d+a+III", "kalt-trocken, dritten Grades", "QUALITY_DEGREE"),
        ("DRY_III_DIRECT", "f2r", "f2r.10", "cholaiin", "ch+ol+a+III", "trocken, dritten Grades", "DIRECT_QUALITY_VALUE"),
        ("DRY_III_FUSED", "f17v", "f17v.8", "choldaiin", "ch+ol+d+a+III", "trocken, dritten Grades", "FUSED_QUALITY_VALUE"),
        ("F17_TWO_GRADES", "f17r", "f17r.11", "cthar okaiin chol daiiin", "cth-Part | o+k+a+III | ch+ol | d+a+IV", "vegetatives Gut: heiß Grad III; trocken Grad IV", "PART_WITH_TWO_QUALITY_GRADES"),
        ("F51_MATCHED_III", "f51v", "f51v.6", "qotaiin otykol chol daiin", "qo+t+a+III | ... | ch+ol | d+a+III", "kalt Grad III; ...; trocken Grad III", "SAME_LINE_QUALITY_GRADES"),
        ("F14_LEAF_DRY_III", "f14v", "f14v.2", "cthy otchy ty chol daiin", "cthy | o+t+ch+y | ... | ch+ol | d+a+III", "Blattgut, kalt-trocken; Trockenheit Grad III", "PART_QUALITY_DEGREE"),
        ("F45_OR_PART", "f45v", "f45v.2", "chor daiin cthy", "chor | d+a+III | cthy", "Pflanzenteil: drei Maße oder Grad III; danach Blattgut", "OR_PART_VALUE_RIVAL"),
    ]
    rows: list[dict[str, object]] = []
    for case_id, page, locus, expression, segmentation, reading, reading_type in specs:
        if expression not in line_text[locus]:
            raise RuntimeError(f"missing concrete expression: {case_id}")
        target = expression.split()
        alternate_hits = {
            label: contains_sequence(cross_by_locus[locus][field].split(), target)
            for label, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
        }
        missing = [label for label, hit in alternate_hits.items() if not hit]
        rows.append({
            "case_id": case_id, "page": page, "locus": locus, "surface_expression": expression,
            "segmentation": segmentation, "working_reading_de": reading,
            "reading_type": reading_type,
            "triple_expression_exact": int(not missing),
            "reader_status": "TRIPLE_EXACT" if not missing else "TRANSCRIPTION_VARIANT",
            "reader_note": "alle drei Lesungen tragen den Ausdruck" if not missing else "Ausdruck fehlt als exakte Folge in " + ",".join(missing),
            "surface_line": line_text[locus],
        })
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    allowlist = read_tsv(ROOT / ALLOWLIST_REL)
    pages = {row["page"] for row in allowlist}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("unsafe page allow-list")
    token_rows, token_guard = guarded_query(TOKENS_REL, pages, "page,locus,code,kind,section,language,hand,token_index,eva")
    cross_rows, cross_guard = guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    tokens = annotate_stability(token_rows, stable_capacities(cross_rows))
    by_line, line_text = line_maps(tokens)
    annotate_pair_stability(by_line, stable_pair_capacities(cross_rows))
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    cth_family = {row["surface"]: row for row in read_tsv(ROOT / G625_CTH_REL)}
    if cth_family["cthar"]["root_default_de"] != "Blatt-/Krautteil-Familie":
        raise RuntimeError("inherited cthar part-family reading changed")

    matrix = make_matrix(tokens)
    occurrences = make_carrier_occurrences(tokens, by_line, line_text)
    contrasts, contrast_summary = make_contrasts(by_line, line_text)
    chol = make_chol(tokens, by_line, line_text)
    extensions = make_extensions(tokens)
    value_grid, value_summary = make_value_paths(tokens, by_line)
    chol_values = make_chol_values(tokens, by_line, line_text)
    inherited_y_quality = {row["surface"] for row in read_tsv(ROOT / G624_READER_REL)}
    inherited_degree_quality = {row["surface"] for row in read_tsv(ROOT / G627_AXIS_REL)}
    ol_quality = {surface for surface, (_wrapper, core, ending) in LATTICE_PARSE.items() if core and ending == "ol"}
    terminal = make_terminal(chol_values, inherited_y_quality | inherited_degree_quality | ol_quality)
    ol_phrases = make_d_phrases(tokens, by_line, line_text, "ol")
    or_phrases = make_d_phrases(tokens, by_line, line_text, "or")
    ranking = make_ranking()
    dictionary = make_dictionary()
    cases = make_cases(line_text, cross_by_locus)

    write_tsv(ROOT / OUTPUTS["allowlist"], allowlist, ("page",))
    write_tsv(ROOT / OUTPUTS["matrix"], matrix, ("wrapper", "quality_core", "ending", "surface", "composition", "role", "working_meaning_de", "occurrences", "pages", "loci", "triple_stable_occurrences", "occupied"))
    write_tsv(ROOT / OUTPUTS["occurrences"], occurrences, ("occurrence_id", "page", "locus", "token_index", "surface", "wrapper", "quality_core", "ending", "role", "working_meaning_de", "left_surface", "right_surface", "position", "section", "hand", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["contrasts"], contrasts, ("contrast_id", "page", "locus", "contrast_type", "left_surface", "right_surface", "minimum_token_distance", "adjacent", "both_have_stable_token", "both_have_adjacent_stable_tokens", "section", "surface_line"))
    write_tsv(ROOT / OUTPUTS["contrast_summary"], contrast_summary, ("contrast_type", "left_surface", "right_surface", "lines", "pages", "stable_lines", "adjacent_lines", "stable_adjacent_lines", "example_loci"))
    write_tsv(ROOT / OUTPUTS["chol"], chol, ("chol_id", "page", "locus", "token_index", "surface", "composition", "working_meaning_de", "left_surface", "right_surface", "position", "section", "hand", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["extensions"], extensions, ("surface", "extension_class", "left_extension", "right_extension", "working_parse", "occurrences", "pages", "triple_stable_occurrences", "example_loci"))
    write_tsv(ROOT / OUTPUTS["value_grid"], value_grid, ("base_surface", "wrapper", "quality_core", "ending", "working_value", "working_roman", "realization_mode", "predicted_surface", "occurrences", "pages", "triple_stable_occurrences", "occupied"))
    write_tsv(ROOT / OUTPUTS["value_summary"], value_summary, ("realization_mode", "registered_cells", "occupied_cells", "occurrences", "triple_stable_occurrences", "bases_with_occurrence"))
    write_tsv(ROOT / OUTPUTS["chol_values"], chol_values, ("realization_id", "page", "locus", "token_index", "realization_mode", "surface_expression", "segmentation", "working_value", "working_roman", "working_reading_de", "phrase_line_end", "all_expression_tokens_stable", "section", "surface_line"))
    write_tsv(ROOT / OUTPUTS["terminal"], terminal, ("witness_id", "page", "locus", "d_value_surface", "working_roman", "working_reading_de", "earlier_quality_surfaces", "earlier_part_surfaces", "local_evidence_class", "local_caution", "all_expression_tokens_stable", "surface_line"))
    phrase_fields = ("phrase_id", "page", "locus", "token_index", "carrier_surface", "quality_core", "d_value_surface", "working_value", "working_roman", "contextual_role", "working_reading_de", "phrase_line_end", "all_expression_tokens_stable", "surface_line")
    write_tsv(ROOT / OUTPUTS["ol_phrases"], ol_phrases, phrase_fields)
    write_tsv(ROOT / OUTPUTS["or_phrases"], or_phrases, phrase_fields)
    write_tsv(ROOT / OUTPUTS["ranking"], ranking, ("rank", "model", "working_reading_de", "support", "counterevidence", "disposition"))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))
    write_tsv(ROOT / OUTPUTS["cases"], cases, ("case_id", "page", "locus", "surface_expression", "segmentation", "working_reading_de", "reading_type", "triple_expression_exact", "reader_status", "reader_note", "surface_line"))

    mode_counts = {row["realization_mode"]: int(row["occurrences"]) for row in value_summary}
    chol_modes = Counter(str(row["realization_mode"]) for row in chol_values)
    chol_value_counts = Counter(str(row["working_roman"]) for row in chol_values)
    contrast_types = Counter(str(row["contrast_type"]) for row in contrasts)
    result = {
        "schema": "GDT628_CHOL_QUALITY_CARRIER_RESULT_V1",
        "experiment_id": "GDT628",
        "status": "OL_QUALITY_CARRIER_LATTICE__CHOL_DRY_DEGREES_I_IV__D_CONTEXT_SPLIT",
        "claim_boundary": "The productive OL/OR carrier lattice resolves chol compositionally as ch+ol. Under the inherited quality orientation its primary fluent reading is dry, with dry material as the nominal form. Direct cholaiin, fused choldaiin, and separate chol daiin realize the same working value III through three spacing modes. In the fixed terminal chol d-value frame, d selects Galenic degree I-IV. After OR/plant-part carriers, amount, portion, class, or degree remains contextual; no absolute unit is assigned.",
        "guard": {
            "f1r": "EXCLUDED_BY_ALLOWLIST", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "safe_pages": len(pages), "safe_token_rows": len(tokens), "safe_cross_rows": len(cross_rows),
            "token_query": token_guard, "cross_query": cross_guard, "new_image_pages": 0,
        },
        "carrier_lattice": {
            "registered_cells": len(matrix), "occupied_cells": sum(int(row["occupied"]) for row in matrix),
            "occurrences": len(occurrences), "stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in occurrences),
            "pages": len({str(row["page"]) for row in occurrences}), "loci": len({str(row["locus"]) for row in occurrences}),
            "ol_occurrences": sum(int(row["occurrences"]) for row in matrix if row["ending"] == "OL"),
            "or_occurrences": sum(int(row["occurrences"]) for row in matrix if row["ending"] == "OR"),
            "ol_occupied_cells": sum(int(row["occupied"]) for row in matrix if row["ending"] == "OL"),
            "or_occupied_cells": sum(int(row["occupied"]) for row in matrix if row["ending"] == "OR"),
            "coreful_ol_registered_cells": sum(1 for row in matrix if row["ending"] == "OL" and row["quality_core"] != "NONE"),
            "coreful_ol_occupied_cells": sum(int(row["occupied"]) for row in matrix if row["ending"] == "OL" and row["quality_core"] != "NONE"),
            "local_contrasts": len(contrasts), "stable_local_contrasts": sum(int(row["both_have_stable_token"]) for row in contrasts),
            "adjacent_contrasts": sum(int(row["adjacent"]) for row in contrasts),
            "stable_adjacent_contrasts": sum(int(row["both_have_adjacent_stable_tokens"]) for row in contrasts),
            "contrast_type_counts": dict(sorted(contrast_types.items())),
        },
        "chol": {
            "exact_occurrences": len(chol), "exact_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in chol),
            "pages": len({str(row["page"]) for row in chol}),
            "position_counts": dict(sorted(Counter(str(row["position"]) for row in chol).items())),
            "substring_occurrences": sum(int(row["occurrences"]) for row in extensions), "substring_types": len(extensions),
            "extension_class_occurrences": dict(sorted(Counter({kind: sum(int(row["occurrences"]) for row in extensions if row["extension_class"] == kind) for kind in {str(row["extension_class"]) for row in extensions}}).items())),
            "working_default": "chol=ch+ol=trocken; nominal trockenes Gut/Material",
        },
        "value_realization": {
            "all_carrier_mode_counts": mode_counts,
            "all_carrier_occurrences": sum(mode_counts.values()),
            "chol_mode_counts": dict(sorted(chol_modes.items())),
            "chol_value_counts": dict(sorted(chol_value_counts.items(), key=lambda item: list(ROMAN.values()).index(item[0]))),
            "chol_realizations": len(chol_values),
            "chol_stable_realizations": sum(int(row["all_expression_tokens_stable"]) for row in chol_values),
            "chol_terminal_separate": len(terminal),
            "chol_terminal_context_classes": dict(sorted(Counter(str(row["local_evidence_class"]) for row in terminal).items())),
            "ol_quality_separate_phrases": len(ol_phrases),
            "or_carrier_separate_phrases": len(or_phrases),
        },
        "working_lexicon_updates": {
            "ol": "Eigenschafts-/Zustands-/Materialträger; mit Qualität meist null",
            "chol": "trocken; nominal trockenes Gut/Material",
            "shol": "feucht; nominal feuchtes Gut/Material",
            "kol_tol": "heiß/kalt in OL-Form",
            "kchol_tchol": "heiß-trocken/kalt-trocken in OL-Form",
            "chol_d_values": "trocken, Grad I/II/III/IV",
            "d": "freier Wertträger; nach OL-Qualität Grad, nach OR/Part Menge oder Grad",
        },
        "manual_sources": {
            "historical_syntax_comparators": len(read_tsv(ROOT / G627_HISTORICAL_REL)),
            "inherited_visual_judgments": len(read_tsv(ROOT / G627_VISUAL_REL)),
            "role_models": len(ranking), "concrete_readings": len(cases),
            "triple_exact_concrete_readings": sum(int(row["triple_expression_exact"]) for row in cases),
            "transcription_variant_concrete_readings": sum(not int(row["triple_expression_exact"]) for row in cases),
        },
        "inputs": {str(path): sha256(ROOT / path) for path in (
            TOKENS_REL, CROSS_REL, ALLOWLIST_REL, G627_RESULT_REL, G627_DICT_REL,
            G627_HISTORICAL_REL, G627_VISUAL_REL, G627_AXIS_REL, G623_DICT_REL, G624_READER_REL,
            G625_CTH_REL,
        )},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "GDT628 built: "
        f"lattice={result['carrier_lattice']['occupied_cells']}/54 tokens={len(occurrences)} "
        f"same_line={len(contrasts)} adjacent={result['carrier_lattice']['adjacent_contrasts']} "
        f"chol={len(chol)} extensions={len(extensions)} modes={mode_counts} "
        f"cholvalues={len(chol_values)} terminal={len(terminal)} olD={len(ol_phrases)} orD={len(or_phrases)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
