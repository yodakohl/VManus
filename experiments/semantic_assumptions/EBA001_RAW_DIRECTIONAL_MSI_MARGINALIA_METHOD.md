# EBA001 raw multi-exposure MSI marginalia acquisition

Date frozen: 2026-08-13

## Why this is a new observable

The completed public-MSI worth screen inspected processed colour composites.
NVA002 subsequently enumerated the public raw-TIFF folders without opening a
TIFF body. This experiment does not rerun the processed-image anchor screen. It
tests a property absent from a single processed composite: whether the same
faint mark is independently present in three separately timed public 16-bit
TIFF capture products whose filenames contain `MB365UV`.

Before this method was written, HTTP range requests of 1 MiB were used to
confirm that the six named objects were accessible TIFF files and to measure
their byte sizes. No pixels were rendered or visually inspected. This preflight
exposure is recorded rather than hidden; all files, targets, and the initial
scientific question were frozen before a complete image body was acquired or
viewed.

## Primary question and post-acquisition correction

For the mixed-script marginal material already localized on f17r and f116v, is
the visible trace repeatably present in the individual source capture products, or is it
confined to one capture or introduced by processed-image production?

This distinguishes only:

- `H_SOURCE_CAPTURE_STABLE_TRACE`: the same dark trace occurs at corresponding
  apparent manuscript coordinates in each separately timed source capture;
- `H_SINGLE_CAPTURE_OR_PROCESSING_ARTIFACT`: the trace is absent from one or
  more source captures or exists only in a processed composite.

The initial preregistration described the files as opposing or combined
illumination and proposed an absorptive-mark versus relief decision. Inspection
of the public filenames and TIFF metadata showed that they do not document the
physical role of exposures 007, 029, and 037. Independent audit therefore
narrowed the decision before publication. Persistence proves neither
absorption nor ink and does not reject every fixed-relief mechanism.

The corrected test does **not** distinguish ink, a stain, fluorescence deficit,
fixed surface relief, or another material response. It does not date the mark,
identify its writer, read it, or show that adjacent scripts are a gloss. A
repeatable source-capture trace is a prerequisite for later chemistry, chronology, or
palaeographic work, not a translation.

## Frozen public objects

Credit: The Lazarus Project and the Chester F. Carlson Center for Imaging
Science at RIT; manuscript witness Beinecke MS 408. Folder release:
`https://drive.google.com/drive/folders/1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig`.

Only these six public 16-bit TIFF capture products were opened:

| folio | filename | Google Drive file id | registered exposure |
|---|---|---|---|
| f17r | `Voynich_17r+MB365UV_007_F.tif` | `13Qxw2IvaYgprVPE-mb5RWDeCN-LxdtN1` | 007 |
| f17r | `Voynich_17r+MB365UV_029_F.tif` | `1tjUlqHFFYOoP7wXhMSevC-MsDc4NqZ9Q` | 029 |
| f17r | `Voynich_17r+MB365UV_037_F.tif` | `1PVcYQimUWy49xJd1XL7jWFxGGCzNAtw4` | 037 |
| f116v | `Voynich_116v+MB365UV_007_F.tif` | `1fFFH6lVG7UgwSj49CdI_JqsBHdhplnQX` | 007 |
| f116v | `Voynich_116v+MB365UV_029_F.tif` | `12txJIKIYVWSmaTrqX9KThj8fRMwtJQtE` | 029 |
| f116v | `Voynich_116v+MB365UV_037_F.tif` | `1n_woSHJebH1oPN67y5a5mAxao-QWtAlf` | 037 |

No directional or combined-light identity may be inferred. Gross
mounting-shadow change is descriptive context, not a claim about local lamp
direction or the trace's physical mechanism.

The file bytes are acquired into a fresh temporary directory outside the
repository. Source URL, byte count, SHA-256, TIFF dimensions, sample depth, and
TIFF metadata are recorded before rendering. TIFF bodies and crops are never
committed.

## Fixed targets and deterministic crops

Targets come from prior official ordinary-light localization, not favourable
MSI appearance:

1. f17r: the complete faint upper marginal line, retaining the registered
   mixed-script context;
2. f116v: the initial mixed-script span of the lowest of the four principal
   marginal lines: the two previously registered manuscript-style groups
   followed on the same approximate baseline by adjacent plain-script-looking
   strokes. Its continuation is truncated by the right context-crop boundary.

The native source context boxes are f17r `800,1600,1000,4100` followed by
`ROTATE_270`, and f116v `6200,700,1976,2900` followed by `ROTATE_90`. In the
oriented contexts, the target ROIs are respectively `850,80,2500,300` and
`1120,1170,1780,320` (`x,y,w,h`). The gross-shadow context ROIs are
`900,0,2300,160` and `500,250,1900,500`. These retain page-edge/mounting
features as a descriptive moving-shadow control, not a local relief control.
The positive-dark reference ROIs are `850,100,650,260` and
`1500,500,1350,350`.

For display, each full image's 0.5th percentile maps to black and its 99.5th
percentile to white with linear clipping. There is no gamma, local contrast
enhancement, denoising, learned method, or silent registration. Crop extraction
and lossless orientation are deterministic and every derived PNG hash is
recorded outside the repository.

Native visual inspection records separately for each capture:

- target and positive-dark-reference state:
  `VISIBLE_DARK`, `NOT_VISIBLE`, or `UNRESOLVED`;
- gross-shadow ROI state: `CAPTURE_SPECIFIC_PATTERN`,
  `NO_CAPTURE_SPECIFIC_PATTERN`, or `UNRESOLVED`;
- source and derived-crop hashes and coordinates;
- a neutral description with no proposed reading.

The exact folio-level aggregation is
`PERSISTENT_AT_CORRESPONDING_COORDINATES` plus
`MULTI_EXPOSURE_STABLE_DARK_TRACE` only when all three target states are
`VISIBLE_DARK`; the mechanism remains `UNRESOLVED`.

No OCR, transcription, glyph classifier, CLIP, embedding, image similarity,
decoder, language fit, or semantic model is permitted.

## Corrected decision

- `MULTI_EXPOSURE_STABLE_DARK_TRACE`: the same trace is visible at the same
  corresponding apparent manuscript coordinates in all three file-labelled `MB365UV`
  captures.
- `SINGLE_CAPTURE_OR_PROCESSING_COMPATIBLE`: it is missing or spatially
  inconsistent in any source capture.
- Otherwise: `UNRESOLVED`.

A stable result rejects the single-capture and processed-composite-artifact
alternatives for that trace. It does not reject all fixed-relief explanations.
The other two states stop this public-data route.

## Required output and ceiling

Publish a source inventory, observation TSV/JSON, compact report, deterministic
metadata/acquisition and crop-rendering scripts, and a record-integrity
validator. Never publish the large TIFFs or derived crops. The validator binds
the published record but does not repeat visual judgment without the raw
bodies. The strongest possible claim is that a specified marginal trace is
repeatably visible in three individual source TIFF captures. No physical
mechanism, character, word, sound, language, cipher, plaintext, gloss, meaning,
or translation follows.
