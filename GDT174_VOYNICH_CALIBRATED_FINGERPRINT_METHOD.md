# GDT174 — Voynich fingerprint against frozen A/B2/factorial-B controls

Status at registration: **FROZEN_BEFORE_VOYNICH_FINGERPRINT_SCORING**.

## Question

Where does the already frozen Voynich VManus architecture fall on each
separate GDT173 calibration axis when lexical A, human-grown distributed B2,
and factorial distributed B are kept exactly as published?

This is a rank-and-direction comparison, not a model-selection score.  No
threshold, synthetic renderer, parser rule, control value, or composite score
may be changed after seeing the Voynich fingerprint.  B3 is not constructed.

## Frozen inputs and scope

The three controls are read only from the published GDT172/GDT173 parse,
diagnostic, recovery, and three-system fingerprint artifacts.  Their hashes
are committed in `gdt174_design.json`; A, B2, and factorial B are never
regenerated.

Voynich uses the frozen HPR2 inventory
`gdt062_right_family_inventory.tsv`, restricted before retention to the
f84-free complete physical lines already registered in
`gdt046_line_frames.tsv`.  The primary panel therefore contains only lines for
which every source group has an HPR2 row.  No f84 row may be retained, parsed,
joined, or scored.  The experiment reads no image and creates no new parser.

## Frozen representation bridge

For parser-independent host diagnostics, `PAGE_HOST` is the opaque host.  The
HPR2 compiler signature is retained without a gloss:

- `outer_left = WRAPPER`;
- `local_left = (INNER_D, LOCAL_FRAME)` as one categorical pair;
- `right_inner = RIGHT_FAMILY`;
- `right_outer = (DY, B3)` as one categorical pair.

This bridge does not claim that HPR2 fields equal the blind parser's inferred
fields.  It merely supplies the same categorical slots required by the frozen
diagnostics.

Raw-token LEFT and RIGHT operations are discovered with the exact GDT170/173
visible prefix/suffix rules: lengths 1--3, at least eight distinct residual
hosts, at least five physical folios, at most twelve operations per side, and
the unchanged deterministic ranking.  Compatibility uses the exact 1,024
world GDT173 support-randomization formula.  It is the cleanest directly
comparable axis.

## Frozen diagnostic axes

1. `HOST_RECOVERY_ACCURACY` and `EXACT_TRUE_HOST` are **not comparable** for
   Voynich because there is no lexical-ID oracle.  Recurrent-host mass and
   cross-folio host mass are reported as proxies, never as recovery.
2. `LEFT_RIGHT_COMPATIBILITY` uses the exact synthetic definition and reports
   density, null density, excess, and inclusive p.
3. `SHORT_HOST_STRUCTURE` is the exact token-weighted PAGE_HOST length-2/3
   mass.
4. `SAME_GROUP_SUBSTITUTION` uses the exact repeated one-glyph substitution
   delta-cosine endpoint, but the HPR2 six-field compiler signature makes it
   structurally analogous rather than oracle-equivalent.
5. `EXTERNAL_SUBSTITUTION` uses the exact PAGE_HOST +/-2 physical-line window
   endpoint.
6. `NEXT_HOST` and `WHOLE_LINE` use the exact GDT173 held-folio smoothing and
   codelength-gain formulas on complete physical lines.  Raw gain magnitude is
   not directly comparable across unequal corpora; only sign is ranked.
7. `CLOSURE` treats any nonempty RIGHT_FAMILY, DY, or B3 as an HPR2 right mark.
   Paragraph ends are derived from the frozen editorial paragraph-start field
   within the complete-line panel.  This is structurally analogous, not a
   direct synthetic-record endpoint.
8. `REGISTER_ALIGNMENT` applies the same anonymous host-signature and greedy
   matching formula across powered Voynich registers.  Synthetic renderers
   contain parallel content whereas Voynich registers do not, so its rank is
   always `UNRESOLVED_NOT_DIRECTLY_COMPARABLE` regardless of its number.

## Rank rules

No composite score is allowed.  For a dimensionless directly comparable axis,
a Voynich value outside the closed synthetic range is `OUTSIDE_SYNTHETIC_RANGE`;
otherwise its nearest published control by unscaled absolute distance is
`A_LIKE`, `B2_LIKE`, or `FACTORIAL_B_LIKE`, with exact ties reported as
`UNRESOLVED_TIE`.  For raw codelength gains only the sign is compared; a sign
shared by all controls is `UNRESOLVED_SHARED_DIRECTION`, while a sign shared
by a strict subset names that subset.  Structurally analogous or nonparallel
axes are always `UNRESOLVED_NOT_DIRECTLY_COMPARABLE`.

## Outputs and claim ceiling

The result must publish one side-by-side metric table, an axis-placement table,
counterexamples, a result JSON, a non-importing validator, and a report.  It
may identify which architectural coordinates are or are not covered by the
three frozen controls.  It cannot establish a Voynich encoder, word, code,
language, morpheme, role, meaning, plaintext, or translation.
