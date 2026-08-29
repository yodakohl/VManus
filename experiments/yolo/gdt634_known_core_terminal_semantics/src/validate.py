#!/usr/bin/env python3
"""Independently validate and byte-replay the GDT634 working edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt634_known_core_terminal_semantics")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V10 = ROOT / "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/WORKING_DICTIONARY_V10.tsv"
INHERITED_ALLOW = ROOT / "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/PAGE_ALLOWLIST.tsv"

# VALIDATION.json is intentionally absent: the builder neither creates nor
# binds its validator output, so replay cannot become self-referential.
GENERATED = (
    ART / "PAGE_ALLOWLIST.tsv",
    ART / "TARGET_LINES.tsv",
    ART / "TARGET_WORD_CENSUS.tsv",
    ART / "COMPLETE_TOKEN_WORKING_EDITION.tsv",
    ART / "COMPLETE_MICROLINE_TRANSLATIONS.tsv",
    ART / "QUALITY_E_LENGTH_GLOBAL_SUMMARY.tsv",
    ART / "QUALITY_TERMINAL_TARGETS.tsv",
    ART / "O_PREPARATION_TRANSFER_PARADIGMS.tsv",
    ART / "AL_AR_OL_OR_CARRIER_LATTICE.tsv",
    ART / "LEXICAL_HEAD_COMPOSITION_GRID.tsv",
    ART / "AGGRESSIVE_DEFAULT_COMPOSITION_CHECKS.tsv",
    ART / "INITIAL_HEAD_POSITION_AND_BACKOFF.tsv",
    ART / "CARRIER_VOWEL_BODY_BRIDGES.tsv",
    ART / "HISTORICAL_STEM_ANALOGIES.tsv",
    ART / "TERMINAL_M_PROFILE.tsv",
    ART / "CROSS_READER_READING_EVIDENCE.tsv",
    ART / "WORKING_DICTIONARY_V11.tsv",
    RESULT,
)

EXPECTED_LINES = (
    ("G634-L01", "f29r", "f29r.1", "posaiin she aiin chep oty chy qotchy qoty cheecthy"),
    ("G634-L02", "f82v", "f82v.36", "saiin shey qokeedy qokar sheecthey qokaiin daltedy rcheald"),
    ("G634-L03", "f80r", "f80r.18", "paiin sheol qokain chety qokeedy qokar shcthy qotol shecthy qokain olkam"),
    ("G634-L04", "f80v", "f80v.10", "sol sheey qokaiin shcthy dolshedy qokal shecthy qotainol"),
    ("G634-L05", "f20v", "f20v.10", "shokaiin chocthy chol daiin chy chor ety"),
    ("G634-L06", "f22v", "f22v.15", "sho cthy chocthy qokchy dory"),
    ("G634-L07", "f114v", "f114v.33", "kaiin sheey oaiin sheol qoteey qokeeedy cheo ctheey qokeeo lkealy"),
    ("G634-L08", "f85r1", "f85r1.21", "daiir cheody oraiin ol okaiin cheocthey olor otedy qotaiin chor chedy"),
)

EXPECTED_INPUTS = {
    "transcription/voynich_zl3b_tokens.tsv",
    "transcription/voynich_cross_transcription_lines.tsv",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/PAGE_ALLOWLIST.tsv",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/WORKING_DICTIONARY_V10.tsv",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/RESULT.json",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/src/run.py",
    "gdt044_result.json",
    "GDT044_OKAM_TERMINAL_M_REPORT.md",
}

EXPECTED_QUALITY_GLOBAL = {
    0: (907, 18, 163, 699, 16, "Grundform"),
    1: (2275, 23, 142, 1562, 22, "Bindungsstufe 1"),
    2: (1663, 21, 134, 1271, 19, "Bindungsstufe 2"),
    3: (105, 13, 43, 80, 12, "Bindungsstufe 3"),
}

# occurrence, page, locus, triple-exact counts for the thirteen target forms.
EXPECTED_QUALITY_TARGETS = {
    "chy": (162, 96, 153, 114),
    "shey": (232, 76, 209, 179),
    "sheey": (127, 64, 124, 105),
    "qoty": (86, 53, 85, 77),
    "oty": (101, 66, 99, 92),
    "qoteey": (40, 28, 38, 38),
    "chedy": (470, 74, 420, 296),
    "cheody": (69, 42, 69, 54),
    "otedy": (131, 49, 122, 75),
    "qokeedy": (292, 52, 251, 201),
    "qokeeedy": (4, 4, 4, 1),
    "chety": (18, 17, 18, 16),
    "ety": (6, 6, 6, 6),
}

EXPECTED_O_COUNTS = {
    "OA_VALUE": {"oain": 11, "oaiin": 22},
    "SHOKA_VALUE": {"shokain": 1, "shokaiin": 4},
    "QOK_TERMINAL_O_E": {"qokeo": 8, "qokeeo": 17},
    "CH_INNER_ODY_E": {"chody": 78, "cheody": 69, "cheeody": 10},
    "OT_DY_E": {"otdy": 1, "otedy": 131, "oteedy": 88, "oteeedy": 2},
    "COLD_Y_WRAPPERS": {"ty": 20, "oty": 101, "qoty": 86},
    "COLD_EE_Y_WRAPPERS": {"teey": 17, "oteey": 100, "qoteey": 40},
    "COLD_E_DY_WRAPPERS": {"tedy": 31, "otedy": 131, "qotedy": 78},
    "HOT_EE_DY_WRAPPERS": {"keedy": 59, "okeedy": 94, "qokeedy": 292},
}

EXPECTED_M = {
    "ALL_TERMINAL_M": (838, 144, 591, 592),
    "ALL_AM": (628, 130, 462, 440),
    "kam": (7, 7, 5, 1),
    "okam": (27, 24, 19, 17),
    "qokam": (25, 21, 21, 22),
    "olkam": (11, 9, 8, 9),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def parse_count_field(value: str) -> dict[str, int]:
    if not value or value == "NONE":
        return {}
    parsed: dict[str, int] = {}
    for item in value.split("|"):
        form, count = item.rsplit(":", 1)
        parsed[form] = int(count)
    return parsed


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(VALIDATION not in GENERATED, "validation output excluded from replay set")
    check(len(GENERATED) == 18 and len(set(GENERATED)) == 18, "eighteen unique builder outputs")
    check(all(path.is_file() for path in GENERATED), "all generated artifacts exist before replay")
    before = {path: path.read_bytes() for path in GENERATED}
    completed = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False,
    )
    check(completed.returncode == 0, "builder exits zero")
    check(
        completed.stdout.strip()
        == "GDT634 built: lines=8 tokens=69 types=58 quality=4950/75 dictionary=132 unassigned=0",
        "builder summary",
    )
    check(all(path.read_bytes() == before[path] for path in GENERATED), "builder replay is byte-identical")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT634_KNOWN_CORE_TERMINAL_SEMANTICS_RESULT_V1", "result schema")
    check(result["experiment_id"] == "GDT634", "result experiment id")
    check(
        result["status"] == "COMPLETE_8_LINE_CONCRETE_WORKING_EDITION__69_OF_69_TOKENS_DEFAULTED",
        "result status",
    )
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(result["content_sha256"] == canonical_hash(result_core), "canonical result content hash")
    check(result["guard"] == {
        "allowed_pages": 179,
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    }, "guarded source scope")

    check(set(result["inputs"]) == EXPECTED_INPUTS, "complete inherited input set")
    for path, digest in sorted(result["inputs"].items()):
        check((ROOT / path).is_file(), f"input exists {path}")
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    expected_bound_outputs = {rel(path) for path in GENERATED if path != RESULT}
    check(set(result["outputs"]) == expected_bound_outputs, "result binds every evidence output and not validation")
    check(rel(VALIDATION) not in result["outputs"], "validation hash is non-self-referential")
    for path, digest in sorted(result["outputs"].items()):
        check((ROOT / path).is_file(), f"output exists {path}")
        check(sha256(ROOT / path) == digest, f"output hash {path}")

    allow = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    allow_pages = [row["page"] for row in allow]
    check(len(allow_pages) == 179 and len(set(allow_pages)) == 179, "179 unique allowed pages")
    check(allow_pages == sorted(allow_pages), "allow-list is deterministic and sorted")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == INHERITED_ALLOW.read_bytes(), "allow-list exactly inherits GDT633 scope")
    check(all(page != "f1r" and not page.startswith("f84") for page in allow_pages), "allow-list excludes f1r, f84, and f84r")
    allowed = set(allow_pages)

    # Page/locus columns in every emitted TSV must stay inside the inherited
    # allow-list. Raw mixed transcription tables are never parsed here.
    for path in GENERATED:
        if path.suffix != ".tsv":
            continue
        rows = read_tsv(path)
        for row in rows:
            if "page" in row:
                check(row["page"] in allowed, f"allowed page in {path.name}: {row['page']}")
            if "locus" in row:
                page = row["locus"].split(".", 1)[0]
                check(page in allowed, f"allowed locus in {path.name}: {row['locus']}")
                check(page != "f1r" and not page.startswith("f84"), f"excluded locus absent in {path.name}: {row['locus']}")

    lines = read_tsv(ART / "TARGET_LINES.tsv")
    check(len(lines) == 8, "eight target lines")
    check(
        tuple((row["line_id"], row["page"], row["locus"], row["zl3b_line"]) for row in lines) == EXPECTED_LINES,
        "exact target loci and line order",
    )
    expected_token_counts = [len(text.split()) for _, _, _, text in EXPECTED_LINES]
    check([int(row["token_count"]) for row in lines] == expected_token_counts, "exact per-line token counts")
    check(sum(expected_token_counts) == 69, "target lines contain 69 tokens")
    check(all(row["it2a_line"] and row["rf1b_line"] and row["reader_evidence_de"] for row in lines), "all lines retain reader evidence")

    tokens = read_tsv(ART / "COMPLETE_TOKEN_WORKING_EDITION.tsv")
    check(len(tokens) == 69, "69 token-position editions")
    check([row["edition_id"] for row in tokens] == [f"G634-T{i:03d}" for i in range(1, 70)], "edition IDs are exact and ordered")
    expected_flat: list[tuple[str, str, int, str]] = []
    for line_id, _, locus, text in EXPECTED_LINES:
        expected_flat.extend((line_id, locus, position, surface) for position, surface in enumerate(text.split(), 1))
    observed_flat = [(row["line_id"], row["locus"], int(row["position"]), row["surface"]) for row in tokens]
    check(observed_flat == expected_flat, "all 69 surfaces preserve exact line and position order")
    check(len({row["surface"] for row in tokens}) == 58, "69 editions contain 58 surface types")
    required_token_fields = ("structural_parse", "working_default_de", "basis", "confidence", "live_rival_de")
    check(all(all(row[field].strip() for field in required_token_fields) for row in tokens), "every token has parse, concrete default, basis, confidence, and rival")
    check(sum(int(row["ordinal_surface_all_readers_exact"]) for row in tokens) == 51, "51 target tokens pass ordinal surface exactness in all readers")
    check(sum(int(row["zl_surface_split_normalized_all_readers"]) for row in tokens) == 53, "53 ZL surfaces survive exact or reader-split normalization")
    rescued = {
        row["surface"] for row in tokens
        if row["ordinal_surface_all_readers_exact"] == "0"
        and row["zl_surface_split_normalized_all_readers"] == "1"
    }
    check(rescued == {"saiin", "qotainol"}, "only saiin and qotainol gain through ZL-surface split normalization")
    check(not any(" oder " in row["working_default_de"] or " / " in row["working_default_de"] for row in tokens), "every token has one primary gloss; alternatives stay in rival fields")
    token_by_locus_surface = {(row["locus"], row["surface"]): row for row in tokens}
    check(token_by_locus_surface[("f85r1.21", "daiir")]["working_default_de"] == "Maß III", "daiir normalization is concrete at target locus")
    for locus, surface in (("f80r.18", "shcthy"), ("f80r.18", "shecthy"), ("f80v.10", "shcthy"), ("f80v.10", "shecthy"), ("f114v.33", "ctheey")):
        check("Blatt" not in token_by_locus_surface[(locus, surface)]["working_default_de"], f"non-Herbal CTH stays generic drug material {locus} {surface}")
    for locus, surface in (("f29r.1", "cheecthy"), ("f20v.10", "chocthy"), ("f22v.15", "cthy"), ("f22v.15", "chocthy")):
        check("Blatt" in token_by_locus_surface[(locus, surface)]["working_default_de"], f"Herbal CTH receives leaf-herb specialization {locus} {surface}")

    generic = re.compile(
        r"Arbeitsgut|Arbeitsschritt|Arbeitsmaterial|ausf(?:ü|ue)hren|weiterleit|leite\s+weiter|"
        r"\b(?:arbeite|prozessiere|verarbeite)\b|nimm\s+Werkzeug|bring\s+das\s+Produkt",
        re.IGNORECASE,
    )
    check(not any(generic.search(row["working_default_de"]) for row in tokens), "token defaults contain no generic work/process filler")

    micro = read_tsv(ART / "COMPLETE_MICROLINE_TRANSLATIONS.tsv")
    check(len(micro) == 8, "eight complete micro-line translations")
    check([row["line_id"] for row in micro] == [row[0] for row in EXPECTED_LINES], "micro-line order matches target lines")
    for row, (_, _, locus, text), count in zip(micro, EXPECTED_LINES, expected_token_counts):
        check(row["locus"] == locus and row["surface_line"] == text, f"micro-line source replay {locus}")
        check((int(row["token_count"]), int(row["tokens_with_primary_default"]), int(row["unassigned_or_banned_filler_tokens"])) == (count, count, 0), f"complete defaults {locus}")
        check(bool(row["working_translation_de"].strip()), f"nonempty translation {locus}")
        check(not generic.search(row["working_translation_de"]), f"no generic filler in translation {locus}")
        check(len(row["working_translation_de"].rstrip(".").split(" | ")) == count, f"token-aligned gloss count {locus}")

    census = read_tsv(ART / "TARGET_WORD_CENSUS.tsv")
    check(len(census) == 58 and len({row["surface"] for row in census}) == 58, "58 unique target census rows")
    check([row["surface"] for row in census] == sorted(row["surface"] for row in census), "target census is sorted")
    target_counter = Counter(row["surface"] for row in tokens)
    check({row["surface"]: int(row["target_occurrences"]) for row in census} == dict(target_counter), "census exactly covers target occurrences")
    for row in census:
        check(int(row["allowed_occurrences"]) >= int(row["target_occurrences"]), f"allowed count covers target {row['surface']}")
        check(int(row["ordinal_surface_all_readers_exact_occurrences"]) <= int(row["allowed_occurrences"]), f"exact count bounded {row['surface']}")
        check(int(row["zl_surface_split_normalized_all_readers_occurrences"]) <= int(row["allowed_occurrences"]), f"boundary count bounded {row['surface']}")
        check(all(row[field].strip() for field in ("structural_parse", "working_default_de", "basis", "confidence")), f"complete census semantics {row['surface']}")
        check(not generic.search(row["working_default_de"]), f"no generic census filler {row['surface']}")

    quality_global_rows = read_tsv(ART / "QUALITY_E_LENGTH_GLOBAL_SUMMARY.tsv")
    quality_global = {int(row["e_level"]): row for row in quality_global_rows}
    check(set(quality_global) == {0, 1, 2, 3}, "complete literal e0-e3 global table")
    for level, expected in EXPECTED_QUALITY_GLOBAL.items():
        row = quality_global[level]
        observed = tuple(int(row[field]) for field in (
            "occurrences", "types", "pages", "ordinal_surface_all_readers_exact_occurrences",
            "types_with_any_ordinal_surface_all_readers_exact",
        )) + (row["working_slot_de"],)
        check(observed == expected, f"exact global quality counts e{level}")
    check(sum(int(row["occurrences"]) for row in quality_global_rows) == 4950, "4950 global quality occurrences")
    check(sum(int(row["types"]) for row in quality_global_rows) == 75, "75 global quality types")
    check(sum(int(row["ordinal_surface_all_readers_exact_occurrences"]) for row in quality_global_rows) == 3612, "3612 ordinal-surface all-reader-exact quality occurrences")
    check(result["quality_terminal"]["main_pages"] == 176, "quality family spans 176 pages")

    quality_targets_rows = read_tsv(ART / "QUALITY_TERMINAL_TARGETS.tsv")
    quality_targets = {row["surface"]: row for row in quality_targets_rows}
    check(set(quality_targets) == set(EXPECTED_QUALITY_TARGETS), "exact thirteen quality target forms")
    for surface, expected in EXPECTED_QUALITY_TARGETS.items():
        row = quality_targets[surface]
        observed = tuple(int(row[field]) for field in ("occurrences", "pages", "loci", "ordinal_surface_all_readers_exact_occurrences"))
        check(observed == expected, f"quality target census {surface}")
        check(bool(row["structural_parse"] and row["working_default_de"] and row["confidence"]), f"quality target default {surface}")
    check(result["quality_terminal"] == {
        "e_level_counts": {"0": 907, "1": 2275, "2": 1663, "3": 105},
        "main_occurrences": 4950, "main_pages": 176, "main_ordinal_surface_all_readers_exact": 3612, "main_types": 75,
        "target_zl_ladder_loci_union": 138,
        "target_all_member_ordinal_surface_all_readers_exact_ladder_loci_union": 69, "target_types": 13,
    }, "result quality summary")

    o_rows = {row["paradigm_id"]: row for row in read_tsv(ART / "O_PREPARATION_TRANSFER_PARADIGMS.tsv")}
    check(set(o_rows) == set(EXPECTED_O_COUNTS), "nine exact o-transfer paradigms")
    for paradigm, expected in EXPECTED_O_COUNTS.items():
        row = o_rows[paradigm]
        check(parse_count_field(row["occurrences_by_form"]) == expected, f"o-transfer counts {paradigm}")
        check(row["forms"].split("|") == list(expected), f"o-transfer form order {paradigm}")
        check("nicht Wasser, Wein oder Öl" in row["boundary_de"], f"o-specific-medium boundary {paradigm}")

    carriers = {row["prefix"]: row for row in read_tsv(ART / "AL_AR_OL_OR_CARRIER_LATTICE.tsv")}
    check(len(carriers) == 14 and {"BARE", "qok"} <= set(carriers), "fourteen carrier-prefix rows")
    bare_counts = {ending: int(carriers["BARE"][f"{ending}_occurrences"]) for ending in ("al", "ar", "ol", "or")}
    qok_counts = {ending: int(carriers["qok"][f"{ending}_occurrences"]) for ending in ("al", "ar", "ol", "or")}
    check(bare_counts == {"al": 204, "ar": 321, "ol": 463, "or": 321}, "bare AL/AR/OL/OR counts")
    check(qok_counts == {"al": 180, "ar": 153, "ol": 88, "or": 29}, "qok AL/AR/OL/OR counts")
    check(carriers["qok"]["zl_same_line_pairs"] == "al~ar:16|al~ol:3|ar~ol:1|ar~or:2", "qok ZL same-line carrier pairs")
    check(result["carrier_checks"] == {
        "bare": bare_counts, "qok": qok_counts,
        "qok_zl_same_line_pairs": "al~ar:16|al~ol:3|ar~ol:1|ar~or:2",
    }, "result carrier summary")

    composition = read_tsv(ART / "AGGRESSIVE_DEFAULT_COMPOSITION_CHECKS.tsv")
    check(len(composition) == 10 and len({row["check_id"] for row in composition}) == 10, "ten aggressive-default composition checks")
    check(Counter(row["status"] for row in composition) == Counter({"MULTIPLE_LISTED_FORMS_ATTESTED": 8, "ONE_SIDED_ONLY": 2}), "eight multi-form and two one-sided composition checks")
    check({row["check_id"] for row in composition if row["status"] == "ONE_SIDED_ONLY"} == {"R_ROOT_DRY_MOIST", "L_LIQUID_HOT_COLD"}, "initial r/l defaults remain the two one-sided checks")
    check(result["aggressive_composition_checks"] == {
        "rows": 10, "multiple_listed_forms_attested_rows": 8, "one_sided_rows": 2,
    }, "result aggressive-composition summary")

    heads = {row["head"]: row for row in read_tsv(ART / "INITIAL_HEAD_POSITION_AND_BACKOFF.tsv")}
    expected_heads = {
        "p": (503, 277, 395, 170, 360, 129, 14, 5),
        "s": (801, 248, 728, 178, 408, 282, 111, 272),
        "r": (332, 116, 313, 97, 15, 221, 96, 129),
        "l": (1224, 344, 1137, 261, 66, 930, 228, 163),
    }
    check(set(heads) == set(expected_heads), "exact p/s/r/l initial-head profiles")
    head_fields = (
        "prefixed_occurrences", "prefixed_types", "delete_head_counterpart_occurrences",
        "delete_head_counterpart_types", "first_occurrences", "middle_occurrences",
        "last_occurrences", "standalone_occurrences",
    )
    for head, expected in expected_heads.items():
        check(tuple(int(heads[head][field]) for field in head_fields) == expected, f"head position and backoff {head}")
    check(result["head_backoff"] == {
        head: {
            "prefixed_occurrences": expected[0],
            "delete_head_counterpart_occurrences": expected[2],
            "first_occurrences": expected[4],
        } for head, expected in expected_heads.items()
    }, "result initial-head backoff summary")

    bridges = {row["terminal"]: row for row in read_tsv(ART / "CARRIER_VOWEL_BODY_BRIDGES.tsv")}
    expected_bridges = {"L": (325, 364, 115, 1431, 2313), "R": (417, 337, 131, 1864, 1576)}
    check(set(bridges) == {"L", "R"}, "L/R carrier-vowel bridge rows")
    bridge_fields = ("a_carrier_types", "o_carrier_types", "shared_bodies", "shared_a_occurrences", "shared_o_occurrences")
    for terminal, expected in expected_bridges.items():
        check(tuple(int(bridges[terminal][field]) for field in bridge_fields) == expected, f"carrier-vowel bridge {terminal}")
    check(result["carrier_vowel_bridges"] == {
        terminal: {"shared_bodies": expected[2], "shared_a_occurrences": expected[3], "shared_o_occurrences": expected[4]}
        for terminal, expected in expected_bridges.items()
    }, "result carrier-vowel bridge summary")

    terminal_m_rows = {row["population"]: row for row in read_tsv(ART / "TERMINAL_M_PROFILE.tsv")}
    check(set(terminal_m_rows) == set(EXPECTED_M), "complete terminal-m profile")
    for population, expected in EXPECTED_M.items():
        row = terminal_m_rows[population]
        observed = tuple(int(row[field]) for field in (
            "occurrences", "pages", "line_final_occurrences", "ordinal_surface_all_readers_exact_occurrences",
        ))
        check(observed == expected, f"terminal-m counts {population}")
        check(row["line_final_share"] == f"{expected[2] / expected[0]:.6f}", f"terminal-m share {population}")
        check("unbekannt" in row["working_default_de"], f"terminal-m value remains unknown {population}")
    check(result["terminal_m"] == {
        "all_occurrences": 838, "all_line_final": 591, "olkam_occurrences": 11, "olkam_line_final": 8,
    }, "result terminal-m summary")
    check("unbekannt" in result["concrete_transfers"]["m"], "result does not assign terminal-m a silent meaning")

    old_dictionary = read_tsv(V10)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V11.tsv")
    check(len(old_dictionary) == 76, "V10 has 76 inherited entries")
    check(len(dictionary) == 132 and len({row["entry"] for row in dictionary}) == 132, "V11 has 132 unique entries")
    check(dictionary[:76] == old_dictionary, "V11 preserves all inherited rows and context rules byte-for-byte at row level")
    check(len(dictionary[76:]) == 56, "fifty-six V11 entries added")
    target_dictionary = {
        row["entry"].split("@", 1)[0]: row for row in dictionary
        if row["entry"].split("@", 1)[0] in target_counter
    }
    check(set(target_dictionary) == set(target_counter), "dictionary has one default for every target type")
    check(all(row["working_meaning_de"].strip() and row["composition"].strip() for row in target_dictionary.values()), "all target dictionary entries are concrete and composed")
    check(not any(generic.search(row["working_meaning_de"]) for row in target_dictionary.values()), "dictionary target defaults contain no generic filler")
    check(result["working_dictionary"] == {
        "entries": 132, "inherited_v10_entries": 76, "revised_v10_entries": 0, "new_v11_entries": 56,
    }, "result dictionary summary")

    check(result["edition"] == {
        "basis_counts": dict(sorted(Counter(row["basis"] for row in tokens).items())),
        "lines": 8, "tokens": 69, "tokens_with_primary_default": 69,
        "zl_surface_split_normalized_all_readers_target_tokens": 53,
        "ordinal_surface_all_readers_exact_target_tokens": 51,
        "types": 58, "unassigned_or_banned_filler_tokens": 0,
    }, "result edition summary")
    check("all 69 token positions and all 58 surface types" in result["claim_boundary"], "claim boundary states complete target coverage")
    check("not a solved language" in result["claim_boundary"], "claim boundary keeps the edition provisional")

    payload_core = {
        "schema": "GDT634_VALIDATION_V1", "experiment_id": "GDT634", "status": "PASS",
        "check_count": len(checks), "checks": checks, "byte_replay_artifacts": len(GENERATED),
        "edition": {"lines": 8, "tokens": 69, "types": 58, "unassigned_or_banned_filler_tokens": 0},
        "quality": {"occurrences": 4950, "types": 75, "pages": 176, "ordinal_surface_all_readers_exact": 3612},
        "composition_checks": {"rows": 10, "multiple_listed_forms_attested": 8, "one_sided": 2},
        "dictionary_entries": 132, "result_sha256": sha256(RESULT),
    }
    payload = {**payload_core, "content_sha256": canonical_hash(payload_core)}
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
