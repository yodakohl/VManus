# GDT1386: fixed transfer is formally compatible, meanings remain unselected

The unchanged R771 constructor accepts the complete f75r.32–46 scope in all
six predeclared reader/phase combinations, with **zero parser errors**. This
answers the registered portability question. It does not select a language,
word meaning, reader, phrase direction or authorial construction rule.

The model and exact target were public in commit `99ae396ea` before this work.
The wrapper, independent checker, specification and input hashes were locked
locally at 22:53:01 UTC on 15 October 2026, before their first target run.
This is an exposed comparison on the opposite side of the same physical
folio as the development paragraph; independent confirmation leaves: **0**.
The old f75r.33 example informed selection. No reserved source was opened.

## Complete result and capacity

| Reader | Raw groups | Exact types reused from its development reading | Positions with reused types | New opaque types | Frames in either phase |
|---|---:|---:|---:|---:|---:|
| IT2a | 120 | 21 / 68 | 62 / 120 | 47 | 3 |
| ZL3b | 122 | 18 / 68 | 59 / 122 | 50 | 1 |
| RF1b | 121 | 17 / 75 | 47 / 121 | 58 | 2 |

IT and ZL mark this entire paragraph with their own start/end flags; RF supplies
the corresponding 15-line window without those flags. The 363 reader groups
are alternative transcriptions, not independent observations. Applying two
phases reuses them again. Both phases pass for every reader; there is no
success-only selection.

No reader contains an exact standalone `tol` or `daiin` here. Their universal
binding and explicit membership rules therefore receive no positive transfer
evidence from this paragraph. IT contains two exact `qokar`, RF one, ZL none.
Only POST-IT uses one finite local split construction, `qol chedy` at .33.
The PRE version instead predicates B and P of the current variable. In ZL and
RF the two phases give the same frames and bodies on this source.

The spellings that cause those differences remain literal. ZL `.32 qotar`
and `.35 qoka[in:r]` are not changed into QOKAR. RF `.33 ched@222;` and
`.32 she@152;y` remain unclassified whole forms. Source flags are retained;
no whitespace, annotation, word or scope repair was made.

## What the longer reading actually says

These are unknown symbolic predicates, **not translations**. Each `N_word`
stands for one unassigned predicate with that exact raw spelling. A/B/P/Q and
the operator functions remain assumptions inherited from the frozen model.

POST-IT has this complete structure, with its full source and every individual
predication retained in [RESULT.json](artifacts/RESULT.json):

1. An assumed initial object x1 has the seven predicates written before
   `.32 qokar`: N_polshy, N_dal, Q, N_qokain, N_das, N_chsdy, Q.
2. `.32 qokar shedy` introduces x2 satisfying Q. Its body has 23 terms. One is
   the local assertion that some object z satisfies B and P (`qol chedy`);
   it does not make z the current object. The other terms apply to x2.
3. `.35 qokar ol` introduces x3 satisfying A. All remaining 85 terms apply to
   x3, through the paragraph end. No extra line boundary resets this scope.

The three top-level existential assertions are conjoined. Different variable
names do not assert different real objects. PRE-IT changes the second body's
local B/P existential into two current-object predicates and has 24 body terms.
The third body is unchanged.

ZL reduces the whole paragraph to 122 predicates of its assumed initial x1.
RF opens a second existential at `.32 qokar she@152;y`, with an unassigned
restriction; its second body has 112 terms. These are complete conditional
accounts, with markedly different structure despite all being accepted.

One manually inspected source line makes the limitation visible:

```text
IT2a f75r.38: qokeedy qokeedy qokedy qokedy qokeedy ldy
```

Under the unchanged current-object rule, this says N_qokeedy(x3) three times,
N_qokedy(x3) twice and N_ldy(x3) once. All six written positions are preserved,
but repeated predicates add no truth condition. This is the already recorded
repetition limitation in a concrete transfer passage, not a new discovery
that manuscript repetitions are meaningless. Distinct predicates also need
not denote distinct classes.

The freedom is structural: with one domain element belonging to every
predicate, every output here is satisfied. This follows from the positive
formulas; it is not a new toy-world score or a native truth observation.
Other interpretations can distinguish the formulas. Mere existence of a
satisfying interpretation cannot favor one of them. The model currently
provides no explanation for the order or multiplicity of these predicates.

## Decision and next work

Retain **ALL_CASES_FORMALLY_COMPATIBLE_NO_MEANING_SELECTION**. The exact grammar
was not contradicted in this scope. Its broad default absorbs 47/50/58 new
whole-form predicates; this is not 155 newly understood words, nor a passed
independent semantic gate. Confirmed words remain **0**.

Do not start another paragraph-coverage loop. The next bounded synthesis
question belongs in the existing R771 dossier: does the final `olchedy` in
f75v reuse a class specification, or require reference to a previously
introduced object? Compare the actual complete R771 frames and the identity
condition such a reference would add. A comparison must retain the rest of
the paragraph and every reader; RF's annotated final form remains opaque.
It must not silently promote a Class to an individual or invent an extra
USE operator. This is a proposed explanatory comparison, not a selected
meaning or a registered new test.

IDEA842 contains a broader, still unreviewed specification/instance/result
proposal; its recipe, batch and location vocabulary is not adopted here.
IDEA895 already constructed a different partial TOKEN/PATTERN account and
found no bound restrictive consumer. Its USE(b)/USE(c1) contrast is not new
work and does not establish the required identity. Before implementing any
continuation, inspect those prior requirements and identify an actual written
restriction in the full current passage. If none is available, retain the
unresolved alternatives without building another interpreter or repeating
the missing-input audit. Existing failures, including GDT1047 and R_TOKEN,
remain binding.

## Reproduction and limits

Run the two commands in [experiment.json](experiment.json). The wrapper imports
only the byte-frozen original parser. The separately authored checker imports
neither it nor the wrapper and reconstructs the exact source projection,
grammar, errors, reuse counts and six decisions. Its result is
[PASS](artifacts/VALIDATION.json) for source and implementation correctness,
not blind semantic confirmation. No target toy truth scores were run.

The primary's historical asymmetry was recorded before execution: binders
consume the next raw group without a definite-gap gate; split pairs and
C DAIIN require a definite internal seam. The old development validator's
stronger binder-gap assertion is not added as a new scientific gate here.
All original files remain unchanged.

References: [fixed method](METHOD.md), [input and decision specification](src/SPEC.json),
[implementation lock](CODE_LOCK.json), [source projection](artifacts/SOURCE.json),
[original R771 assessment](../../../research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/R771_WITNESS_REVIEW_20261016.json).
