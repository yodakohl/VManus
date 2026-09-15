# Rota variable-code review

2026-09-15. Source-only design review, begun 12:50 UTC and bounded to 13:10 UTC.
No target paragraph length, content, cycle or candidate count was inspected or
selected. No decoder was built. Published primary reports were read for their
contracts; their incidental historical examples are not new test inputs.

**Approve the revised glyph-projection conjugacy screen as a necessary test of
one explicitly conditional source-copy family. Prefer it to a decisive padded-
space screen.** A negative can exclude that family in the complete literal
intake. A positive supplies structural capacity only: it neither produces a
shared code nor recovers the three musical parts. The complete three-part code
remains a possible whole-reading hypothesis, with its musical interpretation
conditional on the source and representation assumptions below.

## Source consequence, including rhythm

My pes/rules observation was sealed before reading the producer's event file.
The producer retained its own pre-comparison matrix hash and identified the
seven-line upper-stave correction as comparison-triggered. Both records retain
the upper irregular-ink and end-boundary qualifications. The producer supplies
the complete melody; this review does not claim an independent native reading
of its 73 notes and six pauses.

In the current event inventory, the upper pes is AB and the lower BA, where
A contains F–G–F–G–A, including the ascending final G–A ligature; B contains
C–B-flat–C–pause. Both pes contain nine written events. This is a relation
between the whole retained parts, not selected repeated snippets.

I independently reconstructed pitch/duration tuples from the source JSON and
checked all four declared documentary branches. They all satisfy the exact
event-word identity `P2 = P1[5:] + P1[:5]`. C0/C1/C3 give A = 12 and B = 12
breves; the Hurry-prose C2 countercase gives A = 11 and B = 12. Therefore
conjugacy does **not** require a half-period shift, an equal-duration split or
the same number of notes in the two blocks. A = 11/B = 12 remains conjugacy.

The general source assumption is a shared, rotation-equivariant interpretation
of corresponding notational events in their circular contexts. A duration
policy that changes a note merely because it happens to start/end the written
line could break the timed identity. Such a policy is not silently included
in the theorem. The source's continuous repeat instructions support using
cyclic context, but the current four documentary branches are not a proved
exhaustion of all historical rhythmic readings. The unresolved melody
duration attribution remains unresolved even though it does not affect the
two-pes necessary condition.

Keeping each two-note ligature as one compound event instead of two events
also preserves AB/BA: the corresponding complete ligature lies inside A in
both parts. Splitting it into two consistently marked members preserves the
relation as well. In neither case may a ligature be regrouped differently in
the two parts after seeing target strings. A pause remains a source event.

Final source binding: public commit `e1e48a273`, push confirmed 13:02:48 UTC;
ROTA_SOURCE_EVENTS.json SHA-256
`3923d12c26de3d309bef06cfbd1732985ae8d5ba133adc21f1633ff56fb8f34a`;
source compiler SHA-256
`97d2bf4a4f5ce2ba6aba70d65db08536e778ff05a7b14564f46908a69abf9f71`.
The earlier wrapper `9c71ce7df1264fc74bb437fe30db1005e9db3f0e132a58ba97c07f075a789a54`
was exposed during this review. After the final publication I independently
rechecked equality of all 97 events to the public pre-comparison array
`2ff05f993c8ffcba901184bf811557ad604f4e497f785a5d80fedce3b37163fd`,
every pes pitch/rest against my own record, all four branch change maps, the
AB/BA identities, block durations and type/singleton counts. They are unchanged.
The final source explicitly labels initialization NOT_SEPARATELY_COMPARED;
its steady-period executions are not an independent comparison of warm-up.
This is a review binding, not a claim that the conditional duration branches
have become certified medieval readings.

## Minimal full model and its honest scope

The smallest concrete full hypothesis is:

1. Three distinct complete target paragraphs in one edition encode the complete
   normalized event contents of M, P1 and P2. Their order/locations can be
   unknown. No source event or written target group is omitted. Source event
   boundaries may fall inside target groups or span their spaces.
2. Choose one declared source interpretation. An event type is a pitch/duration
   pair, or a rest/duration pair; it is not an occurrence ID. The same type
   receives the same code everywhere in all three parts. The source has
   79/9/9 events, not a prescribed number of target words.
3. One injective codeword assignment maps event types to nonempty strings over
   literal lowercase letters and spaces. Codewords are prefix-free and each
   contains at least one letter. Their widths are arbitrary positive values.
   Prefix freedom is a later full-parse condition, not an assumption needed
   to prove conjugacy itself.
4. If h is the concatenative extension of that assignment, the observed
   paragraph is `trim_spaces(h(part))`. Only exterior ordinary spaces are
   trimmed. Interior spaces remain part of the required full output. Line
   wrapping and group-separator serialization must be specified once from
   the original admitted paragraph data before testing. No phonetic or EVA-
   letter value, note-per-word rule, voice-specific code or header is assumed.

This is a finite exact source-copy hypothesis once the full target strings
are supplied: source occurrence counts bound the possible code lengths. It
does not require equal-width digits, a fixed target word count, a natural-
language lexicon or independent target note anchors. All complete code witnesses
and source branches would have to be retained; no preferred key follows from
finding one solution.

The source C0/C2/C3 pitch-duration alphabets have 24 event types and C1 has 26.
Across the 97 events, the respective singleton-type counts are 2, 2, 3 and 5
when ordered C0, C2, C3, C1. Thus most code values recur, but some codewords
would still have only one source occurrence. This is a real degree-of-freedom
limit on a positive, not an excuse to assign free codes to every occurrence.

This minimal model encodes **normalized part contents**, not all marks or prose
on the folio. Clefs and the flat sign are interpreted into pitches. The native
seven-versus-six staff rulings are not encoded as musical events. If one
instead emits clefs, headings, lyrics or control instructions as target text,
that is a different full model and must account for them explicitly.

In particular, the entry cross and the black/red instructions are not proved
decoded by a note/rest code. A source-instance hypothesis may stipulate the
known rota performance rule as its external interpreter. It must then say
that entry, repetition and performer-count semantics are assumed from the
source, not recovered from extra target words. Alternatively, a complete
instruction-reading model can encode those controls prospectively, but its
linear strings need not satisfy the same unqualified pes conjugacy gate.

## Necessary projection theorem

Let pi delete only the space symbol. With the revised model,

`pi(trim_spaces(h(AB))) = pi(h(A)) pi(h(B)) = UV`

and

`pi(trim_spaces(h(BA))) = pi(h(B)) pi(h(A)) = VU`.

Both U and V are nonempty because every event code contains a letter. Therefore
the two projected whole paragraphs have equal glyph lengths and belong to the
same cyclic-conjugacy class. This proof needs no pitch values, equal-duration
halves, word boundaries at event boundaries, or recovered code.

The proposed bounded screen may group **all distinct complete literal paragraph
IDs within each edition** by their projected cyclic word. It must retain every
pair in every non-singleton group, including identical projected strings and
rotation offset zero. A same-leaf or adjacent-paragraph requirement is not
needed for a broad negative; adding one would narrow the model and needs its
own prospective ownership justification. Different editions remain alternate
readings of one manuscript, not independent replications.

The inherited GDT928 intake can supply paragraph boundaries/provenance, but a
new test must require its entire selected paragraph to meet the fixed literal
and seam policy. Nonliteral/gapped material and RF's missing complete paragraph
boundaries remain unknown or outside the literal test, not negative music
evidence. No shorter windows or fitting source fragments are needed.

GDT928's anchor-line minimum of two groups is not necessary for this model:
one literal group on a line can contain several encoded musical events. Reuse
its complete-boundary and provenance rules, but remove that anchor-specific
minimum before registration, or accurately describe a narrower inherited
eligibility scope. No target count is needed to decide this definition.

If there is no eligible pair, no complete three-part witness exists in that
literal scope under these assumptions. If a pair survives, it has not yet
passed the repeated-event constraints, prefix-free key, third-part requirement,
spaces, source branch or complete re-encoding. Even a nine-letter pair such as
`abcdefghi` and `fghiabcde` is conjugate but cannot encode this nine-event pes
through a non-erasing code: all event codewords would have length one, and the
source's repeated F occurrences would wrongly require `a = c`.

## Why the boundary revision is preferable

Padding every raw paragraph by one final space can represent a genuine closing
word separator under an explicitly chosen channel. For example, source codes
`a -> "x "` and `b -> "yz "` naturally produce the padded cyclic pair
`"x yz " / "yz x "`. Omitting the final separator would disrupt that relation.

But padding is not an innocuous operation on every homomorphism. Bare codes
`a -> "a"`, `b -> "b"` give conjugate outputs `"ab" / "ba"`; appending an
external common space produces `"ab " / "ba "`, which are not conjugate.
Thus padded-space equality may be decisive only for a channel that already
places that boundary symbol inside h's output. It is not a theorem about all
complete non-erasing codes. The revised trim-and-project test avoids choosing
between these legitimate exterior-space conventions.

Projection also loses injectivity. For a concrete source-only counterexample,
distinguish the longa G as G and the ligature G as g and use these seven
distinct width-four codewords (underscore means a literal space):

| Event | Code |
|---|---|
| F | `aaaa` |
| G | `_aaa` |
| g | `_a_a` |
| A | `aa_a` |
| C | `a_aa` |
| B | `aaa_` |
| Rest | `a_a_` |

This is an injective prefix-free event code and every code contains a letter.
The whole words `FGFgACBCR` and `CBCRFGFgA` encode to different conjugate
36-character strings. Trimming gives 35 and 36 characters, each with ordinary
single internal spaces. Both glyph projections are the same 27-letter string.
This construction was checked independently without target data. It proves
that equal projected strings must not be excluded, that full trimmed lengths
need not agree, and that a glyph-only positive does not explain the spaces.

## Meaning ceiling and predecessor boundary

The necessary screen is purely structural. It never distinguishes music from
another cyclic list, nor checks harmonic intervals, entry timing, source note
names, or correct ligature durations. GDT397's identical-observation argument
and GDT611's meaning permutations apply to promoting that result into a gloss.
GDT911 likewise warns that satisfaction of one formal content constraint does
not uniquely fix a meaning. Prefix freedom supplies unique parsing under a
given full key, not a proof of intended musical denotation.

A later complete three-part witness would be stronger: the key would map every
target character and space to a previously frozen, source-owned score and
therefore specify a whole musical reading **within the hypothesis**. It would
not be merely an after-the-fact name for an anonymous recurrent role. But it
would still not logically force musical intent. With an unrestricted atomic
event code, a global permutation of source event labels accompanied by the
inverse code permutation preserves the equality pattern while potentially
changing the music. Full-score compatibility, source attribution and semantic
uniqueness are distinct claims; all equivalent keys/interpretations matter.

GDT928 does not settle this screen. Its anchors contained at least three whole
words, at least two different forms, stayed inside individual lines, and paired
different physical leaves. A character rotation may cut inside a word, cross
line wraps, or use the same leaf. GDT925 concerned whole-line word multisets.
Neither result excludes the newly defined complete-paragraph character
consequence. GDT898's prefix-code injectivity proof remains valid at the full
code level, but does not survive a lossy projection as injectivity. GDT901's
22-record solmization model required whole-word realizations and paragraph-first
heads; it remains closed and supplies no blanket music rejection.

Finally, composition knowledge motivates shared parts but does not certify
this context-free homomorphism. GDT608's whole-form residuals and retained
entry-context effects remain potential failure modes. Permitting them later
through unbounded context-specific event codes would destroy the present
necessity and constitute a new model, not repair this one. If the weak screen
is negative, close this fixed family; if positive, review a complete source/
code contract before any parser work. Neither outcome confirms a word, licenses
a reserve, or automatically extends this test.
