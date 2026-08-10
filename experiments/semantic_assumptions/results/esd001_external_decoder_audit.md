# ESD001 external Elu-Sinhala decoder audit

Status: **REJECT_EXTERNAL_DECODER_AS_TRANSLATION_EVIDENCE**

The public decoder cannot be imported as a Voynich translation. Its own
committed specificity test puts Sinhala below its random-decoder mean
(Z=-0.82;
154/200
random decoders meet or beat H12). Re-running the unchanged public test against
the current committed source still fails (Z=-0.76;
146/200)
and changes the result bytes, so the release result is stale.

The advertised `run_all.sh` includes the odd/even holdout but omits the failed
decoder-specificity test. The holdout loads the full curated decoded vocabulary
before creating its train/test lists; later decoder layers also select variants
when they improve a full Sinhala dictionary or curated gloss tier. It is
therefore not a held-out discovery of the mapping or English lexicon.

The file titled “Complete English Translation” reports only
13,472/36,231
(37.18%) translated gloss slots and
22,759 gaps. Its renderer performs exact EVA-type lookup,
small regex reorderings, capitalization, and punctuation; it does not derive
sentence meanings. The V20 database later fills all tokens, but
20,571/36,633 (56.15%) tokens alone
come from the three explicit provenance classes “context/gloss assigned, no
direct external attestation” or rule-generated q-/ch- compounds.

This is a useful falsification, not a translation: the repository supplies a
deterministic romanization candidate, but it does not demonstrate that the
mapping is specifically Sinhala or that its English gloss stream is plaintext.
The result closes only this audited decoder version.
