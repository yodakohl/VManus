# Method: a bounded number of variant word positions

Let N be the number of complete written groups, D the number of distinct source
word tokens, and S10 the total occurrences of the ten commonest source tokens.
A fixed base form per source token can have at most D forms and at least S10
occurrences in its own ten most frequent forms, even if base forms collide.
Changing at most K occurrences can add at most K forms. The original top-ten
base-form set loses at most K occurrences; the new top ten cannot contain fewer
than this retained set. Hence D_out<=min(N,D+K), S10_out>=max(0,S10-K).

The candidate permits at most one changed occurrence per physical written line.
If the selected target projection touches L lines, K<=L. All touched lines count,
including partial lines. Multiple retained fragments of one line count once.
Changes may be at ANY position, need not shorten, may have unlimited distinct
aliases, and need not be decodable. This optimistic relaxation contains every
actual one-changed-word-per-line shortening implementation under this contract.
Base identity depends only on exact source token. Each source token yields one
nonempty group; no insertion, deletion, fusion, reordering or additional state.

Source frequencies are the existing GDT1202 first8000 inventories. Target
membership exactly repeats GDT1174, retaining its known gaps/working inventory:
GDT1170 guarded projection, allowed SPEC pages, prose only, definite outer seams,
nonempty complete22-sign parsing, seed1174 shuffled page order, lexical locus
order and numeric group order. Reconstructed counts must equal its stored types
and top-ten mass before any decision. The added statistic is touched-line count.
The target sample is a filtered exposed projection, not8000consecutive physical
words or an independent sample. The mismatch is conditional on this same screen.

All12book/reader cases use unchanged integer tolerance400 (0.05*8000) on types
and top-ten count. A capacity failure on either necessary direction excludes
that case; an overall not-excluded status requires every case. Neither passing
inequality proves simultaneous achievability or a readable writer. Record
K_min=max(0,target_types-400-D,S10-target_top10-400) as a necessary lower bound,
not a sufficient edit budget or proof that manuscript writing changed K words.

No original image, pixel width, native shortening/semantic value or general
language claim. GDT1202's different two-spellings bound stays failed. IDEA200's
descriptive context geometry remains unexecuted;801/802's layout association
and their limits remain. Local construction checkpoint, not public release.
