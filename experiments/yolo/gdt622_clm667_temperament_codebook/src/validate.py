#!/usr/bin/env python3
"""Offline consistency validator for the GDT622 working codebook."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt622_clm667_temperament_codebook")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
MANIFEST_REL = BASE_REL / "experiment.json"
RUN_REL = BASE_REL / "src/run.py"

GENERATED_RELS = (
    BASE_REL / "artifacts/CANDIDATE_FAMILY_SUMMARY.tsv",
    BASE_REL / "artifacts/CANDIDATE_FAMILY_OCCURRENCES.tsv",
    BASE_REL / "artifacts/EXACT_FORM_OCCURRENCES.tsv",
    BASE_REL / "artifacts/MINIMAL_PAIR_EVIDENCE.tsv",
    BASE_REL / "artifacts/DEGREE_PAIR_MATRIX.tsv",
    BASE_REL / "artifacts/BLOCK_EVIDENCE.tsv",
    BASE_REL / "artifacts/CANDIDATE_ALIGNMENT.tsv",
    BASE_REL / "artifacts/ORIENTATION_COMPARISON.tsv",
    BASE_REL / "artifacts/DECK_ORIENTATION_COMPARISON.tsv",
    BASE_REL / "artifacts/MARKER_PREVALENCE.tsv",
    BASE_REL / "artifacts/ALTERNATE_READING_EVIDENCE.tsv",
    BASE_REL / "artifacts/WORKING_DICTIONARY.tsv",
    BASE_REL / "artifacts/WORKING_TRANSLATION.tsv",
    RESULT_REL,
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")
PRIVATE_PATHS = "/" + "home/" + "|/" + "tmp/"
PRIVATE = re.compile(
    PRIVATE_PATHS + r"|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
    r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
    r"password\s*[=:]|api[_-]?key\s*[=:]|secret\s*[=:]",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    checks: list[str] = []

    def require(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    before = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    replay = subprocess.run(
        [sys.executable, str(ROOT / RUN_REL)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(replay.returncode == 0, "builder replay exits zero")
    require("sealed_rows_rejected" in replay.stdout, "builder reports guarded rows")
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    source = read_tsv(ART / "SOURCE_OBSERVATIONS.tsv")
    require(len(source) == 28, "28 manual Clm observations")
    require(len({row["row_id"] for row in source}) == 28, "Clm row ids unique")
    require({int(row["scan"]) for row in source} == {161, 163, 165, 167, 169}, "five Clm scans")
    require({row["thermal"] for row in source} == {"HOT", "COLD"}, "both thermal values observed")
    require({row["moisture"] for row in source if row["moisture"]} == {"DRY", "MOIST"}, "both moisture values observed")
    degrees = {
        value
        for row in source
        for value in (row["thermal_degree"], row["moisture_degree"])
        if value
    }
    require(degrees == {"1", "2", "3", "4"}, "degrees one through four observed")
    require(all(row["image_url"].startswith("https://api.digitale-sammlungen.de/iiif/image/v2/bsb00051579_") for row in source), "official BSB image URLs only")
    require(all(HEX64.fullmatch(row["image_sha256"]) for row in source), "source image hashes are SHA256")
    require(any(row["lemma"] == "Balsamum" and row["code_surface"] == "c s 2" for row in source), "Balsamum hot-dry-two control")
    require(any(row["lemma"] == "Bdellium" and row["code_surface"] == "c 2 h pbar" for row in source), "separate hot-moist degrees control")
    require(any(row["lemma"] == "terra sigillata" for row in source), "nonplant drug control")

    provenance = read_tsv(ART / "SOURCE_PROVENANCE.tsv")
    require(len(provenance) == 7, "seven compact provenance bindings")
    provenance_by_id = {row["source_id"]: row for row in provenance}
    require(provenance_by_id["BSB_CLM667_MANIFEST"]["sha256"] == "6d45ab1c1e2318445033ffe053e3267ac9681ecd9745d2f3304f6af8ee5db2c1", "official Clm667 manifest hash")
    require(provenance_by_id["GDT621_FINAL_CONTEXT"]["sha256"] == sha256(ROOT / "experiments/yolo/gdt621_manual_source_double_reading/FINAL_RESULT.md"), "corrected GDT621 source report bound")

    candidates = read_tsv(ART / "CANDIDATE_DECK.tsv")
    require(len(candidates) == 11, "eleven candidate rows")
    require(len({row["candidate_id"] for row in candidates}) == 11, "candidate ids unique")
    preferred = {
        row["plant"]: (row["folio"], row["name_carrier_default"])
        for row in candidates
        if row["working_selection"] == "PREFERRED"
    }
    require(
        preferred
        == {
            "Balsamus": ("f38r", "tolor"),
            "Cerfolium": ("f41v", "keeredal"),
            "Cucurbita": ("f24r", "por"),
            "Diptamus": ("f3r", "tsheos"),
            "Liquiritia": ("f45r", "pykydal"),
        },
        "one explicit preferred page and carrier per plant",
    )
    require(all(row["identity_source_ref"] and row["identity_scope"] for row in candidates), "every identity candidate has explicit provenance scope")
    require(not any(row["folio"].startswith("f84") for row in candidates), "candidate deck excludes sealed folios")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT622_CLM667_TEMPERAMENT_CODEBOOK_RESULT_V1", "result schema")
    require(result["status"] == "CONCRETE_COMPOSITIONAL_WORKING_TRANSLATION_V1", "result status")
    claimed_content_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_content_hash, "result canonical content hash")
    result["content_sha256"] = claimed_content_hash
    require(result["guard"]["skipped_forbidden"] == 709, "mixed TSV rejects all sealed rows")
    require(all(int(value) > 0 for value in result["guard"]["manual_reading_forbidden_rows_skipped"].values()), "manual sources reject sealed loci before payload parse")
    require(result["guard"]["f84"] == "FORBIDDEN_AND_REJECTED_BEFORE_ROW_PARSE", "f84 guard status")
    require(result["guard"]["f84r"] == "FORBIDDEN_AND_REJECTED_BEFORE_ROW_PARSE", "f84r guard status")
    require(result["historical_mechanism"]["confirmed_values"] == {"c": "HOT", "f": "COLD", "h": "MOIST", "pbar": "DEGREE_1", "s": "DRY"}, "historical code values")
    require(result["voynich_working_model"]["working_values"] == {"ch": "MOIST", "k": "HOT", "qo": "QUALITY_FIELD_WRAPPER", "sh": "DRY", "t": "COLD"}, "Voynich quality defaults")
    require(result["voynich_working_model"]["local_working_degree_defaults"] == {"I": "UNMARKED_ON_LIQUORICE_WINDOWS_ONLY", "II": "otaiin-family candidate", "III": "(q)okol + daiin candidate"}, "three explicitly local degree defaults")
    require("adjacency is not established" in result["voynich_working_model"]["grammar"], "page-record grammar does not invent adjacency")
    for path, expected_hash in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected_hash, f"result input hash {path}")
    for path, expected_hash in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected_hash, f"result output hash {path}")
    require(set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL}, "result binds every generated evidence artifact")

    exact = read_tsv(ART / "EXACT_FORM_OCCURRENCES.tsv")
    exact_counts = Counter(row["surface"] for row in exact)
    require(set(exact_counts) == {"qokchy", "qokchey", "qokshy", "qokshey", "qotchy", "qotchey", "qotshy", "qotshey"}, "all eight exact orthographic quality forms occur")
    require(sum(row["surface"] == "qokshey" and row["corpus_group"] == "HERBAL_A" for row in exact) == 1, "qokshey fragility is explicit")
    require(not any(row["page"].startswith("f84") for row in exact), "exact-form artifact excludes sealed folios")

    minimal = read_tsv(ART / "MINIMAL_PAIR_EVIDENCE.tsv")
    require(len(minimal) == 13, "thirteen exact within-line minimal pairs")
    require(Counter(row["changed_axis"] for row in minimal) == {"THERMAL_K_T": 10, "MOISTURE_CH_SH": 3}, "both compositional axes have minimal pairs")
    require({("f24r", "f24r.12"), ("f25r", "f25r.3"), ("f28v", "f28v.5")} <= {(row["page"], row["locus"]) for row in minimal}, "canonical thermal and moisture minimal pairs")

    alternate = read_tsv(ART / "ALTERNATE_READING_EVIDENCE.tsv")
    require(len(alternate) == 33, "thirty-three selected three-reading loci")
    alternate_by_locus = {row["locus"]: row for row in alternate}
    require(alternate_by_locus["f3r.13"]["agreement_class"] == "ZL_RF_QOKSHEY__IT_QOKCHEY", "f3 hot-dry reading disagreement explicit")
    require(alternate_by_locus["f24r.12"]["agreement_class"] == "QOKCHY_QOTCHY_STABLE_ALL_THREE", "f24 thermal pair stable across readings")
    require(alternate_by_locus["f24r.1"]["agreement_class"] == "ZL_POR_SPLIT__IT_RF_PORORY_JOINED", "f24 carrier tokenization instability explicit")
    require(all(row["reading_rule"] == "ALTERNATE_READINGS_OF_ONE_MANUSCRIPT" for row in alternate), "readings never counted as replications")

    orientation = read_tsv(ART / "ORIENTATION_COMPARISON.tsv")
    require(len(orientation) == 8, "all eight axis orientations compared")
    require(orientation[0]["assignment_id"] == "KT_THERMAL__k_HOT__ch_MOIST" and orientation[0]["matched_occurrences"] == "8" and orientation[0]["total_family_occurrences"] == "13", "proposed orientation leads preferred local count score")
    require(orientation[1]["matched_occurrences"] == "6", "orientation runner-up remains visible")

    deck_orientation = read_tsv(ART / "DECK_ORIENTATION_COMPARISON.tsv")
    require(len(deck_orientation) == 16, "two decks by eight orientations")
    proposed_direct = next(row for row in deck_orientation if row["deck_id"] == "INTERNAL_DIRECT_IMAGE_MATCHES" and row["assignment_id"] == "KT_THERMAL__k_HOT__ch_MOIST")
    require(proposed_direct["count_rank_min"] == "1" and proposed_direct["binary_rank_min"] == "2" and proposed_direct["degree_marker_matches"] == "2", "direct-image weakness remains explicit")

    markers = {row["marker"]: row for row in read_tsv(ART / "MARKER_PREVALENCE.tsv")}
    require((markers["OTAIIN_FAMILY"]["occurrences"], markers["OTAIIN_FAMILY"]["pages"]) == ("234", "81"), "otaiin commonness recorded")
    require((markers["QOKOL_DAIIN_ADJACENT"]["occurrences"], markers["QOKOL_DAIIN_ADJACENT"]["pages"]) == ("9", "8"), "rare degree-III candidate prevalence recorded")

    alignment = {row["plant"]: row for row in read_tsv(ART / "CANDIDATE_ALIGNMENT.tsv")}
    require(len(alignment) == 5, "five candidate alignment records")
    require(alignment["Balsamus"]["alignment_scope"] == "SAME_LINE", "Balsam name and quality same-line")
    require(alignment["Diptamus"]["name_to_quality_line_distance"] == "12", "Diptam attachment distance explicit")
    require(alignment["Cucurbita"]["name_surface"].startswith("por [ZL3b] | porory"), "Cucurbita carrier is a reading variant not a fixed word")

    blocks = read_tsv(ART / "BLOCK_EVIDENCE.tsv")
    require(len(blocks) == 9, "nine local candidate blocks")
    preferred_blocks = [row for row in blocks if row["working_selection"] == "PREFERRED"]
    require(len(preferred_blocks) == 4, "four coded preferred blocks")
    require(all(row["degree_marker_match"] == "1" for row in preferred_blocks), "all preferred coded blocks match degree defaults")
    require({row["candidate_id"] for row in blocks if row["degree_marker_match"] == "0"} == {"BAL_DIRECT_1", "CUC_DIRECT_1"}, "two retained visual alternatives expose degree mismatches")
    require(not any(row["folio"].startswith("f84") for row in blocks), "block artifact excludes sealed folios")
    require(all(row["herbal_a_baseline_pages"] == "90" for row in blocks), "every block has a 90-page Herbal-A baseline")

    dictionary = read_tsv(ART / "WORKING_DICTIONARY.tsv")
    dictionary_map = {(row["surface"], row["default_meaning_de"]) for row in dictionary}
    require({("k", "heiß"), ("t", "kalt"), ("ch", "feucht"), ("sh", "trocken")} <= dictionary_map, "four atomic quality defaults")
    require({("qokch-(y|ey)", "Temperament: heiß und feucht"), ("qoksh-(y|ey)", "Temperament: heiß und trocken"), ("qotch-(y|ey)", "Temperament: kalt und feucht"), ("qotsh-(y|ey)", "Temperament: kalt und trocken")} <= dictionary_map, "four complete quality bundle readings")
    require(("otaiin-family", "Grad 2") in dictionary_map and ("(q)okol + daiin", "Grad 3") in dictionary_map, "concrete degree-II and degree-III defaults")
    require(not any(row["surface"] in {"sy | s y", "d- … -d"} for row in dictionary), "unsupported syntax carryovers absent")

    translations = read_tsv(ART / "WORKING_TRANSLATION.tsv")
    require(len(translations) == 5, "five candidate page readings")
    require(sum(bool(row["voynich_span_reading_de"]) for row in translations) == 4, "exactly four target temperament span readings")
    require(sum(row["status"] == "VISUAL_LABEL_IDENTITY_HYPOTHESIS_ONLY" for row in translations) == 1, "Cerfolium remains one visual label hypothesis")
    joined_translation = " ".join(
        row["source_expected_content_de"]
        + " "
        + row["voynich_span_reading_de"]
        + " "
        + row["unmapped_source_content_de"]
        for row in translations
    )
    require(all(term in joined_translation for term in ("Balsam", "Kerbel", "Kürbis", "Diptam", "Süßholz", "Wurzel", "heiß", "kalt", "feucht", "trocken", "Grad 1", "Grad 2", "Grad 3")), "candidate readings retain concrete plants, properties, part and degrees")
    require(all(row["voynich_span_reading_de"] == "" or re.match(r"^f[0-9]+[rv][0-9]*\.[0-9]+ [^ ]+ → (?:KCH|KSH|TCH|TSH) → ", row["voynich_span_reading_de"]) for row in translations), "every concrete target meaning names one locus and surface")
    require("Wurzel hat noch keinen Voynich-Span" in joined_translation, "unmapped liquorice root remains explicit")
    require(not re.search(r"Arbeitsgut|Arbeitschritt|leite weiter|führe .+ aus", joined_translation, re.IGNORECASE), "generic placeholder prose absent")

    manifest = json.loads((ROOT / MANIFEST_REL).read_text(encoding="utf-8"))
    require(manifest["experiment_id"] == "GDT622", "manifest experiment id")
    require(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals both forbidden folios")
    for entry in manifest["inputs"] + manifest["outputs"]:
        if entry["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / entry["path"]
        require(path.is_file(), f"manifest file exists {entry['path']}")
        require(sha256(path) == entry["sha256"], f"manifest hash {entry['path']}")

    for path in BASE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".py", ".tsv"}:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        require(PRIVATE.search(text) is None, f"privacy scan {path.relative_to(ROOT)}")

    validation = {
        "schema": "GDT622_VALIDATION_V1",
        "experiment_id": "GDT622",
        "status": "PASS",
        "checks": checks,
        "check_count": len(checks),
        "result_content_sha256": claimed_content_hash,
        "builder_replay": "BYTE_IDENTICAL",
    }
    validation["content_sha256"] = canonical_hash(validation)
    (ROOT / VALIDATION_REL).write_bytes(canonical_bytes(validation))
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
