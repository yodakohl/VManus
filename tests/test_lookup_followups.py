"""Regression tests for stale next-step navigation, without manuscript reads."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.lookup_followups import lookup_with_followups, render_followups


class FollowupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.index = Path(self.tmp.name) / 'index.tsv'
        self.rows = [self.row(939, '', 'C0_DRAFT'),
                     self.row(940, 'gdt00939', 'REJECT_FIXED_NOMINAL_EXTENSION'),
                     self.row(943, 'GDT939', 'UNSELECTED'),
                     self.row(944, 'GDT939;GDT943', 'UNSELECTED'),
                     self.row(945, 'GDT944', 'REJECTED'),
                     self.row(999, 'GDT9390', 'UNRELATED')]
        self.write()

    def row(self, number, dependencies, status):
        return dict(experiment_id=f'GDT{number}', dependencies=dependencies,
                    question=f'Question {number}?', status=status,
                    primary_report=f'reports/gdt{number}/REPORT.md')

    def write(self):
        with self.index.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.rows[0], delimiter='\t')
            writer.writeheader()
            writer.writerows(self.rows)

    def lookup(self, *ids, **kwargs):
        return lookup_with_followups(ids or ['GDT939'], index_path=self.index, **kwargs)

    def test_old_draft_automatically_exposes_failed_continuation(self):
        card = self.lookup()[0]
        self.assertEqual(card['status'], 'C0_DRAFT')
        later = card['followups']['items']
        self.assertEqual(later[0]['experiment_id'], 'GDT940')
        self.assertEqual(later[0]['status'], 'REJECT_FIXED_NOMINAL_EXTENSION')
        self.assertEqual([r['experiment_id'] for r in later], ['GDT940', 'GDT943', 'GDT944'])
        self.assertIn('not supersession', render_followups([card]))

    def test_transitive_branch_has_provenance_and_no_duplicate(self):
        result = self.lookup(transitive=True)[0]['followups']
        self.assertEqual(result['total'], 4)
        last = result['items'][-1]
        self.assertEqual((last['experiment_id'], last['distance'], last['via']),
                         ('GDT945', 2, ['GDT944']))

    def test_paging_preserves_immediate_then_distant_references(self):
        first = self.lookup(transitive=True, limit=2)[0]['followups']
        second = self.lookup(transitive=True, limit=2, offset=2)[0]['followups']
        self.assertEqual(first['next_offset'], 2)
        self.assertIsNone(second['next_offset'])
        self.assertEqual([x['experiment_id'] for x in second['items']], ['GDT944', 'GDT945'])
        self.assertIn('--followups --offset 2 --limit 2', render_followups(self.lookup(transitive=True, limit=2)))

    def test_no_references_is_not_absence_of_research(self):
        card = self.lookup('GDT945')[0]
        self.assertEqual(card['followups']['total'], 0)
        self.assertIn('No matches does not establish absent research', render_followups([card]))

    def test_later_failure_does_not_erase_positive_or_veto_exploration(self):
        for row in self.rows:
            row['claim_ceiling'] = 'Only this fixed model was evaluated.'
        self.rows[0]['status'] = 'POSITIVE_WITH_SUPPLIED_CANDIDATES'
        self.rows[0]['claim_ceiling'] = 'Supervised recovery supported; unknown inventories untested.'
        self.write()
        cards = self.lookup()
        rendered = render_followups(cards)
        self.assertIn('POSITIVE_WITH_SUPPLIED_CANDIDATES', rendered)
        self.assertIn('REJECT_FIXED_NOMINAL_EXTENSION', rendered)
        self.assertIn('Supervised recovery supported; unknown inventories untested.', rendered)
        self.assertIn('Only this fixed model was evaluated.', rendered)
        self.assertIn('do not require an already confirmed word', rendered)
        self.assertIn('grants or denies no research permission', rendered)
        self.assertEqual(json.loads(render_followups(cards, json_output=True))[0]['status'],
                         'POSITIVE_WITH_SUPPLIED_CANDIDATES')

    def test_missing_dependency_column_is_explicit(self):
        for row in self.rows:
            del row['dependencies']
        self.write()
        card = self.lookup()[0]
        self.assertFalse(card['followups']['dependency_column_available'])
        self.assertIn('UNAVAILABLE', render_followups([card]))

    def test_exact_ids_malformed_unknown_and_cycles(self):
        self.rows[0]['dependencies'] = 'GDT945'
        self.rows[1]['dependencies'] += ';bogus;GDT939/GDT944;GDT940'
        self.write()
        card = self.lookup(transitive=True)[0]
        self.assertEqual(card['followups']['total'], 4)
        self.assertEqual(card['followups']['unresolved_dependency_count'], 5)
        self.assertNotIn('GDT999 via', render_followups([card]))

    def test_duplicate_edges_normalized(self):
        self.rows[1]['dependencies'] = 'GDT939;gdt00939; GDT939 '
        self.write()
        self.assertEqual(self.lookup()[0]['followups']['total'], 3)

    def test_does_not_open_any_report_or_manuscript_payload(self):
        self.rows[1]['primary_report'] = 'sealed/f84r/REPORT.md'
        self.write()
        original = Path.open
        def guarded(path, *args, **kwargs):
            self.assertEqual(path, self.index)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', guarded):
            self.lookup(transitive=True)

    def test_invalid_requests_and_pagination_fail(self):
        for args, kwargs in [(['GDT999999'], {}), (['GDT939','gdt00939'], {}),
                             (['GDT939'], {'limit': 21}), (['GDT939'], {'offset': -1})]:
            with self.subTest(args=args, kwargs=kwargs), self.assertRaises(ValueError):
                self.lookup(*args, **kwargs)

    def test_missing_index_does_not_leak_private_path(self):
        self.index.unlink()
        with self.assertRaisesRegex(ValueError, r'^cannot read experiment index \(FileNotFoundError\)$'):
            self.lookup()

    def test_multiline_metadata_survives_and_json_keeps_limits(self):
        self.rows[1]['question'] = 'Whole\nquestion?'
        self.rows[1]['status'] = 'REJECTED\noriginal decision'
        self.rows[1]['primary_report'] = 'report\nname.md'
        self.write()
        cards = self.lookup()
        restored = json.loads(render_followups(cards, json_output=True))
        self.assertEqual(restored[0]['followups']['items'][0]['question'], 'Whole\nquestion?')
        self.assertEqual(len(restored[0]['followups']['index_sha256']), 64)
        rendered = render_followups(cards)
        self.assertIn(': REJECTED original decision\n', rendered)
        self.assertIn('primary_report: report name.md\n', rendered)
        self.assertEqual(restored[0]['followups']['items'][0]['status'], 'REJECTED\noriginal decision')

    def test_changed_index_fails_without_mixed_snapshot(self):
        original = Path.read_bytes
        count = 0
        def changed(path):
            nonlocal count
            count += 1
            return original(path) + (b'\n' if count == 2 else b'')
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'changed during lookup'):
            self.lookup()


if __name__ == '__main__':
    unittest.main()
