#!/usr/bin/env python3
"""Independent release validator for GDT655."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
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
BASE = Path("experiments/yolo/gdt655_dal_al_measured_material_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G654 = Path("experiments/yolo/gdt654_ar_or_surface_consolidation")
G654_ALLOW = G654 / "artifacts/PAGE_ALLOWLIST.tsv"
G654_COVERAGE = G654 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V31.tsv"
G654_COMPLETE = G654 / "artifacts/COMPLETE_PASSAGES_V31.tsv"
G654_ONE = G654 / "artifacts/ONE_UNKNOWN_PASSAGES_V31.tsv"
G654_GLOSSARY = G654 / "artifacts/V31_EXACT_TOKEN_GLOSSARY.tsv"
G654_DICTIONARY = G654 / "artifacts/WORKING_DICTIONARY_V31.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
STATUS = "PASS_18_ANCHORED_PLUS_1_PREDICTED_DAL_AL_SURFACES__V32"
RESULT_CONTENT = "9263a1fd1a7d9cfa83740a9f60e6fb8fa22b0c6e801e564e106644e2de62e5f1"

# surface: mode, V32 meaning, composition, occurrences, pages, exact, normalized
TARGETS = {
    "al": ("NEW_EXACT_WHOLE", "Rohstoffklasse I", "AL_CLASS_I", 204, 63, 167, 167),
    "dal": ("NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I", "D_MEASURE+AL_CLASS_I", 191, 87, 147, 147),
    "chdal": ("NEW_EXACT_WHOLE", "trockene abgemessene Rohstoffmenge I am Gradanfang", "CH_DRY_START+DAL_MEASURED_MATERIAL_I", 19, 15, 13, 13),
    "shedal": ("NEW_EXACT_WHOLE", "feuchte abgemessene Rohstoffmenge I in der Gradmitte", "SHE_MOIST_MIDDLE+DAL_MEASURED_MATERIAL_I", 11, 7, 7, 7),
    "ail": ("NEW_EXACT_WHOLE", "Rohstoffklasse II", "AL_CLASS_II", 5, 4, 3, 3),
    "aiil": ("NEW_EXACT_WHOLE", "Rohstoffklasse III", "AL_CLASS_III", 1, 1, 1, 1),
    "dail": ("NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge II", "D_MEASURE+AL_CLASS_II", 2, 2, 2, 2),
    "daiil": ("READER_UNSTABLE_COMPOSITIONAL_WHOLE", "abgemessene Rohstoffmenge III", "D_MEASURE+AL_CLASS_III", 1, 1, 0, 0),
    "aly": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, Grundform", "AL_CLASS_I+Y_BASE", 18, 16, 12, 12),
    "aldy": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, abgeschlossen", "AL_CLASS_I+DY_COMPLETE", 10, 10, 5, 5),
    "daly": ("NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I, Grundform", "DAL_MEASURED_MATERIAL_I+Y_BASE", 24, 19, 18, 18),
    "daldy": ("NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I, abgeschlossen", "DAL_MEASURED_MATERIAL_I+DY_COMPLETE", 19, 17, 6, 8),
    "chedal": ("NEW_EXACT_WHOLE", "trockene abgemessene Rohstoffmenge I in der Gradmitte", "CHE_DRY_MIDDLE+DAL_MEASURED_MATERIAL_I", 22, 15, 15, 15),
    "shdal": ("NEW_EXACT_WHOLE", "feuchte abgemessene Rohstoffmenge I am Gradanfang", "SH_MOIST_START+DAL_MEASURED_MATERIAL_I", 4, 4, 3, 3),
    "odal": ("NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I im Ansatz", "O_PREP+DAL_MEASURED_MATERIAL_I", 14, 14, 11, 11),
    "qodal": ("NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I im Ansatz", "QO_SCOPE+DAL_MEASURED_MATERIAL_I", 7, 6, 6, 6),
    "oral": ("REVISE_AL_OR_COMPOSITION", "Rohstoffportion, Klasse I", "OR_PORTION+AL_CLASS_I", 10, 10, 6, 7),
    "chdaly": ("REVISE_DAL_MODEL", "trockene abgemessene Rohstoffmenge I am Gradanfang, Grundform", "CH_DRY_START+DAL_MEASURED_MATERIAL_I+Y_BASE", 3, 3, 3, 3),
    "sodal": ("REVISE_DAL_MODEL", "abgemessene Saat-Rohstoffmenge I im Ansatz", "S_SEED+O_PREP+DAL_MEASURED_MATERIAL_I", 2, 2, 1, 1),
}
TARGET_ORDER = list(TARGETS)
REVISED = {surface for surface, spec in TARGETS.items() if spec[0].startswith("REVISE")}
PREDICTED = {"daiil"}
NEW = {surface for surface, spec in TARGETS.items() if spec[0].startswith("NEW")}
EXTENDED = set(TARGETS) - REVISED

# family, surface, decomposition, level/role, planned role, occ, pages, exact, normalized, status
LATTICE = (
    ("AL_MINIM_LADDER", "al", "A+L", "I", "TARGET", 204, 63, 167, 167, "ACCEPTED_V32"),
    ("AL_MINIM_LADDER", "ail", "A+I+L", "II", "TARGET", 5, 4, 3, 3, "ACCEPTED_V32"),
    ("AL_MINIM_LADDER", "aiil", "A+II+L", "III", "TARGET", 1, 1, 1, 1, "ACCEPTED_V32"),
    ("AL_MINIM_LADDER", "aiiil", "A+III+L", "IV", "ZERO_EXACT_HOLD", 1, 1, 0, 0, "OBSERVED_ZERO_EXACT_HOLD"),
    ("AL_TAILS", "aly", "AL+Y", "BASE", "TARGET", 18, 16, 12, 12, "ACCEPTED_V32"),
    ("AL_TAILS", "aldy", "AL+DY", "COMPLETE", "TARGET", 10, 10, 5, 5, "ACCEPTED_V32"),
    ("D_AL_MINIM_LADDER", "dal", "D+A+L", "I", "TARGET", 191, 87, 147, 147, "ACCEPTED_V32"),
    ("D_AL_MINIM_LADDER", "dail", "D+A+I+L", "II", "TARGET", 2, 2, 2, 2, "ACCEPTED_V32"),
    ("D_AL_MINIM_LADDER", "daiil", "D+A+II+L", "III", "TARGET_READER_UNSTABLE", 1, 1, 0, 0, "ACCEPTED_V32"),
    ("D_AL_TAILS", "daly", "DAL+Y", "BASE", "TARGET", 24, 19, 18, 18, "ACCEPTED_V32"),
    ("D_AL_TAILS", "daldy", "DAL+DY", "COMPLETE", "TARGET", 19, 17, 6, 8, "ACCEPTED_V32"),
    ("DRY_MOIST_DAL_SHELLS", "chdal", "CH+DAL", "DRY", "TARGET", 19, 15, 13, 13, "ACCEPTED_V32"),
    ("DRY_MOIST_DAL_SHELLS", "chedal", "CHE+DAL", "DRY_BOUND", "TARGET", 22, 15, 15, 15, "ACCEPTED_V32"),
    ("DRY_MOIST_DAL_SHELLS", "shdal", "SH+DAL", "MOIST", "TARGET", 4, 4, 3, 3, "ACCEPTED_V32"),
    ("DRY_MOIST_DAL_SHELLS", "shedal", "SHE+DAL", "MOIST_BOUND", "TARGET", 11, 7, 7, 7, "ACCEPTED_V32"),
    ("PREPARATION_DAL_SHELLS", "odal", "O+DAL", "O_PREP", "TARGET", 14, 14, 11, 11, "ACCEPTED_V32"),
    ("PREPARATION_DAL_SHELLS", "qodal", "QO+DAL", "QO_SCOPE", "TARGET", 7, 6, 6, 6, "ACCEPTED_V32"),
    ("PORTION_AL_COMPOUND", "oral", "OR+AL", "PORTION_CLASS_I", "TARGET_REVISION", 10, 10, 6, 7, "ACCEPTED_V32"),
    ("HEAD_DAL_COMPOUNDS", "chdaly", "CH+DAL+Y", "DRY_BASE", "TARGET_REVISION", 3, 3, 3, 3, "ACCEPTED_V32"),
    ("HEAD_DAL_COMPOUNDS", "chdaldy", "CH+DAL+DY", "DRY_COMPLETE", "ZERO_EXACT_HOLD", 1, 1, 0, 0, "OBSERVED_ZERO_EXACT_HOLD"),
    ("HEAD_DAL_COMPOUNDS", "sodal", "S+O+DAL", "SEED_PREP", "TARGET_REVISION", 2, 2, 1, 1, "ACCEPTED_V32"),
    ("MATERIAL_AL_ANCHORS", "pal", "P+AL", "POWDER", "V31_ANCHOR", 2, 1, 2, 2, "V31_ANCHOR"),
    ("MATERIAL_AL_ANCHORS", "sal", "S+AL", "SEED", "V31_ANCHOR", 37, 28, 33, 33, "V31_ANCHOR"),
    ("MATERIAL_AL_ANCHORS", "ral", "R+AL", "ROOT", "V31_ANCHOR", 16, 14, 12, 13, "V31_ANCHOR"),
    ("MATERIAL_AL_ANCHORS", "lal", "L+AL", "WOOD", "V31_ANCHOR", 6, 6, 6, 6, "V31_ANCHOR"),
    ("MEASURED_AR_ANCHORS", "dar", "D+AR", "I", "V31_ANCHOR", 245, 110, 195, 195, "V31_ANCHOR"),
    ("MEASURED_AR_ANCHORS", "dair", "D+AIR", "II", "V31_ANCHOR", 77, 59, 63, 64, "V31_ANCHOR"),
    ("MEASURED_AR_ANCHORS", "daiir", "D+AIIR", "III", "V31_ANCHOR", 14, 14, 8, 8, "V31_ANCHOR"),
)
BOUNDARIES = {
    "G655-B01": ("AL_MATERIAL_SPLIT", "f54v.1", "sal / s al", ("s al", "sal", "s al")),
    "G655-B02": ("AL_MATERIAL_SPLIT", "f76r.33", "ral / r al", ("r ol", "ral", "r al")),
    "G655-B03": ("AL_MATERIAL_SPLIT", "f116r.50", "chal / ch al", ("ch al", "chal", "chal")),
    "G655-B04": ("AL_PORTION_SPLIT", "f79r.19", "oral / or al", ("oral", "or al", "or al")),
    "G655-B05": ("DAL_DY_SPLIT", "f75v.22", "daldy / dal dy", ("daldy", "dal dy", "daldy")),
    "G655-B06": ("DAL_DY_SPLIT", "f89v1.13", "daldy / dal dy", ("daldy", "dal dy", "dal dy")),
    "G655-B07": ("DAL_DY_Y_SPLIT", "f103r.1", "daldy / dal dy / dal y", ("daldy", "dal dy", "dal y")),
    "G655-B08": ("CHEDAL_PARSE_WARNING", "f58v.12", "chedal dy / che al y", ("chedal dy", "chedal dy", "che al y")),
    "G655-B09": ("S_ODAL_SPLIT", "f93r.11", "sodal / s odal", ("s odam", "sodal", "s odal")),
}
PARALLELS = {
    "G655-P01": ("f45v.4", "DAIN_DAIL_DAIR_LEVEL_II"),
    "G655-P02": ("f78r.27", "DAIIL_TO_AIIL_READER_FORK"),
    "G655-P03": ("f55r.9", "COORDINATED_D_OMISSION"),
    "G655-P04": ("f83r.48", "DAL_AND_CHDAL"),
    "G655-P05": ("f80v.28", "OR_AND_AL"),
    "G655-P06": ("f83v.16", "SAR_AND_AL"),
}
PAIRS = (
    ("al", "dal", "Rohstoffklasse I / abgemessene Rohstoffmenge I"),
    ("dal", "dail", "abgemessene Rohstoffmenge I / II"),
    ("dal", "daldy", "Rohstoffmenge / abgeschlossene Rohstoffmenge"),
    ("dal", "chdal", "Rohstoffmenge / trockene Rohstoffmenge"),
    ("al", "oral", "Rohstoffklasse I / Rohstoffportion"),
    ("dal", "daiin", "abgemessene Rohstoffmenge I / Mengen- oder Gradwert III"),
)
BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 15846, "unknown_token_positions": 16493,
    "complete_multi_token_lines": 123, "strict_complete_lines": 75, "one_unknown_lines": 197,
    "strict_one_unknown_lines": 44, "working_glossary_surfaces": 437,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 16398, "unknown_token_positions": 15941,
    "complete_multi_token_lines": 130, "strict_complete_lines": 77, "one_unknown_lines": 225,
    "strict_one_unknown_lines": 54, "working_glossary_surfaces": 453,
}
# surface, dictionary size, known, unknown, complete, strict complete, one-hole,
# strict one-hole, glossary size
ROUNDS = (
    ("BASE_V31", 510, 15846, 16493, 123, 75, 197, 44, 437),
    ("al", 511, 16050, 16289, 123, 75, 207, 48, 438),
    ("dal", 512, 16241, 16098, 127, 75, 216, 53, 439),
    ("chdal", 513, 16260, 16079, 128, 76, 216, 53, 440),
    ("shedal", 514, 16271, 16068, 129, 77, 216, 52, 441),
    ("ail", 515, 16276, 16063, 129, 77, 217, 52, 442),
    ("aiil", 516, 16277, 16062, 129, 77, 217, 52, 443),
    ("dail", 517, 16279, 16060, 129, 77, 219, 53, 444),
    ("daiil", 518, 16280, 16059, 129, 77, 220, 53, 445),
    ("aly", 519, 16298, 16041, 129, 77, 221, 53, 446),
    ("aldy", 520, 16308, 16031, 130, 77, 220, 53, 447),
    ("daly", 521, 16332, 16007, 130, 77, 223, 54, 448),
    ("daldy", 522, 16351, 15988, 130, 77, 224, 54, 449),
    ("chedal", 523, 16373, 15966, 130, 77, 224, 54, 450),
    ("shdal", 524, 16377, 15962, 130, 77, 224, 54, 451),
    ("odal", 525, 16391, 15948, 130, 77, 225, 54, 452),
    ("qodal", 526, 16398, 15941, 130, 77, 225, 54, 453),
    ("oral", 527, 16398, 15941, 130, 77, 225, 54, 453),
    ("chdaly", 528, 16398, 15941, 130, 77, 225, 54, 453),
    ("sodal", 529, 16398, 15941, 130, 77, 225, 54, 453),
)
NEW_COMPLETE = {"f75r.40", "f77v.13", "f77v.30", "f78r.27", "f83r.14", "f83r.47", "f83r.48"}
STRICT_NEW_COMPLETE = {"f83r.47", "f83r.48"}
QUALITY_AXIS_CURATED = {
    "f83r.47": "Kalt-trockener Ansatz am Gradanfang abgeschlossen; heiß-trockener Ansatz am Gradanfang abgeschlossen; feuchte abgemessene Rohstoffmenge I in der Gradmitte.",
    "f83r.48": "Abgemessene Rohstoffmenge I; trockener Drogenstoff; Holzstoff; trockene abgemessene Rohstoffmenge I am Gradanfang; Menge III.",
}
ONE_HOLE_INTROS = (10, 12, 1, 1, 1, 0, 2, 1, 1, 0, 3, 1, 0, 0, 1, 0, 0, 0, 0)
BUILDER_OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "DAL_AL_LATTICE_ATLAS.tsv",
    "BOUNDARY_EVIDENCE_ATLAS.tsv", "PARALLEL_MEASURE_EVIDENCE.tsv", "PAIR_CONTRAST_COUNTS.tsv",
    "REVISION_LEDGER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "CURATED_COMPLETE_PASSAGE_READINGS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V32_WORKING_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V32.tsv", "COMPLETE_PASSAGES_V32.tsv",
    "ONE_UNKNOWN_PASSAGES_V32.tsv", "WORKING_DICTIONARY_V32.tsv",
)
REPLAY_OUTPUTS = (*BUILDER_OUTPUTS, "RESULT.json")
INPUTS = {
    str(G654 / "src/run.py"), str(G654_ALLOW), str(G654_COVERAGE), str(G654_COMPLETE),
    str(G654_ONE), str(G654_GLOSSARY), str(G654_DICTIONARY), str(G654 / "artifacts/RESULT.json"),
    str(G654 / "REPORT.md"), "experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md",
    "experiments/yolo/gdt649_strict_v25_hole_completion/REPORT.md",
    "experiments/yolo/gdt653_strict_v29_boundary_compounds/REPORT.md", str(TOKENS), str(CROSS),
}
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


def independent_records(token_rows, cross_rows, surfaces: set[str]) -> list[dict[str, object]]:
    cross = {row["locus"]: row for row in cross_rows}
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        by_locus[row["locus"]].append(row)
    for line in by_locus.values():
        line.sort(key=lambda item: int(item["token_index"]))
    records: list[dict[str, object]] = []
    for surface in surfaces:
        members = [row for row in token_rows if row["eva"] == surface]
        members.sort(key=lambda item: (item["page"], item["locus"], int(item["token_index"])))
        seen: Counter[str] = Counter()
        for row in members:
            locus = row["locus"]
            seen[locus] += 1
            needed = seen[locus]
            reader_lines = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
            direct = [tokens.count(surface) for tokens in reader_lines]
            spans = [span_count(tokens, surface) for tokens in reader_lines]
            line = by_locus[locus]
            ordinal = next(i for i, token in enumerate(line, 1) if token is row)
            records.append({
                **row, "token_ordinal": ordinal,
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": cross[locus]["zl3b_clean"], "it2a_line": cross[locus]["it2a_clean"],
                "rf1b_line": cross[locus]["rf1b_clean"],
                "reader_exact": int(needed <= min(direct)),
                "split_normalized": int(needed <= min(spans)),
            })
    return records


def census(records: list[dict[str, object]], surface: str) -> tuple[int, int, int, int]:
    members = [row for row in records if row["eva"] == surface]
    return (len(members), len({str(row["page"]) for row in members}),
            sum(int(row["reader_exact"]) for row in members),
            sum(int(row["split_normalized"]) for row in members))


def metrics(coverage, complete, one_unknown, glossary_size: int) -> dict[str, int]:
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
    spec = importlib.util.spec_from_file_location("gdt655_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT655 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("schema") == "GDT655_DAL_AL_MEASURED_MATERIAL_RESULT_V1", "result schema")
    check(result.get("experiment_id") == "GDT655" and result.get("status") == STATUS, "result identity/status")
    check(result.get("content_sha256") == RESULT_CONTENT == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash and final quality-axis seal")

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allow_rows}
    check(len(allow_rows) == len(pages) == 179, "179 unique guarded pages")
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "f1r excluded and f84/f84r forbidden")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G654_ALLOW).read_bytes(), "V31 allowlist inherited byte-identically")
    token_rows, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    expected_token_stats = {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}
    expected_cross_stats = {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}
    check(len(token_rows) == 32339 and token_stats == expected_token_stats, "guarded token census", repr(token_stats))
    check(len(cross_rows) == 4137 and cross_stats == expected_cross_stats, "guarded cross census", repr(cross_stats))
    guard = result.get("guard", {})
    check(guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats, "result guarded counts")
    check(guard.get("allowed_pages") == 179 and guard.get("f1r") == "EXCLUDED" and guard.get("f84") == guard.get("f84r") == "FORBIDDEN" and guard.get("new_pages") == guard.get("new_images") == 0, "result guard ceiling")

    lattice_surfaces = {row[1] for row in LATTICE}
    records = independent_records(token_rows, cross_rows, lattice_surfaces | set(TARGETS))
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by) == 19 and list(deck_by) == TARGET_ORDER, "19 ordered target cards")
    check([row["candidate_id"] for row in deck] == [f"G655-C{i:02d}" for i in range(1, 20)], "ordered candidate ids")
    for index, (surface, spec) in enumerate(TARGETS.items(), 1):
        row = deck_by[surface]
        expected_counts = spec[3:]
        artifact_counts = tuple(int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(census(records, surface) == expected_counts, f"independent target census:{surface}", repr(census(records, surface)))
        check(artifact_counts == expected_counts, f"deck target census:{surface}", repr(artifact_counts))
        check((row["mode"], row["v32_meaning_de"], row["composition"]) == spec[:3], f"target value:{surface}")
        expected_decision = "ACCEPT_V32_READER_UNSTABLE_PREDICTED_WHOLE" if surface in PREDICTED else "ACCEPT_V32_EXACT_WHOLE"
        check(row["candidate_order"] == str(index) and row["decision"] == expected_decision, f"target admission:{surface}")
        check(bool(row["rival_de"] and row["strongest_counterargument"]), f"target rival/counterargument:{surface}")
    check(all(row.get("decision_basis", "").strip() for row in deck), "all target cards retain explicit decision basis")
    check(sum(spec[3] for spec in TARGETS.values()) == 567 and sum(spec[5] for spec in TARGETS.values()) == 426 and sum(spec[6] for spec in TARGETS.values()) == 429, "567/426/429 target totals")
    check(len([surface for surface, spec in TARGETS.items() if spec[5] > 0]) == 18 and PREDICTED == {surface for surface, spec in TARGETS.items() if spec[5] == 0}, "18 anchored plus one predicted")
    check(NEW == set(result["target_run"]["reader_anchored_new_surfaces"]) and EXTENDED == set(result["target_run"]["all_new_surfaces"]) and REVISED == set(result["target_run"]["revised_surfaces"]) and PREDICTED == set(result["target_run"]["reader_unstable_predicted_surfaces"]), "15 anchored-new, one predicted-new and three revised targets")

    lattice = read_tsv(ART / "DAL_AL_LATTICE_ATLAS.tsv")
    check(len(lattice) == 28, "28-row complete DAL/AL lattice")
    for row, expected in zip(lattice, LATTICE):
        family, surface, decomposition, level, role, occ, page_count, exact, normalized, status = expected
        identity = (row["family"], row["surface"], row["decomposition"], row["level_or_role"], row["planned_role"])
        artifact_counts = tuple(int(row[field]) for field in ("zl3b_occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(identity == expected[:5] and row["final_status"] == status, f"lattice identity/status:{surface}")
        check(census(records, surface) == (occ, page_count, exact, normalized) == artifact_counts, f"independent lattice census:{surface}")
        if surface in TARGETS:
            check(row["v32_meaning_de"] == TARGETS[surface][1], f"lattice target meaning:{surface}")
    lattice_by = {row["surface"]: row for row in lattice}
    check({surface for surface in ("aiiil", "chdaldy") if lattice_by[surface]["final_status"] == "OBSERVED_ZERO_EXACT_HOLD" and lattice_by[surface]["v32_meaning_de"] == "NOT_ASSIGNED"} == {"aiiil", "chdaldy"}, "AIIIL and CHDALDY retained as zero-exact holds")

    cross_by = {row["locus"]: row for row in cross_rows}
    boundary_rows = read_tsv(ART / "BOUNDARY_EVIDENCE_ATLAS.tsv")
    boundary_by = {row["bridge_id"]: row for row in boundary_rows}
    check(len(boundary_rows) == len(boundary_by) == 9 and list(boundary_by) == list(BOUNDARIES), "nine ordered boundary witnesses")
    for bridge_id, (kind, locus, diagnostic, patterns) in BOUNDARIES.items():
        row, source = boundary_by[bridge_id], cross_by[locus]
        check((row["evidence_type"], row["locus"], row["diagnostic_surface"]) == (kind, locus, diagnostic), f"boundary identity:{bridge_id}")
        check(row["page"] == source["page"] and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[field] for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")), f"boundary source fidelity:{bridge_id}")
        check(all(pattern in source[field] for pattern, field in zip(patterns, ("zl3b_clean", "it2a_clean", "rf1b_clean"))) and bool(row["supports"]), f"boundary split/fusion visible:{bridge_id}")

    parallel_rows = read_tsv(ART / "PARALLEL_MEASURE_EVIDENCE.tsv")
    parallel_by = {row["evidence_id"]: row for row in parallel_rows}
    check(len(parallel_rows) == len(parallel_by) == 6 and list(parallel_by) == list(PARALLELS), "six ordered parallel-measure witnesses")
    for evidence_id, (locus, relation) in PARALLELS.items():
        row, source = parallel_by[evidence_id], cross_by[locus]
        expected_exact = str(int(source["all_three_present"]) == 1 and int(source["all_present_exact"]) == 1)
        check((row["locus"], row["relation"], row["page"]) == (locus, relation, source["page"]), f"parallel identity:{evidence_id}")
        check(tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[field] for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")) and row["all_three_exact_line"] == expected_exact and bool(row["working_reading_de"]), f"parallel source fidelity:{evidence_id}")

    lines: dict[str, set[str]] = defaultdict(set)
    for row in token_rows:
        lines[row["locus"]].add(row["eva"])
    pair_rows = read_tsv(ART / "PAIR_CONTRAST_COUNTS.tsv")
    check(len(pair_rows) == 6, "six pair-contrast rows")
    for row, (first, second, distinction) in zip(pair_rows, PAIRS):
        loci = sorted(locus for locus, surfaces in lines.items() if first in surfaces and second in surfaces)
        exact_lines = sum(int(cross_by[locus]["all_three_present"]) == 1 and int(cross_by[locus]["all_present_exact"]) == 1 for locus in loci)
        expected_examples = "|".join(loci[:12]) or "NONE"
        check((row["first_surface"], row["second_surface"], row["required_distinction_de"]) == (first, second, distinction) and (int(row["cooccurrence_lines"]), int(row["all_reader_exact_lines"]), row["example_loci"]) == (len(loci), exact_lines, expected_examples), f"independent pair contrast:{first}/{second}")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 567, "567 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: spec[3] for surface, spec in TARGETS.items()}), "audit surface census")
    check(sum(int(row["reader_exact"]) for row in audits) == 426 and sum(int(row["split_normalized"]) for row in audits) == 429, "audit 426 exact and 429 normalized")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no target hard collisions")
    independent_by_surface = {surface: [row for row in records if row["eva"] == surface] for surface in TARGETS}
    audit_by_surface = {surface: [row for row in audits if row["surface"] == surface] for surface in TARGETS}
    for round_number, surface in enumerate(TARGET_ORDER, 1):
        expected_rows, artifact_rows = independent_by_surface[surface], audit_by_surface[surface]
        fidelity = len(expected_rows) == len(artifact_rows)
        for occurrence, (expected, row) in enumerate(zip(expected_rows, artifact_rows), 1):
            expected_support = "ALL_THREE_EXACT" if expected["reader_exact"] else "ALL_THREE_SPLIT_NORMALIZED" if expected["split_normalized"] else "READER_VARIANT"
            fidelity &= (
                row["audit_id"] == f"G655-A{round_number:02d}-{occurrence:04d}"
                and row["round"] == str(round_number) and row["mode"] == TARGETS[surface][0]
                and (row["page"], row["locus"], row["section"], row["language"], row["hand"])
                == tuple(str(expected[field]) for field in ("page", "locus", "section", "language", "hand"))
                and (row["token_ordinal"], row["previous"], row["following"])
                == (str(expected["token_ordinal"]), str(expected["previous"]), str(expected["following"]))
                and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line"))
                == tuple(str(expected[field]) for field in ("zl3b_line", "it2a_line", "rf1b_line"))
                and (row["reader_exact"], row["split_normalized"], row["reader_support"])
                == (str(expected["reader_exact"]), str(expected["split_normalized"]), expected_support)
            )
        check(fidelity, f"independent audit source/reader replay:{surface}")
    verdicts = Counter(row["verdict"] for row in audits)
    check(verdicts == Counter({"CONCRETE_CONTEXT_COMPATIBLE": 376, "SHORT_OR_OPAQUE_CONTEXT": 53, "READER_VARIANT_WARNING": 138}), "audit verdict totals")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 141 and Counter(row["reader_support"] for row in variants) == Counter({"ALL_THREE_SPLIT_NORMALIZED": 3, "READER_VARIANT": 138}), "141 non-exact variants: three splits and 138 warnings")
    expected_variants = Counter((row["surface"], row["page"], row["locus"], row["reader_support"], TARGETS[row["surface"]][1]) for row in audits if row["reader_exact"] == "0")
    artifact_variants = Counter((row["surface"], row["page"], row["locus"], row["reader_support"], row["working_meaning_de"]) for row in variants)
    check(artifact_variants == expected_variants and all(row["decision"] == "RETAIN_EXACT_ZL3B_WITH_READER_WARNING" for row in variants), "variant audit exactly covers non-exact targets")

    revisions = read_tsv(ART / "REVISION_LEDGER.tsv")
    revision_by = {row["surface"]: row for row in revisions}
    check(len(revisions) == 3 and list(revision_by) == ["oral", "chdaly", "sodal"], "three ordered visible composition revisions")
    check((revision_by["oral"]["v31_meaning_de"], revision_by["oral"]["v32_meaning_de"], revision_by["oral"]["occurrences"], revision_by["oral"]["reader_exact_occurrences"]) == ("Ansatz aus Wurzelrohstoff, Form I", TARGETS["oral"][1], "10", "6"), "ORAL revision and census")
    check((revision_by["chdaly"]["v31_meaning_de"], revision_by["chdaly"]["v32_meaning_de"]) == ("trockener Rohdrogenposten, Grundform", TARGETS["chdaly"][1]), "CHDALY revision")
    check((revision_by["sodal"]["v31_meaning_de"], revision_by["sodal"]["v32_meaning_de"]) == ("Ansatz aus einem Saatdrogenposten", TARGETS["sodal"][1]), "SODAL revision")

    base_gloss_rows = read_tsv(ROOT / G654_GLOSSARY)
    gloss_rows = read_tsv(ART / "V32_WORKING_TOKEN_GLOSSARY.tsv")
    base_gloss = {row["surface"]: row for row in base_gloss_rows}
    glossary = {row["surface"]: row for row in gloss_rows}
    check(len(base_gloss_rows) == len(base_gloss) == 437 and len(gloss_rows) == len(glossary) == 453, "glossary 437 to 453")
    check(set(glossary) == set(base_gloss) | EXTENDED, "exact 16-surface glossary extension")
    check(all(glossary[surface] == row for surface, row in base_gloss.items() if surface not in REVISED), "non-revised V31 glossary retained")
    for surface, spec in TARGETS.items():
        row = glossary[surface]
        predicted = surface in PREDICTED
        expected_card = (
            spec[1], f"GDT655:{spec[0]}",
            "READER_UNSTABLE_COMPOSITIONAL_WHOLE" if predicted else "EXACT_WHOLE_DAL_AL_CONSOLIDATION",
            "KNOWN_ZL3B_PREDICTED_WHOLE_READER_UNSTABLE" if predicted else "KNOWN_EXACT_WHOLE",
            "151" if predicted else "152",
        )
        check(tuple(row[field] for field in ("working_meaning_de", "source", "strength", "scope_state", "priority")) == expected_card, f"V32 glossary card:{surface}")
    check(not ({"aiiil", "chdaldy"} & set(glossary)), "zero-exact holds not exported to glossary")

    base_dictionary = read_tsv(ROOT / G654_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V32.tsv")
    additions = dictionary[len(base_dictionary):]
    check(len(base_dictionary) == 510 and len(dictionary) == 529, "dictionary 510 to 529")
    check(dictionary[:510] == base_dictionary, "V31 dictionary prefix unchanged")
    check([row["entry"].split("@", 1)[0] for row in additions] == TARGET_ORDER, "19 ordered dictionary additions")
    for index, (surface, row) in enumerate(zip(TARGET_ORDER, additions), 1):
        spec = TARGETS[surface]
        expected = (
            f"{surface}@GDT655_{'PREDICTED_WHOLE' if surface in PREDICTED else 'EXACT_WHOLE'}",
            "PREDICTED_ZL3B_WHOLE_READER_UNSTABLE" if surface in PREDICTED else f"EXACT_ZL3B_WHOLE_{spec[0]}",
            spec[1], spec[2], f"NEW_V32_ACCEPTED_ROUND_{index:02d}",
        )
        check(tuple(row[field] for field in ("entry", "kind", "working_meaning_de", "composition", "status")) == expected, f"dictionary addition:{surface}")
    defaults = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    check(len(defaults) == 19 and [row["surface"] for row in defaults] == TARGET_ORDER, "19 ordered accepted defaults")
    defaults_ok = all(
        row["entry"] == additions[index]["entry"] and row["working_meaning_de"] == TARGETS[row["surface"]][1]
        and row["composition"] == TARGETS[row["surface"]][2] and row["occurrences"] == str(TARGETS[row["surface"]][3])
        and row["acceptance_mode"] == TARGETS[row["surface"]][0]
        for index, row in enumerate(defaults)
    )
    check(defaults_ok, "accepted defaults mirror dictionary cards")

    base_cov = read_tsv(ROOT / G654_COVERAGE)
    base_complete = read_tsv(ROOT / G654_COMPLETE)
    base_one = read_tsv(ROOT / G654_ONE)
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V32.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V32.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V32.tsv")
    check(metrics(base_cov, base_complete, base_one, len(base_gloss)) == BASE_METRICS, "V31 metrics")
    check(metrics(coverage, complete, one, len(glossary)) == FINAL_METRICS, "V32 metrics")
    check(sum(int(row["token_count"]) for row in coverage) == 32339, "V32 token census")
    check(FINAL_METRICS["known_token_positions"] - BASE_METRICS["known_token_positions"] == 552 == sum(TARGETS[surface][3] for surface in EXTENDED), "552 newly known positions")
    base_cov_by = {row["locus"]: row for row in base_cov}
    cov_by = {row["locus"]: row for row in coverage}
    new_positions = Counter(row["locus"] for row in token_rows if row["eva"] in EXTENDED)
    check(all(int(cov_by[locus]["known_tokens"]) - int(base_cov_by[locus]["known_tokens"]) == new_positions[locus] for locus in cov_by), "linewise 16-extension deltas")
    target_loci = {row["locus"] for row in token_rows if row["eva"] in TARGETS}
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    affected_by = {row["locus"]: row for row in affected}
    check(len(affected) == len(affected_by) == len(target_loci) == 499 and set(affected_by) == target_loci, "499 exact affected lines")
    affected_ok = all(
        row["page"] == cov_by[locus]["page"] and row["zl3b_line"] == cov_by[locus]["zl3b_line"]
        and row["v31_tokenwise_de"] == base_cov_by[locus]["token_glosses_de"]
        and row["v32_tokenwise_de"] == cov_by[locus]["token_glosses_de"]
        and row["complete_v32"] == str(int(cov_by[locus]["unknown_tokens"]) == 0)
        for locus, row in affected_by.items()
    )
    check(affected_ok, "affected-line source and edition fidelity")

    base_complete_by = {row["locus"]: row for row in base_complete}
    complete_by = {row["locus"]: row for row in complete}
    check(set(complete_by) - set(base_complete_by) == NEW_COMPLETE, "exact seven new complete loci")
    new_rows = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_by = {row["locus"]: row for row in new_rows}
    check(len(new_rows) == len(new_by) == 7 and set(new_by) == NEW_COMPLETE, "seven new-complete artifact rows")
    check({row["locus"] for row in new_rows if row["strict_complete"] == "1"} == STRICT_NEW_COMPLETE, "two newly strict complete lines")
    check(all(row["curated_workshop_reading_de"] != "NOT_CURATED" and row["literal_v32_de"] and row["curated_workshop_reading_de"] for row in new_rows), "all seven new lines have concrete readings")
    curated = read_tsv(ART / "CURATED_COMPLETE_PASSAGE_READINGS.tsv")
    curated_by = {row["locus"]: row for row in curated}
    check(len(curated) == len(curated_by) == 7 and set(curated_by) == NEW_COMPLETE, "seven curated complete readings")
    check(all(row["curated_workshop_reading_de"] == new_by[locus]["curated_workshop_reading_de"] and "[" not in row["curated_workshop_reading_de"] and "?" not in row["curated_workshop_reading_de"] for locus, row in curated_by.items()), "curated readings concrete and synchronized")
    check(all(curated_by[locus]["curated_workshop_reading_de"] == reading == new_by[locus]["curated_workshop_reading_de"] for locus, reading in QUALITY_AXIS_CURATED.items()), "quality-axis curated readings fixed at f83r.47/f83r.48")

    exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    exposed_by = {row["locus"]: row for row in exposed}
    check(len(exposed) == len(exposed_by) == 34, "34 unique sequentially exposed one-hole rows")
    check(tuple(sum(row["introduced_round"] == str(i) for row in exposed) for i in range(1, 20)) == ONE_HOLE_INTROS, "one-hole introduction counts by round")
    sequential_ok = all(
        1 <= int(row["introduced_round"]) <= 19
        and row["enabled_by_surface"] == TARGET_ORDER[int(row["introduced_round"]) - 1]
        and row["enabled_by_surface"] in lines[row["locus"]]
        and row["unknown_tokens"] == "1" and row["unknown_ordinal"] in row["unknown_ordinals"].split("|")
        and row["unknown_surface"] in row["unknown_surfaces"].split("|")
        for row in exposed
    )
    check(sequential_ok, "one-hole rows retain round/surface/unknown provenance")
    base_one_loci, final_one_loci = {row["locus"] for row in base_one}, {row["locus"] for row in one}
    check(set(exposed_by) == (final_one_loci - base_one_loci) | {"f78r.27", "f83r.48"}, "sequential one-hole frontier reconciles with V31/V32")

    round_rows = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(round_rows) == 20 and [row["round"] for row in round_rows] == [str(i) for i in range(20)], "20 ordered coverage rounds")
    for index, expected in enumerate(ROUNDS):
        row = round_rows[index]
        observed = (row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]), int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]), int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]), int(row["working_glossary_surfaces"]))
        check(observed == expected, f"round metrics:{index}", repr(observed))
        check(row["dictionary_sha256"] == canonical_hash(dictionary[:int(row["dictionary_entries"])]), f"round dictionary hash:{index}")

    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    check(len(reality) == 30 and set(row["surface"] for row in reality) == set(TARGETS), "30 reality checks cover all 19 targets")
    reality_ok = all(
        row["locus"] in cross_by and row["zl3b_line"] == cross_by[row["locus"]]["zl3b_clean"]
        and row["tokenwise_v32_de"] == cov_by[row["locus"]]["token_glosses_de"]
        and row["working_reading_de"] and not FILLER.search(row["working_reading_de"])
        for row in reality
    )
    check(reality_ok, "reality-check source and reading fidelity")

    target_run = result.get("target_run", {})
    check((target_run.get("candidates"), target_run.get("accepted_whole_cards"), target_run.get("reader_anchored_exact_wholes"), target_run.get("reader_unstable_predicted_wholes"), target_run.get("audited_occurrences"), target_run.get("all_reader_exact_occurrences"), target_run.get("split_normalized_occurrences"), target_run.get("reader_variant_warnings"), target_run.get("hard_collisions")) == (19, 19, 18, 1, 567, 426, 429, 138, 0), "result target metrics")
    check(target_run.get("accepted_surfaces") == TARGET_ORDER, "result ordered accepted surfaces")
    check(target_run.get("verdicts") == dict(sorted({"CONCRETE_CONTEXT_COMPATIBLE": 376, "READER_VARIANT_WARNING": 138, "SHORT_OR_OPAQUE_CONTEXT": 53}.items())), "result verdict packet")
    check(result.get("coverage") == {"base": BASE_METRICS, "final": FINAL_METRICS, "newly_completed_lines": 7, "newly_exposed_one_hole_lines": 34, "affected_lines": 499}, "result coverage packet")
    working = result.get("working_dictionary", {})
    check((working.get("v31_entries"), working.get("v32_entries"), working.get("accepted_tail_entries"), working.get("v31_glossary_surfaces"), working.get("v32_glossary_surfaces")) == (510, 529, 19, 437, 453), "result dictionary metrics")
    check(working.get("v31_prefix_sha256") == canonical_hash(base_dictionary) and working.get("v32_sha256") == canonical_hash(dictionary), "result dictionary hashes")
    semantic = result.get("semantic_model", {})
    check(semantic.get("ORAL") == "Rohstoffportion, Klasse I" and semantic.get("zero_exact_holds") == ["aiiil", "chdaldy"] and "daiil=" in semantic.get("reader_unstable_prediction", "") and "f45v.4" in semantic.get("strongest_parallel", "") and "raw-drug lot" in semantic.get("strongest_rival", "") and {"CH_DRY_START", "SHE_MOIST_MIDDLE"} <= set(semantic.get("structural_tags_not_free_words", [])), "result ORAL/lattice/rival/quality-axis core")
    claim = str(result.get("claim_boundary", "")).lower()
    check(all(term in claim for term in ("exploratory", "fifteen new", "reader-unstable", "oral", "chdaly", "sodal", "no free component", "other zero-exact", "plaintext", "exact ingredient", "f1r", "new page", "new image")), "result claim core including ORAL and no-other-zero-exact ceiling")

    scan_paths = [ROOT / BASE / name for name in ("REPORT.md", "METHOD.md", "README.md", "artifacts/README.md", "artifacts/RESULT.json")] + sorted(ART.glob("*.tsv"))
    filler_hits = [str(path.relative_to(ROOT)) for path in scan_paths if FILLER.search(path.read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic filler", repr(filler_hits))
    inputs = result.get("inputs", {})
    check(set(inputs) == INPUTS and all(not Path(path).is_absolute() and (ROOT / path).is_file() for path in inputs), "result input path set")
    for path, digest in inputs.items():
        check(sha256(ROOT / path) == digest, f"result input hash:{path}")
    outputs = result.get("outputs", {})
    expected_outputs = {str(BASE / "artifacts" / name) for name in BUILDER_OUTPUTS}
    check(set(outputs) == expected_outputs, "result output path set")
    for path, digest in outputs.items():
        check(sha256(ROOT / path) == digest, f"result output hash:{path}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT655" and manifest.get("slug") == "dal_al_measured_material_completion", "manifest identity")
    check(manifest.get("status") == STATUS, "manifest status")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("commands") == {"run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"}, "manifest commands")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check({"GDT636", "GDT649", "GDT653", "GDT654"} <= set(manifest.get("dependencies", [])), "manifest dependency core")
    question, ceiling = str(manifest.get("question", "")).lower(), str(manifest.get("claim_ceiling", "")).lower()
    check(len(question) >= 80 and all(term in question for term in ("al", "dal", "eighteen", "daiil", "oral", "concrete")), "manifest question core")
    check(len(ceiling) >= 120 and all(term in ceiling for term in ("explor", "exact whole", "reader", "free component", "plaintext", "exact ingredient")), "manifest claim ceiling core")
    manifest_inputs = {row.get("path"): row for row in manifest.get("inputs", [])}
    check(set(manifest_inputs) == set(inputs), "manifest/result inputs")
    for path, row in manifest_inputs.items():
        check(row.get("sha256") == inputs[path] == sha256(ROOT / path) and bool(row.get("role")), f"manifest input seal:{path}")
    manifest_outputs = {row.get("path"): row for row in manifest.get("outputs", [])}
    required = {str(BASE / path) for path in (
        "METHOD.md", "README.md", "REPORT.md", "artifacts/README.md", "artifacts/TARGET_DECISION_DECK.tsv",
        "artifacts/DAL_AL_LATTICE_ATLAS.tsv", "artifacts/BOUNDARY_EVIDENCE_ATLAS.tsv",
        "artifacts/PARALLEL_MEASURE_EVIDENCE.tsv", "artifacts/READER_VARIANT_AUDIT.tsv",
        "artifacts/REVISION_LEDGER.tsv", "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        "artifacts/CURATED_COMPLETE_PASSAGE_READINGS.tsv", "artifacts/NEWLY_COMPLETED_LINES.tsv",
        "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "artifacts/RESULT.json",
        "artifacts/V32_WORKING_TOKEN_GLOSSARY.tsv", "artifacts/ALL_LINE_CONCRETE_COVERAGE_V32.tsv",
        "artifacts/COMPLETE_PASSAGES_V32.tsv", "artifacts/ONE_UNKNOWN_PASSAGES_V32.tsv",
        "artifacts/WORKING_DICTIONARY_V32.tsv", "artifacts/VALIDATION.json", "src/run.py", "src/validate.py",
    )}
    check(required <= set(manifest_outputs), "manifest core outputs")
    for path, row in manifest_outputs.items():
        target_path = ROOT / str(path)
        check(not Path(str(path)).is_absolute() and target_path.is_file() and bool(row.get("role")), f"manifest output path:{path}")
        if str(path) != str(BASE / "artifacts/VALIDATION.json") and target_path.is_file():
            check(row.get("sha256") == sha256(target_path), f"manifest output seal:{path}")

    report_text = REPORT.read_text(encoding="utf-8").lower()
    for needle in ("rohstoffklasse", "abgemessene rohstoffmenge", "rohstoffportion, klasse i", "oral", "trockene abgemessene rohstoffmenge i am gradanfang", "trockene abgemessene rohstoffmenge i in der gradmitte", "feuchte abgemessene rohstoffmenge i am gradanfang", "feuchte abgemessene rohstoffmenge i in der gradmitte", "daiil", "f45v.4", "567", "426", "429", "15.846", "16.398", "f75r.40", "f83r.48", "explorative"):
        check(needle in report_text, f"report contains:{needle}")

    # Import and full deterministic replay deliberately run last: every census,
    # semantic, boundary, edition and hash check above is builder-independent.
    try:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="gdt655_validate_") as temporary:
            replay = Path(temporary)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(REPLAY_OUTPUTS), "replay output set")
            for name in REPLAY_OUTPUTS:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT655_VALIDATION_V1", "experiment_id": "GDT655",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT655 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT655 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
