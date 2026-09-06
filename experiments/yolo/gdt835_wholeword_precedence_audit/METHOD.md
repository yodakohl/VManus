# GDT835 method — necessary wholeword precedence

This is a retrospective diagnostic on the 48 already public GDT834 keys.
The analysis code and decision are registered before the new classifications.
Existing truth and the 21-correct/27-wrong outcome classes are known; procedural
staging is not a fresh blinded recovery experiment. There is no new key,
optimization, language score, candidate selection or repaired GDT834 outcome.

## New falsifier and prior scope

GDT834 found correct keys but selected a wrong map. Its decoder checks role
counts, positional domains and candidate injection, and then concatenates
outputs. The source generator inherits GDT832 `logical_encode_word`: whenever
a wholeword entry exists, it must be used before suffix or literal spelling.
That mandatory inverse condition is absent from GDT834 `Search::legal()`.
A high-scoring key can therefore belong to the relaxed fitted space without
belonging to the declared deterministic encoder family. This possibility has
not yet been counted when the present protocol is fixed.

Duplicate navigation returned learned-reader precedence routes such as GDT466,
whose ordered identity/function/family fallback is not this cipher-key inverse
test. GDT834's failed result and GDT616/CDA001 closures remain unchanged. No
Voynich data, new page admission or public decipherment search is involved.

## Invariant

For candidate key K, let D_K(c) concatenate the outputs of one observed cipher
word c, and let W_K(w) be the unique W carrier emitting plaintext word w.
The registered mandatory-wholeword-first encoder implies:

    if D_K(c) is in this candidate's W-output dictionary,
    then c must equal the singleton [W_K(D_K(c))].

Use the candidate's own entire dictionary, including inactive W carriers.
Never use the planted wholeword-value list, true key or a reference language
to decide compatibility. A composed spelling of a candidate W output violates
the invariant even if that W carrier is never itself observed. This is why
observed duplicate plaintext values alone are an insufficient test.

Report distinct ciphertext spellings with the same decoded word separately as
alias classes. Such aliases cannot both be canonical under a deterministic
encoder, but the primary gate here checks mandatory W precedence only. No
suffix precedence, suffix ordering or full inverse compatibility is asserted.
Optional abbreviation or homophonic encoders may allow both spellings and would
not be governed by this invariant. No such writing rule is established for
Voynich.

## Two executable stages

First, audit every distinct discovery ciphertext word type with its full token
multiplicity, for all 48 fixed restarts across three keys and TYPED/BLIND arms.
The gate reads only each candidate's packages and its discovery ciphertext.
Write all violations, expected singleton carriers and alias classes, including
zero-violation cases. GATE_LOCK binds the complete GATE artifact, SPEC and all
48 candidate hashes before the second stage. No candidate is removed or chosen.

Second, join the locked classifications to the previously published observed
truth maps and apply the identical invariant to all 48 held ciphertext views.
Recompute exact word/paragraph recovery as descriptive confirmation. Include
all four compatibility-by-truth cells, even if empty, and every world/arm cell.
The three encryption keys share a single historical content split. Repeated
key counts do not imply independent text samples or statistical significance.

## Decision

INVARIANT_FAILURE if any observed-truth-equivalent discovery key fails, or no
such true key exists. Otherwise RETROSPECTIVE_PRECEDENCE_SEPARATION_PASS requires:
all true observed maps pass discovery; every other map fails discovery; each
of the six world/arm cells contains at least one compatible key; and every
discovery-compatible key has zero held W violations and all held words exact.
Other outcomes are SEPARATION_NOT_CONFIRMED. No thresholds or candidate subsets
change after counts. Passing this retrospective separation does not repair
GDT834 or establish a new successful end-to-end decoder.

## Separate exploratory source context

Before the mechanical inverse test was selected, a source-only reviewer
examined all 42 actual discovery occurrences implicated in GDT834's errors.
SOURCE_CONTEXT.json preserves the exhaustive original-word/UD annotation joins,
head distances, reference coverage and construction differences. A raw extra
`ut` syntactic component belongs to a longer written multiword token and was
never the encrypted standalone word. This grammar census is exploratory,
pre-registration and does not choose or weight any gate condition. The proposed
likelihood decomposition and fresh Questio/Eclogue control remain unexecuted.
