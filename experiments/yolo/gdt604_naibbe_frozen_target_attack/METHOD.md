# GDT604 method

## Question

Does the GDT603-recoverable public Naibbe architecture yield one stable,
held-folio language reading when its segmentation dictionaries and key are
learned only from an f84-free Voynich training partition?

## Inputs

- the 91-folio page set already exposed by GDT327;
- ZL3b rows emitted only through `./vmanus-exp query-tsv` with 180 explicit
  page allow-values and `--forbid-prefix f84`;
- Caesar Latin, Dante Old Italian and five MHG4SNA Middle High German texts;
- GDT603's public architecture: each supplied whitespace token is either one
  U surface or one P+S surface, with at most 138 types per state and six
  surfaces per state/plaintext letter.

## Method

Physical folios are sorted by the SHA-256 of
`gdt604-held-v1|physical_folio`; the first 23 are held and the remaining 68
train every dictionary, cut, marginal and key. The held partition is not used
to select a segmentation or key.

The primary factoriser fixes U=138; U=115 and U=132 are navigation only. It
alternates capped P/S maximum coverage, P×S occurrence marginals and
Poisson-deviance U updates. An unseen held token receives a cut only from the
frozen P/S dictionaries; otherwise it is an explicit gap and resets the
language model.

Every language uses 120,000 rendered reference characters and a matched null
that shuffles characters independently inside each 90-character reference
chunk. The capacity-constrained key solver runs seeds 11, 29 and 47 with two
restarts and 50,000 annealing iterations for both the real and destroyed
language models: 36 train-only keys in total. Held order is compared with 32
within-run shuffles preserving folio, line, gaps, lengths, segmentation and
character counts.

## Decision rule and claim ceiling

A language-like reading requires exactly one language to satisfy all of:

1. held decoded-token coverage at least 80%;
2. every real-key restart held order z at least 5 and at least 16/23 held
   folios positive;
3. every real-key restart beats its paired destroyed-model-key result by at
   least 0.10 bit per decoded character;
4. every real-key pair has at least 70% type agreement and 85% held-occurrence
   weighted agreement; and
5. all-six held decoded-character consensus at least 90%.

Failure of any gate is `LM_DRIVEN_PSEUDOTEXT_NO_READING`. The result may reject
this exact target attack. It may not reject every cipher family or assign a
Voynich language, sound, lexeme, plaintext, translation or meaning. f84 and
f84r remain forbidden.
