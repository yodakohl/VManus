#!/usr/bin/env python3
"""GDT113: synthesize HPR2 evidence into a page-conditioned record-code model."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METHOD = ROOT / "GDT113_PAGE_CONDITIONED_RECORD_CODE_METHOD.md"
REPORT = ROOT / "GDT113_PAGE_CONDITIONED_RECORD_CODE_REPORT.md"
MATRIX = ROOT / "gdt113_hpr2_hypothesis_matrix.tsv"
MODEL = ROOT / "gdt113_page_conditioned_record_code_model.json"
RESULT = ROOT / "gdt113_result.json"
BOUND = ("gdt003_results.json",) + tuple(f"gdt{number:03d}_result.json" for number in (20, 37, 51, 55, 62, 73, 83, 85, 86, 87, 91, 94, 95, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    for name in BOUND: assert (ROOT / name).exists()
    matrix = [
        {"hypothesis": "H1_PAGE_HOST_EXTERNAL_CONTENT", "status": "WEAKENED_NO_TRANSFER", "support": "GDT103 exposed panel +27.462 bits; GDT110 PAGE_HOST +2.864 bits on three contact folios", "counterevidence": "GDT109 -31.726 bits; GDT112 cross-frame exact-host -138.337; GDT073 cross-section behavior -61.992", "model_action": "RENAME_PAGE_HOST_TO_CODEWORD_BODY", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H2_O_OT_PRESERVES_HOST_CONTENT", "status": "NOT_SUPPORTED_BROAD_TAGS", "support": "O/OT placement effects transfer source-only", "counterevidence": "GDT112 CROSS_FRAME loses 138.337 bits on 88 of 92 folios", "model_action": "RETAIN_AS_PLACEMENT_FRAME_ONLY", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H3_STRIPPING_COMPILER_EXPOSES_CONTENT", "status": "FAILED_FOR_HOST_EDGE", "support": "Compiler-only external models generally weak", "counterevidence": "GDT106 stripping one final host character costs 67.675 bits versus full host", "model_action": "COUPLE_BODY_AND_EDGE_STATE", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H4_DY_PRE_POST_TRANSITION", "status": "FAILED_TESTED_TRANSITION_ALGEBRA", "support": "GDT020 coarse post-DY phase and GDT103 relation increments", "counterevidence": "GDT111 next host -1634.368; full transition 79.406 bits worse than previous host alone", "model_action": "DY_LICENSED_BY_PREVIOUS_EDGE", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H5_RIGHT_FAMILY_RENDERER", "status": "FORMALLY_SUPPORTED", "support": "GDT062 held register conditioning; GDT105 universal final-edge prediction", "counterevidence": "External relation increments are axis-specific and CONTACT/GAP does not transfer", "model_action": "RETAIN_REGISTER_HOST_CONDITIONED_RENDERER", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H6_WRAPPER_PRESERVES_CONTENT", "status": "WEAK_LOCAL_ONLY", "support": "GDT110 wrapper contact contrast +.433 in three mixed arrays", "counterevidence": "max-six p .235; GDT059 wrapper preservation mixed/negative on relation axes", "model_action": "RETAIN_ROUTER_NOT_CONTENT_PRESERVER", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H7_B3_CONTENT_NEUTRAL_CLOSE", "status": "SUPPORTED_NEGATIVE_CONTROL", "support": "GDT103 active-only increment -.338; GDT110 effect -.067", "counterevidence": "categorical absence encoding creates known artifact", "model_action": "RETAIN_OPTIONAL_CLOSE_STATE", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H8_BEHAVIOR_CLASSES_EXTERNAL_CONTENT", "status": "NOT_TRANSFERABLE", "support": "GDT069-071 postselected archived leads", "counterevidence": "GDT073 cross-section transfer -61.992 bits", "model_action": "RETAIN_FORMAL_CLASSES_ONLY", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H9_Q_D_BRANCH_ROUTERS", "status": "STRONGLY_FORMALLY_SUPPORTED", "support": "GDT086/GDT087/GDT091/GDT094: q-O early and d-Y late across tails, folios and registers", "counterevidence": "identical to strong first-character/string baseline", "model_action": "RETAIN_OUTER_ROUTER_COORDINATES", "semantic_role": "UNASSIGNED"},
        {"hypothesis": "H10_PAGE_LOCAL_CODEBOOK", "status": "STRONGLY_FORMALLY_SUPPORTED", "support": "GDT082/GDT083 page-local PAGE_HOST signal; page-conditioned root inventory", "counterevidence": "f86v5 concentration; external associations fail", "model_action": "MOVE_PUTATIVE_PAYLOAD_TO_PAGE_RECORD_LEVEL", "semantic_role": "UNASSIGNED"},
    ]
    write(MATRIX, matrix)

    theories = [
        {"theory": "COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE", "abductive_score_10": 4, "strength": "free/bound reuse and recurrent formal operations", "failure": "nested paradigms do not beat string baselines; stable token semantics do not transfer"},
        {"theory": "STABLE_TOKEN_TECHNICAL_NOTATION", "abductive_score_10": 5, "strength": "record fields, line reset, page codebooks, repeated labels", "failure": "exact host and behavior-class external associations fail transfer"},
        {"theory": "HYBRID_TOKEN_CONTENT_ADDRESS_PLUS_RENDERER", "abductive_score_10": 5, "strength": "PAGE_HOST internal page vocabulary and compiler decomposition", "failure": "GDT109/GDT112 external transfer failures and GDT106 inseparable edge"},
        {"theory": "PAGE_CONDITIONED_RECORD_CODE", "abductive_score_10": 9, "strength": "jointly explains page vocabulary, register effects, edge licensing, routers, record structure, GDT003/string ceiling and semantic instability", "failure": "does not yet identify what record-level states refer to or prove meaningful content"},
    ]
    model = {
        "schema": "GDT113_PAGE_CONDITIONED_RECORD_CODE_MODEL_V1",
        "leading_theory": "PAGE_CONDITIONED_RECORD_CODE",
        "theory_comparison": theories,
        "generative_grammar": [
            "PAGE := PAGE_PROFILE CODEBOOK RECORD+",
            "CODEBOOK := register_conditioned_set(CODEWORD_BODY)",
            "RECORD := ENTRY_ROUTER? FIELD (FIELD_LINK FIELD)* B3_CLOSE?",
            "FIELD := OUTER_ROUTER? POSITION_FRAME? COUPLED_CODEWORD RENDERER?",
            "OUTER_ROUTER := q_on_O_branch | d_on_Y_branch | conditional_other_wrapper",
            "POSITION_FRAME := O | OT | NONE",
            "COUPLED_CODEWORD := BODY_WITH_EDGE_STATE",
            "RENDERER := DY_if_licensed_by_edge | RIGHT_FAMILY_if_licensed_by_host_register | BARE",
            "B3_CLOSE := optional_terminal_M_state",
        ],
        "formal_components": [
            {"component": "PAGE_PROFILE", "provisional_function": "select register and local codebook distribution", "confidence": "STRONG_FORMAL"},
            {"component": "CODEWORD_BODY", "provisional_function": "page-local reusable formal identity; semantic level unresolved", "confidence": "STRONG_FORMAL_WEAK_EXTERNAL"},
            {"component": "EDGE_STATE", "provisional_function": "coupled state licensing DY/right/bare rendering", "confidence": "VERY_STRONG_FORMAL"},
            {"component": "q", "provisional_function": "early O-branch router", "confidence": "VERY_STRONG_FORMAL_STRING_EQUIVALENT"},
            {"component": "d", "provisional_function": "late Y-branch router", "confidence": "STRONG_FORMAL_STRING_EQUIVALENT"},
            {"component": "O_OT", "provisional_function": "position/frame coordinate without demonstrated content preservation", "confidence": "STRONG_PLACEMENT"},
            {"component": "DY", "provisional_function": "edge-licensed renderer/closure, not supported as pre-post transition", "confidence": "VERY_STRONG_FORMAL"},
            {"component": "RIGHT_FAMILY", "provisional_function": "host/register-conditioned rendering", "confidence": "STRONG_FORMAL"},
            {"component": "B3", "provisional_function": "optional close-state negative control", "confidence": "PROVISIONAL_FORMAL"},
        ],
        "representative_parses": [
            {"surface": "qopchedy", "formal_parse": "q + O(pch+e) + DY", "interpretation": "O-branch routed codeword with e edge licensing DY"},
            {"surface": "pchedar", "formal_parse": "pch+d + RIGHT(ar)", "interpretation": "d-edge codeword selecting right renderer"},
            {"surface": "pchey", "formal_parse": "pch+ey + BARE", "interpretation": "bare edge state"},
            {"surface": "ypcheddy", "formal_parse": "y+pch+ed + DY", "interpretation": "alternate body/edge realization selecting DY"},
            {"surface": "qotedy", "formal_parse": "q + OT(e) + DY", "interpretation": "router/frame/edge composition; not linguistic morphology"},
        ],
        "translation_strategy": [
            "stop assigning stable meanings to exact PAGE_HOSTs from archive annotations",
            "identify repeated whole-record templates with externally distinct page/diagram states",
            "treat codeword inventories as page-conditioned and compare record-level substitutions",
            "infer latent record fields before lexical units",
            "only propose glosses after record-level transfer across independent physical folios",
        ],
        "frozen_non_f84_predictions": [
            "previous CODEWORD edge will predict DY/right/bare more strongly than the following host",
            "q-O and d-Y branch licensing will transfer to new source registers but remain matched by local string features",
            "exact PAGE_HOST visual glosses will usually fail cross-folio transfer unless conditioned on a repeated record template",
            "record-template alignment will outperform isolated-host alignment on new external structure",
            "B3 will remain near-neutral for external content after active-only encoding",
        ],
        "semantic_assignments": [],
        "claim_ceiling": "Explicit formal encoding theory only; no semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False, "prediction_frozen": False},
    }
    MODEL.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(f"""# GDT113 — page-conditioned record-code synthesis

## Leading theory

**PAGE_CONDITIONED_RECORD_CODE**

The strongest current generative theory is no longer “stable content-bearing
PAGE_HOST plus detachable renderer.” It is a page/register-conditioned codebook
whose codeword body and final edge are jointly generated inside a record
compiler. Any recoverable content association is now predicted to live first
at the **record/template and page-codebook level**, not at isolated exact hosts.

This theory scores 9/10 abductively versus compressed natural language 4/10,
stable token notation 5/10, and the prior hybrid content-address model 5/10.
The score is explanatory judgment, not statistical evidence.

## Why it leads

- PAGE_HOST is excellent internal page-local vocabulary but fails broad
  external transfer in GDT109 and GDT112.
- Final host character predicts renderer state manuscript-wide and predicts DY
  closure by +4,658.949 held bits in GDT111.
- The following host is harmful for DY prediction; the full transition is
  79.406 bits worse than previous-host trigrams alone. DY is edge licensing,
  not a supported transition algebra.
- q-O early and d-Y late routing survives tails, folios and registers but is
  also a first-character string rule.
- GDT003's formal rectangles do not beat character/string statistics, exactly
  as a productive record-code generator predicts.
- External single-host glosses are unstable; B3 remains near-neutral and
  RIGHT_FAMILY remains register-conditioned rendering.

## Translation route

The next path is to align **whole repeated record templates** to independently
varying external structures, then infer which field substitutions track those
structures. Glossing PAGE_HOSTs first is now the wrong level. A successful
record-level alignment could later make codeword identities interpretable;
without that alignment, isolated host meanings will continue to overfit.

All ten hypothesis states, four compared theories, nine formal components,
five representative parses, and five new non-f84 predictions are exported.
No semantic assignments are made. f84r receives no prediction and remains
completely sealed: it was not opened, retained, queried, joined, scored, or
targeted.
""", encoding="utf-8")
    result = {"schema": "GDT113_PAGE_CONDITIONED_RECORD_CODE_RESULT_V1", "status": "PAGE_CONDITIONED_RECORD_CODE_IS_LEADING_GENERATIVE_THEORY",
              "leading_theory": model["leading_theory"], "theory_comparison": theories,
              "hypotheses": len(matrix), "formal_components": len(model["formal_components"]),
              "representative_parses": len(model["representative_parses"]), "frozen_predictions": len(model["frozen_non_f84_predictions"]),
              "semantic_assignments": 0, "interpretation": "YOLO abductive theory revision after external-transfer and DY-transition failures.",
              "claim_ceiling": model["claim_ceiling"], "f84r": model["f84r"],
              "inputs": {name: sha(ROOT / name) for name in BOUND},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {MATRIX.name: sha(MATRIX), MODEL.name: sha(MODEL)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "leader": result["leading_theory"], "hypotheses": len(matrix), "semantic_assignments": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
