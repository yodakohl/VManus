# Source-rule acquisition protocol, 4 October 2026

Exploratory source description, accepted by the user. This is not a new GDT
experiment, key search, independent confirmation, or Voynich reading. The parent
NEXT_MEANING_TASK_STRATEGIC_REVIEW.md records selection, predecessors, decision
consequences and assumptions. Some source examples, including nonlocal
`sequitur`, were inspected before writing this protocol. No blind claim.

## Fixed descriptive question

What finite **ordered local relation** does the existing character declaration
actually supply, and which complete editorial groups does that relation fail
to express? This relation is a deliberately minimal part of a writer, not an
assertion that the historical writer was local. Its failure does not refute
historical abbreviation. No fitting, word vocabulary, probability threshold,
or adaptive rule insertion is used.

Read only the six original CoReMA TEI sources and two declarations pinned in
GDT1166/src/SOURCE.json. Preserve them. Source leaf numbers do not refer to
Voynich leaves. No Voynich input or image is read. TEI source texts are supplied
by CoReMA, University of Graz (editors identified in the originals), CC BY 4.0.

## Relation fixed before complete enumeration

For each consistent declared Unicode graphic class, union **all** normalized
strings in the character declaration, not just the alternatives observed in
the six texts. Strip declaration formatting whitespace only. Keep multi-letter
and whole-expression strings. Empty normalized mappings mean only an empty
editorial rendering; they do not license arbitrary restorations. Ordinary
ASCII characters have their literal identity as an additional alternative.
Other undeclared literal characters retain their identity. Conflicting or
missing glyph declarations remain UNKNOWN; never infer values from IDs.

Apply each permitted string at its character's position, in written order.
Membership of the full expansion is computed without using `ex` positions,
abbreviation boundaries or value-bearing glyph IDs. It has no language model,
word list, lexical override, case folding, spelling repair, or free insertion.
Declared mappings are supplied values: success is source reconstruction, not
unknown-key recovery. Unicode classes are editorial renderings, not certified
native allographs; the editorial guideline explicitly permits substitutes.

## Whole-group projection

Walk body elements in document order. Whitespace and line/page/column changes
separate groups outside editor-supplied `w`; `w` joins them. Top-level recipe
segments and `ab` elements delimit records. `abbr` and `am` never create word
boundaries. The written stream drops `ex` and unwraps `am`; the expanded stream
retains `ex` and drops `am`. Outside `am`, use the original referenced glyph's
normalization only for the reference expansion. Retain literal case and all
written hyphen signs. This is the edition's normalization, not modern German.

Use final-state deletion omission and retain readable additions in XML order;
mark revisions. Exclude modern notes, pointers and transposition instructions.
Unclear/supplied/expanded-only/gap/metamark/choice spans and undeclared or
conflicting glyphs produce explicit UNKNOWN obligations. Keep source XML
ordinals and page/line locators. Conserve every body abbreviation as either
represented in a complete group or explicitly excluded by an ancestor policy.
Empty containers (including those whose entire content was deleted) are
counted separately as `empty_final_state_container`; never count them as words.
The deliverable retains all groups containing `abbr`, `ex`, `am`, or a declared
abbreviation sign; count other groups separately. Source rules also cover
ordinary allographs and diacritics used in those complete groups.

## Description and checks

Report represented, unresolved and incompatible obligations separately for
each book. Complete-group failures stay failures. Save all groups and every
failure, with all declared alternatives and original source locators. Inspect
the full mismatch list; never add a rule to improve these counts. An
independent membership implementation checks every known row. XML source pins,
raw abbreviation conservation and deterministic replay must also pass.

Separately describe explicit script-description conditions, whether their
required distinctions are retained in the transcription, and counterexamples
to compulsory shortening (same exact expanded group has both abbreviated and
unabbreviated realizations in the same witness). These pairs demonstrate
optional occurrence, not randomness or identical scribal contexts. Observed
positions are not promoted to universal licensing rules. No counts supply
statistical significance or a decipherment percentage.

## Decision

A complete writer would need externally justified nonlocal and contextual
rules, plus evidence of when abbreviation is compulsory or optional. If those
are missing, publish the useful finite partial relation and precise missing
conditions, then stop; do not launch a decoder or repair GDT1166. No automatic
new control corpus. The user revoked the previous 45-minute cap; completion is
bounded by this source deliverable rather than a replacement timer.

Preparation note: the first build stopped at abbreviation conservation before
producing counts. It exposed empty containers and containers enclosing only
deleted text. The explicit empty-final-state accounting above was added before
the first successful enumeration; no writing relation was altered.
The first enumeration then exposed two projection defects before validation:
tail text needed the preceding child's final locator rather than the parent's
opening locator, and `brevigraph` entries without `n="abbr"` were being missed
by the sign-selection flag (including the stroked-j half-unit). Both were
corrected. Identical half-unit signs are not optional full/short spelling pairs.
