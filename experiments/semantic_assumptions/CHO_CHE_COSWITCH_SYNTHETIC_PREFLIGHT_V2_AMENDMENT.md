# `cho/che` co-switch synthetic preflight v2 — blockwise intersection

V1 is preserved as a target-free stop.  It produced 0/64 null passes and 8/8
power for both distributed plants, and rejected six adversarial families, but
accepted 2/8 `ONE_BLOCK` worlds.  The failure occurred because the combined
scorer required only positive mean alignment in a second block; random noise
occasionally satisfied that weak condition.

V2 is a different, stricter falsifier.  It changes only the multi-block gate:

- compute the minimum-reading mean pairwise alignment separately for each of
  `FAMILY_RATE`, `ENDPOINT_RATE`, and `BIGRAM_RATE`;
- compute each block's own inclusive 256-sign synchronous exact p-value;
- require at least two blocks independently to have alignment at least `.10`
  and p no larger than `.01`.

The combined statistic, every held-leaf/orientation/domain/reading/
concentration gate, world generator, seeds, strengths, noise, geometry,
features, and all other thresholds remain unchanged.  V2 must reject all eight
previously generated one-block controls while retaining at least 7/8 power for
both frozen distributed plants and all original null/control gates.  Failure
closes the broader co-switch route before target access.

No target family sequence or manuscript feature/state association has been
opened.  This amendment supplies no co-switch result, meaning, sound,
wordhood, language, cipher, plaintext, or translation.
