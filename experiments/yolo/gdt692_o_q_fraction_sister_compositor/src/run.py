#!/usr/bin/env python3
"""Build V65 by composing the complete admitted O/Q fraction sister lattice."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt692_o_q_fraction_sister_compositor"
ART = BASE / "artifacts"
SRC = BASE / "src"
G691 = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch"
V64_TOKENS = G691 / "artifacts/V64_479_TOKEN_READER.tsv"
V64_LINES = G691 / "artifacts/V64_51_LINE_PRACTICAL_READER.tsv"
V64_VERBS = G691 / "artifacts/V64_113_VERB_PRESERVATION.tsv"
V64_RESULT = G691 / "artifacts/RESULT.json"
COMPONENTS = SRC / "V65_COMPONENT_LEXICON.tsv"
SURFACE_RULES = SRC / "V65_FRACTION_SURFACE_RULES.tsv"
CARRY_RULES = SRC / "V65_CONTEXT_CARRY_RULES.tsv"
BOUND_SPANS = SRC / "V65_BOUND_SPAN_RULES.tsv"
CONTEXTUAL_RIVALS = SRC / "V65_CONTEXTUAL_PRODUCT_RIVALS.tsv"
HISTORICAL_ANALOGUES = SRC / "V65_HISTORICAL_HEAD_ANALOGUES.tsv"
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        if not rows:
            raise ValueError(f"Cannot infer fields for empty TSV {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(glosses: list[str]) -> tuple[str, list[dict[str, object]]]:
    text = ""
    segments: list[dict[str, object]] = []
    for ordinal, gloss in enumerate(glosses, 1):
        if gloss in {";", "."}:
            stripped = text.rstrip(" ,;.")
            for segment in segments:
                if int(segment["end"]) > len(stripped):
                    segment["end"] = len(stripped)
            text = stripped
            start = len(text)
            text += gloss
            segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator
        start = len(text)
        text += gloss
        segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
    if text and not text.endswith("."):
        text += "."
    if text:
        text = text[:1].upper() + text[1:]
    return text, segments


def root_occurrences(glosses: list[str], root: str) -> tuple[int, int]:
    occurrences = 0
    positions = 0
    for gloss in glosses:
        hits = sum(root in word.casefold() for word in WORD_RE.findall(gloss))
        occurrences += hits
        positions += int(hits > 0)
    return occurrences, positions


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    token_rows = read_tsv(V64_TOKENS)
    line_rows = read_tsv(V64_LINES)
    verb_rows = read_tsv(V64_VERBS)
    component_rows = read_tsv(COMPONENTS)
    rule_rows = read_tsv(SURFACE_RULES)
    carry_rows = read_tsv(CARRY_RULES)
    bound_rows = read_tsv(BOUND_SPANS)
    rival_rows = read_tsv(CONTEXTUAL_RIVALS)
    historical_rows = read_tsv(HISTORICAL_ANALOGUES)
    v64_result = json.loads(V64_RESULT.read_text(encoding="utf-8"))

    assert len(token_rows) == 479 and len(line_rows) == 51 and len(verb_rows) == 113
    assert len(rule_rows) == 16 and len(component_rows) == 9 and len(carry_rows) == 2
    assert len(bound_rows) == 2 and len(rival_rows) == 6 and len(historical_rows) == 2
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in token_rows)
    assert v64_result["basis"]["new_pages"] == 0

    component_by_id = {row["component"]: row for row in component_rows}
    assert len(component_by_id) == len(component_rows)
    rule_by_surface = {row["surface"]: row for row in rule_rows}
    assert len(rule_by_surface) == len(rule_rows)
    carry_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in carry_rows}
    assert len(carry_by_key) == len(carry_rows)
    rival_by_span = {
        (row["locus"], int(row["start_ordinal"]), int(row["end_ordinal"])): row
        for row in rival_rows
    }
    assert len(rival_by_span) == len(rival_rows)
    for rule in rule_rows:
        visible = ""
        for component in rule["composition"].split("+"):
            assert component in component_by_id, (rule["surface"], component)
            visible += component_by_id[component]["surface_literal"]
        visible += rule["visible_tail"]
        assert visible == rule["surface"], (rule["surface"], visible)
        if rule["visible_tail"]:
            assert rule["whole_extension"] != "NONE"

    source_by_key: dict[tuple[str, int], dict[str, str]] = {}
    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        key = (row["locus"], int(row["token_ordinal"]))
        assert key not in source_by_key
        source_by_key[key] = row
        tokens_by_locus[row["locus"]].append(row)
    for rows in tokens_by_locus.values():
        rows.sort(key=lambda row: int(row["token_ordinal"]))

    surface_counts = Counter(row["surface"] for row in token_rows if row["surface"] in rule_by_surface)
    assert set(surface_counts) == set(rule_by_surface)
    assert sum(surface_counts.values()) == 41
    for surface, rule in rule_by_surface.items():
        assert surface_counts[surface] == int(rule["expected_positions"]), (surface, surface_counts[surface])

    token_out: list[dict[str, object]] = []
    target_audit: list[dict[str, object]] = []
    revisions: list[dict[str, object]] = []
    rendered: dict[tuple[str, int], str] = {}
    used_rules: Counter[str] = Counter()

    for source in token_rows:
        key = (source["locus"], int(source["token_ordinal"]))
        old = source["v64_token_gloss_de"]
        rule = rule_by_surface.get(source["surface"])
        carry = carry_by_key.get(key)
        assert not (rule and carry)
        if rule:
            assert old == rule["expected_v64_gloss_de"], (key, old, rule["expected_v64_gloss_de"])
            new = rule["selected_v65_gloss_de"]
            rule_id = rule["rule_id"]
            composition = rule["composition"]
            family = rule["family"]
            product_rival = rule["product_rival_de"]
            visible_tail = rule["visible_tail"]
            whole_extension = rule["whole_extension"]
            basis = rule["basis"]
            action_licensed = int(rule["action_licensed"])
            used_rules[rule_id] += 1
        elif carry:
            assert source["surface"] == carry["surface"]
            assert old == carry["expected_v64_gloss_de"], (key, old, carry["expected_v64_gloss_de"])
            new = carry["selected_v65_gloss_de"]
            rule_id = carry["rule_id"]
            composition = carry["composition"]
            family = "CONTEXT_CARRY"
            product_rival = old
            visible_tail = ""
            whole_extension = "NONE"
            basis = carry["basis"]
            action_licensed = 0
            used_rules[rule_id] += 1
        else:
            new = old
            rule_id = "NONE"
            composition = "INHERITED"
            family = "INHERITED"
            product_rival = "NONE"
            visible_tail = ""
            whole_extension = "NONE"
            basis = "UNCHANGED_V64"
            action_licensed = 0
        changed = int(new != old)
        rendered[key] = new
        out: dict[str, object] = dict(source)
        out.update({
            "v65_token_gloss_de": new, "v65_changed": changed,
            "v65_rule_id": rule_id, "v65_composition": composition,
            "v65_family": family, "v65_product_rival_de": product_rival,
            "v65_visible_tail": visible_tail, "v65_whole_extension": whole_extension,
            "v65_basis": basis,
        })
        token_out.append(out)
        if rule:
            target_audit.append({
                "page": source["page"], "locus": source["locus"],
                "token_ordinal": source["token_ordinal"], "surface": source["surface"],
                "rule_id": rule_id, "composition": composition, "family": family,
                "visible_tail": visible_tail, "whole_extension": whole_extension,
                "action_licensed": action_licensed, "v64_gloss_de": old,
                "v65_gloss_de": new, "changed": changed,
                "product_rival_de": product_rival, "basis": basis,
            })
        if changed:
            revisions.append({
                "page": source["page"], "locus": source["locus"],
                "token_ordinal": source["token_ordinal"], "surface": source["surface"],
                "rule_id": rule_id, "composition": composition,
                "visible_tail": visible_tail, "whole_extension": whole_extension,
                "v64_gloss_de": old, "v65_gloss_de": new,
                "product_rival_de": product_rival, "basis": basis,
            })

    assert len(target_audit) == 41
    assert len(revisions) == 32
    assert sum(1 for row in target_audit if int(row["changed"])) == 30
    assert used_rules == {
        "F001": 2, "F002": 1, "F003": 1, "F004": 1, "F005": 2,
        "F006": 2, "F007": 1, "F008": 2, "F009": 1, "F010": 1,
        "F011": 16, "F012": 1, "F013": 6, "F014": 2, "F015": 1,
        "F016": 1, "C001": 1, "C002": 1,
    }

    lattice_rows: list[dict[str, object]] = []
    for rule in rule_rows:
        surface = rule["surface"]
        rows = [row for row in target_audit if row["surface"] == surface]
        lattice_rows.append({
            "rule_id": rule["rule_id"], "surface": surface,
            "composition": rule["composition"], "family": rule["family"],
            "visible_tail": rule["visible_tail"], "whole_extension": rule["whole_extension"],
            "positions": len(rows), "changed_positions": sum(int(row["changed"]) for row in rows),
            "action_licensed": rule["action_licensed"],
            "v64_gloss_de": rule["expected_v64_gloss_de"],
            "v65_gloss_de": rule["selected_v65_gloss_de"],
            "product_rival_de": rule["product_rival_de"],
            "loci": "|".join(f"{row['locus']}#{row['token_ordinal']}" for row in rows),
            "basis": rule["basis"],
        })

    component_use: Counter[str] = Counter()
    component_weighted: Counter[str] = Counter()
    for rule in rule_rows:
        for component in rule["composition"].split("+"):
            component_use[component] += 1
            component_weighted[component] += int(rule["expected_positions"])
    component_summary: list[dict[str, object]] = []
    for row in component_rows:
        component = row["component"]
        assert component_use[component] > 0
        component_summary.append({
            **row, "surface_rules": component_use[component],
            "weighted_occurrences": component_weighted[component],
        })

    bound_span_out: list[dict[str, object]] = []
    bound_by_locus: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    covered_bound_keys: set[tuple[str, int]] = set()
    for bound in bound_rows:
        locus = bound["locus"]
        start = int(bound["start_ordinal"])
        end = int(bound["end_ordinal"])
        assert 1 <= start <= end <= len(tokens_by_locus[locus])
        assert start not in bound_by_locus[locus]
        span_tokens = tokens_by_locus[locus][start - 1:end]
        actual_surfaces = "|".join(row["surface"] for row in span_tokens)
        actual_glosses = "|".join(rendered[(locus, int(row["token_ordinal"]))] for row in span_tokens)
        assert actual_surfaces == bound["surfaces"], (bound["span_id"], actual_surfaces)
        assert actual_glosses == bound["expected_v65_token_glosses"], (bound["span_id"], actual_glosses)
        for ordinal in range(start, end + 1):
            key = (locus, ordinal)
            assert key not in covered_bound_keys
            covered_bound_keys.add(key)
        bound_by_locus[locus][start] = bound
        rival = rival_by_span.get((locus, start, end))
        bound_span_out.append({
            **bound,
            "actual_surfaces": actual_surfaces,
            "actual_v65_token_glosses": actual_glosses,
            "contextual_product_rival_de": rival["contextual_rival_de"] if rival else "NONE",
            "validated": 1,
        })

    contextual_rival_out: list[dict[str, object]] = []
    for rival in rival_rows:
        locus = rival["locus"]
        start = int(rival["start_ordinal"])
        end = int(rival["end_ordinal"])
        if start == end:
            selected_span = rendered[(locus, start)]
        else:
            bound = bound_by_locus[locus].get(start)
            assert bound and int(bound["end_ordinal"]) == end
            selected_span = bound["combined_v65_gloss_de"]
        assert selected_span == rival["main_v65_span_de"], (rival["rival_id"], selected_span)
        contextual_rival_out.append({
            **rival,
            "selected_status": "CONTEXTUAL_RIVAL_RETAINED__NOT_GLOBAL_DEFAULT",
            "validated": 1,
        })

    line_by_locus = {row["locus"]: row for row in line_rows}
    assert len(line_by_locus) == 51 and set(line_by_locus) == set(tokens_by_locus)
    line_out: list[dict[str, object]] = []
    token_out_by_key = {(str(row["locus"]), int(row["token_ordinal"])): row for row in token_out}
    for locus, source_line in line_by_locus.items():
        rows = tokens_by_locus[locus]
        old_glosses = [row["v64_token_gloss_de"] for row in rows]
        new_glosses = [rendered[(locus, int(row["token_ordinal"]))] for row in rows]
        new_units: list[str] = []
        ordinal = 1
        while ordinal <= len(rows):
            bound = bound_by_locus[locus].get(ordinal)
            if bound:
                new_units.append(bound["combined_v65_gloss_de"])
                ordinal = int(bound["end_ordinal"]) + 1
            else:
                new_units.append(new_glosses[ordinal - 1])
                ordinal += 1
        old_text, _old_segments = render(old_glosses)
        new_text, _new_segments = render(new_units)
        assert old_text == source_line["v64_practical_translation_de"], (locus, old_text, source_line["v64_practical_translation_de"])
        changed_ordinals = [int(row["token_ordinal"]) for row, old, new in zip(rows, old_glosses, new_glosses) if old != new]
        apparatus = []
        for row, old, new in zip(rows, old_glosses, new_glosses):
            if old == new:
                continue
            item = token_out_by_key[(locus, int(row["token_ordinal"]))]
            apparatus.append(f"#{row['token_ordinal']} {row['surface']}: {old} → {new} [{item['v65_rule_id']}]")
        for start, bound in sorted(bound_by_locus[locus].items()):
            apparatus.append(
                f"#{start}–{bound['end_ordinal']} {bound['surfaces']}: "
                f"als gebundene Spanne → {bound['combined_v65_gloss_de']} [{bound['span_id']}]"
            )
        out: dict[str, object] = dict(source_line)
        out.update({
            "v65_compositional_translation_de": new_text,
            "v65_changed_token_positions": len(changed_ordinals),
            "v65_changed_ordinals": "|".join(map(str, changed_ordinals)) or "NONE",
            "v65_compact_apparatus_de": " || ".join(apparatus) or "NONE",
            "v65_status": "COMPLETE_FRACTION_SISTER_COMPOSITION__BOUND_SPANS__AUSZUG_ONLY_EXPLICIT_WORKFLOW",
        })
        line_out.append(out)
    assert len(line_out) == 51
    assert sum(int(row["v65_changed_token_positions"]) for row in line_out) == 32

    verb_out: list[dict[str, object]] = []
    for verb in verb_rows:
        key = (verb["locus"], int(verb["token_ordinal"]))
        old = source_by_key[key]["v64_token_gloss_de"]
        new = rendered[key]
        matched = verb["verb_de"]
        old_present = int(matched.casefold() in old.casefold())
        new_present = int(matched.casefold() in new.casefold())
        assert old_present == int(verb["v64_exact_form_present"])
        assert old_present == new_present, (key, matched, old, new)
        verb_out.append({
            "page": verb["page"], "locus": verb["locus"],
            "token_ordinal": verb["token_ordinal"], "surface": verb["surface"],
            "verb_de": matched, "canonical_lemma": verb["canonical_lemma"],
            "v64_token_gloss_de": old, "v65_token_gloss_de": new,
            "action_licensed": verb["action_licensed"],
            "v64_exact_form_present": old_present,
            "v65_exact_form_present": new_present,
            "preserved_exact_ordinal": 1,
            "gdt692_additional_verb_form_loss": 0,
        })
    assert len(verb_out) == 113
    assert not any(int(row["gdt692_additional_verb_form_loss"]) for row in verb_out)

    v64_glosses = [row["v64_token_gloss_de"] for row in token_rows]
    v65_glosses = [rendered[(row["locus"], int(row["token_ordinal"]))] for row in token_rows]
    term_comparison: list[dict[str, object]] = []
    for root in ["ansatz", "auszug", "fraktion", "absud", "mazerat", "masse"]:
        before_occurrences, before_positions = root_occurrences(v64_glosses, root)
        after_occurrences, after_positions = root_occurrences(v65_glosses, root)
        term_comparison.append({
            "root": root, "v64_occurrences": before_occurrences,
            "v65_occurrences": after_occurrences,
            "delta": after_occurrences - before_occurrences,
            "v64_token_positions": before_positions,
            "v65_token_positions": after_positions,
        })
    term_counts = {row["root"]: int(row["v65_occurrences"]) for row in term_comparison}
    before_terms = {row["root"]: int(row["v64_occurrences"]) for row in term_comparison}
    assert before_terms["auszug"] == 32 and term_counts["auszug"] == 7

    remaining_auszug = [
        row for row in token_out
        if any("auszug" in word.casefold() for word in WORD_RE.findall(str(row["v65_token_gloss_de"])))
    ]
    explicit_workflow_surfaces = {"qoteed", "olord", "oteed", "okeeodar", "qokeod", "kchod", "keeod"}
    assert len(remaining_auszug) == 7
    assert {str(row["surface"]) for row in remaining_auszug} == explicit_workflow_surfaces
    workflow_rows = [{
        "page": row["page"], "locus": row["locus"], "token_ordinal": row["token_ordinal"],
        "surface": row["surface"], "v65_gloss_de": row["v65_token_gloss_de"],
        "workflow_basis": "EXPLICIT_ABZIEH_OR_INHERITED_DRAW_OFF_PRODUCT_CARD",
    } for row in remaining_auszug]

    write_tsv(output_dir / "V64_41_FRACTION_SISTER_OCCURRENCES.tsv", target_audit)
    write_tsv(output_dir / "V65_16_SURFACE_SISTER_LATTICE.tsv", lattice_rows)
    write_tsv(output_dir / "V65_COMPONENT_USE_SUMMARY.tsv", component_summary)
    write_tsv(output_dir / "V65_479_TOKEN_READER.tsv", token_out)
    write_tsv(output_dir / "V65_51_LINE_COMPOSITIONAL_READER.tsv", line_out)
    write_tsv(output_dir / "V64_V65_32_TOKEN_REVISIONS.tsv", revisions)
    write_tsv(output_dir / "V65_113_VERB_PRESERVATION.tsv", verb_out)
    write_tsv(output_dir / "V64_V65_TERM_COMPARISON.tsv", term_comparison)
    write_tsv(output_dir / "V65_7_EXPLICIT_WORKFLOW_AUSZUGS.tsv", workflow_rows)
    write_tsv(output_dir / "V65_COMPONENT_LEXICON.tsv", component_rows)
    write_tsv(output_dir / "V65_2_BOUND_MULTI_TOKEN_SPANS.tsv", bound_span_out)
    write_tsv(output_dir / "V65_6_CONTEXTUAL_PRODUCT_RIVALS.tsv", contextual_rival_out)
    write_tsv(output_dir / "V65_2_HISTORICAL_HEAD_ANALOGUES.tsv", historical_rows)

    reader_doc = [
        "# GDT692 V65 — kompositionelle Fraktionsfassung", "",
        "Die r-Leiter bleibt in jeder Schwester sichtbar: AR/AIR/AIIR = Fraktion I/II/III. O setzt die Fraktion in einen begrenzten Ansatz-/Zubereitungsrahmen; K/T geben vorläufig heiß/kalt; L trägt Holz; D misst. QO bleibt ein einheitlicher Rahmen, während Verben und Resultatschwänze nur als belegte Ganzformwerte gelten. Zwei Mengenbindungen werden als Mehrwortspannen gerendert. Auszug bleibt global nur auf sieben expliziten Abzieh-/Produktkarten; sechs lokal starke Holzauszug-Lesungen bleiben sichtbar als Rivalen.", "",
    ]
    for line in line_out:
        reader_doc.extend([
            f"## {line['locus']}", "", f"`{line['zl3b_line']}`", "",
            str(line["v65_compositional_translation_de"]), "",
            f"Apparat: {line['v65_compact_apparatus_de']}", "",
        ])
    (output_dir / "GDT692_V65_COMPOSITIONAL_FRACTION_READER.md").write_text(
        "\n".join(reader_doc).rstrip() + "\n", encoding="utf-8"
    )

    generated = {
        "GDT692_V65_COMPOSITIONAL_FRACTION_READER.md",
        "V64_41_FRACTION_SISTER_OCCURRENCES.tsv", "V65_16_SURFACE_SISTER_LATTICE.tsv",
        "V65_COMPONENT_USE_SUMMARY.tsv", "V65_479_TOKEN_READER.tsv",
        "V65_51_LINE_COMPOSITIONAL_READER.tsv", "V64_V65_32_TOKEN_REVISIONS.tsv",
        "V65_113_VERB_PRESERVATION.tsv", "V64_V65_TERM_COMPARISON.tsv",
        "V65_7_EXPLICIT_WORKFLOW_AUSZUGS.tsv", "V65_COMPONENT_LEXICON.tsv",
        "V65_2_BOUND_MULTI_TOKEN_SPANS.tsv", "V65_6_CONTEXTUAL_PRODUCT_RIVALS.tsv",
        "V65_2_HISTORICAL_HEAD_ANALOGUES.tsv",
    }
    input_paths = [
        V64_TOKENS, V64_LINES, V64_VERBS, V64_RESULT,
        COMPONENTS, SURFACE_RULES, CARRY_RULES, BOUND_SPANS, CONTEXTUAL_RIVALS,
        HISTORICAL_ANALOGUES,
        Path(__file__).resolve(),
    ]
    result = {
        "status": "PASS_V65_16_SURFACE_41_OCCURRENCE_COMPOSITOR__32_TOKEN_REVISIONS__AUSZUG_32_TO_7_EXPLICIT_WORKFLOW_ONLY",
        "basis": {
            "lines": 51, "token_positions": 479, "target_surfaces": 16,
            "target_occurrences": 41, "context_carries": 2,
            "bound_multi_token_spans": 2, "contextual_product_rivals": 6,
            "historical_head_analogues": 2,
            "pages": len({row["page"] for row in token_rows}),
            "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
        "component_model": {
            "components": len(component_rows), "surface_rules": len(rule_rows),
            "surface_rule_occurrences": len(target_audit),
            "surface_changes": sum(int(row["changed"]) for row in target_audit),
            "context_carry_changes": len(carry_rows), "total_changes": len(revisions),
            "fraction_axis": "AR/AIR/AIIR = I/II/III",
            "temperature_axis": "K/T = hot/cold",
            "preparation_axis": "O = bounded preparation frame",
            "material_axis": "L = bounded wood head",
            "qo_axis": "QO is one frame; action remains exact-whole licensed",
            "action_axis": "D and exact-whole QO action values only at existing action ordinals",
            "result_axis": "finished is an exact-whole otardy tail, not a productive DY component",
            "recursive_axis": "the second AR in otarar recursively subselects fraction I",
            "literal_replay": "all 16 surface strings equal concatenated component literals plus any exact-whole visible tail",
        },
        "selected_decision": {
            "family_head": "Fraktion, not Auszug",
            "oar_oair": "fraction I/II of the preparation",
            "okar_otar_otair": "fraction I/II of the hot/cold preparation",
            "olkar_olkaiir": "fraction I/III of the hot wood preparation",
            "qokar_qotar": "hot/cold drug fraction I without invented action",
            "odar_qodar_qokaiir": "preserve existing measure/take action ordinals",
            "otarar_otardy": "recursive AR and exact-whole result tail preserve OTAR's fraction head",
            "bound_spans": "two GDT686 amount-head bindings are rendered as indivisible practical units",
            "contextual_rivals": "six locally strong wood-extract readings remain available without global promotion",
            "historical_challenger": "class/stage I/II/III remains a stronger period-neutral challenger wherever separation is absent",
            "product_rival": "Auszug stays an explicit rival but is not promoted without draw-off/product evidence",
        },
        "term_counts_v65": term_counts,
        "remaining_auszug_surfaces": sorted(explicit_workflow_surfaces),
        "verbs": {"exact_action_ordinals_preserved": len(verb_out), "additional_exact_form_loss": 0},
        "inherited_debt": v64_result["inherited_debt"],
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "files": {name: sha256(output_dir / name) for name in sorted(generated)},
        "claim_ceiling": "V65 is an exploratory compositional renderer over the same 51 lines. It selects the simplest shared working head across the admitted O/Q fraction sisters; it does not prove historical Voynich plaintext, phonetics, a carrier liquid, extraction method, ingredient, disease, patient or cure. Component values are bounded to the listed exact compositions.",
    }
    return result


def main() -> int:
    result = build(ART)
    write_json(ART / "RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
