#!/usr/bin/env python3
"""Independent release validator for GDT658.

The raw census and the four semantic/family gates are deliberately evaluated
before the GDT658 builder module is imported.  Mixed transcription tables are
only accessed through the repository guard.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import inspect
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt658_four_residual_concrete_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"

G657 = Path("experiments/yolo/gdt657_multi_quality_al_shell_order")
G657_ALLOW = G657 / "artifacts/PAGE_ALLOWLIST.tsv"
G657_COVERAGE = G657 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V34.tsv"
G657_COMPLETE = G657 / "artifacts/COMPLETE_PASSAGES_V34.tsv"
G657_ONE = G657 / "artifacts/ONE_UNKNOWN_PASSAGES_V34.tsv"
G657_GLOSSARY = G657 / "artifacts/V34_WORKING_TOKEN_GLOSSARY.tsv"
G657_DICTIONARY = G657 / "artifacts/WORKING_DICTIONARY_V34.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_4_RESIDUAL_CONCRETE_WHOLES__V35"
TARGET_ORDER = ("otam", "shedefam", "schos", "chokcheo")
TARGETS = {
    "otam": {
        "census": (44, 43, 34, 39, 39),
        "meaning_terms": ("ein Maß", "kalten Ansatzes"),
        "composition_terms": ("O_PREP", "T_COLD", "AM_MEASURE_I"),
        "warning": False,
    },
    "shedefam": {
        "census": (1, 1, 1, 0, 0),
        "meaning_terms": ("ein Maß", "eingeweichter", "Blütendroge"),
        "composition_terms": ("SHEDE_LOCAL_MOIST", "F_BOUND_FLOWER_DRUG_HEAD", "AM_MEASURE_I"),
        "warning": True,
    },
    "schos": {
        "census": (1, 1, 1, 1, 1),
        "meaning_terms": ("trockene", "Arzneimischung", "Samen"),
        "composition_terms": ("S_SEED_HEAD", "CHO_DRY", "S_"),
        "warning": False,
    },
    "chokcheo": {
        "census": (1, 1, 1, 1, 1),
        "meaning_terms": ("Trockenansatz", "heiß", "Trockenpräparat"),
        "composition_terms": ("CHO_DRY", "K_HOT", "CHEO_DRY"),
        "warning": False,
    },
}

# positions, physical lines, pages, exact in all three readers, split-normalized
AM_GRID = {
    "kam": (7, 7, 7, 1, 1),
    "tam": (6, 6, 6, 3, 3),
    "okam": (27, 27, 24, 17, 17),
    "otam": (44, 43, 34, 39, 39),
    "qokam": (25, 25, 21, 22, 22),
    "qotam": (11, 11, 9, 10, 10),
    "cham": (15, 15, 13, 15, 15),
    "sham": (6, 6, 5, 6, 6),
}

# Ten F+body forms whose bodies are already strong V34 fields.  The eight
# complete five-head grids are the subset without CHEODY and CHOR.
# Bodies shared by at least three P/S/R/L heads, excluding the bound CHO
# preparation head rather than treating it as a materia body.
F_CLEAR = {
    "faiir": (1, 1, 1, 1, 1),
    "far": (2, 2, 2, 2, 2),
    "fchdy": (3, 3, 3, 2, 2),
    "fchedy": (9, 9, 9, 4, 4),
    "fcheey": (4, 4, 4, 4, 4),
    "fchey": (2, 2, 2, 2, 2),
    "fchody": (1, 1, 1, 0, 0),
    "fchol": (2, 2, 2, 1, 1),
    "fchor": (3, 3, 3, 2, 2),
    "fol": (1, 1, 1, 0, 0),
    "folchey": (1, 1, 1, 1, 1),
    "fshedy": (2, 2, 2, 1, 1),
}
F_COMPLETE_BODIES = ("ar", "chdy", "chedy", "cheey", "chey", "chol", "ol", "shedy")
FIVE_HEAD_GRID = {
    "ar": {"par": (6, 4), "sar": (62, 45), "rar": (14, 11), "lar": (8, 5), "far": (2, 2)},
    "chdy": {"pchdy": (10, 6), "schdy": (2, 1), "rchdy": (1, 0), "lchdy": (18, 14), "fchdy": (3, 2)},
    "chedy": {"pchedy": (35, 25), "schedy": (7, 4), "rchedy": (10, 6), "lchedy": (116, 75), "fchedy": (9, 4)},
    "cheey": {"pcheey": (3, 3), "scheey": (1, 0), "rcheey": (5, 4), "lcheey": (13, 10), "fcheey": (4, 4)},
    "chey": {"pchey": (8, 6), "schey": (5, 4), "rchey": (8, 5), "lchey": (46, 37), "fchey": (2, 2)},
    "chol": {"pchol": (5, 5), "schol": (3, 3), "rchol": (1, 0), "lchol": (3, 3), "fchol": (2, 1)},
    "ol": {"pol": (16, 13), "sol": (57, 49), "rol": (20, 14), "lol": (35, 31), "fol": (1, 0)},
    "shedy": {"pshedy": (3, 3), "sshedy": (6, 4), "rshedy": (5, 3), "lshedy": (38, 24), "fshedy": (2, 1)},
}

K_T_CHEO = {
    "kcheo": (3, 3, 3, 3, 3),
    "tcheo": (5, 5, 5, 5, 5),
    "qokcheo": (2, 2, 2, 2, 2),
    "qotcheo": (4, 3, 3, 4, 4),
    "otcheo": (1, 1, 1, 1, 1),
    "lkcheo": (1, 1, 1, 1, 1),
    "cheokcheo": (1, 1, 1, 1, 1),
    "chokcheo": (1, 1, 1, 1, 1),
}
ABSENT_K_T_CHEO_CONTROLS = ("okcheo", "cheotcheo", "chotcheo", "ltcheo")
TERMINAL_S_CORE = {
    "chos": (30, 30, 22, 27, 27),
    "cheos": (28, 28, 25, 22, 22),
    "cheeos": (6, 5, 5, 6, 6),
    "shos": (9, 9, 9, 7, 7),
    "sheos": (9, 9, 9, 7, 7),
    "sheeos": (1, 1, 1, 1, 1),
}

BASE_METRICS = {
    "physical_lines": 4128,
    "known_token_positions": 16696,
    "unknown_token_positions": 15643,
    "complete_multi_token_lines": 133,
    "strict_complete_lines": 78,
    "one_unknown_lines": 243,
    "strict_one_unknown_lines": 59,
    "working_glossary_surfaces": 491,
}
FINAL_METRICS = {
    "physical_lines": 4128,
    "known_token_positions": 16743,
    "unknown_token_positions": 15596,
    "complete_multi_token_lines": 138,
    "strict_complete_lines": 80,
    "one_unknown_lines": 239,
    "strict_one_unknown_lines": 57,
    "working_glossary_surfaces": 495,
}
ROUND_METRICS = (
    (0, "BASE_V34", 570, 16696, 15643, 133, 78, 243, 59, 491),
    (1, "otam", 571, 16740, 15599, 135, 78, 242, 59, 492),
    (2, "shedefam", 572, 16741, 15598, 136, 78, 241, 59, 493),
    (3, "schos", 573, 16742, 15597, 137, 79, 240, 58, 494),
    (4, "chokcheo", 574, 16743, 15596, 138, 80, 239, 57, 495),
)
NEW_COMPLETE = {
    "f33r.5": ("otam", 0),
    "f107r.41": ("otam", 0),
    "f66v.5": ("shedefam", 0),
    "f93r.32": ("schos", 1),
    "f56r.13": ("chokcheo", 1),
}
NEW_ONE = {"f80v.21": ("otam", "y", 0)}

FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|"
    r"werkzeug|produkt weiter|f.hre .* aus|leite .* weiter|geh(?:e)? zur arbeit|nimm .* arbeite",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stats_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats_lines) != 1:
        raise RuntimeError(done.stderr or "guarded query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("excluded or forbidden page materialized")
    return rows, json.loads(stats_lines[0].removeprefix("GUARD_STATS "))


def span_count(tokens: list[str], target: str) -> int:
    total = 0
    for start in range(len(tokens)):
        joined = ""
        for token in tokens[start:]:
            joined += token
            if joined == target:
                total += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return total


def independent_records(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]], surfaces: set[str]
) -> list[dict[str, object]]:
    cross = {row["locus"]: row for row in cross_rows}
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        by_locus[row["locus"]].append(row)
    for line in by_locus.values():
        line.sort(key=lambda item: int(item["token_index"]))
    records: list[dict[str, object]] = []
    for surface in sorted(surfaces):
        members = [row for row in token_rows if row["eva"] == surface]
        members.sort(key=lambda item: (item["page"], item["locus"], int(item["token_index"])))
        seen: Counter[str] = Counter()
        for row in members:
            locus = row["locus"]
            seen[locus] += 1
            occurrence_in_line = seen[locus]
            readers = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
            direct = [tokens.count(surface) for tokens in readers]
            spans = [span_count(tokens, surface) for tokens in readers]
            line = by_locus[locus]
            ordinal = next(i for i, token in enumerate(line, 1) if token is row)
            records.append(
                {
                    **row,
                    "token_ordinal": ordinal,
                    "line_position": "ONLY" if len(line) == 1 else ("INITIAL" if ordinal == 1 else ("FINAL" if ordinal == len(line) else "MEDIAL")),
                    "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                    "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                    "zl3b_line": cross[locus]["zl3b_clean"],
                    "it2a_line": cross[locus]["it2a_clean"],
                    "rf1b_line": cross[locus]["rf1b_clean"],
                    "reader_exact": int(occurrence_in_line <= min(direct)),
                    "split_normalized": int(occurrence_in_line <= min(spans)),
                }
            )
    return records


def census(records: list[dict[str, object]], surface: str) -> tuple[int, int, int, int, int]:
    members = [row for row in records if row["eva"] == surface]
    return (
        len(members),
        len({str(row["locus"]) for row in members}),
        len({str(row["page"]) for row in members}),
        sum(int(row["reader_exact"]) for row in members),
        sum(int(row["split_normalized"]) for row in members),
    )


def coverage_metrics(
    coverage: list[dict[str, str]], complete: list[dict[str, str]], one_unknown: list[dict[str, str]], glossary_size: int
) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": glossary_size,
    }


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt658_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT658 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    # ---- Independent raw census.  No GDT658 builder import above this line. ----
    inherited_allow = read_tsv(ROOT / G657_ALLOW)
    pages = {row["page"] for row in inherited_allow}
    check(len(inherited_allow) == len(pages) == 179, "179 unique inherited guarded pages")
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "f1r excluded; f84/f84r forbidden")

    token_rows, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(
        CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    expected_token_stats = {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}
    expected_cross_stats = {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}
    check(len(token_rows) == 32339 and token_stats == expected_token_stats, "guarded token recensus", repr(token_stats))
    check(len(cross_rows) == 4137 and cross_stats == expected_cross_stats, "guarded cross-reader recensus", repr(cross_stats))

    all_surfaces = {row["eva"] for row in token_rows}
    raw_surfaces = set(TARGETS) | set(AM_GRID) | set(F_CLEAR) | set(K_T_CHEO) | set(TERMINAL_S_CORE)
    for body_grid in FIVE_HEAD_GRID.values():
        raw_surfaces.update(body_grid)
    raw_surfaces.update({"rchos", "schol", "schor"})
    records = independent_records(token_rows, cross_rows, raw_surfaces)
    target_records = [row for row in records if str(row["eva"]) in TARGETS]

    for surface, spec in TARGETS.items():
        check(census(records, surface) == spec["census"], f"raw target census:{surface}", repr(census(records, surface)))
    check(
        (
            len(target_records), len({str(row["locus"]) for row in target_records}),
            len({str(row["page"]) for row in target_records}),
            sum(int(row["reader_exact"]) for row in target_records),
            sum(int(row["split_normalized"]) for row in target_records),
        )
        == (47, 46, 37, 41, 41),
        "47/46/37/41 aggregate target census",
    )
    position_counts = Counter(str(row["line_position"]) for row in target_records)
    otam_positions = Counter(str(row["line_position"]) for row in target_records if row["eva"] == "otam")
    check(position_counts == {"MEDIAL": 18, "FINAL": 29}, "target position distribution", repr(position_counts))
    check(otam_positions == {"MEDIAL": 16, "FINAL": 28}, "OTAM final preference", repr(otam_positions))
    check(
        Counter(str(row["section"]) for row in target_records) == {"S": 18, "H": 17, "T": 8, "B": 2, "C": 1, "P": 1}
        and Counter(str(row["language"]) for row in target_records) == {"B": 38, "A": 9}
        and Counter(str(row["hand"]) for row in target_records) == {"3": 19, "2": 16, "1": 8, "5": 4},
        "target section/language/hand spread",
    )

    # K/T x AM evidence: the three paired K/T shells are all populated and the
    # CH/SH sister heads independently show that AM is a recurrent body.
    for surface, expected in AM_GRID.items():
        check(census(records, surface) == expected, f"K/T-AM family census:{surface}", repr(census(records, surface)))
    check(all({left, right} <= all_surfaces for left, right in (("kam", "tam"), ("okam", "otam"), ("qokam", "qotam"))), "three complete K/T-AM pairs")

    # F is tested only as a family-bound fifth head.  These checks do not and
    # must not create a free f=flower component.
    f_initial_surfaces = {surface for surface in all_surfaces if len(surface) > 1 and surface.startswith("f")}
    f_initial_rows = [row for row in token_rows if row["eva"] in f_initial_surfaces]
    check(
        (len(f_initial_surfaces), len(f_initial_rows), len({row["page"] for row in f_initial_rows})) == (77, 102, 65),
        "full initial-F inventory 77/102/65",
    )
    shared_f_surfaces = {
        surface
        for surface in f_initial_surfaces
        if any(head + surface[1:] in all_surfaces for head in "psrl")
    }
    shared_f_rows = [row for row in token_rows if row["eva"] in shared_f_surfaces]
    check(
        (len(shared_f_surfaces), len(shared_f_rows), len({row["page"] for row in shared_f_rows})) == (43, 67, 50),
        "F forms with P/S/R/L sister 43/67/50",
    )
    for surface, expected in F_CLEAR.items():
        check(census(records, surface) == expected, f"clear F+body census:{surface}", repr(census(records, surface)))
    f_records = [row for row in records if str(row["eva"]) in F_CLEAR]
    check(
        (len(F_CLEAR), len(f_records), len({str(row["locus"]) for row in f_records}), len({str(row["page"]) for row in f_records}), sum(int(row["reader_exact"]) for row in f_records))
        == (12, 31, 30, 27, 20),
        "twelve strong F forms at 31 positions",
    )
    for body, grid in FIVE_HEAD_GRID.items():
        check(set(grid) == {head + body for head in "psrlf"}, f"complete P/S/R/L/F grid:{body}")
        for surface, (positions, exact) in grid.items():
            actual = census(records, surface)
            check((actual[0], actual[3]) == (positions, exact), f"five-head cell:{surface}", repr(actual))
    check(tuple(FIVE_HEAD_GRID) == F_COMPLETE_BODIES, "exactly eight registered five-head bodies")

    # SCHOS has an independent, exact same-page boundary witness and an R-head
    # sister.  Initial and final S stay separate by construction.
    line_lengths = Counter(row["locus"] for row in token_rows)
    terminal_s_rows = [row for row in token_rows if len(row["eva"]) > 1 and row["eva"].endswith("s")]
    check(
        (
            len(terminal_s_rows),
            sum(int(row["token_index"]) < line_lengths[row["locus"]] for row in terminal_s_rows),
            sum(int(row["token_index"]) == line_lengths[row["locus"]] for row in terminal_s_rows),
        )
        == (725, 622, 103),
        "non-singleton terminal-S inventory and line positions",
    )
    for surface, expected in TERMINAL_S_CORE.items():
        check(census(records, surface) == expected, f"terminal-S core census:{surface}", repr(census(records, surface)))
    terminal_core_records = [row for row in records if str(row["eva"]) in TERMINAL_S_CORE]
    check(
        (
            len(terminal_core_records), len({str(row["locus"]) for row in terminal_core_records}),
            len({str(row["page"]) for row in terminal_core_records}),
            sum(int(row["reader_exact"]) for row in terminal_core_records),
        )
        == (83, 78, 49, 70),
        "six-form terminal-S core 83/78/49/70",
    )
    for surface, expected in {"schol": (3, 3, 3, 3, 3), "schor": (3, 3, 3, 3, 3), "schos": (1, 1, 1, 1, 1)}.items():
        check(census(records, surface) == expected, f"S-CHO-L/R/S contrast:{surface}", repr(census(records, surface)))
    cross_by = {row["locus"]: row for row in cross_rows}
    check(
        all(" s cho s " in f" {cross_by['f93r.6'][field]} " for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")),
        "f93r.6 exact s|cho|s reader boundary",
    )
    check(census(records, "rchos") == (1, 1, 1, 1, 1), "RCHOS exact material-head sister", repr(census(records, "rchos")))
    check(
        cross_by["f93r.32"]["zl3b_clean"] == cross_by["f93r.32"]["it2a_clean"] == cross_by["f93r.32"]["rf1b_clean"] == "dol chokal schos",
        "SCHOS exact source line",
    )
    check(
        all(" rchos " in f" {cross_by['f115v.44'][field]} " for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")),
        "RCHOS source-line reader support",
    )

    # CHEO nesting evidence and absent pair controls.
    for surface, expected in K_T_CHEO.items():
        check(census(records, surface) == expected, f"K/T-CHEO family census:{surface}", repr(census(records, surface)))
    check(not (set(ABSENT_K_T_CHEO_CONTROLS) & all_surfaces), "four absent K/T-CHEO control cells")
    check(
        cross_by["f56r.13"]["zl3b_clean"] == cross_by["f56r.13"]["it2a_clean"] == cross_by["f56r.13"]["rf1b_clean"] == "okchy chokcheo kchal",
        "CHOKCHEO exact nested source line",
    )
    check(
        cross_by["f66v.5"]["zl3b_clean"] == cross_by["f66v.5"]["it2a_clean"] == "shdy shedefam qokedy chokal dal"
        and cross_by["f66v.5"]["rf1b_clean"] == "shd she efam qokedy chokal dal",
        "SHEDEFAM exact two-reader whole and RF split warning",
    )

    # Artifact, semantic, provenance and replay checks are added below.  They
    # remain after every independent raw gate above to preserve validation
    # independence from the implementation.
    if not (ART / "RESULT.json").is_file():
        issues.append("builder artifacts: RESULT.json is not yet materialized")
    else:
        validate_release_artifacts(
            check, token_rows, cross_rows, target_records, token_stats, cross_stats, pages, passed, issues
        )

    validation = {
        "schema": "GDT658_VALIDATION_V1",
        "experiment_id": "GDT658",
        "status": "PASS" if not issues else "FAIL",
        "checks_passed": len(passed),
        "checks_failed": len(issues),
        "passed": passed,
        "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT658 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT658 validation PASS: {len(passed)} checks")
    return 0


def validate_release_artifacts(
    check,
    token_rows: list[dict[str, str]],
    cross_rows: list[dict[str, str]],
    target_records: list[dict[str, object]],
    token_stats: dict[str, int],
    cross_stats: dict[str, int],
    pages: set[str],
    passed: list[str],
    issues: list[str],
) -> None:
    """Validate materialized GDT658 artifacts, then import/replay the builder."""
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("schema") == "GDT658_FOUR_RESIDUAL_CONCRETE_COMPLETION_RESULT_V1", "result schema")
    check(result.get("experiment_id") == "GDT658" and result.get("status") == STATUS, "result identity/status")
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(result.get("content_sha256") == canonical_hash(result_core), "result canonical content hash")

    required_files = (
        "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
        "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv", "ROUND_COVERAGE_COUNTS.tsv",
        "TARGET_LINE_TRANSLATIONS.tsv", "SOURCE_READING_AUDIT.tsv", "NEWLY_COMPLETED_LINES.tsv",
        "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V35_WORKING_TOKEN_GLOSSARY.tsv",
        "ALL_LINE_CONCRETE_COVERAGE_V35.tsv", "COMPLETE_PASSAGES_V35.tsv",
        "ONE_UNKNOWN_PASSAGES_V35.tsv", "WORKING_DICTIONARY_V35.tsv",
    )
    for name in required_files:
        check((ART / name).is_file(), f"required artifact:{name}")
    if not all((ART / name).is_file() for name in required_files):
        return

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G657_ALLOW).read_bytes(), "V34 allowlist inherited byte-identically")
    check(len(allow_rows) == len(pages) == 179 and {row["page"] for row in allow_rows} == pages, "artifact allowlist identity")
    guard = result.get("guard", {})
    check(guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats, "result guarded query stats")
    check(
        guard.get("allowed_pages") == 179
        and guard.get("f1r") == "EXCLUDED"
        and guard.get("f84") == guard.get("f84r") == "FORBIDDEN"
        and guard.get("new_pages") == guard.get("new_images") == 0,
        "result guard ceiling",
    )

    cross_by = {row["locus"]: row for row in cross_rows}
    raw_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        raw_by_locus[row["locus"]].append(row)
    for rows in raw_by_locus.values():
        rows.sort(key=lambda item: int(item["token_index"]))

    # Four concrete whole cards, with the reader warning confined to SHEDEFAM.
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    check(len(deck) == 4 and [row.get("surface") for row in deck] == list(TARGET_ORDER), "four-card target order")
    deck_by = {row.get("surface", ""): row for row in deck}
    check(set(deck_by) == set(TARGETS), "target deck exact surface set")
    for surface, spec in TARGETS.items():
        row = deck_by.get(surface, {})
        meaning = row.get("working_meaning_de", "")
        composition = row.get("composition", "")
        rival = row.get("rival_de", "")
        expected = spec["census"]
        check(all(term.lower() in meaning.lower() for term in spec["meaning_terms"]), f"concrete meaning:{surface}", meaning)
        check(all(term.lower() in composition.lower() for term in spec["composition_terms"]), f"visible composition:{surface}", composition)
        check(bool(rival) and rival != meaning and not FILLER.search(rival), f"live rival:{surface}", rival)
        check(
            tuple(int(row.get(field, "-1")) for field in ("occurrences", "lines", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
            == expected,
            f"deck census:{surface}",
            repr(row),
        )
        warning_text = " ".join(row.get(field, "") for field in ("mode", "decision", "reader_status")).upper()
        check(("WARNING" in warning_text) == bool(spec["warning"]), f"reader-warning confinement:{surface}", warning_text)
        check(not FILLER.search(meaning), f"no generic card filler:{surface}", meaning)
    check(
        all(term in deck_by["shedefam"].get("rival_de", "").lower() for term in ("frucht", "blatt", "opak")),
        "SHEDEFAM keeps fruit/leaf/opaque-F rivals",
    )
    check(
        "salz" in deck_by["schos"].get("rival_de", "").lower()
        and any(term in deck_by["schos"].get("rival_de", "").lower() for term in ("form", "sorte")),
        "SCHOS keeps salt and form/sort rivals",
    )
    check(deck_by["otam"].get("working_meaning_de") == "ein Maß kalten Ansatzes", "OTAM practical core")

    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    accepted_by = {row.get("surface", ""): row for row in accepted}
    check(len(accepted) == 4 and set(accepted_by) == set(TARGETS), "four accepted exact-whole entries")
    for surface, row in accepted_by.items():
        check(
            row.get("working_meaning_de") == deck_by[surface].get("working_meaning_de")
            and row.get("composition") == deck_by[surface].get("composition")
            and "exact complete zl3b surface only" in row.get("context_rule", "").lower()
            and "no substring inheritance" in row.get("context_rule", "").lower(),
            f"accepted whole-card fidelity:{surface}",
        )

    audit = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audit) == 47 and len({row.get("audit_id") for row in audit}) == 47, "47 unique occurrence audits")
    raw_occurrence_by = {
        (str(row["eva"]), str(row["locus"]), str(row["token_ordinal"])): row for row in target_records
    }
    audit_by = {(row.get("surface", ""), row.get("locus", ""), row.get("token_ordinal", "")): row for row in audit}
    check(set(audit_by) == set(raw_occurrence_by), "occurrence audit/raw ordinal identity")
    occurrence_ok = True
    for key, raw in raw_occurrence_by.items():
        row = audit_by.get(key, {})
        occurrence_ok &= (
            row.get("page") == raw["page"]
            and row.get("section") == raw["section"]
            and row.get("language") == raw["language"]
            and row.get("hand") == raw["hand"]
            and row.get("line_position") == raw["line_position"]
            and row.get("previous") == raw["previous"]
            and row.get("following") == raw["following"]
            and row.get("zl3b_line") == raw["zl3b_line"]
            and row.get("it2a_line") == raw["it2a_line"]
            and row.get("rf1b_line") == raw["rf1b_line"]
            and row.get("reader_exact") == str(raw["reader_exact"])
            and row.get("split_normalized") == str(raw["split_normalized"])
            and row.get("after_gloss_de") == deck_by[key[0]].get("working_meaning_de")
            and row.get("hard_collision") == "0"
            and not FILLER.search(row.get("after_gloss_de", ""))
        )
    check(occurrence_ok, "independent 47-row occurrence replay")
    check(
        all(
            row.get("contextual_meaning_de") == "ein Maß kalten Ansatzes" + ("." if row.get("line_position") == "FINAL" else "")
            and "Eintrag abgeschlossen" not in row.get("v35_line_de", "")
            for row in audit if row.get("surface") == "otam"
        ),
        "OTAM uses punctuation, not a spoken closure gloss",
    )

    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    raw_variants = {
        (str(row["eva"]), str(row["locus"])): row
        for row in target_records if not int(row["reader_exact"])
    }
    variant_by = {(row.get("surface", ""), row.get("locus", "")): row for row in variants}
    check(len(variants) == len(raw_variants) == 6 and set(variant_by) == set(raw_variants), "six raw reader-variant rows")
    check(
        all(
            row.get("zl3b_line") == raw_variants[key]["zl3b_line"]
            and row.get("it2a_line") == raw_variants[key]["it2a_line"]
            and row.get("rf1b_line") == raw_variants[key]["rf1b_line"]
            for key, row in variant_by.items() if key in raw_variants
        ),
        "reader-variant source fidelity",
    )
    check(
        any(row.get("surface") == "shedefam" and row.get("rf1b_line") == "shd she efam qokedy chokal dal" for row in variants),
        "SHEDEFAM full RF1b split retained",
    )

    base_glossary = read_tsv(ROOT / G657_GLOSSARY)
    glossary = read_tsv(ART / "V35_WORKING_TOKEN_GLOSSARY.tsv")
    base_gloss_by = {row["surface"]: row for row in base_glossary}
    gloss_by = {row["surface"]: row for row in glossary}
    check(len(base_glossary) == 491 and len(glossary) == len(gloss_by) == 495, "V34/V35 glossary sizes")
    check(set(gloss_by) - set(base_gloss_by) == set(TARGETS), "only four glossary surfaces added")
    check(all(gloss_by.get(surface) == row for surface, row in base_gloss_by.items()), "all V34 glossary rows unchanged")
    for surface in TARGETS:
        row = gloss_by.get(surface, {})
        check(
            row.get("working_meaning_de") == deck_by[surface].get("working_meaning_de")
            and row.get("scope_state") == "KNOWN_EXACT_WHOLE",
            f"V35 glossary card:{surface}",
        )

    base_dictionary = read_tsv(ROOT / G657_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V35.tsv")
    check(len(base_dictionary) == 570 and len(dictionary) == 574, "V34/V35 dictionary sizes")
    check(dictionary[:570] == base_dictionary, "V34 dictionary is exact V35 prefix")
    appended = dictionary[570:]
    check(len(appended) == 4 and [row.get("entry", "").split("@", 1)[0] for row in appended] == list(TARGET_ORDER), "four appended whole dictionary cards")
    check(
        not any(row.get("entry", "").split("@", 1)[0] in {"f", "s", "shede"} for row in appended),
        "no free F, terminal-S or SHEDE dictionary card",
    )

    base_coverage = read_tsv(ROOT / G657_COVERAGE)
    base_complete = read_tsv(ROOT / G657_COMPLETE)
    base_one = read_tsv(ROOT / G657_ONE)
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V35.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V35.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V35.tsv")
    base_cov_by = {row["locus"]: row for row in base_coverage}
    cov_by = {row["locus"]: row for row in coverage}
    check(len(base_cov_by) == len(cov_by) == 4128 and set(base_cov_by) == set(cov_by) == set(raw_by_locus), "4128-line coverage identity")
    coverage_source_ok = True
    for locus, row in cov_by.items():
        raw_line = " ".join(token["eva"] for token in raw_by_locus[locus])
        coverage_source_ok &= row.get("zl3b_line") == raw_line and int(row.get("token_count", "-1")) == len(raw_by_locus[locus])
    check(coverage_source_ok, "coverage/raw source fidelity")
    check(coverage_metrics(base_coverage, base_complete, base_one, len(base_glossary)) == BASE_METRICS, "recomputed V34 base metrics")
    check(coverage_metrics(coverage, complete, one, len(glossary)) == FINAL_METRICS, "recomputed V35 final metrics")
    check(
        {row["locus"] for row in complete} == {row["locus"] for row in coverage if int(row["token_count"]) > 1 and row["unknown_tokens"] == "0"}
        and {row["locus"] for row in one} == {row["locus"] for row in coverage if int(row["token_count"]) > 1 and row["unknown_tokens"] == "1"},
        "complete and one-hole tables independently derived",
    )

    target_counts_by_locus = Counter(str(row["locus"]) for row in target_records)
    delta_ok = True
    unchanged_ok = True
    for locus, final_row in cov_by.items():
        before = base_cov_by[locus]
        delta = target_counts_by_locus[locus]
        delta_ok &= (
            int(final_row["known_tokens"]) - int(before["known_tokens"]) == delta
            and int(before["unknown_tokens"]) - int(final_row["unknown_tokens"]) == delta
        )
        if not delta:
            unchanged_ok &= final_row == before
    check(delta_ok and sum(target_counts_by_locus.values()) == 47, "exact 47-position V34-to-V35 coverage delta")
    check(unchanged_ok, "all 4082 unaffected line rows unchanged")
    check(all(not any(surface in row.get("unknown_surfaces", "").split("|") for surface in TARGETS) for row in coverage), "no target remains unknown")

    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_complete_by = {row["locus"]: row for row in new_complete}
    check(len(new_complete) == 5 and set(new_complete_by) == set(NEW_COMPLETE), "exact five new complete lines")
    for locus, (surface, strict) in NEW_COMPLETE.items():
        row = new_complete_by.get(locus, {})
        check(
            row.get("strict_complete") == str(strict)
            and surface in row.get("enabled_by_surfaces", "").split("|")
            and row.get("zl3b_line") == cross_by[locus]["zl3b_clean"]
            and not re.search(r"\[[a-z]+:\?\]", row.get("practical_v35_de", ""), re.IGNORECASE),
            f"new complete line:{locus}",
        )
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(
        len(new_one) == 1
        and new_one[0].get("locus") == "f80v.21"
        and new_one[0].get("enabled_by_surface") == "otam"
        and new_one[0].get("unknown_surface") == "y"
        and new_one[0].get("strict_eligible") == "0",
        "new f80v.21 one-hole Y frontier",
        repr(new_one),
    )

    affected = read_tsv(ART / "TARGET_LINE_TRANSLATIONS.tsv")
    affected_by = {row["locus"]: row for row in affected}
    check(len(affected) == len(affected_by) == 46 and set(affected_by) == set(target_counts_by_locus), "46 affected physical lines")
    check(
        all(
            row.get("zl3b_line") == cross_by[locus]["zl3b_clean"]
            and row.get("v34_tokenwise_de") == base_cov_by[locus]["token_glosses_de"]
            and row.get("v35_tokenwise_de") == cov_by[locus]["token_glosses_de"]
            and not FILLER.search(row.get("v35_tokenwise_de", ""))
            for locus, row in affected_by.items()
        ),
        "affected-line source/translation fidelity",
    )

    reality = read_tsv(ART / "SOURCE_READING_AUDIT.tsv")
    expected_source_loci = {"f33r.5", "f66v.5", "f93r.6", "f93r.32", "f115v.44", "f56r.13", "f80v.21", "f107r.41", "f41r.6", "f104v.29"}
    check(len(reality) == 10 and {row.get("locus") for row in reality} == expected_source_loci, "ten source-reading audits")
    check(
        all(
            row.get("locus") in cross_by
            and row.get("zl3b_line") == cross_by[row["locus"]]["zl3b_clean"]
            and row.get("it2a_line") == cross_by[row["locus"]]["it2a_clean"]
            and row.get("rf1b_line") == cross_by[row["locus"]]["rf1b_clean"]
            and row.get("all_three_present") == cross_by[row["locus"]]["all_three_present"]
            and row.get("all_present_exact") == cross_by[row["locus"]]["all_present_exact"]
            for row in reality
        ),
        "source-reading three-reader fidelity",
    )

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    actual_rounds = []
    for row in rounds:
        actual_rounds.append(
            (
                int(row["round"]), row["surface"], int(row["dictionary_entries"]),
                int(row["known_token_positions"]), int(row["unknown_token_positions"]),
                int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]),
                int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]),
                int(row["working_glossary_surfaces"]),
            )
        )
    check(tuple(actual_rounds) == ROUND_METRICS, "five-step V34-to-V35 sequential replay", repr(actual_rounds))

    # Family artifacts are recognized by their content-bearing names; exact
    # row/column gates are supplied once the packet has been materialized.
    family_names = {
        "K_T_AM_FAMILY_GRID.tsv", "F_HEAD_BODY_FAMILY_ATLAS.tsv", "F_HEAD_BODY_OCCURRENCES.tsv",
        "SHEDEFAM_BOUND_F_AUDIT.tsv", "S_CHO_S_FAMILY_EVIDENCE.tsv", "KCHEO_TCHEO_FAMILY_ATLAS.tsv",
    }
    for name in sorted(family_names):
        check((ART / name).is_file(), f"family/rival artifact:{name}")

    if all((ART / name).is_file() for name in family_names):
        am_rows = read_tsv(ART / "K_T_AM_FAMILY_GRID.tsv")
        am_by = {row["surface"]: row for row in am_rows}
        check(len(am_rows) == 8 and set(am_by) == set(AM_GRID), "eight-cell K/T-AM artifact")
        am_ok = True
        for surface, expected in AM_GRID.items():
            row = am_by.get(surface, {})
            am_ok &= tuple(
                int(row.get(field, "-1"))
                for field in ("occurrences", "lines", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
            ) == expected
            am_ok &= (row.get("v35_decision") == "ACCEPT_EXACT_WHOLE") == (surface == "otam")
        check(am_ok, "K/T-AM artifact/raw recensus and decision confinement")
        check(
            tuple(int(am_by["otam"][field]) for field in ("initial", "medial", "final", "only")) == (0, 16, 28, 0),
            "OTAM artifact position profile",
        )

        f_atlas = read_tsv(ART / "F_HEAD_BODY_FAMILY_ATLAS.tsv")
        observed = {row["eva"] for row in token_rows}
        shared_bodies = sorted(
            {
                surface[1:]
                for surface in observed
                if len(surface) > 1 and surface.startswith("f")
                and any(head + surface[1:] in observed for head in "psrl")
            }
        )
        atlas_by = {(row["body"], row["head"]): row for row in f_atlas}
        check(len(shared_bodies) == 43 and len(f_atlas) == len(atlas_by) == 215, "43-body x five-head F atlas")
        check(set(atlas_by) == {(body, head) for body in shared_bodies for head in "psrlf"}, "F atlas exact body/head grid")
        atlas_surfaces = {head + body for body in shared_bodies for head in "psrlf"}
        atlas_records = independent_records(token_rows, cross_rows, atlas_surfaces)
        atlas_ok = True
        complete_bodies: set[str] = set()
        strong_bodies: set[str] = set()
        for body in shared_bodies:
            supported = [head for head in "psrl" if head + body in observed]
            if len(supported) == 4:
                complete_bodies.add(body)
            if len(supported) >= 3 and body != "cho":
                strong_bodies.add(body)
            for head in "psrlf":
                row = atlas_by[(body, head)]
                surface = head + body
                actual = census(atlas_records, surface)
                atlas_ok &= (
                    row["surface"] == surface
                    and tuple(
                        int(row[field])
                        for field in ("occurrences", "lines", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
                    ) == actual
                    and int(row["four_head_support_count"]) == len(supported)
                    and row["four_head_support"] == "|".join(supported)
                    and int(row["complete_p_s_r_l_f_grid"]) == int(len(supported) == 4)
                    and "F_VALUE_BOUND" in row["interpretation"]
                )
        check(atlas_ok, "independent 215-row F-head atlas replay")
        check(complete_bodies == set(F_COMPLETE_BODIES), "eight complete P/S/R/L/F bodies from raw atlas", repr(sorted(complete_bodies)))
        check(strong_bodies == {surface[1:] for surface in F_CLEAR}, "twelve strong F bodies exclude bound CHO", repr(sorted(strong_bodies)))

        f_occurrences = read_tsv(ART / "F_HEAD_BODY_OCCURRENCES.tsv")
        raw_f_records = independent_records(token_rows, cross_rows, {"f" + body for body in shared_bodies})
        expected_f_occ: dict[tuple[str, str], dict[str, object]] = {}
        for surface in sorted({str(row["eva"]) for row in raw_f_records}):
            members = [row for row in raw_f_records if row["eva"] == surface]
            for ordinal, row in enumerate(members, 1):
                expected_f_occ[(surface, str(ordinal))] = row
        f_occ_by = {(row["surface"], row["occurrence"]): row for row in f_occurrences}
        check(len(f_occurrences) == len(f_occ_by) == len(expected_f_occ) == 67 and set(f_occ_by) == set(expected_f_occ), "67 shared-body F occurrences")
        f_occ_ok = True
        for key, raw in expected_f_occ.items():
            row = f_occ_by.get(key, {})
            f_occ_ok &= (
                row.get("body") == key[0][1:]
                and row.get("page") == raw["page"]
                and row.get("locus") == raw["locus"]
                and row.get("line_position") == raw["line_position"]
                and row.get("reader_exact") == str(raw["reader_exact"])
                and row.get("split_normalized") == str(raw["split_normalized"])
                and row.get("zl3b_line") == raw["zl3b_line"]
                and row.get("it2a_line") == raw["it2a_line"]
                and row.get("rf1b_line") == raw["rf1b_line"]
            )
        check(f_occ_ok and sum(int(row["reader_exact"]) for row in f_occurrences) == 42, "independent F occurrence source/reader replay")

        shede = read_tsv(ART / "SHEDEFAM_BOUND_F_AUDIT.tsv")
        shede_by = {row["surface"]: row for row in shede}
        check(len(shede) == 3 and set(shede_by) == {"shedey", "shedeeey", "shedefam"}, "three-row SHEDEFAM bound audit")
        check(
            shede_by["shedefam"].get("composition") == deck_by["shedefam"].get("composition")
            and "only here" in shede_by["shedefam"].get("note", "")
            and shede_by["shedefam"].get("decision") == "ACCEPT_TARGET_WHOLE_WITH_READER_WARNING",
            "SHEDEFAM F value remains local and reader-warned",
        )

        s_rows = read_tsv(ART / "S_CHO_S_FAMILY_EVIDENCE.tsv")
        check(len(s_rows) == 14, "fourteen-row S-CHO-S evidence atlas")
        global_s = [row for row in s_rows if row["evidence_type"] == "GLOBAL_TERMINAL_S_PROFILE"]
        terminal_surfaces = {row["eva"] for row in token_rows if len(row["eva"]) > 1 and row["eva"].endswith("s")}
        terminal_records = independent_records(token_rows, cross_rows, terminal_surfaces)
        check(
            len(global_s) == 1
            and tuple(
                int(global_s[0][field])
                for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
            )
            == (
                len(terminal_records), len({str(row["page"]) for row in terminal_records}),
                sum(int(row["reader_exact"]) for row in terminal_records),
                sum(int(row["split_normalized"]) for row in terminal_records),
            )
            == (725, 155, 524, 537)
            and "NOT_FREE_VALUE" in global_s[0]["role"],
            "independent global terminal-S artifact replay",
        )
        surface_s = {row["surface_or_locus"]: row for row in s_rows if row["evidence_type"] == "SURFACE_FAMILY"}
        expected_s_surfaces = {"scho", "schos", "rchos", "fchos", *TERMINAL_S_CORE, "schol", "schor"}
        check(set(surface_s) == expected_s_surfaces, "twelve exact S-family surface rows")
        s_family_records = independent_records(token_rows, cross_rows, expected_s_surfaces)
        s_family_ok = True
        for surface, row in surface_s.items():
            actual = census(s_family_records, surface)
            s_family_ok &= tuple(
                int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
            ) == (actual[0], actual[2], actual[3], actual[4])
            s_family_ok &= "no global terminal-S value" in row["note"]
        check(s_family_ok, "independent twelve-surface S-family replay")
        boundaries = [row for row in s_rows if row["evidence_type"] == "THREE_TOKEN_BOUNDARY"]
        check(
            len(boundaries) == 1 and boundaries[0]["surface_or_locus"] == "f93r.6"
            and boundaries[0]["parse_or_sequence"] == "s | cho | s"
            and boundaries[0]["reader_exact_occurrences"] == "1",
            "S|CHO|S boundary artifact",
        )

        kcheo_rows = read_tsv(ART / "KCHEO_TCHEO_FAMILY_ATLAS.tsv")
        kcheo_by = {row["surface"]: row for row in kcheo_rows}
        check(len(kcheo_rows) == 8 and set(kcheo_by) == set(K_T_CHEO), "eight-cell K/T-CHEO artifact")
        kcheo_ok = True
        for surface, expected in K_T_CHEO.items():
            row = kcheo_by.get(surface, {})
            kcheo_ok &= tuple(
                int(row.get(field, "-1"))
                for field in ("occurrences", "lines", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
            ) == expected
            kcheo_ok &= (row.get("decision") == "ACCEPT_TARGET_WHOLE") == (surface == "chokcheo")
        check(kcheo_ok, "K/T-CHEO artifact/raw recensus and target confinement")
        check(
            kcheo_by["chokcheo"].get("composition") == deck_by["chokcheo"].get("composition")
            and kcheo_by["cheokcheo"].get("composition", "").startswith("CHEO_DRY_PREPARED+K_HOT"),
            "CHO outer nesting distinguished from CHEO outer nesting",
        )

    target_run = result.get("target_run", {})
    check(
        (
            target_run.get("candidates"), target_run.get("accepted_whole_cards"),
            target_run.get("audited_occurrences"), target_run.get("target_lines"), target_run.get("target_pages"),
            target_run.get("all_reader_exact_occurrences"), target_run.get("split_normalized_occurrences"),
            target_run.get("reader_variant_warnings"), target_run.get("hard_collisions"),
        )
        == (4, 4, 47, 46, 37, 41, 41, 6, 0),
        "result target metrics",
        repr(target_run),
    )
    check(target_run.get("accepted_surfaces") == list(TARGET_ORDER), "result accepted order")
    check(result.get("coverage", {}).get("base") == BASE_METRICS and result.get("coverage", {}).get("final") == FINAL_METRICS, "result coverage packet")
    check(
        result.get("coverage", {}).get("newly_completed_lines") == 5
        and result.get("coverage", {}).get("newly_exposed_one_hole_lines") == 1
        and result.get("coverage", {}).get("affected_lines") == 46,
        "result closure packet",
    )
    working = result.get("working_dictionary", {})
    check(
        (
            working.get("v34_entries"), working.get("v35_entries"), working.get("accepted_tail_entries"),
            working.get("v34_glossary_surfaces"), working.get("v35_glossary_surfaces"),
        )
        == (570, 574, 4, 491, 495),
        "result dictionary metrics",
    )
    claim = str(result.get("claim_boundary", "")).lower()
    check(
        all(
            term in claim
            for term in (
                "exploratory", "exact-whole", "plaintext", "substring", "free component",
                "phonetics", "language", "ingredient identity", "f1r", "new page", "image",
            )
        ),
        "result claim ceiling",
        claim,
    )

    inputs = result.get("inputs", {})
    required_input_subset = {
        str(G657_ALLOW), str(G657_COVERAGE), str(G657_COMPLETE), str(G657_ONE), str(G657_GLOSSARY),
        str(G657_DICTIONARY), str(G657 / "artifacts/RESULT.json"), str(G657 / "REPORT.md"),
        "experiments/yolo/gdt635_initial_head_same_remainder_swaps/REPORT.md",
        "experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md",
        "experiments/yolo/gdt640_downstream_component_prediction/REPORT.md",
        str(TOKENS), str(CROSS),
    }
    check(required_input_subset <= set(inputs), "result primary input subset")
    check(all(not Path(path).is_absolute() and (ROOT / path).is_file() for path in inputs), "result input paths local and present")
    for path, digest in inputs.items():
        if not Path(path).is_absolute() and (ROOT / path).is_file():
            check(sha256(ROOT / path) == digest, f"result input hash:{path}")
    outputs = result.get("outputs", {})
    check(bool(outputs) and all(Path(path).parent == BASE / "artifacts" for path in outputs), "result output paths confined to artifact directory")
    for path, digest in outputs.items():
        check((ROOT / path).is_file() and sha256(ROOT / path) == digest, f"result output hash:{path}")

    report_text = REPORT.read_text(encoding="utf-8")
    report_lower = report_text.lower()
    report_flat = re.sub(r"\s+", " ", report_lower)
    for needle in (
        "47 tokenpositionen", "46 zeilen", "37 seiten", "41 positionen",
        "ein maß eingeweichter blütendroge", "trockene arzneimischung aus samen", "trockenansatz aus heißem trockenpräparat",
        "102 token", "67 davon", "acht körper", "725 tokenfinalen", "622 haben noch ein folgetoken",
        "f93r.6", "s | cho | s", "f80v.21", "nackte form `y`",
    ):
        check(needle in report_flat, f"report contains:{needle}")
    check(
        "ein maß kalten ansatzes" in report_flat or "ein maß des kalten ansatzes" in report_flat,
        "report contains practical OTAM measure",
    )
    check("shd | she | efam" in report_lower, "report retains complete RF1b SHEDEFAM split")
    for source in (
        "https://digi.vatlib.it/iiif/MSS_Pal.lat.1234/manifest.json",
        "https://celt.ucc.ie/published/G600006/text554.html",
        "https://celt.ucc.ie/published/G600006/text397.html",
        "https://wellcomecollection.org/works/n674z2xd",
        "https://wellcomecollection.org/works/rexwctzt",
    ):
        check(source in report_text, f"historical primary comparator:{source}")
    check(
        "beweisen keine lateinische lautung" in report_flat
        and "nicht der beweis `s=species`" in report_flat,
        "historical comparators remain architecture analogies",
    )
    # Prose may quote rejected filler terms while explaining the rejection;
    # executable semantic tables may not use them as readings.
    scan_paths = sorted(ART.glob("*.tsv"))
    filler_hits = [str(path.relative_to(ROOT)) for path in scan_paths if FILLER.search(path.read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic filler in release packet", repr(filler_hits))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT658" and manifest.get("slug") == "four_residual_concrete_completion", "manifest identity")
    check(manifest.get("status") == STATUS, "manifest status")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(
        manifest.get("commands") == {"run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"},
        "manifest commands",
    )
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation packet")
    check({"GDT635", "GDT636", "GDT640", "GDT657"} <= set(manifest.get("dependencies", [])), "manifest dependency core")
    question = str(manifest.get("question", "")).lower()
    ceiling = str(manifest.get("claim_ceiling", "")).lower()
    check(len(question) >= 80 and all(term in question for term in ("four", "residual", "concrete", "famil")), "manifest question core")
    check(
        len(ceiling) >= 120
        and all(term in ceiling for term in ("explor", "exact whole", "reader", "substring", "plaintext", "ingredient")),
        "manifest claim ceiling core",
    )
    manifest_inputs = {row.get("path"): row for row in manifest.get("inputs", [])}
    check(set(manifest_inputs) == set(inputs), "manifest/result input identity")
    for path, row in manifest_inputs.items():
        if path in inputs and (ROOT / path).is_file():
            check(row.get("sha256") == inputs[path] == sha256(ROOT / path) and bool(row.get("role")), f"manifest input seal:{path}")
    manifest_outputs = {row.get("path"): row for row in manifest.get("outputs", [])}
    required_manifest_outputs = {
        str(BASE / path)
        for path in ("METHOD.md", "README.md", "REPORT.md", "artifacts/README.md", "artifacts/RESULT.json", "artifacts/VALIDATION.json", "src/run.py", "src/validate.py")
    } | set(outputs)
    check(required_manifest_outputs <= set(manifest_outputs), "manifest core output inventory")
    for path, row in manifest_outputs.items():
        target = ROOT / str(path)
        check(not Path(str(path)).is_absolute() and target.is_file() and bool(row.get("role")), f"manifest output path:{path}")
        if str(path) != str(BASE / "artifacts/VALIDATION.json") and target.is_file():
            check(row.get("sha256") == sha256(target), f"manifest output seal:{path}")

    # Only now, after raw census, semantic/family, coverage, provenance, report
    # and manifest gates, may the implementation be imported and replayed.
    try:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="gdt658_validate_") as temporary:
            replay = Path(temporary)
            signature = inspect.signature(builder.build)
            if len(signature.parameters) != 1:
                raise RuntimeError(f"unexpected build signature: {signature}")
            builder.build(replay)
            expected_replay = {Path(path).name for path in outputs} | {"RESULT.json"}
            check({path.name for path in replay.iterdir()} == expected_replay, "replay output set")
            for name in sorted(expected_replay):
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
