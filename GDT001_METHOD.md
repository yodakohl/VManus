# GDT001 whole-manuscript tournament method

Status: exploratory YOLO-branch method. Nothing produced here is a confirmed
translation.

## Input and alternate observations

`build_gdt001_corpus_lattice.py` constructs one full-manuscript lattice from
ZL3b, IT2a, and RF1b. They are alternate observations of one object, never
independent witnesses. An alternative is a complete physical-line path. It
retains manual group separators, raw IVTFF group text, drawing-interruption
states, line resets, page, physical folio, section, Currier, catalogued hand,
layout role, and the available STA construction metadata. Byte-identical
edition paths collapse. Choosing among `n` distinct line paths costs
`log2(n)` bits in addition to its exact raw/separator residual.

## Common code

Every candidate uses:

```
L_total = L(class)
        + L(key / parameters / transducer / dictionary)
        + L(latent text or records)
        + L(source | latent, decoder)
        + L(lattice choice + raw manual residual + separators)
        + L(exceptions)
```

All components are in bits. `gdt001_score_breakdown.tsv` allocates global
variable costs over Currier and section in proportion to source-symbol count
and retains class/key bits as a separate global row; the allocation is a
diagnostic, not a refit. `gdt001_edition_sensitivity.json` scores the three
edition-constrained path selections under the frozen winning predictor.

## Systems

- `ABBR_LANG`: a shared monotonic mapping into a frozen historical character
  LM. Stage 1 uses one source letter per latent letter. Stage 2 uses a frozen,
  explicit longest-match multigraph inventory and tests one paid null rule.
  Allography/homophony pays an exact reverse Dirichlet code.
- `HOMOPHONIC_CIPHER`: every source unit has an explicit target letter; many
  source units may share a target, with exact reverse ambiguity cost.
- `RECORD_NOTATION`: anonymous prefix/operator, core/value, suffix/state
  records, plus a separate whole-group anonymous dictionary theory.
- `NONSEMANTIC_GENERATOR`: integrated character n-grams, page unigram,
  explicit copy-modify programs, and an int8 quantized GRU whose retained
  probability calculation is reconstructed by NumPy on CPU. Follow-up source
  baselines include a canonical-locus-order prequential mixture of seven
  causal KT experts. Each order-2 context maintains its own Bayesian weights
  over shared, longer-history, Currier, section, hand, layout-kind, and
  grammar-scope experts; weights update only after the encoded source event
  and then undergo a paid fixed-share step. The model is conditional on the
  metadata already carried by the lattice. Its serialization is not asserted
  to be physical writing chronology.
  A separate within-line latent-state test assigns one explicit hidden state to
  every modeled source event, pays an integrated first-order state-path code,
  and emits symbols from state-by-observed-history KT tables. It is distinct
  from the earlier one-state-per-line model; its complete state paths and
  restart hashes are retained.
- `HYBRID`: a Codex-originated explicit mechanism in which the first group
  supplies a page-sequential entry state and subsequent groups are reusable
  stem/modifier programs.

The six provenance-clean language packs are Latin, Middle High German, Middle
French, Old Italian/Tuscan, medieval Czech, and Old Hungarian. The committed
manifest binds source URLs, repository commits or archive hashes, licenses,
normalization, and normalized-corpus hashes. Generated pseudo-medieval text is
not used.

## Search and exact reconstruction

The RTX 3090 evaluates large mapping populations, multigraph assignments,
homophonic assignments, and three neural-null restarts. Population sizes,
seeds, generations, configs, exact keys, and failures are retained. The
published crossover benchmark shows when CUDA becomes material. GPU scores
must agree with CPU scores within `2e-6` bits before a key can be retained.
The original winning n-gram is reconstructed independently from line paths and
context counts by `validate_gdt001_tournament.py`. Later branch-local leaders
have their own independent validators; in particular,
`validate_gdt001_online_context_mixer.py` reconstructs every pre-event
probability for all six frozen share rates without importing the producer.

## Controls

Five deterministic counterfactual lattices transform every alternate path
while retaining its original observation cost: within-line, page-conditioned,
global frequency-preserving, boundary-preserving identity, and page-local
Timm/copy-modify controls. Representative nonsemantic, record, language, and
cipher systems are refit to each. Controls are interpretive diagnostics, not a
folio-held confirmation test.

The later context-mixer control uses exactly the same frozen causal algorithm
and winning share on all five counterfactuals. Its larger gain on the Timm
copy/modify manuscript makes it a stronger generic source null, not evidence
for decipherment.

## Candidate export and fixed packet

The export comprises the five global MDL leaders plus the strongest missing
required system classes, for ten total candidates. Each has an explicit
mapping, complete-manuscript segmentation and output, lexicon, model spec,
reverse-generation comparison, failure analysis, structural explanation, and
ten frozen risky predictions. The fixed packet contains Herbal Currier A,
Currier B, label-rich f75v, f57v, f67r2, f75v, circular f69v, and f116v. No
output is paraphrased or repaired.

For stochastic source models, reverse generation compares the actual selected
form to a frozen wrong form made by rotating each multi-symbol manual group by
one source symbol. Record systems deterministically reconstruct the source
from the exported anonymous record and dictionary; wrong forms have zero
conditional probability.

## Decision

A candidate is freeze-worthy only if it is competitive after full key cost,
stable across restarts, mostly shared across manuscript strata, better on the
real manuscript than counterfactuals, reverse-generative, explicit, and able
to state falsifiable predictions without unlimited exceptions. If none meets
that standard, the branch decision is `NO_DECIPHERMENT_CANDIDATE_FREEZE`, not
a repaired translation.
