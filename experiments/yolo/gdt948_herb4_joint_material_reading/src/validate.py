#!/usr/bin/env python3
"""Independent GDT948 source, coverage, provenance and consequence audit.

This validator does not import or replay run.py/consequences.py. It checks the
registered source against the original GDT809 fenced blocks, then derives its
own coverage and event matrix from the current model.
"""

from __future__ import annotations

import hashlib
import json
import re
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
SOURCE_REL = "experiments/yolo/gdt948_herb4_joint_material_reading/src/SOURCE.json"
MODEL_REL = "experiments/yolo/gdt948_herb4_joint_material_reading/src/MODEL.json"
LOCK_REL = "experiments/yolo/gdt948_herb4_joint_material_reading/PREREG_LOCK.json"
ORIGINAL_REL = "experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament/artifacts/JOINT_COMPETING_PARAGRAPH_READINGS.md"

EXPECTED_BLOCKS = [
    ("JP01", "H17", ["f17r.4", "f17r.5", "f17r.6"]),
    ("JP02", "H21", ["f21r.8", "f21r.9", "f21r.10", "f21r.11", "f21r.12"]),
    ("JP03", "H32", ["f32v.7", "f32v.8", "f32v.9", "f32v.10", "f32v.11"]),
    ("JP04", "H29", ["f29v.1", "f29v.2", "f29v.3", "f29v.4"]),
]
VALID_KINDS = {"THING", "ACTION", "LINK", "QUALITY", "QUANTITY"}
VALID_CHECK_STATUSES = {"assumed", "source_link", "unknown", "contradiction"}
IDENTITY_KEYS = {"identity_of", "same_as", "same_entity_as", "equivalent_to", "identity_refs", "same_physical_entity"}


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(errors: list[dict[str, Any]], kind: str, **detail: Any) -> None:
    errors.append({"kind": kind, **detail})


def refs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(x) for x in value] if isinstance(value, list) else []


def records_for_source(source: dict[str, Any], errors: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[str]]]:
    records: list[dict[str, Any]] = []
    by_ref: dict[str, dict[str, Any]] = {}
    paragraphs: dict[str, list[str]] = defaultdict(list)
    for line in source.get("lines", []):
        locus, paragraph = line.get("locus", ""), line.get("paragraph", "")
        raw, tokens = line.get("raw", ""), line.get("tokens", [])
        if raw != " ".join(tokens):
            add(errors, "SOURCE_RAW_TOKEN_MISMATCH", locus=locus)
        if locus in paragraphs.get(paragraph, []):
            add(errors, "SOURCE_DUPLICATE_LINE", locus=locus, paragraph=paragraph)
        paragraphs[paragraph].append(locus)
        for index, form in enumerate(tokens, 1):
            ref = f"{locus}#{index}"
            if ref in by_ref:
                add(errors, "SOURCE_DUPLICATE_REF", ref=ref)
            rec = {"ref": ref, "locus": locus, "index": index, "paragraph": paragraph, "raw": form}
            records.append(rec)
            by_ref[ref] = rec
    return records, by_ref, paragraphs


def extract_fenced_blocks(original: str, errors: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    pattern = re.compile(r"^##\s+(JP\d{2})\s+[^\n]*\n\n```text\n(.*?)\n```", re.MULTILINE | re.DOTALL)
    found = list(pattern.finditer(original))
    if len(found) != len(EXPECTED_BLOCKS):
        add(errors, "SOURCE_FENCED_BLOCK_COUNT", expected=len(EXPECTED_BLOCKS), actual=len(found))
    blocks: list[dict[str, Any]] = []
    canonical_lines: list[str] = []
    for match in found:
        block_id, body = match.group(1), match.group(2)
        parsed: list[dict[str, Any]] = []
        for line in body.splitlines():
            parsed_match = re.fullmatch(r"(\S+)  (.+)", line)
            if not parsed_match:
                add(errors, "SOURCE_FENCED_LINE_SCHEMA", block=block_id, line=line)
                continue
            locus, raw = parsed_match.groups()
            parsed.append({"locus": locus, "raw": raw, "tokens": raw.split()})
            canonical_lines.append(line)
        blocks.append({"id": block_id, "lines": parsed})
    return blocks, "\n".join(canonical_lines) + ("\n" if canonical_lines else "")


def check_source(source: dict[str, Any], errors: list[dict[str, Any]]) -> dict[str, Any]:
    path = ROOT / ORIGINAL_REL
    if not path.is_file():
        add(errors, "SOURCE_ORIGINAL_MISSING", path=ORIGINAL_REL)
        return {"original_sha256": None, "fenced_block_sha256": None, "fenced_blocks": 0}
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    original_sha = hashlib.sha256(original_bytes).hexdigest()
    if source.get("sha256") != original_sha:
        add(errors, "SOURCE_ORIGINAL_HASH_MISMATCH", expected=source.get("sha256"), actual=original_sha)
    blocks, canonical = extract_fenced_blocks(original, errors)
    expected_ids = [x[0] for x in EXPECTED_BLOCKS]
    if [b["id"] for b in blocks] != expected_ids:
        add(errors, "SOURCE_FENCED_BLOCK_ORDER", expected=expected_ids, actual=[b["id"] for b in blocks])
    source_lines = source.get("lines", [])
    expected_flat = [(block, paragraph, locus) for block, paragraph, loci in EXPECTED_BLOCKS for locus in loci]
    if len(source_lines) != len(expected_flat):
        add(errors, "SOURCE_LINE_COUNT", expected=len(expected_flat), actual=len(source_lines))
    extracted_flat = [(b["id"], paragraph, line) for b, (_, paragraph, _) in zip(blocks, EXPECTED_BLOCKS) for line in b["lines"]]
    if len(extracted_flat) != len(source_lines):
        add(errors, "SOURCE_EXTRACTED_LINE_COUNT", expected=len(source_lines), actual=len(extracted_flat))
    for index, ((block_id, paragraph, expected_locus), src_line) in enumerate(zip(expected_flat, source_lines)):
        if src_line.get("locus") != expected_locus or src_line.get("paragraph") != paragraph:
            add(errors, "SOURCE_REGISTERED_LINE_ORDER", index=index, expected={"block": block_id, "paragraph": paragraph, "locus": expected_locus}, actual={"paragraph": src_line.get("paragraph"), "locus": src_line.get("locus")})
    for index, (source_line, extracted) in enumerate(zip(source_lines, extracted_flat)):
        block_id, paragraph, line = extracted
        if source_line.get("paragraph") != paragraph or source_line.get("locus") != line.get("locus") or source_line.get("raw") != line.get("raw") or source_line.get("tokens") != line.get("tokens"):
            add(errors, "SOURCE_FENCED_CONTENT_MISMATCH", index=index, block=block_id, registered=source_line, extracted={"paragraph": paragraph, **line})
    expected_canonical = "\n".join(f"{line.get('locus', '')}  {line.get('raw', '')}" for line in source_lines) + ("\n" if source_lines else "")
    if canonical != expected_canonical:
        add(errors, "SOURCE_CANONICAL_EXTRACTION_MISMATCH")
    if source.get("paragraphs") != [x[1] for x in EXPECTED_BLOCKS]:
        add(errors, "SOURCE_PARAGRAPH_ORDER", expected=[x[1] for x in EXPECTED_BLOCKS], actual=source.get("paragraphs"))
    return {"original_sha256": original_sha, "fenced_block_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "fenced_blocks": len(blocks), "fenced_lines": len(extracted_flat)}


def check_lock(errors: list[dict[str, Any]]) -> list[str]:
    lock = load(LOCK_REL)
    checked: list[str] = []
    for rel, expected in lock.get("files", {}).items():
        path = EXP / ("src/SOURCE.json" if rel == "SOURCE.json" else rel)
        if not path.is_file():
            add(errors, "LOCKED_FILE_MISSING", file=rel)
            continue
        actual = digest(path)
        checked.append(rel)
        if actual != expected:
            add(errors, "LOCKED_FILE_HASH_MISMATCH", file=rel, expected=expected, actual=actual)
    return checked


def check_lexicon(model: dict[str, Any], records: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    lex = model.get("lexicon")
    if not isinstance(lex, dict):
        add(errors, "LEXICON_SCHEMA", detail="lexicon must be an object")
        return {"source_types": 0, "lexicon_types": 0, "singletons": 0, "action_occurrences": 0, "action_types": 0}
    counts = Counter(r["raw"] for r in records)
    source_types, lex_types = set(counts), set(lex)
    for form in sorted(source_types - lex_types):
        add(errors, "LEXICON_MISSING_TYPE", form=form)
    for form in sorted(lex_types - source_types):
        add(errors, "LEXICON_EXTRA_TYPE", form=form)
    for form, value in lex.items():
        if not isinstance(value, dict):
            add(errors, "LEXICON_ENTRY_SCHEMA", form=form)
            continue
        required = {"process", "catalogue", "kind"}
        if not required <= set(value):
            add(errors, "LEXICON_ENTRY_FIELDS", form=form, missing=sorted(required - set(value)))
        if not isinstance(value.get("process"), str) or not isinstance(value.get("catalogue"), str):
            add(errors, "LEXICON_ENTRY_TEXT_TYPE", form=form)
        if value.get("kind") not in VALID_KINDS:
            add(errors, "LEXICON_ENTRY_KIND", form=form, kind=value.get("kind"))
    # A type is read through one fixed map for every occurrence; no per-token
    # gloss can silently vary.
    occurrence_values: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for record in records:
        value = lex.get(record["raw"])
        if isinstance(value, dict):
            occurrence_values[record["raw"]].add((value.get("process", ""), value.get("catalogue", ""), value.get("kind", "")))
    for form, values in occurrence_values.items():
        if len(values) != 1:
            add(errors, "LEXICON_NONDETERMINISTIC", form=form, values=sorted(values))
    actions = [r for r in records if isinstance(lex.get(r["raw"]), dict) and lex[r["raw"]].get("kind") == "ACTION"]
    singleton_forms = sorted(form for form, count in counts.items() if count == 1)
    return {"source_types": len(source_types), "lexicon_types": len(lex_types), "singletons": len(singleton_forms), "singleton_forms": singleton_forms, "action_occurrences": len(actions), "action_types": len({r["raw"] for r in actions}), "kind_counts": dict(Counter(lex.get(r["raw"], {}).get("kind") for r in records if isinstance(lex.get(r["raw"]), dict)))}


def check_clauses(model: dict[str, Any], by_ref: dict[str, dict[str, Any]], records: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    clauses = model.get("clauses")
    if not isinstance(clauses, list):
        add(errors, "CLAUSE_SCHEMA", detail="clauses must be a list")
        return {"clauses": 0, "clause_refs": 0, "partition_exact": False}
    ids = [c.get("id") for c in clauses if isinstance(c, dict)]
    for ident, count in Counter(ids).items():
        if count != 1:
            add(errors, "CLAUSE_DUPLICATE_ID", id=ident, count=count)
    seen: list[str] = []
    for clause in clauses:
        if not isinstance(clause, dict):
            add(errors, "CLAUSE_ENTRY_SCHEMA")
            continue
        cid, paragraph = clause.get("id", ""), clause.get("paragraph", "")
        cref = clause.get("refs")
        if not isinstance(clause.get("process_text"), str) or not isinstance(clause.get("catalogue_text"), str):
            add(errors, "CLAUSE_READING_FIELDS", clause=cid)
        if not refs(cref):
            add(errors, "CLAUSE_EMPTY", clause=cid)
        for ref in refs(cref):
            if ref not in by_ref:
                add(errors, "CLAUSE_REF_MISSING", clause=cid, ref=ref)
                continue
            seen.append(ref)
            if by_ref[ref]["paragraph"] != paragraph:
                add(errors, "CLAUSE_CROSS_PARAGRAPH", clause=cid, ref=ref, clause_paragraph=paragraph, source_paragraph=by_ref[ref]["paragraph"])
    counts = Counter(seen)
    for ref, count in counts.items():
        if count != 1:
            add(errors, "CLAUSE_REF_NOT_UNIQUE", ref=ref, count=count)
    expected = {r["ref"] for r in records}
    exact = set(seen) == expected and len(seen) == len(records)
    if not exact:
        add(errors, "CLAUSE_PARTITION_NOT_EXACT", expected=len(records), seen=len(seen), missing=sorted(expected - set(seen)), extra=sorted(set(seen) - expected))
    return {"clauses": len(clauses), "clause_refs": len(seen), "partition_exact": exact}


def word_tokens(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)


def check_revisions(model: dict[str, Any], errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Ensure post-draft value changes are disclosed as exploratory repairs."""
    revisions = model.get("revisions", [])
    if not revisions:
        return {"revisions": 0, "revision_changes": 0}
    try:
        prior = load("experiments/yolo/gdt948_herb4_joint_material_reading/src/MODEL_v01.json")
    except Exception as exc:  # pragma: no cover - a missing predecessor is itself a finding
        add(errors, "MODEL_V01_MISSING", detail=str(exc))
        return {"revisions": len(revisions), "revision_changes": 0}
    current_lex = model.get("lexicon", {})
    prior_lex = prior.get("lexicon", {})
    changes = 0
    for revision in revisions:
        status = str(revision.get("status", "")).lower()
        if not all(term in status for term in ("postdraft", "exploratory")) or "prediction" not in status:
            add(errors, "REVISION_STATUS_NOT_EXPLORATORY", status=revision.get("status"))
        for change in revision.get("changes", []):
            changes += 1
            form, before, after = change.get("form"), change.get("before"), change.get("after")
            old = prior_lex.get(form, {}).get("process") if isinstance(prior_lex.get(form), dict) else None
            new = current_lex.get(form, {}).get("process") if isinstance(current_lex.get(form), dict) else None
            if old != before or new != after:
                add(errors, "REVISION_VALUE_MISMATCH", form=form, expected_before=old, recorded_before=before, expected_after=new, recorded_after=after)
            reason = str(change.get("reason", "")).lower()
            if not reason:
                add(errors, "REVISION_REASON_MISSING", form=form)
            if form in {"cphaldy", "otyky", "kor"} and "singleton" not in reason:
                add(errors, "SINGLETON_REPAIR_NOT_DISCLOSED", form=form, reason=change.get("reason", ""))
    return {"revisions": len(revisions), "revision_changes": changes}


def check_identity_links(value: Any, owner: dict[str, Any], entity_map: dict[str, dict[str, Any]], by_ref: dict[str, dict[str, Any]], errors: list[dict[str, Any]], path: str) -> None:
    if not isinstance(value, dict):
        return
    for key in IDENTITY_KEYS:
        if key not in value:
            continue
        for target in refs(value[key]):
            if target in entity_map:
                if entity_map[target].get("paragraph") != owner.get("paragraph"):
                    add(errors, "CROSS_PARAGRAPH_IDENTITY", owner=owner.get("id"), target=target, path=path)
            elif target not in by_ref:
                add(errors, "IDENTITY_TARGET_MISSING", owner=owner.get("id"), target=target, path=path)


def producer_cycles(events: list[dict[str, Any]], entities: list[dict[str, Any]]) -> list[list[str]]:
    event_map = {e.get("id"): e for e in events}
    entity_map = {e.get("id"): e for e in entities}
    graph = {eid: set() for eid in event_map}
    for eid, event in event_map.items():
        for entity_id in refs(event.get("inputs")):
            producer = entity_map.get(entity_id, {}).get("producer")
            if producer in graph and producer != eid:
                graph[eid].add(producer)
    cycles: list[list[str]] = []
    finished: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in trail:
            cycles.append(trail[trail.index(node):] + [node])
            return
        if node in finished:
            return
        for dep in sorted(graph[node]):
            visit(dep, trail + [node])
        finished.add(node)

    for eid in graph:
        visit(eid, [])
    return cycles


def consequence_row(event: dict[str, Any], event_index: int, by_ref: dict[str, dict[str, Any]], entity_map: dict[str, dict[str, Any]], lex: dict[str, dict[str, Any]]) -> dict[str, Any]:
    trigger = event.get("trigger_ref", "")
    trigger_rec = by_ref.get(trigger)
    input_ids, output_ids = refs(event.get("inputs")), refs(event.get("outputs"))
    checks = event.get("checks", []) if isinstance(event.get("checks", []), list) else []
    statuses = Counter(c.get("status", "unknown") for c in checks if isinstance(c, dict))
    requirement_rows = []
    for requirement in event.get("requirements", []) if isinstance(event.get("requirements", []), list) else []:
        entity_id, prop, required = requirement.get("entity"), requirement.get("property"), requirement.get("value")
        entity = entity_map.get(entity_id)
        assigned = entity.get("initial_state", {}).get(prop, "UNSPECIFIED") if isinstance(entity, dict) and isinstance(entity.get("initial_state", {}), dict) else "UNSPECIFIED"
        if assigned == "UNSPECIFIED":
            verdict = "UNKNOWN"
            obligation_type = "desired_end_state_not_observed" if prop in {"settled", "ready", "bound"} else "assumed_input_requirement"
        elif assigned == required:
            verdict = "CONDITIONAL_MATCH"
            obligation_type = "assumed_input_requirement"
        else:
            verdict = "CONDITIONAL_CONTRADICTION"
            obligation_type = "assumed_input_requirement"
        requirement_rows.append({"entity": entity_id, "property": prop, "required": required, "assigned": assigned, "verdict": verdict, "obligation_type": obligation_type})
    trigger_valid = bool(trigger_rec and trigger_rec.get("paragraph") == event.get("paragraph") and isinstance(lex.get(trigger_rec.get("raw")), dict) and lex[trigger_rec.get("raw")].get("kind") == "ACTION")
    inputs_valid = all(x in entity_map and entity_map[x].get("paragraph") == event.get("paragraph") for x in input_ids)
    outputs_valid = all(x in entity_map and entity_map[x].get("paragraph") == event.get("paragraph") for x in output_ids)
    if statuses.get("contradiction", 0):
        status = "CONTRADICTION"
    elif statuses.get("unknown", 0):
        status = "UNRESOLVED"
    elif statuses.get("source_link", 0):
        status = "SOURCE_LINKED"
    else:
        status = "ASSUMED_ONLY"
    return {"event": event.get("id", ""), "event_index": event_index, "paragraph": event.get("paragraph", ""), "trigger_ref": trigger, "trigger_form": trigger_rec.get("raw") if trigger_rec else None, "trigger_valid": trigger_valid, "inputs": len(input_ids), "inputs_valid": inputs_valid, "outputs": len(output_ids), "outputs_valid": outputs_valid, "checks": len(checks), "assumed": statuses.get("assumed", 0), "source_link": statuses.get("source_link", 0), "unknown": statuses.get("unknown", 0), "contradiction": statuses.get("contradiction", 0), "requirements": requirement_rows, "status": status, "conditional_only": True}


def compare_declared_matrix(model: dict[str, Any], rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> None:
    declared: Any = model.get("consequence_matrix", model.get("consequences"))
    if declared is None:
        declared = [e.get("consequence", e.get("consequences")) for e in model.get("events", []) if isinstance(e, dict) and ("consequence" in e or "consequences" in e)]
    if isinstance(declared, dict):
        declared = [{"event": key, **value} for key, value in declared.items() if isinstance(value, dict)]
    if not isinstance(declared, list) or not declared:
        return
    by_event = {row["event"]: row for row in rows}
    keys = {"trigger_valid", "inputs_valid", "outputs_valid", "checks", "assumed", "source_link", "unknown", "contradiction", "status"}
    for item in declared:
        if not isinstance(item, dict):
            add(errors, "CONSEQUENCE_DECLARATION_SCHEMA")
            continue
        event_id = item.get("event", item.get("event_id", item.get("id")))
        if event_id not in by_event:
            add(errors, "CONSEQUENCE_EVENT_MISSING", event=event_id)
            continue
        for key in keys & set(item):
            if item[key] != by_event[event_id][key]:
                add(errors, "CONSEQUENCE_MATRIX_MISMATCH", event=event_id, field=key, declared=item[key], recomputed=by_event[event_id][key])


def check_candidate_artifacts(source: dict[str, Any], model: dict[str, Any], current_rows: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Check the three frozen candidate summaries without running their builder."""
    result_path = EXP / "artifacts" / "CONSEQUENCE_RESULT.json"
    table_path = EXP / "artifacts" / "QOTCHY_CANDIDATES.tsv"
    if not result_path.is_file() or not table_path.is_file():
        add(errors, "CANDIDATE_ARTIFACT_MISSING")
        return {"candidates": [], "lexical_delta": [], "state_table_rows": 0}
    result = json.loads(result_path.read_text(encoding="utf-8"))
    expected_names = {"M_v01", "M_v02", "I_v02"}
    candidates = result.get("candidates", [])
    names = {c.get("candidate") for c in candidates if isinstance(c, dict)}
    if names != expected_names:
        add(errors, "CANDIDATE_SET_MISMATCH", expected=sorted(expected_names), actual=sorted(names))
    expected = {
        "M_v01": (30, {"CONDITIONAL_MATCH": 9, "CONDITIONAL_CONTRADICTION": 1, "UNKNOWN": 2}),
        "M_v02": (32, {"CONDITIONAL_MATCH": 11, "UNKNOWN": 2}),
        "I_v02": (32, {"CONDITIONAL_MATCH": 11, "UNKNOWN": 2}),
    }
    candidate_summary = {}
    for candidate in candidates:
        name = candidate.get("candidate")
        if name not in expected:
            continue
        actions, reqs = expected[name]
        if candidate.get("tokens") != 145 or candidate.get("fixed_values") != 103:
            add(errors, "CANDIDATE_SOURCE_COUNTS", candidate=name, tokens=candidate.get("tokens"), fixed_values=candidate.get("fixed_values"))
        if candidate.get("action_occurrences") != actions:
            add(errors, "CANDIDATE_ACTION_COUNT", candidate=name, expected=actions, actual=candidate.get("action_occurrences"))
        if candidate.get("requirement_results") != reqs:
            add(errors, "CANDIDATE_REQUIREMENT_MATRIX", candidate=name, expected=reqs, actual=candidate.get("requirement_results"))
        if candidate.get("independent_meaning_confirmation_capacity") != 0:
            add(errors, "CANDIDATE_MEANING_CAPACITY", candidate=name, actual=candidate.get("independent_meaning_confirmation_capacity"))
        candidate_summary[name] = {"action_occurrences": candidate.get("action_occurrences"), "requirement_results": candidate.get("requirement_results"), "independent_meaning_confirmation_capacity": candidate.get("independent_meaning_confirmation_capacity")}
    source_summary = result.get("source", {})
    if source_summary.get("tokens") != 145 or source_summary.get("types") != 103 or source_summary.get("singleton_types") != 84 or source_summary.get("physical_leaves") != 4:
        add(errors, "CANDIDATE_SOURCE_SUMMARY", actual=source_summary)
    if result.get("chosen_truth_candidate") is not None or result.get("independently_translated_words") != 0 or result.get("meaning_confirmation_capacity") != 0:
        add(errors, "CANDIDATE_SELECTION_CLAIM", chosen=result.get("chosen_truth_candidate"), translated=result.get("independently_translated_words"), capacity=result.get("meaning_confirmation_capacity"))
    delta = result.get("lexical_rival_changes", [])
    expected_delta = [
        {"form": "qotchy", "M_v02": "trenne", "I_v02": "prüfe", "occurrences": 2},
        {"form": "cfhy", "M_v02": "mit dem Sieb", "I_v02": "Feinheit", "occurrences": 1},
    ]
    if delta != expected_delta:
        add(errors, "LEXICAL_DELTA_MISMATCH", expected=expected_delta, actual=delta)
    rival = str(result.get("catalogue_rival", ""))
    if not rival or "does not assert execution" not in rival or "cannot be penalized" not in rival:
        add(errors, "CATALOGUE_RIVAL_NOT_EXPLICIT", detail=rival)
    qrows = list(csv.DictReader(table_path.open(encoding="utf-8"), delimiter="\t"))
    if len(qrows) != 6 or {r.get("candidate") for r in qrows} != expected_names:
        add(errors, "QOTCHY_CANDIDATE_TABLE_SHAPE", rows=len(qrows), candidates=sorted({r.get("candidate") for r in qrows}))
    for row in qrows:
        if row.get("decision") != "UNDISTINGUISHED_BY_THE_OBSERVED_TEXT" or row.get("independent_output_identity_evidence") != "0":
            add(errors, "QOTCHY_RIVAL_DECISION", row=row)
        if row.get("candidate", "").startswith("I_") and (row.get("physical_creation_assumed") != "False" or row.get("named_outputs")):
            add(errors, "QOTCHY_INSPECT_OUTPUT_CLAIM", row=row)
        if row.get("candidate", "").startswith("M_") and row.get("physical_creation_assumed") != "True":
            add(errors, "QOTCHY_PROCESS_OUTPUT_CLAIM", row=row)
    state_path = EXP / "artifacts" / "STATE_CONSEQUENCES.tsv"
    state_rows = list(csv.DictReader(state_path.open(encoding="utf-8"), delimiter="\t")) if state_path.is_file() else []
    current_requirements = {(row["event"], req["entity"], req["property"]): req["verdict"] for row in current_rows for req in row.get("requirements", [])}
    supplied_v02 = {(row.get("event"), row.get("entity"), row.get("property")): row.get("verdict") for row in state_rows if row.get("candidate") == "M_v02"}
    if supplied_v02 != current_requirements:
        add(errors, "STATE_MATRIX_MISMATCH", expected=current_requirements, actual=supplied_v02)
    return {"candidates": sorted(names), "candidate_summary": candidate_summary, "lexical_delta": delta, "state_table_rows": len(state_rows)}


def check_events(model: dict[str, Any], records: list[dict[str, Any]], by_ref: dict[str, dict[str, Any]], errors: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lex = model.get("lexicon", {}) if isinstance(model.get("lexicon", {}), dict) else {}
    entities = model.get("entities", []) if isinstance(model.get("entities", []), list) else []
    events = model.get("events", []) if isinstance(model.get("events", []), list) else []
    entity_ids = [e.get("id") for e in entities if isinstance(e, dict)]
    event_ids = [e.get("id") for e in events if isinstance(e, dict)]
    for ident, count in Counter(entity_ids).items():
        if count != 1:
            add(errors, "ENTITY_DUPLICATE_ID", id=ident, count=count)
    for ident, count in Counter(event_ids).items():
        if count != 1:
            add(errors, "EVENT_DUPLICATE_ID", id=ident, count=count)
    entity_map = {e.get("id"): e for e in entities if isinstance(e, dict)}
    event_map = {e.get("id"): e for e in events if isinstance(e, dict)}
    paragraphs = {r["paragraph"] for r in records}
    clause_by_ref: dict[str, dict[str, Any]] = {}
    for clause in model.get("clauses", []) if isinstance(model.get("clauses", []), list) else []:
        if isinstance(clause, dict):
            for ref in refs(clause.get("refs")):
                clause_by_ref[ref] = clause
    producers: dict[str, list[str]] = defaultdict(list)
    for entity in entities:
        if not isinstance(entity, dict):
            add(errors, "ENTITY_ENTRY_SCHEMA")
            continue
        eid, paragraph = entity.get("id", ""), entity.get("paragraph", "")
        if paragraph not in paragraphs:
            add(errors, "ENTITY_PARAGRAPH_UNKNOWN", entity=eid, paragraph=paragraph)
        if entity.get("origin") not in {"external", "event"}:
            add(errors, "ENTITY_ORIGIN_INVALID", entity=eid, origin=entity.get("origin"))
        for ref in refs(entity.get("anchor_refs")):
            if ref not in by_ref:
                add(errors, "ENTITY_ANCHOR_MISSING", entity=eid, ref=ref)
            elif by_ref[ref]["paragraph"] != paragraph:
                add(errors, "ENTITY_ANCHOR_CROSS_PARAGRAPH", entity=eid, ref=ref)
        if entity.get("producer"):
            producers[str(entity["producer"])].append(eid)
        check_identity_links(entity, entity, entity_map, by_ref, errors, f"entity:{eid}")
    rows: list[dict[str, Any]] = []
    trigger_counts = Counter()
    action_refs = [r["ref"] for r in records if isinstance(lex.get(r["raw"]), dict) and lex[r["raw"]].get("kind") == "ACTION"]
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            add(errors, "EVENT_ENTRY_SCHEMA")
            continue
        eid, paragraph, trigger = event.get("id", ""), event.get("paragraph", ""), event.get("trigger_ref", "")
        trigger_counts[trigger] += 1
        trigger_rec = by_ref.get(trigger)
        if trigger_rec is None:
            add(errors, "EVENT_TRIGGER_MISSING", event=eid, ref=trigger)
        else:
            if trigger_rec["paragraph"] != paragraph:
                add(errors, "EVENT_TRIGGER_CROSS_PARAGRAPH", event=eid, ref=trigger)
            elif not isinstance(lex.get(trigger_rec["raw"]), dict) or lex[trigger_rec["raw"]].get("kind") != "ACTION":
                add(errors, "EVENT_TRIGGER_NOT_ACTION", event=eid, ref=trigger, form=trigger_rec["raw"])
            expected_verb = lex.get(trigger_rec["raw"], {}).get("process") if isinstance(lex.get(trigger_rec["raw"]), dict) else None
            if expected_verb and event.get("verb") != expected_verb:
                warnings.append({"kind": "EVENT_VERB_DIFFERS_FROM_LEXICON", "event": eid, "trigger": trigger, "lexicon_process": expected_verb, "event_verb": event.get("verb")})
            clause = clause_by_ref.get(trigger)
            if clause is None:
                add(errors, "EVENT_CLAUSE_MISSING", event=eid, ref=trigger)
            else:
                prose_words = word_tokens(str(clause.get("process_text", "")))
                verb_words = word_tokens(str(event.get("verb", "")))
                cursor = 0
                for component in verb_words:
                    try:
                        cursor = prose_words.index(component, cursor) + 1
                    except ValueError:
                        warnings.append({"kind": "EVENT_VERB_PROSE_ALIGNMENT_LIMIT", "event": eid, "clause": clause.get("id"), "verb": event.get("verb"), "detail": "event verb is passive, split across the continued clause, or uses a near-synonymous process wording"})
                        break
        if paragraph not in paragraphs:
            add(errors, "EVENT_PARAGRAPH_UNKNOWN", event=eid, paragraph=paragraph)
        for role in ("inputs", "outputs"):
            for entity_id in refs(event.get(role)):
                if entity_id not in entity_map:
                    add(errors, "EVENT_ENTITY_MISSING", event=eid, role=role, entity=entity_id)
                elif entity_map[entity_id].get("paragraph") != paragraph:
                    add(errors, "EVENT_ENTITY_CROSS_PARAGRAPH", event=eid, role=role, entity=entity_id)
        for requirement in event.get("requirements", []) if isinstance(event.get("requirements", []), list) else []:
            if not isinstance(requirement, dict) or not {"entity", "property", "value"} <= set(requirement):
                add(errors, "REQUIREMENT_SCHEMA", event=eid)
                continue
            target = entity_map.get(requirement["entity"])
            if target is None:
                add(errors, "REQUIREMENT_ENTITY_MISSING", event=eid, entity=requirement["entity"])
            elif target.get("paragraph") != paragraph:
                add(errors, "REQUIREMENT_ENTITY_CROSS_PARAGRAPH", event=eid, entity=requirement["entity"])
        for effect in event.get("effects", []) if isinstance(event.get("effects", []), list) else []:
            if not isinstance(effect, dict) or not {"entity", "property", "value"} <= set(effect):
                add(errors, "EFFECT_SCHEMA", event=eid)
                continue
            target = entity_map.get(effect["entity"])
            if target is None:
                add(errors, "EFFECT_ENTITY_MISSING", event=eid, entity=effect["entity"])
            elif target.get("paragraph") != paragraph:
                add(errors, "EFFECT_ENTITY_CROSS_PARAGRAPH", event=eid, entity=effect["entity"])
        for output in refs(event.get("outputs")):
            if output in entity_map and entity_map[output].get("producer") and entity_map[output].get("producer") != eid:
                add(errors, "OUTPUT_PRODUCER_MISMATCH", event=eid, entity=output, declared_producer=entity_map[output].get("producer"))
        checks = event.get("checks", [])
        if not isinstance(checks, list):
            add(errors, "EVENT_CHECKS_SCHEMA", event=eid)
            checks = []
        if not checks:
            warnings.append({"kind": "EVENT_NO_CHECKS", "event": eid})
        for check in checks:
            if not isinstance(check, dict):
                add(errors, "CHECK_SCHEMA", event=eid)
                continue
            status = check.get("status", "unknown")
            if status not in VALID_CHECK_STATUSES:
                add(errors, "CHECK_STATUS_INVALID", event=eid, status=status)
            for ref in refs(check.get("evidence_refs")):
                if ref not in by_ref:
                    add(errors, "CHECK_EVIDENCE_MISSING", event=eid, ref=ref)
                elif by_ref[ref]["paragraph"] != paragraph:
                    add(errors, "CHECK_EVIDENCE_CROSS_PARAGRAPH", event=eid, ref=ref)
        # Surface supplied actors/subjects rather than treating them as source
        # facts.  No such field is accepted silently.
        for field in ("actor", "agent", "subject"):
            if event.get(field) and not any(event.get(k) for k in (f"{field}_ref", f"{field}_refs", "evidence_refs")):
                warnings.append({"kind": "SUPPLIED_ACTOR_OR_SUBJECT_UNSOURCED", "event": eid, "field": field})
        if not isinstance(event.get("supplied", []), list) or not all(isinstance(item, str) for item in event.get("supplied", [])):
            add(errors, "EVENT_SUPPLIED_SCHEMA", event=eid)
        rows.append(consequence_row(event, index, by_ref, entity_map, lex))
    action_set = set(action_refs)
    for ref in action_refs:
        if trigger_counts.get(ref, 0) != 1:
            add(errors, "ACTION_EVENT_COVERAGE", ref=ref, event_count=trigger_counts.get(ref, 0))
    for trigger, count in trigger_counts.items():
        if trigger not in action_set:
            add(errors, "NON_ACTION_EVENT_TRIGGER", ref=trigger, event_count=count)
    for producer, output_entities in producers.items():
        if producer not in event_map:
            add(errors, "ENTITY_PRODUCER_EVENT_MISSING", producer=producer, entities=output_entities)
        elif not set(output_entities) <= set(refs(event_map[producer].get("outputs"))):
            add(errors, "ENTITY_PRODUCER_NOT_DECLARED_OUTPUT", producer=producer, entities=output_entities)
    for entity in entities:
        if isinstance(entity, dict) and entity.get("origin") == "event" and not entity.get("producer"):
            add(errors, "EVENT_ENTITY_PRODUCER_MISSING", entity=entity.get("id"))
    # Two known narrative bridges are explicitly marked as supplied.  Their
    # presence is checked here so they cannot become hidden source facts.
    for clause in model.get("clauses", []) if isinstance(model.get("clauses", []), list) else []:
        if not isinstance(clause, dict):
            continue
        text = str(clause.get("process_text", "")).lower()
        supplied = " ".join(str(x) for x in clause.get("supplied", [])).lower()
        if clause.get("id") == "C09" and "nimm" in text and "nimm" not in supplied:
            add(errors, "SUPPLIED_NIMM_NOT_MARKED", clause="C09")
        if clause.get("id") == "C02" and "zweiten" in text and not any(term in supplied for term in ("zweite", "ansatz")):
            add(errors, "SUPPLIED_SECOND_PORTION_NOT_MARKED", clause="C02")
    cycles = producer_cycles([e for e in events if isinstance(e, dict)], [e for e in entities if isinstance(e, dict)])
    if cycles:
        add(errors, "PRODUCER_CYCLES", cycles=cycles)
    event_positions = {e.get("id"): i for i, e in enumerate(events) if isinstance(e, dict)}
    for eid, event in event_map.items():
        for entity_id in refs(event.get("inputs")):
            producer = entity_map.get(entity_id, {}).get("producer")
            if producer in event_positions and event_positions[producer] >= event_positions[eid] and producer != eid:
                add(errors, "ENTITY_PRODUCER_AFTER_USE", event=eid, entity=entity_id, producer=producer)
    compare_declared_matrix(model, rows, errors)
    singleton_forms = {r["raw"] for r in records if sum(x["raw"] == r["raw"] for x in records) == 1}
    requirement_counts = Counter(req["verdict"] for row in rows for req in row.get("requirements", []))
    stats = {"entities": len(entities), "events": len(events), "action_occurrences": len(action_refs), "action_event_gaps": sum(1 for ref in action_refs if trigger_counts.get(ref, 0) != 1), "singleton_trigger_events": sum(1 for row in rows if row.get("trigger_form") in singleton_forms), "producer_cycles": cycles, "contradiction_checks": sum(row["contradiction"] for row in rows), "unknown_checks": sum(row["unknown"] for row in rows), "requirement_results": dict(requirement_counts)}
    return stats, rows


def main() -> int:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checked_locks = check_lock(errors)
    source = load(SOURCE_REL)
    model = load(MODEL_REL)
    source_audit = check_source(source, errors)
    records, by_ref, paragraphs = records_for_source(source, errors)
    lex_stats = check_lexicon(model, records, errors)
    clause_stats = check_clauses(model, by_ref, records, errors)
    revision_stats = check_revisions(model, errors)
    event_stats, matrix = check_events(model, records, by_ref, errors, warnings)
    candidate_stats = check_candidate_artifacts(source, model, matrix, errors)
    rival = model.get("rival", model.get("rival_note"))
    rival_text = json.dumps(rival, ensure_ascii=False) if isinstance(rival, (dict, list)) else str(rival or "")
    if not rival_text.strip():
        add(errors, "RIVAL_MISSING")
    if not any(word in rival_text.lower() for word in ("catalog", "k retains", "does not assert", "rival")):
        warnings.append({"kind": "RIVAL_DESCRIPTION_UNCLEAR"})
    result = {
        "experiment": "GDT948",
        "status": "PASS" if not errors else "FAIL",
        "independent": True,
        "locked_files": checked_locks,
        "source": source_audit,
        "coverage": {"lines": len(source.get("lines", [])), "tokens": len(records), "paragraphs": list(paragraphs), **lex_stats, **clause_stats, **revision_stats},
        "events": event_stats,
        "core_consequence_matrix": matrix,
        "candidate_audit": candidate_stats,
        "errors": errors,
        "warnings": warnings,
        "meaning_confirmed": False,
        "semantics_validated": False,
        "scoring": False,
        "claim_ceiling": "conditional joint process/catalogue presentation; no confirmed words, plant names, event history, or independent meaning test",
    }
    out = EXP / "artifacts" / "VALIDATION.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
