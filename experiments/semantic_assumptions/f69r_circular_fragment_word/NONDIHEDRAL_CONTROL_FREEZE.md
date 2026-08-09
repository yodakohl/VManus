# F69C001 post-hoc non-dihedral control freeze

Status: **REGISTERED AFTER TARGET EXPOSURE — CORRECTS AN INVALID FIXTURE**

## Error found

The frozen misaligned-reading fixture assigned IT2a slot `i+1 mod 6` to slot
`i`. That is a rotation of the six-cycle. Because F69C001 explicitly quotients
all rotations and reversals, this transformation preserves every circular
adjacency and belongs to the target's 12-member dihedral symmetry class. It is
not a valid adjacency-destroying negative control.

The original F69C001 nonconfirmation remains unchanged: it failed independent
reading and deletion gates before the subsequent human glyph QC. The invalid
fixture may not be removed post hoc to upgrade that experiment.

## Exposed sensitivity motivating the correction

In the explicitly post-hoc sensitivity where only IT2a f69r.49 changes from
stored `em` to human-QC-preferred `ed`, the combined and all individual orbit
ranks are 1/60. The six deletion ranks become `1,1,2,2,2,2` of 12. Thus all
primary and deletion gates pass. The cyclic fixture remains rank 1 precisely
because it is a symmetry, not because it supplies a meaningful veto.

## Frozen exhaustive corrected control

No model is refit for a relabeling. Starting from the `ed`-resolved sensitivity:

1. Compute the frozen 720 orientation z-scores once for each reading.
2. Enumerate all `6! = 720` bijections assigning the six IT2a chunk surfaces
   to the six physical slots.
3. Identify the 12 rotations/reflections of identity with the same canonical
   dihedral function used by F69C001. These are declared hypothesis symmetries
   and excluded from the negative panel.
4. For each of the remaining **708 non-dihedral relabelings**, permute the IT2a
   orientation-score table algebraically, leave ZL3b and RF1b unchanged, and
   recompute the three-reading minimum-z / maximum-orientation target-orbit
   inclusive rank.
5. Report the complete rank histogram, rank-vector SHA-256, number and fraction
   attaining rank 1, and the observed physical alignment's rank.

The corrected control is specific only if the observed physical alignment is
rank 1 and at most 35 of 708 non-dihedral relabelings (at most 5%) also attain
rank 1. A separate implementation must reconstruct the permutation action,
symmetry exclusions, all ranks, digest, and decision.

## Claim ceiling

A specificity pass would retain only a **strong post-hoc structural lead**:
the physically adjudicated six-cycle is more ordinary-word-like than almost
all adjacency-breaking cross-reading relabelings under this one model. It
cannot confirm F69C001, choose a start or handedness, emit a joined surface,
or establish a sound, word, root, lexeme, language, plaintext, direction name,
or translation. Confirmation would require an independent author-visible
target fixed before scoring.
