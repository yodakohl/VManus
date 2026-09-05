# GDT832 method

## Question and scope

Does a shared mixed spelling key benefit jointly from continuous word context
and independently attested word-family relations when reconstructing held
historical Latin? This is an instrument control, not a Voynich run. It implements
a limited co-lemma family factor, not a complete historical paradigm generator.
Reference forms are incomplete and ambiguous.

GDT610's per-word scoring and GDT612's chunk objective motivate the test.
GDT001 already used word context, GDT603 recovered a continuous alphabetic
control, and GDT604 failed its target application. The new falsifier is matched
incremental exact recovery across mixed interfaces and family ablations.
GDT616 and CDA001 remain closed.

## Sources and preliminary design correction

`sources/MANIFEST.json` pins UD Latin ITTB TRAIN and UD Latin UDante TRAIN at
exact commits/hashes. ITTB supplies reference sentence probabilities and
attested form-to-(lemma,UPOS) sets. Control is Monarchia: Book I discovery,
Books II/III held. A paragraph is a maximal contiguous original annotation
citation run. Eight reused citation labels retain separate occurrence-numbered
runs; no chapter is invented.

Written `# text` supplies ordered words. Casefolding, ligature expansion and
combining-mark removal are explicit normalization; punctuation and spacing
are unscored. An unrepresentable alphabetic word excludes its whole paragraph,
not that word alone. No control paragraph was excluded. Exact unambiguous
written-token annotation joins supply lemmas; other joins stay unknown.
Reference sentences sharing any 20-word sequence with control are excluded;
none met that condition. Control words are never selected or duplicated to
fit Voynich statistics.

Before key generation, the local preliminary design required eight discovery
occurrences of each of four nominal suffix rules. Its sole failure was a rule
absent from both partitions. `prepared/CAPACITY.json` preserves that initial
`SOURCE_CAPACITY_STOP` byte-for-byte. No public preregistration or decoder fit
preceded those source counts.

The explicit pre-fit correction in `prepared/ACTIVE_RULE_CAPACITY.json` requires
coverage of each suffix observed in either partition. Unused rules receive no
identification credit, as for unused letters. The four-rule deck remains in
the encoder; its observable control has 24 alphabetic, three suffix and eight
wholeword rules. Corpus, split, deck, seeds and numerical recovery/gain
thresholds did not change. The initial gate is not retroactively passed.

## Encoder and observation

The public architecture has 26 bijective L carriers, four injective S suffix
cards and eight injective W wholeword cards. True suffix deck: `um/is/ae/us`;
W: `et/in/non/est/ad/quod/ut/per`. W takes precedence, then a suffix after at
least three remaining characters, then literal letters. One randomized key
applies everywhere. Seeds 83201/83202/83203 give three robustness replicates
of the same content, not independent historical sources. Atomic roles and
word/paragraph boundaries are given; this is stronger information than Voynich
provides.

Every word and its order is preserved by encoding. Pseudo controls independently
shuffle whole words within discovery and held paragraphs, preserving inventory,
spelling structure and source-family graph. Their words may legitimately be
deciphered; their order must not count as evidence of coherent reading. Truth
is reserved in `sealed/` for the independent evaluator. Public deterministic
source/seed specifications give procedural, not cryptographic, blinding.

## Objective and comparisons

All arms share candidate support: a letter bijection, injective selection from
12 suffix candidates, and injective selection from the 128 most frequent
reference words of length 2–10 (lexical tie break). No per-locus values,
deletions or free extra dictionary entries are allowed.

Word backoff is `P0(w)=.97*count(w)/N+.03*Pchar(w)`. Pchar is an order-four
character word model with three start symbols, an end symbol, additive .1
smoothing over 27 outputs and longest-observed-context backoff. An absolute-
discounted word bigram (discount .5) backs off to P0. FULL sums log conditional
probabilities through each paragraph. Identical plaintext has identical language
probability regardless of cipher packing. This is word context with a character
word backoff, not an unrestricted discourse model.

Before decoding, distinct source word types sharing all but their last atom,
with an identical prefix of at least three atoms, form undirected edges. No key
or semantic label enters extraction. Each edge weighs `1/max(endpoint_degrees)`.
It earns eight times that weight in nats if its distinct decoded forms share
an attested reference lemma/POS. Unknown forms earn zero, not exclusion.
Accidental source relatives remain in the graph.

- FULL uses both factors.
- CUT resets word context only where either adjacent cipher word is W.
- OFF removes family information, retaining all context.
- REWIRED degree-preservingly rewires form/lemma memberships; frequencies,
  candidates, ambiguity degrees and family degrees remain unchanged.

REWIRED is diagnostic. FULL must improve on OFF too; beating incorrect family
information alone does not establish useful additional information.

## Search and evaluation

`src/SPEC.json` fixes numerical settings. Eight starts per arm/key each receive
60,000 annealing proposals and four greedy sweeps. Letter initialization uses
reference/cipher frequency ranks; macro values remain unknown. At most 24 CPU
workers run. `run.py` never opens held ciphertext. Discovery objective alone
selects keys, with lowest start breaking ties. All 120 restarts and 15 selected
keys are hash-locked before evaluation accesses key truth. No subsequent fit
or retuning follows scores.

FULL must attain, for each key, at least 95% exact held words, 99% aligned
characters, and 90% novel composed-form and novel-lemma occurrence accuracy.
Novelty is against original discovery plaintext; only L/S-composed tokens count
in novelty endpoints. Character accuracy is one minus summed wordwise
Levenshtein distance over summed maximum word lengths, excluding known spaces.
Exact paragraph and distinct-type results are reported separately.

FULL must improve by at least two percentage points on average over CUT and
OFF on the fixed union of macro-containing or novel-composed-form occurrences,
with nonnegative gain in every key. Held word-order evidence uses 999 within-
paragraph shuffles under the frozen key: `(1 + #null >= observed)/1000`. Real
FULL requires p<=.01; pseudo FULL requires p>.01. Three pseudo replicates do
not estimate a general false-positive rate. After fits are fixed, the true
key is also scored under each objective, distinguishing search failure from
objectives preferring wrong keys. This is descriptive and licenses no refit.

## Reproduction and limits

From the repository root:

```sh
python experiments/yolo/gdt832_joint_family_context_control/src/prepare.py --phase sources --fetch-sources
python experiments/yolo/gdt832_joint_family_context_control/src/prepare.py --phase sources --active-rule-control
python experiments/yolo/gdt832_joint_family_context_control/src/prepare.py --phase generate --active-rule-control --confirm-spec-sha256 e25b8ec9e44d86d87d78566a528537cdd76c639cf03aa4cda051986553363499
python -m unittest discover -s experiments/yolo/gdt832_joint_family_context_control/src -p 'test_*.py'
python experiments/yolo/gdt832_joint_family_context_control/src/run.py --fit
python experiments/yolo/gdt832_joint_family_context_control/src/run.py --check
```

The runner refuses to overwrite locked fits. Evaluator/validator CLI help
documents independent reconstruction and replay. Runtime models/executables
are regenerated under ignored `runtime/`; compact source inputs and code are
published. No LLM/API key or Voynich payload is involved. Exact source copyrights
and CC BY-NC-SA 3.0 attribution are retained in `sources/`.

A pass demonstrates this supplied control architecture and the specified
extra information. It establishes no Voynich coding class, segmentation,
language, meaning or translation. Source-family pairs here are Latin control
data, not new Voynich relation evidence. No new page or GDT388 semantic edge
is used; f84 and f84r remain forbidden.
