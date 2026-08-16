# GDT175 — recurrence with next-partner instability calibration

Status at registration: **DIAGNOSTIC_FROZEN_BEFORE_CONTROL_CALIBRATION**.

## Question

Can GDT174's combination of high cross-folio PAGE_HOST recurrence and negative
held-folio NEXT_HOST gain be explained by finite sampling, by register/section
mixture, or by genuinely folio-conditioned partner distributions?

GDT175 builds no encoder and no B3. Lexical A, human-grown B2, and factorial B
remain byte-frozen. The complete diagnostic is fixed and run on those controls
before the Voynich panel may be opened by the GDT175 scorer.

## Frozen event and host definitions

The control calibration uses only the published `SURFACE_ONLY` inferred-host
rows from GDT172/GDT173. A Voynich application, if later authorized by the
published control freeze, must use the exact f84-free complete-line HPR2 panel
from GDT174 and opaque `PAGE_HOST` identity.

A next event is physical-line group `i -> i+1`; no edge crosses a physical line.
A recurrent source host is eligible in a scope only when it has at least two
next events on at least two physical folios. Occurrence count means source-side
next-event count, not all group occurrences. The fixed bins are:

- `N2_4`: 2--4;
- `N5_15`: 5--15;
- `N16_63`: 16--63;
- `N64_PLUS`: 64 or more.

Coverage is always reported separately: total groups, total next events,
eligible hosts, eligible events, event coverage, and physical folios.

## Per-host metrics

For every eligible host in every scope report:

1. **Held-folio gain.** Use GDT173's exact alpha=16 nuisance and beta=8 host
   smoothing. The nuisance key is `(group index, line ordinal mod 3, physical
   line group count)`. Aggregate `log2(P_host/P_nuisance)` by host and folio.
2. **Partner-set overlap.** Mean unweighted Jaccard overlap over every pair of
   folios on which the source host occurs.
3. **Distribution divergence.** Mean pairwise Jensen-Shannon divergence in
   bits. Each folio distribution receives Jeffreys 1/2 smoothing over the
   source host's pooled target support.
4. **Target entropy.** Shannon entropy in bits of the pooled next-partner
   distribution, plus the unweighted mean empirical within-folio entropy.

The main overlap, divergence, and entropy summaries weight eligible hosts
equally. Held gain is summed over events and also reported as raw bits/event.
No metric is rescaled across corpora.

## Host-specific sampling null

For each host retain its exact pooled partner multiset and its exact number of
source events on every folio. In each of 256 deterministic worlds, shuffle the
partner labels and repartition them into the unchanged folio event counts.
This preserves frequency, partner frequency, host recurrence, number of
folios, and per-folio opportunity while destroying folio-specific pairing.

Report null means and observed-minus-null excess for overlap and Jensen-Shannon
divergence, plus inclusive lower-tail overlap and upper-tail divergence p-values.
The null is descriptive per host; no multiple-host confirmation claim is made.

## Scopes and power

Run `GLOBAL` for every system. Repeat unchanged within every register and,
where metadata exist, every section. A register/section scope is powered only
with at least three physical folios, twenty next events, and three eligible
hosts. Synthetic controls have register metadata but no manuscript-section
field; synthetic section scope is explicitly unavailable, not imputed.

A count-bin summary is powered for architectural placement only with at least
five eligible hosts in that system/bin. Report all smaller bins as capacity
rows but do not use them for diagnosis.

## Frozen diagnosis rules

For every powered bin form the closed min--max envelope of the three controls
for held bits/event, overlap excess, and divergence excess. Voynich values are
never used to define a bin, threshold, weight, or control range.

- `SAMPLING_FREQUENCY_SUFFICIENT`: at least three powered Voynich bins and, in
  every one, all three metrics lie inside their control envelopes.
- `REGISTER_MIXTURE_DOMINANT`: global held gain is negative; at least three
  powered Voynich register scopes exist; at least 75% have positive held
  bits/event; and aggregate within-register held gain is positive.
- `FOLIO_CONDITIONED_INSTABILITY_SUPPORTED`: global held gain is negative; at
  least three powered bins exist; at least 75% of them have held bits/event
  below the control minimum and either overlap excess below the control minimum
  or divergence excess above the control maximum; at least three powered
  register scopes exist and at least 75% remain negative.
- otherwise `MIXED_OR_UNRESOLVED`.

These statuses diagnose the frozen panel only. Section rows are an additional
mixture sensitivity and do not replace the preregistered register gate.

## Publication sequence and claim ceiling

First publish this method/design. Next publish the A/B2/factorial-B host rows,
bin summaries, register summaries, source-only validator, and exact hashes.
Only a later commit may apply the frozen code to Voynich. The result can locate
partner instability relative to three synthetic controls. It cannot establish
a new architecture, word, code, language, morphology, role, meaning, plaintext,
or translation. No f84r row or image may be accessed.
