# CRE001 — page-specific circular-to-label construction echoes

Status: **REGISTERED_UNSCORED**

## Question and novelty

Do IVTFF label (`L`) groups reuse short source-native constructions found in
the circular (`C`) text on the same page more than in circular text on other
pages of the same physical folio?

This is not the closed duplicated-zodiac cross-role test. That experiment
forbade same-page comparison and asked whether two public duplicate-sign
relations were exceptional across pages. CRE001 tests page-specific
within-page echo under complete same-folio reassignment. It uses no sign name,
figure attribute, inferred object ownership, image proximity, or circular
start/direction.

## Frozen panel and inputs

- `results/circle_crossrole_echo_capacity.json` fixes 16 pages on five
  physical folios, after excluding the sole no-control singleton f69r.
- Every target page has both `C` and `L` material in all three manual readings
  and at least one different same-folio C page.
- The primary complete synchronous orbit has 138,240 within-folio mappings.
- The mandatory zodiac-only sensitivity has 12 pages/four folios and 5,760
  mappings.
- `results/source_sta_group_alignment.tsv` supplies source-native STA-family
  strings; `results/source_separator_transcription.tsv` supplies source-group
  identity and IVTFF role.
- Only rows with zero alternative sites enter. ZL3b, IT2a, and RF1b are
  alternate readings and are scored separately.

No retained parser root/role, OCR, automated vision, English gloss, exact sign
identity, label-to-figure assignment, object attribute, or historical word
list may enter.

## Frozen representation

For each source group, take contiguous STA-family n-grams internally; never
cross a source separator. Use exactly family trigrams and family four-grams.

For an L-page and candidate C-page in one reading, define `coverage_k` as the
fraction of L-role k-gram occurrences whose k-gram occurs at least once in the
candidate C-role bag. Multiplicity in L is retained; multiplicity in C is
binary. The page-pair similarity is

`S = (coverage_3 + coverage_4) / 2`.

No whole-group feature, edit distance, learned embedding, parser feature,
feature selection, IDF, or tuned weight is allowed.

## Frozen score and null

For each reading, average `S(L_page, C_assigned_page)` first across pages within
each folio and then equally across folios. Subtract that reading's complete
orbit mean. This yields `T_e`; the joint statistic is `M = min_e T_e`.

Enumerate every product of within-folio C-page permutations, synchronously in
all readings. The observed mapping is page identity. Use the inclusive
one-sided exact tail with tolerance `1e-15`:

`p = count(null_M >= observed_M - 1e-15) / number_of_mappings`.

Emit exact similarity-matrix, assignment-matrix, orbit, component, page-effect,
folio-effect, and result digests. Positive affine transforms of the two
coverage components, simultaneous page relabeling within folio, feature-token
renaming, input serialization, and reading insertion order must preserve the
registered decision after canonical reordering.

## Mandatory sensitivities

1. **NO_EXACT_GROUP_ECHO:** before forming L n-grams, remove every L group whose
   complete STA-family string also occurs as a complete C group on that same
   page and reading. This prevents a whole-group duplicate from establishing
   a stem/construction result.
2. **ZODIAC_ONLY:** repeat the complete test on the frozen twelve-page zodiac
   panel.
3. Report trigram and four-gram components separately. Each component's
   observed-minus-orbit-mean effect must be positive in every reading; neither
   may be selected alone.

## Target-blind controls

Before opening any real n-gram identity or similarity, synthetic bags must:

- recover a distributed page-specific partial-construction plant across all
  five folios and readings under the full and no-exact-group panels;
- reject null, one-folio-only, one-reading-disagreement, whole-group-duplicate-
  only, and length/exposure-only worlds;
- recover a four-folio zodiac plant under its smaller orbit;
- enforce exact 138,240 and 5,760 unique assignment rows and the identity row;
- preserve the invariances and all hashes above.

Controls are target-blind and supply no manuscript result.

## Frozen confirmation gates

All must pass:

1. controls, hashes, source isolation, finiteness, and independent
   reconstruction;
2. primary `M >= .04`, exact `p <= .01`, and every reading `T_e > 0`;
3. NO_EXACT_GROUP_ECHO `M >= .03`, `p <= .05`, every reading positive;
4. ZODIAC_ONLY `M >= .03`, `p <= .05`, every reading positive;
5. both trigram and four-gram component effects positive in every reading;
6. at least four of five primary folios positive in every reading;
7. at least three of four zodiac folios positive in every reading;
8. every primary leave-one-folio-out `M > .02`;
9. no primary folio supplies more than .45 of total absolute folio effect in
   any reading.

No page, folio, role direction, reading, n-gram length, group subset, component,
or threshold may change after target access.

## Claim ceiling

On pass: L-role labels and same-page C-role circular text share a transferable
page-specific source-native construction field beyond same-folio alternatives,
including partial echoes after complete-group duplicates are removed. This
would justify localizing the responsible anonymous constructions in a new
preregistered experiment.

On failure: this fixed partial-construction representation does not support a
page-specific C-to-L echo.

Neither outcome establishes which label belongs to which object, a sign name,
person, star, degree, day, number, word, morpheme, sound, language, meaning,
plaintext, or translation.
