# GDT339 comparator-first incidence report

Status: **NO_TRANSFERABLE_COMPARATOR_INVARIANT**.

The comparator stage used 22,394 CoReMA semantic units from six held collections and 421,720 Nuremberg section-labelled token occurrences from four held books. All lexical forms were replaced by opaque IDs before feature construction; no position, word shape, language feature, or local sequence entered a model.

The selected transferable feature family is **TOPOLOGY_ONLY**. It gains +76.944 class-balanced held bits over uniform (+75.359 after the fixed three-model selector), is positive in 3/10 held collections/books, and has fixed-prediction max-three diagnostic p=0.000488. Task gains over the frequency-degree model are +9090.173 bits for CoReMA and -2618.617 bits for Nuremberg. Exact opaque-ID lookup is reported as a namespace-specific ceiling and was ineligible for selection.

The selected CoReMA coefficients and anonymous class order `C0..C4` are frozen in `artifacts/gdt339_invariant_freeze.json` before any Voynich outcome is scored. Comparator semantic names remain audit metadata and may not be exported as Voynich meanings.

## Claim ceiling

Comparator-calibrated opaque incidence only. No Voynich tuple, role, word, meaning, language, plaintext, translation, or f84 result follows from this stage.
