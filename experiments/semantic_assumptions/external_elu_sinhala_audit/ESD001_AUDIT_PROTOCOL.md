# ESD001 external Elu-Sinhala decoder audit protocol

Status: post-publication diagnostic audit. This is not a preregistered test:
the public target repository and its claimed translation were already visible
when the audit was designed.

## Question

Can the public `kamb-code/Voynich` V8 decoder be admitted as independent
translation evidence?

## Frozen public target

- Repository: `https://github.com/kamb-code/Voynich`
- Commit: `e608818b754ac79fc86e7f3bdbe3194db2260c51`
- Audit date: 2026-08-10

The audit uses only public text, source code, word lists, result files, and the
SQLite corpus. It does not use the repository's images, OCR products, plant
identifications, or visual interpretations.

## Checks

1. Read the committed decoder-specificity result and its current source.
2. Re-run that public script once without changing its seed or null.
3. Check whether the specificity test is part of the advertised `run_all.sh`
   validation gate.
4. Inspect whether decoder choices or English meanings use the full curated
   vocabulary before the odd/even folio split.
5. Reconstruct the stated coverage of the published English output.
6. Count evidence tiers and provenance labels in the canonical V20 database.

## Decision rule

Reject the public decoder as independent translation evidence if any of these
conditions holds:

- its own specificity null places H12 at or below the random-decoder mean for
  Sinhala;
- the advertised validation gate omits that failed specificity test;
- the held-folio analysis uses a globally curated decoder/gloss vocabulary;
- the published English output is a partial gloss stream rather than readable
  sentence translation.

Passing this audit would still establish only a candidate phonetic mapping,
not Voynich plaintext. Failing it does not disprove Elu-Sinhala in the
abstract; it rejects this decoder and its published English glosses as usable
evidence for VManus.
