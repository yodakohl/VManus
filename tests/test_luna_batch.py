"""Focused safety and handoff tests for the Luna batch helper."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools import luna_batch


class LunaBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "inputs").mkdir()
        (self.root / "inputs/a.json").write_text('{"a": 1}\n', encoding="utf-8")
        (self.root / "inputs/b.json").write_text('{"b": 2}\n', encoding="utf-8")
        self.packet_path = self.root / "PACKET.json"
        self.packet = {
            "schema_version": 1,
            "purpose": "fixture",
            "claim_ceiling": "administrative only",
            "allowed_selectors": ["f77r"],
            "inputs": [self._input("inputs/a.json", "a"), self._input("inputs/b.json", "b")],
            "output_dir": "outputs",
            "tasks": [
                {"id": "one", "owner": "worker-one", "question": "Q1",
                 "input_paths": ["inputs/a.json"], "output_path": "outputs/one.json",
                 "required_result_fields": ["status", "summary", "evidence_paths"]},
                {"id": "two", "owner": "worker-two", "question": "Q2",
                 "input_paths": ["inputs/b.json"], "output_path": "outputs/two.json",
                 "required_result_fields": ["status", "summary"]},
            ],
        }
        self._write_packet()

    def _input(self, path: str, role: str) -> dict[str, str]:
        return {"path": path, "sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest(), "role": role}

    def _write_packet(self):
        self.packet_path.write_text(json.dumps(self.packet), encoding="utf-8")

    def _run(self, *args: str) -> tuple[int, dict]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = luna_batch.main(["--root", str(self.root), *args])
        return code, json.loads(out.getvalue())

    def test_validate_hashes_bound_inputs_and_detects_tampering(self):
        code, result = self._run("validate", "PACKET.json")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "VALID")
        (self.root / "inputs/a.json").write_text("tampered\n", encoding="utf-8")
        code, result = self._run("validate", "PACKET.json")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "INVALID")

    def test_rejects_sealed_selector_traversal_and_symlink_inputs(self):
        (self.root / "packet_link.json").symlink_to(self.packet_path)
        code, result = self._run("validate", "packet_link.json")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "INVALID")

        for selector in ("f84r", "f116v"):
            self.packet["allowed_selectors"] = [selector]
            self._write_packet()
            code, result = self._run("validate", "PACKET.json")
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "INVALID")

        self.packet["allowed_selectors"] = ["f77r"]
        self.packet["inputs"][0]["path"] = "../outside.json"
        self._write_packet()
        code, result = self._run("validate", "PACKET.json")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "INVALID")

        self.packet["inputs"][0] = self._input("inputs/a.json", "a")
        outside = self.root.parent / (self.root.name + "-outside.json")
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        (self.root / "linked.json").symlink_to(outside)
        self.packet["inputs"][0] = {"path": "linked.json", "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(), "role": "a"}
        self._write_packet()
        code, result = self._run("validate", "PACKET.json")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "INVALID")

        self.packet["tasks"][0]["output_path"] = "inputs/a.json"
        self._write_packet()
        code, result = self._run("validate", "PACKET.json")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "INVALID")

    def test_brief_is_task_specific(self):
        code, result = self._run("brief", "PACKET.json", "one")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["task"]["id"], "one")
        self.assertEqual([row["path"] for row in result["bound_inputs"]], ["inputs/a.json"])
        self.assertNotIn("inputs/b.json", json.dumps(result))
        self.assertNotIn("{\"a\": 1}", json.dumps(result))

    def test_collect_reports_pending_invalid_and_done(self):
        code, result = self._run("collect", "PACKET.json")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PENDING")
        self.assertEqual({row["status"] for row in result["tasks"]}, {"PENDING"})

        output_dir = self.root / "outputs"
        output_dir.mkdir()
        (output_dir / "one.json").write_text('{"status": "DONE"}\n', encoding="utf-8")
        code, result = self._run("collect", "PACKET.json")
        self.assertEqual(code, 1)
        statuses = {row["id"]: row["status"] for row in result["tasks"]}
        self.assertEqual(statuses, {"one": "INVALID", "two": "PENDING"})

        (output_dir / "one.json").write_text(
            json.dumps({"status": "DONE", "summary": "checked", "evidence_paths": ["outputs/missing.txt"]}),
            encoding="utf-8")
        code, result = self._run("collect", "PACKET.json")
        self.assertEqual(code, 1)
        self.assertEqual({row["id"]: row["status"] for row in result["tasks"]}["one"], "INVALID")

        (output_dir / "one.json").write_text(
            json.dumps({"status": "DONE", "summary": "checked", "evidence_paths": ["inputs/a.json"]}),
            encoding="utf-8")
        (output_dir / "two.json").write_text(
            json.dumps({"status": "DONE", "summary": "checked", "evidence_paths": ["outputs/two.json"]}),
            encoding="utf-8")
        code, result = self._run("collect", "PACKET.json")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual({row["status"] for row in result["tasks"]}, {"DONE"})


if __name__ == "__main__":
    unittest.main()
