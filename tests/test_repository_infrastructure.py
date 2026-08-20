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
    check_reproducibility_bindings,
    check_manifest_dependency_graph,
    check_structured_layout,
)
from tools.guarded_tsv_query import query as query_guarded_tsv
from tools.relation_edge_intake import (
    EDGE_COLUMNS,
    NULL_COLUMNS,
    validate_relation_edge_packet,
)
from tools.route_duplicate_query import query_routes
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

    @staticmethod
    def _edge_row(edge_id: str, page: str, folio: str, fold: str) -> dict[str, str]:
        digest = "a" * 64
        return {
            "edge_id": edge_id,
            "batch_id": "B01",
            "page": page,
            "physical_folio": folio,
            "diagram_unit_id": "UNIT1",
            "pivot_visual_id": "PV1",
            "pivot_locus": f"{page}.1",
            "target_visual_id": "TV1",
            "target_locus": f"{page}.2",
            "relation_type": "DIRECTED_CONNECTOR",
            "direction_basis": "AUTHORIAL_POINTER",
            "ownership_basis": "SINGULAR_EXACT",
            "geometry_only_selection": "TRUE",
            "source_manifest_id": "SOURCE1",
            "page_crop_sha256": digest,
            "pivot_crop_sha256": digest,
            "target_crop_sha256": digest,
            "source_aware_localizer": "LOCALIZER_A",
            "relation_reviewer": "REVIEWER_B",
            "relation_confidence": "HIGH",
            "ambiguity_state": "RESOLVED",
            "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": fold,
            "eligibility_status": "ELIGIBLE",
        }

    def test_edge_intake_requires_capacity_holdout_and_mobile_null(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            packet = directory / "packet.tsv"
            nulls = directory / "nulls.tsv"
            edge_rows = []
            null_rows = []
            for index in range(50):
                folio_number = 10 + index % 5
                page = f"f{folio_number}r"
                edge_id = f"E{index:03d}"
                edge_row = self._edge_row(
                    edge_id,
                    page,
                    f"f{folio_number}",
                    "HOLDOUT" if index % 5 == 0 else "DISCOVERY",
                )
                edge_row["pivot_locus"] = f"{page}.i{index}a"
                edge_row["target_locus"] = f"{page}.i{index}b"
                edge_rows.append(edge_row)
                null_rows.extend(
                    [
                        {
                            "edge_id": edge_id,
                            "candidate_target_locus": f"{page}.i{index}b",
                            "is_observed_target": "TRUE",
                            "matched_topology": "TRUE",
                            "eligible_under_null": "TRUE",
                        },
                        {
                            "edge_id": edge_id,
                            "candidate_target_locus": f"{page}.i{index}c",
                            "is_observed_target": "FALSE",
                            "matched_topology": "TRUE",
                            "eligible_under_null": "TRUE",
                        },
                    ]
                )
            with packet.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=EDGE_COLUMNS, delimiter="\t")
                writer.writeheader()
                writer.writerows(edge_rows)
            with nulls.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=NULL_COLUMNS, delimiter="\t")
                writer.writeheader()
                writer.writerows(null_rows)
            report = validate_relation_edge_packet(packet, nulls)
            self.assertEqual(report["status"], "SCORE_READY")
            self.assertEqual(report["eligible_edges"], 50)
            self.assertEqual(report["eligible_folios"], 5)
            self.assertEqual(report["mobile_edges"], 50)

    def test_edge_intake_rejects_f84_before_payload_parse(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            packet = Path(raw) / "packet.tsv"
            packet.write_text(
                "\t".join(EDGE_COLUMNS)
                + "\n"
                + "E1\tB01\tf84r\tf84\tSEALED_PAYLOAD_THAT_MUST_NOT_PARSE\n",
                encoding="utf-8",
            )
            with self.assertRaises(SealedDataError):
                validate_relation_edge_packet(packet)

    def test_route_duplicate_query_ranks_closed_family(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            closed = directory / "closed.tsv"
            index = directory / "index.tsv"
            closed.write_text(
                "family\tstatus\twhat_the_archive_establishes\treopen_only_if\tarchive_pointer\n"
                "CONNECTOR_RELATION\tCLOSED\tvisible connector parent edges have zero capacity\tnew directed endpoint\treport.md\n"
                "CALENDAR\tCLOSED\tmonth and number routes fail\tnew arithmetic equality\tcalendar.md\n",
                encoding="utf-8",
            )
            index.write_text(
                "experiment_id\tlatest_date\texperiment_name\tstatus\tprimary_report\tprimary_report_exists\tlayout\tfile_count\ttotal_bytes\tledger_entries\tmanifest\tquestion\tclaim_ceiling\tdependencies\tmethods\treports\trunners\tvalidators\tartifacts\n"
                "GDT001\t2026-01-01\tmonth_probe\tFAIL\tgdt001.md\ttrue\tLEGACY\t1\t1\t1\t\tDoes a month mapping work?\tNone\t\t\t\t\t\t\n",
                encoding="utf-8",
            )
            result = query_routes(
                "authorial connector relation edge",
                closed_path=closed,
                index_path=index,
                limit=2,
            )
            self.assertEqual(result[0]["identifier"], "CONNECTOR_RELATION")
            self.assertEqual(result[0]["kind"], "CLOSED_ROUTE")

    def test_reproducibility_files_must_be_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = root / "experiments/yolo/gdt400_fixture"
            (directory / "src").mkdir(parents=True)
            manifest = directory / "experiment.json"
            report = directory / "REPORT.md"
            runner = directory / "src/run.py"
            report.write_text("# report\n", encoding="utf-8")
            runner.write_text("# runner\n", encoding="utf-8")
            data = {"inputs": [], "outputs": []}
            errors = check_reproducibility_bindings(data, manifest, root)
            self.assertEqual(len(errors), 2)

            import hashlib

            result_path = directory / "artifacts/gdt400_result.json"
            result_path.parent.mkdir()
            result_path.write_text(
                json.dumps(
                    {
                        "document_hashes": {
                            report.relative_to(root).as_posix(): hashlib.sha256(
                                report.read_bytes()
                            ).hexdigest()
                        },
                        "implementation_hashes": {
                            runner.relative_to(root).as_posix(): hashlib.sha256(
                                runner.read_bytes()
                            ).hexdigest()
                        },
                    }
                ),
                encoding="utf-8",
            )
            data["outputs"] = [{"path": result_path.relative_to(root).as_posix()}]
            self.assertEqual(check_reproducibility_bindings(data, manifest, root), [])

    def test_manifest_dependency_graph_rejects_forward_and_missing_edges(self) -> None:
        manifests = [
            (
                ROOT / "experiments/yolo/gdt400_fixture/experiment.json",
                {"experiment_id": "GDT400", "dependencies": ["GDT399", "GDT401"]},
            )
        ]
        errors = check_manifest_dependency_graph(manifests, available_ids={399, 400})
        self.assertTrue(any("missing dependency GDT401" in error for error in errors))
        self.assertTrue(any("dependency is not earlier GDT401" in error for error in errors))

    def test_manifest_dependency_graph_accepts_acyclic_history(self) -> None:
        manifests = [
            (
                ROOT / "experiments/yolo/gdt399_a/experiment.json",
                {"experiment_id": "GDT399", "dependencies": []},
            ),
            (
                ROOT / "experiments/yolo/gdt400_b/experiment.json",
                {"experiment_id": "GDT400", "dependencies": ["GDT399"]},
            ),
        ]
        self.assertEqual(
            check_manifest_dependency_graph(manifests, available_ids={399, 400}),
            [],
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
            self.assertEqual(data["sealed_data"]["f84"], "FORBIDDEN")
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

    def test_new_manifest_requires_whole_f84_seal(self) -> None:
        data = {
            "schema_version": 1,
            "experiment_id": "GDT394",
            "slug": "fixture",
            "title": "fixture",
            "status": "REGISTERED_UNSCORED",
            "created": "2026-08-20",
            "updated": "2026-08-20",
            "question": "",
            "claim_ceiling": "",
            "sealed_data": {"f84r": "FORBIDDEN"},
            "commands": {"run": "true", "validate": "true"},
            "dependencies": [],
            "inputs": [],
            "outputs": [],
            "validation": {"status": "NOT_RUN", "artifact": None},
            "artifact_policy": {
                "max_inline_bytes": 1,
                "large_artifact_justification": "",
            },
        }
        self.assertIn(
            "GDT394+ sealed_data.f84 must equal FORBIDDEN",
            validate_manifest_data(data),
        )
        data["sealed_data"]["f84"] = "FORBIDDEN"
        self.assertEqual(validate_manifest_data(data), [])

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
