#!/usr/bin/env python3
"""Independently rebuild and validate GDT681."""

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
EXP = ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V54_PATH = ROOT / "experiments/yolo/gdt680_eight_four_hole_family_completion/artifacts/V54_51_LINE_READER.tsv"
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
    spec = importlib.util.spec_from_file_location("gdt681_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT681 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "INHERITED_CARD_REUSE.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "BOUNDARY_DECISIONS.tsv",
        "SIX_COMPLETED_LINES_V55.tsv",
        "V55_51_LINE_READER.tsv",
        "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT681_SIX_COMPLETED_PRACTICAL_READER.md",
        "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt681-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_"), "rebuilt status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "TARGET_FAMILY_CARDS.tsv")
    reuse = read_tsv(ART / "INHERITED_CARD_REUSE.tsv")
    occurrences = read_tsv(ART / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv")
    boundaries = read_tsv(ART / "BOUNDARY_DECISIONS.tsv")
    completed = read_tsv(ART / "SIX_COMPLETED_LINES_V55.tsv")
    v55 = read_tsv(ART / "V55_51_LINE_READER.tsv")
    global_closed = read_tsv(ART / "GLOBAL_NEWLY_COMPLETED_LINES.tsv")
    predictions = read_tsv(ART / "FAMILY_PREDICTIONS.tsv")
    analogs = read_tsv(ART / "HISTORICAL_ANALOG_ATLAS.tsv")
    v54 = read_tsv(V54_PATH)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 29, "twenty-nine new cards")
    audit.check(len({row["surface"] for row in cards}) == 29, "unique cards")
    audit.check(len(reuse) == 1 and reuse[0]["surface"] == "chepy", "one inherited chepy card")
    audit.check(reuse[0]["source_experiment"] == "GDT680", "chepy source")
    audit.check(reuse[0]["working_meaning_de"] == "Trockenpulver in Grundform", "chepy unchanged")
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    audit.check(sum(expected_counts.values()) == 104, "card counts total 104")
    card_by_surface = {row["surface"]: row for row in cards}
    audit.check(card_by_surface["aiir"]["working_meaning_de"] == "Drogenfraktion III", "aiir ladder")
    audit.check(card_by_surface["aiir"]["observed_occurrences"] == "20", "aiir twenty contexts")
    audit.check(card_by_surface["ytedy"]["observed_occurrences"] == "24", "ytedy family")
    audit.check(card_by_surface["ytedy"]["action_license"] == "1", "ytedy process")
    audit.check(card_by_surface["ls"]["observed_occurrences"] == "12", "ls family")
    audit.check(card_by_surface["shx"]["working_meaning_de"] == "eingeweichtes Gummiharz", "shx concrete candidate")
    audit.check(card_by_surface["shx"]["confidence"] == "LOW_EXPLORATORY", "shx visibly weak")
    audit.check("Wurzelpulver" in card_by_surface["ypchesy"]["strongest_rival_de"], "seed root rival")
    audit.check(card_by_surface["tchedaiin"]["composition"] == "T_COLD+CHEDAIIN_DRY_DOSE_III", "cold dry triple dose")
    audit.check(card_by_surface["cpheesy"]["working_meaning_de"].endswith("Arzneikompositum"), "composite preparation")
    audit.check(card_by_surface["sail"]["working_meaning_de"] == "Saatgut, Charge II", "sail seed charge")
    audit.check(card_by_surface["oram"]["working_meaning_de"] == "eine Maßportion Ansatz", "oram measure portion")
    audit.check(sum(int(row["action_license"]) for row in cards) == 10, "ten action cards")

    audit.check(len(occurrences) == 104, "104 occurrence rows")
    audit.check(len({(row["locus"], row["ordinal"]) for row in occurrences}) == 104, "unique occurrence keys")
    audit.check(Counter(row["surface"] for row in occurrences) == expected_counts, "occurrence distribution")
    audit.check(len({row["locus"] for row in occurrences}) == 77, "77 target loci")
    audit.check(len({row["page"] for row in occurrences}) == 49, "49 target pages")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(all(not GENERIC.search(row["context_after_de"]) for row in occurrences), "no generic occurrence filler")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {
        "BOTH_EXACT": 60,
        "IT2A_ONLY_EXACT": 23,
        "RF1B_ONLY_EXACT": 11,
        "NEITHER_EXACT": 10,
    }, "reader support distribution")
    audit.check(sum(row["context_decision"] == "HOLD_SAME_CARD" for row in occurrences) == 60, "60 fully exact holds")

    audit.check(len(boundaries) == 44, "forty-four reader decisions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" for row in boundaries) == 10, "ten neither-exact decisions")
    source_ls = next(row for row in boundaries if row["locus"] == "f26r.2" and row["surface"] == "ls")
    audit.check(source_ls["it2a_render"] == source_ls["rf1b_render"] == "lr", "source ls bilateral lr")
    audit.check(source_ls["applied_render_de"] == "Wurzelholz", "source ls root-wood override")
    repaired_ytedy = next(row for row in boundaries if row["locus"] == "f104v.14")
    audit.check(repaired_ytedy["it2a_render"] == repaired_ytedy["rf1b_render"] == "ytchedy", "ytedy bilateral dry repair")
    cheop = next(row for row in boundaries if row["surface"] == "cheop")
    audit.check(cheop["it2a_render"] == "cheopolteeedy" and cheop["rf1b_render"] == "cheopol", "cheop bilateral join")
    audit.check("Pulverstoff" in cheop["applied_render_de"], "cheop material override")
    sheeey = next(row for row in boundaries if row["locus"] == "f115v.34" and row["surface"] == "sheeey")
    audit.check(sheeey["it2a_render"] == "sheckeey" and sheeey["rf1b_render"] == "sheckhey", "sheeey bilateral CKH repair")
    audit.check("Arzneikompositum" in sheeey["applied_render_de"], "sheeey local composite override")

    audit.check(len(completed) == 6, "six completed source lines")
    audit.check(len({row["locus"] for row in completed}) == 6, "unique source loci")
    audit.check(sum(len(row["closed_surfaces"].split("|")) for row in completed) == 30, "30 source slots")
    audit.check(sum(len([] if row["added_action_ordinals"] == "NONE" else row["added_action_ordinals"].split("|")) for row in completed) == 10, "ten new source actions")
    for row in completed:
        tokens = row["zl3b_line"].split()
        chunks = row["aligned_line_de"].rstrip(".").split(" · ")
        literals = row["new_literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(chunks) == len(literals) == int(row["token_count"]), f"token alignment {row['locus']}")
        audit.check("⟦" not in row["aligned_line_de"] and ":?]" not in row["new_literal_token_glosses_de"], f"line closed {row['locus']}")
        audit.check(not GENERIC.search(row["aligned_line_de"]), f"no generic aligned filler {row['locus']}")
        audit.check(not GENERIC.search(row["practical_translation_de"]), f"no generic practical filler {row['locus']}")
    f104 = next(row for row in completed if row["locus"] == "f104v.2")
    audit.check("ein Maß nehmen, erhitzen und fertigstellen" in f104["aligned_line_de"], "f104 concrete measure heat action")
    f105 = next(row for row in completed if row["locus"] == "f105r.31")
    audit.check("eingeweichtes Gummiharz" in f105["aligned_line_de"], "f105 resin candidate")
    f114 = next(row for row in completed if row["locus"] == "f114r.24")
    audit.check("Drogenfraktion III" in f114["aligned_line_de"] and "Pulverzubereitung" in f114["aligned_line_de"], "f114 fraction powder register")
    f115 = next(row for row in completed if row["locus"] == "f115r.1")
    audit.check("erste Blütenfraktion abmessen" in f115["aligned_line_de"], "f115 flower action")
    f26 = next(row for row in completed if row["locus"] == "f26r.2")
    audit.check(f26["aligned_line_de"].endswith("Wurzelholz."), "f26 bilateral root-wood ending")
    f86 = next(row for row in completed if row["locus"] == "f86v5.4")
    audit.check("Samenpulver" in f86["aligned_line_de"] and "Trockenpulver in Grundform" in f86["aligned_line_de"], "f86 seed powder and reused chepy")

    audit.check(len(v55) == 51, "51 V55 lines")
    audit.check(sum(int(row["token_count"]) for row in v55) == 479, "479 tokens")
    audit.check(sum(int(row["new_v55_positions"]) for row in v55) == 30, "30 V55 positions")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v55) == 7, "seven V55 gaps")
    audit.check(sum(row["complete"] == "1" for row in v55) == 50, "50 complete V55 lines")
    audit.check(Counter(int(row["residual_unknown_positions"]) for row in v55) == {0: 50, 7: 1}, "V55 gap distribution")
    audit.check(sum(int(row["action_positions"]) for row in v55) == 85, "85 V55 actions")
    audit.check(Counter(row["line_mode"] for row in v55) == {
        "ACTION_SEQUENCE": 16,
        "MIXED_RECORD": 23,
        "NOMINAL_REGISTER": 6,
        "QUANTITY_LABEL": 6,
    }, "V55 modes")
    audit.check(all(not GENERIC.search(row["aligned_line_de"]) for row in v55), "V55 aligned no generic")
    audit.check(all(not GENERIC.search(row["practical_translation_de"]) for row in v55), "V55 practical no generic")
    v54_by_locus = {row["locus"]: row for row in v54}
    completed_loci = {row["locus"] for row in completed}
    for row in v55:
        old = v54_by_locus[row["locus"]]
        if row["locus"] not in completed_loci:
            audit.check(row["aligned_line_de"] == old["aligned_line_de"], f"untouched aligned V54 line {row['locus']}")
            audit.check(row["literal_token_glosses_de"] == old["literal_token_glosses_de"], f"untouched literal V54 line {row['locus']}")
            audit.check(row["practical_translation_de"] == old["practical_translation_de"], f"untouched practical V54 line {row['locus']}")

    audit.check(len(global_closed) == 10, "ten global closures")
    audit.check(completed_loci.issubset({row["locus"] for row in global_closed}), "global closures include source")
    audit.check({row["locus"] for row in global_closed} - completed_loci == {"f33v.11", "f75v.53", "f79r.17", "f88r.13"}, "four extra global closures")
    audit.check(all(":?]" not in row["after_literal_de"] for row in global_closed), "global rows closed")
    audit.check(len(predictions) == 8 and len({row["prediction_id"] for row in predictions}) == 8, "eight predictions")
    audit.check(len(analogs) == 7, "seven analogs")
    audit.check(all(row["source_url"].startswith("https://") for row in analogs), "analog URLs")
    audit.check(all(row["scope_limit"] for row in analogs), "analog limits")

    audit.check(result["status"] == "PASS_29_NEW_CARDS__104_CONTEXTS_HOLD__1_CARD_REUSED__6_V55_LINES_CLOSED__V55_7_OPEN", "result status")
    audit.check(result["basis"]["cross_guard"] == {"selected": 77, "skipped_forbidden": 98, "skipped_not_allowed": 5211}, "guard counts")
    audit.check(result["global_overlay"] == {
        "unknown_positions_before": 7677,
        "unknown_positions_after": 7573,
        "new_assigned_positions": 104,
        "complete_lines_before": 1429,
        "complete_lines_after": 1439,
        "newly_completed_lines": 10,
        "newly_completed_outside_v54_source": ["f33v.11", "f75v.53", "f79r.17", "f88r.13"],
    }, "global result")
    audit.check(result["v55_reader"]["unknown_after"] == 7, "result V55 gaps")
    audit.check(result["v55_reader"]["assigned_after"] == 472, "result V55 assigned")
    audit.check(result["v55_reader"]["complete_after"] == 50, "result V55 complete")
    audit.check(result["v55_reader"]["new_action_positions"] == 10, "result new actions")
    audit.check(result["v55_reader"]["hard_generic_hits"] == 0, "result zero generic")
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
        "cards": 29,
        "inherited_cards_reused": 1,
        "occurrences": 104,
        "boundary_decisions": 44,
        "completed_source_lines": 6,
        "global_newly_completed_lines": 10,
        "v55_lines": 51,
        "v55_tokens": 479,
        "v55_unknown": 7,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
