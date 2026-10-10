# GDT1316: fixed midpoint fragments predict complete words

Decision note10October2026. Inclusive08:17–08:52UTC budget covers predecessor
review, preparation, execution, verification and publication. No expansion after
budget; no post-outcome split, smoothing, context or mixture repair.

1308retains useful whole-form weighting over its position-aware M1character
predictor;1309shows distributed contributions, not a minimal dictionary. Unknown:
can a fixed, transparent recombination of learned fragments also predict complete
TRAIN-unseen words better than that same M1? If both ALL and globally unseen-word
gates pass, retain this particular productive statistical component. Otherwise
stop this fixed recombination model; do not reject all compositional spelling.
The rule is a probabilistic construction of written forms, not a full language,
encoding of messages, morphological analysis or proposed medieval technique.

Construction H: for each supplied(Currier,exact working-unit length n>=4)cell,
split EVERYword at k=floor(n/2), w=l+r. Count complete left halves C_left(l),
right halves conditioned only on the last unit a of the left C_right(a,r), and
C_end(a)=sum_l:last(l)=a C_left(l), using only1308odd-leafTRAINwords. LetNbe the
TRAINcell total. Choose l with probabilityC_left(l)/N; choose r from the matching
a-table with probabilityC_right(a,r)/C_end(a). Outputlr. Thus
H(lr)=C_left(l)*C_right(last(l),r)/(N*C_end(last(l))).
Unseen lefts or missing(a,r)haveH=0; never evaluate0/0. This procedure is normalized
over all22^nstrings, not just observed words, and can emit an unobserved whole
when both pieces and seam context were learned. It preserves exact leading and
trailing units. The midpoint is a fixed analytical convention, not inferred
syllable/morpheme boundaries. Tables and their costs remain explicit.

Use the frozen1308M1probabilities and its empirical whole modelQ without retuning:
MIX_H=(M1+H)/2 in nonemptyTRAINcells, elseM1. OriginalMIX_Q=(M1+Q)/2unchanged.
Primary score log(MIX_H/M1). Require BOTH ALL and GLOBAL_UNSEENcohorts to have
>=100held occurrences, >=10physical leaves, equal-leaf mean>=.01nat/word and at
least2/3positive leaves. ZLprimary;IT/RFsensitivities, never independent replications.
GLOBAL_UNSEENmeans exact whole unit tuple absentfromALLTRAINCurrier cells, as1308.
Retain ALL,Qzero/Hzero and unseen failures, with no selection of successful forms.
Report MIX_HversusMIX_Qas diagnostic only, never substitute its result for gates.
Also retain Hpositive, Hzero and known-whole diagnostic cohorts, per-leaf gains,
all per-word probabilities and the TRAINleft/right-table entry counts. No pvalue,
synthetic significance claim or new holdout: all pages historically exposed.

Primary uses1308MODEL.json andEVENTS.json.gz, frozen before this proposal. It
reconstructs chunk counts from the TRAINwhole counts and scores all originalheld
rows. Independent verifier reconstructs TRAIN/EVALfrom1233and915sources, checks
oldM1/Qprobabilities against1308events, rebuilds fragment counts by a different
aggregation, validates all scores/gates and normalized tables. Source-free binary
fixtures exhaust all length4words, including positive unseen recombination and
unsupported-piece zero. Protocol/program/input hashes sealed before nativecounts.
No new image, rawTSV, source corpus, f84/f84r/f116v/f1rbody,327/336body or reserves.

Predecessors:608predicts exterior roles of BPE merge tokens;1305/1306selection
caveats remain.326factors opaque host/renderer coordinates, not raw written halves.
1246tests identical dy-final ASCIIhalves under fixed margins, not held complete-word
prediction; its no-excess/capacity result remains. The old opening-to-closing
negative and1285two-previous-unit estimator failure remain; this is neither a
newlast-unit target nor a tuned higher-order Markov retry. Hstores complete halves
with one fixed seam condition; M1baseline and all its input controls are preserved.
A gain would not identify chunks as meaningful or prove a unique mechanism.

Assumptions:22workingunits/gaps; supplied Currierandlength; exposed odd/even split;
fixed midpoint, empirical fragment frequencies, one-unit seam and50:50weight.
Unknown source content and every word meaning remain unassigned. Even a PASS
needs a separate justified source/physical construction before any decipherment.
