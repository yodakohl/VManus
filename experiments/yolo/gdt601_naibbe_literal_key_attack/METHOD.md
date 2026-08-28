# GDT601 method

## Question

Does Michael A. Greshko's complete published Naibbe table act as a literal
Latin or Italian decipherment key for independent Voynich text?

## Inputs

- Greshko's 414-entry table and shipped Naibbe encryption of Pliny, pinned to
  commit `f2675ec5dd275268bc64dd48ea64fc0e0e9827a2`.
- Caesar's *De bello Gallico* and Dante's *Commedia* as independent Latin and
  Italian character-model corpora.
- `transcription/voynich_zl3b_lines.tsv`, materialized only through
  `./vmanus-exp query-tsv`; the explicit page allow-list comes from the
  f84-free GDT327 interlinear.

Every external byte source has a pinned URL and SHA-256 in `src/run.py` and in
the result artifact. Greshko's code/data license permits reuse with citation;
the experiment cites Greshko, *Cryptologia* (2025), DOI
`10.1080/01611194.2025.2566408`.

## Method

For each visible token, enumerate only literal readings admitted by the table:
an exact unigram code or one exact prefix+suffix split. Parsed tokens
concatenate because Naibbe removes plaintext word boundaries. Unparsed tokens
hard-reset the candidate run. A fourth-order character model selects among
literal ambiguities by line-level Viterbi search.

The order statistic is mean language-model bits per decoded character. Each of
32 nulls shuffles token order only inside existing contiguous parsed runs, so
coverage, unknown-token locations, run lengths, ambiguity sets, pages and
lines remain fixed. The genuine Naibbe ciphertext must separate strongly from
these nulls before a target result is interpretable.

## Decision rule and claim ceiling

Reject the literal table if the Latin positive control has `z >= 8` while both
Voynich target-language scores have `z <= 0`. This rejects only the exact
published table in normal token/glyph orientation with this gap treatment. It
does not reject all verbose or homophonic ciphers, establish a language, or
assign a Voynich form any meaning.
