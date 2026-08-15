# GDT100 — revised HPR2 generative theory

## Leading theory

**HYBRID CONTENT ADDRESS + ABBREVIATION + RECORD COMPILER**

The best current generator is still hybrid, but GDT092's claim that PAGE_HOST
directly supplies a content lexicon was too strong. The safer and more useful
model is:

```text
PAGE  := PAGE_PROFILE + CONTENT_ADDRESS_INVENTORY + LINE+
LINE  := ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?
FIELD := OUTER_WRAPPER? O_OT_FRAME? CONTENT_ADDRESS RIGHT_FAMILY?

CONTENT_ADDRESS := opaque PAGE_HOST
                 | O/Y branch + tail
                 | reusable subhost motif + residual

q -> O branch, early          d -> Y branch, late
RIGHT_FAMILY -> register-conditioned rendering
```

The compiler half is the strongest part. q/O and d/Y transfer to unseen tails
and folios, RIGHT_FAMILY transfers by register, and line/reset/field structure
is pervasive. Those operations still do not beat string statistics as a
linguistic morphology model.

The content-address half is plausible but ungrounded. PAGE_HOSTs have page-local
inventory signal. The narrow GDT089 and GDT096 external leads favor PAGE_HOST
over compiler features in limited panels, but GDT095's exhaustive descriptor
channel does not pay selection and GDT099 finds no global submotif association.
`PCH` is the clearest concrete new candidate: a recurrent HB/S record-phase
host family with a domain-local pharmaceutical spatial-context association,
not a manuscript-wide spatial word.

This remains more coherent than compressed natural language alone or pure
notation alone because it explains formal reuse, register rendering, page
vocabulary, and record serialization together. It is not ready for translation.
Six new non-f84 predictions are frozen. f84r receives no prediction and remains
completely sealed.
