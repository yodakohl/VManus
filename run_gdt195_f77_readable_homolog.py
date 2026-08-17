#!/usr/bin/env python3
"""Build the GDT195 target-exposed readable-homolog audit."""

import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "gdt195_source_manifest.tsv"
FEATURES = ROOT / "gdt195_comparator_features.tsv"
COMPARE = ROOT / "gdt195_homolog_comparison.tsv"
NULL = ROOT / "gdt195_quality_cycle_null.tsv"
PRED = ROOT / "gdt195_predictions.tsv"
COUNTER = ROOT / "gdt195_counterexamples.tsv"
RESULT = ROOT / "gdt195_result.json"
METHOD = ROOT / "GDT195_F77_READABLE_HOMOLOG_METHOD.md"
REPORT = ROOT / "GDT195_F77_READABLE_HOMOLOG_REPORT.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def admissible(sequence: tuple[int, ...], mask: tuple[int, ...]) -> bool:
    edges = []
    for left, right, emits in zip(sequence, sequence[1:], mask):
        if emits:
            if (left - right) % 4 not in (1, 3):
                return False
            edges.append(tuple(sorted((left, right))))
        elif left != right:
            return False
    return len(edges) == 4 and set(edges) == {(0, 1), (1, 2), (2, 3), (0, 3)}


def main() -> None:
    sources = [
        dict(source_id="W73", authority="OFFICIAL_MANUSCRIPT_DESCRIPTION", manuscript="Walters MS W.73 f.7v", date="late 12th century", bibliographic_reference="Digital Walters W.73 description; inherited GDT179 source freeze", url="https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html", retrieved_utc="2026-08-17", payload_sha256="c29438b3f7a0d773dcc866adc68efe5cdfae8b3963eecbfb8f55b6ac354e018c", use="FOUR_ELEMENT_QUALITY_SQUARE"),
        dict(source_id="OBRIST2003", authority="SCHOLARLY_ARTICLE", manuscript="multiple medieval alchemical manuscripts", date="13th-15th centuries", bibliographic_reference="Barbara Obrist, Visualization in Medieval Alchemy, HYLE 9.2 (2003)", url="https://www.hyle.org/journal/issues/9-2/obrist.htm", retrieved_utc="2026-08-17", payload_sha256="3e2e609e58ccbbb31159b1b96ed81dbaac5953b54e64ce5dd9b625ed8d8f4308", use="APPARATUS_TEXT_AND_TRANSFORMATION_STAGE_HISTORY"),
        dict(source_id="WELLCOME_MS140", authority="OFFICIAL_MANUSCRIPT_CATALOGUE", manuscript="Wellcome MS.140", date="early 15th century", bibliographic_reference="Bonaventura da Iseo, Liber Compostelle, Wellcome Collection MS.140", url="https://wellcomecollection.org/works/yx25hcdh", retrieved_utc="2026-08-17", payload_sha256="8b5fe1fc63565252b2ebc63a54cef369870b0a775e45a8eade9839337643b7c0", use="PERIOD_MEDICAL_ALCHEMICAL_RECIPE_APPARATUS_COMPARATOR"),
        dict(source_id="WELLCOME_DISTILATIO", authority="OFFICIAL_COLLECTION_CATALOGUE", manuscript="unidentified Albertina 14th-century alchemical manuscript photograph", date="14th century source manuscript", bibliographic_reference="Wellcome Collection M0007061", url="https://wellcomecollection.org/works/erunapfa", retrieved_utc="2026-08-17", payload_sha256="b0e9ce5d2a155cbe1c934511fb68badfa7c23351faebda31701cb9570dbf1232", use="READABLE_APPARATUS_LABEL_COMPARATOR"),
        dict(source_id="LEHIGH_ARNALD", authority="UNIVERSITY_MANUSCRIPT_EXHIBIT", manuscript="Arnald of Brussels alchemical manuscript", date="1472-1490", bibliographic_reference="Lehigh University, Being Medieval, Arnald of Brussels", url="https://exhibits.lib.lehigh.edu/exhibits/show/medieval/secular/abrussels", retrieved_utc="2026-08-17", payload_sha256="eee7f0d3f3ff334d0fdca8f11181d35ff9b385cbc6aa6763bd5a36780a84543b", use="FOUR_ELEMENT_FOUR_STAGE_DIAGRAM_COMPARATOR"),
        dict(source_id="PAL_CR23", authority="SCHOLARLY_MANUSCRIPT_CATALOGUE", manuscript="Edinburgh Royal Observatory Cr. 2.3", date="14th c. second half-15th c. second half", bibliographic_reference="Ptolemaeus Arabus et Latinus manuscript record 6274", url="https://ptolemaeus.badw.de/jordanus/ms/6274", retrieved_utc="2026-08-17", payload_sha256="16e4e1419b28d566656d38ae58b5d5b974652fc9785e8011de422ed93dec115f", use="REPEATED_QUALITY_STATE_VOLVELLE_COMPARATOR"),
    ]
    features = [
        dict(fact_id="F01", source_id="W73", statement="A readable medieval cosmography fixes Fire=hot/dry, Air=hot/moist, Water=moist/cold and Earth=cold/dry.", support="SUPPORTED"),
        dict(fact_id="F02", source_id="OBRIST2003", statement="Medieval alchemical manuscripts link written instructions to drawings of vessels and furnaces.", support="SUPPORTED"),
        dict(fact_id="F03", source_id="OBRIST2003", statement="Fourteenth-century alchemical visualization includes diverse processes and stages of transformation in vessels.", support="SUPPORTED"),
        dict(fact_id="F04", source_id="WELLCOME_MS140", statement="MS.140 is an early-fifteenth-century Italian Latin/Italian alchemical compilation with medical and alchemical waters, recipes, distillation and sublimation.", support="SUPPORTED"),
        dict(fact_id="F05", source_id="WELLCOME_MS140", statement="MS.140 contains small pen drawings of distilling apparatus within text and in a margin.", support="SUPPORTED"),
        dict(fact_id="F06", source_id="WELLCOME_DISTILATIO", statement="A fourteenth-century alchemical apparatus image carries the readable scroll label Distilatio Aceti.", support="SUPPORTED"),
        dict(fact_id="F07", source_id="LEHIGH_ARNALD", statement="The Arnald diagram orders Water, Air, Fire and Earth and gives directions for separating the stone in four stages.", support="SUPPORTED"),
        dict(fact_id="F08", source_id="PAL_CR23", statement="A five-circle volvelle is inscribed with compound quality states and repeats calidum et humidum.", support="SUPPORTED"),
    ]
    comparison = [
        dict(comparator_id="W73", diagram_kind="ELEMENT_QUALITY_COSMOGRAPHY", four_quality_system=1, staged_process=0, apparatus=0, readable_labels=1, six_ordered_states=0, one_repeat_hold=0, mixed_four_output_one_no_output=0, exact_f77_homolog=0, assessment="GENERIC_QUALITY_SQUARE_ONLY"),
        dict(comparator_id="OBRIST2003", diagram_kind="SCHOLARLY_MULTI_MANUSCRIPT_SURVEY", four_quality_system=0, staged_process=1, apparatus=1, readable_labels=1, six_ordered_states=0, one_repeat_hold=0, mixed_four_output_one_no_output=0, exact_f77_homolog=0, assessment="GENERIC_APPARATUS_AND_STAGE_TRADITION"),
        dict(comparator_id="WELLCOME_MS140", diagram_kind="RECIPE_COMPILATION_WITH_APPARATUS", four_quality_system=0, staged_process=1, apparatus=1, readable_labels=1, six_ordered_states=0, one_repeat_hold=0, mixed_four_output_one_no_output=0, exact_f77_homolog=0, assessment="PERIOD_MEDICAL_ALCHEMICAL_ECOLOGY"),
        dict(comparator_id="WELLCOME_DISTILATIO", diagram_kind="LABELLED_DISTILLING_APPARATUS", four_quality_system=0, staged_process=0, apparatus=1, readable_labels=1, six_ordered_states=0, one_repeat_hold=0, mixed_four_output_one_no_output=0, exact_f77_homolog=0, assessment="READABLE_APPARATUS_TITLE_ONLY"),
        dict(comparator_id="LEHIGH_ARNALD", diagram_kind="FOUR_ELEMENT_SEPARATION_DIAGRAM", four_quality_system=1, staged_process=1, apparatus=0, readable_labels=1, six_ordered_states=0, one_repeat_hold=0, mixed_four_output_one_no_output=0, exact_f77_homolog=0, assessment="FOUR_ELEMENT_FOUR_STAGE_PARTIAL"),
        dict(comparator_id="PAL_CR23", diagram_kind="FIVE_CIRCLE_QUALITY_VOLVELLE", four_quality_system=1, staged_process=0, apparatus=0, readable_labels=1, six_ordered_states=0, one_repeat_hold=1, mixed_four_output_one_no_output=0, exact_f77_homolog=0, assessment="REPEATED_STATE_TOPOLOGY_PARTIAL"),
    ]
    fixed_mask = (1, 1, 0, 1, 1)
    sequences = list(itertools.product(range(4), repeat=6))
    fixed = [s for s in sequences if admissible(s, fixed_mask)]
    movable = set()
    for hold in range(5):
        mask = tuple(0 if i == hold else 1 for i in range(5))
        movable.update(s for s in sequences if admissible(s, mask))
    null_rows = [
        dict(metric="ALL_SIX_STATE_STRINGS", value=len(sequences), interpretation="complete 4^6 space"),
        dict(metric="FIXED_OBSERVED_MASK_COMPLETE_CYCLE", value=len(fixed), interpretation="four rotations times two directions"),
        dict(metric="MOVABLE_SINGLE_HOLD_COMPLETE_CYCLE", value=len(movable), interpretation="fixed solutions times five hold positions"),
        dict(metric="RETAINED_COMPARATOR_EXACT_HOMOLOGS", value=sum(int(x["exact_f77_homolog"]) for x in comparison), interpretation="none of six retained sources documents the full structure"),
    ]
    predictions = [
        dict(prediction_id="P01", frozen_requirement="A readable exact homolog has six ordered quality-state cells and the same four-output/one-no-output boundary topology.", status="UNSATISFIED_IN_RETAINED_SOURCES"),
        dict(prediction_id="P02", frozen_requirement="An independently owned readable legend fixes the four emitted products or relations without using Voynich strings.", status="NOT_AVAILABLE"),
        dict(prediction_id="P03", frozen_requirement="A second source-owned Voynich segmented system receives a complete state prediction before its inscriptions are exposed.", status="NO_ELIGIBLE_TARGET"),
        dict(prediction_id="P04", frozen_requirement="The exact six-state mixed-output structure, not generic four-quality incidence, must carry future evidential weight.", status="ACTIVE_REQUIREMENT"),
    ]
    counter = [
        dict(counterexample_id="C01", observation="None of six retained readable comparators has the full six-state mixed-output topology.", impact="no exact historical homolog"),
        dict(counterexample_id="C02", observation="Four-element coverage is forced by a complete traversal of the four-quality cycle.", impact="not independent semantic evidence"),
        dict(counterexample_id="C03", observation="The GDT180 state assignment was exposed and inherited from a post-hoc f57 decoder.", impact="cannot confirm itself"),
        dict(counterexample_id="C04", observation="A cached human puff-order proposal disagrees with the predicted four-output order at all four positions.", impact="blocks direct output glosses"),
        dict(counterexample_id="C05", observation="No second mixed-output segmented Voynich system exists in the current annotation capacity.", impact="no prospective transfer"),
        dict(counterexample_id="C06", observation="The PAL volvelle repeats a quality state without a process hold or mixed-output topology.", impact="repetition alone is nonspecific"),
    ]
    write_tsv(MANIFEST, sources)
    write_tsv(FEATURES, features)
    write_tsv(COMPARE, comparison)
    write_tsv(NULL, null_rows)
    write_tsv(PRED, predictions)
    write_tsv(COUNTER, counter)
    result = {
        "experiment": "GDT195_F77_READABLE_HOMOLOG_AUDIT",
        "status": "ALCHEMICAL_SOURCE_FAMILY_PLAUSIBLE_EXACT_F77_HOMOLOG_NOT_FOUND",
        "target_exposure": "POSTHOC_SOURCE_FAMILY_AUDIT_OF_EXPOSED_GDT180_TARGET",
        "counts": {
            "sources": len(sources),
            "source_facts": len(features),
            "comparators": len(comparison),
            "exact_homologs": sum(int(x["exact_f77_homolog"]) for x in comparison),
            "all_six_state_sequences": len(sequences),
            "fixed_mask_complete_cycles": len(fixed),
            "movable_hold_complete_cycles": len(movable),
            "predictions": len(predictions),
            "counterexamples": len(counter),
        },
        "interpretation": {
            "broad_medical_alchemical_diagram_ecology": "SUPPORTED_AS_HISTORICAL_PRIOR",
            "exact_six_state_mixed_output_homolog": "NOT_FOUND_IN_RETAINED_SOURCES",
            "four_element_coverage_independent_evidence": False,
            "f77_state_words_translated": False,
        },
        "inputs": {
            "gdt179_w73_comparator_manifest.tsv": sha(ROOT / "gdt179_w73_comparator_manifest.tsv"),
            "gdt179_source_provenance.json": sha(ROOT / "gdt179_source_provenance.json"),
            "gdt180_f77_process_steps.tsv": sha(ROOT / "gdt180_f77_process_steps.tsv"),
            "gdt180_f77_transition_translation.tsv": sha(ROOT / "gdt180_f77_transition_translation.tsv"),
            "gdt180_result.json": sha(ROOT / "gdt180_result.json"),
        },
        "outputs": {p.name: sha(p) for p in (MANIFEST, FEATURES, COMPARE, NULL, PRED, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": sha(Path(__file__)),
        "f84_accessed": False,
        "claim_ceiling": "Broad medieval medical-alchemical diagram-practice prior and an algebraic dependency correction only; no Voynich state name, word, operation, material, language, plaintext, or translation.",
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], result["counts"])


if __name__ == "__main__":
    main()
