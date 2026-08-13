# GDT001 MTF dynamic-rank cipher screen

Status: **exploratory preregistration on the YOLO branch; not a translation**.

This terminal bounded screen tests one mechanism absent from the existing
GDT001 tournament: a decoded symbol changes the cipher state used for the next
symbol. It does not reopen fixed substitution, periodic keys, source-context
allography, fixed transposition, or latent-state keys.

## Frozen transform

The corpus paths are the exact paths already exported for
`nonsemantic_ngram_o2`. The 25 modeled nonspace source signs and every frozen
source-space event are retained. That stream includes the known legacy cleaner
fragment separators and is not asserted to consist only of manual or authorial
word spaces. For each physical line:

1. reset an ordered list `L` to a transmitted permutation `L0` of `a`–`z`;
2. map source sign `c` through a transmitted bijection `R(c)` onto ranks
   `0..24`;
3. emit `L[R(c)]`, then move that emitted letter to the front of `L`;
4. emit a target space for every frozen source-space event, without updating
   `L`.

Rank 25 is never selected. Because no selected rank can move the item at index
25, the initial letter in that position remains omitted for the complete line.
Given `R`, `L0`, and the emitted stream, inverse MTF reconstructs every source
sign and boundary exactly. No null, exception, expansion, homophone, or latent
boundary channel is allowed.

## Search and accounting

The only historical models are the six frozen order-2 language packs. Three
fixed seeds (`67101`, `67102`, `67103`) initialize `R` and `L0`. Alternating
best-pair-swap descent examines all 300 swaps of `R` and all 325 swaps of `L0`
until no exact retained-score improvement remains. This is heuristic search;
only the retained key score is exact.

The historical key charge is

`3 + log2(6) + U(2) + log2(3) + log2(25!) + log2(26!)` bits.

The matched anonymous control uses the identical line-reset rank process but
an integrated KT order-2 model over exactly 25 reachable anonymous rank labels
plus space. Target-name
permutations are unidentifiable under KT, so it pays `log2(25!)`, not
`log2(26!)`, plus the same class/order/restart terms. A static injective
historical baseline pays `log2(26!)` and the same historical selectors.

The complete score is the frozen lattice observation/separator/raw cost plus
the paid key plus the order-2 payload. No raw neural likelihood is compared.

## Decision

Continue only if one historical MTF candidate simultaneously:

- round-trips all 5,386 lines exactly;
- beats the optimized matched anonymous MTF control;
- beats the optimized static injective historical comparator;
- beats the selector-adjusted current global source leader;
- and yields one identical winning-language decoder in all three starts.

Failure of any condition stops this exact line-reset, order-2 MTF screen. It
does not prove all dynamic ciphers false. Even a pass would be an anonymous
formal decoder lead, not a letter value, language, plaintext, meaning, or
translation.

The frozen length-preserving within-line symbol shuffle is a required
specificity gate. Define gain as `matched anonymous total - historical MTF
total`; the real gain must be strictly greater than the refitted shuffle gain.
The Timm copy/modify synthetic is retained as a per-event diagnostic because
its event count differs; it is not a raw-total gate.
