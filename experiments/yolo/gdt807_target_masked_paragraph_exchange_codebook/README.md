# GDT807 — target-masked paragraph exchange codebook

Status: `COMPLETE__0_ROBUST__3_PROVISIONAL__0_NO_SPLIT__ZERO_SEMANTIC_PROMOTION`

GDT807 asks whether the text left in a complete paragraph after every line
containing a target whole has been removed can distinguish three fixed pairs:
`cheol/otal`, `qokol/qotal`, and `qokeol/qokol`.  The score never sees the
target line, any target whole, a German renderer label, or a semantic tag.

The unit is one target membership in one strictly start-to-end bounded
paragraph.  The classifier is trained and tested by physical folio, and a
cyclic exchange null moves complete target sets between matched paragraph
remainders.  Exact GDT757 line-initial wholes and concrete German rivals are
reported only after the primary surface-only calculation; neither can rescue
a failed split.

The run reconstructs 665 strict paragraphs; 609 remain eligible after 847
target-bearing lines are removed.  All three pairs show a provisional held-folio
split, but none clears the K24 specificity comparison.  `cheol/otal` comes
closest (seven of eight robustness gates), while `qokeol/qokol` is most resistant
to the edit-neighbour ablation.  The deliberately broad landmark screen selects
380 pair×surface rows and is not a dictionary.

The outcome therefore identifies reproducible **paragraph ecology**, not what
either target means.  It licenses no substring, lexeme, renderer patch or
plaintext.  See `REPORT.md` for the scores and `artifacts/VALIDATION.json` for
the independent reconstruction.
