# GDT1347 — known phoneme classes versus nonphonetic instruction roles

## Decision note before selecting or scoring controls

User explicitly requests a phoneme-based positive control and nonlinguistic
negative controls before any native application.1346failed exact vowel-LETTER
recovery on historical spelling, not phoneme recovery. Existing ASJP/Q20P001
contains12owned lists of39–40modern phonetic forms, but sparse inventories and
no independently joined class table; its failed Kartvelian mapping is retained.
No Q20 target data are opened or rerun.

Question: can a bounded unsupervised binary learner recover an independently
annotated phone distinction, and can its structural alternation gate distinguish
that from explicitly nonphonetic but reversible instruction records? These are
separate questions. Sensitivity without specificity does not license a native
sound inference. The strict instruction control's alternating shape is known
analytically in advance; report it as a deliberate specificity challenge, not a
surprise or a proposed Voynich writer.

Smallest adequate test: one official pronunciation dictionary; one fixed learner;
one phone-word split; two fixed procedural controls; one shuffled-phone null.
No decoder, native census, new language roster or automatic metric redesign.
Budget45minutes inclusive of source review/acquisition, code, validation and
publication, from first recorded clock05:40:26UTC12October2026. Some initial
route retrieval preceded this clock; no invented exact total time is claimed.
If phoneme sensitivity fails, or either procedural control passes the structural
gate, do NOT apply this as a phonetic detector to Voynich. Both outcomes change
which component, if any, may be retained: phone-label recovery versus origin
specificity. Neither supplies a native sound value.

## Source, independent classes and sampling

Pinned official CMUdict commit74790861f652b15e4ac49015a90074ad62a27690, local exact
dictionary/phones/README/LICENSE bytes retained. cmudict.phones independently
marks15vowels among39base phones. Its stop/fricative/affricate/nasal/liquid/
semivowel/aspirate categories form the other class. Stress suffix0/1/2 is removed
for learning; validate stress only occurs on listed vowels. No pronunciation
is invented from spelling. This is contemporary US English dictionary speech
notation, not connected-speech annotation or a medieval source. README error
caveat retained. No syllable boundary annotations exist here; evaluate vowel-
nucleus counts, NOT recovered syllable boundaries.

Read all dictionary lines. Base lemma is spelling before terminal(n)variant
marker. Retain bases matching lowercase[a-z]+ and exactly ONE distinct unstressed
phone sequence across their listed variants. Deduplicate identical phone sequences
across all bases, keeping lexicographically first base as representative; retain
all group membership in source receipts. This ensures homophones and pronunciation
variants cannot leak across splits. Require at least5phones, so trimming the first
and last leaves>=3, matching1264interior eligibility.

SHA256('1347split|'+space-joined phones) determines TRAIN/TEST by first byte<128
versus>=128. Sort each side by that same digest and take first8192unique sequences.
If either side has fewer than8192, STOP_NO_CAPACITY. One weight per sequence;
no speech-frequency claim. Map all39phones to opaque integer IDs by sorting
SHA256('1347opaque|'+phone). Learner receives only numeric sequences and weights,
not names, spelling, vowel labels, stress or source words. Root sees source and
truth: programmatic masking, not independent human blinding.

## Fixed negative controls

For each procedural corpus generate16384distinct records with deterministic
random.Random seeds1347001(STRICT)or1347002(VARIABLE). First8192train, rest test.
Each record encodes exactly3SET(address,value)commands with39opaque symbols:
24address symbols and15value-digit symbols. Distinct inventories make decoding
unambiguous. Message values are finite address/digit strings, including their
width; do not collapse leading zeros. No spoken word or sound class is computed.
STRICT has one address symbol and one value symbol per command (six units).
VARIABLE independently chooses each field length uniformly from{1,2}; symbols
are uniform inside their field inventory. Interleave fields, preserving all
symbols; validate exact reconstruction of all six fields in each record.
No native frequencies, fitted parameters, after-the-fact lengths or substitutions.
Roles identify fields, not letters. Apply an independent fixed opaque permutation
by sorting SHA256('1347procopaque|'+original symbol number).

SHUFFLED takes each selected CMU sequence and uniformly permutes its units with
an independent deterministic per-record seed from SHA256('1347shuffle|'+sequence).
It preserves each full record's length and unit bag. This is a destroyed-order
control, not an example of meaningful nonphonetic writing. Splits remain original.
All four corpora retain full records; all training uses their trimmed interiors.

## Learner fixed before outcomes

Use1264mathematical signed-cut objective: summed observed undirected adjacency
minus2count(a)count(b)/interior_length. Aggregate exact rational pair weights,
then round each times10^6 nearest/ties-to-even. Keep every active training unit;
no22-node cap and no merge chosen to improve recovery.

Bounded HEURISTIC, not exhaustive optimizer:64SHA256-seeded initial binary masks,
opaque ID0fixed to0, others given by low bits of SHA256('1347start|start|ID').
If empty, setID1. Up to500strictly improving single-vertex steps; choose maximum
integer gain, smallest ID on ties; never create an empty class. Each final score
and all starts retained. Select highest score, then smallest bitmask. No planted
label input, class-size constraint, alternative seed, hyperparameter search or
restart expansion. Verify every retained score and one-flip local optimality;
if500steps reached, flag optimization limit. No global-optimum claim.

## Separate endpoints, all retained

1. Known-label recovery: report complement-invariant balanced TYPEaccuracy on
active training IDs (vowels versus others, or address/value); fix that orientation
once for whole TEST. Unknown-training IDs count as errors. Report TESTtoken
accuracy and fraction of full TESTrecords with exactly correct number of
vowels/value units. The latter is a count consequence, not independent syllable
segmentation. CMU sensitivity requires balanced accuracy>=0.90, token accuracy
>=0.95, count accuracy>=0.85 and no optimizer/capacity limit. These are explicit
engineering gates, not natural-language laws. Report raw denominators and errors.
Also compare learned training score against the known-label score: a lower score
may indicate inadequate search, not absence of phonetic structure.

2. Structural transfer: for each TESTinterior use fixed learned labels to compute
switch excess over its exact class bag, divided by its adjacent-edge count.
Partition8192records into32fixed consecutive blocks of256; within each block
aggregate excess/edges, then average blocks equally. Gate: mean>=0.03 and at least
22of32blocks positive, with all records classifiable. No pvalue or physical-folio
independence. This adapts the old descriptive1264gate to explicit control blocks.
Report effects for every corpus including both procedural controls and shuffle.

A strict/variable procedural pass is a false positive ONLYfor interpreting this
structural gate as evidence of phonetic origin. It is correct role detection.
If either passes, the gate is not a sufficient phonetic discriminator, regardless
of CMU recovery. Do not promote an added measure after inspecting controls.
Only if CMU sensitivity+transfer pass, both procedural transfer gates fail and
shuffle fails would this limited suite support further evaluation; no universal
specificity or Voynich applicability follows from that conditional result.

## Verification and preservation

Independent validator reparses selected source entries/class metadata, checks
source and split hashes, vocabulary disjointness, control roundtrips, all learned
integer scores/local optima, direct per-record test statistics and recovery
counts. Small exhaustive fixtures test cut arithmetic and the procedural inverse.
No Voynich raw TSV, image, f84/f84r/f116v/f1rbody, native word meanings or target
scores.1346and old native results retain their original decisions. Raw proposal
IDEA001023 is a proposal, not an endorsed phonetic reading.

Prospective peer clarifications, before scoring: at balanced-accuracy orientation
exactly0.5 retain the unflipped0/1labels. If the500stepcap is reached, verify
current score and flag the limit; do not assert local optimality. Any TRAIN-
inactive ID in a whole TESTrecord makes that record's nucleus/value count wrong
for evaluation, even if a default count would accidentally agree. No default
class is assigned to an unseen ID. These clarifications change no source/model.
