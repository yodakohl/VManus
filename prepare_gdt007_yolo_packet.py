#!/usr/bin/env python3
"""Reconcile two GDT007 localizers and emit an opaque review packet."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


def rows(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def xywh(value):
    return tuple(map(int, value.split(",")))


def key(row):
    return row["pair_id"], row["arm"], row["cut_ordinal"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("localizer_a")
    p.add_argument("localizer_b")
    p.add_argument("output_dir")
    p.add_argument("public_reconciliation")
    p.add_argument("--nonce-file", required=True)
    p.add_argument("--max-delta", type=int, default=50)
    args = p.parse_args()
    out = Path(args.output_dir)
    (out / "images").mkdir(parents=True, exist_ok=True)
    nonce = Path(args.nonce_file).read_text().strip()
    assert len(nonce) >= 32

    aa = {key(r): r for r in rows(args.localizer_a)}
    bb = {key(r): r for r in rows(args.localizer_b)}
    assert len(aa) == len(bb) == 34 and set(aa) == set(bb)
    public = []
    private = []
    for probe in sorted(aa):
        a, b = aa[probe], bb[probe]
        ax = xywh(a["crop_xywh"])[0] + int(a["marker_x_in_crop"])
        bx = xywh(b["crop_xywh"])[0] + int(b["marker_x_in_crop"])
        delta = abs(ax - bx)
        agree = delta <= args.max_delta
        variants = [("A", a)] if agree else [("A", a), ("B", b)]
        for label, row in variants:
            if label == "A":
                image = Path(args.localizer_a).parent / "marked_source_named" / row["marked_crop_file"]
            else:
                image = Path(row["marked_crop_path"])
            assert image.is_file()
            stable = "|".join(probe + (label, str(delta)))
            blind_id = "YC" + hashlib.sha256((nonce + "|" + stable).encode()).hexdigest()[:14].upper()
            destination = out / "images" / f"{blind_id}.png"
            shutil.copyfile(image, destination)
            private.append({
                "blind_id": blind_id,
                "pair_id": probe[0], "arm": probe[1], "cut_ordinal": probe[2],
                "locus": a["locus"], "surface": a["surface"],
                "localizer_variant": label, "localizer_delta_px": str(delta),
                "localizer_a_confidence": a["confidence"], "localizer_b_confidence": b["confidence"],
                "agreement_within_50px": "1" if agree else "0",
                "delivered_image_sha256": digest(destination),
            })
        public.append({
            "pair_id": probe[0], "arm": probe[1], "cut_ordinal": probe[2],
            "locus": a["locus"], "group_index": a["group_index"], "surface": a["surface"],
            "original_display_cut_offset": a["original_display_cut_offset"],
            "effective_display_cut_offset": a["effective_display_cut_offset"],
            "original_offset_state": a["original_offset_state"], "replacement_rule": a["replacement_rule"],
            "source_sta_codes": a["source_sta_codes"], "canvas_id": a["canvas_id"],
            "full_image_url": a["full_image_url"], "full_image_sha256": a["full_image_sha256"],
            "localizer_a_crop_xywh": a["crop_xywh"], "localizer_a_marker_x_in_crop": a["marker_x_in_crop"], "localizer_a_marker_y_range": a["marker_y_range"],
            "localizer_b_crop_xywh": b["crop_xywh"], "localizer_b_marker_x_in_crop": b["marker_x_in_crop"], "localizer_b_marker_y_range": b["marker_y_range"],
            "localizer_a_full_x": str(ax), "localizer_b_full_x": str(bx), "absolute_delta_px": str(delta),
            "localizer_a_confidence": a["confidence"], "localizer_b_confidence": b["confidence"],
            "reconciliation_state": "AGREE_WITHIN_50PX" if agree else "DISAGREE_RETAIN_BOTH_VARIANTS",
            "review_variant_count": str(len(variants)),
            "localizer_a_crop_sha256": a["marked_crop_sha256"],
            "localizer_b_crop_sha256": digest(b["marked_crop_path"]),
            "provenance": "AI_DIRECT_VISUAL_OBSERVATION_LOCALIZATION_ONLY",
        })

    private.sort(key=lambda r: r["blind_id"])
    with (out / "worklist.tsv").open("w", newline="", encoding="utf-8") as f:
        fields = ["blind_id", "image_path", "image_sha256", "marker_instruction", "allowed_states"]
        w = csv.DictWriter(f, delimiter="\t", lineterminator="\n", fieldnames=fields); w.writeheader()
        for row in private:
            w.writerow({"blind_id": row["blind_id"], "image_path": f"images/{row['blind_id']}.png", "image_sha256": row["delivered_image_sha256"], "marker_instruction": "Classify manuscript geometry at red marker; ignore overlay", "allowed_states": "INK_TOUCH_OR_CROSSING|NARROW_VISIBLE_GAP|ORDINARY_VISIBLE_GAP|WIDE_VISIBLE_GAP|UNRESOLVED"})
    private_path = out.parent / f"{out.name}_private_join.tsv"
    with private_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, delimiter="\t", lineterminator="\n", fieldnames=list(private[0])); w.writeheader(); w.writerows(private)
    with Path(args.public_reconciliation).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, delimiter="\t", lineterminator="\n", fieldnames=list(public[0])); w.writeheader(); w.writerows(public)
    summary = {"probes": len(public), "agreement_within_50px": sum(r["reconciliation_state"] == "AGREE_WITHIN_50PX" for r in public), "disagreements": sum(r["reconciliation_state"].startswith("DISAGREE") for r in public), "review_crops": len(private), "max_delta_px": args.max_delta, "localizer_a_sha256": digest(args.localizer_a), "localizer_b_sha256": digest(args.localizer_b), "worklist_sha256": digest(out / "worklist.tsv")}
    (out / "packet_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
