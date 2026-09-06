"""Bounded, read-only navigation of explicitly selected source-review receipts.

No source text is opened. Interval relationships and recorded decisions never
imply proposition identity, full coverage, scientific status, or permission to
skip work. Review files must be explicitly enabled by the caller; no private
supplements, registry rebuild, or persistent cache is discovered automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

CONTAINERS = frozenset({
    'reviewed_blocks', 'results', 'source_reassessments', 'dispositions',
    'source_disposition_reviews',
})
OPEN_STATUSES = frozenset({
    'scope_open', 'scope_comparison_open', 'scope_unresolved_form_assignment',
    'unresolved_full_scope', 'unresolved_local_observation', 'pending',
    'not_yet_reviewed', 'not_fully_reviewed',
})
RECORDED_STATUSES = frozenset({
    'scoped_proposition_candidates', 'method_editorial_or_instance_only',
    'existing_explicit_proposition_or_instance', 'no_separate_semantic_proposition',
    'historical_full_assertion_recovered', 'historical_full_proposition_recovered',
    'existing_full_revision', 'existing_full_model_and_rival',
    'existing_model_instances', 'existing_model_exposition', 'existing_rule_instance',
    'existing_whole_reading', 'existing_whole_card_scope_revision',
    'existing_proposition_source_audit_only', 'method', 'result', 'heading_only',
    'incomplete_heading', 'edition_instance', 'edition_result',
    'formal_renderer_scope', 'synthetic_renderer_result', 'synthetic_roundtrip_result',
    'prospective_renderer_control', 'edition_and_prospective_method',
    'prospective_edition_task', 'formal_parse', 'formal_scope_assessment',
    'method_scope_limit', 'method_content_slot_licensing', 'method_artifact_pointer',
    'scope_limit', 'historical_model_assessment', 'rival_limit_and_prospective_gate',
    'incomplete_future_introduction', 'historical_rival_context',
})
MEANING = ('NAVIGATION_ONLY: no automatic skip, proposition identity, complete '
           'coverage, scientific verdict, or reopening authorization')


def _relative(value: str) -> str:
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('expected a safe relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or str(p) != value:
        raise ValueError('expected a normalized relative path')
    return value


def _review_path(root: Path, relative: str) -> Path:
    relative = _relative(relative)
    p = PurePosixPath(relative)
    if p.parts[:2] != ('research_registry', 'decisions') or p.suffix != '.json':
        raise ValueError('reviews must be explicitly enabled decisions/*.json files')
    path = root / relative
    if not path.resolve().is_relative_to((root / 'research_registry' / 'decisions').resolve()):
        raise ValueError('review symlink escapes decisions directory')
    return path


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _evidence(row: dict) -> list[dict]:
    value = row.get('evidence', [])
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []
    result = []
    for e in value:
        if not isinstance(e, dict):
            continue
        try:
            path = _relative(e.get('path'))
        except ValueError:
            continue
        start = e.get('line')
        end = e.get('line_end')
        if end is None and isinstance(e.get('quote'), str):
            end = start + max(1, len(e['quote'].splitlines())) - 1 if _positive_int(start) else None
        if end is None:
            end = start
        if not _positive_int(start) or not _positive_int(end) or end < start:
            continue
        result.append({'path': path, 'line': start, 'line_end': end,
                       'source_sha256': e.get('sha256')})
    return result


def _rows(document: dict):
    # Only source assessment containers: selections, exclusions, card evidence,
    # and arbitrary recursively nested references are deliberately not receipts.
    for key in sorted(CONTAINERS):
        rows = document.get(key, [])
        if not isinstance(rows, list):
            continue
        for i, row in enumerate(rows):
            if isinstance(row, dict) and isinstance(row.get('source_id'), str):
                yield f'/{key}/{i}', row


def _state(row: dict) -> str:
    decision = row.get('decision', row.get('original_decision'))
    if not isinstance(decision, str):
        return 'unknown'
    if decision in OPEN_STATUSES or any(t in decision.lower() for t in ('unresolved', 'pending')):
        return 'pending'
    if decision in RECORDED_STATUSES:
        return 'recorded_decision'
    return 'unknown'


def lookup(root: Path, *, review_paths: list[str], source_id: str | None = None,
           path: str | None = None, line: int | None = None,
           line_end: int | None = None, source_sha256: str | None = None,
           limit: int = 8, offset: int = 0) -> dict:
    """Return a bounded page of receipts; never reads the candidate source file.

    A hash match means caller-supplied metadata equals receipt metadata; this
    function does not claim to have freshly validated the source bytes.
    """
    if not 1 <= limit <= 20 or type(limit) is not int or type(offset) is not int or offset < 0:
        raise ValueError('limit must be 1..20 and offset must be nonnegative')
    if source_id is not None and (not isinstance(source_id, str) or not source_id):
        raise ValueError('source_id must be a nonempty string')
    if path is not None:
        path = _relative(path)
        line_end = line if line_end is None else line_end
        if not _positive_int(line) or not _positive_int(line_end) or line_end < line:
            raise ValueError('path queries require valid line and line_end')
    elif line is not None or line_end is not None:
        raise ValueError('line coordinates require path')
    if source_id is None and path is None:
        raise ValueError('provide source_id or path and coordinates')
    if source_sha256 is not None and (len(source_sha256) != 64 or any(c not in '0123456789abcdef' for c in source_sha256)):
        raise ValueError('source_sha256 must be a lowercase SHA256')
    if not review_paths:
        raise ValueError('explicit review_paths required')
    matches = []
    inputs = []
    for relative in sorted(set(review_paths)):
        raw = _review_path(root, relative).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        document = json.loads(raw.decode('utf-8-sig'))
        if not isinstance(document, dict):
            raise ValueError(f'expected review object: {relative}')
        inputs.append({'path': relative, 'sha256': digest})
        for pointer, row in _rows(document):
            exact = source_id is not None and row['source_id'] == source_id
            evidence = _evidence(row)
            related = []
            for e in evidence:
                if path is not None and e['path'] == path and not (line_end < e['line'] or line > e['line_end']):
                    relation = 'contains_span' if e['line'] <= line and e['line_end'] >= line_end else 'partial_overlap'
                    related.append({**e, 'relation': relation})
            if not exact and not related:
                continue
            relevant = related if related else evidence
            hashes = {e.get('source_sha256') for e in relevant}
            binding = 'unknown'
            if source_sha256 is not None and hashes:
                if hashes == {source_sha256}:
                    binding = 'matches_supplied_hash'
                elif all(isinstance(h, str) and len(h) == 64 for h in hashes):
                    binding = 'mismatch_or_conflict'
            full_read = any(row.get(k) is True for k in (
                'full_block_read', 'full_selected_span_read', 'full_report_context_read'))
            relationships = (['exact_id'] if exact else []) + sorted({e['relation'] for e in related})
            matches.append({
                'source_id': row['source_id'], 'relationships': relationships,
                'review_state': _state(row), 'full_read_recorded': full_read,
                'decision': str(row.get('decision', row.get('original_decision', '')))[:180],
                'original_decision': str(row.get('original_decision', ''))[:180],
                'reason': str(row.get('reason', ''))[:500],
                'source_binding': binding,
                'evidence': relevant[:8], 'evidence_count': len(relevant),
                'review_path': relative, 'review_sha256': digest, 'locator': pointer,
            })
    matches.sort(key=lambda r: ('exact_id' not in r['relationships'], r['review_path'], r['locator']))
    page = matches[offset:offset + limit]
    return {'results': page, 'matched': len(matches), 'limit': limit, 'offset': offset,
            'next_offset': offset + limit if offset + limit < len(matches) else None,
            'review_inputs': inputs, 'meaning': MEANING,
            'source_bytes_read': False}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.cwd())
    p.add_argument('--review', action='append', required=True, dest='review_paths')
    p.add_argument('--source-id')
    p.add_argument('--path')
    p.add_argument('--line', type=int)
    p.add_argument('--line-end', type=int)
    p.add_argument('--source-sha256')
    p.add_argument('--limit', type=int, default=8)
    p.add_argument('--offset', type=int, default=0)
    args = vars(p.parse_args(argv))
    root = args.pop('root')
    try:
        result = lookup(root, **args)
    except (ValueError, OSError) as e:
        p.error(str(e))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
