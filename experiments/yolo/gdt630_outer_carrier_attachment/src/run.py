#!/usr/bin/env python3
"""Build GDT630: attach fused and separated OL/OR value expressions to visible parts."""

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
BASE_REL = Path("experiments/yolo/gdt630_outer_carrier_attachment")
ART = ROOT / BASE_REL / "artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
G628 = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts")
ALLOW_REL = G628 / "PAGE_ALLOWLIST.tsv"
G628_RESULT_REL = G628 / "RESULT.json"
G628_PATHS_REL = G628 / "VALUE_REALIZATION_PATHS.tsv"
G628_OL_REL = G628 / "OL_QUALITY_D_VALUE_PHRASES.tsv"
G628_OR_REL = G628 / "OR_CARRIER_D_VALUE_PHRASES.tsv"
G629 = Path("experiments/yolo/gdt629_part_quality_degree_clause/artifacts")
G629_RESULT_REL = G629 / "RESULT.json"
G629_DICT_REL = G629 / "WORKING_DICTIONARY_V6.tsv"
G629_BRIDGES_REL = G629 / "CROSS_READER_BOUNDARY_BRIDGES.tsv"
G625 = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts")
G625_CTH_REL = G625 / "CTH_ROOT_FAMILY.tsv"
G625_CANDIDATES_REL = G625 / "CANDIDATE_TERM_ROLE_SUMMARY.tsv"
G623_DICT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv")
G627_HISTORICAL_REL = Path("experiments/yolo/gdt627_value_head_role_atlas/artifacts/HISTORICAL_SYNTAX_COMPARATORS.tsv")

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "expressions": BASE_REL / "artifacts/VALUE_EXPRESSION_OCCURRENCES.tsv",
    "reader_modes": BASE_REL / "artifacts/CROSS_READER_MODE_EQUIVALENCE.tsv",
    "cell_counterparts": BASE_REL / "artifacts/FUSED_CELL_SEPARATE_COUNTERPARTS.tsv",
    "contacts": BASE_REL / "artifacts/KNOWN_OUTER_PART_CONTACTS.tsv",
    "attachments": BASE_REL / "artifacts/IMMEDIATE_PART_QUALITY_ATTACHMENTS.tsv",
    "neighbors": BASE_REL / "artifacts/OUTER_NEIGHBOR_SUMMARY.tsv",
    "modes": BASE_REL / "artifacts/BOUNDARY_MODE_SUMMARY.tsv",
    "orders": BASE_REL / "artifacts/CLAUSE_ORDER_SUMMARY.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_CLAUSES_V2.tsv",
    "ranking": BASE_REL / "artifacts/OUTER_ATTACHMENT_ROLE_RANKING.tsv",
    "open_candidates": BASE_REL / "artifacts/OPEN_OUTER_HEAD_CANDIDATES.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V7.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

WRAPPERS = ("", "o", "qo")
CORES = ("", "k", "t", "ch", "sh", "kch", "ksh", "tch", "tsh")
ENDINGS = ("ol", "or")
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}
VALUE_TAIL = {value: "a" + "i" * (value - 1) + "n" for value in ROMAN}
D_VALUE = {value: "d" + VALUE_TAIL[value] for value in ROMAN}
INVERSE_D = {surface: value for value, surface in D_VALUE.items()}
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
LATTICE_PARSE = {
    wrapper + core + ending: (wrapper, core, ending)
    for wrapper in WRAPPERS
    for core in CORES
    for ending in ENDINGS
}
FUSED_PARSE = {
    base + D_VALUE[value]: (base, value)
    for base in LATTICE_PARSE
    for value in ROMAN
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
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"] == "f1r" or row["page"].startswith("f84") for row in rows):
        raise RuntimeError("forbidden page materialized")
    return rows, {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}


def line_number(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    if match is None:
        raise ValueError(locus)
    return int(match.group(1))


def token_sort_key(row: dict[str, object]) -> tuple[str, int, int]:
    return str(row["page"]), line_number(str(row["locus"])), int(row["token_index"])


def line_maps(tokens: list[dict[str, object]]) -> tuple[dict[str, list[dict[str, object]]], dict[str, str]]:
    by_line: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        by_line[str(row["locus"])].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    return by_line, {locus: " ".join(str(row["eva"]) for row in line) for locus, line in by_line.items()}


def stable_capacities(cross_rows: list[dict[str, str]]) -> tuple[dict[str, Counter[str]], dict[str, Counter[tuple[str, str]]]]:
    tokens: dict[str, Counter[str]] = {}
    pairs: dict[str, Counter[tuple[str, str]]] = {}
    for row in cross_rows:
        reader_words = [row[field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        token_counts = [Counter(words) for words in reader_words]
        token_universe = set().union(*(counts.keys() for counts in token_counts))
        tokens[row["locus"]] = Counter({
            surface: min(counts[surface] for counts in token_counts)
            for surface in token_universe
            if min(counts[surface] for counts in token_counts) > 0
        })
        pair_counts = [Counter(zip(words, words[1:])) for words in reader_words]
        pair_universe = set().union(*(counts.keys() for counts in pair_counts))
        pairs[row["locus"]] = Counter({
            pair: min(counts[pair] for counts in pair_counts)
            for pair in pair_universe
            if min(counts[pair] for counts in pair_counts) > 0
        })
    return tokens, pairs


def annotate_stability(
    tokens: list[dict[str, str]],
    token_caps: dict[str, Counter[str]],
    pair_caps: dict[str, Counter[tuple[str, str]]],
) -> list[dict[str, object]]:
    token_ordinals: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, object]] = []
    for source in sorted(tokens, key=token_sort_key):
        row: dict[str, object] = dict(source)
        key = source["locus"], source["eva"]
        token_ordinals[key] += 1
        row["triple_reading_token_stable"] = int(token_ordinals[key] <= token_caps.get(source["locus"], Counter())[source["eva"]])
        rows.append(row)
    by_line, _line_text = line_maps(rows)
    for locus, line in by_line.items():
        pair_ordinals: Counter[tuple[str, str]] = Counter()
        for left, right in zip(line, line[1:]):
            pair = str(left["eva"]), str(right["eva"])
            pair_ordinals[pair] += 1
            left["right_pair_triple_stable"] = int(pair_ordinals[pair] <= pair_caps.get(locus, Counter())[pair])
        if line:
            line[-1]["right_pair_triple_stable"] = 0
    return rows


def wrapper_de(wrapper: str) -> str:
    return {"": "unmarkiert", "o": "im o-Rahmen", "qo": "im qo-Qualitätsrahmen"}[wrapper]


def expression_class(core: str, ending: str) -> str:
    if ending == "ol" and core:
        return "CORE_BEARING_OL_QUALITY"
    if ending == "ol":
        return "BARE_OL_CARRIER"
    return "OR_NOMINAL_OR_PART_CARRIER"


def quality_reading(wrapper: str, core: str, ending: str, roman: str) -> str:
    if ending == "ol" and core:
        if wrapper:
            return f"{wrapper_de(wrapper)}: {CORE_DE[core]}, Grad {roman}"
        return f"{CORE_DE[core]}, Grad {roman}"
    if ending == "ol":
        return f"Qualitäts-/Materialträger, Wert {roman}; Kern offen"
    return f"Teil-/Nominalträger, Wert {roman}; Qualität offen"


def known_part_map() -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for row in read_tsv(ROOT / G625_CTH_REL):
        surface = row["surface"]
        mapping[surface] = {
            "role": "BLATT_KRAUTTEIL_FAMILY",
            "noun_de": "Blatt-/Krautteilform",
            "status": row["status"],
            "provenance": "GDT625_CTH_ROOT_FAMILY",
        }
    mapping["cthy"] = {
        "role": "BLATTGUT",
        "noun_de": "Blattgut/Blattdroge",
        "status": "PRIMARY_CTHY_FORM",
        "provenance": "GDT625_CTH_ROOT_FAMILY",
    }
    mapping["chor"] = {
        "role": "PFLANZEN_REPRODUKTIONSTEIL",
        "noun_de": "Pflanzen-/Reproduktionsteil",
        "status": "INHERITED_CONTEXT_SPLIT",
        "provenance": "GDT629_WORKING_DICTIONARY_V6",
    }
    mapping["shor"] = {
        "role": "BLUETEN_FRUCHTSTAND",
        "noun_de": "Blüten-/Fruchtstand",
        "status": "INHERITED_CONTEXT_SPLIT",
        "provenance": "GDT629_WORKING_DICTIONARY_V6",
    }
    candidate_rows = {row["surface"]: row for row in read_tsv(ROOT / G625_CANDIDATES_REL)}
    for surface, noun, role in (("dair", "Wurzelteil/Radix", "WURZELTEIL"), ("sair", "Wurzelteil", "WURZELTEIL_WEAK")):
        source = candidate_rows[surface]
        mapping[surface] = {
            "role": role,
            "noun_de": noun,
            "status": source["status"],
            "provenance": "GDT625_CANDIDATE_TERM_ROLE_SUMMARY",
        }
    mapping["kooiin"] = {
        "role": "WURZELDROGE_SUBCLASS",
        "noun_de": "dicke/kriechende Wurzeldroge",
        "status": "CONCRETE_VISUAL_DEFAULT_MEDIUM",
        "provenance": "GDT623_WORKING_DICTIONARY_V2",
    }
    for surface in ("pdrairdy", "podairol", "podair", "pdair", "pdsairy"):
        mapping[surface] = {
            "role": "WURZELDROGEN_EINTRAG",
            "noun_de": "Wurzelteil/Wurzeldrogen-Eintrag",
            "status": "CONCRETE_VISUAL_DEFAULT_MEDIUM",
            "provenance": "GDT623_WORKING_DICTIONARY_V2",
        }
    return mapping


def contains_ngram(words: list[str], target: list[str]) -> bool:
    return any(words[index:index + len(target)] == target for index in range(max(0, len(words) - len(target) + 1)))


def contains_concatenated_span(words: list[str], target: str) -> bool:
    for start in range(len(words)):
        joined = ""
        for end in range(start, len(words)):
            joined += words[end]
            if joined == target:
                return True
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return False


def make_expressions(
    by_line: dict[str, list[dict[str, object]]],
    line_text: dict[str, str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locus, line in by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface in FUSED_PARSE:
                base, value = FUSED_PARSE[surface]
                mode, end = "FUSED_D_VALUE", index + 1
                expression = surface
                stable = int(token["triple_reading_token_stable"])
            elif surface in LATTICE_PARSE and index + 1 < len(line) and str(line[index + 1]["eva"]) in INVERSE_D:
                base, value = surface, INVERSE_D[str(line[index + 1]["eva"])]
                mode, end = "SEPARATE_D_VALUE", index + 2
                expression = f"{surface} {line[index + 1]['eva']}"
                stable = int(token["right_pair_triple_stable"])
            else:
                continue
            wrapper, core, ending = LATTICE_PARSE[base]
            context = {}
            for distance in (1, 2, 3):
                left_index, right_index = index - distance, end - 1 + distance
                context[f"left_{distance}"] = str(line[left_index]["eva"]) if left_index >= 0 else "<START>"
                context[f"right_{distance}"] = str(line[right_index]["eva"]) if right_index < len(line) else "<END>"
            rows.append({
                "expression_id": "", "page": token["page"], "locus": locus,
                "token_index_start": int(token["token_index"]), "token_index_end": int(line[end - 1]["token_index"]),
                "realization_mode": mode, "base_surface": base, "wrapper": wrapper or "BARE",
                "quality_core": core or "NONE", "ending": ending.upper(),
                "expression_class": expression_class(core, ending), "working_value": value,
                "working_roman": ROMAN[value], "surface_expression": expression,
                "segmentation": f"{base}+d+a+{ROMAN[value]}" if mode == "FUSED_D_VALUE" else f"{base} | d+a+{ROMAN[value]}",
                "working_reading_de": quality_reading(wrapper, core, ending, ROMAN[value]),
                "core_quality_concrete": int(bool(core) and ending == "ol"),
                "expression_triple_reader_stable": stable,
                "phrase_line_end": int(end == len(line)), "section": token["section"], "hand": token["hand"],
                **context, "surface_line": line_text[locus],
            })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), int(row["token_index_start"])))
    for index, row in enumerate(rows, 1):
        row["expression_id"] = f"G630-E{index:03d}"
    return rows


def make_contacts(
    expressions: list[dict[str, object]],
    known_parts: dict[str, dict[str, str]],
    cross_by_locus: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    contacts: list[dict[str, object]] = []
    attachments: list[dict[str, object]] = []
    readers = ("zl3b_clean", "it2a_clean", "rf1b_clean")
    for expression in expressions:
        for side in ("LEFT", "RIGHT"):
            for distance in (1, 2, 3):
                surface = str(expression[f"{side.lower()}_{distance}"])
                if surface not in known_parts:
                    continue
                part = known_parts[surface]
                order = "PART_BEFORE_VALUE_EXPRESSION" if side == "LEFT" else "VALUE_EXPRESSION_BEFORE_PART"
                immediate = int(distance == 1)
                concrete = int(immediate and int(expression["core_quality_concrete"]))
                if side == "LEFT":
                    clause_tokens = [surface] + str(expression["surface_expression"]).split()
                    normalized_clause = surface + str(expression["surface_expression"]).replace(" ", "")
                else:
                    clause_tokens = str(expression["surface_expression"]).split() + [surface]
                    normalized_clause = str(expression["surface_expression"]).replace(" ", "") + surface
                cross = cross_by_locus[str(expression["locus"])]
                exact_stable = int(all(contains_ngram(cross[field].split(), clause_tokens) for field in readers))
                normalized_stable = int(all(contains_concatenated_span(cross[field].split(), normalized_clause) for field in readers))
                if concrete:
                    reading = f"{part['noun_de']}: {expression['working_reading_de']}"
                    evidence = "IMMEDIATE_CONCRETE_PART_QUALITY_DEGREE_CLAUSE"
                elif immediate:
                    reading = f"{part['noun_de']}: {expression['working_reading_de']}"
                    evidence = "IMMEDIATE_PART_WITH_OPEN_VALUE_HEAD"
                else:
                    reading = f"{part['noun_de']} nahe {expression['working_reading_de']}; Bindung offen"
                    evidence = "NEAR_PART_CONTACT__NO_BINDING_ASSUMED"
                row: dict[str, object] = {
                    "contact_id": "", "expression_id": expression["expression_id"], "page": expression["page"],
                    "locus": expression["locus"], "realization_mode": expression["realization_mode"],
                    "base_surface": expression["base_surface"], "working_roman": expression["working_roman"],
                    "part_surface": surface, "part_role": part["role"], "part_status": part["status"],
                    "part_provenance": part["provenance"], "side": side, "distance": distance, "order": order,
                    "immediate": immediate, "core_quality_concrete": expression["core_quality_concrete"],
                    "surface_clause": " ".join(clause_tokens), "normalized_clause": normalized_clause,
                    "working_reading_de": reading,
                    "dose_rival_de": f"{part['noun_de']}: {expression['working_value']} Portionen/Maße oder Qualitätsgrad {expression['working_roman']}",
                    "exact_clause_triple_reader_stable": exact_stable,
                    "boundary_normalized_clause_triple_reader_stable": normalized_stable,
                    "evidence_class": evidence, "surface_line": expression["surface_line"],
                }
                contacts.append(row)
                if concrete:
                    attachments.append(dict(row))
    contacts.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), int(row["distance"]), str(row["side"]), str(row["part_surface"])))
    for index, row in enumerate(contacts, 1):
        row["contact_id"] = f"G630-P{index:03d}"
    attachment_keys = {(str(row["expression_id"]), str(row["side"]), int(row["distance"]), str(row["part_surface"])): row["contact_id"] for row in contacts}
    for row in attachments:
        row["contact_id"] = attachment_keys[(str(row["expression_id"]), str(row["side"]), int(row["distance"]), str(row["part_surface"]))]
    attachments.sort(key=lambda row: str(row["contact_id"]))
    return contacts, attachments


def reader_realization_mode(words: list[str], base: str, value: int) -> str:
    fused = base + D_VALUE[value] in words
    separate = any(left == base and right == D_VALUE[value] for left, right in zip(words, words[1:]))
    if fused and separate:
        return "BOTH"
    if fused:
        return "FUSED_D_VALUE"
    if separate:
        return "SEPARATE_D_VALUE"
    if contains_concatenated_span(words, base + D_VALUE[value]):
        return "OTHER_BOUNDARY_SAME_SURFACE"
    return "ABSENT_OR_DIFFERENT"


def make_reader_modes(
    expressions: list[dict[str, object]],
    cross_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    reader_fields = (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
    for expression in expressions:
        cross = cross_by_locus[str(expression["locus"])]
        modes = {
            reader: reader_realization_mode(cross[field].split(), str(expression["base_surface"]), int(expression["working_value"]))
            for reader, field in reader_fields
        }
        source_mode = str(expression["realization_mode"])
        alternate_mode = "SEPARATE_D_VALUE" if source_mode == "FUSED_D_VALUE" else "FUSED_D_VALUE"
        normalized_stable = int(all(mode != "ABSENT_OR_DIFFERENT" for mode in modes.values()))
        exact_source_stable = int(all(mode in {source_mode, "BOTH"} for mode in modes.values()))
        alternate_reader_present = int(any(mode in {alternate_mode, "BOTH"} for mode in modes.values()))
        rows.append({
            "expression_id": expression["expression_id"], "page": expression["page"], "locus": expression["locus"],
            "source_mode": source_mode, "base_surface": expression["base_surface"],
            "working_roman": expression["working_roman"], "surface_expression": expression["surface_expression"],
            "zl3b_mode": modes["ZL3b"], "it2a_mode": modes["IT2a"], "rf1b_mode": modes["RF1b"],
            "exact_source_mode_triple_reader": exact_source_stable,
            "boundary_normalized_triple_reader": normalized_stable,
            "alternate_boundary_reader_present": alternate_reader_present,
            "boundary_variant_with_normalized_support": int(normalized_stable and alternate_reader_present),
        })
    return rows


def make_cell_counterparts(
    expressions: list[dict[str, object]],
    attachments: list[dict[str, object]],
    reader_modes: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_cell: dict[tuple[str, int], dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
    for row in expressions:
        by_cell[str(row["base_surface"]), int(row["working_value"])][str(row["realization_mode"])].append(row)
    attachment_counts = Counter(str(row["expression_id"]) for row in attachments)
    reader_by_id = {str(row["expression_id"]): row for row in reader_modes}
    rows: list[dict[str, object]] = []
    for (base, value), modes in sorted(by_cell.items()):
        fused = modes.get("FUSED_D_VALUE", [])
        if not fused:
            continue
        separate = modes.get("SEPARATE_D_VALUE", [])
        wrapper, core, ending = LATTICE_PARSE[base]
        shared: list[str] = []
        for side in ("left_1", "right_1"):
            fused_neighbors = {str(row[side]) for row in fused if not str(row[side]).startswith("<")}
            separate_neighbors = {str(row[side]) for row in separate if not str(row[side]).startswith("<")}
            shared.extend(f"{side.upper()}:{surface}" for surface in sorted(fused_neighbors & separate_neighbors))
        rows.append({
            "base_surface": base, "working_value": value, "working_roman": ROMAN[value],
            "expression_class": expression_class(core, ending),
            "fused_surface": base + D_VALUE[value], "separate_surface": f"{base} {D_VALUE[value]}",
            "fused_occurrences": len(fused), "fused_pages": len({str(row["page"]) for row in fused}),
            "separate_occurrences": len(separate), "separate_pages": len({str(row["page"]) for row in separate}),
            "fused_exact_triple_reader": sum(int(reader_by_id[str(row["expression_id"])]["exact_source_mode_triple_reader"]) for row in fused),
            "fused_boundary_normalized_triple_reader": sum(int(reader_by_id[str(row["expression_id"])]["boundary_normalized_triple_reader"]) for row in fused),
            "fused_boundary_variant_loci": sum(int(reader_by_id[str(row["expression_id"])]["alternate_boundary_reader_present"]) for row in fused),
            "fused_immediate_part_attachments": sum(attachment_counts[str(row["expression_id"])] for row in fused),
            "separate_immediate_part_attachments": sum(attachment_counts[str(row["expression_id"])] for row in separate),
            "shared_lexical_immediate_neighbors": "|".join(shared) or "NONE",
            "fused_example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in fused[:8])),
            "separate_example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in separate[:8])) or "NONE",
        })
    return rows


def make_neighbor_summary(
    expressions: list[dict[str, object]],
    known_parts: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for expression in expressions:
        for side in ("LEFT", "RIGHT"):
            surface = str(expression[f"{side.lower()}_1"])
            grouped[surface, side].append(expression)
    rows: list[dict[str, object]] = []
    for (surface, side), selected in grouped.items():
        modes = Counter(str(row["realization_mode"]) for row in selected)
        part = known_parts.get(surface)
        rows.append({
            "surface": surface, "side": side, "occurrences": len(selected),
            "pages": len({str(row["page"]) for row in selected}),
            "fused_occurrences": modes["FUSED_D_VALUE"], "separate_occurrences": modes["SEPARATE_D_VALUE"],
            "cross_mode": int(modes["FUSED_D_VALUE"] > 0 and modes["SEPARATE_D_VALUE"] > 0),
            "core_quality_occurrences": sum(int(row["core_quality_concrete"]) for row in selected),
            "known_part_role": part["role"] if part else "OPEN",
            "known_part_status": part["status"] if part else "OPEN",
            "example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in selected[:8])),
        })
    rows.sort(key=lambda row: (-int(row["known_part_role"] != "OPEN"), -int(row["cross_mode"]), -int(row["occurrences"]), str(row["surface"]), str(row["side"])))
    return rows


def make_mode_summary(expressions: list[dict[str, object]], attachments: list[dict[str, object]]) -> list[dict[str, object]]:
    attachment_ids = Counter(str(row["expression_id"]) for row in attachments)
    rows: list[dict[str, object]] = []
    for mode in ("FUSED_D_VALUE", "SEPARATE_D_VALUE"):
        for klass in ("CORE_BEARING_OL_QUALITY", "BARE_OL_CARRIER", "OR_NOMINAL_OR_PART_CARRIER"):
            selected = [row for row in expressions if row["realization_mode"] == mode and row["expression_class"] == klass]
            rows.append({
                "realization_mode": mode, "expression_class": klass, "occurrences": len(selected),
                "pages": len({str(row["page"]) for row in selected}),
                "triple_reader_stable_occurrences": sum(int(row["expression_triple_reader_stable"]) for row in selected),
                "immediate_concrete_part_attachments": sum(attachment_ids[str(row["expression_id"])] for row in selected),
                "example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in selected[:8])) or "NONE",
            })
    return rows


def make_order_summary(attachments: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in attachments:
        grouped[str(row["realization_mode"]), str(row["order"])].append(row)
    rows: list[dict[str, object]] = []
    for (mode, order), selected in sorted(grouped.items()):
        rows.append({
            "realization_mode": mode, "order": order, "clauses": len(selected),
            "pages": len({str(row["page"]) for row in selected}),
            "exact_triple_reader_clauses": sum(int(row["exact_clause_triple_reader_stable"]) for row in selected),
            "boundary_normalized_triple_reader_clauses": sum(int(row["boundary_normalized_clause_triple_reader_stable"]) for row in selected),
            "part_surfaces": "|".join(sorted({str(row["part_surface"]) for row in selected})),
            "example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in selected[:8])),
        })
    return rows


def make_cases(attachments: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = [row for row in attachments if int(row["boundary_normalized_clause_triple_reader_stable"])]
    rows: list[dict[str, object]] = []
    for index, row in enumerate(selected, 1):
        rows.append({
            "case_id": f"G630-C{index:02d}", "page": row["page"], "locus": row["locus"],
            "surface_clause": row["surface_clause"], "realization_mode": row["realization_mode"],
            "order": row["order"], "working_reading_de": row["working_reading_de"],
            "dose_rival_de": row["dose_rival_de"],
            "reader_status": "TRIPLE_EXACT" if int(row["exact_clause_triple_reader_stable"]) else "TRIPLE_BOUNDARY_NORMALIZED",
            "residual_policy": "Tokens außerhalb der kleinsten Klammer bleiben sichtbar und OPEN",
        })
    return rows


def make_ranking() -> list[dict[str, object]]:
    return [
        {"rank": 1, "model": "BILATERAL_PART_QUALITY_DEGREE_CELLS", "working_model_de": "Pflanzenteil und Qualitätsgrad können in beiden Oberflächenreihenfolgen eine lokale Zelle bilden", "support": "cthy steht vor qokol daiin und nach chol daiin; f8 verbindet sholdaiin/shol daiin direkt mit shor", "counterevidence": "Adjazenz kann zwei benachbarte technische Zellen statt Nominalsyntax verbinden", "disposition": "PRIMARY_WORKING_ATTACHMENT"},
        {"rank": 2, "model": "ADJACENT_INDEPENDENT_TECHNICAL_CELLS", "working_model_de": "Partslot und Qualitätsfeld sind benachbarte, aber separat lesbare Tabellenzellen", "support": "beide Reihenfolgen und Wiederholung von cthy passen zu zelliger Notation", "counterevidence": "wiederkehrende unmittelbare und leserstabile Paarungen erlauben eine gemeinsame fluente Klausel", "disposition": "LIVE_LAYOUT_RIVAL"},
        {"rank": 3, "model": "PART_OR_MATERIAL_PLUS_DOSE", "working_model_de": "Pflanzenteil oder Qualitätsgut mit N Portionen", "support": "Ingredienz-Einheit-Zahl ist historisch echt und getrennte d-Werte erlauben sie", "counterevidence": "direkte und fusionierte Qualitätswerte sowie heiß/kalt/trocken/feucht-Parallelen brauchen keine wechselnde Einheit", "disposition": "LIVE_SEPARATE_FORM_RIVAL"},
        {"rank": 4, "model": "GENERIC_OPERATION_PROSE", "working_model_de": "nimm, arbeite, halte oder leite weiter", "support": "keiner", "counterevidence": "liefert weder Part-, Qualitäts-, Grad- noch Grenzvorhersagen", "disposition": "REJECTED_AS_DEFAULT"},
    ]


def make_open_candidates(neighbors: list[dict[str, object]]) -> list[dict[str, object]]:
    lookup = {(str(row["surface"]), str(row["side"])): row for row in neighbors}
    specs = (
        (1, "chcthy", "LEFT", "ch+cthy = trockenes Blattgut", "zweimal unmittelbar vor kernhaltigem OL-Grad III; f45r.3 chcthy kchol daiin ist dreifach exakt", "f19v.4 verliert in RF1b das d; ch vor cthy ist außerhalb dieses Slots noch nicht produktiv bewiesen", "NEXT_COMPOSITION_TARGET"),
        (2, "qotor", "LEFT", "wiederkehrender nominaler Zutaten-/Materialkopf; genaue Bedeutung offen", "zweimal unmittelbar vor chol daiin", "OR-Form und Dosislesung bleiben offen; keine konkrete Partbedeutung", "KEEP_OPEN_RECURRENT_HEAD"),
        (3, "chol", "LEFT", "vorangehende trockene Qualitäts-/Materialzelle", "sieben unmittelbare Vorkommen und beide Spacingmodi", "Wiederholung verlangt mehrere Zellen; chol ist dadurch kein neuer Stoffkopf", "MULTI_CELL_NOT_NEW_NOUN"),
        (4, "dy", "LEFT", "möglicher struktureller Bindungs-/Abschlussrahmen", "kommt in fusioniertem und getrenntem Modus vor", "keine konkrete Stoff- oder Partbedeutung", "STRUCTURAL_OPEN"),
    )
    rows: list[dict[str, object]] = []
    for rank, surface, side, hypothesis, support, limitation, disposition in specs:
        source = lookup[surface, side]
        rows.append({
            "rank": rank, "surface": surface, "side": side, "occurrences": source["occurrences"],
            "pages": source["pages"], "fused_occurrences": source["fused_occurrences"],
            "separate_occurrences": source["separate_occurrences"], "core_quality_occurrences": source["core_quality_occurrences"],
            "working_hypothesis_de": hypothesis, "support": support, "limitation": limitation,
            "disposition": disposition, "example_loci": source["example_loci"],
        })
    return rows


def make_dictionary(old: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict(row) for row in old]
    rows.extend([
        {"entry": "sholdaiin|shol daiin", "kind": "MOIST_III_BOUNDARY_EQUIVALENCE", "working_meaning_de": "feucht, Grad III", "composition": "sh+ol+d+a+III | sh+ol | d+a+III", "context_rule": "f8r.9 wechselt am selben Span nur die Leser-Wortgrenze", "status": "NEW_EXACT_BOUNDARY_BRIDGE"},
        {"entry": "sholdaiin shor|shol daiin shor", "kind": "POSTPOSED_REPRODUCTIVE_PART_CLAUSE", "working_meaning_de": "Blüten-/Fruchtstand: feucht, Grad III", "composition": "sh+ol(+|space)d+a+III | shor", "context_rule": "f8r.9 dreifach grenznormalisiert; Qualität steht vor Part", "status": "NEW_PRIMARY_CLAUSE"},
        {"entry": "chol daiin cthy", "kind": "POSTPOSED_LEAF_PART_CLAUSE", "working_meaning_de": "Blattgut/Blattdroge: trocken, Grad III", "composition": "ch+ol | d+a+III | cthy", "context_rule": "f3r.3 dreifach exakt; f15v.11 Zielspan ebenfalls dreifach exakt", "status": "NEW_PRIMARY_CLAUSE"},
        {"entry": "cthy qokol daiin", "kind": "PREPOSED_LEAF_PART_CLAUSE", "working_meaning_de": "Blattgut/Blattdroge: im qo-Rahmen heiß, Grad III", "composition": "cthy | qo+k+ol | d+a+III", "context_rule": "f22v.8 dreifach exakt; Part steht vor Qualität", "status": "NEW_PRIMARY_CLAUSE"},
        {"entry": "OL_QUALITY dN CTH_PART", "kind": "POSTPOSED_PART_FRAME", "working_meaning_de": "Blatt-/Krautteilform: Qualität im Grad N", "composition": "QUALITY_CORE+ol | d+a+N | cth*", "context_rule": "nur bei unmittelbar sichtbarem cth-Partslot; Rest bleibt OPEN", "status": "NEW_COMPOSITIONAL_FRAME"},
        {"entry": "CTH_PART OL_QUALITY dN", "kind": "PREPOSED_PART_FRAME", "working_meaning_de": "Blatt-/Krautteilform: Qualität im Grad N", "composition": "cth* | QUALITY_CORE+ol | d+a+N", "context_rule": "nur bei unmittelbar sichtbarem cth-Partslot; Rest bleibt OPEN", "status": "NEW_COMPOSITIONAL_FRAME"},
    ])
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains forbidden page")
    token_rows, token_stats = guarded_query(TOKENS_REL, pages, "page,locus,token_index,eva,section,hand")
    cross_rows, cross_stats = guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    token_caps, pair_caps = stable_capacities(cross_rows)
    tokens = annotate_stability(token_rows, token_caps, pair_caps)
    by_line, line_text = line_maps(tokens)
    known_parts = known_part_map()
    expressions = make_expressions(by_line, line_text)
    contacts, attachments = make_contacts(expressions, known_parts, cross_by_locus)
    reader_modes = make_reader_modes(expressions, cross_by_locus)
    cell_counterparts = make_cell_counterparts(expressions, attachments, reader_modes)
    neighbors = make_neighbor_summary(expressions, known_parts)
    mode_summary = make_mode_summary(expressions, attachments)
    order_summary = make_order_summary(attachments)
    cases = make_cases(attachments)
    ranking = make_ranking()
    open_candidates = make_open_candidates(neighbors)
    dictionary = make_dictionary(read_tsv(ROOT / G629_DICT_REL))

    mode_counts = Counter(str(row["realization_mode"]) for row in expressions)
    class_counts = Counter(str(row["expression_class"]) for row in expressions)
    fused_class_counts = Counter(str(row["expression_class"]) for row in expressions if row["realization_mode"] == "FUSED_D_VALUE")
    separate_class_counts = Counter(str(row["expression_class"]) for row in expressions if row["realization_mode"] == "SEPARATE_D_VALUE")
    if mode_counts != Counter({"FUSED_D_VALUE": 15, "SEPARATE_D_VALUE": 120}):
        raise RuntimeError(f"unexpected mode counts {mode_counts}")
    expected_fused = {"CORE_BEARING_OL_QUALITY": 6, "BARE_OL_CARRIER": 8, "OR_NOMINAL_OR_PART_CARRIER": 1}
    expected_separate = {"CORE_BEARING_OL_QUALITY": 80, "BARE_OL_CARRIER": 11, "OR_NOMINAL_OR_PART_CARRIER": 29}
    if dict(fused_class_counts) != expected_fused or dict(separate_class_counts) != expected_separate:
        raise RuntimeError(f"unexpected class split {fused_class_counts} {separate_class_counts}")
    reader_mode_counts = {
        mode: {
            "exact_source_mode_triple_reader": sum(int(row["exact_source_mode_triple_reader"]) for row in reader_modes if row["source_mode"] == mode),
            "boundary_normalized_triple_reader": sum(int(row["boundary_normalized_triple_reader"]) for row in reader_modes if row["source_mode"] == mode),
            "alternate_boundary_reader_present": sum(int(row["alternate_boundary_reader_present"]) for row in reader_modes if row["source_mode"] == mode),
            "boundary_variant_with_normalized_support": sum(int(row["boundary_variant_with_normalized_support"]) for row in reader_modes if row["source_mode"] == mode),
        }
        for mode in ("FUSED_D_VALUE", "SEPARATE_D_VALUE")
    }
    if reader_mode_counts != {
        "FUSED_D_VALUE": {"exact_source_mode_triple_reader": 9, "boundary_normalized_triple_reader": 13, "alternate_boundary_reader_present": 5, "boundary_variant_with_normalized_support": 4},
        "SEPARATE_D_VALUE": {"exact_source_mode_triple_reader": 93, "boundary_normalized_triple_reader": 98, "alternate_boundary_reader_present": 4, "boundary_variant_with_normalized_support": 4},
    }:
        raise RuntimeError(f"unexpected cross-reader mode counts {reader_mode_counts}")
    if len(cell_counterparts) != 6 or sum(int(row["separate_occurrences"]) for row in cell_counterparts) != 56:
        raise RuntimeError("fused-cell counterpart coverage changed")

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["expressions"], expressions, (
        "expression_id", "page", "locus", "token_index_start", "token_index_end", "realization_mode",
        "base_surface", "wrapper", "quality_core", "ending", "expression_class", "working_value", "working_roman",
        "surface_expression", "segmentation", "working_reading_de", "core_quality_concrete",
        "expression_triple_reader_stable", "phrase_line_end", "left_3", "left_2", "left_1", "right_1", "right_2", "right_3",
        "section", "hand", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["reader_modes"], reader_modes, (
        "expression_id", "page", "locus", "source_mode", "base_surface", "working_roman", "surface_expression",
        "zl3b_mode", "it2a_mode", "rf1b_mode", "exact_source_mode_triple_reader",
        "boundary_normalized_triple_reader", "alternate_boundary_reader_present", "boundary_variant_with_normalized_support",
    ))
    write_tsv(ROOT / OUTPUTS["cell_counterparts"], cell_counterparts, (
        "base_surface", "working_value", "working_roman", "expression_class", "fused_surface", "separate_surface",
        "fused_occurrences", "fused_pages", "separate_occurrences", "separate_pages", "fused_exact_triple_reader",
        "fused_boundary_normalized_triple_reader", "fused_boundary_variant_loci", "fused_immediate_part_attachments",
        "separate_immediate_part_attachments", "shared_lexical_immediate_neighbors", "fused_example_loci", "separate_example_loci",
    ))
    contact_fields = (
        "contact_id", "expression_id", "page", "locus", "realization_mode", "base_surface", "working_roman",
        "part_surface", "part_role", "part_status", "part_provenance", "side", "distance", "order", "immediate",
        "core_quality_concrete", "surface_clause", "normalized_clause", "working_reading_de", "dose_rival_de",
        "exact_clause_triple_reader_stable", "boundary_normalized_clause_triple_reader_stable", "evidence_class", "surface_line",
    )
    write_tsv(ROOT / OUTPUTS["contacts"], contacts, contact_fields)
    write_tsv(ROOT / OUTPUTS["attachments"], attachments, contact_fields)
    write_tsv(ROOT / OUTPUTS["neighbors"], neighbors, (
        "surface", "side", "occurrences", "pages", "fused_occurrences", "separate_occurrences", "cross_mode",
        "core_quality_occurrences", "known_part_role", "known_part_status", "example_loci",
    ))
    write_tsv(ROOT / OUTPUTS["modes"], mode_summary, (
        "realization_mode", "expression_class", "occurrences", "pages", "triple_reader_stable_occurrences",
        "immediate_concrete_part_attachments", "example_loci",
    ))
    write_tsv(ROOT / OUTPUTS["orders"], order_summary, (
        "realization_mode", "order", "clauses", "pages", "exact_triple_reader_clauses",
        "boundary_normalized_triple_reader_clauses", "part_surfaces", "example_loci",
    ))
    write_tsv(ROOT / OUTPUTS["cases"], cases, (
        "case_id", "page", "locus", "surface_clause", "realization_mode", "order", "working_reading_de",
        "dose_rival_de", "reader_status", "residual_policy",
    ))
    write_tsv(ROOT / OUTPUTS["ranking"], ranking, ("rank", "model", "working_model_de", "support", "counterevidence", "disposition"))
    write_tsv(ROOT / OUTPUTS["open_candidates"], open_candidates, (
        "rank", "surface", "side", "occurrences", "pages", "fused_occurrences", "separate_occurrences",
        "core_quality_occurrences", "working_hypothesis_de", "support", "limitation", "disposition", "example_loci",
    ))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    output_hashes = {
        str(path): sha256(ROOT / path)
        for key, path in OUTPUTS.items()
        if key != "result"
    }
    input_paths = (
        TOKENS_REL, CROSS_REL, ALLOW_REL, G628_RESULT_REL, G628_PATHS_REL, G628_OL_REL, G628_OR_REL,
        G629_RESULT_REL, G629_DICT_REL, G629_BRIDGES_REL, G625_CTH_REL, G625_CANDIDATES_REL, G623_DICT_REL,
        G627_HISTORICAL_REL,
    )
    result_core = {
        "schema": "GDT630_OUTER_CARRIER_ATTACHMENT_RESULT_V1",
        "experiment_id": "GDT630",
        "status": "BILATERAL_PART_QUALITY_DEGREE_FRAMES__F8_MOIST_III_REPRODUCTIVE_PART_BOUNDARY_BRIDGE",
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
            "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats,
        },
        "value_expressions": {
            "occurrences": len(expressions), "mode_counts": dict(sorted(mode_counts.items())),
            "class_counts": dict(sorted(class_counts.items())),
            "fused_class_counts": dict(sorted(fused_class_counts.items())),
            "separate_class_counts": dict(sorted(separate_class_counts.items())),
            "triple_reader_stable_expressions": sum(int(row["expression_triple_reader_stable"]) for row in expressions),
        },
        "cross_reader_boundary": {
            "mode_counts": reader_mode_counts,
            "fused_cells": len(cell_counterparts),
            "fused_cells_with_separate_counterpart": sum(int(row["separate_occurrences"]) > 0 for row in cell_counterparts),
            "separate_counterpart_occurrences": sum(int(row["separate_occurrences"]) for row in cell_counterparts),
            "cells_with_shared_lexical_immediate_neighbor": sum(row["shared_lexical_immediate_neighbors"] != "NONE" for row in cell_counterparts),
        },
        "outer_attachment": {
            "known_contacts_within_three": len(contacts),
            "immediate_concrete_attachments": len(attachments),
            "attachment_pages": len({str(row["page"]) for row in attachments}),
            "exact_triple_reader_clauses": sum(int(row["exact_clause_triple_reader_stable"]) for row in attachments),
            "boundary_normalized_triple_reader_clauses": sum(int(row["boundary_normalized_clause_triple_reader_stable"]) for row in attachments),
            "order_counts": dict(sorted(Counter(str(row["order"]) for row in attachments).items())),
            "mode_counts": dict(sorted(Counter(str(row["realization_mode"]) for row in attachments).items())),
            "part_surface_counts": dict(sorted(Counter(str(row["part_surface"]) for row in attachments).items())),
        },
        "key_clauses": {
            "f8r_9": "sholdaiin shor | shol daiin shor = Blüten-/Fruchtstand: feucht, Grad III",
            "f3r_3": "chol daiin cthy = Blattgut/Blattdroge: trocken, Grad III",
            "f15v_11": "chol daiin cthy = Blattgut/Blattdroge: trocken, Grad III",
            "f22v_8": "cthy qokol daiin = Blattgut/Blattdroge: im qo-Rahmen heiß, Grad III",
        },
        "working_grammar": {
            "preposed_part": "PART | OL_QUALITY | d+a+N",
            "postposed_part": "OL_QUALITY | d+a+N | PART",
            "fused_quality": "OL_QUALITY+d+a+N | PART",
            "interpretation": "visible part and quality-degree cells can pair on either side; fluent German puts the part first",
            "layout_rival": "the two visible cells may be adjacent technical entries rather than noun syntax",
        },
        "working_dictionary": {"entries": len(dictionary), "inherited_v6": 32, "new_v7": len(dictionary) - 32},
        "manual_models": {"role_rankings": len(ranking), "concrete_cases": len(cases), "open_outer_head_candidates": len(open_candidates)},
        "claim_boundary": "The 15 fused and 120 separated carrier-value expressions split into only 6 fused and 80 separated core-bearing OL quality phrases; the remainder have bare or OR heads and stay semantically open. Immediate visible part heads produce bilateral working clauses, including triple-exact chol daiin cthy and cthy qokol daiin plus the f8 same-span sholdaiin/shol daiin shor boundary bridge. Adjacency-as-separate-cells and dose remain live rivals; no distant token is bound and no surrounding line is generically translated.",
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"GDT630 built: expressions={len(expressions)} modes={dict(mode_counts)} classes={dict(class_counts)} "
        f"contacts={len(contacts)} attachments={len(attachments)} cases={len(cases)} dictionary={len(dictionary)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
