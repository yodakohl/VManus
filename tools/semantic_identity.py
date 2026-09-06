"""Source-bound, append-only judgments of proposition identity.

This is a navigation overlay, never an inference of meaning, test status, or
permission. Only latest approved decisions act. Explicit alternative/nonidentity
pairs constrain the entire transitive closure. No lexical matching is performed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RELATIONS = frozenset({'equivalent_proposition', 'alternative_to',
                       'related_not_equivalent', 'specializes'})
STATUSES = frozenset({'approved', 'rejected', 'proposed'})
MAX_PAGE = 100


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def original_basis(card):
    """Use the clean-card builder's original-assertion provenance contract."""
    from tools.semantic_ideas import card_basis
    return card_basis(card)


def effective_basis(card):
    """Also bind a scope-restated proposition, not just its archived original."""
    return _digest({key: card[key] for key in ('claim', 'claim_type')})


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')


def _evidence(root, evidence):
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('exact source evidence required')
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError('invalid evidence')
        path = item.get('path')
        _text(path, 'evidence path')
        rel = Path(path)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('evidence path must be within root')
        resolved = (root / rel).resolve()
        if not resolved.is_relative_to(root.resolve()):
            raise ValueError('evidence path escapes root')
        raw = resolved.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item.get('sha256'):
            raise ValueError('stale evidence hash')
        line = item.get('line')
        if type(line) is not int or line < 1:
            raise ValueError('invalid source line')
        quote = item.get('quote')
        _text(quote, 'evidence quote')
        quote_lines = quote.splitlines()
        source_lines = raw.decode('utf-8-sig').splitlines()
        if source_lines[line - 1:line - 1 + len(quote_lines)] != quote_lines:
            raise ValueError('inexact source quote')


def _structure(decision):
    if not isinstance(decision, dict):
        raise ValueError('decision must be an object')
    for field in ('id', 'decision_key', 'reviewer', 'reason'):
        _text(decision.get(field), field)
    if decision.get('relation') not in RELATIONS:
        raise ValueError('invalid identity relation')
    if decision.get('status') not in STATUSES:
        raise ValueError('invalid decision status')
    members = decision.get('member_ids')
    if not isinstance(members, list) or len(members) < 2:
        raise ValueError('at least two concrete member IDs required')
    for member in members:
        _text(member, 'member ID')
    if len(set(members)) != len(members):
        raise ValueError('duplicate member ID')
    if decision['relation'] != 'equivalent_proposition' and len(members) != 2:
        raise ValueError('directed and nonidentity relations require two IDs')
    if 'previous_revision' not in decision:
        raise ValueError('explicit previous_revision required')
    previous = decision['previous_revision']
    if previous is not None:
        _text(previous, 'previous_revision')
    for field in ('card_basis', 'effective_basis'):
        basis = decision.get(field)
        if not isinstance(basis, dict) or set(basis) != set(members):
            raise ValueError(f'{field} must bind every member exactly')
        for digest in basis.values():
            if (not isinstance(digest, str) or len(digest) != 64
                    or any(c not in '0123456789abcdef' for c in digest)):
                raise ValueError(f'invalid {field} hash')


def _latest(decisions):
    latest, seen = {}, set()
    for decision in decisions:
        _structure(decision)
        identifier, key = decision['id'], decision['decision_key']
        if identifier in seen:
            raise ValueError('duplicate decision ID')
        previous = latest.get(key)
        expected = previous['id'] if previous else None
        if decision['previous_revision'] != expected:
            raise ValueError('broken decision revision chain')
        seen.add(identifier)
        latest[key] = decision
    return latest


def _bounds(offset, limit):
    if type(offset) is not int or offset < 0:
        raise ValueError('offset must be nonnegative integer')
    if type(limit) is not int or not 1 <= limit <= MAX_PAGE:
        raise ValueError(f'limit must be 1..{MAX_PAGE}')


class IdentityIndex:
    """In-memory ID-only index, with bounded public views; no source-card edits."""

    def __init__(self, groups, relations, inactive_decision_ids):
        self._groups = groups
        self._ordered = sorted(groups)
        self._card_to_group = {card: group for group, members in groups.items()
                               for card in members}
        self._relations = relations
        self.inactive_decision_ids = tuple(inactive_decision_ids)

    @property
    def counts(self):
        return {'cards': len(self._card_to_group), 'groups': len(self._groups),
                'multi_member_groups': sum(len(x) > 1 for x in self._groups.values()),
                'relations': len(self._relations)}

    def lookup_cards(self, card_ids):
        """Return ID mappings only, bounded to 100 requested cards."""
        ids = list(card_ids)
        if len(ids) > MAX_PAGE:
            raise ValueError('too many card IDs')
        return {card: self._card_to_group.get(card) for card in ids}

    def page_groups(self, offset=0, limit=8):
        _bounds(offset, limit)
        return [{'id': key, 'member_count': len(self._groups[key])}
                for key in self._ordered[offset:offset + limit]]

    def get_group(self, group_id, offset=0, limit=8):
        _bounds(offset, limit)
        members = self._groups[group_id]
        return {'id': group_id, 'member_count': len(members),
                'member_ids': list(members[offset:offset + limit]), 'offset': offset}

    def page_relations(self, offset=0, limit=8):
        _bounds(offset, limit)
        return [dict(row, member_ids=list(row['member_ids']))
                for row in self._relations[offset:offset + limit]]


def build_index(cards, decisions, root: Path, archived_ids=()):
    """Validate latest judgments and compute constrained equivalence closure.

    An archived member disables its entire decision, rather than inventing a
    new subgroup. Superseded judgments retain history but have no current force.
    A stale latest judgment raises; it is never silently used or omitted.
    """
    root = Path(root)
    source = list(cards.values()) if isinstance(cards, dict) else list(cards)
    by_id = {card['id']: card for card in source}
    if len(by_id) != len(source):
        raise ValueError('duplicate source card IDs')
    archived = set(archived_ids)
    active_ids = set(by_id) - archived
    latest = _latest(decisions)
    operative, inactive = [], []
    for key in sorted(latest):
        decision = latest[key]
        members = decision['member_ids']
        if set(members) - set(by_id) - archived:
            raise ValueError('unknown decision card')
        if set(members) & archived:
            inactive.append(decision['id'])
            continue
        for member in members:
            card = by_id[member]
            if original_basis(card) != decision['card_basis'][member]:
                raise ValueError('stale original card basis')
            if effective_basis(card) != decision['effective_basis'][member]:
                raise ValueError('stale effective proposition')
        _evidence(root, decision.get('evidence'))
        if decision['status'] == 'approved':
            operative.append(decision)
    parent = {i: i for i in active_ids}
    size = dict.fromkeys(active_ids, 1)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    # Compute union first, then reject any global contradiction. This catches
    # both insertion orders, including a blocker added after earlier unions.
    for decision in operative:
        if decision['relation'] == 'equivalent_proposition':
            a = decision['member_ids'][0]
            for b in decision['member_ids'][1:]:
                ra, rb = find(a), find(b)
                if ra != rb:
                    if size[ra] < size[rb]:
                        ra, rb = rb, ra
                    parent[rb] = ra
                    size[ra] += size[rb]
    for decision in operative:
        if decision['relation'] in ('alternative_to', 'related_not_equivalent'):
            a, b = decision['member_ids']
            if find(a) == find(b):
                raise ValueError('equivalence closure crosses explicit nonidentity pair')
    components = {}
    for member in sorted(active_ids):
        components.setdefault(find(member), []).append(member)
    groups = {'IDENTITY:' + _digest(members): tuple(members)
              for members in components.values()}
    relations = [{'decision_id': d['id'], 'relation': d['relation'],
                  'member_ids': tuple(d['member_ids'])}
                 for d in operative if d['relation'] != 'equivalent_proposition']
    return IdentityIndex(groups, relations, inactive)


def read_decisions(path: Path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_decision(root: Path, path: Path, decision, cards, archived_ids=()):
    """Validate the resulting overlay under a lock, then append one JSON line.

    No existing history is rewritten. Rejected/proposed equivalence is not a
    claim of nonidentity. Callers must explicitly approve a nonidentity relation.
    """
    import fcntl
    import os
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+', encoding='utf-8') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        existing_text = stream.read()
        decisions = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
        _structure(decision)
        _evidence(Path(root), decision.get('evidence'))
        build_index(cards, decisions + [decision], Path(root), archived_ids)
        encoded = json.dumps(decision, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':'))
        if existing_text and not existing_text.endswith('\n'):
            stream.write('\n')
        stream.write(encoded + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    return decision['id']
