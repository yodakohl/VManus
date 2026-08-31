#!/usr/bin/env python3
"""Independently rebuild and validate GDT679."""

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
EXP = ROOT / "experiments/yolo/gdt679_eight_three_hole_family_completion"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V52_PATH = ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion/artifacts/V52_51_LINE_READER.tsv"
GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|Arbeitsstelle|"
    r"Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|Arbeitsschritt|Stationsansatz|"
    r"Stationsposten|Stationswert|Stationsanteil|Stationseinheit|weiterführen|work item|"
    r"working material|worksite|work cycle|source vessel|destination place|destination vessel)\b",
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
    spec = importlib.util.spec_from_file_location("gdt679_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT679 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "BOUNDARY_DECISIONS.tsv",
        "EIGHT_COMPLETED_LINES_V53.tsv",
        "V53_51_LINE_READER.tsv",
        "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT679_EIGHT_COMPLETED_PRACTICAL_READER.md",
        "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt679-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_"), "rebuilt status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "TARGET_FAMILY_CARDS.tsv")
    occurrences = read_tsv(ART / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv")
    boundaries = read_tsv(ART / "BOUNDARY_DECISIONS.tsv")
    completed = read_tsv(ART / "EIGHT_COMPLETED_LINES_V53.tsv")
    v53 = read_tsv(ART / "V53_51_LINE_READER.tsv")
    global_closed = read_tsv(ART / "GLOBAL_NEWLY_COMPLETED_LINES.tsv")
    predictions = read_tsv(ART / "FAMILY_PREDICTIONS.tsv")
    analogs = read_tsv(ART / "HISTORICAL_ANALOG_ATLAS.tsv")
    v52 = read_tsv(V52_PATH)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 24, "twenty-four cards")
    audit.check(len({row["surface"] for row in cards}) == 24, "unique cards")
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    audit.check(sum(expected_counts.values()) == 57, "card counts total 57")
    card_by_surface = {row["surface"]: row for row in cards}
    audit.check(card_by_surface["ckhol"]["working_meaning_de"] == "Drogenstoff aus Arzneikompositum", "ckhol concrete")
    audit.check(card_by_surface["ckhol"]["observed_occurrences"] == "17", "ckhol mass carrier")
    audit.check(card_by_surface["qeeey"]["card_type"] == "ANAPHORIC_PROCESS_COMMAND", "qeeey process choice")
    audit.check("vorstehende Behandlung" in card_by_surface["qeeey"]["working_meaning_de"], "qeeey left binding")
    audit.check(card_by_surface["kc"]["composition"] == "K_HOT+CH_DRY+S_TERM_SPECIES", "kc repaired composition")
    audit.check(card_by_surface["daiiiry"]["composition"] == "D_MEASURE+AIIIR_FRACTION_IV+CHY_DRY_START", "daiiiry repaired composition")
    audit.check(card_by_surface["tolg"]["confidence"] == "LOW_EXPLORATORY", "tolg visibly weak")
    audit.check(sum(int(row["action_license"]) for row in cards) == 5, "five action cards")

    audit.check(len(occurrences) == 57, "57 occurrence rows")
    audit.check(len({(row["locus"], row["ordinal"]) for row in occurrences}) == 57, "unique occurrence keys")
    audit.check(Counter(row["surface"] for row in occurrences) == expected_counts, "occurrence distribution")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(all(not GENERIC.search(row["context_after_de"]) for row in occurrences), "no generic occurrence filler")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {
        "BOTH_EXACT": 44,
        "IT2A_ONLY_EXACT": 4,
        "RF1B_ONLY_EXACT": 2,
        "NEITHER_EXACT": 7,
    }, "reader support distribution")
    audit.check(sum(row["context_decision"] == "HOLD_SAME_CARD" for row in occurrences) == 44, "44 fully exact holds")

    audit.check(len(boundaries) == 13, "thirteen reader decisions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" for row in boundaries) == 7, "seven neither-exact decisions")
    kc = next(row for row in boundaries if row["surface"] == "kc")
    audit.check(kc["it2a_render"] == kc["rf1b_render"] == "kchs", "kc bilateral repair")
    daiiiry = next(row for row in boundaries if row["surface"] == "daiiiry")
    audit.check(daiiiry["it2a_render"] == daiiiry["rf1b_render"] == "daiiirchy", "daiiiry bilateral repair")
    cthor = next(row for row in boundaries if row["surface"] == "cthororaiin")
    audit.check(cthor["it2a_operation"] == cthor["rf1b_operation"] == "SPLIT_2", "cthor bilateral split")
    orsheey = next(row for row in boundaries if row["surface"] == "orsheey")
    audit.check(orsheey["it2a_render"] == "orsheey" and orsheey["rf1b_render"] == "orshee", "orsheey split and rival")
    tolg = next(row for row in boundaries if row["surface"] == "tolg")
    audit.check(tolg["it2a_render"] == "tolm" and tolg["rf1b_render"] == "chotolg", "tolg unit dispute")

    audit.check(len(completed) == 8, "eight completed source lines")
    audit.check(len({row["locus"] for row in completed}) == 8, "unique source loci")
    audit.check(sum(len(row["closed_surfaces"].split("|")) for row in completed) == 24, "24 source slots")
    audit.check(sum(len([] if row["added_action_ordinals"] == "NONE" else row["added_action_ordinals"].split("|")) for row in completed) == 5, "five new source actions")
    for row in completed:
        tokens = row["zl3b_line"].split()
        chunks = row["aligned_line_de"].rstrip(".").split(" · ")
        literals = row["new_literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(chunks) == len(literals) == int(row["token_count"]), f"token alignment {row['locus']}")
        audit.check("⟦" not in row["aligned_line_de"] and ":?]" not in row["new_literal_token_glosses_de"], f"line closed {row['locus']}")
        audit.check(not GENERIC.search(row["aligned_line_de"]), f"no generic aligned filler {row['locus']}")
        audit.check(not GENERIC.search(row["practical_translation_de"]), f"no generic practical filler {row['locus']}")
    f107 = next(row for row in completed if row["locus"] == "f107r.2")
    audit.check("vollständig zu Ende trocknen und abschließen" in f107["practical_translation_de"], "f107 qeeey practical")
    f113 = next(row for row in completed if row["locus"] == "f113v.17")
    audit.check("drei Portionen Blatt- oder Krautdroge" in f113["aligned_line_de"], "f113 herb portions")
    f8 = next(row for row in completed if row["locus"] == "f8r.15")
    audit.check("Charge heißgetrockneter Droge" in f8["aligned_line_de"], "f8 kchs practical")
    audit.check("vierte abgemessene Trockenfraktion" in f8["aligned_line_de"], "f8 daiiirchy practical")

    audit.check(len(v53) == 51, "51 V53 lines")
    audit.check(sum(int(row["token_count"]) for row in v53) == 479, "479 tokens")
    audit.check(sum(int(row["new_v53_positions"]) for row in v53) == 24, "24 V53 positions")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v53) == 69, "69 V53 gaps")
    audit.check(sum(row["complete"] == "1" for row in v53) == 36, "36 complete V53 lines")
    audit.check(Counter(int(row["residual_unknown_positions"]) for row in v53) == {0: 36, 4: 8, 5: 6, 7: 1}, "V53 gap distribution")
    audit.check(sum(int(row["action_positions"]) for row in v53) == 65, "65 V53 actions")
    audit.check(Counter(row["line_mode"] for row in v53) == {
        "ACTION_SEQUENCE": 13,
        "MIXED_RECORD": 21,
        "NOMINAL_REGISTER": 10,
        "QUANTITY_LABEL": 7,
    }, "V53 modes")
    audit.check(all(not GENERIC.search(row["aligned_line_de"]) for row in v53), "V53 aligned no generic")
    audit.check(all(not GENERIC.search(row["practical_translation_de"]) for row in v53), "V53 practical no generic")
    v52_by_locus = {row["locus"]: row for row in v52}
    completed_loci = {row["locus"] for row in completed}
    prose_repairs = {"f105r.2", "f77v.7"}
    for row in v53:
        old = v52_by_locus[row["locus"]]
        if row["locus"] not in completed_loci:
            audit.check(row["aligned_line_de"] == old["aligned_line_de"], f"untouched aligned V52 line {row['locus']}")
            audit.check(row["literal_token_glosses_de"] == old["literal_token_glosses_de"], f"untouched literal V52 line {row['locus']}")
            if row["locus"] not in prose_repairs:
                audit.check(row["practical_translation_de"] == old["practical_translation_de"], f"untouched practical V52 line {row['locus']}")
    audit.check("weiterführen" not in next(row for row in v53 if row["locus"] == "f105r.2")["practical_translation_de"], "f105 prose repair")
    audit.check("weiterführen" not in next(row for row in v53 if row["locus"] == "f77v.7")["practical_translation_de"], "f77 prose repair")

    audit.check(len(global_closed) == 8, "eight global closures")
    audit.check({row["locus"] for row in global_closed} == completed_loci, "global closures equal source")
    audit.check(all(":?]" not in row["after_literal_de"] for row in global_closed), "global rows closed")
    audit.check(len(predictions) == 8 and len({row["prediction_id"] for row in predictions}) == 8, "eight predictions")
    audit.check(len(analogs) == 7, "seven analogs")
    audit.check(all(row["source_url"].startswith("https://") for row in analogs), "analog URLs")
    audit.check(all(row["scope_limit"] for row in analogs), "analog limits")

    audit.check(result["status"] == "PASS_24_FAMILY_CARDS__57_CONTEXTS_HOLD__8_V53_LINES_CLOSED__V53_69_OPEN", "result status")
    audit.check(result["basis"]["cross_guard"] == {"selected": 41, "skipped_forbidden": 98, "skipped_not_allowed": 5247}, "guard counts")
    audit.check(result["global_overlay"] == {
        "unknown_positions_before": 7822,
        "unknown_positions_after": 7765,
        "new_assigned_positions": 57,
        "complete_lines_before": 1410,
        "complete_lines_after": 1418,
        "newly_completed_lines": 8,
        "newly_completed_outside_v52_source": [],
    }, "global result")
    audit.check(result["v53_reader"]["unknown_after"] == 69, "result V53 gaps")
    audit.check(result["v53_reader"]["assigned_after"] == 410, "result V53 assigned")
    audit.check(result["v53_reader"]["complete_after"] == 36, "result V53 complete")
    audit.check(result["v53_reader"]["new_action_positions"] == 5, "result new actions")
    audit.check(result["v53_reader"]["hard_generic_hits"] == 0, "result zero generic")
    for name, digest in result["files"].items():
        audit.check(builder.sha256(ART / name) == digest, f"result hash {name}")

    local_home_prefix = "/" + "home/"
    secret_markers = ("BEGIN " + "PRIVATE KEY", "BEGIN " + "OPENSSH PRIVATE KEY", "AK" + "IA")
    for name in artifact_names:
        content = (ART / name).read_text(encoding="utf-8")
        audit.check(local_home_prefix not in content and "file://" not in content, f"no local path {name}")
        audit.check(not any(marker in content for marker in secret_markers), f"no credential marker {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_identical_rebuild_files": len(artifact_names),
        "cards": 24,
        "occurrences": 57,
        "boundary_decisions": 13,
        "completed_source_lines": 8,
        "global_newly_completed_lines": 8,
        "v53_lines": 51,
        "v53_tokens": 479,
        "v53_unknown": 69,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
