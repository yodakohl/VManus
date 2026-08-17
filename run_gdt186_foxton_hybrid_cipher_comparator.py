#!/usr/bin/env python3
"""Freeze the GDT186 historical source/mechanism comparator."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MANIFEST = ROOT / "gdt186_source_manifest.tsv"
FACTS = ROOT / "gdt186_historical_mechanisms.tsv"
COMPARE = ROOT / "gdt186_architecture_comparison.tsv"
PREDICTIONS = ROOT / "gdt186_predictions.tsv"
COUNTER = ROOT / "gdt186_counterexamples.tsv"
RESULT = ROOT / "gdt186_result.json"
METHOD = ROOT / "GDT186_FOXTON_HYBRID_CIPHER_COMPARATOR_METHOD.md"
REPORT = ROOT / "GDT186_FOXTON_HYBRID_CIPHER_COMPARATOR_REPORT.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path, rows):
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields,
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    sources = [
        dict(source_id="FOXTON_ARTICLE", authority="SCHOLARLY_ARTICLE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="John Block Friedman, The Cipher Alphabet of John de Foxton's Liber Cosmographiae, Scriptorium 36.2 (1982), 219-235", url="https://www.persee.fr/doc/scrip_0036-9772_1982_num_36_2_1268", cited_pages="219-235", retrieved_utc="2026-08-17", retrieved_payload_sha256="ab97426a30acea859ef762e865a07e68cbaed570ab6904bcc91ddb7321aecf1c", use="PRIMARY_MECHANISM_SOURCE"),
        dict(source_id="FOXTON_P220", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0220_0000", cited_pages="220", retrieved_utc="2026-08-17", retrieved_payload_sha256="9850ede37e71b74af7fe0cfa867c5ccc1eb6b8246d5786b05d9eb1f5405e4dd2", use="DIAGRAM_KEY_AND_SELECTIVE_CIPHER"),
        dict(source_id="FOXTON_P227", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="comparative scientific ciphers", date="13th-15th centuries", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0227_0000", cited_pages="227", retrieved_utc="2026-08-17", retrieved_payload_sha256="424c81d0f2bc79ccd22cc7e8118f483895146d514f50e7c3a3544ddcb44def54", use="FONTANA_FULL_TEXT_COMPARATOR"),
        dict(source_id="FOXTON_P228", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="Giovanni Fontana comparator", date="15th century", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0228_0000", cited_pages="228", retrieved_utc="2026-08-17", retrieved_payload_sha256="412cd65b63bdb77328758a0fee0a181daa51e71831a0ecc49b8425622ca52ea6", use="FULL_TEXT_AND_ABBREVIATION_COMPARATOR"),
        dict(source_id="FOXTON_P231", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0231_0000", cited_pages="231", retrieved_utc="2026-08-17", retrieved_payload_sha256="dd4e3b0744cffeb2e6840b58eeefcbf187ea44b7b0eb9997cdd816af95203247", use="SCRIBES_AND_CIPHER_KEY"),
        dict(source_id="FOXTON_P232", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0232_0000", cited_pages="232", retrieved_utc="2026-08-17", retrieved_payload_sha256="f4f1b8d4c6e70df297a7a1f87f5d93b51bdfefbd6dfde8d3e9b1d0f3e413d347", use="ABBREVIATION_AND_CIPHERED_WORD_COUNTS"),
        dict(source_id="FOXTON_P233", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0233_0000", cited_pages="233", retrieved_utc="2026-08-17", retrieved_payload_sha256="c821334759329677ed2a4de3ca2535006c70ad8f2117fca2380fe7f14923e71f", use="OMITTED_HEADWORD_AND_PARTIAL_CIPHER"),
        dict(source_id="FOXTON_P234", authority="SCHOLARLY_ARTICLE_PAGE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="Friedman 1982", url="https://www.persee.fr/doc/page/scrip_0036-9772_1982_num_36_2_1268/scrip_0036-9772_1982_num_36_2_T1_0234_0000", cited_pages="234", retrieved_utc="2026-08-17", retrieved_payload_sha256="c882c3238c592edb2fce169afe03d7a25942a624d29248fc0fd12c90003368b5", use="CIPHERED_RUBRICS"),
        dict(source_id="TRINITY_CATALOGUE", authority="OFFICIAL_MANUSCRIPT_CATALOGUE", manuscript="Trinity Cambridge R.15.21", date="1408", bibliographic_reference="The James Catalogue of Western Manuscripts, R.15.21", url="https://mss-cat.trin.cam.ac.uk/Manuscript/R.15.21", cited_pages="catalogue record", retrieved_utc="2026-08-17", retrieved_payload_sha256="981278dcb8a1ad1b44767350c2ddcc1f3db39311cc40f7b402231f321a858fcf", use="DATE_LANGUAGE_CONTENT_PROVENANCE"),
        dict(source_id="BYRHTFERTH_OGHAM", authority="SCHOLARLY_PROJECT_ACCOUNT", manuscript="Oxford St John's College MS 17 f7v", date="early 12th century", bibliographic_reference="Deborah Hayden, Byrhtferth's Ogam Signature, OG(H)AM project (2023)", url="https://ogham.glasgow.ac.uk/index.php/2023/01/18/byrhtferths-ogam-signature-and-oxford-st-johns-college-ms-17/", cited_pages="web article", retrieved_utc="2026-08-17", retrieved_payload_sha256="6518e029f4afe9f525c7f8628a21b26b8dd0f20b845e600fa63a44436c8bfd95", use="COMPUTUS_DIAGRAM_CRYPTIC_WRITING_COMPARATOR"),
    ]
    facts = [
        dict(fact_id="F01", source_id="TRINITY_CATALOGUE", statement="R.15.21 is a Latin cosmographical compendium completed in 1408.", evidence_scope="OFFICIAL_CATALOGUE", support="SUPPORTED"),
        dict(fact_id="F02", source_id="TRINITY_CATALOGUE", statement="Its documented contents combine calendars, lunar and planetary tables, zodiac, temperaments, bleeding, medicine, prognostication, and diagrams.", evidence_scope="OFFICIAL_CATALOGUE", support="SUPPORTED"),
        dict(fact_id="F03", source_id="FOXTON_P220", statement="An artificial substitution alphabet selectively conceals physiognomic body-part terms that key groups of chapters.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F04", source_id="FOXTON_P232", statement="Friedman counts 135 ciphered words; 12 concern sexual, gynecological, or obstetrical matter.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F05", source_id="FOXTON_P233", statement="About 55 ciphered words occur in physiognomy and palmistry chapters and 39 identify veins in practical diagrams.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F06", source_id="FOXTON_P233", statement="A body-part headword can be supplied by a diagram/list and omitted from the descriptive paragraphs that depend on it.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F07", source_id="FOXTON_P233", statement="Foxton sometimes ciphers only the first syllable of a recurrent headword while leaving the remainder in ordinary Latin and respecting case.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F08", source_id="FOXTON_P232", statement="Standard Latin abbreviation conventions are used inside the artificial cipher.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F09", source_id="FOXTON_P234", statement="Astrological fortunes use ciphered recurrent rubrics so otherwise readable remedies are difficult to interpret.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F10", source_id="FOXTON_P231", statement="Cipher occurs in the long second-hand portion, not in the first professional hand's calendar and prologue.", evidence_scope="SCHOLARLY_ARTICLE", support="SUPPORTED"),
        dict(fact_id="F11", source_id="FOXTON_P227", statement="Fontana's fifteenth-century technical work is almost wholly written in an artificial alphabet, with limited cleartext framing.", evidence_scope="SCHOLARLY_ARTICLE_COMPARATOR", support="SUPPORTED"),
        dict(fact_id="F12", source_id="FOXTON_P228", statement="Fontana's artificial alphabet uses systematic graphic families and deliberately displaced abbreviation marks.", evidence_scope="SCHOLARLY_ARTICLE_COMPARATOR", support="SUPPORTED"),
        dict(fact_id="F13", source_id="BYRHTFERTH_OGHAM", statement="A computus diagram joins calendrical and cosmological systems with uncertain Ogham-like cryptic writing; a substitution reading has been proposed but is disputed.", evidence_scope="SCHOLARLY_PROJECT_COMPARATOR", support="SUPPORTED_WITH_INTERPRETIVE_DISPUTE"),
    ]
    comparison = [
        dict(axis="DATE_AND_DOCUMENT_ECOLOGY", foxton="1408 technical medical astrological compendium", voynich="early fifteenth-century illustrated technical/astrological/medical ecology is the leading source prior", fit="MATCH", consequence="strong historical-practice prior, no source identity"),
        dict(axis="WHOLE_DOCUMENT_OPACITY", foxton="mostly readable Latin with 135 selectively ciphered words", voynich="no readable substrate or plaintext clause recovered", fit="CONTRADICTION", consequence="selective Foxton substitution cannot be the whole mechanism"),
        dict(axis="FULL_TEXT_ARTIFICIAL_ALPHABET", foxton="not Foxton; contemporary Fontana supplies this comparator", voynich="nearly all visible text is opaque", fit="PARTIAL", consequence="full scientific cipher is historically plausible but remains undecoded"),
        dict(axis="SIMPLE_SUBSTITUTION", foxton="artificial substitution alphabet is decipherable with a key", voynich="historical-language injective/homophonic/simple decoder families lose to nonsemantic controls", fit="CONTRADICTION", consequence="do not search Foxton glyph values as a Voynich key"),
        dict(axis="OPERATIVE_OR_RUBRIC_WORD_SELECTION", foxton="operative headwords and rubrics preferentially concealed", voynich="PAGE_HOST remains the leading opaque address/content layer but has zero confirmed glosses", fit="PARTIAL", consequence="supports a keyed-address hypothesis, not a word reading"),
        dict(axis="DIAGRAM_KEYED_HEADWORD", foxton="diagram/list supplies body-part key for dependent chapter material", voynich="diagram labels and prose coexist but ownership and exact semantic transfer mostly fail", fit="PARTIAL", consequence="test label inventories as keys for distributed/omitted page content"),
        dict(axis="HEADWORD_OMISSION", foxton="dependent prose can omit the keyed noun entirely", voynich="exact label-to-prose recurrence is weak and broad label-host semantics fail", fit="PARTIAL", consequence="absence of verbatim recurrence is not by itself a falsifier"),
        dict(axis="PARTIAL_WORD_CIPHER", foxton="ciphered first syllable plus clear Latin remainder", voynich="free/bound reuse and wrapper/host/right decomposition are formal but not linguistic", fit="PARTIAL", consequence="historical analogue for layered rendering, not proof of morphemes"),
        dict(axis="ABBREVIATION_INSIDE_CIPHER", foxton="ordinary Latin abbreviation operates in cipher strings", voynich="abbreviation-only controls explain part but not all of the architecture", fit="PARTIAL", consequence="cipher and abbreviation need not be exclusive"),
        dict(axis="LINE_RESET_AND_RECORD_COMPILER", foxton="no reported Voynich-like line-reset field compiler", voynich="physical line reset, field chaining, wrappers, right families and B3 closure are reproducible", fit="CONTRADICTION", consequence="an added record compiler is required"),
        dict(axis="HAND_OR_REGISTER_RESTRICTION", foxton="cipher concentrated in the second hand's portion", voynich="shared system spans hands/registers with strong distributional shifts", fit="PARTIAL", consequence="hand can select rendering regime but not explain the common system"),
        dict(axis="REPEATED_TECHNICAL_KEYS", foxton="repeated operative terms such as orificium and manu are re-enciphered", voynich="high PAGE_HOST recurrence coexists with unstable neighbors", fit="PARTIAL", consequence="recurrent opaque addresses remain compatible with technical keys"),
        dict(axis="RECOVERABLE_LANGUAGE", foxton="cipher resolves to Latin words and inflection", voynich="no language, phonology, lexicon or plaintext survives held controls", fit="CONTRADICTION", consequence="analogy stops before translation"),
    ]
    predictions = [
        dict(prediction_id="P01", mechanism="DIAGRAM_KEYED_HEADWORD", frozen_prediction="On nonsealed labelled pages, the page label PAGE_HOST inventory improves prediction of paragraph-opening or field-template distributions beyond page/register and label-count nuisance, even when exact label hosts do not recur.", falsifier="No gain over same-page label-host permutations and page/register baselines.", status="FROZEN_NOT_RUN"),
        dict(prediction_id="P02", mechanism="HEADWORD_OMISSION", frozen_prediction="Exact label PAGE_HOST recurrence in dependent prose is no stronger than matched same-page host recurrence, while a broader host-family or compiler-profile relation can remain positive.", falsifier="Only exact string recurrence carries the effect, consistent with ordinary local vocabulary reuse.", status="FROZEN_NOT_RUN"),
        dict(prediction_id="P03", mechanism="PARTIAL_WORD_CIPHER", frozen_prediction="If a stable cleartext-like residue exists, one edge layer should transfer across labels and prose more consistently than the opaque host identity after controlling register and hand.", falsifier="Every edge effect is host/register specific or loses to string controls.", status="FROZEN_NOT_RUN"),
        dict(prediction_id="P04", mechanism="DIRECT_FOXTON_SUBSTITUTION", frozen_prediction="A direct letter substitution should support a stable historical-language decoding without a separate line-reset compiler.", falsifier="Existing global decoder losses plus compiler residual persist.", status="ALREADY_FALSIFIED_FOR_TESTED_FAMILIES"),
    ]
    counter = [
        dict(counterexample_id="C01", observation="Foxton leaves most Latin readable; Voynich does not.", impact="rejects direct selective-cipher identity"),
        dict(counterexample_id="C02", observation="Foxton has a recoverable letter key; no stable Voynich letter or phoneme map exists.", impact="rejects alphabet transfer"),
        dict(counterexample_id="C03", observation="GDT001 historical-language substitution, homophonic, abbreviation and word-code candidates remain behind the best nonsemantic source model.", impact="rejects simple language-plus-key explanation in tested families"),
        dict(counterexample_id="C04", observation="Voynich line reset, DY chaining and B3 closure require structure not reported for Foxton's substitution.", impact="requires an additional compiler"),
        dict(counterexample_id="C05", observation="Archived label-to-visual PAGE_HOST associations do not survive global correction.", impact="no diagram label is promoted to a headword meaning"),
        dict(counterexample_id="C06", observation="Fontana proves full-text artificial cipher plausibility but not Voynich identity or readability.", impact="historical possibility is not decoder evidence"),
        dict(counterexample_id="C07", observation="Byrhtferth pseudo-Ogham interpretation is disputed.", impact="use only as diagrammatic cryptic-writing context"),
    ]
    write_tsv(MANIFEST, sources)
    write_tsv(FACTS, facts)
    write_tsv(COMPARE, comparison)
    write_tsv(PREDICTIONS, predictions)
    write_tsv(COUNTER, counter)
    result = {
        "experiment": "GDT186_FOXTON_HYBRID_CIPHER_COMPARATOR",
        "status": "FOXTON_SIMPLE_SUBSTITUTION_INSUFFICIENT_HYBRID_RUBRIC_POINTER_ROUTE_OPEN",
        "counts": {
            "sources": len(sources), "frozen_facts": len(facts),
            "architecture_axes": len(comparison), "matches": sum(x["fit"] == "MATCH" for x in comparison),
            "partials": sum(x["fit"] == "PARTIAL" for x in comparison),
            "contradictions": sum(x["fit"] == "CONTRADICTION" for x in comparison),
            "predictions": len(predictions), "counterexamples": len(counter),
        },
        "direct_foxton_selective_substitution": "INSUFFICIENT",
        "historical_hybrid_rubric_codebook_mechanism": "ATTESTED_ROUTE_OPEN_NOT_VOYNICH_CONFIRMED",
        "next_route": "SOURCE_NATIVE_LABEL_INVENTORY_TO_PARAGRAPH_FIELD_KEYED_OMISSION_TEST",
        "f84r_accessed": False,
        "claim_ceiling": "Historical mechanism comparison only; no Voynich sign value, language, alphabet, word, rubric, plaintext, or translation.",
        "outputs": {p.name: sha(p) for p in (MANIFEST, FACTS, COMPARE, PREDICTIONS, COUNTER)},
        "documents": {p.name: sha(p) for p in (METHOD, REPORT)},
        "implementation": sha(Path(__file__)),
    }
    RESULT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(result["status"], result["counts"])


if __name__ == "__main__":
    main()
