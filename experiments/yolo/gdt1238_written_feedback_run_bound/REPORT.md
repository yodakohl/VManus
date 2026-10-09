# GDT1238 — repeated-sign bound is inconclusive

The registered maximum-run bound excludes no whole group in any of the three
alternate readings. Native groups contain runs of up to four identical working
units; this requires at least three identical consecutive source letters for
the fixed injective previous-written-glyph family. The unchanged bare Deot
projection does contain such a source run. **RUN_BOUND_INCONCLUSIVE_ALL_READINGS**
is the scientific result, not a successful writer or selected cipher key.

| Reading | Strict whole groups | Groups with maximum run 2 / 3 / 4 | Necessary source maximum |
|---|---:|---:|---:|
| IT2a | 22,528 | 5,526 / 378 / 9 | at least 3 |
| RF1b | 19,321 | 4,762 / 333 / 8 | at least 3 |
| ZL3b | 19,332 | 4,865 / 318 / 5 | at least 3 |

All longest-run forms are singletons in this strict selection. Complete forms,
locations, working units, run positions and separate-reader support are retained
in RESULT and NATIVE_RUNS; no exceptional form is deleted. For example,
`deeeese` at f7r.8, `keeees` at f21v.3 and `qoeeeety` at f87r.13 occur in all
three readings. This is transcription agreement about the same manuscript,
not three independent observations or an image examination.

The source has 6,288 words and 24,668 letters. There are 6,028 words with maximum
run 1, 259 with maximum 2, and one with maximum 3. The latter is the projected
form `מממונ`, section 6:10, zero-based word index 59. Its three initial mems
are retained by the original source projection. No Hebrew word is assigned to
a native form. The source maximum permits an output maximum of four; this
inequality says nothing about the requisite word length, position, common
table, word frequencies or complete sentence content.

The proof was reviewed before counting. The implementation checked all 4,080
binary permutation-row/source/entry examples up to source length eight and a
noninjective counterexample. The independent validator reconstructed every
source section from all seven cached raw chapters, every native/source run and
form-support record, and the fixtures using different algorithms. PASS is a
correctness check by separate code from the same author, not independent
palaeographic or semantic confirmation. Inputs and both scripts were frozen at
17:28:01 UTC, before the new counts; validation completed at 17:28:14 UTC.

Keep the old GDT001 instability and GDT1230 source-feedback entropy exclusion
unchanged. In GDT001, the actual preceding-context code already uses observed
glyphs despite the old source-context wording; the present family is not a new
cipher invention. No key optimizer, extra state, reserve, new image, glyph
correction or native meaning was used. Working-unit/group assumptions and the
rare longest-run witnesses limit the result. No automatic decoder follows.

A possible length-and-position consequence was noticed only after RESULT was
read. It is not part of this registered result and may be assessed separately;
it cannot retrospectively convert this maximum-only test into an exclusion.

Reproduce with the two commands in experiment.json. This is a local construction
checkpoint under the preserved 4 October instruction; no commit or push.
