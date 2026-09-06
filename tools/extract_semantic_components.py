#!/usr/bin/env python3
"""Conservative, deterministic inventory of tracked report/theory prose.

Extracts quoted historical proposals, never validates or deduplicates meanings.
No raw TSV, raster, runtime or source artifact is read. Coverage includes every
tracked filename whose basename contains report or theory, including exclusions.
"""
import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = "research_registry/decisions/legacy_semantic_components.jsonl"
SEMANTIC = re.compile(r"meaning|semantic|translation|gloss|lexem|hypothes|theor|mechanism|interpret|Bedeut|Lesung|Lesart|Arbeitshyp|Versuch|Kandidat|Übersetz|Deutung|Modell|reading", re.I)
PROPOSAL = re.compile(r"hypothes|propos|candidate|working (?:gloss|reading|meaning|model|interpretation)|trial|can (?:mean|express)|may (?:mean|express)|Arbeitshyp|Versuch|Kandidat|Vermut|bedeutet|steht für", re.I)
TABLE = re.compile(r"meaning|gloss|translation|reading|interpretation|hypothesis|candidate|Bedeut|Lesung|Lesart|Kandidat|Deutung|Arbeitshyp|Expansion", re.I)
SEALED = re.compile(r"(?<![A-Za-z0-9])f84[A-Za-z0-9]*(?![A-Za-z0-9])", re.I)
# Strict equals assignment only: prose colons/arrows are not gloss declarations.
MAPPING = re.compile(r"(?<![A-Za-z0-9_])(?:`|\*\*)?([A-Za-z]{1,24}(?:[+/-][A-Za-z]{1,24})*)\s*=\s*(?!=)(?:`|\*\*)?([A-Za-zÄÖÜäöüß][^\n]{0,180})")
META_LABEL = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*|`)?(?:status|decision|gate|result|method|validation|checks?|claim ceiling|verdict|source|scope|provenance|corrected provenance|ergebnis|entscheidung)\s*(?:\*\*|`)?\s*[:=]", re.I)
META_LHS = {"status", "decision", "gate", "result", "method", "validation", "checks", "source", "scope", "provenance", "p", "n", "rank", "auc", "score"}


def explicit_mapping(text):
    if META_LABEL.search(text):
        return False
    for match in MAPPING.finditer(text):
        lhs = match.group(1)
        # P is a historical uppercase core; lowercase p is commonly a p-value.
        if lhs.lower() in META_LHS and lhs != "P":
            continue
        # Marked assignments and uppercase historical core declarations are
        # retained. Unmarked lowercase assignments need an explicit trial cue.
        marked = "`" in text or "**" in text
        if marked or lhs.isupper() or PROPOSAL.search(text):
            return True
    return False
CAUTION = "Historical wording only; extraction is not scientific validation, endorsement, complete semantic parsing, or deduplication."


def stable(path, line, kind):
    return "LEGACY_COMPONENT:" + hashlib.sha256(f"{path}:{line}:{kind}".encode()).hexdigest()[:20]


def parse(lines):
    """Return (components, unresolved, skipped), with one-based exact spans."""
    components, unresolved, skipped = [], [], Counter()
    section = ""
    section_start = 1
    section_semantic = False
    section_hits = 0
    in_fence = False
    table_header = None
    i = 0

    def close(end):
        if section_semantic and section_hits == 0 and end >= section_start:
            unresolved.append({"line_start": section_start, "line_end": end,
                               "section": section, "reason": "semantic_heading_without_conservative_extractable_component"})

    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            skipped["fenced_code_boundary"] += 1
            i += 1
            continue
        if in_fence:
            skipped["fenced_body_line"] += 1
            i += 1
            continue
        if SEALED.search(line):
            skipped["sealed_selector_line"] += 1
            i += 1
            continue
        heading = re.match(r"^#{1,6}\s+(.+)", line)
        if heading:
            close(i)
            section, section_start, section_hits = heading.group(1), i + 1, 0
            section_semantic = bool(SEMANTIC.search(section))
            table_header = None
            i += 1
            continue
        if not line.strip():
            table_header = None
            i += 1
            continue
        if line.lstrip().startswith("|"):
            if table_header is None:
                table_header = line
                i += 1
                continue
            if re.fullmatch(r"[| :\-]+", line):
                i += 1
                continue
            if TABLE.search(table_header):
                components.append({"line_start": i + 1, "line_end": i + 1,
                    "section": section, "kind": "semantic_table_row",
                    "exact_statement": line, "table_header": table_header,
                    "interpretation_status": "explicit_table_component_requires_review"})
                section_hits += 1
            elif SEMANTIC.search(line):
                unresolved.append({"line_start": i + 1, "line_end": i + 1,
                    "section": section, "reason": "table_without_explicit_semantic_column"})
            i += 1
            continue
        # Preserve wrapped prose/list items, excluding source code and drawings.
        start = i
        block = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^\s*(?:#{1,6} |```|~~~|\||[-*] |\d+\. )", lines[i]):
            block.append(lines[i])
            i += 1
        text = "\n".join(block)
        if SEALED.search(text):
            skipped["sealed_selector_block"] += 1
            continue
        if len(text) > 4000:
            if SEMANTIC.search(text):
                unresolved.append({"line_start": start + 1, "line_end": i,
                    "section": section, "reason": "long_semantic_block_requires_manual_review"})
            continue
        mapping = explicit_mapping(text)
        proposal = bool(PROPOSAL.search(text)) and bool(SEMANTIC.search(text)) and not META_LABEL.search(text)
        if mapping or proposal:
            components.append({"line_start": start + 1, "line_end": i,
                "section": section, "kind": "explicit_mapping_candidate" if mapping else "explicit_hypothesis_prose",
                "exact_statement": text, "interpretation_status": "unreviewed_candidate_may_include_rejection_or_limitation"})
            section_hits += 1
        elif SEMANTIC.search(text) or META_LABEL.search(text):
            unresolved.append({"line_start": start + 1, "line_end": i,
                "section": section, "reason": "semantic_prose_without_explicit_component_pattern"})
    close(len(lines))
    return components, unresolved, dict(skipped)


def run():
    paths = sorted(subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"))
    paths = [p for p in paths if p and re.search(r"report|theory", Path(p).name, re.I)]
    records = []
    for path in paths:
        parent = re.search(r"(?:^|/)(gdt\d+)(?:_|/|\b)", path, re.I)
        parent_id = parent.group(1).upper() if parent else None
        coverage = {"record_type": "source_coverage", "source_path": path,
                    "parent_gdt": parent_id, "components": 0, "unresolved_blocks": 0}
        reason = None
        if Path(path).suffix.lower() != ".md":
            reason = "not_markdown_report_or_theory_prose"
        elif SEALED.search(path):
            reason = "sealed_selector_in_filename"
        elif any(part.lower() in {"runtime", "artifacts", "raw", "private", "fixtures", "testdata"} for part in Path(path).parts):
            reason = "non_prose_or_private_source_directory"
        elif Path(path).is_absolute() or (ROOT / path).is_symlink():
            reason = "unsafe_path"
        if reason:
            coverage.update(status="excluded_before_body_read", reason=reason)
            records.append(coverage)
            continue
        data = (ROOT / path).read_bytes()
        try:
            lines = data.decode("utf-8").splitlines()
        except UnicodeDecodeError:
            coverage.update(status="excluded", reason="non_utf8_prose")
            records.append(coverage)
            continue
        source_sha = hashlib.sha256(data).hexdigest()
        status_lines = [{"line": i + 1, "text": line} for i, line in enumerate(lines[:50])
                        if not SEALED.search(line) and re.match(r"^\s*(?:Status|Decision|Entscheidung|Ergebnisstatus)\s*:", line, re.I)]
        comp, unresolved, skipped = parse(lines)
        # A pattern extractor cannot certify complete semantic coverage. Keep
        # the whole safe source reachable, even when some rows were extracted.
        unresolved.append({"line_start": 1, "line_end": len(lines),
                           "section": "", "reason": "unreviewed_source_remainder_no_exhaustive_semantic_parse"})
        common = {"source_path": path, "source_sha256": source_sha, "parent_gdt": parent_id,
                  "assessment_basis": "automatic_historical_prose_extraction", "verdict": "unreviewed",
                  "inherited_status": status_lines or [{"text": "not_explicitly_declared_in_first_50_lines"}],
                  "claim_ceiling": CAUTION}
        for c in comp:
            records.append(dict(common, record_type="hypothesis_component",
                                record_id=stable(path, c["line_start"], c["kind"]), **c))
        for c in unresolved:
            records.append(dict(common, record_type="unresolved_block",
                                record_id=stable(path, c["line_start"], c["reason"]), **c))
        coverage.update(status="processed", source_sha256=source_sha, line_count=len(lines),
                        components=len(comp), unresolved_blocks=len(unresolved), skipped=skipped,
                        reason="conservative_patterns_applied_not_complete_semantic_review")
        records.append(coverage)
    counts = Counter(r["record_type"] for r in records)
    summary = {"record_type": "extraction_summary", "schema_version": 1,
               "inventory_rule": "All git-tracked basenames containing report or theory, case insensitive; content read only for eligible markdown prose.",
               "source_count": len(paths), "counts": dict(counts),
               "limits": [CAUTION, "Unresolved pointers are not extracted hypotheses.",
                          "Report-level PASS may describe software or inherited working glosses; no component inherits scientific support.",
                          "Filename coverage is complete for this declared snapshot, not all historical ideas or all semantic content.",
                          "Fenced text and sealed-selector lines/blocks are excluded. Raw source tables and images are not read."]}
    output = ROOT / OUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in [summary] + records))
    print(json.dumps(summary, ensure_ascii=False))


def controls():
    example = ["# Proposed reading", "", "New trial: **qolchedy = daraus? wird?**.", "", "| core | meaning |", "|---|---|", "| X | thing? |", "", "```text", "SECRET_RAW = avoid", "```", "", "f84r forbidden = avoid"]
    comp, _, skipped = parse(example)
    assert len(comp) == 2
    assert comp[0]["line_start"] == 3 and comp[1]["line_start"] == 7
    assert not any("SECRET_RAW" in c["exact_statement"] or "f84" in c["exact_statement"] for c in comp)
    assert skipped["fenced_body_line"] == 1 and skipped["sealed_selector_line"] == 1
    assert not explicit_mapping("Status: **exploratory stop; not a translation**")
    assert not explicit_mapping("Status: NO_CLEAN")
    assert not explicit_mapping("**Corrected provenance:** a source binding changed.")
    assert not explicit_mapping("`SH→S` is an adjacency, not a meaning.")
    assert explicit_mapping("- `AIR=BAHN` becomes a working gloss.")
    assert explicit_mapping("New trial: **qolchedy = daraus? wird?**.")
    assert stable("a.md", 3, "k") == stable("a.md", 3, "k")
    print(json.dumps({"controls": "PASS", "claim": "Extraction/source-boundary fixtures only; no scientific validation."}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args()
    controls() if args.controls else run()
