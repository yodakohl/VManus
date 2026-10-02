# GDT1142 independent validation plan

Prepared before reviewing any native-image pixels, root observations, or second-observer answers. This planning pass used only the current route, `METHOD.md`, and `src/SOURCE.json`. Do not inspect image data or observer records until root's final release. After release, write only the experiment's `src/validate.py` and `artifacts/VALIDATION.json` / `VALIDATION.md`.

## 1. Registered source and public acquisition receipt

- Verify every exact `input_pins` SHA256 from `src/SOURCE.json`, including the old GDT1095 registration/source, GDT1092 source receipt, and the new native-metadata receipt. Check the native metadata receipt's recorded Yale canvas and dimensions against the contract.
- Validate that one acquisition request was made to the exact registered public URL for canvas `1006123`, on the already admitted f25v canvas. Require a successful HTTP 200 image response, final URL/canvas consistent with the registered endpoint, and actual decoded dimensions exactly 2863×3769. Record/verify request time, response status, final URL, byte count, SHA256, content type, and image dimensions in the acquisition receipt. A failed/mismatched request must produce `MISSING_REGISTERED_NATIVE_INPUT`; do not accept a retry at another size or an alternate endpoint.
- Independently check `2863 × 3769 = 10,790,647` against the pinned metadata maximum. Record that a proportional 3000px-wide rendition would exceed this area cap as a plausible explanation of GDT1095's earlier failure, not a proven diagnosis. Validate that the older GDT1095 report/artifacts remain unchanged and its registered result is not retroactively repaired.
- Confirm the acquisition is finer sampling of the same photograph/canvas, not a new image key or independent confirmation. Sealed f84/f84r, unadmitted f116v, reserves, contacts, and all other pages remain out of scope.

## 2. Pixel and crop provenance

- Verify hashes for the untouched downloaded image and any permitted derivative. The sole crop must come directly from those bytes at original sampling, with normalized bounds `(0.65, 0.68, 1.00, 1.00)` converted as `floor(left/top)` and `ceil(right/bottom)`: expected integer bounds `(1860, 2562, 2863, 3769)` and dimensions 1003×1207 for a 2863×3769 source.
- Check the crop bytes equal that exact decoded pixel slice and the parent hash is the acquired native image. Reject resampling, enhancement, altered color, OCR, image generation, or any additional crop/view. Merely reading dimensions and hashes is not a visual observation.
- Both observers must first receive the full unmodified image, then only the single registered crop. Check their release records bind the same full-image/crop hashes and show the required order. Do not view pixels before this release.

## 3. Separate fixed observations and reconciliation order

- Verify exactly five questions, each answered `PRESENT`, `ABSENT_AT_SUPPLIED_SCALE`, or `UNRESOLVED`, with a direct visual reason and no inferred narrative: LEAF_CONTINUITY, SEPARATE_SHAFT, TETHER, DISTINCT_BODY, SECOND_ACTOR. No post-view feature may be added.
- Confirm both observer records are complete, independently timestamped and frozen separately before root comparison. The second observer's packet must not expose root's new answers or the compared historical narratives. Verify hashes/receipts freeze each initial record; any root reconciliation must cite and preserve them unchanged.
- Preserve observer disagreements and all `UNRESOLVED` values. Do not vote answers into facts or retroactively change labels. Validate reconciliation against the method's rules: `PRESENT` needs a described visible structure; absence is limited to the supplied scale; unresolved remains unknown. A diagnostic connection is unresolved if either record identifies ambiguity about that claimed structure.
- Do not certify visual truth. The validator checks completeness, allowed values, provenance, order, immutable records, and bounded wording only.

## 4. Decision and claim limits

- Validate outcome assignment from the receipt and frozen records: `MISSING_REGISTERED_NATIVE_INPUT` for a failed or mismatched registered acquisition; `NATIVE_OBSERVATIONS_RETAINED_ROLE_UNSELECTED` when acquisition and records succeed without a clearly distinguishing structure; `PROVISIONAL_ROLE_CONSTRAINT` only when a clearly described, relevant additional structure has explicit competing interpretations.
- Any provisional constraint must be tied to the predeclared questions (especially separate shaft, tether, distinct body, or second actor) and retain the alternatives: mouth/leaf contact alone does not decide consumption, contact-healing, proximity, or emblematic roles. No word, relation score, species, copied-source claim, or translation follows.
- State plainly that the native image is the same exposed photograph at higher sampling, not a holdout; old GDT1095 is unchanged; no independent confirmation or significance claim is available. A validator PASS is not a visual finding.
- Do not expand the question set, acquire more pixels, open another page, or use enhancement after ambiguity. Preserve all observer limits and disagreements.

## 5. Work boundary

- Keep preparation, acquisition, observation, reconciliation, validation, and publication within the registered 13:24 UTC checkpoint; reassess rather than truncate required checks or expand scope. The user's minimum work-block end 13:52:40 UTC is separate.
- Write no global route/state/ledger, source/author files, registry, or Git changes. Do not run a semantic experiment or use these observations to choose a word meaning.
