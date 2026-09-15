# GDT969 independent validation review

**PASS.** The independent validator reconstructs all four eligible edition/frame
observations and exactly reproduces all 39,600 finite input/width consequences.
There are no local candidates, joint candidates or unvisited candidate triples.
Every target case fails at INPUT or HIGH, before the subsequent extraction,
remainder and proof fields are examined. The result is an exclusion of the fixed
writing contract in its adequate literal panel, not evidence that target text
expresses incorrect arithmetic or that square-root content generally is absent.

## Source, registration and independence

The validator checks all 28 bindings in PREREG_LOCK.json, including the fixed
programme source, runner, method, provenance and parent caches. The lock hash is
`7496d7aecf5c63e434ec873e6301f47483b7438cebd8895acc91901c621b1de0`.
The 9,900-row SOURCE_PROGRAMMES.tsv hash is
`e54af4eb80b58865311019557a1b08eae278416d50012db45f205f513043772d`.
The preserved metadata timing correction remains part of those bindings: the
preflight ran at 11:55:14 UTC, rather than the original manually estimated minute.

Source arithmetic and synthetic parser checks passed before public registration
commit `750f7d478`, confirmed at 12:08:59 UTC. Actual target reconstruction and
the full replay branch were implemented and executed after that confirmation.
The validator is deliberately outside the scientific preregistration lock; its
completed bytes and receipt are closure artifacts.

Neither the independent trace generator, parser, key merger nor target intake
imports the runner's implementation. Synthetic checks import the frozen runner
only to compare independently planted positive and negative examples; module
import does not run its target intake. This is an independent implementation of
the same contract, not an independent historical interpretation or holdout.

For every integer 100 through 9999, the validator obtains the root from an
independent square interval and checks the prescribed maximal trial digit
against all ten possibilities. It reconstructs all 22 numeric outputs and the
standalone CHECK, verifies exact remainder identity, non-strict remainder bound
and modulo-seven proof, and compares every printed source TSV cell. It also
checks the complete programme summary and all ten published examples. The
modern generated outputs remain distinct from historically printed fields.

## Finite parse and complete intake

For a fixed input and positive digit width, canonical decimal output lengths
uniquely determine every suffix cut. The bound
`min(len(numeric_group) - 1)` includes every feasible width because each numeric
group must retain a nonempty opcode and at least one digit. Requiring repeated
opcode identity, distinct opcodes, consistent digits and injective digit codes
therefore exhausts this fixed parse domain. The typed grammar permits opcode
prefix overlap and does not require a joint opcode/digit prefix code.

Unused digits have exactly the reported falling-factorial number of injective
completions among literal strings of the same width. They are not decoded or
assigned a preferred completion. A joint candidate requires the same width and
opcode map, compatible injective digit maps, three distinct inputs and three
distinct physical leaves. Each retained candidate would be re-encoded in full.

The validator independently rebuilds paragraph intervals from the six original
GDT915 caches, verifies the 179-selector scope and inherited eight GDT928 source
bindings, and applies the fixed start/end, consecutive-index, literal-group and
definite-seam rules. It checks the full metadata histograms, all 14 complete
23-group frame rows and every reported denominator against the frozen preflight.
It reconstructs the exact TARGET.json including all group strings and source
IDs. The four observations contain 92 checked source-group ID occurrences;
these are not 92 independent manuscript observations.

## Exhaustive actual consequences

All four records have width upper bound one. Each therefore has exactly 9,900
input/width cases. Every consequence TSV row was compared in order, including
its exact first contradiction reason and position.

| Edition | Complete frame | INPUT: prefix length | INPUT: digit inconsistency | HIGH: digit inconsistency |
|---|---|---:|---:|---:|
| ZL3b | f114v.23–f114v.25 | 0 | 4,716 | 5,184 |
| IT2a | f103v.12–f103v.13 | 9,900 | 0 | 0 |
| IT2a | f114v.23–f114v.25 | 0 | 4,716 | 5,184 |
| IT2a | f24v.6–f24v.11 | 0 | 4,716 | 5,184 |

The totals are 9,900 prefix-length and 29,700 digit-consistency contradictions;
24,048 cases stop at position one and 15,552 at position two. The f114v strings
are identical across ZL3b and IT2a; these transcriptions are not replication.
The exact candidate lists, result counters, panel statuses and empty joint
artifact reconcile. Since every local domain is empty, no actual joint search
is required to establish that no shared-key triple exists.

The fixed literal IT2a panel has three eligible leaves and is
FIXED_TRACE_MODEL_CONTRADICTED. ZL3b has one eligible leaf, whose local cases
also fail, but its panel status remains INSUFFICIENT_LITERAL_THREE_LEAF_CAPACITY.
RF1b supplies no complete eligible paragraphs and has the same capacity status.
Ten other complete 23-group frames remain transcription/segmentation unknown;
other lengths are outside the registered format. None of these distinctions
permits a broader exclusion of arithmetic, programmes or manuscript meaning.

## Controls and limitations

Twenty-nine synthetic checks cover 14 complete planted parses at widths one
and two, five mutations with matching first-failure certificates, two independent
domain guards, one complete shared-key triple, three incompatible-key cases,
one cross-record digit alias and three arithmetic countercases. The controls
retain the 960 equality case, the required post-sum reduction for 105, and an
864 counterexample where modulo agreement and a remainder bound hold despite
failure of exact identity. Full target arithmetic and positive joint execution
are not newly tested by the observed negative target result.

Before sealing, the root corrected timeout propagation through a capacity-limited
panel, counting of unvisited joint tuples, and the empty-width-domain shortcut.
The actual run exercised no runtime limit. The receipt explicitly labels deadline
execution paths NOT_EXERCISED; synthetics and source inspection do not establish
empirical completeness under an interrupted run.

Reproduce the source-only audit with
`python experiments/yolo/gdt969_fibonacci_generated_root_trace/src/validate.py --registration-only`.
Reproduce the complete audit with the same command without that option; this
writes artifacts/VALIDATION.json with deterministic counts and artifact hashes.
The receipt's claim ceiling is conditional source, code and result fidelity.
Confirmed words and independent meaning confirmation remain zero.
