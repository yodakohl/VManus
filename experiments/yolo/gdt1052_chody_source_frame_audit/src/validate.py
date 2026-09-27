"""Independent exact-source replay of GDT1052, including guarded edge rows."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock = json.loads((HERE / "PREREG_LOCK.json").read_text())
    assert digest(HERE / "METHOD.md") == lock["method_sha256"]
    assert digest(HERE / "PREREGISTRATION.md") == lock["preregistration_sha256"]
    source_path = ROOT / lock["source"]
    assert digest(source_path) == lock["input_sha256"]
    source = json.loads(source_path.read_text())
    result = json.loads((HERE / "artifacts/RESULT.json").read_text())
    checks = []
    expected = []
    eligible_counts = {}
    for reader in ("ZL3b", "IT2a"):
        eligible_counts[reader] = len(source[reader])
        for paragraph in source[reader]:
            assert not paragraph["page"].startswith("f84")
            total = sum(len(line["words"]) for line in paragraph["lines"])
            offset = 0
            for line in paragraph["lines"]:
                for local_index, word in enumerate(line["words"]):
                    if word == "chody":
                        position = offset + local_index + 1
                        expected.append((reader, paragraph["id"], line["source_ids"][local_index], position, total, position - 1, total - position))
                offset += len(line["words"])
            assert offset == total
    actual = [(h["reader"], h["paragraph_id"], h["source_id"], h["position_1based"], h["paragraph_length"], h["left_count"], h["right_count"]) for h in result["hits"]]
    assert Counter(expected) == Counter(actual)
    checks.append("every_exact_hit_source_id_position_and_edge_replayed")
    assert len(result["hits"]) == len(expected)
    assert len({(h["reader"], h["source_id"]) for h in result["hits"]}) == len(expected)
    checks.append("no_hit_omission_or_duplication")
    for reader in ("ZL3b", "IT2a"):
        hits = [h for h in result["hits"] if h["reader"] == reader]
        summary = result["reader_summaries"][reader]
        assert summary["complete_paragraphs_in_source"] == eligible_counts[reader]
        assert summary["exact_hits"] == len(hits)
        assert summary["paragraphs_with_hit"] == len({h["paragraph_id"] for h in hits})
        assert summary["edge_classes"] == dict(sorted(Counter(h["edge_class"] for h in hits).items()))
    checks.append("reader_summaries_replayed")
    for h in result["hits"]:
        assert h["edge_class"] == ("FIRST" if h["left_count"] == 0 else "LAST" if h["right_count"] == 0 else "MIDDLE")
        paragraph = next(p for p in result["containing_paragraphs"] if p["reader"] == h["reader"] and p["paragraph_id"] == h["paragraph_id"])
        assert len(paragraph["words"]) == h["paragraph_length"]
        assert paragraph["words"][h["position_1based"] - 1] == "chody"
    checks.append("containing_paragraphs_and_classes_replayed")
    edge_hits = [h for h in result["hits"] if h["edge_class"] != "MIDDLE"]
    assert result["source_frame_global_decision"] == ("REJECTED_BY_PARAGRAPH_EDGE" if edge_hits else "MINIMAL_CAPACITY_ONLY")
    checks.append("frozen_decision_rule_applied")
    with (HERE / "artifacts/EDGE_SPOTCHECK.tsv").open(newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert {r["locus"] for r in rows} == {"f88v.20", "f42r.15"}
    ends = [r for r in rows if r["locus"] == "f88v.20" and r["ivtff_group_raw"] == "chody"]
    assert {r["edition"] for r in ends} == {"ZL3b", "IT2a", "RF1b"}
    assert all(r["right_separator"] == "LINE_END" for r in ends)
    assert all(r["paragraph_end"] == "1" for r in ends if r["edition"] != "RF1b")
    assert any(r["locus"] == "f42r.15" and r["edition"] == "IT2a" and r["source_group_index"] == "1" and r["ivtff_group_raw"] == "chody" and r["paragraph_start"] == "1" for r in rows)
    checks.append("guarded_exact_edge_source_rechecked")
    validation = {"status": "PASS", "checks": checks, "source_sha256": lock["input_sha256"], "edge_source_rows": len(rows), "edge_hits": [{k: h[k] for k in ("reader", "locus", "source_id", "edge_class")} for h in edge_hits], "note": "String/paragraph replay only; no semantic validation"}
    (HERE / "artifacts/VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "edge_hits": len(edge_hits)}))


if __name__ == "__main__":
    main()
