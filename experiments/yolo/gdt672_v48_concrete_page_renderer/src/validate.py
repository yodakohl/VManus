#!/usr/bin/env python3
"""Independent validator for GDT672."""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt672_v48_concrete_page_renderer")
BASE = ROOT / BASE_REL
SRC = BASE / "src"
ART = BASE / "artifacts"
V48 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G589 = ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
EXPECTED_STATUS = "PASS_F1R_214_POSITION_CONCRETE_TRANSFER__129_V48_EXACT__85_EXPLICIT_TRANSFER"
OUTPUT_NAMES = (
    "F1R_SOURCE_ALIGNMENT.tsv", "F1R_TOKEN_READINGS.tsv", "F1R_COMPONENT_TRACES.tsv",
    "F1R_COMPOSITION_RIVALS.tsv", "F1R_CLAUSE_FRAMES.tsv", "F1R_LINE_READER.tsv",
    "F1R_GDT589_COMPARISON.tsv", "F1R_TRANSFER_CARDS.tsv", "F1R_OCCURRENCE_AUDIT.tsv",
    "F1R_VALUE_ATTACHMENT_AUDIT.tsv",
    "RENDERER_RULE_CARDS.tsv", "REGISTER_DIVERSE_RENDER_AUDIT.tsv",
    "GDT672_F1R_CONCRETE_WORKING_READER.md", "RESULT.json",
)

GENERIC_FILLER = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|work item|working material|worksite|"
    r"work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)
ACTION_RE = re.compile(
    r"\b(?:abmessen|abteilen|abkühlen|abschließen|ansetzen|einweichen|erhitzen|"
    r"erwärmen|fertigstellen|filtrieren|hinzugeben|kühlen|mahlen|nehmen|reiben|"
    r"schließen|seihen|trocknen|waschen|zugeben|zerstoßen|kühle|trockne|erhitze|"
    r"weiche|nimm|gib|führe|seihe|schließe|miss)\b",
    re.IGNORECASE,
)
QUANTITY_RE = re.compile(
    r"\b(?:zwei|drei|vier|Teil(?:e)?|Maß(?:e)?|Dosis|Dosen|Portion|Menge|"
    r"Fraktion|Pfund|Handvoll|Gran)\b",
    re.IGNORECASE,
)
STAGE_RE = re.compile(r"\b(?:Grad\w*|Stufe\w*|Mittelstufe|Endstufe|Gradanfang|Gradmitte)\b", re.IGNORECASE)
REFERENCE_RE = re.compile(r"\b(?:davon|daraus|darin|dazu|hierzu|hiervon)\b", re.IGNORECASE)
BROAD_CARRIER = re.compile(
    r"\b(?:\w*Ansatz\w*|\w*Kompositum\w*|Trockengut|Heißgut|Kaltgut|"
    r"Zubereitungsgut|Drogenstoffposten|\w*Species\w*)\b",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_query(rel: Path, columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    completed = subprocess.run(
        [
            str(ROOT / "vmanus-exp"), "query-tsv", str(rel), "--selector", "page",
            "--allow", "f1r", "--columns", columns, "--forbid-prefix", "f84",
        ],
        cwd=ROOT, check=True, text=True, capture_output=True,
    )
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("missing GUARD_STATS")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return rows, {str(key): int(value) for key, value in json.loads(match.group(1)).items()}


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, name: str, condition: bool, detail: str = "") -> None:
        self.rows.append({"name": name, "ok": bool(condition), "detail": detail})

    @property
    def passed(self) -> bool:
        return all(row["ok"] for row in self.rows)


def main() -> int:
    checks = Checks()
    try:
        source, token_guard = guarded_query(
            TOKENS_REL, "page,locus,token_index,eva,kind,section,language,hand",
        )
        cross, cross_guard = guarded_query(
            CROSS_REL,
            "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
        )
        checks.add("guarded token selected", token_guard.get("selected") == 214, str(token_guard))
        checks.add("guarded cross selected", cross_guard.get("selected") == 28, str(cross_guard))
        checks.add("guard rejected token rows", token_guard.get("skipped_forbidden", 0) > 0, str(token_guard))
        checks.add("guard rejected cross rows", cross_guard.get("skipped_forbidden", 0) > 0, str(cross_guard))
        checks.add("source token census", len(source) == 214, str(len(source)))
        checks.add("source key uniqueness", len({(r["locus"], r["token_index"]) for r in source}) == 214)
        checks.add("source f1r only", all(r["page"] == "f1r" and not r["page"].startswith("f84") for r in source))
        checks.add("cross f1r only", all(r["page"] == "f1r" and not r["page"].startswith("f84") for r in cross))
        checks.add("source line census", len({r["locus"] for r in source}) == 28)
        checks.add("cross line census", len(cross) == 28)
        checks.add("cross all readers", sum(int(r["all_three_present"]) for r in cross) == 28)
        checks.add("cross exact readers", sum(int(r["all_present_exact"]) for r in cross) == 5)

        source_keys = [(r["page"], r["locus"], r["token_index"], r["eva"]) for r in source]
        by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in source:
            by_line[row["locus"]].append(row)
        checks.add("source physical order", list(by_line) == [f"f1r.{i}" for i in range(1, 29)])
        for index in range(1, 29):
            locus = f"f1r.{index}"
            rows = by_line[locus]
            checks.add(
                f"source indices {locus}",
                [int(r["token_index"]) for r in rows] == list(range(1, len(rows) + 1)),
            )
        cross_by_locus = {r["locus"]: r for r in cross}
        for locus, rows in by_line.items():
            checks.add(
                f"source cross replay {locus}",
                " ".join(r["eva"] for r in rows) == cross_by_locus[locus]["zl3b_clean"],
            )

        alignment = read_tsv(ART / "F1R_SOURCE_ALIGNMENT.tsv")
        tokens = read_tsv(ART / "F1R_TOKEN_READINGS.tsv")
        components = read_tsv(ART / "F1R_COMPONENT_TRACES.tsv")
        rivals = read_tsv(ART / "F1R_COMPOSITION_RIVALS.tsv")
        clauses = read_tsv(ART / "F1R_CLAUSE_FRAMES.tsv")
        lines = read_tsv(ART / "F1R_LINE_READER.tsv")
        comparison = read_tsv(ART / "F1R_GDT589_COMPARISON.tsv")
        transfer = read_tsv(ART / "F1R_TRANSFER_CARDS.tsv")
        occurrences = read_tsv(ART / "F1R_OCCURRENCE_AUDIT.tsv")
        attachments = read_tsv(ART / "F1R_VALUE_ATTACHMENT_AUDIT.tsv")
        rules = read_tsv(ART / "RENDERER_RULE_CARDS.tsv")
        controls = read_tsv(ART / "REGISTER_DIVERSE_RENDER_AUDIT.tsv")
        result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
        reader = (ART / "GDT672_F1R_CONCRETE_WORKING_READER.md").read_text(encoding="utf-8")

        checks.add("alignment row count", len(alignment) == 214)
        checks.add("token reading row count", len(tokens) == 214)
        checks.add("line row count", len(lines) == 28)
        checks.add("clause row count", len(clauses) == 28)
        checks.add("transfer card count", len(transfer) == 80 and len({r["surface"] for r in transfer}) == 80)
        checks.add("transfer position count", sum(int(r["count"]) for r in transfer) == 85)
        checks.add("rival card count", len(rivals) == 80)
        checks.add("occurrence audit count", len(occurrences) == 7)
        checks.add("value attachment count", len(attachments) == 17)
        checks.add("renderer rule count", len(rules) == 12)
        checks.add("control count", len(controls) == 6)
        checks.add("comparison statement count", len(comparison) == 7)
        checks.add("result status", result["status"] == EXPECTED_STATUS, result["status"])

        artifact_keys = [(r["page"], r["locus"], r["token_index"], r["eva"]) for r in alignment]
        token_keys = [(r["page"], r["locus"], r["token_index"], r["eva"]) for r in tokens]
        checks.add("alignment exact source replay", artifact_keys == source_keys)
        checks.add("token exact source replay", token_keys == source_keys)
        checks.add("alignment gdt589 match", all(r["gdt589_surface_match"] == "1" for r in alignment))

        glossary_rows = read_tsv(V48 / "V48_WORKING_TOKEN_GLOSSARY.tsv")
        glossary = {r["surface"]: r for r in glossary_rows}
        exact = [r for r in tokens if r["route"] == "EXACT_V48"]
        transfer_rows = [r for r in tokens if r["route"] != "EXACT_V48"]
        checks.add("V48 exact position count", len(exact) == 129, str(len(exact)))
        checks.add("V48 exact surface count", len({r["eva"] for r in exact}) == 84)
        checks.add("transfer position count from tokens", len(transfer_rows) == 85)
        checks.add("transfer surface count from tokens", len({r["eva"] for r in transfer_rows}) == 80)
        checks.add("no unassigned route", all(r["route"] in {"EXACT_V48", "ROLE_COMPOSED_TRANSFER", "LOCAL_WHOLE_HYPOTHESIS", "OCCURRENCE_SCOPED_TRANSFER"} for r in tokens))
        checks.add("transfer cannot shadow V48", not ({r["surface"] for r in transfer} & set(glossary)))
        for row in exact:
            card = glossary[row["eva"]]
            checks.add(f"V48 meaning {row['token_ordinal_global']}", row["working_meaning_de"] == card["working_meaning_de"])
            checks.add(f"V48 source {row['token_ordinal_global']}", row["v48_source"] == card["source"])
            checks.add(f"V48 strength {row['token_ordinal_global']}", row["confidence"] == card["strength"])
            checks.add(f"V48 scope {row['token_ordinal_global']}", row["v48_scope_state"] == card["scope_state"])
            checks.add(f"V48 priority {row['token_ordinal_global']}", row["v48_priority"] == card["priority"])
        scope_counts = Counter(r["v48_scope_state"] for r in exact)
        checks.add("V48 exact scope profile", scope_counts == {"KNOWN_EXACT_WHOLE": 89, "KNOWN_CONTEXT_LICENSED": 40}, str(scope_counts))

        source_counts = Counter(r["eva"] for r in source)
        for card in transfer:
            checks.add(f"transfer count {card['surface']}", source_counts[card["surface"]] == int(card["count"]))
            checks.add(f"transfer meaning nonempty {card['surface']}", bool(card["working_meaning_de"].strip()))
            checks.add(f"transfer scope {card['surface']}", card["scope"] in {"F1R_CURATED_ROLE_COMPOSITION", "F1R_EXACT_SURFACE_ONLY"})
            checks.add(f"transfer not promoted {card['surface']}", all(r["promoted_to_v48"] == "0" for r in rivals if r["surface"] == card["surface"]))
        attachment_source = read_tsv(SRC / "F1R_VALUE_ATTACHMENTS.tsv")
        checks.add("value attachment source replay", len(attachment_source) == 17)
        checks.add(
            "value attachment exact replay",
            [tuple(row.get(key, "") for key in ("locus", "token_index", "surface", "contextual_render_de", "head_token_index", "relation", "rationale")) for row in attachments]
            == [tuple(row.get(key, "") for key in ("locus", "token_index", "surface", "contextual_render_de", "head_token_index", "relation", "rationale")) for row in attachment_source],
        )
        attachment_keys = {(row["locus"], row["token_index"]): row for row in attachments}
        for token in tokens:
            attachment = attachment_keys.get((token["locus"], token["token_index"]))
            checks.add(
                f"contextual value {token['token_ordinal_global']}",
                token["contextual_render_de"] == (attachment["contextual_render_de"] if attachment else token["working_meaning_de"]),
            )
            checks.add(
                f"attachment flag {token['token_ordinal_global']}",
                token["value_attachment"] == ("1" if attachment else "0"),
            )

        stem_roles = {r["structural_role"] for r in read_tsv(V48 / "STEM_MODEL_V48.tsv")}
        component_by_token: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in components:
            component_by_token[row["token_ordinal_global"]].append(row)
        checks.add("component token coverage", set(component_by_token) == {str(i) for i in range(1, 215)})
        for token in tokens:
            rows = sorted(component_by_token[token["token_ordinal_global"]], key=lambda r: int(r["component_ordinal"]))
            checks.add(f"component concatenation {token['token_ordinal_global']}", "".join(r["surface_segment"] for r in rows) == token["eva"])
            starts = [int(r["char_start"]) for r in rows]
            ends = [int(r["char_end"]) for r in rows]
            checks.add(f"component offsets {token['token_ordinal_global']}", starts[0] == 0 and ends[-1] == len(token["eva"]) and starts[1:] == ends[:-1])
            if token["route"] == "ROLE_COMPOSED_TRANSFER":
                checks.add(
                    f"productive roles {token['token_ordinal_global']}",
                    all(r["component_role"] in stem_roles | {"KNOWN_SHOR", "KNOWN_SOR"} for r in rows),
                )
                checks.add(f"productive flags {token['token_ordinal_global']}", all(r["productive"] == "1" for r in rows))

        tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in tokens:
            tokens_by_locus[row["locus"]].append(row)
        checks.add("line order", [r["locus"] for r in lines] == [f"f1r.{i}" for i in range(1, 29)])
        for row in lines:
            locus_tokens = tokens_by_locus[row["locus"]]
            expected_literal = " | ".join(f"{r['eva']} = {r['working_meaning_de']}" for r in locus_tokens)
            expected_contextual = " | ".join(f"{r['eva']} = {r['contextual_render_de']}" for r in locus_tokens)
            checks.add(f"line source replay {row['locus']}", row["zl3b_line"] == " ".join(r["eva"] for r in locus_tokens))
            checks.add(f"line literal replay {row['locus']}", row["literal_token_glosses_de"] == expected_literal)
            checks.add(f"line contextual replay {row['locus']}", row["contextual_token_values_de"] == expected_contextual)
            checks.add(f"line token count {row['locus']}", int(row["token_count"]) == len(locus_tokens))
            checks.add(f"line translation nonempty {row['locus']}", bool(row["working_translation_de"].strip()))
            checks.add(f"line no generic filler {row['locus']}", GENERIC_FILLER.search(row["working_translation_de"]) is None)
            features = {feature for token in locus_tokens for feature in token["contextual_semantic_features"].split("+")}
            checks.add(f"line actions licensed {row['locus']}", not ACTION_RE.search(row["working_translation_de"]) or "ACTION" in features)
            checks.add(f"line quantities licensed {row['locus']}", not QUANTITY_RE.search(row["working_translation_de"]) or "QUANTITY" in features)
            checks.add(f"line stages licensed {row['locus']}", not STAGE_RE.search(row["working_translation_de"]) or "STAGE" in features)
            checks.add(f"line references licensed {row['locus']}", not REFERENCE_RE.search(row["working_translation_de"]) or "REFERENCE" in features)
            checks.add(f"reader source visible {row['locus']}", f"`{row['zl3b_line']}`" in reader)
            checks.add(f"reader literal visible {row['locus']}", row["literal_token_glosses_de"] in reader)
            checks.add(f"reader contextual visible {row['locus']}", row["contextual_token_values_de"] in reader)
            checks.add(f"reader translation visible {row['locus']}", row["working_translation_de"] in reader)
            if int(row["learned_transfer_tokens"]):
                checks.add(f"learned uncertainty visible {row['locus']}", "≈" in row["working_translation_de"] and "?" in row["working_translation_de"])
        checks.add("reader block count", len(re.findall(r"^## f1r\.\d+$", reader, re.M)) == 28)
        checks.add("reader no generic filler in translations", all(GENERIC_FILLER.search(r["working_translation_de"]) is None for r in lines))

        g589 = [r for r in read_tsv(G589 / "gdt589_793_count_overlay_statement_reader.tsv") if r["physical_page"] == "f1r"]
        g589.sort(key=lambda r: int(r["reader_statement_ordinal"]))
        g589_surfaces = [s for r in g589 for s in r["surface_sequence"].split()]
        checks.add("GDT589 guarded sequence replay", g589_surfaces == [r["eva"] for r in source])
        checks.add("comparison only flag", all(r["comparison_only_not_meaning_input"] == "1" for r in comparison))
        checks.add("new comparison no filler", sum(int(r["gdt672_generic_filler_hits"]) for r in comparison) == 0)
        checks.add("old comparison has filler", sum(int(r["gdt589_generic_filler_hits"]) for r in comparison) > 0)

        checks.add("five complete controls", sum(int(r["unknown_tokens"]) == 0 for r in controls) == 5)
        checks.add("one abstinence control", sum(int(r["unknown_tokens"]) == 1 for r in controls) == 1)
        checks.add("control six sections", len({r["section"] for r in controls}) == 6)
        checks.add("control two languages", len({r["language"] for r in controls}) >= 2)
        checks.add("control three hands", len({r["hand"] for r in controls}) >= 3)
        checks.add("control no f1r or f84", all(r["page"] != "f1r" and not r["page"].startswith("f84") for r in controls))
        checks.add("control no generic filler", all(GENERIC_FILLER.search(r["new_working_translation_de"]) is None for r in controls))
        coverage = {r["locus"]: r for r in read_tsv(V48 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv")}
        complete = {r["locus"]: r for r in read_tsv(V48 / "COMPLETE_PASSAGES_V48.tsv")}
        for row in controls:
            inherited = coverage[row["locus"]]
            checks.add(f"control source {row['control_id']}", row["zl3b_line"] == inherited["zl3b_line"])
            checks.add(f"control glosses {row['control_id']}", row["v48_token_glosses_de"] == inherited["token_glosses_de"])
            if int(row["unknown_tokens"]) == 0:
                checks.add(f"control complete {row['control_id']}", row["inherited_v48_translation_de"] == complete[row["locus"]]["working_translation_de"])
            else:
                checks.add(f"control open visible {row['control_id']}", "dsheody" in row["new_working_translation_de"] and "offen" in row["new_working_translation_de"])

        checks.add("result source metrics", result["source"]["tokens"] == 214 and result["source"]["physical_lines"] == 28)
        checks.add("result exact metrics", result["coverage"]["exact_v48_positions"] == 129 and result["coverage"]["exact_v48_surface_types"] == 84)
        checks.add("result transfer metrics", result["coverage"]["transfer_positions"] == 85 and result["coverage"]["transfer_surface_types"] == 80)
        checks.add("result no unassigned", result["coverage"]["unassigned_positions"] == 0)
        checks.add("result learned line profile", result["coverage"]["lines_with_learned_transfer"] == 19 and result["coverage"]["lines_without_learned_transfer"] == 9)
        checks.add("result filler zero", result["renderer"]["generic_filler_hits_new"] == 0)
        broad_hits = sum(len(BROAD_CARRIER.findall(row["working_translation_de"])) for row in lines)
        checks.add("result broad carrier count", result["renderer"]["broad_carrier_hits_new"] == broad_hits, str(broad_hits))
        checks.add("result value attachment count", result["renderer"]["value_attachments"] == 17)
        checks.add("manifest forbids sealed pages", json.loads((BASE / "experiment.json").read_text())["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})

        with tempfile.TemporaryDirectory(prefix="gdt672_validate_") as temp:
            temp_path = Path(temp)
            completed = subprocess.run(
                [sys.executable, str(SRC / "run.py"), "--output-dir", str(temp_path), "--no-docs"],
                cwd=ROOT, text=True, capture_output=True,
            )
            checks.add("fresh builder exits zero", completed.returncode == 0, completed.stderr[-1000:])
            if completed.returncode == 0:
                for name in OUTPUT_NAMES:
                    checks.add(f"byte replay {name}", (temp_path / name).read_bytes() == (ART / name).read_bytes())
    except Exception as exc:  # validator must still publish a useful failure artifact
        checks.add("validator exception", False, repr(exc))

    failed = [row for row in checks.rows if not row["ok"]]
    validation = {
        "experiment_id": "GDT672",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks.rows) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
        "checks": checks.rows,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: validation[key] for key in ("status", "checks_passed", "checks_failed")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
