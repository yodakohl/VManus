#!/usr/bin/env python3
"""Validate GDT759 artifacts and a byte-identical builder replay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt759_quantity_part_state_construction_atlas")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("gdt759_builder_for_validation", RUN)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    spans = read_tsv(ART / "EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv")
    quantity = read_tsv(ART / "QUANTITY_96_EXACT_PAIR_ATLAS.tsv")
    summaries = read_tsv(ART / "EXACT_CONSTRUCTION_26_PAIR_SUMMARY.tsv")
    boundaries = read_tsv(ART / "QUANTITY_51_READER_BOUNDARY_CANDIDATES.tsv")
    exact_bridges = read_tsv(ART / "QUANTITY_7_EXACT_BOUNDARY_BRIDGES.tsv")
    fused = read_tsv(ART / "FUSED_S_VALUE_FAMILY_REVISION.tsv")
    part_state = read_tsv(ART / "PART_STATE_23_EXACT_PAIR_ATLAS.tsv")
    objects = read_tsv(ART / "ODOL_OLS_14_OCCURRENCE_ADJUDICATION.tsv")
    dictionary = read_tsv(ART / "GDT759_EXACT_CONSTRUCTION_DICTIONARY.tsv")
    reader = read_tsv(ART / "GDT759_13_YCHOR_REVISED_READER.tsv")
    s_dispatch = read_tsv(ART / "S_154_CONTEXT_DISPATCH.tsv")
    historical = read_tsv(ART / "HISTORICAL_CONSTRUCTION_COMPARATORS.tsv")

    require(result["schema"] == "GDT759_RESULT_V1", "result schema")
    require(result["status"] == builder.STATUS, "result status")
    require(len(spans) == 122, "122 construction spans")
    require(len(quantity) == 96, "96 quantity spans")
    require(len(summaries) == 26, "26 pair summaries")
    require(len(boundaries) == 51, "51 boundary candidates")
    require(len(exact_bridges) == 7, "seven exact boundary bridges")
    require(len(fused) == 4, "four fused s-family revisions")
    require(len(part_state) == 23, "23 part-state spans")
    require(len(objects) == 14, "fourteen odol/ols occurrences")
    require(len(dictionary) == 17, "seventeen observed construction types")
    require(len(reader) == 13, "thirteen ychor lines")
    require(len(s_dispatch) == 154, "154 s dispatches")
    require(len(historical) == 13, "thirteen historical comparator rows")

    quantity_counts = Counter((row["left_surface"], row["right_surface"]) for row in quantity)
    require(quantity_counts[("s", "aiin")] == 23, "23 s aiin spans")
    require(quantity_counts[("or", "aiin")] == 36, "36 or aiin spans")
    require(quantity_counts[("ar", "aiin")] == 16, "16 ar aiin spans")
    bridge_counts = Counter((row["head_surface"], row["value_surface"]) for row in exact_bridges)
    require(bridge_counts[("s", "aiin")] == 4, "four exact s aiin bridges")
    require(bridge_counts[("or", "ain")] == 1, "one exact or ain bridge")
    require(bridge_counts[("or", "aiin")] == 1, "one exact or aiin bridge")
    require(bridge_counts[("ar", "aiin")] == 1, "one exact ar aiin bridge")
    require(all(row["line_normalized_identical_after_target_merges"] == "1" for row in exact_bridges), "exact bridge flag")

    part_counts = Counter((row["left_surface"], row["right_surface"]) for row in part_state)
    require(part_counts[("chor", "chol")] + part_counts[("chol", "chor")] == 15, "fifteen chor/chol spans")
    require(part_counts[("cthy", "chol")] + part_counts[("chol", "cthy")] == 6, "six cthy/chol spans")
    require(part_counts[("chor", "qokchol")] + part_counts[("qokchol", "chor")] == 2, "two chor/qokchol spans")
    require(not any("sheol" in pair for pair in part_counts), "zero observed sheol part pair")

    require(sum(int(row["reader_exact_fused_occurrences"]) for row in fused) == 145, "145 fused s-family occurrences")
    require(all("QUARANTINED" in row["old_seed_default_disposition"] for row in fused), "seed family quarantined")
    require(all("Samen" not in row["new_primary_de"] and "Saat" not in row["new_primary_de"] for row in fused), "no seed in revised primary")
    require(next(row for row in fused if row["surface"] == "saiin")["new_primary_de"] == "drei Drachmen", "saiin primary")

    s_classes = Counter(row["context_class"] for row in s_dispatch)
    require(s_classes == Counter({
        "OTHER_S_CONTEXT": 94,
        "LINE_FINAL_AMOUNT_FORMULA": 34,
        "ORDERED_VALUE_SPAN": 25,
        "EXACT_S_OM_DISTRIBUTIVE_SPAN": 1,
    }), "s dispatch classes")
    require(sum(row["surface"] == "ols" and row["candidate_changed"] == "1" for row in objects) == 12, "all twelve ols occurrences revised")
    require(sum(row["surface"] == "odol" and row["candidate_changed"] == "0" for row in objects) == 2, "both odol occurrences retained")
    require(sum(row["gdt759_changed_from_gdt758"] == "1" for row in reader) == 1, "one ychor line revised")

    for row in spans:
        require(bool(row["primary_render_de"]), f"nonempty render {row['construction_span_id']}")
        require(row["component_export_credit"] == "0", f"zero component credit {row['construction_span_id']}")
        require(row["confirmed_plaintext"] == "0", f"zero plaintext {row['construction_span_id']}")
        require("Arbeitsgut" not in row["primary_render_de"], f"no generic filler {row['construction_span_id']}")
        require(not row["page"].startswith("f84"), f"sealed page absent {row['construction_span_id']}")
    for row in boundaries:
        require(not row["page"].startswith("f84"), f"sealed boundary page absent {row['boundary_candidate_id']}")
        require(row["component_export_credit"] == "0", f"boundary component credit {row['boundary_candidate_id']}")
    for row in historical:
        require(row["voynich_graphic_identity_credit"] == "0", f"historical graphic credit {row['comparator_id']}")
        require(row["historical_lexeme_confirmation"] == "0", f"historical lexeme credit {row['comparator_id']}")

    require(result["claim_boundary"]["confirmed_lexemes"] == 0, "zero confirmed lexemes")
    require(result["claim_boundary"]["confirmed_historical_units"] == 0, "zero confirmed units")
    require(result["claim_boundary"]["component_values"] == 0, "zero components")
    require(result["claim_boundary"]["new_pages"] == 0, "zero new pages")
    require(result["claim_boundary"]["f84_accessed"] is False, "f84 forbidden")
    require(result["claim_boundary"]["f84r_accessed"] is False, "f84r forbidden")

    with tempfile.TemporaryDirectory(prefix="gdt759_replay_") as temp:
        replay_dir = Path(temp)
        replay_result = builder.build(replay_dir)
        require(replay_result == result, "replayed result object")
        for name in builder.OUTPUT_NAMES:
            require((replay_dir / name).is_file(), f"replay output exists {name}")
            require(digest(replay_dir / name) == digest(ART / name), f"byte replay {name}")

    validation = {
        "schema": "GDT759_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "byte_identical_replay": True,
        "scope": result["scope"],
        "quantity_result": result["quantity_result"],
        "part_state_result": result["part_state_result"],
        "preparation_result": result["preparation_result"],
        "claim_ceiling": (
            "Seventeen observed exact construction types and four fused s-value "
            "overlays remain replaceable working readings; zero confirmed lexemes, "
            "units, component values, plaintext clauses or new pages."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
