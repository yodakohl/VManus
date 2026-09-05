# GDT833 method

## New question and intervention

GDT832 recovered all wholeword/suffix values but misread literal `v`; its
reference contained no `v`. That post-result association did not establish a
cause or a corrected decoder. This new experiment uses a **fresh control work**
and a paired intervention on otherwise identical reference sentences.

NATIVE retains reference spelling. COLLAPSED changes exactly reference-side
`v` to `u`. No control word, ciphertext, key, evaluation spelling or candidate
pool is collapsed. The first result's criteria and reported accuracy are not
repaired. Duplicate screening located GDT832 and earlier continuous-context
controls; this reference intervention and original-spelling falsifier differ
from their tests. GDT616 and CDA001 are not reopened.

## Source and observational scope

Both sources are pinned UD Latin UDante at commit
`e02420457780c6fbb503ba39a7d8798ab6a8645c`. All Monarchia sentences supply the
reference (682 sentences, 19,162 normalized words). De vulgari eloquentia is
the fresh control: Book I discovery, Book II held. All words, including quoted
vernacular poetry, are retained. No Latin-looking passage subset is selected.

Source normalization is the unchanged GDT832 casefold/ligature/NFKD alphabetic-
word transformation. Punctuation/spacing are unscored. Maximal contiguous runs
of an exact annotation citation form paragraph units; five reuse events of
four citation labels retain separate occurrence IDs. Unrepresentable alphabetic
words would exclude whole runs; no run required exclusion. Reference sentences
sharing a 20-word control sequence would be removed; none did.

The source-only capacity audit precedes public fit registration and supplies
120 discovery runs/5,866 words and 122 held runs/5,519 words. There are 507/457
v-containing word occurrences; held novelty is 2,138 composed-form and 1,270
unambiguously joined lemma occurrences. NATIVE reference has 1,188 `v` characters;
COLLAPSED has none. The exact positional pairing is checked before fitting.
These developmental counts are not claimed as publicly preregistered findings.

## Fixed encoder and decoder

Use GDT832's 26 literal, four suffix and eight wholeword cards, value decks,
suffix rule, word boundaries and typed roles. Unobserved nominal parameters
are unidentifiable from the outset. All observed S/W rules require eight
discovery occurrences; every held-active literal needs discovery support.
Three source-independent keys use seeds 83301/83302/83303. They encode the same
content; they are not three independent historical samples.

The one common wholeword candidate pool is the native reference's 128 most
frequent length-2–10 words, with lexical tie breaks. Both models use the same
12 suffix candidates and literal bijection. No target words are added to any
candidate list. Empty family resources and the OFF arm keep GDT832's unhelpful
co-lemma factor out of both conditions.

The existing GDT832 `decoder.cpp`, `reference_model.py`, source-normalization
helpers and discovery projection are used byte-for-byte and hash-bound. The
language objective is the same absolute-discounted word bigram with the same
character-word backoff. No probability smoothing, context rule, output capacity
or optimizer setting changes. Eight starts per key/condition receive 60,000
annealing proposals and four polish sweeps. Seeds and budgets are paired;
frequency initialization naturally uses the respective reference and therefore
need not produce identical initial keys. The oracle contrast below isolates
objective direction independently of search initialization.

All 48 restarts and six discovery-selected fits are hash-locked before the
evaluator reads world truth or computes held recovery. Selection uses discovery
objective only, ties lowest start. No post-result fit or threshold change is
permitted. Procedural blinding is explicit: source/seed rules are public, while
the fitter does not inspect control plaintext or planted keys.

## Specific falsifier and general recovery

`src/SPEC.json` fixes all gates. Orthographic-effect confirmation requires:

1. The NATIVE fit identifies the literal `v` output correctly in every key and
   reconstructs at least 95% of held words containing `v` exactly.
2. Its mean v-word advantage over COLLAPSED is at least 20 percentage points,
   with nonnegative gain in each key.
3. Under NATIVE, the true discovery key scores strictly above a single
   preregistered legal mutant swapping the outputs of the `v` and `z` literal
   carriers. Under COLLAPSED, that direction reverses. This swap preserves the
   bijection and all other key values. Both scores are computed only after all
   fits are locked, and do not trigger replacement-key fitting.

General recovery is assessed separately: each NATIVE fit must reach 95% exact
held words, 99% aligned characters, 90% novel composed-form occurrences and
90% novel joined-lemma occurrences. Novelty is relative to original discovery
plaintext, with L/S-composed words only. Character accuracy is one minus summed
wordwise Levenshtein distance over summed maximum word lengths; spaces are
excluded. Original `v` and `u` are distinct in every metric.

Non-v words, exact paragraphs and supported L/S/W values are secondary
diagnostics. No zero-effect requirement is imposed on non-v words: word context
and bijective keys couple their values. The paired intervention supports a
causal statement within these data and this pipeline, not a population p-value
or a claim that every GDT832 error has been causally explained.

## Reproduction and limits

Source preparation can fetch the pinned primary dataset only:

```sh
python experiments/yolo/gdt833_reference_orthography_intervention/src/prepare.py --source-dir experiments/yolo/gdt833_reference_orthography_intervention/runtime/udante_source --fetch-source
python -m unittest discover -s experiments/yolo/gdt833_reference_orthography_intervention/src -p 'test_*.py'
python experiments/yolo/gdt833_reference_orthography_intervention/src/run.py --fit
python experiments/yolo/gdt833_reference_orthography_intervention/src/run.py --check
```

The fitter refuses to overwrite a locked result. Independent source and final
validation commands are documented by `src/validate.py --help`; runtime reference
models and compiled decoder are regenerated under ignored `runtime/`.
Source attribution and CC BY-NC-SA 3.0 terms are retained in `sources/`.

This control supplies known boundaries, role classes and a limited coding
architecture. It does not solve hidden segmentation, identify a Voynich coding
class or establish any manuscript language, word or meaning. f84/f84r stay
forbidden; no Voynich source or new semantic edge is involved.
