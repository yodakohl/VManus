from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.experiment_lookup import lookup_experiments, normalize_id, render_lookup


class ExperimentLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.index = Path(self.temporary.name) / "index.tsv"
        self.prefix = "experiments/yolo/gdt811_fixture/"
        self.rows = [
            {
                "experiment_id": "GDT809",
                "question": "First question?",
                "status": "COMPLETE",
                "primary_report": "experiments/yolo/gdt809_fixture/REPORT.md",
                "manifest": "",
                "methods": "",
                "reports": "",
                "runners": "",
                "validators": "",
                "artifacts": "",
            },
            {
                "experiment_id": "GDT811",
                "question": "Which shared scope?",
                "status": "WORKING_THEORY_ONLY",
                "primary_report": self.prefix + "REPORT.md",
                "manifest": self.prefix + "experiment.json",
                "methods": ";".join(self.prefix + name for name in (
                    "METHOD.md", "PREREGISTRATION.md", "WORKING_THEORY.md", "artifacts/FOUR_PAGES_FULL_TEXT.md")),
                "reports": self.prefix + "REPORT.md",
                "runners": ";".join(self.prefix + "src/" + name for name in (
                    "other.py", "run_experiment.py", "run.py", "validate.py")),
                "validators": self.prefix + "src/validate_joint.py",
                "artifacts": ";".join(self.prefix + f"artifacts/OMITTED_{i}.tsv" for i in range(1000)),
            },
        ]
        self.write_index()

    def write_index(self) -> None:
        with self.index.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.rows[0].keys(), delimiter="\t")
            writer.writeheader()
            writer.writerows(self.rows)

    def test_normalizes_case_and_padding(self) -> None:
        self.assertEqual(normalize_id(" gdt000811 "), "GDT811")
        self.assertEqual(normalize_id("GDT1"), "GDT001")
        for value in ("811", "GDT000", "GDT811/f84r", "../GDT811", "GDT-1"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "invalid experiment ID"):
                normalize_id(value)

    def test_returns_requested_order_and_only_compact_fields(self) -> None:
        cards = lookup_experiments(["gdt811", "GDT809"], index_path=self.index)
        self.assertEqual([card["experiment_id"] for card in cards], ["GDT811", "GDT809"])
        self.assertEqual(set(cards[0]), {"experiment_id", "question", "status", "primary_report", "entrypoints"})
        self.assertEqual(cards[0]["question"], "Which shared scope?")
        entries = cards[0]["entrypoints"]
        self.assertEqual(entries["working_theory"], self.prefix + "WORKING_THEORY.md")
        self.assertEqual(entries["reader"], self.prefix + "artifacts/FOUR_PAGES_FULL_TEXT.md")
        self.assertEqual(entries["runner"], self.prefix + "src/run.py")
        self.assertEqual(entries["validator"], self.prefix + "src/validate.py")
        self.assertEqual(len(entries), 7)
        self.assertNotIn("OMITTED_", render_lookup(cards))
        self.assertLess(len(render_lookup(cards)), 1500)

    def test_json_is_machine_readable_and_complete(self) -> None:
        cards = lookup_experiments(["GDT811"], index_path=self.index)
        self.assertEqual(json.loads(render_lookup(cards, json_output=True)), cards)
        self.assertEqual(render_lookup(cards), render_lookup(cards))

    def test_never_opens_any_pointer_or_raw_source(self) -> None:
        # Even an indexed sealed-source pointer is metadata only, not an access grant.
        self.rows[1]["primary_report"] = "sealed/f84r/report.md"
        self.rows[1]["artifacts"] = "sealed/f84r/LINE_READER.tsv"
        self.write_index()
        original_open = Path.open
        opened = []

        def open_only_index(path, *args, **kwargs):
            opened.append(path)
            self.assertEqual(path, self.index)
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", open_only_index):
            cards = lookup_experiments(["GDT811"], index_path=self.index)
            render_lookup(cards, json_output=True)
        self.assertEqual(opened, [self.index])

    def test_duplicate_request_fails_before_any_read(self) -> None:
        with patch.object(Path, "open", side_effect=AssertionError("unexpected read")):
            with self.assertRaisesRegex(ValueError, "duplicate experiment IDs requested: GDT811$"):
                lookup_experiments(["GDT811", "gdt000811"], index_path=self.index)

    def test_unknown_ids_are_reported_sorted_without_partial_results(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown experiment IDs: GDT998, GDT999$"):
            lookup_experiments(["GDT999", "GDT811", "GDT998"], index_path=self.index)

    def test_duplicate_index_ids_fail_even_when_not_requested(self) -> None:
        self.rows.append(dict(self.rows[0], experiment_id="gdt0809"))
        self.write_index()
        with self.assertRaisesRegex(ValueError, "duplicate experiment IDs in index: GDT809$"):
            lookup_experiments(["GDT811"], index_path=self.index)

    def test_empty_request_fails_before_index_read(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one experiment ID"):
            lookup_experiments([], index_path=self.index)

    def test_missing_columns_and_malformed_rows_fail(self) -> None:
        self.index.write_text("experiment_id\tstatus\nGDT811\tDONE\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "experiment index missing columns: primary_report, question$"):
            lookup_experiments(["GDT811"], index_path=self.index)
        self.index.write_text("experiment_id\tquestion\tstatus\tprimary_report\nGDT811\tQ\tDONE\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "malformed experiment index row at line 2$"):
            lookup_experiments(["GDT811"], index_path=self.index)

    def test_missing_index_error_does_not_leak_local_path(self) -> None:
        with self.assertRaisesRegex(ValueError, r"^cannot read experiment index \(FileNotFoundError\)$"):
            lookup_experiments(["GDT811"], index_path=self.index.parent / "absent.tsv")

    def test_legacy_missing_metadata_is_explicit_and_no_main_script_is_invented(self) -> None:
        self.rows[0].update(question="", runners="alpha.py;beta.py", validators="validate_alpha.py;validate_beta.py")
        self.write_index()
        cards = lookup_experiments(["GDT809"], index_path=self.index)
        self.assertEqual(cards[0]["entrypoints"], {})
        self.assertIn("question: [not recorded in index]", render_lookup(cards))

    def test_full_text_precedes_paragraph_reader_and_tsv_reader(self) -> None:
        self.rows[1]["artifacts"] += ";a_LINE_READER.tsv;b_PARAGRAPH_READINGS.md"
        self.write_index()
        cards = lookup_experiments(["GDT811"], index_path=self.index)
        self.assertEqual(cards[0]["entrypoints"]["reader"], self.prefix + "artifacts/FOUR_PAGES_FULL_TEXT.md")


if __name__ == "__main__":
    unittest.main()
