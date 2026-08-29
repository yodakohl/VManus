#!/usr/bin/env python3
"""Independently validate and byte-replay GDT636."""

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
BASE_REL = Path("experiments/yolo/gdt636_residual_four_head_semantics")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V12 = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/WORKING_DICTIONARY_V12.tsv"
INHERITED_ALLOW = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv"

TSV_NAMES = (
    "PAGE_ALLOWLIST.tsv", "SLOT_COMPOSITION_MODEL.tsv", "MINIM_LADDER_EVIDENCE.tsv",
    "RESIDUAL_BODY_DEFAULTS.tsv", "RESIDUAL_76_FORM_GRID.tsv", "RESIDUAL_BODY_POSITION_PROFILE.tsv",
    "RESIDUAL_OCCURRENCE_CONTEXTS.tsv", "CONTRASTIVE_BODY_COEXISTENCE.tsv",
    "EXACT_RESIDUAL_NEIGHBOR_SWAPS.tsv", "CONCRETE_RESIDUAL_SPAN_TRANSLATIONS.tsv",
    "HISTORICAL_COMPOSITION_COMPARATORS.tsv", "WORKING_DICTIONARY_V13.tsv",
)
GENERATED = tuple(ART / name for name in TSV_NAMES) + (RESULT,)
HEAD_ORDER = ("p", "s", "r", "l")
RESIDUAL_ORDER = (
    "ar", "chey", "al", "y", "air", "chdy", "oiin", "shey", "am", "cheey",
    "chy", "olchedy", "chol", "odaiin", "oraiin", "ody", "cheo", "oaiin", "oral",
)
EXPECTED_COUNTS = {
    "ar": ((6, 62, 14, 8), (4, 45, 11, 5), 321),
    "chey": ((8, 5, 8, 46), (6, 4, 5, 37), 314),
    "al": ((2, 37, 16, 6), (2, 33, 12, 6), 204),
    "y": ((3, 28, 10, 12), (1, 26, 8, 12), 270),
    "air": ((4, 22, 4, 1), (2, 16, 3, 1), 56),
    "chdy": ((10, 2, 1, 18), (6, 1, 0, 14), 133),
    "oiin": ((2, 15, 4, 4), (1, 12, 3, 1), 26),
    "shey": ((1, 5, 2, 17), (0, 4, 1, 14), 232),
    "am": ((1, 7, 11, 5), (0, 4, 9, 3), 67),
    "cheey": ((3, 1, 5, 13), (3, 0, 4, 10), 158),
    "chy": ((2, 2, 3, 8), (1, 2, 2, 7), 162),
    "olchedy": ((7, 6, 1, 1), (3, 2, 0, 0), 34),
    "chol": ((5, 3, 1, 3), (5, 3, 0, 3), 343),
    "odaiin": ((4, 3, 2, 3), (4, 2, 1, 2), 55),
    "oraiin": ((2, 8, 1, 1), (2, 6, 0, 0), 26),
    "ody": ((2, 4, 2, 3), (1, 4, 2, 3), 37),
    "cheo": ((3, 2, 1, 3), (2, 1, 0, 3), 54),
    "oaiin": ((1, 3, 1, 1), (0, 2, 0, 1), 22),
    "oral": ((1, 3, 1, 1), (0, 3, 1, 1), 10),
}
EXPECTED_LADDERS = {
    "AR_PART": (("ar", 321, 90), ("air", 56, 31), ("aiir", 20, 4), ("aiiir", 0, 0)),
    "ON_PREPARATION": (("on", 1, 0), ("oin", 7, 5), ("oiin", 26, 25), ("oiiin", 11, 5)),
    "AM_MEASURE_CLOSE": (("am", 67, 24), ("aim", 5, 2), ("aiim", 1, 1), ("aiiim", 0, 0)),
}
EXPECTED_COEXISTENCE = {
    ("ar", "or"): 48, ("al", "ol"): 20, ("chey", "cheey"): 15,
    ("chy", "chdy"): 7, ("chdy", "chedy"): 24, ("shey", "shedy"): 39,
}
GENERIC_FILLER = re.compile(
    r"Arbeitsgut|Arbeitsschritt|Arbeitsmaterial|ausf(?:ü|ue)hren|weiterleit|"
    r"leite\s+weiter|\b(?:arbeite|prozessiere|verarbeite)\b|nimm\s+Werkzeug|"
    r"bring\s+das\s+Produkt|noch\s+keine\s+konkrete|unbestimmt",
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


def parse_head_map(value: str) -> dict[str, int]:
    return {item.split(":", 1)[0]: int(item.split(":", 1)[1]) for item in value.split("|")}


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(VALIDATION not in GENERATED, "validation excluded from replay set")
    check(len(GENERATED) == 13 and len(set(GENERATED)) == 13, "thirteen unique builder outputs")
    check(all(path.is_file() for path in GENERATED), "all builder outputs exist")
    before = {path: path.read_bytes() for path in GENERATED}
    replay = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    check(replay.returncode == 0, "builder exits zero")
    check(
        replay.stdout.strip() == "GDT636 built: bodies=19 forms=76 occurrences=527 exact=398 frames=2 spans=14 dictionary=251",
        "builder summary exact",
    )
    for path in GENERATED:
        check(path.read_bytes() == before[path], f"byte replay {path.name}")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT636_RESIDUAL_FOUR_HEAD_SEMANTICS_RESULT_V1", "result schema")
    check(result["experiment_id"] == "GDT636", "experiment id")
    check(result["status"] == "ALL_19_RESIDUAL_BODIES_HAVE_SCOPED_COMPOSITIONAL_DEFAULTS", "result status")
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(result["content_sha256"] == canonical_hash(result_core), "canonical result hash")
    check(result["guard"]["allowed_pages"] == 179, "179 guarded pages")
    check(result["guard"]["f1r"] == "EXCLUDED", "f1r excluded")
    check(result["guard"]["f84"] == "FORBIDDEN" and result["guard"]["f84r"] == "FORBIDDEN", "f84 family forbidden")
    check(result["guard"]["new_pages"] == 0 and result["guard"]["new_images"] == 0, "no new page or image")
    run_source = RUN.read_text(encoding="utf-8")
    check(run_source.count("guarded_query(") == 2, "two guarded source projections")
    check("read_tsv(ROOT / TOKENS_REL)" not in run_source and "read_tsv(ROOT / CROSS_REL)" not in run_source,
          "mixed transcription never parsed directly")

    expected_outputs = {str(BASE_REL / "artifacts" / name) for name in TSV_NAMES}
    check(set(result["outputs"]) == expected_outputs, "result binds every evidence TSV")
    for path, digest in sorted(result["inputs"].items()):
        check((ROOT / path).is_file(), f"input exists {path}")
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    for path, digest in sorted(result["outputs"].items()):
        check((ROOT / path).is_file(), f"output exists {path}")
        check(sha256(ROOT / path) == digest, f"output hash {path}")

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    allow_pages = [row["page"] for row in allow_rows]
    check(len(allow_pages) == len(set(allow_pages)) == 179, "allowlist unique")
    check(allow_pages == sorted(allow_pages), "allowlist sorted")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == INHERITED_ALLOW.read_bytes(), "allowlist inherited byte-identically")
    check("f1r" not in allow_pages and all(not page.startswith("f84") for page in allow_pages), "protected pages absent")

    slots = read_tsv(ART / "SLOT_COMPOSITION_MODEL.tsv")
    check(len(slots) == 15 and len({row["slot"] for row in slots}) == 15, "fifteen unique scoped slots")
    for row in slots:
        check(row["working_value_de"] != "" and row["scope_rule"] != "", f"slot concrete {row['slot']}")

    defaults = read_tsv(ART / "RESIDUAL_BODY_DEFAULTS.tsv")
    check([row["body"] for row in defaults] == list(RESIDUAL_ORDER), "nineteen residual bodies in fixed order")
    check(len({row["working_default_de"] for row in defaults}) == 19, "nineteen non-collapsed body labels")
    for row in defaults:
        body = row["body"]
        occurrences, exact, bare = EXPECTED_COUNTS[body]
        check(parse_head_map(row["occurrences_by_head"]) == dict(zip(HEAD_ORDER, occurrences)), f"head counts {body}")
        check(int(row["total_headed_occurrences"]) == sum(occurrences), f"headed total {body}")
        check(int(row["reader_exact_occurrences"]) == sum(exact), f"reader exact {body}")
        check(int(row["bare_body_occurrences"]) == bare, f"bare count {body}")
        check(row["components"] and row["working_default_de"] and row["semantic_family"], f"concrete fields {body}")
        check(not GENERIC_FILLER.search(row["working_default_de"]), f"no generic filler {body}")
        check("bare body is not globalized" in row["scope_rule"], f"scoped body {body}")

    grid = read_tsv(ART / "RESIDUAL_76_FORM_GRID.tsv")
    check(len(grid) == 76 and len({row["cell_id"] for row in grid}) == 76, "seventy-six unique cells")
    check(len({row["form"] for row in grid}) == 76, "seventy-six unique forms")
    grid_by_form = {row["form"]: row for row in grid}
    for body in RESIDUAL_ORDER:
        occurrences, exact, _ = EXPECTED_COUNTS[body]
        for index, head in enumerate(HEAD_ORDER):
            form = head + body
            row = grid_by_form[form]
            check(row["body"] == body and row["head"] == head, f"cell decomposition {form}")
            check(int(row["occurrences"]) == occurrences[index], f"cell count {form}")
            check(int(row["reader_exact_occurrences"]) == exact[index], f"cell exact {form}")
            check(sum(int(row[key]) for key in ("line_first", "line_middle", "line_last")) == occurrences[index],
                  f"cell positions {form}")
            check(row["working_default_de"] and not GENERIC_FILLER.search(row["working_default_de"]),
                  f"concrete form {form}")

    contexts = read_tsv(ART / "RESIDUAL_OCCURRENCE_CONTEXTS.tsv")
    check(len(contexts) == 527 and len({row["context_id"] for row in contexts}) == 527, "527 unique occurrence contexts")
    context_counts = Counter(row["form"] for row in contexts)
    for form, row in grid_by_form.items():
        check(context_counts[form] == int(row["occurrences"]), f"context count {form}")
    for row in contexts:
        tokens = row["zl3b_line"].split()
        ordinal = int(row["token_ordinal"])
        check(tokens[ordinal - 1] == row["form"], f"context target {row['context_id']}")
        check(row["page"] in allow_pages, f"context allowed {row['context_id']}")
        expected_position = "FIRST" if ordinal == 1 else "LAST" if ordinal == len(tokens) else "MIDDLE"
        check(row["line_position"] == expected_position, f"context position {row['context_id']}")
        if row["body"] == "am":
            check(("Eintrag abgeschlossen" in row["working_default_de"]) == (expected_position == "LAST"),
                  f"am closure is terminal only {row['context_id']}")

    position = read_tsv(ART / "RESIDUAL_BODY_POSITION_PROFILE.tsv")
    check(len(position) == 20 and position[-1]["body"] == "ALL_19", "nineteen profiles plus aggregate")
    aggregate = position[-1]
    check((int(aggregate["ps_occurrences"]), int(aggregate["ps_line_first"])) == (285, 128), "p/s aggregate placement")
    check((int(aggregate["rl_occurrences"]), int(aggregate["rl_line_first"])) == (242, 16), "r/l aggregate placement")
    check(int(aggregate["rl_line_middle"]) + int(aggregate["rl_line_last"]) == 226, "r/l internal or final")

    ladders = read_tsv(ART / "MINIM_LADDER_EVIDENCE.tsv")
    check(len(ladders) == 12, "twelve ladder cells")
    by_ladder: dict[str, list[dict[str, str]]] = {}
    for ladder_id in EXPECTED_LADDERS:
        by_ladder[ladder_id] = [row for row in ladders if row["ladder_id"] == ladder_id]
    for ladder_id, expected in EXPECTED_LADDERS.items():
        check(len(by_ladder[ladder_id]) == 4, f"four stages {ladder_id}")
        for row, (body, bare, headed) in zip(by_ladder[ladder_id], expected):
            check((row["body"], int(row["bare_occurrences"]), int(row["headed_occurrences"])) == (body, bare, headed),
                  f"ladder population {ladder_id} {body}")
    check({int(row["lines_with_two_or_more_bare_stages"]) for row in by_ladder["AR_PART"]} == {13}, "thirteen AR multi-stage lines")

    coexistence = read_tsv(ART / "CONTRASTIVE_BODY_COEXISTENCE.tsv")
    check(len(coexistence) == 6, "six contrastive coexistence rows")
    for row in coexistence:
        pair = (row["left_body"], row["right_body"])
        check(int(row["shared_lines"]) == EXPECTED_COEXISTENCE[pair], f"coexistence {pair[0]} {pair[1]}")
        check(row["left_working_value_de"] != row["right_working_value_de"], f"distinct coexisting values {pair[0]} {pair[1]}")

    frames = read_tsv(ART / "EXACT_RESIDUAL_NEIGHBOR_SWAPS.tsv")
    check(len(frames) == 2 and {row["body"] for row in frames} == {"ar"}, "only ar has two exact residual neighbor frames")
    check({(row["previous"], row["following"]) for row in frames} == {("<BOS>", "or"), ("<BOS>", "shey")}, "two exact ar frames")

    spans = read_tsv(ART / "CONCRETE_RESIDUAL_SPAN_TRANSLATIONS.tsv")
    check(len(spans) == 14 and len({row["span_id"] for row in spans}) == 14, "fourteen unique concrete spans")
    check(sum(int(row["end_position"]) - int(row["start_position"]) + 1 for row in spans) == 42, "forty-two translated span tokens")
    check(sum(int(row["all_target_tokens_reader_exact"]) for row in spans) == 9, "nine all-reader-exact spans")
    for row in spans:
        selected = row["zl3b_line"].split()[int(row["start_position"]) - 1:int(row["end_position"])]
        check(" | ".join(selected) == row["surface_span"], f"span alignment {row['span_id']}")
        check(row["working_translation_de"] and not GENERIC_FILLER.search(row["working_translation_de"]),
              f"concrete span {row['span_id']}")

    history = read_tsv(ART / "HISTORICAL_COMPOSITION_COMPARATORS.tsv")
    check(len(history) == 4 and len({row["url"] for row in history}) == 4, "four historical comparators")
    check(all(row["url"].startswith("https://") for row in history), "historical links HTTPS")

    old_dictionary = read_tsv(V12)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V13.tsv")
    check(len(old_dictionary) == 156 and len(dictionary) == 251, "V12 and V13 dictionary sizes")
    for index, old_row in enumerate(old_dictionary):
        check(dictionary[index] == old_row, f"V12 prefix preserved row {index + 1}")
    tail = dictionary[156:]
    check(len(tail) == 95, "ninety-five scoped V13 additions")
    check(sum(row["kind"] == "SCOPED_RESIDUAL_BODY_DEFAULT" for row in tail) == 19, "nineteen body dictionary rows")
    check(sum(row["kind"] == "SCOPED_RESIDUAL_HEAD_FORM" for row in tail) == 76, "seventy-six form dictionary rows")
    check(all("@GDT636_" in row["entry"] for row in tail), "all additions explicitly scoped")
    am_form_rows = [row for row in tail if row["kind"] == "SCOPED_RESIDUAL_HEAD_FORM" and "+am" in row["composition"]]
    check(len(am_form_rows) == 4, "four scoped am head forms")
    check(all("Eintrag abgeschlossen" not in row["working_meaning_de"] for row in am_form_rows),
          "am form defaults do not globalize terminal closure")
    check(all("only line-final" in row["context_rule"] for row in am_form_rows),
          "am dictionary rules carry terminal-only closure")

    check(result["residual_grid"]["headed_occurrences"] == 527, "result headed occurrence count")
    check(result["residual_grid"]["reader_exact_occurrences"] == 398, "result reader-exact count")
    check(result["residual_grid"]["bare_body_occurrences"] == 2524, "result bare occurrence count")
    check(result["syntax_split"]["ps_line_first"] == 128, "result p/s entry count")
    check(result["syntax_split"]["rl_line_middle_or_last"] == 226, "result r/l internal/final count")
    check(result["working_dictionary"]["entries"] == 251, "result dictionary size")
    check("former cooling reading is removed" in result["composition"]["ody_correction"], "ody cooling correction explicit")

    validation_core = {
        "schema": "GDT636_VALIDATION_V1", "experiment_id": "GDT636", "status": "PASS",
        "checks": len(checks), "builder_outputs_replayed": len(GENERATED),
        "residual_bodies": 19, "forms": 76, "occurrence_contexts": 527,
        "reader_exact_occurrences": 398, "concrete_spans": 14,
        "dictionary_entries": 251,
        "validated_claim": (
            "All nineteen residual bodies and seventy-six attested head forms have non-generic scoped defaults; "
            "their counts, reader evidence, placement, contrastive coexistence, ladders, contexts, spans, inherited "
            "dictionary prefix, hashes, guards and deterministic builder replay are independently checked."
        ),
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT636 validation PASS: {len(checks)} checks, {len(GENERATED)} outputs replayed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
