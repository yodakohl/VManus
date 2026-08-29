#!/usr/bin/env python3
"""Build GDT629: part-quality-degree clauses and cross-reader spacing bridges."""

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
BASE_REL = Path("experiments/yolo/gdt629_part_quality_degree_clause")
ART = ROOT / BASE_REL / "artifacts"
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
G628 = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts")
G628_ALLOW_REL = G628 / "PAGE_ALLOWLIST.tsv"
G628_RESULT_REL = G628 / "RESULT.json"
G628_VALUES_REL = G628 / "CHOL_VALUE_REALIZATIONS.tsv"
G628_DICT_REL = G628 / "WORKING_DICTIONARY_V5.tsv"
G628_TERMINAL_REL = G628 / "CHOL_D_TERMINAL_WITNESSES.tsv"
G628_EXTENSIONS_REL = G628 / "CHOL_EXTENSION_PROFILE.tsv"
G625_CTH_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/CTH_ROOT_FAMILY.tsv")
G623_DICT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv")
G627_HISTORICAL_REL = Path("experiments/yolo/gdt627_value_head_role_atlas/artifacts/HISTORICAL_SYNTAX_COMPARATORS.tsv")

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/TARGET_PAGE_ALLOWLIST.tsv",
    "views": BASE_REL / "artifacts/READER_REALIZATION_VIEWS.tsv",
    "loci": BASE_REL / "artifacts/LOCUS_TRIANGULATION.tsv",
    "bridges": BASE_REL / "artifacts/CROSS_READER_BOUNDARY_BRIDGES.tsv",
    "part_clauses": BASE_REL / "artifacts/PART_QUALITY_DEGREE_REALIZATIONS.tsv",
    "contexts": BASE_REL / "artifacts/CHOL_VALUE_CLAUSE_CONTEXTS.tsv",
    "token_defaults": BASE_REL / "artifacts/TARGET_LINE_TOKEN_DEFAULTS.tsv",
    "ranking": BASE_REL / "artifacts/CLAUSE_ROLE_RANKING.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V6.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_CLAUSES_V1.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

TARGET_LOCI = (
    "f2r.10",
    "f17v.8",
    "f21r.12",
    "f27r.6",
    "f32v.10",
    "f49r.6",
    "f58r.18",
    "f100r.22",
)
READERS = (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
KNOWN_PARTS = {"chor", "shor", "cthy", "cthar", "dair", "sair"}


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


def guarded_cross_query(pages: set[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS_REL), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend((
        "--columns", "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
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


def detect_realization(words: list[str]) -> dict[str, object]:
    for index, token in enumerate(words):
        if token == "choldaiin":
            return {
                "mode": "FUSED_D_AIII", "expression": token, "start": index, "end": index + 1,
                "segmentation": "ch+ol+d+a+III", "normalized_surface": "choldaiin",
                "normalized_reading_de": "trocken, Grad III",
            }
    for index, (left, right) in enumerate(zip(words, words[1:])):
        if (left, right) == ("chol", "daiin"):
            return {
                "mode": "SEPARATE_D_AIII", "expression": "chol daiin", "start": index, "end": index + 2,
                "segmentation": "ch+ol | d+a+III", "normalized_surface": "choldaiin",
                "normalized_reading_de": "trocken, Grad III",
            }
    for index, token in enumerate(words):
        if token == "cholaiin":
            return {
                "mode": "DIRECT_AIII", "expression": token, "start": index, "end": index + 1,
                "segmentation": "ch+ol+a+III", "normalized_surface": "cholaiin",
                "normalized_reading_de": "trocken, Grad III",
            }
    for index, (left, right) in enumerate(zip(words, words[1:])):
        if (left, right) == ("chol", "chaiin"):
            return {
                "mode": "SEPARATE_REDUPLICATED_CH_AIII", "expression": "chol chaiin", "start": index, "end": index + 2,
                "segmentation": "ch+ol | ch+a+III", "normalized_surface": "cholchaiin",
                "normalized_reading_de": "trockenes Gut: trocken, Grad III",
            }
    for index, token in enumerate(words):
        if token == "cholchaiin":
            return {
                "mode": "FUSED_REDUPLICATED_CH_AIII", "expression": token, "start": index, "end": index + 1,
                "segmentation": "ch+ol+ch+a+III", "normalized_surface": "cholchaiin",
                "normalized_reading_de": "trockenes Gut: trocken, Grad III",
            }
    raise RuntimeError("target line has no registered dry-III realization")


def make_views(cross_by_locus: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locus in TARGET_LOCI:
        source = cross_by_locus[locus]
        for reader, field in READERS:
            words = source[field].split()
            found = detect_realization(words)
            start, end = int(found["start"]), int(found["end"])
            part_anchor = words[start - 1] if start and words[start - 1] in KNOWN_PARTS else "NONE"
            clause_start = start - 1 if part_anchor != "NONE" else start
            clause_expression = " ".join(words[clause_start:end])
            clause_reading = (
                "Pflanzen-/Reproduktionsteil: trocken, Grad III"
                if part_anchor != "NONE" else str(found["normalized_reading_de"])
            )
            rows.append({
                "view_id": "", "page": source["page"], "locus": locus, "reader": reader,
                "realization_mode": found["mode"], "surface_expression": found["expression"],
                "segmentation": found["segmentation"], "normalized_surface": found["normalized_surface"],
                "normalized_reading_de": found["normalized_reading_de"],
                "part_anchor": part_anchor, "part_immediately_before": int(part_anchor != "NONE"),
                "smallest_clause_expression": clause_expression, "smallest_clause_reading_de": clause_reading,
                "left_residual": " ".join(words[:clause_start]) or "NONE",
                "right_residual": " ".join(words[end:]) or "NONE",
                "surface_line": source[field],
            })
    for index, row in enumerate(rows, 1):
        row["view_id"] = f"G629-V{index:02d}"
    return rows


def make_locus_summaries(views: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in views:
        grouped[str(row["locus"])].append(row)
    rows: list[dict[str, object]] = []
    for locus in TARGET_LOCI:
        selected = grouped[locus]
        modes = {str(row["realization_mode"]) for row in selected}
        expressions = {str(row["surface_expression"]) for row in selected}
        normalized = {str(row["normalized_surface"]) for row in selected}
        part_views = sum(int(row["part_immediately_before"]) for row in selected)
        if part_views == 3:
            level = "COMPLETE_PART_QUALITY_DEGREE_CLAUSE"
            reading = "Pflanzen-/Reproduktionsteil: trocken, Grad III"
        else:
            level = "QUALITY_DEGREE_PHRASE_ONLY"
            reading = "trocken, Grad III; äußerer Träger offen"
        if locus in {"f49r.6", "f100r.22"}:
            note = "gleicher normalisierter chol+d+III-Span; nur Leerzeichengrenze wechselt"
        elif locus == "f27r.6":
            note = "Partslot dreifach; ZL direkt, IT/RF mit zusätzlichem ch im Trockenheitsausdruck"
        elif locus in {"f21r.12", "f32v.10"}:
            note = "dreifach exakte separate Part-Qualität-Grad-Klausel"
        elif locus == "f17v.8":
            note = "dreifach exakte fusionierte Qualitätsphrase; kein unmittelbarer Partslot"
        else:
            note = "dreifach exakte direkte Qualitätsphrase; kein unmittelbarer Partslot"
        rows.append({
            "page": selected[0]["page"], "locus": locus,
            "reader_modes": "|".join(f"{row['reader']}:{row['realization_mode']}" for row in selected),
            "reader_expressions": "|".join(f"{row['reader']}:{row['surface_expression']}" for row in selected),
            "distinct_modes": len(modes), "exact_expression_agreement": int(len(expressions) == 1),
            "normalized_surface_agreement": int(len(normalized) == 1),
            "part_anchor_readers": part_views, "claim_level": level,
            "working_reading_de": reading, "note": note,
        })
    return rows


def make_boundary_bridges(loci: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in loci:
        if int(row["distinct_modes"]) == 1:
            continue
        locus = str(row["locus"])
        if locus in {"f49r.6", "f100r.22"}:
            bridge = "FUSED_D_TO_SEPARATE_D"
            strength = "EXACT_NORMALIZED_BOUNDARY_EQUIVALENCE"
            consequence = "choldaiin und chol daiin sind am selben Manuskriptspan Leerzeichenvarianten"
        else:
            bridge = "DIRECT_TO_REDUPLICATED_CH_DRY"
            strength = "SEMANTIC_READER_VARIANT_NOT_SPACING_ONLY"
            consequence = "f27 trägt in allen Lesungen trocken III,belegt aber keine reine Direkt/Getrennt-Gleichheit"
        rows.append({
            "bridge_id": "", "page": row["page"], "locus": locus, "bridge_type": bridge,
            "reader_modes": row["reader_modes"], "reader_expressions": row["reader_expressions"],
            "normalized_surface_agreement": row["normalized_surface_agreement"],
            "strength": strength, "working_consequence": consequence,
        })
    for index, row in enumerate(rows, 1):
        row["bridge_id"] = f"G629-B{index:02d}"
    return rows


def make_part_clauses(views: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for view in views:
        if not int(view["part_immediately_before"]):
            continue
        locus = str(view["locus"])
        if locus in {"f21r.12", "f32v.10"}:
            evidence = "TRIPLE_EXACT_SEPARATE_CLAUSE"
            rival = "Pflanzenteil/Trockenmaterial: drei Portionen"
        else:
            evidence = "SEMANTIC_TRIPLE_READER_VARIANT__DIRECT_ONLY_IN_ZL3B"
            rival = "Dosislesung benötigt wechselnden oder unausgedrückten Einheitenkopf"
        rows.append({
            "clause_id": "", "page": view["page"], "locus": locus, "reader": view["reader"],
            "surface_clause": view["smallest_clause_expression"],
            "realization_mode": view["realization_mode"], "segmentation": view["segmentation"],
            "working_reading_de": "Pflanzen-/Reproduktionsteil: trocken, Grad III",
            "evidence_class": evidence, "dose_rival_de": rival,
            "right_residual": view["right_residual"], "surface_line": view["surface_line"],
        })
    for index, row in enumerate(rows, 1):
        row["clause_id"] = f"G629-P{index:02d}"
    return rows


def nearest_part(words: list[str], start: int, direction: str) -> tuple[str, int]:
    candidates: list[tuple[int, str]] = []
    for index, word in enumerate(words):
        if word not in KNOWN_PARTS:
            continue
        distance = index - start
        if direction == "LEFT" and distance < 0:
            candidates.append((-distance, word))
        elif direction == "RIGHT" and distance > 0:
            candidates.append((distance, word))
    if not candidates:
        return "NONE", 0
    distance, word = min(candidates)
    return word, distance


def make_contexts(value_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in value_rows:
        words = source["surface_line"].split()
        start = int(source["token_index"]) - 1
        left_part, left_distance = nearest_part(words, start, "LEFT")
        right_part, right_distance = nearest_part(words, start, "RIGHT")
        immediate = left_part != "NONE" and left_distance == 1
        near = (left_part != "NONE" and left_distance <= 3) or (right_part != "NONE" and right_distance <= 3)
        if immediate:
            role = "PART_QUALITY_DEGREE_CLAUSE"
            span = f"{left_part} {source['surface_expression']}"
            reading = f"{left_part}-Pflanzenteil: trocken, Grad {source['working_roman']}"
        elif near:
            role = "QUALITY_DEGREE_WITH_NEAR_PART"
            span = source["surface_expression"]
            reading = f"trocken, Grad {source['working_roman']}; naher Partslot bindet noch offen"
        else:
            role = "QUALITY_DEGREE_PHRASE_ONLY"
            span = source["surface_expression"]
            reading = f"trocken, Grad {source['working_roman']}; äußerer Träger offen"
        rows.append({
            "context_id": source["realization_id"].replace("G628", "G629-C"),
            "page": source["page"], "locus": source["locus"], "realization_mode": source["realization_mode"],
            "surface_expression": source["surface_expression"], "working_roman": source["working_roman"],
            "left_part": left_part, "left_part_distance": left_distance,
            "right_part": right_part, "right_part_distance": right_distance,
            "immediate_part_before": int(immediate), "context_role": role,
            "smallest_supported_span": span, "working_reading_de": reading,
            "expression_triple_stable": source["all_expression_tokens_stable"], "surface_line": source["surface_line"],
        })
    return rows


def make_ranking() -> list[dict[str, object]]:
    return [
        {"rank": 1, "model": "PART_QUALITY_DEGREE", "working_clause_de": "Pflanzen-/Reproduktionsteil: trocken, Grad III", "support": "two triple-exact chor chol daiin clauses; f27 keeps part+dry-III semantics under reader variants; period materia-medica syntax", "counterevidence": "direct part clause is exact only in ZL3b and fused sites lack a part anchor", "disposition": "PRIMARY_WORKING_CLAUSE"},
        {"rank": 2, "model": "PART_OR_DRY_MATERIAL_THREE_PORTIONS", "working_clause_de": "Pflanzenteil/Trockenmaterial: drei Portionen", "support": "separate chor chol daiin has ordinary ingredient-dose order", "counterevidence": "does not economically explain direct cholaiin or the complete OL quality lattice", "disposition": "LIVE_SEPARATE_FORM_RIVAL"},
        {"rank": 3, "model": "PART_DRY_CLASS_III", "working_clause_de": "Pflanzenteil der Trockenklasse III", "support": "technical class and degree can share a four-cell table", "counterevidence": "GDT627 historical degree syntax is more specific", "disposition": "LIVE_NARROW_RIVAL"},
        {"rank": 4, "model": "GENERIC_OPERATION_OR_LIST_WORD", "working_clause_de": "generic take/work/item sequence", "support": "high-frequency forms can be grammatical", "counterevidence": "predictive dry and I-IV composition plus stable boundary bridges make the generic prose uninformative", "disposition": "REJECTED_AS_DEFAULT"},
    ]


def make_token_defaults(
    cross_by_locus: dict[str, dict[str, str]],
    cth_family: dict[str, dict[str, str]],
    extensions: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    exact = {
        "chor": ("CONCRETE_PART", "Pflanzen-/Reproduktionsteil", "gelernte Partform", "GDT623/GDT628"),
        "shor": ("CONCRETE_PART", "Blüten-/Fruchtstand", "gelernte Partform", "GDT623/GDT628"),
        "ol": ("CARRIER", "Qualitäts-/Zustands-/Materialträger; genauer Inhalt offen", "ol", "GDT628"),
        "or": ("CARRIER", "Teil-/Nominalträger; genauer Inhalt offen", "or", "GDT628"),
        "chol": ("CONCRETE_QUALITY", "trocken; nominal trockenes Gut", "ch+ol", "GDT628"),
        "shol": ("CONCRETE_QUALITY", "feucht; nominal feuchtes Gut", "sh+ol", "GDT628"),
        "cholaiin": ("CONCRETE_QUALITY_DEGREE", "trocken, Grad III", "ch+ol+a+III", "GDT628"),
        "choldaiin": ("CONCRETE_QUALITY_DEGREE", "trocken, Grad III", "ch+ol+d+a+III", "GDT628/GDT629"),
        "daiin": ("CONTEXTUAL_VALUE", "nach chol: Grad III; sonst Grad/Maß III", "d+a+III", "GDT627/GDT628"),
        "t": ("QUALITY_ROOT_OPEN_BINDING", "Kältestamm; selbständige Bindung offen", "t", "GDT623"),
    }
    rows: list[dict[str, object]] = []
    for locus in TARGET_LOCI:
        source = cross_by_locus[locus]
        for index, surface in enumerate(source["zl3b_clean"].split(), 1):
            if surface in exact:
                kind, meaning, composition, evidence = exact[surface]
            elif surface in cth_family:
                item = cth_family[surface]
                kind, meaning = "CTH_PART_FAMILY", item["surface_default_de"]
                composition, evidence = f"cth+{item['remainder']}", "GDT625"
            elif surface in extensions and surface != "chol":
                item = extensions[surface]
                kind = "CHOL_EXTENSION_OPEN"
                meaning = "Trockenheits-/Trockenmaterialform; äußere Erweiterung offen"
                composition, evidence = item["working_parse"], "GDT628"
            else:
                match = re.fullmatch(r"(.*a)(i*)n", surface)
                if match and len(match.group(2)) <= 3:
                    roman = ("I", "II", "III", "IV")[len(match.group(2))]
                    kind = "VALUE_WITH_OPEN_HEAD"
                    meaning = f"Wert {roman}; Kopf {match.group(1)} offen"
                    composition, evidence = f"{match.group(1)}+{roman}", "GDT626/GDT627"
                else:
                    kind, meaning, composition, evidence = "OPEN", "OPEN; keine generische Ersatzbedeutung", "OPEN", "NONE"
            rows.append({
                "token_id": "", "page": source["page"], "locus": locus, "token_index": index,
                "surface": surface, "default_type": kind, "default_meaning_de": meaning,
                "composition": composition, "evidence_source": evidence,
            })
    for index, row in enumerate(rows, 1):
        row["token_id"] = f"G629-T{index:03d}"
    return rows


def make_dictionary() -> list[dict[str, object]]:
    inherited = [dict(row) for row in read_tsv(ROOT / G628_DICT_REL)]
    additions = [
        {"entry": "chor cholaiin", "kind": "PART_DIRECT_DRY_III_READER_VARIANT", "working_meaning_de": "Pflanzen-/Reproduktionsteil: trocken, Grad III", "composition": "chor | ch+ol+a+III", "context_rule": "f27r.6 nur ZL3b direkt; IT2a/RF1b tragen zusätzliches ch", "status": "PROVISIONAL_DIRECT_CLAUSE"},
        {"entry": "chor chol daiin", "kind": "PART_SEPARATE_DRY_III_CLAUSE", "working_meaning_de": "Pflanzen-/Reproduktionsteil: trocken, Grad III", "composition": "chor | ch+ol | d+a+III", "context_rule": "f21r.12 und f32v.10 dreifach exakt; Dosisrival bleibt", "status": "NEW_PRIMARY_CLAUSE"},
        {"entry": "choldaiin|chol daiin", "kind": "FUSED_SEPARATE_BOUNDARY_EQUIVALENCE", "working_meaning_de": "trocken, Grad III", "composition": "ch+ol+d+a+III | ch+ol | d+a+III", "context_rule": "f49r.6 und f100r.22 wechseln nur die Wortgrenze", "status": "NEW_EXACT_BOUNDARY_BRIDGE"},
        {"entry": "cholchaiin|chol chaiin", "kind": "REDUPLICATED_DRY_III_READER_VARIANT", "working_meaning_de": "trockenes Gut: trocken, Grad III", "composition": "ch+ol(+|space)ch+a+III", "context_rule": "f27r.6 IT2a/RF1b; nicht mit reinem Spacing verwechseln", "status": "NEW_READER_VARIANT"},
    ]
    return inherited + additions


def make_cases(loci: list[dict[str, object]]) -> list[dict[str, object]]:
    by_locus = {str(row["locus"]): row for row in loci}
    specs = [
        ("F21_EXACT_PART_CLAUSE", "f21r.12", "chor chol daiin", "Pflanzen-/Reproduktionsteil: trocken, Grad III", "TRIPLE_EXACT_COMPLETE_CLAUSE"),
        ("F32_EXACT_PART_CLAUSE", "f32v.10", "chor chol daiin", "Pflanzen-/Reproduktionsteil: trocken, Grad III", "TRIPLE_EXACT_COMPLETE_CLAUSE"),
        ("F27_PART_READER_VARIANT", "f27r.6", "chor + dry-III family", "Pflanzen-/Reproduktionsteil: trocken, Grad III", "SEMANTIC_READER_VARIANT"),
        ("F17_EXACT_FUSED", "f17v.8", "choldaiin", "trocken, Grad III; äußerer Träger offen", "TRIPLE_EXACT_QUALITY_PHRASE"),
        ("F49_BOUNDARY_BRIDGE", "f49r.6", "choldaiin ↔ chol daiin", "trocken, Grad III; äußerer Träger offen", "EXACT_NORMALIZED_BOUNDARY_BRIDGE"),
        ("F100_BOUNDARY_BRIDGE", "f100r.22", "choldaiin ↔ chol daiin", "trocken, Grad III; äußerer Träger offen", "EXACT_NORMALIZED_BOUNDARY_BRIDGE"),
        ("F2_EXACT_DIRECT", "f2r.10", "cholaiin", "trocken, Grad III; äußerer Träger offen", "TRIPLE_EXACT_DIRECT_PHRASE"),
        ("F58_EXACT_DIRECT", "f58r.18", "cholaiin", "trocken, Grad III; äußerer Träger offen", "TRIPLE_EXACT_DIRECT_PHRASE"),
    ]
    return [{
        "case_id": case_id, "page": by_locus[locus]["page"], "locus": locus,
        "surface_expression": expression, "working_reading_de": reading,
        "evidence_class": evidence, "reader_expressions": by_locus[locus]["reader_expressions"],
        "residual_policy": "Tokens außerhalb der kleinsten Klammer bleiben sichtbar und OPEN",
    } for case_id, locus, expression, reading, evidence in specs]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    inherited_pages = {row["page"] for row in read_tsv(ROOT / G628_ALLOW_REL)}
    target_pages = {locus.split(".")[0] for locus in TARGET_LOCI}
    if not target_pages <= inherited_pages or "f1r" in target_pages or any(page.startswith("f84") for page in target_pages):
        raise RuntimeError("unsafe target-page scope")
    cross_rows, guard = guarded_cross_query(target_pages)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    if not set(TARGET_LOCI) <= set(cross_by_locus):
        raise RuntimeError("target locus missing from guarded query")
    cth_family = {row["surface"]: row for row in read_tsv(ROOT / G625_CTH_REL)}
    if cth_family["cthar"]["root_default_de"] != "Blatt-/Krautteil-Familie":
        raise RuntimeError("inherited part-family reading changed")
    quality_roots = {row["surface"]: row for row in read_tsv(ROOT / G623_DICT_REL)}
    if quality_roots["t"]["default_meaning_de"] != "kalt":
        raise RuntimeError("inherited cold root reading changed")

    value_rows = read_tsv(ROOT / G628_VALUES_REL)
    if len(value_rows) != 43:
        raise RuntimeError("GDT628 value atlas changed")
    views = make_views(cross_by_locus)
    loci = make_locus_summaries(views)
    bridges = make_boundary_bridges(loci)
    part_clauses = make_part_clauses(views)
    contexts = make_contexts(value_rows)
    extensions = {row["surface"]: row for row in read_tsv(ROOT / G628_EXTENSIONS_REL)}
    token_defaults = make_token_defaults(cross_by_locus, cth_family, extensions)
    ranking = make_ranking()
    dictionary = make_dictionary()
    cases = make_cases(loci)

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(target_pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["views"], views, (
        "view_id", "page", "locus", "reader", "realization_mode", "surface_expression", "segmentation",
        "normalized_surface", "normalized_reading_de", "part_anchor", "part_immediately_before",
        "smallest_clause_expression", "smallest_clause_reading_de", "left_residual", "right_residual", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["loci"], loci, (
        "page", "locus", "reader_modes", "reader_expressions", "distinct_modes", "exact_expression_agreement",
        "normalized_surface_agreement", "part_anchor_readers", "claim_level", "working_reading_de", "note",
    ))
    write_tsv(ROOT / OUTPUTS["bridges"], bridges, (
        "bridge_id", "page", "locus", "bridge_type", "reader_modes", "reader_expressions",
        "normalized_surface_agreement", "strength", "working_consequence",
    ))
    write_tsv(ROOT / OUTPUTS["part_clauses"], part_clauses, (
        "clause_id", "page", "locus", "reader", "surface_clause", "realization_mode", "segmentation",
        "working_reading_de", "evidence_class", "dose_rival_de", "right_residual", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["contexts"], contexts, (
        "context_id", "page", "locus", "realization_mode", "surface_expression", "working_roman",
        "left_part", "left_part_distance", "right_part", "right_part_distance", "immediate_part_before",
        "context_role", "smallest_supported_span", "working_reading_de", "expression_triple_stable", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["token_defaults"], token_defaults, (
        "token_id", "page", "locus", "token_index", "surface", "default_type",
        "default_meaning_de", "composition", "evidence_source",
    ))
    write_tsv(ROOT / OUTPUTS["ranking"], ranking, (
        "rank", "model", "working_clause_de", "support", "counterevidence", "disposition",
    ))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))
    write_tsv(ROOT / OUTPUTS["cases"], cases, (
        "case_id", "page", "locus", "surface_expression", "working_reading_de", "evidence_class",
        "reader_expressions", "residual_policy",
    ))

    mode_counts = Counter(str(row["realization_mode"]) for row in views)
    context_counts = Counter(str(row["context_role"]) for row in contexts)
    result = {
        "schema": "GDT629_PART_QUALITY_DEGREE_CLAUSE_RESULT_V1",
        "experiment_id": "GDT629",
        "status": "FUSED_SEPARATE_BOUNDARY_EQUIVALENCE__TWO_EXACT_PART_DRY_III_CLAUSES__DIRECT_PART_CLAUSE_READER_VARIANT",
        "claim_boundary": "The same physical spans at f49r.6 and f100r.22 are choldaiin in ZL3b/RF1b and chol daiin in IT2a, promoting exact fused/separate boundary equivalence for dry degree III. f21r.12 and f32v.10 give two triple-exact chor chol daiin clauses, read as plant or reproductive part: dry degree III with a live three-portion rival. f27r.6 retains the same normalized semantic slots across readers but adds ch in IT2a/RF1b, so the direct part clause is ZL3b-provisional. No fused witness has a demonstrated part anchor.",
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
            "target_pages": len(target_pages), "target_loci": len(TARGET_LOCI), "queried_cross_rows": len(cross_rows),
            "cross_query": guard,
        },
        "reader_triangulation": {
            "reader_views": len(views), "mode_counts": dict(sorted(mode_counts.items())),
            "exact_expression_agreement_loci": sum(int(row["exact_expression_agreement"]) for row in loci),
            "normalized_surface_agreement_loci": sum(int(row["normalized_surface_agreement"]) for row in loci),
            "boundary_variant_loci": len(bridges), "exact_fused_separate_bridges": sum(row["strength"] == "EXACT_NORMALIZED_BOUNDARY_EQUIVALENCE" for row in bridges),
        },
        "part_quality_degree": {
            "part_reader_views": len(part_clauses),
            "part_loci": len({str(row["locus"]) for row in part_clauses}),
            "triple_exact_separate_part_loci": 2,
            "exact_clause_loci": ["f21r.12", "f32v.10"],
            "reader_variant_clause_locus": "f27r.6",
            "fused_part_anchor_loci": 0,
            "working_clause_de": "Pflanzen-/Reproduktionsteil: trocken, Grad III",
        },
        "all_chol_value_contexts": {
            "contexts": len(contexts), "role_counts": dict(sorted(context_counts.items())),
            "stable_expressions": sum(int(row["expression_triple_stable"]) for row in contexts),
        },
        "target_line_defaults": {
            "tokens": len(token_defaults),
            "type_counts": dict(sorted(Counter(str(row["default_type"]) for row in token_defaults).items())),
            "unaccounted_tokens": 0,
            "open_tokens": sum(row["default_type"] == "OPEN" for row in token_defaults),
        },
        "working_lexicon_updates": {
            "chor_chol_daiin": "Pflanzen-/Reproduktionsteil: trocken, Grad III",
            "choldaiin_chol_daiin": "trocken, Grad III; fusionierte/getrennte Wortgrenze",
            "chor_cholaiin": "dieselbe Klausel nur ZL3b-direkt; IT2a/RF1b mit zusätzlichem ch",
        },
        "manual_sources": {
            "role_models": len(ranking), "concrete_clauses": len(cases),
            "historical_comparators": len(read_tsv(ROOT / G627_HISTORICAL_REL)),
        },
        "inputs": {str(path): sha256(ROOT / path) for path in (
            CROSS_REL, G628_ALLOW_REL, G628_RESULT_REL, G628_VALUES_REL, G628_DICT_REL,
            G628_TERMINAL_REL, G628_EXTENSIONS_REL, G625_CTH_REL, G623_DICT_REL, G627_HISTORICAL_REL,
        )},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "GDT629 built: "
        f"views={len(views)} modes={dict(sorted(mode_counts.items()))} loci={len(loci)} bridges={len(bridges)} "
        f"partviews={len(part_clauses)} contexts={len(contexts)} tokens={len(token_defaults)} dictionary={len(dictionary)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
