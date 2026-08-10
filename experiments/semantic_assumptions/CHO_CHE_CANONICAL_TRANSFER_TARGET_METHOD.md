# CCT001 one-shot canonical-transfer target

## Frozen target

Use exactly the 2,223 `source_group_id` rows in
`results/cho_che_canonical_transfer_masked_panel.tsv`.  Join each ID once to
the frozen source-separator transcription.  Require one clean ASCII fragment
and exactly one `(ch|sh)(o|e)` site.  The complete fragment is `raw_type`;
replace only the matched `o/e` character by literal `X` to obtain
`canonical_type`.  No other normalization, fragment, site, page, folio,
reading, or manuscript section is eligible.

The physical folio is held out.  ZL3b, IT2a, and RF1b are alternate readings,
not independent samples.  Use the exact scorer, 256 state orbit, 8,192
complexity-matched merger draws, capacity gates, thresholds, domain/prefix
blocks, deletions, concentration rule, and claim ceiling frozen in
`CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_SPEC.md`.  No threshold or
control may change after the target types are opened.

## Capacity stop

Before numeric scoring, require at least 24 true `o/e` collision pairs, at
least 16 pairs in merger shells of size at least two, collision-pair events on
all eight physical leaves and all three readings, exact 2,223-row identity,
and the frozen reading/leaf/side metadata geometry.  Failure emits only the
registered aggregate capacity stop and closes this target unscored.

## Decisions

- All registered scientific gates pass:
  `CONFIRM_USEFUL_GENERAL_CANONICAL_TRANSFER`.
- Core state-excess, state-orbit, merger-null, reading, leaf, deletion, and
  concentration gates pass but any preregistered domain or prefix gate fails:
  `NONCONFIRM_GENERAL_CANONICAL_TRANSFER_DOMAIN_OR_PREFIX_LIMITED`.
- Otherwise: `NONCONFIRM_CANONICAL_TRANSFER`.

The second outcome does not confirm a domain-specific system; it records only
why the general claim failed and does not authorize a post-hoc subset test.

## Isolation and output

The runner must bind an exact public freeze allowlist, verify target/result
absence before loading target rows, install JSON and report without clobbering,
and emit no individual raw type, canonical template, page score, folio score,
or pair identity.  The aggregate frozen score fields are permitted.  A
production-free validator must independently rejoin all 2,223 rows and
reconstruct every emitted numeric, gate, decision, and report before the
result is final.

Even confirmation establishes only useful transferable formal support for
this one-character canonical representation.  It does not establish an
authorial word, sound, phonology, language, cipher operation, plaintext,
lexical meaning, or translation.
