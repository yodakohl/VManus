#!/usr/bin/env python3
"""Reconcile GDT181 predictions with the published GDT182--GDT201 evidence."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
METHOD = R / "GDT202_HYBRID_THEORY_RECONCILIATION_METHOD.md"
REPORT = R / "GDT202_HYBRID_THEORY_RECONCILIATION_REPORT.md"
PRED_IN = R / "gdt181_predictions.tsv"
LEX_IN = R / "gdt181_provisional_translation_lexicon.tsv"
RESULT_IN = R / "gdt181_result.json"
PRED_OUT = R / "gdt202_prediction_reconciliation.tsv"
LEX_OUT = R / "gdt202_lexicon_disposition.tsv"
MODEL_OUT = R / "gdt202_model_disposition.tsv"
COUNTER_OUT = R / "gdt202_counterexamples.tsv"
RESULT = R / "gdt202_result.json"

EVIDENCE_FILES = [
    "gdt182_result.json", "gdt184_result.json", "gdt185_result.json",
    "gdt187_result.json", "gdt188_result.json", "gdt189_result.json",
    "gdt190_result.json", "gdt191_result.json", "gdt192_result.json",
    "gdt193_result.json", "gdt194_result.json", "gdt195_result.json",
    "gdt196_result.json", "gdt197_result.json", "gdt198_result.json",
    "gdt199_result.json", "gdt200_result.json", "gdt201_result.json",
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True,
                         separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def read_tsv(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RECON = {
    "P1": ("UNTESTED_NO_NEW_SCHEMA", "gdt182_result.json;gdt184_result.json",
           "The exposed f57 decoder is nonunique and its fourfold ring lacks four-state capacity; no fresh source-owned four-quality register was acquired.",
           "NONE", "Local four-state diagram code not licensed."),
    "P2": ("UNTESTED_NO_COMPARABLE_PROCESS", "gdt195_result.json;gdt201_result.json",
           "No readable six-state/five-boundary homolog was found; the comparable f83 panel rejects the later zone-renderer transfer but is not a source-owned segmented process.",
           "NONE", "State-change emission remains an unexplained f77-local alignment."),
    "P3": ("NO_HOMOLOG_FOUND", "gdt195_result.json",
           "Six authority-bound comparators support broad alchemical practice but zero has the exact six-state/four-output/one-hold topology.",
           "NONE", "Broad medical-alchemical document prior only."),
    "P4": ("ANTECEDENT_UNDERCUT_NO_HOMOLOG", "gdt184_result.json;gdt185_result.json",
           "R2 has only one stable binary column and does not index the matched 17-sector f67v1 inventory; no readable homolog resolves its confounds.",
           "NONE", "Fourfold reference/ornament remains possible; element table withdrawn."),
    "P5": ("CONTROL_SUPPORTED_TARGET_BRIDGE_FAILED", "gdt187_result.json;gdt188_result.json",
           "Readable historical controls support layered abbreviation/cipher practice, but the fixed label-key bridge is null and direct bijective cipher architecture is insufficient.",
           "NONE", "Historical plausibility retained without a Voynich content key."),
    "P6": ("NO_NEW_REFERENT_EXISTING_BRIDGES_NEGATIVE", "gdt187_result.json;gdt196_result.json;gdt199_result.json",
           "No new independently repeated singular referent was acquired; label/prose, f77 label/prose, and payload-matched label transfers do not recover a dictionary.",
           "NONE", "PAGE_HOST remains an opaque candidate, not a content address."),
    "P7": ("NEGATIVE_PREDICTION_SUPPORTED", "gdt188_result.json;gdt189_result.json;gdt190_result.json;gdt191_result.json;gdt192_result.json;gdt193_result.json;gdt194_result.json",
           "Injective letters, frequent-word nomenclators, context-keyed dictionaries, one/two-letter expansions, consonantal maps, and consonantal homophony all lose to matched source models.",
           "NONE", "A layered/nonliteral architecture is supported negatively; no plaintext is recovered."),
}


def main():
    predictions = read_tsv(PRED_IN)
    lexicon = read_tsv(LEX_IN)
    assert [row["id"] for row in predictions] == [f"P{i}" for i in range(1, 8)]
    evidence = {name: json.loads((R / name).read_text()) for name in EVIDENCE_FILES}
    assert all(evidence[name].get("status") for name in EVIDENCE_FILES)

    pred_rows = []
    for row in predictions:
        status, files, finding, semantic, architecture = RECON[row["id"]]
        pred_rows.append({
            "id": row["id"],
            "scope": row["scope"],
            "original_prediction": row["prediction"],
            "original_failure": row["failure"],
            "reconciliation_status": status,
            "downstream_evidence": files,
            "finding": finding,
            "translation_bearing_success": "0",
            "semantic_value_recovered": semantic,
            "architectural_disposition": architecture,
        })
    write_tsv(PRED_OUT, pred_rows, list(pred_rows[0]))

    formal = {"PAGE_HOST", "WRAPPER", "RIGHT_FAMILY", "DY_CLASS", "B3_CLASS", "Q_OUTER"}
    lex_rows = []
    for row in lexicon:
        retained = row["entry"] in formal
        lex_rows.append({
            "entry": row["entry"],
            "original_scope": row["scope"],
            "original_provisional_role": row["provisional_role"],
            "original_english_gloss": row["english_gloss"],
            "disposition": "FORMAL_ONLY_RETAINED" if retained else "SEMANTIC_GLOSS_WITHDRAWN",
            "active_role": row["provisional_role"] if retained else "UNASSIGNED",
            "active_english_gloss": "UNASSIGNED",
            "reason": "Reproducible anonymous compiler coordinate; no semantic value." if retained else "Page-local semantic selection is nonunique and has no successful fixed transfer or readable homolog.",
        })
    write_tsv(LEX_OUT, lex_rows, list(lex_rows[0]))

    model_rows = [
        {"component": "PHYSICAL_LINE_RESET_AND_FIELD_CHAINING", "disposition": "RETAINED_STRUCTURAL", "basis": "Reproducible manuscript-wide architecture; not a sentence or record translation."},
        {"component": "WRAPPER_RIGHT_DY_B3_COMPILER", "disposition": "RETAINED_STRUCTURAL", "basis": "Formal position/register machinery remains reproducible and unglossed."},
        {"component": "PAGE_HOST_CONTENT_ADDRESS", "disposition": "OPAQUE_CANDIDATE_ONLY", "basis": "Internal identity survives, but every completed external content bridge is negative or nonidentifying."},
        {"component": "F57_TWO_BIT_QUALITY_DECODER", "disposition": "WITHDRAWN_FROM_ACTIVE_SEMANTICS", "basis": "Feature multiplicity, insufficient R2 state capacity, and absent homolog prevent selection."},
        {"component": "F77_QUALITY_STATE_PROCESS", "disposition": "WITHDRAWN_FROM_ACTIVE_SEMANTICS", "basis": "It inherits the exposed f57 assignment; exact homolog, prose bridge, renderer transfer, and comparable-panel transfer do not succeed."},
        {"component": "ONE_LAYER_LANGUAGE_OR_FIXED_CODEBOOK", "disposition": "BOUNDED_VARIANTS_FALSIFIED", "basis": "GDT188--GDT194 lose to matched source controls or lack stable keys."},
        {"component": "PAGE_CONDITIONED_HYBRID_TECHNICAL_COMPILER", "disposition": "LEADING_ABDUCTIVE_ARCHITECTURE_ONLY", "basis": "It still compresses the structural evidence qualitatively, but it has no executable semantic decoder."},
    ]
    write_tsv(MODEL_OUT, model_rows, list(model_rows[0]))

    counters = [
        {"id": "C01", "finding": "GDT182 finds multiple shallow f57 decoders after feature search.", "effect": "The perfect 8/8 local fit does not select a quality code."},
        {"id": "C02", "finding": "GDT184 finds only one stable binary R2 column where four identities require two bits.", "effect": "The proposed four-element table lacks capacity."},
        {"id": "C03", "finding": "GDT195 finds no exact readable f77 homolog and shows four-element coverage is algebraically dependent.", "effect": "Element names do not independently validate the process."},
        {"id": "C04", "finding": "GDT197 does not select starts-ot as terminal-y's global partner.", "effect": "The exposed quality axis is not globally privileged."},
        {"id": "C05", "finding": "GDT198's two f77 payload echoes have assignment-null p=.238095.", "effect": "Local reuse is not a semantic bridge."},
        {"id": "C06", "finding": "GDT199 gets 1/4 on archived payload-matched labels.", "effect": "The renderer rule does not transfer by visual proxy class."},
        {"id": "C07", "finding": "GDT200's perfect d/ot split is explained by exposed f77 panel zone.", "effect": "The local form contrast is confounded."},
        {"id": "C08", "finding": "GDT201 gets 0/4 on the comparable fixed f83 upper/lower panel.", "effect": "Even the panel-zone renderer does not generalize."},
        {"id": "C09", "finding": "Compiler-stripped fixed language/codebook families all lose matched source controls.", "effect": "No bounded one-layer plaintext decoder survives."},
    ]
    write_tsv(COUNTER_OUT, counters, list(counters[0]))

    status = "HYBRID_COMPILER_ARCHITECTURE_RETAINED_F57_F77_SEMANTIC_DECODER_WITHDRAWN"
    report = f'''# GDT202 — the compiler survives; the local semantic decoder does not

Status: **{status}**.

## Outcome

The cumulative GDT182--GDT201 evidence no longer licenses GDT181's executable
f57/f77 quality/process reading.  The local decoder was exposed and nonunique,
its supposed fourfold reference ring has only one stable bit, no exact readable
f77 homolog was found, its `ot` axis is not globally selected, and its renderer
rules fail both the archived payload-matched inventory (1/4) and the comparable
f83 panel (0/4).

All **7/7** frozen predictions were reconciled.  Exactly **0/7** recovered a
semantic value or plaintext.  P7 is a successful *negative* architectural
prediction: bounded one-layer alphabetic, nomenclator, expansion,
consonantal, and homophonic mappings fail.  That supports a layered/nonliteral
surface architecture, but translates no sign or group.

## Revised leading theory

The best surviving generator is an **anonymous page-conditioned technical
compiler**:

```text
PAGE   := PAGE_PROFILE OPAQUE_INVENTORY PHYSICAL_LINE+
LINE   := ENTRY_STATE? FIELD (DY_CLASS FIELD)* B3_CLASS?
FIELD  := WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?
```

`PAGE_HOST` remains the likeliest place for content/address information, but
not a dictionary entry.  The compiler coordinates remain reproducible formal
structure.  The local f57 quality states, f77 process states, and element-like
transition names are now historical hypotheses only and are removed from the
active lexicon.

| active translation coverage | count |
|---|---:|
| confirmed source words | 0 |
| plaintext clauses | 0 |
| licensed semantic state assignments | 0 |
| retained formal-only lexicon entries | {sum(r['disposition']=='FORMAL_ONLY_RETAINED' for r in lex_rows)} |
| withdrawn semantic entries | {sum(r['disposition']=='SEMANTIC_GLOSS_WITHDRAWN' for r in lex_rows)} |

## What a real next step must add

More internal string regularity cannot choose among opaque compiler values.
A translation-bearing successor needs information not generated by the same
surface system: a readable homolog with the same ordered legend/topology, a
source-bound repeated referent with singular ownership and held-folio
replication, a bilingual/keyed legend, or genuinely new physical evidence that
changes the transcription channel.  Until then, local English glosses would be
manufactured rather than decoded.

This checkpoint does not prove that Voynichese lacks language or meaning.  It
withdraws only the active f57/f77 semantic decoder and retains the anonymous
compiler architecture as the best abductive account.  No transcription table,
image, or f84r material was read.
'''
    REPORT.write_text(report, encoding="utf8")

    result = {
        "schema": "GDT202_HYBRID_THEORY_RECONCILIATION_RESULT_V1",
        "status": status,
        "counts": {
            "predictions_reconciled": 7,
            "translation_bearing_prediction_successes": 0,
            "negative_architectural_predictions_supported": 1,
            "formal_entries_retained": sum(r["disposition"] == "FORMAL_ONLY_RETAINED" for r in lex_rows),
            "semantic_entries_withdrawn": sum(r["disposition"] == "SEMANTIC_GLOSS_WITHDRAWN" for r in lex_rows),
            "confirmed_source_words": 0,
            "confirmed_plaintext_clauses": 0,
            "licensed_semantic_state_assignments": 0,
        },
        "leading_theory": "ANONYMOUS_PAGE_CONDITIONED_TECHNICAL_COMPILER",
        "withdrawn": ["F57_TWO_BIT_QUALITY_DECODER", "F77_QUALITY_STATE_PROCESS", "LOCAL_OT_OK_Y_SEMANTIC_COORDINATES"],
        "retained": ["PHYSICAL_LINE_RESET", "FIELD_CHAINING", "FORMAL_WRAPPER_RIGHT_DY_B3", "OPAQUE_PAGE_HOST_CANDIDATE"],
        "interpretation": "The structural compiler remains the leading abductive architecture, but no executable semantic decoder remains active.",
        "claim_ceiling": "Anonymous formal architecture only; no source word, quality, element, process state, operation, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {p.name: sha(p) for p in [PRED_IN, LEX_IN, RESULT_IN] + [R / n for n in EVIDENCE_FILES]},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {p.name: sha(p) for p in [PRED_OUT, LEX_OUT, MODEL_OUT, COUNTER_OUT]},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
