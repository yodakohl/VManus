"""Optional declared scope changes navigation coverage, never semantic identity."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from tools import research_registry as registry


class OptionalDesignScopeTests(unittest.TestCase):
    def setUp(self):
        self.design = dict(mechanism='Fixed  Rewrite', unit='Whole group',
                           contrast='Other construction', prediction='Same ordered output')

    def test_omitted_scope_duplicate_is_retrieved_without_merging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry.write_snapshot(root, [])
            registry.build_index(root)
            first = dict(title='First synthetic idea', summary='Unconfirmed first proposal.',
                         scope='semantic', design=self.design)
            second = dict(title='Second synthetic idea', summary='Unconfirmed second proposal.',
                          scope='structural', design={k: ' ' + v.upper() + ' ' for k, v in self.design.items()})
            one = registry.add_idea(root, first)['id']
            two = registry.add_idea(root, second)['id']
            result = registry.duplicates(root, proposal=first)
            self.assertEqual({row['id'] for row in result['same_declared_design']}, {one, two})
            self.assertEqual(result['decision'], 'CANDIDATES_ONLY_NO_AUTOMATIC_MERGE')
            self.assertEqual(len(registry.read_jsonl(root / registry.DIRECTORY / 'ideas.jsonl')), 2)
            # Top-level scope may change with review; it is not a declared design field.
            self.assertEqual(registry.design_fingerprint(first), registry.design_fingerprint(second))
            self.assertNotEqual(registry.design_fingerprint(first),
                                registry.design_fingerprint(dict(first, design=dict(self.design, scope='semantic'))))

    def test_old_five_field_hash_is_byte_identical(self):
        design = dict(self.design, scope='  One historical  REGIstER ')
        old_keys = ('mechanism', 'unit', 'contrast', 'prediction', 'scope')
        old_normalized = {k: ' '.join(design[k].casefold().split()) for k in old_keys}
        expected = hashlib.sha256(registry.canonical(old_normalized).encode()).hexdigest()
        self.assertEqual(registry.design_fingerprint(dict(design=design)), expected)

    def test_incomplete_or_invalid_supplied_fields_have_no_fingerprint(self):
        for missing in self.design:
            design = dict(self.design)
            del design[missing]
            with self.subTest(missing=missing):
                self.assertEqual(registry.design_fingerprint(dict(design=design)), '')
        for key in (*self.design, 'scope'):
            for invalid in (None, '', '  ', 7, False, [], {}):
                with self.subTest(key=key, invalid=invalid):
                    self.assertEqual(registry.design_fingerprint(
                        dict(design=dict(self.design, **{key: invalid}))), '')
        for design in (None, [], 'invalid'):
            with self.subTest(design=design):
                self.assertEqual(registry.design_fingerprint(dict(design=design)), '')


if __name__ == '__main__':
    unittest.main()
