"""Navigation must use tracked names only, never manuscript/report contents."""
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.report_locator import locate_report_paths, render_locations
from tools.work_cli import main


class ReportLocatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        names = [
            'reports/DIC001_report.md', 'reports/dic001_correction.MD',
            'reports/DIC0010_report.md', 'reports/ADIC001_report.md',
            'reports/DIC001A_report.md', 'reports/DIC001_report.tsv',
            'reports/other.md', 'runtime/DIC001_report.md',
            'private/DIC001_report.md', '.hidden/DIC001_report.md',
            'reports/DIC001_private_notes.md',
        ]
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Payload must not be read; DIC001 mentions are irrelevant.\n')
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        (self.root / 'reports/DIC001_untracked.md').write_text('not tracked')

    def test_exact_case_insensitive_id_and_safe_tracked_names_only(self):
        self.assertEqual(locate_report_paths('dic001', root=self.root),
                         ['reports/DIC001_report.md', 'reports/dic001_correction.MD'])

    def test_no_payload_opening(self):
        # Git's tracked names remain usable even after their worktree payloads vanish.
        for path in self.root.rglob('*.md'):
            path.unlink()
        with patch('pathlib.Path.open', side_effect=AssertionError('payload opened')):
            self.assertEqual(len(locate_report_paths('DIC001', root=self.root)), 2)

    def test_reject_unsafe_id_before_git(self):
        for value in ['../DIC001', 'DIC001;cat', '--help', 'DIC001 extra', 'DIC000', 'DIC001\n']:
            with self.subTest(value=value), patch('tools.report_locator.subprocess.run') as run:
                with self.assertRaises(ValueError):
                    locate_report_paths(value, root=self.root)
                run.assert_not_called()

    def test_navigation_note_and_cli_dispatch(self):
        out = io.StringIO()
        with patch('tools.report_locator.locate_report_paths', return_value=['reports/DIC001_report.md']) as locate:
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(['locate', 'DIC001']), 0)
            locate.assert_called_once_with('DIC001')
        self.assertIn('Navigation only', out.getvalue())
        self.assertIn('no latest-valid report is selected', out.getvalue())
        self.assertIn('reports/DIC001_report.md', out.getvalue())
        self.assertIn('0 matching tracked path(s)', render_locations('DIC999', []))


if __name__ == '__main__':
    unittest.main()
