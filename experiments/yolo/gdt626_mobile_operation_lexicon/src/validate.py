#!/usr/bin/env python3
"""Validate and byte-replay GDT626."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt626_mobile_operation_lexicon")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED_RELS = (
    BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    BASE_REL / "artifacts/MINIM_SUFFIX_OCCURRENCES.tsv",
    BASE_REL / "artifacts/MINIM_VALUE_TOTALS.tsv",
    BASE_REL / "artifacts/VALUE_CONTEXT_PROFILES.tsv",
    BASE_REL / "artifacts/MINIM_FAMILY_SUMMARY.tsv",
    BASE_REL / "artifacts/FOUR_CELL_FAMILIES.tsv",
    BASE_REL / "artifacts/MIXED_VALUE_LINES.tsv",
    BASE_REL / "artifacts/READING_VALUE_TOTALS.tsv",
    BASE_REL / "artifacts/QUALITY_VALUE_COMPOUNDS.tsv",
    BASE_REL / "artifacts/QUALITY_VALUE_MATRIX.tsv",
    BASE_REL / "artifacts/PART_VALUE_COMPOUNDS.tsv",
    BASE_REL / "artifacts/DA_VALUE_CONTEXTS.tsv",
    BASE_REL / "artifacts/ROLE_RIVAL_RANKING.tsv",
    BASE_REL / "artifacts/WORKING_DICTIONARY_V3.tsv",
    BASE_REL / "artifacts/CONCRETE_LOCAL_READINGS.tsv",
    RESULT_REL,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    before = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    completed = subprocess.run([sys.executable, str(BASE / "src/run.py")], cwd=ROOT, text=True, capture_output=True, check=False)
    require(completed.returncode == 0, "builder exits zero")
    require("minim=5176 heads=545 complete4=15 mixed=136 quality=47 parts=28 daiin=721" in completed.stdout, "builder summary")
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT626_MINIM_VALUE_LEXICON_RESULT_V1", "result schema")
    require(result["status"] == "FOUR_CELL_MINIM_VALUE_READER__QUALITY_DEGREES_COMPOSE__DAIIN_RESEGMENTED", "result status")
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "canonical result hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"]["safe_pages"] == 179, "179 safe pages")
    require(result["guard"]["safe_tokens"] == 32339, "32339 safe token rows")
    require(result["guard"]["token_query"] == {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}, "token guard counts")
    require(result["guard"]["cross_query"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}, "cross guard counts")
    require(result["guard"]["new_image_pages"] == 0, "no new image pages")
    require(result["minim_family"] == {
        "above_IV_occurrences": 0,
        "complete_I_II_III_IV_heads": 15,
        "complete_I_II_III_heads": 28,
        "heads": 545,
        "line_last_counts": {"I": 38, "II": 163, "III": 368, "IV": 16},
        "maximum_value": 4,
        "mixed_same_head_lines": 136,
        "occurrences": 5176,
        "stable_mixed_same_head_lines": 96,
        "stable_value_counts": {"I": 83, "II": 1280, "III": 2750, "IV": 80},
        "three_or_more_value_lines": 2,
        "value_counts": {"I": 102, "II": 1565, "III": 3404, "IV": 105},
    }, "minim result summary")
    require(result["quality_value_compounds"] == {"occurrences": 47, "pages": 33, "state_counts": {"KCH": 19, "KSH": 2, "TCH": 23, "TSH": 3}, "surfaces": 38, "triple_stable_occurrences": 37}, "quality result summary")
    require(result["part_value_compounds"] == {"herbal_occurrences": 22, "occurrences": 28, "pages": 22, "root_counts": {"chor": 7, "cth": 20, "shor": 1}, "surfaces": 11}, "part result summary")
    require(result["da_resegmentation"]["counts"] == {"I": 17, "II": 193, "III": 721, "IV": 17}, "da result counts")
    require(result["numeric_rival"]["context_profile_rows"] == 11, "eleven context profiles")
    require(result["manual_sources"] == {"concrete_readings": 9, "historical_numeral_comparators": 9, "visual_judgments": 5}, "manual source counts")
    for path, expected in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"input hash {path}")
    for path, expected in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"output hash {path}")
    require(set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL}, "result binds every generated evidence file")

    allowlist = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    require(len(allowlist) == 179, "allow-list length")
    require(sha256(ART / "PAGE_ALLOWLIST.tsv") == "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483", "canonical allow-list hash")
    require("f1r" not in {row["page"] for row in allowlist}, "allow-list excludes f1r")
    require(not any(row["page"].startswith("f84") for row in allowlist), "allow-list excludes f84 family")

    occurrences = read_tsv(ART / "MINIM_SUFFIX_OCCURRENCES.tsv")
    require(len(occurrences) == 5176, "5176 minim occurrences")
    require(Counter(row["working_roman"] for row in occurrences) == Counter({"I": 102, "II": 1565, "III": 3404, "IV": 105}), "four value totals")
    require(max(int(row["written_i_minims"]) for row in occurrences) == 3, "at most three internal minims")
    require(sum(int(row["triple_reading_token_stable"]) for row in occurrences) == 4193, "4193 stable minim occurrences")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences), "occurrences exclude forbidden pages")

    totals = read_tsv(ART / "MINIM_VALUE_TOTALS.tsv")
    require(len(totals) == 4, "four value summary rows")
    require({row["working_roman"]: int(row["line_last"]) for row in totals} == {"I": 38, "II": 163, "III": 368, "IV": 16}, "line-last value profiles")
    profiles = read_tsv(ART / "VALUE_CONTEXT_PROFILES.tsv")
    require(len(profiles) == 11, "eleven context profile rows")
    profile = {(row["dimension"], row["dimension_value"]): row for row in profiles}
    require(profile["SECTION", "H"]["III_share_among_II_III"] == "0.820952", "Herbal III share")
    require(profile["SECTION", "B"]["III_share_among_II_III"] == "0.454913", "Biological III share")
    require(profile["HAND", "1"]["III_share_among_II_III"] == "0.840283", "Hand 1 III share")
    require(profile["HAND", "2"]["III_share_among_II_III"] == "0.608183", "Hand 2 III share")

    families = read_tsv(ART / "MINIM_FAMILY_SUMMARY.tsv")
    require(len(families) == 545, "545 head families")
    require(sum(int(row["complete_I_II_III"]) for row in families) == 28, "28 complete three-cell families")
    require(sum(int(row["complete_I_II_III_IV"]) for row in families) == 15, "15 complete four-cell families")
    da_family = next(row for row in families if row["head"] == "da")
    require(tuple(da_family[f"count_{value}"] for value in ("I", "II", "III", "IV")) == ("17", "193", "721", "17"), "da family exact counts")
    complete = read_tsv(ART / "FOUR_CELL_FAMILIES.tsv")
    require(len(complete) == 15 and {"da", "a", "qoka", "oka"} <= {row["head"] for row in complete}, "fifteen four-cell families include core heads")

    mixed = read_tsv(ART / "MIXED_VALUE_LINES.tsv")
    require(len(mixed) == 136, "136 mixed-value lines")
    require(sum(int(row["all_series_tokens_triple_stable"]) for row in mixed) == 96, "96 stable mixed-value lines")
    require(sum(len(row["values"].split("|")) >= 3 for row in mixed) == 2, "two three-value lines")
    f42 = next(row for row in mixed if row["locus"] == "f42v.2" and row["head"] == "da")
    require((f42["values"], f42["series_surfaces_in_order"]) == ("I|II|III", "dan|dain|daiin"), "f42 I-II-III witness")
    f38 = next(row for row in mixed if row["locus"] == "f38v.6" and row["head"] == "da")
    require((f38["values"], f38["series_surfaces_in_order"], f38["all_series_tokens_triple_stable"]) == ("II|III|IV", "daiin|daiiin|dain|dain", "1"), "f38 III-IV-II-II witness")

    editions = read_tsv(ART / "READING_VALUE_TOTALS.tsv")
    require(len(editions) == 12, "twelve alternate-reading totals")
    require(all(row["reading_role"] == "ALTERNATE_MANUSCRIPT_READING" for row in editions), "readings are not samples")
    edition_counts = {(row["reading"], row["working_roman"]): int(row["occurrences"]) for row in editions}
    require(edition_counts["ZL3b", "III"] == 3404 and edition_counts["IT2a", "III"] == 3382 and edition_counts["RF1b", "III"] == 3363, "alternate III totals")

    quality = read_tsv(ART / "QUALITY_VALUE_COMPOUNDS.tsv")
    require(len(quality) == 47, "47 quality-value compounds")
    require(len({row["surface"] for row in quality}) == 38, "38 quality-value surfaces")
    require(len({row["page"] for row in quality}) == 33, "33 quality-value pages")
    require(sum(int(row["triple_reading_token_stable"]) for row in quality) == 37, "37 stable quality-value compounds")
    quality_surface = Counter(row["surface"] for row in quality)
    require((quality_surface["qokchain"], quality_surface["qokchaiin"], quality_surface["qotchain"], quality_surface["qotchaiin"]) == (1, 2, 1, 1), "core quality-degree surface counts")
    require(next(row for row in quality if row["surface"] == "qokchain")["working_compound_de"] == "heiß-trocken, Grad II", "qokchain reading")
    require(next(row for row in quality if row["surface"] == "qotchaiin")["working_compound_de"] == "kalt-trocken, Grad III", "qotchaiin reading")
    matrix = read_tsv(ART / "QUALITY_VALUE_MATRIX.tsv")
    require(len(matrix) == 48 and sum(int(row["occurrences"]) for row in matrix) == 22, "complete 48-cell registered matrix with 22 direct occurrences")

    parts = read_tsv(ART / "PART_VALUE_COMPOUNDS.tsv")
    require(len(parts) == 28, "28 part-value compounds")
    require(Counter(row["part_root"] for row in parts) == Counter({"cth": 20, "chor": 7, "shor": 1}), "part-root counts")
    require(Counter(row["surface"] for row in parts)["cthaiin"] == 11, "eleven cthaiin occurrences")
    require(sum(row["section"] == "H" for row in parts) == 22, "22 Herbal part-value compounds")

    da = read_tsv(ART / "DA_VALUE_CONTEXTS.tsv")
    require(len(da) == 948, "948 da-family contexts")
    require(Counter(row["working_roman"] for row in da) == Counter({"I": 17, "II": 193, "III": 721, "IV": 17}), "da value distribution")
    require(len({row["page"] for row in da if row["surface"] == "daiin"}) == 169, "daiin on 169 pages")
    require(sum(int(row["triple_reading_token_stable"]) for row in da if row["surface"] == "daiin") == 602, "602 stable daiin occurrences")

    rivals = read_tsv(ART / "ROLE_RIVAL_RANKING.tsv")
    require(len(rivals) == 6 and rivals[0]["model"] == "FOUR_CELL_MINIM_VALUE_SUFFIX", "six ranked rivals led by value suffix")
    require(rivals[-1]["model"] == "OPERATION_VERB" and rivals[-1]["disposition"] == "DOWNGRADED", "operation verb downgraded")
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V3.tsv")
    require(len(dictionary) == 18, "eighteen dictionary entries")
    require(next(row for row in dictionary if row["entry"] == "daiin")["composition"] == "d+III", "dictionary resegments daiin")
    cases = read_tsv(ART / "CONCRETE_LOCAL_READINGS.tsv")
    require(len(cases) == 9, "nine concrete local readings")
    require(next(row for row in cases if row["case_id"] == "F18_CTH_III")["unit_or_binding"] == "MENGE_DOSIS_GRAD_ODER_KLASSE", "f18 cth unit remains open")
    require(next(row for row in cases if row["case_id"] == "F45_PART_DIII_PART")["working_reading_de"] == "Blüten-/Pflanzenteil; d-Wert III; Blattgut", "f45 non-generic reading")

    historical = read_tsv(ART / "HISTORICAL_NUMERAL_COMPARATORS.tsv")
    require(len(historical) == 9, "nine historical numeral comparators")
    require({"WELLCOME_MS542_QUALITY", "VAT_PAL_LAT_1234", "WELLCOME_MS492_NUMERALS", "MANCHESTER_ENGLISH_MS404", "EVA_DOCUMENTATION"} <= {row["source_id"] for row in historical}, "historical source identities")
    visual = read_tsv(ART / "MANUAL_VISUAL_JUDGMENTS.tsv")
    require(len(visual) == 5 and all(row["new_image_pages"] == "0" for row in visual), "five judgments and no new images")

    private_pattern = re.compile(
        "/" + "home/|/" + "tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
        "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
        "password\\s*[=:]|api[_-]?key\\s*[=:]|secret\\s*[=:]",
        re.IGNORECASE,
    )
    scan_paths = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json", BASE / "artifacts/README.md",
        ART / "HISTORICAL_NUMERAL_COMPARATORS.tsv", ART / "MANUAL_VISUAL_JUDGMENTS.tsv",
        *[ROOT / path for path in GENERATED_RELS],
    )
    for path in scan_paths:
        require(not private_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {path.relative_to(ROOT)}")

    payload = {
        "schema": "GDT626_VALIDATION_V1", "experiment_id": "GDT626", "status": "PASS",
        "checks": checks, "check_count": len(checks), "result_sha256": sha256(ROOT / RESULT_REL),
    }
    (ROOT / VALIDATION_REL).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
