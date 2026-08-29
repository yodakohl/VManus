#!/usr/bin/env python3
"""Validate and byte-replay GDT629."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt629_part_quality_degree_clause")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
G628_DICT = ROOT / "experiments/yolo/gdt628_chol_measure_frame/artifacts/WORKING_DICTIONARY_V5.tsv"
GENERATED_RELS = (
    BASE_REL / "artifacts/TARGET_PAGE_ALLOWLIST.tsv",
    BASE_REL / "artifacts/READER_REALIZATION_VIEWS.tsv",
    BASE_REL / "artifacts/LOCUS_TRIANGULATION.tsv",
    BASE_REL / "artifacts/CROSS_READER_BOUNDARY_BRIDGES.tsv",
    BASE_REL / "artifacts/PART_QUALITY_DEGREE_REALIZATIONS.tsv",
    BASE_REL / "artifacts/CHOL_VALUE_CLAUSE_CONTEXTS.tsv",
    BASE_REL / "artifacts/TARGET_LINE_TOKEN_DEFAULTS.tsv",
    BASE_REL / "artifacts/CLAUSE_ROLE_RANKING.tsv",
    BASE_REL / "artifacts/WORKING_DICTIONARY_V6.tsv",
    BASE_REL / "artifacts/CONCRETE_CLAUSES_V1.tsv",
    RESULT_REL,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    before = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    completed = subprocess.run(
        [sys.executable, str(BASE / "src/run.py")], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    require(completed.returncode == 0, "builder exits zero")
    require(
        "views=24 modes={'DIRECT_AIII': 7, 'FUSED_D_AIII': 7, "
        "'FUSED_REDUPLICATED_CH_AIII': 1, 'SEPARATE_D_AIII': 8, "
        "'SEPARATE_REDUPLICATED_CH_AIII': 1} loci=8 bridges=3 "
        "partviews=9 contexts=43 tokens=65 dictionary=32" in completed.stdout,
        "builder summary",
    )
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT629_PART_QUALITY_DEGREE_CLAUSE_RESULT_V1", "result schema")
    require(result["status"] == "FUSED_SEPARATE_BOUNDARY_EQUIVALENCE__TWO_EXACT_PART_DRY_III_CLAUSES__DIRECT_PART_CLAUSE_READER_VARIANT", "result status")
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "canonical result hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"] == {
        "cross_query": {"selected": 163, "skipped_forbidden": 98, "skipped_not_allowed": 5125},
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
        "queried_cross_rows": 163, "target_loci": 8, "target_pages": 8,
    }, "guarded source scope")
    require(result["reader_triangulation"] == {
        "boundary_variant_loci": 3,
        "exact_expression_agreement_loci": 5,
        "exact_fused_separate_bridges": 2,
        "mode_counts": {
            "DIRECT_AIII": 7, "FUSED_D_AIII": 7, "FUSED_REDUPLICATED_CH_AIII": 1,
            "SEPARATE_D_AIII": 8, "SEPARATE_REDUPLICATED_CH_AIII": 1,
        },
        "normalized_surface_agreement_loci": 7,
        "reader_views": 24,
    }, "reader triangulation summary")
    require(result["part_quality_degree"] == {
        "exact_clause_loci": ["f21r.12", "f32v.10"], "fused_part_anchor_loci": 0,
        "part_loci": 3, "part_reader_views": 9, "reader_variant_clause_locus": "f27r.6",
        "triple_exact_separate_part_loci": 2,
        "working_clause_de": "Pflanzen-/Reproduktionsteil: trocken, Grad III",
    }, "part-quality-degree summary")
    require(result["all_chol_value_contexts"] == {
        "contexts": 43,
        "role_counts": {
            "PART_QUALITY_DEGREE_CLAUSE": 3,
            "QUALITY_DEGREE_PHRASE_ONLY": 33,
            "QUALITY_DEGREE_WITH_NEAR_PART": 7,
        },
        "stable_expressions": 35,
    }, "all chol-value context summary")
    require(result["target_line_defaults"] == {
        "open_tokens": 35, "tokens": 65,
        "type_counts": {
            "CARRIER": 3, "CHOL_EXTENSION_OPEN": 2, "CONCRETE_PART": 4,
            "CONCRETE_QUALITY": 4, "CONCRETE_QUALITY_DEGREE": 6,
            "CONTEXTUAL_VALUE": 3, "CTH_PART_FAMILY": 2, "OPEN": 35,
            "QUALITY_ROOT_OPEN_BINDING": 1, "VALUE_WITH_OPEN_HEAD": 5,
        },
        "unaccounted_tokens": 0,
    }, "target-token default summary")
    require(result["manual_sources"] == {"concrete_clauses": 8, "historical_comparators": 6, "role_models": 4}, "manual source counts")
    for path, expected in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"input hash {path}")
    for path, expected in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"output hash {path}")
    require(set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL}, "result binds every generated evidence file")

    allowlist = read_tsv(ART / "TARGET_PAGE_ALLOWLIST.tsv")
    require([row["page"] for row in allowlist] == ["f100r", "f17v", "f21r", "f27r", "f2r", "f32v", "f49r", "f58r"], "target-page allow-list")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in allowlist), "target pages exclude forbidden folios")

    views = read_tsv(ART / "READER_REALIZATION_VIEWS.tsv")
    require(len(views) == 24, "twenty-four reader views")
    require(Counter(row["reader"] for row in views) == Counter({"ZL3b": 8, "IT2a": 8, "RF1b": 8}), "eight views per reader")
    require(Counter(row["realization_mode"] for row in views) == Counter({
        "SEPARATE_D_AIII": 8, "DIRECT_AIII": 7, "FUSED_D_AIII": 7,
        "FUSED_REDUPLICATED_CH_AIII": 1, "SEPARATE_REDUPLICATED_CH_AIII": 1,
    }), "reader-view mode partition")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in views), "reader views exclude forbidden folios")
    view_key = {(row["locus"], row["reader"]): row for row in views}
    require(view_key["f17v.8", "ZL3b"]["surface_expression"] == "choldaiin", "f17 ZL fused")
    require(view_key["f17v.8", "IT2a"]["surface_expression"] == "choldaiin", "f17 IT fused")
    require(view_key["f49r.6", "ZL3b"]["surface_expression"] == "choldaiin", "f49 ZL fused")
    require(view_key["f49r.6", "IT2a"]["surface_expression"] == "chol daiin", "f49 IT separate")
    require(view_key["f49r.6", "RF1b"]["surface_expression"] == "choldaiin", "f49 RF fused")
    require(view_key["f100r.22", "IT2a"]["surface_expression"] == "chol daiin", "f100 IT separate")
    require(view_key["f27r.6", "ZL3b"]["surface_expression"] == "cholaiin", "f27 ZL direct")
    require(view_key["f27r.6", "IT2a"]["surface_expression"] == "chol chaiin", "f27 IT expanded dry")
    require(view_key["f27r.6", "RF1b"]["surface_expression"] == "cholchaiin", "f27 RF fused expanded dry")
    require(all(view_key[locus, reader]["smallest_clause_expression"].startswith("chor ") for locus in ("f21r.12", "f27r.6", "f32v.10") for reader in ("ZL3b", "IT2a", "RF1b")), "three part loci retain immediate chor in every reader")
    require(not any(row["part_immediately_before"] == "1" for row in views if row["realization_mode"] == "FUSED_D_AIII"), "no fused-d view has immediate part anchor")

    loci = read_tsv(ART / "LOCUS_TRIANGULATION.tsv")
    require(len(loci) == 8, "eight locus summaries")
    require(sum(int(row["exact_expression_agreement"]) for row in loci) == 5, "five exact-expression agreement loci")
    require(sum(int(row["normalized_surface_agreement"]) for row in loci) == 7, "seven normalized-surface agreement loci")
    locus_map = {row["locus"]: row for row in loci}
    require(locus_map["f21r.12"]["claim_level"] == "COMPLETE_PART_QUALITY_DEGREE_CLAUSE", "f21 complete clause")
    require(locus_map["f32v.10"]["claim_level"] == "COMPLETE_PART_QUALITY_DEGREE_CLAUSE", "f32 complete clause")
    require(locus_map["f27r.6"]["exact_expression_agreement"] == "0" and locus_map["f27r.6"]["normalized_surface_agreement"] == "0", "f27 reader variant not reduced to spacing")
    require(all(locus_map[locus]["claim_level"] == "QUALITY_DEGREE_PHRASE_ONLY" for locus in ("f17v.8", "f49r.6", "f100r.22")), "fused loci remain phrase-only")

    bridges = read_tsv(ART / "CROSS_READER_BOUNDARY_BRIDGES.tsv")
    require(len(bridges) == 3, "three reader boundary bridges")
    require(Counter(row["strength"] for row in bridges) == Counter({"EXACT_NORMALIZED_BOUNDARY_EQUIVALENCE": 2, "SEMANTIC_READER_VARIANT_NOT_SPACING_ONLY": 1}), "bridge-strength partition")
    bridge_map = {row["locus"]: row for row in bridges}
    require(bridge_map["f49r.6"]["bridge_type"] == "FUSED_D_TO_SEPARATE_D", "f49 exact boundary bridge")
    require(bridge_map["f100r.22"]["bridge_type"] == "FUSED_D_TO_SEPARATE_D", "f100 exact boundary bridge")
    require(bridge_map["f27r.6"]["bridge_type"] == "DIRECT_TO_REDUPLICATED_CH_DRY", "f27 separate semantic variant")

    part_clauses = read_tsv(ART / "PART_QUALITY_DEGREE_REALIZATIONS.tsv")
    require(len(part_clauses) == 9, "nine part-clause reader views")
    require(Counter(row["locus"] for row in part_clauses) == Counter({"f21r.12": 3, "f27r.6": 3, "f32v.10": 3}), "three part-clause loci")
    require(Counter(row["evidence_class"] for row in part_clauses) == Counter({"TRIPLE_EXACT_SEPARATE_CLAUSE": 6, "SEMANTIC_TRIPLE_READER_VARIANT__DIRECT_ONLY_IN_ZL3B": 3}), "part-clause evidence classes")
    require(all(row["working_reading_de"] == "Pflanzen-/Reproduktionsteil: trocken, Grad III" for row in part_clauses), "normalized part-clause reading")
    require(all(row["dose_rival_de"] != "NONE" for row in part_clauses), "dose rival never hidden")

    contexts = read_tsv(ART / "CHOL_VALUE_CLAUSE_CONTEXTS.tsv")
    require(len(contexts) == 43, "all forty-three inherited chol-value contexts")
    require(sum(int(row["expression_triple_stable"]) for row in contexts) == 35, "thirty-five stable inherited expressions")
    require(Counter(row["context_role"] for row in contexts) == Counter({
        "QUALITY_DEGREE_PHRASE_ONLY": 33, "QUALITY_DEGREE_WITH_NEAR_PART": 7,
        "PART_QUALITY_DEGREE_CLAUSE": 3,
    }), "context-role partition")
    immediate = {row["locus"] for row in contexts if row["immediate_part_before"] == "1"}
    require(immediate == {"f21r.12", "f27r.6", "f32v.10"}, "only three immediate part contexts")
    require(next(row for row in contexts if row["locus"] == "f27r.6")["expression_triple_stable"] == "0", "f27 direct expression instability retained")

    token_defaults = read_tsv(ART / "TARGET_LINE_TOKEN_DEFAULTS.tsv")
    require(len(token_defaults) == 65, "sixty-five ZL target-line token defaults")
    require(Counter(row["default_type"] for row in token_defaults) == Counter({
        "OPEN": 35, "CONCRETE_QUALITY_DEGREE": 6, "VALUE_WITH_OPEN_HEAD": 5,
        "CONCRETE_PART": 4, "CONCRETE_QUALITY": 4, "CARRIER": 3,
        "CONTEXTUAL_VALUE": 3, "CHOL_EXTENSION_OPEN": 2, "CTH_PART_FAMILY": 2,
        "QUALITY_ROOT_OPEN_BINDING": 1,
    }), "target-token default types")
    require(all(row["default_meaning_de"] != "" and row["default_type"] != "NONE" for row in token_defaults), "no target token omitted")
    require(all(row["default_meaning_de"] == "OPEN; keine generische Ersatzbedeutung" for row in token_defaults if row["default_type"] == "OPEN"), "open tokens receive no generic filler")
    token_lines: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_defaults:
        token_lines[row["locus"]].append(row)
    for locus, selected in token_lines.items():
        selected.sort(key=lambda row: int(row["token_index"]))
        reconstructed = " ".join(row["surface"] for row in selected)
        require(reconstructed == view_key[locus, "ZL3b"]["surface_line"], f"ZL token roundtrip {locus}")

    ranking = read_tsv(ART / "CLAUSE_ROLE_RANKING.tsv")
    require(len(ranking) == 4, "four clause models")
    require(ranking[0]["model"] == "PART_QUALITY_DEGREE" and ranking[0]["disposition"] == "PRIMARY_WORKING_CLAUSE", "part-quality-degree model ranks first")
    require(ranking[1]["model"] == "PART_OR_DRY_MATERIAL_THREE_PORTIONS" and ranking[1]["disposition"] == "LIVE_SEPARATE_FORM_RIVAL", "three-portion rival stays live")
    require(ranking[-1]["model"] == "GENERIC_OPERATION_OR_LIST_WORD" and ranking[-1]["disposition"] == "REJECTED_AS_DEFAULT", "generic operation prose rejected")

    old_dictionary = read_tsv(G628_DICT)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V6.tsv")
    require(len(old_dictionary) == 28 and len(dictionary) == 32, "V6 consolidates twenty-eight plus four entries")
    require(dictionary[:28] == old_dictionary, "all V5 entries retained byte-for-field")
    entries = {row["entry"]: row for row in dictionary}
    require(entries["chor chol daiin"]["status"] == "NEW_PRIMARY_CLAUSE", "exact separate clause dictionary entry")
    require(entries["choldaiin|chol daiin"]["status"] == "NEW_EXACT_BOUNDARY_BRIDGE", "boundary bridge dictionary entry")
    require(entries["chor cholaiin"]["status"] == "PROVISIONAL_DIRECT_CLAUSE", "direct part clause remains provisional")
    require(entries["cholchaiin|chol chaiin"]["status"] == "NEW_READER_VARIANT", "extra-ch reader variant retained")

    cases = read_tsv(ART / "CONCRETE_CLAUSES_V1.tsv")
    require(len(cases) == 8, "eight concrete clause records")
    case_map = {row["case_id"]: row for row in cases}
    require(case_map["F21_EXACT_PART_CLAUSE"]["working_reading_de"] == "Pflanzen-/Reproduktionsteil: trocken, Grad III", "f21 concrete clause")
    require(case_map["F32_EXACT_PART_CLAUSE"]["evidence_class"] == "TRIPLE_EXACT_COMPLETE_CLAUSE", "f32 exact clause")
    require(case_map["F27_PART_READER_VARIANT"]["evidence_class"] == "SEMANTIC_READER_VARIANT", "f27 case marks reader variant")
    require(case_map["F17_EXACT_FUSED"]["working_reading_de"].endswith("äußerer Träger offen"), "f17 fused carrier remains open")
    require(all(row["residual_policy"] == "Tokens außerhalb der kleinsten Klammer bleiben sichtbar und OPEN" for row in cases), "no residual token silently translated")

    private_pattern = re.compile(
        "/" + "home/|/" + "tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
        "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
        "password\\s*[=:]|api[_-]?key\\s*[=:]|secret\\s*[=:]", re.IGNORECASE,
    )
    scan_paths = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json",
        BASE / "artifacts/README.md", *[ROOT / path for path in GENERATED_RELS],
    )
    for path in scan_paths:
        require(path.is_file(), f"required file {path.relative_to(ROOT)}")
        require(not private_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {path.relative_to(ROOT)}")

    payload = {
        "schema": "GDT629_VALIDATION_V1", "experiment_id": "GDT629", "status": "PASS",
        "checks": checks, "check_count": len(checks), "result_sha256": sha256(ROOT / RESULT_REL),
    }
    (ROOT / VALIDATION_REL).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
