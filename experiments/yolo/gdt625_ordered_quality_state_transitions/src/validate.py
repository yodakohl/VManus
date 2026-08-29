#!/usr/bin/env python3
"""Validate and byte-replay GDT625."""

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
BASE_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED_RELS = (
    BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    BASE_REL / "artifacts/TERMINAL_QUALITY_OCCURRENCES.tsv",
    BASE_REL / "artifacts/SUCCESSIVE_QUALITY_PAIRS.tsv",
    BASE_REL / "artifacts/SUCCESSIVE_TRANSITION_MATRIX.tsv",
    BASE_REL / "artifacts/MOISTURE_DIRECTION_SUMMARY.tsv",
    BASE_REL / "artifacts/THREE_STATE_CYCLES.tsv",
    BASE_REL / "artifacts/INTERVENING_TOKEN_CANDIDATES.tsv",
    BASE_REL / "artifacts/CANDIDATE_TERM_ROLE_SUMMARY.tsv",
    BASE_REL / "artifacts/CTH_ROOT_FAMILY.tsv",
    BASE_REL / "artifacts/CTHY_PART_CONTACTS.tsv",
    BASE_REL / "artifacts/ANCHOR_QUALITY_CONTACTS.tsv",
    BASE_REL / "artifacts/ANCHOR_QUALITY_SUMMARY.tsv",
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
    require("terminal=1162 pairs=535 moisture_flips=63 cycles=6 cthy=92/90H contacts=32" in completed.stdout, "builder summary")
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT625_ORDERED_QUALITY_STATE_TRANSITIONS_RESULT_V1", "result schema")
    require(result["status"] == "CTHY_BLATTGUT_PROMOTED__STATE_PATHS_SPLIT_PART_CONTRAST_FROM_PROCESS", "result status")
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "canonical result hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"]["safe_pages"] == 179, "179 safe pages")
    require(result["guard"]["safe_tokens"] == 32339, "32339 safe token rows")
    require(result["guard"]["token_query"] == {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}, "token guard counts")
    require(result["guard"]["cross_query"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}, "cross guard counts")
    require(result["guard"]["new_image_pages"] == 0, "no new image pages")
    require(result["quality_terminal_family"] == {
        "extended_prefix_occurrences": 333, "loci": 912, "occurrences": 1162,
        "pages": 168, "registered_grid_occurrences": 829,
        "triple_stable_occurrences": 859, "types": 200,
    }, "terminal family summary")
    require(result["successive_local_pairs"] == {
        "local_exact_frame_dry_to_moist": 7, "local_exact_frame_moist_to_dry": 1,
        "moisture_flips": 63, "next_line": 285, "pairs": 535, "same_line": 250,
        "same_line_dry_to_moist": 17, "same_line_moist_to_dry": 17,
    }, "successive pair summary")
    require(result["three_state_cycles"] == {
        "cycles": 6, "f29v_cycle": "G625-C005", "opened_image_cycles": 1,
        "path_counts": {"KCH->KSH->KCH": 2, "TCH->TSH->TCH": 4},
    }, "cycle summary")
    require(result["cth_role"] == {
        "cthy_adjacent_part_contacts": 10, "cthy_dry_contacts": 11,
        "cthy_herbal_occurrences": 90, "cthy_immediate_quality_contacts": 12,
        "cthy_moist_contacts": 1, "cthy_occurrences": 92, "cthy_part_contacts": 32,
        "cthy_stable_occurrences": 85, "cthy_stable_quality_contacts": 8,
        "family_occurrences": 408, "family_types": 69,
        "working_default": "cth=vegetativer Pflanzenteil; cthy=Blattgut/Blattdroge",
    }, "cth role summary")
    require(result["manual_sources"] == {"concrete_readings": 5, "historical_process_comparators": 9, "visual_judgments": 8}, "manual source totals")
    require("Blattgut" in result["working_lexicon_updates"]["cthy"], "cthy receives Blattgut default")
    require("nur bei gleichem Träger" in result["working_lexicon_updates"]["MOIST_TO_DRY"], "drying is relation conditional")
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

    occurrences = read_tsv(ART / "TERMINAL_QUALITY_OCCURRENCES.tsv")
    require(len(occurrences) == 1162, "1162 terminal occurrences")
    require(len({row["surface"] for row in occurrences}) == 200, "200 terminal surfaces")
    require(len({row["page"] for row in occurrences}) == 168, "168 terminal pages")
    require(len({row["locus"] for row in occurrences}) == 912, "912 terminal loci")
    require(sum(int(row["registered_grid"]) for row in occurrences) == 829, "829 registered-grid occurrences")
    require(sum(int(row["triple_reading_token_stable"]) for row in occurrences) == 859, "859 stable terminal occurrences")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences), "terminal occurrences exclude forbidden pages")

    pairs = read_tsv(ART / "SUCCESSIVE_QUALITY_PAIRS.tsv")
    require(len(pairs) == 535, "535 successive local pairs")
    require(Counter(row["line_delta"] for row in pairs) == Counter({"0": 250, "1": 285}), "pair locality counts")
    require(sum(row["axis_relation"] == "MOISTURE_FLIP" for row in pairs) == 63, "63 moisture flips")
    require(sum(row["direction"] == "DRY_TO_MOIST" and row["line_delta"] == "0" for row in pairs) == 17, "17 same-line dry-to-moist")
    require(sum(row["direction"] == "MOIST_TO_DRY" and row["line_delta"] == "0" for row in pairs) == 17, "17 same-line moist-to-dry")

    matrix = read_tsv(ART / "SUCCESSIVE_TRANSITION_MATRIX.tsv")
    require(len(matrix) == 144, "144 complete transition-matrix cells")
    directions = read_tsv(ART / "MOISTURE_DIRECTION_SUMMARY.tsv")
    require(len(directions) == 18, "eighteen direction summaries")
    direction_lookup = {(row["locality"], row["frame_scope"], row["direction"]): int(row["pairs"]) for row in directions}
    require(direction_lookup["SAME_LINE", "EXACT_FRAME", "DRY_TO_MOIST"] == 5, "five same-line exact dry-to-moist pairs")
    require(direction_lookup["SAME_LINE", "EXACT_FRAME", "MOIST_TO_DRY"] == 0, "zero successive same-line exact moist-to-dry pairs")

    cycles = read_tsv(ART / "THREE_STATE_CYCLES.tsv")
    require(len(cycles) == 6, "six three-state cycles")
    require(Counter(row["state_path"] for row in cycles) == Counter({"TCH->TSH->TCH": 4, "KCH->KSH->KCH": 2}), "all cycles dry-moist-dry")
    require(sum(int(row["opened_image_page"]) for row in cycles) == 1, "one opened-image cycle")

    bridges = read_tsv(ART / "INTERVENING_TOKEN_CANDIDATES.tsv")
    require(len(bridges) == 59, "fifty-nine bridge surfaces")
    bridge_lookup = {row["surface"]: row for row in bridges}
    require((bridge_lookup["cthy"]["moist_to_dry_bridges"], bridge_lookup["cthy"]["dry_to_moist_bridges"]) == ("2", "0"), "cthy bridge direction counts")
    require("NOT_DRYING_VERB" in bridge_lookup["cthy"]["working_role"], "cthy rejected as drying verb")
    require((bridge_lookup["otar"]["moist_to_dry_bridges"], bridge_lookup["otar"]["dry_to_moist_bridges"]) == ("2", "0"), "otar bridge direction counts")

    terms = read_tsv(ART / "CANDIDATE_TERM_ROLE_SUMMARY.tsv")
    require(len(terms) == 7, "seven candidate term summaries")
    term_lookup = {row["surface"]: row for row in terms}
    require((term_lookup["cthy"]["zl3b_occurrences"], term_lookup["cthy"]["herbal_occurrences"], term_lookup["cthy"]["triple_stable_occurrences"]) == ("92", "90", "85"), "cthy counts")
    require(term_lookup["cthy"]["line_first"] == "0", "cthy never line-first")
    require(term_lookup["cthy"]["working_default_de"] == "Blattgut/Blattdroge (folium)", "cthy exact working default")

    family = read_tsv(ART / "CTH_ROOT_FAMILY.tsv")
    require(len(family) == 69, "sixty-nine cth family surfaces")
    require(sum(int(row["occurrences"]) for row in family) == 408, "408 cth family occurrences")
    require(next(row for row in family if row["surface"] == "cthy")["status"] == "PRIMARY_CTHY_FORM", "cthy is primary family form")
    contacts = read_tsv(ART / "CTHY_PART_CONTACTS.tsv")
    require(len(contacts) == 32, "thirty-two cthy part contacts")
    require(sum(int(row["adjacent"]) for row in contacts) == 10, "ten adjacent cthy part contacts")

    quality_contacts = read_tsv(ART / "ANCHOR_QUALITY_CONTACTS.tsv")
    require(len(quality_contacts) == 37, "thirty-seven strict anchor-quality contacts")
    quality_summary = read_tsv(ART / "ANCHOR_QUALITY_SUMMARY.tsv")
    require(len(quality_summary) == 10, "ten anchor-quality summaries")
    cthy_quality = next(row for row in quality_summary if row["anchor_surface"] == "cthy")
    require(tuple(cthy_quality[key] for key in ("immediate_quality_contacts", "stable_immediate_quality_contacts", "dry_ch_contacts", "moist_sh_contacts")) == ("12", "8", "11", "1"), "cthy strict quality contacts")

    cases = read_tsv(ART / "CONCRETE_LOCAL_READINGS.tsv")
    require(len(cases) == 5, "five concrete local readings")
    f29 = next(row for row in cases if row["case_id"] == "F29_TWO_PART_BINDINGS")
    require(f29["local_parse"] == "[otshy okaiin] [cthy oltchy]", "f29 corrected local parse")
    require("PART_CONTRAST_PRIMARY" in f29["operation_status"], "f29 part contrast outranks process")
    require("Blattgut" in f29["working_reading_de"], "f29 concrete Blattgut reading")

    historical = read_tsv(ART / "HISTORICAL_PROCESS_COMPARATORS.tsv")
    require(len(historical) == 9, "nine historical process comparators")
    require({"W541_MIXED_CODEBOOK", "W542_HEAT", "LCC_WET_DRY", "MANCHESTER404", "DURHAM_BIII12"} <= {row["source_id"] for row in historical}, "historical source identities")
    visual = read_tsv(ART / "MANUAL_VISUAL_JUDGMENTS.tsv")
    require(len(visual) == 8, "eight manual visual judgments")
    require(all(row["new_image_pages"] == "0" for row in visual), "manual pass opened no new image page")

    private_pattern = re.compile(
        "/" + "home/|/" + "tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
        "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
        "password\\s*[=:]|api[_-]?key\\s*[=:]|secret\\s*[=:]",
        re.IGNORECASE,
    )
    scan_paths = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json", BASE / "artifacts/README.md",
        ART / "HISTORICAL_PROCESS_COMPARATORS.tsv", ART / "MANUAL_VISUAL_JUDGMENTS.tsv",
        *[ROOT / path for path in GENERATED_RELS],
    )
    for path in scan_paths:
        require(not private_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {path.relative_to(ROOT)}")

    payload = {
        "schema": "GDT625_VALIDATION_V1", "experiment_id": "GDT625", "status": "PASS",
        "checks": checks, "check_count": len(checks), "result_sha256": sha256(ROOT / RESULT_REL),
    }
    (ROOT / VALIDATION_REL).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
