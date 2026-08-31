#!/usr/bin/env python3
"""Independently rebuild and validate GDT684."""

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
EXP = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt684_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT684 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    expected_generated = {
        "V57_479_POSITION_INFORMATION_AUDIT.tsv",
        "V57_SEMANTIC_DEBT_POSITIONS.tsv",
        "V57_SPECIFICITY_OPEN_POSITIONS.tsv",
        "V57_MECHANICAL_SEMANTIC_DEBT_POSITIONS.tsv",
        "V57_LOW_CONFIDENCE_CARD_POSITIONS.tsv",
        "V57_CARD_INFORMATION_INVENTORY.tsv",
        "V57_51_LINE_INFORMATION_SUMMARY.tsv",
        "SEMANTIC_CLASS_SUMMARY.tsv",
        "STRICT_DEBT_CATEGORY_SUMMARY.tsv",
        "MECHANICAL_DEBT_CLASS_SUMMARY.tsv",
        "DEBT_LAYER_CROSSWALK.tsv",
        "SEMANTIC_SIGNAL_RULES.tsv",
        "PRACTICAL_OPERATION_RULES.tsv",
        "ANCHOR_LAYER_DRIFTS.tsv",
        "OUTSIDE_V57_COMPANION_DEBTS.tsv",
        "V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv",
        "GDT684_SEMANTIC_DEBT_PRIORITY_READER.md",
    }
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(set(result["files"]) == expected_generated, "exact generated artifact inventory")
    for name in [*sorted(expected_generated), "RESULT.json"]:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt684-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"] == result["status"], "rebuilt status")
        for name in [*sorted(expected_generated), "RESULT.json"]:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    positions = read_tsv(ART / "V57_479_POSITION_INFORMATION_AUDIT.tsv")
    debts = read_tsv(ART / "V57_SEMANTIC_DEBT_POSITIONS.tsv")
    specificity = read_tsv(ART / "V57_SPECIFICITY_OPEN_POSITIONS.tsv")
    mechanical = read_tsv(ART / "V57_MECHANICAL_SEMANTIC_DEBT_POSITIONS.tsv")
    low_confidence = read_tsv(ART / "V57_LOW_CONFIDENCE_CARD_POSITIONS.tsv")
    cards = read_tsv(ART / "V57_CARD_INFORMATION_INVENTORY.tsv")
    lines = read_tsv(ART / "V57_51_LINE_INFORMATION_SUMMARY.tsv")
    classes = read_tsv(ART / "SEMANTIC_CLASS_SUMMARY.tsv")
    categories = read_tsv(ART / "STRICT_DEBT_CATEGORY_SUMMARY.tsv")
    mechanical_summary = read_tsv(ART / "MECHANICAL_DEBT_CLASS_SUMMARY.tsv")
    debt_crosswalk = read_tsv(ART / "DEBT_LAYER_CROSSWALK.tsv")
    rules = read_tsv(ART / "SEMANTIC_SIGNAL_RULES.tsv")
    practical_rules = read_tsv(ART / "PRACTICAL_OPERATION_RULES.tsv")
    anchors = read_tsv(ART / "ANCHOR_LAYER_DRIFTS.tsv")
    companion = read_tsv(ART / "OUTSIDE_V57_COMPANION_DEBTS.tsv")
    confidence_watch = read_tsv(ART / "V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv")

    audit.check(len(positions) == 479, "479 position rows")
    keys = {(row["locus"], row["ordinal"]) for row in positions}
    audit.check(len(keys) == 479, "479 unique locus ordinals")
    audit.check(len({row["locus"] for row in positions}) == 51, "51 loci")
    audit.check(len({row["surface"] for row in positions}) == 320, "320 unique surfaces")
    audit.check(len({(row["surface"], row["literal_gloss_de"]) for row in positions}) == 324, "324 surface gloss cards")
    audit.check(all(not row["page"].lower().startswith("f84") for row in positions), "sealed pages absent")
    audit.check(all(row["specificity_open"] in {"0", "1"} for row in positions), "specificity flags binary")
    audit.check(all(row["strict_card_debt"] in {"0", "1"} for row in positions), "strict flags binary")
    audit.check(all(row["mechanical_debt"] in {"0", "1"} for row in positions), "mechanical flags binary")
    audit.check(all(row["low_or_exploratory_card"] in {"0", "1"} for row in positions), "low-confidence flags binary")
    audit.check(sum(int(row["action_licensed"]) for row in positions) == 86, "86 licensed action positions")
    audit.check(sum(int(row["strict_card_debt"]) for row in positions) == 139, "139 strict position flags")
    audit.check(sum(int(row["specificity_open"]) for row in positions) == 335, "335 broad-open position flags")
    audit.check(sum(int(row["mechanical_debt"]) for row in positions) == 172, "172 mechanical-debt position flags")
    audit.check(sum(int(row["low_or_exploratory_card"]) for row in positions) == 30, "30 low-confidence position flags")
    audit.check({(row["locus"], row["ordinal"]) for row in debts} == {(row["locus"], row["ordinal"]) for row in positions if row["strict_card_debt"] == "1"}, "strict subset exact")
    audit.check({(row["locus"], row["ordinal"]) for row in specificity} == {(row["locus"], row["ordinal"]) for row in positions if row["specificity_open"] == "1"}, "broad subset exact")
    audit.check({(row["locus"], row["ordinal"]) for row in mechanical} == {(row["locus"], row["ordinal"]) for row in positions if row["mechanical_debt"] == "1"}, "mechanical subset exact")
    audit.check({(row["locus"], row["ordinal"]) for row in low_confidence} == {(row["locus"], row["ordinal"]) for row in positions if row["low_or_exploratory_card"] == "1"}, "low-confidence subset exact")
    audit.check(len(debts) == 139, "139 strict debt rows")
    audit.check(len(specificity) == 335, "335 broad debt rows")
    audit.check(len(mechanical) == 172, "172 mechanical debt rows")
    audit.check(len(low_confidence) == 30, "30 low-confidence rows")
    audit.check(len(cards) == 324, "324 inventory cards")
    audit.check(len(lines) == 51, "51 line summaries")
    audit.check(sum(int(row["token_count"]) for row in lines) == 479, "479 summarized positions")
    audit.check(sum(int(row["licensed_action_positions"]) for row in lines) == 86, "86 summarized actions")

    expected_classes = {
        "A1_LICENSED_OPERATION": 71,
        "A2_IDENTITY_BEARING_ENTITY": 73,
        "B1_LICENSED_OPERATION_WITH_GENERIC_OBJECT": 13,
        "B2_LICENSED_OPERATION_WITH_REGISTER_WRAPPER": 2,
        "C1_FUNCTIONAL_MATERIAL_ROLE_ONLY": 165,
        "C2_STATE_WITHOUT_OBJECT": 72,
        "C3_VALUE_WITHOUT_AXIS_OR_OBJECT": 22,
        "D1_UNRESOLVED_COMPONENT": 20,
        "D2_STRUCTURAL_OR_REGISTER_META": 21,
        "D3_GENERIC_CARRIER": 19,
        "D4_UNLICENSED_LITERAL_ACTION": 1,
    }
    observed_classes = Counter(row["primary_class"] for row in positions)
    audit.check(observed_classes == expected_classes, "exact disjoint information classes")
    audit.check({row["primary_class"]: int(row["positions"]) for row in classes} == expected_classes, "class summary exact")
    audit.check(sum(expected_classes[name] for name in ["A1_LICENSED_OPERATION", "B1_LICENSED_OPERATION_WITH_GENERIC_OBJECT", "B2_LICENSED_OPERATION_WITH_REGISTER_WRAPPER"]) == 86, "action classes partition licensed actions")
    audit.check(Counter(row["debt_severity"] for row in positions) == {"CRITICAL": 61, "MAJOR": 274, "NONE": 144}, "severity census")
    audit.check(result["position_classes"] == dict(sorted(expected_classes.items())), "result class binding")
    audit.check(result["severity"] == {"CRITICAL": 61, "MAJOR": 274, "NONE": 144}, "result severity binding")

    expected_categories = {
        "GENERIC_CARRIER": 10,
        "VALUE_DIMENSION_OPEN": 19,
        "UNRESOLVED_BINDING": 20,
        "STRUCTURAL_META_CARD": 11,
        "OPEN_TAXONOMY_OR_MATERIAL_ALTERNATIVE": 16,
        "GENERIC_DRUG_HEAD": 21,
        "RAW_CLASS_WITHOUT_IDENTITY": 20,
        "OPAQUE_FORM_CODE": 12,
        "QUANTITY_OR_UNIT_WITHOUT_HEAD": 11,
    }
    audit.check({row["strict_debt_category"]: int(row["positions"]) for row in categories} == expected_categories, "strict category counts")
    audit.check(sum(expected_categories.values()) == 140, "140 strict category memberships")
    audit.check(sum(len(row["strict_debt_categories"].split("|")) for row in debts) == 140, "position category memberships exact")
    overlaps = [row for row in debts if "|" in row["strict_debt_categories"]]
    audit.check(len(overlaps) == 1 and overlaps[0]["surface"] == "oidal", "only oidal overlaps strict categories")
    audit.check(result["strict_card_debt_positions"] == 139, "result strict debt binding")
    audit.check(result["strict_debt_category_memberships"] == 140, "result membership binding")
    audit.check(result["broad_specificity_open_positions"] == 335, "result broad binding")

    expected_mechanical = {
        "OPEN_COMPOSITION": 20,
        "NON_SINGLE_GLOSS": 44,
        "STRUCTURAL_META_AS_VALUE": 18,
        "HARD_GENERIC_CARRIER": 47,
        "STATE_ONLY_NO_OBJECT": 65,
    }
    observed_mechanical = Counter(
        flag for row in positions for flag in row["mechanical_debt_flags"].split("|") if flag != "NONE"
    )
    audit.check(observed_mechanical == expected_mechanical, "exact mechanical debt class counts")
    audit.check({row["mechanical_debt_class"]: int(row["positions"]) for row in mechanical_summary} == expected_mechanical, "mechanical summary exact")
    audit.check(sum(expected_mechanical.values()) == 194, "194 overlapping mechanical memberships")
    audit.check(len(debt_crosswalk) == 8, "complete three-layer debt crosswalk")
    audit.check(sum(int(row["positions"]) for row in debt_crosswalk) == 479, "crosswalk partitions all positions")
    cross_counts = {
        (int(row["strict_curated_queue"]), int(row["broad_specificity_open"]), int(row["mechanical_visible_alarm"])): int(row["positions"])
        for row in debt_crosswalk
    }
    audit.check(cross_counts == {
        (0, 0, 0): 108, (0, 0, 1): 12, (0, 1, 0): 143, (0, 1, 1): 77,
        (1, 0, 0): 9, (1, 0, 1): 15, (1, 1, 0): 47, (1, 1, 1): 68,
    }, "exact debt-layer crosswalk")
    audit.check(result["mechanical_visible_debt"] == {
        "union_positions": 172,
        "class_memberships": 194,
        "classes": expected_mechanical,
    }, "result mechanical debt binding")
    audit.check(result["three_debt_layer_union_positions"] == 371, "371 positions carry at least one of three debt signals")
    audit.check(result["four_layer_union_with_low_confidence_positions"] == 381, "381 positions carry debt or low-confidence provenance")
    audit.check(result["no_debt_or_low_confidence_signal_positions"] == 98, "98 positions carry no debt or low-confidence signal")

    expected_low_keys = {
        ("f102v2.3", "1"), ("f105r.2", "2"), ("f105r.31", "1"), ("f105r.31", "2"),
        ("f105r.31", "3"), ("f105r.31", "5"), ("f105r.31", "6"), ("f105v.14", "7"),
        ("f10r.2", "7"), ("f112v.10", "4"), ("f113v.12", "3"), ("f113v.12", "5"),
        ("f114r.24", "4"), ("f114r.24", "10"), ("f114v.36", "2"), ("f115r.1", "1"),
        ("f115r.1", "8"), ("f26r.2", "3"), ("f26r.2", "4"), ("f26r.2", "9"),
        ("f27r.9", "7"), ("f77v.7", "3"), ("f80r.17", "1"), ("f80r.17", "13"),
        ("f83v.12", "3"), ("f83v.12", "4"), ("f86v5.4", "1"), ("f86v6.25", "7"),
        ("f86v6.31", "11"), ("f86v6.5", "11"),
    }
    audit.check({(row["locus"], row["ordinal"]) for row in low_confidence} == expected_low_keys, "exact 30 low-confidence keys")
    audit.check(len({(row["surface"], row["literal_gloss_de"]) for row in low_confidence}) == 28, "28 low-confidence cards")
    audit.check(Counter(row["low_confidence_sources"] for row in low_confidence) == {
        "GDT671": 1, "GDT674": 4, "GDT677": 1, "GDT678": 4,
        "GDT679": 1, "GDT680": 7, "GDT681": 12,
    }, "low-confidence source distribution")
    audit.check(all(row["low_confidence_labels"] == "LOW" for row in low_confidence if row["low_confidence_sources"] == "GDT674"), "GDT674 LOW labels")
    audit.check(all("EXPLORATORY" in row["low_confidence_labels"] for row in low_confidence if row["low_confidence_sources"] != "GDT674"), "exploratory labels retained")
    audit.check(not any(row["locus"] == "f115r.1" and row["ordinal"] == "5" for row in low_confidence), "rewritten cheop compound part not falsely joined")
    prior_clean_low = [
        row for row in low_confidence
        if row["strict_card_debt"] == "0" and row["specificity_open"] == "0" and row["mechanical_debt"] == "0"
    ]
    audit.check(len(prior_clean_low) == 10, "ten low-confidence cards newly reduce the clean remainder")
    audit.check(result["low_or_exploratory_card_positions"] == 30, "result low-confidence positions")
    audit.check(result["low_or_exploratory_surface_gloss_cards"] == 28, "result low-confidence cards")

    d4 = [row for row in positions if row["primary_class"] == "D4_UNLICENSED_LITERAL_ACTION"]
    audit.check(len(d4) == 1, "one literal action mismatch")
    audit.check((d4[0]["locus"], d4[0]["ordinal"], d4[0]["surface"]) == ("f26r.2", "1", "dchey"), "dchey exact mismatch anchor")
    dchey = [row for row in positions if row["surface"] == "dchey"]
    audit.check(len(dchey) == 14, "fourteen dchey positions")
    audit.check(sum(int(row["action_licensed"]) for row in dchey) == 9, "nine licensed dchey actions plus one literal-action metadata conflict")
    audit.check(sum(row["surface"] == "olkar" for row in debts) == 16, "sixteen olkar debts")
    audit.check(sum(row["surface"] == "olam" for row in debts) == 4, "four olam debts")
    audit.check(Counter(row["surface"] for row in positions if row["surface"] in {"chol", "shol", "tol"}) == {"chol": 6, "shol": 1, "tol": 1}, "state plus OL carrier counts")

    expected_anchor_ids = {f"G684-A00{i}" for i in range(1, 8)}
    audit.check(len(anchors) == 7, "seven manual anchor drifts")
    audit.check({row["anchor_id"] for row in anchors} == expected_anchor_ids, "anchor IDs exact")
    audit.check(next(row for row in anchors if row["anchor_id"] == "G684-A005")["locus"] == "f86v3.13", "qodaiin anchor locus")
    audit.check(next(row for row in anchors if row["anchor_id"] == "G684-A005")["drift_class"] == "QUALITY_TO_QUANTITY_SWAP", "qodaiin axis drift")
    for anchor in anchors:
        members = [row for row in positions if row["locus"] == anchor["locus"] and int(anchor["start_ordinal"]) <= int(row["ordinal"]) <= int(anchor["end_ordinal"])]
        audit.check(len(members) == int(anchor["end_ordinal"]) - int(anchor["start_ordinal"]) + 1, f"anchor span exists {anchor['anchor_id']}")
        audit.check(all(anchor["anchor_id"] in row["anchor_drift_ids"].split("|") for row in members), f"anchor attached {anchor['anchor_id']}")

    audit.check(sum(int(row["extra_practical_operation_count"]) for row in lines) == 74, "74 regex-defined extra operation label line pairs")
    audit.check(sum(int(row["extra_practical_operation_count"]) > 0 for row in lines) == 29, "29 prose operation drift lines")
    audit.check(result["action_layer"] == {
        "anchor_layer_drifts": 7,
        "extra_practical_operation_label_line_pairs": 74,
        "lines_with_extra_practical_operations": 29,
    }, "result action layer binding")
    audit.check(len(rules) == 44, "twenty semantic and twenty-four action rules")
    audit.check(Counter(row["channel"] for row in rules) == {"SEMANTIC": 20, "ACTION": 24}, "signal rule channels")
    audit.check(len(practical_rules) == 31, "thirty-one practical operation lemmas")
    audit.check(len({row["operation_lemma"] for row in practical_rules}) == 31, "practical operation lemmas unique")
    f105r2 = next(row for row in lines if row["locus"] == "f105r.2")
    audit.check(f105r2["extra_practical_operation_labels"] == "bereitstellen|bringen|halten|trocknen", "f105r.2 extra operation labels")
    f107r2 = next(row for row in lines if row["locus"] == "f107r.2")
    audit.check(f107r2["extra_practical_operation_labels"] == "stellen", "f107r.2 extra operation label")

    expected_watch = {
        ("f112r.36", "2"), ("f80r.17", "8"), ("f80v.35", "9"),
        ("f86v5.2", "9"), ("f86v6.4", "4"),
    }
    audit.check(len(confidence_watch) == 5, "five provisional learned OL positions")
    audit.check({(row["locus"], row["ordinal"]) for row in confidence_watch} == expected_watch, "exact provisional OL key set")
    audit.check(all(row["working_gloss_de"] == "Grundansatz" and row["source_role"] == "LEARNED_OL_BASE" for row in confidence_watch), "learned OL role visible")
    audit.check(all(row["source_strength"] == "MEDIUM" and row["specificity_open"] == "1" for row in confidence_watch), "OL confidence and broad debt visible")
    audit.check(all(row["strict_debt_inclusion"].startswith("NO__") for row in confidence_watch), "OL watch distinct from strict renderer debt")
    audit.check(all((row["locus"], row["ordinal"]) not in {(debt["locus"], debt["ordinal"]) for debt in debts} for row in confidence_watch), "OL watch excluded from strict queue")
    audit.check(result["provisional_semantic_confidence_watch_positions"] == 5, "result OL watch binding")
    audit.check(result["strict_semantic_debt_with_provisional_ol_positions"] == 144, "139 curated plus five provisional OL semantic debts")
    audit.check(result["mechanical_plus_provisional_ol_union_positions"] == 177, "172 mechanical plus five disjoint provisional OL debts")

    audit.check(len(companion) == 1, "one outside V57 companion debt")
    audit.check((companion[0]["locus"], companion[0]["ordinal"], companion[0]["surface"], companion[0]["in_v57"]) == ("f111v.18", "11", "l", "0"), "outside free l exact")
    audit.check(all(row["locus"] != "f111v.18" for row in positions), "outside companion absent from denominator")
    audit.check(result["outside_v57_companion_debts"] == 1, "result companion binding")

    audit.check(result["basis"] == {
        "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "licensed_action_positions": 86,
        "new_pages_opened": 0, "unique_surface_gloss_cards": 324, "unique_surfaces": 320,
        "v57_lines": 51, "v57_positions": 479,
    }, "result basis exact")
    audit.check(result["next_repair_family"]["family"] == "CH_SH_T_PLUS_OL_STATE_CARRIER", "next carrier family")
    audit.check(result["next_repair_family"]["v57_positions"] == {"chol": 6, "shol": 1, "tol": 1}, "next family V57 counts")
    audit.check(result["next_repair_family"]["status"] == "PREDICTION_TO_TEST__NOT_YET_EXPORTED", "prediction not exported")
    audit.check(result["status"] == "PASS_479_POSITION_INFORMATION_CENSUS__FORMAL_COMPLETENESS_NOT_SEMANTIC_COMPLETENESS", "pass status")
    audit.check("No language" in result["claim_ceiling"] and "new page" in result["claim_ceiling"], "claim ceiling retained")

    for name, digest in result["files"].items():
        audit.check(sha256(ART / name) == digest, f"hash bound {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_rebuilds": len(expected_generated) + 1,
        "v57_positions": 479,
        "strict_card_debt_positions": 139,
        "broad_specificity_open_positions": 335,
        "mechanical_visible_debt_positions": 172,
        "low_or_exploratory_card_positions": 30,
        "four_layer_union_positions": 381,
        "no_debt_or_low_confidence_signal_positions": 98,
        "provisional_semantic_confidence_watch_positions": 5,
        "sealed_pages_absent": True,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
