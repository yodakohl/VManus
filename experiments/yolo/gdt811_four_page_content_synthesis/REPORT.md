# GDT811 — four complete pages and explicit semantic binding

Status: COMPLETE_PAGE_SYNTHESIS__MEANINGS_UNRESOLVED

## Result

There is still no recovered translation. The new deliverable is a
[consolidated content theory](WORKING_THEORY.md) tied to **all178 source loci
and946 tokens** of four inspected physical pages, with the
[entire text and alternate readings](artifacts/FOUR_PAGES_FULL_TEXT.md)
available alongside it. It is not a replacement renderer or a new dictionary.

The most useful distinction is between an illustrated thing, a property of
that thing and a reference/category applied to it. A label is not guaranteed
to be the object's name. The complete texts reveal where the tempting name
and sentence interpretations fail to carry their intended explanatory weight.

| Physical page | Running lines/tokens | Local loci/tokens | Exact complete-label strings reused in running text |
|---|---:|---:|---|
| f17r | 12 / 78 | 1 / 2 | none |
| f77r | 40 / 321 | 10 / 11 | otedy |
| f88r | 16 / 134 | 15 / 16 | okol |
| f72r, three source panels | 10 / 288 | 74 / 96 | okal, okaly, otar, otam |

Running-line status on circular text is inherited transcription annotation,
not proof of prose syntax. There are nine complete ordinary paragraphs on
f17r/f77r/f88r; the ten f72r circular text bands are not silently turned into
ten ordinary paragraphs. The f17r marginal record and multiword labels remain
separate. Eleven exact text-identity edges include duplicated label-to-one-
token contacts; six edges have the declared all-reader support, not six
independent discoveries or pictured-object identifications.

## Two inspected leads, and what their extension really says

### The okol family is not a newly decoded plant name

The strongest local f88r identity is okol at label .15 and prose .19.
The line also has chokol and two qoekol; the next paragraph has okoldy and
five qokol. Those thirteen f88r seed occurrences, including ofaldo/ofal,
retain their separate complete spellings in all three readings.

The exact seven-whole inventory extends this outcome-aware observation:

| Whole | Occurrences | Page/group keys | Outside f88r occurrences |
|---|---:|---:|---:|
| okol | 58 | 45 | 56 |
| chokol | 3 | 3 | 2 |
| qokol | 90 | 52 | 85 |
| okoldy | 8 | 8 | 7 |
| qoekol | 2 | 1 | 0 |
| ofaldo | 1 | 1 | 0 |
| ofal | 2 | 2 | 1 |

The164 occurrences include150 same-line occurrence-rank matches across all
three alternative readings. Rank support is not exact positional alignment.
Raw kinds are156 P, seven L and one C; the C event is running circular text
under GDT791 and is not miscounted as a local label.

okol spans seven source sections, including the released f71v ring text.
okoldy also occurs as a released f68r1 label. This weakens the first impression
of a narrowly specific drug name, without logically disproving a widespread
substance name. Shared properties, categories or reference functions remain
live; none is assigned a translated identity by this census. q, ch, dy, e
and do receive no free meaning.

ofaldo/ofal is a narrower candidate for a learned name: one f88r label, one
f88r prose occurrence and one external prose occurrence at f108r.14. The
last source line is polchal shol qokar shedy pcholy qokal opchdy ofal shor
qokaiin otalod. No species, suffix or noun role is identified by that fact.

### The f17r bracket remains local

Both otchol qodcthy ods chol and otchol cthar okaiin chol are exact in the
three readings; the first crosses a physical line. These motivate explicit
material/form scope and forward-rubric rivals, documented with the full page
in [the local reading](src/F17_SCOPE_PROPOSAL.md).

All30 released pages contain eight prose otchol occurrences. Six have a
subsequent chol in the same strict paragraph, two do not. The intervening
widths are0,12,2,2,30,16; only the two known f17r cases have width two.
The exact f4r otchol chol is a direct counterexample to obligatory two-slot
grammar. Neither the failed generalization nor reader differences erase the
local f17r possibility. The inventory does not prove a subject, property or
sentence boundary.

## Joint content interpretation

The working comparison joins a botanical material register on f88r, botanical
description on f17r, differentiated water applications or bodily powers on
f77r, and member/status inscriptions on f72r. A common property vocabulary
could connect them without turning every plant into an ingredient or every
star-holder into a literal patient. A compendium with different genres remains
a serious alternative to one shared explanatory system.

This historical architecture is not a new codebook identification. The
[source notes](src/F77_HISTORICAL_READING.md) distinguish the actual dates and
layers of the medicinal-water, Wellcome MS510 and Parker MS395 comparators.
They support plausible kinds of content, not an EVA-to-Latin mapping.

The complete-page comparison sharpens possible referents and interpretation
burdens. It supplies zero confirmed lexemes, free components or plaintext
clauses. Smooth German would still require unsupported choices; the dictionary
and existing renderer therefore remain unchanged.

## Scope, reproduction and corrections

The full reader uses six source selectors for four physical pages. The bracket
inventory uses GDT791's35 selectors for30 released physical pages. The word
inventory uses the **union of179 inherited selectors and those35 selectors:
190 selectors**, not190 visually inspected or newly released pages. Explicit
GDT791 keys such as f67r2/f68r1 are preserved; outside that mapping, normalized
side groups are labelled a heuristic. No new manuscript page was admitted and
f84/f84r were rejected before mixed-row materialization.

Two implementation assumptions were corrected before the completed build:
the reference script initially over-normalized released panel keys and stopped
before raw querying; the first relation packet used f72r physical-page keys
where GDT388 requires source selectors. The corrected packet preserves every
locus. All17 text-only edges are ineligible/unsealed; four cross-selector
f72r edges additionally exceed the single-selector packet schema. None is
score-ready. These are disclosed evidence limits, not lexical rejections.

```sh
python3 -B experiments/yolo/gdt811_four_page_content_synthesis/src/run.py
python3 -B experiments/yolo/gdt811_four_page_content_synthesis/src/validate.py --no-write
```

The builder orchestrates all three inventories. The independent validator
checks source conservation, exhaustive exact identity and inventory claims,
not the truth of the proposed meanings. New designs openly disclose the
already inspected motivating cases; no false unseen-test claim is made.
All19 substantive validation groups pass. The repository-wide check remains
subject to the seven pre-existing unbound GDT600 files; those are unrelated
and are not included in this publication.

Do not rerun these same inventories as another semantic discovery. A new
useful step needs a specific identification or distinct contextual prediction,
particularly for the narrow ofaldo/ofal name rival or for a shared property,
not another score for the same inherited German defaults.
