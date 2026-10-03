"""Bounded reverse-dependency navigation; never reads manuscript/report payloads.

Dependency references are not supersession edges. Original decisions remain
visible and missing metadata is never interpreted as absence of later research.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import deque
from pathlib import Path

from tools.experiment_lookup import lookup_experiments, normalize_id, render_lookup
from tools.vmanus_experiment import ROOT

NOTE = ("Dependency references are review leads, not supersession or reopening approval. "
        "Read later primary reports before reusing an old next-step proposal. "
        "No matches does not establish absent research; unindexed/prose-only links are not covered.")
EXPLORATION = ("Exploratory readings do not require an already confirmed word. "
               "A failed specific model does not reject its whole topic or erase earlier positives. "
               "Use frequency, grammar, image context and retained counterexamples to develop justified hypotheses; "
               "confirmation is a separate step. This lookup grants or denies no research permission.")


def lookup_with_followups(identifiers, *, index_path=None, transitive=False,
                          limit=4, offset=0):
    if not 1 <= limit <= 20 or offset < 0:
        raise ValueError("limit must be 1..20 and offset nonnegative")
    path = Path(index_path) if index_path is not None else ROOT / 'experiments/EXPERIMENT_INDEX.tsv'
    # Preserve original lookup's identity/schema validation and no partial output.
    try:
        before = path.read_bytes()
        cards = lookup_experiments(identifiers, index_path=path)
        if before != path.read_bytes():
            raise ValueError('experiment index changed during lookup; retry')
    except OSError as exc:
        raise ValueError(f'cannot read experiment index ({type(exc).__name__})') from exc
    reader = csv.DictReader(io.StringIO(before.decode('utf-8')), delimiter='\t')
    rows = list(reader)
    available = 'dependencies' in (reader.fieldnames or [])
    indexed = {normalize_id(row['experiment_id']): row for row in rows}
    reverse = {identifier: [] for identifier in indexed}
    missing = sum(not row.get('dependencies', '').strip() for row in rows)
    unresolved = []
    for identifier, row in indexed.items():
        dependencies = set()
        for token in row.get('dependencies', '').split(';'):
            if not token.strip():
                continue
            try:
                dependencies.add(normalize_id(token))
            except ValueError:
                unresolved.append(identifier + ': malformed dependency')
        for dependency in sorted(dependencies):
            if dependency not in reverse:
                unresolved.append(identifier + ': unindexed ' + dependency)
            elif int(dependency[3:]) < int(identifier[3:]):
                reverse[dependency].append(identifier)
            else:
                unresolved.append(identifier + ': non-earlier ' + dependency)
    for values in reverse.values():
        values.sort(key=lambda identifier: int(identifier[3:]))
    for card in cards:
        start = card['experiment_id']
        card['claim_ceiling'] = indexed[start].get('claim_ceiling', '')
        card['exploration_policy'] = EXPLORATION
        queue = deque([(start, 0)])
        distances = {start: 0}
        via = {}
        while queue:
            parent, depth = queue.popleft()
            for child in reverse[parent]:
                if child not in distances:
                    distances[child] = depth + 1
                    via[child] = [parent]
                    if transitive:
                        queue.append((child, depth + 1))
                elif distances[child] == depth + 1:
                    via[child].append(parent)
        ordered = sorted(via, key=lambda identifier: (distances[identifier], int(identifier[3:])))
        page = []
        for identifier in ordered[offset:offset + limit]:
            row = indexed[identifier]
            page.append(dict(experiment_id=identifier, distance=distances[identifier],
                             via=via[identifier], status=row['status'], question=row['question'],
                             primary_report=row['primary_report'],
                             claim_ceiling=row.get('claim_ceiling', '')))
        card['followups'] = dict(
            mode='transitive' if transitive else 'direct', total=len(ordered),
            offset=offset, limit=limit, items=page,
            next_offset=offset + limit if offset + limit < len(ordered) else None,
            index_sha256=hashlib.sha256(before).hexdigest(),
            dependency_column_available=available, rows_without_dependencies=missing,
            unresolved_dependency_count=len(unresolved), unresolved_dependency_examples=unresolved[:4], note=NOTE,
        )
    return cards


def render_followups(cards, *, json_output=False):
    if json_output:
        return json.dumps(cards, ensure_ascii=False, indent=2) + '\n'
    sections = []
    for card in cards:
        result = card['followups']
        lines = [render_lookup([card]).rstrip(),
                 '  original_claim_scope: ' + (' '.join(card['claim_ceiling'].split()) or '[not recorded; inspect primary]'),
                 f"  FOLLOWUP REVIEW: {result['total']} {result['mode']} higher-numbered indexed reference(s); "
                 f"showing {len(result['items'])} from offset {result['offset']}."]
        for item in result['items']:
            lines.extend([
                f"    {item['experiment_id']} via {','.join(item['via'])}: " + (' '.join(item['status'].split()) or '[not recorded]'),
                '      question: ' + (' '.join(item['question'].split()) or '[not recorded]'),
                '      claim_scope: ' + (' '.join(item['claim_ceiling'].split()) or '[not recorded; inspect primary]'),
                '      primary_report: ' + (' '.join(item['primary_report'].split()) or '[not recorded]'),
            ])
        if result['next_offset'] is not None:
            extra = ' --followups' if result['mode'] == 'transitive' else ''
            lines.append(f"  MORE: ./vmanus-work lookup {card['experiment_id']}{extra} "
                         f"--offset {result['next_offset']} --limit {result['limit']}")
        if result['mode'] == 'direct':
            lines.append(f"  CHAIN: ./vmanus-work lookup {card['experiment_id']} --followups")
        lines.append(f"  Coverage: index only; {result['rows_without_dependencies']} rows without dependencies.")
        if not result['dependency_column_available']:
            lines.append('  UNAVAILABLE: dependency column missing; reverse-reference coverage unavailable.')
        if result['unresolved_dependency_count']:
            lines.append(f"  INCOMPLETE: {result['unresolved_dependency_count']} unresolved dependency entries; "
                         + '; '.join(result['unresolved_dependency_examples']))
        lines.append('  ' + NOTE)
        lines.append('  ' + EXPLORATION)
        sections.append('\n'.join(lines))
    return '\n\n'.join(sections) + '\n'
