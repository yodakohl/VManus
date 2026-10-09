# GDT1268 — one fixed previous-word column difference writer

Selected before new source encoding/metrics,2026-10-07. Inclusive work allocation
19:55–20:35UTC (40min), including earlier broad positive-prior retrieval, candidate
selection, implementation, validation and local closure. This window begins before
the first20:00 clock readings; it is an allocation, not a measured exact start.
At the deadline stop expansion. No second alignment, source, key or reset repair.

## Unknown and decision
GDT1193 shows reversible source content can pass a coarse screen but uses2130
entries and fails key q/y/entropy diagnostics.1180previous-letter contextual
alphabets fail;1217continuous previous-unit ring fails its fixed expanded source
lengths;1230excludes arbitrary one-PREVIOUS-LETTER rows on Deot by a source bound.
927's mandatory prefix copying has an idempotence counterexample.
001's STOP_DIFFERENTIAL_RECORDS used cost-chosen literal versus KEEP/SUB/DEL/INS
edit records over native groups, with line/page resets; that original stop remains.941writes
vertical blocks with paid row endings, not the rule below.237's native
state/message ambiguity remains uninstantiated; this source-control writer does
not select that native route or translate any written word.

New complete mechanism: maintain the ENTIRE immediately previous decoded source
word, not the last letter or a keep-prefix count. Reuse a fixed22-position ring
at corresponding word coordinates. It can change whole-word equality statistics
without a large wordbook, and repeated output does not force idempotent prefix
copying. Its invariant H2/frequency outcome is not inherited from those writers.
No additional arbitrary context tables are fitted.

Before implementation,1228's original mean3.923028/SD1.337506 is already known to
pass length conditions in many native samples; length alone does not decide.
If the new fixed writer fails the declared necessary screen for a reader, no
global glyph renaming can fix it there. If it survives, retain only a simple
reversible coarse-control candidate: q->o, finaly, edit adjacency, morphology,
source identity and native meaning remain untested. No decoder automatically.

## Exact forward and inverse rule
Source: unchanged whole1228bare Deot projection:71sections,6288words. Ring order
is exactly אבגדהוזחטיכלמנסעפצקרשת (the22base-letter order; final forms already
folded by1228). Work at logical string indices, starting with index0; no visual
right/left alternate is searched. Each section resets the previous word to empty.

For word w and saved previous plaintext v, at each coordinate j output
(rank(w[j])-rank(v[j])) modulo22, using reference0 if j>=len(v).
Output exactly len(w) residues as one group, preserve group/section boundaries,
then replace the saved word with ALL of w. No letter from an older longer word
survives after a short word. Zero is a written symbol, never omitted.

Read each group by adding its residues modulo22 to the same saved previous
plaintext coordinates, or reference0 beyond its length. Replace the whole buffer
only after completing the word. The reader needs one fixed ring, a previous-word
buffer and temporary current word; no perword dictionary. Source-word lengths
and boundaries are visible in output; no invisible length side channel is used.
Each residue can later be mapped bijectively to one of the22working signs; this
screen cannot prefer a native mapping. No native code values are asserted.

Hand fixture over abstract ring A/B/C/D/E (0..4): ABC -> AC -> ACDE -> ACDE
writes012,01,0034,0000. This covers shortening, regrowth withdiscardedtail,
zero-runs and exact source repetition. It is an artificial teaching example.
All source character/word/section sequences must roundtrip exactly in the stated
BARE projection. Printed points/brackets/punctuation lost by1228are not recovered.

## Minimal adequate source-control test
Freeze the single rule and ring, encode each complete section once, decode and
re-encode. Save persection hashes, complete length histogram, wordtype/top10
counts as diagnostics, and exact within-word adjacent residue counts.
Compare precisely the three1228invariants: mean length(relative20%), population
lengthSD(relative25%), within-word conditional entropy(absolute0.30bits).
Use the SAME1228cached equal6288group samples,128seeds per scoreable reader/cell.
For each actual sample apply allthree jointly; ANY joint match prevents exclusion
for that reader. Keep insufficient-capacity cells untested. No new native query,
sample, target normalization or threshold. Readers/cells/samples overlap.

Primary status allreaders excluded only if each reader has0jointmatches;
otherwise NECESSARY_SCREEN_SURVIVES_ONLY for the survivingreader(s), with explicit
perreader decisions. No pooled extrema, pvalues, independent confirmation or
fullVoynichstatistic match. Frequency diagnostics do not add posthoc gates.

Independent validator imports no primary functions: addition-based reconstruction,
wholebuffer update checks, source/encodedhashes, momentsSD and joint-minus-marginal
entropy, cached sample gate reconstruction. Before target/source run, exhaustive
smallalphabet wordsequences verify inverse on variablelength/reset cases; named
fixture catches accidental oldtail retention and premature buffer update.
Lock protocol, programs and inputs before source evaluation.

## Scope and costs
This is an invented hand-executable procedure, not historical attestation. A
22-ring plus whole previous word storage costs more memory than a one-state ring;
no claim of fast penwork or medieval use. The fixed source is an exposed digital
bare edition, not a proven original or universal Hebrew representative. No native
meaning, language choice, images, rawTSV, f84/f84r, f116v or reserves. Local-only
checkpoint under4Octoberinstruction; no push. Original failures stay frozen.
