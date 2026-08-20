# GDT396 prequalification re-audit correction

Status: `AUTHORITATIVE_BEFORE_QUALIFICATION_GENERATION`.

The first full prequalification review remained `HOLD` after every decoder
passed the real pooled-legacy runner. It identified four framework defects.
They were corrected before any qualification or confirmation observation was
generated:

1. Claim uniqueness is now enforced on logical keys, not complete row bytes.
   Conflicting clusters, confidences, Boolean decisions, spans, targets, record
   schemas, or architecture claims cannot coexist under one logical endpoint.
   Status-dependent empty fields and the registered morphology rank cap are
   also enforced.
2. Qualification and confirmation actions authenticate the current instrument
   freeze content, validation-to-freeze hash, every bound implementation file,
   and every decoder/attestation at action time. A stale stored `PASS` is not
   authority. Oracle scoring additionally requires the exact blind-claim
   freeze, manifest hash, file bindings, row count, and decoder-panel hash, and
   refuses to overwrite an existing score.
3. Every semantic endpoint now exports its W10 false-positive quantity even
   when some truth exists. Partition/relation endpoints report the fraction of
   oracle-absent events receiving resolved claims; binary endpoints report the
   positive-prediction rate. The qualifier treats a missing rate as an error,
   never as zero.
4. The experiment manifest/index are regenerated only after the versioned
   correction and decoder panel validate. The historical protocol validation
   remains a disclosed narrow `FAIL`; it is not relabeled as a success.

The correction changes enforcement and bookkeeping only. No decoder feature,
threshold, hidden world, generator, codebook, genealogy, seed, or surface
mapping was selected from qualification/confirmation outcomes. No Voynich
corpus, image, transcription, `f84`, or `f84r` data is an input.
