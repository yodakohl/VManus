"""Ingress quote fidelity; synthetic sources only, no semantic admissibility tests."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import research_registry as registry


class SourceQuoteIngressTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / 'docs/report.md'
        self.source.parent.mkdir()
        self.source.write_bytes('Heading\n  Größe bleibt\n    auf zwei Zeilen.\nTail\n'.encode())
        registry.write_snapshot(self.root, [])
        registry.build_index(self.root)
        self.evidence = dict(path='docs/report.md', line=2, line_end=3,
                             quote='  Größe bleibt\n    auf zwei Zeilen.',
                             sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.proposal = dict(title='Synthetic raw idea', summary='Unconfirmed speculation.',
                             scope='semantic', design=dict(source_evidence=self.evidence))

    def helper(self, evidence):
        return registry.validate_optional_design_source_evidence(
            self.root, dict(source_evidence=evidence))

    def review(self, identifier, **extra):
        return dict(record_id=identifier, reviewer='synthetic-test',
                    reason='Record a bounded source correction.', scope='semantic',
                    verdict='not_tested', blockers=[], relations=[],
                    reopen=dict(policy='unreviewed', all_of=[], not_sufficient=[]), **extra)

    def stored(self, name):
        path = self.root / registry.DIRECTORY / name
        return path.read_bytes() if path.exists() else None

    def test_literal_multiline_accepts_optional_end_and_bom(self):
        for with_end in (True, False):
            evidence = dict(self.evidence)
            if not with_end:
                evidence.pop('line_end')
            with self.subTest(with_end=with_end):
                self.helper(evidence)
        self.source.write_bytes(b'\xef\xbb\xbf' + self.source.read_bytes())
        evidence = dict(self.evidence, sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.helper(evidence)

    def test_no_evidence_keeps_raw_proposals_possible(self):
        registry.validate_optional_design_source_evidence(self.root, {})
        proposal = dict(self.proposal, design={})
        result = registry.add_idea(self.root, proposal)
        self.assertEqual(result['status'], 'UNTESTED_PROPOSAL')
        self.assertEqual(registry.show(self.root, result['id'])['verdict'], 'untested')

    def test_invalid_literal_hash_and_boundaries_are_rejected(self):
        variants = [
            dict(quote='Größe bleibt auf zwei Zeilen.'),
            dict(quote='  Größe bleibt\nauf zwei Zeilen.'),
            dict(line=1), dict(line=0), dict(line=True),
            dict(line_end=4), dict(line_end=1), dict(line_end=True),
            dict(sha256='0' * 64), dict(sha256='not-a-hash'),
            dict(quote=''), dict(path='docs/missing.md'),
        ]
        for delta in variants:
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                self.helper(dict(self.evidence, **delta))
        for missing in ('sha256', 'line', 'path', 'quote'):
            evidence = dict(self.evidence)
            evidence.pop(missing)
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                self.helper(evidence)
        for evidence in (None, 'quote', [self.evidence]):
            with self.subTest(shape=type(evidence).__name__), self.assertRaises(ValueError):
                self.helper(evidence)

    def test_unsafe_and_non_markdown_sources_are_rejected_before_content_read(self):
        blocked = self.root / 'docs/raw.tsv'
        blocked.write_text('selector\tpayload\nf84r\tMUST_NOT_READ\n')
        alias = self.root / 'docs/disguised.md'
        alias.symlink_to(blocked)
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if path.resolve() == blocked.resolve():
                raise AssertionError('Non-Markdown target content was accessed')
            return original_open(path, *args, **kwargs)

        for relative in ('docs/raw.tsv', 'docs/disguised.md', '../outside.md', '/outside.md'):
            with self.subTest(path=relative), patch.object(Path, 'open', guarded_open):
                with self.assertRaises(ValueError):
                    self.helper(dict(self.evidence, path=relative))

    def test_add_rejects_before_mutation_and_preserves_next_id(self):
        before = self.stored('ideas.jsonl')
        bad = copy.deepcopy(self.proposal)
        bad['design']['source_evidence']['quote'] = 'collapsed unsupported prose'
        with patch.object(registry, 'build_index', wraps=registry.build_index) as build:
            with self.assertRaises(ValueError):
                registry.add_idea(self.root, bad)
            build.assert_not_called()
        self.assertEqual(self.stored('ideas.jsonl'), before)
        result = registry.add_idea(self.root, self.proposal)
        self.assertEqual(result['id'], 'IDEA000001')

    def test_supplied_review_design_validates_before_append(self):
        identifier = registry.add_idea(self.root, dict(self.proposal, design={}))['id']
        before = self.stored('curation.jsonl')
        bad = dict(source_evidence=dict(self.evidence, line_end=4))
        with patch.object(registry, 'build_index', wraps=registry.build_index) as build:
            with self.assertRaises(ValueError):
                registry.append_review(self.root, self.review(identifier, design=bad))
            build.assert_not_called()
        self.assertEqual(self.stored('curation.jsonl'), before)
        registry.append_review(self.root, self.review(identifier, design=self.proposal['design']))
        self.assertEqual(registry._assemble(self.root)[identifier]['design'], self.proposal['design'])

    def test_old_bad_design_does_not_block_review_without_replacement(self):
        identifier = registry.add_idea(self.root, self.proposal)['id']
        # Manufacture a legacy pre-guard record without passing it through new ingress.
        path = self.root / registry.DIRECTORY / 'ideas.jsonl'
        rows = registry.read_jsonl(path)
        rows[0]['design']['source_evidence']['quote'] = 'historically incorrect quotation'
        registry.write_jsonl(path, rows)
        before = path.read_bytes()
        registry.append_review(self.root, self.review(identifier))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(registry.show(self.root, identifier)['verdict'], 'not_tested')
        self.assertEqual(registry._assemble(self.root)[identifier]['design']['source_evidence']['quote'],
                         'historically incorrect quotation')


if __name__ == '__main__':
    unittest.main()
