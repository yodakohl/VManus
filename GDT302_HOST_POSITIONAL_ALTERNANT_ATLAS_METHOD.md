# GDT302 — host-specific positional alternant atlas

## Purpose

Turn the validated GDT299/GDT301 exact-form placement channel into a practical
formal normalization atlas.  For each recurring opaque `PAGE_HOST`, enumerate
its complete source forms and identify forms biased toward physical
`FIRST/MIDDLE/LAST` placement relative to the host's own baseline.

This is a post-confirmation descriptive atlas, not a new semantic test.  Raw
complete forms may be displayed only after an exact observation-ID join to the
published f84-free GDT276 inventory.  No substring search or new segmentation
is performed.

## Frozen population and thresholds

Use exactly the GDT299 6,844-event Voynich population.  A scored form must have
at least 8 events on at least 4 physical folios.  Its host must have at least
20 eligible events and at least two scored complete forms.

For every scored host+form report:

- events, folios, sections, hands, registers;
- raw and host-conditional `FIRST/MIDDLE/LAST` rates;
- the role with maximum smoothed log2 ratio `P(role|form)/P(role|host)`;
- exact leave-one-folio codelength contribution to GDT299
  (`PAGE_HOST bits - WHOLE_FORM bits`);
- the number of powered section and hand strata with a same-sign role excess.

Call a form `STABLE_POSITIONAL_ALTERNANT` only when its held-folio contribution
is positive, its maximum role likelihood ratio is at least 1.5, and every
powered section and hand stratum has the same sign (with at least two powered
strata across the two axes combined).  Otherwise label it `PROVISIONAL`,
`WEAK`, or `COUNTEREXAMPLE` by frozen arithmetic rules.  A contrast pair is
two scored forms of the same host with different preferred roles; it is
`STABLE_CONTRAST` only when both are stable candidates.

Report positive-gain concentration in the top 10 and 20 forms and the number
of hosts with stable contrasts.  This quantifies whether the validated channel
is broad or carried by a small alternant dictionary.

## Claim ceiling

The atlas may identify whole-form positional alternants and normalization
candidates only.  `FIRST/MIDDLE/LAST` are physical roles, not grammatical or
semantic labels.  No word meaning, morpheme, sound, language, plaintext, or
translation follows.  No f84 row may be opened, parsed, retained, joined, or
scored.
