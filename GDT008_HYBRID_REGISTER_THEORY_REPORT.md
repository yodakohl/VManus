# GDT008 hybrid procedural-register theory

Status: **SELECTED EXPLORATORY WORLD MODEL — HPR-1**

## Best current overall theory

**Voynichese is an abbreviation-rich technical register: page-local,
natural-language-derived stems are inserted into line-bounded record fields,
then rendered with notation-like left scope/mode operators, right state and
closure codes, and optional joined or detached spelling.**

This is not ordinary continuous prose, but it is not a pure arbitrary code
either. Its cores can preserve lexical or mnemonic material while its visible
surface is dominated by a manuscript-specific field grammar. Labels are the
most contracted form of the register; paragraph lines are expanded
serializations of the same machinery.

The theory is called **HPR-1: Hybrid Procedural Register**. “Procedural” means
that lines serialize ordered technical fields; it does not assert that every
line is an imperative or recipe.

## Why this theory wins the abductive comparison

| rank | architecture | weighted fit | complexity penalty | net score | decision |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | HYBRID_REGISTER | 31.0 | 4.0 | 27.0 | SELECTED_LEADING_THEORY |
| 2 | SEMANTIC_TECHNICAL_NOTATION | 26.5 | 2.5 | 24.0 | RETAINED_AS_RIVAL |
| 3 | COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE | 20.0 | 2.0 | 18.0 | RETAINED_AS_RIVAL |


The score is deliberately post-hoc and is not statistical evidence. Pure
compressed language explains free/bound reuse and directional adjacency, but
handles the line reset, repeated stock forms, metadata-sensitive surface, and
failure of every direct language decoder poorly. Pure notation explains those
features but handles split/join fluidity, pervasive free forms, and the shared
cross-Currier directional construction less naturally. HPR-1 pays extra
complexity for two layers, yet explains both sets with one renderer.

## Explicit generator

```text
MANUSCRIPT := shared construction graph + REGISTER_RENDERER
PAGE       := choose DOMAIN and page-local CORE inventory
PARAGRAPH  := choose INIT or CONTINUE state
LINE       := ENTRY_STATE FIELD+ ; reset coordinate at newline
FIELD      := OUTER_SCOPE? LOCAL/CARRIER? CORE+ RIGHT_STATE? CLOSURE?
SURFACE    := join or detach adjacent components under boundary renderer

OUTER_SCOPE  := q | empty
ENTRY_STATE  := t | d | s | expanded entry form
LOCAL        := d | s | o | ot | ch | sh | ...
CARRIER      := che | related ch/sh frames
CORE         := AR | OL | AI/AII grades | page-selected root
RIGHT_STATE  := DAL | DAR | SY | related terminal class
CLOSURE      := DY | Y | related terminal closure
```

The renderer is probabilistic and conditioned by Currier, page, line position,
layout kind, and neighboring fields. Therefore the context mixer can beat a
rigid morphology grammar without making the underlying fields unreal.

## Historical plausibility

HPR-1 requires no modern cryptographic machinery. A late-medieval practical
compiler could combine abbreviated vernacular or learned stems, conventional
carrier marks, compact tabular/caption fields, and expanded prose-like
serializations. A private technical register also explains why a competent
reader might recover whole field bundles while modern language models fail on
the visible layer. This is an analogy to manuscript practice—not an
identification of a source, region, language, or profession.

## Provisional functional dictionary

These are latent functions, not translations:

- **q-**: outer dependent/current-frame wrapper—roughly “interpret this form
  under the active record frame.”
- **t / d / s at entry**: initialize versus two continuation modes.
- **bound d- / s-**: active/process-like versus state/reference-like local
  mode. This polarity is deliberately speculative.
- **o- / ot-**: unmarked versus expanded local frame; weak because the parse
  competes with `o + TE`.
- **che-**: explicit value-field carrier. `ch/sh` are related carrier modes.
- **AR**: relational/process anchor; **OL**: entity/material/reference anchor.
  Thus AROL is a generic relation-to-reference construction, not “water.”
- **AI/AII+N**: ordered parameter grades, without assuming numbers.
- **TE/TEE**: short/expanded internal graphic grade, not a secure free core.
- **DAL/DAR**: contrastive result or argument settings.
- **SY**: secondary/exception status.
- **DY**: default/completed result-state closure.
- **source space/JOIN**: expansion versus contraction of adjacent fields.

## Representative parses

| locus | surface | provisional parse | abductive reading | caveat |
| --- | --- | --- | --- | --- |
| f103r.12 | `otedy` | `[O:local-frame][TE:internal-grade][DY:closure]` | unmarked framed value, default/closed state | [OT:marked-frame][E:core][DY] |
| f103r.15 | `qotedy` | `[Q:outer-scope][O][TE][DY]` | same framed value under dependent/current scope | [Q][OT][E][DY] |
| f103r.16 | `oteedy` | `[O][TEE:expanded-grade][DY]` | expanded internal grade with the same closure | [OT][EE][DY] |
| f103r.45 | `qoteedy` | `[Q][O][TEE][DY]` | scoped expanded-grade counterpart | [Q][OT][EE][DY] |
| f82r.35 | `darol` | `[D:active-mode][AR:relation][OL:reference]` | active relational-reference record | [DAR:right-state][OL] |
| f83r.51 | `darolsy` | `[D][AR][OL][SY:secondary-status]` | active relational-reference with marked secondary status | [DAR][OL][SY] |
| f83r.50 | `saroldal` | `[S:state-mode][AR][OL][DAL:result-setting]` | state/reference counterpart with alternate result setting | ZL3b [S][AS][OL][DAL] |
| f75v.32 | `daldy` | `[DAL:result-setting][DY:closure]` | stock setting-plus-closure formula | [D][AL][DY] |
| f75v.22 | `daldy` | `[DAL][DY]` | second stock-form occurrence with reading-sensitive closure | IT2a [DAL] |
| f99v.8 | `arol` | `[AR][OL]` | bare relational-reference compound | opaque AROL remains possible |
| f102v2.14 | `sarol` | `[S][AR][OL]` | state/reference rendering of the same compound | [SAR][OL] |
| f80v.41 | `ar | ol / arol` | `[AR] <BOUNDARY_RENDERER> [OL]` | one latent compound with expanded or contracted serialization | two collocated independent fields |
| f100r.25 | `cheol` | `[CHE:explicit-value-carrier][OL:value]` | explicit reference/value field | opaque CHEOL remains possible |


The `otedy/qotedy` and `oteedy/qoteedy` grids are the cleanest illustration:
the same internal grade and closure survive addition of outer `q`. `darolsy`
and the reading-sensitive `saroldal` show a different local mode and terminal
state around shared AR+OL material. `ar | ol` versus `arol` makes the renderer
visible directly.

`daldy` is especially informative under HPR-1. It occurs in 13
all-reading-exact physical groups and also appears twice among f75v's labels,
although one of those two is IT2a-sensitive. It behaves better as a stock
setting-plus-closure formula than as the name of two different figures. The
same form's prose recurrence is expected if labels are compressed record
fields rather than a separate vocabulary.

## What HPR-1 explains at once

1. **Free/bound reuse:** macros and abbreviated stems may occupy their own
   field or be contracted into a neighboring field.
2. **Split/join spellings:** visible spaces are renderer choices over a latent
   field sequence, not necessarily word boundaries.
3. **Right-edge DY:** a closure/status code naturally occurs across many
   otherwise unrelated cores and can also be written alone.
4. **Productive q+X:** scope is outside the local value and therefore combines
   with multiple right states.
5. **Line reset:** every line serializes one record/utterance from entry state
   toward values and closures, then starts a new record.
6. **Page coherence:** the page selects its technical core inventory.
7. **Currier effects with shared grammar:** Currier profiles change the
   renderer and favored carriers while preserving abstract field order.
8. **Dense labels:** captions suppress optional boundaries and carriers,
   yielding more multi-module groups and fewer standalone pieces.
9. **Extreme local compatibility:** reusable field values create many edit
   rectangles; renderer priors also make them look like generic string
   regularity, explaining GDT003's weak precision.
10. **Failed language/cipher mappings:** the surface is neither plaintext nor
    a stationary substitution. A decoder must infer page lexicon, register,
    record schema, and boundary rendering jointly.
11. **Failed simple visual meanings:** AROL-like structures encode relation or
    record function and can accompany apparatus, figures, and plants without
    naming any of them.
12. **Q20 OPEN failure:** an entry field need not lexically predict its body;
    both can be generated from a page schema and record state.

## Awkward observations

- The global nonsemantic context mixer still compresses better than every
  explicit semantic/language model. HPR-1 has not yet supplied a competitive
  complete encoder.
- The literal q plus DY/DAL/DAR subsystem is worse than strong string
  baselines in nested held-folio prediction. Its functional interpretation is
  therefore abductive, not independently predictive.
- Many edge operations are order-dependent, and TE/TEE segmentation is
  particularly ambiguous.
- Visual associations are weak and page-confounded; no core has a secure
  referent.
- Currier A/B may reflect more than rendering—different scribes, source
  strata, or generating processes remain possible.
- A purely synthetic templatic generator could imitate much of HPR-1. The
  cross-Currier directional relation rules out one fixed Timm generator, not
  all synthetic alternatives.

## Novel frozen predictions

Ten predictions are frozen in `gdt008_novel_predictions.tsv`. Four concern the
still-sealed f84r formal payload: increased label contraction, at least one
q-by-right-state partial grid, greater sharing of terminal class than exact
core among repeated labels, and opposing within-line biases for entry versus
closure classes. Six nonholdout predictions test boundary asymmetry, daldy
line position, register collapse, q versus d/s interactions, label/prose JOIN
choice, and page-versus-register information decomposition.

They are predictions of the constructed world model, not prerequisites for
allowing the theory to exist. None was used in the architecture score.

## Conclusion

HPR-1 is the strongest present generative explanation because it treats the
Voynich surface as a **technical register compiler**, not as ordinary words
and not as an arbitrary lookup code. Page-local stem material supplies domain
content; a shared field grammar supplies order; left operators scope or select
record mode; right modules encode state/closure; and the renderer decides how
much to join, detach, or abbreviate.

This pass deliberately chooses that theory. It is concrete enough to generate
forms and risky predictions, but its proposed functions remain exploratory.
f84r has not been opened.
