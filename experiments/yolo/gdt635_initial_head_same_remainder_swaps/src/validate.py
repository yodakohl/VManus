#!/usr/bin/env python3
"""Independently validate and byte-replay the GDT635 working model."""

from __future__ import annotations

import csv
import hashlib
import itertools
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
BASE_REL = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V11 = ROOT / "experiments/yolo/gdt634_known_core_terminal_semantics/artifacts/WORKING_DICTIONARY_V11.tsv"
INHERITED_ALLOW = ROOT / "experiments/yolo/gdt634_known_core_terminal_semantics/artifacts/PAGE_ALLOWLIST.tsv"

TSV_NAMES = (
    "PAGE_ALLOWLIST.tsv",
    "INITIAL_HEAD_SCOPE_PROFILE.tsv",
    "SHARED_REMAINDER_OCCUPANCY.tsv",
    "SHARED_REMAINDER_ATLAS.tsv",
    "HEAD_PAIR_SHARED_REMAINDER_SUMMARY.tsv",
    "FOUR_WAY_REMAINDER_ATLAS.tsv",
    "STATE_BODY_HEAD_GRID.tsv",
    "CONCRETE_FOUR_HEAD_PARADIGMS.tsv",
    "SAME_LINE_HEAD_SWAPS.tsv",
    "EXACT_NEIGHBOR_FRAME_SWAPS.tsv",
    "MATCHED_SPAN_TRANSLATIONS.tsv",
    "HEAD_MODEL_COMPARISON.tsv",
    "ACTIVE_HEAD_CODEBOOK_V12.tsv",
    "HISTORICAL_HEAD_MODEL.tsv",
    "WORKING_DICTIONARY_V12.tsv",
)
GENERATED = tuple(ART / name for name in TSV_NAMES) + (RESULT,)

HEAD_ORDER = ("p", "s", "r", "l")
HEAD_RANK = {head: index for index, head in enumerate(HEAD_ORDER)}
HEAD_LATIN = {"p": "pulvis", "s": "semen", "r": "radix", "l": "lignum"}
HEAD_MEANING = {
    "p": "Pulver/Pulverform",
    "s": "Samen/Saatgut",
    "r": "Wurzel/Wurzeldroge",
    "l": "Drogenholz/holziger Pflanzenteil",
}
HEAD_COUNTS = {
    "p": (503, 277, 140, 438, 361, 360, 129, 14),
    "s": (801, 248, 149, 727, 596, 408, 282, 111),
    "r": (332, 116, 68, 302, 216, 15, 221, 96),
    "l": (1224, 344, 104, 903, 923, 66, 930, 228),
}

EXPECTED_PAIRWISE = {
    "ps": {"shared_bodies": 52, "pair_only": 13, "same_line": 0, "exact_frames": 9, "register_frames": 5},
    "pr": {"shared_bodies": 38, "pair_only": 2, "same_line": 1, "exact_frames": 0, "register_frames": 0},
    "pl": {"shared_bodies": 68, "pair_only": 29, "same_line": 2, "exact_frames": 2, "register_frames": 2},
    "sr": {"shared_bodies": 55, "pair_only": 13, "same_line": 0, "exact_frames": 2, "register_frames": 0},
    "sl": {"shared_bodies": 63, "pair_only": 18, "same_line": 5, "exact_frames": 4, "register_frames": 3},
    "rl": {"shared_bodies": 54, "pair_only": 12, "same_line": 4, "exact_frames": 3, "register_frames": 1},
}

BODY_VALUES = {
    "aiin": "Typ/Charge III",
    "chedy": "getrockneter Zustand",
    "shedy": "angefeuchteter/eingeweichter Zustand",
    "ol": "Stoff/Material",
    "or": "Teil/Portion",
}
CANONICAL_DEFAULTS = {
    ("aiin", "p"): "Pulver, Typ/Charge III",
    ("aiin", "s"): "Samen/Saatgut, Typ/Charge III",
    ("aiin", "r"): "Wurzel, Typ/Charge III",
    ("aiin", "l"): "Drogenholz, Typ/Charge III",
    ("chedy", "p"): "getrocknetes Pulver",
    ("chedy", "s"): "getrocknete Samen/Saat",
    ("chedy", "r"): "getrocknete Wurzel",
    ("chedy", "l"): "getrocknetes Drogenholz",
    ("shedy", "p"): "angefeuchtetes Pulver/Paste",
    ("shedy", "s"): "eingeweichte Samen/Saat",
    ("shedy", "r"): "eingeweichte Wurzel",
    ("shedy", "l"): "eingeweichtes Drogenholz",
    ("ol", "p"): "Pulverstoff",
    ("ol", "s"): "Samenmaterial/Saatgut",
    ("ol", "r"): "Wurzelstoff",
    ("ol", "l"): "Holzstoff",
    ("or", "p"): "Pulverportion",
    ("or", "s"): "Samenportion",
    ("or", "r"): "Wurzelportion",
    ("or", "l"): "Holzportion",
}
CANONICAL_OCCURRENCES = {
    "paiin": 7, "saiin": 109, "raiin": 62, "laiin": 13,
    "pchedy": 35, "schedy": 7, "rchedy": 10, "lchedy": 116,
    "pshedy": 3, "sshedy": 6, "rshedy": 5, "lshedy": 38,
    "pol": 16, "sol": 57, "rol": 20, "lol": 35,
    "por": 7, "sor": 43, "ror": 12, "lor": 38,
}

STATE_BODIES = (
    "chy", "chey", "cheey", "chdy", "chedy",
    "shy", "shey", "sheey", "shdy", "shedy",
)
EXPECTED_EMPTY_STATE_CELLS = {("shy", "s"), ("shy", "r"), ("sheey", "r"), ("shdy", "s")}

EXPECTED_SPANS = {
    "PS_DRY_P": ("f75r.13", 1, 2, ("pchedy", "keedy")),
    "PS_DRY_S": ("f78r.9", 1, 2, ("schedy", "keedy")),
    "PS_MATERIAL_P": ("f77r.38", 1, 2, ("pol", "shedy")),
    "PS_MATERIAL_S": ("f76v.40", 1, 2, ("sol", "shedy")),
    "PS_CLASS_P": ("f10v.1", 1, 2, ("paiin", "daiin")),
    "PS_CLASS_S": ("f81v.3", 1, 2, ("saiin", "daiin")),
    "RL_MATERIAL_R": ("f106v.8", 2, 4, ("cheo", "rol", "aiin")),
    "RL_MATERIAL_L": ("f111v.10", 5, 7, ("cheo", "lol", "aiin")),
    "RL_PORTION_L": ("f103r.21", 11, 12, ("qokeedy", "lor")),
    "RL_PORTION_R": ("f79v.13", 8, 9, ("qokeedy", "ror")),
}

EXPECTED_INPUTS = {
    "transcription/voynich_zl3b_tokens.tsv",
    "transcription/voynich_cross_transcription_lines.tsv",
    "experiments/yolo/gdt634_known_core_terminal_semantics/src/run.py",
    "experiments/yolo/gdt634_known_core_terminal_semantics/artifacts/PAGE_ALLOWLIST.tsv",
    "experiments/yolo/gdt634_known_core_terminal_semantics/artifacts/WORKING_DICTIONARY_V11.tsv",
    "experiments/yolo/gdt634_known_core_terminal_semantics/artifacts/RESULT.json",
    "experiments/yolo/gdt627_value_head_role_atlas/artifacts/HISTORICAL_SYNTAX_COMPARATORS.tsv",
}

GENERIC_FILLER = re.compile(
    r"Arbeitsgut|Arbeitsschritt|Arbeitsmaterial|ausf(?:ü|ue)hren|weiterleit|"
    r"leite\s+weiter|\b(?:arbeite|prozessiere|verarbeite)\b|nimm\s+Werkzeug|"
    r"bring\s+das\s+Produkt|noch\s+keine|unbekannt|unbestimmt",
    re.IGNORECASE,
)
FOLIO_RE = re.compile(r"(?<![A-Za-z0-9])f\d{1,3}[rv](?:\d+)?")


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


def split_pipe(value: str) -> list[str]:
    return [] if not value or value == "NONE" else value.split("|")


def parse_int_map(value: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for item in split_pipe(value):
        key, number = item.split(":", 1)
        parsed[key] = int(number)
    return parsed


def parse_text_map(value: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in split_pipe(value):
        key, text = item.split(":", 1)
        parsed[key] = text
    return parsed


def pair_name(a: str, b: str) -> str:
    return "".join(sorted((a, b), key=HEAD_RANK.__getitem__))


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(VALIDATION not in GENERATED, "validation output excluded from replay set")
    check(len(GENERATED) == 16 and len(set(GENERATED)) == 16, "sixteen unique builder outputs")
    check(all(path.is_file() for path in GENERATED), "all builder outputs exist before replay")
    before = {path: path.read_bytes() for path in GENERATED}
    completed = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False,
    )
    check(completed.returncode == 0, "builder exits zero")
    check(
        completed.stdout.strip()
        == "GDT635 built: initial=2860 bodies=760 shared=144 four_way=24 frames=18 spans=10 dictionary=156",
        "builder summary is exact",
    )
    check(all(path.read_bytes() == before[path] for path in GENERATED), "builder replay is byte-identical")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT635_INITIAL_HEAD_SAME_REMAINDER_SWAPS_RESULT_V1", "result schema")
    check(result["experiment_id"] == "GDT635", "result experiment id")
    check(
        result["status"] == "MATERIA_HEAD_MODEL_PRIMARY__P_PULVIS_S_SEMEN_R_RADIX_L_LIGNUM",
        "result status",
    )
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(result["content_sha256"] == canonical_hash(result_core), "canonical result content hash")

    expected_guard = {
        "allowed_pages": 179,
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
        "new_images": 0, "new_pages": 0, "token_bearing_loci": 4128,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    }
    check(result["guard"] == expected_guard, "guarded source scope and query counters")
    run_source = RUN.read_text(encoding="utf-8")
    check(run_source.count("guarded_query(") == 2, "builder uses guarded query twice")
    check("read_tsv(ROOT / TOKENS_REL)" not in run_source and "read_tsv(ROOT / CROSS_REL)" not in run_source, "builder never parses mixed transcription tables directly")
    check('"f1r" in pages' in run_source and 'page.startswith("f84")' in run_source, "builder has explicit f1r and f84-family allow-list gate")

    check(set(result["inputs"]) == EXPECTED_INPUTS, "complete exact input set")
    for path, digest in sorted(result["inputs"].items()):
        check((ROOT / path).is_file(), f"input exists {path}")
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    expected_bound_outputs = {rel(path) for path in GENERATED if path != RESULT}
    check(set(result["outputs"]) == expected_bound_outputs, "result binds all fifteen evidence TSVs")
    check(rel(VALIDATION) not in result["outputs"] and rel(RESULT) not in result["outputs"], "result and validation are non-self-referential")
    for path, digest in sorted(result["outputs"].items()):
        check((ROOT / path).is_file(), f"output exists {path}")
        check(sha256(ROOT / path) == digest, f"output hash {path}")

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    allow_pages = [row["page"] for row in allow_rows]
    allowed = set(allow_pages)
    check(len(allow_pages) == 179 and len(allowed) == 179, "179 unique allowed pages")
    check(allow_pages == sorted(allow_pages), "allow-list is sorted deterministically")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == INHERITED_ALLOW.read_bytes(), "allow-list byte-identically inherits GDT634")
    check("f1r" not in allowed and all(not page.startswith("f84") for page in allowed), "allow-list excludes f1r, f84, and f84r")

    # Audit every Voynich folio reference in evidence TSVs. External comparator
    # folios in HISTORICAL_HEAD_MODEL are deliberately a different namespace.
    for path in GENERATED:
        if path.suffix != ".tsv":
            continue
        for row in read_tsv(path):
            for field, value in row.items():
                if path.name == "HISTORICAL_HEAD_MODEL.tsv" and field == "folio":
                    continue
                for page in FOLIO_RE.findall(value or ""):
                    check(page in allowed, f"allowed Voynich page in {path.name}: {page}")
                    check(page != "f1r" and not page.startswith("f84"), f"forbidden Voynich page absent in {path.name}: {page}")

    profiles = read_tsv(ART / "INITIAL_HEAD_SCOPE_PROFILE.tsv")
    check([row["head"] for row in profiles] == list(HEAD_ORDER), "four initial-head profiles in fixed order")
    profiles_by_head = {row["head"]: row for row in profiles}
    profile_fields = (
        "initial_occurrences", "initial_types", "initial_pages", "initial_loci",
        "initial_reader_exact_occurrences", "line_first", "line_middle", "line_last",
    )
    for head, expected in HEAD_COUNTS.items():
        row = profiles_by_head[head]
        check(tuple(int(row[field]) for field in profile_fields) == expected, f"exact initial-head profile {head}")
        check(row["latin_stem"] == HEAD_LATIN[head] and row["primary_default_de"] == HEAD_MEANING[head], f"primary Latin stem and German meaning {head}")
        check(sum(int(row[field]) for field in ("line_first", "line_middle", "line_last")) == int(row["initial_occurrences"]), f"line positions partition {head}")
        check(int(row["initial_reader_exact_occurrences"]) <= int(row["initial_occurrences"]), f"reader-exact count bounded {head}")
        check("Einzeichenform" in row["scope_rule_de"] and "terminales Zeichen" in row["scope_rule_de"], f"initial head is scoped away from standalone/internal/terminal {head}")
    check((profiles_by_head["s"]["excluded_sh_occurrences"], profiles_by_head["s"]["excluded_sh_types"]) == ("2755", "463"), "s profile explicitly excludes 2755 sh occurrences and 463 sh types")
    check(all(profiles_by_head[h]["excluded_sh_occurrences"] == "0" for h in ("p", "r", "l")), "sh exclusion is confined to the s head")

    occupancy = read_tsv(ART / "SHARED_REMAINDER_OCCUPANCY.tsv")
    check(len(occupancy) == 760 and len({row["body"] for row in occupancy}) == 760, "760 unique remainder bodies")
    check(Counter(int(row["head_occupancy"]) for row in occupancy) == Counter({1: 616, 2: 87, 3: 33, 4: 24}), "exact 616/87/33/24 head-occupancy distribution")
    head_type_counts: Counter[str] = Counter()
    head_occurrence_counts: Counter[str] = Counter()
    for row in occupancy:
        body = row["body"]
        heads = split_pipe(row["heads"])
        forms = parse_text_map(row["forms"])
        occurrences = parse_int_map(row["occurrences_by_head"])
        pages = parse_int_map(row["pages_by_head"])
        loci = parse_int_map(row["loci_by_head"])
        reader_exact = parse_int_map(row["reader_exact_by_head"])
        check(set(forms) == set(HEAD_ORDER) == set(occurrences) == set(pages) == set(loci) == set(reader_exact), f"complete four-head maps for body {body}")
        check(heads == [head for head in HEAD_ORDER if occurrences[head] > 0], f"occupied heads are ordered and exact for body {body}")
        check(int(row["head_occupancy"]) == len(heads), f"head occupancy agrees for body {body}")
        check(int(row["total_headed_occurrences"]) == sum(occurrences.values()), f"headed occurrence total agrees for body {body}")
        for head in HEAD_ORDER:
            occupied = head in heads
            check(forms[head] == (head + body if occupied else "-"), f"literal head+body form {head}+{body}")
            check((occurrences[head] > 0) == occupied, f"positive occurrence iff occupied {head}+{body}")
            check(0 <= reader_exact[head] <= occurrences[head], f"reader-exact bounded {head}+{body}")
            check(0 <= pages[head] <= loci[head] <= occurrences[head], f"page/locus/occurrence nesting {head}+{body}")
            if occupied:
                head_type_counts[head] += 1
                head_occurrence_counts[head] += occurrences[head]
        check(row["exact_v11_dictionary_body"] in {"0", "1"}, f"binary V11-body flag {body}")
    check(sum(int(row["head_occupancy"]) for row in occupancy) == 985, "985 occupied head-body types")
    check(sum(int(row["total_headed_occurrences"]) for row in occupancy) == 2860, "2860 headed occurrences")
    check(dict(head_type_counts) == {head: HEAD_COUNTS[head][1] for head in HEAD_ORDER}, "occupancy independently reproduces 277/248/116/344 head types")
    check(dict(head_occurrence_counts) == {head: HEAD_COUNTS[head][0] for head in HEAD_ORDER}, "occupancy independently reproduces 503/801/332/1224 occurrences")
    check(not any(row["body"].startswith("h") and "s" in split_pipe(row["heads"]) for row in occupancy), "sh is absent from s+remainder analysis")

    shared = read_tsv(ART / "SHARED_REMAINDER_ATLAS.tsv")
    shared_source = [row for row in occupancy if int(row["head_occupancy"]) >= 2]
    shared_common = tuple(occupancy[0])
    check(len(shared) == 144 and len(shared_source) == 144, "144 shared remainder bodies")
    check([row["shared_id"] for row in shared] == [f"G635-R{i:03d}" for i in range(1, 145)], "shared-atlas IDs are complete and ordered")
    for emitted, source in zip(shared, shared_source):
        check(all(emitted[field] == source[field] for field in shared_common), f"shared atlas exactly inherits occupancy row {source['body']}")
    check(sum(int(row["bare_body_occurrences"]) > 0 for row in shared) == 140, "140 shared bodies also occur bare")
    check(sum(int(row["exact_v11_dictionary_body"]) for row in shared) == 22, "22 shared bodies have exact V11 entries")
    check(sum(int(row["total_headed_occurrences"]) for row in shared) == 1977, "1977 occurrences belong to shared bodies")

    four_way = read_tsv(ART / "FOUR_WAY_REMAINDER_ATLAS.tsv")
    four_source = [row for row in shared if int(row["head_occupancy"]) == 4]
    check(len(four_way) == 24 and len(four_source) == 24, "24 complete four-head remainder bodies")
    check([row["quad_id"] for row in four_way] == [f"G635-Q{i:02d}" for i in range(1, 25)], "four-way IDs are complete and ordered")
    check([row["body"] for row in four_way] == [row["body"] for row in four_source], "four-way atlas is exact occupancy-four subset")
    check(sum(int(row["total_headed_occurrences"]) for row in four_way) == 1166, "1166 occurrences belong to four-way bodies")
    check(set(BODY_VALUES) <= {row["body"] for row in four_way}, "all five canonical bodies are genuinely four-way")

    pair_rows = read_tsv(ART / "HEAD_PAIR_SHARED_REMAINDER_SUMMARY.tsv")
    expected_pair_order = ["ps", "pr", "pl", "sr", "sl", "rl"]
    check([row["pair"] for row in pair_rows] == expected_pair_order, "six head pairs in fixed combinatorial order")
    pair_by_name = {row["pair"]: row for row in pair_rows}
    for pair, expected in EXPECTED_PAIRWISE.items():
        row = pair_by_name[pair]
        a, b = row["head_a"], row["head_b"]
        bodies = [source for source in occupancy if a in split_pipe(source["heads"]) and b in split_pipe(source["heads"])]
        pair_only = [source for source in bodies if set(split_pipe(source["heads"])) == {a, b}]
        a_occ = sum(parse_int_map(source["occurrences_by_head"])[a] for source in bodies)
        b_occ = sum(parse_int_map(source["occurrences_by_head"])[b] for source in bodies)
        both_exact = sum(
            parse_int_map(source["reader_exact_by_head"])[a] > 0
            and parse_int_map(source["reader_exact_by_head"])[b] > 0
            for source in bodies
        )
        check(int(row["shared_bodies"]) == expected["shared_bodies"] == len(bodies), f"shared-body count {pair}")
        check(int(row["exact_pair_only_bodies"]) == expected["pair_only"] == len(pair_only), f"exact-pair-only count {pair}")
        check((int(row["head_a_occurrences_on_shared_bodies"]), int(row["head_b_occurrences_on_shared_bodies"])) == (a_occ, b_occ), f"pair occurrence totals {pair}")
        check(int(row["bodies_with_reader_exact_evidence_for_both"]) == both_exact, f"pair reader-exact-body count {pair}")
        check(int(row["same_line_body_locus_cells"]) == expected["same_line"], f"same-line count {pair}")
        check(int(row["exact_two_sided_frame_cells"]) == expected["exact_frames"], f"two-sided frame count {pair}")
        check(int(row["register_matched_frame_cells"]) == expected["register_frames"], f"register-matched frame count {pair}")
        check("↔" in row["working_contrast_de"] and not GENERIC_FILLER.search(row["working_contrast_de"]), f"concrete contrast {pair}")

    same_line = read_tsv(ART / "SAME_LINE_HEAD_SWAPS.tsv")
    check(len(same_line) == 12, "twelve same-line body+locus swap cells")
    check([row["swap_id"] for row in same_line] == [f"G635-L{i:02d}" for i in range(1, 13)], "same-line IDs are exact")
    same_line_pairs: Counter[str] = Counter()
    shared_lookup = {row["body"]: row for row in shared}
    for row in same_line:
        a, b, body = row["head_a"], row["head_b"], row["body"]
        pair = pair_name(a, b)
        same_line_pairs[pair] += 1
        tokens = row["zl3b_line"].split()
        positions_a = [int(value) for value in row["positions_a"].split("|")]
        positions_b = [int(value) for value in row["positions_b"].split("|")]
        check(row["page"] == row["locus"].split(".", 1)[0], f"same-line page/locus agreement {row['swap_id']}")
        check(row["form_a"] == a + body and row["form_b"] == b + body, f"same-line forms preserve exact common body {row['swap_id']}")
        check(all(tokens[position - 1] == row["form_a"] for position in positions_a), f"same-line A positions replay {row['swap_id']}")
        check(all(tokens[position - 1] == row["form_b"] for position in positions_b), f"same-line B positions replay {row['swap_id']}")
        check(int(row["reader_exact_a"]) <= len(positions_a) and int(row["reader_exact_b"]) <= len(positions_b), f"same-line reader evidence bounded {row['swap_id']}")
        check(body in shared_lookup and {a, b} <= set(split_pipe(shared_lookup[body]["heads"])), f"same-line body/head membership {row['swap_id']}")
        check("↔" in row["working_contrast_de"] and not GENERIC_FILLER.search(row["working_contrast_de"]), f"same-line contrast is concrete {row['swap_id']}")
    check(dict(same_line_pairs) == {pair: values["same_line"] for pair, values in EXPECTED_PAIRWISE.items() if values["same_line"]}, "same-line rows reproduce pair summary")
    required_same_line = {
        ("f105r.19", "aiin", "sl"), ("f116r.6", "ain", "sl"),
        ("f78r.43", "chedy", "pl"), ("f82r.29", "chedy", "rl"),
        ("f82v.15", "chedy", "pr"), ("f83r.6", "chedy", "sl"),
        ("f116r.27", "shedy", "pl"), ("f66r.72", "shedy", "sl"),
        ("f96r.6", "or", "sl"),
    }
    check(required_same_line <= {(row["locus"], row["body"], pair_name(row["head_a"], row["head_b"])) for row in same_line}, "nine named same-line witnesses are present")

    frames = read_tsv(ART / "EXACT_NEIGHBOR_FRAME_SWAPS.tsv")
    check(len(frames) == 18, "eighteen unique exact two-sided frames")
    check([row["frame_id"] for row in frames] == [f"G635-F{i:02d}" for i in range(1, 19)], "frame IDs are exact")
    check(len({(row["body"], row["previous"], row["following"]) for row in frames}) == 18, "frame keys are unique")
    frame_pair_edges: Counter[str] = Counter()
    register_pair_edges: Counter[str] = Counter()
    for row in frames:
        heads = split_pipe(row["heads"])
        forms = split_pipe(row["forms"])
        occurrences = parse_int_map(row["occurrences_by_head"])
        exact = parse_int_map(row["reader_exact_by_head"])
        loci = parse_text_map(row["loci_by_head"])
        check(len(heads) >= 2 and heads == sorted(heads, key=HEAD_RANK.__getitem__), f"frame heads ordered {row['frame_id']}")
        check(forms == [head + row["body"] for head in heads], f"frame forms preserve exact body {row['frame_id']}")
        check(set(occurrences) == set(heads) == set(exact) == set(loci), f"frame keyed evidence is complete {row['frame_id']}")
        check(all(0 <= exact[head] <= occurrences[head] for head in heads), f"frame reader-exact counts bounded {row['frame_id']}")
        frame_pages = set(split_pipe(row["pages"]))
        locus_pages = {locus.split(".", 1)[0] for value in loci.values() for locus in value.split("&")}
        check(frame_pages == locus_pages and frame_pages <= allowed, f"frame pages exactly derive from loci {row['frame_id']}")
        for a, b in itertools.combinations(heads, 2):
            frame_pair_edges[pair_name(a, b)] += 1
            if row["register_matched_all_heads"] == "1":
                register_pair_edges[pair_name(a, b)] += 1
        check(row["register_matched_all_heads"] in {"0", "1"}, f"binary register match {row['frame_id']}")
        check((row["shared_registers"] != "NONE") == (row["register_matched_all_heads"] == "1"), f"register witness agrees {row['frame_id']}")
        check("↔" in row["working_contrast_de"] and not GENERIC_FILLER.search(row["working_contrast_de"]), f"frame contrast is concrete {row['frame_id']}")
    check(Counter(len(split_pipe(row["heads"])) for row in frames) == Counter({2: 17, 3: 1}), "seventeen pair frames and one three-head frame")
    check(dict(frame_pair_edges) == {pair: values["exact_frames"] for pair, values in EXPECTED_PAIRWISE.items() if values["exact_frames"]}, "twenty pairwise frame edges reproduce pair summary")
    check(dict(register_pair_edges) == {pair: values["register_frames"] for pair, values in EXPECTED_PAIRWISE.items() if values["register_frames"]}, "eleven register-matched pair edges reproduce pair summary")
    check(sum(int(row["register_matched_all_heads"]) for row in frames) == 9, "nine unique register-matched frames")
    required_frames = {
        ("aiin", "<BOS>", "daiin", frozenset(("p", "s"))),
        ("chedy", "<BOS>", "keedy", frozenset(("p", "s"))),
        ("ol", "<BOS>", "shedy", frozenset(("p", "s"))),
        ("ol", "cheo", "aiin", frozenset(("r", "l"))),
        ("or", "qokeedy", "<EOS>", frozenset(("r", "l"))),
    }
    check(required_frames <= {(row["body"], row["previous"], row["following"], frozenset(split_pipe(row["heads"]))) for row in frames}, "five named exact-neighbor contrasts are present")

    for pair, row in pair_by_name.items():
        check(int(row["same_line_body_locus_cells"]) == same_line_pairs.get(pair, 0), f"same-line artifact closes pair summary {pair}")
        check(int(row["exact_two_sided_frame_cells"]) == frame_pair_edges.get(pair, 0), f"frame artifact closes pair summary {pair}")
        check(int(row["register_matched_frame_cells"]) == register_pair_edges.get(pair, 0), f"register-frame artifact closes pair summary {pair}")

    state = read_tsv(ART / "STATE_BODY_HEAD_GRID.tsv")
    expected_state_order = [(body, head) for body in STATE_BODIES for head in HEAD_ORDER]
    check(len(state) == 40 and [(row["body"], row["head"]) for row in state] == expected_state_order, "complete ordered ten-body by four-head state grid")
    check([row["cell_id"] for row in state] == [f"G635-S{i:02d}" for i in range(1, 41)], "state-grid IDs are exact")
    occupancy_by_body = {row["body"]: row for row in occupancy}
    observed_empty_state: set[tuple[str, str]] = set()
    for row in state:
        body, head = row["body"], row["head"]
        source = occupancy_by_body.get(body)
        source_occ = parse_int_map(source["occurrences_by_head"])[head] if source else 0
        source_exact = parse_int_map(source["reader_exact_by_head"])[head] if source else 0
        check(row["form"] == head + body, f"state cell is literal head+body {head}+{body}")
        check(int(row["occurrences"]) == source_occ and int(row["reader_exact_occurrences"]) == source_exact, f"state cell counts inherit occupancy {head}+{body}")
        check(int(row["attested"]) == int(source_occ > 0), f"state attestation matches occurrence count {head}+{body}")
        check(not GENERIC_FILLER.search(row["working_default_de"]) and row["body_value_de"].strip(), f"state cell has concrete default {head}+{body}")
        if source_occ:
            check(row["status"] == "ATTESTED_CONCRETE_DEFAULT", f"attested state status {head}+{body}")
        else:
            observed_empty_state.add((body, head))
            check(row["status"] == "PREDICTED_EMPTY_CELL" and all(row[field] == "0" for field in ("pages", "loci", "reader_exact_occurrences")), f"empty state cell remains explicit {head}+{body}")
    check(observed_empty_state == EXPECTED_EMPTY_STATE_CELLS, "exact four predicted-empty state cells")
    check(sum(int(row["attested"]) for row in state) == 36, "36 of 40 state cells are attested")

    canonical = read_tsv(ART / "CONCRETE_FOUR_HEAD_PARADIGMS.tsv")
    expected_canonical_order = [(body, head) for body in BODY_VALUES for head in HEAD_ORDER]
    check(len(canonical) == 20 and [(row["body"], row["head"]) for row in canonical] == expected_canonical_order, "complete ordered five-body by four-head concrete paradigm")
    check([row["cell_id"] for row in canonical] == [f"G635-C{i:02d}" for i in range(1, 21)], "canonical cell IDs are exact")
    for row in canonical:
        body, head = row["body"], row["head"]
        source = occupancy_by_body[body]
        check(row["form"] == head + body, f"canonical form is literal {head}+{body}")
        check(row["body_value_de"] == BODY_VALUES[body] and row["head_value_de"] == HEAD_MEANING[head], f"canonical body and head values {head}+{body}")
        check(row["working_default_de"] == CANONICAL_DEFAULTS[body, head], f"canonical concrete gloss {head}+{body}")
        check(int(row["occurrences"]) == CANONICAL_OCCURRENCES[row["form"]] == parse_int_map(source["occurrences_by_head"])[head], f"canonical occurrence count {row['form']}")
        check(int(row["reader_exact_occurrences"]) == parse_int_map(source["reader_exact_by_head"])[head], f"canonical reader-exact count {row['form']}")
        check(int(row["occurrences"]) > 0 and row["status"] == "ATTESTED_COMPLETE_FOUR_HEAD_PARADIGM", f"canonical cell is attested {row['form']}")
        check(row["confidence"] == "LOW_MEDIUM" and row["live_rival_de"].strip(), f"canonical claim remains provisional with rival {row['form']}")
        check(not GENERIC_FILLER.search(row["working_default_de"]), f"canonical gloss has no generic filler {row['form']}")
    check(sum(int(row["occurrences"]) for row in canonical) == 639, "639 canonical-form occurrences")
    check(sum(int(row["reader_exact_occurrences"]) for row in canonical) == 477, "477 reader-exact canonical-form occurrences")

    spans = read_tsv(ART / "MATCHED_SPAN_TRANSLATIONS.tsv")
    check(len(spans) == 10 and set(row["span_id"] for row in spans) == set(EXPECTED_SPANS), "ten exact named matched spans")
    span_tokens = 0
    for row in spans:
        locus, start, end, expected_surfaces = EXPECTED_SPANS[row["span_id"]]
        surfaces = tuple(row["surface_span"].split(" | "))
        glosses = row["token_glosses_de"].split(" | ")
        line = row["zl3b_line"].split()
        check((row["locus"], int(row["start_position"]), int(row["end_position"]), surfaces) == (locus, start, end, expected_surfaces), f"exact span specification {row['span_id']}")
        check(tuple(line[start - 1:end]) == surfaces, f"span replays exact ZL line positions {row['span_id']}")
        check(row["page"] == locus.split(".", 1)[0] and row["page"] in allowed, f"span page is allowed {row['span_id']}")
        check(len(glosses) == len(surfaces) == end - start + 1, f"one concrete gloss per span token {row['span_id']}")
        check(all(gloss.strip() and not GENERIC_FILLER.search(gloss) for gloss in glosses), f"span token glosses have no unknown/generic filler {row['span_id']}")
        check(row["working_translation_de"].strip() and not GENERIC_FILLER.search(row["working_translation_de"]), f"span translation is concrete {row['span_id']}")
        check(row["concrete_inference_de"].strip() and row["reader_evidence_de"].strip(), f"span inference and reader evidence are explicit {row['span_id']}")
        check(row["it2a_line"].strip() and row["rf1b_line"].strip(), f"span keeps all alternate-reader evidence {row['span_id']}")
        check(row["all_target_tokens_reader_exact"] in {"0", "1"} and row["all_target_tokens_split_normalized"] in {"0", "1"}, f"binary reader flags {row['span_id']}")
        check(int(row["all_target_tokens_reader_exact"]) <= int(row["all_target_tokens_split_normalized"]), f"exact implies split-normalized {row['span_id']}")
        check(row["status"] == "COMPLETE_CONCRETE_WORKING_TRANSLATION", f"complete translation status {row['span_id']}")
        span_tokens += len(surfaces)
    check(span_tokens == 22, "all 22 selected span tokens have explicit glosses")
    check(sum(int(row["all_target_tokens_reader_exact"]) for row in spans) == 7, "seven matched spans are all-reader exact")
    check(sum(int(row["all_target_tokens_split_normalized"]) for row in spans) == 8, "eight matched spans are split-normalized")
    span_by_id = {row["span_id"]: row for row in spans}
    check("Typ/Charge III" in span_by_id["PS_CLASS_P"]["token_glosses_de"] and "Dosis/Maß III" in span_by_id["PS_CLASS_P"]["token_glosses_de"], "p aIII/daiin composition correction is visible")
    check("Typ/Charge III" in span_by_id["PS_CLASS_S"]["token_glosses_de"] and "Dosis/Maß III" in span_by_id["PS_CLASS_S"]["token_glosses_de"], "s aIII/daiin composition correction is visible")

    models = {row["model_id"]: row for row in read_tsv(ART / "HEAD_MODEL_COMPARISON.tsv")}
    check(set(models) == {"G634_PRIOR", "EXTRACT_RIVAL", "MATERIA_QUARTET_V12"}, "three explicit head models compared")
    primary_model = models["MATERIA_QUARTET_V12"]
    check({head: primary_model[head] for head in HEAD_ORDER} == HEAD_LATIN, "primary comparison model is pulvis/semen/radix/lignum")
    check(primary_model["status"] == "PRIMARY_WORKING_MODEL", "materia quartet is the primary working model")
    check(models["G634_PRIOR"]["status"].startswith("DEMOTED") and models["EXTRACT_RIVAL"]["status"] == "LIVE_RIVAL", "older salt/liquor readings remain visible as demoted/rival models")

    active_heads = read_tsv(ART / "ACTIVE_HEAD_CODEBOOK_V12.tsv")
    check([row["entry"] for row in active_heads] == list(HEAD_ORDER), "active codebook contains exactly four heads")
    for row in active_heads:
        head = row["entry"]
        profile = profiles_by_head[head]
        check(row["scope"] == "TOKEN_INITIAL_ONLY" and "Rest bleibt sichtbar" in row["composition_rule"], f"active head scope and compositional remainder {head}")
        check(row["latin_stem"] == HEAD_LATIN[head] and row["working_meaning_de"] == HEAD_MEANING[head], f"active head meaning {head}")
        check((row["occurrences"], row["types"], row["pages"]) == (profile["initial_occurrences"], profile["initial_types"], profile["initial_pages"]), f"active head census agrees with profile {head}")
        check(row["status"] == "GDT635_PRIMARY_WORKING_HEAD" and row["live_rival_de"].strip(), f"active head is primary but keeps a rival {head}")

    history = read_tsv(ART / "HISTORICAL_HEAD_MODEL.tsv")
    check(len(history) == 4 and {row["comparator_id"] for row in history} == {"SALZBURG_MI89_PULVIS", "SALZBURG_MI89_SEMEN", "WELLCOME_MS542_LIGNUM", "WELLCOME_MS542_RADIX"}, "four historical head comparators")
    check(all(row["url"].startswith("https://") and row["source_evidence"].strip() and row["analogy_here"].strip() for row in history), "historical rows retain source URL, evidence, and bounded analogy")
    history_text = " ".join(row["source_evidence"].lower() for row in history)
    check(all(stem in history_text for stem in HEAD_LATIN.values()), "historical evidence explicitly contains pulvis, semen, radix, and lignum")
    check(
        all("keine" in row["analogy_here"] or "Analogie" in row["analogy_here"] for row in history),
        "historical rows explicitly mark analogy or reject identification",
    )

    old_dictionary = read_tsv(V11)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V12.tsv")
    check(len(old_dictionary) == 132, "V11 has 132 inherited entries")
    check(len(dictionary) == 156 and len({row["entry"] for row in dictionary}) == 156, "V12 has 156 unique entries")
    old_lines = V11.read_bytes().splitlines(keepends=True)
    new_lines = (ART / "WORKING_DICTIONARY_V12.tsv").read_bytes().splitlines(keepends=True)
    check(new_lines[:len(old_lines)] == old_lines, "V12 preserves the complete V11 byte prefix including header and 132 rows")
    check(dictionary[:132] == old_dictionary, "V12 preserves all V11 rows field-for-field")
    additions = dictionary[132:]
    check(len(additions) == 24 and all("@GDT635_" in row["entry"] for row in additions), "V12 adds exactly 24 scoped GDT635 entries")
    head_entries = {row["entry"].split("@", 1)[0]: row for row in additions if row["kind"] == "SCOPED_INITIAL_MATERIA_HEAD"}
    form_entries = {row["entry"].split("@", 1)[0]: row for row in additions if row["kind"] == "SCOPED_CONCRETE_HEAD_FORM"}
    check(set(head_entries) == set(HEAD_ORDER), "four scoped initial-head dictionary additions")
    check(set(form_entries) == set(CANONICAL_OCCURRENCES), "twenty scoped concrete-form dictionary additions")
    for head, row in head_entries.items():
        check(row["working_meaning_de"] == HEAD_MEANING[head] and row["composition"] == f"{head}+vollständiger Rest", f"dictionary head entry {head}")
        check("tokeninitial" in row["context_rule"] and row["status"] == "NEW_V12_SCOPED_PRIMARY_HEAD", f"dictionary head remains strictly scoped {head}")
    canonical_by_form = {row["form"]: row for row in canonical}
    for form, row in form_entries.items():
        source = canonical_by_form[form]
        check(row["working_meaning_de"] == source["working_default_de"] and row["composition"] == f"{source['head']}+{source['body']}", f"dictionary concrete form {form}")
        check(row["status"] == "NEW_V12_ATTESTED_CONCRETE_DEFAULT" and not GENERIC_FILLER.search(row["working_meaning_de"]), f"dictionary form has attested concrete default {form}")

    expected_remainder = {
        "bodies": 760, "head_body_types": 985, "headed_occurrences": 2860,
        "occupancy_body_counts": {"1": 616, "2": 87, "3": 33, "4": 24},
        "occupancy_occurrence_counts": {"1": 883, "2": 451, "3": 360, "4": 1166},
        "shared_bodies": 144, "shared_headed_occurrences": 1977,
        "shared_with_bare_body": 140, "shared_with_exact_v11_body": 22,
        "four_way_bodies": 24, "four_way_occurrences": 1166,
    }
    check(result["remainder_atlas"] == expected_remainder, "result remainder-atlas summary")
    check(result["pairwise"] == EXPECTED_PAIRWISE, "result pairwise summary")
    check(result["context"] == {
        "same_line_cells": 12, "unique_exact_frames": 18,
        "pairwise_exact_frame_edges": 20, "register_matched_frames": 9,
        "pairwise_register_edges": 11,
    }, "result local-context summary")
    check(result["concrete_model"] == {
        "primary": HEAD_LATIN, "canonical_bodies": list(BODY_VALUES),
        "canonical_cells": 20, "canonical_occurrences": 639, "canonical_reader_exact": 477,
        "state_grid_cells": 40, "state_grid_attested": 36,
        "matched_spans": 10, "matched_span_tokens": 22,
        "matched_spans_all_reader_exact": 7, "matched_spans_split_normalized": 8,
        "resolved_composition_corrections": 2, "unresolved_material_conflicts": 0,
        "two_axis_aIII_daiin": "headed aIII=Typ/Charge III; d+aIII=Dosis/Maß III",
    }, "result concrete-model summary")
    check(result["working_dictionary"] == {
        "entries": 156, "inherited_v11_entries": 132,
        "new_scoped_head_entries": 4, "new_scoped_form_entries": 20,
        "inherited_prefix_rows_preserved": 132,
    }, "result dictionary summary")
    for head in HEAD_ORDER:
        summary = result["initial_heads"][head]
        profile = profiles_by_head[head]
        check(summary["latin"] == HEAD_LATIN[head] and summary["meaning"] == HEAD_MEANING[head], f"result head identity {head}")
        check((summary["occurrences"], summary["types"], summary["pages"], summary["reader_exact"]) == tuple(int(profile[field]) for field in ("initial_occurrences", "initial_types", "initial_pages", "initial_reader_exact_occurrences")), f"result head census {head}")
        check(summary["line_positions"] == [int(profile[field]) for field in ("line_first", "line_middle", "line_last")], f"result head positions {head}")
    claim = result["claim_boundary"]
    check(all(text in claim for text in ("760 remainder bodies", "144 are shared", "24 occur under all four heads", "p=pulvis", "s=semen", "r=radix", "l=lignum")), "claim boundary names exact empirical base and primary model")
    check("do not prove" in claim and "not a solved language" in claim and "replaceable working theory" in claim, "claim boundary keeps historical analogy and translation provisional")

    payload_core = {
        "schema": "GDT635_VALIDATION_V1", "experiment_id": "GDT635", "status": "PASS",
        "check_count": len(checks), "checks": checks, "byte_replay_artifacts": len(GENERATED),
        "guard": {"allowed_pages": 179, "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "heads": {head: {"occurrences": HEAD_COUNTS[head][0], "types": HEAD_COUNTS[head][1]} for head in HEAD_ORDER},
        "remainder": {"bodies": 760, "shared": 144, "four_way": 24, "occupancy": {"1": 616, "2": 87, "3": 33, "4": 24}},
        "context": {"same_line": 12, "exact_frames": 18, "pair_edges": 20, "register_frames": 9},
        "concrete": {"canonical_cells": 20, "matched_spans": 10, "matched_span_tokens": 22, "unresolved_material_conflicts": 0},
        "dictionary": {"v11_preserved": 132, "v12_entries": 156},
        "result_sha256": sha256(RESULT),
    }
    payload = {**payload_core, "content_sha256": canonical_hash(payload_core)}
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
