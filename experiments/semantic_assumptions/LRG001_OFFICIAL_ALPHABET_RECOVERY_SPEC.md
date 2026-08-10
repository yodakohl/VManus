# LRG001 official-alphabet recovery

Status: `REGISTERED_SYNTHETIC_RECONCILIATION_BEFORE_RECOVERY`

The sealed production target stopped after joining rows but before feature
construction, scoring, or output. The cause is exact: LRG001 used the
contiguous string `ABCDEFGHIJKLMNOPQRSTUVWX`; the already published official
STA inventory is `ABCDEFGHJKLMNPQRSTUVWXYZ`. Both contain 24 positions, but
the former substitutes nonexistent `I/O` positions for official `Y/Z`.

The synthetic generator is defined on integer category indices 0..23. It
converts indices to names and immediately maps names back to the same indices.
Therefore replacing both maps by any 24-symbol bijection should leave every
synthetic feature matrix and score byte-identical. This must be demonstrated
on all 136 frozen v2 worlds and both assignment matrices before recovery.

If and only if exact invariance passes, one separately committed recovery
producer may:

1. use the already validated nonimporting integer-index implementation;
2. map real family surfaces with the official alphabet;
3. reconstruct the unchanged 2,767-row matrix and frozen target decision once;
4. emit no individual sequence, feature weight, or form ranking; and
5. label the result `RECOVERED_INDEPENDENT_SCORER`, never a successful
   production run.

A second implementation must then validate the recovered result using the
frozen production core with only its alphabet/index constants rebound to the
official inventory. No statistic, threshold, cell, row, feature, assignment,
or gate may change.

The claim ceiling remains a transferable label-associated structural profile
on pass. It does not establish an identifier, name, noun, object owner, part
of speech, language, word meaning, plaintext, or translation.
