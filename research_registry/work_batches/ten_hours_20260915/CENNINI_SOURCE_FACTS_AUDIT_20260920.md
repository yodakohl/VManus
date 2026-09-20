# Cennini source-facts draft audit

Status: independent source audit, not a freeze and not a target test. The root
draft and builder remain byte-untouched. Audited files:

* `CENNINI_SOURCE_FACTS_20260920.json` (root draft, SHA256
  `c357182815418f872840fd761712f173237058a5010f7ece394ad0a6ea0fe2c1`),
  231 records in 29 bins C01–C29.
* `CENNINI_PROCESS_PRODUCT_SOURCE_20260920.json` (complete 1821 main-text
  packet, SHA256
  `fec4fbf73be07c164e495e4bdefdcd528cd23e0e3a2071c787698999624241a5`).
* `CENNINI_COMPLETE_FINITE_SOURCE_ACCOUNT_20260920.json` for the existing
  normalized inventory and editorial uncertainty policy.

I checked every C01–C29 bin against Tambroni 1821, printed pages 147–151.
No bin is absent and the draft retains the full four-chapter span. The
following findings concern field ownership, referent precision, modality, or
scope; they do not require a new source account.

## Corrections before freeze

1. **C06 support relation.** `CARPET ON TABLE` / `CARPET ON BOARD` reverses
   the source relation. The model is placed on a carpet, on a table, or on a
   board. Encode one subject (`MODEL` or `WORKPIECE`) with an alternative
   support value (`CARPET`, `TABLE`, `BOARD`), preserving the source's
   alternative scope.

2. **C07 free edge and touch referent.** The text explicitly says the cloth
   edge being placed on the ring teeth is the edge “which is not sewn”; add
   that constraint if the five-field budget permits. `RING TOUCH MODEL` is
   over-specific: the printed `aspettante`/face referent is not securely
   resolved. Keep the no-contact restriction with an unresolved sitter/face
   referent rather than asserting `MODEL`.

3. **C10 anatomical relation.** `TUBES_BOTTOM_JOIN ALLOW_SPACE NASAL_SEPTUM`
   modernizes “the space from one nostril opening to the other.” Preserve the
   written relation as `SPACE_BETWEEN_NOSTRIL_OPENINGS`. The no-expansion rule
   is a property of the nose/nostril insertion, not an independent `INSERTION`
   patient; retain the operation but correct its typed subject or mark it as a
   normalization.

4. **C12 mixture versus dry batch.** The source says the gypsum sets quickly
   after it is put onto the water and made into a workable compound. F107's
   subject `GYPSUM` should be the wet compound (`MIXTURE1`/`CONFECTION1`), not
   the dry batch alone. Likewise F108–F109's “neither too fluid nor too stiff”
   constraints belong to the mixed compound, not `BATCH1` as a dry material.
   Keep `BATCH1_GYPSUM` for cooked/fresh/sifted gypsum and a separate wet
   mixture referent.

5. **C13 mouth/eyes modality.** “Have him keep the mouth and eyes closed” is
   an instruction to the worker about the model, with the no-force and sleep
   comparison retained. F116–F117 currently make `MODEL` the directive
   subject, which makes the model self-command. Use `WORKER` (or a declared
   instruction addressee) as directive subject and `MODEL` as patient; do not
   turn the sleeping comparison into an achieved state beyond the instruction.

6. **C14 setting strength.** “Lasciare riposare ... tanto sia appreso” supports
   a short rest until the compound has taken/set somewhat. `UNTIL SET` is
   stronger than the text. Use `PARTIALLY_SET`/`TAKEN` or retain the exact
   source phrase as an unresolved setting state.

7. **C17 two readings.** The transmitted 1821 passage about raising the model,
   holding the confection, and drawing the face from the mask is difficult;
   Tambroni's conjectural posture/hand reading must remain alongside the
   transmitted alternative. F148's single `WORKING_PARSE` is acceptable only
   if the metadata also owns both readings and does not let the working parse
   become a source fact. `MODEL_SELF` is not an additional actor: it aliases
   `MODEL`, who holds the tubes in C11.

8. **C19 band terminology.** `BABY_SWADDLING` is a convenient gloss for
   `fascia da putti`, but it should be marked as a lexical normalization or
   retained as `CHILD_BAND`; the source does not specify a modern swaddling
   construction. The persistent referent is still the preserved first form.

9. **C22 bench patient.** The form/confection is held on a bench while the
   second gypsum is put on it. F180's `WORKER HOLD_ON BENCH` makes the worker
   the object being held. Encode `FORM1`/`CONFECTION2` as the thing supported
   by `BENCH`, with the worker as the pouring actor if that role is retained.

10. **C23 fill relation.** F187 reverses the source relation. The gypsum is to
    enter every place in the form; `POURED2`/`MIXTURE2` should be the entering
    material and `EVERY_CAVITY` or equivalent the destination. Keep the wax-in-
    seal comparison, gentle other-hand tapping, and separate bubble/blister
    avoidance purposes.

11. **C24 filled-form identity.** `FILLED_MASK1` is not a source-named third
    object. The filled preserved form should remain `FORM1` (or a declared
    `FORM1_FILLED` state), while `MIXTURE2` is the material inside it. The
    half-day and maximum-one-day alternatives are correctly retained.

12. **C25 result identity.** `CAST2` is an invented label at this stage. The
    source says to break the outside crust of the first form while preserving
    the nose and all of the new representation. Keep `OUTER_SHELL = FIRST_FORM`
    and express the protected patient as the not-yet-named final representation
    or `EFFIGY`, without silently presupposing a cast object.

13. **C27 output and audience.** The source directly names the result `effigia`,
    `filosomia`, or `impronta`; F212–F216 should emit that final representation,
    not `CAST2` followed by names. “Of each great lord” scopes the claimed
    result/application; it does not assert that the selected `MODEL` has a
    `GREAT_LORD` property. F217 should therefore be a result scope or
    applicability record.

14. **C29 capability versus employment.** `Abbi pure maestri sofficienti` asks
    the instructor to have competent masters available. `WORKER EMPLOY
    FOUNDER_MASTERS` adds an employment relation absent from the text. Use
    `REQUIRE/ENSURE_AVAILABLE` and retain skill in melting and casting. Keep
    `WORKER`, `MODEL`, and `SPEAKER` as typed construction roles, not as a
    claim that the source names three persons; the direct instructional
    addressee is a model convention.

## Confirmed scope and edition handling

* C15 is correctly represented as a condition on the first mixture's water:
  high-status examples receive warm rose water; others may use warm fountain,
  well, or river water. It is not a second-fill event.
* C16's dry/set gate, C18 preservation, C19–C24 refill and rest, and C25 shell
  destruction preserve the intended first-form continuity, subject to the
  referent correction above.
* C26's current purpose reading agrees with the 1859 CLXXXIV wording (“to make
  the form weaker/easier to break”), while the 1821 wording permits a
  conditional reading. The draft should retain both as edition alternatives;
  the common content is exterior preweakening before filling, never sawing
  through. The checked 1859 chapter is
  https://it.wikisource.org/wiki/Il_libro_dell%27arte/Capitolo_CLXXXIV.
* C28 correctly keeps the later metal-casting antecedent unresolved and lists
  the source's metal alternatives. It must not use the 1821 editorial headings
  as medieval exact-form evidence.

These are source-facts corrections, not target meaning claims. No target,
reserve, image, root draft, builder, route, ledger, or RAW441/442 file was
modified. No additional raw proposal was warranted because the two existing
writer cards already cover the requested delta and typed-operator alternatives.

## Root adjudication before freeze,19:52UTC

The audit concerns the earlier231record hash, while root had separately added
five source details before receiving it. Its conclusions are not automatically
accepted as manuscript facts or source contradictions.

Adopted: explicit unsewn edge; source-level flesh-between-nostrils expression;
quick setting attached to mixed BATCH1; explicit worker-causes-model-closing
record; sufficient-setting wording; neutral child-band term; unambiguous worker/
mold/bench and simultaneity records; explicit all-cavities destination; rest the
same MASK1; source's each-great-lord applicability; ensure masters available.
BATCH1is explicitly defined as a mixed batch, with BATCH1_GYPSUM its ingredient.
The previous code did not assert that BATCH1was dry. Likewise an event's PATIENT
link was not a reversed material flow, but the new explicit destination is clearer.

Retained with caveats: C06carpet-on-table/board is a plausible layering of the
printed support phrase, not a reversed edge; the three-alternative support
reading is retained in uncertainty metadata. C07aspettante is treated as the
sitter, consistent with the ring held clear of the face; no independent new body
part is inferred. C17uses the explicitly disclosed supporting-hands working parse;
the original1821wording and editorial1859clarification remain linked, not replaced.

CAST2is an analytic identifier for the second representation, not an extra object
inserted into the source. Its existence is inferred from second filling and the
instruction to break the first outer form without damaging the representation.
Replacing its identifier with EFFIGY would only rename a shared code variable.
Retain MASK1distinctfromCAST2, and retain the later first-form antecedent unresolved.
C26purpose-to-weaken is the selected reading;1821's typography does not establish
the draftv1's invented 'if difficult to break' condition. No target was consulted.
