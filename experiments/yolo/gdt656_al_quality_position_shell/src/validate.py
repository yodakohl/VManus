#!/usr/bin/env python3
"""Independent release validator for GDT656."""
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
BASE = Path("experiments/yolo/gdt656_al_quality_position_shell")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G655 = Path("experiments/yolo/gdt655_dal_al_measured_material_completion")
G655_ALLOW = G655 / "artifacts/PAGE_ALLOWLIST.tsv"
G655_COVERAGE = G655 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V32.tsv"
G655_COMPLETE = G655 / "artifacts/COMPLETE_PASSAGES_V32.tsv"
G655_ONE = G655 / "artifacts/ONE_UNKNOWN_PASSAGES_V32.tsv"
G655_GLOSSARY = G655 / "artifacts/V32_WORKING_TOKEN_GLOSSARY.tsv"
G655_DICTIONARY = G655 / "artifacts/WORKING_DICTIONARY_V32.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
STATUS = "PASS_21_OBSERVED_AL_POSITION_WHOLES__V33"
RESULT_CONTENT = "13a0693b8f6fb8d64500898d910f6acd93a7ad82fb86a015b0b71ddbf74ac731"

# surface: mode, meaning, composition, occurrences, pages, exact, normalized
TARGETS = {
    "chal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, trocken am Gradanfang", "CH_DRY_START+AL_CLASS_I", 42, 26, 35, 35),
    "cheal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, trocken in der Gradmitte", "CH_DRY_MIDDLE+AL_CLASS_I", 26, 13, 25, 25),
    "cheeal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, trocken am Gradende", "CH_DRY_END+AL_CLASS_I", 3, 3, 2, 2),
    "shal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, feucht am Gradanfang", "SH_MOIST_START+AL_CLASS_I", 15, 12, 11, 11),
    "sheal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, feucht in der Gradmitte", "SH_MOIST_MIDDLE+AL_CLASS_I", 14, 12, 13, 13),
    "sheeal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, feucht am Gradende", "SH_MOIST_END+AL_CLASS_I", 2, 2, 1, 1),
    "kal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, heiß am Gradanfang", "K_HOT_START+AL_CLASS_I", 25, 21, 14, 14),
    "tal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, kalt am Gradanfang", "T_COLD_START+AL_CLASS_I", 20, 13, 14, 14),
    "oal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz", "O_PREP+AL_CLASS_I", 2, 2, 2, 2),
    "oeeal": ("NEW_EXACT_WHOLE_LOCAL_ANALOGY", "Rohstoffklasse I im Ansatz, am Gradende", "OEEAL_EXACT_WHOLE_LOCAL_ANALOGY;O_AL_PARALLEL;EE_END_RIVAL", 2, 2, 2, 2),
    "okal": ("REVISE_AL_QUALITY_MODEL", "Rohstoffklasse I im Ansatz, heiß am Gradanfang", "O_PREP+K_HOT_START+AL_CLASS_I", 123, 64, 102, 102),
    "okeal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz, heiß in der Gradmitte", "O_PREP+K_HOT_MIDDLE+AL_CLASS_I", 10, 8, 8, 8),
    "otal": ("REVISE_AL_QUALITY_MODEL", "Rohstoffklasse I im Ansatz, kalt am Gradanfang", "O_PREP+T_COLD_START+AL_CLASS_I", 119, 57, 109, 109),
    "oteal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz, kalt in der Gradmitte", "O_PREP+T_COLD_MIDDLE+AL_CLASS_I", 5, 4, 5, 5),
    "oteeal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz, kalt am Gradende", "O_PREP+T_COLD_END+AL_CLASS_I", 1, 1, 1, 1),
    "qoal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I", "QO_SCOPE+AL_CLASS_I", 5, 5, 4, 4),
    "qokal": ("REVISE_AL_QUALITY_MODEL", "Rohstoffklasse I, heiß am Gradanfang", "QO_SCOPE+K_HOT_START+AL_CLASS_I", 180, 54, 158, 158),
    "qokeal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, heiß in der Gradmitte", "QO_SCOPE+K_HOT_MIDDLE+AL_CLASS_I", 4, 4, 4, 4),
    "qokeeal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, heiß am Gradende", "QO_SCOPE+K_HOT_END+AL_CLASS_I", 2, 2, 1, 1),
    "qotal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, kalt am Gradanfang", "QO_SCOPE+T_COLD_START+AL_CLASS_I", 57, 36, 54, 54),
    "qoteal": ("NEW_EXACT_WHOLE", "Rohstoffklasse I, kalt in der Gradmitte", "QO_SCOPE+T_COLD_MIDDLE+AL_CLASS_I", 2, 2, 2, 2),
}
TARGET_ORDER = list(TARGETS)
NEW = {surface for surface, spec in TARGETS.items() if spec[0].startswith("NEW")}
REVISED = set(TARGETS) - NEW
HOLDS = {
    "cheeeal": (1, 1, 1, 1, "OBSERVED_EEE_OUTSIDE_THREE_POSITION_AXIS"),
    "keeal": (1, 1, 0, 0, "OBSERVED_ZERO_EXACT_SUPERFORM_WARNING"),
    "eeal": (1, 1, 0, 0, "OBSERVED_UNHEADED_ZERO_EXACT_WARNING"),
}
GRID_ROOTS = ("ch", "sh", "k", "t", "ok", "ot", "qok", "qot")
POSITIONS = {0: "START", 1: "MIDDLE", 2: "END", 3: "EEE_OUTSIDE_AXIS"}
BOUNDARIES = {
    "G656-B01": ("CH_AL_SPLIT", "f116r.50", "ch al / chal", ("ch al", "chal", "chal")),
    "G656-B02": ("CHE_AL_SPLIT", "f58v.12", "cheal / che al", ("cheal", "cheal", "che al")),
    "G656-B03": ("O_AL_SPLIT", "f86v5.28", "o al / oal", ("o al", "oal", "o al")),
    "G656-B04": ("O_KAL_SPLIT", "f8r.20", "o kal / okal", ("o kal", "okal", "o kal")),
    "G656-B05": ("O_KAL_SPLIT", "f107v.37", "o kal / okal", ("o kal", "okal", "okal")),
    "G656-B06": ("O_KAL_SPLIT", "f116r.20", "o kal / okal", ("o kal", "okal", "okal")),
    "G656-B07": ("OT_AL_SPLIT", "f105v.15", "ot al / otal", ("ot al", "otal", "otal")),
    "G656-B08": ("KEEAL_SUPERFORM_WARNING", "f78r.34", "o keeal / okeeal", ("o keeal", "okeeal", "okeeal")),
}
PAIRS = (
    ("chal", "cheal", "trocken am Gradanfang / in der Gradmitte"),
    ("chal", "sheal", "trocken am Gradanfang / feucht in der Gradmitte"),
    ("okal", "otal", "heißer / kalter Rohstoffansatz am Gradanfang"),
    ("qokal", "qotal", "heißer / kalter Rohstoff am Gradanfang"),
    ("cheal", "cheeal", "trocken in der Gradmitte / am Gradende"),
)
LOCAL_EE = (
    ("oeeal", "AL", "TARGET_LOCAL_ANALOGY", 2, 2, 2, 2, "Rohstoffklasse I im Ansatz, am Gradende", "ACCEPT_EXACT_WHOLE_ONLY"),
    ("oeear", "AR", "EXACT_MATERIAL_SISTER", 3, 3, 3, 3, "Fraktionsschwester im Ansatz-/Gradmilieu", "SUPPORT_ANALOGY_ONLY"),
    ("eal", "AL", "MISSING_MIDDLE_RIVAL", 0, 0, 0, 0, "keine beobachtete nackte Mittelzelle", "ABSENT_HOLD"),
    ("oeal", "AL", "MISSING_MIDDLE_RIVAL", 0, 0, 0, 0, "keine beobachtete O-Mittelzelle", "ABSENT_HOLD"),
    ("eeal", "AL", "UNHEADED_READER_WARNING", 1, 1, 0, 0, "unbelegte unqualifizierte Endlesung", "OBSERVED_ZERO_EXACT_HOLD"),
)
HISTORICAL = (
    ("G656-H01", "1415", "Tadhg Ó Cuinn, An Irish Materia Medica", "drug lemma plus hot/cold/dry/wet quality", "https://celt.ucc.ie/published/G600005/index.html", "supports a mixed learned-head plus compact quality notation"),
    ("G656-H02", "1415", "Uiola entry", "beginning of one degree and end of another are both stated", "https://celt.ucc.ie/published/G600006/text890.html", "supports distinct START and END positions within numbered qualities"),
    ("G656-H03", "1415", "Nux longa entry", "middle of one degree contrasts with end of another", "https://celt.ucc.ie/published/G600005/text825.html", "supports distinct MIDDLE and END positions within numbered qualities"),
)
BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 16398, "unknown_token_positions": 15941,
    "complete_multi_token_lines": 130, "strict_complete_lines": 77, "one_unknown_lines": 225,
    "strict_one_unknown_lines": 54, "working_glossary_surfaces": 453,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 16635, "unknown_token_positions": 15704,
    "complete_multi_token_lines": 133, "strict_complete_lines": 78, "one_unknown_lines": 239,
    "strict_one_unknown_lines": 57, "working_glossary_surfaces": 471,
}
ROUNDS = (
    ("BASE_V32", 529, 16398, 15941, 130, 77, 225, 54, 453),
    ("chal", 530, 16440, 15899, 131, 78, 226, 53, 454),
    ("cheal", 531, 16466, 15873, 131, 78, 228, 54, 455),
    ("cheeal", 532, 16469, 15870, 131, 78, 228, 54, 456),
    ("shal", 533, 16484, 15855, 131, 78, 228, 54, 457),
    ("sheal", 534, 16498, 15841, 131, 78, 230, 56, 458),
    ("sheeal", 535, 16500, 15839, 132, 78, 229, 56, 459),
    ("kal", 536, 16525, 15814, 132, 78, 232, 56, 460),
    ("tal", 537, 16545, 15794, 132, 78, 234, 56, 461),
    ("oal", 538, 16547, 15792, 132, 78, 234, 56, 462),
    ("oeeal", 539, 16549, 15790, 132, 78, 234, 56, 463),
    ("okal", 540, 16549, 15790, 132, 78, 234, 56, 463),
    ("okeal", 541, 16559, 15780, 132, 78, 234, 56, 464),
    ("otal", 542, 16559, 15780, 132, 78, 234, 56, 464),
    ("oteal", 543, 16564, 15775, 132, 78, 234, 56, 465),
    ("oteeal", 544, 16565, 15774, 132, 78, 234, 56, 466),
    ("qoal", 545, 16570, 15769, 132, 78, 234, 56, 467),
    ("qokal", 546, 16570, 15769, 132, 78, 234, 56, 467),
    ("qokeal", 547, 16574, 15765, 132, 78, 234, 56, 468),
    ("qokeeal", 548, 16576, 15763, 132, 78, 234, 56, 469),
    ("qotal", 549, 16633, 15706, 133, 78, 238, 57, 470),
    ("qoteal", 550, 16635, 15704, 133, 78, 239, 57, 471),
)
NEW_COMPLETE = {"f83v.16", "f83r.43", "f108v.40"}
STRICT_NEW_COMPLETE = {"f83v.16"}
ONE_HOLE_INTROS = (2, 2, 0, 0, 2, 0, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 1)
CURATED = {
    "f83v.16": ("Grad-/Maßwert III; Rohstoffklasse I, heiß am Gradanfang; feuchtes Arzneikompositum in der Gradmitte; heiß am Gradende; Rohstoffklasse I, trocken am Gradanfang; nochmals heiß am Gradende; heiß, Grad III; trocken in der Gradmitte, abgeschlossen; Samenfraktion I; Rohstoffklasse I.", "dreileser-strikt"),
    "f83r.43": ("Grad-/Maßwert III; feuchtes Material; trocken in der Gradmitte, abgeschlossen; Rohstoffklasse I, kalt am Gradanfang; Samenfraktion I.", "ZL3b-Arbeitslesung; IT2a hat qotyl/rar, RF1b qokal/sar"),
    "f108v.40": ("Grad-/Maßwert III; Rohstoffklasse I, feucht am Gradende; dreimal heiß am Gradende, jeweils abgeschlossen; kalt in der Gradmitte; zweimal heiß am Gradende; kalter Ansatz in der Gradmitte, abgeschlossen; kalt, Grad III.", "ZL3b-Arbeitslesung; RF1b spaltet erstes qokeedy als qokee y und liest oted statt otedy"),
}
BUILDER_OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "AL_QUALITY_LATTICE_ATLAS.tsv",
    "BOUNDARY_EVIDENCE_ATLAS.tsv", "PAIR_CONTRAST_COUNTS.tsv", "HISTORICAL_SUBDEGREE_COMPARATORS.tsv",
    "LOCAL_EE_SISTER_EVIDENCE.tsv", "REVISION_LEDGER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "CURATED_COMPLETE_PASSAGE_READINGS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V33_WORKING_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V33.tsv",
    "COMPLETE_PASSAGES_V33.tsv", "ONE_UNKNOWN_PASSAGES_V33.tsv", "WORKING_DICTIONARY_V33.tsv",
)
REPLAY_OUTPUTS = (*BUILDER_OUTPUTS, "RESULT.json")
INPUTS = {
    str(G655 / "src/run.py"), str(G655_ALLOW), str(G655_COVERAGE), str(G655_COMPLETE), str(G655_ONE),
    str(G655_GLOSSARY), str(G655_DICTIONARY), str(G655 / "artifacts/RESULT.json"), str(G655 / "REPORT.md"),
    "experiments/yolo/gdt647_quality_subdegree_family_migration/REPORT.md",
    "experiments/yolo/gdt652_strict_v28_frontier_completion/REPORT.md", str(TOKENS), str(CROSS),
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
            readers = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
            direct = [tokens.count(surface) for tokens in readers]
            spans = [span_count(tokens, surface) for tokens in readers]
            line = by_locus[locus]
            ordinal = next(i for i, token in enumerate(line, 1) if token is row)
            records.append({
                **row, "token_ordinal": ordinal,
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": cross[locus]["zl3b_clean"], "it2a_line": cross[locus]["it2a_clean"],
                "rf1b_line": cross[locus]["rf1b_clean"],
                "reader_exact": int(needed <= min(direct)), "split_normalized": int(needed <= min(spans)),
            })
    return records


def census(records: list[dict[str, object]], surface: str) -> tuple[int, int, int, int]:
    members = [row for row in records if row["eva"] == surface]
    return (len(members), len({str(row["page"]) for row in members}),
            sum(int(row["reader_exact"]) for row in members),
            sum(int(row["split_normalized"]) for row in members))


def metrics(coverage, complete, one_unknown, glossary_size: int) -> dict[str, int]:
    return {
        "physical_lines": len(coverage), "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": glossary_size,
    }


def lattice_specs() -> list[tuple[str, str, str, str]]:
    rows = [("BASE", "al", "AL", "BASE")]
    rows.extend((root.upper(), f"{root}{'e' * level}al", f"{root.upper()}+{'E' * level if level else 'ZERO_E'}+AL", POSITIONS[level]) for root in GRID_ROOTS for level in range(4))
    rows.extend((
        ("O_UNQUALIFIED", "oal", "O+AL", "UNQUALIFIED_BASE"),
        ("O_UNQUALIFIED", "oeal", "OEAL_UNOBSERVED_WHOLE", "ABSENT_INTERMEDIATE_RIVAL"),
        ("O_UNQUALIFIED", "oeeal", "OEEAL_EXACT_WHOLE;O_AL_PARALLEL", "LOCAL_END_FORM_ANALOGY"),
        ("O_UNQUALIFIED", "oeeeal", "OEEEAL_UNOBSERVED_WHOLE", "EEE_OUTSIDE_AXIS"),
        ("QO_UNQUALIFIED", "qoal", "QO+AL", "UNQUALIFIED_BASE"),
        ("QO_UNQUALIFIED", "qoeal", "QOEAL_UNOBSERVED_WHOLE", "UNLICENSED_POSITION_RIVAL"),
        ("QO_UNQUALIFIED", "qoeeal", "QOEEAL_UNOBSERVED_WHOLE", "UNLICENSED_POSITION_RIVAL"),
        ("QO_UNQUALIFIED", "qoeeeal", "QOEEEAL_UNOBSERVED_WHOLE", "EEE_OUTSIDE_AXIS"),
        ("NO_VISIBLE_HEAD", "eal", "EAL_UNOBSERVED_WHOLE", "UNHEADED_RIVAL"),
        ("NO_VISIBLE_HEAD", "eeal", "EEAL_READER_UNSTABLE_WHOLE", "UNHEADED_RIVAL"),
        ("NO_VISIBLE_HEAD", "eeeal", "EEEAL_UNOBSERVED_WHOLE", "EEE_OUTSIDE_AXIS"),
    ))
    return rows


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt656_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT656 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("schema") == "GDT656_AL_QUALITY_POSITION_SHELL_RESULT_V1", "result schema")
    check(result.get("experiment_id") == "GDT656" and result.get("status") == STATUS, "result identity/status")
    check(result.get("content_sha256") == RESULT_CONTENT == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash")

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allow_rows}
    check(len(allow_rows) == len(pages) == 179, "179 unique guarded pages")
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "f1r excluded and f84/f84r forbidden")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G655_ALLOW).read_bytes(), "V32 allowlist inherited byte-identically")
    token_rows, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    expected_token_stats = {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}
    expected_cross_stats = {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}
    check(len(token_rows) == 32339 and token_stats == expected_token_stats, "guarded token census", repr(token_stats))
    check(len(cross_rows) == 4137 and cross_stats == expected_cross_stats, "guarded cross census", repr(cross_stats))
    guard = result.get("guard", {})
    check(guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats, "result guarded counts")
    check(guard.get("allowed_pages") == 179 and guard.get("f1r") == "EXCLUDED" and guard.get("f84") == guard.get("f84r") == "FORBIDDEN" and guard.get("new_pages") == guard.get("new_images") == 0, "result guard ceiling")

    lattice_plan = lattice_specs()
    source_surfaces = {row[1] for row in lattice_plan} | set(TARGETS) | {row[0] for row in LOCAL_EE}
    records = independent_records(token_rows, cross_rows, source_surfaces)
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by) == 21 and list(deck_by) == TARGET_ORDER, "21 ordered target cards")
    check([row["candidate_id"] for row in deck] == [f"G656-C{i:02d}" for i in range(1, 22)], "ordered candidate ids")
    for index, (surface, spec) in enumerate(TARGETS.items(), 1):
        row = deck_by[surface]
        expected_counts = spec[3:]
        artifact_counts = tuple(int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(census(records, surface) == expected_counts, f"independent target census:{surface}", repr(census(records, surface)))
        check(artifact_counts == expected_counts, f"deck target census:{surface}")
        check((row["mode"], row["v33_meaning_de"], row["composition"]) == spec[:3], f"target semantics:{surface}")
        check(row["candidate_order"] == str(index) and row["decision"] == "ACCEPT_V33_EXACT_WHOLE", f"target admission:{surface}")
        check(bool(row["rival_de"] and row["decision_basis"] and row["strongest_counterargument"]), f"target support/rival:{surface}")
    check(sum(spec[3] for spec in TARGETS.values()) == 659 and sum(spec[5] for spec in TARGETS.values()) == sum(spec[6] for spec in TARGETS.values()) == 567, "659 audits and 567 exact/normalized targets")
    check(len(NEW) == 18 and len(REVISED) == 3 and NEW == set(result["target_run"]["new_surfaces"]) and REVISED == set(result["target_run"]["revised_surfaces"]), "18 new and three revised targets")
    check(deck_by["oeeal"]["mode"] == "NEW_EXACT_WHOLE_LOCAL_ANALOGY" and deck_by["oeeal"]["composition"] == "OEEAL_EXACT_WHOLE_LOCAL_ANALOGY;O_AL_PARALLEL;EE_END_RIVAL", "OEEAL exact-whole local-analogy card")

    lattice = read_tsv(ART / "AL_QUALITY_LATTICE_ATLAS.tsv")
    check(len(lattice) == len(lattice_plan) == 44, "44-cell ordered AL-quality lattice")
    observed_cells = occurrences = exact_total = 0
    for row, identity in zip(lattice, lattice_plan):
        family, surface, decomposition, position = identity
        independent = census(records, surface)
        artifact = tuple(int(row[field]) for field in ("zl3b_occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check((row["family"], row["surface"], row["decomposition"], row["quality_position"]) == identity, f"lattice identity:{surface}")
        check(artifact == independent, f"independent lattice census:{surface}", repr(artifact))
        observed_cells += int(independent[0] > 0)
        occurrences += independent[0]
        exact_total += independent[2]
        if surface in TARGETS:
            check(row["final_status"] == "ACCEPTED_V33" and row["v33_meaning_de"] == TARGETS[surface][1], f"lattice accepted meaning:{surface}")
        elif surface == "al":
            check(row["final_status"] == "V32_BASE" and row["v33_meaning_de"] == "Rohstoffklasse I", "lattice AL base")
        elif surface in HOLDS:
            check(independent == HOLDS[surface][:4] and row["final_status"] == HOLDS[surface][4] and row["v33_meaning_de"] == "NOT_ASSIGNED", f"lattice observed hold:{surface}")
        else:
            check(independent[0] == 0 and row["final_status"] == "ABSENT_HOLD" and row["v33_meaning_de"] == "NOT_ASSIGNED", f"lattice absent hold:{surface}")
    check((observed_cells, occurrences, exact_total) == (25, 866, 735), "25 observed grid cells / 866 occurrences / 735 exact")
    check(result.get("full_al_quality_grid") == {"cells": 44, "observed_cells": 25, "occurrences": 866, "all_reader_exact_occurrences": 735, "accepted_v33_cells": 21, "retained_v32_base_cells": ["al"], "observed_holds": ["cheeeal", "eeal", "keeal"]}, "result full-grid packet")

    cross_by = {row["locus"]: row for row in cross_rows}
    boundary_rows = read_tsv(ART / "BOUNDARY_EVIDENCE_ATLAS.tsv")
    boundary_by = {row["bridge_id"]: row for row in boundary_rows}
    check(len(boundary_rows) == len(boundary_by) == 8 and list(boundary_by) == list(BOUNDARIES), "eight ordered boundary witnesses")
    for bridge_id, (kind, locus, diagnostic, patterns) in BOUNDARIES.items():
        row, source = boundary_by[bridge_id], cross_by[locus]
        check((row["evidence_type"], row["locus"], row["diagnostic_surface"]) == (kind, locus, diagnostic), f"boundary identity:{bridge_id}")
        check(row["page"] == source["page"] and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[field] for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")), f"boundary source fidelity:{bridge_id}")
        check(all(pattern in source[field] for pattern, field in zip(patterns, ("zl3b_clean", "it2a_clean", "rf1b_clean"))) and bool(row["supports"]), f"boundary split/fusion visible:{bridge_id}")

    lines: dict[str, set[str]] = defaultdict(set)
    for row in token_rows:
        lines[row["locus"]].add(row["eva"])
    pair_rows = read_tsv(ART / "PAIR_CONTRAST_COUNTS.tsv")
    check(len(pair_rows) == 5, "five pair-contrast rows")
    for row, (first, second, distinction) in zip(pair_rows, PAIRS):
        loci = sorted(locus for locus, surfaces in lines.items() if first in surfaces and second in surfaces)
        exact_lines = sum(int(cross_by[locus]["all_three_present"]) == 1 and int(cross_by[locus]["all_present_exact"]) == 1 for locus in loci)
        check((row["first_surface"], row["second_surface"], row["required_distinction_de"], int(row["cooccurrence_lines"]), int(row["all_reader_exact_lines"]), row["example_loci"]) == (first, second, distinction, len(loci), exact_lines, "|".join(loci[:12]) or "NONE"), f"independent pair contrast:{first}/{second}")

    historical = read_tsv(ART / "HISTORICAL_SUBDEGREE_COMPARATORS.tsv")
    check(len(historical) == 3 and [tuple(row[field] for field in ("comparator_id", "date", "source", "observed_architecture", "source_url", "supports")) for row in historical] == list(HISTORICAL), "three fixed 1415 architecture comparators")
    sisters = read_tsv(ART / "LOCAL_EE_SISTER_EVIDENCE.tsv")
    check(len(sisters) == 5 and [row["evidence_id"] for row in sisters] == [f"G656-S{i:02d}" for i in range(1, 6)], "five ordered local-EE evidence rows")
    for row, spec in zip(sisters, LOCAL_EE):
        surface, carrier, role, occ, page_count, exact, normalized, interpretation, decision = spec
        expected_loci = "|".join(sorted({str(record["locus"]) for record in records if record["eva"] == surface})) or "NONE"
        check((row["surface"], row["carrier"], row["role"], row["working_interpretation_de"], row["decision"]) == (surface, carrier, role, interpretation, decision), f"local-EE identity:{surface}")
        check(census(records, surface) == (occ, page_count, exact, normalized) == tuple(int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences")) and row["loci"] == expected_loci, f"local-EE independent census:{surface}")
    check(census(records, "oeear") == (3, 3, 3, 3) and census(records, "eal") == census(records, "oeal") == (0, 0, 0, 0) and census(records, "eeal") == (1, 1, 0, 0), "OEEAR support and EAL/OEAL/EEAL counterevidence")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 659, "659 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: spec[3] for surface, spec in TARGETS.items()}), "audit surface census")
    check(sum(int(row["reader_exact"]) for row in audits) == sum(int(row["split_normalized"]) for row in audits) == 567, "audit 567 exact and normalized")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no target hard collisions")
    independent_by = {surface: [row for row in records if row["eva"] == surface] for surface in TARGETS}
    audit_by = {surface: [row for row in audits if row["surface"] == surface] for surface in TARGETS}
    for round_number, surface in enumerate(TARGET_ORDER, 1):
        expected_rows, artifact_rows = independent_by[surface], audit_by[surface]
        fidelity = len(expected_rows) == len(artifact_rows)
        for occurrence, (expected, row) in enumerate(zip(expected_rows, artifact_rows), 1):
            support = "ALL_THREE_EXACT" if expected["reader_exact"] else "ALL_THREE_SPLIT_NORMALIZED" if expected["split_normalized"] else "READER_VARIANT"
            fidelity &= (
                row["audit_id"] == f"G656-A{round_number:02d}-{occurrence:04d}" and row["round"] == str(round_number)
                and row["mode"] == TARGETS[surface][0]
                and tuple(row[field] for field in ("page", "locus", "section", "language", "hand")) == tuple(str(expected[field]) for field in ("page", "locus", "section", "language", "hand"))
                and (row["token_ordinal"], row["previous"], row["following"]) == (str(expected["token_ordinal"]), str(expected["previous"]), str(expected["following"]))
                and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(str(expected[field]) for field in ("zl3b_line", "it2a_line", "rf1b_line"))
                and (row["reader_exact"], row["split_normalized"], row["reader_support"]) == (str(expected["reader_exact"]), str(expected["split_normalized"]), support)
            )
        check(fidelity, f"independent audit source/reader replay:{surface}")
    verdicts = Counter(row["verdict"] for row in audits)
    check(verdicts == Counter({"CONCRETE_CONTEXT_COMPATIBLE": 531, "SHORT_OR_OPAQUE_CONTEXT": 36, "READER_VARIANT_WARNING": 92}), "audit verdict totals")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 92 and Counter(row["reader_support"] for row in variants) == Counter({"READER_VARIANT": 92}), "92 hard reader warnings and no normalized-only targets")
    expected_variants = Counter((row["surface"], row["page"], row["locus"], row["reader_support"], TARGETS[row["surface"]][1]) for row in audits if row["reader_exact"] == "0")
    artifact_variants = Counter((row["surface"], row["page"], row["locus"], row["reader_support"], row["working_meaning_de"]) for row in variants)
    check(artifact_variants == expected_variants and all(row["decision"] == "RETAIN_EXACT_ZL3B_WITH_READER_WARNING" for row in variants), "variant audit exactly covers non-exact targets")

    revisions = read_tsv(ART / "REVISION_LEDGER.tsv")
    revision_by = {row["surface"]: row for row in revisions}
    check(len(revisions) == 3 and list(revision_by) == ["okal", "otal", "qokal"], "three ordered AL-quality revisions")
    old_meanings = {"okal": "Ansatz aus heißem Rohstoff, Form I", "otal": "Ansatz aus kaltem Rohstoff, Form I", "qokal": "heiße Substanz"}
    check(all(revision_by[surface]["v32_meaning_de"] == old_meanings[surface] and revision_by[surface]["v33_meaning_de"] == TARGETS[surface][1] and revision_by[surface]["occurrences"] == str(TARGETS[surface][3]) and revision_by[surface]["reader_exact_occurrences"] == str(TARGETS[surface][5]) for surface in REVISED), "revision meanings and censuses")

    base_gloss_rows = read_tsv(ROOT / G655_GLOSSARY)
    gloss_rows = read_tsv(ART / "V33_WORKING_TOKEN_GLOSSARY.tsv")
    base_gloss = {row["surface"]: row for row in base_gloss_rows}
    glossary = {row["surface"]: row for row in gloss_rows}
    check(len(base_gloss_rows) == len(base_gloss) == 453 and len(gloss_rows) == len(glossary) == 471, "glossary 453 to 471")
    check(set(glossary) == set(base_gloss) | NEW, "exact 18-surface glossary extension")
    check(all(glossary[surface] == row for surface, row in base_gloss.items() if surface not in REVISED), "non-revised V32 glossary retained")
    for surface, spec in TARGETS.items():
        row = glossary[surface]
        check(tuple(row[field] for field in ("working_meaning_de", "source", "strength", "scope_state", "priority")) == (spec[1], f"GDT656:{spec[0]}", "EXACT_WHOLE_AL_QUALITY_POSITION_SHELL", "KNOWN_EXACT_WHOLE", "154"), f"V33 glossary card:{surface}")
    check(not ({"cheeeal", "eeal", "keeal", "eal", "oeal"} & set(glossary)), "observed/absent holds not exported to glossary")

    base_dictionary = read_tsv(ROOT / G655_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V33.tsv")
    additions = dictionary[len(base_dictionary):]
    check(len(base_dictionary) == 529 and len(dictionary) == 550, "dictionary 529 to 550")
    check(dictionary[:529] == base_dictionary, "V32 dictionary prefix unchanged")
    check([row["entry"].split("@", 1)[0] for row in additions] == TARGET_ORDER, "21 ordered dictionary additions")
    for index, (surface, row) in enumerate(zip(TARGET_ORDER, additions), 1):
        spec = TARGETS[surface]
        expected = (f"{surface}@GDT656_EXACT_WHOLE", f"EXACT_ZL3B_WHOLE_{spec[0]}", spec[1], spec[2], f"NEW_V33_ACCEPTED_ROUND_{index:02d}")
        check(tuple(row[field] for field in ("entry", "kind", "working_meaning_de", "composition", "status")) == expected and row["context_rule"].startswith("exact complete surface only;"), f"dictionary exact-whole addition:{surface}")
    check({row["entry"].split("@", 1)[0] for row in additions} == set(TARGETS) and not any(row["entry"].split("@", 1)[0] in {"e", "ee", "eee", "eal", "oeal", "eeal", "keeal", "cheeeal"} for row in additions), "exact-whole suffix nonleak")
    defaults = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    check(len(defaults) == 21 and [row["surface"] for row in defaults] == TARGET_ORDER, "21 ordered accepted defaults")
    check(all(row["entry"] == additions[index]["entry"] and row["working_meaning_de"] == TARGETS[row["surface"]][1] and row["composition"] == TARGETS[row["surface"]][2] and row["occurrences"] == str(TARGETS[row["surface"]][3]) and row["acceptance_mode"] == TARGETS[row["surface"]][0] for index, row in enumerate(defaults)), "accepted defaults mirror exact-whole cards")

    base_cov = read_tsv(ROOT / G655_COVERAGE)
    base_complete = read_tsv(ROOT / G655_COMPLETE)
    base_one = read_tsv(ROOT / G655_ONE)
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V33.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V33.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V33.tsv")
    check(metrics(base_cov, base_complete, base_one, len(base_gloss)) == BASE_METRICS, "V32 metrics")
    check(metrics(coverage, complete, one, len(glossary)) == FINAL_METRICS, "V33 metrics")
    check(sum(int(row["token_count"]) for row in coverage) == 32339, "V33 token census")
    check(FINAL_METRICS["known_token_positions"] - BASE_METRICS["known_token_positions"] == 237 == sum(TARGETS[surface][3] for surface in NEW), "237 newly known positions")
    base_cov_by = {row["locus"]: row for row in base_cov}
    cov_by = {row["locus"]: row for row in coverage}
    new_positions = Counter(row["locus"] for row in token_rows if row["eva"] in NEW)
    check(all(int(cov_by[locus]["known_tokens"]) - int(base_cov_by[locus]["known_tokens"]) == new_positions[locus] for locus in cov_by), "linewise 18-new-surface deltas")
    target_loci = {row["locus"] for row in token_rows if row["eva"] in TARGETS}
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    affected_by = {row["locus"]: row for row in affected}
    check(len(affected) == len(affected_by) == len(target_loci) == 546 and set(affected_by) == target_loci, "546 exact affected lines")
    check(all(row["page"] == cov_by[locus]["page"] and row["zl3b_line"] == cov_by[locus]["zl3b_line"] and row["v32_tokenwise_de"] == base_cov_by[locus]["token_glosses_de"] and row["v33_tokenwise_de"] == cov_by[locus]["token_glosses_de"] and row["complete_v33"] == str(int(cov_by[locus]["unknown_tokens"]) == 0) for locus, row in affected_by.items()), "affected-line edition fidelity")

    base_complete_by = {row["locus"]: row for row in base_complete}
    complete_by = {row["locus"]: row for row in complete}
    check(set(complete_by) - set(base_complete_by) == NEW_COMPLETE, "exact three new complete loci")
    new_rows = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_by = {row["locus"]: row for row in new_rows}
    check(len(new_rows) == len(new_by) == 3 and set(new_by) == NEW_COMPLETE, "three new-complete artifact rows")
    check({row["locus"] for row in new_rows if row["strict_complete"] == "1"} == STRICT_NEW_COMPLETE, "one newly strict complete line")
    curated = read_tsv(ART / "CURATED_COMPLETE_PASSAGE_READINGS.tsv")
    curated_by = {row["locus"]: row for row in curated}
    check(len(curated) == len(curated_by) == 3 and set(curated_by) == NEW_COMPLETE, "three curated complete readings")
    check(all(curated_by[locus]["curated_workshop_reading_de"] == reading and curated_by[locus]["reader_note"] == note and new_by[locus]["curated_workshop_reading_de"] == reading and "[" not in reading and "?" not in reading for locus, (reading, note) in CURATED.items()), "hard curated readings and reader notes")

    exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    exposed_by = {row["locus"]: row for row in exposed}
    check(len(exposed) == len(exposed_by) == 17, "17 unique sequentially exposed one-hole rows")
    check(tuple(sum(row["introduced_round"] == str(i) for row in exposed) for i in range(1, 22)) == ONE_HOLE_INTROS, "one-hole introduction counts by round")
    check(all(1 <= int(row["introduced_round"]) <= 21 and row["enabled_by_surface"] == TARGET_ORDER[int(row["introduced_round"]) - 1] and row["enabled_by_surface"] in lines[row["locus"]] and row["unknown_tokens"] == "1" and row["unknown_ordinal"] in row["unknown_ordinals"].split("|") and row["unknown_surface"] in row["unknown_surfaces"].split("|") for row in exposed), "one-hole round/surface/unknown provenance")
    base_one_loci, final_one_loci = {row["locus"] for row in base_one}, {row["locus"] for row in one}
    check(set(exposed_by) == final_one_loci - base_one_loci and len(base_one_loci - final_one_loci) == 3, "sequential one-hole frontier reconciles with V32/V33")

    round_rows = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(round_rows) == 22 and [row["round"] for row in round_rows] == [str(i) for i in range(22)], "22 ordered coverage rounds")
    for index, expected in enumerate(ROUNDS):
        row = round_rows[index]
        observed = (row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]), int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]), int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]), int(row["working_glossary_surfaces"]))
        check(observed == expected, f"round metrics:{index}", repr(observed))
        check(row["dictionary_sha256"] == canonical_hash(dictionary[:int(row["dictionary_entries"])]), f"round dictionary hash:{index}")

    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    check(len(reality) == 29 and set(row["surface"] for row in reality) == set(TARGETS), "29 reality checks cover all 21 targets")
    check(all(row["locus"] in cross_by and row["zl3b_line"] == cross_by[row["locus"]]["zl3b_clean"] and row["tokenwise_v33_de"] == cov_by[row["locus"]]["token_glosses_de"] and row["working_reading_de"] and not FILLER.search(row["working_reading_de"]) for row in reality), "reality-check source and reading fidelity")
    oeeal_reality = {row["locus"]: row for row in reality if row["surface"] == "oeeal"}
    check(set(oeeal_reality) == {"f104r.14", "f112v.43"} and all(row["reader_support"] == "ALL_THREE_EXACT" and row["syntax_note"] == "MANUAL_PARTIAL_SEQUENCE_READING" for row in oeeal_reality.values()), "OEEAL two exact manual reality loci")

    target_run = result.get("target_run", {})
    check((target_run.get("candidates"), target_run.get("accepted_whole_cards"), target_run.get("reader_anchored_exact_wholes"), target_run.get("audited_occurrences"), target_run.get("all_reader_exact_occurrences"), target_run.get("split_normalized_occurrences"), target_run.get("reader_variant_warnings"), target_run.get("hard_collisions")) == (21, 21, 21, 659, 567, 567, 92, 0), "result target metrics")
    check(target_run.get("accepted_surfaces") == TARGET_ORDER and target_run.get("verdicts") == dict(sorted({"CONCRETE_CONTEXT_COMPATIBLE": 531, "READER_VARIANT_WARNING": 92, "SHORT_OR_OPAQUE_CONTEXT": 36}.items())), "result accepted/verdict packet")
    check(result.get("coverage") == {"base": BASE_METRICS, "final": FINAL_METRICS, "newly_completed_lines": 3, "newly_exposed_one_hole_lines": 17, "affected_lines": 546}, "result coverage packet")
    working = result.get("working_dictionary", {})
    check((working.get("v32_entries"), working.get("v33_entries"), working.get("accepted_tail_entries"), working.get("v32_glossary_surfaces"), working.get("v33_glossary_surfaces")) == (529, 550, 21, 453, 471), "result dictionary metrics")
    check(working.get("v32_prefix_sha256") == canonical_hash(base_dictionary) and working.get("v33_sha256") == canonical_hash(dictionary), "result dictionary hashes")
    semantic = result.get("semantic_model", {})
    check(semantic.get("observed_holds") == ["cheeeal", "eeal", "keeal"] and "OEEAL" in semantic.get("local_exact_whole_analogy", "") and "three exact OEEAR" in semantic.get("local_exact_whole_analogy", "") and "no free or global EE" in semantic.get("local_exact_whole_analogy", "") and "beginning/middle/end" in semantic.get("historical_comparator", ""), "result OEEAL/hold/comparator core")
    claim = str(result.get("claim_boundary", "")).lower()
    check(all(term in claim for term in ("exploratory", "eighteen new", "three revised", "exact-whole local analogy", "not a free ee", "cheeeal", "keeal", "eeal", "free components", "plaintext", "exact ingredient", "f1r", "new pages", "new images")), "result claim ceiling core")

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
    check(manifest.get("experiment_id") == "GDT656" and manifest.get("slug") == "al_quality_position_shell", "manifest identity")
    check(manifest.get("status") == STATUS, "manifest status")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("commands") == {"run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"}, "manifest commands")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check({"GDT647", "GDT652", "GDT655"} <= set(manifest.get("dependencies", [])), "manifest dependency core")
    question, ceiling = str(manifest.get("question", "")).lower(), str(manifest.get("claim_ceiling", "")).lower()
    check(len(question) >= 80 and all(term in question for term in ("twenty-one", "al", "start", "middle", "end", "oeeal", "concrete")), "manifest question core")
    check(len(ceiling) >= 120 and all(term in ceiling for term in ("explor", "exact whole", "oeeal", "free", "plaintext", "exact ingredient")), "manifest claim ceiling core")
    manifest_inputs = {row.get("path"): row for row in manifest.get("inputs", [])}
    check(set(manifest_inputs) == set(inputs), "manifest/result inputs")
    for path, row in manifest_inputs.items():
        check(row.get("sha256") == inputs[path] == sha256(ROOT / path) and bool(row.get("role")), f"manifest input seal:{path}")
    manifest_outputs = {row.get("path"): row for row in manifest.get("outputs", [])}
    required = {str(BASE / path) for path in (
        "METHOD.md", "README.md", "REPORT.md", "artifacts/README.md", "artifacts/TARGET_DECISION_DECK.tsv",
        "artifacts/AL_QUALITY_LATTICE_ATLAS.tsv", "artifacts/BOUNDARY_EVIDENCE_ATLAS.tsv",
        "artifacts/HISTORICAL_SUBDEGREE_COMPARATORS.tsv", "artifacts/LOCAL_EE_SISTER_EVIDENCE.tsv",
        "artifacts/READER_VARIANT_AUDIT.tsv", "artifacts/REVISION_LEDGER.tsv",
        "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "artifacts/CURATED_COMPLETE_PASSAGE_READINGS.tsv",
        "artifacts/NEWLY_COMPLETED_LINES.tsv", "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
        "artifacts/RESULT.json", "artifacts/V33_WORKING_TOKEN_GLOSSARY.tsv",
        "artifacts/ALL_LINE_CONCRETE_COVERAGE_V33.tsv", "artifacts/COMPLETE_PASSAGES_V33.tsv",
        "artifacts/ONE_UNKNOWN_PASSAGES_V33.tsv", "artifacts/WORKING_DICTIONARY_V33.tsv",
        "artifacts/VALIDATION.json", "src/run.py", "src/validate.py",
    )}
    check(required <= set(manifest_outputs), "manifest core outputs")
    for path, row in manifest_outputs.items():
        target_path = ROOT / str(path)
        check(not Path(str(path)).is_absolute() and target_path.is_file() and bool(row.get("role")), f"manifest output path:{path}")
        if str(path) != str(BASE / "artifacts/VALIDATION.json") and target_path.is_file():
            check(row.get("sha256") == sha256(target_path), f"manifest output seal:{path}")

    report_text = REPORT.read_text(encoding="utf-8").lower()
    for needle in ("rohstoffklasse", "gradanfang", "gradmitte", "gradende", "oeeal", "oeear", "cheeeal", "keeal", "eeal", "659", "567", "866", "735", "16.398", "16.635", "f83v.16", "f83r.43", "f108v.40", "explorativ"):
        check(needle in report_text, f"report contains:{needle}")

    # The implementation is imported only after all independent census,
    # semantics, reader, edition, hash, report and manifest checks above.
    try:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="gdt656_validate_") as temporary:
            replay = Path(temporary)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(REPLAY_OUTPUTS), "replay output set")
            for name in REPLAY_OUTPUTS:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT656_VALIDATION_V1", "experiment_id": "GDT656",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT656 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT656 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
