# GDT965 — complete Geniza fruit records under one literal grapheme code

This file and SOURCE.json are the authoritative fixed exploratory contract.
Source selection is exposed exploration, not independent source identification.

## Complete source

PGP40129, T-S Ar.43.225, Avetisyan2022 transcription: PEACH recto5 to recto13
before pomegranate; POMEGRANATE recto13 through verso5 before quince (including
Hippocrates); QUINCE verso5 through verso14. All three named head-bounded entries
are included. Apricot begins before the leaf and apple continues after it;
neither is a complete additional record. Full fragment transcription remains
in SOURCE.json. English translation is selective and is not compiled.

The source includes fruit/part, property, preparation, recipient and outcome
relations; notably eating quince before versus after food has contrary effects.
The exact entire printed source, not selected relation words, must be encoded.
Use SOURCE.json grapheme_words flattened in original order. Each unit is an
NFD base plus all attached combining marks; Hebrew final forms remain distinct.
Omit only printed periods/semicolons and whitespace. No mark interpretation,
restoration, phonetic normalization or freely substituted synonym. These are
edition-level units, not certified historical graphemes. The witness date is
only post-tenth-century in the catalogue; pre1420 copying is not established.
Three entries from one leaf are not three independent historical witnesses.

## Hypothesis and all target cases

One nonempty injective prefix-free string code for all source units maps the
three entire source streams onto three complete admitted Herbal P-kind prose
pages on different physical leaves. No source word must align to an EVA group;
source word offsets are retained for any conditional full-text alignment.

Reuse all357 GDT963 TARGET_FRAMES.json.gz entries,119 per alternate reading.
They were built from the six admitted GDT915 caches: section H,kind P,page!=f1r,
all P-kind groups in source-row order. The published eligibility reasons and
literal concatenation are unchanged. Unknown groups/seams retain the whole
page as UNKNOWN_SOURCE, never a semantic contradiction. Every page/source-role
case is reported (1071 total). Source roles may choose any eligible page.
Three readings are alternate descriptions of one manuscript. No winner is
chosen from edition agreement or disagreement. No new image, admission,
reserve or contact; f84/f84r remain forbidden and f116v unadmitted.

## Consequences and exact search

Before target filtering, freeze source counts and all required consequences.
For every literal source/page case, report four necessary conditions:
1. target length >= source unit count;
2. target first-character multiplicity >= multiplicity of the first source unit;
3. target last-character multiplicity >= multiplicity of the last source unit;
4. if the first and last source unit are identical, target has a nonempty
prefix equal to its suffix, with length at most
floor((target_length - (source_length - unit_frequency))/unit_frequency).
A repeated unit always emits its same nonempty codeword, so these follow even
without prefix freedom. Retain all four observations, not only the first failure.

For a case passing these, reuse GDT900 extend_word/compatible without changes,
passing the complete source stream and complete target string. Stop at the first
verified code witness or after exhaustive failure; each local case has2 seconds
and8 processes may run. Timeout is UNKNOWN_COMPUTATION. No inferred code length
cap, prefix repair or omitted residual. Exact concatenation and prefix freedom
are independently checked on every witness.

If one source role has no possible literal page and no source-unknown frame,
the full edition conjunction is contradicted. Independently, fewer than three
literal physical leaves is NO_LITERAL_CAPACITY; source-unknown pages remain
potentially undecided and cannot be erased. If every role retains non-excluded
literal pages and at least three leaves, search their complete joint assignment
using the same GDT900 enumerator with shared code, distinct leaves and a120-second
per-edition deadline. Source order for search is increasing candidate count,
then source ID; page order is frame ID. Stop after two distinct joint witnesses,
which establishes ambiguity; one witness at deadline does not establish uniqueness.
No solution after exhaustive literal enumeration proves only the literal panel
conjunction. Any source-unknown frame prevents a whole-manuscript exclusion.

Report every candidate's source/page expectation, observed counts, contradiction
certificate or code/timeout, joint projections, equivalent observed predictions,
and remaining ambiguity. Conditional code witnesses may project source meanings
onto character spans but are not source/language identification or confirmed
plant names. Independent confirmation capacity0. No significance claim without
a search-wide control; no GDT388 score-ready relation claim. The old experiments,
including888/913,900, and963, are unchanged.
