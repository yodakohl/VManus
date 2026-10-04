# CoReMA source-rule reconstruction: finite partial relation, incomplete writer

4 October 2026. **The accepted source task produced a reproducible finite
relation, but not a complete historical writing mechanism suitable for a new
Voynich decoder.** There was no unknown-key recovery and no Voynich input.
The practical gain is an explicit source inventory of shared multi-letter
outputs, complete groups, and failures, in place of unconstrained inserted
letters. It does not establish that those rules belong to Voynich.

## What was actually reconstructed

The six original CoReMA transcriptions and their character/editorial
declarations are the already owned, byte-pinned GDT1166 sources. No new corpus
was acquired. The [protocol](PROTOCOL.md) fixes an ordered local relation from
the character declaration before the full enumeration: same declared graphic
class, union of all declared expansions, applied in written order. It retains
ordinary characters, diacritics, multi-letter signs and complete word signs.
It uses neither a word list nor fitted language preferences. It never uses an
`ex` position or a value-bearing glyph ID to choose a class's output.

There are 56 consistent declared graphic classes; 27 occur in the selected
groups. For example, the overline has 18 declared rendering alternatives,
including an empty rendering; the comma-shaped mark has eight. The barred-p
class has five: `par`, `per`, `perir`, `por`, `pri`. A single source libra sign
can supply a whole word. All alternatives, declarations and inconsistent
entries are retained in [DECLARATION_RULES.json](DECLARATION_RULES.json).
These are **editorial classes**, not verified native shape identities.

The relation's values are supplied by the edition. Compatibility below means
that a source expansion is among its outputs, not that an unknown reader
recovered that expansion. Of the 11,517 compatible groups, **11,436 still
permit multiple unrestricted output strings** under this relation. Those
outputs include strings that may not be words. No language filter was applied.

## Full descriptive accounting

The body projection contains 98,720 editorial whitespace/join groups in all.
Every one of the 11,797 `abbr` elements is conserved: 11,727 occur in projected
groups and 70 are excluded by the declared final-state/editorial policy,
including empty containers. Groups and abbreviation elements are different
units: a group can contain multiple elements, and an abbreviation sign can
appear without an `abbr` wrapper.

| Witness | Selected complete groups | Locally compatible | Unresolved | Locally incompatible |
| --- | ---: | ---: | ---: | ---: |
| B4 | 1,178 | 1,164 | 14 | 0 |
| B6 | 55 | 55 | 0 | 0 |
| Br1 | 779 | 778 | 1 | 0 |
| Bs1 | 1,733 | 1,725 | 8 | 0 |
| Gr1 | 4,957 | 4,814 | 141 | 2 |
| W1 | 3,022 | 2,981 | 40 | 1 |
| Total | **11,724** | **11,517** | **204** | **3** |

[GROUPS.json.gz](GROUPS.json.gz) retains every selected group, exact native
character sequence, complete editorial expansion, source element/page/line,
abbreviation IDs, glyph occurrences and flags. [SUMMARY.json](SUMMARY.json)
and [CONSERVATION.json.gz](CONSERVATION.json.gz) bind the denominators and
exclusions. Unknown graphic classes affect 176 selected groups; 26 have
supplied text and two have metamarks. These are unresolved source obligations,
not contradictions of the local relation. Individual flags may overlap.

## All three local counterexamples

1. **Gr1, source fol.019v, line N016**, `gr1:A00549`: the edition has
   `ſeq<ex>ui</ex>t<ex>ur</ex><am><g ref="#urrot"/></am>`, expanded
   `sequitur`. The one written final mark cannot locally insert `ui` before
   the surviving `t`. This demonstrates nonlocal restoration in this encoded
   pair, not a complete generic rule for its unseen variants. The case was
   already identified in the earlier written-data contract.
2. **Gr1, source fol.035v, N012**, `gr1:A01487`: written `plürme`, expanded
   `plurmen`, with a supplied `n` and no `am`. The declared diaeresis's empty
   normalized rendering supplies no final `n`. This known source-contract
   exception cannot establish a general unmarked-deletion rule. Missing or
   incomplete encoding and actual scribal omission are not distinguished here.
3. **W1, source fol.023r, N018**, `w1:A02101`: `lampp<ex>re</ex>` is followed
   by `g ref="#combcomma_re"` **outside** `am`, then `t<ex>e</ex>` plus the
   overline and `n`. Under the fixed literal TEI projection, the expansion is
   `lampprereten`: supplied `re` plus the glyph's normalized `re`. The local
   relation cannot duplicate that syllable. This is an encoding/projection
   discrepancy requiring source/editorial adjudication; it is not evidence
   that a historical writer actually wrote a doubled `re` in the expansion.

No exception was silently corrected and no new rule was fitted to these
three words. [COUNTEREXAMPLES.json](COUNTEREXAMPLES.json) preserves all rows.
The original XML remains the authority. In particular, the two Gr1 examples
are retained countercases, not newly discovered facts renamed as progress.

## Application conditions remain insufficient

The [editorial declaration](https://gams.uni-graz.at/o:corema.editorialdec/TEI_SOURCE),
section `editorialDecl n="glyphs"`, explicitly permits visually similar
substitutes where the character standard has no suitable representation. It
also assigns common allographs ordinary ASCII characters and documents
departures in each manuscript's `scriptDesc`. Consequently, identical Unicode
renderings do not prove identical native signs; a precise positional writer
cannot be derived from these codepoints alone.

The script descriptions do supply contextual observations: B4 describes long
`s` initially/medially and round `s` finally; Br1 explicitly allows long `s`
finally in doubled forms; W1 describes a gradual distinction between raised
`e` and dot-shaped diaeresis. W1 also records occasional `w`/`vv` for the sound
`fu`. These statements have different scopes. They cannot become one global
substitution table, and the last concerns sound rather than the edition's
literal written expansion. No such rewrite was added here.

There are **169 witness-by-exact-expansion pairs** with an explicitly
abbreviated shorter realization and an unabbreviated realization in the same
book, retained in [OPTIONAL_PAIRS.json.gz](OPTIONAL_PAIRS.json.gz). Examples:

- Gr1 `Item`: `It` plus overline at 045r/N001; `Item` at 045r/N020.
- Gr1 `aber`: `ab` plus comma-shaped mark at 011v/N021; `aber` at 011v/N014.
- B4 `oder`: `od` plus comma-shaped mark at 083r/N004; `oder` at 071v/N003.

The examples refute a word-only rule requiring that exact expansion to be
shortened on every occurrence in that witness. They do **not** show the
contexts, hands or available line space to be identical, or rule out a
conditioned preference. The finite declaration gives possible renderings;
it supplies no complete law of obligatory versus optional shortening.

## Research decision and predecessors

**Deliver the finite partial rule package; do not start a decoder from it.**
This is stronger as a source specification than GDT1166's one latent sign and
0–4 letters anywhere in a word: it supplies actual shared finite output sets,
multiple sign classes, ordered composition and whole-word signs. It does not
reopen that failed experiment. These classes were present in the original
source declaration; the contribution is their executable joint accounting,
not a discovery of a previously unknown historical abbreviation mechanism.

GDT157 already learned a historical forward channel with qualified control
success and major Voynich residuals; GDT207 already rejected its direct
one-character attack. GDT1160's conditional supplied-inventory success and
GDT1164/1166's failures stand. Source compatibility with supplied values does
not bridge the missing unknown key. Nor does it establish a Voynich language.

The original objective of obtaining a **complete externally constrained
writer** is therefore not achieved by these sources. Reconsider only with
an independently supported rule linking native sign identity/attachment,
nonlocal restoration and application context across multiple full groups, or
a genuinely different bounded identifying experiment. Merely adding the
three answers, enlarging a vocabulary, or trying another optimizer is not that
input. No automatic source hunt follows this result. Confirmed Voynich words:0.

## Reproduction and validation

From the repository root:

```sh
python research_registry/proposals/production_origin_supply_20261003/source_rule_package/build.py
python research_registry/proposals/production_origin_supply_20261003/source_rule_package/validate.py
```

The builder uses only Python's standard library and the eight already
published source files pinned in SUMMARY. [VALIDATION.json](VALIDATION.json)
records independent regular-expression membership checks of all 11,724 groups,
independently reconstructed declaration alternatives, XML glyph references,
raw abbreviation conservation and all 169 distinct-writing pairs. A second
build reproduced all scientific artifacts byte for byte. This does not
independently reproduce every XML projection decision or collate the native
facsimiles. No probability or significance follows from the descriptive counts.

Attribution: CoReMA, University of Graz; original TEI credits and source links
are retained in GDT1166/sources and SUMMARY. Source text license: CC BY4.0.
Preparation corrections and prior exposure are disclosed in PROTOCOL; this
was not preregistered or analyst-blind confirmation. No target selector,
reserved leaf, opaque Voynich value or concrete Voynich word meaning was used.

Publication checks: the source-package validator and live-context check pass.
The repository-wide preflight still reports pre-existing route-literal,
historical manifest/binding, cached-artifact/layout and index issues outside
this source task; it is not reported as a global PASS. Publication uses an
explicit scoped staged-tree check, including decompressed artifact privacy,
and preserves unrelated working changes. No historical experiment is repaired.
