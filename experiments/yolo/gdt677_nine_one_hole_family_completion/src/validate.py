#!/usr/bin/env python3
"""Independently rebuild and validate GDT677."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V50_PATH = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer/artifacts/V50_EXTERNAL_LINE_READER.tsv"
GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|Arbeitsstelle|"
    r"Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|Arbeitsschritt|Stationsansatz|"
    r"Stationsposten|Stationswert|Stationsanteil|Stationseinheit|work item|working material|"
    r"worksite|work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt677_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT677 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "NINE_COMPLETED_LINES_V51.tsv",
        "V51_51_LINE_READER.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT677_NINE_COMPLETED_WORKING_READER.md",
        "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt677-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_"), "rebuilt status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "TARGET_FAMILY_CARDS.tsv")
    occurrences = read_tsv(ART / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv")
    completed = read_tsv(ART / "NINE_COMPLETED_LINES_V51.tsv")
    v51 = read_tsv(ART / "V51_51_LINE_READER.tsv")
    predictions = read_tsv(ART / "FAMILY_PREDICTIONS.tsv")
    analogs = read_tsv(ART / "HISTORICAL_ANALOG_ATLAS.tsv")
    v50 = read_tsv(V50_PATH)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 9, "nine cards")
    audit.check(len({row["surface"] for row in cards}) == 9, "unique cards")
    audit.check(Counter(row["card_type"] for row in cards) == {
        "PRODUCTIVE_COMPOUND": 7,
        "READER_CONDITIONED_COMPOUND": 1,
        "LEARNED_EXACT_WHOLE": 1,
    }, "card type distribution")
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    audit.check(expected_counts == {
        "ltaiin": 1, "oltaiin": 1, "ykcho": 4, "kchody": 4, "olchain": 1,
        "lolkaiin": 1, "aror": 6, "taiky": 1, "losair": 1,
    }, "exact surface counts")
    card_by_surface = {row["surface"]: row for row in cards}
    audit.check(card_by_surface["ykcho"]["working_meaning_de"] == "hieraus einen heiß-trockenen Ansatz bereiten", "ykcho action")
    audit.check(card_by_surface["kchody"]["working_meaning_de"] == "fertiggestellter heiß-trockener Ansatz", "kchody result")
    audit.check(card_by_surface["losair"]["composition"] == "LOS_WOOD_BATCH+AIR_FRACTION_II", "losair reader split")
    audit.check(card_by_surface["losair"]["strongest_rival_de"].startswith("Holzabsud"), "losair rival visible")
    audit.check("OPAQUE" in card_by_surface["taiky"]["composition"], "taiky middle opaque")
    audit.check(card_by_surface["taiky"]["confidence"] == "LOW_EXPLORATORY", "taiky low")

    audit.check(len(occurrences) == 20, "twenty occurrences")
    audit.check(len({(row["locus"], row["ordinal"]) for row in occurrences}) == 20, "unique occurrence keys")
    audit.check(Counter(row["surface"] for row in occurrences) == expected_counts, "occurrence counts match cards")
    audit.check(all(row["context_decision"].startswith("HOLD_") for row in occurrences), "all contexts hold")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {"BOTH_EXACT": 17, "ONE_EXACT": 3}, "reader support distribution")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(all(not GENERIC.search(row["context_after_de"]) for row in occurrences), "no generic occurrence filler")
    audit.check(sum(int(row["action_license"]) for row in occurrences) == 4, "four ykcho actions")
    audit.check(all(row["action_license"] == "1" for row in occurrences if row["surface"] == "ykcho"), "ykcho actions consistent")
    audit.check(all(row["action_license"] == "0" for row in occurrences if row["surface"] != "ykcho"), "other cards nominal")
    losair = next(row for row in occurrences if row["surface"] == "losair")
    audit.check(losair["rf1b_operation"] == "SPLIT_2" and losair["rf1b_render"] == "losair", "RF1b los air split")
    aror_variant = next(row for row in occurrences if row["locus"] == "f104r.28")
    audit.check(aror_variant["it2a_operation"] == "MERGE_2", "aror merge recorded")
    kchody_variant = next(row for row in occurrences if row["locus"] == "f5r.1")
    audit.check(kchody_variant["reader_support"] == "ONE_EXACT", "kchody variant recorded")

    audit.check(len(completed) == 9, "nine completed rows")
    audit.check(len({row["locus"] for row in completed}) == 9, "nine completed loci")
    audit.check(len({row["closed_surface"] for row in completed}) == 9, "one completion per card")
    for row in completed:
        tokens = row["zl3b_line"].split()
        chunks = row["working_line_de"].rstrip(".").split(" · ")
        literals = row["new_literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(chunks) == len(literals) == int(row["token_count"]), f"token preservation {row['locus']}")
        audit.check("⟦" not in row["working_line_de"] and ":?]" not in row["new_literal_token_glosses_de"], f"line closed {row['locus']}")
        audit.check(not GENERIC.search(row["working_line_de"]), f"no generic line filler {row['locus']}")
    f56 = next(row for row in completed if row["locus"] == "f56r.6")
    audit.check(f56["old_line_mode"] == "NOMINAL_REGISTER", "f56 old mode")
    audit.check(f56["new_line_mode"] == "MIXED_RECORD", "f56 mixed mode")
    audit.check(f56["new_action_ordinals"] == "1" and f56["new_action_surfaces"] == "ykcho", "f56 action")
    audit.check(sum(row["old_line_mode"] != row["new_line_mode"] for row in completed) == 1, "one mode correction")

    audit.check(len(v51) == 51, "51 line deck")
    audit.check(sum(int(row["token_count"]) for row in v51) == 479, "479 tokens")
    audit.check(sum(int(row["new_v51_positions"]) for row in v51) == 9, "nine V51 positions")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v51) == 127, "127 V51 gaps")
    audit.check(sum(row["complete"] == "1" for row in v51) == 11, "eleven complete")
    audit.check(Counter(int(row["residual_unknown_positions"]) for row in v51) == {0: 11, 2: 17, 3: 8, 4: 8, 5: 6, 7: 1}, "gap distribution")
    audit.check(sum(int(row["action_positions"]) for row in v51) == 49, "49 V51 actions")
    audit.check(Counter(row["line_mode"] for row in v51) == {
        "ACTION_SEQUENCE": 11, "MIXED_RECORD": 19, "NOMINAL_REGISTER": 13, "QUANTITY_LABEL": 8,
    }, "V51 modes")
    audit.check(all(not GENERIC.search(row["working_line_de"]) for row in v51), "V51 zero generic")
    v50_by_locus = {row["locus"]: row for row in v50}
    completed_loci = {row["locus"] for row in completed}
    for row in v51:
        old = v50_by_locus[row["locus"]]
        if row["locus"] not in completed_loci:
            audit.check(row["working_line_de"] == old["working_line_de"], f"untouched V50 line {row['locus']}")

    audit.check(len(predictions) == 6, "six predictions")
    audit.check(len({row["prediction_id"] for row in predictions}) == 6, "unique predictions")
    audit.check(len(analogs) == 8, "eight analogs")
    audit.check(all(row["source_url"].startswith("https://") for row in analogs), "analog URLs")
    audit.check(all(row["scope_limit"] for row in analogs), "analog limits")

    audit.check(result["status"] == "PASS_9_FAMILY_CARDS__20_CONTEXTS_HOLD__9_LINES_CLOSED__V51_127_OPEN", "result status")
    audit.check(result["basis"]["cross_guard"] == {"selected": 20, "skipped_forbidden": 98, "skipped_not_allowed": 5268}, "guard counts")
    audit.check(result["global_overlay"]["unknown_positions_after"] == 7923, "global 7923")
    audit.check(result["global_overlay"]["complete_lines_after"] == 1391, "global complete lines")
    audit.check(result["v51_reader"]["unknown_after"] == 127, "result V51 gaps")
    audit.check(result["v51_reader"]["hard_generic_hits"] == 0, "result zero generic")
    audit.check(result["weakest_card"]["surface"] == "taiky", "weakest card named")
    audit.check(result["open_reader_rival"]["surface"] == "losair", "reader rival named")
    for name, digest in result["files"].items():
        audit.check(builder.sha256(ART / name) == digest, f"result hash {name}")

    local_home_prefix = "/" + "home/"
    for name in artifact_names:
        content = (ART / name).read_text(encoding="utf-8")
        audit.check(local_home_prefix not in content and "file://" not in content, f"no local path {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_identical_rebuild_files": len(artifact_names),
        "cards": 9,
        "occurrences": 20,
        "completed_lines": 9,
        "v51_lines": 51,
        "v51_tokens": 479,
        "v51_unknown": 127,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
