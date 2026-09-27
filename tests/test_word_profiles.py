"""Synthetic scope and accounting checks, using the actual guard in a subprocess."""
from __future__ import annotations

import csv
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import word_profiles as words


class WordProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / "cache.sqlite"
        allow = self.root / words.ALLOWLIST
        allow.parent.mkdir(parents=True)
        shutil.copyfile(words.ROOT / words.ALLOWLIST, allow)
        # This synthetic executable implements the same public query-tsv call.
        # Its actual selector-before-payload parser comes from the repository.
        script = '''#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
sys.path.insert(0, ROOT_VALUE)
from tools.guarded_tsv_query import query
p = argparse.ArgumentParser()
p.add_argument('command', choices=['query-tsv'])
p.add_argument('path')
p.add_argument('--selector', required=True)
p.add_argument('--allow', action='append', required=True)
p.add_argument('--columns', required=True)
p.add_argument('--forbid-prefix', action='append', required=True)
a = p.parse_args()
with Path('calls.txt').open('a') as f:
    f.write('query\\n')
query(path=Path(a.path), selector=a.selector, allowed_values=set(a.allow),
      columns=a.columns.split(','), forbidden_prefixes=tuple(a.forbid_prefix))
'''.replace("ROOT_VALUE", repr(str(words.ROOT)))
        wrapper = self.root / "vmanus-exp"
        wrapper.write_text(script, encoding="utf-8")
        wrapper.chmod(0o755)
        self.source = self.root / words.SOURCE
        self.source.parent.mkdir(parents=True)
        self.rows = []
        self.add_line("ZL3b", "f2r", "f2r.1", ["daiin", "daiin", "qodaiin", "dar"], uncertain_after=1)
        self.add_line("ZL3b", "f2r", "f2r.2", ["dar", "daiin"])
        self.add_line("ZL3b", "f2v", "f2v.1", ["daiin"], section="H", currier="B")
        self.add_line("IT2a", "f2r", "f2r.1", ["daiin", "dain", "daiin"])
        self.add_line("IT2a", "f2v", "f2v.1", ["dar"], section="H", currier="B")
        self.add_line("RF1b", "f2r", "f2r.1", ["dain", "qodaiin"])
        self.write_source()

    def add_line(self, edition, page, locus, literals, uncertain_after=None, section="B", currier="A"):
        for index, literal in enumerate(literals, 1):
            row = {key: "" for key in words.SOURCE_COLUMNS}
            row.update(source_group_id=f"{edition}|{locus}|G{index:03d}", edition=edition,
                page=page, locus=locus, section=section, currier=currier, hand="1", kind="P",
                source_group_index=index, source_group_count=len(literals), ivtff_group_raw=literal,
                left_separator="LINE_START" if index == 1 else "UNCERTAIN_SMALL_SPACE" if index-1 == uncertain_after else "DEFINITE_SPACE",
                right_separator="LINE_END" if index == len(literals) else "UNCERTAIN_SMALL_SPACE" if index == uncertain_after else "DEFINITE_SPACE")
            self.rows.append(row)

    def write_source(self):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=words.SOURCE_COLUMNS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(self.rows)
            # Both excluded rows are deliberately malformed after the selector.
            # A full-row parser would reject their width. They must never reach it.
            stream.write('poison|1\tZL3b\tf84r.1\tf84r\tSEALED_POISON\t"\n')
            stream.write('poison|2\tZL3b\tf999r.1\tf999r\tUNADMITTED_POISON\t"\n')

    def connect(self, **kwargs):
        conn = words.ensure_cache(root=self.root, cache=self.cache, **kwargs)
        self.addCleanup(conn.close)
        return conn

    def calls(self):
        return len((self.root / "calls.txt").read_text().splitlines())

    def test_guard_excludes_poison_before_parse_and_receipt_has_no_private_paths(self):
        conn = self.connect()
        provenance = words.receipt(conn)
        self.assertEqual(provenance["guard_stats"], {"selected": 13, "skipped_forbidden": 1, "skipped_not_allowed": 1})
        self.assertNotIn(str(self.root), json.dumps(provenance))
        self.assertFalse(any(row[0].startswith("f84") for row in conn.execute("SELECT DISTINCT page FROM groups")))
        self.assertNotIn(b"POISON", self.cache.read_bytes())
        self.assertIsInstance(conn.execute("SELECT * FROM groups LIMIT 1").fetchone(), sqlite3.Row)
        with self.assertRaises(sqlite3.OperationalError):
            conn.execute("DELETE FROM groups")

    def test_exact_words_and_readers_are_not_pooled(self):
        conn = self.connect()
        card = words.profile(conn, "daiin")
        self.assertEqual({e: v["count"] for e, v in card["editions"].items()}, {"ZL3b": 4, "IT2a": 2, "RF1b": 0})
        zl = card["editions"]["ZL3b"]
        self.assertEqual((zl["total_groups"], zl["pages_total"], zl["pages_with_form"], zl["rank"]), (7, 2, 2, 1))
        self.assertEqual(words.profile(conn, "qodaiin")["editions"]["ZL3b"]["count"], 1)
        self.assertTrue(all(row["ivtff_group_raw"] == "daiin" for row in words.occurrences(conn, "daiin")))
        self.assertEqual({row["edition"] for row in words.occurrences(conn, "daiin", "IT2a")}, {"IT2a"})
        with self.assertRaises(ValueError):
            words.occurrences(conn, "daiin", "pooled")

    def test_positions_repetition_neighbours_and_separators(self):
        conn = self.connect()
        card = words.profile(conn, "daiin")["editions"]["ZL3b"]
        self.assertEqual(card["positions"], {"start": 1, "middle": 1, "end": 1, "single": 1})
        self.assertEqual(card["repetition"], {"lines_with_form": 3, "repeated_lines": 1, "adjacent_pairs": 1, "max_per_line": 2})
        rows = words.occurrences(conn, "daiin", "ZL3b")
        self.assertEqual(rows[0]["right_separator"], "UNCERTAIN_SMALL_SPACE")
        self.assertTrue(rows[0]["next_same"])
        self.assertEqual(rows[0]["line_form_count"], 2)
        self.assertIsNone(rows[0]["previous_literal"])
        self.assertIsNone(rows[2]["next_literal"])
        self.assertIsNone(rows[3]["previous_literal"])
        self.assertIsNone(rows[3]["next_literal"])
        self.assertEqual(rows[1]["next_literal"], "qodaiin")
        self.assertEqual(card["strata"]["currier"], [
            {"value": "A", "count": 3, "total_groups": 6},
            {"value": "B", "count": 1, "total_groups": 1}])
        self.assertIn({"form": "dain", "count": 1}, words.profile(conn, "daiin")["editions"]["IT2a"]["spelling_neighbors"])
        self.assertNotIn("qodaiin", [row["form"] for row in card["spelling_neighbors"]])

    def test_source_change_invalidates_cache_and_reuse_does_not_requery(self):
        first = self.connect()
        original_receipt = words.receipt(first)
        self.connect()
        self.assertEqual(self.calls(), 1)
        self.add_line("ZL3b", "f2r", "f2r.99", ["daiin"])
        self.write_source()
        second = self.connect()
        self.assertEqual(self.calls(), 2)
        self.assertEqual(words.profile(second, "daiin")["editions"]["ZL3b"]["count"], 5)
        self.assertNotEqual(original_receipt["inputs"]["source_sha256"], words.receipt(second)["inputs"]["source_sha256"])
        # The previously opened reader remains a coherent snapshot after replace.
        self.assertEqual(words.profile(first, "daiin")["editions"]["ZL3b"]["count"], 4)

    def test_code_hash_and_corrupt_cache_trigger_rebuild(self):
        self.connect()
        digest = words._sha256
        with patch.object(words, "_sha256", side_effect=lambda path: "f" * 64 if path == Path(words.__file__) else digest(path)):
            changed = self.connect()
            self.assertEqual(words.receipt(changed)["inputs"]["code_sha256"], "f" * 64)
        self.assertEqual(self.calls(), 2)
        self.cache.write_bytes(b"corrupt cache")
        self.connect()
        self.assertEqual(self.calls(), 3)

    def test_scope_change_and_header_change_refused_before_query(self):
        original = (self.root / words.ALLOWLIST).read_bytes()
        (self.root / words.ALLOWLIST).write_bytes(original + b"f84r\n")
        with self.assertRaisesRegex(ValueError, "allowlist changed"):
            self.connect()
        self.assertFalse((self.root / "calls.txt").exists())
        (self.root / words.ALLOWLIST).write_bytes(original)
        text = self.source.read_text()
        self.source.write_text(text.replace("source_group_id", "renamed_id", 1))
        with self.assertRaisesRegex(ValueError, "header changed"):
            self.connect()
        self.assertFalse((self.root / "calls.txt").exists())

    def test_failed_build_preserves_previous_cache(self):
        conn = self.connect()
        old = self.cache.read_bytes()
        self.rows.pop(0)  # Leaves the first admitted source locus incomplete.
        self.write_source()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.connect()
        self.assertEqual(self.cache.read_bytes(), old)
        self.assertEqual(words.profile(conn, "daiin")["editions"]["ZL3b"]["count"], 4)

    def test_spelling_distance_is_exactly_one_edit_and_examples_are_bounded(self):
        for left, right in [("daiin", "dain"), ("daiin", "daiiin"), ("dar", "dal"), ("daiin", "aiin")]:
            self.assertTrue(words._one_edit(left, right))
        for left, right in [("daiin", "daiin"), ("daiin", "qodaiin"), ("dar", "dra"), ("daiin", "dy")]:
            self.assertFalse(words._one_edit(left, right))
        conn = self.connect()
        self.assertEqual(len(words.profile(conn, "daiin", limit=1)["editions"]["ZL3b"]["examples"]), 1)
        self.assertEqual(len(words.occurrences(conn, "daiin", "ZL3b")), 4)
        with self.assertRaises(ValueError):
            words.profile(conn, "daiin", limit=0)
        for invalid in ("", "daiin dar", "daiin\n", "daiïn"):
            with self.assertRaises(ValueError):
                words.profile(conn, invalid)
        with self.assertRaises(ValueError):
            words.profile(conn, "daiin", limit=21)
        self.assertEqual(words.profile(conn, "Daiin")["editions"]["ZL3b"]["count"], 0)


if __name__ == "__main__":
    unittest.main()
