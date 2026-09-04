#!/usr/bin/env python3
"""Validate GDT790 and replay every generated artifact byte-for-byte."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay"
SRC = BASE / "src"
ART = BASE / "artifacts"
sys.path.insert(0, str(SRC))
import run  # noqa: E402


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.messages: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)
        self.messages.append(message)


def main() -> int:
    audit = Audit()

    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    audit.check(len(locks) == 19, "19 source locks")
    for row in locks:
        relative = Path(row["path"])
        audit.check(not relative.is_absolute() and ".." not in relative.parts, f"safe source path {row['path']}")
        path = ROOT / relative
        audit.check(path.is_file(), f"source exists {row['path']}")
        audit.check(sha256(path) == row["sha256"], f"source hash {row['path']}")

    source_lines, guard = run.query_lines()
    audit.check(len(source_lines) == 150, "guarded source has 150 lines")
    audit.check(guard == {"selected": 150, "skipped_forbidden": 98, "skipped_not_allowed": 5137}, "guard statistics fixed")
    audit.check({row["page"] for row in source_lines} == set(run.PAGES), "only three allowed pages materialized")
    audit.check(not any(row["page"].startswith("f84") for row in source_lines), "no f84 or f84r row materialized")

    records = read_tsv(ART / run.OUTPUT_NAMES[0])
    panels = read_tsv(ART / run.OUTPUT_NAMES[1])
    labels = read_tsv(ART / run.OUTPUT_NAMES[2])
    label_tokens = read_tsv(ART / run.OUTPUT_NAMES[3])
    bridges = read_tsv(ART / run.OUTPUT_NAMES[4])
    families = read_tsv(ART / run.OUTPUT_NAMES[5])
    rendered = read_tsv(ART / run.OUTPUT_NAMES[6])
    compatibility = read_tsv(ART / run.OUTPUT_NAMES[7])
    images = read_tsv(ART / run.OUTPUT_NAMES[8])
    source_stats = read_tsv(ART / run.OUTPUT_NAMES[9])
    result = json.loads((ART / run.OUTPUT_NAMES[12]).read_text(encoding="utf-8"))

    audit.check(len(records) == 13, "13 paragraph records")
    audit.check(len({row["record_id"] for row in records}) == 13, "record IDs unique")
    audit.check(len(panels) == 10, "10 image panels")
    audit.check(len({row["panel_id"] for row in panels}) == 10, "panel IDs unique")
    audit.check(sum(int(row["prose_line_count"]) for row in records) == 123, "record line total 123")
    audit.check(sum(int(row["prose_token_count"]) for row in records) == 940, "record token total 940")
    audit.check(sum(int(row["record_count"]) for row in panels) == 13, "panel record total 13")
    audit.check(sum(int(row["prose_line_count"]) for row in panels) == 123, "panel line total 123")
    audit.check(sum(int(row["prose_token_count"]) for row in panels) == 940, "panel token total 940")
    audit.check(all(row["semantic_ceiling"] == "EXTERNAL_TOPIC_NOT_WORD_MEANING" for row in records), "record owners remain external topics")
    audit.check(all(row["text_cells_modified"] == "0" for row in records), "record bindings modify zero text cells")
    audit.check({row["record_kind"] for row in records} == {"MAIN_RECORD", "EMBEDDED_RECORD"}, "main and embedded records explicit")
    audit.check(sum(row["record_kind"] == "EMBEDDED_RECORD" for row in records) == 2, "two f83 embedded records")
    audit.check({row["record_id"] for row in records if row["record_kind"] == "EMBEDDED_RECORD"} == {"F83_Q1", "F83_Q2"}, "embedded records are Q1 and Q2")

    panel_counts = {row["panel_id"]: (int(row["label_locus_count"]), int(row["prose_token_count"])) for row in panels}
    audit.check(panel_counts["F77_TOP_ARCH"] == (8, 142), "f77 upper arch density")
    audit.check(panel_counts["F77_MIDDLE_BODY"] == (1, 92), "f77 middle density")
    audit.check(panel_counts["F77_LOWER_VESSEL"] == (1, 87), "f77 lower density")
    audit.check(panel_counts["F82_BOTTOM_COMMUNAL"] == (12, 126), "f82 bottom density")
    audit.check(panel_counts["F83_LOWER_COUPLED"] == (4, 122), "f83 lower coupled density")

    audit.check(len(labels) == 27, "27 graphical label loci")
    audit.check(len({row["locus"] for row in labels}) == 27, "label loci unique")
    audit.check(len(label_tokens) == 28, "28 label tokens")
    audit.check(len({row["label_token_id"] for row in label_tokens}) == 28, "label token IDs unique")
    audit.check(sum(int(row["label_token_count"]) for row in labels) == 28, "label atlas token total")
    audit.check(all(row["working_local_default_de"] for row in labels), "every label has a local owner default")
    audit.check(all(row["word_meaning_selected"] == "NO" for row in labels), "no label word meaning selected")
    audit.check(all(row["prefix_or_root_export"] == "NO" for row in labels), "no label prefix or root export")
    audit.check(sum(row["anchor_eligible"] == "YES" for row in label_tokens) == 27, "27 multi-character label tokens")
    audit.check(sum(row["anchor_eligible"] != "YES" for row in label_tokens) == 1, "one single-character nonanchor token")

    audit.check(len(bridges) == 10, "10 exact label-to-prose occurrence edges")
    audit.check(len({row["bridge_id"] for row in bridges}) == 10, "bridge IDs unique")
    audit.check(sum(len(row["label_token"]) > 1 for row in bridges) == 9, "nine multi-character edges")
    audit.check(sum(row["same_page"] == "YES" and len(row["label_token"]) > 1 for row in bridges) == 3, "three same-page multi-character edges")
    audit.check(sum(row["same_page"] == "NO" and len(row["label_token"]) > 1 for row in bridges) == 6, "six cross-page multi-character edges")
    audit.check(sum(row["anchor_status"] == "EXACT_SINGLE_CHARACTER_NONANCHOR" for row in bridges) == 1, "single o edge excluded")
    audit.check({row["label_token"] for row in bridges if len(row["label_token"]) > 1} == {"otedy", "otchdy", "okal", "olaiin"}, "four bridged multi-character label forms")
    expected_edges = {
        ("f77r.3", "otedy", "f77r.25", "F77_P2"),
        ("f77r.3", "otedy", "f82r.12", "F82_P2"),
        ("f77r.3", "otedy", "f83r.8", "F83_P1"),
        ("f77r.3", "otedy", "f83r.21", "F83_P3"),
        ("f77r.3", "otedy", "f83r.22", "F83_P3"),
        ("f77r.49", "otchdy", "f83r.47", "F83_Q1"),
        ("f77r.50", "o", "f83r.7", "F83_P1"),
        ("f82r.36", "okal", "f82r.6", "F82_P1"),
        ("f82r.36", "okal", "f82r.12", "F82_P2"),
        ("f82r.44", "olaiin", "f77r.39", "F77_P3"),
    }
    audit.check({(row["label_locus"], row["label_token"], row["prose_locus"], row["prose_record_id"]) for row in bridges} == expected_edges, "exact bridge deck fixed")
    source_by_locus = {row["locus"]: row for row in source_lines}
    for row in bridges:
        tokens = source_by_locus[row["prose_locus"]]["eva_clean"].split()
        ordinals = [int(value) for value in row["prose_token_ordinals"].split("|")]
        audit.check(all(tokens[ordinal - 1] == row["label_token"] for ordinal in ordinals), f"bridge source exact {row['bridge_id']}")
        audit.check(row["semantic_credit"] == "ZERO__STRING_REUSE_ONLY", f"bridge semantic ceiling {row['bridge_id']}")

    audit.check(len(families) == 5, "five image-conditioned form families")
    audit.check({row["family_id"] for row in families} == {"EDY_BOGENSTELLEN", "CHDY_ANSCHLUSS", "OKAL_BECKENSTELLEN", "DAROL_ZU_AUSLASS", "OL_AIIN_STATIONEN"}, "family IDs fixed")
    audit.check(next(row for row in families if row["family_id"] == "DAROL_ZU_AUSLASS")["status"] == "STRONGEST_IMAGE_CONDITIONED_FAMILY_LEAD", "darol family is strongest visual lead")
    audit.check(all(row["free_component_export"] == "NO" and row["unseen_form_prediction"] == "NO" for row in families), "families export no component or unseen prediction")
    audit.check(all(row["renderer_license"] == "EXACT_OCCURRENCE_ONLY" for row in families), "family renderer licence is occurrence-only")

    audit.check(len(rendered) == 123, "123 image-aware rendered lines")
    audit.check(len({row["locus"] for row in rendered}) == 123, "rendered loci unique")
    prose_sources = {row["locus"]: row for row in source_lines if row["locus"] not in {label["locus"] for label in labels}}
    audit.check(set(prose_sources) == {row["locus"] for row in rendered}, "renderer covers every prose locus")
    for row in rendered:
        audit.check(row["zl3b_line"] == prose_sources[row["locus"]]["eva_clean"], f"exact token line retained {row['locus']}")
        audit.check(row["token_count"] == prose_sources[row["locus"]]["token_count"], f"token count retained {row['locus']}")
        audit.check(row["owner_display_de"] in row["image_aware_render_de"], f"owner visible {row['locus']}")
        audit.check(row["token_semantics_changed"] == "0", f"zero token semantics changed {row['locus']}")
        audit.check(row["word_to_single_figure_by_proximity"] == "0", f"no proximity word owner {row['locus']}")

    rendered_by_locus = {row["locus"]: row for row in rendered}
    audit.check("BILDVERWEIS otedy → INNER_PORT_2" in rendered_by_locus["f77r.25"]["structural_cells_de"], "f77 P2 opener points to exact upper label")
    audit.check("BILDVERWEIS okal → TOP_FIGURE_2" in rendered_by_locus["f82r.6"]["structural_cells_de"], "f82 P1 exact forward label reference")
    audit.check("BILDVERWEIS okal → TOP_FIGURE_2" in rendered_by_locus["f82r.12"]["structural_cells_de"], "f82 P2 exact forward label reference")
    audit.check("LABELFORM otchdy" in rendered_by_locus["f83r.47"]["structural_cells_de"], "f83 embedded record cross-page label form")
    audit.check("qokeol → WERT-III-KANDIDAT daiin" in rendered_by_locus["f82r.1"]["structural_cells_de"], "first bounded value field retained")
    audit.check("cheey → WERT-III-KANDIDAT daiin" in rendered_by_locus["f82r.1"]["structural_cells_de"], "second bounded value field retained")
    forbidden_renderer = re.compile(r"(?i)arbeitsgut|arbeitsmaterial|arbeitsschritt|werkstück|drogenstoff|pulverpräparat|nimm das|führe .* aus|leite weiter")
    audit.check(not any(forbidden_renderer.search(row["image_aware_render_de"]) for row in rendered), "generic and obsolete fluent prose absent")

    audit.check(len(compatibility) == 11, "11 compatibility rows")
    audit.check(all(row["status"] in {"PRESERVED_CONSTRAINT", "PRESERVED_AS_LOCAL_LEAD", "PRESERVED_AND_USED", "EXTENDED", "PRESERVED_LAYER", "RETIRED_RENDER_PATH"} for row in compatibility), "compatibility statuses controlled")
    audit.check(len(images) == 3 and {row["page"] for row in images} == set(run.PAGES), "three official image source cards")
    expected_image_hashes = {
        "f77r": "6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df",
        "f82r": "e9f9a8f97346ebf24b57b3425e038ed2ca1d4f2692f94e52535b5208b8f100c2",
        "f83r": "b1bfd576a701497126d444e48801a86da610073c9d66c0b232aa1724d4fb2b77",
    }
    audit.check({row["page"]: row["review_sha256"] for row in images} == expected_image_hashes, "reviewed image hashes fixed")
    audit.check(all(row["image_url"].startswith("https://collections.library.yale.edu/iiif/2/") for row in images), "official Yale IIIF URLs")
    audit.check(len(source_stats) == 1 and source_stats[0]["selected"] == "150", "guarded source stats artifact")
    audit.check(source_stats[0]["f84_materialized"] == source_stats[0]["f84r_materialized"] == "0", "source stats seal f84 and f84r")

    audit.check(result["experiment_id"] == "GDT790" and result["status"] == run.STATUS, "result identity and status")
    audit.check(result["scope"]["image_panels"] == 10 and result["scope"]["records"] == 13, "result panel and record counts")
    audit.check(result["scope"]["prose_lines"] == 123 and result["scope"]["prose_tokens"] == 940, "result prose counts")
    audit.check(result["scope"]["label_loci"] == 27 and result["scope"]["label_tokens"] == 28, "result label counts")
    audit.check(not result["scope"]["f84_used"] and not result["scope"]["f84r_used"], "result records no sealed use")
    audit.check(result["overlay"]["token_meaning_changes"] == result["overlay"]["prefix_or_root_exports"] == 0, "result keeps lexical layer unchanged")
    audit.check(result["decision"]["selected"] == "PANEL_OWNER_OVERLAY_WITH_EXACT_LOCAL_LABEL_REFERENCES", "result selects overlay")
    audit.check("ten image topology classes" in result["decision"]["next"], "result routes topology comparison")

    reader = (ART / run.OUTPUT_NAMES[10]).read_text(encoding="utf-8")
    manual = (ART / run.OUTPUT_NAMES[11]).read_text(encoding="utf-8")
    audit.check(reader.count("\n### f") == 123, "reader contains all 123 prose lines")
    audit.check(reader.count("\n## f") == 13, "reader contains all 13 records")
    audit.check("PAGE → IMAGE PANEL" in manual and "darol/darolsy" in manual, "manual audit states hierarchy and strongest family")
    audit.check("generic action prose is not reused" in manual, "manual audit retires generic prose")

    report = (BASE / "REPORT.md").read_text(encoding="utf-8") if (BASE / "REPORT.md").is_file() else ""
    audit.check("PANEL_OWNER" in report and "otedy" in report and "darol/darolsy" in report, "report states selected model and concrete bridges")
    audit.check("does not translate" in report.lower() or "not a translation" in report.lower(), "report states translation ceiling")

    privacy_patterns = (
        re.compile(r"/" + r"home/[^/\s]+/"),
        re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
        re.compile(r"(?i)(?:password|passwd|api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[^\s$<{][^\s]*"),
    )
    public_files = [
        path for path in BASE.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path != SRC / "validate.py"
    ]
    for path in public_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        audit.check(not any(pattern.search(text) for pattern in privacy_patterns), f"privacy markers absent {path.relative_to(BASE)}")

    with tempfile.TemporaryDirectory(prefix="gdt790-replay-") as temp:
        replay_dir = Path(temp)
        replay_result = run.build(replay_dir)
        audit.check(replay_result == result, "runner result replay")
        for name in run.OUTPUT_NAMES:
            audit.check((replay_dir / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT790_VALIDATION_V1",
        "experiment_id": "GDT790",
        "status": "PASS",
        "checks": audit.checks,
        "messages": audit.messages,
        "runner_outputs_replayed": len(run.OUTPUT_NAMES),
        "source_locks": len(locks),
        "sealed_pages_accessed": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
