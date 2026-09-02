#!/usr/bin/env python3
"""Validate GDT761 artifacts and a byte-identical builder replay."""

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
BASE_REL = Path("experiments/yolo/gdt761_state_pair_outer_carrier_bridge")
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


builder = load_module("gdt761_builder_for_validation", RUN)


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
    occurrences = read_tsv(ART / "TARGET_151_OUTWARD_CONTEXT_ATLAS.tsv")
    contacts = read_tsv(ART / "DIRECT_224_CLEAN_EDGE_ATLAS.tsv")
    deck = read_tsv(ART / "DIRECT_173_SHARED_NEIGHBOR_DECK.tsv")
    direct_frames = read_tsv(ART / "PAIR_SHARED_10_DIRECT_FRAME_ATLAS.tsv")
    radius2_frames = read_tsv(ART / "PAIR_SHARED_8_RADIUS2_FRAME_ATLAS.tsv")
    phrases = read_tsv(ART / "CHOR_5_CARRIER_AND_SHOR_SHEOR_2_RIVAL_SPAN_ATLAS.tsv")
    solvent = read_tsv(ART / "SOLVENT_7_CANDIDATE_AUDIT.tsv")
    revisions = read_tsv(ART / "FIVE_WHOLE_WORKING_REVISION.tsv")

    require(result["schema"] == "GDT761_RESULT_V1", "result schema")
    require(result["status"] == builder.STATUS, "result status")
    require(len(occurrences) == 151, "151 target occurrences")
    require(len(contacts) == 224, "224 clean direct exact contact edges")
    require(len(deck) == 173, "173 distinct clean direct neighbors")
    require(len(direct_frames) == 10, "ten direct shared frames")
    require(len(radius2_frames) == 8, "eight radius-two shared frames")
    require(len(phrases) == 7, "five chor carrier plus two shor base-rival spans")
    require(len(solvent) == 7, "seven solvent candidates audited")
    require(len(revisions) == 5, "five whole revisions")

    require(len({row["target_occurrence_id"] for row in occurrences}) == 151, "unique occurrence ids")
    require(len({row["contact_id"] for row in contacts}) == 224, "unique contact ids")
    require(len({(row["locus"], row["neighbor_ordinal"]) for row in contacts}) == 223, "223 distinct neighbor token positions")
    require(len({row["neighbor_surface"] for row in deck}) == 173, "unique neighbor surfaces")
    require(len({row["phrase_id"] for row in phrases}) == 7, "unique phrase ids")
    require(Counter(row["target_surface"] for row in occurrences) == Counter({
        "cheor": 56, "cheo": 36, "sheor": 31, "sheo": 28,
    }), "fixed four-target recurrence")
    require(Counter(row["target_line_position"] for row in occurrences) == Counter({
        "MIDDLE": 143, "FIRST": 6, "SINGLE": 1, "LAST": 1,
    }), "target position counts")
    require(len({row["locus"] for row in occurrences}) == 150, "150 target loci")
    require(len({row["page"] for row in occurrences}) == 80, "80 target pages")

    direct_status = Counter(
        row[f"{side}_status"] for row in occurrences for side in ("l1", "r1")
    )
    radius2_status = Counter(
        row[f"{side}_status"] for row in occurrences for side in ("l2", "r2")
    )
    require(direct_status == Counter({
        "ELIGIBLE": 224, "NONEXACT": 55, "EDGE": 9, "SUSPECT": 14,
    }), "direct slot status census")
    require(radius2_status == Counter({
        "ELIGIBLE": 176, "EDGE": 77, "NONEXACT": 41,
        "SUSPECT": 6, "TARGET": 2,
    }), "radius-two slot status census")
    require(Counter(row["target_surface"] for row in contacts) == Counter({
        "cheor": 88, "cheo": 48, "sheor": 47, "sheo": 41,
    }), "direct contacts by target")
    require(Counter(row["neighbor_side"] for row in contacts) == Counter({
        "R": 115, "L": 109,
    }), "direct contacts by side")
    require(all(row["neighbor_distance"] == "1" for row in contacts), "contact atlas is direct only")

    require(Counter(row["target_coverage"] for row in deck) == Counter({
        "1": 154, "2": 13, "3": 4, "4": 2,
    }), "target coverage distribution")
    coverage4 = [row["neighbor_surface"] for row in deck if row["target_coverage"] == "4"]
    require(coverage4 == ["chor", "oraiin"], "only chor and oraiin span all four targets")
    coverage3 = {row["neighbor_surface"] for row in deck if row["target_coverage"] == "3"}
    require(coverage3 == {"ol", "aiin", "daiin", "al"}, "four three-target controls")

    chor = next(row for row in deck if row["neighbor_surface"] == "chor")
    oraiin = next(row for row in deck if row["neighbor_surface"] == "oraiin")
    ol = next(row for row in deck if row["neighbor_surface"] == "ol")
    require(chor["direct_contacts"] == "5", "five chor contacts")
    require(chor["direct_contact_pages"] == "5", "five chor pages")
    require(chor["target_counts"] == "cheo:1|cheor:2|sheo:1|sheor:1", "chor touches all targets")
    require(chor["polarity_counts"] == "DRY:3|MOIST:2", "chor crosses both polarities")
    require(chor["descriptive_contact_lift"] == "2.924107", "chor descriptive lift")
    require(chor["decision"] == "SELECT_REPRODUCTIVE_PART_CARRIER_CROSSING_ALL4_TARGETS", "chor selected as carrier lead")
    require(chor["carrier_candidate_selected"] == "1", "one carrier selection")
    require(oraiin["direct_contacts"] == "4", "four oraiin contacts")
    require(oraiin["current_role_class"] == "AMOUNT_OR_VALUE_FORM", "oraiin is amount control")
    require(oraiin["carrier_candidate_selected"] == "0", "amount control not carrier")
    require(ol["polarity_counts"] == "DRY:4|MOIST:2", "ol is not moist-selective")
    al = next(row for row in deck if row["neighbor_surface"] == "al")
    require(al["current_semantic_candidate_de"] == "Material I", "al current material candidate")
    require(al["current_role_class"] == "MATERIAL_CARRIER", "al is not an amount form")
    require(sum(int(row["carrier_candidate_selected"]) for row in deck) == 1, "exactly one selected carrier lead")
    require(all(row["specific_identity_confirmed"] == "0" for row in deck), "no neighbor identity confirmed")
    require(all(row["component_export_credit"] == "0" for row in deck), "no neighbor component export")

    require(Counter(row["pair_role"] for row in direct_frames) == Counter({
        "MATERIAL_PART": 8, "PREPARATION": 2,
    }), "direct shared frames by pair")
    require(Counter(row["pair_role"] for row in radius2_frames) == Counter({
        "MATERIAL_PART": 5, "PREPARATION": 3,
    }), "radius-two shared frames by pair")
    licensed = [row for row in direct_frames if row["exact_composition_license"] == "1"]
    require(len(licensed) == 1, "one exact direct composition frame")
    require(licensed[0]["shared_neighbor_surface"] == "chor", "licensed frame uses chor")
    al_frame = next(row for row in direct_frames if row["shared_neighbor_surface"] == "al")
    require(al_frame["pair_role"] == "PREPARATION", "al shared by preparation pair")
    require(al_frame["interpretation"] == "SAME_MATERIAL_I_CARRIER_FRAME", "al frame is material not amount")
    require(all(row["exact_composition_license"] == "0" for row in radius2_frames), "no radius-two composition")
    cthy = next(row for row in radius2_frames if row["shared_neighbor_surface"] == "cthy")
    require(cthy["pair_role"] == "PREPARATION", "cthy radius-two preparation pair")
    require(cthy["dry_target_contacts"] == "1" and cthy["moist_target_contacts"] == "1", "cthy one hit per preparation target")
    require(cthy["intervening_surface_counts"] == "cheeky:1|shkchor:1", "cthy interveners differ")
    require(cthy["interpretation"] == "SAME_LEAF_DRUG_RADIUS2_LEAD_NO_DIRECT_ATTACHMENT", "cthy stays relay only")
    require(all(row["component_export_credit"] == "0" for row in direct_frames + radius2_frames), "no frame component export")

    require(Counter(row["carrier_surface"] for row in phrases) == Counter({
        "chor": 5, "shor": 2,
    }), "five chor and two shor phrases")
    require(Counter(row["state_whole_surface"] for row in phrases) == Counter({
        "sheor": 3, "cheor": 2, "cheo": 1, "sheo": 1,
    }), "phrase counts by state whole")
    require({row["exact_span_eva"] for row in phrases if row["carrier_surface"] == "chor"} == {
        "chor cheor", "cheor chor", "chor sheor", "cheo chor", "chor sheo",
    }, "five exact chor spans")
    require(sum(row["exact_span_eva"] == "shor sheor" for row in phrases) == 2, "two shor sheor spans")
    require(sum(int(row["exact_phrase_translation_license"]) for row in phrases) == 5, "only five chor phrases licensed")
    require(all(
        row["exact_phrase_translation_license"] == ("1" if row["carrier_surface"] == "chor" else "0")
        for row in phrases
    ), "shor spans remain unlicensed base-family rivals")
    require(all(row["scope"] == "THIS_EXACT_TWO_WHOLE_SPAN_ONLY" for row in phrases), "phrase scope stays local")
    require(all(row["confirmed_plaintext"] == "0" for row in phrases), "phrases are not confirmed plaintext")
    require(all(row["component_export_credit"] == "0" for row in phrases), "phrases grant no components")
    require(all("Arbeitsgut" not in row["working_phrase_de"] for row in phrases), "no generic work-item filler")

    require({row["surface"] for row in solvent} == {
        "ckhy", "dar", "ol", "pcheey", "sain", "shor", "tor",
    }, "fixed solvent audit deck")
    require(all(row["specific_solvent_selected"] == "0" for row in solvent), "no solvent selected")
    require(all(row["confirmed_lexeme"] == "0" for row in solvent), "no solvent lexeme confirmed")
    require(all(row["component_export_credit"] == "0" for row in solvent), "no solvent component export")
    require(next(row for row in solvent if row["surface"] == "ol")["polarity_counts"] == "DRY:4|MOIST:2", "ol solvent rival fails polarity")
    require(next(row for row in solvent if row["surface"] == "ckhy")["polarity_counts"] == "MOIST:2", "ckhy moist-only lead")
    ckhy = next(row for row in solvent if row["surface"] == "ckhy")
    require(ckhy["target_counts"] == "sheo:1|sheor:1", "ckhy crosses moist roles")
    require(ckhy["descriptive_contact_lift"] == "8.234286", "ckhy raw descriptive lift")
    pcheey = next(row for row in solvent if row["surface"] == "pcheey")
    require(pcheey["target_counts"] == "sheo:2", "pcheey repeats after sheo")
    require(pcheey["global_reader_exact_occurrences"] == "3", "pcheey is globally rare")
    require("Pulver" not in pcheey["current_semantic_candidate_de"], "retired p-pulvis gloss absent")

    chor_revision = next(row for row in revisions if row["surface"] == "chor")
    require(chor_revision["new_role_confidence"] == "C2_CROSS_CONSTRUCTION_PART_CARRIER", "chor role promoted")
    require(chor_revision["specific_identity_confidence"] == "C1_REPRODUCTIVE_PART_LEAD", "chor identity stays C1")
    require(chor_revision["new_exact_phrase_positions"] == "5", "five chor phrase licenses")
    require(all(row["global_component_export_allowed"] == "0" for row in revisions), "revisions grant no component export")
    require(all(row["confirmed_lexeme"] == "0" for row in revisions), "revisions confirm no lexeme")

    retired_direct_surfaces = {"schodain", "pshol", "los", "rain", "lkain"}
    require(retired_direct_surfaces.isdisjoint({row["neighbor_surface"] for row in contacts}), "retired head surfaces excluded from clean edges")

    forbidden_filler = ("Arbeitsgut", "Arbeitschritt", "Arbeitsmaterial")
    for row in occurrences:
        require(not row["page"].startswith("f84"), f"sealed page absent {row['target_occurrence_id']}")
        require(row["target_surface"] in {"cheor", "sheor", "cheo", "sheo"}, f"fixed target {row['target_occurrence_id']}")
        require(not any(term in row["target_working_candidate_de"] for term in forbidden_filler), f"no filler {row['target_occurrence_id']}")
        for side in ("l2", "l1", "r1", "r2"):
            require(row[f"{side}_status"] in {"ELIGIBLE", "NONEXACT", "SUSPECT", "TARGET", "EDGE"}, f"slot status {row['target_occurrence_id']} {side}")
            if row[f"{side}_status"] == "SUSPECT":
                require(row[f"{side}_semantic_candidate_de"] == "QUARANTINED_SOURCE_COMPOSITION", f"suspect quarantined {row['target_occurrence_id']} {side}")
    for row in contacts:
        require(not row["page"].startswith("f84"), f"sealed contact page absent {row['contact_id']}")
        require(row["reader_exact_target_and_neighbor"] == "1", f"reader exact contact {row['contact_id']}")
        require(row["component_export_credit"] == "0", f"zero component credit {row['contact_id']}")
        require(row["neighbor_surface"] not in {"cheor", "sheor", "cheo", "sheo"}, f"target excluded as direct neighbor {row['contact_id']}")

    require(result["scope"]["target_occurrences"] == 151, "result target count")
    require(result["scope"]["direct_clean_exact_edges"] == 224, "result edge count")
    require(result["scope"]["direct_distinct_neighbor_positions"] == 223, "result neighbor-position count")
    require(result["scope"]["direct_distinct_neighbor_surfaces"] == 173, "result neighbor count")
    require(result["scope"]["radius2_clean_exact_edges"] == 176, "result radius-two edge count")
    require(result["scope"]["chor_conditional_exact_phrases"] == 5, "result five chor phrases")
    require(result["scope"]["shor_sheor_repeated_base_rival_spans"] == 2, "result two shor rivals")
    require(result["carrier_result"]["chor_target_coverage"] == 4, "result chor target coverage")
    require(result["carrier_result"]["chor_specific_identity"] == "KEEP_C1_FLOWER_OR_SEED_HEAD_LEAD", "result chor identity ceiling")
    require(result["solvent_result"]["specific_solvent_selected"] == 0, "result selects no solvent")
    require(result["solvent_result"]["best_cross_role_moist_medium_candidate"] == "ckhy", "result ckhy lead")
    require(result["solvent_result"]["pcheey_old_pulvis_literal"] == "QUARANTINED_ZERO_CREDIT", "result p-pulvis correction")
    require(result["semantic_quarantine"] == {
        "active_suspect_surface_union": 237,
        "gdt737_retired_head_surfaces": 80,
        "gdt738_retired_salt_surfaces": 2,
        "gdt754_source_composed_surfaces": 172,
        "later_repaired_surface_exemptions": 37,
    }, "three-stage semantic quarantine")
    require(result["claim_boundary"]["confirmed_lexemes"] == 0, "zero confirmed lexemes")
    require(result["claim_boundary"]["confirmed_plaintext_clauses"] == 0, "zero confirmed clauses")
    require(result["claim_boundary"]["confirmed_plant_identities"] == 0, "zero confirmed plant identities")
    require(result["claim_boundary"]["confirmed_solvents"] == 0, "zero confirmed solvents")
    require(result["claim_boundary"]["component_values"] == 0, "zero component values")
    require(result["claim_boundary"]["new_pages"] == 0, "zero new pages")
    require(result["claim_boundary"]["f84_accessed"] is False, "f84 forbidden")
    require(result["claim_boundary"]["f84r_accessed"] is False, "f84r forbidden")

    with tempfile.TemporaryDirectory(prefix="gdt761_replay_") as temp:
        replay_dir = Path(temp)
        replay_result = builder.build(replay_dir)
        require(replay_result == result, "replayed result object")
        for name in builder.OUTPUT_NAMES:
            require((replay_dir / name).is_file(), f"replay output exists {name}")
            require(digest(replay_dir / name) == digest(ART / name), f"byte replay {name}")

    validation = {
        "schema": "GDT761_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "byte_identical_replay": True,
        "scope": result["scope"],
        "carrier_result": result["carrier_result"],
        "pair_result": result["pair_result"],
        "solvent_result": result["solvent_result"],
        "claim_ceiling": (
            "The outward census promotes chor only as an exploratory cross-construction "
            "plant-part carrier and licenses five replaceable chor exact-span readings; "
            "the two shor-sheor repetitions remain unlicensed base-family rivals. It "
            "does not identify flower, seed head, water, wine, oil, any lexeme, any "
            "component value, or any plaintext clause."
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
