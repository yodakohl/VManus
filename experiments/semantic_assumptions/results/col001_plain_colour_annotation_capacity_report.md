# COL001 plain-colour annotation capacity

## Result

**Provisional record-level lead; stop before lexical scoring.**

The human-curated writing inventory at
<https://www.voynich.nu/writing.html> currently lists 13 `COL` records on ten
pages. Twelve are classified as Latin/plain-alphabet (`L`); exactly one is
classified as Voynich script (`V`). The strongest contextual records are:

| folio | human reading | physical relation | readable value |
|---|---|---|---|
| f1v | Latin `g` | under green paint in a leaf | possible green initial |
| f4r | Latin `rot` | written vertically in the plant stem | German *red* |
| f7r | probable Latin `rot` | under paint in the left root | probable German *red* |
| f2r.15 | Voynich `ios an on` | inside the bottom-right leaf and under green paint | unknown |

Other plain-alphabet `COL` records include tentative letters under blue paint
on f9v and single or uncertain letters on f1v, f2v, f20r, f29r, f32r, and
f99v. They strengthen the existence of a production-annotation layer but add
no second Voynich-script observation. The f2r record is the catalogue's only
`COL` candidate written in Voynich script. Alternate human readings ZL3b and
RF1b agree exactly on `ios an on`; IT2a has no row.

The closest documented contemporary comparator, fifteenth-century Vicenza
MS 362, uses German colour names and single-letter colour initials. It supports
the production practice but supplies no equivalence for the three-unit f2r
surface. In particular, similarity of physical function is not a bilingual
mapping.

The current grammar parses it structurally as `i+os | a | o`, with three bare
units. `ios` and `on` occur nowhere else in the complete ZL/RF locus atlas;
`an` occurs at 15 physical loci across several sections, including the ordinary
prose line f2r.12 on the same page. It is therefore not a green-specific form.

Its formal shell is not itself an instruction marker. The exact
`BARE+BARE | BARE | BARE` shell occurs at five physical loci spanning prose,
label, and radial text, while the broader three-word all-`BARE` class occurs
at 37 physical loci. Context, not this grammar shell, is the only evidence for
a production-instruction function.

The strongest defensible partial reading is therefore:

> `f2r.15` may be a pre-paint instruction associated with a green leaf.

This is a function-and-context candidate, not a translation. The source does
not establish that the phrase means GREEN, which unit would carry a colour
value, whether it names a pigment or an action, or whether the painter obeyed
the note. It also does not establish that the plain-alphabet notes were written
by the main-text scribe or that the main text is German. A copied exemplar
annotation and a non-colour label remain viable.

## Capacity stop

There is only one Voynich-script under-paint candidate with a readable colour
context. The remaining catalogue marks are plain-alphabet notes, single
ambiguous letters, or uncertain readings. Consequently there is no replicated
Voynich-script contrast, no negative class, and no fair lexical statistic.
Do not mine shared substrings from f4r/f7r prose or assign `ios`, `an`, `on`,
`i`, `os`, `a`, or `o` a colour gloss.

The only local near-miss was checked explicitly. The older Stolfi comment for
f99v.45 asks whether tiny apparent letters under reddish paint are even real
and tentatively transcribes `qo???`. ZL3b, IT2a, and RF1b all omit that locus;
the current human catalogue instead classifies it as plain alphabet and reads
a single possible `p` or `r`. It therefore cannot serve as an authenticated,
readable second Voynich-script observation.

Reopen only if another provenance-clean human source supplies a second
Voynich-script note physically under paint with an independently readable
colour, or the same complete phrase under another green-painted part.

## Local evidence

- `results/existing_human_page_annotations.tsv`: f1v and f2r human page notes.
- `results/existing_human_exact_locus_annotations.tsv`: f2r.15 is an unhedged
  exact-local label within a leaf.
- `results/pre_grounding_interlinear.tsv`: exact ZL3b/RF1b surface and formal
  parse; IT2a absent.
- `transcription/sources/Stolfi_text25e1-52.evt`: hedged f99v.45 near-miss.

No OCR, automated image recognition, pixel feature, or machine-generated
visual label was used.

Human-source comparator: René Zandbergen, *Voynich 100* presentation (2012),
pp. 13--14, <https://www.voynich.nu/papers/Voynich100_RZ_2012.pdf>.
