# GDT1325 — By/Bdy flank choice across excluded bases and leaves

Decision note/preregistration11October2026, before candidate enumeration or fitting.
Inclusive budget03:55–04:35UTC includes prior review, implementation, independent
validation and publication. No alternate split, feature, smoothing or subgroup
repair after the result. One exposed structural experiment, not a translation.

Unknown: does a single learned external-flank preference predict the y/dy FORMtag
on entirely excluded target bases and physical leaves?1204already contradicts a
DETERMINISTICneighbor rule;1284's same-base/leaf d→qmean is positive but its leaf
consistency fails.311transfers choices on known licensed pairs;865excludes carriers
and leaves for DIFFERENTol/eol,edy/eodycontrasts. No exact same new estimand was
found in bounded review; no exhaustive novelty claim. Original decisions stand.
This test does not rerun1284on a favorable subgroup: it asks prospective rank
transfer from disjoint bases/leaves and matches held tag frequency within each
exact base/page. No standalone-q effect is selected or rescored.

Formal module: nonempty base B of22working units, with final unit notd, followed
by y for tag0or d,y for tag1. Read terminaldy first, otherwise terminaly, then
reject empty bases or bases endingd. This gives exactly one analysis per physical
word. It is a transparent conditional source(base,tag)module, not a whole-language
writer or proof that the native suffix boundary is real. The rival normalizes
to base alone and chooses the tag with an independent coin whose probability may
be arbitrary for each(base,exact page). A positive result would reject that
context-independent nuisance choice and retain a transferable formal cue; no
semantic tag, morphological meaning or grammatical role is thereby established.
A negative result stops this predictor, not all morphology or allography.

Use unchanged1233strict groups, their915original source metadata, and631allowlist.
Require original-index-consecutive LEFT/CENTER/RIGHTgroups at the SAMEexact locus,
all in the strict cache, no bridging gaps or line ends. Currier must be AorB.
Paired bases require both exact terminal forms somewhere in the full strict panel.
This is an exposed, label-dependent pair license, preserved on the fixed test
permutation orbit; it is not a fresh independent confirmation sample.

Physical leaf is numeric fNprefix. Base fold is
SHA256(UTF8('1325|'+','.join(B))).digest()[0] &1.
TRAIN: odd physical leaf AND basefold0. TEST: even leaf AND basefold1. Other
quadrants are not fitted/scored. All target occurrences of a test base are
excluded from training, and all test leaves are excluded. A held-base form may
occur as a neighbor, but its body/tag is never a feature: only the two invariant
flank endpoints are supplied. No center body, length, identity or position feature.

Training model perCurrier: retain TRAIN(base,Currier)cells containing both tags.
For each base/tag separately normalize its event counts of LEFTlastunit to sum1;
do the same for RIGHTfirstunit. SUMthese normalized profiles across bases. Thus
one base contributes unit mass pertag/perside, not one total mass across allbases.
Add1/2to each of22unit counts, then divide by K+11where Kis paired bases in that
Currier. Both tag tables have sameK. Score is the product of dy/yprobability
ratios for the two observed flank units. Use exact rational counts/odds, not
rounded log scores. With no training bases in aCurrier, both tables are uniform
and all its scores1; such held events are NOTdropped.

Retain TEST(base,exact page)cells with both tags. For each, compute exact pairwise
AUC=P(score_dy>score_y)+.5P(tie). Average cells equally within physical leaf,
then average leaves equally. All retained cells/leaves, including constant-score
and exactly chance leaves, stay in the denominator. The matched comparison
removes the need to borrow a held-base prior; chance is AUC1/2.

Capacity perreading: >=10distinct paired training bases overall, >=10held bases,
>=10held physical leaves, >=100held events in retained cells. Also require at least
one retained cell with >=2distinct scores. If either gate fails, NO_CAPACITY or
SCORE_IMMOBILEand no permutations. Otherwise draw1999conditional permutations,
Python random.Random(1325)reset perreading, cells sorted by(base-string,page),
events sorted byid, every draw shuffling original tag lists. Keep models/scores
fixed. Compute exact rational aggregate scores via integer common denominators.
One-sided p=(1+#nullAUC>=observed)/2000. Pass only if AUC>=.55, at least2/3of ALL
retained leaves have AUC>.5, p<=.05/3, and sampled null score is mobile. Common
transfer requires allthree readers; report every failure/partial result separately.
No AUC is a translation or transcription accuracy percentage.

Exchangeability: swapping tag assignments within(base,page)preserves its tagcount,
base license, split and occurrence positions. Each eligible word keeps its first
unit B[0]and lastunity under d insertion/deletion, so flank features remain fixed
even for neighboring target events. TRAINis on disjoint leaves and unchanged.
Under the independent percell coin, all arrangements conditional on the tagcount
are uniform. Selection/transcription masks and layout being tag-independent under
this conditioning remain assumptions; physical glyph width is not reconstructed.
No semantic/author-owned relation edges or newGDT388packet is claimed.

Primary joins1233groups to915metadata and traverses original indices. Separate
validator scans915source-line windows, verifies raw/group joins and every event,
rebuilds matched training profiles with per-event rational weights, scores each
cell by direct dy/y comparisons rather than rank sums, and reconstructs all
permutations. Source-free fixtures check unique suffix inverse, neighboring-feature
invariance and AUCties/rank identity. Code/spec/source hashes locked before run.
All current179selectors only; no rawmixedTSV,newimage,f84/f84r/f116v/f1rbody,
327/336body, reserve, source-language choice or concrete word meaning.
