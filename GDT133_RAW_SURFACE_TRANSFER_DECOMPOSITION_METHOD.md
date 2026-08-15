# GDT133 — raw-surface transfer decomposition

Status: `POST_HOC_DECOMPOSITION_OF_PUBLIC_GDT132_PANEL`

## Question

GDT132 rejected transfer of the final-field `PAGE_HOST` signal from Q20 to
other registers, while raw token trigrams retained a small score lead.  GDT133
asks which formal layer carries that raw-minus-host difference.  It does not
retest or rescue the failed GDT132 gate.

## Fixed panel and model

Reuse the corrected, public GDT132 panel: 31 paragraph-start to immediate-next
line pairs on 24 folios, selected through f84-free `gdt046_line_frames.tsv`
and `gdt016_group_state_inventory.tsv`.  Train only on the 170 ZL3b Q20
records.  Retain GDT132's reference features, count-bin target, ridge 1000,
standardization, and target-side permutation strata.

Fit these six inherited/factored representations without tuning:

1. `HOST_CHAR3`: stripped PAGE_HOST trigrams;
2. `RAW_CHAR3`: complete source-token trigrams;
3. `COMPILER12`: final-field wrapper/O-OT/right/DY/B3 proportions;
4. `EDGE29`: the inherited GDT114 PAGE_HOST final-character distribution,
   mean host length, and exact-host diversity;
5. `FACTORED`: PAGE_HOST trigrams + COMPILER12 + EDGE29;
6. `FACTORED_PLUS_RAW`: FACTORED + complete raw-token trigrams.

The decisive nested contrasts are COMPILER12 and EDGE29 versus the reference,
FACTORED versus HOST_CHAR3, and FACTORED_PLUS_RAW versus FACTORED.  Report
fixed descriptive wrapper/frame/renderer block allocations from COMPILER12,
but do not scan individual wrapper or right-family values.

The decomposition is explicitly post-hoc because the external targets and the
raw lead are already known.  Report gain versus the same reference, top-1 and
top-3 count-bin accuracy, positive folios, section contributions, local
permutation diagnostics, max-six diagnostics, and leave-one-section-out score
decompositions.  The null retains the
known GDT132 opportunity-matching limitation; exact host/raw-length matching
has no usable permutation capacity.

## Interpretation ceiling

A positive compiler or edge block may localize formal transfer texture.  It
cannot establish a heading, recipe, semantic role, word, morpheme, POS, sound,
language, plaintext, meaning, or translation.  Limited f84r audit exposure is
already disclosed by GDT132; GDT133 uses only final f84-free inputs and makes no
further f84r access.
