#!/usr/bin/env python3
"""Validate GDT760 artifacts and a byte-identical builder replay."""

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
BASE_REL = Path("experiments/yolo/gdt760_quantity_bilateral_content_attachment")
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


builder = load_module("gdt760_builder_for_validation", RUN)


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
    expressions = read_tsv(ART / "QUANTITY_281_EXPRESSION_ATLAS.tsv")
    bilateral = read_tsv(ART / "BILATERAL_POSITION_ROLE_SUMMARY.tsv")
    attachments = read_tsv(ART / "CONTENT_45_ATTACHMENT_ATLAS.tsv")
    phrases = read_tsv(ART / "CONTENT_44_AMOUNT_PHRASE_READER.tsv")
    candidates = read_tsv(ART / "CONTENT_ANCHOR_35_CANDIDATE_DECK.tsv")
    forms = read_tsv(ART / "AMOUNT_FORM_17_POSITION_CENSUS.tsv")
    fused_s = read_tsv(ART / "FUSED_S_145_CONTEXT_REVISION.tsv")
    transitions = read_tsv(ART / "LINE_INITIAL_S_15_SEQUENCE_TRANSITIONS.tsv")
    contrasts = read_tsv(ART / "STATE_CONTRAST_AMOUNT_FAMILIES.tsv")
    identities = read_tsv(ART / "TARGET_IDENTITY_COMPETITION.tsv")

    require(result["schema"] == "GDT760_RESULT_V1", "result schema")
    require(result["status"] == builder.STATUS, "result status")
    require(len(expressions) == 281, "281 amount expressions")
    require(len(bilateral) == 9, "nine bilateral summaries")
    require(len(attachments) == 45, "45 clean content attachments")
    require(len(phrases) == 44, "44 content-bearing expression loci")
    require(len(candidates) == 35, "35 exact content surfaces")
    require(len(forms) == 17, "seventeen observed amount forms")
    require(len(fused_s) == 145, "145 fused s occurrences")
    require(len(transitions) == 15, "fifteen initial-s transitions")
    require(len(contrasts) == 2, "two dry/moist whole contrasts")
    require(len(identities) == 8, "eight requested identity competitors")

    require(len({row["expression_id"] for row in expressions}) == 281, "unique expression ids")
    require(len({row["attachment_id"] for row in attachments}) == 45, "unique attachment ids")
    require(len({row["phrase_id"] for row in phrases}) == 44, "unique phrase ids")
    require(Counter(row["mode"] for row in expressions) == Counter({
        "FUSED": 185, "SEPARATED": 96,
    }), "fused and separated expression counts")
    require(Counter(row["expression_line_position"] for row in expressions) == Counter({
        "FIRST": 87, "MIDDLE": 169, "LAST": 25,
    }), "expression position counts")
    require(Counter(row["left_axis_class"] for row in expressions) == Counter({
        "EDGE_OR_NONEXACT": 118, "OPEN": 130, "CONTENT_PREP": 20,
        "QUALITY_VALUE": 10, "AMOUNT_PART": 3,
    }), "left axis classes")
    require(Counter(row["right_axis_class"] for row in expressions) == Counter({
        "EDGE_OR_NONEXACT": 77, "OPEN": 162, "CONTENT_PREP": 25,
        "QUALITY_VALUE": 12, "AMOUNT_PART": 3, "PROCESS_CLOSE": 2,
    }), "right axis classes")

    all_row = next(row for row in bilateral if row["dimension"] == "ALL")
    first = next(row for row in bilateral if row["dimension"] == "POSITION" and row["level"] == "FIRST")
    middle = next(row for row in bilateral if row["dimension"] == "POSITION" and row["level"] == "MIDDLE")
    final = next(row for row in bilateral if row["dimension"] == "POSITION" and row["level"] == "LAST")
    require(all_row["left_content_rate"] == "0.122699", "global left rate")
    require(all_row["right_content_rate"] == "0.122549", "global right rate")
    require(all_row["decision"].startswith("NO_GLOBAL_DIRECTION"), "no universal direction")
    require(first["right_content_preparation_neighbors"] == "14", "first-right content hits")
    require(first["right_eligible_exact_neighbors"] == "72", "first-right eligible")
    require(middle["left_content_preparation_neighbors"] == "19", "middle-left content hits")
    require(middle["right_content_preparation_neighbors"] == "11", "middle-right content hits")
    require(final["left_content_preparation_neighbors"] == "1", "last-left content hits")

    surface_counts = Counter(row["content_surface"] for row in attachments)
    require(surface_counts["cheor"] == 3, "three cheor amount attachments")
    require(surface_counts["sheor"] == 3, "three sheor amount attachments")
    require(surface_counts["cheo"] == 2, "two cheo amount attachments")
    require(surface_counts["sheo"] == 1, "one sheo amount attachment")
    require(surface_counts["cthy"] == 1, "one cthy amount attachment")
    require(next(row for row in candidates if row["content_surface"] == "cthy")["current_working_whole_candidate_de"] == "Blattgut", "cthy leaf candidate retained")
    require(next(row for row in candidates if row["content_surface"] == "cheor")["global_reader_exact_occurrences"] == "56", "cheor global recurrence")
    require(next(row for row in candidates if row["content_surface"] == "sheor")["global_reader_exact_occurrences"] == "31", "sheor global recurrence")

    part_contrast = next(row for row in contrasts if row["contrast_id"] == "G760-C01")
    prep_contrast = next(row for row in contrasts if row["contrast_id"] == "G760-C02")
    require(part_contrast["dry_amount_attachments"] == "3", "dry-part attachments")
    require(part_contrast["moist_amount_attachments"] == "3", "moist-part attachments")
    require(part_contrast["observed_exact_amount_phrases"] == "6", "six part contrast phrases")
    require(prep_contrast["observed_exact_amount_phrases"] == "3", "three preparation contrast phrases")
    require(all(row["component_contrast_export_allowed"] == "0" for row in contrasts), "no contrast component export")

    identity_by_name = {row["target_identity_de"]: row for row in identities}
    require(identity_by_name["Wasser"]["current_amount_attachment_hits"] == "6", "six moist-family water rival contacts")
    require(identity_by_name["Wein"]["current_amount_attachment_hits"] == "6", "six moist-family wine rival contacts")
    require(identity_by_name["Öl"]["current_amount_attachment_hits"] == "0", "zero oil current contacts")
    require(identity_by_name["Salz"]["current_amount_attachment_hits"] == "0", "zero salt current contacts")
    require(identity_by_name["Pulver"]["current_amount_attachment_hits"] == "6", "six dry-class powder rival contacts")
    require(identity_by_name["Blatt"]["specific_identity_selected"] == "1", "leaf remains exploratory lead")
    require(sum(int(row["specific_identity_selected"]) for row in identities) == 1, "one specific exploratory identity lead")
    require(all(row["confirmed_lexeme"] == "0" for row in identities), "identity leads are not confirmed lexemes")

    require(Counter(row["transition_direction"] for row in transitions) == Counter({
        "EQUAL": 10, "DECREASE": 2, "INCREASE": 3,
    }), "initial s transition directions")
    require(len({row["paragraph_id"] for row in transitions}) == 11, "eleven multi-s paragraphs")
    require(all(row["simple_entry_ordinal_default_supported"] == "0" for row in transitions), "simple ordinal default rejected")
    require(sum(int(row["exact_content_phrase_license"]) for row in fused_s) == 22, "22 fused-s content phrase licenses")
    require(sum(row["line_position"] == "FIRST" for row in fused_s) == 76, "76 line-first fused s")
    require(all(row["working_drachm_candidate_retained"] == "1" for row in fused_s), "drachm candidate retained")
    require(all(row["unconditional_global_spoken_drachm_overlay_allowed"] == "0" for row in fused_s), "global fused overlay removed")
    require(all(row["old_seed_reading_quarantined"] == "1" for row in fused_s), "old seed readings stay quarantined")

    separated_s = [row for row in forms if row["mode"] == "SEPARATED" and row["head_surface"] == "s"]
    fused_s_forms = [row for row in forms if row["mode"] == "FUSED" and row["head_surface"] == "s"]
    require(sum(int(row["occurrences"]) for row in separated_s) == 25, "25 separated s expressions")
    require(sum(int(row["line_first"]) for row in separated_s) == 0, "zero line-first separated s")
    require(sum(int(row["occurrences"]) for row in fused_s_forms) == 145, "145 fused s forms")
    require(sum(int(row["line_first"]) for row in fused_s_forms) == 76, "76 line-first fused s forms")

    forbidden_filler = ("Arbeitsgut", "Arbeitschritt", "Arbeitsmaterial")
    for row in expressions:
        require(not row["page"].startswith("f84"), f"sealed page absent {row['expression_id']}")
        require(row["component_export_credit"] == "0", f"zero component credit {row['expression_id']}")
        require(row["confirmed_plaintext"] == "0", f"zero plaintext {row['expression_id']}")
        require(not any(term in row["gdt760_render_de"] for term in forbidden_filler), f"no generic filler {row['expression_id']}")
        require("Samencharge" not in row["gdt760_render_de"], f"no seed charge {row['expression_id']}")
    for row in attachments:
        require(row["scope"] == "THIS_EXACT_AMOUNT_CONTENT_CONTACT_ONLY", f"attachment scope {row['attachment_id']}")
        require(row["literal_identity_confirmed"] == "0", f"attachment identity open {row['attachment_id']}")
        require(not row["page"].startswith("f84"), f"sealed attachment page absent {row['attachment_id']}")
    for row in phrases:
        require(row["candidate_not_plaintext"] == "1", f"phrase is candidate {row['phrase_id']}")
        require(not any(term in row["working_phrase_de"] for term in forbidden_filler), f"phrase no filler {row['phrase_id']}")

    require(result["scope"]["amount_expressions"] == 281, "result expression count")
    require(result["scope"]["cached_pages_in_guarded_context"] == 98, "98 expression-bearing cached pages")
    require(result["fused_s_correction"]["simple_entry_ordinal_default"] == "REJECTED", "result ordinal correction")
    require(result["fused_s_correction"]["drachm_candidate"] == "RETAINED_AS_CONTEXTUAL_LEAD", "result drachm retention")
    require(result["claim_boundary"]["confirmed_lexemes"] == 0, "zero confirmed lexemes")
    require(result["claim_boundary"]["confirmed_units"] == 0, "zero confirmed units")
    require(result["claim_boundary"]["new_pages"] == 0, "zero new pages")
    require(result["claim_boundary"]["f84_accessed"] is False, "f84 forbidden")
    require(result["claim_boundary"]["f84r_accessed"] is False, "f84r forbidden")

    with tempfile.TemporaryDirectory(prefix="gdt760_replay_") as temp:
        replay_dir = Path(temp)
        replay_result = builder.build(replay_dir)
        require(replay_result == result, "replayed result object")
        for name in builder.OUTPUT_NAMES:
            require((replay_dir / name).is_file(), f"replay output exists {name}")
            require(digest(replay_dir / name) == digest(ART / name), f"byte replay {name}")

    validation = {
        "schema": "GDT760_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "byte_identical_replay": True,
        "scope": result["scope"],
        "bilateral_result": result["bilateral_result"],
        "content_result": result["content_result"],
        "fused_s_correction": result["fused_s_correction"],
        "claim_ceiling": (
            "Forty-four exact amount/content positions receive concrete replaceable "
            "candidate phrases; the dry/moist whole contrasts and position-conditioned "
            "attachment rule identify no confirmed lexeme, unit, liquid or plaintext."
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
