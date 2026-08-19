#!/usr/bin/env python3
"""Build the external-only GDT355 LJS 443 diagram-series census."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt355_ljs443_diagram_series_census"
ART = EXP / "artifacts"
GDT354_RESULT = ROOT / "experiments/yolo/gdt354_ljs443_f68v3_source_audit/artifacts/gdt354_result.json"


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# ordinal, current folio, old folio, image number, sha256, topology, count,
# count confidence, central circle, curved, text in primary compartments,
# repeated ring/crescent marks, broad eight-curved family, narrow spiral family,
# neutral description
SERIES = [
    (1,"192r","193r","0388","2b2cc7271160549530540e2aa55033d4c1a6869077f0fe4a9e188612d088e818","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Multiple concentric rings crossed by many radial divisions and filled with text."),
    (2,"192v","193v","0389","8dc9f2bd00c077e41d84d7176f47b507e340e82a4de6b69fccfe791241cf160e","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a multi-ring radial text grid."),
    (3,"193r","194r","0390","e6478526b64d0006316d543f87efade4b36edde1dde400179b2e55897fc14237","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by concentric text rings and radial divisions."),
    (4,"193v","194v","0391","8d0cb583ddb2a3ebcfc449e1d6206c9baea4db5d0bd696ddf8a2f11354bb5d5a","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a multi-ring radial text grid."),
    (5,"194r","195r","0392","6b0e164434dd59d0852346876df97e5c9c373f0b9c523913a5f4efc76ba1c623","CONCENTRIC_PARTITIONED_RINGS","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Separated inner and outer partitioned text rings around a central circle."),
    (6,"194v","195v","0393","892fd80a7e48cee9866564bcc40cafec4d174140c4a0373791418f519a517cca","EIGHT_SECTOR_ANNULAR_GRID","8","HIGH","YES","NO","YES","NO","NO","NO","Eight clear major radial sectors subdivided by concentric rings."),
    (7,"195r","196r","0394","331908d9796a004c68d47616d2910e8593d09eb0e78f91945ea15814557de641","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Dense annular text grid with many radial divisions."),
    (8,"195v","196v","0395","00ab60fcec1f02abb007ee9aaeb20416d3462650d35137b7ab6fdd3c2896294e","RING_WITH_CENTRAL_TEXT","UNKNOWN","UNKNOWN","NO","NO","YES","NO","NO","NO","One partitioned outer text ring enclosing a prose-filled center."),
    (9,"196r","197r","0396","de581d4c773861b500446c9e73106ecc41d1990a5d314db703831b052ff11396","CONCENTRIC_ARC_SERIES","UNKNOWN","UNKNOWN","YES","NO","YES","YES","NO","NO","Nested circular arcs with text and repeated hollow circular marks."),
    (10,"196v","197v","0397","99c59fe22354dc11eb074d960f914386b4c50e0eb177a034be2636808d66fb71","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (11,"197r","198r","0398","0fab117fb224ab7b6c5d35c21e2b4431711ab80de108b17cc72f3b81ded0d544","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (12,"197v","198v","0399","d86f3131c5cdfec1ea7b54bb1debcb0529b572818fbd1be4ea7a541d64448b93","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (13,"198r","199r","0400","8fedf8f382dee2512e21a7f7422101883b57becfec712d037c83b9eeca13148d","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (14,"198v","199v","0401","e5bc618f73e916a1dc8c3c526496301167e58a2ff671e600dec3ef93917309c7","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (15,"199r","200r","0402","d13d9a30a208106c5771cf123b2dc93c371dba52f3583be4a9bc673a2d95b68d","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (16,"199v","200v","0403","0c034888f22df6f45ec0b445225a9d3e7ac39761d35096f2f3bf86d264f68854","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (17,"200r","201r","0404","61def253be82386f18c5d30d0b306e6e61b3023b392db5862198d7e0ae6f0e75","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Open central circle surrounded by a dense radial text grid."),
    (18,"200v","201v","0405","ccaf064135112e8b70ae05030d0a801cc7d33f3ce70dfcfb247957c68f80ef29","BLANK_ANNULAR_GRID","UNKNOWN","UNKNOWN","YES","NO","NO","NO","NO","NO","Unfilled concentric-ring and radial-line grid."),
    (19,"201r","202r","0406","4c2c5c4378f557c1bbb4ba9d96f4aa2816ab65abb6b85af545f0422b9061c87a","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Central text circle surrounded by a dense radial text grid."),
    (20,"201v","202v","0407","f7f0694038ee24c3e23b13d49927d757a64fb2b9e73da3561d3cc8d33ae5358c","INTERLACED_CIRCLE_ROSETTE","UNKNOWN","UNKNOWN","YES","NO","NO","NO","NO","NO","Many interlaced circular loops form a rosette around a small center."),
    (21,"202r","203r","0408","9471c96d543edcd9f257e4afb14717309c67809d63ec71ac12dd91f1cbf4e812","EIGHT_INTERLACED_TEXT_ROSETTE","8","HIGH","YES","NO","YES","NO","NO","NO","Eight interlaced circular zones around a small central rosette, with text in the zones."),
    (22,"202v","203v","0409","03828bef16b6dda95c004879e243a2bfd92f0df529b2f006557134a8f0582301","THREE_TRIPLE_CIRCLE_DIAGRAMS","3_EACH","HIGH","NO","NO","YES","NO","NO","NO","Three separate diagrams, each containing three overlapping circles."),
    (23,"203r","204r","0410","2fab30f439336d9d574cd678ddfb9237d921f16df0853cee0f684f322f621480","INTERLACED_ANNULAR_GRID","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Two crossing families of curved grid lines form a dense annular lattice."),
    (24,"204r","205r","0412","c8a626ca95f35ed1386f8326f01bd838526e0a55e32bbd8bec1d65ecee88cb6f","EIGHT_RADIAL_SECTOR_WHEEL","8","HIGH","YES","NO","YES","NO","NO","NO","Eight straight radial wedges around a small central circle, with text in each wedge."),
    (25,"204v","205v","0413","00e714f36789104a80f092a120b7441c5864195749174afb722da6965a81bf0b","GRIDDED_CIRCLE_WITH_CROSS","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Concentric circular zones crossed by a prominent rectilinear frame and diagonals."),
    (26,"205r","206r","0414","c78103a4ae85ae7caae3629acd5a963a8aeae06fc1a2bda6cb108b1aea014eec","EIGHT_ANNULAR_SECTOR_WHEEL","8","HIGH","NO","NO","YES","NO","NO","NO","Eight straight annular sectors around a prose-filled center."),
    (27,"205v","206v","0415","85f3ab3b7be0ed37a2bf5ba87d3ffdf10163282edd8d712d6810a592479f6c66","ANNULAR_SECTOR_WHEEL","UNKNOWN","UNKNOWN","NO","NO","YES","NO","NO","NO","Multiple straight annular sectors around a prose-filled center; exact primary count retained unknown."),
    (28,"206r","207r","0416","df8c404a3c6b36f9305267099e96f4b31b044e42f94b2fbb09e1a749fc0e51ed","TWELVE_RADIAL_SECTOR_WHEEL","12","HIGH","YES","NO","YES","NO","NO","NO","Twelve straight radial wedges around a central circle, with text in the wedges."),
    (29,"206v","207v","0417","4bbb6c0b44d13270451885fd52759913c007ef4eff64e6a096e6b7a8d89b23ed","TWELVE_CURVED_LOBE_WHEEL","12","HIGH","YES","YES","YES","NO","NO","NO","Twelve curved text-bearing lobes radiate around a central circle."),
    (30,"207r","208r","0418","03466142ceef08dabf3f4aee2f1326600988a089d33a5a2ff10f8862d2468141","EIGHT_DECORATED_CURVED_COMPARTMENT_WHEEL","8","HIGH","YES","YES","YES","NO","YES","NO","Eight decorated petal-like curved text compartments surround a central text circle."),
    (31,"207v","208v","0419","8e6e280e7837d185155cc00b001d81ddeb77c3ba94645e7e28960f587e2a77da","EIGHT_DECORATED_CURVED_COMPARTMENT_WHEEL","8","HIGH","YES","YES","YES","NO","YES","NO","Eight decorated petal-like curved text compartments surround a blank central circle."),
    (32,"208r","209r","0420","07665890586424a0384db862c3f5713ed9a8afd5aab6980650baf1b7a0241274","TWELVE_RADIAL_SECTOR_WHEEL","12","HIGH","YES","NO","YES","NO","NO","NO","Twelve straight radial sectors around concentric central rings."),
    (33,"208v","209v","0421","83a0b642be6ebe4e1ba732cf3e46eb6994b36d7ce79a34c4a124a2b30eb692ba","TWELVE_RADIAL_SECTOR_WHEEL","12","HIGH","YES","NO","YES","NO","NO","NO","Twelve straight radial text sectors around a central circle."),
    (34,"209r","210r","0422","a218414d67f5044281c8cf6e6a3606447d01b023782a8756d1a3a3207a660530","EIGHT_SPIRAL_CURVED_BAND_WHEEL","8","HIGH","YES","YES","YES","YES","YES","YES","Eight inward-curving text bands surround a blank central circle; repeated ringed and crescent-like marks occur around the cycle."),
    (35,"209v","210v","0423","8254c56b22c5990cd560f7cfcc2efa6105803ee87954b2ea11a191b5bad768bf","EIGHT_SPIRAL_CURVED_BAND_WHEEL","8","HIGH","YES","YES","YES","YES","YES","YES","Eight inward-curving text bands surround a blank central circle; repeated crescent-like and circular marks occur around the cycle."),
    (36,"210r","211r","0424","6c5227d8f040c16c9d9eed8d2d5563c3c0d5a711f32038af35e47d5a9d28f875","EIGHT_SPIRAL_CURVED_BAND_WHEEL","8","HIGH","YES","YES","YES","YES","YES","YES","Eight inward-curving text bands surround a blank central circle; repeated ringed and crescent-like marks occur around the cycle."),
    (37,"211r","212r","0426","c525891f0d16035d4feb4dc4eff02f828195afc4915719f15b1837df04cdafcd","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Dense annular table with a narrow radial opening and many concentric rows."),
    (38,"211v","212v","0427","b593006e1a6c3cbe6dff6c643171d5cd70f4829d4fe7d7cabea09cf47f848177","ANNULAR_GRID_TABLE","UNKNOWN","UNKNOWN","YES","NO","YES","NO","NO","NO","Dense annular grid with many radial columns and concentric rows."),
]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    fields = [
        "surface_ordinal","current_folio","old_folio","image_file","official_url","remote_sha256",
        "provenance","review_status","confidence","primary_topology","primary_compartment_count",
        "count_confidence","central_circle","curved_primary_compartments","text_in_primary_compartments",
        "repeated_crescent_or_ring_marks","broad_eight_curved_family","narrow_spiral_band_family",
        "interpretation","neutral_description",
    ]
    census: list[dict[str, object]] = []
    for ordinal,current,old,image,digest,topology,count,count_conf,central,curved,text_in,marks,broad,narrow,description in SERIES:
        census.append(dict(zip(fields, [
            ordinal,current,old,f"0088_{image}_web.jpg",
            f"https://openn.library.upenn.edu/Data/0001/ljs443/data/web/0088_{image}_web.jpg",
            digest,"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","COMPLETE","HIGH",topology,count,count_conf,
            central,curved,text_in,marks,broad,narrow,"NONE_GEOMETRY_ONLY",description,
        ])))

    sources = [{
        "source_id": "LJS443_TEI",
        "source_class": "OFFICIAL_LIBRARY_METADATA",
        "folio_or_scope": "whole manuscript and diagram surfaces on current ff.192r-211v",
        "official_url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/ljs443_TEI.xml",
        "remote_sha256": "becfa33a8ca1952a7c914e09d070e4d7cdd4f3509291998916a956397b8391b4",
        "exact_support": "Armenian post-1416 collection of calendar commentaries, treatises, tables and diagrams; TEI identifies the selected surfaces as diagrams.",
    }]
    sources.extend({
        "source_id": f"LJS443_{row['image_file'][5:9]}",
        "source_class": "OFFICIAL_PRIMARY_FACSIMILE",
        "folio_or_scope": f"{row['current_folio']} = old {row['old_folio']}",
        "official_url": row["official_url"],
        "remote_sha256": row["remote_sha256"],
        "exact_support": "Official OPenn facsimile surface identified as a diagram by the TEI.",
    } for row in census)

    topology_counts = Counter(str(row["primary_topology"]) for row in census)
    summary = [
        {"metric":"TEI_DIAGRAM_SURFACES_REVIEWED","count":"38","basis":"Complete selected OPenn diagram run."},
        {"metric":"NARROW_EIGHT_SPIRAL_BAND_SURFACES","count":str(sum(row["narrow_spiral_band_family"] == "YES" for row in census)),"basis":"Exact GDT354 rendering."},
        {"metric":"BROAD_EIGHT_CURVED_SURFACES","count":str(sum(row["broad_eight_curved_family"] == "YES" for row in census)),"basis":"Eight curved text-bearing compartments around a central circle."},
        {"metric":"NON_EIGHT_CURVED_SURFACES","count":str(sum(row["curved_primary_compartments"] == "YES" and row["primary_compartment_count"] != "8" for row in census)),"basis":"Curved primary compartments with secure non-eight count."},
        {"metric":"OTHER_EXACT_EIGHT_TOPOLOGIES","count":str(sum(row["primary_compartment_count"] == "8" and row["broad_eight_curved_family"] == "NO" for row in census)),"basis":"Secure eightfold count without broad curved-compartment membership."},
        {"metric":"SECURE_COUNT_ROWS","count":str(sum(row["count_confidence"] == "HIGH" for row in census)),"basis":"Only directly clear primary divisions; all others remain UNKNOWN."},
        {"metric":"DISTINCT_TOPOLOGY_CLASSES","count":str(len(topology_counts)),"basis":"Broad descriptive categories, not semantic types."},
    ]
    counterexamples = [
        {"counterexample_id":"CE01_CURVED_NOT_EIGHT","surface":"206v = old 207v","image_file":"0088_0417_web.jpg","observation":"Twelve curved text-bearing lobes surround a central circle.","implication":"The broad curved-lobe idiom is not an eight-value key."},
        {"counterexample_id":"CE02_EIGHT_NOT_ONE_RENDERING","surface":"multiple","image_file":"0088_0393;0408;0412;0414","observation":"Four secure eightfold primary divisions use straight-sector or interlaced-circle topologies.","implication":"Eight recurs across several graphic encodings and does not identify the narrow spiral rendering."},
        {"counterexample_id":"CE03_ONE_LOCAL_SERIES","surface":"192r-211v","image_file":"38 official surfaces","observation":"All observations come from one contiguous diagram run in one manuscript.","implication":"The pages are not independent cultural witnesses or prevalence samples."},
        {"counterexample_id":"CE04_NO_SLOT_KEY","surface":"209r-210r","image_file":"0088_0422;0423;0424","observation":"Visible text and marks do not provide a scholarly compartment transcription, start, direction, or value key.","implication":"No Voynich slot alignment is authorized."},
    ]

    source_path = ART / "gdt355_external_sources.tsv"
    census_path = ART / "gdt355_diagram_census.tsv"
    summary_path = ART / "gdt355_family_summary.tsv"
    counter_path = ART / "gdt355_counterexamples.tsv"
    write_tsv(source_path, sources)
    write_tsv(census_path, census)
    write_tsv(summary_path, summary)
    write_tsv(counter_path, counterexamples)

    result = {
        "experiment":"GDT355",
        "schema":"GDT355_LJS443_DIAGRAM_SERIES_CENSUS_V1",
        "status":"EIGHT_BAND_SUBFAMILY_RECURRENT_RENDERING_NOT_EIGHT_SPECIFIC",
        "exposure":"POST_GDT354_EXTERNAL_SERIES_DESCRIPTIVE_CENSUS",
        "counts":{
            "official_metadata_rows":1,
            "official_facsimile_rows":38,
            "direct_external_visual_observations":38,
            "external_manuscripts":1,
            "narrow_eight_spiral_band_surfaces":3,
            "broad_eight_curved_surfaces":5,
            "secure_non_eight_curved_surfaces":1,
            "other_secure_eight_topologies":4,
            "secure_count_rows":14,
            "distinct_topology_classes":len(topology_counts),
        },
        "key_counterexample":"Current f.206v / old f.207v has twelve curved text-bearing lobes, so curved lobes are not specific to eight.",
        "decision":"Retain LJS 443 as a strong period-appropriate diagram-family comparator and its three-page narrow eight-band subseries; require a scholarly folio key before any semantic or text alignment.",
        "source_access":{
            "external_images_opened":True,
            "voynich_images_opened":False,
            "voynich_transcription_or_formal_payload_opened":False,
            "f84_rows_or_images_accessed":False,
            "automated_visual_classification_used":False,
        },
        "claim_ceiling":"Recurrent local eight-curved-compartment subfamily plus a non-eight curved-lobe counterexample only; no lunar-table identity, slot value, start, direction, copying, Armenian origin, language, plaintext, or translation.",
        "inputs":{
            str(GDT354_RESULT.relative_to(ROOT)):sha(GDT354_RESULT),
        },
        "outputs":{str(path.relative_to(ROOT)):sha(path) for path in (source_path,census_path,summary_path,counter_path)},
        "documents":{str(path.relative_to(ROOT)):sha(path) for path in (EXP/"METHOD.md",EXP/"SOURCE_AUDIT.md",EXP/"REPORT.md")},
        "implementation":{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt355_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
