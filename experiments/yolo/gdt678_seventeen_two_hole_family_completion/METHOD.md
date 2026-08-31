# GDT678 method

## Question

Can the 34 residual forms in V51's seventeen two-gap lines receive concrete,
component- or learned-whole-based meanings that survive all 101 exact admitted
occurrences, close both slots in every source line, and improve practical prose
without hiding alternate-reader boundaries or returning to generic filler?

## Inputs and scope

No manuscript page is newly admitted. The deterministic build uses:

- GDT671's 4,128-line V48 panel as the frozen token and base-gloss surface;
- GDT673, GDT674, GDT675 and GDT677 position artifacts to reconstruct the
  exact current 7,923-gap overlay rather than treating the old V48 panel as the
  current state;
- GDT677's complete 51-line V51 deck as the source edition;
- a guarded locus-selected query of the mixed cross-transcription source for
  exactly 82 target lines and named output columns. `f84*` is rejected from the
  raw selector field before any row is materialized;
- `src/TARGET_CARD_SPECS.tsv`, `src/SOURCE_LINE_SPECS.tsv` and
  `src/BOUNDARY_DECISION_SPECS.tsv` as the explicit semantic and rendering
  inputs;
- `src/THREE_READER_SYNTHESIS.md` and seven sourced historical analogues as
  the recorded reasoning basis.

The route-check returned older one-hole and bulk-family completion passes, not
this V51 two-hole context circuit. GDT678 therefore uses a new context target
and a later overlay even where individual component relatives were learned in
those earlier passes.

## Three independent readings and synthesis

Three read-only passes used deliberately different backgrounds: a
late-medieval recipe copyist/family compositor, a practical apothecary/process
reader, and a historical pharmacology/scribal-boundary reader. Each counted
101 target positions on 82 lines/52 pages and proposed a meaning plus rival for
all 34 forms. The final cards preserve agreement where possible and make an
explicit choice where the readers differed.

The mixed model is intentional. Productive components remain useful, but an
already learned whole can be the better internal unit:

- `qokeod = qokeo+d`: prepare a hot extract and close it;
- `qoin = q+oin`: take the second preparation, with `qo+in`/form II retained
  as the rival;
- `qocho = qo+cho`: take the dry preparation, with “dry and prepare” retained
  as the rival;
- `cphdor = cph+dor`: measure a portion of medicinal composite;
- `qoeeo` keeps learned `oeeo`, second maceration preparation, as a nominal
  object before the following `lldar` measure command.

The high-volume nominal cores are `olchey` (20 occurrences), `oteor` (10),
`chotar` (9), `keeey` (9), `qokeod` (5), `keo` (5) and `pchedaiin` (4). The
lowest cards remain `yey`, `qy`, `rr` and `lldar`; their rivals and replacement
conditions are never omitted.

## Exact-occurrence circuit

`src/run.py` matches whitespace-delimited ZL3b tokens, never substrings. It
asserts the expected 34-surface/101-position distribution and verifies that
every target position is still open after reconstructing the GDT673/674/675/
677 overlays. For every occurrence it:

1. retains the full current before-context;
2. inserts exactly one unchanged card meaning;
3. aligns IT2a and RF1b against the ZL3b line with exact-token, merge and split
   operations;
4. records left/right surfaces, action license, reader support, practical
   boundary override and strongest rival;
5. rejects the inherited hard-generic vocabulary.

Reader support is 65 bilateral exact, fifteen IT2a-only exact, ten RF1b-only
exact and eleven neither exact. Every neither-exact position has a named
boundary or true-rival decision. A twelfth boundary row covers f7r.2, where
RF1b keeps ZL3b `keo` separate while IT2a joins it.

## Boundary-aware practical renderer

The token-parallel and practical layers serve different audit needs. Literal
card values and ZL3b slots remain one-to-one in the TSV. The practical layer
may collapse only a predeclared reader join:

- f7r.2 `keo r` becomes the already learned `keor`, “heiße Drogenportion”;
- f86v6.4 `l karchees` becomes “vollständig getrocknete Charge der ersten
  heißen Holzfraktion” because both alternates write `lkarchees`;
- f77v.7 ZL3b `rr` takes the practical value “getrocknete Wurzeldroge” because
  both alternate readers write `rchr`. The ZL3b-only “zwei Wurzelteile” rival
  stays explicit and no general reduplication rule is created.

Other split forms retain one semantic core without pretending the spaces are
independent evidence: `cholches/chol ches`, `aiindy/aiin dy`, and joined
`oteor y`. True reader rivals at `olchey/oleeey`, `qoin/qoain` and the f95
tail remain visible.

## V52 and global coverage

Each of the seventeen V51 source lines must have exactly two matching targets
and two residual gaps. The builder replaces both, recomputes action ordinals
and line mode, and verifies that no aligned or practical output contains a
remaining unknown marker. Eleven new action positions are added. f49r.16
changes from nominal register to action sequence, and f83v.12 from nominal
register to mixed record.

V52 contains the unchanged 51 lines/479 tokens. Assignment moves 352→386,
gaps 127→93, complete lines 11→28 and licensed actions 49→60. The remaining
gap distribution is eight three-gap, eight four-gap, six five-gap and one
seven-gap line.

The global effect is independently rebuilt from exact position sets. All 101
targets were open. Gaps move 7,923→7,822 and complete lines 1,391→1,410.
Nineteen lines close: the seventeen selected lines plus f38v.6 through
`keeey` and f80r.21 through `oltain`.

## Validation and decision rule

The pass requires:

- 34 unique cards and exactly 101 still-open exact positions on 82 lines/52
  admitted pages;
- the registered per-card occurrence/page counts and one semantic core at
  every position;
- reader support 65/15/10/11 and explicit decisions for every neither-exact
  position;
- seventeen token-preserving source closures, 34 new V52 positions and eleven
  new actions;
- V52 totals 386/479 assigned, 93 gaps and 28 complete lines;
- global totals 7,822 gaps and 1,410 complete lines, including exactly the two
  named extra closures;
- zero hard-generic matches, valid historical scope limits and ten forward
  predictions;
- a temporary independent rebuild byte-identical across all ten generated
  result files.

## Claim ceiling

The cards are concrete, replaceable working meanings in a mixed learned-whole
and productive-component renderer. Validation proves source selection, token
alignment, declared cards, reader operations, action scope, counts and
deterministic reconstruction. It does not prove plaintext, phonetics, a
historical codebook identity, exact plant species, disease, patient, cure,
carrier liquid, or manuscript-wide translation.
