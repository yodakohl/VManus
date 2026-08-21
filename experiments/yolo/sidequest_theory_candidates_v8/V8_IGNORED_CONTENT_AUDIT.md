# Sidequest V8 — ignored-content and terminal-value audit

Date: 2026-08-21

Status: speculative inventory and theory update, not a GDT result or
translation. Only the ten fixed pages and a guarded f84-free GDT327 slice were
used. f84 and f84r were not accessed.

## How much text has actually been interpreted?

The seven fixed prose pages contain 381 exact-card events in 135 fields.

| layer | events | percent | present understanding |
|---|---:|---:|---|
| five core cards: qokaiin, L/O, AIIN, Y, CTHY | 73 | 19.2% | speculative broad source functions |
| five secondary cards: SET/SLOT/ENTRY/PROC/STEP | 38 | 10.0% | anonymous parser roles only |
| attached terminal cards | 90 | 23.6% | COMMIT known; exact payload unknown |
| all other opaque cards | 180 | 47.2% | no role or meaning |

Thus 70.8% of all events still have no source-class reading. Even the 29.2%
assigned to core/secondary cards are not confirmed words.

Field-level coverage is more severe:

- 77/135 fields contain none of the ten core/secondary cards;
- 44 fields contain only terminal cards;
- four long fields of at least four cards contain no core/secondary card;
- the fluent V3–V7 paraphrases rely heavily on inherited roles around opaque
  content.

## Page distribution of ignored prose

| page | total events | core five | secondary five | terminals | fully opaque |
|---|---:|---:|---:|---:|---:|
| f10r | 38 | 13 | 1 | 0 | 24 |
| f11r | 17 | 5 | 0 | 1 | 11 |
| f55v | 18 | 5 | 2 | 3 | 8 |
| f56r | 27 | 2 | 2 | 1 | 22 |
| f81v | 66 | 13 | 9 | 17 | 27 |
| f82r | 62 | 7 | 8 | 19 | 28 |
| f83r | 153 | 28 | 16 | 49 | 60 |

Herbal f56r is the least interpreted page: 22/27 events are completely
opaque. f10r also contains 24 opaque events. The present theory mostly reads
their connective skeleton, not the plant content.

## Completely or mostly ignored text classes

### 1. Page-local Herbal content

Most long open Herbal-A fields remain strings of opaque cards. They could carry:

- plant or variety identifiers;
- named plant parts;
- appearance, taste, temperament or quality;
- habitat, water/moisture relation or season;
- preparation and storage;
- therapeutic use or affected body part;
- source-language prose that the card grammar does not factor.

Water can genuinely occur here. What is rejected is only the unsupported
universal equation `OL/AROL = WATER`.

### 2. Biological local deck

OKE/OKEE/LCHE/CHE/CKHY-like exact cards were usually left as PROCESS,
CONFIGURATION, SETTING or opaque X. They may encode:

- apparatus/pool/path stations;
- body or figure classes;
- input/output route;
- material or liquid state;
- treatment step;
- local value category;
- purely diagrammatic/form coordinates.

No stable external owner distinguishes these possibilities.

### 3. Exact terminal payloads

This is the largest structured ignored channel: 90 events and 38 exact
terminal types.

- 16 terminal types recur;
- 22 are singletons;
- the four most frequent types occur 12, 10, 8 and 8 times;
- one common type occurs across f81v/f82r/f83r;
- 44 fields contain no other interpreted card;
- f82r.27 is a run of seven short committed cells.

The mature model is:

```text
TERMINAL_CARD = EXACT LOCAL VALUE + COMMIT
```

Possible payload classes include:

- categorical state or answer;
- achieved result/product;
- operation or transition to perform;
- route/station selection;
- quantity/unit/value class;
- YES/NO/DEFAULT/NOT-APPLICABLE-like checklist state;
- local lexical card whose field slot supplies its semantic type.

Treating every terminal as “done” loses the exact value. Treating every exact
terminal as a known action invents a dictionary. The likely compromise is a
small recurrent value deck plus rare local values.

### 4. Terminal-only fields

A one-card committed field can be useful if its question/slot is inherited
from the stencil. It may mean:

```text
[slot supplied by form] = [exact categorical value]
```

rather than a one-word sentence. Runs of such fields resemble a status vector,
checklist, tabular row or compact sequence of state assignments.

Conditional medical possibilities are:

- ingredient prepared/not prepared;
- hot/cold/moist/dry or another quality vector;
- body/application station active/inactive;
- procedure stage complete/pending;
- route or vessel state;
- product/result category.

None is selected yet.

### 5. Paragraph-open and paragraph-close payloads

The theory recognizes paragraph reset but has not interpreted the exact cards
that open or end most records. These may be:

- dossier title or owner key;
- recipe/application type;
- condition/indication;
- summary/result;
- local register code;
- merely the first/last value imposed by layout.

### 6. Astro/circle text

The three fixed circle pages are almost entirely ignored semantically:

- f67r2: prose zones, central material, seven-member and twelve-member sets;
- f68r1: central star label plus 28 noncentral labelled stars;
- f69v: all 28 ordered radial entries and their internal strings.

Only layout is currently interpreted. Possible content includes names,
ordinal/value entries, lunar days, astrological conditions, calendrical
stations, electional states, mnemonic labels or a generic diagram catalogue.
The strict LONG/SHORT alternation on f69v is layout; it has no confirmed text
marker or odd/even semantics.

### 7. Renderer and source-boundary information

Wrappers, JOIN/SPACE and hierarchical gaps are modeled as rendering/placement,
but their possible reading conveniences—abbreviation cues, grouping, scope or
copying rhythm—have not been expanded into source phrasing. They should not be
silently treated as sounds or morphemes.

## Best new content theory

The Biological pages likely combine itemized entries with **categorical value
vectors**:

```text
ITEM / NEXT
  → node and associative links
  → reuse or set a reference value
  → fill one or more local categorical slots
  → exact terminal value commits each slot
```

Under this model the many close-only cells are not semantic emptiness. They may
be the densest content on the page because the stencil silently supplies the
questions.

The Herbal pages use fewer explicit cells and therefore spell out more of the
owner/property relation in opaque open cards. This explains why our current
lexicon covers Herbal content poorly without requiring a different language.

## Revised pseudo-translation

> Item: open the next form entry. Associate its marked node with the stated
> reference. For each inherited slot, enter the exact categorical value and
> validate the cell. Continue until the local vector is complete; leave any
> unresolved value open across the physical line.

Conditional medical expansion:

> Item: take the next pictured part or preparation. Relate it to the previously
> stated setting. Record the required states or results in their respective
> cells and confirm each one; continue with the next part.

## Priority after V8

The highest-yield next target is not another connective card. It is the four
recurrent terminal families with 12/10/8/8 events. The useful question is
whether they behave like distinct categorical answers in stable stencil slots
or like lexical actions/results with variable argument frames.

The second priority is the opaque Herbal-A payload, especially f56r, because it
probably contains the actual plant-specific content missing from every current
pseudo-translation.

## Conclusion

The sidequest has so far reconstructed a plausible **record language**, not
the manuscript's content vocabulary. Roughly one fifth of fixed-page events
participate in the proposed functional skeleton. Most potential meaning remains
inside exact page-local cards and terminal values, while all circle-page text
remains ungrounded.
