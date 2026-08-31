#!/usr/bin/env python3
"""Build and select a scoped AR-head renderer over the current V65 deck."""

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
BASE = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament"
SRC = BASE / "src"
ART = BASE / "artifacts"
G692 = ROOT / "experiments/yolo/gdt692_o_q_fraction_sister_compositor"
G688 = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer"
G654 = ROOT / "experiments/yolo/gdt654_ar_or_surface_consolidation"
TOKENS = G692 / "artifacts/V65_479_TOKEN_READER.tsv"
LINES = G692 / "artifacts/V65_51_LINE_COMPOSITIONAL_READER.tsv"
TARGETS = G692 / "artifacts/V64_41_FRACTION_SISTER_OCCURRENCES.tsv"
VERBS = G692 / "artifacts/V65_113_VERB_PRESERVATION.tsv"
G692_RESULT = G692 / "artifacts/RESULT.json"
MODES = G688 / "artifacts/V61_51_LINE_READER.tsv"
PAIR_GRID = G654 / "artifacts/FULL_AR_OR_PAIR_GRID.tsv"
SURFACE_CANDIDATES = SRC / "V66_SURFACE_HEAD_CANDIDATES.tsv"
CONTROL_CANDIDATES = SRC / "V66_AR_OR_CONTROL_CANDIDATES.tsv"
SPAN_CANDIDATES = SRC / "V66_BOUND_SPAN_CANDIDATES.tsv"
TERMINAL_PAIRS = SRC / "V66_R_N_TERMINAL_PAIR_RULES.tsv"
SELECTED_MODEL = SRC / "V66_SELECTED_HEAD_MODEL.tsv"
HEAD_SELECTION = SRC / "V66_HEAD_SELECTION.tsv"
PRODUCT_RIVALS = SRC / "V66_SELECTED_PRODUCT_RIVALS.tsv"
SELECTED_OVERRIDES = SRC / "V66_SELECTED_TOKEN_OVERRIDES.tsv"
CANDIDATES = ("fraction", "share", "stage", "class")
SELECTED = "share"
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


def render(glosses: list[str]) -> str:
    text = ""
    for gloss in glosses:
        if gloss in {";", "."}:
            text = text.rstrip(" ,;.") + gloss
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:] if text else text


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    token_rows = read_tsv(TOKENS)
    line_rows = read_tsv(LINES)
    target_rows = read_tsv(TARGETS)
    verb_rows = read_tsv(VERBS)
    mode_rows = read_tsv(MODES)
    pair_rows = read_tsv(PAIR_GRID)
    surface_rows = read_tsv(SURFACE_CANDIDATES)
    control_rows = read_tsv(CONTROL_CANDIDATES)
    span_rows = read_tsv(SPAN_CANDIDATES)
    terminal_pair_rows = read_tsv(TERMINAL_PAIRS)
    selected_model_rows = read_tsv(SELECTED_MODEL)
    head_selection_rows = read_tsv(HEAD_SELECTION)
    product_rival_rows = read_tsv(PRODUCT_RIVALS)
    selected_override_rows = read_tsv(SELECTED_OVERRIDES)
    g692_result = json.loads(G692_RESULT.read_text(encoding="utf-8"))

    assert len(token_rows) == 479 and len(line_rows) == 51 and len(target_rows) == 41
    assert len(verb_rows) == 113 and len(mode_rows) == 51
    assert len(surface_rows) == 16 and len(control_rows) == 11 and len(span_rows) == 2
    assert len(terminal_pair_rows) == 6
    assert len(selected_model_rows) == 9 and len(head_selection_rows) == 4
    assert len(product_rival_rows) == 6
    assert len(selected_override_rows) == 2
    assert {row["candidate"] for row in head_selection_rows} == set(CANDIDATES)
    assert next(row for row in head_selection_rows if row["decision"] == "SELECTED")["candidate"] == SELECTED
    assert g692_result["basis"]["new_pages"] == 0
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in token_rows)

    surface_by_form = {row["surface"]: row for row in surface_rows}
    control_by_form = {row["surface"]: row for row in control_rows}
    assert len(surface_by_form) == 16 and len(control_by_form) == 11
    target_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in target_rows}
    assert len(target_by_key) == 41
    mode_by_locus = {row["locus"]: row for row in mode_rows}
    assert len(mode_by_locus) == 51

    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in token_rows:
        key = (row["locus"], int(row["token_ordinal"]))
        assert key not in source_by_key
        source_by_key[key] = row
        tokens_by_locus[row["locus"]].append(row)
    for rows in tokens_by_locus.values():
        rows.sort(key=lambda item: int(item["token_ordinal"]))

    candidate_token_values: dict[str, dict[tuple[str, int], str]] = {
        candidate: {} for candidate in CANDIDATES
    }
    token_out: list[dict[str, object]] = []
    target_out: list[dict[str, object]] = []
    control_out: list[dict[str, object]] = []
    control_counts: Counter[str] = Counter()

    for source in token_rows:
        key = (source["locus"], int(source["token_ordinal"]))
        old = source["v65_token_gloss_de"]
        target = target_by_key.get(key)
        control = control_by_form.get(source["surface"])
        if target:
            rule = surface_by_form[source["surface"]]
            assert old == rule["expected_v65_gloss_de"], (key, old, rule["expected_v65_gloss_de"])
            role = "TARGET_41"
            rule_id = rule["rule_id"]
            values = {candidate: rule[f"{candidate}_de"] for candidate in CANDIDATES}
        elif control:
            assert old == control["expected_v65_gloss_de"], (key, old, control["expected_v65_gloss_de"])
            role = f"CONTROL_{control['role']}"
            rule_id = control["rule_id"]
            values = {candidate: control[f"{candidate}_de"] for candidate in CANDIDATES}
            control_counts[source["surface"]] += 1
        else:
            role = "INHERITED"
            rule_id = "NONE"
            values = {candidate: old for candidate in CANDIDATES}
        for candidate, value in values.items():
            candidate_token_values[candidate][key] = value
        out: dict[str, object] = dict(source)
        out.update({"v66_tournament_role": role, "v66_rule_id": rule_id})
        for candidate, value in values.items():
            out[f"v66_{candidate}_de"] = value
            out[f"v66_{candidate}_changed"] = int(value != old)
        token_out.append(out)
        if target:
            row_out: dict[str, object] = {
                "page": source["page"], "locus": source["locus"],
                "token_ordinal": source["token_ordinal"], "surface": source["surface"],
                "line_mode": mode_by_locus[source["locus"]]["line_mode"],
                "reader_mode": mode_by_locus[source["locus"]]["v61_reader_mode"],
                "rule_id": rule_id, "construction": rule["construction"],
                "ar_level": rule["ar_level"], "v65_fraction_de": old,
            }
            row_out.update({f"{candidate}_de": value for candidate, value in values.items()})
            target_out.append(row_out)
        elif control:
            row_out = {
                "page": source["page"], "locus": source["locus"],
                "token_ordinal": source["token_ordinal"], "surface": source["surface"],
                "line_mode": mode_by_locus[source["locus"]]["line_mode"],
                "reader_mode": mode_by_locus[source["locus"]]["v61_reader_mode"],
                "rule_id": rule_id, "role": control["role"],
                "ar_level": control["ar_level"], "v65_gloss_de": old,
            }
            row_out.update({f"{candidate}_de": value for candidate, value in values.items()})
            control_out.append(row_out)

    assert len(target_out) == 41 and len(control_out) == 22
    assert control_counts == {
        "or": 5, "kor": 1, "lor": 1, "tar": 2, "sar": 1, "sair": 1,
        "dar": 5, "dair": 3, "qodor": 1, "aror": 1, "oroiir": 1,
    }
    assert Counter(row["line_mode"] for row in target_out) == {
        "MIXED_RECORD": 18, "NOMINAL_REGISTER": 12,
        "ACTION_SEQUENCE": 10, "QUANTITY_LABEL": 1,
    }

    span_by_locus: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    covered: set[tuple[str, int]] = set()
    for span in span_rows:
        locus = span["locus"]
        start = int(span["start_ordinal"])
        end = int(span["end_ordinal"])
        actual = "|".join(row["surface"] for row in tokens_by_locus[locus][start - 1:end])
        assert actual == span["surfaces"]
        assert start not in span_by_locus[locus]
        for ordinal in range(start, end + 1):
            assert (locus, ordinal) not in covered
            covered.add((locus, ordinal))
        span_by_locus[locus][start] = span

    line_by_locus = {row["locus"]: row for row in line_rows}
    assert len(line_by_locus) == 51 and set(line_by_locus) == set(tokens_by_locus)
    line_out: list[dict[str, object]] = []
    for locus, source_line in line_by_locus.items():
        locus_tokens = tokens_by_locus[locus]
        out: dict[str, object] = dict(source_line)
        out.update({
            "v66_line_mode": mode_by_locus[locus]["line_mode"],
            "v66_reader_mode": mode_by_locus[locus]["v61_reader_mode"],
        })
        for candidate in CANDIDATES:
            units: list[str] = []
            ordinal = 1
            while ordinal <= len(locus_tokens):
                span = span_by_locus[locus].get(ordinal)
                if span:
                    units.append(span[f"{candidate}_de"])
                    ordinal = int(span["end_ordinal"]) + 1
                else:
                    units.append(candidate_token_values[candidate][(locus, ordinal)])
                    ordinal += 1
            candidate_text = render(units)
            out[f"v66_{candidate}_translation_de"] = candidate_text
            out[f"v66_{candidate}_word_count"] = len(words(candidate_text))
            out[f"v66_{candidate}_char_count"] = len(candidate_text)
        assert out["v66_fraction_translation_de"] == source_line["v65_compositional_translation_de"], locus
        line_out.append(out)

    verb_out: list[dict[str, object]] = []
    for verb in verb_rows:
        key = (verb["locus"], int(verb["token_ordinal"]))
        matched = verb["verb_de"]
        out: dict[str, object] = dict(verb)
        for candidate in CANDIDATES:
            value = candidate_token_values[candidate][key]
            present = int(matched.casefold() in value.casefold())
            assert present == int(verb["v65_exact_form_present"]), (candidate, key, matched, value)
            out[f"v66_{candidate}_exact_form_present"] = present
        verb_out.append(out)
    assert len(verb_out) == 113

    census: list[dict[str, object]] = []
    for candidate in CANDIDATES:
        changed = sum(int(row[f"v66_{candidate}_changed"]) for row in token_out)
        target_changed = sum(candidate_token_values[candidate][(row["locus"], int(row["token_ordinal"]))] != row["v65_fraction_de"] for row in target_out)
        control_changed = sum(candidate_token_values[candidate][(row["locus"], int(row["token_ordinal"]))] != row["v65_gloss_de"] for row in control_out)
        all_text = " ".join(candidate_token_values[candidate].values())
        lower_words = [word.casefold() for word in words(all_text)]
        census.append({
            "candidate": candidate,
            "changed_token_positions": changed,
            "target_changes": target_changed,
            "control_changes": control_changed,
            "line_words": sum(int(row[f"v66_{candidate}_word_count"]) for row in line_out),
            "line_characters": sum(int(row[f"v66_{candidate}_char_count"]) for row in line_out),
            "fraktion_word_occurrences": sum("fraktion" in word for word in lower_words),
            "anteil_word_occurrences": sum("anteil" in word for word in lower_words),
            "stufe_word_occurrences": sum("stufe" in word for word in lower_words),
            "klasse_word_occurrences": sum("klasse" in word for word in lower_words),
            "portion_word_occurrences": sum("portion" in word for word in lower_words),
        })
    assert {row["candidate"] for row in census} == set(CANDIDATES)
    assert next(row for row in census if row["candidate"] == "fraction")["changed_token_positions"] == 0

    selected_override_by_key = {
        (row["locus"], int(row["token_ordinal"])): row for row in selected_override_rows
    }
    assert len(selected_override_by_key) == 2
    selected_value_by_key = dict(candidate_token_values[SELECTED])
    for key, override in selected_override_by_key.items():
        source = source_by_key[key]
        assert source["surface"] == override["surface"]
        assert selected_value_by_key[key] == override["expected_share_de"]
        selected_value_by_key[key] = override["selected_de"]

    prior_rows = [
        row for row in pair_rows
        if row["shell"] in {"BARE", "O", "QO"} and row["qualifier"] in {"UNQUALIFIED", "K", "T"}
    ]
    assert len(prior_rows) == 9
    prior_out = [{
        **row,
        "pair_occurrences": int(row["ar_occurrences"]) + int(row["or_occurrences"]),
        "pair_reader_exact": int(row["ar_reader_exact"]) + int(row["or_reader_exact"]),
        "v66_interpretive_use": "AR_HEAD_VERSUS_OR_PORTION_PRIOR__NO_NEW_PAGE_RENDERING",
    } for row in prior_rows]

    terminal_pair_out: list[dict[str, object]] = []
    for pair in terminal_pair_rows:
        for terminal, role_column in (("r", "r_role"), ("n", "n_role")):
            surface = pair[f"{terminal}_surface"]
            occurrences = [row for row in token_rows if row["surface"] == surface]
            expected = int(pair[f"expected_{terminal}_count"])
            assert len(occurrences) == expected, (pair["pair_id"], surface, len(occurrences), expected)
            for row in occurrences:
                key = (row["locus"], int(row["token_ordinal"]))
                terminal_pair_out.append({
                    "pair_id": pair["pair_id"], "left_body": pair["left_body"],
                    "terminal": terminal.upper(), "surface": surface,
                    "page": row["page"], "locus": row["locus"],
                    "token_ordinal": row["token_ordinal"],
                    "v65_gloss_de": row["v65_token_gloss_de"],
                    "v66_selected_gloss_de": selected_value_by_key[key],
                    "typed_role": pair[role_column],
                    "v66_selected_terminal_semantics": (
                        "R_INDEXED_MATERIAL_SHARE_SELECTOR" if terminal == "r"
                        else "N_HEAD_TYPED_GRADE_AMOUNT_OR_BATCH_VALUE"
                    ),
                    "interpretive_contrast": pair["interpretive_contrast"],
                })
    assert len(terminal_pair_out) == 30

    selected_token_out: list[dict[str, object]] = []
    selected_revision_out: list[dict[str, object]] = []
    selected_revisions_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in token_out:
        key = (str(row["locus"]), int(row["token_ordinal"]))
        override = selected_override_by_key.get(key)
        selected_gloss = selected_value_by_key[key]
        changed = int(selected_gloss != row["v65_token_gloss_de"])
        tournament_role = str(row["v66_tournament_role"])
        if override:
            semantic_role = override["semantic_role"]
        elif tournament_role == "TARGET_41" or tournament_role == "CONTROL_AR_HEAD":
            semantic_role = "R_INDEXED_MATERIAL_SHARE_SELECTOR"
        elif tournament_role in {"CONTROL_AR_PLUS_OR", "CONTROL_OR_PLUS_AR"}:
            semantic_role = "R_SHARE_SELECTOR_PLUS_OR_PORTION"
        elif tournament_role.startswith("CONTROL_OR_"):
            semantic_role = "OR_INDEPENDENT_PORTION"
        else:
            semantic_role = "INHERITED_OUTSIDE_GDT693_HEAD_SCOPE"
        selected_row = dict(row)
        selected_row.update({
            "v66_selected_candidate": SELECTED,
            "v66_selected_gloss_de": selected_gloss,
            "v66_selected_changed": changed,
            "v66_selected_semantic_role": semantic_role,
            "v66_selected_override_id": override["override_id"] if override else "NONE",
        })
        selected_token_out.append(selected_row)
        if changed:
            assert override or tournament_role == "TARGET_41" or "AR" in tournament_role
            if override:
                revision_class = override["revision_class"]
                selected_rule_id = override["override_id"]
            else:
                revision_class = (
                    "TARGET_HEAD" if tournament_role == "TARGET_41" else "AR_CONTROL_HEAD"
                )
                selected_rule_id = row["v66_rule_id"]
            revision = {
                "page": row["page"], "locus": row["locus"],
                "token_ordinal": row["token_ordinal"], "surface": row["surface"],
                "revision_class": revision_class,
                "v66_rule_id": selected_rule_id,
                "v65_fraction_de": row["v65_token_gloss_de"],
                "v66_selected_share_de": selected_gloss,
                "v66_selected_semantic_role": semantic_role,
            }
            selected_revision_out.append(revision)
            selected_revisions_by_locus[str(row["locus"])].append(revision)

    assert len(selected_token_out) == 479 and len(selected_revision_out) == 57
    assert Counter(row["revision_class"] for row in selected_revision_out) == {
        "TARGET_HEAD": 41, "AR_CONTROL_HEAD": 14,
        "NEUTRAL_GRAMMAR": 1, "BOUND_RIGHT_HEAD_CARRY_TOKEN": 1,
    }
    ar_control_out = [row for row in control_out if "AR" in row["role"]]
    or_control_out = [row for row in control_out if "OR" in row["role"]]
    assert len(ar_control_out) == 14 and len(or_control_out) == 10
    assert all(row[f"{SELECTED}_de"] != row["v65_gloss_de"] for row in ar_control_out)
    assert all(
        "portion" in selected_value_by_key[(row["locus"], int(row["token_ordinal"]))].casefold()
        for row in or_control_out
    )

    residual_fraction_out: list[dict[str, object]] = []
    for row in selected_token_out:
        if "fraktion" not in str(row["v66_selected_gloss_de"]).casefold():
            continue
        residual_fraction_out.append({
            "page": row["page"], "locus": row["locus"],
            "token_ordinal": row["token_ordinal"], "surface": row["surface"],
            "v66_selected_gloss_de": row["v66_selected_gloss_de"],
            "v65_composition": row["v65_composition"],
            "v65_family": row["v65_family"],
            "v65_basis": row["v65_basis"],
            "v66_scope_status": row["v66_selected_semantic_role"],
            "next_question": "MIGRATE_AS_COMPOSED_R_SHARE_OR_RETAIN_AS_INDEPENDENT_LEARNED_WHOLE",
        })
    assert len(residual_fraction_out) == 22
    assert len({row["surface"] for row in residual_fraction_out}) == 22

    selected_span_out: list[dict[str, object]] = []
    for span in span_rows:
        selected_span_out.append({
            **span,
            "selected_candidate": SELECTED,
            "selected_gloss_de": span[f"{SELECTED}_de"],
            "selected_semantics": "R_INDEXED_MATERIAL_SHARE_WITH_BOUND_QUANTITY",
        })
    assert len(selected_span_out) == 2

    selected_rival_out: list[dict[str, object]] = []
    selected_rivals_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for rival in product_rival_rows:
        locus = rival["locus"]
        start = int(rival["start_ordinal"])
        end = int(rival["end_ordinal"])
        if start == end:
            selected_main = candidate_token_values[SELECTED][(locus, start)]
        else:
            span = span_by_locus[locus][start]
            assert int(span["end_ordinal"]) == end
            selected_main = span[f"{SELECTED}_de"]
        assert selected_main == rival["selected_main_span_de"], (rival["rival_id"], selected_main)
        out = {
            **rival,
            "selected_candidate": SELECTED,
            "main_span_exact": 1,
            "semantic_scope": "LOCAL_REFERENT_RIVAL_ONLY__R_REMAINS_INDEXED_MATERIAL_SHARE",
        }
        selected_rival_out.append(out)
        selected_rivals_by_locus[locus].append(out)
    assert len(selected_rival_out) == 6

    selected_line_out: list[dict[str, object]] = []
    for row in line_out:
        locus = str(row["locus"])
        revisions = sorted(
            selected_revisions_by_locus.get(locus, []),
            key=lambda item: int(item["token_ordinal"]),
        )
        apparatus = [
            f"#{item['token_ordinal']} {item['surface']}: "
            f"{item['v65_fraction_de']} → {item['v66_selected_share_de']} "
            f"[{item['v66_rule_id']}]"
            for item in revisions
        ]
        for span in span_rows:
            if span["locus"] == locus:
                apparatus.append(
                    f"#{span['start_ordinal']}–{span['end_ordinal']} {span['surfaces']}: "
                    f"gebunden → {span[f'{SELECTED}_de']} [{span['span_id']}]"
                )
        rivals = selected_rivals_by_locus.get(locus, [])
        selected_units: list[str] = []
        locus_tokens = tokens_by_locus[locus]
        ordinal = 1
        while ordinal <= len(locus_tokens):
            span = span_by_locus[locus].get(ordinal)
            if span:
                selected_units.append(span[f"{SELECTED}_de"])
                ordinal = int(span["end_ordinal"]) + 1
            else:
                selected_units.append(selected_value_by_key[(locus, ordinal)])
                ordinal += 1
        selected_translation = render(selected_units)
        selected_line_out.append({
            "page": row["page"], "locus": locus, "section": row["section"],
            "language": row["language"], "hand": row["hand"],
            "token_count": row["token_count"], "zl3b_line": row["zl3b_line"],
            "v66_line_mode": row["v66_line_mode"],
            "v66_reader_mode": row["v66_reader_mode"],
            "v65_compositional_translation_de": row["v65_compositional_translation_de"],
            "v66_selected_candidate": SELECTED,
            "v66_selected_translation_de": selected_translation,
            "v66_selected_changed_token_positions": len(revisions),
            "v66_selected_changed_ordinals": (
                "|".join(str(item["token_ordinal"]) for item in revisions) if revisions else "NONE"
            ),
            "v66_selected_compact_apparatus_de": " || ".join(apparatus) if apparatus else "NONE",
            "v66_local_product_rivals_de": (
                " || ".join(
                    f"{item['rival_id']}: {item['local_product_rival_de']}" for item in rivals
                ) if rivals else "NONE"
            ),
            "v66_status": "SCOPED_INDEXED_MATERIAL_SHARE_RENDERER__NO_LOCAL_R_REDEFINITION",
        })
    assert len(selected_line_out) == 51
    assert sum(int(row["v66_selected_changed_token_positions"]) for row in selected_line_out) == 57
    selected_changed_lines = sum(
        row["v66_selected_translation_de"] != row["v65_compositional_translation_de"]
        for row in selected_line_out
    )

    selected_verb_out: list[dict[str, object]] = []
    for row in verb_out:
        key = (row["locus"], int(row["token_ordinal"]))
        selected_verb_out.append({
            **row,
            "v66_selected_candidate": SELECTED,
            "v66_selected_gloss_de": selected_value_by_key[key],
            "v66_selected_exact_form_present": row[f"v66_{SELECTED}_exact_form_present"],
        })
    assert len(selected_verb_out) == 113
    assert all(
        int(row["v66_selected_exact_form_present"]) == int(row["v65_exact_form_present"])
        for row in selected_verb_out
    )

    selected_surface_out = [{
        **row,
        "selected_candidate": SELECTED,
        "selected_gloss_de": row[f"{SELECTED}_de"],
        "selected_formal_role": "R_INDEXED_MATERIAL_SHARE_SELECTOR",
    } for row in surface_rows]
    assert len(selected_surface_out) == 16

    write_tsv(output_dir / "V66_41_TARGET_FOUR_HEAD_RENDERERS.tsv", target_out)
    write_tsv(output_dir / "V66_22_AR_OR_CONTROL_OCCURRENCES.tsv", control_out)
    write_tsv(output_dir / "V66_479_TOKEN_FOUR_HEAD_RENDERERS.tsv", token_out)
    write_tsv(output_dir / "V66_51_LINE_FOUR_HEAD_READERS.tsv", line_out)
    write_tsv(output_dir / "V66_113_VERB_FOUR_HEAD_PRESERVATION.tsv", verb_out)
    write_tsv(output_dir / "V66_FOUR_HEAD_CENSUS.tsv", census)
    write_tsv(output_dir / "V66_GDT654_NINE_AR_OR_PAIR_PRIORS.tsv", prior_out)
    write_tsv(output_dir / "V66_30_R_N_TERMINAL_PAIR_OCCURRENCES.tsv", terminal_pair_out)
    write_tsv(output_dir / "V66_479_TOKEN_SELECTED_SHARE_READER.tsv", selected_token_out)
    write_tsv(output_dir / "V66_57_SELECTED_REVISIONS.tsv", selected_revision_out)
    write_tsv(output_dir / "V66_51_LINE_SELECTED_SHARE_READER.tsv", selected_line_out)
    write_tsv(output_dir / "V66_2_SELECTED_BOUND_SPANS.tsv", selected_span_out)
    write_tsv(output_dir / "V66_6_SELECTED_PRODUCT_RIVALS.tsv", selected_rival_out)
    write_tsv(output_dir / "V66_16_SELECTED_SURFACE_RULES.tsv", selected_surface_out)
    write_tsv(output_dir / "V66_9_SELECTED_HEAD_MODEL.tsv", selected_model_rows)
    write_tsv(output_dir / "V66_4_HEAD_SELECTION.tsv", head_selection_rows)
    write_tsv(output_dir / "V66_113_SELECTED_VERB_PRESERVATION.tsv", selected_verb_out)
    write_tsv(output_dir / "V66_22_RESIDUAL_FRACTION_BEARING_OCCURRENCES.tsv", residual_fraction_out)

    reader = [
        "# GDT693 V66 — vier vollständige AR-Kopf-Renderer", "",
        "Jede Fassung vergleicht dieselben 41 Zielstellen und 22 AR/OR-Kontrollen. Vierzehn Kontrollen tragen AR, zehn tragen OR; zwei Komposita tragen beide. Reine OR-Portionen bleiben unverändert. Keine Fassung öffnet eine neue Seite.", "",
    ]
    for row in line_out:
        reader.extend([
            f"## {row['locus']} — {row['v66_line_mode']}", "",
            f"`{row['zl3b_line']}`", "",
            f"Fraktion: {row['v66_fraction_translation_de']}", "",
            f"Anteil: {row['v66_share_translation_de']}", "",
            f"Stufe: {row['v66_stage_translation_de']}", "",
            f"Klasse: {row['v66_class_translation_de']}", "",
        ])
    (output_dir / "GDT693_V66_FOUR_HEAD_READER.md").write_text("\n".join(reader).rstrip() + "\n", encoding="utf-8")

    selected_reader = [
        "# GDT693 V66 — ausgewählter Anteil-Renderer", "",
        "Arbeitsregel: A plus Minims liefert den Index; R typisiert ihn als ausgewählten Stoffanteil, N als headabhängigen Grad-, Mengen- oder Chargenwert. OR bleibt eine eigenständige Portion. Die Auswahl ändert 41 Zielstellen und 14 AR-Kontrollen; zehn OR-tragende Kontrollen behalten ausdrücklich die Portion. Zusätzlich korrigiert V66 einen deutschen Genitiv und einen tokenisolierten Mengen-Carry. Der Renderer gilt für diesen 63-Stellen-Kopfbereich und migriert noch nicht jede geerbte Fraktionsform des 479-Token-Decks.", "",
    ]
    for row in selected_line_out:
        selected_reader.extend([
            f"## {row['locus']} — {row['v66_line_mode']}", "",
            f"`{row['zl3b_line']}`", "",
            str(row["v66_selected_translation_de"]), "",
            f"Änderungen: {row['v66_selected_compact_apparatus_de']}", "",
            f"Lokaler Produktrivale: {row['v66_local_product_rivals_de']}", "",
        ])
    (output_dir / "GDT693_V66_SELECTED_SHARE_READER.md").write_text(
        "\n".join(selected_reader).rstrip() + "\n", encoding="utf-8"
    )

    generated = {
        "GDT693_V66_FOUR_HEAD_READER.md",
        "V66_41_TARGET_FOUR_HEAD_RENDERERS.tsv",
        "V66_22_AR_OR_CONTROL_OCCURRENCES.tsv",
        "V66_479_TOKEN_FOUR_HEAD_RENDERERS.tsv",
        "V66_51_LINE_FOUR_HEAD_READERS.tsv",
        "V66_113_VERB_FOUR_HEAD_PRESERVATION.tsv",
        "V66_FOUR_HEAD_CENSUS.tsv",
        "V66_GDT654_NINE_AR_OR_PAIR_PRIORS.tsv",
        "V66_30_R_N_TERMINAL_PAIR_OCCURRENCES.tsv",
        "GDT693_V66_SELECTED_SHARE_READER.md",
        "V66_479_TOKEN_SELECTED_SHARE_READER.tsv",
        "V66_57_SELECTED_REVISIONS.tsv",
        "V66_51_LINE_SELECTED_SHARE_READER.tsv",
        "V66_2_SELECTED_BOUND_SPANS.tsv",
        "V66_6_SELECTED_PRODUCT_RIVALS.tsv",
        "V66_16_SELECTED_SURFACE_RULES.tsv",
        "V66_9_SELECTED_HEAD_MODEL.tsv",
        "V66_4_HEAD_SELECTION.tsv",
        "V66_113_SELECTED_VERB_PRESERVATION.tsv",
        "V66_22_RESIDUAL_FRACTION_BEARING_OCCURRENCES.tsv",
    }
    input_paths = [
        TOKENS, LINES, TARGETS, VERBS, G692_RESULT, MODES, PAIR_GRID,
        SURFACE_CANDIDATES, CONTROL_CANDIDATES, SPAN_CANDIDATES, TERMINAL_PAIRS,
        SELECTED_MODEL, HEAD_SELECTION, PRODUCT_RIVALS, SELECTED_OVERRIDES,
        Path(__file__).resolve(),
    ]
    result = {
        "status": "PASS_V66_SCOPED_INDEXED_R_SELECTOR__55_HEAD_PLUS_2_READER_REVISIONS__6_R_N_PAIRS__OR_PORTION_PRESERVED",
        "basis": {
            "lines": 51, "token_positions": 479, "pages": 36,
            "target_occurrences": 41, "control_occurrences": 22,
            "ar_bearing_control_occurrences": 14, "or_bearing_control_occurrences": 10,
            "selected_revisions": len(selected_revision_out),
            "selected_head_revisions": 55,
            "selected_reader_repairs": 2,
            "selected_changed_lines": selected_changed_lines,
            "bound_spans": 2, "product_rivals": len(selected_rival_out),
            "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
        "candidates": list(CANDIDATES),
        "selected": {
            "candidate": SELECTED,
            "running_head_de": "Anteil",
            "abstract_r_value_de": "ausgewählter indexierter Stoffanteil",
            "index_rule": "A+I^(level-1)",
            "r_rule": "INDEX+R -> selected material share",
            "n_rule": "INDEX+N -> head-typed grade, amount or batch value",
            "or_rule": "OR -> independently portioned amount; never O+R",
            "scope": "41 target positions plus 22 AR/OR controls in the current 51-line deck",
            "unmigrated_inherited_fraction_positions": len(residual_fraction_out),
            "unmigrated_inherited_fraction_word_occurrences": len(residual_fraction_out),
            "candidate_share_before_reader_repairs_fraction_word_occurrences": next(
                row for row in census if row["candidate"] == SELECTED
            )["fraktion_word_occurrences"],
        },
        "selection_decisions": {row["candidate"]: row["decision"] for row in head_selection_rows},
        "line_modes_at_targets": dict(Counter(row["line_mode"] for row in target_out)),
        "gdt654_prior": {
            "pair_cells": len(prior_out),
            "occurrences": sum(int(row["pair_occurrences"]) for row in prior_out),
            "reader_exact": sum(int(row["pair_reader_exact"]) for row in prior_out),
            "scope": "inherited aggregate evidence only; no global-page renderer opened",
        },
        "r_n_terminal_evidence": {
            "minimal_pairs": 6, "current_occurrences": len(terminal_pair_out),
            "interpretation": "A plus repeated-I index is typed by R as material selector and by N as head-dependent value",
        },
        "selected_changes": {
            "total": len(selected_revision_out), "head_total": 55,
            "targets": 41, "ar_controls": 14,
            "neutral_grammar_repairs": 1, "bound_carry_token_repairs": 1,
            "or_bearing_controls_preserving_portion": len(or_control_out),
            "bound_spans": len(selected_span_out),
            "local_product_rivals": len(selected_rival_out),
        },
        "candidate_census": {row["candidate"]: row for row in census},
        "verbs": {
            "ordinals": len(verb_out), "all_four_exact_profiles_preserved": 1,
            "selected_exact_profile_preserved": 1,
        },
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "files": {name: sha256(output_dir / name) for name in sorted(generated)},
        "next_gap": "The selected R head is coherent across the 41 targets and 22 controls, but 22 inherited fraction-bearing token positions outside that scoped migration remain to be decomposed or migrated before calling the 479-token reader globally uniform.",
        "claim_ceiling": "V66 selects one scoped German working semantics for the admitted R-selector family: indexed material share. It is a concrete compositional renderer over 63 target/control positions, not recovered plaintext or a claim of distillation. Local extract readings change only the referent. The remaining inherited fraction-bearing forms are explicitly not yet globally normalized.",
    }
    return result


def main() -> int:
    result = build(ART)
    write_json(ART / "RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
