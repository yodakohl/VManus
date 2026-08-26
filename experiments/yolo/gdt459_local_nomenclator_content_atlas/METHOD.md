# GDT459 method

## Question

Does GDT407's single `LOCAL_ADDRESS` bucket hide a historically plausible
mixture of productive technical/address formulae and learned nomenclator
labels? Which events can be read from the existing component deck without
forcing arbitrary long segmentations?

## Inputs

- GDT407's 4,576 running events and 693 local groups.
- GDT413's unchanged 46-component working dictionary.
- GDT441's executable factor gate for already visible recipes.
- Manual original-detail review of official Yale images for the six pages on
  which `LOCAL_ADDRESS` occurs: `f17r`, `f71v`, `f72r`, `f77r`, `f88v`, and
  `f89r`. Object IDs and reviewed-image hashes are stored per event.

## Method

1. Select all 183 GDT407 rows whose recipe is exactly `LOCAL_ADDRESS`.
2. Build an invariant surface→recipe table from the running-text stream.
3. Tier A: if a local surface also occurs in running text with exactly one
   recipe, transfer that recipe unchanged.
4. Build a surface segmenter only from unambiguous one-atom surface forms. Its
   deterministic choice minimizes the number of atoms, then prefers frequent
   forms. Calibrate it against all already parsed running surfaces before using
   it on the local set.
5. Tier B: accept a new surface when its minimal segmentation yields a recipe
   already observed elsewhere in running text.
6. Tier C: provisionally accept only a non-stopping two-atom composition, or a
   repeated local surface whose minimal recipe passes the factor reader.
7. Tier D: treat every remainder as one learned whole label and assign only the
   class visibly licensed by its owner: pictured plant, star-bearing ring
   position, bath/outlet station, or drug/ingredient object.
8. Bind every decision to source order, owner, image object and image hash;
   publish event-, surface-, and owner-level tables.

## Decision rule and claim ceiling

Tier A is the strongest working evidence because exact surface identity and an
invariant recipe agree across prose and label contexts. Tier B transfers an
attested recipe under a new surface. Tier C is explicitly provisional. Tier D
is a learned nomenclator class, not an undecoded formula.

The unrestricted segmenter recovers only 442/761 (58.08%) already known
running recipes, so an arbitrary long parse is never promoted merely because
it exists. Even when the predicted recipe has another surface, calibration is
185/253 (73.12%), useful but not decisive.

This experiment predicts no new surface, adds no page, changes no core meaning,
and confirms no Voynich lexeme, plaintext, language, or individual object name.
