import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.identity_input_receipt import MANIFEST, check, main


class InputReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.required = [self.make('review_a'), self.make('relation_s'), self.make('peer_s')]
        self.write(MANIFEST, {'inputs': self.required})

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value))
        return p

    def make(self, name):
        relative = 'research_registry/decisions/' + name + '.json'
        p = self.write(relative, {'synthetic': name})
        return {'path': relative, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

    def test_exact_receipt_is_read_only_and_not_semantic_approval(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = check(self.root, self.required)
        self.assertEqual(result['status'], 'INPUT_COVERAGE_PASS')
        self.assertTrue(result['exact_set_match'])
        self.assertEqual(result['required_verified_count'], 3)
        self.assertIn('no novelty', result['meaning'])
        self.assertIn('not proof of reading', result['meaning'])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_larger_list_still_misses_required_relation_reviews(self):
        supplied = self.required[:1] + [self.make('extra_' + str(i)) for i in range(5)]
        result = check(self.root, supplied)
        self.assertGreater(result['declared_count'], result['required_count'])
        self.assertEqual(result['status'], 'INPUT_COVERAGE_INCOMPLETE')
        self.assertEqual(result['missing_required'], sorted(r['path'] for r in self.required[1:]))
        self.assertEqual(len(result['extra_declared']), 5)
        self.assertEqual(result['required_verified_count'], 1)

    def test_stale_declared_hash_with_current_manifest(self):
        supplied = [dict(x) for x in self.required]
        supplied[0]['sha256'] = '0' * 64
        result = check(self.root, supplied)
        self.assertEqual(result['status'], 'INPUT_COVERAGE_INCOMPLETE')
        self.assertEqual(len(result['stale_declared_hashes']), 1)
        self.assertEqual(result['stale_manifest_hashes'], [])

    def test_source_changed_blocks_even_when_both_recorded_hashes_match(self):
        self.write(self.required[0]['path'], {'synthetic': 'changed'})
        result = check(self.root, self.required)
        self.assertEqual(result['status'], 'INPUT_COVERAGE_INCOMPLETE')
        self.assertEqual(len(result['stale_manifest_hashes']), 1)
        self.assertEqual(len(result['stale_declared_hashes']), 1)

    def test_missing_file_and_complete_list_with_extras(self):
        extra = self.make('extra')
        result = check(self.root, self.required + [extra])
        self.assertEqual(result['status'], 'INPUT_COVERAGE_PASS')
        self.assertFalse(result['exact_set_match'])
        (self.root / self.required[0]['path']).unlink()
        result = check(self.root, self.required)
        self.assertEqual(result['missing_files'], [self.required[0]['path']])
        self.assertFalse(result['all_required_current'])

    def test_duplicate_and_unsafe_paths_rejected_before_hashing(self):
        with self.assertRaises(ValueError):
            check(self.root, self.required + self.required[:1])
        for name in ['../private.json', '/private.json', 'runtime/private.json', '.hidden/data.json']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                check(self.root, [{'path': name, 'sha256': '0' * 64}])
        link = self.root / 'research_registry/decisions/link.json'
        link.symlink_to(self.root / self.required[0]['path'])
        with self.assertRaises(ValueError):
            check(self.root, [{'path': str(link.relative_to(self.root)), 'sha256': '0' * 64}])

    def test_cli_diagnostics_are_bounded_with_exact_totals(self):
        name = 'research_registry/decisions/large_declaration.json'
        supplied = self.required + [self.make('extra_' + str(i)) for i in range(35)]
        self.write(name, {'inputs': supplied})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['--declared', name], root=self.root)
        result = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertNotIn('required_verified', result)
        self.assertEqual(len(result['extra_declared']), 20)
        self.assertEqual(result['extra_declared_count'], 35)
        self.assertEqual(result['truncated_fields'], ['extra_declared'])
        self.assertEqual(result['declared_count'], 38)
        self.assertEqual(len(check(self.root, supplied)['extra_declared']), 35)

    def test_explicit_nested_list_and_cli_dispatch(self):
        name = 'research_registry/decisions/proposal.json'
        self.write(name, {'prior_identity_screen': {'paths_and_hashes': self.required}})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['--declared', name, '--field', 'prior_identity_screen.paths_and_hashes'], root=self.root)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['declared_count'], 3)
        from tools.work_cli import main as work_main
        with patch('tools.identity_input_receipt.main', return_value=1) as called:
            self.assertEqual(work_main(['identity-inputs', '--declared', name]), 1)
            called.assert_called_once_with(['--declared', name])


if __name__ == '__main__':
    unittest.main()
