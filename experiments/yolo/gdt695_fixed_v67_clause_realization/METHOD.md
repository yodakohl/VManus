# GDT695 method

## Question and fixed scope

Can the complete V67 German working reader be divided into executable clauses
and nominal register blocks without changing a content word, and can every
active verb be checked against the action inventory that actually remains live
after GDT689?

The scope is fixed at the same 479 token positions, 51 lines and 36 admitted
pages used by GDT694. No new page, transcription or image is opened. Both f84
and f84r are forbidden.

## Baseline correction

GDT688/V61 contained 85 action positions and 113 active verb occurrences.
GDT689/V62 then deliberately changed the `dy` sister dispatch: `olchdy` and
`dshedy` became nominal results, while `ytedy`, `checthedy` and `qolsheedy`
inherited four additional active verbs from their sister cards. The live result
is therefore 83 positions and 115 verbs.

Later preservation tables retained the older 113-row V61 profile deck. That
deck remains historical provenance, but it is not a sufficient multiplicity
test for V67. GDT695 instead scans every one of the 479 V67 token glosses with
the same 32 frozen verb regular expressions and compares the ordered lemma
multiset at each position against GDT689's 115-row V62 provenance. A build
stops on any missing, additional, duplicated, reordered or non-action verb.

## Clause realization

The preregistered policy in `src/V68_CLAUSE_REALIZATION_POLICY.tsv` is applied
in this order:

1. Collapse the three GDT694 bound spans without changing their text.
2. Attach four zero-word semicolon/full-stop cards to the preceding unit; none
   becomes an empty clause.
3. Let only a GDT689 `v62_action_ordinal` create an action clause. A multi-verb
   card remains one written clause.
4. Join four exact right-bound introducers only to their immediately following
   target. This adds punctuation, never a word or a carried object.
5. Render ten accepted GDT676 head/value bindings: nine adjacent edges receive
   a colon and one already lies inside a frozen GDT694 span.
6. Join every other maximal nominal run by semicolons and separate action versus
   nominal units by full stops.

`NOMINAL_BLOCK` is an artifact label for a maximal non-action/register run, not
a part-of-speech claim about every included card. Three such blocks contain a
registered right-bound connector. A full stop isolates a state/result block but
does not promote it to an action.

The resulting German word sequence is compared case-insensitively with every
V67 line. Capitalization and punctuation may differ; addition, deletion or
reordering of a word is fatal. No `dann`, pronoun, object, source, destination,
verb or other connective may be supplied for fluency.

## Outputs and independent validation

The builder writes the complete token freeze, 175 clause records, 51-line
reader, 83-position verb multiset audit, 115 exact token-span provenance rows,
three-span freeze, word audit, mode census and the V61/V62/V67 baseline
correction. The independent validator reloads the frozen inputs, rescans all
479 token glosses, verifies the action keyset and word sequences, and rebuilds
all deterministic artifacts byte-for-byte in a temporary directory.

## Decision rule and claim ceiling

Pass requires 83 action clauses, 92 nominal blocks, 175 total clauses, exactly
115 active verbs on exactly the 83 GDT689 action ordinals, zero active verbs
elsewhere, all 479 token glosses and three spans byte-identical, all 51 word
sequences unchanged, and zero new/f84/f84r pages. All requirements pass.

V68 is a grammatical presentation of an exploratory German working renderer.
It does not establish Voynich sentence boundaries, syntax, plaintext, language
or historical lexemes. The punctuation makes the present hypothesis readable;
it does not strengthen its semantic truth.
