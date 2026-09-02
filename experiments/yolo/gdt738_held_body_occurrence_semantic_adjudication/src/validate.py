#!/usr/bin/env python3
"""Independent consistency, scope, and replay audit for GDT738."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
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
BASE = Path("experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication")
EXP = ROOT / BASE
DEFAULT_ART = EXP / "artifacts"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
HELD_OCC = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_811_OCCURRENCE_CONTEXTS.tsv"
HELD_FORMS = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
HELD_BODIES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
COMPACT = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
STATUS = (
    "PARTIAL__TWO_DIRECT_CROSS_HEAD_SURVIVORS__FIVE_ADDITIONAL_W23_FAMILY_SURVIVORS__"
    "FOUR_DISCOVERY_ONLY_FAMILY_PASSES__TWELVE_SCOPED_COMPLETE_WHOLE_CARDS__"
    "LITERAL_SALT_DOWNGRADED__ZERO_LEXEME_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "ADJACENT_1266_SLOT_AUDIT.tsv",
    "NONHEAD_NEIGHBOR_AXIS_ANCHORS.tsv",
    "BODY_120_SEMANTIC_BRIDGE.tsv",
    "BODY_TRANSFER_METRICS.tsv",
    "FORM_273_ADJUDICATION.tsv",
    "AXIS_NEIGHBOR_ENRICHMENT.tsv",
    "MATRIX_WORKING_MODEL.tsv",
    "REPAIRED_SCOPED_WHOLE_CARDS.tsv",
    "ADJUDICATED_17_WHOLE_CARDS.tsv",
    "OCCURRENCE_RENDERER_PATCH.tsv",
    "MANUAL_HOLD_AUDIT.tsv",
    "HISTORICAL_MICROENTRY_MODELS.tsv",
    "RESULT.json",
)
RETIRED = ("pulver", "samen", "saat", "wurzel", "holz")
AXES = (
    ("HEAT", re.compile(r"heiß|erhitz|erwärm|heiz|warm", re.I)),
    ("COLD", re.compile(r"kalt|abgekühl|abkühl", re.I)),
    ("DRY", re.compile(r"trocken|getrock|trockn", re.I)),
    ("MOIST", re.compile(r"feucht|einweich|angefeucht", re.I)),
    ("VALUE", re.compile(r"wert|menge|maß|grad|stufe|klasse|dosis|charge|index|pfund|gewicht|handvoll|gebinde", re.I)),
    ("PART", re.compile(r"\bteil|fraktion|portion|anteil|blüt|frucht|reproduktion", re.I)),
    ("MATERIAL", re.compile(r"material|rohstoff|droge|stoff|\bgut|blatt|kraut", re.I)),
    ("PREPARATION", re.compile(r"ansatz|zubereitung|kompositum|misch", re.I)),
    ("CLOSE", re.compile(r"abgeschlossen|fertig|schluss|geschlossen", re.I)),
    ("PROCESS", re.compile(r"nehmen|abseih|trenn|abmess|abfüll|trocknen|erhitze|einweichen|abkühlen", re.I)),
)
SUPPORTED = {"SUPPORTED_CROSS_HEAD", "SUPPORTED_FAMILY_ONLY"}
DISCOVERY_BODIES = {"ain", "cheedy", "cheol", "cheor", "kaiin", "kain", "kar", "keey", "key", "ky", "sheedy"}
STRICT_BODIES = {"ain", "cheedy", "cheol", "kaiin", "kain", "kar", "sheedy"}
DISCOVERY_FORMS = {
    "lain", "lcheedy", "lcheol", "lcheor", "lkaiin", "lkain", "lkar", "lkeey", "lkey", "lky",
    "lsheedy", "pcheol", "pcheor", "rain", "rsheedy", "sain", "skaiin",
}
STRICT_FORMS = {
    "lain", "lcheedy", "lcheol", "lkaiin", "lkain", "lkar", "lsheedy", "pcheol", "rain",
    "rsheedy", "sain", "skaiin",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(row: dict[str, str], field: str) -> int:
    return int(row[field])


def position_exception(head: str, position: str) -> bool:
    return (head in ("H1", "H2") and position != "FIRST") or (head in ("H3", "H4") and position == "FIRST")


def semantic_axes(text: str) -> tuple[str, ...]:
    selected = tuple(axis for axis, pattern in AXES if pattern.search(text))
    return selected or ("OTHER",)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def require(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT738", "manifest experiment id")
    check(manifest["slug"] == "held_body_occurrence_semantic_adjudication", "manifest slug")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors forbidden")
    placeholder = (
        manifest["status"] == "REGISTERED_UNSCORED"
        and manifest["inputs"] == [] and manifest["outputs"] == []
        and manifest["validation"] == {"artifact": None, "status": "NOT_RUN"}
    )
    if placeholder:
        check(True, "manifest placeholder accepted before sealing")
    else:
        check(manifest["status"] == STATUS, "manifest status")
        check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "manifest validation contract")
        check(bool(manifest["inputs"]), "sealed manifest has inputs")
        check(bool(manifest["outputs"]), "sealed manifest has outputs")
        for binding in manifest["inputs"]:
            path = ROOT / binding["path"]
            require(not Path(binding["path"]).is_absolute(), f"absolute input binding: {binding['path']}")
            require(path.is_file(), f"missing input binding: {binding['path']}")
            require(sha256(path) == binding["sha256"], f"input hash mismatch: {binding['path']}")
        check(True, "all manifest input bindings exist and hash-match")
        output_paths = {binding["path"] for binding in manifest["outputs"]}
        expected = {str(BASE / "artifacts" / name) for name in GENERATED} | {str(VALIDATION_REL)}
        check(expected <= output_paths, "manifest binds generated artifacts and validation")
        for binding in manifest["outputs"]:
            path = ROOT / binding["path"]
            require(not Path(binding["path"]).is_absolute(), f"absolute output binding: {binding['path']}")
            if binding["path"] == str(VALIDATION_REL):
                continue
            require(path.is_file(), f"missing output binding: {binding['path']}")
            require(sha256(path) == binding["sha256"], f"output hash mismatch: {binding['path']}")
        check(True, "all non-validation output bindings exist and hash-match")

    check(art.is_dir(), "artifact directory exists")
    check(all((art / name).is_file() for name in GENERATED), "all generated artifacts exist")

    occurrences = read_tsv(HELD_OCC)
    source_forms = read_tsv(HELD_FORMS)
    source_bodies = read_tsv(HELD_BODIES)
    check(len(occurrences) == 811, "source geometry: 811 occurrences")
    check(len({row["occurrence_id"] for row in occurrences}) == 811, "source occurrence ids unique")
    check(len({(row["locus"], row["token_index"]) for row in occurrences}) == 811, "source occurrence positions unique")
    check(len({row["form"] for row in occurrences}) == len(source_forms) == 273, "source geometry: 273 forms")
    check(len({row["body"] for row in occurrences}) == len(source_bodies) == 120, "source geometry: 120 bodies")
    check(sum(row["all_readers_exact"] == "1" for row in occurrences) == 619, "source geometry: 619 reader-exact occurrences")
    check(len({row["page"] for row in occurrences}) == 134, "source geometry: 134 pages")
    check(len({row["locus"] for row in occurrences}) == 697, "source geometry: 697 loci")
    check(Counter(int(row["head_occupancy"]) for row in source_bodies) == Counter({2: 87, 3: 33}), "source occupancy 87 two-head and 33 three-head bodies")
    check(not any(row["page"].startswith("f84") for row in occurrences), "source occurrences exclude sealed pages")
    occ_map = {row["occurrence_id"]: row for row in occurrences}

    compact_rows = read_tsv(COMPACT)
    check(len(compact_rows) == 32339, "compact cache has 32339 cells")
    check(len({row["page"] for row in compact_rows}) == 179, "compact cache has inherited 179-page boundary")
    check(not any(row["page"].startswith("f84") for row in compact_rows), "compact cache excludes sealed pages")
    compact = {(row["locus"], int(row["token_ordinal"])): row for row in compact_rows}
    check(len(compact) == 32339, "compact locus-ordinal keys unique")

    slots = read_tsv(art / "ADJACENT_1266_SLOT_AUDIT.tsv")
    check(len(slots) == 1266, "1266 adjacent slots")
    check(len({row["slot_id"] for row in slots}) == 1266, "adjacent slot ids unique")
    check(len({(row["source_occurrence_id"], row["side"]) for row in slots}) == 1266, "one slot per occurrence side")
    expected_slot_keys: set[tuple[str, str, int]] = set()
    for occurrence in occurrences:
        ordinal = int(occurrence["token_ordinal"])
        if ordinal > 1:
            expected_slot_keys.add((occurrence["occurrence_id"], "L", ordinal - 1))
        if ordinal < int(occurrence["line_length"]):
            expected_slot_keys.add((occurrence["occurrence_id"], "R", ordinal + 1))
        require(compact[(occurrence["locus"], ordinal)]["surface"] == occurrence["form"], f"compact target mismatch: {occurrence['occurrence_id']}")
    observed_slot_keys = {(row["source_occurrence_id"], row["side"], int(row["neighbor_token_ordinal"])) for row in slots}
    check(observed_slot_keys == expected_slot_keys, "slot deck is complete immediate-neighbour geometry")

    deck_counts: Counter[str] = Counter()
    for row in slots:
        occurrence = occ_map[row["source_occurrence_id"]]
        require(row["target_panel"] == "H", f"non-held target panel: {row['slot_id']}")
        require(all(row[field] == occurrence[field] for field in ("body", "form", "opaque_head_id", "page", "locus", "section", "language", "line_position")), f"slot target provenance: {row['slot_id']}")
        require(integer(row, "target_reader_exact") == int(occurrence["all_readers_exact"]), f"target exactness: {row['slot_id']}")
        require(integer(row, "position_exception") == int(position_exception(occurrence["opaque_head_id"], occurrence["line_position"])), f"slot position exception: {row['slot_id']}")
        cell = compact[(row["locus"], int(row["neighbor_token_ordinal"]))]
        require(row["neighbor_cell_id"] == cell["cell_id"] and row["neighbor_surface"] == cell["surface"], f"compact neighbour provenance: {row['slot_id']}")
        initial = int(len(row["neighbor_surface"]) > 1 and row["neighbor_surface"][0] in "psrl" and not row["neighbor_surface"].startswith("sh"))
        both = integer(row, "target_reader_exact") * integer(row, "neighbor_reader_exact")
        formal = int(both == 1 and initial == 0)
        meaning = cell["v99r7_semantic_value_de"]
        retired = tuple(word for word in RETIRED if word in meaning.lower())
        sem570 = int(formal and cell["unknown_v99r7"] == "0" and not retired)
        axes = semantic_axes(meaning) if sem570 else ()
        pre197 = int(sem570 and cell["gdt734_confidence_level"].startswith(("W2", "W3")))
        strict195 = int(pre197 and axes != ("OTHER",) and cell["gdt734_composition_semantic_credit"] == "0")
        require(integer(row, "strict_initial_head_neighbor") == initial, f"formal head exclusion: {row['slot_id']}")
        require(integer(row, "both_reader_exact") == both, f"joint exactness: {row['slot_id']}")
        require(integer(row, "formal705_slot") == formal, f"FORMAL705 rule: {row['slot_id']}")
        require(integer(row, "sem570_slot") == sem570, f"SEM570 rule: {row['slot_id']}")
        require(integer(row, "w23_axis197_precomposition_slot") == pre197, f"W23-197 rule: {row['slot_id']}")
        require(integer(row, "w23_axis195_slot") == strict195, f"W23-195 rule: {row['slot_id']}")
        require(row["retired_patient_words"] == ("|".join(retired) or "NONE"), f"retired-patient audit: {row['slot_id']}")
        if sem570:
            require(row["neighbor_semantic_value_de"] == meaning, f"semantic text provenance: {row['slot_id']}")
            require(row["neighbor_confidence_level"] == cell["gdt734_confidence_level"], f"confidence provenance: {row['slot_id']}")
            require(row["axis_tags"] == "|".join(axes) == row["semantic_fingerprint"], f"axis fingerprint: {row['slot_id']}")
        else:
            require(row["axis_tags"] == row["semantic_fingerprint"] == "NONE", f"masked fingerprint: {row['slot_id']}")
        require(all(row[field] == "0" for field in ("literal_head_lexeme_credit", "literal_body_lexeme_credit", "component_export_credit")), f"slot export leakage: {row['slot_id']}")
        deck_counts.update({"neighbor_exact": integer(row, "neighbor_reader_exact"), "both": both, "formal": formal, "sem570": sem570, "pre197": pre197, "strict195": strict195})
    check(True, "all slot rules independently replay from source cells")
    check(deck_counts == Counter({"neighbor_exact": 972, "both": 783, "formal": 705, "sem570": 570, "pre197": 197, "strict195": 195}), "exact 972/783/705/570/197/195 deck counts")
    footprints = {}
    for flag in ("formal705_slot", "sem570_slot", "w23_axis197_precomposition_slot", "w23_axis195_slot"):
        selected = [row for row in slots if row[flag] == "1"]
        footprints[flag] = (len({row["source_occurrence_id"] for row in selected}), len({row["body"] for row in selected}), len({row["form"] for row in selected}))
    check(footprints == {"formal705_slot": (520, 109, 182), "sem570_slot": (444, 105, 162), "w23_axis197_precomposition_slot": (180, 71, 90), "w23_axis195_slot": (178, 71, 89)}, "deck target/body/form footprints")
    sem_levels = Counter(row["neighbor_confidence_level"] for row in slots if row["sem570_slot"] == "1")
    strict_levels = Counter(row["neighbor_confidence_level"] for row in slots if row["w23_axis195_slot"] == "1")
    check(sem_levels == Counter({"NA": 356, "W3_SOLID_WORKING_THEORY": 160, "W2_PROVISIONAL_WORKING": 37, "W1_WEAK_WORKING": 15, "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 2}), "SEM570 confidence partition")
    check(strict_levels == Counter({"W3_SOLID_WORKING_THEORY": 160, "W2_PROVISIONAL_WORKING": 35}), "W23-AXIS195 confidence partition")
    anchors = read_tsv(art / "NONHEAD_NEIGHBOR_AXIS_ANCHORS.tsv")
    check(anchors == [row for row in slots if row["sem570_slot"] == "1"], "SEM570 anchor artifact is exact slot projection")

    metrics = read_tsv(art / "BODY_TRANSFER_METRICS.tsv")
    check(len(metrics) == len({row["body"] for row in metrics}) == 120, "120 unique body metrics")
    metric_map = {row["body"]: row for row in metrics}
    slots_by_body: dict[str, list[dict[str, str]]] = defaultdict(list)
    occ_by_body: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slots_by_body[row["body"]].append(row)
    for row in occurrences:
        occ_by_body[row["body"]].append(row)
    for body, row in metric_map.items():
        body_occ, body_slots = occ_by_body[body], slots_by_body[body]
        require(integer(row, "headed_occurrences") == len(body_occ), f"body occurrences: {body}")
        require(integer(row, "reader_exact_occurrences") == sum(item["all_readers_exact"] == "1" for item in body_occ), f"body exact: {body}")
        require(integer(row, "formal705_slots") == sum(item["formal705_slot"] == "1" for item in body_slots), f"body formal: {body}")
        require(integer(row, "sem570_slots") == sum(item["sem570_slot"] == "1" for item in body_slots), f"body sem570: {body}")
        require(integer(row, "w23_axis195_slots") == sum(item["w23_axis195_slot"] == "1" for item in body_slots), f"body w23: {body}")
        exceptions = sum(position_exception(item["opaque_head_id"], item["line_position"]) for item in body_occ)
        require(integer(row, "position_exceptions") == exceptions, f"body position exceptions: {body}")
        capacity = int(integer(row, "reader_exact_occurrences") >= 4) + int(integer(row, "formal705_slots") >= 4)
        require(integer(row, "capacity_points") == capacity, f"body capacity: {body}")
        require(integer(row, "total_penalty") == integer(row, "penalty_single_formal_head") + integer(row, "penalty_position") + integer(row, "penalty_prior"), f"body penalty sum: {body}")
        for prefix in ("discovery", "w23"):
            direct = 2 * int(integer(row, f"{prefix}_shared_surface_count") > 0)
            direct += int(integer(row, f"{prefix}_registered_surface_count") > 0)
            direct += int(integer(row, f"{prefix}_shared_fingerprint_count") > 0)
            direct += int(integer(row, f"{prefix}_registered_fingerprint_count") > 0)
            direct += int(integer(row, f"{prefix}_register_overlap_count") > 0)
            require(integer(row, f"{prefix}_direct_score") == direct, f"{prefix} direct score: {body}")
            surface = float(row[f"{prefix}_family_surface_cosine"])
            axis = float(row[f"{prefix}_family_axis_cosine"])
            register = float(row[f"{prefix}_family_register_cosine"])
            family_points = 2 * int(surface >= .15) + int(axis >= .80) + int(register >= .70)
            require(integer(row, f"{prefix}_family_points") == family_points, f"{prefix} family points: {body}")
            require(integer(row, f"{prefix}_strong_family") == int(surface >= .15 and axis >= .80 and register >= .70), f"{prefix} family gate: {body}")
            require(integer(row, f"{prefix}_working_score_not_probability") == capacity + direct + family_points + integer(row, "total_penalty"), f"{prefix} score: {body}")
            if direct >= 4 and integer(row, "reader_exact_occurrences") >= 4 and integer(row, f"{prefix}_recurrence_heads_balanced_ge2_exact"):
                decision = "SUPPORTED_CROSS_HEAD"
            elif integer(row, f"{prefix}_strong_family") and integer(row, "reader_exact_occurrences") >= 4 and integer(row, "formal705_slots") >= 4:
                decision = "SUPPORTED_FAMILY_ONLY"
            elif row["analogy_family"] != "NONE" and row[f"{prefix}_family_comparator"] != "NONE" and integer(row, "reader_exact_occurrences") >= 5 and integer(row, "formal705_slots") >= 8 and family_points <= 1 and direct <= 1:
                decision = "CONTRADICTED_FAMILY_TRANSFER"
            else:
                decision = "UNDECIDABLE"
            require(row[f"{prefix}_decision"] == decision, f"{prefix} decision: {body}")
        require(all(row[field] == "0" for field in ("body_renderer_license", "literal_head_lexeme_credit", "literal_body_lexeme_credit", "component_export_credit")), f"body export leakage: {body}")
    check(True, "all body counts, scores, gates, and decisions independently recompute")

    discovery_cross = {row["body"] for row in metrics if row["discovery_decision"] == "SUPPORTED_CROSS_HEAD"}
    discovery_family = {row["body"] for row in metrics if row["discovery_decision"] == "SUPPORTED_FAMILY_ONLY"}
    discovery_contradicted = {row["body"] for row in metrics if row["discovery_decision"] == "CONTRADICTED_FAMILY_TRANSFER"}
    strict_cross = {row["body"] for row in metrics if row["w23_decision"] == "SUPPORTED_CROSS_HEAD"}
    strict_family = {row["body"] for row in metrics if row["w23_decision"] == "SUPPORTED_FAMILY_ONLY"}
    strict_contradicted = {row["body"] for row in metrics if row["w23_decision"] == "CONTRADICTED_FAMILY_TRANSFER"}
    check(discovery_cross == {"ain", "sheedy"}, "SEM570 direct cross-head bodies")
    check(discovery_family == {"cheedy", "cheol", "cheor", "kaiin", "kain", "kar", "keey", "key", "ky"}, "SEM570 family-only bodies")
    check(discovery_contradicted == {"char", "cheody"}, "SEM570 contradicted transfers")
    check(discovery_cross | discovery_family == DISCOVERY_BODIES, "SEM570 11-body supported set")
    check(strict_cross == {"ain", "sheedy"}, "W23 direct cross-head bodies")
    check(strict_family == {"cheedy", "cheol", "kaiin", "kain", "kar"}, "W23 family-only bodies")
    check(strict_contradicted == {"chal", "char", "cheody", "chor", "o"}, "W23 contradicted transfers")
    check(strict_cross | strict_family == STRICT_BODIES, "W23 seven-body supported set")
    check(Counter(row["discovery_decision"] for row in metrics) == Counter({"UNDECIDABLE": 107, "SUPPORTED_FAMILY_ONLY": 9, "SUPPORTED_CROSS_HEAD": 2, "CONTRADICTED_FAMILY_TRANSFER": 2}), "SEM570 decision partition")
    check(Counter(row["w23_decision"] for row in metrics) == Counter({"UNDECIDABLE": 108, "SUPPORTED_FAMILY_ONLY": 5, "SUPPORTED_CROSS_HEAD": 2, "CONTRADICTED_FAMILY_TRANSFER": 5}), "W23 decision partition")

    decision_specs = read_tsv(EXP / "src/BODY_DECISION_SPECS.tsv")
    check(len(decision_specs) == len({row["body"] for row in decision_specs}) == 13, "13 unique key-body decision specs")
    for spec in decision_specs:
        metric = metric_map[spec["body"]]
        for prefix in ("discovery", "w23"):
            require(metric[f"{prefix}_family_comparator"] == spec[f"{prefix}_comparator"], f"{prefix} comparator spec: {spec['body']}")
            require(metric[f"{prefix}_working_score_not_probability"] == spec[f"{prefix}_score"], f"{prefix} score spec: {spec['body']}")
            require(metric[f"{prefix}_decision"] == spec[f"{prefix}_decision"], f"{prefix} decision spec: {spec['body']}")
    check(True, "all 13 key-body discovery and W23 specs match metrics")
    check(next(row for row in decision_specs if row["body"] == "cheody")["discovery_comparator"] == "chody" and next(row for row in decision_specs if row["body"] == "cheody")["w23_comparator"] == "ody", "cheody comparator changes by semantic deck")

    forms = read_tsv(art / "FORM_273_ADJUDICATION.tsv")
    check(len(forms) == len({row["form"] for row in forms}) == 273, "273 unique adjudicated forms")
    form_map = {row["form"]: row for row in forms}
    slots_by_form: dict[str, list[dict[str, str]]] = defaultdict(list)
    occ_by_form: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slots_by_form[row["form"]].append(row)
    for row in occurrences:
        occ_by_form[row["form"]].append(row)
    for form, row in form_map.items():
        form_occ, form_slots = occ_by_form[form], slots_by_form[form]
        require(integer(row, "occurrences") == len(form_occ), f"form occurrences: {form}")
        require(integer(row, "reader_exact_occurrences") == sum(item["all_readers_exact"] == "1" for item in form_occ), f"form exact: {form}")
        require(integer(row, "formal705_slots") == sum(item["formal705_slot"] == "1" for item in form_slots), f"form formal: {form}")
        require(integer(row, "sem570_slots") == sum(item["sem570_slot"] == "1" for item in form_slots), f"form sem570: {form}")
        require(integer(row, "w23_axis195_slots") == sum(item["w23_axis195_slot"] == "1" for item in form_slots), f"form w23: {form}")
        body = metric_map[row["body"]]
        discovery_gate = body["discovery_decision"] in SUPPORTED and integer(row, "reader_exact_occurrences") >= 2 and integer(row, "formal705_slots") >= 2
        strict_gate = body["w23_decision"] in SUPPORTED and integer(row, "reader_exact_occurrences") >= 2 and integer(row, "formal705_slots") >= 2
        require(integer(row, "discovery_form_gate") == int(discovery_gate), f"discovery form gate: {form}")
        require(integer(row, "w23_form_gate") == integer(row, "renderer_license") == int(strict_gate), f"W23 form gate: {form}")
        require(all(row[field] == "0" for field in ("unconditional_global_export", "literal_head_lexeme_credit", "literal_body_lexeme_credit", "component_export_credit")), f"form export leakage: {form}")
    check(True, "all form counts and gates independently recompute")
    discovered_forms = {row["form"] for row in forms if row["discovery_form_gate"] == "1"}
    licensed_forms = {row["form"] for row in forms if row["renderer_license"] == "1"}
    check(discovered_forms == DISCOVERY_FORMS, "SEM570 17-form discovery set")
    check(licensed_forms == STRICT_FORMS, "W23 12-form renderer set")
    check(discovered_forms - licensed_forms == {"lcheor", "lkeey", "lkey", "lky", "pcheor"}, "five discovery-only forms")
    check(Counter(row["discovery_form_decision"] for row in forms) == Counter({"UNDECIDABLE": 256, "SUPPORTED_SCOPED_WHOLE": 16, "SUPPORTED_EXACT_WHOLE_EXCEPTION": 1}), "SEM570 form decision partition")
    check(Counter(row["w23_form_decision"] for row in forms) == Counter({"UNDECIDABLE": 261, "SUPPORTED_SCOPED_WHOLE": 11, "SUPPORTED_EXACT_WHOLE_EXCEPTION": 1}), "W23 form decision partition")
    check({row["form"] for row in forms if row["w23_form_decision"] == "SUPPORTED_EXACT_WHOLE_EXCEPTION"} == {"skaiin"}, "skaiin only licensed learned position exception")
    check(sum(integer(form_map[form], "reader_exact_occurrences") for form in STRICT_FORMS) == 203, "12 strict forms have 203 exact occurrences before position scope")

    specs = read_tsv(EXP / "src/MANUAL_WHOLE_SPECS.tsv")
    spec_map = {row["surface"]: row for row in specs}
    check(len(specs) == len(spec_map) == 17 and set(spec_map) == DISCOVERY_FORMS, "manual whole specs cover exactly 17 discovery forms")
    discovery_cards = read_tsv(art / "ADJUDICATED_17_WHOLE_CARDS.tsv")
    check(len(discovery_cards) == 17 and {row["surface"] for row in discovery_cards} == DISCOVERY_FORMS, "17-card discovery deck")
    check({row["surface"] for row in discovery_cards if row["w23_renderer_license"] == "1"} == STRICT_FORMS, "discovery deck exposes exactly 12 W23 licenses")
    check(all(row["discovery_card_visible"] == "1" and row["unconditional_global_export"] == row["literal_plaintext_claimed"] == row["component_export_credit"] == "0" for row in discovery_cards), "discovery cards have zero global/plaintext/component export")

    cards = read_tsv(art / "REPAIRED_SCOPED_WHOLE_CARDS.tsv")
    check(len(cards) == 12 and {row["surface"] for row in cards} == STRICT_FORMS, "12 scoped renderer cards")
    check(len({row["card_id"] for row in cards}) == 12, "renderer card ids unique")
    card_by_id = {row["card_id"]: row for row in cards}
    for card in cards:
        spec = spec_map[card["surface"]]
        require(card["selected_whole_de"] == spec["selected_whole_de"], f"card meaning spec: {card['surface']}")
        require(card["w23_allowed_positions"] == spec["w23_allowed_positions"], f"card positions spec: {card['surface']}")
        require(card["renderer_license"] == "1" and card["renderer_scope"] == "EXACT_COMPLETE_SURFACE_AT_ENUMERATED_OCCURRENCES", f"card scope: {card['surface']}")
        require(card["unconditional_global_export"] == card["literal_plaintext_claimed"] == card["component_export_credit"] == "0", f"card export leakage: {card['surface']}")
        require("salz" not in " ".join(card.values()).lower(), f"literal salt in active card: {card['surface']}")
    check(True, "all 12 renderer cards match manual scope and exclude literal salt")

    patches = read_tsv(art / "OCCURRENCE_RENDERER_PATCH.tsv")
    check(len(patches) == 202, "202 position-scoped renderer patches")
    check(len({row["patch_id"] for row in patches}) == len({row["occurrence_id"] for row in patches}) == 202, "patch and occurrence ids unique")
    eligible: set[str] = set()
    for surface in STRICT_FORMS:
        allowed = set(spec_map[surface]["w23_allowed_positions"].split("|"))
        eligible.update(row["occurrence_id"] for row in occ_by_form[surface] if row["all_readers_exact"] == "1" and row["line_position"] in allowed)
    check({row["occurrence_id"] for row in patches} == eligible, "patch deck equals exact in-position licensed occurrences")
    exact_strict = {row["occurrence_id"] for surface in STRICT_FORMS for row in occ_by_form[surface] if row["all_readers_exact"] == "1"}
    unpatched = exact_strict - eligible
    check(len(exact_strict) == 203 and unpatched == {"G737-O0330"}, "one unpatched exact strict-form occurrence")
    missing = occ_map["G737-O0330"]
    check((missing["form"], missing["opaque_head_id"], missing["line_position"]) == ("lkaiin", "H4", "FIRST"), "unpatched occurrence is initial H4 lkaiin")
    for patch in patches:
        occurrence = occ_map[patch["occurrence_id"]]
        require(occurrence["all_readers_exact"] == "1" and patch["surface"] == occurrence["form"], f"patch identity: {patch['patch_id']}")
        require(all(patch[field] == occurrence[field] for field in ("page", "locus", "token_index", "body", "opaque_head_id", "line_position", "section", "language")), f"patch provenance: {patch['patch_id']}")
        require(card_by_id[patch["card_id"]]["surface"] == patch["surface"], f"patch card link: {patch['patch_id']}")
        field = {"FIRST": "first_realization_de", "MIDDLE": "middle_realization_de", "LAST": "last_realization_de"}[patch["line_position"]]
        require(patch["gdt738_scoped_whole_render_de"] == spec_map[patch["surface"]][field] != "HOLD", f"patch realization: {patch['patch_id']}")
        require(patch["position_exception"] == str(int(position_exception(patch["opaque_head_id"], patch["line_position"]))), f"patch exception flag: {patch['patch_id']}")
        require(patch["scope"] == "EXACT_COMPLETE_SURFACE_AT_ENUMERATED_OCCURRENCE", f"patch scope: {patch['patch_id']}")
        require(patch["unconditional_global_export"] == patch["literal_plaintext_claimed"] == patch["component_export_credit"] == "0", f"patch export leakage: {patch['patch_id']}")
        require("salz" not in patch["gdt738_scoped_whole_render_de"].lower(), f"literal salt patch: {patch['patch_id']}")
    check(True, "all 202 patches have exact provenance, scoped realization, and zero export")

    holds = read_tsv(art / "MANUAL_HOLD_AUDIT.tsv")
    check(len(holds) == 14 and len({row["surface"] for row in holds}) == 14, "14 unique manual hold audits")
    hold_map = {row["surface"]: row for row in holds}
    check({"solaiin", "sols"} <= set(hold_map), "both inherited literal-salt cards audited")
    for surface in ("solaiin", "sols"):
        row = hold_map[surface]
        require(row["decision"] == "HOLD_RETIRED_LITERAL_MATERIAL", f"literal salt not retired: {surface}")
        require(row["manual_text_is_audit_only"] == "1" and row["renderer_license_from_this_table"] == row["component_export_credit"] == "0", f"salt audit export leakage: {surface}")
        require("salz" not in row["best_remaining_candidate_de"].lower(), f"salt active rival: {surface}")
    check(True, "literal salt readings for solaiin and sols are audit-only retired holds")

    historical = read_tsv(art / "HISTORICAL_MICROENTRY_MODELS.tsv")
    check(len(historical) == len({row["model_id"] for row in historical}) == 8, "eight unique historical model rows")
    check(all(row["voynich_relation_credit"] == "0" and row["all_voynich_relation_credit_zero"] == "1" for row in historical), "historical comparators have zero Voynich relation credit")
    check(all(not re.search(r"/(?:home|Users)/", row["primary_urls"]) for row in historical), "historical URLs contain no local path")

    bridge = read_tsv(art / "BODY_120_SEMANTIC_BRIDGE.tsv")
    check(len(bridge) == 120 and {row["body"] for row in bridge} == set(metric_map), "120-row semantic bridge")
    check(all(row["body_renderer_license"] == row["literal_head_lexeme_credit"] == row["literal_body_lexeme_credit"] == row["component_export_credit"] == "0" for row in bridge), "bridge exports no head/body lexeme or component")
    enrichment = read_tsv(art / "AXIS_NEIGHBOR_ENRICHMENT.tsv")
    check(len(enrichment) == 6 and {row["axis"] for row in enrichment} == {"HEAT", "COLD", "DRY", "MOIST", "VALUE", "PART"}, "six core-axis enrichment diagnostics")
    check(all(row["semantic_deck"] == "W23_AXIS195" and row["component_export_credit"] == "0" for row in enrichment), "axis diagnostics are strict-deck ranks with zero export")
    matrix = read_tsv(art / "MATRIX_WORKING_MODEL.tsv")
    check(len(matrix) == 34 and all(row["literal_body_lexeme_credit"] == row["component_export_credit"] == "0" for row in matrix), "34-member analogy matrix has zero lexeme/component export")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT738_TWO_DECK_OCCURRENCE_ADJUDICATION_RESULT_V2", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["inherited_allowlist_pages"] == 179 and result["scope"]["held_pages"] == 134 and result["scope"]["held_loci"] == 697, "result scope geometry")
    check(result["scope"]["new_pages_used"] == 0 and not result["scope"]["f84_used"] and not result["scope"]["f84r_used"], "result uses no new or sealed pages")
    check(result["target"] == {"held_bodies": 120, "occupancy_2_bodies": 87, "occupancy_3_bodies": 33, "held_forms": 273, "held_occurrences": 811, "reader_exact_occurrences": 619, "adjacent_fields": 1266}, "result target geometry")
    check(result["decks"]["formal705"] == 705 and result["decks"]["sem570"] == 570 and result["decks"]["w23_axis197_precomposition"] == 197 and result["decks"]["w23_axis195"] == 195, "result two-deck counts")
    check(set(result["discovery_adjudication"]["supported_bodies"]) == DISCOVERY_BODIES and set(result["discovery_adjudication"]["surviving_forms"]) == DISCOVERY_FORMS, "result 11-body/17-form discovery")
    check(set(result["renderer_adjudication"]["supported_bodies"]) == STRICT_BODIES and set(result["renderer_adjudication"]["licensed_forms"]) == STRICT_FORMS, "result seven-body/12-form renderer")
    check(result["renderer_adjudication"]["patched_reader_exact_in_scope_occurrences"] == 202 and result["renderer_adjudication"]["unpatched_exact_position_exceptions"] == 1, "result 202 plus one position exclusion")
    check(result["claims"]["literal_head_lexemes"] == result["claims"]["literal_body_lexemes"] == result["claims"]["component_export_credit"] == result["claims"]["plaintext_translations_claimed"] == 0, "result claim ceiling")
    result_row_counts = {name: len(read_tsv(art / name)) for name in GENERATED if name.endswith(".tsv")}
    check(result["artifact_rows"] == result_row_counts, "result artifact row census")
    expected_hash_paths = {str(BASE / "artifacts" / name) for name in GENERATED if name.endswith(".tsv")}
    check(set(result["artifact_hashes"]) == expected_hash_paths, "result artifact hash inventory")
    for relative, digest in result["artifact_hashes"].items():
        require(sha256(art / Path(relative).name) == digest, f"result hash mismatch: {relative}")
    check(True, "all result artifact hashes match")

    privacy_paths = [EXP / name for name in ("README.md", "METHOD.md", "PREREGISTRATION.md", "REPORT.md") if (EXP / name).exists()]
    privacy_paths += [path for path in art.iterdir() if path.is_file()]
    for path in privacy_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        require(re.search(r"/(?:home|Users)/[^/\s]+/", text) is None, f"absolute private path: {path}")
    check(True, "documents and artifacts contain no absolute private local path")

    with tempfile.TemporaryDirectory(prefix="gdt738-replay-") as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(EXP / "src/run.py"), "--output-dir", str(replay)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        check(completed.returncode == 0, "builder replay exits zero")
        for name in GENERATED:
            require((replay / name).read_bytes() == (art / name).read_bytes(), f"replay mismatch: {name}")
        check(True, "all 13 generated artifacts replay byte-identically")

    validation = {
        "schema": "GDT738_VALIDATION_V2",
        "status": "PASS",
        "experiment_id": "GDT738",
        "checks_passed": len(checks),
        "checks": checks,
        "manifest_mode": "PLACEHOLDER_PRESEAL" if placeholder else "SEALED",
        "validated_result_sha256": sha256(art / "RESULT.json"),
        "builder_replay": "BYTE_IDENTICAL",
        "claim_ceiling": (
            "GDT738 retains an 11-body/17-form discovery deck and licenses only the W23-AXIS195 "
            "seven-body/12-form intersection at 202 enumerated reader-exact in-position occurrences. "
            "State patients and scalar dimensions remain open. It exports no H1-H4 value, body lexeme, "
            "component, plaintext, unseen form, historical relation, new page, f84, or f84r claim."
        ),
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "checks_passed": len(checks), "manifest_mode": validation["manifest_mode"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
