# GDT812 post-result correction: the f72r image binding

Date: 2026-09-05. Post-result exploratory provenance correction, not a new
experiment, preregistration, translation result, or page admission.

## Primary metadata resolves the side error

The [official Yale manifest](https://collections.library.yale.edu/manifests/2002046)
was inspected directly as metadata, without opening the f72v image body:

| Canvas | Official label | Native dimensions | Consequence |
|---|---|---|---|
| 1006203 | 71v and 72r | 8865 x 3018 | Correct parent image for the f72r panels |
| 1006204 | 72v (part) | 5976 x 3794 | Cannot authenticate f72r visual claims |
| 1006194 | 67r | 4972 x 3738 | A two-panel spread, not an isolated f67r2 image |

The fetched manifest SHA-256 is
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
This agrees with the previously registered manifest object; the discrepancy
is an inherited side/selector binding error, not newly changed Yale metadata.

## Exact affected chain

- `experiments/yolo/sidequest_semantic_four_page_template_transfer_one_thousand_eighth/build_one_thousand_eighth.py`,
  image specification at lines 69-75, binds `physical_page=f72r` to `1006204`.
  Its `PASS1008_IMAGE_MANIFEST.tsv` repeats that binding and the visual claim
  about concentric figure/star wheels without a visible start or direction.
- `experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/VISUAL_BATCH_SPECS.tsv`
  makes that PASS1008 image manifest the f72r visual-review source.
  `src/PAGE_TOPOLOGY_SPECS.tsv` assigns f72r `DIRECT_PAGE_CONTEXT`,
  `RADIAL_ARRAY`, and the corresponding coarse ring/figure/star description.
  `artifacts/GDT791_30_PAGE_EVIDENCE_REGISTRY.tsv` confirms the same source.
- `experiments/yolo/gdt811_four_page_content_synthesis/src/VISUAL_SOURCES.tsv`
  again identifies f72r with `1006204`, marked previously released/personally
  viewed. Its `REPORT.md` calls all four physical pages inspected and combines
  f72r member/status inscriptions with other content. `WORKING_THEORY.md`,
  section "f72r: members of a diagram, not literal treatment subjects", also
  discusses repeated star-bearing figures and their local label contexts.

Quarantine f72r visual authentication through this specific chain, including
its whole-foldout review claim and absence-of-start/direction claims. A correct
hash of the wrong-side image does not repair the binding. Broad radial/member
descriptions can remain hypotheses or be supported by a separately correct
source; they must not cite 1006204 as f72r evidence.

Do **not** discard the separately selector-bound f72r1/f72r2/f72r3 text,
all-reader strings, C/L distinctions, or exact text-identity counts. GDT811's
10 circular-text loci/288 tokens and 74 local loci/96 tokens are text counts,
not observations of 1006204. Its f72r2.22 spelling edges likewise do not
become false merely because this visual binding is wrong; their graphical
attachment was not established by string identity in the first place.

## Correct source and actual present inspection

GDT585 already records correct canvas `1006203` in
`experiments/yolo/gdt585_learned_name_compound_atlas/artifacts/gdt585_4_manual_image_cards.tsv`.
This audit viewed a pre-existing f72r3 crop and then the corresponding
[right-hand target crop from 1006203](https://collections.library.yale.edu/iiif/2/1006203/pct:69,0,31,100/1600,/0/default.jpg).
That crop excludes the left-hand neighboring diagrams but clips part of the
target diagram's leftmost arc. It supports the inspected f72r3 target region,
not a new claim to have visually checked every f72r1/f72r2/f72r3 inscription.
The complete neighboring text arrays were separately read through the guarded
TSV interface with only f67r2/f72r3 allowed and f84/f84r explicitly forbidden.

Recorded/measured image hashes (different renderings are different objects):

| Object | SHA-256 | Audit status |
|---|---|---|
| PASS1008/GDT811 1006204 full/2000 image | `46c961644e15d06a76bc4f7a6d209963edb4875ba8d0a802e255d4733c4154f0` | Inherited record; image not reopened |
| Prior 1000 x 635 cache named for f72r | `9eb3a87df512ffda8fd4c92b549a978f866724445edd368e30d5f053a38fe8dc` | Local bytes hashed only, not viewed in this audit |
| Pre-existing 1400 x 1792 f72r3 crop | `4dbe4522a0a988c1921294c4b1deda4ba0b5a17d587571b5e138f113e46de7de` | Viewed; source content checked against correct canvas |
| Current linked 1006203 target crop | `12d4cac3609b4408419e60121e8b71acd2f48724bb65f71d4c45d36f1d0141f9` | Official source fetched and viewed |

The f72r3.9 inscription lies in the outer star-bearing-figure band, separately
from continuous ring text. Its position is not a leader line or a unique
assignment to person, star, date, or property. No visible scale makes an
intensity or numerical interpretation decidable. ZL3b/IT2a have two wholes
`oteey daiin`; RF1b has the fused `oteeydaiin`. Preserve that boundary rival.

## Admission and incidental exposure accounting

No additional page was admitted. No 1006204/f72v image body was opened in this
audit; its old exposure does not silently extend present selector scope.
The cached file named f67r2 unexpectedly showed the complete 67r spread when
viewed. Incidental f67r1 exposure is disclosed and excluded: no f67r1 text was
queried, analyzed, or used as evidence. Subsequent f67r2 inspection used only
the [right-panel source region](https://collections.library.yale.edu/iiif/2/1006194/pct:51,0,49,100/1500,/0/default.jpg).
No new ray-count, angle decoder, or member/day identification was attempted.
No source image or private cache path is redistributed. The old hash-bound
files remain unchanged; this memo is the forward correction authority.
