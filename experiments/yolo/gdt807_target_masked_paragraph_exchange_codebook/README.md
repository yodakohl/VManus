# GDT807 — target-masked paragraph exchange codebook

Status: `REGISTERED_UNSCORED`

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

The outcome can identify a reproducible **paragraph-ecology split** and its
exact recurrent landmark wholes.  It cannot identify what either target means,
license a substring, or produce plaintext.  `PREREGISTRATION.md` records the
outcome-aware preview and the fixed comparison before the scored builder run.
