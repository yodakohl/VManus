# Sidequest Pass 633: a finite construction grammar

## Result

Five six-card workshop jobs can be expressed in 22 legal written orders when
only physically necessary precedence relations are fixed. These are 22
linearizations of five jobs, not 22 newly invented recipes.

The result advances the working theory in a useful way. The notation is neither
a rigid phrasebook nor free word salad. It behaves like a compact command
register in which independent address and quantity cards may trade places,
while material transformations retain their order.

## Capacity by case

| Case | Legal orders | What may move | What remains fixed |
|---|---:|---|---|
| C1 | 8 | prescribed amount, work compartment, and target can be interleaved | amount and compartment precede washing; washing and target precede holding; holding precedes close |
| C2 | 5 | the bare readiness check can move along the process | prepared amount -> continue -> divide -> target -> full close |
| C3 | 6 | the extraction chain and address chain can interleave | wring -> pour; amount -> target; pour and target -> hold -> close |
| C4 | 1 | nothing | amount -> portion -> subsequent portion -> target -> fasten -> store |
| C5 | 2 | first ingredient and prescribed amount may swap | both precede further stock ingredient -> target -> second stage -> close |

Total: 22.

## Relation to the preceding exercises

- The five Pass-631 orders are all generated.
- All eleven Pass-632 licensed cue movements are generated.
- Eleven additional orders appear because non-cue cards may also trade places
  when their process relations are independent.
- All 22 still expose the branch cue within the first five cards and select the
  intended case.

The new C3 forms are especially informative. `cfhy` can cease to be the first
written card if amount or target is declared before the extraction pair, but
it can never follow `cphy`. Thus the same semantic unit is position-bound
relative to its complement, not necessarily bound to an absolute line slot.

## Generative audit

- Precedence rules: 25, exactly five per case.
- Legal orders: 22.
- Exact backward readings: 132/132 steps.
- Complete orders found in the 381 source events: 0/22.
- Adjacent pair instances absent from the source: 103/110.
- New words, cards, surfaces, pages, and Astro labels: 0.

The high pair novelty is expected because the grammar deliberately combines
known commands rather than copying source phrases. What matters for this
creative sidequest is that the partial-order rules prevent the combinations
from becoming physically self-contradictory.

## Apprentice implementation

The master need only teach five arrows for each job. A learner lays down all six
cards, then repeatedly chooses any card whose prerequisites have already been
written. That produces every legal order exactly once after duplicate sequences
are removed.

For example C3 has two simultaneous chains:

```text
AUSWRINGEN -> EINFUELLEN --+
                            +-> HALTEN -> SCHLUSS
SOLLMASS   -> ZIEL --------+
```

Either chain may begin. Their internal arrows may not be reversed.

## Interpretation

The best current writing-system model is now:

1. visible picture establishes the case owner;
2. one early cue identifies the case supplement;
3. six common functional modules provide the job skeleton;
4. short semantic words and invariant commands fill the modules;
5. a small partial-order grammar linearizes independent cards;
6. the renderer supplies hand/register forms;
7. sixteen residual surface entries remain memorized.

This is simple enough for several scribes to learn because they do not memorize
every complete line. They memorize cards, a handful of arrows, and local
surface habits.

## Next move

The current exercise varies order but not content. Next, define one controlled
substitution slot in each case—quantity, target, hold grade, or close—and swap
only semantically compatible existing cards. This will estimate how many
distinct workshop jobs, rather than merely word orders, the fixed deck can
express.

## Files

- `SIX_HUNDRED_THIRTY_THIRD_25_PRECEDENCE_RULES.tsv`
- `SIX_HUNDRED_THIRTY_THIRD_22_LEGAL_ORDERS.tsv`
- `SIX_HUNDRED_THIRTY_THIRD_132_STEP_BACKWARD_READ.tsv`
- `SIX_HUNDRED_THIRTY_THIRD_110_BIGRAM_AUDIT.tsv`
- `SIX_HUNDRED_THIRTY_THIRD_FINITE_GRAMMAR.md`
- `SIX_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json`
- `build_six_hundred_thirty_third.py`
- `validate_six_hundred_thirty_third.py`
