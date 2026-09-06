"""Independent regression tests for local corrections and conditional priorities."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import semantic_ideas as ideas
from tools import semantic_identity as identity
from tools import semantic_priority_view as priority


class SemanticPriorityViewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'research_registry/decisions').mkdir(parents=True)
        for name, text in [('claim.md', 'The candidate might denote powder.'),
                           ('priority.md', 'An independent contrast is required.'),
                           ('dossier.md', 'The previous test lacked a matched pair.'),
                           ('local.md', 'B3 is a closure rendering, not a word.')]:
            (self.root / name).write_text(text + '\n')
        (self.root / 'research_registry/semantic_inventory.jsonl').write_text(
            '{"id":"SOURCE"}\n')
        for relative in ideas.REVIEWS:
            (self.root / relative).write_text(json.dumps({'cards': [], 'dispositions': []}))
        card = dict(id='PUBLIC', claim='The candidate might denote powder.',
                    claim_type='lexical_hypothesis', member_ids=['SOURCE'],
                    evidence=[self.evidence('claim.md')], status='unconfirmed', ready=False)
        (self.root / ideas.REVIEWS[0]).write_text(json.dumps({'cards': [card], 'dispositions': []}))
        ideas.build(self.root)
        self.card = ideas.registry.read_jsonl(self.root / ideas.DATA)[0]
        self.target = self.card['id']
        self.dossier = dict(
            id='DOSSIER:1', decision_key='DOSSIER', previous_revision=None,
            status='reviewed_scoped_context', targets=[self.target],
            card_basis={self.target: ideas.card_basis(self.card)},
            effective_basis={self.target: identity.effective_basis(self.card)},
            evidence=[self.evidence('dossier.md')], scope='Only the fixed previous test.',
            claim_ceiling='No general rejection of the powder hypothesis.')
        self.write(ideas.FAILURES, [self.dossier])
        self.row = dict(
            id='PRIORITY:1', decision_key='PRIORITY', previous_revision=None,
            rank=1, question='Would an independent contrast distinguish the meanings?',
            readiness='conditional_only', scientific_test_ready=False,
            sem_ids=[self.target], card_basis=self.dossier['card_basis'].copy(),
            effective_basis=self.dossier['effective_basis'].copy(),
            dossier_keys=['DOSSIER'], dossier_basis={'DOSSIER': self.digest(self.dossier)},
            evidence=[self.evidence('priority.md')], next_work_object='Locate a qualifying pair.',
            outcome_decisions={'absent': 'Do not run', 'present': 'Review source eligibility'},
            smallest_adequate_check='Check one independently owned pair.',
            blockers=['No matched pair'], changed_inputs={'available': False},
            budget_minutes=5, scope='Conditional priority; not an accepted meaning.')
        self.write(priority.DATA, [self.row])

    @staticmethod
    def digest(value):
        return hashlib.sha256(ideas.registry.canonical(value).encode()).hexdigest()

    def evidence(self, name):
        path = self.root / name
        return dict(path=name, line=1, quote=path.read_text().splitlines()[0],
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    def write(self, relative, rows):
        ideas.registry.write_jsonl(self.root / relative, rows)

    def test_priority_rank_is_not_support_or_permission_and_pages_are_bounded(self):
        rows = [dict(self.row, id=f'P:{n}', decision_key=f'P{n}', rank=n)
                for n in range(1, 8)]
        self.write(priority.DATA, list(reversed(rows)))
        pages = [priority.get_page(self.root, limit=3, offset=n) for n in (0, 3, 6)]
        self.assertEqual([len(p['results']) for p in pages], [3, 3, 1])
        self.assertEqual([p['next_offset'] for p in pages], [3, 6, None])
        self.assertEqual([r['rank'] for p in pages for r in p['results']], list(range(1, 8)))
        self.assertTrue(all(r['scientific_test_ready'] is False for p in pages for r in p['results']))
        self.assertIn('neither support', pages[0]['scope'])
        self.assertEqual(ideas.show(self.root, self.target)['status'], 'unconfirmed')
        self.assertIs(ideas.show(self.root, self.target)['ready'], False)
        for limit, offset in [(0, 0), (21, 0), (2, -1)]:
            with self.subTest(limit=limit, offset=offset), self.assertRaises(ValueError):
                priority.get_page(self.root, limit=limit, offset=offset)
        self.assertEqual(priority.get_page(self.root, 'no-match')['matched'], 0)

    def test_priority_cannot_set_execution_ready(self):
        self.write(priority.DATA, [dict(self.row, scientific_test_ready=True)])
        with self.assertRaisesRegex(ValueError, 'approve execution'):
            priority.get_page(self.root)

    def test_changed_direct_priority_source_blocks_cached_view(self):
        priority.get_page(self.root)
        (self.root / 'priority.md').write_text('The contrast requirement changed.\n')
        with self.assertRaises(ValueError):
            priority.get_page(self.root)

    def test_dossier_revision_requires_explicit_priority_rebinding(self):
        priority.get_page(self.root)
        second = dict(self.dossier, id='DOSSIER:2', previous_revision='DOSSIER:1')
        self.write(ideas.FAILURES, [self.dossier, second])
        with self.assertRaisesRegex(ValueError, 'stale priority dossier'):
            priority.get_page(self.root)

    def test_dossier_only_source_change_blocks_cached_priority(self):
        # This source belongs neither to the card snapshot nor to priority evidence.
        priority.get_page(self.root)
        (self.root / 'dossier.md').write_text('A different limitation now applies.\n')
        with self.assertRaises(ValueError):
            priority.get_page(self.root)

    def test_declared_dossier_cannot_omit_its_hash_binding(self):
        self.write(priority.DATA, [dict(self.row, dossier_basis={})])
        with self.assertRaises(ValueError):
            priority.get_page(self.root)

    def test_dossier_target_basis_is_checked_even_with_matching_dossier_hash(self):
        dossier = copy.deepcopy(self.dossier)
        dossier['card_basis'][self.target] = '0' * 64
        self.write(ideas.FAILURES, [dossier])
        self.write(priority.DATA, [dict(self.row, dossier_basis={'DOSSIER': self.digest(dossier)})])
        with self.assertRaises(ValueError):
            priority.get_page(self.root)

    def test_dossier_target_outside_priority_cards_must_still_be_current(self):
        local = self.install_local()
        dossier = copy.deepcopy(self.dossier)
        dossier['targets'].append(local['id'])
        dossier['card_basis'][local['id']] = ideas.card_basis(local)
        dossier['effective_basis'][local['id']] = identity.effective_basis(local)
        self.write(ideas.FAILURES, [dossier])
        row = dict(self.row, dossier_basis={'DOSSIER': self.digest(dossier)})
        self.write(priority.DATA, [row])
        self.assertEqual(priority.get_page(self.root)['matched'], 1)
        # A scoped restatement invalidates the dossier even though the priority
        # itself lists only the unchanged public card.
        correction = self.correction(local, 'restate_scope', replacement={
            'claim': 'B3 marks completion of the current record.', 'claim_type': 'formal_role'})
        self.write('research_registry/runtime/semantic_local_corrections.jsonl', [correction])
        with self.assertRaises(ValueError):
            priority.get_page(self.root)

    def test_priority_proposition_binding_and_revision_chain_are_checked(self):
        bad = copy.deepcopy(self.row)
        bad['effective_basis'][self.target] = '0' * 64
        self.write(priority.DATA, [bad])
        with self.assertRaisesRegex(ValueError, 'stale priority proposition'):
            priority.get_page(self.root)
        second = dict(self.row, id='PRIORITY:2', rank=2)
        self.write(priority.DATA, [self.row, second])
        with self.assertRaisesRegex(ValueError, 'revision chain'):
            priority.get_page(self.root)
        second['previous_revision'] = self.row['id']
        self.write(priority.DATA, [self.row, second])
        self.assertEqual(priority.get_page(self.root)['results'][0]['id'], 'PRIORITY:2')
        self.assertEqual(len(ideas.registry.read_jsonl(self.root / priority.DATA)), 2)

    def install_local(self):
        runtime = self.root / 'research_registry/runtime'
        runtime.mkdir(exist_ok=True)
        local = dict(id='LOCAL_B3', claim='B3 means record complete.',
                     claim_type='lexical_hypothesis', member_ids=['LOCAL_SOURCE'],
                     evidence=[self.evidence('local.md')], status='unconfirmed', ready=False)
        (runtime / 'clean_local_review.json').write_text(json.dumps({'cards': [local]}))
        patcher = patch('tools.semantic_inventory.local_items', return_value=[{'id': 'LOCAL_SOURCE'}])
        patcher.start()
        self.addCleanup(patcher.stop)
        return ideas.local_cards(self.root)[0]

    def correction(self, card, action, **extra):
        return dict(id='LOCAL_CORRECTION:1', target=card['id'], previous_revision=None,
                    target_basis_sha256=ideas.card_basis(card), action=action,
                    reason='Original source defines a closure rendering, not a lexical word.',
                    evidence=[self.evidence('local.md')], **extra)

    def test_local_archive_removes_semantic_count_but_preserves_show_and_public_bytes(self):
        card = self.install_local()
        before = {p: (self.root / p).read_bytes() for p in [ideas.DATA, ideas.MANIFEST, ideas.ARCHIVE]}
        self.assertEqual(ideas.get_page(self.root)['matched'], 2)
        correction = self.correction(card, 'archive_source_error')
        self.write('research_registry/runtime/semantic_local_corrections.jsonl', [correction])
        self.assertEqual(ideas.get_page(self.root)['matched'], 1)
        for identifier in [card['id'], 'LOCAL_B3']:
            archived = ideas.show(self.root, identifier)
            self.assertEqual(archived['status'], 'source_extraction_withdrawn')
            self.assertIs(archived['ready'], False)
            self.assertEqual(archived['source_correction_history'][0]['id'], correction['id'])
            self.assertEqual(ideas.show(self.root, identifier, 'cases')['matched'], 1)
        self.assertEqual(before, {p: (self.root / p).read_bytes() for p in before})

    def test_local_restatement_changes_semantic_count_without_erasing_original(self):
        card = self.install_local()
        correction = self.correction(card, 'restate_scope', replacement={
            'claim': 'B3 marks completion of the current record.', 'claim_type': 'formal_role'})
        relative = 'research_registry/runtime/semantic_local_corrections.jsonl'
        self.write(relative, [correction])
        self.assertEqual(ideas.get_page(self.root)['matched'], 1)
        self.assertEqual(ideas.get_page(self.root, include_formal=True)['matched'], 2)
        current = ideas.show(self.root, 'LOCAL_B3')
        self.assertEqual(current['source_original_assertion']['claim'], card['claim'])
        self.assertEqual(current['claim_type'], 'formal_role')
        # Explicit append-only reversal restores the original hypothesis and counts.
        second = self.correction(card, 'retain_as_hypothesis')
        second.update(id='LOCAL_CORRECTION:2', previous_revision=correction['id'])
        self.write(relative, [correction, second])
        self.assertEqual(ideas.get_page(self.root)['matched'], 2)
        self.assertEqual(len(ideas.show(self.root, 'LOCAL_B3')['source_correction_history']), 2)

    def test_stale_or_broken_local_correction_is_not_silently_ignored(self):
        card = self.install_local()
        correction = self.correction(card, 'archive_source_error')
        second = dict(correction, id='LOCAL_CORRECTION:2')
        relative = 'research_registry/runtime/semantic_local_corrections.jsonl'
        self.write(relative, [correction, second])
        with self.assertRaisesRegex(ValueError, 'revision chain'):
            ideas.get_page(self.root)
        bad = dict(correction, target_basis_sha256='0' * 64)
        self.write(relative, [bad])
        with self.assertRaisesRegex(ValueError, 'changed corrected claim'):
            ideas.get_page(self.root)


if __name__ == '__main__':
    unittest.main()
