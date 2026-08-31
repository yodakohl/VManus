#!/usr/bin/env python3
"""Independent validator for GDT694's exact-card V67 reader."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt694_residual_fraction_share_migration"
SRC = BASE / "src"
ART = BASE / "artifacts"
G693 = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts"
EXPECTED_STATUS = "PASS_V67_22_RESIDUAL_SHARE_MIGRATIONS__ZERO_FRAKTION_479_TOKEN_READER__3_BOUND_SPANS"
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term_count(texts: list[str], needle: str) -> int:
    return sum(
        needle.casefold() in word.casefold()
        for text in texts
        for word in WORD_RE.findall(text)
    )


def render(units: list[str]) -> str:
    text = ""
    for unit in units:
        if unit in {";", "."}:
            text = text.rstrip(" ,;.") + unit
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator + unit
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:] if text else text


def make_spans(
    rows: list[dict[str, str]],
    token_surface: dict[tuple[str, int], str],
) -> dict[str, dict[int, dict[str, str]]]:
    spans: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    occupied: set[tuple[str, int]] = set()
    for row in rows:
        locus = row["locus"]
        start, end = int(row["start_ordinal"]), int(row["end_ordinal"])
        actual = "|".join(token_surface[(locus, ordinal)] for ordinal in range(start, end + 1))
        assert actual == row["surfaces"]
        assert start not in spans[locus]
        for ordinal in range(start, end + 1):
            assert (locus, ordinal) not in occupied
            occupied.add((locus, ordinal))
        spans[locus][start] = row
    return spans


def render_line(
    locus: str,
    count: int,
    values: dict[tuple[str, int], str],
    spans: dict[str, dict[int, dict[str, str]]],
) -> str:
    units: list[str] = []
    ordinal = 1
    while ordinal <= count:
        span = spans.get(locus, {}).get(ordinal)
        if span:
            units.append(span["v67_selected_gloss_de"])
            ordinal = int(span["end_ordinal"]) + 1
        else:
            units.append(values[(locus, ordinal)])
            ordinal += 1
    return render(units)


def main() -> int:
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    base_tokens = read_tsv(G693 / "V66_479_TOKEN_SELECTED_SHARE_READER.tsv")
    base_lines = read_tsv(G693 / "V66_51_LINE_SELECTED_SHARE_READER.tsv")
    residuals = read_tsv(G693 / "V66_22_RESIDUAL_FRACTION_BEARING_OCCURRENCES.tsv")
    base_verbs = read_tsv(G693 / "V66_113_SELECTED_VERB_PRESERVATION.tsv")
    base_spans = read_tsv(G693 / "V66_2_SELECTED_BOUND_SPANS.tsv")
    base_rivals = read_tsv(G693 / "V66_6_SELECTED_PRODUCT_RIVALS.tsv")
    rules = read_tsv(SRC / "V67_22_RESIDUAL_SHARE_RULES.tsv")
    tokens = read_tsv(ART / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv")
    lines = read_tsv(ART / "V67_51_LINE_ZERO_FRACTION_READER.tsv")
    migrations = read_tsv(ART / "V67_22_RESIDUAL_SHARE_MIGRATIONS.tsv")
    changed_lines = read_tsv(ART / "V67_17_CHANGED_LINE_AUDIT.tsv")
    spans = read_tsv(ART / "V67_3_BOUND_SPANS.tsv")
    verbs = read_tsv(ART / "V67_113_VERB_PRESERVATION.tsv")
    rivals = read_tsv(ART / "V67_6_PRODUCT_RIVALS.tsv")
    census = read_tsv(ART / "V67_TERM_CENSUS.tsv")
    class_census = read_tsv(ART / "V67_COMPOSITION_CLASS_CENSUS.tsv")

    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: {detail}")
        checks.append({"check": name, "passed": 1, "detail": detail})

    check("result_status", result["status"] == EXPECTED_STATUS, EXPECTED_STATUS)
    check(
        "fixed_deck_dimensions",
        len(base_tokens) == len(tokens) == 479 and len(base_lines) == len(lines) == 51,
        "479 token positions and 51 lines",
    )
    check(
        "forbidden_folios_absent",
        all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in tokens),
        "no f84/f84r selector in materialized token deck",
    )

    def key(row: dict[str, str]) -> tuple[str, int]:
        return row["locus"], int(row["token_ordinal"])

    base_by_key = {key(row): row for row in base_tokens}
    token_by_key = {key(row): row for row in tokens}
    residual_by_key = {key(row): row for row in residuals}
    rule_by_key = {key(row): row for row in rules}
    migration_by_key = {key(row): row for row in migrations}
    check(
        "exact_rule_keyset",
        len(residual_by_key) == len(rule_by_key) == len(migration_by_key) == 22
        and set(residual_by_key) == set(rule_by_key) == set(migration_by_key),
        "22 unique residual keys equal 22 source rules and 22 materialized migrations",
    )
    rule_match = all(
        rule["surface"] == residual_by_key[k]["surface"] == base_by_key[k]["surface"]
        and rule["expected_v66_gloss_de"] == residual_by_key[k]["v66_selected_gloss_de"]
        and rule["expected_v66_gloss_de"] == base_by_key[k]["v66_selected_gloss_de"]
        and rule["v67_share_gloss_de"] == token_by_key[k]["v67_token_gloss_de"]
        for k, rule in rule_by_key.items()
    )
    check("rule_surface_and_gloss_match", rule_match, "all exact cards bind source surface, old gloss and new gloss")
    check(
        "all_rules_exact_card_scoped",
        all(row["exact_card_only"] == "1" for row in migrations)
        and sum(int(row["learned_whole_renderer"]) for row in migrations) == 3,
        "all 22 rules are exact-card scoped; three additionally remain learned whole renderers",
    )

    actual_changed = {
        k for k in base_by_key
        if base_by_key[k]["v66_selected_gloss_de"] != token_by_key[k]["v67_token_gloss_de"]
    }
    check(
        "only_22_positions_changed",
        actual_changed == set(rule_by_key) and len(actual_changed) == 22,
        "the exact 22 residual keys changed; all other 457 token glosses are byte-identical",
    )
    check(
        "seventeen_changed_lines",
        len(changed_lines) == 17
        and {row["locus"] for row in changed_lines} == {locus for locus, _ in actual_changed},
        "22 migrations occupy 17 unique loci",
    )
    check(
        "zero_fraktion_tokens",
        term_count([row["v67_token_gloss_de"] for row in tokens], "fraktion") == 0,
        "zero Fraktion-bearing words in 479 V67 token glosses",
    )
    check(
        "zero_fraktion_lines",
        term_count([row["v67_translation_de"] for row in lines], "fraktion") == 0,
        "zero Fraktion-bearing words in 51 V67 lines",
    )
    check(
        "mixed_composition_architecture",
        sum(int(row["exact_cards"]) for row in class_census) == 22
        and next(row for row in class_census if row["migration_class"] == "LEARNED_WHOLE_WITH_SHARE_RENDERER")["exact_cards"] == "3",
        "22 exact cards across explicit modes, including three learned whole-form renderers",
    )

    token_surface = {k: row["surface"] for k, row in token_by_key.items()}
    span_lookup = make_spans(spans, token_surface)
    check(
        "three_exact_nonoverlapping_spans",
        len(spans) == 3 and {row["span_id"] for row in spans} == {"B001", "B002", "B003"},
        "two inherited spans plus exact l|karchees span",
    )

    counts = Counter(row["locus"] for row in tokens)
    v67_values = {k: row["v67_token_gloss_de"] for k, row in token_by_key.items()}
    v67_line_by_locus = {row["locus"]: row for row in lines}
    replay_v67 = all(
        render_line(locus, counts[locus], v67_values, span_lookup)
        == v67_line_by_locus[locus]["v67_translation_de"]
        for locus in counts
    )
    check("independent_v67_line_replay", replay_v67, "all 51 V67 lines reconstruct from token glosses and three spans")

    inherited_spans = [
        {
            "span_id": row["span_id"], "locus": row["locus"],
            "start_ordinal": row["start_ordinal"], "end_ordinal": row["end_ordinal"],
            "surfaces": row["surfaces"], "v67_selected_gloss_de": row["selected_gloss_de"],
        }
        for row in base_spans
    ]
    old_span_lookup = make_spans(inherited_spans, token_surface)
    v66_values = {k: row["v66_selected_gloss_de"] for k, row in base_by_key.items()}
    base_line_by_locus = {row["locus"]: row for row in base_lines}
    replay_v66 = all(
        render_line(locus, counts[locus], v66_values, old_span_lookup)
        == base_line_by_locus[locus]["v66_selected_translation_de"]
        for locus in counts
    )
    check("independent_v66_line_replay", replay_v66, "all 51 inherited V66 lines reconstruct before migration")

    base_verb_by_key = {(key(row), row["verb_de"]): row for row in base_verbs}
    verb_by_key = {(key(row), row["verb_de"]): row for row in verbs}
    verb_parity = (
        len(base_verb_by_key) == len(verb_by_key) == 113
        and set(base_verb_by_key) == set(verb_by_key)
        and all(
            row["v67_exact_form_present"] == base_verb_by_key[k]["v66_selected_exact_form_present"]
            and row["v67_preserved_exact_ordinal"] == "1"
            for k, row in verb_by_key.items()
        )
        and sum(int(row["v67_exact_form_present"]) for row in verbs) == 110
    )
    check("verb_profile_parity", verb_parity, "113/113 ordinal profiles preserved; 110 exact surface forms present")

    rival_fields = list(base_rivals[0])
    rival_parity = len(rivals) == len(base_rivals) == 6 and all(
        all(rivals[i][field] == base_rivals[i][field] for field in rival_fields)
        and rivals[i]["v67_main_span_preserved"] == "1"
        for i in range(6)
    )
    check("six_product_rivals_preserved", rival_parity, "all inherited rival fields are byte-identical and marked preserved")

    census_by_channel = {row["channel"]: row for row in census}
    census_ok = (
        census_by_channel["V66_TOKEN"]["fraktion_bearing_words"] == "22"
        and census_by_channel["V66_LINE"]["fraktion_bearing_words"] == "22"
        and census_by_channel["V67_TOKEN"]["fraktion_bearing_words"] == "0"
        and census_by_channel["V67_LINE"]["fraktion_bearing_words"] == "0"
    )
    check("term_census_replay", census_ok, "Fraktion census is 22→0 in token and line channels")

    critical = {
        row["surface"]: row for row in migrations
        if row["surface"] in {"okeeodar", "araram", "chdar", "chear", "karchees"}
    }
    b003 = next(row for row in spans if row["span_id"] == "B003")
    critical_ok = (
        critical["okeeodar"]["v67_gloss_de"] == "Anteil I des vollständig erhitzten Auszugs"
        and "abgemessener Anteil I" in critical["okeeodar"]["local_rival_de"]
        and critical["araram"]["v67_gloss_de"] == "Drogenanteil I; davon ein Maß"
        and "Unteranteils" in critical["araram"]["local_rival_de"]
        and "Anfangsstufe" not in critical["chdar"]["v67_gloss_de"]
        and critical["chear"]["v67_gloss_de"] == "trockener Drogenanteil I"
        and "Mittelstufe" not in critical["chear"]["v67_gloss_de"]
        and b003["surfaces"] == "l|karchees"
        and "Holzdroge" in b003["v67_selected_gloss_de"]
    )
    check("critical_ambiguity_repairs", critical_ok, "single-D, boundary, index, bound-dry-shell and bound-L repairs are materialized")

    input_hashes_ok = all((ROOT / rel).is_file() and sha256(ROOT / rel) == digest for rel, digest in result["inputs"].items())
    check("input_hashes", input_hashes_ok, f"{len(result['inputs'])} input hashes match")
    file_hashes_ok = all((ART / name).is_file() and sha256(ART / name) == digest for name, digest in result["files"].items())
    check("output_hashes", file_hashes_ok, f"{len(result['files'])} generated file hashes match RESULT")

    with tempfile.TemporaryDirectory(prefix="gdt694-replay-") as tmp:
        replay_dir = Path(tmp)
        completed = subprocess.run(
            [sys.executable, str(SRC / "run.py"), str(replay_dir)],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        replay_names = set(result["files"]) | {"RESULT.json"}
        replay_ok = completed.returncode == 0 and all(
            (replay_dir / name).is_file() and (replay_dir / name).read_bytes() == (ART / name).read_bytes()
            for name in replay_names
        )
    check("byte_replay", replay_ok, f"builder reproduces {len(replay_names)} generated files byte-for-byte in a clean temporary directory")

    payload = {
        "status": "PASS",
        "experiment": "GDT694",
        "validated_status": EXPECTED_STATUS,
        "checks_passed": len(checks),
        "checks": checks,
        "summary": {
            "token_positions": 479, "lines": 51, "migrations": 22,
            "changed_lines": 17, "bound_spans": 3, "verb_profiles": 113,
            "exact_verb_forms": 110, "product_rivals": 6,
            "v67_fraktion_bearing_token_words": 0,
            "v67_fraktion_bearing_line_words": 0,
            "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
