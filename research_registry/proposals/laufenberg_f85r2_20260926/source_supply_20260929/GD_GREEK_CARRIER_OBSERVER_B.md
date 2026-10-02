# Greek carrier observer B — frozen source observation

Frozen 2026-10-02T02:48:48.741832+00:00. Registered checkpoint: 2026-10-02 03:13:33 UTC.
Status: **source-local partial rule; unresolved attachment retained**.

This independent reading covers selected τ/μ carriers in the cached native
Reg.gr.181 **219v**, exact canvas **p0470**, and Allen's complete source explanation
(JHS XI, 1890, 286–293; carrier rules 288–289; table discussion 290–292 and plate X).
The source was already known. This is neither a blind reading nor a full
219v transcription. Root's new observation was not read before this freeze.
No native 265v image, new fetch, OCR or Voynich target was accessed. Local
inspection enlargements and PDF rasterizations did not change primary bytes.

| Selected source example | Native retained carrier / marks | Allen-assisted reading | Rule status |
|---|---|---|---|
| I first word, native line 20 after + | recognizable οις, arch and pair over οι, near iota | τοῖς supplies τ at word prefix | attachment to single letter versus whole οι span unresolved; nearest-iota insertion would instead yield οτις |
| μὲν, native line 21 after παραχρῆμα | εν; two dots below ε | μ before ε → μεν | admitted one-letter insertion; accents separate |
| αὐτός, native line 23 left | connected αυ-like group + ο + ς; pair above ο | τ between αυ and ο → αυτος | admitted insertion; αυ-ligature interpretation assisted by Allen, not two independently isolated glyphs |
| double note, native line 22 far right | two rounded forms with horizontal stroke below | ὀφθαλμῶν; Allen says doubled single note forms plural | native double form resolved; lexical stem/case expansion and single-note paradigm not independently resolved |
| μετὰ fragment, native line 22 | ε-like fragment with lower pair; following curved group and upper pair | μετὰ | full carrier segmentation/τ gap unresolved; excluded from executable cases |

Native line numbers count the main text's first complete line as 1; contextual
locators govern if line counting differs. The JSON records the exact source
paths/hashes, carrier assignments, editorial dependencies and withheld cases.

## Finite rule and its actual capacity

For **annotated** retained string `s`, source-supported mark value `l ∈ {τ, μ}`
and independently resolved insertion gap `g`, return
`s[:g] + l + s[g:]`. If any input is unresolved, return **UNRESOLVED** without
choosing a Greek word from context. Preserve retained-letter order. The two
admitted cases are `(εν, μ, 0) → μεν` and `(αυος, τ, 2) → αυτος`.
This is executable at the annotation level. It is not a pixel classifier or
an autonomous transcription rule. The first τοῖς provides the exact remaining
obligation: identify the carrier span independently of its expected expansion.
No complete-word generalization is claimed from its editorial prefix placement.

## Constraints that prevent a false total rule

Allen explicitly expanded ordinary ligatures/abbreviations before printing
(288), while approximating distorted shorthand. A normalized printed word
cannot certify that all its letters are separately retained in the manuscript.
Literal carriers, ordinary expansion, supplied shorthand letters and editorial
accents therefore remain separate layers.

Vertical placement alone does not identify a letter: Allen reports τ dots
**below** iota in III to avoid iota's own dots **above** (288). This is an
edition-reported countercase, not another newly inspected native example.
Carrier spans may be ordinary written letters or abbreviation signs (289).
The native ambiguity over οι is therefore material, not permission to move a
mark wherever the expected word needs it.

Actual doubling and actual overlap are different. The native doubled note in
I corresponds to a plural expansion (288); an inflected lexical result does
not follow from doubling bare omicrons. Conversely Allen's εἰς note plus extra
sigma and κατά note plus extra alpha already include the added letter (289,
291). Those cases need separately identified overlap, not plain concatenation.
They license no general removal of duplicates; their native forms were not
admitted in this bounded inspection.

The table contains ordinary and shorthand forms, signs absent from running
text, two εκ forms, a two-word υπερ τας entry and uncertain dots/shapes/meanings
(291–292, plate X). It supplies neither an exhaustive deterministic dictionary
nor a rule that every dot is τ/μ. Allen retains an unresolved word in I and
questions superfluous dots elsewhere (288); neither is repaired here.

The result is a **two-case partial source rule**, with concrete withheld inputs.
A larger source reconstruction needs independently resolved carrier spans,
ordinary-abbreviation values, exact overlap cases and inflected note expansions.
This packet supplies no Greek/Voynich key and nominates no continuation or
experiment.
