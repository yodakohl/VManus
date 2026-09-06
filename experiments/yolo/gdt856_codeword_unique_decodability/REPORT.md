# GDT856 — the published98-unit code is not freely uniquely decodable

**Exact collision witness: `CE` = [`C`, `E`] = [`CE`].**

All three case-sensitive codewords C, E and CE belong to the frozen published
GDT605 final-unit inventory. The two different codeword sequences concatenate
to the identical collapsed-symbol string CE. The inventory has98distinct,
nonempty entries and passes the registered input-validity check.

This finite witness settles the registered free-code question: the98-unit
vocabulary alone does not uniquely segment unrestricted concatenations.
Additional constraints, such as the fixed ordered BPE merge procedure or
context, are needed to select one representation. The deterministic BPE
procedure itself is not contradicted.

## Exact scope of the result

The witness is a property of the published aggregate code, not a newly read
manuscript passage. CE need not occur as a manuscript sequence, and neither
witness segmentation is claimed to be reachable as a canonical BPE output.
Collapse preprocessing and source grammar can impose additional legality
constraints. No inference of ambiguous authorial writing follows.

Symbols are exact case-sensitive collapsed strings; no EVA expansion was
performed. GDT605's original180selector scope differs from the current179
text scope. This test does not enlarge current access or assert a current-
corpus frequency, natural alphabet, physical glyph identity, language or
meaning. No synchronization, decoder, BPE refit or language model was run.

The breadth-first search stopped at its first collision. RESULT.json retains
the witness and partial explored graph, explicitly marked incomplete. It is
not a full exhaustion certificate or a claim that this is the shortest
possible collision string; a full graph is necessary only for a UD conclusion.

## Reproduction and decision

Public preregistration83c43c7f preceded unit-value loading. The source hash
matched the registered published inventory. Only its unit column was used;
frequency columns were not analyzed. No manuscript sequence or image input.

The independent residual-set closure also found non-UD, then verified that
both different witness sequences consist of inventory codewords and have
exactly equal concatenations. All six preregistered synthetic controls passed
in both implementations. Cached replay was byte-identical; binding passed.
Execution and validation completed in well under one second. No additional
search was needed after the decisive witness.

The proposed free unique-segmentation premise is closed for this exact
inventory. This is a useful model-property correction, not decipherment
progress or a reason to refit the closed alphabet model.
