# GDT790 method

## Question

Can the visible layout of f77r, f82r and f83r be added to the current
hierarchical text model as an external panel-owner grammar, while preserving
all existing H1–H4, whole-word and bounded-field structures and avoiding the
failed move from mere word proximity to a single pictured owner?

## Inputs

- Three already admitted official Yale IIIF images: f77r, f82r and f83r. URL,
  pixel dimensions and reviewed SHA-256 are fixed in
  `src/IMAGE_SOURCE_SPECS.tsv`; image files are not republished.
- ZL3b line transcription from `transcription/voynich_zl3b_lines.tsv`, read
  only through `./vmanus-exp query-tsv` with three explicit page allow-values,
  seven explicit output columns and both f84/f84r forbidden prefixes.
- Manual panel/record and label/component specifications in
  `src/PANEL_RECORD_SPECS.tsv` and `src/LABEL_OWNER_SPECS.tsv`.
- The prior constraints and structures summarized in
  `src/COMPATIBILITY_SPECS.tsv`: especially GDT201, GDT260, GDT262, GDT263,
  GDT389/GDT391, GDT585, GDT590, GDT736/GDT737, GDT741 and GDT764.

All source hashes are fixed in `src/SOURCE_LOCK.tsv`. No OCR or image decoding
is repeated by the runner.

## Method

### 1. Separate prose records and graphical labels

The guarded source contains 150 loci. Twenty-seven are graphical label loci;
the remaining 123 lines form thirteen transcription-delimited paragraph
records. The manual record table maps those records to ten visible panels:
three on f77r, three on f82r, three single-figure panels plus one lower coupled
panel on f83r. The two small f83r blocks Q1 and Q2 remain embedded records under
the lower coupled panel rather than being flattened into its main prose.

### 2. Add a silent owner above the text grammar

The selected hierarchy is:

`PAGE → IMAGE_PANEL_OWNER → PARAGRAPH_RECORD → LINE/FIELD → EXACT_LABEL_ANCHOR`

The panel owner is a description of the visible configuration, not a Voynich
word meaning. Existing token order and text cells are unchanged. H1–H4
line-head tendencies and the bounded `X daiin` field cue remain below this new
layer.

### 3. Keep label ownership local

Every graphical label receives one visible component or component zone and an
explicit relation class: attachment, proximity, or ambiguous proximity. This
produces a useful occurrence-local address such as “left vertical inflow” or
“upper pool figure 2.” It does not translate the written label.

### 4. Build only exact label-to-prose edges

Each of the 28 label tokens is compared with every prose token on the three
pages. A bridge is emitted only for exact ZL3b token equality. Same-page edges
may be rendered as image-reference candidates. Cross-page edges are rendered
only as recurring label/name/formula forms. The one-character token `o` is
counted but is not an anchor. Approximate edit-distance families do not create
edges because GDT262 already showed that a topology-preserving null explains
the earlier maximum-search lead.

### 5. Preserve exploratory composition separately

Five visually motivated whole-form families are retained in
`src/IMAGE_FORM_FAMILY_SPECS.tsv`. They receive concrete working family
descriptions and rivals, but no free component, unseen-form prediction or
general renderer licence.

### 6. Render owner plus structure, not invented action prose

For each prose line the renderer prints:

1. visible panel owner and local subfield;
2. exact ZL3b line;
3. line-head class when available;
4. exact same-page image references or cross-page label-form reuse;
5. bounded `X → daiin` value-field candidates;
6. all remaining complete forms as open.

The old generic work-item/action prose and obsolete drug-part imports are not
used.

## Decision and claim ceiling

The overlay is selected if all 123 prose lines map once to the thirteen
records, all 27 label loci map once to a visible component or zone, the guarded
source materializes no f84/f84r row, exact bridges replay from the source, and
zero token meanings or prefix/root values are changed.

The result may establish an executable image-conditioned owner layer and
occurrence-local label references on these three pages. It does not establish
a plaintext translation, a Voynich lexeme, a free component meaning, a
single-word figure owner from proximity, flow direction, a unit, a substance,
or transfer to an unseen page.
