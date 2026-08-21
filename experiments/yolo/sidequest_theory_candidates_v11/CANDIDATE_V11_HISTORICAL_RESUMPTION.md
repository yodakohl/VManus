# V11 historical resumption candidate

Date: 2026-08-21

Status: **independent speculative sidequest candidate, not a GDT result or
translation**.

## Decision

The historical pass ends at:

```text
TOPIC_CARRIER_NOT_DISTINGUISHABLE_FROM_LOCAL_PROSE_RECURRENCE
```

The useful anonymous architecture is `ARTICLE_LOCAL_RECURRENCE`: both target
cards repeatedly reactivate something already live in one illustrated Herbal
article, but the fixed evidence cannot tell whether that something is the
pictured simple, a recurrent part or preparation, or an ordinary technical
content item. `PAGE_OWNER` is too strong. None of the six occurrences is the
first card of its paragraph record.

This is a positive architectural conclusion and a negative lexical conclusion.
The article keeps local referents or subjects active across physical lines; it
does not yet supply a recoverable pronoun, plant name, or content word.

## Provenance and permitted evidence

The complete exact-card census was selected from the f84-free GDT327
interlinear with the guarded repository command and an explicit four-page
allow-list (`f10r`, `f11r`, `f55v`, `f56r`). The selected slice contains 100
events. No substring, edit-distance, PAGE_HOST coordinate, phonetic comparison,
or visual semantic label was used. `f84` and `f84r` were neither selected nor
inspected.

The two targets are exact opaque joint-tuple identities:

- `OWNER-10`: `4d4559019a961b834aa1`;
- `O56`: `2cc054357a929df85f64`.

Surface spellings below are shown only to make the source context auditable.
They were not used to construct a similarity class.

## All six occurrences

| target | locus/event | record and placement | complete physical line | accounting |
|---|---|---|---|---|
| `OWNER-10` | f10r.2#3 | paragraph record 1; MIDDLE | `dchey cthoor [char] chty os chair otytchol oky daiin etyd` | first record contains one copy, embedded after two opaque cards and before seven others |
| `OWNER-10` | f10r.8#8 | paragraph record 2; LAST | `qotchor chor otol chol cholor chol daiin [dar]` | second record contains one copy, but at a physical-line tail after seven cards; record continues on f10r.9 |
| `O56` | f56r.5#2 | sole paragraph record; MIDDLE | `chochor [cho] chodaly daiin` | first physical line of the record, but not record entry |
| `O56` | f56r.7#1 | same record; FIRST | `[sho] kchol otchor choky dal` | physical-line restart with a new right context |
| `O56` | f56r.12#2 | same record; MIDDLE | `sh [cho] kchey qokokchy` | medial recurrence after an opaque card |
| `O56` | f56r.18#1 | same record; FIRST | `[sho] chokchy kchoar sotodan` | second physical-line restart with another right context |

The two line-first `O56` occurrences use the `sh` realization and both medial
occurrences use `ch`. That is compatible with the already known physical-line
renderer. It does **not** make the recurrence itself a renderer artifact: all
four events retain the same exact opaque tuple while their following cards
differ. `OWNER-10` likewise survives the visible `char`/`dar` variation, but
its two positions are MIDDLE and LAST rather than a common entry slot.

## Matched recurrent-card controls

Counts below use the same 100-event four-Herbal-page slice. “Neighbour
diversity” counts distinct immediately adjacent exact tuples, with physical-line
START/END as possible neighbours.

| anonymous exact card | events | pages | lines | records | FIRST/MIDDLE/LAST | left/right neighbour diversity |
|---|---:|---:|---:|---:|---:|---:|
| portable `A` | 9 | 4 | 8 | 5 | 2/4/3 | 8/7 |
| portable `Y` | 9 | 3 | 5 | 3 | 0/7/2 | 8/7 |
| portable `R` | 5 | 2 | 4 | 2 | 0/5/0 | 5/4 |
| target `O56` | 4 | 1 | 4 | 1 | 2/2/0 | 3/4 |
| local `L` | 3 | 1 | 2 | 2 | 0/3/0 | 3/3 |
| target `OWNER-10` | 2 | 1 | 2 | 2 | 0/1/1 | 2/2 |
| matched two-event portable card `10488b91...` | 2 | 2 | 2 | 2 | 1/1/0 | 2/2 |

The targets are therefore not unique merely because they tolerate several
neighbours. The stronger facts are narrower:

- `OWNER-10` is the only two-copy page-local identity in this primary pair and
  occurs once in each f10r paragraph;
- `O56` spans four of f56r's seven physical lines and alone mixes two FIRST and
  two MIDDLE uses at this frequency;
- nevertheless, local `L` also spans both f10r paragraphs, and the portable
  controls show equal or greater neighbour diversity.

Page locality is therefore evidence for article-local content as readily as
for an article-local reference mechanism. The selection was discovered on
these same pages and has no untouched-page transfer.

## Deletion check

Deleting the two `OWNER-10` events yields ordinary-looking open sequences of
nine and seven remaining cards. It exposes no repeated adjacency or fixed
boundary and merely removes one item from each paragraph. Deleting `O56`
leaves four well-formed-looking three- or four-card physical lines:

```text
f56r.5   chochor chodaly daiin
f56r.7   kchol otchor choky dal
f56r.12  sh kchey qokokchy
f56r.18  chokchy kchoar sotodan
```

This rules against an obligatory delimiter or syntactic connector. It does not
separate optional topical anaphora from a repeatedly mentioned plant part,
liquid, preparation, property, or action: deletion removes the identity in
both cases.

## Historical comparison: what a scribe around 1420 could learn

The closest date-controlled comparison is Tadhg Ó Cuinn's Irish *Materia
Medica*, explicitly dated 1415. The scholarly CELT edition describes its normal
entry order as Latin chapter heading, Irish drug name, qualities, general
virtues, and specific uses, and identifies the *Circa instans* as the principal
source and format model. It is thus a strong control for an article that keeps
one simple active while moving through heterogeneous statements—not evidence
for any Voynich language or source.

More importantly, its readable entries alternate several ordinary resumption
devices inside a single chapter. The burdock entry repeatedly refers to the
root, juice, “this herb,” and “roots of this”; the elecampane entry alternates
“this herb,” “the same herb,” and “roots of the same herb.” Other long entries
similarly move among the whole simple, its juice, powder, roots, flowers and
foliage. These are structurally indistinguishable without readable words: a
recurrent item can be a general anaphor, a head-noun phrase, or repeated local
content. [CELT introduction and date](https://celt.ucc.ie/document/G600005/),
[burdock and neighbouring entries](https://celt.ucc.ie/document/G600005/),
[elecampane passage](https://celt.ucc.ie/document/G600005/).

A fifteenth-century Middle English *Circa instans* comparison printed by
Garrido-Anes is even more direct. Parallel Aloe passages proceed through
successive clauses using repeated `hit/it`, while the chapter's drug remains
the understood topic. The same study describes *Circa instans* articles as
moving from complexion into ailments and administration, with possible
harvest time, origin, varieties and adulteration warnings. That breadth makes
repetition across distinct local contexts historically normal.
[Garrido-Anes, “Manuscript Relations through Form and Content in the Middle
English Circa Instans,” *SELIM* 13 (2005–06), pp. 201–226](https://reunido.uniovi.es/index.php/SELIM/article/download/13436/12167/28494).

Late-medieval recipe collections supply a related but distinct mechanism:
headings such as “Another,” “Another for the same,” and “For the same” avoid
repeating an ailment or medicament. Sylwanowicz's corpus study explicitly
classifies these as one heading type. This makes a learnable resume-card
historically plausible, especially at a new packet start, but predicts a
generic cross-entry device rather than two unrelated page-private identities.
[Sylwanowicz, “Medieval Medical Writings and Their Readers,” *Linguistica
Silesiana* 38 (2017), pp. 111–124](https://journals.pan.pl/Content/101748/PDF/LS%2038_8%20Sylwanowicz.pdf?handler=pdf).

Finally, a German paper *Circa instans* manuscript of the 1440s–1450s contains
277 drug chapters, while the tradition comprises roughly 133 manuscripts from
the late twelfth through late fifteenth century. This confirms that long,
repeatable simple-monograph organization is chronologically and materially
ordinary, not that this manuscript is the Voynich exemplar.
[Wellcome MS.624 catalogue](https://wellcomecollection.org/works/y78kt23d).

### Historical mechanism ranking

| possible source practice | fit to six events | problem |
|---|---|---|
| title/rubric or repeated plant name | low | zero of six events begins a paragraph record; f10r's second copy is a physical-line tail |
| generic `it/this herb/the same`-like resumption | medium-high | historically common and position-flexible, but should usually be portable across articles |
| `Item/another/for the same` entry resumption | medium | explains two line-first O56 copies, not its two medial copies or either OWNER-10 placement |
| repeated part/preparation/medium/process | medium-high | naturally page-local and historically repeated, but its referent is not visible independently |
| ordinary frequent technical abbreviation | medium-high | fully compatible with counts and neighbour diversity; offers no special discourse prediction |
| renderer-only alternation | low | explains `sho/cho` placement realization, not recurrence of the exact underlying card |

No single historically ordinary mechanism distinguishes the two medium-high
families on these pages. A scribe could learn either with minimal machinery:

```text
ARTICLE TOPIC remains active until paragraph/page reset
LOCAL RECURRENT CARD recalls either that topic or one article-local subtopic
SURFACE WRAPPER adapts at physical-line entry
```

The middle line intentionally leaves “topic or subtopic” unresolved.

## Controlled continuous reading

This reading preserves all six occurrences and refuses lexical expansion:

> **f10r, paragraph 1:** For the pictured simple, record opaque identifying or
> descriptive material; mention `LOCAL-A`; continue through further opaque
> properties, relations or uses. **Paragraph 2:** continue the same illustrated
> article through a different sequence; return once to `LOCAL-A` near the end
> of an internal physical line; continue on the next line.

> **f56r:** For the pictured simple, proceed through one long open article.
> `LOCAL-B` recurs in four packets—twice after one preceding card and twice at
> physical-line restart—each time with a different continuation. Three other
> packets omit it. `LOCAL-B` therefore marks a repeatedly relevant article
> node, not an obligatory line opener or closer.

A deliberately looser historical expansion is possible but not selected:

> “Of/for this [simple or part] ...; likewise concerning it ...; this [part or
> preparation] ...; return to it ...”

`this`, `it`, `part`, and `preparation` are illustrative alternatives, not
assigned meanings.

## Strongest counterexamples and falsifiers

1. `OWNER-10` ends f10r.8 while its paragraph continues on f10r.9. That is
   awkward for a simple paragraph-opening resume card and entirely ordinary
   for content.
2. `O56` is absent from three of seven lines in its sole record. It is not a
   mandatory current-topic flag.
3. Local `L` already recurs across both f10r paragraphs with comparable
   neighbour diversity. Repetition across paragraphs is not unique evidence of
   page ownership.
4. Both targets are page-local in the fixed sample. A generic pronoun or
   `ITEM/FOR-THE-SAME` abbreviation would more naturally recur in other Herbal
   articles; a page-local part or preparation predicts the observed
   concentration at least as well.
5. The target set was selected after inspecting these pages, so none of its
   recurrence is prospective.

Fixed-page evidence would favour `TOPIC_RESUME` if one of the same exact cards
appeared in an independently defined continuation packet after a paragraph or
layout interruption while matched content cards did not. It would favour
`REPEATED_PART_OR_PROCESS` if the card consistently occupied one relation or
argument environment while generic resumption used a different portable card.
Neither discriminator is present in the six events.

## Claim ceiling

The historical record supports a simple learnable workshop rule: an Herbal
article may keep one pictured topic and several local subtopics active across
physical lines, using repetition, anaphora, ellipsis, or abbreviated resume
formulas. It does not identify which mechanism `OWNER-10` or `O56` realizes.
The cards remain anonymous article-local recurrences; no plant, part, liquid,
pronoun, article, preposition, verb, language, plaintext, or translation is
established.
