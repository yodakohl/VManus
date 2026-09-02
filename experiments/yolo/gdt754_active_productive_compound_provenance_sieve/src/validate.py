#!/usr/bin/env python3
"""Invariant and byte-replay validation for GDT754."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
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
BASE = Path("experiments/yolo/gdt754_active_productive_compound_provenance_sieve")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__172_ACTIVE_PRODUCTIVE_COMPOUNDS__889_SOURCE_PROSE_CELLS_159_PAGES__"
    "686_READER_EXACT__168_COMPOSITION_AXES_ONLY__1_LOCAL_ROLE_PATCH_FAMILY_42_CELLS__"
    "1_FORM_ANALOGY_ONLY__2_CORRECTED_PAIR_HYPOTHESES__12_GDT737_QUARANTINES__"
    "ZERO_SOURCE_LITERAL_PROSE_SPOKEN__172_BACKGROUND_HYPOTHESES_PRESERVED__"
    "24_HISTORICAL_BRIDGE_TARGETS__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv",
    "LATER_WHOLE_ROLE_EVIDENCE.tsv",
    "PROVENANCE_SIEVE_172_DECISIONS.tsv",
    "CURRENT_SOURCE_PROSE_POSITION_PATCH.tsv",
    "TOP_24_HISTORICAL_VOCABULARY_BRIDGE_DECK.tsv",
    "GDT754_PRODUCTIVE_COMPOUND_READER.md",
    "RESULT.json",
)
BRIDGE_SURFACES = [
    "air", "lkaiin", "opchedy", "okeol", "qokeol", "olchedy", "chees",
    "qopchedy", "okam", "qoaiin", "lky", "ykedy", "orain", "chky",
    "qockhey", "ychor", "cthody", "ykol", "olar", "otaly", "qolchedy",
    "chdam", "olchy", "qopchey",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT754", "manifest id")
    check(manifest["slug"] == "active_productive_compound_provenance_sieve", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["dependencies"] == [
        "GDT664", "GDT666", "GDT734", "GDT737", "GDT738", "GDT745",
        "GDT746", "GDT748", "GDT749", "GDT750", "GDT753",
    ], "manifest dependencies")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest claim ceiling")
    check(manifest["validation"] == {
        "artifact": str(VALIDATION_REL), "status": "PASS",
    }, "validation contract")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    inventory = read_tsv(art / GENERATED[0])
    evidence = read_tsv(art / GENERATED[1])
    decisions = read_tsv(art / GENERATED[2])
    patches = read_tsv(art / GENERATED[3])
    bridge = read_tsv(art / GENERATED[4])
    check(len(inventory) == 172, "172 inventory rows")
    check(len(evidence) == 16, "16 later evidence rows")
    check(len(decisions) == 172, "172 decision rows")
    check(len(patches) == 889, "889 position patches")
    check(len(bridge) == 24, "24 bridge rows")
    check(len({row["surface"] for row in inventory}) == 172, "inventory unique surfaces")
    check(len({row["surface"] for row in decisions}) == 172, "decision unique surfaces")
    check(len({row["gdt754_patch_id"] for row in patches}) == 889, "patch ids unique")

    check(Counter(row["source_gdt"] for row in inventory) == Counter({
        "GDT664": 65, "GDT666": 107,
    }), "source gdt counts")
    check({source: sum(int(row["current_source_prose_active_cells"]) for row in inventory if row["source_gdt"] == source) for source in ("GDT664", "GDT666")} == {
        "GDT664": 449, "GDT666": 440,
    }, "source cell counts")
    check(sum(int(row["source_dictionary_occurrences"]) for row in inventory) == 889, "source occurrence sum")
    check(sum(int(row["current_cache_cells"]) for row in inventory) == 889, "cache cell sum")
    check(sum(int(row["current_reader_exact_cells"]) for row in inventory) == 686, "reader exact sum")
    check(sum(int(row["current_source_prose_active_cells"]) for row in inventory) == 889, "source prose active sum")
    check(Counter(row["current_confidence"] for row in inventory) == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 54,
        "W1_WEAK_WORKING": 28,
        "W2_PROVISIONAL_WORKING": 43,
        "W3_SOLID_WORKING_THEORY": 47,
    }), "confidence census")
    check(Counter(row["source_strength"] for row in inventory) == Counter({
        "LOW_EXPLORATORY": 54,
        "MEDIUM_EXACT_WHOLE": 74,
        "STRONG_PRACTICAL_OR_COMPOSITIONAL": 44,
    }), "source strength census")
    for row in inventory:
        surface = row["surface"]
        check(row["source_card_type"] == "PRODUCTIVE_COMPOUND", f"productive source {surface}")
        check(row["source_composition_axes"] != "NONE", f"composition axes {surface}")
        check(int(row["current_cache_cells"]) > 0, f"active footprint {surface}")
        check(row["literal_identity"] == "OPEN", f"inventory literal open {surface}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"inventory no export {surface}")

    check(Counter(row["later_source"] for row in evidence) == Counter({
        "GDT737": 12, "GDT738": 2, "GDT753": 2,
    }), "evidence source counts")
    check({row["surface"] for row in evidence if int(row["strength_tier_0_4"]) > 0} == {
        "lkaiin", "lky", "qokeol", "okeol",
    }, "four positive later surfaces")
    check(sum(row["evidence_scope"] == "NEGATIVE_LITERAL_PROVENANCE" for row in evidence) == 12, "twelve quarantine evidence rows")
    check(all(row["literal_identity"] == "OPEN" for row in evidence), "evidence literal open")
    check(all(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in evidence), "evidence no export")

    check(Counter(row["renderer_disposition"] for row in decisions) == Counter({
        "COMPOSITION_AXES_HYPOTHESIS_ONLY": 168,
        "CORRECTED_PAIR_SHARED_ROLE_HYPOTHESIS": 2,
        "FORM_ANALOGY_ROLE_HYPOTHESIS_ONLY": 1,
        "GLOBAL_COMPOSITION_HYPOTHESIS_PLUS_LOCAL_ROLE_PATCH": 1,
    }), "decision disposition census")
    decision_map = {row["surface"]: row for row in decisions}
    check(decision_map["qokeol"]["current_working_whole_default_de"] == "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen", "qokeol corrected")
    check(decision_map["okeol"]["current_working_whole_default_de"] == "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen", "okeol corrected")
    check(decision_map["lkaiin"]["renderer_disposition"] == "GLOBAL_COMPOSITION_HYPOTHESIS_PLUS_LOCAL_ROLE_PATCH", "lkaiin local")
    check(decision_map["lkaiin"]["later_role_axes_selected"] == "HOT|LEVEL_III", "lkaiin later axes")
    check(decision_map["lky"]["renderer_disposition"] == "FORM_ANALOGY_ROLE_HYPOTHESIS_ONLY", "lky analogy")
    check(decision_map["lky"]["later_role_axes_selected"] == "HOT", "lky hot")
    check(decision_map["air"]["current_working_whole_default_de"] == "Arbeitshypothese: Index/Stufe II, Teil-/Fraktionsfeld; genaue Ganzformbedeutung offen", "air compact default")
    for row in decisions:
        surface = row["surface"]
        check(row["source_literal_prose_spoken_after_gdt754"] == "0", f"old prose silent {surface}")
        check(bool(row["current_working_whole_default_de"]), f"nonempty default {surface}")
        check(bool(row["retained_background_hypothesis_de"]), f"background preserved {surface}")
        check(row["literal_identity"] == "OPEN", f"decision literal open {surface}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"decision no export {surface}")

    check(Counter(row["patch_scope"] for row in patches) == Counter({
        "GDT754_WHOLE_DEFAULT": 847,
        "GDT738_OCCURRENCE_ROLE_PRESERVED": 42,
    }), "patch scope counts")
    check(sum(row["reader_exact"] == "1" for row in patches) == 686, "patch reader exact count")
    check(len({row["page"] for row in patches}) == 159, "patch 159 pages")
    for row in patches:
        patch_id = row["gdt754_patch_id"]
        check(not row["page"].startswith("f84"), f"sealed page absent {patch_id}")
        words = row["written_line_eva"].split()
        check(words[int(row["token_ordinal"]) - 1] == row["surface"], f"patch coordinate {patch_id}")
        check(row["old_source_prose_de"] != row["gdt754_render_de"], f"patch changes prose {patch_id}")
        check(bool(row["background_hypothesis_de"]), f"patch background {patch_id}")
        check(row["literal_identity"] == "OPEN", f"patch literal open {patch_id}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"patch no export {patch_id}")

    check([row["surface"] for row in bridge] == BRIDGE_SURFACES, "bridge exact ranking")
    check([int(row["bridge_rank"]) for row in bridge] == list(range(1, 25)), "bridge rank sequence")
    for row in bridge:
        check(row["comparison_unit"] == "EXACT_COMPLETE_SURFACE_ONLY", f"bridge whole only {row['surface']}")
        check(row["eva_initial_or_substring_value_allowed"] == "0", f"bridge no substring {row['surface']}")
        check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0", f"bridge literal {row['surface']}")
        check(row["component_export_credit"] == "0", f"bridge no component {row['surface']}")

    reader = (art / GENERATED[5]).read_text(encoding="utf-8")
    check("**172**" in reader and "**889**" in reader, "reader scope")
    check("COMPOSITION_AXES_HYPOTHESIS_ONLY | 168" in reader, "reader 168")
    check("`air` | 56/35" in reader, "reader air")
    check("does not read EVA characters as Latin initials" in reader, "reader no initials")

    result = json.loads((art / GENERATED[6]).read_text(encoding="utf-8"))
    check(result["schema"] == "GDT754_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {
        "active_gdt664_gdt666_productive_compound_surfaces": 172,
        "current_cache_cells_on_target_surfaces": 889,
        "current_reader_exact_cells_on_target_surfaces": 686,
        "current_source_prose_active_cells": 889,
        "current_source_prose_active_pages": 159,
        "gdt737_negative_quarantine_surfaces": 12,
        "historical_bridge_deck": 24,
        "later_evidence_rows": 16,
        "later_positive_evidence_surfaces": 4,
        "source_dictionary_occurrence_sum": 889,
    }, "result scope")
    check(result["disposition_counts"] == {
        "COMPOSITION_AXES_HYPOTHESIS_ONLY": 168,
        "CORRECTED_PAIR_SHARED_ROLE_HYPOTHESIS": 2,
        "FORM_ANALOGY_ROLE_HYPOTHESIS_ONLY": 1,
        "GLOBAL_COMPOSITION_HYPOTHESIS_PLUS_LOCAL_ROLE_PATCH": 1,
    }, "result disposition")
    check(result["later_evidence_source_counts"] == {
        "GDT737": 12, "GDT738": 2, "GDT753": 2,
    }, "result evidence sources")
    check(result["renderer_correction"] == {
        "background_composition_hypotheses_preserved": 172,
        "position_patch_scope_counts": {
            "GDT738_OCCURRENCE_ROLE_PRESERVED": 42,
            "GDT754_WHOLE_DEFAULT": 847,
        },
        "position_patches": 889,
        "source_literal_prose_cells_spoken_after_gdt754": 0,
        "source_literal_prose_surfaces_spoken_after_gdt754": 0,
    }, "result renderer")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"] == {
        "component_export_credit": 0,
        "confirmed_lexemes": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
        "historical_word_matches": 0,
        "new_pages": 0,
        "plaintext_clauses": 0,
    }, "claim boundary")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt754_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT754_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "disposition_counts": result["disposition_counts"],
        "renderer_correction": result["renderer_correction"],
        "claim_ceiling": (
            "Provenance and whole-role renderer correction for 172 exact "
            "productive-compound surfaces only. Old component compositions "
            "remain background hypotheses. No component, substring, confirmed "
            "lexeme, literal operation, patient, preparation, ingredient, "
            "plant, disease, cure, person, vessel, unit, plaintext, historical "
            "word match, new page, image, transcription, f84 or f84r."
        ),
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
