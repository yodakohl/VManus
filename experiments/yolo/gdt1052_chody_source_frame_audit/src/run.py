"""Exact whole-group positional audit of the frozen GDT928 paragraph artifact."""

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json"
EXPECTED = "667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b"


def main():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    data = json.loads(raw)
    assert set(data) == {"ZL3b", "IT2a", "RF1b"}
    hits = []
    paragraphs = []
    for reader in ("ZL3b", "IT2a"):
        for paragraph in data[reader]:
            assert not paragraph["page"].startswith("f84")
            seq = []
            for line in paragraph["lines"]:
                assert len(line["words"]) == len(line["source_ids"])
                seq.extend((word, source_id, line["locus"]) for word, source_id in zip(line["words"], line["source_ids"]))
            positions = [i for i, item in enumerate(seq) if item[0] == "chody"]
            if not positions:
                continue
            paragraphs.append({"reader": reader, "paragraph_id": paragraph["id"], "page": paragraph["page"], "words": [item[0] for item in seq]})
            for i in positions:
                left, right = i, len(seq) - 1 - i
                hits.append({"reader": reader, "paragraph_id": paragraph["id"], "page": paragraph["page"], "locus": seq[i][2], "source_id": seq[i][1], "position_1based": i + 1, "paragraph_length": len(seq), "left_count": left, "right_count": right, "edge_class": "FIRST" if left == 0 else "LAST" if right == 0 else "MIDDLE", "immediate_left": seq[i-1][0] if left else None, "immediate_right": seq[i+1][0] if right else None})
    summaries = {}
    for reader in ("ZL3b", "IT2a"):
        reader_hits = [h for h in hits if h["reader"] == reader]
        summaries[reader] = {"complete_paragraphs_in_source": len(data[reader]), "paragraphs_with_hit": len({h["paragraph_id"] for h in reader_hits}), "exact_hits": len(reader_hits), "edge_classes": dict(sorted(Counter(h["edge_class"] for h in reader_hits).items()))}
    source_frame_global = "REJECTED_BY_PARAGRAPH_EDGE" if any(h["edge_class"] != "MIDDLE" for h in hits) else "MINIMAL_CAPACITY_ONLY"
    f89 = [h for h in hits if h["locus"] == "f89v1.14"]
    result = {"source_sha256": EXPECTED, "rule": "exact chody must have at least one written group on both sides in the same complete paragraph", "source_frame_global_decision": source_frame_global, "reader_summaries": summaries, "known_f89v1_14_hits": f89, "hits": hits, "containing_paragraphs": paragraphs, "excluded": "RF1b has no independently defined complete paragraph boundaries in GDT928; non-complete ZL3b/IT2a paragraphs are outside the frozen source"}
    out = HERE / "artifacts/RESULT.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"decision": source_frame_global, "summaries": summaries, "f89_hits": len(f89)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
