# GDT1077 preregistration — terminal r/l and the next written initial

An [external 2026 analysis](https://github.com/Workwrite-Niidome/voynich-manuscript-analysis/blob/master/FINAL_PAPER_v3.md)
reports that the next group's initial is associated with the preceding
terminal r/l/n. This is a source claim, not a verified result in VManus. Its
"vowel" terminology is not imported as a Voynich phonetic value. GDT915's
known-pair terminal-r/l concordance and GDT916's failure on new stem pairs
measure the **next terminal**, not the next initial. The unknown here is a
same-rest, same-section/hand written adjacency effect. A positive result
would make next-initial context worth including in formal alternate-ending
models; a failure would stop this exact proposed link. Neither outcome gives
a sound, grammatical case, meaning or translation.

Use only GDT631's 179 admitted page selectors through `query-tsv`; reject
`f84*` in the raw selector before materializing other columns. Keep each
reader separate. In running P-lines, retain every adjacent pair of source
groups whose raw forms match `[a-z]+`, whose between-group boundary is a
definite space, and whose left group has length at least three and ends in
literal `r` or `l`. The rest is that complete left raw form minus its final
letter. The fixed right-initial graphic class is `{a,e,i,o}`; every other
lowercase initial is the other class. Do not slide over uncertain groups,
cross a line, add normalized allographs or remove common words.

For each `(reader, rest, section, hand)` cell retain all r/l events and
physical-folio counts. A cell is informative only if each ending occurs at
least three times on at least two distinct physical folios. Compare the
fraction followed by `{a,e,i,o}` after r against that after l. Primary ZL3b
gate: at least ten informative cells, at least two-thirds with strictly
higher r fraction, and equal-cell mean difference at least 0.05. Ties count
against the two-thirds condition. IT2a/RF1b are sensitivity, not additional
trials. Record all cells, including insufficient and reverse ones.

This is a prespecified descriptive transfer of an externally nominated
contrast, not a calibrated test of all historical hypotheses. Do not call a
positive "sandhi" or phonetic evidence: exact next-word bigrams, page and
line position can cause it. No significance claim. Prior project exposure
and the external paper's complete-manuscript exposure preclude a blind
confirmation claim. Budget 35 wall minutes including implementation,
validation, report and publication; stop at the limit without changing the
graphic class or thresholds.
