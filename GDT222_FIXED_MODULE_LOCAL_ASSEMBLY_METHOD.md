# GDT222 — fixed-module local-assembly test

## Question

GDT221 found no transferable top/bottom assignment when complete source
groups, PAGE_HOST strings, or source-family strings were compared as character
bags.  That is not the same prediction as the older GDT002 morphology proposal:
a small reusable module inventory may recur inside very different complete
forms.  GDT222 therefore asks whether the already proposed non-wrapper modules
`ar`, `ol`, `dal`, `dar`, `sy`, `te`, `tee`, and `dy` align the two
human-defined top/bottom label/prose assemblies on f75v and f83r.

The module list is frozen in `gdt222_module_manifest.tsv`; it was not selected
from the two assembly scores.  Matching is literal contiguous-substring
presence in the public source display.  Overlaps are retained (`tee` also
contains `te`) and no segmentation, linguistic boundary, morpheme, or meaning
is asserted.  Outer `d/s/q/o/ot` material is deliberately excluded because
this test concerns the proposed local content inventory rather than common
compiler wrappers.

## Inputs and seal

The visual assemblies are unchanged from `gdt221_assembly_manifest.tsv`.
Labels come from the f84-free GDT012 annotated inventory.  Prose comes from the
source-native GDT016 group inventory; rows on any f84 page are rejected before
retention and the selected locus whitelist contains only f75v/f83r.  No image,
new annotation, or f84 artifact is opened.

As in GDT221, strict label rows are missing for f75v.22, f75v.23, and f83r.50.
They are reported, never imputed.  All available selected prose groups are used
because module presence does not require complete HPR2 line coverage; the
complete-line restriction is retained as a sensitivity.

## Fixed scores

For each page and assembly, the scorer forms a binary set of present modules.
Similarity is Jaccard overlap.  The correct-assignment lead is

`J(label_top, prose_top) + J(label_bottom, prose_bottom)
 - J(label_top, prose_bottom) - J(label_bottom, prose_top)`.

The exact null independently swaps the two prose assemblies on each page, so
there are four worlds.  The module-level diagnostic separately asks whether a
module has the same discriminating top/bottom presence pattern in labels and
prose.  Its familywise statistic is the maximum number of supported pages over
all eight frozen modules in each of the same four worlds.  Leave-one-module-out
scores expose dependence on individual modules.

## Interpretation

This is an exposed, two-page exploratory localization test.  A positive result
may nominate a compact module as a page-local assembly discriminator and a
prospective target; it cannot supply a universal role or word.  The minimum
possible exact p-value is 0.25.  No semantic value, language, sound, plaintext,
or translation may be assigned.
