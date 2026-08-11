# Pharmaceutical root-colour native-visual ownership capacity

Date: 2026-08-11

## Purpose

Test whether source-bound native visual inspection can repair the ownership
failure in `PUBLIC_PHARMA_ROOT_COLOR_CAPACITY` without opening any Voynich
label identity. The old source-only inventory contains a balanced dark/light
root contrast but only four manually certified clear pairings, all on f100.

This is an ownership-capacity audit, not a lexical score.

## Frozen source panel

Bind:

- `results/public_pharma_root_color_candidates.tsv`, SHA-256
  `092bdfcbbf17c78da2ebd00576921a464f61cfd50bc08ee070da8def444860ec`;
- `results/public_pharma_root_color_capacity.json`, SHA-256
  `0cc6bf6b675a45c86b841d971be65c4c348f1eb789bfcec61d59b52bbc3d9909`;
- official Yale manifest
  `https://collections.library.yale.edu/manifests/2002046`.

Retain only rows with `primary_current_mapping=1`. The source-record ID,
source page/location, physical folio, frozen human root state, mapped locus,
and source pairing metadata may be inspected. Voynich surface strings,
formal roots/roles, and token identities remain sealed.

The full physical folio f88 is the disclosed layout-development folio because
f88r was inspected while defining the visual rule. The primary held panel is
f89, f99, f100, f101, and f102. All mapped candidate rows on those folios are
audited; no favourable subset may be selected.

## Frozen visual ownership grades

- `CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL`: exactly one source-indexed plant
  fragment and one short label occupy a shared local whitespace cell. The
  label is separated from competing fragments/labels by row geometry, a
  drawing boundary, or a visibly larger intervening gap; no second fragment
  is a plausible owner.
- `AMBIGUOUS_NEAREST_NEIGHBOUR`: a label is near a fragment but two or more
  owners remain plausible, labels form a shared run, or a page fold/crop
  removes the needed boundary.
- `NO_VISIBLE_CURRENT_LABEL`: the source-indexed fragment is visible but its
  mapped label is not recoverable as a distinct visual item.
- `SOURCE_LOCATION_UNRESOLVED`: the old source location cannot be mapped to
  one visible fragment without consulting label identity.

Text need not be inside a drawn box. Proximity alone is insufficient; the
whole local arrangement must isolate one label and one fragment. No glyph is
read or compared during grading.

Root colour remains the pre-existing human source state `DARK` or `LIGHT`.
Rows with a published cross-description `CONFLICT` are ineligible regardless
of visual clarity. Absence of a colour mention is never a negative state.

## Capacity gate

The hidden-label route may advance to a separately preregistered text test only
if the held panel contains:

1. at least four eligible clear pairings in each state;
2. each state on at least two held physical folios;
3. at least twelve eligible clear pairings total;
4. no single folio contributing more than 60% of eligible rows; and
5. exact source/image bindings and a source-only validator pass.

Failure stops the route before any Voynich string is opened. Passing this gate
does not authorize a favourable form search; the later statistic, null,
thresholds, and holdout must be frozen separately.

## Method and exclusions

Use only source-bound direct native inspection of the complete official Yale
canvases and deterministic IIIF regions. No OCR, automated transcription,
segmentation, object detection, CLIP, embedding, similarity score, batch image
recognition, automated plant identification, or automated colour classifier is
permitted. The observations are machine-authored, not literal human
annotation.

This audit can establish only label-to-fragment ownership capacity for a
human-described dark/light root contrast. It cannot assign DARK, LIGHT, ROOT,
a word, sound, language, cipher, plaintext, meaning, or translation.
