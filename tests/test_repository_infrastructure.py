from __future__ import annotations

import importlib.util
import io
import json
import csv
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.repository_preflight import (
    CREDENTIAL_PATTERNS,
    LOCAL_PATH_PATTERNS,
    check_structured_layout,
)
from tools.guarded_tsv_query import query as query_guarded_tsv
from tools.vmanus_experiment import (
    GuardedTSV,
    SealedDataError,
    deterministic_seed,
    load_manifest,
    validate_manifest_data,
    verify_manifest_bindings,
)


ROOT = Path(__file__).resolve().parents[1]


class InfrastructureTests(unittest.TestCase):
    @staticmethod
    def load_module(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def test_guarded_tsv_filters_before_payload_parse(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "fixture.tsv"
            source.write_text(
                "value\tpage\tpayload\n"
                "1\tf83r\tADMIT\n"
                "2\tf84r\tSEALED\n"
                "3\tf85v\tOTHER\n",
                encoding="utf-8",
            )
            guarded = GuardedTSV(
                source,
                selector_column="page",
                allowed_values={"f83r"},
                forbidden_prefixes=("f84",),
            )
            self.assertEqual(
                list(guarded), [{"value": "1", "page": "f83r", "payload": "ADMIT"}]
            )
            self.assertEqual(
                (
                    guarded.stats.lines_seen,
                    guarded.stats.selected,
                    guarded.stats.skipped_forbidden,
                    guarded.stats.skipped_not_allowed,
                ),
                (3, 1, 1, 1),
            )

    def test_guarded_tsv_hard_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "fixture.tsv"
            source.write_text('page\tpayload\n"f84r"\tSEALED\n', encoding="utf-8")
            with self.assertRaises(SealedDataError):
                list(GuardedTSV(source, selector_column="page", forbidden_action="error"))

    def test_guarded_query_requires_explicit_allowlist_and_columns(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "fixture.tsv"
            source.write_text(
                "page\tsection\tpayload\n"
                "f83r\tB\tADMIT\n"
                "f84r\tB\tSEALED\n"
                "f85v\tH\tOTHER\n",
                encoding="utf-8",
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(
                    query_guarded_tsv(
                        path=source,
                        selector="page",
                        allowed_values={"f83r", "f84r"},
                        columns=["page", "section"],
                    ),
                    0,
                )
            self.assertEqual(stdout.getvalue(), "page\tsection\nf83r\tB\n")
            self.assertNotIn("SEALED", stdout.getvalue())
            self.assertIn('"skipped_forbidden": 1', stderr.getvalue())

    def test_guarded_query_rejects_unbounded_or_unknown_projection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "fixture.tsv"
            source.write_text("page\tpayload\nf83r\tADMIT\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "explicit --allow"):
                query_guarded_tsv(
                    path=source,
                    selector="page",
                    allowed_values=set(),
                    columns=["page"],
                )
            with self.assertRaisesRegex(ValueError, "missing TSV columns"):
                query_guarded_tsv(
                    path=source,
                    selector="page",
                    allowed_values={"f83r"},
                    columns=["unknown"],
                )

    def test_scaffold_manifest_and_scripts(self) -> None:
        module = self.load_module("test_scaffolder", ROOT / "tools/new_yolo_experiment.py")
        with tempfile.TemporaryDirectory() as raw:
            temporary_root = Path(raw)
            (temporary_root / "AGENTS.md").write_text("fixture", encoding="utf-8")
            (temporary_root / ".git").mkdir()
            old_root, old_argv = module.ROOT, sys.argv
            module.ROOT = temporary_root
            sys.argv = ["new_yolo_experiment.py", "fixture", "--id", "337"]
            try:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
            finally:
                module.ROOT, sys.argv = old_root, old_argv
            manifest_path = temporary_root / "experiments/yolo/gdt337_fixture/experiment.json"
            data = load_manifest(manifest_path)
            self.assertEqual(validate_manifest_data(data, manifest_path), [])
            self.assertEqual(verify_manifest_bindings(data, temporary_root), [])
            for name in ("run.py", "validate.py"):
                compile((manifest_path.parent / "src" / name).read_text(), name, "exec")

    def test_schema_and_layout_contract(self) -> None:
        schema = json.loads((ROOT / "experiments/yolo/experiment.schema.json").read_text())
        self.assertEqual(
            schema["properties"]["sealed_data"]["properties"]["f84r"]["const"],
            "FORBIDDEN",
        )
        self.assertEqual(
            check_structured_layout(
                [
                    "experiments/yolo/gdt337_probe/experiment.json",
                    "experiments/yolo/gdt337_probe/src/run.py",
                ]
            ),
            [],
        )
        self.assertTrue(check_structured_layout(["GDT337_BAD.md"]))

    def test_structured_manifest_drives_index(self) -> None:
        indexer = self.load_module("test_indexer", ROOT / "tools/build_experiment_index.py")
        with tempfile.TemporaryDirectory() as raw:
            temporary_root = Path(raw)
            directory = temporary_root / "experiments/yolo/gdt337_fixture"
            (directory / "src").mkdir(parents=True)
            report = directory / "REPORT.md"
            report.write_text("# report\n", encoding="utf-8")
            (directory / "src/run.py").write_text("# depends on GDT003\n", encoding="utf-8")
            manifest = {
                "schema_version": 1,
                "experiment_id": "GDT337",
                "slug": "fixture",
                "title": "Structured fixture",
                "status": "PASS",
                "created": "2026-08-18",
                "updated": "2026-08-18",
                "question": "Does the manifest drive the index?",
                "claim_ceiling": "Infrastructure only.",
                "sealed_data": {"f84r": "FORBIDDEN"},
                "commands": {"run": "true", "validate": "true"},
                "dependencies": ["GDT003"],
                "inputs": [],
                "outputs": [
                    {
                        "path": "experiments/yolo/gdt337_fixture/REPORT.md",
                        "role": "PRIMARY_REPORT",
                        "sha256": None,
                    }
                ],
                "validation": {"status": "NOT_RUN", "artifact": None},
                "artifact_policy": {
                    "max_inline_bytes": 5000000,
                    "large_artifact_justification": "",
                },
            }
            manifest_path = directory / "experiment.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            paths = [
                "experiments/yolo/gdt337_fixture/REPORT.md",
                "experiments/yolo/gdt337_fixture/experiment.json",
                "experiments/yolo/gdt337_fixture/src/run.py",
            ]
            ledger = [
                {
                    "date": "2026-08-19",
                    "experiment": "GDT337_fixture_result",
                    "status": "LEDGER_STATUS",
                    "live_scope": "fixture",
                    "forbidden_inference": "fixture",
                    "primary_report": "experiments/yolo/gdt337_fixture/REPORT.md",
                }
            ]
            old_root = indexer.ROOT
            indexer.ROOT = temporary_root
            try:
                experiments = indexer.build_experiments(paths, ledger)
                tsv, _ = indexer.render(experiments)
            finally:
                indexer.ROOT = old_root
            row = next(csv.DictReader(io.StringIO(tsv.decode()), delimiter="\t"))
            self.assertEqual(row["status"], "LEDGER_STATUS")
            self.assertEqual(row["manifest"], "experiments/yolo/gdt337_fixture/experiment.json")
            self.assertEqual(row["question"], "Does the manifest drive the index?")
            self.assertEqual(row["dependencies"], "GDT003")

    def test_deterministic_seed(self) -> None:
        self.assertEqual(
            deterministic_seed("vmanus-fixture"), deterministic_seed("vmanus-fixture")
        )
        self.assertNotEqual(
            deterministic_seed("vmanus-fixture"), deterministic_seed("vmanus-other")
        )

    def test_privacy_patterns_detect_fixtures(self) -> None:
        credential = b"api" + b"_key = example-not-a-real-secret"
        local_path = b"path=/" + b"home" + b"/private/workspace"
        self.assertTrue(any(pattern.search(credential) for pattern in CREDENTIAL_PATTERNS))
        self.assertTrue(any(pattern.search(local_path) for pattern in LOCAL_PATH_PATTERNS))


if __name__ == "__main__":
    unittest.main()
