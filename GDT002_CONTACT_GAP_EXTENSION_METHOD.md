# GDT002 contact/gap complete-unit extension

Status: **REGISTERED BEFORE NEW TARGET-REGION REVIEW**.

This exploratory extension asks whether the crop-review states from the failed
three-folio acquisition can be turned into a four-folio, complete-unit panel.
It does not assign semantic roles and does not reopen the failed f89 panel.

## Frozen panel

Three calls complete the previously sampled units:

- f99v/L2: add f99v.16 and f99v.19 to the four frozen calls, producing the six
  source-mapped loci f99v.15-.20;
- f100r/L2: add f100r.6 to the five frozen calls, producing the six
  source-mapped loci f100r.6-.11. The formal reading at f100r.6 is
  alternative-bearing and must later be marginalized, never silently deleted.

Two source-nominated units are reserved as whole-folio transfer panels:

- f88r/L1: f88r.2-.6;
- f102v1/L1: f102v1.2-.6.

The thirteen new calls and their order are frozen in
`gdt002_contact_gap_extension_selection.tsv`. The nine existing f99/f100 calls
remain frozen by the hashes of the prior observation and result artifacts.
The failed f89 panel remains reported and excluded; no row may be added to
rescue it.

## Census before judgment

An exact-locus table is not by itself a census of visible inscriptions. A
source-aware localizer must inspect each complete unit before making any
CONTACT/GAP judgment and record one of:

- `EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_ANNOTATED_UNIT`;
- `EXTRA_UNMAPPED_INSCRIPTION`;
- `UNCERTAIN`.

This is particularly material for f88r/L1: its historical comment says six
labels alternate with five plants although only five exact current loci are
mapped. f102v1/L1 has five exact loci but no independent numerical
completeness statement. If either transfer unit is not securely exhausted by
the five frozen loci, the acquisition stops before randomized review and no
formal comparison may run. The same census is recorded for f99 and f100.

## Localizer and reviewers

The source-aware localizer receives page, locus, frozen ordinal, and official
full image. They create exact context and target boxes and the census record,
but make no CONTACT/GAP call.

Two reviewers independently receive only randomized crop IDs, marked target
crops, and this rubric:

- `CONTACT`: at least one target-writing stroke visibly touches or overlaps a
  drawn non-writing contour;
- `CLEAR_GAP`: visible background separates every target-writing stroke from
  the nearby drawn contour;
- `UNCERTAIN`: localization, fading, overlap, damage, or geometry prevents a
  secure binary call.

The reviewers receive no folio, locus, catalogue comment, transcription,
formal family, object name, discovery/transfer flag, or each other's calls.
Disagreement becomes `UNCERTAIN`; there is no full-page or text-informed
adjudication. All new calls are `AI_DIRECT_VISUAL_OBSERVATION`.

No OCR, automated segmentation, object detection, image embedding, image
classifier, or other automated vision is allowed.

## Visual gates

The f99 and f100 complete units are discovery. f88 and f102 are whole-physical-
folio transfer units. Each of the four units must independently contain:

- at least one consensus `CONTACT`;
- at least two consensus `CLEAR_GAP`;
- zero `UNCERTAIN` calls.

Failure of either fresh transfer folio yields `STOP_NO_REPLICATION`. Failure of
either completed discovery unit yields `STOP_DISCOVERY_CAPACITY`. In either
case the process stops before formal features are joined.

Prior repository and image exposure is disclosed: these folios are not
observer-pristine. The new procedural observable is the independently graded,
complete-unit CONTACT/CLEAR_GAP panel, not pristine manuscript access.

## Frozen conditional formal test

This section is activated only if all visual gates pass. It is frozen now so
the construction channel cannot be chosen after seeing the new calls.

The only latent states are anonymous `R0` and `R1`, corresponding mechanically
to the two registered visual calls. They are not OBJECT, PROCESS, MATERIAL, or
any other semantic role.

Allowed source-native formal features are:

- total modeled-symbol count and group count, used only as nuisance/conditioning
  variables;
- unordered STA-family histogram;
- synchronized boundary-count and boundary-type profile.

Forbidden predictors include ordered family sequence, exact member identity,
root, literal surface, locus, page, folio, object identity, catalogue class,
legacy carrier/parser semantics, and preferred-edition selection. ZL3b, IT2a,
and RF1b remain alternate readings of one object. f100r.6 must be marginalized
over its frozen lattice alternatives with their observation costs.

Fit two Dirichlet-multinomial construction-profile distributions on complete
f99 and f100 only, conditional on length/group count, and compare them with a
matched state-blind construction model receiving the same information.
Evaluate without refitting on f88 and f102. The exact null enumerates
within-array state permutations preserving each array's observed state counts.
The formal test passes only if held codelength gain is positive on both fresh
folios, joint exact p <= 0.05, and the sign survives a length/group-count-
matched null. All smoothing and selector costs must be fixed from discovery
only and reported explicitly by a later solver preregistration/result.

## Claim ceiling

Even a pass would support only a transferable anonymous physical-relation /
source-native-construction constraint. It would not establish ownership,
object class, semantic role, lexeme, POS, sound, language, plaintext, meaning,
or translation. A visual-gate failure supports no formal inference at all.
