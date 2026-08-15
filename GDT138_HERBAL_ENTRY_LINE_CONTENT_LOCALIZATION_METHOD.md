# GDT138 — Herbal entry-line content localization

Status: `FROZEN_POST_GDT137_POSITIONAL_ABLATION_BEFORE_WINDOW_SCORING`

## Question

GDT137 found no null-surviving whole-page association between formal text bags
and 12 archived visible plant features. A coherent alternative is that the
page's identifying/content signal is concentrated in an entry line and is
diluted by subsequent prose. GDT138 tests that one positional explanation; it
does not search for a PAGE_HOST meaning.

The feature panel, nuisance variables, folio folds, and human provenance are
inherited unchanged from GDT137. Both panel and hypothesis are exposed, so
this is a post-hoc localization test.

## Frozen pages and windows

Use the 126 GDT137 Herbal pages with at least two complete source lines. Exclude
the sole one-line page f57r because FIRST and LAST are identical. Sort physical
lines by the numeric source locus suffix and create exactly four windows:

1. `FIRST_LINE` — all groups on the first retained physical line;
2. `BODY_AFTER_FIRST` — every group after that line;
3. `LAST_LINE` — all groups on the last retained physical line;
4. `ALL_PAGE` — the GDT137 whole-page integrity anchor.

No editorial paragraph marker, text value, or visual outcome selects a line.
The primary prediction is `FIRST_LINE`; LAST is a positional control and ALL
must exactly reproduce GDT137 after the f57r deletion.

## Representations and scoring

For each window run exactly three bags: `PAGE_HOST_IDENTITY`,
`PAGE_HOST_CHAR3`, and `RAW_CHAR3`. Use GDT137's seven-neighbor nuisance code,
shrink 8, leave-one-physical-folio folds, eight primary-capacity visible
features, and six cross-Currier features. Compiler-only is omitted because the
question is content localization and GDT137 already found it weaker.

Permute complete feature vectors within Currier × hand × illustration profile
in 10,000 worlds and recompute all predictions. Correct over all 12
window/representation combinations. Report per-feature and per-folio effects.

## Gates and ceiling

FIRST_LINE PAGE_HOST evidence requires the better of identity/char3 to be
positive after the 12-way selector, beat FIRST_LINE raw, beat the matching
LAST_LINE, BODY_AFTER_FIRST, and ALL_PAGE host models, be positive on at least
six of eight features and 35 of the 62 retained folios, remain positive on the
cross-Currier panel, and have max-12 `p<=.05`.

A pass would establish only page-entry localization of a visible-feature
association. It would not identify a name field or assign a semantic role,
gloss, word, morpheme, POS, sound, language, plaintext, meaning, plant
identity, or translation. Every f84 row must be rejected before retention and
no new f84 access is authorized.
