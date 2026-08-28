# Frozen target contract: blind Naibbe-family attack on GDT327 corpus

Frozen before querying any target transcription row.

## Inputs and safety

- Target rows may be emitted only by `./vmanus-exp query-tsv` from
  `transcription/voynich_zl3b_lines.tsv`.
- Selector is `page`; every `--allow` value must come from the already f84-free
  `gdt327_joint_tuple_interlinear.tsv` page set.  `--forbid-prefix f84` is
  mandatory.  Output columns are only
  `page,locus,line_number,section,language,hand,eva_clean`.
- Any selector/output beginning `f84` aborts.  f84/f84r are forbidden and may
  never be materialized.
- Page-to-physical-folio mapping may be read from the f84-free GDT327 artifact;
  no transcription string is read there.

## Physical-folio split

- Sort the 91 physical folios by
  `sha256("gdt604-held-v1|" + physical_folio)`.
- First 23 are held; remaining 68 are training.
- Dictionaries, cuts, surface keys, score selection, and rankings use training
  folios only.  Held folios are opened only by the frozen evaluator.

## Segmentation

- Given whitespace token boundaries, every token is either U or exactly P+S
  at one proper character cut.
- Independent ciphertext-only alternating maximum-coverage P/S dictionaries,
  hard P x S occurrence EM, and positive Poisson-deviance U updates.
- Public maximum: six homophones per state/letter on the fixed active
  23-letter renderer `abcdefghilmnopqrstuvxyz`; maximum 138 U, P, or S types.
- Confirmatory model fixes U=138.  U=115 and U=132 are navigation diagnostics
  only and cannot override the confirmatory decision.
- Learned P/S dictionaries and pair marginals are frozen on train.  A held
  token is B only if a frozen P/S cut exists; otherwise it is U only if it is
  in the frozen U dictionary, else unknown.  Multiple held cuts use frozen
  train marginals.

## Reference models

- Latin: Caesar `caesar_la.txt`, pinned SHA-256
  `84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c`.
- Old Italian: Dante `divina_commedia.txt`, pinned SHA-256
  `aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e`.
- Middle High German: MHG4SNA commit
  `3eddc3dc1620cf400c152d9ed8915416cb8d6d7a`, five pinned CoNLL files; tokens
  only, punctuation/annotations excluded.
- Renderer: Unicode NFKD, strip diacritics, `æ->ae`, `œ->oe`, `ß->ss`, then
  `j->i`, `k->c`, `w->uu`; retain only the fixed 23 letters.
- Exactly 120,000 rendered reference characters per language.  MHG contributes
  24,000 from each of Erec, Iwein, Parzival, Rolandslied, and Willehalm.
- Char-4 interpolated/backoff model, alpha 0.25, artificial reset every 90
  rendered characters.
- Paired order-destroyed null for every language: independently shuffle the
  characters inside each 90-character reference chunk with fixed SHA-derived
  seeds, preserving chunk unigram counts and boundaries, then fit the same LM.

## Key fitting and nulls

- Objective: reference char-4 likelihood subject to at most six distinct
  surfaces per state/letter.
- Seeds 11, 29, 47; 50,000 annealing iterations; two independent restarts per
  seed plus capacity-respecting coordinate/swap polishing.
- Fit both the real reference LM and its order-destroyed paired LM on train.
- Held order null: 32 deterministic shuffles within every contiguous decoded
  run of every held line.  Gaps, line/folio identity, run lengths, character
  counts, segmentation, and key stay fixed.

## Frozen outputs and decision

Report train/held dictionary capacities and coverage; all six real-LM restart
scores and keys; pairwise type- and held-occurrence-weighted key agreement;
held folio scores; real-versus-destroyed LM likelihood ratios; order-null z;
and complete top held lines with locus, EVA input, every restart output, and
restart consensus.

A language-like reading requires, for exactly one language:

1. held decoded-unit coverage at least 80%;
2. every real-LM restart has held within-run order z >= 5 and at least 16/23
   held folios have positive observed-minus-null order gain;
3. every seed's real-key held real-vs-destroyed likelihood ratio exceeds its
   paired destroyed-LM-key result by at least 0.10 bit/decoded character;
4. all real-key restart pairs have at least 70% type agreement and 85%
   held-occurrence-weighted agreement on shared codes;
5. global held decoded-character restart consensus is at least 90%.

Failure of any gate is `LM_DRIVEN_PSEUDOTEXT_NO_READING`.  Isolated readable
substrings or top lines cannot override the corpus-wide gates.  No output may
be assigned a lexeme, sound, language, translation, or meaning merely because
it resembles a reference-language string.
