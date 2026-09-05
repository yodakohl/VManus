"""Keep startup compact and the additive CLI usable without opening raw data."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.work_cli import main

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_current_route_stays_compact_and_preserves_boundaries(self):
        body = (ROOT / 'VOYNICH_CURRENT_ROUTE.md').read_text(encoding='utf-8')
        self.assertLessEqual(len(body.encode('utf-8')), 8500)
        self.assertLessEqual(len(body.splitlines()), 150)
        self.assertLessEqual(max(map(len, body.splitlines())), 160)
        for required in ['Confirmed English lexemes: **0**', 'f84r is sealed',
                         'GDT327', 'GDT336', '179', '190',
                         'VOYNICH_ACTIVE_STATE.md', 'ACTIVE_EXPERIMENT_LEDGER.tsv']:
            self.assertIn(required, body)

    def test_lookup_cli_json(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(['lookup', 'GDT811', '--json']), 0)
        cards = json.loads(out.getvalue())
        self.assertEqual(cards[0]['experiment_id'], 'GDT811')
        self.assertIn('WORKING_THEORY.md', cards[0]['entrypoints']['working_theory'])

    def test_lookup_cli_unknown_fails_without_partial_output(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), self.assertRaises(SystemExit) as exc:
            main(['lookup', 'GDT811', 'GDT999999'])
        self.assertEqual(exc.exception.code, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('unknown experiment', err.getvalue())

    def test_check_staged_forwards_exact_scope(self):
        with patch('tools.work_preflight.main', return_value=0) as check:
            self.assertEqual(main(['check-staged', '--experiment', 'GDT811',
                                   '--include', 'VOYNICH_CURRENT_ROUTE.md']), 0)
        check.assert_called_once_with(['--experiment', 'GDT811', '--include', 'VOYNICH_CURRENT_ROUTE.md'])


if __name__ == '__main__':
    unittest.main()
