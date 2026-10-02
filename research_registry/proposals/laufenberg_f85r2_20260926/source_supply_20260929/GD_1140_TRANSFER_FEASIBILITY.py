#!/usr/bin/env python3
"""Bounded exploratory spelling feasibility; no meaning or syntax assignment.

Run from the repository root. Reads only the public GDT905 selected packet
and the frozen GDT1140 lexicon. Writes this dossier's single JSON result.
"""
import argparse
import hashlib
import json
from pathlib import Path


INPUTS = {
    "target": "experiments/yolo/gdt905_joint_cv_complete_passage_candidates/artifacts/TARGET.json",
    "scope": "experiments/yolo/gdt905_joint_cv_complete_passage_candidates/artifacts/SCOPE.json",
    "core": "experiments/yolo/gdt1140_fortune_status_whole_reading/CORE.json",
    "account": "experiments/yolo/gdt1140_fortune_status_whole_reading/artifacts/AUTHOR_ACCOUNT.json",
}


def reachable(word, lexicon):
    positions = {0}
    for start in range(len(word)):
        if start in positions:
            for primitive in lexicon:
                if word.startswith(primitive, start):
                    positions.add(start + len(primitive))
    return len(word) in positions


def substrings(word, old):
    return sorted(
        {word[i:j] for i in range(len(word)) for j in range(i + 1, len(word) + 1)} - old,
        key=lambda item: (len(item), item),
    )


def check(words, old):
    types = sorted(set(words), key=lambda word: (len(word), word))
    missing = [word for word in types if not reachable(word, old)]
    pairs = 0
    one_candidates = 0
    witness = [] if not missing else None
    if missing:
        # Any successful pair must contain at least one substring of the
        # first old-unreachable word. Trying all such u is exhaustive.
        for u in substrings(missing[0], old):
            one_candidates += 1
            remaining = [word for word in missing if not reachable(word, old | {u})]
            if not remaining:
                witness = [u]
                break
            # A successful second v must occur in the first word still
            # unreachable under old+u; otherwise it cannot help that word.
            for v in substrings(remaining[0], old):
                pairs += 1
                if all(reachable(word, old | {u, v}) for word in remaining):
                    witness = [u, v]
                    break
            if witness is not None:
                break
    return {
        "word_count": len(words),
        "type_count": len(types),
        "old_unreachable_types": missing,
        "old_unreachable_type_count": len(missing),
        "first_primitive_candidates_tested": one_candidates,
        "second_primitive_pairs_tested": pairs,
        "at_most_two_new_substrings_spelling_feasible": witness is not None,
        "witness": witness,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    documents = {}
    pins = {}
    for name, relative in INPUTS.items():
        raw = (args.root / relative).read_bytes()
        documents[name] = json.loads(raw)
        pins[name] = {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}
    old = frozenset(documents["core"]["lexicon"]) | frozenset(
        documents["account"]["extensions"]["primitive_entries"]
    )
    assert len(old) == 32 and all(old), "Unexpected frozen primitive inventory"
    rows = []
    selected_by_reader = {}
    for reader, packets in documents["target"]["panels"].items():
        count = 0
        for packet in packets:
            # Apply public registration's whole-packet length scope before
            # reading its words or making any language assessment.
            if not 12 <= len(packet["words"]) <= 24:
                continue
            assert not packet["page"].startswith("f84")
            assert packet["page"] != "f116v"
            count += 1
            rows.append({
                "reader": reader,
                "page": packet["page"],
                "paragraph_id": packet["paragraph_id"],
                "loci": sorted(set(packet["loci"])),
                **check(packet["words"], old),
            })
        assert count == documents["scope"][reader]["selected"]
        selected_by_reader[reader] = count
    assert len(rows) == 49 and len({row["paragraph_id"] for row in rows}) == 41
    result = {
        "status": "EXPLORATORY_SPELLING_FEASIBILITY_NOT_SEMANTIC_TEST",
        "inputs": pins,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "old_primitive_inventory": sorted(old),
        "old_primitive_count": len(old),
        "scope": "Only original public GDT905/906 12-24-group whole-passage cases",
        "rule": "Exact nonempty concatenation; unchanged old primitives plus at most two arbitrary new substrings; no spelling edits, omissions or new semantic assignments",
        "selection": "Exposed target-aware exploratory feasibility, not blind testing",
        "selected_by_reader": selected_by_reader,
        "selected_cases": len(rows),
        "distinct_paragraphs": len({row["paragraph_id"] for row in rows}),
        "min_old_unreachable_types": min(row["old_unreachable_type_count"] for row in rows),
        "pairs_tested": sum(row["second_primitive_pairs_tested"] for row in rows),
        "feasible_cases": sum(row["at_most_two_new_substrings_spelling_feasible"] for row in rows),
        "limits": [
            "Necessary spelling condition only; no morpheme identification or valid operator arguments asserted",
            "Two-whole exceptions are a subset of the permitted arbitrary-substring additions",
            "No exclusion of other lexicons, budgets, passages, ordinary language or Voynich semantics",
            "Alternative readers describe one manuscript, not independent confirmations",
        ],
        "cases": rows,
    }
    destination = Path(__file__).with_suffix(".json")
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "selected_cases", "distinct_paragraphs", "min_old_unreachable_types",
        "pairs_tested", "feasible_cases",
    )}))


if __name__ == "__main__":
    main()
