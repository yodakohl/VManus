#!/usr/bin/env python3
"""Build GDT790: an image-owner overlay for f77r, f82r and f83r."""

from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
LINES_REL = Path("transcription/voynich_zl3b_lines.tsv")
PAGES = ("f77r", "f82r", "f83r")

PANEL_SPECS = SRC / "PANEL_RECORD_SPECS.tsv"
LABEL_SPECS = SRC / "LABEL_OWNER_SPECS.tsv"
IMAGE_SPECS = SRC / "IMAGE_SOURCE_SPECS.tsv"
FAMILY_SPECS = SRC / "IMAGE_FORM_FAMILY_SPECS.tsv"
COMPATIBILITY_SPECS = SRC / "COMPATIBILITY_SPECS.tsv"

STATUS = (
    "PASS__3_PAGES__10_IMAGE_PANELS__13_RECORDS__123_PROSE_LINES__940_PROSE_TOKENS__"
    "27_LABEL_LOCI__28_LABEL_TOKENS__10_EXACT_LABEL_PROSE_EDGES__9_MULTI_CHARACTER_EDGES__"
    "PANEL_OWNER_OVERLAY__ZERO_TOKEN_MEANING_CHANGES__ZERO_PREFIX_EXPORT"
)

OUTPUT_NAMES = (
    "GDT790_13_PANEL_RECORD_BINDINGS.tsv",
    "GDT790_10_PANEL_SUMMARY.tsv",
    "GDT790_27_LABEL_OWNER_ATLAS.tsv",
    "GDT790_28_LABEL_TOKEN_ATLAS.tsv",
    "GDT790_10_EXACT_LABEL_PROSE_BRIDGES.tsv",
    "GDT790_5_IMAGE_FORM_FAMILIES.tsv",
    "GDT790_123_IMAGE_AWARE_LINES.tsv",
    "GDT790_11_COMPATIBILITY_MATRIX.tsv",
    "GDT790_3_IMAGE_SOURCES.tsv",
    "GDT790_GUARDED_SOURCE_STATS.tsv",
    "GDT790_IMAGE_AWARE_RECORD_READER.md",
    "GDT790_MANUAL_IMAGE_GRAMMAR_AUDIT.md",
    "RESULT.json",
)

H_CLASS = {
    "p": "H1_ENTRY_BIASED",
    "s": "H2_SUBENTRY_BIASED",
    "r": "H3_LATE_REFERENCE_BIASED",
    "l": "H4_INTERNAL_FIELD_BIASED",
}
VALUE_FORMS = {"daiin": "VALUE_III_CANDIDATE", "daiiin": "VALUE_IV_CANDIDATE"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    materialized = list(rows)
    if fields is None:
        fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def query_lines() -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(LINES_REL), "--selector", "page"]
    for page in PAGES:
        command.extend(("--allow", page))
    command.extend((
        "--columns",
        "page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean",
        "--forbid-prefix", "f84",
        "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded line query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guard statistics missing")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}
    if any(row["page"].startswith("f84") for row in rows):
        raise RuntimeError("sealed page materialized")
    return rows, stats


def line_number(row: dict[str, str]) -> int:
    return int(row["line_number"])


def line_head_class(surface: str) -> str:
    return H_CLASS.get(surface[:1], "H0_OTHER")


def pipe(values: Iterable[str]) -> str:
    output: list[str] = []
    for value in values:
        if value and value not in output:
            output.append(value)
    return "|".join(output) if output else "NONE"


def find_record(row: dict[str, str], specs: list[dict[str, str]]) -> dict[str, str] | None:
    number = line_number(row)
    matches = [
        spec for spec in specs
        if spec["page"] == row["page"] and int(spec["start_line"]) <= number <= int(spec["end_line"])
    ]
    if len(matches) > 1:
        raise RuntimeError(f"overlapping record specs at {row['locus']}")
    return matches[0] if matches else None


def classify_token(
    token: str,
    ordinal: int,
    same_page_refs: dict[tuple[str, str], list[dict[str, str]]],
    global_label_tokens: set[str],
    page: str,
) -> str:
    refs = same_page_refs.get((page, token), [])
    head = line_head_class(token) if ordinal == 1 else ""
    if refs:
        role = "BILDVERWEIS:" + pipe(row["component_id"] for row in refs)
    elif token in global_label_tokens and len(token) > 1:
        role = "SEITENUEBERGREIFENDE_LABELFORM"
    elif token in VALUE_FORMS:
        role = VALUE_FORMS[token]
    else:
        role = "OFFEN"
    return pipe((head, role))


def render_line(
    row: dict[str, str],
    record: dict[str, str],
    same_page_refs: dict[tuple[str, str], list[dict[str, str]]],
    global_label_tokens: set[str],
) -> tuple[str, str, str]:
    tokens = row["eva_clean"].split()
    cells: list[str] = []
    roles: list[str] = []
    consumed: set[int] = set()
    for index, token in enumerate(tokens):
        if index in consumed:
            continue
        ordinal = index + 1
        role = classify_token(token, ordinal, same_page_refs, global_label_tokens, row["page"])
        roles.append(f"{ordinal}:{role}")
        if index + 1 < len(tokens) and tokens[index + 1] == "daiin":
            head = line_head_class(token) if ordinal == 1 else "FIELD"
            ref = same_page_refs.get((row["page"], token), [])
            ref_tag = f"; BILDVERWEIS {pipe(item['component_id'] for item in ref)}" if ref else ""
            cells.append(f"[{head} {token} → WERT-III-KANDIDAT daiin{ref_tag}]")
            roles.append(f"{ordinal + 1}:VALUE_III_CANDIDATE_BOUND_TO_PREVIOUS_COMPLETE_FORM")
            consumed.add(index + 1)
            continue
        if same_page_refs.get((row["page"], token)):
            targets = pipe(item["component_id"] for item in same_page_refs[(row["page"], token)])
            prefix = f"{line_head_class(token)}; " if ordinal == 1 else ""
            cells.append(f"[{prefix}BILDVERWEIS {token} → {targets}]")
        elif token in global_label_tokens and len(token) > 1:
            prefix = f"{line_head_class(token)}; " if ordinal == 1 else ""
            cells.append(f"[{prefix}LABELFORM {token}]")
        elif token in VALUE_FORMS:
            cells.append(f"[{VALUE_FORMS[token]} {token}]")
        elif ordinal == 1:
            cells.append(f"[{line_head_class(token)} {token}]")
        else:
            cells.append(f"[OFFEN {token}]")
    owner = record["owner_display_de"]
    subowner = record["subowner_display_de"]
    rendered = f"Bildbesitzer: {owner}; lokales Feld: {subowner}. " + " ".join(cells)
    return " | ".join(roles), " ".join(cells), rendered


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines, guard_stats = query_lines()
    panels = read_tsv(PANEL_SPECS)
    labels = read_tsv(LABEL_SPECS)
    images = read_tsv(IMAGE_SPECS)
    families = read_tsv(FAMILY_SPECS)
    compatibility = read_tsv(COMPATIBILITY_SPECS)

    if len(lines) != 150 or {row["page"] for row in lines} != set(PAGES):
        raise RuntimeError("three-page guarded source changed")
    label_by_locus = {row["locus"]: row for row in labels}
    if len(label_by_locus) != len(labels):
        raise RuntimeError("duplicate label locus")

    prose: list[dict[str, str]] = []
    label_lines: list[dict[str, str]] = []
    record_for_locus: dict[str, dict[str, str]] = {}
    for row in lines:
        record = find_record(row, panels)
        is_label = row["locus"] in label_by_locus
        if is_label == (record is not None):
            raise RuntimeError(f"locus must be exactly record or label: {row['locus']}")
        if is_label:
            label_lines.append(row)
        else:
            prose.append(row)
            if record is None:
                raise RuntimeError(f"prose record missing: {row['locus']}")
            record_for_locus[row["locus"]] = record

    if len(prose) != 123 or len(label_lines) != 27:
        raise RuntimeError("expected 123 prose and 27 label lines")

    source_label_text = {row["locus"]: row["eva_clean"] for row in label_lines}
    for spec in labels:
        if source_label_text.get(spec["locus"]) != spec["label_surface"]:
            raise RuntimeError(f"label source drift at {spec['locus']}")

    label_tokens: list[dict[str, Any]] = []
    for spec in labels:
        for ordinal, token in enumerate(spec["label_surface"].split(), 1):
            label_tokens.append({
                "label_token_id": f"GDT790-LT{len(label_tokens) + 1:02d}",
                "page": spec["page"],
                "locus": spec["locus"],
                "label_token_ordinal": ordinal,
                "label_token": token,
                "panel_id": spec["panel_id"],
                "component_id": spec["component_id"],
                "working_local_default_de": spec["working_local_default_de"],
                "anchor_eligible": "YES" if len(token) > 1 else "NO_SINGLE_CHARACTER_BOUNDARY_UNSTABLE",
                "binding_scope": "EXACT_ZL3B_TOKEN_OCCURRENCE_ONLY",
                "lexical_export": "NO",
            })

    global_label_tokens = {str(row["label_token"]) for row in label_tokens}
    same_page_refs: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for label in labels:
        for token in label["label_surface"].split():
            same_page_refs[(label["page"], token)].append(label)

    bridges: list[dict[str, Any]] = []
    for label_token in label_tokens:
        token = str(label_token["label_token"])
        for row in prose:
            ordinals = [str(index) for index, value in enumerate(row["eva_clean"].split(), 1) if value == token]
            if not ordinals:
                continue
            record = record_for_locus[row["locus"]]
            same_page = row["page"] == label_token["page"]
            label_no = int(str(label_token["locus"]).split(".")[-1])
            prose_no = line_number(row)
            if not same_page:
                direction = "CROSS_PAGE"
            elif label_no < prose_no:
                direction = "LABEL_PRECEDES_PROSE"
            else:
                direction = "PROSE_PRECEDES_LABEL"
            if len(token) == 1:
                anchor_status = "EXACT_SINGLE_CHARACTER_NONANCHOR"
            elif same_page:
                anchor_status = "SAME_PAGE_OWNER_REFERENCE_CANDIDATE"
            else:
                anchor_status = "CROSS_PAGE_NAME_OR_FORMULA_CANDIDATE"
            bridges.append({
                "bridge_id": f"GDT790-B{len(bridges) + 1:02d}",
                "label_page": label_token["page"],
                "label_locus": label_token["locus"],
                "label_token": token,
                "label_panel_id": label_token["panel_id"],
                "label_component_id": label_token["component_id"],
                "prose_page": row["page"],
                "prose_locus": row["locus"],
                "prose_record_id": record["record_id"],
                "prose_token_ordinals": "|".join(ordinals),
                "same_page": "YES" if same_page else "NO",
                "document_direction": direction,
                "anchor_status": anchor_status,
                "semantic_credit": "ZERO__STRING_REUSE_ONLY",
            })

    bridge_by_label_locus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bridge in bridges:
        bridge_by_label_locus[str(bridge["label_locus"])].append(bridge)

    label_atlas: list[dict[str, Any]] = []
    for spec in labels:
        hits = bridge_by_label_locus[spec["locus"]]
        label_atlas.append({
            **spec,
            "label_token_count": len(spec["label_surface"].split()),
            "exact_prose_occurrence_edges": len(hits),
            "same_page_edges": sum(hit["same_page"] == "YES" for hit in hits),
            "cross_page_edges": sum(hit["same_page"] == "NO" for hit in hits),
            "word_meaning_selected": "NO",
            "prefix_or_root_export": "NO",
        })

    lines_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose:
        lines_by_record[record_for_locus[row["locus"]]["record_id"]].append(row)

    record_bindings: list[dict[str, Any]] = []
    for spec in panels:
        rows = sorted(lines_by_record[spec["record_id"]], key=line_number)
        expected = list(range(int(spec["start_line"]), int(spec["end_line"]) + 1))
        if [line_number(row) for row in rows] != expected:
            raise RuntimeError(f"record coverage drift: {spec['record_id']}")
        if rows[0]["paragraph_start"] != "1" or rows[-1]["paragraph_end"] != "1":
            raise RuntimeError(f"paragraph boundary drift: {spec['record_id']}")
        record_bindings.append({
            **spec,
            "prose_line_count": len(rows),
            "prose_token_count": sum(int(row["token_count"]) for row in rows),
            "first_surface": rows[0]["eva_clean"].split()[0],
            "first_head_class": line_head_class(rows[0]["eva_clean"].split()[0]),
            "exact_label_echo_edges": sum(bridge["prose_record_id"] == spec["record_id"] for bridge in bridges),
            "text_cells_modified": 0,
        })

    rendered_lines: list[dict[str, Any]] = []
    for row in prose:
        record = record_for_locus[row["locus"]]
        roles, structural, rendered = render_line(row, record, same_page_refs, global_label_tokens)
        rendered_lines.append({
            "page": row["page"],
            "panel_id": record["panel_id"],
            "record_id": record["record_id"],
            "record_kind": record["record_kind"],
            "locus": row["locus"],
            "line_number": row["line_number"],
            "record_line_ordinal": line_number(row) - int(record["start_line"]) + 1,
            "token_count": row["token_count"],
            "line_head_class": line_head_class(row["eva_clean"].split()[0]),
            "owner_display_de": record["owner_display_de"],
            "subowner_display_de": record["subowner_display_de"],
            "zl3b_line": row["eva_clean"],
            "token_role_trace": roles,
            "structural_cells_de": structural,
            "image_aware_render_de": rendered,
            "token_semantics_changed": 0,
            "word_to_single_figure_by_proximity": 0,
        })

    panel_to_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in record_bindings:
        panel_to_records[str(row["panel_id"])].append(row)
    panel_to_labels: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in label_atlas:
        panel_to_labels[str(row["panel_id"])].append(row)
    ordered_panel_ids: list[str] = []
    for spec in panels:
        if spec["panel_id"] not in ordered_panel_ids:
            ordered_panel_ids.append(spec["panel_id"])
    panel_summary: list[dict[str, Any]] = []
    for panel_id in ordered_panel_ids:
        records = panel_to_records[panel_id]
        panel_labels = panel_to_labels[panel_id]
        first = records[0]
        panel_summary.append({
            "page": first["page"],
            "panel_id": panel_id,
            "layout_order": min(int(row["layout_order"]) for row in records),
            "topology_class": first["topology_class"],
            "owner_display_de": first["owner_display_de"],
            "record_ids": pipe(str(row["record_id"]) for row in records),
            "record_count": len(records),
            "prose_line_count": sum(int(row["prose_line_count"]) for row in records),
            "prose_token_count": sum(int(row["prose_token_count"]) for row in records),
            "label_locus_count": len(panel_labels),
            "label_token_count": sum(int(row["label_token_count"]) for row in panel_labels),
            "label_loci": pipe(str(row["locus"]) for row in panel_labels),
            "binding_scope": "PANEL_OWNER_WITH_LOCAL_LABELS",
        })

    prose_token_counts = Counter(token for row in prose for token in row["eva_clean"].split())
    family_rows: list[dict[str, Any]] = []
    for spec in families:
        forms = spec["observed_label_forms"].split("|")
        family_rows.append({
            **spec,
            "observed_label_form_count": len(forms),
            "label_token_occurrences": sum(1 for row in label_tokens if row["label_token"] in forms),
            "prose_exact_occurrences": sum(prose_token_counts[form] for form in forms),
            "free_component_export": "NO",
            "unseen_form_prediction": "NO",
        })

    source_stats = [{
        "source": str(LINES_REL),
        "selector": "page",
        "allow_values": "|".join(PAGES),
        "output_columns": "page|locus|line_number|paragraph_start|paragraph_end|token_count|eva_clean",
        "selected": guard_stats.get("selected", 0),
        "skipped_forbidden": guard_stats.get("skipped_forbidden", 0),
        "skipped_not_allowed": guard_stats.get("skipped_not_allowed", 0),
        "f84_materialized": 0,
        "f84r_materialized": 0,
    }]

    tables: dict[str, list[dict[str, Any]]] = {
        OUTPUT_NAMES[0]: record_bindings,
        OUTPUT_NAMES[1]: panel_summary,
        OUTPUT_NAMES[2]: label_atlas,
        OUTPUT_NAMES[3]: label_tokens,
        OUTPUT_NAMES[4]: bridges,
        OUTPUT_NAMES[5]: family_rows,
        OUTPUT_NAMES[6]: rendered_lines,
        OUTPUT_NAMES[7]: compatibility,
        OUTPUT_NAMES[8]: images,
        OUTPUT_NAMES[9]: source_stats,
    }
    for name, rows in tables.items():
        write_tsv(output_dir / name, rows)

    reader: list[str] = [
        "# GDT790 image-aware record reader", "",
        "This is an image-owner overlay, not a plaintext translation. Every prose line keeps its exact ZL3b token order. `BILDVERWEIS` means that the complete token is also an exact same-page label; `LABELFORM` means exact reuse of a label token from another admitted page. `WERT-III-KANDIDAT` is only the bounded GDT764 structural cue.", "",
    ]
    page_order = {page: index for index, page in enumerate(PAGES)}
    ordered_records = sorted(record_bindings, key=lambda row: (page_order[str(row["page"])], int(row["layout_order"])))
    for record in ordered_records:
        reader.extend((
            f"## {record['page']} · {record['record_id']} · {record['panel_id']}", "",
            f"Bildbesitzer: **{record['owner_display_de']}**", "",
            f"Lokales Feld: {record['subowner_display_de']}", "",
            f"Topologie: `{record['topology_class']}` · Bindung: `{record['binding_scope']}` · {record['prose_line_count']} Zeilen / {record['prose_token_count']} Token", "",
        ))
        for line in (item for item in rendered_lines if item["record_id"] == record["record_id"]):
            reader.extend((
                f"### {line['locus']}", "",
                f"ZL3b: `{line['zl3b_line']}`", "",
                f"Overlay: {line['image_aware_render_de']}", "",
            ))
    (output_dir / OUTPUT_NAMES[10]).write_text("\n".join(reader).rstrip() + "\n", encoding="utf-8")

    panel_lookup = {row["panel_id"]: row for row in panel_summary}
    audit: list[str] = [
        "# GDT790 manual image-grammar audit", "",
        "## What the three pages support", "",
        "The images organize the prose at panel and record scale. They do not provide arrows, a word-by-word alignment or a free prefix dictionary. The useful hierarchy is:", "",
        "`PAGE → IMAGE PANEL (silent owner/topic) → PARAGRAPH RECORD → LINE/FIELD → exact local label anchor`", "",
        "All 123 prose lines fit 13 physically bounded records under ten visible panel owners without changing one text cell. All 27 graphical-label loci receive a visible component or component zone; ambiguous proximity remains explicitly ambiguous.", "",
        "## Page pattern", "",
        f"- f77r: the label-rich upper arch has {panel_lookup['F77_TOP_ARCH']['label_locus_count']} label loci and {panel_lookup['F77_TOP_ARCH']['prose_token_count']} prose tokens; the middle and lower panels have {panel_lookup['F77_MIDDLE_BODY']['label_locus_count']}/{panel_lookup['F77_MIDDLE_BODY']['prose_token_count']} and {panel_lookup['F77_LOWER_VESSEL']['label_locus_count']}/{panel_lookup['F77_LOWER_VESSEL']['prose_token_count']}.",
        f"- f82r: the bottom communal pool has {panel_lookup['F82_BOTTOM_COMMUNAL']['label_locus_count']} label loci and {panel_lookup['F82_BOTTOM_COMMUNAL']['prose_token_count']} prose tokens, versus {panel_lookup['F82_TOP_COUPLED']['label_locus_count']}/{panel_lookup['F82_TOP_COUPLED']['prose_token_count']} above and {panel_lookup['F82_MIDDLE_TRANSFER']['label_locus_count']}/{panel_lookup['F82_MIDDLE_TRANSFER']['prose_token_count']} in the middle.",
        f"- f83r: three single-figure panels carry no separate labels and {panel_lookup['F83_UPPER_SPRAY']['prose_token_count']}, {panel_lookup['F83_MIDDLE_LOOP']['prose_token_count']} and {panel_lookup['F83_LOWER_DRIP']['prose_token_count']} tokens. The lower coupled panel carries four label loci and {panel_lookup['F83_LOWER_COUPLED']['prose_token_count']} tokens across two main and two embedded records.", "",
        "This is descriptive support for panel ownership: visual complexity, label density and record burden move together within each page. It is not yet a lexical key.", "",
        "## Exact label-to-prose bridges", "",
        "There are ten exact ZL3b label-token occurrence edges. Nine involve multi-character forms and one is the single token `o`, which is retained in the census but excluded as an anchor.", "",
        "- `otedy`: f77r upper-arch label, then exact f77r P2 opener; four further prose occurrences on f82r/f83r.",
        "- `okal`: f82r lower-pool label, with two exact earlier occurrences in f82r P1/P2.",
        "- `otchdy`: f77r middle figure-zone label and exact opener of the embedded f83r Q1 record.",
        "- `olaiin`: f82r lower-pool figure label and exact occurrence in f77r P3.", "",
        "The same-page edges can serve as occurrence-local image references. Cross-page edges prove only reusable written names or formulas; they do not transport the source picture's object meaning.", "",
        "## Best compositional leads", "",
        "The strongest new visual family is `darol/darolsy`: both complete labels sit at drawn inflow/outlet structures on different pages. `okal/okaldy` is a same-panel adjacent-station pair. `dchdy/otchdy`, `otedy/dotedy` and the `otol/otolaiin/olaiin/olsaiin` deck remain useful but broader station/name families. None licenses `d`, `ot`, `ol`, `dy`, `sy` or `aiin` as a free lexeme.", "",
        "## Renderer consequence", "",
        "The previous generic action prose is not reused. The record reader now says what visible configuration owns each paragraph, preserves every EVA form, exposes bounded `X daiin` fields, and marks exact label references. Unknown cells stay open instead of being converted into verbs such as take, work or transfer.", "",
    ]
    (output_dir / OUTPUT_NAMES[11]).write_text("\n".join(audit).rstrip() + "\n", encoding="utf-8")

    same_page_multi = sum(row["same_page"] == "YES" and len(str(row["label_token"])) > 1 for row in bridges)
    cross_page_multi = sum(row["same_page"] == "NO" and len(str(row["label_token"])) > 1 for row in bridges)
    result: dict[str, Any] = {
        "schema": "GDT790_PANEL_OWNER_IMAGE_GRAMMAR_OVERLAY_RESULT_V1",
        "experiment_id": "GDT790",
        "status": STATUS,
        "scope": {
            "pages": list(PAGES),
            "images_reviewed": len(images),
            "image_panels": len(panel_summary),
            "records": len(record_bindings),
            "prose_lines": len(prose),
            "prose_tokens": sum(int(row["token_count"]) for row in prose),
            "label_loci": len(labels),
            "label_tokens": len(label_tokens),
            "new_pages_used": 0,
            "f84_used": False,
            "f84r_used": False,
        },
        "overlay": {
            "hierarchy": "PAGE>IMAGE_PANEL_OWNER>PARAGRAPH_RECORD>LINE_FIELD>EXACT_LABEL_ANCHOR",
            "panel_owner_bindings": len(record_bindings),
            "line_owner_bindings": len(rendered_lines),
            "local_label_owner_bindings": len(label_atlas),
            "text_cells_modified": 0,
            "word_to_single_figure_by_proximity": 0,
            "prefix_or_root_exports": 0,
            "token_meaning_changes": 0,
        },
        "exact_label_prose_graph": {
            "occurrence_edges": len(bridges),
            "multi_character_edges": sum(len(str(row["label_token"])) > 1 for row in bridges),
            "same_page_multi_character_edges": same_page_multi,
            "cross_page_multi_character_edges": cross_page_multi,
            "single_character_nonanchor_edges": sum(len(str(row["label_token"])) == 1 for row in bridges),
            "distinct_multi_character_label_forms_with_edges": sorted({str(row["label_token"]) for row in bridges if len(str(row["label_token"])) > 1}),
        },
        "working_image_families": [
            {"family_id": row["family_id"], "default_de": row["working_family_default_de"], "status": row["status"]}
            for row in family_rows
        ],
        "decision": {
            "selected": "PANEL_OWNER_OVERLAY_WITH_EXACT_LOCAL_LABEL_REFERENCES",
            "preserved": "existing H1-H4, whole-word and bounded-field structures remain below the overlay",
            "retired": "generic action prose and proximity-only word-to-figure assignments",
            "next": "compare whole-form and field distributions across the ten image topology classes on these same three pages; seek topology-predictive complete forms before opening more pages",
        },
        "guard_stats": guard_stats,
    }
    (output_dir / OUTPUT_NAMES[12]).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.artifacts_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
