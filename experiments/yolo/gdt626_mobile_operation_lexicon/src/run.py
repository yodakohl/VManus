#!/usr/bin/env python3
"""Build GDT626: the bounded minim-value suffix and concrete compounds."""

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
BASE_REL = Path("experiments/yolo/gdt626_mobile_operation_lexicon")
ART = ROOT / BASE_REL / "artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
ALLOWLIST_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PAGE_ALLOWLIST.tsv")
GDT623_DICT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv")
GDT624_READER_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PRODUCTIVE_READER.tsv")
GDT625_RESULT_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/RESULT.json")
HISTORICAL_REL = BASE_REL / "artifacts/HISTORICAL_NUMERAL_COMPARATORS.tsv"
VISUAL_REL = BASE_REL / "artifacts/MANUAL_VISUAL_JUDGMENTS.tsv"

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "occurrences": BASE_REL / "artifacts/MINIM_SUFFIX_OCCURRENCES.tsv",
    "totals": BASE_REL / "artifacts/MINIM_VALUE_TOTALS.tsv",
    "profiles": BASE_REL / "artifacts/VALUE_CONTEXT_PROFILES.tsv",
    "families": BASE_REL / "artifacts/MINIM_FAMILY_SUMMARY.tsv",
    "complete": BASE_REL / "artifacts/FOUR_CELL_FAMILIES.tsv",
    "mixed": BASE_REL / "artifacts/MIXED_VALUE_LINES.tsv",
    "editions": BASE_REL / "artifacts/READING_VALUE_TOTALS.tsv",
    "quality": BASE_REL / "artifacts/QUALITY_VALUE_COMPOUNDS.tsv",
    "quality_matrix": BASE_REL / "artifacts/QUALITY_VALUE_MATRIX.tsv",
    "parts": BASE_REL / "artifacts/PART_VALUE_COMPOUNDS.tsv",
    "da": BASE_REL / "artifacts/DA_VALUE_CONTEXTS.tsv",
    "rivals": BASE_REL / "artifacts/ROLE_RIVAL_RANKING.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V3.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_LOCAL_READINGS.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

MINIM_RE = re.compile(r"^(?P<head>.*a)(?P<minims>i*)n$")
QUALITY_VALUE_RE = re.compile(r"^(?P<wrapper>.*?)(?P<thermal>k|t)(?P<moisture>ch|sh)(?P<frame>[ed]*)a(?P<minims>i{0,3})n$")
PART_VALUE_RE = re.compile(r"^(?P<wrapper>.*?)(?P<root>cth|shor|chor|dair|sair)a(?P<minims>i{0,3})n$")
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}
STATE_ID = {("k", "ch"): "KCH", ("k", "sh"): "KSH", ("t", "ch"): "TCH", ("t", "sh"): "TSH"}
STATE_DE = {("k", "ch"): "heiß-trocken", ("k", "sh"): "heiß-feucht", ("t", "ch"): "kalt-trocken", ("t", "sh"): "kalt-feucht"}
PART_DE = {
    "cth": "Blatt-/oberirdisches Drogengut",
    "shor": "Blüten-/Fruchtstand",
    "chor": "Blüten-/Pflanzenteil",
    "dair": "Wurzelteil",
    "sair": "Wurzelteil (air-Familie)",
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
    fieldnames = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "NONE") if row.get(field, "") != "" else "NONE" for field in fieldnames})


def safe_pages() -> set[str]:
    pages = {row["page"] for row in read_tsv(ROOT / ALLOWLIST_REL)}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("unsafe page allow-list")
    return pages


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
    if not match:
        raise ValueError(locus)
    return int(match.group(1))


def token_sort_key(row: dict[str, str]) -> tuple[str, int, int]:
    return row["page"], line_number(row["locus"]), int(row["token_index"])


def parse_minim(surface: str) -> tuple[str, int] | None:
    match = MINIM_RE.fullmatch(surface)
    if match is None:
        return None
    return match.group("head"), len(match.group("minims")) + 1


def stable_capacities(cross_rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    stable: dict[str, Counter[str]] = {}
    for row in cross_rows:
        readings = [Counter(row[field].split()) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        universe = set().union(*(reading.keys() for reading in readings))
        stable[row["locus"]] = Counter({
            word: min(reading[word] for reading in readings)
            for word in universe if min(reading[word] for reading in readings) > 0
        })
    return stable


def line_maps(tokens: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, str]]:
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sorted(tokens, key=token_sort_key):
        by_line[row["locus"]].append(row)
    return by_line, {locus: " ".join(row["eva"] for row in rows) for locus, rows in by_line.items()}


def make_occurrences(tokens: list[dict[str, str]], stable: dict[str, Counter[str]], line_text: dict[str, str]) -> list[dict[str, object]]:
    stable_ordinals: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, object]] = []
    for token in sorted(tokens, key=token_sort_key):
        parsed = parse_minim(token["eva"])
        if parsed is None:
            continue
        head, value = parsed
        stable_ordinals[token["locus"], token["eva"]] += 1
        rows.append({
            "occurrence_id": f"G626-M{len(rows) + 1:05d}", "page": token["page"], "locus": token["locus"],
            "line_number": line_number(token["locus"]), "token_index": int(token["token_index"]), "surface": token["eva"],
            "head": head, "written_i_minims": value - 1, "working_value": value,
            "working_roman": ROMAN.get(value, f">IV:{value}"), "section": token["section"], "language": token["language"],
            "hand": token["hand"],
            "triple_reading_token_stable": int(stable_ordinals[token["locus"], token["eva"]] <= stable.get(token["locus"], Counter())[token["eva"]]),
            "surface_line": line_text[token["locus"]],
        })
    return rows


def make_totals(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for value in range(1, 5):
        selected = [row for row in occurrences if int(row["working_value"]) == value]
        rows.append({
            "working_value": value, "working_roman": ROMAN[value], "written_tail": "i" * (value - 1) + "n",
            "occurrences": len(selected), "surfaces": len({str(row["surface"]) for row in selected}),
            "heads": len({str(row["head"]) for row in selected}), "pages": len({str(row["page"]) for row in selected}),
            "loci": len({str(row["locus"]) for row in selected}),
            "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
            "herbal_occurrences": sum(row["section"] == "H" for row in selected),
            "line_first": sum(int(row["token_index"]) == 1 for row in selected),
            "line_last": sum(int(row["token_index"]) == len(str(row["surface_line"]).split()) for row in selected),
            "line_middle": sum(int(row["token_index"]) not in (1, len(str(row["surface_line"]).split())) for row in selected),
        })
    return rows


def make_profiles(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dimension, field in (("SECTION", "section"), ("HAND", "hand")):
        for value_name in sorted({str(row[field]) for row in occurrences}):
            selected = [row for row in occurrences if str(row[field]) == value_name]
            counts = Counter(int(row["working_value"]) for row in selected)
            denominator = counts[2] + counts[3]
            rows.append({
                "dimension": dimension, "dimension_value": value_name or "NONE", "occurrences": len(selected),
                "count_I": counts[1], "count_II": counts[2], "count_III": counts[3], "count_IV": counts[4],
                "III_share_among_II_III": f"{counts[3] / denominator:.6f}" if denominator else "0.000000",
                "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
            })
    return rows


def make_families(occurrences: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_head: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        if int(row["working_value"]) <= 4:
            by_head[str(row["head"])].append(row)
    rows: list[dict[str, object]] = []
    for head, selected in by_head.items():
        counts = Counter(int(row["working_value"]) for row in selected)
        stable = Counter()
        for row in selected:
            stable[int(row["working_value"])] += int(row["triple_reading_token_stable"])
        present = sorted(counts)
        rows.append({
            "head": head, "surface_I": head + "n", "surface_II": head + "in", "surface_III": head + "iin", "surface_IV": head + "iiin",
            "count_I": counts[1], "count_II": counts[2], "count_III": counts[3], "count_IV": counts[4],
            "stable_I": stable[1], "stable_II": stable[2], "stable_III": stable[3], "stable_IV": stable[4],
            "distinct_values": len(present), "present_values": "|".join(ROMAN[value] for value in present),
            "complete_I_II_III": int(all(counts[value] for value in (1, 2, 3))),
            "complete_I_II_III_IV": int(all(counts[value] for value in (1, 2, 3, 4))),
            "occurrences": len(selected), "pages": len({str(row["page"]) for row in selected}),
            "herbal_occurrences": sum(row["section"] == "H" for row in selected),
        })
    rows.sort(key=lambda row: (-int(row["distinct_values"]), -int(row["occurrences"]), str(row["head"])))
    return rows, [row for row in rows if int(row["complete_I_II_III_IV"])]


def make_mixed_lines(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        if int(row["working_value"]) <= 4:
            grouped[str(row["locus"]), str(row["head"])].append(row)
    rows: list[dict[str, object]] = []
    for (locus, head), selected in grouped.items():
        values = sorted({int(row["working_value"]) for row in selected})
        if len(values) < 2:
            continue
        selected.sort(key=lambda row: int(row["token_index"]))
        rows.append({
            "page": selected[0]["page"], "locus": locus, "head": head,
            "values": "|".join(ROMAN[value] for value in values), "value_span": max(values) - min(values),
            "series_surfaces_in_order": "|".join(str(row["surface"]) for row in selected),
            "series_token_count": len(selected), "all_series_tokens_triple_stable": int(all(int(row["triple_reading_token_stable"]) for row in selected)),
            "section": selected[0]["section"], "surface_line": selected[0]["surface_line"],
        })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), str(row["head"])))
    for index, row in enumerate(rows, 1):
        row["mixed_id"] = f"G626-L{index:04d}"
    return rows


def make_reading_totals(cross_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")):
        buckets: dict[int, list[tuple[str, str, str]]] = defaultdict(list)
        for line in cross_rows:
            for surface in line[field].split():
                parsed = parse_minim(surface)
                if parsed is not None and parsed[1] <= 4:
                    buckets[parsed[1]].append((line["page"], line["locus"], surface))
        for value in range(1, 5):
            selected = buckets[value]
            rows.append({
                "reading": label, "reading_role": "ALTERNATE_MANUSCRIPT_READING", "working_value": value,
                "working_roman": ROMAN[value], "occurrences": len(selected),
                "surfaces": len({surface for _, _, surface in selected}), "pages": len({page for page, _, _ in selected}),
                "loci": len({locus for _, locus, _ in selected}),
            })
    return rows


def make_quality_compounds(occurrences: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        match = QUALITY_VALUE_RE.fullmatch(str(occurrence["surface"]))
        if match is None:
            continue
        thermal, moisture, wrapper = match.group("thermal"), match.group("moisture"), match.group("wrapper")
        frame = match.group("frame")
        value = len(match.group("minims")) + 1
        wrapper_class = wrapper.upper() if wrapper in {"o", "qo"} else ("BARE" if not wrapper else "EXTENDED")
        rows.append({
            "compound_id": f"G626-Q{len(rows) + 1:04d}", "page": occurrence["page"], "locus": occurrence["locus"],
            "token_index": occurrence["token_index"], "surface": occurrence["surface"], "wrapper": wrapper or "BARE",
            "wrapper_class": wrapper_class, "thermal": thermal, "moisture": moisture,
            "frame_markers": frame or "BARE",
            "state_id": STATE_ID[thermal, moisture], "working_quality_de": STATE_DE[thermal, moisture],
            "working_value": value, "working_roman": ROMAN[value],
            "working_compound_de": f"{STATE_DE[thermal, moisture]}, Grad {ROMAN[value]}",
            "section": occurrence["section"], "triple_reading_token_stable": occurrence["triple_reading_token_stable"],
            "surface_line": occurrence["surface_line"],
        })
    matrix: list[dict[str, object]] = []
    for wrapper_class in ("BARE", "O", "QO"):
        for thermal, moisture in (("k", "ch"), ("k", "sh"), ("t", "ch"), ("t", "sh")):
            for value in range(1, 5):
                selected = [row for row in rows if row["wrapper_class"] == wrapper_class and row["frame_markers"] == "BARE" and row["state_id"] == STATE_ID[thermal, moisture] and int(row["working_value"]) == value]
                matrix.append({
                    "wrapper_class": wrapper_class, "state_id": STATE_ID[thermal, moisture], "working_quality_de": STATE_DE[thermal, moisture],
                    "working_value": value, "working_roman": ROMAN[value], "occurrences": len(selected),
                    "surfaces": "|".join(sorted({str(row["surface"]) for row in selected})) or "NONE",
                    "pages": len({str(row["page"]) for row in selected}),
                    "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in selected),
                })
    return rows, matrix


def make_part_compounds(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        match = PART_VALUE_RE.fullmatch(str(occurrence["surface"]))
        if match is None:
            continue
        value = len(match.group("minims")) + 1
        root, wrapper = match.group("root"), match.group("wrapper")
        rows.append({
            "compound_id": f"G626-P{len(rows) + 1:04d}", "page": occurrence["page"], "locus": occurrence["locus"],
            "token_index": occurrence["token_index"], "surface": occurrence["surface"], "wrapper": wrapper or "BARE",
            "part_root": root, "working_part_de": PART_DE[root], "working_value": value, "working_roman": ROMAN[value],
            "working_compound_de": f"{PART_DE[root]}, Mengen-/Gradstufe {ROMAN[value]}",
            "unit_status": "OFFEN__MENGE_DOSIS_GRAD_ODER_KLASSE", "section": occurrence["section"],
            "triple_reading_token_stable": occurrence["triple_reading_token_stable"], "surface_line": occurrence["surface_line"],
        })
    return rows


def make_da_contexts(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        if occurrence["head"] != "da" or int(occurrence["working_value"]) > 4:
            continue
        row = dict(occurrence)
        row["working_default_de"] = f"d-Wert {ROMAN[int(occurrence['working_value'])]}; lokal Mengen-/Gradmarker"
        row["whole_word_status"] = "NICHT_ALS_OPERATION_ODER_UND_LESEN__D_HEAD_OFFEN"
        rows.append(row)
    return rows


def make_rivals(occurrences: list[dict[str, object]], mixed: list[dict[str, object]], quality: list[dict[str, object]], parts: list[dict[str, object]]) -> list[dict[str, object]]:
    stable = sum(int(row["triple_reading_token_stable"]) for row in occurrences if int(row["working_value"]) <= 4)
    return [
        {"rank": 1, "model": "FOUR_CELL_MINIM_VALUE_SUFFIX", "default_reading": "-an/-ain/-aiin/-aiiin = I/II/III/IV", "support": f"bounded at four values; {len(mixed)} same-head mixed lines; {stable} triple-reading-stable tokens", "problem": "numeric value is an historical-form working inference, not a plaintext proof", "disposition": "PRIMARY_WORKING_MODEL"},
        {"rank": 2, "model": "HEAD_DEPENDENT_DEGREE", "default_reading": "on kch/ksh/tch/tsh heads: Galenic degree I-IV", "support": f"{len(quality)} exact quality-value compounds; real early-fifteenth-century quality rubrics use in ii/iii gradu", "problem": "quality-axis meanings remain working defaults", "disposition": "PRIMARY_ON_QUALITY_HEADS"},
        {"rank": 3, "model": "HEAD_DEPENDENT_AMOUNT", "default_reading": "on drug/part heads: amount or dosage class I-IV", "support": f"{len(parts)} exact part-value compounds in list-like Herbal contexts; contemporary recipes use j/ij/iij/iiij after units", "problem": "no Voynich unit or absolute amount is identified", "disposition": "PRIMARY_RIVAL_ON_PART_HEADS"},
        {"rank": 4, "model": "ORTHOGRAPHIC_OR_INFLECTIONAL_GRADE", "default_reading": "four written grades without numerical semantics", "support": "the tail is a genuine minim string and older alphabets treated in/iin as units", "problem": "must explain bounded four-cell paradigms and same-line contrasts without reducing them to random spelling", "disposition": "LIVE_COUNTERMODEL"},
        {"rank": 5, "model": "LEARNED_DAIIN_FUNCTION_WORD", "default_reading": "daiin has an additional learned local linking use", "support": "daiin is frequent and bridges known part carriers more often than its siblings", "problem": "the complete da paradigm makes a simple whole-word conjunction or item marker insufficient", "disposition": "SECONDARY_SURFACE_SPECIFIC_RIVAL"},
        {"rank": 6, "model": "OPERATION_VERB", "default_reading": "take/process/pass on", "support": "position can look mobile in isolated lines", "problem": "721 occurrences on 169 pages plus the minim paradigm and exact quality/part compounds provide no operation-specific content", "disposition": "DOWNGRADED"},
    ]


def make_dictionary() -> list[dict[str, object]]:
    return [
        {"entry": "-an", "kind": "VALUE_SUFFIX", "working_meaning_de": "Stufe/Wert I", "composition": "Kopf + a + Schlussstrich n", "scope": "alle passenden Köpfe", "status": "WORKING_DEFAULT"},
        {"entry": "-ain", "kind": "VALUE_SUFFIX", "working_meaning_de": "Stufe/Wert II", "composition": "Kopf + a + i+n", "scope": "alle passenden Köpfe", "status": "WORKING_DEFAULT"},
        {"entry": "-aiin", "kind": "VALUE_SUFFIX", "working_meaning_de": "Stufe/Wert III", "composition": "Kopf + a + ii+n", "scope": "alle passenden Köpfe", "status": "WORKING_DEFAULT"},
        {"entry": "-aiiin", "kind": "VALUE_SUFFIX", "working_meaning_de": "Stufe/Wert IV", "composition": "Kopf + a + iii+n", "scope": "alle passenden Köpfe", "status": "WORKING_DEFAULT_RARE"},
        {"entry": "k", "kind": "QUALITY_STEM", "working_meaning_de": "heiß", "composition": "thermaler Pol", "scope": "k/t + ch/sh Qualitätskern", "status": "INHERITED_WORKING_DEFAULT"},
        {"entry": "t", "kind": "QUALITY_STEM", "working_meaning_de": "kalt", "composition": "thermaler Pol", "scope": "k/t + ch/sh Qualitätskern", "status": "INHERITED_WORKING_DEFAULT"},
        {"entry": "ch", "kind": "QUALITY_STEM", "working_meaning_de": "trocken", "composition": "Feuchtepol", "scope": "k/t + ch/sh Qualitätskern", "status": "INHERITED_WORKING_DEFAULT"},
        {"entry": "sh", "kind": "QUALITY_STEM", "working_meaning_de": "feucht", "composition": "Feuchtepol", "scope": "k/t + ch/sh Qualitätskern", "status": "INHERITED_WORKING_DEFAULT"},
        {"entry": "kcha(i*)n", "kind": "QUALITY_VALUE_COMPOUND", "working_meaning_de": "heiß-trocken, Grad I-IV", "composition": "k+ch+Wert", "scope": "exakte Endkomposita", "status": "NEW_COMPOSITIONAL_DEFAULT"},
        {"entry": "ksha(i*)n", "kind": "QUALITY_VALUE_COMPOUND", "working_meaning_de": "heiß-feucht, Grad I-IV", "composition": "k+sh+Wert", "scope": "exakte Endkomposita", "status": "NEW_COMPOSITIONAL_DEFAULT"},
        {"entry": "tcha(i*)n", "kind": "QUALITY_VALUE_COMPOUND", "working_meaning_de": "kalt-trocken, Grad I-IV", "composition": "t+ch+Wert", "scope": "exakte Endkomposita", "status": "NEW_COMPOSITIONAL_DEFAULT"},
        {"entry": "tsha(i*)n", "kind": "QUALITY_VALUE_COMPOUND", "working_meaning_de": "kalt-feucht, Grad I-IV", "composition": "t+sh+Wert", "scope": "exakte Endkomposita", "status": "NEW_COMPOSITIONAL_DEFAULT"},
        {"entry": "cth", "kind": "PART_STEM", "working_meaning_de": "Blatt-/oberirdisches Drogengut", "composition": "Pflanzenteilkopf", "scope": "Herbal", "status": "INHERITED_WORKING_DEFAULT"},
        {"entry": "cthan/cthain/cthaiin", "kind": "PART_VALUE_COMPOUND", "working_meaning_de": "Blatt-/oberirdisches Drogengut, Stufe I/II/III", "composition": "cth+Wert", "scope": "Herbal; Einheit offen", "status": "NEW_COMPOSITIONAL_DEFAULT"},
        {"entry": "chor", "kind": "PART_STEM", "working_meaning_de": "Blüten-/Pflanzenteil", "composition": "Pflanzenteilkopf", "scope": "Herbal", "status": "INHERITED_WEAK_DEFAULT"},
        {"entry": "chorain/choraiin", "kind": "PART_VALUE_COMPOUND", "working_meaning_de": "Blüten-/Pflanzenteil, Stufe II/III", "composition": "chor+Wert", "scope": "Herbal; Einheit offen", "status": "NEW_COMPOSITIONAL_DEFAULT"},
        {"entry": "d", "kind": "OPEN_VALUE_HEAD", "working_meaning_de": "unbekannter d-Kopf vor einem Wert", "composition": "d+Wert", "scope": "dan/dain/daiin/daiiin", "status": "OPEN_HEAD"},
        {"entry": "daiin", "kind": "OPEN_VALUE_COMPOUND", "working_meaning_de": "d-Wert III; lokal Mengen-/Gradmarker", "composition": "d+III", "scope": "nicht automatisch und/item/Operation", "status": "NEW_RESEGMENTED_DEFAULT"},
    ]


def make_cases(line_text: dict[str, str], quality: list[dict[str, object]], parts: list[dict[str, object]]) -> list[dict[str, object]]:
    q_lookup = {(str(row["locus"]), str(row["surface"])): row for row in quality}
    p_lookup = {(str(row["locus"]), str(row["surface"])): row for row in parts}
    return [
        {"case_id": "F42_DA_SERIES", "page": "f42v", "locus": "f42v.2", "surface_line": line_text["f42v.2"], "segmentation": "... dan | dain | ... | daiin", "working_reading_de": "... d-Wert I; d-Wert II; ...; d-Wert III", "concrete_gain": "drei Stufen desselben d-Kopfes in einer Zeile", "unit_or_binding": "OFFEN", "status": "STRONG_PARADIGM_WITNESS"},
        {"case_id": "F38_DA_SERIES", "page": "f38v", "locus": "f38v.6", "surface_line": line_text["f38v.6"], "segmentation": "... daiin | daiiin | dain | dain", "working_reading_de": "... d-Wert III; d-Wert IV; d-Wert II; d-Wert II", "concrete_gain": "seltene IV-Stufe kontrastiert direkt mit II und III", "unit_or_binding": "OFFEN", "status": "STRONG_PARADIGM_WITNESS"},
        {"case_id": "F35_HOT_DRY_III", "page": "f35r", "locus": "f35r.13", "surface_line": line_text["f35r.13"], "segmentation": "qokch + aiin", "working_reading_de": q_lookup["f35r.13", "qokchaiin"]["working_compound_de"], "concrete_gain": "Qualitätskern sagt den Gradkompositum voraus", "unit_or_binding": "GRAD", "status": "PRIMARY_QUALITY_READING"},
        {"case_id": "F44_HOT_DRY_II", "page": "f44v", "locus": "f44v.2", "surface_line": line_text["f44v.2"], "segmentation": "qokch + ain", "working_reading_de": q_lookup["f44v.2", "qokchain"]["working_compound_de"], "concrete_gain": "gleicher Qualitätskopf mit anderem Grad", "unit_or_binding": "GRAD", "status": "PRIMARY_QUALITY_READING"},
        {"case_id": "F25_COLD_DRY_II", "page": "f25r", "locus": "f25r.4", "surface_line": line_text["f25r.4"], "segmentation": "qotch + ain", "working_reading_de": q_lookup["f25r.4", "qotchain"]["working_compound_de"], "concrete_gain": "Gegenpol behält dieselbe Gradendung", "unit_or_binding": "GRAD", "status": "PRIMARY_QUALITY_READING"},
        {"case_id": "F28_COLD_DRY_III", "page": "f28r", "locus": "f28r.3", "surface_line": line_text["f28r.3"], "segmentation": "qotch + aiin", "working_reading_de": q_lookup["f28r.3", "qotchaiin"]["working_compound_de"], "concrete_gain": "kalt-trockenes Gegenstück zu qokchaiin", "unit_or_binding": "GRAD", "status": "PRIMARY_QUALITY_READING"},
        {"case_id": "F18_CTH_III", "page": "f18r", "locus": "f18r.5", "surface_line": line_text["f18r.5"], "segmentation": "tchor | shor | cth + aiin | cthol ...", "working_reading_de": p_lookup["f18r.5", "cthaiin"]["working_compound_de"], "concrete_gain": "Blatt-/Krautteil mit III-Markierung in sichtbarer Teilfolge", "unit_or_binding": "MENGE_DOSIS_GRAD_ODER_KLASSE", "status": "PRIMARY_PART_READING"},
        {"case_id": "F18_CTH_QUALITY", "page": "f18r", "locus": "f18r.12", "surface_line": line_text["f18r.12"], "segmentation": "... qokchy | cthy", "working_reading_de": "heiß-trockenes Blattgut", "concrete_gain": "dieselbe Teilfamilie nimmt unabhängig einen Qualitätscode", "unit_or_binding": "QUALITY_THEN_PART", "status": "INHERITED_CONTROL"},
        {"case_id": "F45_PART_DIII_PART", "page": "f45v", "locus": "f45v.2", "surface_line": line_text["f45v.2"], "segmentation": "chor | d + aiin | cthy", "working_reading_de": "Blüten-/Pflanzenteil; d-Wert III; Blattgut", "concrete_gain": "daiin ist eine III-markierte Form zwischen zwei Pflanzenteilen, kein leeres Tätigkeitswort", "unit_or_binding": "D_HEAD_AND_DIRECTION_OPEN", "status": "PRIMARY_RESEGMENTED_READING"},
    ]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = safe_pages()
    tokens, token_guard = guarded_query(TOKENS_REL, pages, "page,locus,code,kind,section,language,hand,token_index,eva")
    cross_rows, cross_guard = guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    tokens.sort(key=token_sort_key)
    stable = stable_capacities(cross_rows)
    _, line_text = line_maps(tokens)

    occurrences = make_occurrences(tokens, stable, line_text)
    if any(int(row["working_value"]) > 4 for row in occurrences):
        raise RuntimeError("minim series exceeds four cells")
    totals = make_totals(occurrences)
    profiles = make_profiles(occurrences)
    families, complete = make_families(occurrences)
    mixed = make_mixed_lines(occurrences)
    editions = make_reading_totals(cross_rows)
    quality, quality_matrix = make_quality_compounds(occurrences)
    parts = make_part_compounds(occurrences)
    da = make_da_contexts(occurrences)
    rivals = make_rivals(occurrences, mixed, quality, parts)
    dictionary = make_dictionary()
    cases = make_cases(line_text, quality, parts)

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["occurrences"], occurrences, ("occurrence_id", "page", "locus", "line_number", "token_index", "surface", "head", "written_i_minims", "working_value", "working_roman", "section", "language", "hand", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["totals"], totals, ("working_value", "working_roman", "written_tail", "occurrences", "surfaces", "heads", "pages", "loci", "triple_stable_occurrences", "herbal_occurrences", "line_first", "line_middle", "line_last"))
    write_tsv(ROOT / OUTPUTS["profiles"], profiles, ("dimension", "dimension_value", "occurrences", "count_I", "count_II", "count_III", "count_IV", "III_share_among_II_III", "triple_stable_occurrences"))
    write_tsv(ROOT / OUTPUTS["families"], families, ("head", "surface_I", "surface_II", "surface_III", "surface_IV", "count_I", "count_II", "count_III", "count_IV", "stable_I", "stable_II", "stable_III", "stable_IV", "distinct_values", "present_values", "complete_I_II_III", "complete_I_II_III_IV", "occurrences", "pages", "herbal_occurrences"))
    write_tsv(ROOT / OUTPUTS["complete"], complete, ("head", "surface_I", "surface_II", "surface_III", "surface_IV", "count_I", "count_II", "count_III", "count_IV", "stable_I", "stable_II", "stable_III", "stable_IV", "occurrences", "pages", "herbal_occurrences"))
    write_tsv(ROOT / OUTPUTS["mixed"], mixed, ("mixed_id", "page", "locus", "head", "values", "value_span", "series_surfaces_in_order", "series_token_count", "all_series_tokens_triple_stable", "section", "surface_line"))
    write_tsv(ROOT / OUTPUTS["editions"], editions, ("reading", "reading_role", "working_value", "working_roman", "occurrences", "surfaces", "pages", "loci"))
    write_tsv(ROOT / OUTPUTS["quality"], quality, ("compound_id", "page", "locus", "token_index", "surface", "wrapper", "wrapper_class", "thermal", "moisture", "frame_markers", "state_id", "working_quality_de", "working_value", "working_roman", "working_compound_de", "section", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["quality_matrix"], quality_matrix, ("wrapper_class", "state_id", "working_quality_de", "working_value", "working_roman", "occurrences", "surfaces", "pages", "triple_stable_occurrences"))
    write_tsv(ROOT / OUTPUTS["parts"], parts, ("compound_id", "page", "locus", "token_index", "surface", "wrapper", "part_root", "working_part_de", "working_value", "working_roman", "working_compound_de", "unit_status", "section", "triple_reading_token_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["da"], da, ("occurrence_id", "page", "locus", "line_number", "token_index", "surface", "head", "written_i_minims", "working_value", "working_roman", "section", "language", "hand", "triple_reading_token_stable", "working_default_de", "whole_word_status", "surface_line"))
    write_tsv(ROOT / OUTPUTS["rivals"], rivals, ("rank", "model", "default_reading", "support", "problem", "disposition"))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "scope", "status"))
    write_tsv(ROOT / OUTPUTS["cases"], cases, ("case_id", "page", "locus", "surface_line", "segmentation", "working_reading_de", "concrete_gain", "unit_or_binding", "status"))

    historical, visual = read_tsv(ROOT / HISTORICAL_REL), read_tsv(ROOT / VISUAL_REL)
    totals_by_value = {int(row["working_value"]): row for row in totals}
    da_counts = Counter(int(row["working_value"]) for row in da)
    part_counts = Counter(str(row["part_root"]) for row in parts)
    quality_states = Counter(str(row["state_id"]) for row in quality)
    result = {
        "schema": "GDT626_MINIM_VALUE_LEXICON_RESULT_V1", "experiment_id": "GDT626",
        "status": "FOUR_CELL_MINIM_VALUE_READER__QUALITY_DEGREES_COMPOSE__DAIIN_RESEGMENTED",
        "claim_boundary": "The terminal -an/-ain/-aiin/-aiiin family is a bounded four-cell written paradigm. Its current practical default is value I/II/III/IV by analogy with final-j medieval numeral notation. On inherited quality heads this yields directly predictable Galenic degree compounds; on plant-part heads it yields an amount/dose/degree/class value whose unit remains open. daiin is therefore resegmented as d+III, not translated as an operation or conjunction. The value semantics, d head, absolute unit, language and plaintext remain working hypotheses.",
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN_BEFORE_PAYLOAD", "f84r": "FORBIDDEN_BEFORE_PAYLOAD", "safe_pages": len(pages), "safe_tokens": len(tokens), "token_query": token_guard, "cross_query": cross_guard, "new_image_pages": 0},
        "minim_family": {
            "occurrences": len(occurrences), "heads": len(families), "complete_I_II_III_heads": sum(int(row["complete_I_II_III"]) for row in families),
            "complete_I_II_III_IV_heads": len(complete), "mixed_same_head_lines": len(mixed),
            "stable_mixed_same_head_lines": sum(int(row["all_series_tokens_triple_stable"]) for row in mixed),
            "three_or_more_value_lines": sum(len(str(row["values"]).split("|")) >= 3 for row in mixed),
            "maximum_value": max(int(row["working_value"]) for row in occurrences), "above_IV_occurrences": 0,
            "value_counts": {ROMAN[value]: int(totals_by_value[value]["occurrences"]) for value in range(1, 5)},
            "stable_value_counts": {ROMAN[value]: int(totals_by_value[value]["triple_stable_occurrences"]) for value in range(1, 5)},
            "line_last_counts": {ROMAN[value]: int(totals_by_value[value]["line_last"]) for value in range(1, 5)},
        },
        "numeric_rival": {"model": "lexically or grammatically conditioned four-grade suffix", "reason_retained": "value frequencies and line-edge profiles depend strongly on head, section and hand; a numeric use may coexist with grammatical conditioning", "context_profile_rows": len(profiles), "decisive_future_observation": "an independently countable referent that tracks I-IV under the same head and frame"},
        "quality_value_compounds": {"occurrences": len(quality), "surfaces": len({str(row["surface"]) for row in quality}), "pages": len({str(row["page"]) for row in quality}), "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in quality), "state_counts": dict(sorted(quality_states.items()))},
        "part_value_compounds": {"occurrences": len(parts), "surfaces": len({str(row["surface"]) for row in parts}), "pages": len({str(row["page"]) for row in parts}), "herbal_occurrences": sum(row["section"] == "H" for row in parts), "root_counts": dict(sorted(part_counts.items()))},
        "da_resegmentation": {"occurrences": len(da), "counts": {ROMAN[value]: da_counts[value] for value in range(1, 5)}, "daiin_occurrences": da_counts[3], "working_default": "daiin=d+III; local amount/degree marker; d head unresolved", "operation_status": "DOWNGRADED"},
        "working_lexicon_updates": {"-an": "Wert I", "-ain": "Wert II", "-aiin": "Wert III", "-aiiin": "Wert IV", "qokchain": "heiß-trocken, Grad II", "qokchaiin": "heiß-trocken, Grad III", "qotchain": "kalt-trocken, Grad II", "qotchaiin": "kalt-trocken, Grad III", "cthan_cthain_cthaiin": "Blatt-/oberirdisches Drogengut, Stufe I/II/III; Einheit offen", "daiin": "d-Wert III; nicht automatisch Operation/und/item"},
        "manual_sources": {"historical_numeral_comparators": len(historical), "visual_judgments": len(visual), "concrete_readings": len(cases)},
        "inputs": {str(path): sha256(ROOT / path) for path in (TOKENS_REL, CROSS_REL, ALLOWLIST_REL, GDT623_DICT_REL, GDT624_READER_REL, GDT625_RESULT_REL, HISTORICAL_REL, VISUAL_REL)},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GDT626 built: minim={len(occurrences)} heads={len(families)} complete4={len(complete)} mixed={len(mixed)} quality={len(quality)} parts={len(parts)} daiin={da_counts[3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
