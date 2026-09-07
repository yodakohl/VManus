"""Read-only coverage view for source-reviewed semantic cards and scoped questions."""
from __future__ import annotations

import argparse
import json

from tools import research_registry as registry
from tools import semantic_ideas as ideas

ROOT = ideas.ROOT


def _question_id(row):
    return row.get("decision_key") or row.get("id")


def _source_case_ids(card):
    ids = []
    for case in card.get("cases", []):
        value = case.get("id")
        if value and value not in ids:
            ids.append(value)
    return ids


def _latest_questions(root):
    latest = {}
    seen = set()
    for decision in registry.read_jsonl(root / ideas.FAILURES):
        key = decision["decision_key"]
        expected = latest[key]["id"] if key in latest else None
        if decision["id"] in seen or decision.get("previous_revision") != expected:
            raise ValueError("broken scoped-assessment revision chain")
        seen.add(decision["id"])
        latest[key] = decision
    return latest


def get_page(root=ROOT, query="", without_question=False, include_formal=False,
             limit=8, offset=0):
    """Return bounded card/question coverage; never changes semantic inputs."""
    if not 1 <= limit <= 20 or offset < 0:
        raise ValueError("limit 1..20 and offset >=0 required")
    con = ideas.connect(root)
    con.close()
    rows = registry.read_jsonl(root / ideas.DATA)
    by_id = {card["id"]: card for card in rows}
    latest = _latest_questions(root)
    for decision in latest.values():
        if not decision.get("targets"):
            raise ValueError("scoped assessment needs at least one target")
        missing = [target for target in decision.get("targets", []) if target not in by_id]
        if missing:
            raise ValueError("scoped assessment target is missing: " + missing[0])
    # Validate each latest question once through the existing binding validator;
    # its returned decisions are then reused for all target cards.
    by_target = {card_id: [] for card_id in by_id}
    validated = set()
    for decision in latest.values():
        targets = decision.get("targets", [])
        if decision["decision_key"] in validated:
            continue
        checked = ideas.scoped_assessments(root, by_id[targets[0]])
        if decision["id"] not in {item["id"] for item in checked}:
            raise ValueError("latest scoped assessment was not validated")
        for item in checked:
            validated.add(item["decision_key"])
            for target in item.get("targets", []):
                if target in by_target and item not in by_target[target]:
                    by_target[target].append(item)
    query_terms = query.casefold().split()
    candidates = []
    for card in rows:
        if not include_formal and card.get("claim_type") == "formal_role":
            continue
        if query_terms:
            haystack = registry.canonical({"id": card.get("id"), "claim": card.get("claim"),
                                           "claim_type": card.get("claim_type")}).casefold()
            if not all(term in haystack for term in query_terms):
                continue
        assessments = by_target[card["id"]]
        question_ids = [_question_id(d) for d in assessments]
        if without_question and question_ids:
            continue
        candidates.append((card, question_ids))
    selected = candidates[offset:offset + limit]
    results = []
    for card, question_ids in selected:
        claim = card["claim"]
        results.append({"id": card["id"], "claim": claim[:600],
                        "claim_truncated": len(claim) > 600,
                        "claim_type": card["claim_type"],
                        "source_case_ids": _source_case_ids(card),
                        "source_case_count": len(_source_case_ids(card)),
                        "scoped_question_ids": question_ids,
                        "scoped_question_count": len(question_ids)})
    total_questions = sum(len(item[1]) for item in candidates)
    unique_questions = len({question for _, questions in candidates for question in questions})
    return {"results": results, "matched": len(candidates),
            "card_question_binding_count": total_questions,
            "unique_scoped_question_count": unique_questions,
            "next_offset": offset + len(results) if offset + len(results) < len(candidates) else None,
            "scope": "Public individual cards only, without local supplements or equivalent-card grouping. Source cases and directly bound scoped questions are distinct; coverage is not a scientific verdict or readiness decision.",
            "question_binding": "Only latest scoped assessments are shown; stale or dangling bindings raise an error."}


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--without-question", action="store_true")
    parser.add_argument("--include-formal", action="store_true")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 20 or args.offset < 0:
        parser.error("limit 1..20 and offset >=0 required")
    print(json.dumps(get_page(root, args.query, args.without_question,
                              args.include_formal, args.limit, args.offset),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
