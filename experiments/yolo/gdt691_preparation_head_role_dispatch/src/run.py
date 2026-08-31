#!/usr/bin/env python3
"""Build V64: role-dispatch 140 preparation nouns and remove generic support heads."""

from __future__ import annotations

import csv
import hashlib
import json
import os
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
BASE = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch"
ART = BASE / "artifacts"
SRC = BASE / "src"
G690 = ROOT / "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus"
V63_TOKENS = G690 / "artifacts/V63_479_TOKEN_NOUN_BINDING.tsv"
V63_LINES = G690 / "artifacts/V63_51_LINE_MAIN_AND_APPARATUS.tsv"
V63_NOUNS = G690 / "artifacts/V63_MAIN_NOUN_OCCURRENCE_PROVENANCE.tsv"
V63_RESULT = G690 / "artifacts/RESULT.json"
V61_VERBS = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer/artifacts/V61_113_VERB_OCCURRENCE_PROVENANCE.tsv"
G652_O_ATLAS = ROOT / "experiments/yolo/gdt652_strict_v28_frontier_completion/artifacts/FAMILY_EVIDENCE_ATLAS.tsv"
EXACT_RULES = SRC / "V64_EXACT_TOKEN_RULES.tsv"
HISTORICAL_CONTROL = SRC / "HISTORICAL_PREPARATION_CONTROL.tsv"

WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
QUANTITY_PREFIX_RE = re.compile(
    r"(?:Portion(?:en)?|Maß(?:portion)?|Handvoll|Charge|Teil|Dosen)"
    r"(?:\s+[A-Za-zÄÖÜäöüß-]+){0,2}\s*$",
    re.IGNORECASE,
)
SOURCE_PREFIX_RE = re.compile(r"(?:aus|aus dem|aus Holzrohstoff)\s*$", re.IGNORECASE)
STATE_PATTERNS = {
    "HOT": re.compile(r"heiß|erhitz|erwärm|Heiz", re.IGNORECASE),
    "COLD": re.compile(r"kalt|gekühl|abgekühl|nachgekühl|kühl", re.IGNORECASE),
    "DRY": re.compile(r"trocken|getrockn|angetrockn", re.IGNORECASE),
    "MOIST": re.compile(r"feucht|eingeweich|angefeucht", re.IGNORECASE),
    "FINISHED": re.compile(r"fertig|vollständig|abgeschlossen|Endstufe|letzten", re.IGNORECASE),
}
PREPARATION_ROOTS = {
    "ansatz": "ANSATZ",
    "zubereitung": "ZUBEREITUNG",
    "auszug": "AUSZUG",
    "absud": "ABSUD",
    "mazerat": "MAZERAT",
    "rückstand": "RUECKSTAND",
    "trockengut": "TROCKENGUT",
    "extrakt": "EXTRAKT",
    "masse": "MASSE",
    "mischung": "MISCHUNG",
    "bad": "BAD",
}


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


def mention_role(row: dict[str, str]) -> str:
    start = int(row["token_char_start"])
    prefix = row["token_gloss_de"][:start].rstrip()
    surface = row["noun_surface_de"]
    canonical = row["canonical_noun_de"]
    if prefix.endswith("im"):
        return "LOCATIVE_CONTEXT"
    if (surface != canonical and surface.endswith("s")) or SOURCE_PREFIX_RE.search(prefix):
        return "GENITIVE_SOURCE"
    if QUANTITY_PREFIX_RE.search(prefix):
        return "QUANTITY_OBJECT"
    if canonical in {"Ansatz", "Auszug", "Zubereitung"}:
        return "HEAD"
    return "COMPOUND_HEAD"


def formal_route(row: dict[str, str], exact_o_prep_surfaces: set[str]) -> str:
    surface = row["surface"]
    if surface in exact_o_prep_surfaces:
        return "GDT652_EXACT_O_PREP_SURFACE"
    if surface.startswith("ol") and surface not in {"ol", "olal"}:
        return "PROVISIONAL_LOCAL_SCOPE"
    if row["productive_initial_head"] == "s":
        return "PRODUCTIVE_HEAD"
    return "LEARNED_WHOLE_OR_UNEXPORTED"


def preparation_terms(gloss: str) -> list[tuple[int, int, str, str]]:
    terms: list[tuple[int, int, str, str]] = []
    for match in WORD_RE.finditer(gloss):
        normalized = match.group(0).casefold()
        hits = [(root, label) for root, label in PREPARATION_ROOTS.items() if root in normalized]
        if not hits:
            continue
        _root, label = sorted(hits, key=lambda item: len(item[0]), reverse=True)[0]
        terms.append((match.start(), match.end(), match.group(0), label))
    return terms


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    token_rows = read_tsv(V63_TOKENS)
    line_rows = read_tsv(V63_LINES)
    noun_rows = read_tsv(V63_NOUNS)
    prep_rows = [dict(row) for row in noun_rows if row["noun_class"] == "PREPARATION"]
    v63_result = json.loads(V63_RESULT.read_text(encoding="utf-8"))
    verb_rows = read_tsv(V61_VERBS)
    o_atlas_rows = read_tsv(G652_O_ATLAS)
    rule_rows = read_tsv(EXACT_RULES)
    historical_rows = read_tsv(HISTORICAL_CONTROL)
    exact_o_prep_surfaces = {
        row["surface"] for row in o_atlas_rows
        if "O_PREP" in row["family"] and row["final_status"] in {"ACCEPTED_V29", "V28_ANCHOR"}
    }
    assert exact_o_prep_surfaces

    assert len(token_rows) == 479 and len(line_rows) == 51 and len(noun_rows) == 725
    assert len(prep_rows) == 140 and len(verb_rows) == 113 and len(rule_rows) == 54
    assert len({(row["locus"], row["token_ordinal"]) for row in prep_rows}) == 139
    assert len({row["surface"] for row in prep_rows}) == 99
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in token_rows)

    token_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in token_rows}
    assert len(token_by_key) == 479
    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        tokens_by_locus[row["locus"]].append(row)
    for rows in tokens_by_locus.values():
        rows.sort(key=lambda row: int(row["token_ordinal"]))

    role_audit: list[dict[str, object]] = []
    prep_by_key: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for source in prep_rows:
        row: dict[str, object] = dict(source)
        ordinal = int(source["token_ordinal"])
        neighbours = [
            token_by_key[(source["locus"], near)]["v63_main_token_gloss_de"]
            for near in range(max(1, ordinal - 1), min(len(tokens_by_locus[source["locus"]]), ordinal + 1) + 1)
        ]
        window = " || ".join(neighbours)
        row["mention_role"] = mention_role(source)
        row["formal_route"] = formal_route(source, exact_o_prep_surfaces)
        for name, pattern in STATE_PATTERNS.items():
            row[f"window_{name.lower()}"] = int(bool(pattern.search(window)))
        row["v63_neighbour_window_de"] = window
        prep_by_key[(source["locus"], ordinal)].append(row)
        role_audit.append(row)

    role_counts = Counter(str(row["mention_role"]) for row in role_audit)
    route_counts = Counter(str(row["formal_route"]) for row in role_audit)
    assert role_counts == {"HEAD": 49, "COMPOUND_HEAD": 34, "LOCATIVE_CONTEXT": 35, "GENITIVE_SOURCE": 15, "QUANTITY_OBJECT": 7}
    assert route_counts == {"LEARNED_WHOLE_OR_UNEXPORTED": 100, "PROVISIONAL_LOCAL_SCOPE": 30, "GDT652_EXACT_O_PREP_SURFACE": 7, "PRODUCTIVE_HEAD": 3}

    rule_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for rule in rule_rows:
        key = (rule["surface"], rule["expected_v63_gloss_de"])
        assert key not in rule_by_key
        rule_by_key[key] = rule

    used_rules: Counter[str] = Counter()
    rendered_tokens: dict[tuple[str, int], str] = {}
    token_out: list[dict[str, object]] = []
    revisions: list[dict[str, object]] = []
    for source in token_rows:
        key = (source["locus"], int(source["token_ordinal"]))
        old = source["v63_main_token_gloss_de"]
        rule = rule_by_key.get((source["surface"], old))
        occurrences = prep_by_key.get(key, [])
        if rule is not None:
            new = rule["v64_main_gloss_de"]
            rule_id = rule["rule_id"]
            decision_class = rule["decision_class"]
            practical_head = rule["practical_head_de"]
            rivals = rule["live_rivals_de"]
            basis = rule["basis"]
            used_rules[rule_id] += 1
        else:
            new = old
            rule_id = "NONE"
            decision_class = "KEEP_V63"
            practical_head = "INHERITED"
            rivals = "NONE"
            basis = "NONE"
        rendered_tokens[key] = new
        changed = int(old != new)
        packed_roles = "|".join(str(row["mention_role"]) for row in occurrences) or "NONE"
        packed_routes = "|".join(str(row["formal_route"]) for row in occurrences) or "NONE"
        token_out.append({
            "page": source["page"], "locus": source["locus"], "token_ordinal": source["token_ordinal"],
            "surface": source["surface"], "v63_token_gloss_de": old, "v64_token_gloss_de": new,
            "v64_changed": changed, "v64_rule_id": rule_id, "decision_class": decision_class,
            "practical_head_de": practical_head, "live_rivals_de": rivals,
            "preparation_span_count": len(occurrences), "preparation_roles": packed_roles,
            "formal_routes": packed_routes, "basis": basis,
        })
        if changed:
            revisions.append(dict(token_out[-1]))

    assert set(used_rules) == {row["rule_id"] for row in rule_rows}
    assert sum(used_rules.values()) == 77
    assert len(revisions) == 77
    assert sum(row["v64_rule_id"] == "P037" for row in revisions) == 1

    token_out_by_key = {(str(row["locus"]), int(str(row["token_ordinal"]))): row for row in token_out}
    for row in role_audit:
        key = (str(row["locus"]), int(str(row["token_ordinal"])))
        token = token_out_by_key[key]
        row["v64_rule_id"] = token["v64_rule_id"]
        if row["mention_role"] == "LOCATIVE_CONTEXT" and token["v64_changed"]:
            row["v64_occurrence_action"] = "EXACT_CONTEXT_RELATION_REWRITE"
        elif row["mention_role"] == "LOCATIVE_CONTEXT":
            row["v64_occurrence_action"] = "KEEP_EXPLICIT_CONTEXT_RELATION"
        elif token["v64_changed"]:
            row["v64_occurrence_action"] = "EXACT_TOKEN_REWRITE"
        else:
            row["v64_occurrence_action"] = "KEEP_CURRENT_WORKING_VALUE"

    line_out: list[dict[str, object]] = []
    output_spans: list[dict[str, object]] = []
    for source_line in line_rows:
        locus = source_line["locus"]
        source_tokens = source_line["zl3b_line"].split()
        glosses = [rendered_tokens[(locus, ordinal)] for ordinal in range(1, len(source_tokens) + 1)]
        text, segments = render(glosses)
        assert len(glosses) == int(source_line["token_count"])
        changed_ordinals = [
            ordinal for ordinal in range(1, len(source_tokens) + 1)
            if token_by_key[(locus, ordinal)]["v63_main_token_gloss_de"] != glosses[ordinal - 1]
        ]
        apparatus: list[str] = []
        for ordinal in changed_ordinals:
            token = token_out_by_key[(locus, ordinal)]
            apparatus.append(
                f"#{ordinal} {token['surface']}: {token['v63_token_gloss_de']} → {token['v64_token_gloss_de']} [{token['v64_rule_id']}]"
            )
        line_out.append({
            "page": source_line["page"], "locus": locus, "section": source_line["section"],
            "language": source_line["language"], "hand": source_line["hand"],
            "token_count": source_line["token_count"], "zl3b_line": source_line["zl3b_line"],
            "v63_main_translation_de": source_line["v63_main_translation_de"],
            "v64_practical_translation_de": text, "v64_changed_token_positions": len(changed_ordinals),
            "v64_changed_ordinals": "|".join(map(str, changed_ordinals)) or "NONE",
            "v64_compact_apparatus_de": " || ".join(apparatus) or "NONE",
            "v64_status": "EXPLICIT_CONTEXT_RELATIONS__PRACTICAL_HEADS_EXACT_ORDINAL",
        })
        for ordinal, (surface, gloss, segment) in enumerate(zip(source_tokens, glosses, segments), 1):
            for start, end, matched, term_class in preparation_terms(gloss):
                line_start = int(segment["start"]) + start
                line_end = int(segment["start"]) + end
                assert text[line_start:line_end].casefold() == matched.casefold()
                output_spans.append({
                    "page": source_line["page"], "locus": locus, "token_ordinal": ordinal,
                    "surface": surface, "token_char_start": start, "token_char_end": end,
                    "line_char_start": line_start, "line_char_end": line_end,
                    "matched_term_de": text[line_start:line_end], "term_class": term_class,
                    "token_gloss_de": gloss,
                })

    assert len(line_out) == 51
    assert sum(int(row["v64_changed_token_positions"]) for row in line_out) == 77
    assert sum(row["v64_practical_translation_de"].count(" im Ansatz") for row in line_out) == 3
    assert not any(" im Trockenansatz" in row["v64_practical_translation_de"] for row in line_out)
    assert not any(row["term_class"] == "BAD" for row in output_spans)

    verb_out: list[dict[str, object]] = []
    for verb in verb_rows:
        key = (verb["locus"], int(verb["source_ordinal"]))
        old_gloss = token_by_key[key]["v63_main_token_gloss_de"]
        new_gloss = rendered_tokens[key]
        matched = verb["matched_text"]
        present_v63 = int(matched.casefold() in old_gloss.casefold())
        present_v64 = int(matched.casefold() in new_gloss.casefold())
        assert present_v63 == present_v64, (key, matched, old_gloss, new_gloss)
        verb_out.append({
            "page": verb["page"], "locus": verb["locus"], "token_ordinal": verb["source_ordinal"],
            "surface": verb["source_surface"], "verb_de": matched, "canonical_lemma": verb["canonical_lemma"],
            "v63_token_gloss_de": old_gloss, "v64_token_gloss_de": new_gloss,
            "action_licensed": verb["action_licensed"], "v63_exact_form_present": present_v63,
            "v64_exact_form_present": present_v64, "preserved_exact_ordinal": 1,
            "gdt691_additional_verb_form_loss": 0,
        })
    assert len(verb_out) == 113 and sum(row["preserved_exact_ordinal"] for row in verb_out) == 113
    assert not any(row["gdt691_additional_verb_form_loss"] for row in verb_out)

    term_comparison: list[dict[str, object]] = []
    v63_glosses = [row["v63_main_token_gloss_de"] for row in token_rows]
    v64_glosses = [rendered_tokens[(row["locus"], int(row["token_ordinal"]))] for row in token_rows]
    for root, label in PREPARATION_ROOTS.items():
        before_occurrences = sum(sum(root in word.casefold() for word in WORD_RE.findall(gloss)) for gloss in v63_glosses)
        after_occurrences = sum(sum(root in word.casefold() for word in WORD_RE.findall(gloss)) for gloss in v64_glosses)
        before_positions = sum(any(root in word.casefold() for word in WORD_RE.findall(gloss)) for gloss in v63_glosses)
        after_positions = sum(any(root in word.casefold() for word in WORD_RE.findall(gloss)) for gloss in v64_glosses)
        term_comparison.append({
            "term_class": label, "root": root, "v63_occurrences": before_occurrences,
            "v64_occurrences": after_occurrences, "delta": after_occurrences - before_occurrences,
            "v63_token_positions": before_positions, "v64_token_positions": after_positions,
        })

    rule_summary: list[dict[str, object]] = []
    for rule in rule_rows:
        rule_summary.append({
            "rule_id": rule["rule_id"], "surface": rule["surface"], "uses": used_rules[rule["rule_id"]],
            "practical_head_de": rule["practical_head_de"], "decision_class": rule["decision_class"],
            "live_rivals_de": rule["live_rivals_de"],
        })
    write_tsv(output_dir / "V63_140_PREPARATION_ROLE_AUDIT.tsv", role_audit)
    write_tsv(output_dir / "V64_479_TOKEN_READER.tsv", token_out)
    write_tsv(output_dir / "V64_77_TOKEN_REVISIONS.tsv", revisions)
    write_tsv(output_dir / "V64_51_LINE_PRACTICAL_READER.tsv", line_out)
    write_tsv(output_dir / "V64_PREPARATION_OUTPUT_SPANS.tsv", output_spans)
    write_tsv(output_dir / "V64_113_VERB_PRESERVATION.tsv", verb_out)
    write_tsv(output_dir / "V63_V64_PREPARATION_TERM_COMPARISON.tsv", term_comparison)
    write_tsv(output_dir / "V64_RULE_USE_SUMMARY.tsv", rule_summary)
    write_tsv(output_dir / "HISTORICAL_PREPARATION_CONTROL.tsv", historical_rows)

    reader_doc = [
        "# GDT691 V64 — praktische Präparationsfassung", "",
        "Präparat-Teilprodukt-Relationen bleiben ausdrücklich sichtbar. Eng gebundene Ganzformen tragen kurze Arbeitswerte; laufende Gradstufen behalten Ansatz, wenn noch kein Produktkopf sichtbar ist.", "",
    ]
    for line in line_out:
        reader_doc.extend([
            f"## {line['locus']}", "", f"`{line['zl3b_line']}`", "",
            str(line["v64_practical_translation_de"]), "",
            f"Apparat: {line['v64_compact_apparatus_de']}", "",
        ])
    (output_dir / "GDT691_V64_PRACTICAL_PREPARATION_READER.md").write_text(
        "\n".join(reader_doc).rstrip() + "\n", encoding="utf-8"
    )

    generated = {
        "GDT691_V64_PRACTICAL_PREPARATION_READER.md", "HISTORICAL_PREPARATION_CONTROL.tsv",
        "V63_140_PREPARATION_ROLE_AUDIT.tsv", "V63_V64_PREPARATION_TERM_COMPARISON.tsv",
        "V64_113_VERB_PRESERVATION.tsv", "V64_479_TOKEN_READER.tsv",
        "V64_51_LINE_PRACTICAL_READER.tsv", "V64_77_TOKEN_REVISIONS.tsv",
        "V64_PREPARATION_OUTPUT_SPANS.tsv", "V64_RULE_USE_SUMMARY.tsv",
    }
    input_paths = [V63_TOKENS, V63_LINES, V63_NOUNS, V63_RESULT, V61_VERBS, G652_O_ATLAS, EXACT_RULES, HISTORICAL_CONTROL, Path(__file__).resolve()]
    term_counts_after = {row["term_class"]: row["v64_occurrences"] for row in term_comparison}
    result = {
        "status": "PASS_V64_140_ROLE_DISPATCH__35_CONTEXT_RELATIONS_PRESERVED__54_EXACT_RULES_77_TOKEN_REVISIONS",
        "basis": {
            "lines": 51, "token_positions": 479, "preparation_spans_v63": 140,
            "preparation_token_positions_v63": 139, "surfaces": 99,
            "pages": len({row["page"] for row in token_rows}), "new_pages": 0,
            "f84_access": 0, "f84r_access": 0,
        },
        "role_dispatch": dict(sorted(role_counts.items())),
        "formal_routes": dict(sorted(route_counts.items())),
        "renderer": {
            "exact_rules": len(rule_rows), "exact_rule_uses": sum(used_rules.values()),
            "locative_relation_rewrites": 32, "locative_relations_retained_verbatim": 3,
            "changed_token_positions": len(revisions),
            "v64_preparation_output_spans": len(output_spans),
            "v64_term_occurrences": term_counts_after,
            "verbs_preserved_exact_ordinal": len(verb_out),
            "bad_main_assignments": term_counts_after["BAD"],
        },
        "main_decisions": {
            "locative_context": "35/35 treated as relations, not independent heads; 32 exact rerenders and 3 explicit original relations",
            "qoteed_oteed": "Auszug",
            "abgezogen_wholes": "qoteed, oteed, keeod, kchod and okeeodar use Auszug; heat alone never creates Absud",
            "qokeod": "retains Auszug; Absud remains rival because cooking is not written",
            "six_sh_preparation_wholes": "Mazerat working main with Einweichung/Feuchtzubereitung rivals",
            "terminal_dry_wholes": "Masse/Trockenmasse or concrete material result; Rückstand remains rival",
            "intermediate_dry_wholes": "Zubereitung",
            "chokol_chain": "sole Absud main: heißer Absud aus Trockengut; dry modifies source, not liquid",
            "ongoing_grade_cells": "retain Ansatz",
            "bad": "historical control only, no main assignment",
        },
        "inherited_debt": v63_result["inherited_debt"],
        "claim_ceiling": "V64 is an exploratory practical renderer over the same 51 lines. Mention roles and exact output ordinals are reproducible; the German heads remain replaceable working values, not recovered plaintext. State words alone do not license Absud, Kaltauszug, Mazerat or Bad. No verb, ordinal, p/s/r/l material head, page, transcription or sealed datum changes.",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "files": {},
    }
    for name in sorted(generated):
        result["files"][name] = sha256(output_dir / name)
    write_json(output_dir / "RESULT.json", result)
    return result


def main() -> int:
    result = build(Path(os.environ.get("GDT691_OUTPUT_DIR", ART)))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
