"""Synthetic offline registry tests: navigation must never authorize research."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools import research_registry as registry


def record(identifier, title='Synthetic shared topic', **updates):
    result = dict(id=identifier, kind='idea', aliases=[], title=title,
                  summary='Synthetic offline evidence fixture.', source_status='IMPORTED',
                  scope='unknown', review_status='imported_unreviewed', verdict='unreviewed',
                  blockers=[], reopen=dict(policy='unreviewed', all_of=[], not_sufficient=[]),
                  relations=[], sources=[], events=[])
    result.update(updates)
    return result


class RegistryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def snapshot(self, rows, manifest=None):
        registry.write_snapshot(self.root, rows, manifest)
        return registry.build_index(self.root)

    def test_ten_thousand_records_bounded_search_and_no_title_merging(self):
        rows = [record(f'IP{i:05d}', title='Shared synthetic constellation') for i in range(10000)]
        self.snapshot(rows)
        default = registry.search(self.root, 'constellation')
        self.assertGreater(len(default['results']), 0)
        self.assertLessEqual(len(default['results']), 8)
        maximum = registry.search(self.root, 'constellation', limit=20)
        self.assertEqual(len(maximum['results']), 20)
        self.assertEqual(len({x['id'] for x in maximum['results']}), 20)
        for identifier in ['IP00000', 'IP09999']:
            self.assertIn(identifier, json.dumps(registry.show(self.root, identifier)))

    def test_exact_alias_lookup_does_not_resolve_a_prefix(self):
        self.snapshot([record('IP001', aliases=['EXACT_ALIAS']),
                       record('IP002', aliases=['EXACT_ALIAS_LONGER'])])
        self.assertIn('IP001', json.dumps(registry.show(self.root, 'EXACT_ALIAS')))
        with self.assertRaises((ValueError, KeyError)):
            registry.show(self.root, 'EXACT_ALIA')

    def test_same_title_and_summary_preserve_distinct_records(self):
        self.snapshot([record('IP001'), record('IP002')])
        self.assertEqual({x['id'] for x in registry.search(self.root, 'shared')['results']},
                         {'IP001', 'IP002'})

    def test_canonical_jsonl_change_cannot_leave_search_index_silently_stale(self):
        self.snapshot([record('IP001', title='Oldfixturetoken')])
        registry.write_snapshot(self.root, [record('IP001', title='Newfixturetoken')])
        result = registry.search(self.root, 'Newfixturetoken')
        self.assertEqual([x['id'] for x in result['results']], ['IP001'])

    def test_source_content_change_is_detected(self):
        source = self.root / 'docs/source.md'
        source.parent.mkdir()
        source.write_text('original synthetic source\n')
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest = dict(version=1, sources=[dict(path='docs/source.md', sha256=sha)])
        self.snapshot([record('IP001')], manifest)
        source.write_text('changed synthetic source\n')
        result = registry.check_registry(self.root)
        self.assertNotEqual(result['status'], 'PASS')
        self.assertTrue(result['errors'])

    def test_unreviewed_record_cannot_be_reopened_by_more_pages(self):
        self.snapshot([record('IP001')])
        with self.assertRaises(ValueError):
            registry.reconsider(self.root, 'IP001', ['more_pages'], [])
        result = registry.reconsider(self.root, 'IP001', ['new_data'], [])
        self.assertNotEqual(result.get('decision'), 'RECONSIDERATION_REVIEW_REQUIRED')
        self.assertNotIn(result.get('decision'), ['APPROVED', 'ELIGIBLE', 'REOPENED'])

    def curate(self, verdict='not_tested', policy='conditional', requirements=None):
        report = self.root / 'docs/report.md'
        report.parent.mkdir(exist_ok=True)
        report.write_text('Synthetic reviewed report, no manuscript data.\n')
        requirements = requirements or [dict(id='new_relation', change='new_data',
            detail='Independent relation required', evidence=['docs/report.md'])]
        curation = dict(record_id='IP001', scope='semantic', verdict=verdict,
                        blockers=[], relations=[], reopen=dict(policy=policy,
                        all_of=requirements, not_sufficient=['More unqualified pages']))
        (self.root / 'research_registry/curation.jsonl').write_text(json.dumps(curation)+'\n')
        registry.bind_curations(self.root)
        registry.build_index(self.root)

    def test_missing_report_prevents_review_candidate(self):
        self.snapshot([record('IP001')])
        self.curate()
        (self.root / 'docs/report.md').unlink()
        result = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
        self.assertNotEqual(result.get('decision'), 'RECONSIDERATION_REVIEW_REQUIRED')

    def test_changed_bound_report_prevents_review_candidate(self):
        self.snapshot([record('IP001')])
        self.curate()
        (self.root / 'docs/report.md').write_text('Changed after review.\n')
        result = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
        self.assertNotEqual(result.get('decision'), 'RECONSIDERATION_REVIEW_REQUIRED')

    def test_no_evidence_and_partial_all_requirements_cannot_pass(self):
        self.snapshot([record('IP001')])
        self.curate(requirements=[
            dict(id='relation', change='new_data', detail='New relation', evidence=['docs/report.md']),
            dict(id='design', change='new_design', detail='Independent design', evidence=['docs/report.md'])])
        for changes, evidence in [(['new_data'], ['docs/report.md']),
                                  (['new_data', 'new_design'], [])]:
            result = registry.reconsider(self.root, 'IP001', changes, evidence)
            self.assertNotEqual(result.get('decision'), 'RECONSIDERATION_REVIEW_REQUIRED')

    def test_review_candidate_never_verifies_facts_or_approves(self):
        self.snapshot([record('IP001')])
        self.curate(requirements=[dict(id='coverage', change='new_data', detail='Three folios',
            evidence=['docs/report.md'], fact=dict(key='folios', op='gte', value=3))])
        result = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
        self.assertEqual(result['decision'], 'RECONSIDERATION_REVIEW_REQUIRED')
        self.assertIs(result['approved'], False)
        self.assertTrue(result['conditions'])
        self.assertTrue(all(x['verification']=='UNVERIFIED_CONTENT' for x in result['conditions']))

    def test_more_data_cannot_reopen_user_stop_or_failed_same_model(self):
        self.snapshot([record('IP001')])
        for verdict, policy, expected in [
                ('stopped_by_user', 'user_stopped', 'USER_STOP_NO_RERUN'),
                ('refuted_specific_model', 'conditional', 'SAME_MODEL_NOT_REOPENED'),
                ('nonconfirming', 'do_not_repeat_same_model', 'SAME_MODEL_NOT_REOPENED')]:
            with self.subTest(verdict=verdict):
                self.curate(verdict=verdict, policy=policy)
                result = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
                self.assertEqual(result['decision'], expected)
                self.assertIs(result['approved'], False)

    def test_search_limit_rejects_excess_before_unbounded_output(self):
        self.snapshot([record('IP001')])
        for limit in [0, -1, 21, 10000]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                registry.search(self.root, 'shared', limit=limit)

    def test_duplicate_ids_and_dangling_or_cyclic_identity_links_rejected(self):
        cases = [[record('IP001'), record('IP001')],
                 [record('IP001', relations=[dict(type='related_to', target='MISSING')])],
                 [record('IP001', relations=[dict(type='duplicate_of', target='IP002')]),
                  record('IP002', relations=[dict(type='supersedes', target='IP001')])]]
        for rows in cases:
            with self.subTest(rows=rows):
                registry.write_snapshot(self.root, rows)
                with self.assertRaises(ValueError):
                    registry.build_index(self.root)

    def test_source_paths_cannot_escape_through_symlink(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other)/'report.md'
            outside.write_text('Synthetic outside file')
            (self.root/'reports').symlink_to(Path(other), target_is_directory=True)
            registry.write_snapshot(self.root, [record('IP001', sources=[dict(path='reports/report.md')])])
            with self.assertRaises(ValueError):
                registry.build_index(self.root)

    def test_ambiguous_alias_fails_without_selecting_a_record(self):
        self.snapshot([record('IP001', aliases=['SAME']), record('IP002', aliases=['same'])])
        with self.assertRaises(ValueError):
            registry.show(self.root, 'same')

    def test_new_event_content_invalidates_review_but_row_movement_does_not(self):
        base = record('IP001', events=[dict(status='old', source_row=1)])
        moved = record('IP001', events=[dict(status='old', source_row=99)])
        changed = record('IP001', events=[dict(status='new', source_row=1)])
        self.assertEqual(registry.record_fingerprint(base), registry.record_fingerprint(moved))
        self.assertNotEqual(registry.record_fingerprint(base), registry.record_fingerprint(changed))
        self.snapshot([base])
        self.curate()
        registry.write_snapshot(self.root, [changed])
        result = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
        self.assertEqual(result['decision'], 'SOURCE_REVIEW_REQUIRED')
        self.assertIs(result['approved'], False)

    def test_large_detail_and_review_views_are_bounded_and_explicitly_truncated(self):
        self.snapshot([record('IP001')])
        self.curate(requirements=[dict(id=f'condition{i}', change='new_data',
            detail='long synthetic condition ' * 2000, evidence=['docs/report.md'])
            for i in range(40)])
        for result in [registry.show(self.root, 'IP001'),
                       registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])]:
            self.assertLessEqual(len(registry.canonical(result)), 12000)
            self.assertIs(result['_display_truncated'], True)
            self.assertIn('_continuation', result)
        self.assertIs(registry.reconsider(self.root, 'IP001', ['new_data'],
                                          ['docs/report.md'])['approved'], False)

    def test_search_paging_preserves_every_result_exactly_once(self):
        self.snapshot([record(f'IP{i:03d}') for i in range(25)])
        seen = []
        offset = 0
        while offset is not None:
            page = registry.search(self.root, 'shared', offset=offset)
            self.assertLessEqual(len(page['results']), 8)
            seen.extend(x['id'] for x in page['results'])
            next_offset = page['next_offset']
            if next_offset is not None:
                self.assertEqual(next_offset, offset + 8)
            offset = next_offset
        self.assertEqual(len(seen), 25)
        self.assertEqual(len(set(seen)), 25)

    def test_same_experiment_reference_preserves_distinct_history_identity(self):
        self.snapshot([record('GDT001', kind='attempt'),
                       record('HIST:one', kind='history', relations=[
                           dict(type='same_experiment_reference', target='GDT001')])])
        self.assertEqual(registry.show(self.root, 'HIST:one')['id'], 'HIST:one')
        self.assertEqual(registry.show(self.root, 'GDT001')['id'], 'GDT001')

    def test_corrupted_import_snapshot_fails_freshness_and_search(self):
        self.snapshot([record('IP001')])
        path=self.root/'research_registry/imported.jsonl'
        path.write_text(path.read_text().replace('Synthetic shared topic','Unregistered mutation'))
        self.assertEqual(registry.check_registry(self.root)['status'], 'FAIL')
        with self.assertRaises(ValueError):
            registry.search(self.root, 'mutation')

    def test_ten_thousand_identity_chain_does_not_recurse_or_merge(self):
        rows=[record(f'IP{i:05d}', relations=[dict(type='duplicate_of',target=f'IP{i+1:05d}')]
                     if i<9999 else []) for i in range(10000)]
        result=self.snapshot(rows)
        self.assertEqual(result['records'], 10000)
        self.assertEqual(registry.show(self.root,'IP00000')['id'],'IP00000')
        self.assertEqual(registry.show(self.root,'IP09999')['id'],'IP09999')

    def test_inherited_summary_cannot_be_review_candidate(self):
        self.snapshot([record('IP001')])
        self.curate()
        path=self.root/'research_registry/curation.jsonl'
        review=json.loads(path.read_text())
        review['assessment_basis']='registry_summary_only'
        path.write_text(json.dumps(review)+'\n')
        result=registry.reconsider(self.root,'IP001',['new_data'],['docs/report.md'])
        self.assertEqual(result['decision'],'SOURCE_REVIEW_REQUIRED')
        self.assertIs(result['approved'],False)
        self.assertEqual(registry.show(self.root,'IP001')['review'],'inherited_summary')

    def test_long_paged_requirements_never_skip_truncated_items(self):
        self.snapshot([record('IP001')])
        self.curate(requirements=[dict(id=f'c{i}',change='new_data',detail='long condition '*3000,
                                      evidence=['docs/report.md']) for i in range(35)])
        found=[];offset=0
        while offset is not None:
            result=registry.page_field(self.root,'IP001','requirements',limit=20,offset=offset)
            self.assertLessEqual(len(registry.canonical(result)),12000)
            self.assertTrue(result['items'])
            found.extend(x['id'] for x in result['items'])
            next_offset=result['next_offset']
            if next_offset is not None:self.assertEqual(next_offset,offset+len(result['items']))
            offset=next_offset
        self.assertEqual(found,[f'c{i}' for i in range(35)])

    def test_public_path_safety(self):
        self.assertTrue(registry.safe_relative_path('reports/source.md'))
        for path in ['/synthetic-fixture/record.md', '../outside.md', 'reports/../../outside.md',
                     'runtime/private.md', 'private/source.md', '.hidden/source.md']:
            with self.subTest(path=path):
                self.assertFalse(registry.safe_relative_path(path))


if __name__ == '__main__':
    unittest.main()
