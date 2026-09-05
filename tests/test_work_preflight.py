from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.work_preflight import INDEX_PATH, run


class WorkPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.write("tools/fixture.py", "# baseline\n")
        self.git("add", ".")
        self.commit()

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def commit(self) -> None:
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--no-gpg-sign", "-qm", "fixture")

    def write(self, path: str, content: str) -> None:
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    def check(self, *, experiments: tuple[str, ...] = (),
              includes: tuple[str, ...] = ()) -> dict:
        return run(root=self.root, experiments=experiments, includes=includes)

    def fixture_experiment(self) -> tuple[str, dict]:
        prefix = "experiments/yolo/gdt811_fixture/"
        payloads = {
            prefix + "REPORT.md": "# fixture report\n",
            prefix + "src/run.py": "# fixture runner\n",
            prefix + "artifacts/validation.json": '{"status":"PASS"}\n',
            "fixtures/source.tsv": "selector\tpayload\nf1r\tFIXTURE\n",
        }
        for path, content in payloads.items():
            self.write(path, content)
        binding = lambda path: {
            "path": path, "role": "fixture", "sha256": hashlib.sha256(
                payloads[path].encode()).hexdigest(),
        }
        data = {
            "schema_version": 1, "experiment_id": "GDT811", "slug": "fixture",
            "title": "Fixture", "status": "COMPLETE", "created": "2026-09-05",
            "updated": "2026-09-05", "question": "Fixture question?",
            "claim_ceiling": "Infrastructure fixture only.",
            "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
            "commands": {"run": "true", "validate": "true"}, "dependencies": [],
            "inputs": [binding("fixtures/source.tsv")],
            "outputs": [binding(path) for path in payloads if path.startswith(prefix)],
            "validation": {"status": "PASS", "artifact": prefix + "artifacts/validation.json"},
            "artifact_policy": {"max_inline_bytes": 100000, "large_artifact_justification": ""},
        }
        self.write(prefix + "experiment.json", json.dumps(data))
        self.write(INDEX_PATH, "experiment_id\tmanifest\tprimary_report\n"
                   f"GDT811\t{prefix}experiment.json\t{prefix}REPORT.md\n")
        self.git("add", ".")
        return prefix, data

    def experiment_check(self) -> dict:
        return self.check(experiments=("GDT811",), includes=(INDEX_PATH, "fixtures/source.tsv"))

    def test_exact_infrastructure_scope_passes(self) -> None:
        self.write("tools/fixture.py", "# changed\n")
        self.git("add", "tools/fixture.py")
        result = self.check(includes=("tools/fixture.py",))
        self.assertEqual(result["errors"], [])
        self.assertIn("NOT_RUN", result["global_check"])
        self.assertIn("experiment validators", result["not_checked"])

    def test_no_implicit_scope_or_staged_changes(self) -> None:
        result = self.check()
        self.assertTrue(any("no implicit scope" in item for item in result["errors"]))
        self.assertIn("no staged changes", result["errors"])

    def test_include_is_not_a_glob_or_directory(self) -> None:
        self.write("tools/fixture.py", "# changed\n")
        self.git("add", ".")
        for include in ("tools/*", "tools", "../tools/fixture.py"):
            with self.subTest(include=include):
                self.assertTrue(self.check(includes=(include,))["errors"])

    def test_unrelated_stage_is_rejected_and_still_privacy_scanned(self) -> None:
        self.write("tools/fixture.py", "# changed\n")
        self.write("unrelated.txt", "api" + "_key = fixture-not-a-secret\n")
        self.git("add", ".")
        errors = self.check(includes=("tools/fixture.py",))["errors"]
        self.assertTrue(any("outside declared task scope" in error for error in errors))
        self.assertTrue(any("credential/private-key" in error for error in errors))

    def test_safe_worktree_cannot_hide_unsafe_staged_blob(self) -> None:
        self.write("tools/fixture.py", "path=/" + "home" + "/private/fixture\n")
        self.git("add", ".")
        self.write("tools/fixture.py", "# safe unstaged replacement\n")
        errors = self.check(includes=("tools/fixture.py",))["errors"]
        self.assertTrue(any("private/local absolute path" in error for error in errors))

    def test_unstaged_worktree_does_not_replace_checked_blob(self) -> None:
        self.write("tools/fixture.py", "# safe staged\n")
        self.git("add", ".")
        self.write("tools/fixture.py", "api" + "_key = unstaged-fixture\n")
        self.assertEqual(self.check(includes=("tools/fixture.py",))["errors"], [])

    def test_deletions_and_renames_are_scoped(self) -> None:
        self.git("rm", "tools/fixture.py")
        self.write("tools/renamed.py", "# baseline\n")
        self.git("add", ".")
        errors = self.check(includes=("tools/renamed.py",))["errors"]
        self.assertTrue(any("tools/fixture.py" in error for error in errors))
        self.assertEqual(self.check(includes=("tools/renamed.py", "tools/fixture.py"))["errors"], [])

    def test_nonregular_staged_files_rejected(self) -> None:
        (self.root / "symlink").symlink_to("tools/fixture.py")
        self.git("add", "symlink")
        self.assertTrue(any("non-regular" in error for error in
                            self.check(includes=("symlink",))["errors"]))

    def test_sensitive_filename_rejected(self) -> None:
        self.write(".env", "fixture\n")
        self.git("add", ".env")
        self.assertTrue(any("sensitive staged filename" in error for error in
                            self.check(includes=(".env",))["errors"]))

    def test_complete_experiment_passes_without_global_worktree_audit(self) -> None:
        self.fixture_experiment()
        self.write("experiments/yolo/gdt600_unfinished/REPORT.md", "# untracked debt\n")
        result = self.experiment_check()
        self.assertEqual(result["errors"], [])
        self.assertIn("unrelated historical manifests", result["not_checked"])

    def test_include_cannot_bypass_experiment_selection(self) -> None:
        prefix, _ = self.fixture_experiment()
        includes = tuple(subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=self.root, check=True,
            text=True, stdout=subprocess.PIPE).stdout.splitlines())
        errors = self.check(includes=includes)["errors"]
        self.assertTrue(any("changed experiment must be selected" in error for error in errors))

    def test_manifest_bytes_come_from_index(self) -> None:
        prefix, data = self.fixture_experiment()
        data["sealed_data"] = {}
        self.write(prefix + "experiment.json", json.dumps(data))
        self.assertEqual(self.experiment_check()["errors"], [])
        self.git("add", prefix + "experiment.json")
        self.assertTrue(any("sealed_data" in error for error in self.experiment_check()["errors"]))

    def test_bindings_use_staged_bytes_not_worktree(self) -> None:
        prefix, _ = self.fixture_experiment()
        self.write(prefix + "REPORT.md", "# altered only in worktree\n")
        self.assertEqual(self.experiment_check()["errors"], [])
        self.git("add", prefix + "REPORT.md")
        self.assertTrue(any("hash mismatch" in error for error in self.experiment_check()["errors"]))

    def test_missing_bound_deleted_file_is_rejected(self) -> None:
        prefix, _ = self.fixture_experiment()
        self.commit()
        self.git("rm", prefix + "REPORT.md")
        self.assertTrue(any("missing staged-tree binding" in error for error in
                            self.experiment_check()["errors"]))

    def test_unbound_reproducibility_file_is_rejected(self) -> None:
        prefix, _ = self.fixture_experiment()
        self.write(prefix + "src/unbound.py", "# unbound\n")
        self.git("add", ".")
        self.assertTrue(any("unbound reproducibility file" in error for error in
                            self.experiment_check()["errors"]))

    def test_dependency_existence_and_order_are_checked(self) -> None:
        prefix, data = self.fixture_experiment()
        data["dependencies"] = ["GDT999"]
        self.write(prefix + "experiment.json", json.dumps(data))
        self.git("add", ".")
        self.assertTrue(any("missing indexed dependency" in error for error in
                            self.experiment_check()["errors"]))
        self.write(INDEX_PATH, (self.root / INDEX_PATH).read_text()
                   + "GDT999\tmissing/experiment.json\tmissing/report.md\n")
        self.git("add", INDEX_PATH)
        self.assertTrue(any("dependency is not earlier" in error for error in
                            self.experiment_check()["errors"]))

    def test_untracked_dependency_cannot_satisfy_index(self) -> None:
        prefix, data = self.fixture_experiment()
        data["dependencies"] = ["GDT810"]
        self.write(prefix + "experiment.json", json.dumps(data))
        self.write(INDEX_PATH, (self.root / INDEX_PATH).read_text()
                   + "GDT810\texperiments/yolo/gdt810_dependency/experiment.json\t\n")
        self.git("add", prefix + "experiment.json", INDEX_PATH)
        self.write("experiments/yolo/gdt810_dependency/experiment.json", "{}\n")
        self.assertTrue(any("dependency missing from staged tree" in error for error in
                            self.experiment_check()["errors"]))

    def test_null_hash_and_unjustified_large_artifact_are_rejected(self) -> None:
        prefix, data = self.fixture_experiment()
        data["inputs"][0]["sha256"] = None
        data["artifact_policy"]["max_inline_bytes"] = 1
        self.write(prefix + "experiment.json", json.dumps(data))
        self.git("add", prefix + "experiment.json")
        errors = self.experiment_check()["errors"]
        self.assertTrue(any("unbound input" in error for error in errors))
        self.assertTrue(any("oversized artifact" in error for error in errors))

    def test_deleted_manifest_does_not_disappear_from_selected_scope(self) -> None:
        prefix, _ = self.fixture_experiment()
        self.commit()
        self.git("rm", prefix + "experiment.json")
        self.assertTrue(any("selected experiment missing" in error for error in
                            self.experiment_check()["errors"]))

    def test_indirect_reproducibility_hashes_use_staged_tree(self) -> None:
        prefix, data = self.fixture_experiment()
        report = data["outputs"].pop(0)
        result_path = prefix + "artifacts/gdt811_result.json"
        content = json.dumps({"document_hashes": {report["path"]: report["sha256"]}})
        self.write(result_path, content)
        data["outputs"].append({"path": result_path, "role": "fixture",
                                "sha256": hashlib.sha256(content.encode()).hexdigest()})
        self.write(prefix + "experiment.json", json.dumps(data))
        self.git("add", ".")
        self.assertEqual(self.experiment_check()["errors"], [])
        self.write(report["path"], "# changed\n")
        self.git("add", report["path"])
        self.assertTrue(any("indirect staged-tree hash mismatch" in error for error in
                            self.experiment_check()["errors"]))

    def test_selected_index_manifest_must_agree(self) -> None:
        self.fixture_experiment()
        self.write(INDEX_PATH, "experiment_id\tmanifest\nGDT811\twrong/experiment.json\n")
        self.git("add", INDEX_PATH)
        self.assertTrue(any("index manifest mismatch" in error for error in
                            self.experiment_check()["errors"]))

    def test_malformed_result_hash_container_fails_explicitly(self) -> None:
        prefix, data = self.fixture_experiment()
        result_path = prefix + "artifacts/gdt811_result.json"
        data["outputs"].append({"path": result_path, "role": "fixture", "sha256": None})
        for result, message in (([], "root must be an object"),
                                ({"document_hashes": []}, "document_hashes must be an object")):
            with self.subTest(result=result):
                content = json.dumps(result)
                self.write(result_path, content)
                data["outputs"][-1]["sha256"] = hashlib.sha256(content.encode()).hexdigest()
                self.write(prefix + "experiment.json", json.dumps(data))
                self.git("add", ".")
                self.assertTrue(any(message in error for error in self.experiment_check()["errors"]))

    def test_frozen_legacy_and_bad_layout_cannot_be_included(self) -> None:
        for path in ("GDT336_FROZEN.md", "GDT812_BAD.md"):
            self.write(path, "# fixture\n")
            self.git("add", path)
        errors = self.check(includes=("GDT336_FROZEN.md", "GDT812_BAD.md"))["errors"]
        self.assertTrue(any("byte-frozen" in error for error in errors))
        self.assertTrue(any("violates structured layout" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
