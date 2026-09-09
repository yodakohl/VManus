# GDT884 — a fixed historical passage as a conditional crib

Prospective contract, 2026-09-09, before the selected Voynich source projection
or any word-equation search. A candidate source text is not established plaintext.

Question: can the complete f85r2 North block (.2–.6), under any of the three
recorded primary exact STA-member readings, expand by one fixed string-valued
symbol mapping to the 14 introductory verses of chapter IV in the 1491 Laufenberg
Regimen? Each symbol may map to an empty or arbitrarily long string; different
symbols may share a string. Each visible source group must emit at least one
character. No target word boundaries, letter bijection, syllable length cap,
language-model score or guessed Voynich word meaning is imposed. Erase written
spaces and line breaks on both sides; preserve every recorded STA member symbol.
Only those three recorded primary paths are tested. Marked alternatives remain
reported and are not claimed exhaustively resolved by these paths.

Decision and predecessor: GDT606 produced unstable stylistic pseudotext from
language models, with no carrier-stable values. The new input here is a bounded
real source passage selected from an already proposed image-program parallel,
not a language-model preference. The inherited f85r2/Laufenberg primary reports
are missing from the worktree and local Git history; only their limited image-role
summary survives in VOYNICH_ACTIVE_STATE.md. It does not establish a copied text.
Fresh official KdiH and HAB sources establish the historical passage and show
that physical lines may contain complete rhyme pairs; no Voynich verse order or
phase is inferred from that fact. This test uses whole-block concatenation, not
the stopped cross-block rhyme test or f57/f85 root-identity bridge.

Source: HAB A:167.9 Poet., 1491, scan00161, only the 14 verses after the chapter-IV
heading and subtitle. Exclude the two preceding chapter-III verses. Two readings
of the original produced three unresolved local spellings. Preregister every
combination in SOURCE_INTRO.json, eight source strings; no later spelling repair.
Normalize historical text using Unicode decomposition, remove combining marks,
long-s->s, sharp-s->ss, lowercase, v->u and j->i, and retain only a-z. No lexical
modernization or semantic paraphrase. The photographic hash and official URLs
bind the source; the text predates copyright.

Voynich source projection: exactly five fixed loci; guarded source_separator
and source_sta_group_alignment queries with raw locus selector allow-values and
f84/f84r forbidden. Per reading reconstruct complete ordered groups and source
counts; indices and separators must match across the two atlases. Join lines
in their stated North-block order. Record source annotations and alternatives.
No source expansion, glyph family merging, learned chunks, deletion of source
symbols or extra target passage after failure.

Exact search: prefix DFS over symbol string mappings, with necessary residual
length pruning. Empty symbol strings are real assignments. Freeze each of the
24 reader/source-variant searches at 1,000,000 nodes or60 seconds; at most1,000
solutions per case. Up to24 CPU processes, at most32 total workers. Report UNSAT
only if the search is exhausted, SAT_COMPLETE only if all solutions are listed,
SAT_PARTIAL at solution/budget limits after a witness, otherwise UNKNOWN_BUDGET.
Full source reconstruction and independent certificate replay are required.
An independent solver checks exhausted UNSAT cases; unresolved disagreement stops
interpretation. No tuning of null capacity or normalization follows a failure.

If all24 searches are UNSAT, close this exact candidate-text/encoding contract.
If any search is incomplete, report its limit, without increasing it automatically.
Only after a nonempty complete finite North-key set is available may the fixed
South/Winter continuation be opened: f85r2.12–.17 and the complete36 historical
Winter verses on HAB170–171 (heading/image on169, stop before the next heading
on171). Freeze the North maps before that comparison. A cold complete decoding
requires every Winter code already assigned; no invented value for new codes.
A surviving North map is compatibility, not a decipherment or historical source
identification. Winter work, if reached, must retain this exact scope and report
all surviving North maps rather than choose a key after seeing its answer.

Total budget:30 minutes for the initial North test, including source preparation,
implementation, all searches, validation and publication. Stop expansion at that
limit and report the actual result; unknown or a source error is not an exclusion.
Winter continuation is conditional and gets a separate bounded checkpoint within
the same contract. No new Voynich visual page is needed; no f84/f84r access.
