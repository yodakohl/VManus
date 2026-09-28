# GDT1071 method

## Decision note (fixed before the complete annotation query)

Unknown after RLO001 and GDT790/791: whether any of the **other 27** originally
image-reviewed pages contain a human-annotated, singularly attached local
inscription whose exact complete ZL3b form also appears in running prose. RLO001
only tested label-to-label cross-page repetition; GDT790/791 recorded exact
label-to-prose edges on the three deeply annotated f77r/f82r/f83r pages. A
new strict local-to-prose bridge would nominate a concrete, image-owned whole
for semantic reading. Zero new bridges would close this already exposed
30-page capacity route. Neither outcome alone assigns a word meaning.

Known counterexamples: all ten GDT790 edges cross panel owners, so an exact
match need not be a direct reference; RLO001's 57 singular labels have zero
cross-page label repeats. The same word may be an entry address or class.

Smallest adequate test: take only the frozen GDT791 30-page ZL3b occurrence
spine and the existing human exact-locus annotation file, excluding f1r
entirely under the current marginal-only scope. Query that mixed annotation
file **by raw `page` selector**, with the 34 source-selector allow-values for
the 29 physical pages derived from GDT791's specs, before materializing
annotation fields. A bounded `f70v`/`f70v1`/`f70v2` selector check before the
complete query found that annotations use `f70v1`/`f70v2`, so panel selectors
must be retained; that check disclosed no word or relation fields.
Do not open an image or a new transcription. For every local one-token locus,
mark strict ownership only if an annotation is UNHEDGED, OBJECT_BEARING and
has REL_EXPLICIT_ATTACHMENT, REL_DIRECT_ENCLOSURE or REL_EXPLICIT_IDENTITY.
List all eligible labels, including zero matches. Match the **exact whole**
ZL3b surface to every running event on the same physical page and the other
28 pages, retaining duplicate occurrences and panel/record fields. Keep
non-strict local labels as a descriptive comparison; do not promote them.
Report one-character matches in the full tables, but require at least two
characters for a candidate bridge because a one-character exact match has
little lexical specificity.

No p-value, whole-search control, all-reader identity, single-object prose
ownership or meaning is claimed. Alternate readings are one manuscript.
If a strict match is found, inspect its precise image and text ownership in a
separately registered follow-up, preserving the entire candidate list. The
current test decides only whether that next step has capacity.

Budget: 45 wall minutes from the first complete annotation query, including
query, implementation, independent validation, decision and publication.
At the limit stop expansion and report capacity, without widening scope.

## Inputs and implementation

GDT791 `GDT791_5866_OCCURRENCE_SPINE.tsv` SHA256
`4075ffca8e7a8b9cefda62c9ec6997fb6c518dba8f86790f5309bfe2a8574707`.
GDT791 `PAGE_SELECTOR_SPECS.tsv` SHA256
`69e5463f7ce6c22bd83fe35e4fdc0601731a3c470b5c510a15ac3befa1716bae`.
Human `existing_human_exact_locus_annotations.tsv` SHA256
`79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61`.
The runner constructs the exact `vmanus-exp query-tsv` command with repeated
`--allow` values and `--columns` before reading the resulting rows. Input
hashes are checked first. All result artifacts are derived, previously exposed
data and will retain source locators. f84/f84r are forbidden.
