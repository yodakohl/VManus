#!/usr/bin/env python3
"""Compile ALIM553 body-family occurrences without rewriting the source."""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter
from pathlib import Path

ROMAN = {x: i for i, x in enumerate(
    "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII XXIV XXV XXVI XXVII XXVIII XXIX XXX XXXI XXXII XXXIII".split(), 1
)}
# Full observed form tables. Bracket removal and casefolding apply only to keys.
FORMS = {
    "AQUA": ("aqua","aquam","aquas","aque","aquis","unda","undam","undis","limpha"),
    "HEAD": ("caput","capitis","capitus","capiti"),
    "STOMACH": ("stomachiq[u]e","stomachi","stomachum","stomacho","stomacus"),
    "OCULUS": ("oculos","oculis","oculorum"),
    "LIVER": ("epar","iecur","Iecur","Iecoris","Jecur"),
    "SPLEEN": ("splenis","splene","splenisq[ue]","splem"),
    "SKIN": ("cute","cutis","cutim"),
    "LUNG": ("pulmonem","pulmoni","pulmonis"),
    "KIDNEY": ("renes","renibus"),
    "BLADDER": ("vesicas","vesicam","vesice"),
    "WOMB": ("matricem","matrices","matrix","matrice"),
    "NERVOUS_TISSUE": ("neruos","neruis"),
    "HYDROPS": ("ydropicis","ydropicos","ydropisis"),
}
RULES = {
    "AQUA": "Lexical noun forms aqua/unda/limpha only; aquosas and lymphato excluded.",
    "HEAD": "Clinical caput family: caput, capitis, capitus, capiti; I capue caput excluded.",
    "STOMACH": "All observed stomachus-family forms, including stomachiq[u]e and stomacus.",
    "OCULUS": "Oculus forms only; lumen-family witnesses excluded explicitly.",
    "LIVER": "All observed epar/iecur/jecur spellings, including Iecoris and Jecur.",
    "SPLEEN": "All observed splen/splem forms, including splenisq[ue].",
    "SKIN": "All observed cutis/cute/cutim forms.",
    "LUNG": "All observed pulmonem/pulmoni/pulmonis forms.",
    "KIDNEY": "All observed renes/renibus forms.",
    "BLADDER": "All observed vesicas/vesicam/vesice forms.",
    "WOMB": "All observed matricem/matrices/matrix/matrice forms.",
    "NERVOUS_TISSUE": "All observed neruos/neruis forms; nerve/sinew breadth unresolved.",
    "HYDROPS": "All observed ydropicis/ydropicos/ydropisis forms.",
}
EXCLUDED = {
    "AQUA_ADJECTIVE_EXCLUDED": (("aquosas","lymphato"), "adjective/participle, not lexical water noun"),
    "OCULUS_NONFORM_LUMEN_EXCLUDED": (("lumine","Luminis","lumina","Lumina","Luminibus","lumen"), "lumen-family witness, possibly visual/light context, not oculus form"),
    "HEAD_I_CIVIC_LIGHT_EXCLUDED": (("capue","caput"), "I capue caput witness outside clinical HEAD"),
}

def norm(token: str) -> str:
    return token.rstrip(".,;:!?()~").casefold().replace("[", "").replace("]", "")

def compile_source(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    starts = []
    for line_no, line in enumerate(lines, 1):
        m = re.match(r"^([IVX]+)\. ", line)
        if m:
            starts.append((ROMAN[m.group(1)], m.group(1), line_no, line.rstrip("\n")))
    all_records = []
    for i, (number, roman, start, header) in enumerate(starts):
        end = starts[i + 1][2] - 1 if i + 1 < len(starts) else len(lines)
        name = re.match(r"^[IVX]+\. \[([^]]+)\]", header).group(1)
        all_records.append({"record_id": number, "roman": roman, "name": name,
                            "start_line": start, "end_line": end,
                            "header_exact": header, "complete_numbered_entry": True})
    records = [r for r in all_records if r["record_id"] != 31]
    record_for_line = {n: r["record_id"] for r in records
                       for n in range(r["start_line"], r["end_line"] + 1)}
    line_offsets, offset = [], 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)
    dictionaries = {family: {norm(form) for form in forms}
                    for family, forms in FORMS.items()}
    occurrences = {family: [] for family in FORMS}
    for line_no, line in enumerate(lines, 1):
        if line_no not in record_for_line:
            continue
        tokens = list(re.finditer(r"\S+", line.rstrip("\n")))
        for token_index, match in enumerate(tokens):
            raw = match.group()
            for family, keys in dictionaries.items():
                if norm(raw) not in keys:
                    continue
                if family == "HEAD" and line_no == 23:
                    continue
                occurrences[family].append({
                    "record_id": record_for_line[line_no], "source_line": line_no,
                    "char_offset": line_offsets[line_no - 1] + match.start(),
                    "line_column": match.start(), "source_token_index": token_index,
                    "sourceword_exact": raw, "polarity": "unreviewed",
                    "context_role": "unreviewed_source_context",
                    "annotation_status": "UNREVIEWED",
                    "source_line_exact": line.rstrip("\n"),
                })
    excluded = []
    for label, (forms, reason) in EXCLUDED.items():
        wanted = set(forms)
        for line_no, line in enumerate(lines, 1):
            if line_no not in record_for_line:
                continue
            if label == "HEAD_I_CIVIC_LIGHT_EXCLUDED" and line_no != 23:
                continue
            for token_index, match in enumerate(re.finditer(r"\S+", line.rstrip("\n"))):
                raw = match.group()
                if raw.rstrip(".,;:!?()~") not in wanted:
                    continue
                excluded.append({
                    "exclusion": label, "record_id": record_for_line[line_no],
                    "source_line": line_no,
                    "char_offset": line_offsets[line_no - 1] + match.start(),
                    "line_column": match.start(), "source_token_index": token_index,
                    "sourceword_exact": raw, "reason": reason,
                    "source_line_exact": line.rstrip("\n"),
                })
    source = {"path": str(path), "sha256": hashlib.sha256(text.encode()).hexdigest(),
              "line_count": len(lines),
              "offset_convention": "0-based Unicode character offset in complete source; source_line is 1-based; line_column and source_token_index are 0-based.",
              "matching_normalization": "Dictionary matching only: trim token-edge punctuation, casefold, and remove square-bracket markers while retaining bracket contents; stored source text is never normalized.",
              "scope": "32 complete numbered bath entries: I-XXX and XXXII-XXXIII; dedication XXXI excluded; prolog excluded."}
    by_record = {f: dict(sorted(Counter(str(o["record_id"]) for o in values).items(),
                                key=lambda pair: int(pair[0])))
                 for f, values in occurrences.items()}
    return {
        "schema": "balneis_body_source.v2", "status": "SOURCE_ONLY_AUDITED",
        "revision_history": {
            "initial_json_sha256": "b2db4bda3aa2abd9a2b61c631e0f303484e8cc55f6d9d92f0e4a4285cb2b2238",
            "initial_md_sha256": "d0b3bc43df29a5de03628429292bf64010e9940872f7aeae1dce630745b9d21d",
            "deviations_corrected": [
                "All 33 headers are bounded before excluding XXXI; XXX ends at line 364 and dedication lines 365-376 are excluded.",
                "HEAD adds capitus line 201 and capiti line 206.",
                "STOMACH adds stomacus line 387.",
                "LIVER adds Jecur line 79, Iecoris line 385, and Jecur line 397.",
                "AQUA excludes dedication aquis at line 370."
            ],
            "polarity_and_context": "Occurrence annotations are explicitly UNREVIEWED and non-operative."
        },
        "source": source, "family_rules": RULES,
        "family_form_tables": {f: {"source_forms": list(forms),
                                  "dictionary_keys": sorted(dictionaries[f])}
                               for f, forms in FORMS.items()},
        "records": records, "all_header_boundaries": all_records,
        "families": {f: {"count_total": len(values), "count_by_record": by_record[f],
                         "occurrences": values}
                     for f, values in occurrences.items()},
        "excluded_witnesses": excluded,
        "coverage_notes": [
            "Counts are lexical-form incidences, not independent clinical concepts or Voynich semantic units.",
            "Printed forms, bracket notation, capitalization, punctuation, and offsets are preserved.",
            "Polarity and context annotations are unreviewed and not operative.",
            "Only the explicitly listed family aliases are grouped; no additional synonym merging or target reading is asserted."
        ],
    }

def render(data: dict) -> str:
    s = data["source"]
    out = ["# *De balneis*: 32-entry body-term source inventory", "",
           "**Status:** SOURCE_ONLY_AUDITED (2026-09-15). No Voynich text, target image, decoder, or target body reading was used.", "",
           "## Source and revision", "",
           f"- Source: {s['path']}; SHA-256 {s['sha256']}; {s['line_count']} lines.",
           "- Compiler matching only trims token-edge punctuation, casefolds, and removes square-bracket markers; stored source text and offsets remain exact.",
           "- All 33 headers are bounded first. Selected records are I-XXX and XXXII-XXXIII; dedication XXXI (lines 365-376) and prolog are excluded.",
           "- Initial draft receipts: JSON b2db4bda3aa2abd9a2b61c631e0f303484e8cc55f6d9d92f0e4a4285cb2b2238; MD d0b3bc43df29a5de03628429292bf64010e9940872f7aeae1dce630745b9d21d.",
           "- Corrections retain all printed forms: capitus/capiti, stomacus, Jecur/Iecoris/Jecur; dedication aquis is removed from AQUA.",
           "- Polarity and context columns are explicitly unreviewed and non-operative.", "",
           "## Complete record boundaries", "",
           "| record | title | source lines | selected |", "|---:|---|---:|:---:|"]
    for r in data["all_header_boundaries"]:
        selected = "yes" if r["record_id"] != 31 else "no (dedication)"
        out.append(f"| {r['record_id']} ({r['roman']}) | {r['name']} | {r['start_line']}-{r['end_line']} | {selected} |")
    out += ["", "## Full family form tables", "",
            "Source-form lists are complete observed forms admitted to each family. Dictionary keys are shown in JSON; normalization is dictionary-only.", "",
            "| family | source forms | rule |", "|---|---|---|"]
    for f, forms in data["family_form_tables"].items():
        out.append(f"| {f} | {', '.join(forms['source_forms'])} | {data['family_rules'][f]} |")
    out += ["", "## Family counts", "", "| family | total | records with occurrence |", "|---|---:|---|"]
    for f, fd in data["families"].items():
        out.append(f"| {f} | {fd['count_total']} | {', '.join(fd['count_by_record']) or 'none'} |")
    out += ["", "## Occurrence ledger", "",
            "Each row preserves the complete source line, exact token, and offsets. Polarity/context are unreviewed and non-operative.", ""]
    for f, fd in data["families"].items():
        out += [f"### {f} ({fd['count_total']})", "",
                "| record | line | char offset | line column | exact sourceword | polarity | context role | exact source line |",
                "|---:|---:|---:|---:|---|---|---|---|"]
        for o in fd["occurrences"]:
            line = o["source_line_exact"].replace("|", r"\|")
            out.append(f"| {o['record_id']} | {o['source_line']} | {o['char_offset']} | {o['line_column']} | {o['sourceword_exact']} | {o['polarity']} | {o['context_role']} | {line} |")
        out.append("")
    out += ["## Excluded witness ledger", "",
            "Excluded forms remain visible for audit and are not counted.", "",
            "| exclusion | record | line | char offset | exact sourceword | reason | exact source line |", "|---|---:|---:|---:|---|---|---|"]
    for o in data["excluded_witnesses"]:
        line = o["source_line_exact"].replace("|", r"\|")
        out.append(f"| {o['exclusion']} | {o['record_id']} | {o['source_line']} | {o['char_offset']} | {o['sourceword_exact']} | {o['reason']} | {line} |")
    out += ["", "## Interpretation ceiling", "",
            "- These are lexical-form incidences, not 13 semantic units, a disease ontology, or target correspondences.",
            "- Clinical-looking lumen terms remain in exclusions; aquosas, lymphato, and I capue caput are also explicit exclusions.",
            "- NERVOUS_TISSUE preserves neruos/neruis without deciding nerve versus sinew.",
            "- This is source compilation only; no idea card or target reading was added.", ""]
    return "\n".join(out)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--json", required=True, type=Path)
    ap.add_argument("--markdown", required=True, type=Path)
    args = ap.parse_args()
    data = compile_source(args.source)
    args.json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render(data), encoding="utf-8")

if __name__ == "__main__":
    main()
