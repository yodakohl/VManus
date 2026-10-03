# Unpaired neural decipherment: actual capacity and missing bridge

2026-10-03. Bounded primary-literature review. No implementation, fitting,
corpus download, source-plaintext acquisition or new manuscript access.
Published performance below is author-reported, not independently reproduced.
This is a focused comparison, not a claim to exhaust all recent literature.

**Decision: a relevant unpaired latent-sequence architecture exists, but no
reviewed demonstrated model jointly supplies our unknown compositional writing
channel, whole-form effects and identifiable plaintext. Do not launch another
decoder merely by replacing its optimizer with a neural network.**

## Local evidence that must remain operative

- GDT608/current composition brief: directed component order and exact whole-form
  residuals both matter. Neither establishes phonetic units or an output language.
- `experiments/yolo/gdt616_joint_child_feasible_binding/REPORT.md`: original
  registered configuration is exact UNSAT. Later minimum-relaxation diagnostics
  do not turn it into a successful joint decoder or license another synthetic
  generator repair.
- `experiments/yolo/gdt1160_contextual_abbreviation_inverse/REPORT.md`: supervised
  resolution among training-attested expansions succeeds; neural macro accuracy
  79.651%, versus linear76.155%, over21,512 held sites. This does not learn an
  unknown expansion inventory or unknown script-to-language relation.
- `experiments/yolo/gdt905_joint_cv_complete_passage_candidates/REPORT.md` and
  `experiments/yolo/gdt906_complete_cv_key_enumeration/REPORT.md`: unchanged finite
  CV/Latin construction exhausted439,399 cases on49 paragraph/readings with zero
  grammar-accepted keys. A neural search over that same space cannot manufacture
  a valid solution. GDT892's unexecuted12+9 source recovery control remains a
  separate capacity stop.

## Four specific primary methods

### Luo, Cao and Barzilay2019: variable-length word transduction, not sentence meaning

The character seq2seq model and latent vocabulary alignment are jointly trained
through alternating neural optimization and minimum-cost flow. Inputs are
segmented vocabularies in related languages; assumptions include predominantly
monotone spelling correspondence, sparse mostly one-to-one cognates and substantial
overlap. Word-pair labels are not training anchors. LinearB includes919 lost
tokens, with919 Greek candidates in the noiseless task or455 name candidates;
reported accuracy is84.7% and67.3% respectively. Ugaritic has7,353 lost tokens,
41,263 known tokens and2,214 gold cognates. This is genuine unknown correspondence
learning, including syllabic input, but not free reconstruction of full sentences
from an arbitrary writing system. Minimum-cost flow is exact for its current
costs; alternating neural training is not an exhaustive global-identification
proof. [Primary paper, §§3–5](https://aclanthology.org/P19-1303.pdf);
[official repository](https://github.com/j-luo93/NeuroDecipher).

### Luo et al.2021: unknown word segmentation, constrained alphabetic phonology

The model jointly selects nonoverlapping cognate spans and learns character
correspondences, using dynamic programming and phonological regularization.
Monotone edits allow deletion and insertion of up to two aligned characters.
It explicitly assumes alphabetic lost-side units; known-side IPA and gold stems
are supplied. Unmatched characters have a uniform background model rather than
being fully translated. Data:40,518 Gothic tokens,7,353 Ugaritic vocabulary
items,3,466 undersegmented Iberian chunks. With no supplied Gothic boundaries,
base-model top10 accuracy is.820/.213/.046 against Proto-Germanic/OldNorse/
OldEnglish; full-phonetic-knowledge scores are.863/.597/.497. These are different
information settings, not one wholly unanchored success rate. Iberian name
evaluation uses Latin-recorded names; it does not establish a full Iberian
translation. This relaxes segmentation, not arbitrary compositional abbreviation.
[Primary paper, §§3–5, Tables1–2](https://aclanthology.org/2021.tacl-1.5.pdf);
[official repository](https://github.com/j-luo93/DecipherUnsegmented).

### He, Wang, Neubig and Berg-Kirkpatrick2020: closest architectural ingredient

A latent complete target sequence generates each observed sequence. Variational
training combines reconstruction, language-model priors and entropy regularization;
parameters are shared across transduction directions. This genuinely learns from
unpaired corpora and can represent context-dependent sequence transformations.
However, its decipherment evidence is whole-word substitution:200,000 sentences
per domain,100% enciphered vocabulary,100,000 paired test sentences. Reported
78.4 BLEU versus76.4 UNMT is not exact-key or complete-plaintext recovery.
Removing parameter sharing produces effectively failed outputs. A simpler
backtranslation-plus-LM ablation collapses to repetitive fluent sentences on
style tasks: low perplexity alone is not fidelity. Therefore the general
architecture is relevant, but its published decipherment experiment does not
validate unknown variable-length abbreviations or manuscript-sized training.
[Primary paper, §§3–5 and AppendixA](https://arxiv.org/pdf/2002.03912).
The [official implementation](https://github.com/cindyxinyiwang/deep-latent-sequence-model)
requires pretrained domain LMs; no code or datasets were acquired here.

### Ryskina et al.2020: a useful negative check on neural flexibility

Unpaired informal romanization uses a variable-length WFST channel plus a
character language model; a character-level neural UNMT baseline is compared.
Each language has5,000 romanized training sentences. Native-language LM data
are49,000 Arabic sentences and307,000 Russian sentences. Uninformed WFST
character error rates are.735/.660; phonetic priors improve them to.377/.222,
while UNMT obtains.791/.242. Thus the neural model fails badly on the smaller
Arabic setting even though the language and character-level task are known.
The informative priors come from phonetic keyboards/visual confusables, not
meaning-free observations. This is evidence for variable-length unpaired
channels, but also evidence that their performance depends on available
channel information. It is not evidence that a free neural model will discover
our channel. [Primary paper, Tables2–3 and §§3–6](https://aclanthology.org/2020.acl-main.737.pdf);
[official repository](https://github.com/ryskina/romanization-decipherment).

## What could genuinely use our structure — and what remains unproved

The closest design ingredient is He et al.'s latent **complete sequence**,
with a separately constrained variable-span channel. A prospective model could
tie ordered component rewrites globally, allow a limited whole-form residual
and condition permitted alternatives on neighboring written context. This would
represent all three GDT608/1160 requirements without providing word translations
as anchors. It is a proposed new model, not functionality demonstrated by the
reviewed packages. Its residual capacity, allowed span operations and known-side
language/domain would all be paid assumptions, not conclusions from608.

The central problem is identifiability, not the availability of gradients.
With flexible encoder/decoder pairs, a different hidden language-like sequence
can be re-encoded consistently. A strong language prior can favor plausible
prose unrelated to the document; a whole-form residual can memorize that mapping.
Directed composition constrains a representation but does not by itself name its
referents. These are model-design deductions, not external experimental findings.

A genuinely different source-control question would remove all expansion-pair
supervision from1160 and require exact human-gold recovery of unseen complete
contexts under an independently specified, restricted channel. Success would
show unpaired recovery capacity in that task; failure would distinguish it from
the already successful candidate-disambiguation task. Reconstruction loss,
fluency, restarts agreeing or fitting training forms would not meet that endpoint.
No suitable independent gold/channel contract is established by this review,
and a positive source test would still not reopen905/906's unchanged target space.

**Current action: retain this precise architectural gap and do not implement.**
The literature refutes the blanket claim that unpaired variable-length neural
learning is impossible. It does not supply an already validated, small-data,
anchor-free compositional Voynich decoder or a new target-discriminating
consequence. No assigned meanings, new experiment or reopened route follows.

## Root cross-check: two superficially closer demonstrations

Chu, Valenti and Knight2020's dictionary-code method is explicitly a
known-plaintext attack. An extracted wordbank already decodes40.8% of evaluation
tokens; dictionary ordering then bounds candidate words between anchors.
The neural model ranks those lattices. It does not demonstrate recovery of
an unknown lexical code from zero word correspondences. The abstract,
introduction and evaluation contain different accuracy figures; no single
headline rate is imported as our expected accuracy. [Primary paper, §§4–6]
(https://aclanthology.org/2020.emnlp-main.471.pdf).

Gorman et al.2021 train supervised abbreviation models and use a strict
nonempty subsequence channel: retained letters keep their identity and order,
with one observed word per expanded word. This supplies productive deletion
expansion beyond a lookup dictionary, but does not learn unknown symbols,
historical special signs or arbitrary contraction rules without pairs.
The21,318 annotated training sentences and separate large LM corpus differ
substantially from our single manuscript. [Primary paper, §§1.3–5]
(https://aclanthology.org/2021.findings-emnlp.85.pdf).

Root also read the complete GDT603/604 and833/834 primary reports.603's96.6949%
control recovery and833's5519/5519 held words,122/122 complete paragraphs are
important retained positives: no aligned plaintext or pretranslated target
word is logically necessary under a supplied identifiable writing model.
604 nevertheless failed actual target transfer;834 recovered all35 observed
roles but selected two wrong wholeword values. These distinguish channel
recovery, objective fidelity and target suitability. See the companion
UNPAIRED_DECIPHERMENT_PREDECESSOR_REVIEW.md before choosing a successor.
No decoder, corpus expansion or new fit is selected by this review.
