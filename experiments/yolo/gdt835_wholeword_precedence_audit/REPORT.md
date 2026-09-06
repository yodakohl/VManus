# GDT835 — an omitted encoder constraint separates the frozen key classes

Status: **RETROSPECTIVE_PRECEDENCE_SEPARATION_PASS**.

A necessary rule of the declared control encoder rejects all 27 wrong GDT834
candidates and accepts all 21 candidates with the correct observed key. This
refines the previous selection diagnosis: GDT834's language objective preferred
wrong candidates inside a fitted space that omitted mandatory wholeword
precedence. Those candidates cannot generate the observed ciphertext under
that declared writing rule. The language score comparison remains numerically
correct; it was not restricted to the intended deterministic encoder family.

This is a retrospective diagnosis on already exposed keys and text. No new
key was fitted or selected, no language score was computed, and GDT834 remains
**BASELINE_RECOVERY_FAIL**. A fresh test of an integrated constraint has not
been performed.

## The independent condition

The control generator writes a word with its W carrier whenever one is
assigned, before considering suffix or literal spelling. For each candidate,
the gate builds that candidate's own W-output dictionary, including inactive
W slots. If a decoded complete word belongs to this dictionary, its source
cipher word must be exactly the corresponding singleton W carrier.

The gate uses neither the planted word deck nor a reference language, known
plaintext or held material. GDT834 `Search::legal()` checked role counts,
positions and injection but omitted this condition; `logical_encode_word`
in the inherited source generator mandates it. A zero-violation result tests
this necessary condition only, not complete suffix or inverse correctness.

## Exact contradiction

Every wrong candidate reads both an opaque W carrier and a three-literal
cipher word as `cum`. The latter spelling contradicts the mandatory W entry:

| Candidate's `cum` spelling | Discovery occurrences | Held occurrences |
|---|---:|---:|
| Singleton wholeword carrier | 17 | 109 |
| Three literal carriers | 15 | 44 |

For the representative world83401 BLIND start2, these are `[X22]` and
`[X28,X02,X27]`. Other keys have independently shuffled IDs and the same
content. All 48 candidates were audited; the example did not define the gate.

The 15/44 composed occurrences are correctly decoded plaintext words under
GDT834's metric. They expose the incompatible W assignment elsewhere. They
are therefore different counts from GDT834's 42 discovery /168 held wrong
plaintext words (`ut→quod`, `quod→cum`). Each wrong candidate has exactly one
violating ciphertext type and one decoded alias class. Every correct candidate
has zero W violations and no observed plaintext alias class in either split.

## Complete frozen-panel result

| Observed key class, joined after gate lock | Discovery gate passes | Discovery gate fails |
|---|---:|---:|
| Correct observed role/value map | 21 | 0 |
| Other observed map | 0 | 27 |

Every world/arm cell contains a compatible candidate. All 21 discovery-compatible
candidates also have zero held violations and exactly 6,511/6,511 held words
and 172/172 held paragraphs. The 27 incompatible candidates each retain their
44 held violations. No surviving candidate is substituted for GDT834's
registered selections. Three source-independent encryption keys share one
historical contentsplit; this is not 48 independent texts or a population
accuracy estimate.

Public analysis registration `a71f0f2b` was pushed before the new compatibility
classifications. All 48 discovery decisions were then written and locked before
the evaluator joined public truth and interpreted held ciphertext. Gate-only
independent validation passed before that confirmation stage.
GATE_LOCK SHA-256:
`82a9fcc40773aa860d5c78aaac821013bcdf8226a02cadae1e45bb28012d7f6d`.

Ten invented-fixture tests pass, including inactive W values, order, token
multiplicity, aliases and executable discovery-stage isolation. Independent
validation and exact replay reconstruct all 48 discovery gates across 152,640
candidate-word occurrences and all 48 held confirmations across 312,528
candidate-word occurrences, including the complete truth/compatibility cross-tab.
The old GDT834 fit and primary artifact hashes remain unchanged.

## Separate source exploration and implications

An earlier exhaustive source-only census of the 42 erroneous discovery word
occurrences found annotated heads beyond immediate neighbors in35/42 cases,
but literal reference coverage for only9/38 finite-anchor occurrences. The
reference/control distribution of `ut` constructions also differs. A raw extra
`ut` annotation was a component of a longer written multiword token, not a
26th encrypted occurrence. These exploratory annotations supplied no gate
condition, score or threshold. SOURCE_CONTEXT.json retains the exact joins.
No grammar scorer, likelihood decomposition or fresh Questio/Eclogue control
was run from that exploration.

The concrete next implementation question is enforcement of this already
specified forward-writing constraint during inference, followed by a genuinely
fresh control. The present separation is not such an integrated search test.
Mandatory W priority is a property of this synthetic control architecture;
optional abbreviation or homophonic writing may permit both spellings. No
corresponding rule, language or translated word has been established for the
Voynich manuscript. GDT616/CDA001 remain closed; no target fit is selected.

Source, protocol, validators and compact artifacts are published. Exact staged
privacy/scope and GDT835 binding checks pass. The separate full repository audit
retains unrelated GDT600 binding and index debt; it is not reported as cleared.
