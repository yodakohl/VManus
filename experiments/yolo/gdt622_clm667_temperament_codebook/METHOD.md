# GDT622 method

## Question

Can a real late-medieval hybrid codebook—learned whole names followed by
compositional temperament abbreviations—supply short, concrete default meanings
for recurrent Voynich Herbal forms?

## Inputs

- 28 manually read code rows on official BSB Clm 667 scans 161, 163, 165,
  167, and 169;
- GDT621's corrected Manfredus source report and canonical result;
- eleven explicit Voynich plant candidates with public proposal provenance or
  a separately labelled internal direct-image comparison;
- the f84-free GDT327 page inventory and guarded ZL3b token table;
- selected native ZL3b, IT2a, and RF1b loci for reading sensitivity.

The complete mixed token table is opened only through `GuardedTSV` with
explicit allowed pages. Native manual files are read with the locus selector
parsed first; every `f84*` row is discarded before its payload is parsed.

## Construction

1. Reconstruct the Clm 667 grammar from observed rows:
   `WHOLE NAME + (c|f) [degree]? + (s|h) [degree]?`, where `c/f` are
   hot/cold and `s/h` dry/moist.
2. Enumerate the four Voynich surface families `KCH`, `KSH`, `TCH`, and `TSH`
   and their exact `qo-...-(y|ey)` forms.
3. Locate within-line forms that differ on exactly one of the `k/t` or `ch/sh`
   axes while keeping the ending fixed. These are formal compositional minimal
   pairs; the three transcriptions are alternate readings, never replications.
4. Compare all eight possible assignments of the two binary axes on four
   pre-existing external plant proposals. Repeat the same comparison on four
   internal direct-image candidates so that selection dependence is visible.
5. Keep whole-page substring counts, local-window counts, rates, and a
   90-page Herbal-A baseline separate from exact `qo-` forms.
6. Audit three local degree defaults: unmarked on the liquorice windows,
   `otaiin` for degree II, and adjacent `(q)okol daiin` for degree III. Publish
   corpus prevalence so common markers cannot masquerade as unique keys.
7. For every preferred page, record the candidate name locus, the exact target
   quality locus and surface, the degree locus if present, and their line
   distances. A source property with no target span remains explicitly
   unmapped.

The local windows were chosen during exploration around the candidate evidence.
They describe the working theory; they are not an independent confirmation.

## Interpretation tiers

- `HISTORICAL_CODE_CONFIRMED`: values actually read in Clm 667.
- `CONCRETE_EXPLORATORY_DEFAULT`: concrete Voynich quality readings supported
  by the current orientation and exact surface family.
- `EXPLORATORY_DEGREE_DEFAULT`: throughput defaults with their prevalence and
  counterexamples exposed.
- `CANDIDATE_NAME_CARRIER_DEFAULT`: a page-level placeholder only; never a
  confirmed lexeme.

The method supports a page-record hypothesis with distributed fields. It does
not yet support the stricter sequential grammar “name immediately followed by
quality and degree.”

## Claim ceiling

Clm 667 establishes historical plausibility for the hybrid mechanism. GDT622
establishes a real formal 2×2 Voynich family and one leading semantic
orientation that can be used as an exploratory reader. It does not establish
the plant identifications, headword attachment, language, phonetic values,
full plaintext, or a complete manuscript solution.
