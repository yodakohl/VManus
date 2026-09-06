# GDT853 — context transfer conditional on exact unspaced form

Question: does retained spacing predict external written neighbors when
unspaced whole W is exactly fixed? Root reviewed605/839/850 and IL026;
this is a fixed same-W held-folio directional prediction, not a new family
inventory or a claim that spelling splits reveal meaning.

Use only the lossless published GDT851 SOURCE_ZL3b cache,179selectors. Input
hash comes from its published manifest before data inspection here. No new
query, page, image or alternate-reading pooling. f84/f84r remain excluded.
Every included target group and immediate external neighbor must match
[a-z]+ exactly: exclude annotations, do not normalize them. Joined target is
one raw W; split target is exactly two consecutive X Y with W=X+Y and
DEFINITE_SPACE internally. Both outer boundaries must be definite, group
indices consecutive through both external neighbors, and all groups within
one source line. Keep every physical span once; do not duplicate a joined
occurrence for different possible split points. Different one-cut splits of
one W share the binary SPLIT class. No longer split spans or line edges.

Physical folio is numeric fN stripped from the selector, retaining selector
separately. Even-numbered folios are discovery; odd are held. These manuscript
pages were previously exposed: this is exploratory transfer, not untouched
confirmation. W qualifies only if discovery has at least2joined and2split
occurrences, each class distributed over at least2physical folios.

Select held pairs without neighbor identities. A joined and split candidate
must have identical W, physical folio, selector, kind, section, hand and
exact starting source_group_index. They may occupy different source lines.
Enumerate all such pairs. Canonical metadata record consists of W, folio,
selector, kind, section, hand, start index, joined occurrence ID and split
occurrence ID; JSON encode that list with ASCII compact separators. Rank by
SHA256 of the UTF-8 string '853|'+that JSON, breaking ties by the JSON itself.
Select only the smallest ranked pair per held physical folio. This is a fixed
metadata-only selector, not optimization for balance, contexts or outcomes.
Require at least8selected folios, at least3W, and no W on more than half the
selected pairs. If capacity fails, stop: do not compute any predictor scores.

If capacity passes, each W and side has a discovery vocabulary equal to the
union of both classes' exact neighbors, plus one UNKNOWN category. Let V be
its size, N_c the number of discovery occurrences in class c, and n_c(v)
its count for that side. The score contribution for a known neighbor v is
log((n_SPLIT(v)+1)/(N_SPLIT+V)) -
log((n_JOINED(v)+1)/(N_JOINED+V)). UNKNOWN contributes exactly zero, even
though its reserved category enters V. Target score is the mean of left and
right contributions. Report known/unknown counts separately by held class and
side: the zero-UNKNOWN policy can predict through unequal familiarity. Pair correct iff score(split)>score(joined); exact ties
are failures. Record every selected pair and both scores. No fitted weights,
subgroup rescue, alternate smoothing, wider neighbor radius or threshold tuning.

Descriptive success requires correct fraction>=0.875 over ALL selected pairs
and at least8nontied folios; otherwise report failure. No binomial p value:
residual layout dependence and nonrandom assignment remain. Transfer would
support a contextual distinction between written realizations, not meanings,
causal effects or universal grammar. Text-level predictability may reflect
transcription choices; GDT852 visually checks only one target seam, not all
spacing. No authorial-intent or manuscript-language claim follows. Capacity failure stops this comparator;
score failure stops this fixed predictor. Neither licenses widening the scope.

Budget20min total including preparation, independent validation and root
publication. Root publishes protocol and returns GO before manuscript data
are loaded. Complete source enumeration and independent pair/score validation
are required; source rows and metadata are retained without glosses.
