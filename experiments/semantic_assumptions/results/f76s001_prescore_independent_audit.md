# F76S001 independent prescore audit

Date: 2026-08-09
Decision: **REVISE — TARGET MUST REMAIN UNRUN**

## Blocking revisions

1. **The real source/alignment audit is not hash-bound.** The preregistration
   freezes `f76r_keylike_sequence_source_audit.md` at
   `27593399b74b00e72cbd939519d324d5ace1c4846b457435263b92a3c3104744`.
   The runner instead names `existing_human_current_locus_crosswalk.tsv`
   `SOURCE_AUDIT`, binds only its hash
   `4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc`,
   and the control report consequently says the source audit is bound. That TSV
   contains zero `f76r` rows and cannot attest the nine mark/line pairings.
   Bind and verify the actual source report explicitly; retain the crosswalk
   only under its correct name if it is still required.

2. **The required conservative-tie control is not an effective control.** The
   implementation correctly uses `>=` with a tolerance, but none of the nine
   frozen assertions requires a known tied-target tail count. The assertions
   still have their expected pass/fail pattern if `>=` is replaced by strict
   `>`. Add a fixture with a predeclared nonunique top target and assert its
   exact tail count is greater than one. This must be prospective and must not
   inspect the real panel.

3. **“Exactly nine paired rows” is not enforced against duplicate input
   rows.** `load_target_panel()` stores rows in a dictionary, so a second row
   with the same `(edition,locus)` silently overwrites the first. Require
   exactly one `CONFIRMED_PROSE` row for each of the 27 frozen
   reading/locus keys and reject duplicates before extracting features. Apply
   the same cardinality and scope checks in the independent validator.

4. **The future validator does not validate the complete result binding.** It
   checks only the input hash from the target artifact. It does not rehash the
   actual source audit, crosswalk, preregistration, runner, validator, or
   control result; nor does it compare the stored nine pairings, experiment
   mode/status, or claim ceiling. Add these checks before its numerical
   reconstruction can satisfy the preregistered independent gate.

## Checks that pass

- The hard-coded pairing and repeated-`s` positions agree between the
  preregistration and runner. The source report supports only approximate
  aligned-line use and unresolved ownership, which the claim ceiling mostly
  respects.
- Controls do not load target rows: they hash the input and evaluate synthetic
  panels only. `TARGET_RESULT.json` is absent and was not created or read.
- All 84 combinations are enumerated once. Population standardization is
  performed separately by reading, the same subset is evaluated
  synchronously, and the minimum reading-wise z-score is a valid conjunction
  statistic. ZL3b/IT2a/RF1b are not treated as independent samples.
- The seven numerical/robustness gates implement the published thresholds:
  `4/84`, per-reading rank at most three, minimum raw-score effect `0.10`, all
  three target pairs strictly above the 36-pair median, and every two-channel
  deletion at `p<=4/84`. Degenerate primary or deletion orbits stop.
- An independent anonymous reconstruction reproduced 40 stored control fields
  and all 84-subset counts without opening the target. The planted, different-
  triplet, single-channel, two-line leverage, reading-disagreement, and
  degeneracy fixtures otherwise behave as described; current artifact hashes
  match their stored values.
- The mechanism is genuinely distinct from F76M001's whole-line/interval
  root-and-role bags and F76J001's character-level mark/word fusion. F76S001
  tests only a positional first-token construction using carrier, q-state, and
  q-stripped role path. It remains explicitly post-exposure and exploratory.

## Claim ceiling

After the revisions and a new independent prescore check, a complete pass
could support only an association **under the fixed human-editorial aligned-
line pairing** between the repeated margin `s` positions and coherent
root-free line-entry states. It could not establish authorial ownership, a
selector function, paragraph segmentation, reuse outside this one panel,
glyph meaning, sound, lexeme, plaintext, language, or translation.

No target score is authorized from the current artifacts.
