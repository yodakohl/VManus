#!/usr/bin/env python3
"""Independent invariant and byte-replay validator for GDT755."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt755_top24_historical_register_crosswalk")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED = (
    "TOP24_448_OCCURRENCE_FIELDS.tsv",
    "TOP24_CHANNEL_CENSUS.tsv",
    "EXACT_FORM_INITIAL_POSITION_COMPARATOR.tsv",
    "TOP24_CANDIDATE_RANKING.tsv",
    "TOP24_WORKING_GLOSS_UPDATE.tsv",
    "CONCRETE_VOCABULARY_SLOT_AUDIT.tsv",
    "TOP24_448_CANDIDATE_RENDERER.tsv",
    "GDT755_HISTORICAL_REGISTER_READER.md",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__24_CONCRETE_COMPLETE_FORM_CANDIDATES__"
    "448_EXACT_OCCURRENCES__198_COMPLETE_INDEPENDENT_FIELDS__"
    "52_HISTORICAL_EXPRESSIONS__13_SOURCES__"
    "2_C2_15_C1_7_C0__YCHOR_UNIQUE_13_OF_13_INITIAL_RANK1_OF373__"
    "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)
EXPECTED_GLOSSES = {
    "air": "zweiter Teil oder Abschnitt",
    "lkaiin": "heiß im dritten Grad",
    "opchedy": "trockne",
    "okeol": "heiß im zweiten Grad",
    "qokeol": "heiß im zweiten Grad",
    "olchedy": "getrocknet",
    "chees": "vollständig getrocknet",
    "qopchedy": "bis zur Hälfte trocknen",
    "okam": "eine Drachme",
    "qoaiin": "nimm drei Einheiten",
    "lky": "heiß oder warm",
    "ykedy": "warm halten oder aufbewahren",
    "orain": "zwei Teile",
    "chky": "heiß und trocken im ersten Grad",
    "qockhey": "mische",
    "ychor": "nimm",
    "cthody": "Salbe",
    "ykol": "heißes Heilmittel",
    "olar": "erster Teil oder Anteil",
    "otaly": "kalt im ersten Grad",
    "qolchedy": "bis zur Hälfte trocknen",
    "chdam": "eine Drachme",
    "olchy": "trockene Zubereitung",
    "qopchey": "trockne",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def vals(text: str) -> set[str]:
    return {value for value in text.split("|") if value and value != "NONE"}


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    occurrences = read_tsv(ART / GENERATED[0])
    census = read_tsv(ART / GENERATED[1])
    positions = read_tsv(ART / GENERATED[2])
    rankings = read_tsv(ART / GENERATED[3])
    glosses = read_tsv(ART / GENERATED[4])
    slots = read_tsv(ART / GENERATED[5])
    renderer = read_tsv(ART / GENERATED[6])
    sources = read_tsv(EXP / "src/HISTORICAL_SOURCE_REGISTRY.tsv")
    bank = read_tsv(EXP / "src/HISTORICAL_EXPRESSION_BANK.tsv")
    priors = read_tsv(EXP / "src/TARGET_CANDIDATE_PRIORS.tsv")
    inventory = read_tsv(
        ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
        "artifacts/ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv"
    )
    suspect = {row["surface"] for row in inventory}

    check(manifest["experiment_id"] == "GDT755", "manifest experiment id")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(result["status"] == STATUS, "result status")
    check(len(sources) == 13 and len({row["source_id"] for row in sources}) == 13, "13 unique historical sources")
    check(all(row["primary_url"].startswith("https://") for row in sources), "historical source urls")
    check(len(bank) == 52 and len({row["candidate_id"] for row in bank}) == 52, "52 unique expression classes")
    source_ids = {row["source_id"] for row in sources}
    for row in bank:
        check(bool(vals(row["source_ids"])) and vals(row["source_ids"]) <= source_ids, f"bank sources {row['candidate_id']}")
        check(row["normalized_expression"] != "" and row["working_gloss_de"] != "", f"bank expression {row['candidate_id']}")
        check(row["date_tier_0_3"] in {"0", "1", "2", "3"}, f"bank date tier {row['candidate_id']}")

    check(len(suspect) == 172, "172 suspect productive compounds")
    check(len(priors) == 24 and {row["surface"] for row in priors} == set(EXPECTED_GLOSSES), "24 complete candidate priors")
    check(all(len({row["primary_candidate_id"], row["alternate_candidate_1"], row["alternate_candidate_2"]}) == 3 for row in priors), "three distinct priors per whole")

    check(len(occurrences) == 448, "448 reader-exact occurrences")
    check(len({row["gdt755_occurrence_id"] for row in occurrences}) == 448, "unique occurrence ids")
    check(len({row["page"] for row in occurrences}) == 125, "125 admitted pages")
    check(sum(row["boundary_complete"] == "1" for row in occurrences) == 198, "198 complete independent fields")
    check(all(row["reader_exact_target"] == "1" for row in occurrences), "all targets reader exact")
    check(all(row["all_172_productive_compound_axes_excluded_from_field"] == "1" for row in occurrences), "all occurrence exclusion flags")
    check(sum(int(row["suspect_172_neighbor_cells_with_axes_excluded"]) for row in occurrences) > 0, "suspect neighbors materially excluded")
    for row in occurrences:
        anchors = vals(row["independent_anchor_surfaces"])
        check(not anchors & suspect, f"no suspect anchor {row['gdt755_occurrence_id']}")
        check(row["surface"] not in anchors, f"no self anchor {row['gdt755_occurrence_id']}")
        check(not row["page"].lower().startswith("f84"), f"no sealed page {row['gdt755_occurrence_id']}")
        check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0", f"occurrence claim boundary {row['gdt755_occurrence_id']}")

    check(len(census) == 24 and {row["surface"] for row in census} == set(EXPECTED_GLOSSES), "24 census rows")
    check(sum(int(row["reader_exact_occurrences"]) for row in census) == 448, "census occurrence sum")
    check(sum(int(row["complete_independent_fields"]) for row in census) == 198, "census complete sum")
    check(all(row["all_172_productive_compound_axes_excluded_from_fields"] == "1" for row in census), "census exclusions")

    check(len(positions) == 373, "373 recurrent-form position comparators")
    check(len({row["surface"] for row in positions}) == 373, "unique comparator surfaces")
    check(all(int(row["reader_exact_occurrences"]) >= 10 for row in positions), "comparator minimum recurrence")
    check(sum(row["line_first_rate"] == "1.000000" for row in positions) == 1, "one fully line-initial recurrent form")
    ychor_position = next(row for row in positions if row["surface"] == "ychor")
    check(ychor_position["line_initial_rate_rank"] == "1", "ychor initial rate rank one")
    check(ychor_position["line_first_occurrences"] == "13" and ychor_position["reader_exact_occurrences"] == "13", "ychor comparator 13 of 13")
    check(ychor_position["paragraph_first_occurrences"] == "0", "ychor never paragraph first")
    check(all(row["comparison_used_semantics"] == "0" for row in positions), "position comparator semantic free")
    check(all(not row["surface"].lower().startswith("f84") for row in positions), "position comparator contains surfaces not selectors")

    check(len(rankings) == 72, "72 candidate rankings")
    by_surface: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rankings:
        by_surface[row["surface"]].append(row)
        check(row["comparison_unit"] == "EXACT_COMPLETE_SURFACE_ROLE_NOT_EVA_SPELLING", f"whole comparison {row['surface']} {row['candidate_rank']}")
        check(row["historical_graphic_match_claimed"] == "0", f"no graphic match {row['surface']} {row['candidate_rank']}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"ranking ceiling {row['surface']} {row['candidate_rank']}")
    for surface, rows in by_surface.items():
        check(sorted(int(row["candidate_rank"]) for row in rows) == [1, 2, 3], f"three ranks {surface}")
        primary = [row for row in rows if row["selected_primary"] == "1"]
        check(len(primary) == 1 and primary[0]["candidate_rank"] == "1", f"one primary {surface}")
        check(primary[0]["hard_role_fit"] == "1", f"primary role fit {surface}")

    check(len(glosses) == 24 and {row["surface"] for row in glosses} == set(EXPECTED_GLOSSES), "24 gloss rows")
    for row in glosses:
        check(row["gdt755_working_candidate_de"] == EXPECTED_GLOSSES[row["surface"]], f"expected gloss {row['surface']}")
        check(row["gdt755_spoken_candidate_render_de"] == f"Arbeitshypothese: {EXPECTED_GLOSSES[row['surface']]}", f"spoken candidate {row['surface']}")
        check(row["candidate_layer_scope"] == "EXACT_COMPLETE_SURFACE_ON_ENUMERATED_READER_EXACT_POSITIONS", f"gloss scope {row['surface']}")
        check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0", f"gloss ceiling {row['surface']}")
        check(row["evidence"] != "" and row["counterevidence"] != "", f"gloss evidence {row['surface']}")
    check(Counter(row["working_confidence"] for row in glosses) == Counter({
        "C0_FORCED_DEFAULT": 7,
        "C1_CONSTRAINED_CANDIDATE": 15,
        "C2_STRONG_EXPLORATORY": 2,
    }), "confidence distribution")

    ychor_occ = [row for row in occurrences if row["surface"] == "ychor"]
    check(len(ychor_occ) == 13, "ychor thirteen exact")
    check(all(row["line_position"] == "FIRST" for row in ychor_occ), "ychor all line first")
    check(sum(row["boundary_complete"] == "1" for row in ychor_occ) == 8, "ychor eight complete")
    check(sum(row["boundary_complete"] == "1" and row["field_channel"] == "PRESCRIPTIVE_RECIPE" for row in ychor_occ) == 3, "ychor three recipe fields")
    check(next(row for row in glosses if row["surface"] == "ychor")["gdt755_primary_historical_expression"] == "Recipe", "ychor Recipe primary")
    cthody = next(row for row in rankings if row["surface"] == "cthody" and row["selected_primary"] == "1")
    check(cthody["candidate_id"] == "E026" and cthody["literal_content_axis_supported"] == "0", "cthody ointment explicitly unsupported")

    check(len(slots) == 26 and len({row["concept_de"] for row in slots}) == 26, "26 slot audit rows")
    for concept in ("Wasser", "Wein", "Oel", "Salz", "Wurzel", "Blatt", "Samen", "Holz", "Pulver", "Gefaess", "Frau", "Krankheit", "baden"):
        row = next(item for item in slots if item["concept_de"] == concept)
        check(row["literal_axis_supported_count"] == "0", f"no literal top24 slot {concept}")
    check(next(row for row in slots if row["concept_de"] == "nimm")["used_as_primary_top24_surfaces"] == "ychor", "nimm primary ychor")
    check(next(row for row in slots if row["concept_de"] == "trocknen")["structurally_compatible_count"] == "9", "nine drying role slots")
    check(next(row for row in slots if row["concept_de"] == "einweichen")["structurally_compatible_count"] == "0", "no soak role slot")

    check(len(renderer) == 448, "448 renderer rows")
    check({row["gdt755_occurrence_id"] for row in renderer} == {row["gdt755_occurrence_id"] for row in occurrences}, "renderer occurrence coverage")
    for row in renderer:
        check(f"[{row['working_candidate_de']}]" in row["candidate_hybrid_line_de"], f"hybrid contains candidate {row['gdt755_occurrence_id']}")
        check(row["candidate_layer_not_plaintext"] == "1" and row["unmapped_tokens_preserved_as_eva"] == "1", f"renderer boundary {row['gdt755_occurrence_id']}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"renderer ceiling {row['gdt755_occurrence_id']}")

    banned = ("work item", "working material", "Arbeitsgut", "Arbeitschritt", "destination vessel")
    for name in GENERATED:
        text = (ART / name).read_text(encoding="utf-8")
        check(not any(term in text for term in banned), f"no generic filler in {name}")

    check(result["scope"] == {
        "candidate_renderer_positions": 448,
        "candidate_rows": 72,
        "complete_independent_fields": 198,
        "concrete_slot_audit_concepts": 26,
        "historical_expression_classes": 52,
        "historical_sources": 13,
        "position_comparator_forms_min10": 373,
        "reader_exact_occurrences": 448,
        "reader_exact_pages": 125,
        "top_complete_forms": 24,
        "working_gloss_updates": 24,
    }, "result scope")
    check(result["candidate_confidence_counts"] == {
        "C0_FORCED_DEFAULT": 7,
        "C1_CONSTRAINED_CANDIDATE": 15,
        "C2_STRONG_EXPLORATORY": 2,
    }, "result confidence")
    check(result["strongest_new_lead"] == {
        "candidate": "Recipe / nimm",
        "complete_prescriptive_recipe_fields": 3,
        "forms_min10_with_100_percent_line_initial": 1,
        "line_first_occurrences": 13,
        "line_initial_rate_rank_among_forms_min10": 1,
        "paragraph_first_occurrences": 0,
        "reader_exact_occurrences": 13,
        "status": "STRONG_EXPLORATORY_COMPLETE_WHOLE_CANDIDATE",
        "surface": "ychor",
    }, "result strongest lead")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"] == {
        "component_export_credit": 0,
        "concrete_working_defaults": 24,
        "confirmed_historical_graphic_matches": 0,
        "confirmed_lexemes": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
        "literal_content_identifications": 0,
        "new_pages": 0,
        "plaintext_clauses": 0,
    }, "result claim boundary")

    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")
    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt755_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT755_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "confidence": result["candidate_confidence_counts"],
        "strongest_new_lead": result["strongest_new_lead"],
        "claim_ceiling": (
            "Twenty-four replaceable exact-whole historical-register candidates; "
            "zero confirmed lexemes, graphic matches, plaintext clauses, content "
            "identities, component exports, new pages, f84 or f84r access."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
