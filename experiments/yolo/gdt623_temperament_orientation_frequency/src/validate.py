#!/usr/bin/env python3
"""Deterministic validator for GDT623."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RUN_REL = BASE_REL / "src/run.py"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
MANIFEST_REL = BASE_REL / "experiment.json"

GENERATED_RELS = (
    BASE_REL / "artifacts/FAMILY_COUNTS.tsv",
    BASE_REL / "artifacts/SECTION_FAMILY_COUNTS.tsv",
    BASE_REL / "artifacts/SOURCE_QUADRANT_COUNTS.tsv",
    BASE_REL / "artifacts/ORIENTATION_FREQUENCY_COMPARISON.tsv",
    BASE_REL / "artifacts/MARGINAL_AXIS_COMPARISON.tsv",
    BASE_REL / "artifacts/HEADER_REPEAT_AUDIT.tsv",
    BASE_REL / "artifacts/INITIAL_SHELL_AUDIT.tsv",
    BASE_REL / "artifacts/CARRIER_EVIDENCE.tsv",
    BASE_REL / "artifacts/CARRIER_FAMILY_SUMMARY.tsv",
    BASE_REL / "artifacts/SUFFIX_AUDIT.tsv",
    BASE_REL / "artifacts/STATE_WORD_AUDIT.tsv",
    BASE_REL / "artifacts/BINDING_RULES.tsv",
    BASE_REL / "artifacts/WORKING_DICTIONARY_V2.tsv",
    BASE_REL / "artifacts/CONCRETE_READINGS_V2.tsv",
    RESULT_REL,
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")
PRIVATE = re.compile(
    r"/home/|/tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
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
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


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
    require("sealed_rows_rejected=709" in replay.stdout, "builder reports 709 guarded rows")
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT623_TEMPERAMENT_ORIENTATION_AND_ATTACHMENT_RESULT_V1", "result schema")
    require(result["status"] == "WORKING_TRANSLATION_V2__MOISTURE_AXIS_FLIPPED__LOCAL_ATTACHMENT_REPAIRED", "result status")
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "result canonical content hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"]["skipped_forbidden"] == 709, "mixed TSV rejects all sealed rows")
    require(result["guard"]["f1r"] == "EXCLUDED_BEFORE_QUERY_ALLOW_LIST", "f1r excluded before query")
    require(result["guard"]["manual_extra_pages"] == ["f31v"], "one explicit visual-only extra page")
    require(result["summary"]["safe_pages_no_f1r"] == 179, "179-page frequency panel")
    require(result["summary"]["safe_tokens_no_f1r"] == 32339, "32339-token frequency panel")
    require(result["summary"]["concrete_reading_spans"] == 20, "twenty concrete reading spans")
    require(result["summary"]["historical_layout_rows"] == 8, "eight historical layout rows")
    require(result["summary"]["visual_role_rows"] == 11, "eleven visual role rows")
    for path, expected in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"result input hash {path}")
    for path, expected in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"result output hash {path}")
    require(set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL}, "result binds all generated evidence")

    source = read_tsv(ART / "SOURCE_QUADRANT_COUNTS.tsv")
    source_map = {(row["thermal"], row["moisture"]): int(row["observations"]) for row in source}
    require(source_map == {("HOT", "DRY"): 19, ("HOT", "MOIST"): 3, ("COLD", "DRY"): 5, ("COLD", "MOIST"): 0}, "Clm complete-row quadrant counts")

    families = read_tsv(ART / "FAMILY_COUNTS.tsv")
    count_map = {(row["scope"], row["mode"], row["family"]): int(row["occurrences"]) for row in families}
    require([count_map[("ALL_SAFE_NO_F1R", "EXACT_Y_EY", family)] for family in ("KCH", "KSH", "TCH", "TSH")] == [89, 17, 79, 7], "whole-panel exact family counts")
    require([count_map[("ALL_SAFE_NO_F1R", "Q_PREFIX", family)] for family in ("KCH", "KSH", "TCH", "TSH")] == [250, 41, 205, 16], "whole-panel q-prefix family counts")
    require([count_map[("HERBAL_A", "EXACT_Y_EY", family)] for family in ("KCH", "KSH", "TCH", "TSH")] == [42, 4, 55, 5], "Herbal-A exact family counts")
    require([count_map[("HERBAL_A", "Q_PREFIX", family)] for family in ("KCH", "KSH", "TCH", "TSH")] == [93, 7, 110, 6], "Herbal-A q-prefix family counts")

    marginals = read_tsv(ART / "MARGINAL_AXIS_COMPARISON.tsv")
    all_prefix = {(row["symbol_axis"], row["semantic_axis"], row["mapping"]): row for row in marginals if row["scope"] == "ALL_SAFE_NO_F1R" and row["mode"] == "Q_PREFIX"}
    require(all_prefix[("CH_SH", "MOISTURE", "CH=DRY")]["target_fraction"] == "0.888672", "ch dry prefix fraction")
    require(float(all_prefix[("CH_SH", "MOISTURE", "CH=DRY")]["absolute_error"]) < 0.001, "ch-dry marginal matches source")
    require(float(all_prefix[("CH_SH", "MOISTURE", "SH=DRY")]["absolute_error"]) > 0.77, "old sh-dry marginal strongly mismatches")

    orientations = read_tsv(ART / "ORIENTATION_FREQUENCY_COMPARISON.tsv")
    def orientation(scope: str, mode: str, flag: str) -> dict[str, str]:
        return next(row for row in orientations if row["scope"] == scope and row["mode"] == mode and row[flag] == "1")
    require(orientation("ALL_SAFE_NO_F1R", "EXACT_Y_EY", "is_v2")["rank_within_scope_mode"] == "1", "v2 leads whole-panel exact frequency")
    require(orientation("ALL_SAFE_NO_F1R", "Q_PREFIX", "is_v2")["rank_within_scope_mode"] == "1", "v2 leads whole-panel prefix frequency")
    require(orientation("HERBAL_A", "EXACT_Y_EY", "is_v2")["rank_within_scope_mode"] == "3", "v2 only third on Herbal-A exact frequency")
    require(orientation("HERBAL_A", "EXACT_Y_EY", "is_v1")["rank_within_scope_mode"] == "8", "old v1 last on Herbal-A exact frequency")
    require(result["working_v2"]["values"] == {"ch": "DRY", "k": "HOT", "sh": "MOIST", "t": "COLD"}, "v2 atomic defaults")

    headers = {row["surface"]: row for row in read_tsv(ART / "HEADER_REPEAT_AUDIT.tsv")}
    require(headers["kooiin"]["header_occurrences"] == "2" and headers["kooiin"]["nearest_quality_families_plus3"] == "TCH|TCH", "kooiin exact double TCH page head")
    initials = {(row["inventory"], row["initial"]): row for row in read_tsv(ART / "INITIAL_SHELL_AUDIT.tsv")}
    require(float(initials[("HERBAL_PAGE_HEADS", "P_OR_T_OR_K_OR_F")]["rate"]) > 0.89, "p-t-k-f shell enriched at Herbal heads")
    require(float(initials[("ALL_TOKENS", "P_OR_T_OR_K_OR_F")]["rate"]) < 0.09, "p-t-k-f shell rare globally")

    carriers = read_tsv(ART / "CARRIER_FAMILY_SUMMARY.tsv")
    accepted = [row for row in carriers if row["accepted_local_attachment"] == "1"]
    require(len(accepted) == 6, "six accepted local carrier families")
    require(all(row["carrier_id"].startswith("EXACT_") and row["exact_surface_occurs_twice_globally"] == "1" for row in accepted), "all accepted carriers are exact twice forms")
    require({row["carrier_id"] for row in accepted} == {"EXACT_DSHEODY", "EXACT_KOOIIN", "EXACT_PORAIIN", "EXACT_TCHDOR", "EXACT_TSHOD", "EXACT_YSHOL"}, "accepted carrier ids")
    pdair = next(row for row in carriers if row["carrier_id"] == "FAMILY_PDAIR_ROOT")
    require(pdair["qualified_occurrences"] == "5" and set(pdair["pages"].split("|")) == {"f18r", "f23v", "f31v", "f39v", "f43v"}, "five p-air visual heads")
    require(pdair["accepted_local_attachment"] == "0" and pdair["expected_families"] == "MIXED", "p-air keeps temperament separate")
    koary = next(row for row in carriers if row["carrier_id"] == "FAMILY_KOARY")
    require(koary["members"] == "koary|korary" and koary["accepted_local_attachment"] == "0", "koair excluded and distant koary family not called local")

    states = read_tsv(ART / "STATE_WORD_AUDIT.tsv")
    state_map = {(row["state_id"], row["context"]): row for row in states}
    chody = state_map[("CHODY", "ALL_SAFE_NO_F1R")]
    require((chody["occurrences"], chody["pages"], chody["no_strict_q_on_page"], chody["nearest_dry"], chody["nearest_moist"]) == ("78", "56", "12", "65", "1"), "chody nearest-code counts")
    require((chody["within_one_line_dry"], chody["within_one_line_moist"]) == ("33", "1"), "chody one-line counts")
    shody = state_map[("SHODY", "ALL_SAFE_NO_F1R")]
    require((shody["nearest_dry"], shody["nearest_moist"]) == ("37", "1"), "shody counterevidence explicit")
    shedy = state_map[("SHEDY", "ALL_SAFE_NO_F1R")]
    require((shedy["occurrences"], shedy["nearest_dry"], shedy["nearest_moist"]) == ("390", "247", "79"), "shedy nearest-code counts")
    require(state_map[("SHEDY", "SECTION_B__LANG_B")]["occurrences"] == "184", "Biological-B shedy concentration")
    require(("CHODY", "SECTION_B__LANG_B") not in state_map, "Biological section has no exact chody")
    require(float(shedy["nearest_moist_rate"]) > 2 * float(shedy["corpus_q_moist_rate"]), "shedy moist enrichment exceeds twofold")

    suffixes = {row["surface_or_pair"]: row for row in read_tsv(ART / "SUFFIX_AUDIT.tsv")}
    require((suffixes["or"]["occurrences"], suffixes["or"]["types_or_left_bases"]) == ("1855", "337"), "or suffix counts")
    require((suffixes["os"]["occurrences"], suffixes["os"]["types_or_left_bases"]) == ("257", "115"), "os suffix counts")
    require((suffixes["dal"]["occurrences"], suffixes["dal"]["types_or_left_bases"]) == ("415", "107"), "dal suffix counts")

    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V2.tsv")
    dictionary_map = {(row["surface"], row["default_meaning_de"]) for row in dictionary}
    require({("k", "heiß"), ("t", "kalt"), ("ch", "trocken"), ("sh", "feucht")} <= dictionary_map, "four atomic v2 meanings")
    require({("qokch-", "heiß und trocken"), ("qoksh-", "heiß und feucht"), ("qotch-", "kalt und trocken"), ("qotsh-", "kalt und feucht")} <= dictionary_map, "four concrete v2 bundles")
    require(("chody", "trocken oder Trockenklasse") in dictionary_map, "chody concrete dry-class default")
    require(("shody", "gelernte Form im Trocken-Kontext; konkrete Bedeutung offen") in dictionary_map, "shody moist reading rejected")
    require(("shedy", "feucht oder Feuchtklasse") in dictionary_map, "shedy weak moist-class default")
    require(any(row["surface"].startswith("pdrairdy|") and row["default_meaning_de"].startswith("Wurzelteil") for row in dictionary), "p-air radix default")
    require(("shor", "Blüten- oder Fruchtstand; reproduktiver Kopf") in dictionary_map, "shor reproductive-head default")
    require(("koary|korary", "Frucht-, Samen- oder Reproduktivdroge") in dictionary_map, "koary reproductive-drug default")
    require(not any("Pflanzenmaterial zeitgebunden beschaffen" in row["default_meaning_de"] for row in dictionary), "no long generic pseudo-lexeme")

    readings = read_tsv(ART / "CONCRETE_READINGS_V2.tsv")
    require(len(readings) == 20, "twenty rendered spans")
    require({"PDROOT_F23", "PDROOT_F31", "KOOIIN_F2", "KOOIIN_F29", "DSHEODY_F86", "STATE_CHODY_F56"} <= {row["reading_id"] for row in readings}, "root state and carrier readings present")
    joined = " ".join(row["working_reading_de"] for row in readings)
    require(all(term in joined for term in ("Wurzelteil/Radix-Eintrag", "kalt und trocken", "heiß und trocken", "trocken/Trockenklasse", "feucht/Feuchtklasse?", "Blüten-/Fruchtstand?")), "concrete vocabulary appears in readings")
    require("<" in joined and ">" in joined, "unknown surfaces remain visible")
    require(not re.search(r"Arbeitsgut|Arbeitschritt|leite weiter|führe .+ aus", joined, re.IGNORECASE), "generic placeholder prose absent")

    provenance = read_tsv(ART / "SOURCE_PROVENANCE.tsv")
    provenance_map = {row["source_id"]: row for row in provenance}
    require(provenance_map["BAV_PAL1234_MANIFEST"]["sha256"] == "e7e451a26b35763f7f0b9473854927306bcd0105d2393b5b180161aca5dbcdbb", "Pal.lat.1234 manifest hash")
    require(provenance_map["YALE_F23V"]["sha256"] == "0908354978f67f76d6f022879e235c96f415f85d2fbdc5b0925fc241037bc381", "f23v image hash")
    require(provenance_map["YALE_F31V"]["sha256"] == "e3ec3fb25fc9134d0489567f103a90be666e366fbc0a95fe38596eb20f5230f3", "f31v image hash")
    require(provenance_map["WELLCOME_MS541_F184R"]["sha256"] == "e803af4d70ad9f1c2526e269dfaf0def09f674698cf38b410ca0d948b2ec8fa1", "Wellcome MS541 f184r image hash")
    require(all(row["sha256"] == "WEB_RESULT_NOT_HASHED" or HEX64.fullmatch(row["sha256"]) for row in provenance), "provenance hashes valid or explicitly web-only")
    require(len(read_tsv(ART / "VISUAL_OBSERVATIONS.tsv")) == 7, "seven manual visual observations")
    require(len(read_tsv(ART / "HISTORICAL_LAYOUT_OBSERVATIONS.tsv")) == 8, "eight historical layout observations")
    require(len(read_tsv(ART / "VISUAL_ROLE_AUDIT.tsv")) == 11, "eleven manual visual role rows")
    require(len(read_tsv(ART / "ALTERNATE_READING_AUDIT.tsv")) == 8, "eight alternate-reading audits")

    manifest = json.loads((ROOT / MANIFEST_REL).read_text(encoding="utf-8"))
    require(manifest["experiment_id"] == "GDT623", "manifest experiment id")
    require(manifest["status"] == result["status"], "manifest and result status agree")
    require(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals f84 and f84r")
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
        require(PRIVATE.search(path.read_text(encoding="utf-8")) is None, f"privacy scan {path.relative_to(ROOT)}")

    validation = {
        "schema": "GDT623_VALIDATION_V1",
        "experiment_id": "GDT623",
        "status": "PASS",
        "checks": checks,
        "check_count": len(checks),
        "result_content_sha256": claimed_hash,
        "builder_replay": "BYTE_IDENTICAL",
    }
    validation["content_sha256"] = canonical_hash(validation)
    (ROOT / VALIDATION_REL).write_bytes(canonical_bytes(validation))
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
