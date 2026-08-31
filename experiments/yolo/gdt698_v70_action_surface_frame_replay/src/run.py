#!/usr/bin/env python3
"""Replay the nine V70 target frames over every exact action-surface occurrence."""

from __future__ import annotations

import csv
import hashlib
import json
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
EXP = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay"
SRC = EXP / "src"
ART = EXP / "artifacts"
G697 = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords"
G697_ART = G697 / "artifacts"

SPECS = SRC / "V71_EXACT_TARGET_FRAME_TEMPLATES.tsv"
MICROS = G697_ART / "V70_7_EXACT_MICRORECORDS.tsv"
EDGES = G697_ART / "V70_9_EDGE_WINDOW_COVERAGE.tsv"
TOKENS = G697_ART / "V70_479_TOKEN_FREEZE.tsv"
LINES = G697_ART / "V70_51_LINE_MICRORECORD_OVERLAY.tsv"
SPANS = G697_ART / "V70_3_BOUND_SPAN_FREEZE.tsv"
G697_RESULT = G697_ART / "RESULT.json"

TEMPLATES_OUT = ART / "V71_9_EXACT_TARGET_FRAME_TEMPLATES.tsv"
OCCURRENCES_OUT = ART / "V71_10_ACTION_SURFACE_OCCURRENCES.tsv"
CONTRASTS_OUT = ART / "V71_3_UNBOUND_QOL_TEMPLATE_CONTRASTS.tsv"
SURFACE_CENSUS_OUT = ART / "V71_6_ACTION_SURFACE_CENSUS.tsv"
TOKENS_OUT = ART / "V71_479_TOKEN_FREEZE.tsv"
LINES_OUT = ART / "V71_51_LINE_FREEZE.tsv"
SPANS_OUT = ART / "V71_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT698_V71_ACTION_SURFACE_FRAME_REPLAY_READER.md"
ARTIFACT_README = ART / "README.md"
RESULT_OUT = ART / "RESULT.json"

STATUS = (
    "PASS_V71_6_SURFACES_10_OCCURRENCES__9_EXISTING_MATCHES_1_UNBOUND_HELD__"
    "0_CROSS_REPLAYS__ZERO_WORD_DELTA"
)
CLAIM_CEILING = (
    "V71 exhausts the exact occurrences of the six action surfaces used by V70 "
    "and replays only nine already observed contiguous participant frames. All "
    "nine matches are self-source matches; the sole unbound qol remains held. "
    "No relation, microrecord, word meaning, or page is added."
)

TEMPLATE_FIELDS = [
    "template_id", "source_edge_id", "microrecord_id", "action_surface",
    "target_offset", "window_surfaces", "window_glosses_de", "window_role_trace",
    "participant_frame_de", "topology", "replay_gate", "forbidden_shortcut",
    "source_locus", "source_target_ordinal", "window_start_ordinal",
    "window_end_ordinal", "window_length", "observed_surfaces",
    "observed_glosses_de", "observed_role_trace", "source_match_exact",
    "total_exact_hits", "self_source_hits", "cross_occurrence_hits", "status",
]
OCCURRENCE_FIELDS = [
    "occurrence_id", "page", "locus", "token_ordinal", "action_surface",
    "v70_token_gloss_de", "v68_clause_id", "v68_clause_type",
    "eligible_template_ids", "exact_match_template_ids", "exact_match_edge_ids",
    "inherited_target_edge_ids", "already_bound", "unbound_candidate",
    "context_start_ordinal", "context_end_ordinal", "context_surfaces",
    "context_glosses_de", "context_roles", "decision", "new_edge_count",
    "new_microrecord_count", "note",
]
CONTRAST_FIELDS = [
    "candidate_locus", "candidate_ordinal", "candidate_surface", "template_id",
    "source_edge_id", "expected_window_surfaces", "observed_aligned_surfaces",
    "expected_participant_frame_de", "observed_aligned_roles", "mismatch_offsets",
    "mismatch_count", "surface_frame_exact", "decision", "reason_de",
]
SURFACE_FIELDS = [
    "action_surface", "occurrence_count", "already_bound_count", "unbound_count",
    "template_count", "exact_template_hits", "self_source_hits",
    "cross_occurrence_hits", "new_candidate_hits", "participant_frame_multiplicity",
    "frame_determinacy", "decision",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tsv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.reader(handle, delimiter="\t"))
    require(bool(raw), f"empty TSV: {path}")
    fields = raw[0]
    require(len(set(fields)) == len(fields), f"duplicate TSV header: {path}")
    for number, row in enumerate(raw[1:], 2):
        require(len(row) == len(fields), f"TSV width mismatch {path}:{number}")
    return [dict(zip(fields, row)) for row in raw[1:]], fields


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [] if not value or value == "NONE" else value.split("|")


def split_double(value: str) -> list[str]:
    return [] if not value or value == "NONE" else value.split(" || ")


def pipe(values: list[object]) -> str:
    return "NONE" if not values else "|".join(str(value) for value in values)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def md(value: str) -> str:
    return value.replace("|", "<br>").replace("\n", " ")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs, _ = read_tsv(SPECS)
    micros, _ = read_tsv(MICROS)
    edges, _ = read_tsv(EDGES)
    tokens, token_fields = read_tsv(TOKENS)
    lines, line_fields = read_tsv(LINES)
    spans, span_fields = read_tsv(SPANS)
    base_result = json.loads(G697_RESULT.read_text(encoding="utf-8"))

    require(base_result["status"].startswith("PASS_V70_"), "GDT697 is not a passing V70 base")
    require(len(specs) == 9 and [row["template_id"] for row in specs] == [f"T{i:03d}" for i in range(1, 10)], "template deck changed")
    require(len(micros) == 7 and len(edges) == 9, "V70 window/edge deck changed")
    require(len(tokens) == 479 and len(lines) == 51 and len(spans) == 3, "V70 freeze size changed")
    require(not any(row["locus"].lower().startswith("f84") for row in tokens), "f84/f84r entered scope")
    require(all(row["v70_word_delta"] == "0" for row in tokens + lines), "V70 word delta changed")
    require(all(row["v70_byte_identical"] == "1" for row in spans), "V70 span freeze changed")

    edge_by_id = {row["edge_id"]: row for row in edges}
    micro_by_id = {row["microrecord_id"]: row for row in micros}
    token_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in tokens}
    line_by_locus = {row["locus"]: row for row in lines}
    require(len(edge_by_id) == 9 and len(token_by_key) == 479 and len(line_by_locus) == 51, "duplicate V70 key")
    require({row["source_edge_id"] for row in specs} == set(edge_by_id), "templates do not cover C001-C009")
    require(len({row["source_edge_id"] for row in specs}) == 9, "duplicate source edge template")

    template_work: list[dict[str, object]] = []
    template_by_id: dict[str, dict[str, object]] = {}
    for spec in specs:
        edge = edge_by_id[spec["source_edge_id"]]
        require(edge["microrecord_id"] == spec["microrecord_id"], f"microrecord join changed {spec['template_id']}")
        require(edge["topology"] == spec["topology"], f"topology join changed {spec['template_id']}")
        target = int(edge["target_action_ordinal"])
        nodes = [int(value) for value in split_pipe(edge["node_ordinals"])]
        start = min(nodes)
        offset = int(spec["target_offset"])
        require(target - start == offset, f"target offset changed {spec['template_id']}")
        locus = edge["locus"]
        observed = [token_by_key[(locus, ordinal)] for ordinal in range(start, target + 1)]
        observed_surfaces = [row["surface"] for row in observed]
        observed_glosses = [row["v70_token_gloss_de"] for row in observed]
        observed_roles = [row["v69_relation_roles"] for row in observed]
        require(observed_surfaces == split_pipe(spec["window_surfaces"]), f"source surfaces changed {spec['template_id']}")
        require(observed_glosses == split_double(spec["window_glosses_de"]), f"source glosses changed {spec['template_id']}")
        require(observed_roles == split_double(spec["window_role_trace"]), f"source roles changed {spec['template_id']}")
        require(observed[-1]["surface"] == spec["action_surface"], f"target surface changed {spec['template_id']}")
        row: dict[str, object] = dict(spec)
        row.update({
            "source_locus": locus,
            "source_target_ordinal": target,
            "window_start_ordinal": start,
            "window_end_ordinal": target,
            "window_length": len(observed),
            "observed_surfaces": pipe(observed_surfaces),
            "observed_glosses_de": " || ".join(observed_glosses),
            "observed_role_trace": " || ".join(observed_roles),
            "source_match_exact": 1,
        })
        template_work.append(row)
        template_by_id[spec["template_id"]] = row

    action_surfaces = {str(row["action_surface"]) for row in template_work}
    require(action_surfaces == {"qokamdy", "ykaiin", "yteeeor", "qey", "qol", "qodar"}, "action surface set changed")
    action_tokens = [row for row in tokens if row["surface"] in action_surfaces]
    require(len(action_tokens) == 10, f"expected ten exact action-surface occurrences, got {len(action_tokens)}")
    require(all(row["v68_clause_type"] == "ACTION_CLAUSE" for row in action_tokens), "an action surface escaped its action clause")
    require(Counter(row["surface"] for row in action_tokens) == Counter({
        "qokamdy": 1, "ykaiin": 2, "yteeeor": 1, "qey": 1, "qol": 4, "qodar": 1,
    }), "action surface occurrence census changed")

    occurrence_rows: list[dict[str, object]] = []
    template_hits: Counter[str] = Counter()
    template_self_hits: Counter[str] = Counter()
    template_cross_hits: Counter[str] = Counter()
    occurrence_by_key: dict[tuple[str, int], dict[str, object]] = {}
    for index, token in enumerate(action_tokens, 1):
        locus = token["locus"]
        ordinal = int(token["token_ordinal"])
        eligible = [row for row in template_work if row["action_surface"] == token["surface"]]
        matches: list[dict[str, object]] = []
        for template in eligible:
            start = ordinal - int(template["target_offset"])
            expected = split_pipe(str(template["window_surfaces"]))
            observed: list[str] = []
            if start >= 1:
                for candidate_ordinal in range(start, ordinal + 1):
                    candidate = token_by_key.get((locus, candidate_ordinal))
                    if candidate is None:
                        observed = []
                        break
                    observed.append(candidate["surface"])
            if observed == expected:
                matches.append(template)
                template_id = str(template["template_id"])
                template_hits[template_id] += 1
                if locus == template["source_locus"] and ordinal == int(template["source_target_ordinal"]):
                    template_self_hits[template_id] += 1
                else:
                    template_cross_hits[template_id] += 1

        inherited_edges = split_pipe(token["v69_target_edge_ids"])
        matched_edges = [str(row["source_edge_id"]) for row in matches]
        require(set(matched_edges) == set(inherited_edges), f"exact frame match disagrees with inherited edge at {locus}#{ordinal}")
        already_bound = bool(inherited_edges)
        unbound = not already_bound
        context_start = max(1, ordinal - 3)
        context = [token_by_key[(locus, value)] for value in range(context_start, ordinal + 1)]
        if already_bound:
            decision = "ALREADY_ADMITTED_EXACT_SELF_REPLAY"
            note = "Exact template match is the template's own GDT697 source occurrence; it adds no transfer."
        else:
            decision = "UNBOUND_NO_EXACT_PARTICIPANT_FRAME"
            note = "Only a coarse nominal-block plus qol clause shape repeats; none of the three exact qol surface frames matches."
        row = {
            "occurrence_id": f"A{index:03d}",
            "page": token["page"],
            "locus": locus,
            "token_ordinal": ordinal,
            "action_surface": token["surface"],
            "v70_token_gloss_de": token["v70_token_gloss_de"],
            "v68_clause_id": token["v68_clause_id"],
            "v68_clause_type": token["v68_clause_type"],
            "eligible_template_ids": pipe([row["template_id"] for row in eligible]),
            "exact_match_template_ids": pipe([row["template_id"] for row in matches]),
            "exact_match_edge_ids": pipe(matched_edges),
            "inherited_target_edge_ids": pipe(inherited_edges),
            "already_bound": int(already_bound),
            "unbound_candidate": int(unbound),
            "context_start_ordinal": context_start,
            "context_end_ordinal": ordinal,
            "context_surfaces": pipe([row["surface"] for row in context]),
            "context_glosses_de": " || ".join(row["v70_token_gloss_de"] for row in context),
            "context_roles": " || ".join(row["v69_relation_roles"] for row in context),
            "decision": decision,
            "new_edge_count": 0,
            "new_microrecord_count": 0,
            "note": note,
        }
        occurrence_rows.append(row)
        occurrence_by_key[(locus, ordinal)] = row

    require(Counter(row["decision"] for row in occurrence_rows) == Counter({
        "ALREADY_ADMITTED_EXACT_SELF_REPLAY": 9,
        "UNBOUND_NO_EXACT_PARTICIPANT_FRAME": 1,
    }), "occurrence decisions changed")
    require(sum(template_hits.values()) == 9 and sum(template_self_hits.values()) == 9, "existing template hit count changed")
    require(sum(template_cross_hits.values()) == 0, "an exact cross-occurrence frame unexpectedly appeared")
    unbound_rows = [row for row in occurrence_rows if row["unbound_candidate"] == 1]
    require(len(unbound_rows) == 1 and (unbound_rows[0]["locus"], unbound_rows[0]["token_ordinal"], unbound_rows[0]["action_surface"]) == ("f77r.38", 9, "qol"), "unbound occurrence changed")
    bound_qol = [row for row in occurrence_rows if row["locus"] == "f77r.38" and row["token_ordinal"] == 6]
    require(len(bound_qol) == 1 and bound_qol[0]["already_bound"] == 1, "bound f77r.38 qol control changed")
    prior_clause_shapes: list[list[dict[str, str]]] = []
    for target_ordinal in (6, 9):
        target = token_by_key[("f77r.38", target_ordinal)]
        prior_clause_id = str(int(target["v68_clause_id"]) - 1)
        prior = [row for row in tokens if row["locus"] == "f77r.38" and row["v68_clause_id"] == prior_clause_id]
        require(len(prior) == 2 and all(row["v68_clause_type"] == "NOMINAL_BLOCK" for row in prior), "f77r qol shape control changed")
        prior_clause_shapes.append(prior)
    require(
        [row["surface"] for row in prior_clause_shapes[0]] != [row["surface"] for row in prior_clause_shapes[1]],
        "shape-only false friend unexpectedly became an exact frame",
    )

    template_rows: list[dict[str, object]] = []
    for row in template_work:
        template_id = str(row["template_id"])
        row.update({
            "total_exact_hits": template_hits[template_id],
            "self_source_hits": template_self_hits[template_id],
            "cross_occurrence_hits": template_cross_hits[template_id],
            "status": "SOURCE_REPLAY_ONLY__NO_CROSS_OCCURRENCE_TRANSFER",
        })
        require(template_hits[template_id] == template_self_hits[template_id] == 1, f"template is not self-only: {template_id}")
        template_rows.append(row)

    # The only open action occurrence is contrasted against all three existing
    # qol participant frames at their exact target-aligned offsets.
    candidate = unbound_rows[0]
    candidate_locus = str(candidate["locus"])
    candidate_ordinal = int(candidate["token_ordinal"])
    contrast_rows: list[dict[str, object]] = []
    reason_by_edge = {
        "C004": "Der geschriebene Zielanteil und der Hierzu-Verweis fehlen; ltaiin|shedy ist kein olkar|y-Rahmen.",
        "C005": "Unmittelbar vor #9 steht der Feuchtzustand shedy, nicht das zugelassene Zugabeobjekt chcphey.",
        "C008": "Die zwei qol sind durch ltaiin|shedy und eine neue Nominalklausel getrennt; der gemeinsame olkar-Zielrahmen fehlt.",
    }
    qol_templates = [row for row in template_rows if row["action_surface"] == "qol"]
    require([row["source_edge_id"] for row in qol_templates] == ["C004", "C005", "C008"], "qol template order changed")
    for template in qol_templates:
        offset = int(template["target_offset"])
        start = candidate_ordinal - offset
        aligned = [token_by_key[(candidate_locus, ordinal)] for ordinal in range(start, candidate_ordinal + 1)]
        expected = split_pipe(str(template["window_surfaces"]))
        observed = [row["surface"] for row in aligned]
        mismatches = [index for index, (left, right) in enumerate(zip(expected, observed)) if left != right]
        require(mismatches, f"unbound qol unexpectedly matches {template['template_id']}")
        contrast_rows.append({
            "candidate_locus": candidate_locus,
            "candidate_ordinal": candidate_ordinal,
            "candidate_surface": "qol",
            "template_id": template["template_id"],
            "source_edge_id": template["source_edge_id"],
            "expected_window_surfaces": template["window_surfaces"],
            "observed_aligned_surfaces": pipe(observed),
            "expected_participant_frame_de": template["participant_frame_de"],
            "observed_aligned_roles": " || ".join(row["v69_relation_roles"] for row in aligned),
            "mismatch_offsets": pipe(mismatches),
            "mismatch_count": len(mismatches),
            "surface_frame_exact": 0,
            "decision": "HOLD_NO_EXACT_FRAME_REPLAY",
            "reason_de": reason_by_edge[str(template["source_edge_id"])],
        })
    require([row["mismatch_count"] for row in contrast_rows] == [2, 1, 3], "qol mismatch profile changed")

    surface_rows: list[dict[str, object]] = []
    for surface in ["qokamdy", "ykaiin", "yteeeor", "qey", "qol", "qodar"]:
        occurrences = [row for row in occurrence_rows if row["action_surface"] == surface]
        templates = [row for row in template_rows if row["action_surface"] == surface]
        multiplicity = len(templates)
        determinacy = "MULTIPLE_ADMITTED_PARTICIPANT_FRAMES" if multiplicity > 1 else "SINGLE_OBSERVED_FRAME"
        decision = "SURFACE_DOES_NOT_DETERMINE_PARTICIPANT_FRAME" if multiplicity > 1 else "NO_CROSS_OCCURRENCE_TRANSFER_TEST_AVAILABLE"
        surface_rows.append({
            "action_surface": surface,
            "occurrence_count": len(occurrences),
            "already_bound_count": sum(int(row["already_bound"]) for row in occurrences),
            "unbound_count": sum(int(row["unbound_candidate"]) for row in occurrences),
            "template_count": len(templates),
            "exact_template_hits": sum(template_hits[str(row["template_id"])] for row in templates),
            "self_source_hits": sum(template_self_hits[str(row["template_id"])] for row in templates),
            "cross_occurrence_hits": sum(template_cross_hits[str(row["template_id"])] for row in templates),
            "new_candidate_hits": 0,
            "participant_frame_multiplicity": multiplicity,
            "frame_determinacy": determinacy,
            "decision": decision,
        })
    require(Counter(row["frame_determinacy"] for row in surface_rows) == Counter({
        "MULTIPLE_ADMITTED_PARTICIPANT_FRAMES": 2,
        "SINGLE_OBSERVED_FRAME": 4,
    }), "surface frame multiplicity changed")

    token_out: list[dict[str, object]] = []
    for row in tokens:
        occurrence = occurrence_by_key.get((row["locus"], int(row["token_ordinal"])))
        new = dict(row)
        new.update({
            "v71_action_surface_scan": 1 if occurrence else 0,
            "v71_action_occurrence_id": occurrence["occurrence_id"] if occurrence else "NONE",
            "v71_exact_frame_match_ids": occurrence["exact_match_template_ids"] if occurrence else "NONE",
            "v71_frame_decision": occurrence["decision"] if occurrence else "NOT_IN_ACTION_SURFACE_SCAN",
            "v71_token_gloss_de": row["v70_token_gloss_de"],
            "v71_word_delta": 0,
            "v71_status": "V70_TOKEN_GLOSS_BYTE_IDENTICAL__FRAME_REPLAY_METADATA_ONLY",
        })
        token_out.append(new)

    occurrences_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        occurrences_by_locus[str(row["locus"])].append(row)
    line_out: list[dict[str, object]] = []
    for row in lines:
        local = occurrences_by_locus[row["locus"]]
        new = dict(row)
        new.update({
            "v71_action_occurrence_ids": pipe([item["occurrence_id"] for item in local]),
            "v71_existing_frame_match_count": sum(int(item["already_bound"]) for item in local),
            "v71_unbound_action_count": sum(int(item["unbound_candidate"]) for item in local),
            "v71_new_frame_replay_count": 0,
            "v71_clause_translation_de": row["v70_clause_translation_de"],
            "v71_word_delta": 0,
            "v71_status": "V70_LINE_BYTE_IDENTICAL__ACTION_FRAME_SCAN_ONLY",
        })
        line_out.append(new)

    span_out: list[dict[str, object]] = []
    for row in spans:
        new = dict(row)
        new.update({
            "v71_selected_gloss_de": row["v70_selected_gloss_de"],
            "v71_byte_identical": 1,
            "v71_frame_replay_change": "NONE",
            "v71_status": "V70_BOUND_SPAN_BYTE_IDENTICAL",
        })
        span_out.append(new)

    write_tsv(TEMPLATES_OUT, template_rows, TEMPLATE_FIELDS)
    write_tsv(OCCURRENCES_OUT, occurrence_rows, OCCURRENCE_FIELDS)
    write_tsv(CONTRASTS_OUT, contrast_rows, CONTRAST_FIELDS)
    write_tsv(SURFACE_CENSUS_OUT, surface_rows, SURFACE_FIELDS)
    write_tsv(TOKENS_OUT, token_out, token_fields + [
        "v71_action_surface_scan", "v71_action_occurrence_id", "v71_exact_frame_match_ids",
        "v71_frame_decision", "v71_token_gloss_de", "v71_word_delta", "v71_status",
    ])
    write_tsv(LINES_OUT, line_out, line_fields + [
        "v71_action_occurrence_ids", "v71_existing_frame_match_count", "v71_unbound_action_count",
        "v71_new_frame_replay_count", "v71_clause_translation_de", "v71_word_delta", "v71_status",
    ])
    write_tsv(SPANS_OUT, span_out, span_fields + [
        "v71_selected_gloss_de", "v71_byte_identical", "v71_frame_replay_change", "v71_status",
    ])

    reader = [
        "# GDT698 / V71 — exakter Aktionsoberflächen-Rahmenreplay", "", f"Status: `{STATUS}`", "",
        "Die sechs Aktionsoberflächen der sieben V70-Mikrorecords kommen im vollständigen 479-Token-Bestand zehnmal vor. Neun Vorkommen sind bereits genau die neun gebundenen Zielaktionen. Das einzige offene Vorkommen bleibt offen.",
        "", "## Alle zehn Vorkommen", "",
        "| ID | Stelle | Form | Glosse | exakter Rahmen | Entscheidung |",
        "|---|---|---|---|---|---|",
    ]
    for row in occurrence_rows:
        reader.append(
            f"| {row['occurrence_id']} | `{row['locus']}#{row['token_ordinal']}` | `{row['action_surface']}` | "
            f"{md(str(row['v70_token_gloss_de']))} | `{md(str(row['exact_match_template_ids']))}` | `{row['decision']}` |"
        )
    reader.extend([
        "", "## Das offene `qol` auf f77r.38#9", "",
        "Die grobe Form ist verführerisch: Wie bei `qol` #6 geht ein zweigliedriger Nominalblock voraus. Das ist aber nur eine Klauselform, kein Teilnehmerrahmen.",
        "", "| bekannte qol-Kante | erwartete exakte Folge | tatsächlich vor #9 | Abweichungen | Urteil |", "|---|---|---|---:|---|",
    ])
    for row in contrast_rows:
        reader.append(
            f"| {row['source_edge_id']} | `{md(str(row['expected_window_surfaces']))}` | "
            f"`{md(str(row['observed_aligned_surfaces']))}` | {row['mismatch_count']} | {row['reason_de']} |"
        )
    reader.extend([
        "", "Sichere Arbeitsausgabe:", "",
        "> Holz, kalt auf Stufe III; mittlere Feuchtstufe erreicht. **[Teilnehmerbindung offen:]** Drogenstoff zugeben.",
        "", "## Ergebnis", "",
        "- 6 Aktionsoberflächen, 10 Vorkommen, 9 schon gebundene Zielaktionen.",
        "- 9 exakte Template-Treffer, sämtlich nur am eigenen Quellvorkommen.",
        "- 0 exakte Cross-Occurrence-Replays und 0 neue Mikrorecords oder Kanten.",
        "- `ykaiin` besitzt zwei und `qol` drei verschiedene bereits zugelassene Teilnehmerrahmen: Die Aktionsoberfläche allein bestimmt ihr Objekt oder Ziel nicht.",
        "- 479 Token, 51 Zeilen und 3 gebundene Spannen bleiben unverändert.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")
    ARTIFACT_README.write_text(
        "# GDT698 artifacts\n\n"
        "- `V71_9_EXACT_TARGET_FRAME_TEMPLATES.tsv`: nine target-aligned V70 surface frames.\n"
        "- `V71_10_ACTION_SURFACE_OCCURRENCES.tsv`: exhaustive six-surface occurrence scan.\n"
        "- `V71_3_UNBOUND_QOL_TEMPLATE_CONTRASTS.tsv`: the sole open occurrence against all qol frames.\n"
        "- `V71_6_ACTION_SURFACE_CENSUS.tsv`: surface multiplicity and transfer census.\n"
        "- `V71_479_TOKEN_FREEZE.tsv`, `V71_51_LINE_FREEZE.tsv`, `V71_3_BOUND_SPAN_FREEZE.tsv`: complete unchanged V70 scope.\n"
        "- `GDT698_V71_ACTION_SURFACE_FRAME_REPLAY_READER.md`: compact human result.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    generated = [
        TEMPLATES_OUT, OCCURRENCES_OUT, CONTRASTS_OUT, SURFACE_CENSUS_OUT,
        TOKENS_OUT, LINES_OUT, SPANS_OUT, READER_OUT, ARTIFACT_README,
    ]
    inputs = [SPECS, MICROS, EDGES, TOKENS, LINES, SPANS, G697_RESULT, Path(__file__).resolve()]
    result = {
        "status": STATUS,
        "question": "Do any unbound occurrences of the six V70 action surfaces reproduce an already observed exact contiguous participant frame?",
        "claim_ceiling": CLAIM_CEILING,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "bound_spans": 3, "v70_microrecords": 7, "v70_edges": 9,
            "f84_access": 0, "f84r_access": 0,
        },
        "scan": {
            "action_surface_types": 6, "action_surface_occurrences": 10,
            "repeated_action_surface_types": 2, "repeated_surface_occurrences": 6,
            "single_occurrence_surface_types": 4, "exact_frame_templates": 9,
            "already_bound_target_occurrences": 9, "unbound_target_occurrences": 1,
            "exact_template_hits": 9, "self_source_template_hits": 9,
            "cross_occurrence_template_hits": 0, "new_candidate_hits": 0,
            "new_edges": 0, "new_microrecords": 0,
            "surface_types_with_multiple_participant_frames": 2,
            "shape_only_false_friends": 1,
        },
        "surface_counts": {row["action_surface"]: int(row["occurrence_count"]) for row in surface_rows},
        "unbound_decision": {
            "locus": "f77r.38", "ordinal": 9, "surface": "qol",
            "eligible_qol_frames": 3, "exact_matches": 0,
            "decision": "HOLD_NO_EXACT_FRAME_REPLAY",
        },
        "freeze": {
            "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0,
            "changed_word_meanings": 0, "content_word_additions": 0,
            "content_word_deletions": 0, "content_word_reorders": 0,
        },
        "inputs": {rel(path): digest(path) for path in inputs},
        "files": {path.name: digest(path) for path in generated},
        "next_gap": "Test only the five already identified backward-referential HEAT actions: two admitted prototypes and three open occurrences. Admit one immediately preceding complete nominal block or an admitted action output under the same exact geometry; forbid generic objects, nearest-noun fallback, block splitting and invented results.",
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": STATUS, "surface_types": 6, "occurrences": 10,
        "existing_matches": 9, "unbound_held": 1, "cross_replays": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
