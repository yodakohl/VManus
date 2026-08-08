# Confirmed grammar baseline

This file is the active description of what the text itself supports. “Grammar”
means reproducible formal organization; it does not imply ordinary speech or
licensed English meanings.

## Representation

- Treat ZL3b, IT2a, and RF1b as alternate readings of one physical manuscript.
- Preserve visible spaces. They are informative hierarchical boundaries, but
  not necessarily European words.
- Preserve physical lines as record/utterance units.
- Keep literal roots separate from FORM, ROLE, and CONTEXT annotations.

## Best current model

The safest compact model is a **manuscript-wide hierarchical, page-conditioned,
line-reset construction system**. “Record-like” describes its organization;
it does not identify the system as a record notation rather than language,
mnemonic text, or a synthetic/generative process.

```text
MANUSCRIPT: shared cross-stratum assembly + cross-Currier directional relation
  PAGE: qualified order-free literal-root inventory
    PARAGRAPH: opening versus continuation state
      LINE: entry carrier + rising line-local coordinate, reset at next line
        SEQUENCE: root identities assembled non-exchangeably at local edges
          FORM: literal root + reusable shell/bound/free operations
            BOUNDARY: root-conditioned JOIN / SPACE / detached completion
```

This hierarchy combines the held page result with held local adjacency. It is
more specific than calling the manuscript merely a bag of page vocabulary or
merely a line template. It still supplies no lexical key.

## Core observations

- Reusable roots and form pieces productively recombine. Held unseen forms can
  usually be rebuilt from previously seen pieces.
- Formal states have directional order within lines and reset at line breaks.
- Position-controlled local transition families include D-to-q and E-to-q.
- REL_I, FREE_L, and FREE_R can be written joined or as detached completions.
- Bare d/s/t occur as line-entry carriers with a qualified paragraph-state
  split; these tags are positional, not translated commands.
- Strict AII+N precedes strict AI+N more often than the reverse.
- Roots have a small distributed left-to-right content/identifier gradient.
- Exact `che+VALUE` is a productive E-bound carrier frame. JOIN versus SPACE
  after `che` is root-conditioned. Its relative content direction is qualified;
  its lexical function is unknown.
- Literal roots show qualified page-scale coherence beyond known form shells
  and line length: nonadjacent same-page lines overlap more than matched
  cross-page lines in a frozen held test and both alternate readings agree in
  direction. Immediate neighbors do not show excess overlap over matched
  nonadjacent same-page lines.
- Adjacent literal-root identities are non-exchangeable inside physical lines
  after the full page vocabulary, exact root-free form shells, horizontal
  position, paragraph-entry state, stratum, and every D/C edge location are
  fixed. The held ZL residual is +0.03518 bit/edge (69.4% positive pages,
  conservative p=0.000488), with IT/RF in the same direction. Thus roots are
  assembled into local sequences rather than drawn independently from a page
  bag.
- The aggregate adjacency relation is not confined to matching metadata
  strata. On held ZL pages, models trained with the target Currier value,
  section, or catalogued hand completely excluded retain +0.03023, +0.02819,
  and +0.03391 bit/edge respectively (joint-family p=0.00196, 0.00244, and
  0.000488); IT/RF keep every direction positive with sufficient page reuse.
  This supports one shared manuscript-wide construction system across those
  boundaries. The three metadata axes are correlated, so they are not three
  independent effects or replications and do not identify authorship.
- Across Currier A/B specifically, the shared relation contains transferable
  physical-orientation information beyond unordered D-C pair affinity and
  root-side propensity. With the target Currier value excluded from training,
  the held ZL oriented-minus-collapsed increment is +0.01725 bit/edge on 80.6%
  of pages (joint-family p=0.0171); IT/RF remain positive with sufficient page
  reuse. Equivalent section and hand increments did not confirm. This is a
  directional construction constraint, not proof that physical left-to-right
  order is spoken reading order.
- That Currier-transferring directional increment exceeds a fixed local
  self-citation process under the identical relaid geometry and exact
  conditional null. ZL is +0.01692 bit/edge with 80.6% positive pages; zero of
  62 eligible sealed Timm controls match either statistic (conservative
  p=0.01587). The specific generator is insufficient, but this does not choose
  language over notation, mnemonics, or other generative mechanisms.

## Explicit non-results

There is no confirmed noun, verb, adjective, negator, number, person marker,
case, tense, sound value, SVO/SOV order, language family, cipher, codebook,
plant name, page topic, or plaintext sentence. The page-scale result does not
establish semantic continuity or rule out local production effects. Structured
root adjacency does not identify a linguistic phrase, dependency label, POS,
or meaning. Cross-stratum transfer does not prove ordinary language, one
author, or a single spoken variety. Failure of the fixed Timm control does not
prove ordinary language or rule out synthetic generation generally. Terms such
as carrier, value, dependent,
opening-associated, continuation-associated, content-like, and identifier-like
are structural tags only.

## Legacy v0.51 quarantine

`FIRST_TRANSLATION.md` and the v0.51 all-token artifact are recovery-era
diagnostics, not the active claim registry. Their complete coverage means that
every locus could be represented while leaving unknown roots literal; it does
not mean every token was understood.

The old `ar/al` agreement/harmony analogy, bathing/herbal meanings for `ol`,
`l+X`, `X+ol/X+od`, `che+od/o/k`, star-entry templates, hard-D bathing label,
and FREE_A herbal label are not active claims. Re-admission would require a
primary-evidence audit and a new held invariant under the current method rules.

The exact reports, result files, and runners are enumerated in
`PRIMARY_EVIDENCE.tsv` and bound by the archive SHA-256 manifest.
