# F76S001 repaired prescore re-audit

Date: 2026-08-09
Decision: **PASS_REPAIRED_PRESCORE; TARGET UNRUN**

## Scope and blinding

This audit used only the registered F76S001 specification and amendment, the
prior prescore and source-alignment reports, the final production runner and
future nonimporting validator, and the anonymous control artifacts. It did not
invoke `--target`, parse or reconstruct any of the 27 manuscript target rows,
or use OCR, images, or automated vision. The interlinear and current-locus
crosswalk were read only as opaque bytes for SHA-256 verification.

`TARGET_RESULT.json` was absent before the audit and remained absent after it.

## Repaired blockers

1. **Separate provenance bindings pass.** The runner, validator, and control
   artifact separately name and bind the alignment/source report at
   `27593399b74b00e72cbd939519d324d5ace1c4846b457435263b92a3c3104744`
   and the current-locus crosswalk at
   `4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc`.
   Both live hashes match, and the two artifacts are not conflated.

2. **The prospective conservative-tie control passes and is
   mutation-sensitive.** An independent scalar reconstruction of the frozen
   four-identical-position fixture gives exactly four inclusive upper-tail
   subsets, zero strictly greater subsets, and four target ties. Replacing the
   inclusive tail by the strict tail would give zero rather than four and fail
   the frozen assertion. The fixture therefore genuinely distinguishes `>=`
   from `>`.

3. **The exact 27-row contract passes in both implementations.** The actual
   runner guard and the actual validator loader were isolated without importing
   either module and exercised on in-memory synthetic TSV rows. Each accepts
   exactly one row for every frozen `(reading, locus)` key and rejects, in both
   implementations, a duplicate key, a missing key, page drift, and grammar-
   scope drift. No target data were used in these tests.

4. **The future validator contract is complete.** Before a future validation
   can pass, it rehashes the input, alignment report, crosswalk,
   preregistration, amendment, runner, validator, and corrected control result;
   checks the exact 15-member control assertion set and its experiment, mode,
   status, bindings, and pass flag; checks target experiment, mode, recomputed
   status, exact nine pairings, complete bindings, and exact claim ceiling;
   enforces the row contract; and independently reconstructs the primary
   result, every channel deletion, all gates, and the final decision.

## Independent numerical and control reconstruction

The audit uses a separate scalar implementation with explicit triple loops, a
full-matrix edit-distance routine, and independently implemented mean, median,
population standard deviation, ranks, pair gates, synchronous minimum, and
tail counts. It imports neither production implementation.

- The combination space is exactly 84 distinct three-line subsets.
- All six stored synthetic results were reconstructed, covering 1,512 primary
  reading-specific triplet-score evaluations.
- The five nondegenerate full-gate fixtures were also reconstructed under all
  three channel deletions, covering another 3,780 reading-specific triplet-
  score evaluations.
- Every stored scalar, gate, rank, pair detail, exact tail, and primary orbit
  digest agrees within the frozen `1e-12` tolerance.
- The exact membership and truth value of all 15 control assertions agrees in
  the independent reconstruction, the final runner, the final validator, and
  `CONTROL_RESULT.json`.

The final bound artifacts are:

- runner SHA-256:
  `9d63fbeb5cf5a0a079c110759249e95eda75c656a6e00425e2effc2723e0839c`;
- validator SHA-256:
  `9be7adec89d562448bf1b2edbc3411a5652250a71899e4c17207ea86083ae266`;
- corrected control-result SHA-256:
  `4e225a5bece548f6980e10c89a3f5f6753620785c03c9e31190f65fb76f69938`;
- independent audit script SHA-256:
  `e0c5ac686e20cdae505394a3cc8d617ee6093f97bcc857ea02d9adcbad024587`.

Reproduction command:

```bash
PYTHONDONTWRITEBYTECODE=1 ./vpy experiments/semantic_assumptions/f76s001_line_entry_selector/audit_f76s001_prescore_repaired.py
```

It reports 19/19 passing audit checks and independently confirms
`TARGET_RESULT.json` absent before and after execution.

## Claim boundary

This is a prescore software/provenance PASS only. It contains no manuscript
score and establishes no margin-mark ownership, selector function, reuse
outside the fixed aligned-line panel, glyph meaning, sound, lexeme, plaintext,
language, or translation. If the separately governed target is later invoked,
its maximum possible claim remains the exploratory root-free repeated-`s`
line-entry association under the fixed human-editorial pairing.
