# Picatrix IV.ix purpose extraction

Source-only extraction of all 28 lunar-mansion headings in Pingree’s *Picatrix Latinus* (Liber IV, ix, §§29–56; printed pp. 228–234), using the local `pdftotext -layout` output. Each JSON row preserves the Latin heading purpose, English and German paraphrases, source line and printed-page locators, then records body-level additional purposes or variable cases separately from materials, depicted images, spirit/domain names and procedure.

Rows 3 (Azoraye/Pliades) and 7 (Aldira) repeat the exact headline **ad acquirendum omne bonum** and are retained as distinct rows. Row 22 (§50) is an explicit source lacuna and remains `UNKNOWN`. No body text explicitly reverses a heading result; the JSON therefore separates `explicit_inversion` from the independent negative/reverse-valence flag. §57’s cross-row inscription rule is recorded as an out-of-scope note and not folded into the 28 headings.
