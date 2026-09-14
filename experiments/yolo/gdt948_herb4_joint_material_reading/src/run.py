#!/usr/bin/env python3
"""GDT948 deterministic dictionary/clause/event presentation audit."""
import csv, hashlib, io, json, re
from collections import Counter
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
SOURCE = "experiments/yolo/gdt948_herb4_joint_material_reading/src/SOURCE.json"
LOCK = "experiments/yolo/gdt948_herb4_joint_material_reading/PREREG_LOCK.json"

def read(rel): return json.loads((R / rel).read_text(encoding="utf-8"))
def tab(rows, fields):
    s = io.StringIO(); w = csv.DictWriter(s, fieldnames=fields, delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows); return s.getvalue()
def parse_ref(ref):
    m = re.fullmatch(r"(.+)#([1-9][0-9]*)", str(ref))
    return (m.group(1), int(m.group(2))) if m else (None, None)

def producer_cycles(events, entities):
    """Events depend on producers of their INPUT entities; in-place outputs add no edge."""
    emap = {e.get("id"): e for e in events}; ent = {e.get("id"): e for e in entities}
    graph = {eid: set() for eid in emap}
    for eid, ev in emap.items():
        for entity_id in ev.get("inputs", []):
            producer = ent.get(entity_id, {}).get("producer")
            if producer in graph and producer != eid: graph[eid].add(producer)
    found, done = [], set()
    def visit(node, path):
        if node in path:
            found.append(path[path.index(node):] + [node]); return
        if node in done: return
        for dep in graph[node]: visit(dep, path + [node])
        done.add(node)
    for eid in graph: visit(eid, [])
    return found

def action_trigger_gaps(action_refs, events):
    counts = Counter(e.get("trigger_ref") for e in events)
    return [(ref, counts.get(ref, 0)) for ref in action_refs if counts.get(ref, 0) != 1]

def _self_test():
    # Valid chain, genuine dependency cycle, and missing action trigger fixtures.
    chain_e = [{"id": "e1", "inputs": ["x"], "outputs": ["y"]}, {"id": "e2", "inputs": ["y"], "outputs": ["z"]}]
    chain_x = [{"id": "x"}, {"id": "y", "producer": "e1"}, {"id": "z", "producer": "e2"}]
    assert producer_cycles(chain_e, chain_x) == []
    cyc_e = [{"id": "e1", "inputs": ["z"], "outputs": ["y"]}, {"id": "e2", "inputs": ["y"], "outputs": ["z"]}]
    cyc_x = [{"id": "y", "producer": "e1"}, {"id": "z", "producer": "e2"}]
    assert producer_cycles(cyc_e, cyc_x)
    assert action_trigger_gaps(["a#1", "a#2"], [{"id": "e", "trigger_ref": "a#1"}]) == [("a#2", 0)]

def build(model=None):
    _self_test()
    # Verify the frozen registration before consuming model/source content.
    lock = read(LOCK)
    for rel, expected in lock["files"].items():
        got = hashlib.sha256((R / ("experiments/yolo/gdt948_herb4_joint_material_reading/src/" + rel if rel == "SOURCE.json" else "experiments/yolo/gdt948_herb4_joint_material_reading/" + rel)).read_bytes()).hexdigest()
        if got != expected: raise RuntimeError(f"frozen lock mismatch: {rel}")
    if model is None: model = read("experiments/yolo/gdt948_herb4_joint_material_reading/src/MODEL.json")
    src = read(SOURCE)
    records, by_ref, paragraphs = [], {}, {}
    for line in src["lines"]:
        locus, paragraph = line["locus"], line["paragraph"]
        paragraphs.setdefault(paragraph, []).append(locus)
        for i, raw in enumerate(line["tokens"], 1):
            ref = f"{locus}#{i}"
            rec = {"ref": ref, "locus": locus, "index": i, "paragraph": paragraph, "raw": raw}
            records.append(rec); by_ref[ref] = rec
    errors, warnings = [], []
    lex = model.get("lexicon", {})
    types = Counter(r["raw"] for r in records)
    missing = sorted(set(types) - set(lex)); extra = sorted(set(lex) - set(types))
    if missing: errors.append({"kind": "LEXICON_MISSING_TYPES", "items": missing})
    if extra: errors.append({"kind": "LEXICON_EXTRA_TYPES", "items": extra})
    for form, value in lex.items():
        if not isinstance(value, dict) or not {"process", "catalogue", "kind"} <= set(value): errors.append({"kind": "LEXICON_SCHEMA", "form": form})
    alignment = []
    for n, r in enumerate(records, 1):
        v = lex.get(r["raw"], {})
        alignment.append({"occurrence": n, "ref": r["ref"], "paragraph": r["paragraph"], "locus": r["locus"], "index": r["index"], "form": r["raw"], "frequency": types[r["raw"]], "process": v.get("process", "UNKNOWN"), "catalogue": v.get("catalogue", "UNKNOWN"), "kind": v.get("kind", "UNKNOWN")})

    def refs_of(item): return item.get("refs", []) if isinstance(item, dict) else []
    clauses = model.get("clauses", [])
    for kind, items in [("CLAUSE", clauses)]:
        ids = [x.get("id") for x in items]
        for ident, count in Counter(ids).items():
            if count > 1: errors.append({"kind": f"{kind}_DUPLICATE_ID", "id": ident, "count": count})
    seen = []
    clause_rows = []
    for c in clauses:
        cid, cp = c.get("id", ""), c.get("paragraph", "")
        rr = []
        for ref in refs_of(c):
            if ref not in by_ref: errors.append({"kind": "CLAUSE_REF_MISSING", "clause": cid, "ref": ref}); continue
            rr.append(ref); seen.append(ref)
            if by_ref[ref]["paragraph"] != cp: errors.append({"kind": "CLAUSE_PARAGRAPH_MISMATCH", "clause": cid, "ref": ref})
        raw_source = " ".join(by_ref[x]["raw"] for x in rr)
        clause_rows.append({"id": cid, "paragraph": cp, "refs": "|".join(rr), "source_text": raw_source, "process_text": c.get("process_text", ""), "catalogue_text": c.get("catalogue_text", ""), "supplied": "|".join(map(str, c.get("supplied", [])))})
    if len(seen) != len(set(seen)): errors.append({"kind": "CLAUSE_DUPLICATE_REFS", "count": len(seen) - len(set(seen))})
    if len(seen) != len(records) or set(seen) != set(by_ref): errors.append({"kind": "CLAUSE_PARTITION_NOT_EXACT", "expected": len(records), "seen": len(seen), "missing": sorted(set(by_ref) - set(seen))})

    entities = model.get("entities", []); entity_ids = [e.get("id") for e in entities]
    for ident, count in Counter(entity_ids).items():
        if count > 1: errors.append({"kind": "ENTITY_DUPLICATE_ID", "id": ident, "count": count})
    entity_map = {e.get("id"): e for e in entities}
    producers = {}
    for e in entities:
        eid, ep = e.get("id", ""), e.get("paragraph", "")
        if e.get("origin") not in {"external", "event"}: errors.append({"kind": "ENTITY_ORIGIN", "entity": eid})
        for ref in e.get("anchor_refs", []):
            if ref not in by_ref: errors.append({"kind": "ENTITY_ANCHOR_MISSING", "entity": eid, "ref": ref})
            elif by_ref[ref]["paragraph"] != ep: errors.append({"kind": "ENTITY_PARAGRAPH_MISMATCH", "entity": eid, "ref": ref})
        if e.get("producer"): producers.setdefault(e["producer"], []).append(eid)

    events = model.get("events", []); event_ids = [e.get("id") for e in events]
    for ident, count in Counter(event_ids).items():
        if count > 1: errors.append({"kind": "EVENT_DUPLICATE_ID", "id": ident, "count": count})
    event_map = {e.get("id"): e for e in events}; event_rows = []
    status_counts = Counter(); contradiction_rows = []; check_rows = []
    for ev in events:
        eid, ep, trigger = ev.get("id", ""), ev.get("paragraph", ""), ev.get("trigger_ref", "")
        tr = by_ref.get(trigger)
        if not tr: errors.append({"kind": "EVENT_TRIGGER_MISSING", "event": eid, "ref": trigger})
        elif tr["paragraph"] != ep: errors.append({"kind": "EVENT_PARAGRAPH_MISMATCH", "event": eid, "ref": trigger})
        elif lex.get(tr["raw"], {}).get("kind") != "ACTION": errors.append({"kind": "EVENT_TRIGGER_NOT_ACTION", "event": eid, "ref": trigger, "form": tr["raw"]})
        for x in ev.get("inputs", []) + ev.get("outputs", []):
            if x not in entity_map: errors.append({"kind": "EVENT_ENTITY_MISSING", "event": eid, "entity": x})
            elif entity_map[x].get("paragraph") != ep: errors.append({"kind": "EVENT_ENTITY_PARAGRAPH_MISMATCH", "event": eid, "entity": x})
        for field in ("requirements", "effects"):
            for state in ev.get(field, []):
                entity_id = state.get("entity") if isinstance(state, dict) else None
                if entity_id not in entity_map:
                    errors.append({"kind": "EVENT_STATE_ENTITY_MISSING", "event": eid, "field": field, "entity": entity_id})
                elif entity_map[entity_id].get("paragraph") != ep:
                    errors.append({"kind": "EVENT_STATE_PARAGRAPH_MISMATCH", "event": eid, "field": field, "entity": entity_id})
        for x in ev.get("outputs", []):
            if x in entity_map:
                declared_producer = entity_map[x].get("producer")
                if declared_producer and declared_producer != eid: errors.append({"kind": "OUTPUT_PRODUCER_MISMATCH", "event": eid, "entity": x, "declared_producer": declared_producer})
        checks = ev.get("checks", [])
        for check_index, check in enumerate(checks, 1):
            st = check.get("status", "unknown"); status_counts[st] += 1
            if st not in {"assumed", "source_link", "unknown", "contradiction"}: errors.append({"kind": "CHECK_STATUS_INVALID", "event": eid, "status": st})
            badrefs = [ref for ref in check.get("evidence_refs", []) if ref not in by_ref]
            if badrefs: errors.append({"kind": "CHECK_EVIDENCE_MISSING", "event": eid, "refs": badrefs})
            for ref in check.get("evidence_refs", []):
                if ref in by_ref and by_ref[ref]["paragraph"] != ep: errors.append({"kind": "CHECK_EVIDENCE_PARAGRAPH_MISMATCH", "event": eid, "ref": ref})
            if st == "contradiction": contradiction_rows.append({"event": eid, "claim": check.get("claim", ""), "evidence_refs": "|".join(check.get("evidence_refs", []))})
            check_rows.append({"event": eid, "paragraph": ep, "check_index": check_index, "claim": check.get("claim", ""), "evidence_refs": "|".join(check.get("evidence_refs", [])), "status": st})
        event_rows.append({"id": eid, "paragraph": ep, "trigger_ref": trigger, "verb": ev.get("verb", ""), "inputs": "|".join(ev.get("inputs", [])), "outputs": "|".join(ev.get("outputs", [])), "requirements": json.dumps(ev.get("requirements", []), ensure_ascii=False, separators=(",", ":")), "effects": json.dumps(ev.get("effects", []), ensure_ascii=False, separators=(",", ":")), "supplied": "|".join(map(str, ev.get("supplied", []))), "check_count": len(checks), "check_statuses": "|".join(sorted(set(c.get("status", "unknown") for c in checks))), "contradictions": sum(c.get("status") == "contradiction" for c in checks)})
    for eid, out_entities in producers.items():
        if eid not in event_map: errors.append({"kind": "ENTITY_PRODUCER_MISSING_EVENT", "event": eid, "entities": out_entities})
        else:
            declared = set(event_map[eid].get("outputs", []))
            for ent in out_entities:
                if ent not in declared: errors.append({"kind": "ENTITY_PRODUCER_NOT_OUTPUT", "event": eid, "entity": ent})
    for e in entities:
        if e.get("origin") == "event" and not e.get("producer"): errors.append({"kind": "EVENT_ENTITY_MISSING_PRODUCER", "entity": e.get("id")})
    # Producer graph follows INPUT entities only; in-place state updates add no edge.
    cycles = producer_cycles(events, entities)
    if cycles: errors.append({"kind": "PRODUCER_CYCLES", "cycles": cycles})
    action_refs = [r["ref"] for r in records if lex.get(r["raw"], {}).get("kind") == "ACTION"]
    action_gaps = action_trigger_gaps(action_refs, events)
    for ref, count in action_gaps:
        errors.append({"kind": "ACTION_TRIGGER_COVERAGE", "ref": ref, "event_count": count})

    # Full two-reader clause presentation, preserving explicit supplied text.
    md = ["# GDT948 HERB4 clause readings", "", "Process and descriptive catalogue readings are both model outputs; neither is a confirmed translation.", ""]
    for p in sorted(paragraphs):
        md += [f"## {p}", ""]
        for c in [x for x in clause_rows if x["paragraph"] == p]:
            md += [f"### {c['id']}", f"Refs: `{c['refs']}`", "", f"**Source:** `{c['source_text']}`", "", f"**Process:** {c['process_text']}", "", f"**Catalogue:** {c['catalogue_text']}", "", f"**Supplied:** {c['supplied'] or '(none)'}", ""]
    rival = model.get("rival", model.get("rival_note", ""))
    md += ["## Rival", json.dumps(rival, ensure_ascii=False) if isinstance(rival, (dict, list)) else str(rival), ""]
    outputs = {
        "ALIGNMENT.tsv": tab(alignment, ["occurrence", "ref", "paragraph", "locus", "index", "form", "frequency", "process", "catalogue", "kind"]),
        "CLAUSES.md": "\n".join(md),
        "CLAUSES.tsv": tab(clause_rows, ["id", "paragraph", "refs", "source_text", "process_text", "catalogue_text", "supplied"]),
        "EVENTS.tsv": tab(event_rows, ["id", "paragraph", "trigger_ref", "verb", "inputs", "outputs", "requirements", "effects", "supplied", "check_count", "check_statuses", "contradictions"]),
        "CHECKS.tsv": tab(check_rows, ["event", "paragraph", "check_index", "claim", "evidence_refs", "status"]),
        "CONTRADICTIONS.tsv": tab(contradiction_rows, ["event", "claim", "evidence_refs"]),
        "ENTITIES.tsv": tab([{"id": e.get("id", ""), "paragraph": e.get("paragraph", ""), "label": e.get("label", ""), "origin": e.get("origin", ""), "anchor_refs": "|".join(e.get("anchor_refs", [])), "producer": e.get("producer", "")} for e in entities], ["id", "paragraph", "label", "anchor_refs", "producer", "origin"]),
        "RESULT.json": json.dumps({"experiment": "GDT948", "model_version": model.get("version", "unknown"), "status": "PRESENTATION_AUDIT_COMPLETE", "source_lines": len(src["lines"]), "source_tokens": len(records), "source_types": len(types), "lexicon_types": len(lex), "clauses": len(clauses), "clause_refs": len(seen), "entities": len(entities), "events": len(events), "checks": len(check_rows), "state_requirements": sum(len(e.get("requirements", [])) for e in events), "state_effects": sum(len(e.get("effects", [])) for e in events), "action_occurrences": len(action_refs), "action_trigger_gaps": len(action_gaps), "supplied_assumptions": sum(len(c.get("supplied", [])) for c in clauses) + sum(len(e.get("supplied", [])) for e in events), "supplied_evidence_refs": sum(len(c.get("evidence_refs", [])) for e in events for c in e.get("checks", [])), "check_statuses": dict(status_counts), "missing_sources": errors, "producer_cycles": cycles, "contradictions": len(contradiction_rows), "meaning_confirmed": False, "scoring": False, "rival": rival}, ensure_ascii=False, indent=2) + "\n"
    }
    outputs["README.md"] = """# GDT948 generated artifacts

`ALIGNMENT.tsv` covers all 145 source tokens and repeats each type frequency with its fixed process/catalogue/kind fields. `CLAUSES.md` presents each raw source line, process reading, descriptive catalogue reading, and supplied notes with complete refs. `CLAUSES.tsv` preserves the same fields. `EVENTS.tsv` retains inputs, outputs, requirements, and effects; `CHECKS.tsv`, `ENTITIES.tsv`, and `CONTRADICTIONS.tsv` expose every event check claim/evidence/status, missing producers, cycles, and contradictions. `RESULT.json` reports coverage and supplied evidence/status counts. Coverage is an audit result, not a semantic win; no meanings are confirmed and no scores are computed.
"""
    return outputs

def main():
    from consequences import build as build_consequences
    outputs = {**build(), **build_consequences()}
    for name, value in outputs.items(): (E / "artifacts" / name).write_text(value, encoding="utf-8")
    print(outputs["RESULT.json"], end="")
    return 0

if __name__ == "__main__": raise SystemExit(main())
