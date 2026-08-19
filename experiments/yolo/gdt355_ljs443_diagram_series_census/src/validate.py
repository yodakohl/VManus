#!/usr/bin/env python3
"""Nonimporting integrity validator for the external-only GDT355 census."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt355_ljs443_diagram_series_census"
ART = EXP / "artifacts"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


EXPECTED = [
    ("192r","193r","0388","2b2cc7271160549530540e2aa55033d4c1a6869077f0fe4a9e188612d088e818"),
    ("192v","193v","0389","8dc9f2bd00c077e41d84d7176f47b507e340e82a4de6b69fccfe791241cf160e"),
    ("193r","194r","0390","e6478526b64d0006316d543f87efade4b36edde1dde400179b2e55897fc14237"),
    ("193v","194v","0391","8d0cb583ddb2a3ebcfc449e1d6206c9baea4db5d0bd696ddf8a2f11354bb5d5a"),
    ("194r","195r","0392","6b0e164434dd59d0852346876df97e5c9c373f0b9c523913a5f4efc76ba1c623"),
    ("194v","195v","0393","892fd80a7e48cee9866564bcc40cafec4d174140c4a0373791418f519a517cca"),
    ("195r","196r","0394","331908d9796a004c68d47616d2910e8593d09eb0e78f91945ea15814557de641"),
    ("195v","196v","0395","00ab60fcec1f02abb007ee9aaeb20416d3462650d35137b7ab6fdd3c2896294e"),
    ("196r","197r","0396","de581d4c773861b500446c9e73106ecc41d1990a5d314db703831b052ff11396"),
    ("196v","197v","0397","99c59fe22354dc11eb074d960f914386b4c50e0eb177a034be2636808d66fb71"),
    ("197r","198r","0398","0fab117fb224ab7b6c5d35c21e2b4431711ab80de108b17cc72f3b81ded0d544"),
    ("197v","198v","0399","d86f3131c5cdfec1ea7b54bb1debcb0529b572818fbd1be4ea7a541d64448b93"),
    ("198r","199r","0400","8fedf8f382dee2512e21a7f7422101883b57becfec712d037c83b9eeca13148d"),
    ("198v","199v","0401","e5bc618f73e916a1dc8c3c526496301167e58a2ff671e600dec3ef93917309c7"),
    ("199r","200r","0402","d13d9a30a208106c5771cf123b2dc93c371dba52f3583be4a9bc673a2d95b68d"),
    ("199v","200v","0403","0c034888f22df6f45ec0b445225a9d3e7ac39761d35096f2f3bf86d264f68854"),
    ("200r","201r","0404","61def253be82386f18c5d30d0b306e6e61b3023b392db5862198d7e0ae6f0e75"),
    ("200v","201v","0405","ccaf064135112e8b70ae05030d0a801cc7d33f3ce70dfcfb247957c68f80ef29"),
    ("201r","202r","0406","4c2c5c4378f557c1bbb4ba9d96f4aa2816ab65abb6b85af545f0422b9061c87a"),
    ("201v","202v","0407","f7f0694038ee24c3e23b13d49927d757a64fb2b9e73da3561d3cc8d33ae5358c"),
    ("202r","203r","0408","9471c96d543edcd9f257e4afb14717309c67809d63ec71ac12dd91f1cbf4e812"),
    ("202v","203v","0409","03828bef16b6dda95c004879e243a2bfd92f0df529b2f006557134a8f0582301"),
    ("203r","204r","0410","2fab30f439336d9d574cd678ddfb9237d921f16df0853cee0f684f322f621480"),
    ("204r","205r","0412","c8a626ca95f35ed1386f8326f01bd838526e0a55e32bbd8bec1d65ecee88cb6f"),
    ("204v","205v","0413","00e714f36789104a80f092a120b7441c5864195749174afb722da6965a81bf0b"),
    ("205r","206r","0414","c78103a4ae85ae7caae3629acd5a963a8aeae06fc1a2bda6cb108b1aea014eec"),
    ("205v","206v","0415","85f3ab3b7be0ed37a2bf5ba87d3ffdf10163282edd8d712d6810a592479f6c66"),
    ("206r","207r","0416","df8c404a3c6b36f9305267099e96f4b31b044e42f94b2fbb09e1a749fc0e51ed"),
    ("206v","207v","0417","4bbb6c0b44d13270451885fd52759913c007ef4eff64e6a096e6b7a8d89b23ed"),
    ("207r","208r","0418","03466142ceef08dabf3f4aee2f1326600988a089d33a5a2ff10f8862d2468141"),
    ("207v","208v","0419","8e6e280e7837d185155cc00b001d81ddeb77c3ba94645e7e28960f587e2a77da"),
    ("208r","209r","0420","07665890586424a0384db862c3f5713ed9a8afd5aab6980650baf1b7a0241274"),
    ("208v","209v","0421","83a0b642be6ebe4e1ba732cf3e46eb6994b36d7ce79a34c4a124a2b30eb692ba"),
    ("209r","210r","0422","a218414d67f5044281c8cf6e6a3606447d01b023782a8756d1a3a3207a660530"),
    ("209v","210v","0423","8254c56b22c5990cd560f7cfcc2efa6105803ee87954b2ea11a191b5bad768bf"),
    ("210r","211r","0424","6c5227d8f040c16c9d9eed8d2d5563c3c0d5a711f32038af35e47d5a9d28f875"),
    ("211r","212r","0426","c525891f0d16035d4feb4dc4eff02f828195afc4915719f15b1837df04cdafcd"),
    ("211v","212v","0427","b593006e1a6c3cbe6dff6c643171d5cd70f4829d4fe7d7cabea09cf47f848177"),
]


def main() -> None:
    sources = read(ART / "gdt355_external_sources.tsv")
    census = read(ART / "gdt355_diagram_census.tsv")
    summary = read(ART / "gdt355_family_summary.tsv")
    counterexamples = read(ART / "gdt355_counterexamples.tsv")
    result = json.loads((ART / "gdt355_result.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def ck(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name":name,"pass":bool(passed),"detail":detail})

    ck("census_count", len(census) == 38)
    ck("source_count", len(sources) == 39)
    ck("ordinals", [int(row["surface_ordinal"]) for row in census] == list(range(1,39)))
    observed = [(row["current_folio"],row["old_folio"],row["image_file"][5:9],row["remote_sha256"]) for row in census]
    ck("exact_surface_mapping", observed == EXPECTED)
    ck("unique_surface_files", len({row["image_file"] for row in census}) == 38)
    ck("hash_shapes", all(len(row["remote_sha256"]) == 64 for row in census))
    ck("official_urls", all(row["official_url"].endswith(row["image_file"]) for row in census))
    ck("direct_external_provenance", all(row["provenance"] == "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION" for row in census))
    ck("complete_reviews", all(row["review_status"] == "COMPLETE" for row in census))
    ck("neutral_interpretation", all(row["interpretation"] == "NONE_GEOMETRY_ONLY" for row in census))

    narrow = [row["image_file"][5:9] for row in census if row["narrow_spiral_band_family"] == "YES"]
    broad = [row["image_file"][5:9] for row in census if row["broad_eight_curved_family"] == "YES"]
    curved_non8 = [row["image_file"][5:9] for row in census if row["curved_primary_compartments"] == "YES" and row["primary_compartment_count"] != "8"]
    other8 = [row["image_file"][5:9] for row in census if row["primary_compartment_count"] == "8" and row["broad_eight_curved_family"] == "NO"]
    ck("narrow_exact", narrow == ["0422","0423","0424"])
    ck("broad_exact", broad == ["0418","0419","0422","0423","0424"])
    ck("curved_non8_exact", curved_non8 == ["0417"])
    ck("curved_non8_count", next(row for row in census if row["image_file"] == "0088_0417_web.jpg")["primary_compartment_count"] == "12")
    ck("other8_exact", other8 == ["0393","0408","0412","0414"])
    ck("secure_count_rows", sum(row["count_confidence"] == "HIGH" for row in census) == 14)
    ck("unknowns_explicit", all(row["primary_compartment_count"] != "" and row["count_confidence"] != "" for row in census))

    by_metric = {row["metric"]:int(row["count"]) for row in summary}
    ck("summary_surface_count", by_metric.get("TEI_DIAGRAM_SURFACES_REVIEWED") == 38)
    ck("summary_narrow", by_metric.get("NARROW_EIGHT_SPIRAL_BAND_SURFACES") == len(narrow) == 3)
    ck("summary_broad", by_metric.get("BROAD_EIGHT_CURVED_SURFACES") == len(broad) == 5)
    ck("summary_non8", by_metric.get("NON_EIGHT_CURVED_SURFACES") == len(curved_non8) == 1)
    ck("summary_other8", by_metric.get("OTHER_EXACT_EIGHT_TOPOLOGIES") == len(other8) == 4)
    ck("counterexample_count", len(counterexamples) == 4)
    ck("counterexample_0417", counterexamples[0]["image_file"] == "0088_0417_web.jpg" and "Twelve" in counterexamples[0]["observation"])

    ck("result_status", result["status"] == "EIGHT_BAND_SUBFAMILY_RECURRENT_RENDERING_NOT_EIGHT_SPECIFIC")
    ck("result_counts", result["counts"]["official_facsimile_rows"] == 38 and result["counts"]["broad_eight_curved_surfaces"] == 5)
    ck("no_voynich_image", result["source_access"]["voynich_images_opened"] is False)
    ck("no_voynich_formal", result["source_access"]["voynich_transcription_or_formal_payload_opened"] is False)
    ck("no_f84_access", result["source_access"]["f84_rows_or_images_accessed"] is False)
    ck("no_automated_visual_classifier", result["source_access"]["automated_visual_classification_used"] is False)
    # Inspect provenance-bearing identifiers and descriptions, not digest text:
    # a valid external-image SHA-256 happens to contain the substring ``f84``.
    seal_fields = {
        "source_id", "manuscript_folio", "legacy_folio", "image_file",
        "source_url", "topology_class", "neutral_description",
        "family", "member_surface_ids", "counterexample", "implication",
    }
    ck(
        "no_f84_output",
        all(
            "f84" not in "\t".join(
                str(value) for key, value in row.items() if key in seal_fields
            ).lower()
            for row in sources + census + summary + counterexamples
        ),
    )
    ck("no_vendored_images", not any(EXP.rglob("*.jpg")) and not any(EXP.rglob("*.png")))

    for rel,digest in result["inputs"].items():
        ck("input_hash:"+rel, sha(ROOT/rel) == digest)
    for rel,digest in result["outputs"].items():
        ck("output_hash:"+rel, sha(ROOT/rel) == digest)
    for rel,digest in result["documents"].items():
        ck("document_hash:"+rel, sha(ROOT/rel) == digest)
    for rel,digest in result["implementation"].items():
        ck("implementation_hash:"+rel, sha(ROOT/rel) == digest)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    ck("content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)

    output = {
        "experiment":"GDT355",
        "schema":"GDT355_VALIDATION_V1",
        "status":"PASS" if all(row["pass"] for row in checks) else "FAIL",
        "scope":"Independent fixed-inventory, family-membership, count, hash and seal validation. It does not independently re-review or classify the external facsimiles and does not re-fetch remote bytes.",
        "checks_passed":sum(row["pass"] for row in checks),
        "checks_failed":sum(not row["pass"] for row in checks),
        "checks":checks,
        "result_sha256":sha(ART/"gdt355_result.json"),
        "implementation_sha256":sha(Path(__file__)),
    }
    (ART/"gdt355_validation.json").write_bytes(stable(output))
    print(output["status"],output["checks_passed"],output["checks_failed"])
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
