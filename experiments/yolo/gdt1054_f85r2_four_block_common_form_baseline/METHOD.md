# GDT1054 method — post-selection f85r2 four-block baseline

## Question and status

GDT1042 found that exact `aiin` is the only form present in all four fixed f85r2 spatial blocks in all three alternate readings. Is four-block occupancy unusual even under the minimal null that keeps this page's exact word inventory and the four block lengths? This diagnostic was selected **after** GDT1042 and after root inspected `aiin` counts and calculated its conditional occupancy probabilities (ZL .224, IT .090, RF .222). It is not a prospective significance test or an independent target discovery.

## Inputs and boundaries

Use only the frozen `native_groups.tsv` artifact of GDT1042. For each reader independently, retain all raw exact groups in N/E/S/W; exclude the explicitly OUTSIDE `.1`/`.24` groups. Do not normalize uncertain readings or combine readers as independent witnesses. Confirm the source file SHA-256 against the input field in `experiment.json`. f84/f84r and reserves stay closed.

## Calculation

For each reader, report block lengths, all whole forms with at least four occurrences, the exact four-block occupants, and exact `aiin` count by block. Calculate the probability that a *preselected* form with its observed page count occupies all four blocks under a uniform allocation of its occurrences to the fixed block positions, by summing multivariate-hypergeometric configurations. Separately run 100,000 deterministic full-inventory permutations (seed 1054), preserving every exact whole's multiplicity and block lengths, and report the fraction with *any* four-block occupant. Monte Carlo interval describes algorithmic precision only. A separate validator must recompute the inventories and analytic probabilities, check all result fields and replay the shuffle result.

## Decision and claim ceiling

The before-seeing-data target choice and earlier calculation make the numerical results exploratory. If occupancy is ordinary, do not promote `aiin` as a fourfold age/season word merely because it recurs; if it is unusual under this weak null, seek a new source-bound meaning distinction before glossing it. Either outcome leaves f85r2 figure ownership, historical meaning, and translation unconfirmed. This test cannot make a project-wide significance claim: it does not correct the entire search and the three readings are one manuscript.

The smallest implementation is one source-only runner, one independently written validator, this method, a compact result and report. Budget: 30 minutes including validation/publication; stop if the source/manifest boundary does not validate rather than repairing unrelated infrastructure.
