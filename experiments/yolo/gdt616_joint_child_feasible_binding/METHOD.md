# GDT616 method

## Question

Can the fixed GDT608/GDT614 inventory jointly choose a same-role primitive
binding, all eight actual paid merge locations and cards, and a complete
TRAIN-only world while exposing every merge's unoverridden recursive child
span, and can three such committed worlds pass held, oracle, and recovery?

## Inputs

GDT608 supplies the directed 98-unit/64-merge DAG. GDT614 supplies the V2
grammar, 34 roles/output cards, four short and four macro paid cards, exact
macro side licenses, qok restriction, 21 transitions, and downstream gates.
GDT615 supplies the frozen 28,101-entry TRAIN substring relation, partition
hashes/access order, and the terminal failure showing why a relaxed mapping
must not be committed before paid-child feasibility. Exact hashes are in
`artifacts/REGISTERED_SEARCH.json`; the GDT615 selected mapping is excluded.

## Method

Stage A is an exact TRAIN-only necessary bound. `X` is a same-role card
bijection and `Z` assigns every one of the eight paid cards exactly once to
eight distinct merges. Recursively, `child=effective(left)+effective(right)`
and `effective=paid output` at paid nodes or `child` at defaults. Every
merge's child and effective render must be registered TRAIN substrings, every
paid output must differ from its child, and rank-7 `qok` cannot be paid macro.
Stage-A SAT freezes nothing and only opens Stage B over the complete feasible
space.

Stage B jointly selects `X`, `Z`, and full W0 ordered traces/98-unit tilings.
It enforces the exact V2 grammar, macro hosts, collisions, 21 transitions,
paid-child/default labelling, exposure/null/focal thresholds, and all train
gates. The hierarchy maximizes minimum 42-card type exposure, then minimum
paid-card occurrence and total labelled merge occurrences, then minimizes the
primitive card sequence, paid assignment tuple, and canonical trace bytes.
Raw support is never scored.

Two seeded equal-role/equal-length contrast worlds must pass the same TRAIN
contract. Only the hash-committed three-world bundle opens held; only a held
pass opens `lm_confirm`, oracle scoring, and blind recovery. No post-commit
retuning is allowed.

## Decision rule and claim ceiling

Exact Stage-A UNSAT rejects the joint child-feasible binding family. Exact
Stage-B UNSAT rejects a complete W0; failure of the two bounded seeded worlds
stops the generator. Timeout, `unknown`, or incomplete optimality is
`SEARCH_INCOMPLETE`, never a pass. Later outcomes retain the inherited held,
oracle, and recovery meanings listed in `PREREGISTRATION.md`.

GDT616 tests a synthetic generator only. It uses no Voynich target and assigns
no Voynich sound, word, language, plaintext, object, operation, or meaning;
f84/f84r are forbidden.
