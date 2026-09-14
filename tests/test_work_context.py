"""Bounded restart and live excerpts without reading manuscript/experiment payloads."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import work_context as context
from tools.work_cli import main as work_main

ROOT = Path(__file__).resolve().parents[1]


class ContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in [context.ROUTE, context.CATALOG, *context.SOURCES.values()]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())

    def edit_catalog(self, change):
        path = self.root / context.CATALOG
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False))

    def invoke(self, args):
        out = io.StringIO()
        with redirect_stdout(out):
            result = context.main(args, root=self.root)
        self.assertEqual(result, 0)
        return out.getvalue()

    def assert_cli_failure(self, args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), self.assertRaises(SystemExit) as failed:
            context.main(args, root=self.root)
        self.assertEqual(failed.exception.code, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertLess(len(err.getvalue().encode()), 1000)
        self.assertNotIn(str(self.root), err.getvalue())

    def test_live_contract_and_aliases(self):
        result = context.check(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertLessEqual(result['start_bytes'], 4096)
        self.assertLessEqual(result['largest_topic_bytes'], 6000)
        cases = {'Wortzusammensetzung': 'composition', 'Blattausschluss': 'transfer',
                 'Generationen': 'genealogy', 'Rezeptlesung': 'recipes',
                 'Chiffrierzustand': 'differential', 'keedy': 'forms'}
        for query, identifier in cases.items():
            with self.subTest(query=query):
                self.assertEqual(context.topic(self.root, query), context.topic(self.root, identifier))

    def test_cli_delegates_to_additive_module(self):
        with patch('tools.work_context.main', return_value=0) as delegated:
            self.assertEqual(work_main(['context', 'start']), 0)
        delegated.assert_called_once_with(['start'])

    def test_topics_are_paged_not_dumped(self):
        first = json.loads(self.invoke(['topics']))
        second = json.loads(self.invoke(['topics', '--offset', str(first['next_offset'])]))
        self.assertEqual(len(first['topics']), 8)
        ids = [x['id'] for x in first['topics'] + second['topics']]
        self.assertEqual(len(set(ids)), first['total'])
        self.assertIsNone(second['next_offset'])
        self.assertNotIn('blocks', first['topics'][0])

    def test_restart_is_constant_after_1000_extra_experiments(self):
        before_start = context.start(self.root)
        before_topic = context.topic(self.root, 'Wortzusammensetzung')
        archive = self.root / 'experiments'
        archive.mkdir()
        # Metadata fixture only: no real experiments are created or assessed.
        (archive / 'EXPERIMENT_INDEX.tsv').write_text(''.join(
            f'EXTRA{i:04}\tSynthetic unrelated archival record {i}\n' for i in range(1000)))
        (self.root / 'research_registry/imported.jsonl').write_text(''.join(
            json.dumps({'id': f'EXTRA{i:04}', 'summary': 'Synthetic history only'}) + '\n'
            for i in range(1000)))
        (archive / 'sealed_payload.tsv').write_text('MUST_NEVER_BE_READ\n')
        allowed = {self.root / context.ROUTE, self.root / context.CATALOG,
                   self.root / context.SOURCES['brief']}
        opened = set()
        original = Path.open

        def guarded(path, *args, **kwargs):
            self.assertIn(path, allowed, 'startup/topic attempted an unrelated payload read')
            opened.add(path)
            return original(path, *args, **kwargs)

        with patch.object(Path, 'open', guarded):
            self.assertEqual(context.start(self.root), before_start)
            self.assertEqual(context.topic(self.root, 'Wortzusammensetzung'), before_topic)
        self.assertEqual(opened, allowed)

    def test_resume_fields_cannot_disappear_or_duplicate(self):
        path = self.root / context.ROUTE
        original = path.read_text()
        for field in context.FIELDS:
            with self.subTest(field=field):
                path.write_text('\n'.join(line for line in original.splitlines()
                                          if not line.startswith(field + ':')))
                with self.assertRaisesRegex(ValueError, field):
                    context.start(self.root)
        path.write_text(original + '\nResume: second competing resume point\n')
        with self.assertRaisesRegex(ValueError, 'Resume'):
            context.start(self.root)

    def test_sealed_boundary_and_phase_are_checked(self):
        path = self.root / context.ROUTE
        original = path.read_text()
        path.write_text(original.replace('f84 and f84r remain sealed.', 'f84 and f84r are open.'))
        self.assert_cli_failure(['start'])
        path.write_text(original.replace('Phase: workflow', 'Phase: invented'))
        self.assert_cli_failure(['start'])

    def test_overlong_start_and_source_fail_without_truncation(self):
        path = self.root / context.ROUTE
        path.write_text(path.read_text() + 'ä' * 4096)
        self.assert_cli_failure(['start'])
        source = self.root / context.SOURCES['brief']
        source.write_text(source.read_text() + 'z' * context.SOURCE_BYTES)
        self.assert_cli_failure(['topic', 'composition'])

    def test_changed_source_is_live_and_hash_identifies_it(self):
        before = context.topic(self.root, 'composition')
        source = self.root / context.SOURCES['brief']
        source.write_text(source.read_text().replace(
            'Hierarchie an Leerstellen', 'UPDATED_FIXTURE Hierarchie an Leerstellen', 1))
        after = context.topic(self.root, 'composition')
        self.assertNotEqual(before, after)
        self.assertIn('UPDATED_FIXTURE', after)
        self.assertIn(hashlib.sha256(source.read_bytes()).hexdigest(), after)

    def test_missing_or_ambiguous_selectors_fail(self):
        source = self.root / context.SOURCES['map']
        original = source.read_text()
        row = next(line for line in original.splitlines() if line.startswith('| K02 —'))
        source.write_text(original.replace(row, ''))
        self.assert_cli_failure(['topic', 'forms'])
        source.write_text(original + '\n' + row + '\n')
        self.assert_cli_failure(['topic', 'forms'])

    def test_row_cannot_inherit_unrelated_table_header(self):
        source = self.root / context.SOURCES['map']
        original = source.read_text()
        header = '| ID / Thema | Vorhandener Befund | Grenze und Konsequenz für Weiterarbeit |\n|---|---|---|'
        source.write_text(original.replace(header, '', 1))
        self.assert_cli_failure(['topic', 'forms'])

    def test_no_arbitrary_sources_or_symlink_escape(self):
        self.edit_catalog(lambda d: d['topics'][0]['blocks'][0].update(source='experiments/sealed.tsv'))
        self.assert_cli_failure(['topic', 'composition'])
        (self.root / context.CATALOG).write_bytes((ROOT / context.CATALOG).read_bytes())
        source = self.root / context.SOURCES['brief']
        target = self.root / 'not_a_context_source.md'
        target.write_text('MUST_NOT_BE_READ')
        source.unlink()
        source.symlink_to(target)
        self.assert_cli_failure(['topic', 'composition'])

    def test_ambiguous_alias_unknown_query_and_bad_paging_fail(self):
        self.assert_cli_failure(['topic', 'unknown semantic family'])
        self.assert_cli_failure(['topics', '--limit', '9'])
        self.assert_cli_failure(['topics', '--offset', '-1'])
        self.edit_catalog(lambda d: d['topics'][1]['aliases'].append('Wortzusammensetzung'))
        self.assert_cli_failure(['topic', 'Wortzusammensetzung'])

    def test_overlong_complete_topic_and_list_fail_not_clip(self):
        def expand(d):
            d['topics'][0]['blocks'] = [d['topics'][0]['blocks'][0]] * 4
        self.edit_catalog(expand)
        source = self.root / context.SOURCES['brief']
        source.write_text(source.read_text().replace('Hierarchie an Leerstellen', 'x' * 1400, 1))
        self.assert_cli_failure(['topic', 'composition'])
        def long_aliases(d):
            for index, record in enumerate(d['topics'][:8]):
                record['aliases'] = [f'alias{index}_{j}_' + 'x' * 65 for j in range(12)]
        self.edit_catalog(long_aliases)
        self.assert_cli_failure(['topics'])
        self.assertEqual(len(json.loads(self.invoke(['topics', '--limit', '1']))['topics']), 1)

    def test_bullet_excerpt_retains_limits_without_next_candidate(self):
        output = context.topic(self.root, 'Rezeptlesung')
        self.assertIn('W89', output)
        self.assertIn('Beschreibung', output)
        self.assertNotIn('Benennungsroute geparkt', output)
        closing = context.topic(self.root, 'closure')
        self.assertIn('Dependencies and ceiling', closing)
        self.assertIn('Decision and reopening condition', closing)
        self.assertNotIn('Append one material ledger row', closing)


if __name__ == '__main__':
    unittest.main()
