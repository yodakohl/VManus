#!/usr/bin/env python3
"""Independently validate and byte-replay GDT637."""

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
BASE_REL = Path("experiments/yolo/gdt637_ladder_completion_one_unknown_passages")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V13 = ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/WORKING_DICTIONARY_V13.tsv"
INHERITED_ALLOW = ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/PAGE_ALLOWLIST.tsv"

TSV_NAMES = (
    "PAGE_ALLOWLIST.tsv", "LADDER_16_HEAD_CELL_GRID.tsv", "LADDER_OCCURRENCE_CONTEXTS.tsv",
    "LADDER_CONTEXT_TRANSFER.tsv", "LADDER_BODY_CONTRASTS.tsv", "V14_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE.tsv", "ONE_UNKNOWN_PASSAGE_RANKING.tsv",
    "STRICT_ONE_UNKNOWN_PASSAGES.tsv", "PROPOSED_UNKNOWN_DEFAULTS.tsv",
    "COMPLETE_PASSAGE_CANDIDATES.tsv", "WORKING_DICTIONARY_V14.tsv",
)
GENERATED = tuple(ART / name for name in TSV_NAMES) + (RESULT,)
HEAD_ORDER = ("p", "s", "r", "l")
TARGET_ORDER = ("aiir", "oiiin", "aim", "aiim")
EXPECTED_CELLS = {
    "paiir": (2, 2, 1, 1, 0), "saiir": (1, 0, 1, 0, 0),
    "raiir": (1, 0, 0, 1, 0), "laiir": (0, 0, 0, 0, 0),
    "poiiin": (0, 0, 0, 0, 0), "soiiin": (3, 3, 2, 1, 0),
    "roiiin": (1, 0, 0, 0, 1), "loiiin": (1, 1, 0, 1, 0),
    "paim": (0, 0, 0, 0, 0), "saim": (2, 1, 0, 1, 1),
    "raim": (0, 0, 0, 0, 0), "laim": (0, 0, 0, 0, 0),
    "paiim": (0, 0, 0, 0, 0), "saiim": (1, 1, 0, 0, 1),
    "raiim": (0, 0, 0, 0, 0), "laiim": (0, 0, 0, 0, 0),
}
EXPECTED_CONTRASTS = {
    ("ar", "aiir"): (5, 5), ("air", "aiir"): (1, 0),
    ("aiir", "aim"): (1, 0), ("aiim", "am"): (1, 1),
}
ALLOWED_STATES = {
    "KNOWN_EXACT_WHOLE", "KNOWN_CONTEXT_LICENSED", "AMBIGUOUS_ACTIVE_RIVAL",
    "UNKNOWN_SURFACE", "READER_BOUNDARY_UNSTABLE",
}
GENERIC_FILLER = re.compile(
    r"Arbeitsgut|Arbeitsschritt|Arbeitsmaterial|ausf(?:ü|ue)hren|weiterleit|"
    r"leite\s+weiter|\b(?:arbeite|prozessiere|verarbeite)\b|nimm\s+Werkzeug|"
    r"bring\s+das\s+Produkt|noch\s+unbestimmt",
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


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(VALIDATION not in GENERATED, "validation excluded from replay")
    check(len(GENERATED) == 13 and len(set(GENERATED)) == 13, "thirteen unique builder outputs")
    check(all(path.is_file() for path in GENERATED), "all builder outputs exist")
    before = {path: path.read_bytes() for path in GENERATED}
    replay = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    check(replay.returncode == 0, "builder exits zero")
    check(
        replay.stdout.strip() == "GDT637 built: cells=16 attested=8 occurrences=12 glossary=212 complete=16 one_unknown=65 strict=30",
        "builder summary exact",
    )
    for path in GENERATED:
        check(path.read_bytes() == before[path], f"byte replay {path.name}")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT637_LADDER_COMPLETION_ONE_UNKNOWN_PASSAGES_RESULT_V1", "result schema")
    check(result["experiment_id"] == "GDT637", "experiment id")
    check(result["status"] == "EIGHT_ATTESTED_LADDER_CELLS_ADDED__ONE_UNKNOWN_PASSAGES_RANKED", "result status")
    core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(result["content_sha256"] == canonical_hash(core), "canonical result hash")
    guard = result["guard"]
    check(guard["allowed_pages"] == 179 and guard["new_pages"] == guard["new_images"] == 0, "unchanged 179-page scope")
    check(guard["f1r"] == "EXCLUDED", "f1r excluded")
    check(guard["f84"] == guard["f84r"] == "FORBIDDEN", "f84 family forbidden")
    source = RUN.read_text(encoding="utf-8")
    check(source.count("guarded_query(") == 2, "two guarded source projections")
    check("read_tsv(ROOT / TOKENS_REL)" not in source and "read_tsv(ROOT / CROSS_REL)" not in source,
          "mixed transcription not parsed directly")

    expected_outputs = {str(BASE_REL / "artifacts" / name) for name in TSV_NAMES}
    check(set(result["outputs"]) == expected_outputs, "result binds every evidence TSV")
    for path, digest in sorted(result["inputs"].items()):
        check((ROOT / path).is_file(), f"input exists {path}")
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    for path, digest in sorted(result["outputs"].items()):
        check((ROOT / path).is_file(), f"output exists {path}")
        check(sha256(ROOT / path) == digest, f"output hash {path}")

    allow = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = [row["page"] for row in allow]
    check(len(pages) == len(set(pages)) == 179, "179 unique allowed pages")
    check(pages == sorted(pages), "allowlist sorted")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == INHERITED_ALLOW.read_bytes(), "allowlist inherited byte-identically")
    check("f1r" not in pages and all(not page.startswith("f84") for page in pages), "protected pages absent")

    grid = read_tsv(ART / "LADDER_16_HEAD_CELL_GRID.tsv")
    check(len(grid) == 16 and len({row["cell_id"] for row in grid}) == 16, "sixteen unique ladder cells")
    check([row["body"] for row in grid[::4]] == list(TARGET_ORDER), "target body order")
    check([row["head"] for row in grid[:4]] == list(HEAD_ORDER), "head order")
    by_form = {row["form"]: row for row in grid}
    check(set(by_form) == set(EXPECTED_CELLS), "exact target form set")
    for form, expected in EXPECTED_CELLS.items():
        row = by_form[form]
        actual = tuple(int(row[key]) for key in (
            "occurrences", "reader_exact_occurrences", "line_first", "line_middle", "line_last",
        ))
        check(actual == expected, f"cell census {form}")
        check(sum(actual[2:]) == actual[0], f"cell positions {form}")
        check(bool(row["working_default_de"]), f"cell meaning {form}")
        check(not GENERIC_FILLER.search(row["working_default_de"]), f"no generic filler {form}")
        expected_status = "ATTESTED_SCOPED_LADDER_DEFAULT" if actual[0] else "PREDICTED_UNATTESTED_CELL"
        check(row["status"] == expected_status, f"cell status {form}")
    check(sum(int(row["occurrences"]) for row in grid) == 12, "twelve target occurrences")
    check(sum(int(row["reader_exact_occurrences"]) for row in grid) == 8, "eight reader-exact target occurrences")

    contexts = read_tsv(ART / "LADDER_OCCURRENCE_CONTEXTS.tsv")
    check(len(contexts) == 12 and len({row["context_id"] for row in contexts}) == 12, "twelve target contexts")
    counts = Counter(row["form"] for row in contexts)
    for form, row in by_form.items():
        check(counts[form] == int(row["occurrences"]), f"context count {form}")
    for row in contexts:
        tokens = row["zl3b_line"].split()
        ordinal = int(row["token_ordinal"])
        check(tokens[ordinal - 1] == row["form"], f"context alignment {row['context_id']}")
        position = "FIRST" if ordinal == 1 else "LAST" if ordinal == len(tokens) else "MIDDLE"
        check(row["line_position"] == position, f"context position {row['context_id']}")
        if row["body"] in {"aim", "aiim"}:
            check(("Eintrag abgeschlossen" in row["working_default_de"]) == (position == "LAST"),
                  f"unit closure terminal only {row['context_id']}")

    transfer = read_tsv(ART / "LADDER_CONTEXT_TRANSFER.tsv")
    check(len(transfer) == 16 and {row["form"] for row in transfer} == set(EXPECTED_CELLS), "sixteen transfer rows")
    check(all(int(row["exact_shared_neighbor_frames"]) == 0 for row in transfer), "no invented exact-frame support")
    check(sum(row["status"] == "ATTESTED_TRANSFER" for row in transfer) == 8, "eight attested transfers")

    contrasts = read_tsv(ART / "LADDER_BODY_CONTRASTS.tsv")
    check(len(contrasts) == 4, "four body contrasts")
    for row in contrasts:
        pair = (row["left_surface"], row["right_surface"])
        check(pair in EXPECTED_CONTRASTS, f"registered contrast {pair}")
        check((int(row["shared_lines"]), int(row["reader_exact_shared_lines"])) == EXPECTED_CONTRASTS[pair],
              f"contrast census {pair}")
        check(row["left_surface"] != row["right_surface"], f"contrast distinct {pair}")

    glossary = read_tsv(ART / "V14_EXACT_TOKEN_GLOSSARY.tsv")
    check(len(glossary) == len({row["surface"] for row in glossary}) == 212, "212 unique exact glossary surfaces")
    check({row["scope_state"] for row in glossary} <= ALLOWED_STATES, "glossary states registered")
    check(sum(row["scope_state"] == "AMBIGUOUS_ACTIVE_RIVAL" for row in glossary) == 2, "two explicit ambiguous carriers")
    check(all("SCOPED_RESIDUAL_BODY_DEFAULT" not in row["source"] for row in glossary), "no bare residual globalization")
    check(all(row["surface"] not in {"ar", "air", "aiir", "oiiin", "aim", "aiim"} for row in glossary),
          "bare target bodies absent from exact glossary")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE.tsv")
    check(len(coverage) == len({row["locus"] for row in coverage}) == 4128, "4128 unique physical lines")
    coverage_by_locus = {row["locus"]: row for row in coverage}
    for row in coverage:
        count = int(row["token_count"])
        known, unknown = int(row["known_tokens"]), int(row["unknown_tokens"])
        check(known + unknown == count, f"coverage partition {row['locus']}")
        check(len(row["zl3b_line"].split()) == count, f"line token count {row['locus']}")
        check(len(row["token_glosses_de"].split(" | ")) == count, f"gloss count {row['locus']}")
        states = row["scope_states"].split(" | ")
        check(len(states) == count and set(states) <= ALLOWED_STATES, f"scope states {row['locus']}")
        check(states.count("UNKNOWN_SURFACE") == unknown, f"unknown state count {row['locus']}")
        check(states.count("READER_BOUNDARY_UNSTABLE") == int(row["reader_unstable_tokens"]),
              f"reader state count {row['locus']}")
        check(abs(float(row["coverage_fraction"]) - known / count) < 0.000001, f"coverage fraction {row['locus']}")
        check(row["page"] in pages, f"coverage page allowed {row['locus']}")

    one_unknown = read_tsv(ART / "ONE_UNKNOWN_PASSAGE_RANKING.tsv")
    check(len(one_unknown) == 65, "65 one-unknown lines")
    check([int(row["rank"]) for row in one_unknown] == list(range(1, 66)), "exploratory ranks consecutive")
    check(len({row["locus"] for row in one_unknown}) == 65, "one-unknown loci unique")
    for row in one_unknown:
        base = coverage_by_locus[row["locus"]]
        check(int(base["unknown_tokens"]) == int(row["unknown_tokens"]) == 1, f"one unknown {row['locus']}")
        ordinal = int(row["unknown_ordinal"])
        check(base["zl3b_line"].split()[ordinal - 1] == row["unknown_surface"], f"unknown alignment {row['locus']}")
        check(bool(row["proposed_default_de"] and row["proposal_basis"]), f"proposal fields {row['locus']}")
        check(not GENERIC_FILLER.search(row["proposed_default_de"]), f"no generic proposal {row['locus']}")
        if row["proposal_strength"] == "OPEN":
            check("ungeklärt" in row["proposed_default_de"], f"open proposal explicit {row['locus']}")
        else:
            check("ungeklärt" not in row["proposed_default_de"], f"composed proposal concrete {row['locus']}")
    check(one_unknown[0]["locus"] == "f79v.4" and one_unknown[0]["unknown_surface"] == "qoky",
          "top exploratory passage fixed")

    strict = read_tsv(ART / "STRICT_ONE_UNKNOWN_PASSAGES.tsv")
    check(len(strict) == 30, "thirty strict one-unknown lines")
    check([int(row["rank"]) for row in strict] == list(range(1, 31)), "strict ranks consecutive")
    check({row["locus"] for row in strict} <= {row["locus"] for row in one_unknown}, "strict subset")
    for row in strict:
        check(row["strict_eligible"] == "1", f"strict flag {row['locus']}")
        check(int(row["ambiguous_tokens"]) == int(row["reader_unstable_tokens"]) == 0,
              f"strict state clean {row['locus']}")
        check(row["all_present_exact"] == "1", f"strict reader exact line {row['locus']}")
    check(strict[0]["locus"] == "f4r.3" and strict[0]["unknown_surface"] == "otchol", "top strict passage fixed")

    proposals = read_tsv(ART / "PROPOSED_UNKNOWN_DEFAULTS.tsv")
    check(len(proposals) == len({row["surface"] for row in proposals}) == 64, "64 unique unknown proposals")
    check(sum(int(row["candidate_lines"]) for row in proposals) == 65, "proposal rows cover all one-unknown lines")
    check(all(row["status"] == "WORKSHEET_PROPOSAL_NOT_IN_V14" for row in proposals), "proposals excluded from V14")
    proposed_by_surface = {row["surface"]: row for row in proposals}
    expected_manual = {
        "otchol": "kalt-trockenes Zubereitungsmaterial", "keechy": "heiß gebundene Trockenform II",
        "cthoiin": "Blatt-/Krautzubereitung, Form III", "qotchol": "kalt-trockenes Material",
        "cthor": "Blatt-/Krautportion", "choiin": "Trockenansatz, Form III",
        "dol": "abgemessenes Material", "doiin": "Dosis der Zubereitungsform III",
        "oaiir": "Zubereitungs-Teilklasse III", "kcho": "heiß-trockener Ansatz",
    }
    for surface, meaning in expected_manual.items():
        check(proposed_by_surface[surface]["proposed_default_de"] == meaning, f"manual proposal {surface}")

    complete = read_tsv(ART / "COMPLETE_PASSAGE_CANDIDATES.tsv")
    check(len(complete) == 16 and sum(int(row["strict_complete"]) for row in complete) == 7,
          "sixteen complete and seven strict complete lines")
    check([int(row["rank"]) for row in complete] == list(range(1, 17)), "complete ranks consecutive")
    for row in complete:
        check(int(row["unknown_tokens"]) == 0 and int(row["known_tokens"]) == int(row["token_count"]),
              f"complete coverage {row['locus']}")
        check(not re.search(r"\[[a-z]+:\?\]", row["working_translation_de"]),
              f"complete no open marker {row['locus']}")
    check(complete[0]["locus"] == "f20v.10", "top strict complete line fixed")

    old_dictionary = read_tsv(V13)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V14.tsv")
    check(len(old_dictionary) == 251 and len(dictionary) == 259, "V13 and V14 sizes")
    for index, old_row in enumerate(old_dictionary):
        check(dictionary[index] == old_row, f"V13 prefix preserved row {index + 1}")
    tail = dictionary[251:]
    check(len(tail) == 8 and all(row["kind"] == "SCOPED_LADDER_HEAD_FORM" for row in tail), "eight scoped V14 rows")
    attested_forms = {row["form"] for row in grid if int(row["occurrences"]) > 0}
    predicted_forms = {row["form"] for row in grid if int(row["occurrences"]) == 0}
    dictionary_forms = {row["entry"].split("@", 1)[0] for row in tail}
    check(dictionary_forms == attested_forms, "only attested ladder forms added")
    check(not (dictionary_forms & predicted_forms), "predicted empty cells excluded")
    unit_rows = [row for row in tail if row["entry"].split("@", 1)[0] in {"saim", "saiim"}]
    check(all("only line-final" in row["context_rule"] for row in unit_rows), "unit closure scoped line-final")

    ladder = result["ladder_completion"]
    check((ladder["candidate_cells"], ladder["attested_cells"], ladder["predicted_unattested_cells"]) == (16, 8, 8),
          "result ladder cells")
    check((ladder["attested_occurrences"], ladder["reader_exact_occurrences"]) == (12, 8), "result ladder tokens")
    passages = result["passage_coverage"]
    check((passages["physical_lines"], passages["one_unknown_lines"], passages["strict_one_unknown_lines"]) == (4128, 65, 30),
          "result passage census")
    check((passages["complete_multi_token_lines"], passages["exact_glossary_surfaces"]) == (16, 212),
          "result complete and glossary census")
    check(result["working_dictionary"]["entries"] == 259, "result dictionary size")

    validation_core = {
        "schema": "GDT637_VALIDATION_V1", "experiment_id": "GDT637", "status": "PASS",
        "checks": len(checks), "builder_outputs_replayed": len(GENERATED),
        "candidate_cells": 16, "attested_cells": 8, "attested_occurrences": 12,
        "reader_exact_occurrences": 8, "physical_lines": 4128,
        "complete_multi_token_lines": 16, "one_unknown_lines": 65,
        "strict_one_unknown_lines": 30, "dictionary_entries": 259,
        "validated_claim": (
            "Four visible minim ladders yield eight observed scoped head forms and eight explicit empty predictions. "
            "The V13/V14 surface reader publishes scope- and reader-aware coverage for all 4,128 physical lines, "
            "including complete and exactly-one-unknown passage queues without promoting worksheet proposals."
        ),
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT637 validation PASS: {len(checks)} checks, {len(GENERATED)} outputs replayed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
