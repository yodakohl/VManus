# GDT623 method

## Question

Which orientation of the formal GDT622 `qo+(k|t)+(ch|sh)` square best fits a
real late-medieval temperament codebook once source frequency, historically
plausible scope, repeated Voynich carriers, and the pictures are considered?
Can that corrected reader support short concrete defaults beyond the four
quality bundles?

## Admitted material

The frequency panel is the guarded page inventory from
`gdt327_joint_tuple_interlinear.tsv`, with `f1r` removed before the mixed token
table is queried. This leaves 179 pages and 32,339 ZL3b tokens. `f84` and `f84r`
are rejected from the selector field before any remaining columns are
materialized. The command projects only page, locus, source code, kind,
section, language, hand, token index, and EVA surface.

The manually inspected f31v root page lies outside that frequency panel. It is
queried as one explicit supplemental allow-value and is used only in the
five-page `p...air...` visual/head audit. It never enters frequency totals,
state-word totals, suffix counts, or orientation ranks.

The readable comparison rows are the 28 manually transcribed Clm 667 entries
from GDT622. Twenty-seven contain both axes: 19 hot/dry, three hot/moist, five
cold/dry, and zero cold/moist. This is a small readable sample, not an unbiased
census of medieval materia medica.

Official images and their hashes are bound in `SOURCE_PROVENANCE.tsv`.
`VISUAL_OBSERVATIONS.tsv` records only manually visible features and keeps
species identification separate from those observations.

## Formal families and orientation comparison

The strict exact family is:

```text
^qo(k|t)(ch|sh)(y|ey)$
```

The broader strict prefix family is:

```text
^qo(k|t)(ch|sh)
```

An exploratory substring census is retained separately and never substituted
for the two strict definitions. Counts are made for the complete 179-page
panel, all Herbal pages, and Herbal-A.

All eight ways to choose an axis pair and orient both binary values are mapped
onto hot/dry, hot/moist, cold/dry, and cold/moist. Each target distribution is
compared with the smoothed Clm 667 distribution by total variation. This is a
ranking aid: frequency can orient a working key but cannot prove that the
Voynich forms mean temperament.

## Historical scope rule

Four real layouts supply the attachment model:

1. Clm 667 attaches a compact code to a learned drug name on the same line.
2. The circa-1400 Pal.lat.1234 list lets a written quality-and-degree rubric
   scope forward down a column, with nested plant-part rubrics.
3. The 1484 Mainz Herbarius puts a named chapter before an immediate quality
   sentence and explicitly re-anchors later entries.
4. Mid-fifteenth-century Wellcome MS.541 f184r independently places learned
   whole drug names before compact hot/cold, dry/moist, and degree
   abbreviations on the same line.

The resulting priority is same line, then a one- or two-line record opening,
then a visibly headed forward block. A longer link needs an explicit repeated
name/class carrier or uninterrupted block. Silent backward attachment from a
late code to the first token of a page is rejected.

## Repeated carriers

Candidate carriers are line-first or page-first exact forms. The next strict
quality code is selected forward inside the registered horizon. A family is
called a local attachment only when it has at least two qualified occurrences,
every contact has the expected family, and every distance is at most three
physical lines. The search is exploratory and post-hoc; the artifact labels it
accordingly.

Six exact forms occur twice globally in the admitted token set and satisfy the
local rule in both places. Alternate-reading stability is checked manually in
ZL3b, IT2a, and RF1b, which remain alternate readings of one manuscript.

## State-word audit

The concrete targets are exact `chody`, exact `shody`, exact `shedy`, and the
display-only union `shody|shedy`. A strict q-code on the same page is assigned
by minimum absolute physical-line distance, then same-line token distance,
then source order. Pages with no strict q-code remain missing. A second count
retains only assignments within one physical line.

The full result and each section/language slice are emitted. This exposes the
important asymmetry: `chody` is consistently dry-contextual; `shody` is not
moist-contextual; `shedy` is moist-enriched overall but the enrichment varies
by section. Consequently only `chody = dry/dry class` receives medium status.
`shody = moist` is rejected. `shedy = moist/moist class` remains an explicit
weak register-local default; fresh and intentionally moistened are kept as
different historical concepts rather than synonyms.

## Visual part-word audit

`kooiin` is an exact two-page Herbal head on f2v and f29v; one-edit `koaiin`
heads f3v. The pictured plants differ, but all three emphasize a horizontal or
segmented underground stock. The exact two heads both lead locally to TCH.
“Rootstock” is a modern visual gloss; the expected medieval category is the
broader *radix*, often qualified by a shape word.

The broader `p...air...` set is manually finite rather than regex-mined after
viewing: `pdrairdy` f18r, `podairol` f23v, `podair` f31v, `pdair` f39v, and
`pdsairy` f43v. All five are Herbal page heads and all five pictures strongly
emphasize an underground part. Their strict or partial q-onsets differ, so the
head family receives a part/drug value but no temperament value.

`VISUAL_ROLE_AUDIT.tsv` fixes the eleven inspected pages before assigning two
additional weak roles. Exact `shor` occurs eight times on six of them and is
read as a flower/fruit stand or reproductive head. The only `koary` and
`korary` page heads accompany many terminal bodies and receive a weak
fruit/seed/reproductive-drug default. `koair` is excluded from that family
because its `air` core may instead belong with the root-part heads.

## Claim boundary

This is an exploratory working reader intended to generate concrete
predictions. It changes the active sidequest dictionary, but it does not
establish the language, sounds, cipher, plant identities, degree values, or a
complete plaintext. Untranslated surfaces remain visible in angle brackets in
`CONCRETE_READINGS_V2.tsv`; they are not padded with generic instructions.
