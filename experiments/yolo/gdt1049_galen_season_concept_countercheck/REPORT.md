# GDT1049 — seasons in the complete Brock Galen edition

**Winter and summer occur in a small part of this complete physiological
argument. This does not provide a Voynich frequency bound or select a word
meaning.** The predeclared broad-seasonality counterexample was not found;
the already unpreferred seasonal guesses remain unpreferred, without a new
semantic rejection.

All 266 authorial paragraphs in 41 chapters were read, covering 42,707
whitespace-delimited English words. The fixed source is Brock's 1916
[translation of Galen, *On the Natural Faculties*](https://www.gutenberg.org/ebooks/43383).
Frontmatter, footnotes and repeated language bodies were excluded. Native
paragraphs range from 9 to 567 words; they are editorial units, not established
Voynich equivalents. Complete row-level annotations and hashes are published.

| Whole source | Paragraphs | WINTER definite–possible | SUMMER definite–possible |
|---|---:|---:|---:|
| Book I | 104 | 2–2 | 1–1 |
| Book II | 66 | 1–3 | 0–4 |
| Book III | 96 | 0–0 | 0–0 |
| All three books, one work | 266 | **3–5** | **1–5** |

On the separate chapter scale, winter occurs in 3 of 41 chapters under either
bound; summer occurs in 1–2 of 41. No continuing seasonal topic outside the
locally definite/uncertain references was identified. These are annotation
bounds for this edition, not confidence intervals or estimates of a corpus
maximum. No statistical significance is claimed.

## Every positive or unresolved location

`E` means expressed, `U` unresolved identity, and `N` no local reference under
the fixed rules. A paragraph may express a seasonal class without uniquely
selecting winter or summer; such cases are preserved as possible references.

| Paragraph ID | Winter | Summer | Content and limit |
|---|---|---|---|
| I_13.p017 | E | E | Different purgative effects under explicit winter/summer conditions. |
| I_17.p007 | E | N | An explicit winter observation about urine after drinking. |
| II_8.p009 | E | N | Cold animals' inactivity explicitly situated in winter. |
| II_8.p010 | U | U | Colder/warmer seasons among several humoral determinants; no unique season identification. |
| II_8.p014 | N | U | Warm seasons among circumstances favouring bile; not automatically summer. |
| II_8.p015 | U | U | Seasonal warmth and opposite circumstances; the possible winter component stays uncertain. |
| II_8.p016 | N | U | Back-reference to previously listed warming causes, including seasonal conditions. |

Cold, heat, age, daily timing, pregnancy duration and digestive stages were
not silently seasonalized. The explicitly named autumn in II_9.p005 does not
supply either tested concept merely through a four-season scheme. Repeated
physiological examples do not automatically inherit an earlier winter setting.
All remaining 259 paragraphs retain their individual negative annotations;
none was classified negative merely for lacking a search word.

## Review and reproducibility

Two first readers divided the whole work: Books I/II and Book III. All first
annotations were frozen at 16:23:54 UTC. A separate agent read all 266 paragraphs
in complete chapter context, froze its observations before seeing the first
annotations, and then reread all 82 required rows: every positive/uncertain/topic
row plus each chapter's first and last paragraph. It retained all original
judgements. The supplementary search, performed only after the freeze, checked
34 candidate paragraphs and found no omitted seasonal reference. The search
also has false positives and misses one anaphoric possible reference, illustrating
why it did not supply the original labels.

No Greek ambiguity check was needed or performed; this remains an English
edition result. Agent agreement is a second reading, not an independent
manuscript witness or a proof of perfect semantic recall. Mechanical validation
separately checks raw source hash, complete extraction, annotations, review
coverage, frozen original bytes and count arithmetic. See
[VALIDATION](artifacts/VALIDATION.json) and [semantic review](artifacts/SECOND_REVIEW.json).

One upstream footnote number was literal text rather than a tagged reference.
Its exact removal from I_16.p001 implements the original exclusion rule;
[initial metadata and correction](artifacts/EXTRACTION_CORRECTION.json) preserve
that change. No paragraph boundary, wordcount or semantic endpoint changed.
All substantive bracketed translator additions remain. The independent extractor
also records the final empty page-marker paragraph among editorial exclusions;
it yields the same 266 authorial paragraphs and every final text hash.

The source's raw and full extracted text remain local. The runner can acquire
the public HTML only at the fixed hash; changed remote bytes are not accepted.
The [README](README.md) gives reproduction commands. The executable replays
explicit annotations; it does not automatically reproduce human comprehension.

## Research decision

The countercheck adds a fully inspected source example with limited seasonality.
It does not license treating Galen as a representative sample of the Voynich
manuscript, equating its chapters/paragraphs with Voynich units, or setting a
universal winter/summer ceiling from these counts. A highly seasonal handbook
could differ sharply. No target data or reserves were opened here.

Do not expand this pilot automatically to the other two source works or build
a frequency classifier. IDEA607's original feasibility decision and IDEA608's
missing source-to-target bridge are unchanged. A later semantic hypothesis may
use this source profile as an explicitly limited comparison, but must still
account for the actual distribution and construction of its proposed word.
Confirmed translated words remain zero.

Registration was at 16:11:57 UTC with an inclusive deadline of 17:11:57 UTC.
Actual validation/publication time is recorded in the block checkpoint; the
hour is a ceiling, not a claim that an hour elapsed.
