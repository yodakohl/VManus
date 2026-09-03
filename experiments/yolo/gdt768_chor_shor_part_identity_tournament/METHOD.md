# GDT768 method

## Question

Which of five fixed complete-word models best explains `chor` and `shor`, and
what is the most concrete reader that can be retained without pretending that
the flower-versus-seed/fruit direction has been identified?

The primary output is therefore a usable working reader. The statistical
tournament decides whether that reader may replace either target default; it
does not assign sounds or Latin values to EVA signs.

## Fixed inputs

GDT768 uses only the already admitted guarded cache. It opens no new page,
image, or transcription and explicitly excludes `f84` and `f84r`. The six
reader-exact complete-form anchors are:

| target | role in this experiment |
|---|---|
| `chor`, `shor` | target nominal wholes |
| `cthy` | leaf/aerial-herb comparison |
| `dair` | measured-fraction comparison with an old local root rival |
| `kooiin`, `koaiin` | weak rootstock-class visual comparisons |

The route and priors come from GDT625, GDT631, GDT735, GDT737, GDT759,
GDT762, and GDT767. Exact model, anchor, comparison, historical, and line
defaults live in `src/*.tsv`. Historical rows carry source IDs and expected
register patterns; they never carry Voynich identity credit.

Before a donor can enter any context measurement, the 172 complete surfaces
quarantined by GDT754 as source-composed are removed. This blocks 54 potential
target-context exposures. Family distance is applied only after that gate.

## Core atlas

`src/core_atlas.py` enumerates every reader-exact occurrence of the six
anchors, retaining page, locus, section, hand, line position, paragraph
position, full EVA line, and nearby eligible donors. It builds three context
scopes:

- `D1`: immediate neighbors;
- `R3`: a three-token radius;
- `LINE`: all other positions on the written line.

Every scope is recomputed at edit-distance radii ED0, ED1, and ED2. ED0 blocks
the target itself as a donor. ED1 and ED2 additionally block complete donor
surfaces within the corresponding Levenshtein distance of that target. Edit
distance is only a written-form contamination control: it yields no component,
sound, stem, or meaning.

Eligible donors contribute the fixed target-excluding feature vector
`DRY, MOIST, HOT, COLD, STAGE, VALUE_AMOUNT, PREP, PROCESS_CLOSE, H1..H4`.
Anchor contacts are counted separately. The core also emits exact pair counts,
multi-anchor lines, and global role geometry.

## Observed metrics

### State polarity

For target `t`, radius `r`, and scope `s`, direct and line polarity is:

```text
P(t,r,s) = (DRY - MOIST) / (DRY + MOIST)
```

Positive is dry-affine and negative moist-affine. Empty denominators score
zero. The three radii reveal whether an apparent contrast survives removal of
near-family donor forms.

### Exact state-whole persistence (CF04)

CF04 is measured from the D1 donor census, not assigned a constant. Its fixed
comparison deck consists of complete written forms:

```text
dry-side deck   = chol | qokchol | cheor
moist-side deck = shol | sheol | sheor
```

These labels describe inherited working-state classes only. The forms are not
split into EVA components.

For M01, target retention is the expected-family count at ED2 divided by its
ED0 count. The pair score is conjunctive:

```text
CF04_M01 = min(chor dry-side ED2 / ED0,
               shor moist-side ED2 / ED0)
```

For M02 and M03, CF04 instead measures symmetric form-conditioned nominal
compatibility: the weighted Jaccard of the two target-normalised six-form
profiles at ED2. Thus actual shared survival can support two parallel nominal
items, while contributing exactly zero credit to the direction “flower” versus
“seed/fruit”. M04 uses the observed fraction of named state-whole types around
`chor` at ED0 and reports the matching `shor` breadth as counterevidence.

### Other comparison channels

- CF05/CF06 count exact lines and direct pairs with `cthy`, `dair`, `kooiin`,
  and `koaiin`, normalised by target opportunities.
- CF07 is explicitly a `BROAD_VALUE_AMOUNT_PROXY`. It is not a bound quantity
  formula and cannot identify an organ.
- CF08 compares line and paragraph position by Jensen-Shannon similarity.
- CF09 compares section distributions by Jensen-Shannon similarity.
- CF10 compares the target-excluding 12-dimensional cofields by cosine and
  weighted Jaccard at every scope and radius.
- CF11 measures replicated `chor`/`shor` same-line and direct pairing.
- CF12 is a cached broad reproductive visual prior for `shor`.
- CF13 checks whether each model has its declared circa-1400 architectural
  comparators. Historical coverage supplies no target-word identity points.

## Five fixed models and scoring

The fixed competitors are:

1. M01: dry and moist forms of the same reproductive part;
2. M02: `chor` flower, `shor` seed/fruit;
3. M03: the reverse assignment;
4. M04: `chor` general herb, `shor` reproductive part;
5. M05: two role-distinct learned wholes.

For every applicable feature, `src/model_scoring.py` returns a match in
`[0,1]`, an evidence sentence, and a counterevidence sentence. Model scores
are the declared weighted means:

```text
score(model) = sum(weight_i * match_i) / sum(applicable weight_i)
```

Unknown identity never helps M05. Historical and visual priors are explicit
and bounded. M02 and M03 receive identical evidence because the admitted
observations contain no directional discriminator.

A high score alone cannot replace a dictionary default. M01 additionally
requires persistent opposite state polarity; M04 requires exposure-controlled
`chor` breadth; M05 requires two stable divergence channels. M02 or M03 needs
two independent directional contrasts and a lead of at least 0.10 over its
reverse. When they tie, their shared two-part relation may be retained, but
both directional minimum-support flags remain false.

## Concrete reader construction

The six-anchor dictionary keeps two layers:

- a portable role or class reading;
- a bold, concrete, immediately replaceable German default.

The twelve selected complete lines contain 94 reader-exact tokens. Every token
has a default and a visible rival or confidence note; no token is silently
discarded as “work item” or “perform operation”. The complete line text,
token-by-token defaults, and a readable German rendering are emitted together.

The bold defaults make the record legible enough to compare models. They are
not asserted plaintext. In particular, the current display
`chor=Blütenstand`, `shor=Fruchtstand` may be reversed without changing the
winning shared relation.

## Historical comparison

The circa-1400 comparators show two compatible record architectures: parallel
part rubrics such as flower, seed, fruit, leaf, root, wood, and gum; and learned
materia names followed by part, quality, state, degree, amount, or recipe
fields. GDT768 tests whether the observed complete wholes behave like entries
in such architectures. It does not equate an EVA initial with the initial of
`flos`, `semen`, `radix`, `lignum`, or any other Latin word.

## Claim ceiling

GDT768 may rank the five whole-word models, retain the shared parallel-part
reading, and publish concrete replaceable defaults. It confirms no lexeme,
plaintext clause, plant, substance, language, cipher, sound, glyph value, or
productive EVA component. Flower-versus-seed identity credit and component
export credit are both fixed to zero.
