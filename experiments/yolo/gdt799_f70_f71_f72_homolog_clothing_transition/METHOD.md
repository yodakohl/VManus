# GDT799 method — label-blind homolog clothing transition

## Question

Do the 18 previously uncoded outer-ring figures on admitted f70v1 and f72r1
carry an upper-garment pattern that independently supports the fixed
f70-R0/f71-F9/f72-R0 alignment from GDT796, or is the apparent contrast a
page/ring-level drawing facies?

## Inputs

- The two already admitted official Yale canvases locked in
  `src/SOURCE_LOCK.tsv`.
- Nine complete Kluge-A positions on each new ring: A06--A13 and A15.  A14 is
  absent from the formal atlas and is not silently restored.
- The ten previously published f71v outer clothing calls from GDT796/ZCV001,
  used only after the new visual acquisition is complete.
- The fixed GDT796 mapping in
  `GDT796_OUTER10_BOUNDARY_POSITION_CONTRIBUTIONS.tsv`.

## Method

Each target is a 520x520 crop with a shuffled `Xnn` identifier.  Reviewers see
only the crop and the following closed state inventory:

- `TORSO_COVERED`: a clear bodice, tunic, or cloth boundary encloses the chest
  or upper torso;
- `TORSO_UNCOVERED`: the chest/breasts are visibly bare and no upper-torso
  garment boundary is present;
- `UNCERTAIN`: the crop, fold, damage, overlap, or faintness prevents the
  distinction.

A barrel, lower skirt/drape, isolated cuff, hair, necklace, or arm line does
not by itself cover the torso.  Two reviewers work independently.  Agreement
is accepted; a decisive-versus-uncertain split takes the decisive call but is
marked single-reader; opposite decisive calls require a disclosed
source-aware adjudication.

After unblinding, the builder reports:

1. acquisition agreement and page/ring state margins;
2. pairwise decisive matches on the nine shared A positions for f70--f71,
   f70--f72, and f71--f72 under the fixed R0/F9/R0 alignment;
3. identity and all 400 f71-by-f72 D10 alignment scores, preserving missing
   A14 rather than imputing it;
4. exact tie counts and the rank of F9/R0;
5. a page-facies diagnostic showing whether either new ring lacks within-ring
   state mobility;
6. a GDT388 header-only edge packet check.  The homologs are analyst-fixed
   correspondences, not author-drawn directed relation edges.

## Decision rule and claim ceiling

The visual acquisition is mobile only if both new rings contain at least two
decisive covered and two decisive uncovered targets.  Failure does not erase
the observations; it selects `PAGE_RING_FACIES_ONLY` and prevents a reusable
position relation.

If mobility passes, fixed F9/R0 must rank in the top 10% of the 400 transforms,
with no more than 40 tied transforms, and must beat identity to retain a
position-specific C0 relation rival.  Any other transform is descriptive only
and cannot replace the frozen alignment in this pass.

The experiment may acquire 18 visible states and say whether the fixed
alignment receives independent image support.  It cannot establish a label
owner, clothing word, social/planetary status, sex, language, sound, cipher,
plaintext clause, morpheme, component meaning, or translation.
