#!/usr/bin/env python3
"""Build the GDT624 productive quality-shell reader."""

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
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

BASE_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid")
ART = ROOT / BASE_REL / "artifacts"
SAFE_REL = Path("gdt327_joint_tuple_interlinear.tsv")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
GDT623_REPORT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/REPORT.md")
GDT623_RESULT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/RESULT.json")
GDT623_DICT_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv")
HISTORICAL_REL = BASE_REL / "artifacts/HISTORICAL_BINDING_COMPARATORS.tsv"
OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "cells": BASE_REL / "artifacts/GRID_CELLS.tsv",
    "occurrences": BASE_REL / "artifacts/GRID_OCCURRENCES.tsv",
    "frames": BASE_REL / "artifacts/QUADRANT_FRAME_COUNTS.tsv",
    "marginals": BASE_REL / "artifacts/FACTOR_MARGINALS.tsv",
    "edges": BASE_REL / "artifacts/LOCAL_ONE_BIT_EDGES.tsv",
    "edge_summary": BASE_REL / "artifacts/LOCAL_EDGE_SUMMARY.tsv",
    "wrapper_triplets": BASE_REL / "artifacts/WRAPPER_TRIPLETS.tsv",
    "length_series": BASE_REL / "artifacts/E_LENGTH_SERIES.tsv",
    "length_local": BASE_REL / "artifacts/E_LENGTH_LOCAL_SERIES.tsv",
    "exemplars": BASE_REL / "artifacts/LOCAL_EXEMPLARS.tsv",
    "herbal_bindings": BASE_REL / "artifacts/LOCAL_HERBAL_BINDINGS.tsv",
    "reader": BASE_REL / "artifacts/PRODUCTIVE_READER.tsv",
    "readings": BASE_REL / "artifacts/CONCRETE_LINE_READINGS.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

WRAPPERS = ("", "o", "qo")
THERMALS = ("k", "t")
MOISTURES = ("ch", "sh")
BITS = (0, 1)
MANUAL_EXTRA_PAGES = {"f31v"}
GRID_RE = re.compile(
    r"^(?P<wrapper>qo|o)?(?P<thermal>k|t)(?P<moisture>ch|sh)"
    r"(?P<e>e?)(?P<d>d?)y$"
)
V2 = {"k": "HOT", "t": "COLD", "ch": "DRY", "sh": "MOIST"}
QUAD_DE = {
    ("HOT", "DRY"): "heiß-trocken",
    ("HOT", "MOIST"): "heiß-feucht",
    ("COLD", "DRY"): "kalt-trocken",
    ("COLD", "MOIST"): "kalt-feucht",
}
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    fieldnames = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "NONE") if row.get(field, "") != "" else "NONE" for field in fieldnames})


def safe_pages() -> set[str]:
    source = GuardedTSV(ROOT / SAFE_REL, selector_column="page", allowed_values=None, forbidden_prefixes=("f84",), forbidden_action="error")
    pages = {row["page"] for row in source}
    pages.discard("f1r")
    if not pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("unsafe page inventory")
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
        raise RuntimeError("guarded query omitted unique guard statistics")
    stats = {key: int(value) for key, value in json.loads(stats_lines[0].removeprefix("GUARD_STATS ")).items()}
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"].startswith("f84") or row["page"] == "f1r" for row in rows):
        raise RuntimeError("forbidden selector materialized")
    return rows, stats


def line_number(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    if not match:
        raise ValueError(f"bad locus: {locus}")
    return int(match.group(1))


def token_sort_key(row: dict[str, str]) -> tuple[str, int, int]:
    return row["page"], line_number(row["locus"]), int(row["token_index"])


def surface(wrapper: str, thermal: str, moisture: str, e_bit: int, d_bit: int) -> str:
    return f"{wrapper}{thermal}{moisture}{'e' if e_bit else ''}{'d' if d_bit else ''}y"


def parse_grid(value: str) -> tuple[str, str, str, int, int] | None:
    match = GRID_RE.fullmatch(value)
    if not match:
        return None
    return (match.group("wrapper") or "", match.group("thermal"), match.group("moisture"), int(bool(match.group("e"))), int(bool(match.group("d"))))


def quality_values(thermal: str, moisture: str) -> tuple[str, str]:
    return V2[thermal], V2[moisture]


def complete_default(wrapper: str, thermal: str, moisture: str, e_bit: int, d_bit: int) -> str:
    values = quality_values(thermal, moisture)
    if d_bit:
        core = f"{QUAD_DE[values]}e Zustands-/Bindungsform"
        if e_bit:
            core += "; vorwärts gebunden/attributiv"
    else:
        core = QUAD_DE[values]
        core += " (vorwärts gebunden/attributiv)" if e_bit else " (unmarkiert/prädikativ)"
    if wrapper == "o":
        return f"im o-Rahmen: {core}"
    if wrapper == "qo":
        return f"im qo-Qualitätsrahmen: {core}"
    return core


def stable_capacities(cross_rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    stable: dict[str, Counter[str]] = {}
    for row in cross_rows:
        editions = [Counter(row[field].split()) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        universe = set().union(*(counter.keys() for counter in editions))
        stable[row["locus"]] = Counter({item: min(counter[item] for counter in editions) for item in universe if min(counter[item] for counter in editions) > 0})
    return stable


def make_grid(tokens: list[dict[str, str]], stable: dict[str, Counter[str]], edition_counts: dict[str, Counter[str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, list[dict[str, str]]], dict[str, Counter[str]]]:
    ordinals: Counter[tuple[str, str]] = Counter()
    occurrences: list[dict[str, object]] = []
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    stable_by_locus: dict[str, Counter[str]] = defaultdict(Counter)
    for row in sorted(tokens, key=token_sort_key):
        parsed = parse_grid(row["eva"])
        if parsed is None:
            continue
        wrapper, thermal, moisture, e_bit, d_bit = parsed
        by_surface[row["eva"]].append(row)
        key = row["locus"], row["eva"]
        ordinals[key] += 1
        triple_stable = int(ordinals[key] <= stable.get(row["locus"], Counter())[row["eva"]])
        if triple_stable:
            stable_by_locus[row["locus"]][row["eva"]] += 1
        hot_cold, dry_moist = quality_values(thermal, moisture)
        cell_ordinal = 1 + WRAPPERS.index(wrapper) * 16 + THERMALS.index(thermal) * 8 + MOISTURES.index(moisture) * 4 + e_bit * 2 + d_bit
        occurrences.append({
            "cell_id": f"G624-C{cell_ordinal:03d}",
            "page": row["page"], "locus": row["locus"], "token_index": row["token_index"], "surface": row["eva"],
            "wrapper": wrapper or "BARE", "thermal_symbol": thermal, "moisture_symbol": moisture, "e_bit": e_bit, "d_bit": d_bit,
            "quadrant": f"{hot_cold}_{dry_moist}", "section": row["section"], "language": row["language"],
            "triple_reading_token_stable": triple_stable, "working_default_de": complete_default(wrapper, thermal, moisture, e_bit, d_bit),
        })

    cells: list[dict[str, object]] = []
    for wrapper in WRAPPERS:
        for thermal in THERMALS:
            for moisture in MOISTURES:
                for e_bit in BITS:
                    for d_bit in BITS:
                        item = surface(wrapper, thermal, moisture, e_bit, d_bit)
                        rows = by_surface[item]
                        stable_count = sum(counter[item] for counter in stable_by_locus.values())
                        hot_cold, dry_moist = quality_values(thermal, moisture)
                        cell_ordinal = 1 + WRAPPERS.index(wrapper) * 16 + THERMALS.index(thermal) * 8 + MOISTURES.index(moisture) * 4 + e_bit * 2 + d_bit
                        cells.append({
                            "cell_id": f"G624-C{cell_ordinal:03d}", "surface": item, "wrapper": wrapper or "BARE", "thermal_symbol": thermal, "thermal_default": hot_cold,
                            "moisture_symbol": moisture, "moisture_default": dry_moist, "e_bit": e_bit,
                            "e_default": "FORWARD_BOUND_OR_ATTRIBUTIVE__DEGREE_RIVAL" if e_bit else "UNMARKED_OR_PREDICATIVE", "d_bit": d_bit,
                            "d_default": "GRAMMATICAL_DY_BINDING_OR_STATE_CLOSURE" if d_bit else "BASIC_QUALITY_FORM", "occurrences": len(rows),
                            "pages": len({row["page"] for row in rows}), "it2a_occurrences": edition_counts["IT2a"][item], "rf1b_occurrences": edition_counts["RF1b"][item],
                            "triple_reading_stable_occurrences": stable_count,
                            "triple_reading_stable_pages": len({row["page"] for row in rows if stable_by_locus[row["locus"]][item]}),
                            "working_default_de": complete_default(wrapper, thermal, moisture, e_bit, d_bit),
                        })
    return cells, occurrences, by_surface, stable_by_locus


def make_frame_counts(cells: list[dict[str, object]]) -> list[dict[str, object]]:
    lookup = {str(row["surface"]): int(row["occurrences"]) for row in cells}
    rows: list[dict[str, object]] = []
    for wrapper in WRAPPERS:
        for e_bit, d_bit, ending in ((0, 0, "y"), (1, 0, "ey"), (0, 1, "dy"), (1, 1, "edy")):
            counts = {f"{thermal.upper()}{moisture.upper()}": lookup[surface(wrapper, thermal, moisture, e_bit, d_bit)] for thermal in THERMALS for moisture in MOISTURES}
            rows.append({"wrapper": wrapper or "BARE", "ending_frame": ending, **counts, "total": sum(counts.values())})
    return rows


def make_factor_marginals(cells: list[dict[str, object]]) -> list[dict[str, object]]:
    dimensions = [
        ("WRAPPER", ("BARE", "o", "qo"), lambda row: row["wrapper"]),
        ("THERMAL", ("k", "t"), lambda row: row["thermal_symbol"]),
        ("MOISTURE", ("ch", "sh"), lambda row: row["moisture_symbol"]),
        ("E_BIT", (0, 1), lambda row: row["e_bit"]),
        ("D_BIT", (0, 1), lambda row: row["d_bit"]),
        ("ENDING", ("y", "ey", "dy", "edy"), lambda row: ("e" if int(row["e_bit"]) else "") + ("d" if int(row["d_bit"]) else "") + "y"),
    ]
    output: list[dict[str, object]] = []
    for dimension, values, accessor in dimensions:
        for value in values:
            selected = [row for row in cells if accessor(row) == value]
            output.append({
                "dimension": dimension, "value": value,
                "zl3b_occurrences": sum(int(row["occurrences"]) for row in selected),
                "it2a_occurrences": sum(int(row["it2a_occurrences"]) for row in selected),
                "rf1b_occurrences": sum(int(row["rf1b_occurrences"]) for row in selected),
                "stable_min_occurrences": sum(int(row["triple_reading_stable_occurrences"]) for row in selected),
            })
    return output


def make_edges(by_surface: dict[str, list[dict[str, str]]], stable_by_locus: dict[str, Counter[str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    line_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for item, rows in by_surface.items():
        for row in rows:
            line_counts[row["locus"]][item] += 1
    specs: list[tuple[str, str, str, str]] = []
    for wrapper in WRAPPERS:
        for moisture in MOISTURES:
            for e_bit in BITS:
                for d_bit in BITS:
                    specs.append(("THERMAL_K_T", surface(wrapper, "k", moisture, e_bit, d_bit), surface(wrapper, "t", moisture, e_bit, d_bit), f"{wrapper or 'BARE'}:{moisture}:e{e_bit}:d{d_bit}"))
        for thermal in THERMALS:
            for e_bit in BITS:
                for d_bit in BITS:
                    specs.append(("MOISTURE_CH_SH", surface(wrapper, thermal, "ch", e_bit, d_bit), surface(wrapper, thermal, "sh", e_bit, d_bit), f"{wrapper or 'BARE'}:{thermal}:e{e_bit}:d{d_bit}"))
        for thermal in THERMALS:
            for moisture in MOISTURES:
                for d_bit in BITS:
                    specs.append(("E_INSERTION", surface(wrapper, thermal, moisture, 0, d_bit), surface(wrapper, thermal, moisture, 1, d_bit), f"{wrapper or 'BARE'}:{thermal}:{moisture}:d{d_bit}"))
                for e_bit in BITS:
                    specs.append(("D_INSERTION", surface(wrapper, thermal, moisture, e_bit, 0), surface(wrapper, thermal, moisture, e_bit, 1), f"{wrapper or 'BARE'}:{thermal}:{moisture}:e{e_bit}"))
    for thermal in THERMALS:
        for moisture in MOISTURES:
            for e_bit in BITS:
                for d_bit in BITS:
                    core = surface("", thermal, moisture, e_bit, d_bit)
                    o_form = surface("o", thermal, moisture, e_bit, d_bit)
                    qo_form = surface("qo", thermal, moisture, e_bit, d_bit)
                    context = f"{thermal}:{moisture}:e{e_bit}:d{d_bit}"
                    specs.append(("WRAPPER_BARE_O", core, o_form, context))
                    specs.append(("WRAPPER_O_QO", o_form, qo_form, context))

    rows: list[dict[str, object]] = []
    for axis, left, right, context in specs:
        loci = sorted(locus for locus, counts in line_counts.items() if counts[left] and counts[right])
        stable_loci = [locus for locus in loci if stable_by_locus[locus][left] and stable_by_locus[locus][right]]
        rows.append({"axis": axis, "context": context, "left_surface": left, "right_surface": right,
                     "same_line_loci": len(loci), "triple_stable_same_line_loci": len(stable_loci),
                     "example_loci": "|".join(loci[:8]) or "NONE", "stable_example_loci": "|".join(stable_loci[:8]) or "NONE"})
    summary: list[dict[str, object]] = []
    for axis in ("THERMAL_K_T", "MOISTURE_CH_SH", "E_INSERTION", "D_INSERTION", "WRAPPER_BARE_O", "WRAPPER_O_QO"):
        selected = [row for row in rows if row["axis"] == axis]
        summary.append({"axis": axis, "candidate_edge_types": len(selected),
                        "same_line_edge_types": sum(int(row["same_line_loci"]) > 0 for row in selected),
                        "triple_stable_edge_types": sum(int(row["triple_stable_same_line_loci"]) > 0 for row in selected),
                        "same_line_loci": sum(int(row["same_line_loci"]) for row in selected),
                        "triple_stable_same_line_loci": sum(int(row["triple_stable_same_line_loci"]) for row in selected)})
    return rows, summary


def make_wrapper_triplets(by_surface: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for thermal in THERMALS:
        for moisture in MOISTURES:
            for e_bit in BITS:
                for d_bit in BITS:
                    forms = [surface(wrapper, thermal, moisture, e_bit, d_bit) for wrapper in WRAPPERS]
                    page_loci: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
                    for item in forms:
                        for token in by_surface[item]:
                            page_loci[token["page"]][item].append(token["locus"])
                    for page in sorted(page_loci):
                        if all(page_loci[page][item] for item in forms):
                            rows.append({"page": page, "core": forms[0], "bare_surface": forms[0], "o_surface": forms[1], "qo_surface": forms[2],
                                         "bare_loci": "|".join(sorted(set(page_loci[page][forms[0]]))),
                                         "o_loci": "|".join(sorted(set(page_loci[page][forms[1]]))),
                                         "qo_loci": "|".join(sorted(set(page_loci[page][forms[2]]))),
                                         "interpretation": "SAME_QUALITY_CORE_UNDER_THREE_SCOPE_WRAPPERS"})
    return rows


def make_length_series(tokens: list[dict[str, str]], stable: dict[str, Counter[str]], edition_counts: dict[str, Counter[str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    token_counts = Counter(row["eva"] for row in tokens)
    token_pages: dict[str, set[str]] = defaultdict(set)
    by_locus: dict[str, Counter[str]] = defaultdict(Counter)
    for row in tokens:
        token_pages[row["eva"]].add(row["page"])
        by_locus[row["locus"]][row["eva"]] += 1
    stable_counts = Counter()
    for counter in stable.values():
        stable_counts.update(counter)
    groups = [(stem, tail) for stem in ("ch", "sh", "k", "t", "ok", "ot") for tail in ("dy", "ody")]
    rows: list[dict[str, object]] = []
    local: list[dict[str, object]] = []
    for stem, tail in groups:
        group = f"{stem.upper()}_{tail.upper()}"
        forms = tuple(f"{stem}{'e' * e_length}{tail}" for e_length in range(5))
        for e_length, item in enumerate(forms):
            rows.append({"series": group, "stem": stem, "tail": tail, "e_length": e_length, "surface": item, "occurrences": token_counts[item],
                         "it2a_occurrences": edition_counts["IT2a"][item], "rf1b_occurrences": edition_counts["RF1b"][item],
                         "pages": len(token_pages[item]), "triple_stable_occurrences": stable_counts[item],
                         "working_default": "PRODUCTIVE_E_LENGTH__BOUND_OR_GRADE_EXPANSION__DIRECTION_OPEN"})
        for locus, counter in sorted(by_locus.items()):
            present = [item for item in forms if counter[item]]
            if len(present) < 2:
                continue
            stable_present = [item for item in present if stable.get(locus, Counter())[item]]
            present_lengths = [forms.index(item) for item in present]
            local.append({"series": group, "locus": locus, "present_e_lengths": "|".join(map(str, present_lengths)), "present_members": "|".join(present), "present_member_count": len(present),
                          "triple_stable_members": "|".join(stable_present) or "NONE", "triple_stable_member_count": len(stable_present)})
    return rows, local


def make_exemplars(tokens: list[dict[str, str]], cross_rows: list[dict[str, str]], stable: dict[str, Counter[str]]) -> list[dict[str, object]]:
    cross = {row["locus"]: row for row in cross_rows}
    specs = [
        ("STATE_EDY_CH_SH", "f104r.7", ("shedy", "chedy"), "feuchter ↔ trockener markierter Zustand"),
        ("ODY_CH_SH_CAUTION", "f86v5.36", ("shody", "chody"), "formaler Gegenpol; shody-Inhalt bleibt offen"),
        ("EODY_CH_SH", "f88v.16", ("sheody", "cheody"), "markierte feucht/trocken-Variante"),
        ("THERMAL_EY", "f42v.2", ("kchey", "tchey"), "heiß-trocken ↔ kalt-trocken; markierte Stufe"),
        ("THERMAL_EDY", "f85r1.5", ("tchedy", "kchedy"), "kalt-trockener ↔ heiß-trockener Zustand; markierte Stufe"),
        ("WRAPPER_O_QO", "f107v.38", ("okchey", "qokchey"), "derselbe heiß-trockene Kern unter o/qo-Rahmen"),
        ("E_LENGTH_SH", "f116r.10", ("shdy", "shedy", "sheedy"), "feuchte Zustandsreihe mit drei e-Längen"),
        ("E_INSERTION", "f20r.12", ("otchy", "otchey"), "kalt-trocken unmarkiert ↔ markierte Stufe"),
        ("D_INSERTION", "f105v.9", ("otchey", "otchedy"), "kalt-trocken markiert ↔ Zustands-/Ergebnisform"),
    ]
    output: list[dict[str, object]] = []
    for exemplar_id, locus, forms, reading in specs:
        row = cross.get(locus)
        if row is None or not all(Counter(row["zl3b_clean"].split())[item] for item in forms):
            raise RuntimeError(f"bad exemplar {locus}: {forms}")
        output.append({"exemplar_id": exemplar_id, "page": row["page"], "locus": locus, "forms": "|".join(forms),
                       "all_forms_triple_token_stable": int(all(stable[locus][item] for item in forms)),
                       "zl3b_line": row["zl3b_clean"], "it2a_line": row["it2a_clean"], "rf1b_line": row["rf1b_clean"],
                       "working_contrast_de": reading})
    wanted = ("okchey", "okshey", "otchey", "otshey")
    page_rows = [row for row in tokens if row["page"] == "f79r"]
    loci = {item: sorted({row["locus"] for row in page_rows if row["eva"] == item}) for item in wanted}
    if not all(loci[item] for item in wanted):
        raise RuntimeError("f79r lacks the four o-ey corners")
    output.append({"exemplar_id": "FOUR_CORNERS_ONE_PAGE", "page": "f79r", "locus": "|".join(sorted({value for values in loci.values() for value in values})),
                   "forms": "|".join(wanted), "all_forms_triple_token_stable": int(all(any(stable[locus][item] for locus in loci[item]) for item in wanted)),
                   "zl3b_line": "PAGE_BUNDLE", "it2a_line": "PAGE_BUNDLE", "rf1b_line": "PAGE_BUNDLE",
                   "working_contrast_de": "alle vier heiß/kalt × trocken/feucht-Ecken im o-Rahmen"})
    return output


def make_reader(cells: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cell in cells:
        rows.append({
            "surface": cell["surface"], "composition": f"{cell['wrapper']}+{cell['thermal_symbol']}+{cell['moisture_symbol']}+e{cell['e_bit']}+d{cell['d_bit']}+y",
            "working_reading_de": cell["working_default_de"], "thermal_atom": f"{cell['thermal_symbol']}={str(cell['thermal_default']).lower()}",
            "moisture_atom": f"{cell['moisture_symbol']}={str(cell['moisture_default']).lower()}",
            "e_atom": "vorwärts gebunden/attributiv; Grad-Rivale offen" if int(cell["e_bit"]) else "unmarkiert/prädikativ", "d_atom": "grammatische DY-Bindung/Zustandsabschluss" if int(cell["d_bit"]) else "Grundform",
            "wrapper_atom": {"BARE": "unmarkierter Rahmen", "o": "o-Scope", "qo": "qo-Qualitätsfeld"}[str(cell["wrapper"])],
            "occurrences": cell["occurrences"], "triple_stable_occurrences": cell["triple_reading_stable_occurrences"],
            "status": "COMPLETE_COMPOSITIONAL_DEFAULT__E_ATTRIBUTIVE_D_BINDING_WORKING_READER",
        })
    return rows


def make_herbal_bindings(cross_rows: list[dict[str, str]], stable: dict[str, Counter[str]]) -> list[dict[str, object]]:
    """Render the six direct quality-to-part contacts on already opened images."""
    cross = {row["locus"]: row for row in cross_rows}
    specs = [
        ("ROOT_F23", "f23v.4", "okchey", "dair", "QUALITY_BEFORE_PART", "heiß-trockene Wurzel / Radix"),
        ("ROOT_F31", "f31v.3", "okchey", "sair", "QUALITY_BEFORE_PART", "heiß-trockener Wurzelteil"),
        ("REPRO_F39", "f39v.6", "okchey", "shor", "QUALITY_BEFORE_PART", "heiß-trockener Blüten- oder Fruchtstand"),
        ("REPRO_F29", "f29v.1", "shor", "chetchy", "PART_BEFORE_EMBEDDED_QUALITY", "Blüten- oder Fruchtstand: kalt-trocken"),
        ("REPRO_F23", "f23v.6", "shor", "shkshy", "PART_BEFORE_EMBEDDED_QUALITY", "Blüten- oder Fruchtstand: heiß-feucht"),
        ("REPRO_F45", "f45v.1", "shor", "ykchy", "PART_BEFORE_EMBEDDED_QUALITY", "Blüten- oder Fruchtstand: heiß-trocken"),
    ]
    rows: list[dict[str, object]] = []
    for binding_id, locus, part_a, part_b, order, phrase in specs:
        row = cross.get(locus)
        if row is None:
            raise RuntimeError(f"missing Herbal binding locus {locus}")
        zl = row["zl3b_clean"].split()
        if part_a not in zl or part_b not in zl:
            raise RuntimeError(f"missing Herbal binding at {locus}")
        left_index, right_index = zl.index(part_a), zl.index(part_b)
        rows.append({
            "binding_id": binding_id,
            "page": row["page"],
            "locus": locus,
            "left_surface": part_a,
            "right_surface": part_b,
            "token_distance": abs(right_index - left_index),
            "binding_order": order,
            "left_triple_token_stable": int(stable.get(locus, Counter())[part_a] > 0),
            "right_triple_token_stable": int(stable.get(locus, Counter())[part_b] > 0),
            "zl3b_line": row["zl3b_clean"],
            "working_phrase_de": phrase,
            "interpretation": "QUALITY_OR_STATE_DESCRIPTOR__NOT_OPERATION",
            "visual_scope": "PREVIOUSLY_OPENED_HERBAL_IMAGE_ONLY",
        })
    return rows


def make_readings(exemplars: list[dict[str, object]], herbal_bindings: list[dict[str, object]], reader: list[dict[str, object]]) -> list[dict[str, object]]:
    exact = {str(row["surface"]): str(row["working_reading_de"]) for row in reader}
    extra = {
        "chdy": "trockene Zustands-/Bindungsform", "chedy": "trockene Zustandsform; vorwärts gebunden", "cheedy": "trockene Zustandsform; erweiterte e-Bindung",
        "shdy": "feuchte Zustands-/Bindungsform", "shedy": "feuchte Zustandsform; vorwärts gebunden", "sheedy": "feuchte Zustandsform; erweiterte e-Bindung",
        "chody": "trocken/Trockenklasse", "shody": "gelernte Form im Trocken-Kontext; Inhalt offen",
        "cheody": "gebundene trockene Variante?", "sheody": "gebundene feuchte Variante?",
        "okedy": "heiße Zustandsform; vorwärts gebunden", "otedy": "kalte Zustandsform; vorwärts gebunden", "shor": "Blüten-/Fruchtstand",
        "dair": "Wurzelteil/Radix", "sair": "Wurzelteil?; air-Kern",
        "chetchy": "gebundene kalt-trockene Qualitätsform", "shkshy": "gebundene heiß-feuchte Qualitätsform",
        "ykchy": "gebundene heiß-trockene Qualitätsform", "kooiin": "dicke/kriechende Wurzeldroge",
        "korary": "Frucht-/Samen-/Reproduktivdroge?",
    }

    def render(line: str) -> tuple[str, int]:
        rendered: list[str] = []
        translated = 0
        for item in line.split():
            gloss = exact.get(item, extra.get(item))
            if gloss is None:
                rendered.append(f"<{item}>")
            else:
                rendered.append(f"[{gloss}]")
                translated += 1
        return " ".join(rendered), translated

    rows: list[dict[str, object]] = []
    for exemplar in exemplars:
        if exemplar["zl3b_line"] == "PAGE_BUNDLE":
            continue
        translated, count = render(str(exemplar["zl3b_line"]))
        rows.append({"reading_id": exemplar["exemplar_id"], "page": exemplar["page"], "locus": exemplar["locus"], "surface_line": exemplar["zl3b_line"],
                     "working_reading_de": translated, "translated_token_count": count, "line_token_count": len(str(exemplar["zl3b_line"]).split()),
                     "unknown_policy": "ANGLE_BRACKETS_KEEP_EVERY_UNTRANSLATED_SURFACE"})
    for binding in herbal_bindings:
        translated, count = render(str(binding["zl3b_line"]))
        rows.append({"reading_id": binding["binding_id"], "page": binding["page"], "locus": binding["locus"], "surface_line": binding["zl3b_line"],
                     "working_reading_de": translated, "translated_token_count": count, "line_token_count": len(str(binding["zl3b_line"]).split()),
                     "unknown_policy": "ANGLE_BRACKETS_KEEP_EVERY_UNTRANSLATED_SURFACE"})
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = safe_pages()
    tokens, token_guard = guarded_query(TOKENS_REL, pages, "page,locus,code,kind,section,language,hand,token_index,eva")
    cross_rows, cross_guard = guarded_query(CROSS_REL, pages | MANUAL_EXTRA_PAGES, "page,locus,all_three_present,all_present_exact,zl3b_it2a_similarity,zl3b_rf1b_similarity,zl3b_clean,it2a_clean,rf1b_clean")
    tokens.sort(key=token_sort_key)
    cross_frequency_rows = [row for row in cross_rows if row["page"] in pages]
    stable = stable_capacities(cross_frequency_rows)
    stable_all = stable_capacities(cross_rows)
    edition_counts = {
        "IT2a": Counter(word for row in cross_frequency_rows for word in row["it2a_clean"].split()),
        "RF1b": Counter(word for row in cross_frequency_rows for word in row["rf1b_clean"].split()),
    }
    cells, occurrences, by_surface, stable_by_locus = make_grid(tokens, stable, edition_counts)
    frames = make_frame_counts(cells)
    marginals = make_factor_marginals(cells)
    edges, edge_summary = make_edges(by_surface, stable_by_locus)
    wrapper_triplets = make_wrapper_triplets(by_surface)
    length_series, length_local = make_length_series(tokens, stable, edition_counts)
    exemplars = make_exemplars(tokens, cross_rows, stable)
    herbal_bindings = make_herbal_bindings(cross_rows, stable_all)
    reader = make_reader(cells)
    readings = make_readings(exemplars, herbal_bindings, reader)

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["cells"], cells, ("cell_id", "surface", "wrapper", "thermal_symbol", "thermal_default", "moisture_symbol", "moisture_default", "e_bit", "e_default", "d_bit", "d_default", "occurrences", "pages", "it2a_occurrences", "rf1b_occurrences", "triple_reading_stable_occurrences", "triple_reading_stable_pages", "working_default_de"))
    write_tsv(ROOT / OUTPUTS["occurrences"], occurrences, ("cell_id", "page", "locus", "token_index", "surface", "wrapper", "thermal_symbol", "moisture_symbol", "e_bit", "d_bit", "quadrant", "section", "language", "triple_reading_token_stable", "working_default_de"))
    write_tsv(ROOT / OUTPUTS["frames"], frames, ("wrapper", "ending_frame", "KCH", "KSH", "TCH", "TSH", "total"))
    write_tsv(ROOT / OUTPUTS["marginals"], marginals, ("dimension", "value", "zl3b_occurrences", "it2a_occurrences", "rf1b_occurrences", "stable_min_occurrences"))
    write_tsv(ROOT / OUTPUTS["edges"], edges, ("axis", "context", "left_surface", "right_surface", "same_line_loci", "triple_stable_same_line_loci", "example_loci", "stable_example_loci"))
    write_tsv(ROOT / OUTPUTS["edge_summary"], edge_summary, ("axis", "candidate_edge_types", "same_line_edge_types", "triple_stable_edge_types", "same_line_loci", "triple_stable_same_line_loci"))
    write_tsv(ROOT / OUTPUTS["wrapper_triplets"], wrapper_triplets, ("page", "core", "bare_surface", "o_surface", "qo_surface", "bare_loci", "o_loci", "qo_loci", "interpretation"))
    write_tsv(ROOT / OUTPUTS["length_series"], length_series, ("series", "stem", "tail", "e_length", "surface", "occurrences", "it2a_occurrences", "rf1b_occurrences", "pages", "triple_stable_occurrences", "working_default"))
    write_tsv(ROOT / OUTPUTS["length_local"], length_local, ("series", "locus", "present_e_lengths", "present_members", "present_member_count", "triple_stable_members", "triple_stable_member_count"))
    write_tsv(ROOT / OUTPUTS["exemplars"], exemplars, ("exemplar_id", "page", "locus", "forms", "all_forms_triple_token_stable", "zl3b_line", "it2a_line", "rf1b_line", "working_contrast_de"))
    write_tsv(ROOT / OUTPUTS["herbal_bindings"], herbal_bindings, ("binding_id", "page", "locus", "left_surface", "right_surface", "token_distance", "binding_order", "left_triple_token_stable", "right_triple_token_stable", "zl3b_line", "working_phrase_de", "interpretation", "visual_scope"))
    write_tsv(ROOT / OUTPUTS["reader"], reader, ("surface", "composition", "working_reading_de", "thermal_atom", "moisture_atom", "e_atom", "d_atom", "wrapper_atom", "occurrences", "triple_stable_occurrences", "status"))
    write_tsv(ROOT / OUTPUTS["readings"], readings, ("reading_id", "page", "locus", "surface_line", "working_reading_de", "translated_token_count", "line_token_count", "unknown_policy"))

    edge_lookup = {str(row["axis"]): row for row in edge_summary}
    result = {
        "schema": "GDT624_PRODUCTIVE_QUALITY_SHELL_GRID_RESULT_V1", "experiment_id": "GDT624",
        "status": "COMPLETE_48_CELL_SURFACE_LATTICE__COMPOSITIONAL_QUALITY_CORE_WORKING_READER",
        "claim_boundary": "All 48 exact wrapper by thermal by moisture by e by d by y cells are observed and every type has a three-reading-stable witness. Read k/t as hot/cold and ch/sh as dry/moist under the GDT623 working key. The best throughput defaults are e as a forward-bound or attributive quality form and d as grammatical DY binding or state closure; historical degree and result readings remain rivals. No grid word is an operation by itself. Wrapper alternation does not create three unrelated whole words.",
        "grammar": {"surface": "P+{k,t}+{ch,sh}+[e?]+[d?]+y", "P": ["BARE", "o", "qo"], "values": V2,
                    "e": "FORWARD_BOUND_OR_ATTRIBUTIVE__HISTORICAL_DEGREE_RIVAL", "d": "GRAMMATICAL_DY_BINDING_OR_STATE_CLOSURE__NOT_OPERATION", "y": "CLOSURE"},
        "guard": {"f1r": "EXCLUDED_BEFORE_ALLOW_LIST", "f84": "FORBIDDEN_BEFORE_PAYLOAD", "f84r": "FORBIDDEN_BEFORE_PAYLOAD",
                  "safe_pages": len(pages), "safe_tokens": len(tokens), "manual_extra_pages": sorted(MANUAL_EXTRA_PAGES), "token_query": token_guard, "cross_query": cross_guard},
        "grid": {"possible_cells": 48, "observed_cells": sum(int(row["occurrences"]) > 0 for row in cells),
                 "triple_stable_cells": sum(int(row["triple_reading_stable_occurrences"]) > 0 for row in cells), "occurrences": len(occurrences),
                 "it2a_occurrences": sum(int(row["it2a_occurrences"]) for row in cells), "rf1b_occurrences": sum(int(row["rf1b_occurrences"]) for row in cells),
                 "pages": len({str(row["page"]) for row in occurrences}), "loci": len({str(row["locus"]) for row in occurrences}),
                 "triple_stable_occurrences": sum(int(row["triple_reading_token_stable"]) for row in occurrences), "wrapper_triplet_page_cases": len(wrapper_triplets)},
        "local_edges": {axis: {key: int(value) for key, value in row.items() if key != "axis"} for axis, row in edge_lookup.items()},
        "e_length_counts": {str(row["surface"]): int(row["occurrences"]) for row in length_series},
        "translation": {"complete_word_defaults": len(reader), "rendered_lines": len(readings), "direct_herbal_part_bindings": len(herbal_bindings), "unknown_surfaces_are_preserved": True},
        "historical_binding_comparators": {"rows": len(read_tsv(ROOT / HISTORICAL_REL)), "primary_e_default": "FORWARD_BOUND_OR_ATTRIBUTIVE", "degree_rival": "LIVE", "operation_default": "REJECTED_FOR_GRID_WORDS"},
        "inputs": {str(path): sha256(ROOT / path) for path in (SAFE_REL, TOKENS_REL, CROSS_REL, GDT623_REPORT_REL, GDT623_RESULT_REL, GDT623_DICT_REL, HISTORICAL_REL)},
        "outputs": {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GDT624 built: cells={result['grid']['observed_cells']}/48 events={len(occurrences)} stable={result['grid']['triple_stable_occurrences']} wrapper_triplets={len(wrapper_triplets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
