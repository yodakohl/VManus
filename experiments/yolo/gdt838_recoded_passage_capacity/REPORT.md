# GDT838 — no discovery candidates for the fixed recoding screen

**CAPACITY_STOP.** The public preregistration bba4741d preceded manuscript
extraction. This ten-minute screen tested a necessary discovery condition for
the previously unexecuted internal parallel-passage proposal: an exact shared
ordered repetition pattern admitting a nonidentity whole-group bijection.

| Stage | Count |
|---|---:|
| Admitted odd-numbered discovery selectors | 88 |
| ZL3b bounded paragraph scaffold | 339 paragraphs, 368 segments |
| Contiguous 16-group windows before boundary filtering | 8490 |
| Windows rejected for an uncertain small-space boundary | 5392 |
| Windows meeting six-type / four-repeated-type criteria | 14 |
| Physical folios represented by these windows | 5 |
| Cross-folio pairs with the same ordered equality pattern | **0** |
| Qualifying pairs with at least six nonidentity mappings | **0** |

The eligible windows occur on f21v, f31r, f77v, f81r, f81v and f103v: six
selectors but five physical folios. The 14 windows can overlap and are not
independent evidence. All eligible windows and their complete raw group IDs are
saved in WINDOWS.json; PAIRS.json is empty. The source query selected 46771 group
rows across alternate readings on the allowed odd selectors and rejected 2122
f84-prefixed rows before materialization. Only ZL3b enters the actual window
analysis. Source paragraph flags provide bounded spatial streams, not verified
authorial sentences; drawings and nonadjacency remain barriers.

**Research decision:** do not build a large fixed-bijection decoder or held
prediction pipeline for this registered screen: it currently supplies no pair
to learn from. No shortening, boundary cleanup, lower repetition threshold or
additional reading/source is selected to turn this negative into a lead.

This is a capacity result, not a rejection of all internal parallel passages,
recoding, language or meaningful text. The exact 16-group and repetition criteria
are uncalibrated; most windows have uncertain boundaries, and only odd admitted
folios were searched. No p-value, full-search null comparison, held prediction,
image inspection or semantic inference was performed. Even folios were excluded
from the guarded query and remain unused by this experiment; prior project
exposure is not erased. f84/f84r remain sealed. No relation evidence is score-ready.

The next expensive step has been avoided on actual manuscript evidence rather
than by repairing another artificial Latin decoder. The modest new fact is
absence of candidate cross-folio equality patterns within this fixed sample and
filter, not a newly established property of the entire manuscript.

Validation: three invented direct-bijection checks pass; a separate direct
forward/reverse-map implementation exhaustively checks all 14 saved windows and
confirms the zero pair count without using the search's signature matcher.
Source extraction reuses frozen GDT829 helpers and is not independently rewritten.
A second guarded extraction with run.py --check reproduces all artifacts byte for
byte. Reproduction: run src/run.py, src/validate.py; use their --check modes to
verify existing artifacts. No implementation or criterion changed after public
registration. See PREREGISTRATION.md for decision, budget and predecessor limits.

Focused staged privacy/scope and manifest checks pass. The separate full-repository
check retains the pre-existing seven unbound GDT600 files and stale legacy TSV
index; those unrelated files and rows are not changed by this experiment.
