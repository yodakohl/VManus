# Constructive Judaeo-Arabic model: independent architecture critique

2026-09-15. Bounded source/architecture review; no target paragraphs inspected
and no decoder implemented. This note changes no experiment or registered result.

## Decision

**The concrete grapheme-code variant is a legitimate restricted construction
hypothesis. It need not reduce to arbitrary singleton gloss assignment.** Use
the 32 exact source grapheme units, the finite attested surface-word inventory,
one shared injective prefix-free code, complete target groups corresponding to
complete source words, and a frozen language of complete source-derived clauses.
Every hypothetical word then has a fixed spelling whose repeated graphemes
constrain other words, including words occurring only once.

A finite product of source clause templates is acceptable. Describe it as a
restricted source-derived paragraph language, not a general grammar of Arabic.
It can yield an explicit, plausible *hypothetical* paragraph if its lexical
senses, argument relations and discourse references are also coherent. No
confirmed Voynich anchor is required to construct or falsify that hypothesis.
Such a witness would establish conditional representability, not identify the
source language, fruit, manuscript topic or historical code.

## What predecessors do and do not settle

[GDT905 METHOD](../../gdt905_joint_cv_complete_passage_candidates/METHOD.md)
already distinguishes constructive paragraphs from copied source passages and
requires a global component code, complete lexical analyses and full grammar
acceptance. Its [REPORT](../../gdt905_joint_cv_complete_passage_candidates/REPORT.md)
records two whole-paragraph lexical keys, both rejected by its grammar. All 49
full searches remained UNKNOWN. This is a retained counterexample to treating
dictionary words as a coherent reading; it is not a general impossibility result.
Those two keys also differed and concerned the same physical leaf.

[GDT193](../../../../GDT193_COMPILER_STRIPPED_CONSONANTAL_REPORT.md) and
[GDT194](../../../../GDT194_CONSONANTAL_HOMOPHONY_REPORT.md) rejected their static
consonantal mappings for six particular Latin-script language packs. Neither
tested this Judaeo-Arabic inventory, this grammar or a nonempty string code over
its preserved graphemes. They supply no license to delete Hebrew combining
marks, normalize final forms, or claim consonantal writing has been refuted.

[GDT965](../../gdt965_genizah_complete_record_grapheme_code/REPORT.md)
retains its exact complete-record result. The new proposal relaxes the fixed
plaintext requirement but adds a word-boundary requirement and a construction
grammar. The full models therefore differ in more than paragraph length and
are not simply the same test rerun. Nevertheless, they are related hypotheses:
call this an exposed, explicitly changed generative model. A success would not
rescue GDT965's failed exact-record claim. Do not progressively expand the
grammar, source inventory or alignment exceptions after inspecting failures.

## Actual degrees of freedom

Independent counts from GDT965's frozen SOURCE.json: **241 tokens, 157 surface
word types, 117 types occurring once, 135 types appearing in only one of the
three records, and 22 types shared by at least two records.** All forms use 32
distinct preserved grapheme units. Root's approximate inventory of 140 should
therefore be corrected to 157 if all three records' attested forms are used.

An atomic word-code model would permit many unconstrained assignments. For T
distinct target group types, even an injective assignment has an upper bound
of `(157)_T` lexical assignments before grammar and equality restrictions;
same-category lexical permutations can preserve every shallow grammar feature.
Making each singleton root a separate encoded morpheme recreates much of this
freedom. It would not fit every possible paragraph automatically, but a neat
reading could mainly reflect how meanings were attached to unique strings.

The proposed grapheme variant avoids a separate code parameter for every root.
Its free parameters are the shared code strings, choices among attested lexical
forms/complete analyses, licensed template substitutions, and paragraph parses.
These are still substantial: a raw N-position vocabulary product has `157^N`
assignments before constraints. A grammar must remove real combinations rather
than just relabel them. Report equivalent keys, lexical permutations and
unobserved code values; do not collapse their ambiguity into a preferred story.

## Minimum source-bound specification

1. **Freeze the exact inventory.** Use the 157 surface forms from the three
   complete records, retaining every final shape and mark. Do not add apricot
   continuation, apple or margin forms through the construction note. Link
   each complete word analysis and source sense to actual occurrences. Permit
   ambiguous analyses as linked alternatives, not independent products of
   convenient lemma, gender, role and sense labels. Marked and unmarked
   spellings remain distinct even when assigned a common lexical interpretation.
2. **Keep encoding below the lexical root.** Encode source grapheme clusters
   with one nonempty injective prefix-free string code. Source morpheme analyses
   constrain the grammar; they are not freely assigned new ciphertext strings.
   Keep one source surface word per target group as an explicit hypothesis,
   justified for testing by the known hierarchy at spaces, not as an established
   identification of manuscript words. No token deletion, vowel restoration,
   local code values or per-word escape units.
3. **Freeze complete clause templates and substitutions.** Annotate complete
   attested clauses, not just adjacent noun pairs. Give each slot a finite list
   of source-attested forms and complete compatible analyses. Substitution may
   vary typed arguments and properties only under the bindings below. At the
   12–24-group bound the generated language is finite; accepting arbitrary
   concatenations of isolated phrases would weaken the intended test.
4. **Define a complete paragraph derivation.** Every word belongs to a complete
   clause. Keep subject/topic continuity, conditional dependencies and pronoun
   antecedents explicit. Require at least two linked clauses for the proposed
   paragraph model; use exact declared clause-count bounds rather than a new
   exception whenever a target length fails. A named heading need not be
   mandatory in every paragraph unless that is explicitly part of the hypothesis.
5. **Require codebook completion.** A paragraph may omit some of the 32 units.
   GDT900 returns an observed partial key. Check whether that key can extend to
   all 32 units over a target alphabet declared for the whole model, not inferred
   from that paragraph. A prefix-free partial key can already exhaust the code
   tree. With unbounded finite lengths, an available trie branch can accommodate
   finitely many additional words; a complete occupied tree cannot. Display any
   unobserved completion as arbitrary, as GDT905 does.

## Bindings needed for coherent clauses

| Feature | Necessary binding in the small model | What must not be allowed |
| --- | --- | --- |
| Nominal roles | Separate fruit, part/product, organ, person, quality and preparation/event slots using the source analyses. | Every noun substituted into every noun position. |
| Attributive agreement | Bind noun and adjective analyses jointly, including the attested definite marking and written inflection. | Independently choosing a convenient modifier ending or deleting an article to obtain a match. |
| Bare predicates | Separate named-subject plus unprefixed-property clauses from article-bearing attributive NPs. | Treating the two constructions as interchangeable token lists. |
| Idafa | Bind the possessed head to its complement and the modifier to the appropriate embedded noun. | Inferring possession from every unprefixed word followed by a definite noun. |
| Verb/event frame | Preserve valency, argument roles and finite/predicative analysis, with a licensed subject or inherited topic. | Moving a verb into an adjective or noun slot because its spelling fits. |
| Condition and outcome | Keep condition branches tied to their licensed effects; quince before/after food and constricting/softening effects are a concrete paired dependency. | Independently swapping condition, preparation and outcome words. |
| Possession/reference | Bind a suffixed form to an antecedent of the appropriate source-supported analysis within the declared discourse model. | Accepting a dangling “her” merely because the noun-plus-suffix form is in the lexicon. |
| Paragraph continuity | Carry the same fruit, patient or preparation through linked clauses unless an explicit template introduces a new referent. | Concatenating unrelated individually grammatical source clauses and calling their sequence one explanation. |

The corrected [construction note](../../../../research_registry/work_batches/ten_hours_20260915/PGP40129_CONSTRUCTION_SOURCE.md) supports
several of these restrictions, but it does not itself supply a complete finite
grammar. In particular, recto 17 `עקל אלטביעה` must not be an idafa example;
its corrected verb–object analysis belongs in the event inventory. The repeated
`פם מעדתהא` licenses an attested possession construction, not a productive
suffix paradigm over every noun. Preserve the observed distinction between
free `מעדה` and suffixed `מעדתהא`; do not declare the entire final written
sequence an invariant suffix without analysing the noun's bound form. Apple
and margin comparisons cannot enlarge the three-record grammar silently.

If the source packet cannot justify an inflectional substitution, either keep
that template slot lexically fixed or record the proposed generalization as a
new, explicit language assumption before testing. Source-derived templates can
support useful recombination without claiming that their small set exhausts
Arabic syntax or medieval medical reasoning.

## Smallest adequate test and decision consequences

First make a small **source-only grammar preflight**: the selected complete
source clauses must receive their intended full analyses; a few deliberately
crossed role, reference, article and condition/outcome combinations must fail
for the declared model reasons. These are checks of the restricted model,
not claims that every rejected string is impossible Arabic. Publish each
template, permitted substitution set and complete sense/role dependency.

Then reuse the entire fixed GDT905 12–24-group whole-paragraph panel without
choosing promising pages by appearance. Treat its readings as alternatives of
one manuscript. Enumerate shared observed grapheme keys and complete grammar
derivations within a declared budget. GDT900's unchanged string enumerator can
serve the exact code-equation step; it is not by itself an efficient grammar
and lexicon search strategy. Do not launch the raw vocabulary product.

For every witness, publish the whole source-script paragraph, literal working
translation, original target groups, complete parse, lexical/source references,
condition/participant graph, full reencoding, observed key and completion
ambiguities. Do not select the most fluent of several readings after search.
A second complete paragraph on a different admitted physical leaf can test
the same frozen key if that transfer is preregistered; separate seed keys do
not establish manuscript-wide sharing. Such previously exposed transfer still
is not independent confirmation.

The unknown after GDT905 and GDT965 is whether this particular finite
source-derived paragraph language and channel has any complete candidate in
that fixed scope. A verified witness supplies a concrete hypothetical reading
and its next fixed consequences. Exhaustive absence rejects this finite
inventory/grammar/channel/alignment conjunction for the evaluated literal
paragraphs. Many inequivalent witnesses establish ambiguity. Timeout remains
UNKNOWN. Nonliteral or otherwise source-unknown paragraphs are never converted
to linguistic contradictions. None of these outcomes refutes broader Arabic,
Semitic writing, all morphology or the possibility of a different source text.

Suggested decision budget: **45 minutes total**, including 15 minutes to freeze
the source grammar and check its own complete clauses, 5 minutes for targeted
independent validation, 15 minutes for a bounded target search, and 10 minutes
for result/limitation publication. If the first 15 minutes cannot yield a
coherent explicit finite grammar, stop at that source-model incompleteness;
do not spend the remaining budget inventing a broad parser. At search expiry,
report the completed prefix and unknown remainder without an automatic larger
lexicon, changed channel or decoder successor.
