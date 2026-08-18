# GDT299 — opaque whole-form physical-role transfer

## Question

Does a complete source-group identity predict its physical position in a line
beyond its stripped opaque PAGE_HOST on unseen folios?  This tests the GDT298
proposal that high-capacity joint forms are functional record renderings rather
than arbitrary spelling variants.

No source string or PAGE_HOST substring is inspected.  Complete forms are
represented only by the frozen `source_surface_sha256` identity.

## Frozen panel

Use every GDT278 native-order panel.  Exclude one-group lines because `ONLY` is
then deterministic.  An event is scoreable only when its exact host and exact
surface hash both occur outside its physical folio.  A panel is powered for
descriptive scoring at 500 events; it enters the randomized family only with at
least 100 identity-mobile events.  These gates are fixed from identity/support
counts before any `FIRST/MIDDLE/LAST` score is computed.

The outcome is mechanical physical group position:

- `FIRST`: group index 1;
- `LAST`: group index equals physical line group count;
- `MIDDLE`: otherwise.

## Models

Within each held-folio fold use hierarchical Dirichlet-1/2 / prior-mass-11
codes:

1. `LAYOUT`: exact section, Currier, hand, and physical group count, backed off
   to the panel distribution;
2. `PAGE_HOST`: exact opaque host, backed off to `LAYOUT`;
3. `WHOLE_FORM`: exact surface hash, backed off to `PAGE_HOST`.

The primary effect is `PAGE_HOST bits - WHOLE_FORM bits` per event.  Report
top-1, positive folios, and all panel effects.  Voynich prior masses 5 and 22
are fixed sensitivities.

## Null

In 64 deterministic worlds, permute surface identities within exact panel ×
physical folio × section × Currier × hand × physical group count × PAGE_HOST
strata before held-folio fitting.  This preserves host, exact opportunity,
line length, every surface identity's per-folio count, and all outcomes while
destroying only the observed whole-form-to-position alignment where mobility
exists.  Report local and max-family inclusive tails over all null-variable
panels.

## Decision and ceiling

Call `WHOLE_FORM_PHYSICAL_ROLE_TRANSFERS` only if Voynich gain is positive,
at least 60/91 folios are positive, both prior sensitivities are positive, and
the corrected tail is at most .05.  Otherwise call
`WHOLE_FORM_PHYSICAL_ROLE_WEAK_OR_LOCAL`.

Even support would identify only held-folio physical-line placement carried by
opaque whole forms.  It establishes no word, morphology, function, semantic
role, code value, language, meaning, plaintext, or translation.  No f84 row
may be opened, parsed, retained, joined, or scored.
